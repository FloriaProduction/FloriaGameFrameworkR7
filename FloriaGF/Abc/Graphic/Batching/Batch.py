from abc import ABC, abstractmethod
import typing as t

from ... import Mixins
from ...Managers.Manager import Manager

if t.TYPE_CHECKING:
    from uuid import UUID

    from ..Windows.Window import Window
    from .InstanceObject import InstanceObject
    from ..ShaderPrograms.ComposeShaderProgram import ComposeShaderProgram
    from ....Graphic.Objects.FBO import FBO
    from ..Materials.Material import Material
    from ..Camera import Camera


class Batch(
    Manager['InstanceObject'],
    Mixins.ID['UUID'],
    Mixins.Nameable[t.Optional[str]],
    Mixins.DrawRender,
    ABC,
):
    __slots__ = ()

    @abstractmethod
    def Register[TItem: 'InstanceObject'](self, item: TItem) -> TItem: ...

    @t.overload
    def Remove[TItem: 'InstanceObject'](self, item: TItem, /) -> TItem: ...
    @t.overload
    def Remove[TItem: 'InstanceObject', TDefault: t.Any](self, item: TItem, default: TDefault, /) -> TItem | TDefault: ...
    @abstractmethod
    def Remove(self, *args: t.Any) -> t.Any: ...

    @abstractmethod
    def Render(self, camera: 'Camera', *args: t.Any, **kwargs: t.Any): ...

    @abstractmethod
    def Draw(self, *args: t.Any, **kwargs: t.Any): ...

    @abstractmethod
    def UpdateObject[TObj: InstanceObject](self, obj: TObj) -> TObj: ...

    @abstractmethod
    def UpdateMaterial(self, material: 'Material'): ...

    @property
    @abstractmethod
    def window(self) -> 'Window': ...

    @property
    @abstractmethod
    def index(self) -> int: ...

    @property
    @abstractmethod
    def program_compose(self) -> 'ComposeShaderProgram': ...

    @property
    @abstractmethod
    def fbo(self) -> 'FBO': ...
