import typing as t

from .Sequence import Sequence


TItem = t.TypeVar('TItem', bound=t.Any, covariant=True)


class TypeSequence(
    Sequence[TItem],
    t.Generic[TItem],
):
    __slots__ = ()

    @classmethod
    def _Create[U: t.Any](cls, source: t.Iterable[U]):
        return TypeSequence(source)

    def OfType[U: t.Any](self, type: t.Type[U]):
        return self._Create((item for item in self._source if isinstance(item, type)))

    if t.TYPE_CHECKING:

        # base

        def Filter(self, predicate: t.Callable[[TItem], bool]):
            return t.cast(TypeSequence[TItem], super().Filter(predicate))

        def Map[U: t.Any](self, transform: t.Callable[[TItem], U]):
            return t.cast(TypeSequence[U], super().Map(transform))

        def FlatMap[U: t.Any](self, transform: t.Callable[[TItem], t.Iterable[U]]):
            return t.cast(TypeSequence[U], super().FlatMap(transform))

        def Take(self, n: int):
            return t.cast(TypeSequence[TItem], super().Take(n))

        def Skip(self, n: int):
            return t.cast(TypeSequence[TItem], super().Skip(n))

        def Sort(self, key: t.Callable[[TItem], t.Any], reversed: bool = False):
            return t.cast(TypeSequence[TItem], super().Sort(key, reversed))


if t.TYPE_CHECKING:

    class Example(TypeSequence[TItem], t.Generic[TItem]):
        if t.TYPE_CHECKING:

            # type

            def OfType[U: t.Any](self, type: t.Type[U]):
                return t.cast(Example[U], super().OfType(type))
