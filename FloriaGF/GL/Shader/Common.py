from OpenGL import GL
import glfw
import typing as t
import types as ts
from collections import deque
from contextlib import contextmanager

from .. import Binding, hints, Convert


def Create(type: hints.shader_type, source: str, /) -> int:
    if (id := GL.glCreateShader(Convert.ToOpenGLShaderType(type))) is None:
        raise

    GL.glShaderSource(id, source)
    GL.glCompileShader(id)

    if GL.glGetShaderiv(id, GL.GL_COMPILE_STATUS) == GL.GL_FALSE:
        raise RuntimeError(f'error: {GL.glGetShaderInfoLog(id)}\nsource: {source}')

    return int(id)


def Delete(*ids: int):
    for id in ids:
        GL.glDeleteShader(id)


_stack = deque[int]()


def _Get(id: int):
    glfw.make_context_current(id)


def _Release(id: int):
    glfw.make_context_current(None)


@contextmanager
def Bind(id: int):
    with Binding.Bind(
        _stack,
        id,
        _Get,
        _Release,
        name='Shader',
    ):
        yield
