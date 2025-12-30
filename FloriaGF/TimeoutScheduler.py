import typing as t
import asyncio

from . import Utils


TimeoutSchedulerCallbackFunc = t.Union[
    t.Callable[[], t.Any],
    t.Callable[[], t.Coroutine[t.Any, t.Any, t.Any]],
]
"""Тип для коллбэков таймера: может быть синхронной функцией или асинхронной корутиной."""


class TimeoutScheduler:
    """Планировщик асинхронных таймеров с отменой по ID.

    Управляет набором отложенных вызовов, которые выполняются достижении заданного времени.
    Поддерживает отмену задач по уникальному ID.

    Example::

        scheduler = TimeoutScheduler()

        # Запуск таймера
        timer_id = scheduler.SetTimeout(1.5, lambda: print("Выполнено"))

        # Отмена таймера
        scheduler.Cancel(timer_id)
    """

    __slots__ = ('_timers', '_id')

    def __init__(self) -> None:
        self._timers: dict[int, asyncio.Task[t.Any]] = {}
        self._id: int = 0

    def _GetID(self):
        id = self._id
        self._id += 1
        return id

    def SetTimeout(
        self,
        delay: float,
        callback: TimeoutSchedulerCallbackFunc,
    ) -> int:
        """Регистрирует новый таймер с задержкой.

        Args:
            delay (float): Задержка в секундах до срабатывания.
            callback (TimeoutSchedulerCallbackFunc): Функция или корутина для выполнения.

        Returns:
            int: Уникальный идентификатор таймера для последующей отмены.
        """

        id = self._GetID()

        async def Wrapper():
            await asyncio.sleep(delay)
            await Utils.Invoke(callback)

        def DoneCallback(*args: t.Any, **kwargs: t.Any):
            self._timers.pop(id)

        task = asyncio.create_task(Wrapper())
        task.add_done_callback(DoneCallback)

        self._timers[id] = task

        return id

    def Cancel(self, timer_id: t.Optional[int]):
        """Отменяет запланированный таймер по ID.

        Args:
            timer_id (int | None): Идентификатор таймера для отмены.

        Returns:
            (TimeoutSchedulerCallbackFunc | None): Коллбэк отмененного таймера или None, если таймер не найден.
        """

        if timer_id is not None and (task := self._timers.pop(timer_id, None)) is not None:
            task.cancel()
