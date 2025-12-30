import typing as t

from .. import Abc
from .Manager import Manager
from ..Sequences.MaterialManager import MaterialSequence


class MaterialManager(
    Manager[Abc.Graphic.Materials.Material],
):
    def __init__(self, window: Abc.Graphic.Windows.Window) -> None:
        super().__init__()

        self._window = window

    @property
    def window(self):
        return self._window

    @property
    def sequence(self) -> MaterialSequence[Abc.Material]:
        return MaterialSequence(self._storage.values())

    def Register[T: Abc.Graphic.Materials.Material](self, item: T) -> T:
        return t.cast(T, super().Register(item))

    @t.overload
    def Remove[T: Abc.Graphic.Materials.Material](self, item: T, /) -> T: ...
    @t.overload
    def Remove[T: Abc.Graphic.Materials.Material, TDefault: t.Any](self, item: T, default: TDefault, /) -> T | TDefault: ...

    def Remove(self, *args: t.Any):
        return super().Remove(*args)
