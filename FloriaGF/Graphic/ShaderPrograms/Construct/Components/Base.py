import typing as t
from abc import ABC, abstractmethod


class Component(ABC):
    @abstractmethod
    def GetSource(self) -> str: ...


class ComponentNamed(Component):
    __auto_name__: bool = True
    '''Если включено и не задано имя, автоматически подставит его из переменной, к которой присвоен компонент.'''

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
