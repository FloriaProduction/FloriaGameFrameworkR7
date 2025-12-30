from OpenGL import GL
import typing as t
import numpy as np
from collections import deque
from contextlib import contextmanager
import ctypes

from .. import Binding, hints, Convert


def Create() -> int:
    return int(GL.glGenVertexArrays(1))


def Delete(*ids: int):
    GL.glDeleteVertexArrays(len(ids), ids)


def VertexAttribPointer(
    index: int,
    type: hints.glsl_type,
    stride: int = 0,
    pointer: int = 0,
    *,
    attrib_divisor: int = 0,
    enable_attrib_array: bool = True,
):
    def _VertexAttribPointer(
        index: int,
        type: hints.np_type,
        size: int,
        stride: int,
        pointer: int,
    ):
        gl_type = Convert.NumpyToOpenGLType(type)
        ctype_pointer = ctypes.c_void_p(pointer)

        if enable_attrib_array:
            GL.glEnableVertexAttribArray(index)

        match type:
            case np.float32:
                GL.glVertexAttribPointer(
                    index,
                    size,
                    gl_type,
                    GL.GL_FALSE,
                    stride,
                    ctype_pointer,
                )

            case np.int32 | np.uint32:
                GL.glVertexAttribIPointer(
                    index,
                    size,
                    gl_type,
                    stride,
                    ctype_pointer,
                )

            case _:
                raise ValueError()

        if attrib_divisor > 0:
            GL.glVertexAttribDivisor(index, attrib_divisor)

    match type:
        case 'mat3':
            offset = 3 * ctypes.sizeof(ctypes.c_float)
            for i in range(3):
                _VertexAttribPointer(
                    index + i,
                    np.float32,
                    3,
                    stride,
                    pointer + i * offset,
                )

        case 'mat4':
            offset = 4 * ctypes.sizeof(ctypes.c_float)
            for i in range(4):
                _VertexAttribPointer(
                    index + i,
                    np.float32,
                    4,
                    stride,
                    pointer + i * offset,
                )

        case _:
            np_type, size = Convert.GLSLTypeToNumpy(type)

            _VertexAttribPointer(
                index,
                np_type,
                sum(size),
                stride,
                pointer,
            )


_stack = deque[int]()


def _Get(id: int):
    GL.glBindVertexArray(id)


def _Release(id: int):
    GL.glBindVertexArray(0)


@contextmanager
def Bind(id: int):
    with Binding.Bind(
        _stack,
        id,
        _Get,
        _Release,
        name='VAO',
    ):
        yield
