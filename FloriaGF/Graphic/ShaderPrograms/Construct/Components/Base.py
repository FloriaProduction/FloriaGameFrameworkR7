import typing as t
from abc import ABC


class Component(ABC):
    pass


class ComponentNamed(Component):
    def __init__(self, name: t.Optional[str] = None):
        super().__init__()

        self._name: t.Optional[str] = name

    def SetName(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self.SetName(value)

    def __str__(self) -> str:
        if self.name is None:
            raise ValueError()
        return self.name
