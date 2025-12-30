import typing as t

import numpy as np
from contextlib import contextmanager

from ... import Types, Abc, GL

if t.TYPE_CHECKING:
    from PIL import Image


class Texture(
    Abc.Mixins.ID[int],
    Abc.Mixins.Binding,
    Abc.Mixins.Disposable,
):
    '''
    Все методы требуют контекста OpenGL
    '''

    __slots__ = ('_window', '_type', '_id', '_size', '_depth')

    def __init__(
        self,
        window: Abc.Window,
        type: GL.hints.texture_type = 'texture_2d',
        *,
        wrap_t: GL.hints.texture_wrap = 'clamp',
        wrap_s: GL.hints.texture_wrap = 'clamp',
        min_filter: GL.hints.texture_filter = 'nearest',
        mag_filter: GL.hints.texture_filter = 'nearest',
        **kwargs: t.Any,
    ):
        self._window = window

        self._type: GL.hints.texture_type = type
        self._id: int = GL.Texture.Create()
        self._size: Types.Vec2[int] = Types.Vec2(0, 0)
        self._depth: int = 0

        self.TexParameter(
            wrap_t=wrap_t,
            wrap_s=wrap_s,
            min_filter=min_filter,
            mag_filter=mag_filter,
        )

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        with self.window.Bind():
            GL.Texture.Delete(self.id)

    def TexParameter(
        self,
        *,
        wrap_t: GL.hints.texture_wrap,
        wrap_s: GL.hints.texture_wrap,
        min_filter: GL.hints.texture_filter,
        mag_filter: GL.hints.texture_filter,
    ):
        with self.Bind():
            GL.Texture.TexParameterWrap(
                self.type,
                wrap_t,
                wrap_s,
                self.window.context_version,
            )
            GL.Texture.TexParameterFilter(
                self.type,
                min_filter,
                mag_filter,
                self.window.context_version,
            )

    def TexImage2D(
        self,
        size: Types.hints.size_2d,
        data: t.Optional[np.ndarray] = None,
        *,
        internal_format: GL.hints.texture_internal_format = 'rgba',
        format: GL.hints.texture_format = 'rgba',
        border: int = 0,
        pixel_type: GL.hints.texture_pixel_type = 'unsigned_byte',
        level: int = 0,
        context_version: t.Optional[Types.hints.context_version] = None,
    ):
        if self.type != 'texture_2d':
            raise RuntimeError()

        GL.Texture.TexImage2D(
            size,
            data,
            self.type,
            internal_format,
            format,
            border,
            pixel_type,
            level,
            context_version,
        )

        self._size = Types.Vec2[int].New(size)
        self._depth = 1

    def TexStorage3D(self, layers: t.Sequence['Image.Image']):
        if self.type != 'texture_2d_array':
            raise RuntimeError()

        width, height = layers[0].size
        depth = len(layers)

        if depth == 0:
            raise ValueError()

        pixels = np.empty((depth, height, width, 4), dtype=np.uint8)
        for i, layer in enumerate(layers):
            pixels[i] = np.array(layer)

        size_3d = (width, height, depth)

        GL.Texture.TexStorage3D(size_3d, self.type)
        GL.Texture.TexSubImage3D(size_3d, pixels, self.type)

        self._size = Types.Vec2(width, height)
        self._depth = depth

    def GetID(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def type_gl(self):
        return GL.Convert.ToOpenGLTextureType(self.type)

    @property
    def size(self):
        return self._size

    @contextmanager
    def Bind(self):
        with GL.Texture.Bind(self.type, self.id):
            yield self

    @property
    def window(self):
        return self._window
