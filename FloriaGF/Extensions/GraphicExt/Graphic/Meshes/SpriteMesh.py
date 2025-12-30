from FloriaGF import Abc
from FloriaGF.Graphic import Mesh


SPRITE_MESH_NAME: str = 'sprite-mesh'


def CreateSpriteMesh(name: str = SPRITE_MESH_NAME) -> Abc.Mesh:
    return Mesh(
        'triangle_fan',
        (
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
        ),
        (
            0,
            1,
            1,
            1,
            1,
            0,
            0,
            0,
        ),
        name=name,
    )
