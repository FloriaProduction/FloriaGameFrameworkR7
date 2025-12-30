import typing as t

from .Base import Component


class ContexVersion(Component):
    def __init__(
        self,
        version: int = 420,
        type: t.Literal['core'] = 'core',
    ):
        super().__init__()

        self.version = version
        self.type = type

    @property
    def source(self):
        return f'#version {self.version} {self.type}'
