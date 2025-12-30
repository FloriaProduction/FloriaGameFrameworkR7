import typing as t

from OpenGL import GL as _GL
from contextlib import contextmanager, asynccontextmanager
import functools

from ... import Abc, Utils, Convert, Validator, GL
from ...Core import Core
from .Construct import ShaderConstuct, C

if t.TYPE_CHECKING:
    from ... import Assets, Types
    from ...Graphic.Objects.Texture import Texture


class BaseVertexShader(ShaderConstuct):
    pass


class ShaderProgram(Abc.Graphic.ShaderPrograms.ShaderProgram):
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

        self._uniform_cache: dict[str, t.Any] = {}
        self._uniform_ids_cache: dict[str, int] = {}
        self._uniform_block_ids_cache: dict[str, int] = {}

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        GL.ShaderProgram.Delete(self.id)

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

    # def CheckUniformCache(self, name: str, value: t.Any) -> bool:
    #     if name in self._uniform_cache and self._uniform_cache[name] == value:
    #         return True
    #     self._uniform_cache[name] = value
    #     return False

    def SetUniformFloat(self, name: str, value: float):
        _GL.glUniform1f(
            self.GetUniformLocation(name),
            value,
        )

    def SetUniformVector(self, name: str, value: tuple[float, ...]):
        count = len(value)
        loc = self.GetUniformLocation(name)

        if count == 2:
            _GL.glUniform2f(loc, *value)

        elif count == 3:
            _GL.glUniform3f(loc, *value)

        elif count == 4:
            _GL.glUniform4f(loc, *value)

        else:
            raise

    @contextmanager
    def Bind(self, *args: t.Any, **kwargs: t.Any):
        with GL.ShaderProgram.Bind(self.id):
            if (depth := self.depth) is not None:
                GL.Enable('depth')
                GL.DepthFunc(depth)
            else:
                GL.Disable('depth')

            if self.blend_equation is not None or self.blend_factors is not None:
                GL.Enable('blend')

                if self.blend_equation is not None:
                    GL.BlendEquation(self.blend_equation)

                if self.blend_factors is not None:
                    GL.BlendFactors(self.blend_factors)
            else:
                GL.Disable('blend')

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

    @property
    def depth(self) -> t.Optional['GL.hints.depth_func']:
        return self.__class__.__depth__

    @property
    def blend_equation(self) -> t.Optional['GL.hints.blend_equation']:
        return self.__class__.__blend_equation__

    @property
    def blend_factors(self) -> t.Optional[tuple['GL.hints.blend_factor', 'GL.hints.blend_factor']]:
        return self.__class__.__blend_factors__
