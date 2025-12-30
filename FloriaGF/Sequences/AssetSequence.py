import typing as t
import pathlib

from .. import Abc, Utils, Convert, Types
from .Sequence import Sequence
from .TypeSequence import TypeSequence

if t.TYPE_CHECKING:
    from ..Assets import Asset


TItem = t.TypeVar('TItem', bound='Asset', covariant=True)


class AssetSequence(
    TypeSequence[TItem],
    Sequence[TItem],
    t.Generic[TItem],
):
    __slots__ = ()

    @classmethod
    def _Create[U: t.Any](cls, source: t.Iterable[U]):
        return AssetSequence(source)

    def WithPath(self, path: Types.hints.path):
        return self._Create(
            filter(
                lambda item: (item_path := item.path) is not None and item_path.is_file() and Utils.ComparePath(path, item_path),
                self._source,
            )
        )

    def WithPathes(self, pathes: t.Iterable[Types.hints.path]):
        return self._Create(
            filter(
                lambda item: (item_path := item.path) is not None
                and item_path.is_file()
                and all(Utils.ComparePath(path, item_path) for path in pathes),
                self._source,
            )
        )

    def WithDir(self, dir: Types.hints.path):
        return self._Create(
            filter(
                lambda item: (path := item.path) is not None and path.is_dir() and Utils.DirectoryContainsFile(dir, path),
                self._source,
            )
        )

    def WithDirs(self, dirs: t.Iterable[Types.hints.path]):
        return self._Create(
            filter(
                lambda item: (path := item.path) is not None
                and path.is_dir()
                and all(Utils.DirectoryContainsFile(dir, path) for dir in dirs),
                self._source,
            )
        )

    if t.TYPE_CHECKING:

        # base

        def Filter(self, predicate: t.Callable[[TItem], bool]):
            return t.cast(AssetSequence[TItem], super().Filter(predicate))

        def Map[U: t.Any](self, transform: t.Callable[[TItem], U]):
            return t.cast(AssetSequence[U], super().Map(transform))

        def FlatMap[U: t.Any](self, transform: t.Callable[[TItem], t.Iterable[U]]):
            return t.cast(AssetSequence[U], super().FlatMap(transform))

        def Take(self, n: int):
            return t.cast(AssetSequence[TItem], super().Take(n))

        def Skip(self, n: int):
            return t.cast(AssetSequence[TItem], super().Skip(n))

        def Sort(self, key: t.Callable[[TItem], t.Any], reversed: bool = False):
            return t.cast(AssetSequence[TItem], super().Sort(key, reversed))

        # type

        def OfType[U: t.Any](self, type: t.Type[U]):
            return t.cast(AssetSequence[U], super().OfType(type))
