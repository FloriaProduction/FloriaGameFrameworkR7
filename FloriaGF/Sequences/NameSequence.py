import typing as t

from .Sequence import Sequence

if t.TYPE_CHECKING:
    from ..Protocols import Named


TName = t.Optional[str]
TItem = t.TypeVar('TItem', bound='Named[TName]', covariant=True)


class NameSequence(
    Sequence[TItem],
    t.Generic[TItem],
):
    __slots__ = ()

    @classmethod
    def _Create[U: t.Any](cls, source: t.Iterable[U]):
        return NameSequence(source)

    def WithName(self, name: TName):
        return self._Create(filter(lambda item: item.name is not None and item.name == name, self._source))

    def WithNames(self, names: t.Iterable[TName]):
        return self._Create(filter(lambda item: item.name is not None and item.name in names, self._source))

    def Names(self):
        return set(filter(lambda name: name is not None, (item.name for item in self._source)))

    def GetByName(
        self,
        name: TName,
        predicate: t.Optional[t.Callable[[TItem], bool]] = None,
    ) -> TItem:
        for item in self.WithName(name):
            if predicate is not None and predicate(item) is False:
                continue
            return item
        raise ValueError()

    def GetByNameOrDefault[TDefault: t.Optional[t.Any]](
        self,
        name: TName,
        default: TDefault = None,
        predicate: t.Optional[t.Callable[[TItem], bool]] = None,
    ) -> TItem | TDefault:
        for item in self.WithName(name):
            if predicate is not None and predicate(item) is False:
                continue
            return item
        return default

    def GetByNameOrDefaultLazy[TDefault: t.Optional[t.Any]](
        self,
        name: TName,
        default: t.Callable[[], TDefault],
        predicate: t.Optional[t.Callable[[TItem], bool]] = None,
    ) -> TItem | TDefault:
        for item in self.WithName(name):
            if predicate is not None and predicate(item) is False:
                continue
            return item
        return default()

    if t.TYPE_CHECKING:

        def Filter(self, predicate: t.Callable[[TItem], bool]):
            return t.cast(NameSequence[TItem], super().Filter(predicate))

        def Map[U: t.Any](self, transform: t.Callable[[TItem], U]):
            return t.cast(NameSequence[U], super().Map(transform))

        def FlatMap[U: t.Any](self, transform: t.Callable[[TItem], t.Iterable[U]]):
            return t.cast(NameSequence[U], super().FlatMap(transform))

        def Take(self, n: int):
            return t.cast(NameSequence[TItem], super().Take(n))

        def Skip(self, n: int):
            return t.cast(NameSequence[TItem], super().Skip(n))

        def Sort(self, key: t.Callable[[TItem], t.Any], reversed: bool = False):
            return t.cast(NameSequence[TItem], super().Sort(key, reversed))


if t.TYPE_CHECKING:

    class Example(NameSequence[TItem], t.Generic[TItem]):
        if t.TYPE_CHECKING:

            # name

            def WithName(self, name: TName):
                return t.cast(Example[TItem], super().WithName(name))

            def WithNames(self, names: t.Iterable[TName]):
                return t.cast(Example[TItem], super().WithNames(names))
