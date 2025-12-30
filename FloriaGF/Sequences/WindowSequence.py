import typing as t

from .. import Abc, Utils
from .NameSequence import NameSequence, TName
from .IDSequence import IDSequence, TID
from .TypeSequence import TypeSequence
from .Sequence import Sequence


TItem = t.TypeVar('TItem', bound=Abc.Window, covariant=True)


class WindowSequence(
    NameSequence[TItem],
    IDSequence[TItem],
    TypeSequence[TItem],
    Sequence[TItem],
    t.Generic[TItem],
):
    __slots__ = ()

    @classmethod
    def _Create[U: t.Any](cls, source: t.Iterable[U]):
        return WindowSequence(source)

    if t.TYPE_CHECKING:

        # base

        def Filter(self, predicate: t.Callable[[TItem], bool]):
            return t.cast(WindowSequence[TItem], super().Filter(predicate))

        def Map[U: t.Any](self, transform: t.Callable[[TItem], U]):
            return t.cast(WindowSequence[U], super().Map(transform))

        def FlatMap[U: t.Any](self, transform: t.Callable[[TItem], t.Iterable[U]]):
            return t.cast(WindowSequence[U], super().FlatMap(transform))

        def Take(self, n: int):
            return t.cast(WindowSequence[TItem], super().Take(n))

        def Skip(self, n: int):
            return t.cast(WindowSequence[TItem], super().Skip(n))

        def Sort(self, key: t.Callable[[TItem], t.Any], reversed: bool = False):
            return t.cast(WindowSequence[TItem], super().Sort(key, reversed))

        # type

        def OfType[U: t.Any](self, type: t.Type[U]):
            return t.cast(WindowSequence[U], super().OfType(type))

        # id

        def WithID(self, id: TID):
            return t.cast(WindowSequence[TItem], super().WithID(id))

        def WithIDS(self, ids: t.Iterable[TID]):
            return t.cast(WindowSequence[TItem], super().WithIDS(ids))

        # name

        def WithName(self, name: TName):
            return t.cast(WindowSequence[TItem], super().WithName(name))

        def WithNames(self, names: t.Iterable[TName]):
            return t.cast(WindowSequence[TItem], super().WithNames(names))
