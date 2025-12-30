from abc import ABC, abstractmethod
import typing as t


class DisposableAsync(ABC):
    __slots__ = ()

    @abstractmethod
    async def Dispose(self, *args: t.Any, **kwargs: t.Any): ...


class Disposable(ABC):
    __slots__ = ()

    @abstractmethod
    def Dispose(self, *args: t.Any, **kwargs: t.Any): ...
