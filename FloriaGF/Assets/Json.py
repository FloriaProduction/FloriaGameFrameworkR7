import typing as t
from pathlib import Path
import json
import asyncio
import aiofiles

from .. import Abc, Types, Validator
from .Text import Text


class Json(
    Text,
):
    def __init__(
        self,
        path: t.Optional[str | Path] = None,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        super().__init__(path, *args, **kwargs)

        self._data: t.Optional[Types.JSON] = None

    @classmethod
    async def Create(cls, data: Types.JSON, *args: t.Any, **kwargs: t.Any) -> 'Json':
        asset = Json(None)

        asset.data = data

        return asset

    @classmethod
    async def Load(cls, path: str | Path) -> 'Json':
        asset = Json(path)

        async with aiofiles.open(path, 'r') as file:
            asset._text = await file.read()

        return asset

    def SetText(self, value: t.Optional[str]):
        super().SetText(value)
        self._data = None

    def GetData(self) -> t.Optional[Types.JSON]:
        if self._data is None:
            self._data = json.loads(Validator.NotNone(self.text))
        return self._data

    def SetData(self, value: t.Optional[Types.JSON]):
        self.SetText(json.dumps(value))

    @property
    def data(self):
        return self.GetData()

    @data.setter
    def data(self, value: Types.JSON):
        self.SetData(value)
