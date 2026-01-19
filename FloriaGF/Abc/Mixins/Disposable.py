from abc import ABC, abstractmethod
import typing as t

if t.TYPE_CHECKING:
    from ...AsyncEvent import AsyncEvent


class BaseDisposable(ABC):
    __slots__ = ()

    @property
    @abstractmethod
    def on_dispose(self) -> 'AsyncEvent[...]': ...


class DisposableAsync(BaseDisposable):
    __slots__ = ()

    @abstractmethod
    async def Dispose(self, *args: t.Any, **kwargs: t.Any): ...


class Disposable(BaseDisposable):
    __slots__ = ()

    @abstractmethod
    def Dispose(self, *args: t.Any, **kwargs: t.Any): ...
