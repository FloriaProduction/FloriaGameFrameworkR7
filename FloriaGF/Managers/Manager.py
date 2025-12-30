import typing as t

from .. import Abc, Protocols
from ..Sequences import Sequence


class Manager[
    TItem: Protocols.ID | t.Any,
](
    Abc.Managers.Manager[TItem],
):
    __slots__ = (
        '_storage',
        *Abc.Managers.Manager.__slots__,
    )

    def __init__(self):
        super().__init__()

        self._storage: dict[t.Any, TItem] = {}

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        self.RemoveAll()

    def Register(self, item: TItem) -> TItem:
        key = self._GetKey(item)

        if key in self._storage:
            raise ValueError()

        self._storage[key] = item

        return item

    @t.overload
    def Remove(self, item: TItem, /) -> TItem: ...
    @t.overload
    def Remove[TDefault: t.Optional[t.Any]](self, item: TItem, default: TDefault, /) -> TItem | TDefault: ...
    def Remove(self, *args: TItem | t.Any):
        item = t.cast(TItem, args[0])
        key = self._GetKey(item)

        if key not in self._storage:
            if len(args) >= 2:
                return args[1]
            raise ValueError()

        return self._storage.pop(key)

    def RemoveAll(self):
        for item in (*self._storage.values(),):
            if (del_item := self.Remove(item, None)) is not None and isinstance(del_item, Abc.Mixins.Disposable):
                del_item.Dispose()

    def Has(self, item: TItem) -> bool:
        return item in self._storage

    @staticmethod
    def _GetKey(item: TItem) -> t.Any:
        '''
        Уникальный идентификатор объекта
        '''
        if isinstance(item, Protocols.ID):
            return item.id
        return hash(item)

    @property
    def sequence(self) -> Sequence[TItem]:
        return Sequence(self._storage.values())

    @property
    def count(self) -> int:
        return len(self._storage)
