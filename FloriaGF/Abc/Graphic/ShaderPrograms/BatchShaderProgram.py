from abc import ABC, abstractmethod
import typing as t
from contextlib import contextmanager

from .ShaderProgram import ShaderProgram

if t.TYPE_CHECKING:
    from ..Camera import Camera
    from .... import Abc


class BatchShaderProgram(
    ShaderProgram,
    ABC,
):
    __slots__ = ()

    @contextmanager
    @abstractmethod
    def Bind(self, camera: 'Camera', *args: t.Any, **kwargs: t.Any):
        if (
            self._ValidateSchemeCompatibility(
                camera.GetIntanceAttributeItems(),
                self.GetCameraUBOAttributeItems(),
            )
            is False
        ):
            raise

        with super().Bind():
            yield self

    @classmethod
    @abstractmethod
    def GetCameraUBOAttributeItems(cls) -> 'tuple[Abc.Graphic.ShaderPrograms.SchemeItem, ...]': ...
