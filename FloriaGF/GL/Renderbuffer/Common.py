from OpenGL import GL
import typing as t
from collections import deque
from contextlib import contextmanager
import asyncio

from ... import Types
from .. import Binding


def Create() -> int:
    return int(GL.glGenRenderbuffers(1))


def Delete(id: int):
    GL.glDeleteRenderbuffers(1, [id])


def Storage(size: Types.hints.size_2d):
    GL.glRenderbufferStorage(
        GL.GL_RENDERBUFFER,
        GL.GL_DEPTH24_STENCIL8,
        *size,
    )


_stack = deque[int]()


def _Get(id: int):
    GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, id)


def _Release(id: int):
    GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, 0)


@contextmanager
def Bind(id: int):
    with Binding.Bind(
        _stack,
        id,
        _Get,
        _Release,
        name='RenderBuffer',
    ):
        yield
