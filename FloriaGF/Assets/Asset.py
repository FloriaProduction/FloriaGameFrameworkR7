import typing as t
import pathlib
from uuid import uuid4, UUID
from abc import ABC, abstractmethod

from .. import Abc, Utils, Convert


class Asset(
    Abc.Mixins.Repr,
    Abc.Mixins.ID[UUID],
    ABC,
):
    __slots__ = (
        '_id',
        '_path',
    )

    @classmethod
    @abstractmethod
    async def Load(cls, path: str | pathlib.Path) -> 'Asset':
        '''
        Загружает ассет из полученого пути
        '''

    @classmethod
    @abstractmethod
    async def Create(cls, *args: t.Any, **kwargs: t.Any) -> 'Asset':
        '''
        Создает ассет из полученых данных
        '''

    @abstractmethod
    async def Save(self, path: t.Optional[str | pathlib.Path] = None) -> t.Self:
        '''
        Сохраняет ассет в указанный путь.
        Изменяет путь ассета.
        '''

    def __init__(
        self,
        path: t.Optional[str | pathlib.Path] = None,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        self._id: UUID = uuid4()

        self._path: t.Optional[pathlib.Path] = None if path is None else Convert.ToPath(path)

    def GetPath(self):
        return self._path

    def SetPath(self, value: t.Optional[str | pathlib.Path]):
        self._path = None if value is None else Convert.ToPath(value)

    def GetID(self):
        return self._id

    @property
    def path(self):
        return self.GetPath()

    @path.setter
    def path(self, value: t.Optional[str | pathlib.Path]):
        self.SetPath(value)
