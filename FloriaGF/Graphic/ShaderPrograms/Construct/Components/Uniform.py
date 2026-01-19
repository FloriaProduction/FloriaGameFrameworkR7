import typing as t

from .Base import ComponentNamed
from .Struct import Struct
from ..... import GL, Abc


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

    def GetSource(self) -> str:
        return f'uniform {self.type} {self.name}{f' = {self.value}' if self.value is not None else ''};'


class UniformBlock(ComponentNamed):
    def __init__(
        self,
        fields_or_struct: t.Sequence[Abc.Graphic.ShaderPrograms.SchemeItem] | Struct,
        block_name: t.Optional[str] = None,
        layout: t.Optional[str] = "std140",
        binding: t.Optional[int] = None,
        name: t.Optional[str] = None,
    ):
        super().__init__(name)

        self.fields_or_struct = fields_or_struct
        self.block_name = block_name
        self.layout = layout
        self.binding = binding

    def GetBlockName(self) -> str:
        name: t.Optional[str] = self.block_name

        if isinstance(fos := self.fields_or_struct, Struct):
            name = fos.name

        if name is None:
            raise

        return name

    def GetScheme(self) -> tuple[Abc.Graphic.ShaderPrograms.SchemeItem, ...]:
        return fos.fields if isinstance(fos := self.fields_or_struct, Struct) else tuple(fos)

    def GetSource(self) -> str:
        return f'''
        {
            ''
            if self.layout is None and self.binding is None
            else 
            f'layout ({
                ', '.join(item for item in (
                    self.layout,
                    None if self.binding is None else f'binding = {self.binding}'    
                ) if item is not None)    
            })'
        }
        uniform {self.GetBlockName()} 
        {{{
            '\n'.join(f'{field["type"]} {field['name']};' for field in self.GetScheme())
        }}} {'' if self.name is None else self.name};
        '''
