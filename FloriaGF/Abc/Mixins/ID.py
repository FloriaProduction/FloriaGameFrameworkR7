from abc import ABC, abstractmethod
import typing as t
from uuid import UUID


class ID[TID: t.Any = UUID](ABC):
    __slots__ = ()

    @abstractmethod
    def GetID(self) -> TID: ...

    @property
    def id(self):
        return self.GetID()
