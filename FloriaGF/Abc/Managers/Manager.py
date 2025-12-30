from abc import ABC, abstractmethod
import typing as t

from ... import Protocols
from .. import Mixins

if t.TYPE_CHECKING:
    from ...Sequences.Sequence import Sequence


class Manager[TItem: Protocols.ID | t.Any](
    Mixins.Repr,
    Mixins.Disposable,
    ABC,
):
    __slots__ = (
        *Mixins.Repr.__slots__,
        *Mixins.Disposable.__slots__,
    )

    @abstractmethod
    def Register(self, item: TItem) -> TItem: ...

    @t.overload
    def Remove(self, item: TItem, /) -> TItem: ...
    @t.overload
    def Remove[TDefault: t.Optional[t.Any]](self, item: TItem, default: TDefault, /) -> TItem | TDefault: ...
    @abstractmethod
    def Remove(self, *args: t.Any) -> t.Any: ...

    @abstractmethod
    def RemoveAll(self): ...

    @abstractmethod
    def Has(self, item: TItem) -> bool: ...

    @property
    @abstractmethod
    def sequence(self) -> 'Sequence[TItem]': ...

    @property
    @abstractmethod
    def count(self) -> int: ...

    def RegisterMany(self, *items: TItem):
        for item in items:
            self.Register(item)

    def __len__(self) -> int:
        return self.count

    def __contains__(self, item: TItem):
        return self.Has(item)
