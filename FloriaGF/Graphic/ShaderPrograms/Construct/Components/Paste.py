from .Base import Component


class Paste(Component):
    def __init__(self, source: str):
        super().__init__()

        self.source = source
