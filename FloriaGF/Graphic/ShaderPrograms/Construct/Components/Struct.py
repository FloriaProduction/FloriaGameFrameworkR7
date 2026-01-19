import typing as t

from .Base import ComponentNamed
from ..... import GL, Abc


class Struct(ComponentNamed):
    def __init__(
        self,
        *fields: Abc.Graphic.ShaderPrograms.SchemeItem,
        name: t.Optional[str] = None,
    ):
        super().__init__(name)

        self.fields = tuple(fields)

    def GetSource(self) -> str:
        return f'''
        struct  {self.name}
        {{
            {'\n'.join(f'{field['type']} {field['name']};' for field in self.fields)}
        }};
        '''
