import typing as t

import numpy as np
from contextlib import contextmanager, asynccontextmanager
import ctypes

from ... import Abc, Convert, GL

if t.TYPE_CHECKING:
    from ... import Types, GL


class VAO(
    Abc.Mixins.ID[int],
    Abc.Mixins.Binding,
    Abc.Mixins.Disposable,
):
    '''
    Все методы требуют контекста OpenGL
    '''

    __slots__ = (
        '_window',
        '_id',
    )

    def __init__(
        self,
        window: Abc.Window,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        self._window = window

        self._id: int = GL.VAO.Create()

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        with self.Bind():
            GL.VAO.Delete(self.id)

    def VertexAttribPointer(
        self,
        index: int,
        type: 'GL.hints.glsl_type',
        stride: int = 0,
        pointer: int = 0,
        *,
        attrib_divisor: int = 0,
        enable_attrib_array: bool = True,
    ):
        GL.VAO.VertexAttribPointer(
            index,
            type,
            stride,
            pointer,
            attrib_divisor=attrib_divisor,
            enable_attrib_array=enable_attrib_array,
        )

    @contextmanager
    def Bind(self):
        with GL.VAO.Bind(self.id):
            yield self

    def GetID(self):
        return self._id

    @property
    def window(self):
        return self._window

    @classmethod
    def NewQuad(cls, window: Abc.Window):
        from .BO import BO

        vao: VAO = VAO(window)
        with vao.Bind() as vao:

            vbo: BO = BO(window)
            with vbo.Bind() as vbo:
                vbo.SetData(
                    np.array(
                        [
                            -1,
                            -1,
                            1,
                            0,
                            1,
                            -1,
                            0,
                            0,
                            1,
                            1,
                            0,
                            1,
                            -1,
                            1,
                            1,
                            1,
                        ],
                        dtype=np.float32,
                    )
                )

                float_size = ctypes.sizeof(ctypes.c_float)

                vao.VertexAttribPointer(0, 'vec2', 4 * float_size, 0 * float_size)
                vao.VertexAttribPointer(1, 'vec2', 4 * float_size, 2 * float_size)

        return vao
