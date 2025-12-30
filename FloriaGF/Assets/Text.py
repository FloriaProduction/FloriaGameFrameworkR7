import typing as t
from pathlib import Path
import aiofiles

from .. import Abc, Convert, Validator
from .Asset import Asset


class Text(Asset):
    __slots__ = ('_text',)

    def __init__(
        self,
        path: t.Optional[str | Path] = None,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        super().__init__(path, *args, **kwargs)

        self._text: t.Optional[str] = None

    @classmethod
    async def Load(cls, path: str | Path) -> 'Text':
        asset = Text(path)

        async with aiofiles.open(path, 'r') as file:
            asset._text = await file.read()

        return asset

    @classmethod
    async def Create(cls, text: str, *args: t.Any, **kwargs: t.Any) -> 'Text':
        asset = Text(None)

        asset.text = text

        return asset

    async def Save(self, path: t.Optional[str | Path] = None, *args: t.Any, **kwargs: t.Any) -> t.Self:
        if path is not None:
            path = self.path = Convert.ToPath(path)
        else:
            path = self.path

        async with aiofiles.open(Validator.NotNone(path), 'w') as file:
            await file.write(Validator.NotNone(self._text))

        return self

    def GetText(self) -> t.Optional[str]:
        return self._text

    def SetText(self, value: t.Optional[str]):
        self._text = value

    @property
    def text(self):
        return self.GetText()

    @text.setter
    def text(self, value: str):
        self.SetText(value)
