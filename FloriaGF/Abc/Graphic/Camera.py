from abc import ABC, abstractmethod
import typing as t

from .. import Mixins
from ...InstanceAttributeManager import InstanceAttributeManager

if t.TYPE_CHECKING:
    from ... import Types
    from ..Graphic.Windows.Window import Window
    from ...Graphic.Objects.FBO import FBO
    from ...Graphic.Objects.BO import BO
    from ...Managers.BatchObjectManager import BatchObjectManager
    from .ShaderPrograms.ComposeShaderProgram import ComposeShaderProgram


class Camera(
    InstanceAttributeManager,
    Mixins.Disposable,
    Mixins.DrawRender,
    ABC,
):
    @abstractmethod
    def SetProjectionOrthographic(
        self,
        width: t.Optional[float] = None,
        height: t.Optional[float] = None,
        near: float = 0.001,
        far: float = 1000,
    ):
        """Изменить проекцию камеры на ортогональную.

        Args:
            width (float, optional): Ширина камеры в единицах измерения. Defaults to None.
            height (float, optional): Высота камеры в единицах измерения. Defaults to None.
            near (float, optional): Минимальное расстояние в единицах измерения. Defaults to 0.001.
            far (float, optional): Максимальное расстояние в единицах измерения. Defaults to 1000.
        """

    @abstractmethod
    def SetProjectionPerspective(
        self,
        fov: float,
        near: float = 0.001,
        far: float = 1000,
    ):
        """Изменить проекцию камеры на перспективную.

        Args:
            fov (float): Угол обзора в градусах, от 0 до 180 `не включительно`.
            near (float, optional): Минимальное расстояние в единицах измерения. Defaults to 0.001.
            far (float, optional): Максимальное расстояние в единицах измерения. Defaults to 1000.
        """

    @t.overload
    @abstractmethod
    def LookAt(
        self,
        target: 'Types.hints.position_3d',
        /,
    ) -> None: ...
    @t.overload
    @abstractmethod
    def LookAt(
        self,
        target: 'Types.hints.position_3d',
        up: 'Types.hints.position_3d',
        /,
    ) -> None: ...

    @property
    @abstractmethod
    def ubo(self) -> 'BO': ...

    @property
    @abstractmethod
    def resolution(self) -> 'Types.Vec2[int]': ...
    @resolution.setter
    @abstractmethod
    def resolution(self, value: 'tuple[int, int] | Types.Vec2[int]'): ...

    @property
    @abstractmethod
    def position(self) -> 'Types.Vec3[float]': ...
    @position.setter
    @abstractmethod
    def position(
        self,
        value: 'Types.hints.position_3d',
    ): ...

    @property
    @abstractmethod
    def rotation(self) -> 'Types.Quaternion[float]': ...
    @rotation.setter
    @abstractmethod
    def rotation(
        self,
        value: 'Types.hints.rotation',
    ): ...

    @property
    @abstractmethod
    def window(self) -> 'Window': ...

    @property
    @abstractmethod
    def fbo(self) -> 'FBO': ...

    @property
    @abstractmethod
    def batch_manager(self) -> 'BatchObjectManager': ...

    @property
    @abstractmethod
    def compose_program(self) -> 'ComposeShaderProgram': ...

    @property
    def aspect(self) -> float:
        """Соотношение сторон разрешения."""
        return self.resolution[0] / self.resolution[1]
