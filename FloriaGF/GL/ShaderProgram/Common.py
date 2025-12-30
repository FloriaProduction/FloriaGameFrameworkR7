from OpenGL import GL
import glfw
import typing as t
import types as ts
from collections import deque
from contextlib import contextmanager, asynccontextmanager
import asyncio

from .. import Binding


def Create() -> int:
    return int(GL.glCreateProgram())


def Delete(id: int):
    GL.glDeleteProgram(id)


def Attach(id: int, *shader_ids: int):
    for shader_id in shader_ids:
        GL.glAttachShader(id, shader_id)


def Link(id: int):
    GL.glLinkProgram(id)
    if GL.glGetProgramiv(id, GL.GL_LINK_STATUS) == GL.GL_FALSE:
        raise RuntimeError(GL.glGetProgramInfoLog(id).decode())


def Validate(id: int):
    GL.glValidateProgram(id)
    if GL.glGetProgramiv(id, GL.GL_VALIDATE_STATUS) == GL.GL_FALSE:
        raise RuntimeError(GL.glGetProgramInfoLog(id).decode())


def GetUniformLocation(id: int, name: str) -> int:
    return GL.glGetUniformLocation(id, name)


def GetUniformBlockIndex(id: int, name: str) -> int:
    if (index := GL.glGetUniformBlockIndex(id, name)) == GL.GL_INVALID_INDEX:
        raise
    return index


_stack = deque[int]()


def _Get(id: int):
    GL.glUseProgram(id)


def _Release(id: int):
    GL.glUseProgram(0)


@contextmanager
def Bind(id: int):
    with Binding.Bind(
        _stack,
        id,
        _Get,
        _Release,
        name='ShaderProgram',
    ):
        yield
