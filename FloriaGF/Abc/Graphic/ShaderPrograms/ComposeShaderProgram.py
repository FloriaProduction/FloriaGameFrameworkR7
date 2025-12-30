from abc import ABC, abstractmethod
import typing as t
from contextlib import contextmanager

from .ShaderProgram import ShaderProgram

if t.TYPE_CHECKING:
    from ....Graphic.Objects.FBO import FBO


class ComposeShaderProgram(
    ShaderProgram,
    ABC,
):
    __slots__ = ()

    @contextmanager
    @abstractmethod
    def Bind(self, fbo: 'FBO', *args: t.Any, **kwargs: t.Any):
        yield self
