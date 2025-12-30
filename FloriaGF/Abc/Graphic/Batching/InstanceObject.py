from abc import ABC, abstractmethod
import typing as t

from ... import Mixins
from ....InstanceAttributeManager import InstanceAttributeManager

if t.TYPE_CHECKING:
    from uuid import UUID

    from ..Mesh import Mesh
    from .Batch import Batch
    from .... import Types
    from ..Materials.Material import Material


class InstanceObject(
    InstanceAttributeManager,
    Mixins.ID['UUID'],
    Mixins.Signaturable,
    Mixins.Disposable,
    Mixins.Repr,
    ABC,
):
    __slots__ = ()

    @property
    @abstractmethod
    def position(self) -> 'Types.Vec3[float]': ...
    @position.setter
    @abstractmethod
    def position(self, value: 'Types.hints.position_3d'): ...

    @property
    @abstractmethod
    def rotation(self) -> 'Types.Vec3[float]': ...
    @rotation.setter
    @abstractmethod
    def rotation(self, value: 'Types.hints.rotation'): ...

    @property
    @abstractmethod
    def scale(self) -> 'Types.Vec3[float]': ...
    @scale.setter
    @abstractmethod
    def scale(self, value: 'Types.hints.scale_3d'): ...

    @property
    @abstractmethod
    def opacity(self) -> float: ...
    @opacity.setter
    @abstractmethod
    def opacity(self, value: float): ...

    @property
    @abstractmethod
    def visible(self) -> bool: ...
    @visible.setter
    @abstractmethod
    def visible(self, value: bool): ...

    @property
    @abstractmethod
    def batch(self) -> 'Batch': ...

    @property
    @abstractmethod
    def mesh(self) -> 'Mesh': ...

    @property
    @abstractmethod
    def material(self) -> 'Material': ...

    def _GetStrKwargs(self) -> dict[str, t.Any]:
        return {
            **super()._GetStrKwargs(),
            'id': self.id,
        }
