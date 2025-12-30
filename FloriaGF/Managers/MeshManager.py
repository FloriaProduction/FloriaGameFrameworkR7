import typing as t

from .. import Abc
from .Manager import Manager
from ..Sequences import MeshSequence


class MeshManager(
    Manager[Abc.Graphic.Mesh],
):
    @property
    def sequence(self) -> MeshSequence[Abc.Mesh]:
        return MeshSequence(self._storage.values())

    def Register[T: Abc.Mesh](self, item: T) -> T:
        return t.cast(T, super().Register(item))

    @t.overload
    def Remove[T: Abc.Mesh](self, item: T, /) -> T: ...
    @t.overload
    def Remove[T: Abc.Mesh, TDefault: t.Any](self, item: T, default: TDefault, /) -> T | TDefault: ...

    def Remove(self, *args: t.Any):
        return super().Remove(*args)
