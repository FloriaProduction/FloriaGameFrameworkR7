from abc import ABC, abstractmethod
import typing as t


class Simulatable(ABC):
    @abstractmethod
    def Simulate(self, *args: t.Any, **kwargs: t.Any): ...


class SimulatableAsync(ABC):
    @abstractmethod
    async def Simulate(self, *args: t.Any, **kwargs: t.Any): ...


SimulatableAny = t.Union[
    Simulatable,
    SimulatableAsync,
]
