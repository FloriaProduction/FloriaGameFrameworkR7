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
from ..Stopwatch import Stopwatch


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
        vao_quad: t.Optional[VAO] = None,
        program_compose: t.Optional[Abc.ComposeShaderProgram] = None,
        projection: t.Optional[t.Union[ProjectionOrthographic, ProjectionPerspective]] = None,
        **kwargs: t.Any,
    ):
        super().__init__()

        self._window = window

        with self.window.Bind():
            self._vao: VAO = VAO.NewQuad(window) if vao_quad is None else vao_quad
            self._ubo = BO(window, 'uniform_buffer')

        self._compose_program: Abc.ComposeShaderProgram = Utils.CoalesceLazy(
            program_compose,
            lambda: ComposeShaderProgram(window),
        )
        self._fbo: t.Optional[FBO] = None
        self._batch_manager: BatchObjectManager = BatchObjectManager(self.window)

        self._position: Types.Vec3[float] = Types.Vec3[float].New(position)
        self._rotation: Types.Quaternion[float] = Types.Quaternion.New(rotation)

        self._resolution: Types.Vec2[int] = Types.Vec2(640, 360) if resolution is None else Types.Vec2[int].New(resolution)
        self._scale: float = 1

        self._display_mode: t.Optional[Types.hints.display_mode] = 'letterbox'

        self._projection_matrix_type: t.Optional[t.Literal['orthographic', 'perspective']] = None
        self._near: t.Optional[float] = 0.001
        self._far: t.Optional[float] = 1000
        # orthographic
        self._orthographic_size: t.Optional[Types.Vec2[float]] = None
        # perspective
        self._fov: t.Optional[float] = None

        self._instance_dtype: t.Optional[np.dtype] = None

        self._stopwatch_Render = Stopwatch()
        self._stopwatch_Draw = Stopwatch()
        self._stopwatch_Update = Stopwatch()

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
                    projection['fov'],
                    projection.get('near', 0.001),
                    projection.get('far', 1000),
                )
            else:
                raise ValueError()

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        self._batch_manager.Dispose()
        self._ubo.Dispose()
        if self._fbo is not None:
            self._fbo.Dispose()

    def Render(self, *args: t.Any, **kwargs: t.Any):
        '''
        Требует контекста OpenGL
        '''
        with self._stopwatch_Render:
            if self.request_intance_update:
                self.Update()

            if self._fbo is None or self._fbo.size != self.resolution:
                self._fbo = FBO(self.window, self.resolution)

            with self.fbo.Bind():
                GL.ClearColor((0, 0, 0, 0))
                GL.Clear('color', 'depth')

                with self._vao.Bind():
                    self.batch_manager.Draw(self)

    def Draw(self):
        with self._stopwatch_Draw:
            with self._vao.Bind():
                with self.compose_program.Bind(self.fbo):
                    GL.Draw.Arrays('triangle_fan', 4)

    def Update(self, *args: t.Any, **kwargs: t.Any):
        with self._stopwatch_Update:
            with self.ubo.Bind() as ubo:
                ubo.SetData(
                    np.array(
                        self.GetInstanceData(),
                        dtype=self.instance_dtype,
                    ),
                    'dynamic_draw',
                )

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
        if self._projection_matrix_type == 'orthographic':
            if self._orthographic_size is None:
                raise
            width, height = self._orthographic_size

            return pyrr.Matrix44(
                pyrr.matrix44.create_orthogonal_projection_matrix(
                    -width / 2,
                    width / 2,
                    -height / 2,
                    height / 2,
                    self.near,
                    self.far,
                    dtype=np.float32,
                )
            )

        else:
            return pyrr.Matrix44(
                pyrr.matrix44.create_perspective_projection(
                    self.fov,
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
        if value <= 0:
            raise
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

    def GetScale(self) -> float:
        return self._scale

    def SetScale(self, value: float):
        if value <= 0:
            raise
        self._scale = value

    @property
    def scale(self):
        return self.GetScale()

    @scale.setter
    def scale(self, value: float):
        self.SetScale(value)

    @property
    def instance_dtype(self):
        if self._instance_dtype is None:
            self._instance_dtype = self.GetInstanceDType()
        return self._instance_dtype
