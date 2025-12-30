from abc import ABC, abstractmethod
import typing as t

from ...Types.JSON import JSON_DICT


class Serializable[TSerializeModel: t.Any = JSON_DICT](ABC):
    __slots__ = ()

    @classmethod
    @abstractmethod
    async def Deserialize(cls, data: TSerializeModel, *args: t.Any, **kwargs: t.Any) -> t.Self: ...

    @abstractmethod
    async def Serialize(self) -> TSerializeModel: ...

    @staticmethod
    def MergenDicts(*items: dict[str, t.Any], override_keys: t.Iterable[str] = ()) -> dict[str, t.Any]:
        result: dict[str, t.Any] = {}
        for item in items:
            for key in item:
                if key in result and key not in override_keys:
                    raise ValueError(f'Attempt to override key "{key}"')
            result.update(item)
        return result
