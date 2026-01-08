import typing as t

from .Base import ComponentNamed
from ..... import GL


class Param(ComponentNamed):
    def __init__(
        self,
        direction: t.Literal['in', 'out'],
        type: GL.hints.glsl_type,
        name: t.Optional[str] = None,
    ):
        super().__init__(name)

        self.type: GL.hints.glsl_type = type
        self.direction = direction

    def GetSource(self) -> str:
        return f'{'flat' if self.type in ('int', 'uint') else ''} {self.direction} {self.type} {self.name};'


class ParamIn(Param):
    def __init__(
        self,
        type: GL.hints.glsl_type,
        name: t.Optional[str] = None,
    ):
        super().__init__('in', type, name)


class ParamOut(Param):
    def __init__(
        self,
        type: GL.hints.glsl_type,
        name: t.Optional[str] = None,
    ):
        super().__init__('out', type, name)
