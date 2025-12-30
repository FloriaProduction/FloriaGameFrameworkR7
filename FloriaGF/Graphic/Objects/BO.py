import typing as t

from contextlib import contextmanager, asynccontextmanager
import functools

from ... import Utils, Abc, Convert, GL

if t.TYPE_CHECKING:
    import numpy as np

    from ... import Types, GL


class BO(
    Abc.Mixins.ID[int],
    Abc.Mixins.Binding,
    Abc.Mixins.Disposable,
):
    '''
    Все методы требуют контекста OpenGL
    '''

    __slots__ = ('_window', '_type', '_id', '_usage')

    def __init__(self, window: Abc.Window, type: 'GL.hints.buffer_type' = 'array_buffer', *args: t.Any, **kwargs: t.Any):
        self._window = window

        self._type: 'GL.hints.buffer_type' = type
        self._id: int = GL.Buffer.Create()
        self._usage: t.Optional['GL.hints.buffet_data_usage'] = None

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        with self.window.Bind():
            GL.Buffer.Delete(self.id)

    def SetData(self, data: 'np.ndarray', usage: 'GL.hints.buffet_data_usage' = 'static_draw'):
        GL.Buffer.Data(self.type, data, usage)
        self._usage = usage

    def SetSubData(self, offset: int, data: 'np.ndarray'):
        GL.Buffer.SubData(self.type, offset, data)

    @contextmanager
    def Bind(self):
        with GL.Buffer.Bind(self.type, self.id):
            yield self

    def GetID(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def type_gl(self):
        return GL.Convert.ToOpenGLBufferType(self.type)

    @property
    def window(self):
        return self._window

    @property
    def usage(self):
        if self._usage is None:
            raise RuntimeError()
        return self._usage

    @property
    def usage_gl(self):
        return GL.Convert.ToOpenGLBufferDataUsage(self.usage)
