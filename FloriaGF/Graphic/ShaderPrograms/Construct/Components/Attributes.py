import typing as t

from ..... import GL, Validator
from .Base import ComponentNamed


class Attrib(ComponentNamed):
    def __init__(
        self,
        type: GL.hints.glsl_type,
        name: t.Optional[str] = None,
        instanced: bool = False,
    ):
        super().__init__(name)

        self.type: GL.hints.glsl_type = type
        self.instanced: bool = instanced

        self.index: t.Optional[int] = None

    def GetSource(self) -> str:
        return f'layout(location = {Validator.NotNone(self.index)}) in {self.type} {Validator.NotNone(self.name)};'


class AttribInst(Attrib):
    def __init__(
        self,
        type: GL.hints.glsl_type,
        name: t.Optional[str] = None,
    ):
        super().__init__(type, name, True)


class AttribVertice(Attrib):
    def __init__(
        self,
        type: GL.hints.glsl_type,
    ):
        super().__init__(type, None, False)

    def SetName(self, name: str):
        if name != 'vertice':
            raise ValueError()
        return super().SetName(name)


class AttribTexcoord(Attrib):
    def __init__(
        self,
        type: GL.hints.glsl_type,
    ):
        super().__init__(type, None, False)

    def SetName(self, name: str):
        if name != 'texcoord':
            raise ValueError()
        return super().SetName(name)
