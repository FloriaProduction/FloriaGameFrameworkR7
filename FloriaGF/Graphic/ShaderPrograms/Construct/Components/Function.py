import typing as t

from .Base import ComponentNamed


class Function(ComponentNamed):
    def __init__(
        self,
        source: str,
        name: t.Optional[str] = None,
    ):
        super().__init__(name)

        self.source = source
