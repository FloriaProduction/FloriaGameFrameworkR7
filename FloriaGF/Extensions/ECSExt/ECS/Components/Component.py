import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from ..World import World

    from ..Systems import EntitySystemAny


class Component(ABC):
    @classmethod
    def GetSystems(cls) -> t.Iterable[t.Type['EntitySystemAny']]:
        return ()
