import typing as t

from OpenGL import GL
from contextlib import contextmanager

from ... import Abc
from .ShaderProgram import ShaderProgram, ShaderConstuct, C


class CameraVertexShader(ShaderConstuct):
    camera = C.UniformBlock(
        'Camera',
        (
            {'name': 'projection', 'type': 'mat4'},
            {'name': 'view', 'type': 'mat4'},
            {'name': 'resolution', 'type': 'vec2'},
        ),
    )


class CameraShaderProgram(
    ShaderProgram,
    Abc.Graphic.ShaderPrograms.BatchShaderProgram,
):
    __vertex__ = CameraVertexShader

    @contextmanager
    def Bind(self, camera: Abc.Camera, *args: t.Any, **kwargs: t.Any):
        with super().Bind():
            GL.glBindBufferBase(
                GL.GL_UNIFORM_BUFFER,
                self.GetUniformBlockLocation('Camera'),
                camera.ubo.id,
            )

            yield self

    @classmethod
    def GetCameraUBOAttributeItems(cls) -> tuple[Abc.Graphic.ShaderPrograms.SchemeItem, ...]:
        return t.cast(CameraVertexShader, cls.__vertex__).camera.GetScheme()
