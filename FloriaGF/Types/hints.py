import typing as t

if t.TYPE_CHECKING:
    import numpy as np
    import pathlib

    from .Vec import Vec2, Vec3
    from .Quaternion import Quaternion
    from .Color import RGB, RGBA


number = float | int

position_3d = t.Union[
    tuple[number, number, number],
    'Vec3[number]',
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
    tuple[number, number, number],  # xyz
    tuple[number, number, number, number],  # wxyz
    'Vec3[number]',
    'Quaternion[number]',
    t.Iterable[number],
]
scale_3d = t.Union[
    number,
    tuple[number, number, number],
    'Vec3[number]',
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


viewport_mode = t.Literal[
    'stretch',
    'letterbox',
    'pixel_perfect',
]

context_version = tuple[int, int]

path = t.Union[
    str,
    'pathlib.Path',
]
