import typing as t


TName = t.TypeVar('TName', bound=t.Any, default=str, covariant=True)


@t.runtime_checkable
class Named(t.Protocol, t.Generic[TName]):
    @property
    def name(self) -> TName: ...
