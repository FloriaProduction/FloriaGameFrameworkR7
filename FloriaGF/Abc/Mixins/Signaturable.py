from abc import ABC, abstractmethod
import typing as t


class Signaturable(ABC):
    __slots__ = ()

    @abstractmethod
    def GetSignature(self, *args: t.Any, **kwargs: t.Any) -> int: ...
