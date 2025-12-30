import typing as t
from OpenGL import GL
from PIL import Image
from FloriaGF.Graphic.Objects import Texture
from FloriaGF import Abc


class TextureArrays:
    def __init__(self):
        self._storage: dict[str, Texture] = {}

    @t.overload
    def Register(self, name: str, texture: Texture, /) -> Texture: ...

    @t.overload
    def Register(self, name: str, layers: t.Sequence[Image.Image], window: Abc.Window, /) -> Texture: ...

    def Register(self, *args: str | Texture | t.Sequence[Image.Image] | Abc.Window) -> Texture:
        name = t.cast(str, args[0])
        if name in self._storage:
            raise RuntimeError()

        if isinstance(args[1], Texture):
            texture = args[1]

        elif isinstance(args[1], t.Sequence):
            layers = t.cast(t.Sequence[Image.Image], args[1])
            window = t.cast(Abc.Window, args[2])

            texture = Texture(
                window,
                'texture_2d_array',
            )
            with texture.Bind():
                texture.TexStorage3D(layers)

        else:
            raise RuntimeError()

        if texture.type != 'texture_2d_array':
            raise RuntimeError()

        self._storage[name] = texture

        return texture

    def Get(self, name: str) -> t.Optional[Texture]:
        return self._storage.get(name)

    def Has(self, name: str) -> bool:
        return name in self._storage

    @property
    def count(self) -> int:
        return len(self._storage)

    def __contains__(self, item: str):
        return self.Has(item)

    def __len__(self):
        return self.count
