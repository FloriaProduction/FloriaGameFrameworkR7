import typing as t

import glm
import numpy as np

from .. import Abc, Types, Utils, GL
from ..Config import Config
from .Objects.BO import BO
from .Objects.FBO import FBO
from .Objects.VAO import VAO
from ..Managers.BatchObjectManager import BatchObjectManager
from .ShaderPrograms.ComposeShaderProgram import ComposeShaderProgram
from ..Stopwatch import stopwatch
from ..InterpolationField import InterpolationField


class Projection(t.TypedDict):
    near: t.NotRequired[float]
    '''Ближняя граница в единицах измерения.'''
    far: t.NotRequired[float]
    '''Дальная граница в единицах измерения.'''


class ProjectionOrthographic(Projection):
    width: t.NotRequired[float]
    '''Ширина в единицах измерения.'''
    height: t.NotRequired[float]
    '''Высота в единицах измерения.'''


class ProjectionPerspective(Projection):
    fov: float
    '''Поле зрения в градусах, должно быть между `0 и 180 не включительно`'''


class Camera(
    Abc.Graphic.Camera,
):
    ATTRIBS = t.Union[
        t.Literal[
            'projection',
            'view',
            'resolution',
        ],
    ]

    def __init__(
        self,
        window: Abc.Window,
        position: Types.hints.position_3d = (0, 0, 0),
        rotation: Types.hints.rotation = (0, 0, 0),
        *,
        resolution: Types.hints.size_2d = (640, 360),
        viewport_mode: Types.hints.viewport_mode = 'letterbox',
        projection_orthographic: t.Optional[ProjectionOrthographic] = None,
        projection_perspective: t.Optional[ProjectionPerspective] = None,
        near: float = 0.0001,
        far: float = 10000,
        scale: float = 1,
        program_compose: t.Optional[Abc.ComposeShaderProgram] = None,
        vao_quad: t.Optional[VAO] = None,
        **kwargs: t.Any,
    ):
        super().__init__()

        self._window = window

        with self.window.Bind():
            self._vao: VAO = VAO.NewQuad(window) if vao_quad is None else vao_quad
            self._ubo = BO(window, 'uniform_buffer')

        self._compose_program: Abc.ComposeShaderProgram = (
            ComposeShaderProgram(window) if program_compose is None else program_compose
        )
        self._fbo: t.Optional[FBO] = None
        self._batch_manager: BatchObjectManager = BatchObjectManager(self.window)

        self._interp_position = InterpolationField(
            Types.Vec3[float].New(position),
            lambda prev, next, progress: Types.Vec3[float].New(Utils.SmoothIter(prev, next, progress)),
            lambda value: self._UpdateInstanceAttributes('view'),
            self.window.on_simulate,
        )

        self._interp_rotation = InterpolationField(
            Types.Quaternion[float].New(rotation),
            lambda prev, next, progress: Types.Quaternion[float].New(Utils.Slerp(prev, next, progress)),
            lambda value: self._UpdateInstanceAttributes('view'),
            self.window.on_simulate,
        )

        self._viewport_mode: Types.hints.viewport_mode = viewport_mode
        self._resolution: Types.Vec2[int] = Types.Vec2[int].New(resolution)
        self._scale: float = scale

        # projections
        self._projection_matrix_type: t.Optional[t.Literal['orthographic', 'perspective']] = None
        self._near: t.Optional[float] = near
        self._far: t.Optional[float] = far
        # orthographic
        self._orthographic_size: t.Optional[Types.Vec2[float]] = None
        # perspective
        self._fov: t.Optional[float] = None

        self._instance_dtype_cache: t.Optional[np.dtype] = None

        if projection_orthographic is None and projection_perspective is None:
            self.SetProjectionOrthographic()

        elif projection_orthographic is not None and projection_perspective is not None:
            raise ValueError()

        elif projection_orthographic is not None:
            self.SetProjectionOrthographic(
                projection_orthographic.get('width'),
                projection_orthographic.get('height'),
                projection_orthographic.get('near', 0.001),
                projection_orthographic.get('far', 1000),
            )

        elif projection_perspective is not None:
            self.SetProjectionPerspective(
                projection_perspective['fov'],
                projection_perspective.get('near', 0.001),
                projection_perspective.get('far', 1000),
            )

        else:
            raise RuntimeError('Как?')

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        self._batch_manager.Dispose()
        self._ubo.Dispose()
        if self._fbo is not None:
            self._fbo.Dispose()

    @stopwatch
    def Update(self, *args: t.Any, **kwargs: t.Any):
        with self.ubo.Bind() as ubo:
            ubo.SetData(
                np.array(
                    tuple(self.GetInstanceData().values()),
                    dtype=self.instance_dtype,
                ),
                'dynamic_draw',
            )

    def UpdateViewport(self, *args: t.Any, **kwargs: t.Any):
        window_size = self.window.size
        resolution = self.resolution

        if self.viewport_mode == 'stretch':
            GL.Viewport((0, 0), window_size)

        elif self.viewport_mode == 'letterbox':
            base_aspect = 1 if 0 in resolution else resolution.width / resolution.height
            window_aspect = 1 if 0 in window_size else window_size.width / window_size.height

            if window_aspect > base_aspect:
                viewport_height = window_size.height
                viewport_width = int(viewport_height * base_aspect)
                offset_x = (window_size.width - viewport_width) // 2
                offset_y = 0
            else:
                viewport_width = window_size.width
                viewport_height = int(viewport_width / base_aspect)
                offset_x = 0
                offset_y = (window_size.height - viewport_height) // 2

            GL.Viewport((offset_x, offset_y), (viewport_width, viewport_height))

        elif self.viewport_mode == 'pixel_perfect':
            max_scale_x = window_size.width // resolution.width
            max_scale_y = window_size.height // resolution.height

            scale = min(max_scale_x, max_scale_y)

            if scale < 1:
                scale = 1

            viewport_width = resolution.width * scale
            viewport_height = resolution.height * scale

            if viewport_width > window_size.width:
                viewport_width = window_size.width
            if viewport_height > window_size.height:
                viewport_height = window_size.height

            offset_x = max(0, (window_size.width - viewport_width) // 2)
            offset_y = max(0, (window_size.height - viewport_height) // 2)

            GL.Viewport((offset_x, offset_y), (viewport_width, viewport_height))

        else:
            raise

    @stopwatch
    def Render(self, *args: t.Any, **kwargs: t.Any):
        if self.request_intance_update:
            self.Update()

        if self._fbo is None or self._fbo.size != self.resolution:
            self._fbo = FBO(self.window, self.resolution)

        with self.fbo.Bind():
            GL.ClearColor(self.window.background_color)
            GL.Clear('color', 'depth')

            with self._vao.Bind():
                self.batch_manager.Draw(self)

    @stopwatch
    def Draw(self):
        GL.ClearColor((0, 0, 0, 0))
        GL.Clear('color', 'depth')

        self.UpdateViewport()

        with self._vao.Bind():
            with self.compose_program.Bind(self.fbo):
                GL.Draw.Arrays('triangle_fan', 4)

    def SetProjectionOrthographic(
        self,
        width: t.Optional[float] = None,
        height: t.Optional[float] = None,
        near: t.Optional[float] = None,
        far: t.Optional[float] = None,
    ):
        self._projection_matrix_type = 'orthographic'
        self._orthographic_size = Types.Vec2[float](
            self.resolution.width * Config.PIX_scale if width is None else width,
            self.resolution.height * Config.PIX_scale if height is None else height,
        )
        if near is not None:
            self.near = near
        if far is not None:
            self.far = far

        self._UpdateInstanceAttributes('projection')

    def SetProjectionPerspective(
        self,
        fov: float,
        near: t.Optional[float] = None,
        far: t.Optional[float] = None,
    ):
        self._projection_matrix_type = 'perspective'
        self._fov = fov
        if near is not None:
            self.near = near
        if far is not None:
            self.far = far

        self._UpdateInstanceAttributes('projection')

    def _GetProjectionMatrix(self) -> tuple[
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
    ]:
        scale = max(0.000001, self.scale)  # max 1 000 000 scale

        if self._projection_matrix_type == 'orthographic':
            if self._orthographic_size is None:
                raise
            width, height = self._orthographic_size

            left = -width / 2 / scale
            right = width / 2 / scale
            bottom = -height / 2 / scale
            top = height / 2 / scale

            return glm.ortho(
                left,
                right,
                bottom,
                top,
                self.near,
                self.far,
            ).to_tuple()

        else:
            return glm.perspective(
                glm.radians(self.fov / scale),
                self.aspect,
                self.near,
                self.far,
            ).to_tuple()

    def _GetViewMatrix(self) -> tuple[
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
    ]:
        return glm.lookAt(
            self.position,
            glm.vec3(*self.position) + (rotation_glm := glm.quat(*self.rotation)) * (0.0, 0.0, -1.0),
            rotation_glm * (0.0, 1.0, 0.0),
        ).to_tuple()

    def GetIntanceAttributeItems(self) -> tuple[Abc.Graphic.ShaderPrograms.SchemeItem[Camera.ATTRIBS], ...]:
        return (
            {
                'name': 'projection',
                'type': 'mat4',
            },
            {
                'name': 'view',
                'type': 'mat4',
            },
            {
                'name': 'resolution',
                'type': 'vec2',
            },
        )

    def _GetInstanceAttribute(self, name: Camera.ATTRIBS | str) -> t.Any:
        if name == 'projection':
            return self._GetProjectionMatrix()

        elif name == 'view':
            return self._GetViewMatrix()

        elif name == 'resolution':
            return self.resolution

        raise

    def GetPosition(self) -> 'Types.Vec3[float]':
        return self._interp_position.GetValue()

    def SetPosition(self, value: 'Types.hints.position_3d', flash: bool = True):
        self._interp_position.SetValue(Types.Vec3[float].New(value), flash)
        self._UpdateInstanceAttributes('view')

    @property
    def position(self):
        return self.GetPosition()

    @position.setter
    def position(self, value: 'Types.hints.position_3d'):
        self.SetPosition(value, False)

    def GetRotation(self) -> Types.Quaternion[float]:
        return self._interp_rotation.GetValue()

    def SetRotation(self, value: Types.hints.rotation, flash: bool = True):
        self._interp_rotation.SetValue(Types.Quaternion[float].New(value), flash)
        self._UpdateInstanceAttributes('view')

    @property
    def rotation(self):
        return self.GetRotation()

    @rotation.setter
    def rotation(self, value: 'Types.hints.rotation'):
        self.SetRotation(value, False)

    def LookAt(
        self,
        target: Types.hints.position_3d,
        up: Types.hints.position_3d = (0.0, 1.0, 0.0),
    ):
        self.rotation = Types.Quaternion[float].New(
            glm.quat_cast(
                glm.lookAt(
                    glm.vec3(*self.position),
                    glm.vec3(*target),
                    glm.vec3(*up),
                )
            )
        )

    @property
    def ubo(self):
        return self._ubo

    def GetResolution(self):
        return self._resolution

    def SetResolution(self, value: Types.hints.size_2d):
        self._resolution = Types.Vec2(*value)
        self._UpdateInstanceAttributes('resolution', 'projection')

    @property
    def window(self):
        return self._window

    @property
    def fbo(self):
        if self._fbo is None:
            raise RuntimeError()
        return self._fbo

    @property
    def batch_manager(self):
        return self._batch_manager

    @property
    def compose_program(self):
        return self._compose_program

    def GetNear(self) -> float:
        if self._near is None:
            raise
        return self._near

    def SetNear(self, value: float):
        self._near = value

    def GetFar(self) -> float:
        if self._far is None:
            raise
        return self._far

    def SetFar(self, value: float):
        if value <= self.near:
            raise
        self._far = value

    def GetFov(self) -> float:
        if self._fov is None:
            raise
        return self._fov

    @property
    def instance_dtype(self):
        if self._instance_dtype_cache is None:
            self._instance_dtype_cache = self.GetInstanceDType()
        return self._instance_dtype_cache

    def GetViewportMode(self) -> Types.hints.viewport_mode:
        return self._viewport_mode

    def SetViewportMode(self, value: Types.hints.viewport_mode):
        self._viewport_mode = value

    def GetScale(self) -> float:
        return self._scale

    def SetScale(self, value: float):
        if value <= 0:
            raise
        self._scale = value
        self._UpdateInstanceAttributes('projection')

    if t.TYPE_CHECKING:

        def _GetInstanceAttributeCache(self, name: Camera.ATTRIBS | str) -> t.Optional[t.Any]: ...

        def _UpdateInstanceAttributes(self, *names: Camera.ATTRIBS | str, all: bool = False): ...
