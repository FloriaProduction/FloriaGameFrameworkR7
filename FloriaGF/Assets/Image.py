from pathlib import Path
import typing as t
import PIL.Image
import asyncio
import numpy as np

from .. import Abc, Types, Validator, Convert
from .Asset import Asset
from ..Graphic.Objects.Texture import Texture


class Image(Asset):
    __slots__ = ('image', '_texture')

    def __init__(
        self,
        path: t.Optional[str | Path] = None,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        super().__init__(path, *args, **kwargs)

        self.image: t.Optional[PIL.Image.Image] = None
        self._texture: t.Optional[Texture] = None

    @classmethod
    async def Load(cls, path: str | Path) -> 'Image':
        asset = Image(path)

        asset.image = await asyncio.to_thread(PIL.Image.open, path)

        return asset

    @classmethod
    async def Create(cls, image: PIL.Image.Image, *args: t.Any, **kwargs: t.Any) -> 'Image':
        asset = Image(None)

        asset.image = image

        return asset

    async def Save(self, path: t.Optional[str | Path] = None) -> t.Self:
        if path is not None:
            path = self.path = Convert.ToPath(path)
        else:
            path = self.path

        Validator.NotNone(self.image).save(Validator.NotNone(path))

        return self

    def CreateTexture(self, window: Abc.Window) -> Texture:
        if self._texture is None:
            with window.Bind():
                self._texture = Texture(window, 'texture_2d')
                with self._texture.Bind() as texture:
                    texture.TexImage2D(self.size, np.array(self.image, dtype=np.uint8))
        return self._texture

    @property
    def size(self) -> Types.Vec2[int]:
        return Types.Vec2[int].New(Validator.NotNone(self.image).size)
