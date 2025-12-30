import typing as t

from .. import Abc
from .Manager import Manager
from ..Sequences.ShaderSequence import ShaderSequence


class ShaderManager(
    Manager[Abc.Graphic.ShaderPrograms.ShaderProgram],
):
    def __init__(self, window: Abc.Graphic.Windows.Window) -> None:
        super().__init__()

        self._window = window

    @property
    def window(self):
        return self._window

    @property
    def sequence(self) -> ShaderSequence[Abc.ShaderProgram]:
        return ShaderSequence(self._storage.values())

    def Register[T: Abc.Graphic.ShaderPrograms.ShaderProgram](self, item: T) -> T:
        return t.cast(T, super().Register(item))

    @t.overload
    def Remove[T: Abc.Graphic.ShaderPrograms.ShaderProgram](self, item: T, /) -> T: ...
    @t.overload
    def Remove[T: Abc.Graphic.ShaderPrograms.ShaderProgram, TDefault: t.Any](
        self, item: T, default: TDefault, /
    ) -> T | TDefault: ...

    def Remove(self, *args: t.Any):
        return super().Remove(*args)
