import typing as t
from uuid import UUID


TID = t.TypeVar('TID', bound=t.Any, default=UUID, covariant=True)


@t.runtime_checkable
class ID(t.Protocol, t.Generic[TID]):
    @property
    def id(self) -> TID: ...
