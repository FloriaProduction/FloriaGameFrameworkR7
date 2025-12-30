from abc import ABC, abstractmethod
import typing as t


class Nameable[TName: t.Any = str](ABC):
    __slots__ = ()

    @abstractmethod
    def GetName(self) -> TName: ...

    @property
    def name(self) -> TName:
        return self.GetName()
