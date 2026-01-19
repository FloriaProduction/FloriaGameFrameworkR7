import typing as t

from OpenGL import GL as _GL
from contextlib import contextmanager
import functools
import numpy as np

from ... import Abc, Utils, Convert, Validator, GL
from ..Objects.BO import BO
from .Construct import ShaderConstuct, Components as C
from ...AsyncEvent import AsyncEvent
from ...Stopwatch import stopwatch


class ShaderProgram(
    Abc.Graphic.ShaderPrograms.ShaderProgram,
):
    __vertex__: t.Optional[str | t.Type[ShaderConstuct]] = None

    __fragment__: t.Optional[str | t.Type[ShaderConstuct]] = None

    __scheme__: t.Optional[Abc.Graphic.ShaderPrograms.Scheme] = None

    __depth__: t.Optional['GL.hints.depth_func'] = None
    __blend_equation__: t.Optional['GL.hints.blend_equation'] = None
    __blend_factors__: t.Optional[tuple['GL.hints.blend_factor', 'GL.hints.blend_factor']] = None

    def __init__(
        self,
        window: Abc.Window,
        name: t.Optional[str] = None,
    ):
        self._window = window

        with self.window.Bind():
            self._id: int = GL.ShaderProgram.Create()
            self._name: t.Optional[str] = name

            vertex_id = GL.Shader.Create('vertex', self._GetVertexSource())
            fragment_id = GL.Shader.Create('fragment', self._GetFragmentSource())

            GL.ShaderProgram.Attach(
                self.id,
                vertex_id,
                fragment_id,
            )

            try:
                GL.ShaderProgram.Link(self.id)
                GL.ShaderProgram.Validate(self.id)

            finally:
                GL.Shader.Delete(
                    vertex_id,
                    fragment_id,
                )

        self._uniform_ids_cache: dict[str, int] = {}
        self._uniform_block_ids_cache: dict[str, int] = {}
        self._uniform_buffer_objects: dict[str, BO] = {}

        self._on_dispose = AsyncEvent[Abc.ShaderProgram]()

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        GL.ShaderProgram.Delete(self.id)
        for ubo in self._uniform_buffer_objects.values():
            ubo.Dispose()
        self._uniform_buffer_objects.clear()

    @classmethod
    @functools.lru_cache(1)
    def _GetVertexSource(cls) -> str:
        vertex = Validator.NotNone(
            t.cast(
                t.Optional[str | t.Type[ShaderConstuct]],
                Utils.GetClassAttrib(cls, '__vertex__'),
            ),
        )

        return vertex if isinstance(vertex, str) else vertex.GetSource()

    @classmethod
    @functools.lru_cache(1)
    def _GetFragmentSource(cls) -> str:
        fragment = Validator.NotNone(
            t.cast(
                t.Optional[str | t.Type[ShaderConstuct]],
                Utils.GetClassAttrib(cls, '__fragment__'),
            ),
        )

        return fragment if isinstance(fragment, str) else fragment.GetSource()

    @classmethod
    @functools.lru_cache(1)
    def _GetScheme(cls) -> Abc.Graphic.ShaderPrograms.Scheme:
        scheme: t.Optional[Abc.Graphic.ShaderPrograms.Scheme] = None
        if (
            vertex := t.cast(
                t.Optional[str | t.Type[ShaderConstuct]],
                Utils.GetClassAttrib(cls, '__vertex__'),
            )
        ) is None or isinstance(vertex, str):
            scheme = t.cast(
                t.Optional[Abc.Graphic.ShaderPrograms.Scheme],
                Utils.GetClassAttrib(cls, '__scheme__'),
            )

        else:
            scheme = vertex.GetScheme()

        return Validator.NotNone(scheme)

    def GetUniformLocation(self, name: str) -> int:
        if (loc := self._uniform_ids_cache.get(name)) is None:
            if (loc := GL.ShaderProgram.GetUniformLocation(self.id, name)) < 0:
                raise
            self._uniform_ids_cache[name] = loc
        return loc

    def GetUniformBlockLocation(self, name: str) -> int:
        if (loc := self._uniform_block_ids_cache.get(name)) is None:
            self._uniform_block_ids_cache[name] = loc = GL.ShaderProgram.GetUniformBlockIndex(self.id, name)
        return loc

    @stopwatch
    def BindUniformBlock(
        self,
        block_name: str,
        data: dict[str, t.Any],
        struct_name: t.Optional[str] = None,
    ):
        if struct_name is None:
            struct_name = block_name

        np_data = np.array(
            tuple(data[field['name']] for field in self.GetStruct(struct_name)),
            dtype=self.GetStructDType(struct_name),
        )

        if (ubo := self._uniform_buffer_objects.get(block_name)) is None:
            ubo = BO(self.window, 'uniform_buffer')
            with ubo.Bind():
                ubo.SetData(np_data, 'dynamic_draw')

            self._uniform_buffer_objects[block_name] = ubo

        else:
            with ubo.Bind():
                ubo.SetSubData(0, np_data)

        _GL.glBindBufferBase(
            _GL.GL_UNIFORM_BUFFER,
            self.GetUniformBlockLocation(block_name),
            ubo.id,
        )

    def SetUniformFloat(self, name: str, value: float):
        _GL.glUniform1f(
            self.GetUniformLocation(name),
            value,
        )

    def SetUniformVector(
        self,
        name: str,
        value: t.Union[
            tuple[float, float],
            tuple[float, float, float],
            tuple[float, float, float, float],
        ],
    ):
        loc = self.GetUniformLocation(name)

        if (count := len(value)) == 2:
            _GL.glUniform2f(loc, *value)

        elif count == 3:
            _GL.glUniform3f(loc, *value)

        elif count == 3:
            _GL.glUniform4f(loc, *value)

        else:
            raise

    @contextmanager
    def Bind(self, *args: t.Any, **kwargs: t.Any):
        with GL.ShaderProgram.Bind(self.id):
            glfw_window = self.window.glfw_window

            if (depth := self.__depth__) is not None:
                GL.Enable(glfw_window, 'depth')
                GL.DepthFunc(depth)
            else:
                GL.Disable(glfw_window, 'depth')

            if self.__blend_equation__ is not None or self.__blend_factors__ is not None:
                GL.Enable(glfw_window, 'blend')

                if self.__blend_equation__ is not None:
                    GL.BlendEquation(self.__blend_equation__)

                if self.__blend_factors__ is not None:
                    GL.BlendFactors(self.__blend_factors__)
            else:
                GL.Disable(glfw_window, 'blend')

            yield self

    def GetID(self):
        return self._id

    def GetName(self):
        return self._name

    @property
    def window(self):
        return self._window

    @property
    def scheme(self):
        return self._GetScheme()

    @classmethod
    def GetStruct(cls, name: str) -> tuple[Abc.Graphic.ShaderPrograms.SchemeItem, ...]:
        raise ValueError()

    @classmethod
    @functools.lru_cache(10)
    def GetStructDType(cls, name: str) -> np.dtype:
        return np.dtype(
            [
                (
                    item['name'],
                    *GL.Convert.GLSLTypeToNumpy(item['type']),
                )
                for item in cls.GetStruct(name)
            ]
        )

    @property
    def on_dispose(self) -> AsyncEvent[Abc.ShaderProgram]:
        return self._on_dispose
