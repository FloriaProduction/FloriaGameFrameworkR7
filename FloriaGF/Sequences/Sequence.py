import typing as t
import itertools
import functools


TItem = t.TypeVar('TItem', bound=t.Any, covariant=True)


class Sequence(
    t.Generic[TItem],
):
    __slots__ = ('_source',)

    def __init__(self, source: t.Iterable[TItem]):
        super().__init__()

        self._source: t.Iterable[TItem] = source

    @classmethod
    def _Create[U: t.Any](cls, source: t.Iterable[U]):
        return Sequence(source)

    def Filter(self, predicate: t.Callable[[TItem], bool]):
        return self._Create(filter(predicate, self._source))

    def Map[U: t.Any](self, transform: t.Callable[[TItem], U]):
        return self._Create(map(transform, self._source))

    def FlatMap[U: t.Any](self, transform: t.Callable[[TItem], t.Iterable[U]]):
        return self._Create(item_transformed for item in self._source for item_transformed in transform(item))

    def Take(self, n: int):
        return self._Create(itertools.islice(self._source, n))

    def Skip(self, n: int):
        return self._Create(itertools.islice(self._source, n, None))

    def Sort(self, key: t.Callable[[TItem], t.Any], reversed: bool = False):
        return self._Create(sorted(self._source, key=key, reverse=reversed))

    def ToList(self) -> list[TItem]:
        return list(self._source)

    def ToTuple(self) -> tuple[TItem, ...]:
        return tuple(self._source)

    def ToSet(self) -> set[TItem]:
        return set(self._source)

    @functools.cached_property
    def count(self) -> int:
        return sum(1 for _ in self)

    @functools.cached_property
    def is_empty(self) -> bool:
        for _ in self._source:
            return False
        return True

    def First(self, predicat: t.Optional[t.Callable[[TItem], bool]] = None) -> TItem:
        for item in self._source:
            if predicat is not None and predicat(item) is False:
                continue
            return item
        raise ValueError()

    def FirstOrDefault[TDefault: t.Optional[t.Any]](
        self,
        default: TDefault = None,
        predicat: t.Optional[t.Callable[[TItem], bool]] = None,
    ) -> TItem | TDefault:
        for item in self._source:
            if predicat is not None and predicat(item) is False:
                continue
            return item
        return default

    def FirstOrDefaultLazy[TDefault: t.Optional[t.Any]](
        self,
        default: t.Callable[[], TDefault],
        predicat: t.Optional[t.Callable[[TItem], bool]] = None,
    ) -> TItem | TDefault:
        for item in self._source:
            if predicat is not None and predicat(item) is False:
                continue
            return item
        return default()

    def Any(self, predicat: t.Callable[[TItem], bool]):
        return any(predicat(item) for item in self._source)

    def All(self, predicat: t.Callable[[TItem], bool]):
        return all(predicat(item) for item in self._source)

    def __iter__(self) -> t.Generator[TItem, t.Any, None]:
        yield from self._source

    def __len__(self):
        return self.count

    def __bool__(self):
        return not self.is_empty

    def __getitem__(self, key: slice | int):
        if isinstance(key, slice):
            return Sequence(itertools.islice(self._source, key.start, key.stop, key.step))

        elif isinstance(key, int):
            if key < 0:
                return tuple(self._source)[key]

            else:
                for i, item in enumerate(self._source):
                    if i == key:
                        return item

                raise IndexError("sequence index out of range")

        raise TypeError("sequence indices must be integers or slices")


if t.TYPE_CHECKING:

    class Example(Sequence[TItem], t.Generic[TItem]):
        if t.TYPE_CHECKING:

            # base

            def Filter(self, predicate: t.Callable[[TItem], bool]):
                return t.cast(Example[TItem], super().Filter(predicate))

            def Map[U: t.Any](self, transform: t.Callable[[TItem], U]):
                return t.cast(Example[U], super().Map(transform))

            def FlatMap[U: t.Any](self, transform: t.Callable[[TItem], t.Iterable[U]]):
                return t.cast(Example[U], super().FlatMap(transform))

            def Take(self, n: int):
                return t.cast(Example[TItem], super().Take(n))

            def Skip(self, n: int):
                return t.cast(Example[TItem], super().Skip(n))

            def Sort(self, key: t.Callable[[TItem], t.Any], reversed: bool = False):
                return t.cast(Example[TItem], super().Sort(key, reversed))
