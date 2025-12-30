import typing as t

from contextlib import contextmanager, asynccontextmanager

from ... import Abc, GL, Types
from .Texture import Texture


class FBO(
    Abc.Mixins.ID[int],
    Abc.Mixins.Binding,
    Abc.Mixins.Disposable,
):
    '''
    Все методы требуют контекста OpenGL
    '''

    __slots__ = (
        '_window',
        '_size',
        '_id',
        '_texture',
        '_depth_texture',
    )

    def __init__(
        self,
        window: Abc.Window,
        size: Types.hints.size_2d,
        *args: t.Any,
        depth: bool = True,
        **kwargs: t.Any,
    ):
        self._window = window

        self._size: tuple[int, int] = Types.Vec2[int].New(size)
        self._id: int = GL.Framebuffer.Create()

        with self.Bind():
            self._texture: Texture = Texture(window)
            with self._texture.Bind():
                self._texture.TexImage2D(size)
            GL.Framebuffer.AttachTexture2D(self._texture, 'color_attachment_0')

            self._depth_texture: t.Optional[Texture] = Texture(window) if depth else None
            if self._depth_texture is not None:
                with self._depth_texture.Bind():
                    self._depth_texture.TexImage2D(
                        size,
                        internal_format='depth_component',
                        format='depth_component',
                        pixel_type='float',
                    )
                GL.Framebuffer.AttachTexture2D(self._depth_texture, 'depth_attachment')

            GL.Framebuffer.CheckStatus()

    def Dispose(self, *args: t.Any, **kwargs: t.Any):
        with self.window.Bind():
            GL.Framebuffer.Delete(self.id)

            self._texture.Dispose()
            if self._depth_texture is not None:
                self._depth_texture.Dispose()

    @contextmanager
    def Bind(self):
        with GL.Framebuffer.Bind(self.id, self.size):
            yield self

    def GetID(self):
        return self._id

    @property
    def texture(self):
        return self._texture

    @property
    def texture_depth(self):
        return self._depth_texture

    @property
    def size(self):
        return self._size

    @property
    def window(self):
        return self._window
