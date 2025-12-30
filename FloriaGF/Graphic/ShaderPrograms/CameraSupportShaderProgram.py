import typing as t

from OpenGL import GL
from contextlib import contextmanager

from ... import Abc
from .ShaderProgram import ShaderProgram, ShaderConstuct, C


class CameraVertexShader(ShaderConstuct):
    camera = C.Paste(
        '''
        layout (std140) uniform Camera {
            mat4 projection;
            mat4 view;
            vec2 resolution;
        } camera;
        '''
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
