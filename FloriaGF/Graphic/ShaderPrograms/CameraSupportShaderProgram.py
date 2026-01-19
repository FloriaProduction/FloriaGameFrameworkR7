import typing as t
from contextlib import contextmanager

from ... import Abc
from .ShaderProgram import ShaderProgram
from .Construct import ShaderConstuct, Components as C


class CameraVertexShader(ShaderConstuct):
    camera = C.UniformBlock(
        (
            {'name': 'projection', 'type': 'mat4'},
            {'name': 'view', 'type': 'mat4'},
            {'name': 'resolution', 'type': 'vec2'},
        ),
        'CameraData',
    )


class CameraShaderProgram(
    ShaderProgram,
    Abc.Graphic.ShaderPrograms.BatchShaderProgram,
):
    __vertex__ = CameraVertexShader

    @contextmanager
    def Bind(self, camera: Abc.Camera, *args: t.Any, **kwargs: t.Any):
        with super().Bind():
            self.BindUniformBlock(
                'CameraData',
                camera.GetInstanceData(),
            )

            yield self

    @classmethod
    def GetStruct(cls, name: str):
        if name == 'CameraData':
            return t.cast(CameraVertexShader, cls.__vertex__).camera.GetScheme()
        return super().GetStruct(name)
