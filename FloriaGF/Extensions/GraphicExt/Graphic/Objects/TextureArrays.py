import typing as t

from FloriaGF.Graphic.Objects import Texture
from FloriaGF import Abc

if t.TYPE_CHECKING:
    from ..Animation import Animation


class TextureArrays:
    def __init__(self):
        self._storage: dict['Animation', Texture] = {}

    @t.overload
    def Register(self, animation: 'Animation', texture: Texture, /) -> Texture: ...

    @t.overload
    def Register(self, animation: 'Animation', window: Abc.Window, /) -> Texture: ...

    def Register(self, *args: 'Animation | Texture | Abc.Window') -> Texture:
        if self.Has(animation := t.cast('Animation', args[0])):
            raise RuntimeError()

        if isinstance(args[1], Texture):
            texture = args[1]
            if texture.type != 'texture_2d_array':
                raise RuntimeError()

        elif isinstance(args[1], Abc.Window):
            texture = Texture(
                args[1],
                'texture_2d_array',
            )
            with texture.Bind():
                texture.TexStorage3D(animation.GetFrames())

        else:
            raise RuntimeError()

        self._storage[animation] = texture

        return texture

    def Get(self, animation: 'Animation') -> t.Optional[Texture]:
        return self._storage.get(animation)

    def Has(self, animation: 'Animation') -> bool:
        return animation in self._storage

    @property
    def count(self) -> int:
        return len(self._storage)

    def __contains__(self, item: 'Animation'):
        return self.Has(item)

    def __len__(self):
        return self.count
