import typing as t
from contextlib import contextmanager, asynccontextmanager
from uuid import UUID, uuid4

from ... import Abc, Validator


class Material[
    TProgram: Abc.Graphic.ShaderPrograms.BatchShaderProgram,
](
    Abc.Graphic.Materials.Material[TProgram],
):
    __slots__ = (
        '_id',
        '_name',
        '_program',
    )

    def __init__(
        self,
        program: TProgram,
        name: t.Optional[str] = None,
    ):
        self._id: UUID = uuid4()
        self._name: t.Optional[str] = name

        self._program: TProgram = t.cast(TProgram, Validator.Instance(program, Abc.ShaderProgram))

    class Modify_Kwargs(
        t.TypedDict,
        total=False,
    ):
        name: t.Optional[str]

    def Modify(self, **kwargs: t.Unpack[Modify_Kwargs]):
        return self.__class__(
            self.program,
            kwargs.get('name', self.name),
        )

    @contextmanager
    def Bind(self, camera: Abc.Camera, *args: t.Any, **kwargs: t.Any):
        with self.program.Bind(camera):
            yield self

    @property
    def program(self) -> TProgram:
        return self._program

    def GetID(self):
        return self._id

    def GetName(self) -> t.Optional[str]:
        return self._name

    def GetSignature(self) -> int:
        return hash((self.program.id,))
