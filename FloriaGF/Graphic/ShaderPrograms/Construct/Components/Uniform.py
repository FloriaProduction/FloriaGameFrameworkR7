import typing as t

from .Base import ComponentNamed
from ..... import GL


class Uniform(ComponentNamed):
    def __init__(
        self,
        type: GL.hints.glsl_type,
        value: t.Optional[str | int | float] = None,
        name: t.Optional[str] = None,
    ):
        super().__init__(name)

        self.type: GL.hints.glsl_type = type
        self.value: t.Optional[str] = f'{value}' if value is not None else None
