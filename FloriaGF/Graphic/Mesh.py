import typing as t
import numpy as np
from uuid import UUID, uuid4

from .. import Abc

if t.TYPE_CHECKING:
    from .. import GL


class Mesh(
    Abc.Graphic.Mesh,
):
    def __init__(
        self,
        primitive: 'GL.hints.primitive',
        vertices: t.Sequence[float],
        texcoords: t.Optional[t.Sequence[float]] = None,
        indices: t.Optional[t.Sequence[int]] = None,
        vertice_size: int = 2,
        texcoord_size: int = 2,
        name: t.Optional[str] = None,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        if texcoords is not None and len(vertices) / vertice_size != len(texcoords) / texcoord_size:
            raise ValueError()

        self._id: UUID = uuid4()

        self._vertices = np.array(vertices, dtype=np.float32)
        self._texcoords = None if texcoords is None else np.array(texcoords, dtype=np.float32)
        self._indices = None if indices is None else np.array(indices, dtype=np.uint32)
        self._primitive: 'GL.hints.primitive' = primitive
        self._vertice_size = vertice_size
        self._texcoord_size = texcoord_size

        self._name: t.Optional[str] = name

    @property
    def vertices(self):
        return self._vertices

    @property
    def vertice_size(self):
        return self._vertice_size

    @property
    def texcoords(self):
        return self._texcoords

    @property
    def texcoord_size(self):
        return None if self._texcoords is None else self._texcoord_size

    @property
    def indices(self):
        return self._indices

    @property
    def primitive(self):
        return self._primitive

    @property
    def count(self):
        return len(self.vertices) // self._vertice_size

    def GetName(self) -> t.Optional[str]:
        return self._name

    def GetID(self):
        return self._id

    def GetSignature(self) -> int:
        return hash(self.id)
