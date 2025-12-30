from abc import ABC, abstractmethod
import typing as t
from contextlib import asynccontextmanager, contextmanager


class Binding(ABC):
    __slots__ = ()

    @contextmanager
    @abstractmethod
    def Bind(self, *args: t.Any, **kwargs: t.Any) -> t.Generator[t.Self, t.Any, None]:
        yield self
