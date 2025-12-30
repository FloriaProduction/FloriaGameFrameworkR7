import typing as t
from uuid import UUID

from .Sequence import Sequence

if t.TYPE_CHECKING:
    from ..Protocols import ID


TID = UUID
TItem = t.TypeVar('TItem', bound='ID[TID]', covariant=True)


class IDSequence(
    Sequence[TItem],
    t.Generic[TItem],
):
    __slots__ = ()

    @classmethod
    def _Create[U: t.Any](cls, source: t.Iterable[U]):
        return IDSequence(source)

    def WithID(self, id: TID):
        return self._Create(filter(lambda item: item.id == id, self._source))

    def WithIDS(self, ids: t.Iterable[TID]):
        return self._Create(filter(lambda item: item.id in ids, self._source))

    def GetByID(
        self,
        id: TID,
        predicate: t.Optional[t.Callable[[TItem], bool]] = None,
    ) -> TItem:
        for item in self.WithID(id):
            if predicate is not None and predicate(item) is False:
                continue
            return item
        raise ValueError()

    def GetByIDOrDefault[TDefault: t.Optional[t.Any] = None](
        self,
        id: TID,
        default: TDefault = None,
        predicate: t.Optional[t.Callable[[TItem], bool]] = None,
    ) -> TItem | TDefault:
        for item in self.WithID(id):
            if predicate is not None and predicate(item) is False:
                continue
            return item
        return default

    def GetByIDOrDefaultLazy[TDefault: t.Optional[t.Any] = None](
        self,
        id: TID,
        default: t.Callable[[], TDefault],
        predicate: t.Optional[t.Callable[[TItem], bool]] = None,
    ) -> TItem | TDefault:
        for item in self.WithID(id):
            if predicate is not None and predicate(item) is False:
                continue
            return item
        return default()

    if t.TYPE_CHECKING:

        # base

        def Filter(self, predicate: t.Callable[[TItem], bool]):
            return t.cast(IDSequence[TItem], super().Filter(predicate))

        def Map[U: t.Any](self, transform: t.Callable[[TItem], U]):
            return t.cast(IDSequence[U], super().Map(transform))

        def FlatMap[U: t.Any](self, transform: t.Callable[[TItem], t.Iterable[U]]):
            return t.cast(IDSequence[U], super().FlatMap(transform))

        def Take(self, n: int):
            return t.cast(IDSequence[TItem], super().Take(n))

        def Skip(self, n: int):
            return t.cast(IDSequence[TItem], super().Skip(n))

        def Sort(self, key: t.Callable[[TItem], t.Any], reversed: bool = False):
            return t.cast(IDSequence[TItem], super().Sort(key, reversed))


if t.TYPE_CHECKING:

    class Example(IDSequence[TItem], t.Generic[TItem]):
        if t.TYPE_CHECKING:

            # id

            def WithID(self, id: TID):
                return t.cast(Example[TItem], super().WithID(id))

            def WithIDS(self, ids: t.Iterable[TID]):
                return t.cast(Example[TItem], super().WithIDS(ids))
