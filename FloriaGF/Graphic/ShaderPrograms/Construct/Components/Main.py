from .Function import Function


class Main(Function):
    def __init__(self, source: str):
        super().__init__('void main() ' + source)
