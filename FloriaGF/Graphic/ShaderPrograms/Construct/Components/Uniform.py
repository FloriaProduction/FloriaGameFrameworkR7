import typing as t

from .Base import ComponentNamed
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
        block_name: str,
        fields: t.Sequence[Abc.Graphic.ShaderPrograms.SchemeItem],
        layout: t.Optional[str] = "std140",
        binding: t.Optional[int] = None,
        name: t.Optional[str] = None,
    ):
        super().__init__(name)

        self.block_name = block_name
        self.fields = tuple(fields)
        self.layout = layout
        self.binding = binding

    def GetScheme(self) -> tuple[Abc.Graphic.ShaderPrograms.SchemeItem, ...]:
        return self.fields

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
        uniform {self.block_name} 
        {{{
            '\n'.join(f'{field["type"]} {field['name']};' for field in self.fields)
        }}} {'' if self.name is None else self.name};
        '''
