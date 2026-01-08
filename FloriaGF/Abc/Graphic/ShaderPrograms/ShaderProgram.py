from abc import ABC, abstractmethod
import typing as t
from contextlib import contextmanager

from ... import Mixins

if t.TYPE_CHECKING:
    from .Scheme import Scheme, SchemeItem


class ShaderProgram(
    Mixins.ID[int],
    Mixins.Nameable[t.Optional[str]],
    Mixins.Binding,
    Mixins.Disposable,
    ABC,
):
    __slots__ = ()

    @property
    @abstractmethod
    def scheme(self) -> 'Scheme': ...

    @abstractmethod
    def SetUniformFloat(self, name: str, value: float): ...
    @abstractmethod
    def SetUniformVector(self, name: str, value: tuple[float, ...]): ...

    @contextmanager
    @abstractmethod
    def Bind(self, *args: t.Any, **kwargs: t.Any):
        yield self

    @staticmethod
    def _ValidateSchemeCompatibility(
        camera_scheme: 'tuple[SchemeItem, ...]',
        shader_scheme: 'tuple[SchemeItem, ...]',
    ) -> bool:
        for shader_item, cam_item in zip(shader_scheme, camera_scheme):
            if cam_item['name'] != shader_item['name'] or cam_item['type'] != shader_item['type']:
                return False
        return True
