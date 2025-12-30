import typing as t
from OpenGL import GL
import functools

from .. import Types
from . import hints, Convert


def ClearColor(color: Types.hints.rgba | Types.hints.rgb):
    values: tuple[int, ...] = (*color,)

    if len(values) < 4:
        values = (*values, 255)

    GL.glClearColor(*(x / 255 for x in values))


def Clear(*masks: hints.mask):
    GL.glClear(
        functools.reduce(
            lambda x, y: x | y,
            (Convert.ToOpenGLMask(mask) for mask in masks),
            0,
        ),
    )


def Viewport(
    offset: Types.hints.offset_2d,
    size: Types.hints.size_2d,
):
    GL.glViewport(*offset, *size)


def DepthFunc(value: hints.depth_func):
    GL.glDepthFunc(Convert.ToDepthFunc(value))


def BlendEquation(value: hints.blend_equation):
    GL.glBlendEquation(Convert.ToOpenGLBlendEquation(value))


def BlendFactors(blend_factors: tuple[hints.blend_factor, hints.blend_factor]):
    GL.glBlendFunc(*(Convert.ToOpenGLBlendFactor(factor) for factor in blend_factors))
