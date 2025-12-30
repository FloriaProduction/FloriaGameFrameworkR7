import typing as t

from FloriaGF.Sequences.NameSequence import NameSequence, TName
from FloriaGF.Sequences.TypeSequence import TypeSequence
from FloriaGF.Sequences.Sequence import Sequence

from ..Graphic.Animation import Animation


TItem = t.TypeVar('TItem', bound=Animation, covariant=True)


class AnimationSequence(
    NameSequence[TItem],
    TypeSequence[TItem],
    Sequence[TItem],
    t.Generic[TItem],
):
    @classmethod
    def _Create[U: t.Any](cls, source: t.Iterable[U]):
        return AnimationSequence(source)

    if t.TYPE_CHECKING:

        # base

        def Filter(self, predicate: t.Callable[[TItem], bool]):
            return t.cast(AnimationSequence[TItem], super().Filter(predicate))

        def Map[U: t.Any](self, transform: t.Callable[[TItem], U]):
            return t.cast(AnimationSequence[U], super().Map(transform))

        def FlatMap[U: t.Any](self, transform: t.Callable[[TItem], t.Iterable[U]]):
            return t.cast(AnimationSequence[U], super().FlatMap(transform))

        def Take(self, n: int):
            return t.cast(AnimationSequence[TItem], super().Take(n))

        def Skip(self, n: int):
            return t.cast(AnimationSequence[TItem], super().Skip(n))

        def Sort(self, key: t.Callable[[TItem], t.Any], reversed: bool = False):
            return t.cast(AnimationSequence[TItem], super().Sort(key, reversed))

        # type

        def OfType[U: t.Any](self, type: t.Type[U]):
            return t.cast(AnimationSequence[U], super().OfType(type))

        # name

        def WithName(self, name: TName):
            return t.cast(AnimationSequence[TItem], super().WithName(name))

        def WithNames(self, names: t.Iterable[TName]):
            return t.cast(AnimationSequence[TItem], super().WithNames(names))
