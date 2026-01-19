import typing as t

if t.TYPE_CHECKING:
    from .... import GL


TName = t.TypeVar('TName', bound=str, default=str, covariant=True)


class SchemeItem(t.TypedDict, t.Generic[TName]):
    name: TName
    type: 'GL.hints.glsl_type'


class Scheme(t.TypedDict):
    base: dict[int, SchemeItem]
    instance: t.NotRequired[dict[int, SchemeItem]]
