from OpenGL import GL
import typing as t
import types as ts
import numpy as np
from collections import deque
from contextlib import contextmanager
import asyncio

from ... import Types, Validator
from .. import Binding, hints, Convert
from ..Common import Viewport

if t.TYPE_CHECKING:
    from ...Graphic.Objects.Texture import Texture


def Create() -> int:
    return int(GL.glGenFramebuffers(1))


def Delete(*ids: int):
    GL.glDeleteFramebuffers(len(ids), ids)


def AttachTexture2D[TTex: 'Texture | int'](
    texture: TTex,
    attachment: hints.framebuffer_texture_2d_attachment,
    *,
    target: hints.framebuffer_texture_2d_target = 'framebuffer',
    texture_target: t.Optional[hints.texture_type] = None,  # = 'texture_2d',
    level: int = 0,
) -> TTex:
    GL.glFramebufferTexture2D(
        Convert.ToOpenGLFramebufferTexture2DTarget(target),
        Convert.ToOpenGLFramebufferTexture2DAttachment(attachment),
        Convert.ToOpenGLTextureType(
            (Validator.Raiser('') if isinstance(texture, int) else texture.type) if texture_target is None else texture_target
        ),
        texture if isinstance(texture, int) else texture.id,
        level,
    )
    return texture


def CheckStatus():
    if (status := GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)) != GL.GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError(f'Framebuffer is not complete!\nStatus: {status}')


_item = tuple[int, Types.hints.size_2d]
_stack = deque[_item]()


def _Get(item: _item):
    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, item[0])
    Viewport((0, 0), item[1])


def _Release(item: _item):
    GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)


@contextmanager
def Bind(id: int, size: Types.hints.size_2d):
    with Binding.Bind(
        _stack,
        (id, size),
        _Get,
        _Release,
        name='FrameBuffer',
    ):
        yield
