import typing as t

from .. import Abc, Utils
from .NameSequence import NameSequence, TName
from .TypeSequence import TypeSequence
from .Sequence import Sequence


TItem = t.TypeVar('TItem', bound=Abc.ShaderProgram, covariant=True)


class ShaderSequence(
    NameSequence[TItem],
    TypeSequence[TItem],
    t.Generic[TItem],
):
    __slots__ = ()

    @classmethod
    def _Create[U: t.Any](cls, source: t.Iterable[U]):
        return ShaderSequence(source)

    if t.TYPE_CHECKING:

        # base

        def Filter(self, predicate: t.Callable[[TItem], bool]):
            return t.cast(ShaderSequence[TItem], super().Filter(predicate))

        def Map[U: t.Any](self, transform: t.Callable[[TItem], U]):
            return t.cast(ShaderSequence[U], super().Map(transform))

        def FlatMap[U: t.Any](self, transform: t.Callable[[TItem], t.Iterable[U]]):
            return t.cast(ShaderSequence[U], super().FlatMap(transform))

        def Take(self, n: int):
            return t.cast(ShaderSequence[TItem], super().Take(n))

        def Skip(self, n: int):
            return t.cast(ShaderSequence[TItem], super().Skip(n))

        def Sort(self, key: t.Callable[[TItem], t.Any], reversed: bool = False):
            return t.cast(ShaderSequence[TItem], super().Sort(key, reversed))

        # type

        def OfType[U: t.Any](self, type: t.Type[U]):
            return t.cast(ShaderSequence[U], super().OfType(type))

        # name

        def WithName(self, name: TName):
            return t.cast(ShaderSequence[TItem], super().WithName(name))

        def WithNames(self, names: t.Iterable[TName]):
            return t.cast(ShaderSequence[TItem], super().WithNames(names))
