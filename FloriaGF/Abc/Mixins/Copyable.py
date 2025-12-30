from abc import ABC, abstractmethod
import typing as t


class CopyableAsync(ABC):
    __slots__ = ()

    @abstractmethod
    async def Copy(self, *args: t.Any, **kwargs: t.Any) -> t.Any: ...


class Copyable(ABC):
    __slots__ = ()

    @abstractmethod
    def Copy(self, *args: t.Any, **kwargs: t.Any) -> t.Any: ...
