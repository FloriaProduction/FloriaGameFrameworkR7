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

    @abstractmethod
    def GetPosition(self) -> Types.Vec3[float]: ...

    @abstractmethod
    def SetPosition(self, value: Types.hints.position_3d): ...

    @property
    def position(self):
        return self.GetPosition()

    @position.setter
    def position(self, value: Types.hints.position_3d):
        self.SetPosition(value)

    @abstractmethod
    def GetRotation(self) -> Types.Quaternion[float]: ...

    @abstractmethod
    def SetRotation(self, value: Types.hints.rotation): ...

    @property
    def rotation(self) -> 'Types.Quaternion[float]':
        return self.GetRotation()

    @rotation.setter
    def rotation(self, value: 'Types.hints.rotation'):
        self.SetRotation(value)

    @abstractmethod
    def GetScale(self) -> Types.Vec3[float]: ...

    @abstractmethod
    def SetScale(self, value: Types.hints.scale_3d): ...

    @property
    def scale(self):
        return self.GetScale()

    @scale.setter
    def scale(self, value: Types.hints.scale_3d):
        self.SetScale(value)

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
