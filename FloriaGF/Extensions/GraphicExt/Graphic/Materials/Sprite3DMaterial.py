import typing as t
import PIL.Image
from time import perf_counter
from uuid import UUID
from OpenGL import GL
from contextlib import contextmanager

from FloriaGF import Abc, Core, Utils
from FloriaGF.Graphic.Objects.Texture import Texture
from FloriaGF.Graphic.Materials.Material import Material

from ..ShaderPrograms.Sprite3DShaderProgram import Sprite3DShaderProgram
from ..Objects.TextureArrays import TextureArrays


if t.TYPE_CHECKING:
    from ..Animation import Animation


class Sprite3DMaterial(Material[Sprite3DShaderProgram]):
    PROGRAM_NAME = 'sprite-3d-program'

    # Window.id: TextureArrays
    _texture_arrays: dict[UUID, TextureArrays] = {}

    __slots__ = ('_animation',)

    @classmethod
    def New(
        cls,
        window: Abc.Window,
        animation: t.Optional['Animation'] = None,
        name: t.Optional[str] = None,
    ):
        program = window.shader_manager.sequence.OfType(Sprite3DShaderProgram).GetByNameOrDefaultLazy(
            cls.PROGRAM_NAME,
            lambda: window.shader_manager.Register(Sprite3DShaderProgram(window, cls.PROGRAM_NAME)),
        )

        return Sprite3DMaterial(
            program,
            animation,
            name,
        )

    def __init__(
        self,
        program: Sprite3DShaderProgram,
        animation: t.Optional['Animation'] = None,
        name: t.Optional[str] = None,
    ):
        super().__init__(program, name)

        self._animation: t.Optional['Animation'] = animation

    class Modify_Kwargs(
        Material.Modify_Kwargs,
        total=False,
    ):
        animation: t.Optional['Animation']

    def Modify(self, **kwargs: t.Unpack[Modify_Kwargs]):
        return self.__class__(
            self.program,
            kwargs.get('animation', self.animation),
            kwargs.get('name', self.name),
        )

    @classmethod
    def _GetTexture(cls, window: Abc.Window, animation: 'Animation') -> Texture:
        if (texture_arrays := cls._texture_arrays.get(window.id)) is None:
            texture_arrays = TextureArrays()
            cls._texture_arrays[window.id] = texture_arrays

            @window.on_closed.Register
            def _(window: Abc.Window):
                cls._texture_arrays.pop(window.id, None)

        if (texture := texture_arrays.Get(animation.name)) is None:
            texture = texture_arrays.Register(animation.name, animation.GetFrames(), window)

        return texture

    @property
    def texture(self) -> t.Optional[Texture]:
        if self._animation is None:
            return None
        return self._GetTexture(self.program.window, self._animation)

    @property
    def animation(self):
        return self._animation

    @contextmanager
    def Bind(self, camera: Abc.Camera, *args: t.Any, **kwargs: t.Any):
        with self.program.Bind(camera):
            with texture.Bind() if (texture := self.texture) is not None else Utils.EmptyBind():
                yield self

    def GetSignature(self):
        return hash(
            (
                super().GetSignature(),
                None if self.animation is None else self.animation.GetSignature(),
            )
        )
