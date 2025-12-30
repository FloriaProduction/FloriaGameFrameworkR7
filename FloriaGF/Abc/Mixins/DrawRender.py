from abc import ABC, abstractmethod
import typing as t


class DrawRender(ABC):
    __slots__ = ()

    @abstractmethod
    def Render(self, *args: t.Any, **kwargs: t.Any) -> t.Any: ...

    @abstractmethod
    def Draw(self, *args: t.Any, **kwargs: t.Any) -> t.Any: ...
