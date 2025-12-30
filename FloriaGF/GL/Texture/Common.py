from OpenGL import GL
import glfw
import typing as t
import types as ts
from collections import deque
from contextlib import contextmanager
import asyncio
import numpy as np

from ... import Types
from .. import Binding, hints, Convert


def Create() -> int:
    return int(GL.glGenTextures(1))


def Delete(id: int):
    GL.glDeleteTextures(1, [id])


def TexImage2D(
    size: Types.hints.size_2d,
    data: t.Optional[np.ndarray],
    type: hints.texture_type = 'texture_2d',
    internal_format: hints.texture_internal_format = 'rgba',
    format: hints.texture_format = 'rgba',
    border: int = 0,
    pixel_type: hints.texture_pixel_type = 'unsigned_byte',
    level: int = 0,
    context_version: t.Optional[Types.hints.context_version] = None,
):
    GL.glTexImage2D(
        Convert.ToOpenGLTextureType(type, context_version),
        level,
        Convert.ToOpenGLTextureInternalFormat(internal_format, context_version),
        *size,
        border,
        Convert.ToOpenGLTextureFormat(format, context_version),
        Convert.ToOpenGLType(pixel_type, context_version),
        data,
    )


def TexStorage3D(
    size: Types.hints.size_3d,
    type: hints.texture_type = 'texture_2d',
    internal_format: hints.texture_internal_format = 'rgba8',
    levels: int = 1,
    context_version: t.Optional[Types.hints.context_version] = None,
):
    GL.glTexStorage3D(
        Convert.ToOpenGLTextureType(type, context_version),
        levels,
        Convert.ToOpenGLTextureInternalFormat(internal_format, context_version),
        *size,
    )


def TexSubImage3D(
    size: Types.hints.size_3d,
    pixels: np.ndarray,
    type: hints.texture_type = 'texture_2d',
    *,
    format: hints.texture_format = 'rgba',
    pixel_type: hints.texture_pixel_type = 'unsigned_byte',
    offset: Types.hints.offset_3d = (0, 0, 0),
    levels: int = 0,
    context_version: t.Optional[Types.hints.context_version] = None,
):
    GL.glTexSubImage3D(
        Convert.ToOpenGLTextureType(type),
        levels,
        *offset,
        *size,
        Convert.ToOpenGLTextureFormat(format),
        Convert.ToOpenGLType(pixel_type, context_version),
        pixels,
    )


def TexParameterWrap(
    type: hints.texture_type,
    wrap_t: hints.texture_wrap,
    wrap_s: hints.texture_wrap,
    context_version: Types.hints.context_version,
):
    gl_type = Convert.ToOpenGLTextureType(type)

    GL.glTexParameter(
        gl_type,
        GL.GL_TEXTURE_WRAP_T,
        Convert.ToOpenGLTextureWrap(wrap_t, context_version),
    )
    GL.glTexParameter(
        gl_type,
        GL.GL_TEXTURE_WRAP_S,
        Convert.ToOpenGLTextureWrap(wrap_s, context_version),
    )


def TexParameterFilter(
    type: hints.texture_type,
    min_filter: hints.texture_filter,
    mag_filter: hints.texture_filter,
    context_version: Types.hints.context_version,
):
    gl_type = Convert.ToOpenGLTextureType(type)

    GL.glTexParameter(
        gl_type,
        GL.GL_TEXTURE_MIN_FILTER,
        Convert.ToOpenGLTextureFilter(min_filter, context_version),
    )
    GL.glTexParameter(
        gl_type,
        GL.GL_TEXTURE_MAG_FILTER,
        Convert.ToOpenGLTextureFilter(mag_filter, context_version),
    )


_item = tuple[hints.texture_type, int]
_stack = deque[_item]()


def _Get(item: _item):
    GL.glBindTexture(Convert.ToOpenGLTextureType(item[0]), item[1])


def _Release(item: _item):
    GL.glBindTexture(Convert.ToOpenGLTextureType(item[0]), 0)


@contextmanager
def Bind(type: hints.texture_type, id: int):
    with Binding.Bind(
        _stack,
        (type, id),
        _Get,
        _Release,
        name='Texture',
    ):
        yield
