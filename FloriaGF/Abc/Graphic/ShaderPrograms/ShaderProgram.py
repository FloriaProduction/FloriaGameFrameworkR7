from abc import ABC, abstractmethod
import typing as t
from contextlib import contextmanager

from ... import Mixins

if t.TYPE_CHECKING:
    from .Scheme import Scheme
    from ....AsyncEvent import AsyncEvent


class ShaderProgram(
    Mixins.ID[int],
    Mixins.Nameable[t.Optional[str]],
    Mixins.Binding,
    Mixins.Disposable,
    ABC,
):
    __slots__ = ()

    @property
    @abstractmethod
    def scheme(self) -> 'Scheme': ...

    @abstractmethod
    def SetUniformFloat(self, name: str, value: float): ...
    @abstractmethod
    def SetUniformVector(
        self,
        name: str,
        value: t.Union[
            tuple[float, float],
            tuple[float, float, float],
            tuple[float, float, float, float],
        ],
    ): ...

    @contextmanager
    @abstractmethod
    def Bind(self, *args: t.Any, **kwargs: t.Any):
        yield self

    @property
    @abstractmethod
    def on_dispose(self) -> 'AsyncEvent[t.Self]': ...
