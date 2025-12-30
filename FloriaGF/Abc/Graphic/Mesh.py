from abc import ABC, abstractmethod
import typing as t

from .. import Mixins
from ... import GL

if t.TYPE_CHECKING:
    import numpy as np
    from uuid import UUID


class Mesh(
    Mixins.ID['UUID'],
    Mixins.Signaturable,
    Mixins.Nameable[t.Optional[str]],
    ABC,
):
    __slots__ = ()

    @property
    @abstractmethod
    def vertices(self) -> 'np.typing.NDArray[np.float32]': ...

    @property
    @abstractmethod
    def vertice_size(self) -> int:
        '''
        Количество чисел на вершину
        '''

    @property
    @abstractmethod
    def texcoords(self) -> 't.Optional[np.typing.NDArray[np.float32]]': ...

    @property
    @abstractmethod
    def texcoord_size(self) -> t.Optional[int]:
        '''
        Количество чисел на текстурную координату
        '''

    @property
    @abstractmethod
    def indices(self) -> 't.Optional[np.typing.NDArray[np.uint32]]': ...

    @property
    @abstractmethod
    def primitive(self) -> 'GL.hints.primitive': ...

    @property
    @abstractmethod
    def count(self) -> int:
        '''
        Количество вершин
        '''

    def __len__(self) -> int:
        return self.count

    def GetSignature(self) -> int:
        return hash(self.name)

    @property
    def primitive_gl(self) -> int:
        return GL.Convert.ToOpenGLPrimitive(self.primitive)
