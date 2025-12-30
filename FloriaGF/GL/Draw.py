import typing as t
from OpenGL import GL

# from .. import Types, Convert
from . import hints, Convert


def Arrays(
    primitive: hints.primitive,
    count: int,
    first: int = 0,
):
    GL.glDrawArrays(Convert.ToOpenGLPrimitive(primitive), first, count)


def ArraysInstanced(
    primitive: hints.primitive,
    count: int,
    instance_count: int,
    first: int = 0,
):
    GL.glDrawArraysInstanced(
        Convert.ToOpenGLPrimitive(primitive),
        first,
        count,
        instance_count,
    )


def ElementsInstanced(
    primitive: hints.primitive,
    count: int,
    instance_count: int,
):
    GL.glDrawElementsInstanced(
        Convert.ToOpenGLPrimitive(primitive),
        count,
        GL.GL_UNSIGNED_INT,
        None,
        instance_count,
    )
