import typing as t
from abc import ABC, abstractmethod
import numpy as np

from . import Abc, Convert, GL
from .Stopwatch import Stopwatch


class InstanceAttributeManager[
    TAttribs: str = str,
](
    ABC,
):
    __slots__ = (
        '_update_instance_attribute_names',
        '__instance_data_cache',
        '_stopwatch_GetInstanceData',
        '_stopwatch__UpdateInstanceAttributes',
    )

    def __init__(self) -> None:
        super().__init__()

        self._update_instance_attribute_names: set[TAttribs] = set()
        self.__instance_data_cache: t.Optional[dict[TAttribs, t.Any]] = None

        self._stopwatch_GetInstanceData = Stopwatch()
        self._stopwatch__UpdateInstanceAttributes = Stopwatch()

    @abstractmethod
    def _GetIntanceAttributeItems(self) -> tuple[Abc.Graphic.ShaderPrograms.SchemeItem[TAttribs], ...]: ...

    @abstractmethod
    def _GetInstanceAttribute(self, attrib: TAttribs) -> t.Any: ...

    def _GetInstanceAttributeCache(self, attrib: TAttribs) -> t.Optional[t.Any]:
        if (data := self.__instance_data_cache) is None:
            return None
        return data.get(attrib)

    def _UpdateInstanceAttributes(self, *fields: TAttribs, all: bool = False):
        with self._stopwatch__UpdateInstanceAttributes:
            if all:
                self.__instance_data_cache = None
            else:
                allow_fields = set(item['attrib'] for item in self._GetIntanceAttributeItems())
                if any(field not in allow_fields for field in fields):
                    raise
                self._update_instance_attribute_names.update(fields)

    @t.final
    def GetInstanceData(self) -> tuple[t.Any, ...]:
        with self._stopwatch_GetInstanceData:
            if self.__instance_data_cache is None:
                self.__instance_data_cache = {
                    item['attrib']: self._GetInstanceAttribute(item['attrib'])  # pyright: ignore[reportArgumentType]
                    for item in self._GetIntanceAttributeItems()
                }

            else:
                for field in self._update_instance_attribute_names:
                    self.__instance_data_cache[field] = self._GetInstanceAttribute(field)

            self._update_instance_attribute_names.clear()

            return tuple(self.__instance_data_cache.values())

    def GetInstanceDType(self) -> np.dtype:
        return np.dtype(
            [
                (
                    item['attrib'],
                    *GL.Convert.GLSLTypeToNumpy(item['type']),
                )
                for item in self._GetIntanceAttributeItems()
            ]
        )

    @property
    def request_intance_update(self):
        return self.__instance_data_cache is None or len(self._update_instance_attribute_names) > 0
