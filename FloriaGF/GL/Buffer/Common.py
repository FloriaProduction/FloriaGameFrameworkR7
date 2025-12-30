from OpenGL import GL
import typing as t
import types as ts
import numpy as np
from collections import deque
from contextlib import contextmanager

from .. import Binding, hints, Convert


def Create() -> int:
    return int(GL.glGenBuffers(1))


def Delete(*ids: int):
    GL.glDeleteBuffers(len(ids), ids)


def Data(
    type: hints.buffer_type,
    data: np.ndarray,
    usage: hints.buffet_data_usage = 'static_draw',
):
    GL.glBufferData(
        Convert.ToOpenGLBufferType(type),
        data.nbytes,
        data,
        Convert.ToOpenGLBufferDataUsage(usage),
    )


def SubData(
    type: hints.buffer_type,
    offset: int,
    data: 'np.ndarray',
):
    GL.glBufferSubData(
        Convert.ToOpenGLBufferType(type),
        offset,
        data.nbytes,
        data,
    )


_item = tuple[hints.buffer_type, int]
_stack = deque[_item]()


def _Get(item: _item):
    GL.glBindBuffer(Convert.ToOpenGLBufferType(item[0]), item[1])


def _Release(item: _item):
    GL.glBindBuffer(Convert.ToOpenGLBufferType(item[0]), 0)


@contextmanager
def Bind(type: hints.buffer_type, id: int):
    with Binding.Bind(
        _stack,
        (type, id),
        _Get,
        _Release,
        name='Buffer',
    ):
        yield
