import typing as t

if t.TYPE_CHECKING:
    import pyrr
    import numpy as np
    import pathlib

    from .Vec import Vec2, Vec3
    from .Color import RGB, RGBA


number = float | int

position_3d = t.Union[
    tuple[number, number, number],
    'Vec3[number]',
    'pyrr.Vector3',
    t.Iterable[number],
]
offset_2d = t.Union[
    tuple[int, int],
    'Vec2[int]',
]
offset_3d = t.Union[
    tuple[int, int, int],
    'Vec3[int]',
]
rotation = t.Union[
    tuple[number, number, number],
    'Vec3[number]',
    'pyrr.Quaternion',
    t.Iterable[number],
]
scale_3d = t.Union[
    number,
    tuple[number, number, number],
    'Vec3[number]',
    'pyrr.Vector3',
    t.Iterable[number],
]
size_2d = t.Union[
    tuple[int, int],
    'Vec2[int]',
]
size_3d = t.Union[
    tuple[int, int, int],
    'Vec3[int]',
]


rgb = t.Union[
    tuple[int, int, int],
    'RGB[int]',
    t.Iterable[int],
]

rgba = t.Union[
    tuple[int, int, int, int],
    'RGBA[int]',
    t.Iterable[int],
]


display_mode = t.Literal[
    'stretch',
    'letterbox',
]

context_version = tuple[int, int]

path = t.Union[
    str,
    'pathlib.Path',
]
