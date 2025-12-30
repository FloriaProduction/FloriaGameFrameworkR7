from abc import ABC, abstractmethod
import typing as t
from contextlib import contextmanager

from ... import Mixins

if t.TYPE_CHECKING:
    from uuid import UUID

    from ..Batching.Batch import Batch
    from ..ShaderPrograms.BatchShaderProgram import BatchShaderProgram
    from ..Camera import Camera


class Material[TProgram: 'BatchShaderProgram' = 'BatchShaderProgram'](
    Mixins.ID['UUID'],
    Mixins.Signaturable,
    Mixins.Nameable[t.Optional[str]],
    Mixins.Repr,
    Mixins.Binding,
    ABC,
):
    __slots__ = ()

    @property
    @abstractmethod
    def program(self) -> TProgram: ...

    @contextmanager
    @abstractmethod
    def Bind(self, camera: 'Camera', *args: t.Any, **kwargs: t.Any):
        yield self
