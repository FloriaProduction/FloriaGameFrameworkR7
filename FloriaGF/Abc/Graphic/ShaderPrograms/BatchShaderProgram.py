from abc import ABC, abstractmethod
import typing as t
from contextlib import contextmanager

from .ShaderProgram import ShaderProgram

if t.TYPE_CHECKING:
    from ..Camera import Camera


class BatchShaderProgram(
    ShaderProgram,
    ABC,
):
    __slots__ = ()

    @contextmanager
    @abstractmethod
    def Bind(self, camera: 'Camera', *args: t.Any, **kwargs: t.Any):
        yield self
