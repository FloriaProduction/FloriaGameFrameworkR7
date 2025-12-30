import typing as t
from uuid import UUID

from .. import Abc
from .Sequence import Sequence
from .TypeSequence import TypeSequence
from .IDSequence import IDSequence, TID


TItem = t.TypeVar('TItem', bound=Abc.InstanceObject, covariant=True)


class InstanceObjectSequence(
    IDSequence[TItem],
    TypeSequence[TItem],
    Sequence[TItem],
):
    __slots__ = ()

    @classmethod
    def _Create[U: t.Any](cls, source: t.Iterable[U]):
        return InstanceObjectSequence(source)

    if t.TYPE_CHECKING:

        # base

        def Filter(self, predicate: t.Callable[[TItem], bool]):
            return t.cast(InstanceObjectSequence[TItem], super().Filter(predicate))

        def Map[U: t.Any](self, transform: t.Callable[[TItem], U]):
            return t.cast(InstanceObjectSequence[U], super().Map(transform))

        def FlatMap[U: t.Any](self, transform: t.Callable[[TItem], t.Iterable[U]]):
            return t.cast(InstanceObjectSequence[U], super().FlatMap(transform))

        def Take(self, n: int):
            return t.cast(InstanceObjectSequence[TItem], super().Take(n))

        def Skip(self, n: int):
            return t.cast(InstanceObjectSequence[TItem], super().Skip(n))

        def Sort(self, key: t.Callable[[TItem], t.Any], reversed: bool = False):
            return t.cast(InstanceObjectSequence[TItem], super().Sort(key, reversed))

        # type

        def OfType[U: t.Any](self, type: t.Type[U]):
            return t.cast(InstanceObjectSequence[U], super().OfType(type))

        # id

        def WithID(self, id: TID):
            return t.cast(InstanceObjectSequence[TItem], super().WithID(id))

        def WithIDS(self, ids: t.Iterable[TID]):
            return t.cast(InstanceObjectSequence[TItem], super().WithIDS(ids))
