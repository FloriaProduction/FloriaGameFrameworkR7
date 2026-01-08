import typing as t
import asyncio
from weakref import WeakMethod

from .Stopwatch import stopwatch


P = t.ParamSpec('P')


class EventCallable(t.Protocol[P]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> t.Any: ...


class AsyncEventCallable(t.Protocol[P]):
    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> t.Any: ...


class EventWrappedFunction(t.Generic[P]):
    __slots__ = (
        '_func',
        'once',
        'wait',
    )

    def __init__(
        self,
        func: t.Union[AsyncEventCallable[P], EventCallable[P]],
        weak: bool = True,
        once: bool = False,
        wait: bool = True,
    ) -> None:
        self._func: t.Union[
            WeakMethod[AsyncEventCallable[P]],
            WeakMethod[EventCallable[P]],
            AsyncEventCallable[P],
            EventCallable[P],
        ] = (
            WeakMethod(func) if hasattr(func, '__self__') and weak else func
        )
        self.once: bool = once
        self.wait: bool = wait

    @property
    def func(self) -> t.Optional[t.Union[AsyncEventCallable[P], EventCallable[P]]]:
        return (
            t.cast(
                t.Union[AsyncEventCallable[P], EventCallable[P]],
                self._func(),  # pyright: ignore[reportUnknownMemberType]
            )
            if isinstance(self._func, WeakMethod)
            else self._func
        )


class AsyncEvent(t.Generic[P]):
    __slots__ = (
        '_funcs',
        '_id',
    )

    def __init__(self) -> None:
        self._funcs: dict[int, EventWrappedFunction[P]] = {}
        self._id: int = 0

    def _GenID(self):
        self._id += 1
        return self._id

    def Register(
        self,
        func: AsyncEventCallable[P] | EventCallable[P],
        once: bool = False,
        wait: bool = True,
    ) -> int:
        """Регистрирует функцию для дальнейшего вызова событием.

        Args:
            func (AsyncEventCallable[P] | EventCallable[P]): Целевая функция.
            once (bool, optional): Вызвать функцию единожды. Defaults to False.
            wait (bool, optional): Блокирует ли функция поток выполнения. Defaults to True.

        Returns:
            int: Уникальный идентификатор, по которому можно отписаться от события.
        """
        id = self._GenID()
        self._funcs[id] = EventWrappedFunction(
            func,
            True,
            once,
            wait,
        )
        return id

    def Remove(self, id: t.Optional[int]) -> bool:
        if id is None:
            return False
        if self._funcs.pop(id, None) is None:
            return False
        return True

    def RegisterOnce(
        self,
        func: t.Union[AsyncEventCallable[P], EventCallable[P]],
        wait: bool = True,
    ):
        return self.Register(func, True, wait)

    def RegisterNoWait(
        self,
        func: t.Union[AsyncEventCallable[P], EventCallable[P]],
        once: bool = False,
    ):
        return self.Register(func, once, False)

    def RegisterOnceNoWait(
        self,
        func: t.Union[AsyncEventCallable[P], EventCallable[P]],
    ):
        return self.Register(func, True, False)

    def _Invoke(self, *args: P.args, **kwargs: P.kwargs) -> t.Sequence[asyncio.Task[t.Any]]:
        if len(self._funcs) == 0:
            return ()

        to_remove: list[int] = []
        tasks: list[asyncio.Task[t.Any]] = []

        for id, wrapped in (*self._funcs.items(),):
            if (func := wrapped.func) is None or wrapped.once:
                to_remove.append(id)
                if func is None:
                    continue

            result = func(*args, **kwargs)

            if isinstance(result, t.Coroutine):
                task = asyncio.create_task(result)  # pyright: ignore[reportUnknownArgumentType]
                if wrapped.wait:
                    tasks.append(task)
                else:
                    task.add_done_callback(self._TaskDoneCallback)

        for i in to_remove:
            self._funcs.pop(i)

        return tasks

    @stopwatch
    async def InvokeAsync(self, *args: P.args, **kwargs: P.kwargs):
        if len(tasks := self._Invoke(*args, **kwargs)) > 0:
            await asyncio.gather(*tasks)

    @stopwatch
    def Invoke(self, *args: P.args, **kwargs: P.kwargs):
        for task in self._Invoke(*args, **kwargs):
            task.add_done_callback(self._TaskDoneCallback)

    @staticmethod
    def _TaskDoneCallback(task: asyncio.Task[t.Any]) -> None:
        try:
            task.result()

        except asyncio.CancelledError:
            pass

        except Exception as ex:
            from .Core import Core

            Core.InvokeException(ex)

    @property
    def count(self):
        return len(self._funcs)

    def __len__(self):
        return self.count
