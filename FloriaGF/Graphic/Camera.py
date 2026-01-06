import typing as t

import pyrr
import numpy as np

from .. import Abc, Types, Utils, GL
from ..Config import Config
from .Objects.BO import BO
from .Objects.FBO import FBO
from .Objects.VAO import VAO
from ..Managers.BatchObjectManager import BatchObjectManager
from .ShaderPrograms.ComposeShaderProgram import ComposeShaderProgram
from ..Stopwatch import stopwatch


class Projection(t.TypedDict):
    type: t.Literal['orthographic', 'perspective']
    near: t.NotRequired[float]
    far: t.NotRequired[float]


class ProjectionOrthographic(Projection):
    width: t.NotRequired[int]
    height: t.NotRequired[int]


class ProjectionPerspective(Projection):
    fov: float


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
        resolution: t.Optional[tuple[int, int] | Types.Vec2[int]] = None,
        viewport_mode: t.Optional[Types.hints.viewport_mode] = None,
        projection: t.Optional[t.Union[ProjectionOrthographic, ProjectionPerspective]] = None,
        scale: t.Optional[float] = None,
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

        self._position: Types.Vec3[float] = Types.Vec3[float].New(position)
        self._rotation: Types.Quaternion[float] = Types.Quaternion.New(rotation)

        self._resolution: Types.Vec2[int] = Types.Vec2(640, 360) if resolution is None else Types.Vec2[int].New(resolution)
        self._scale: float = 1 if scale is None else scale

        self._projection_matrix_type: t.Optional[t.Literal['orthographic', 'perspective']] = None
        self._near: t.Optional[float] = 0.001
        self._far: t.Optional[float] = 1000
        # orthographic
        self._orthographic_size: t.Optional[Types.Vec2[float]] = None
        # perspective
        self._fov: t.Optional[float] = None

        self._instance_dtype: t.Optional[np.dtype] = None

        self._viewport_mode: Types.hints.viewport_mode = 'stretch' if viewport_mode is None else viewport_mode

        if projection is not None:
            if projection['type'] == 'orthographic':
                self.SetProjectionOrthographic(
                    projection.get('width'),
                    projection.get('height'),
                    projection.get('near', 0.001),
                    projection.get('far', 1000),
                )
            elif projection['type'] == 'perspective':
                self.SetProjectionPerspective(
                    projection.get('fov', 60),
                    projection.get('near', 0.001),
                    projection.get('far', 1000),
                )
            else:
                raise ValueError()

        else:
            self.SetProjectionOrthographic()

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
                    self.GetInstanceData(),
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
            base_aspect = resolution.width / resolution.height
            window_aspect = window_size.width / window_size.height

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
        near: float = 0.001,
        far: float = 1000,
    ):
        self._projection_matrix_type = 'orthographic'
        self._orthographic_size = Types.Vec2[float](
            Config.PIX_scale * self.resolution.width if width is None else width,
            Config.PIX_scale * self.resolution.height if height is None else height,
        )
        self.near = near
        self.far = far

        self._UpdateInstanceAttributes('projection')

    def SetProjectionPerspective(
        self,
        fov: float,
        near: float = 0.001,
        far: float = 1000,
    ):
        self._projection_matrix_type = 'perspective'
        self.fov = fov
        self.near = near
        self.far = far

        self._UpdateInstanceAttributes('projection')

    def GetProjectionMatrix(self) -> pyrr.Matrix44:
        scale = max(0.000001, self.scale)  # max 1 000 000 scale

        if self._projection_matrix_type == 'orthographic':
            if self._orthographic_size is None:
                raise
            width, height = self._orthographic_size

            return pyrr.Matrix44(
                pyrr.matrix44.create_orthogonal_projection_matrix(
                    -width / 2 / scale,
                    width / 2 / scale,
                    -height / 2 / scale,
                    height / 2 / scale,
                    self.near,
                    self.far,
                    dtype=np.float32,
                )
            )

        else:
            return pyrr.Matrix44(
                pyrr.matrix44.create_perspective_projection(
                    self.fov / scale,
                    self.aspect,
                    self.near,
                    self.far,
                    dtype=np.float32,
                )
            )

    def GetViewMatrix(self) -> pyrr.Matrix44:
        return pyrr.Matrix44(
            pyrr.matrix44.create_look_at(
                self.position,
                self.position + pyrr.quaternion.apply_to_vector(self.rotation, (0.0, 0.0, -1.0)),
                pyrr.quaternion.apply_to_vector(self.rotation, (0.0, 1.0, 0.0)),
                dtype=np.float32,
            )
        )

    def _GetIntanceAttributeItems(self) -> tuple[Abc.Graphic.ShaderPrograms.SchemeItem[Camera.ATTRIBS], ...]:
        return (
            {
                'attrib': 'projection',
                'type': 'mat4',
            },
            {
                'attrib': 'view',
                'type': 'mat4',
            },
            {
                'attrib': 'resolution',
                'type': 'vec2',
            },
        )

    def _GetInstanceAttribute(self, attrib: Camera.ATTRIBS | str) -> t.Any:
        if attrib == 'projection':
            return self.GetProjectionMatrix()

        elif attrib == 'view':
            return self.GetViewMatrix()

        elif attrib == 'resolution':
            return self.resolution

        raise

    def _GetInstanceAttributeCache(self, attrib: Camera.ATTRIBS | str) -> t.Optional[t.Any]:
        return super()._GetInstanceAttributeCache(attrib)

    def _UpdateInstanceAttributes(self, *fields: Camera.ATTRIBS | str, all: bool = False):
        return super()._UpdateInstanceAttributes(*fields, all=all)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: Types.hints.position_3d):
        self._position = Types.Vec3[float].New(value)
        self._UpdateInstanceAttributes('view')

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value: Types.hints.rotation):
        self._rotation = Types.Quaternion[float].New(value)
        self._UpdateInstanceAttributes('view')

    def LookAt(
        self,
        target: Types.hints.position_3d,
        up: Types.hints.position_3d = Types.Vec3(0.0, 1.0, 0.0),
    ):
        if not isinstance(target, Types.Vec3):
            target = Types.Vec3[float].New(target)

        if self.position == target:
            return

        if not isinstance(up, Types.Vec3):
            up = Types.Vec3[float].New(up)

        self.rotation = pyrr.Quaternion(
            pyrr.quaternion.create_from_matrix(pyrr.matrix44.create_look_at(self.position, target, up, dtype=np.float32))
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
    def resolution(self):
        return self.GetResolution()

    @resolution.setter
    def resolution(self, value: Types.hints.size_2d):
        self.SetResolution(value)

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

    @property
    def near(self):
        return self.GetNear()

    @near.setter
    def near(self, value: float):
        self.SetNear(value)

    def GetFar(self) -> float:
        if self._far is None:
            raise
        return self._far

    def SetFar(self, value: float):
        if value <= self.near:
            raise
        self._far = value

    @property
    def far(self):
        return self.GetFar()

    @far.setter
    def far(self, value: float):
        self.SetFar(value)

    def GetFov(self) -> float:
        if self._fov is None:
            raise
        return self._fov

    def SetFov(self, value: float):
        if 0 > value >= 180:
            raise ValueError()
        self._fov = value

    @property
    def fov(self):
        return self.GetFar()

    @fov.setter
    def fov(self, value: float):
        self.SetFov(value)

    @property
    def instance_dtype(self):
        if self._instance_dtype is None:
            self._instance_dtype = self.GetInstanceDType()
        return self._instance_dtype

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
