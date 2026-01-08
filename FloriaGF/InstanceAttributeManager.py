import typing as t
from abc import ABC, abstractmethod
import numpy as np

from . import Abc, GL
from .Stopwatch import stopwatch


class InstanceAttributeManager[
    TName: str = str,
](
    ABC,
):
    """Менеджер атрибутов инстансов для инстансированного рендеринга.

    Базовый абстрактный класс для управления данными атрибутов, передаваемыми в шейдеры
    через инстансированный рендеринг. Обеспечивает кэширование, обновление по требованию
    и автоматическое создание numpy dtype для передачи в OpenGL буферы.
    """

    __slots__ = (
        '__update_names',
        '__data_cache',
    )

    def __init__(self) -> None:
        super().__init__()

        self.__update_names: set[TName] = set()
        self.__data_cache: t.Optional[dict[TName, t.Any]] = None

    @abstractmethod
    def GetIntanceAttributeItems(self) -> tuple[Abc.Graphic.ShaderPrograms.SchemeItem[TName], ...]:
        """Возвращает схему атрибутов инстансов.

        Returns:
            Кортеж словарей SchemeItem с описанием атрибутов и их типов в GLSL.

        Example::

            return (
                {'name': 'model_matrix', 'type': 'mat4'},
                {'name': 'color', 'type': 'vec4'},
            )
        """

    @abstractmethod
    def _GetInstanceAttribute(self, name: TName) -> t.Any:
        """Возвращает значение конкретного атрибута инстанса.

        Args:
            name: Имя атрибута из схемы.

        Returns:
            Значение атрибута в формате, совместимом с numpy/OpenGL.

        Raises:
            ValueError: Если запрашивается неизвестный атрибут.
        """

    def _GetInstanceAttributeCache(self, name: TName) -> t.Optional[t.Any]:
        """Возвращает кэшированное значение атрибута, если оно есть.

        Args:
            name: Имя атрибута для получения из кэша.

        Returns:
            Кэшированное значение атрибута или None, если кэш пуст или атрибут отсутствует.
        """

        if (data := self.__data_cache) is None:
            return None
        return data.get(name)

    @stopwatch
    def _UpdateInstanceAttributes(self, *names: TName, all: bool = False):
        """Помечает атрибуты для обновления.

        Args:
            *fields: Имена атрибутов, требующих обновления.
            all: Если True, помечает все атрибуты для полного обновления.

        Raises:
            ValueError: Если передан недопустимый атрибут (не входящий в схему).

        Note:
            Фактическое обновление происходит при вызове GetInstanceData().
            Используйте all=True для принудительного пересчета всех атрибутов.
        """

        if all:
            self.__data_cache = None
        else:
            allow_fields = set(item['name'] for item in self.GetIntanceAttributeItems())
            if any(field not in allow_fields for field in names):
                raise ValueError()
            self.__update_names.update(names)

    @stopwatch
    def GetInstanceData(self) -> dict[TName, t.Any]:
        """Возвращает актуальные данные всех атрибутов инстанса.

        Returns:
            Словарь всех атрибутов в порядке, определенном схемой.

        Side Effects:
            - Обновляет кэш данных атрибутов.
            - Очищает очередь обновлений.
            - При первом вызове вычисляет все атрибуты.
            - При последующих вызовах обновляет только измененные атрибуты.

        Performance:
            Использует кэширование для минимизации вычислений. Обновляет только атрибуты, помеченные через _UpdateInstanceAttributes().
        """

        if self.__data_cache is None:
            self.__data_cache = {
                item['name']: self._GetInstanceAttribute(item['name']) for item in self.GetIntanceAttributeItems()
            }

        else:
            for field in self.__update_names:
                self.__data_cache[field] = self._GetInstanceAttribute(field)

        self.__update_names.clear()

        return dict(self.__data_cache)

    def GetInstanceDType(self) -> np.dtype:
        """Создает numpy dtype для передачи данных в OpenGL буфер.

        Returns:
            np.dtype: Структурированный dtype, соответствующий схеме атрибутов.
        """
        return np.dtype(
            [
                (
                    item['name'],
                    *GL.Convert.GLSLTypeToNumpy(item['type']),
                )
                for item in self.GetIntanceAttributeItems()
            ]
        )

    @property
    def request_intance_update(self) -> bool:
        """Проверяет, требуется ли обновление данных инстанса.

        Returns:
            True, если кэш пуст или есть ожидающие обновления атрибуты, иначе False.
        """
        return self.__data_cache is None or len(self.__update_names) > 0
