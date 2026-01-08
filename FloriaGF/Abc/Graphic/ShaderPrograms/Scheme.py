import typing as t

if t.TYPE_CHECKING:
    from .... import GL


scheme_item_attrib = t.Union[
    t.Literal[
        'vertice',
        'texcoord',
    ],
    str,
]

TName = t.TypeVar('TName', bound=str, default=scheme_item_attrib, covariant=True)


class SchemeItem(t.TypedDict, t.Generic[TName]):
    name: TName
    type: 'GL.hints.glsl_type'


class Scheme(t.TypedDict):
    base: dict[int, SchemeItem]
    instance: t.NotRequired[dict[int, SchemeItem]]
