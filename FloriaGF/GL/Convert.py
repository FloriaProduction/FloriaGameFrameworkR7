import typing as t
import numpy as np
from OpenGL import GL

from .. import Exceptions
from ..Config import Config
from . import hints
from .. import Types


TKey = t.TypeVar('TKey', covariant=True)
TValue = t.TypeVar('TValue', covariant=True)


def _GetFromDict(
    data: t.Mapping[
        TKey,
        t.Union[
            t.Mapping[Types.hints.context_version, TValue],
            TValue,
        ],
    ],
    key: TKey,
    context: t.Optional[Types.hints.context_version] = None,
) -> TValue:
    if (result := data.get(key)) is None:
        raise Exceptions.ConvertError(f'Unsupported value: {key}. Supported values: {', '.join(map(str, data.keys()))}')

    if not isinstance(result, t.Mapping):
        return result

    result = t.cast(t.Mapping[Types.hints.context_version, TValue], result)

    if context is None:
        context = Config.CONTEXT_VERSIONS

    for context_check in sorted(result.keys(), reverse=True):
        if context >= context_check:
            return result[context_check]

    raise Exceptions.ConvertError(
        f'Unsupported context version: {context}. Supported versions: {', '.join(map(str, result.keys()))}'
    )


_GLSLTypeToNumpy_data: dict[hints.glsl_type, tuple[np.typing.DTypeLike, tuple[int, ...]]] = {
    'float': (np.float32, (1,)),
    'int': (np.int32, (1,)),
    'uint': (np.uint32, (1,)),
    'vec2': (np.float32, (2,)),
    'vec3': (np.float32, (3,)),
    'vec4': (np.float32, (4,)),
    'mat3': (np.float32, (3, 3)),
    'mat4': (np.float32, (4, 4)),
}


def GLSLTypeToNumpy(
    value: hints.glsl_type,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> tuple[np.typing.DTypeLike, tuple[int, ...]]:
    return _GetFromDict(_GLSLTypeToNumpy_data, value, context_version)


_NumpyToOpenGLType_data: dict[hints.np_type, int] = {
    np.float32: GL.GL_FLOAT,
    np.int32: GL.GL_INT,
    np.uint32: GL.GL_UNSIGNED_INT,
}


def NumpyToOpenGLType(
    type: hints.np_type,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_NumpyToOpenGLType_data, type, context_version)


_ToDepthFunc_data: dict[hints.depth_func, int] = {
    'always': GL.GL_ALWAYS,
    'equal': GL.GL_EQUAL,
    'gequal': GL.GL_GEQUAL,
    'greater': GL.GL_GREATER,
    'lequal': GL.GL_LEQUAL,
    'less': GL.GL_LESS,
    'never': GL.GL_NEVER,
    'notequal': GL.GL_NOTEQUAL,
}


def ToDepthFunc(
    value: hints.depth_func,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> t.Optional[int]:
    return _GetFromDict(_ToDepthFunc_data, value, context_version)


def ToOpenGLBool(value: bool) -> int:
    return GL.GL_TRUE if value else GL.GL_FALSE


_ToOpenGLBlendEquation_data: dict[hints.blend_equation, int] = {
    'func_add': GL.GL_FUNC_ADD,
    'func_reverse_subtract': GL.GL_FUNC_REVERSE_SUBTRACT,
    'func_subtract': GL.GL_FUNC_SUBTRACT,
    'max': GL.GL_MAX,
    'min': GL.GL_MIN,
}


def ToOpenGLBlendEquation(
    value: hints.blend_equation,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLBlendEquation_data, value, context_version)


_ToOpenGLBlendFactor_data: dict[hints.blend_factor, int] = {
    'constant_alpha': GL.GL_CONSTANT_ALPHA,
    'constant_color': GL.GL_CONSTANT_COLOR,
    'dst_alpha': GL.GL_DST_ALPHA,
    'dst_color': GL.GL_DST_COLOR,
    'one': GL.GL_ONE,
    'one_minus_constant_alpha': GL.GL_ONE_MINUS_CONSTANT_ALPHA,
    'one_minus_constant_color': GL.GL_ONE_MINUS_CONSTANT_COLOR,
    'one_minus_dst_alpha': GL.GL_ONE_MINUS_DST_ALPHA,
    'one_minus_src1_alpha': GL.GL_ONE_MINUS_SRC1_ALPHA,
    'one_minus_src1_color': GL.GL_ONE_MINUS_SRC1_COLOR,
    'one_minus_src_alpha': GL.GL_ONE_MINUS_SRC_ALPHA,
    'one_minus_src_color': GL.GL_ONE_MINUS_SRC_COLOR,
    'src1_alpha': GL.GL_SRC1_ALPHA,
    'src1_color': GL.GL_SRC1_COLOR,
    'src_alpha_saturate': GL.GL_SRC_ALPHA_SATURATE,
    'src_color': GL.GL_SRC_COLOR,
    'src_alpha': GL.GL_SRC_ALPHA,
    'zero': GL.GL_ZERO,
}


def ToOpenGLBlendFactor(
    value: hints.blend_factor,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLBlendFactor_data, value, context_version)


_ToOpenGLTextureWrap_data: dict[hints.texture_wrap, int | dict[Types.hints.context_version, int]] = {
    'clamp': {
        (3, 0): GL.GL_CLAMP_TO_EDGE,
        (2, 0): GL.GL_CLAMP,
    },
    'repeat': GL.GL_REPEAT,
}


def ToOpenGLTextureWrap(
    value: hints.texture_wrap,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLTextureWrap_data, value, context_version)


_ToOpenGLTextureFilter_data: dict[hints.texture_filter, int] = {
    'linear': GL.GL_LINEAR,
    'nearest': GL.GL_NEAREST,
}


def ToOpenGLTextureFilter(
    value: hints.texture_filter,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLTextureFilter_data, value, context_version)


_ToOpenGLBufferDataUsage_data: dict[hints.buffet_data_usage, int] = {
    'dynamic_draw': GL.GL_DYNAMIC_DRAW,
    'dynamic_read': GL.GL_DYNAMIC_READ,
    'dynamic_copy': GL.GL_DYNAMIC_COPY,
    'static_draw': GL.GL_STATIC_DRAW,
    'static_read': GL.GL_STATIC_READ,
    'static_copy': GL.GL_STATIC_COPY,
    'stream_draw': GL.GL_STREAM_DRAW,
    'stream_read': GL.GL_STREAM_READ,
    'stream_copy': GL.GL_STREAM_COPY,
}


def ToOpenGLBufferDataUsage(
    value: hints.buffet_data_usage,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLBufferDataUsage_data, value, context_version)


_ToOpenGLBufferType_data: dict[hints.buffer_type, int] = {
    'array_buffer': GL.GL_ARRAY_BUFFER,
    'atomic_counter_buffer': GL.GL_ATOMIC_COUNTER_BUFFER,
    'copy_read_buffer': GL.GL_COPY_READ_BUFFER,
    'copy_write_buffer': GL.GL_COPY_WRITE_BUFFER,
    'dispatch_indirect_buffer': GL.GL_DISPATCH_INDIRECT_BUFFER,
    'draw_indirect_buffer': GL.GL_DRAW_INDIRECT_BUFFER,
    'element_array_buffer': GL.GL_ELEMENT_ARRAY_BUFFER,
    'pixel_pack_buffer': GL.GL_PIXEL_PACK_BUFFER,
    'pixel_unpack_buffer': GL.GL_PIXEL_UNPACK_BUFFER,
    'query_buffer': GL.GL_QUERY_BUFFER,
    'shader_storage_buffer': GL.GL_SHADER_STORAGE_BUFFER,
    'texture_buffer': GL.GL_TEXTURE_BUFFER,
    'transform_feedback_buffer': GL.GL_TRANSFORM_FEEDBACK_BUFFER,
    'uniform_buffer': GL.GL_UNIFORM_BUFFER,
}


def ToOpenGLBufferType(
    value: hints.buffer_type,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLBufferType_data, value, context_version)


_ToOpenGLTextureType_data: dict[hints.texture_type, int] = {
    'texture_1d': GL.GL_TEXTURE_1D,
    'texture_2d': GL.GL_TEXTURE_2D,
    'texture_3d': GL.GL_TEXTURE_3D,
    'texture_rectangle': GL.GL_TEXTURE_RECTANGLE,
    'texture_buffer': GL.GL_TEXTURE_BUFFER,
    'texture_cube_map': GL.GL_TEXTURE_CUBE_MAP,
    'texture_1d_array': GL.GL_TEXTURE_1D_ARRAY,
    'texture_2d_array': GL.GL_TEXTURE_2D_ARRAY,
    'texture_cube_map_array': GL.GL_TEXTURE_CUBE_MAP_ARRAY,
    'texture_2d_multisample': GL.GL_TEXTURE_2D_MULTISAMPLE,
    'texture_2d_multisample_array': GL.GL_TEXTURE_2D_MULTISAMPLE_ARRAY,
}


def ToOpenGLTextureType(
    value: hints.texture_type,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLTextureType_data, value, context_version)


_ToOpenGLPrimitive_data: dict[hints.primitive, int] = {
    'points': GL.GL_POINTS,
    'lines': GL.GL_LINES,
    'line_loop': GL.GL_LINE_LOOP,
    'line_strip': GL.GL_LINE_STRIP,
    'triangles': GL.GL_TRIANGLES,
    'triangle_strip': GL.GL_TRIANGLE_STRIP,
    'triangle_fan': GL.GL_TRIANGLE_FAN,
    'lines_adjacency': GL.GL_LINES_ADJACENCY,
    'line_strip_adjacency': GL.GL_LINE_STRIP_ADJACENCY,
    'triangles_adjacency': GL.GL_TRIANGLES_ADJACENCY,
    'triangle_strip_adjacency': GL.GL_TRIANGLE_STRIP_ADJACENCY,
}


def ToOpenGLPrimitive(
    value: hints.primitive,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLPrimitive_data, value, context_version)


_ToOpenGLCapability_data: dict[hints.capability, int] = {
    'depth': GL.GL_DEPTH_TEST,
    'blend': GL.GL_BLEND,
    'multisample': GL.GL_MULTISAMPLE,
}


def ToOpenGLCapability(
    value: hints.capability,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLCapability_data, value, context_version)


_ToOpenGLMask_data: dict[hints.mask, int] = {
    'color': GL.GL_COLOR_BUFFER_BIT,
    'depth': GL.GL_DEPTH_BUFFER_BIT,
}


def ToOpenGLMask(
    value: hints.mask,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLMask_data, value, context_version)


_ToOpenGLShaderType_data: dict[hints.shader_type, int] = {
    'vertex': GL.GL_VERTEX_SHADER,
    'fragment': GL.GL_FRAGMENT_SHADER,
}


def ToOpenGLShaderType(
    value: hints.shader_type,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLShaderType_data, value, context_version)


_ToOpenGLTextureInternalFormat_data: dict[hints.texture_internal_format, int] = {
    'alpha': GL.GL_ALPHA,
    'alpha4': GL.GL_ALPHA4,
    'alpha8': GL.GL_ALPHA8,
    'alpha12': GL.GL_ALPHA12,
    'alpha16': GL.GL_ALPHA16,
    'luminance': GL.GL_LUMINANCE,
    'luminance4': GL.GL_LUMINANCE4,
    'luminance8': GL.GL_LUMINANCE8,
    'luminance12': GL.GL_LUMINANCE12,
    'luminance16': GL.GL_LUMINANCE16,
    #
    'luminance_alpha': GL.GL_LUMINANCE_ALPHA,
    'luminance4_alpha4': GL.GL_LUMINANCE4_ALPHA4,
    'luminance6_alpha2': GL.GL_LUMINANCE6_ALPHA2,
    'luminance8_alpha8': GL.GL_LUMINANCE8_ALPHA8,
    'luminance12_alpha4': GL.GL_LUMINANCE12_ALPHA4,
    'luminance12_alpha12': GL.GL_LUMINANCE12_ALPHA12,
    'luminance16_alpha16': GL.GL_LUMINANCE16_ALPHA16,
    #
    'intensity': GL.GL_INTENSITY,
    'intensity4': GL.GL_INTENSITY4,
    'intensity8': GL.GL_INTENSITY8,
    'intensity12': GL.GL_INTENSITY12,
    'intensity16': GL.GL_INTENSITY16,
    #
    'r3_g3_b3': GL.GL_R3_G3_B2,
    #
    'rgb': GL.GL_RGB,
    'rgb4': GL.GL_RGB4,
    'rgb5': GL.GL_RGB5,
    'rgb8': GL.GL_RGB8,
    'rgb10': GL.GL_RGB10,
    'rgb12': GL.GL_RGB12,
    'rgb16': GL.GL_RGB16,
    #
    'rgba': GL.GL_RGBA,
    'rgba2': GL.GL_RGBA2,
    'rgba4': GL.GL_RGBA4,
    'rgb5_a1': GL.GL_RGB5_A1,
    'rgba8': GL.GL_RGBA8,
    'rgb10_a2': GL.GL_RGB10_A2,
    'rgba12': GL.GL_RGBA12,
    'rgba16': GL.GL_RGBA16,
    #
    'depth_component': GL.GL_DEPTH_COMPONENT,
    'depth_component16': GL.GL_DEPTH_COMPONENT16,
    'depth_component24': GL.GL_DEPTH_COMPONENT24,
    'depth_component32': GL.GL_DEPTH_COMPONENT32,
    'depth_component32f': GL.GL_DEPTH_COMPONENT32F,
    'depth_components': GL.GL_DEPTH_COMPONENTS,
}


def ToOpenGLTextureInternalFormat(
    value: hints.texture_internal_format,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLTextureInternalFormat_data, value, context_version)


_ToOpenGLTextureFormat_data: dict[hints.texture_format, int] = {
    'color_index': GL.GL_COLOR_INDEX,
    'red': GL.GL_RED,
    'green': GL.GL_GREEN,
    'blue': GL.GL_BLUE,
    'alpha': GL.GL_ALPHA,
    'rgb': GL.GL_RGB,
    'rgba': GL.GL_RGBA,
    'luminance': GL.GL_LUMINANCE,
    'luminance_alpha': GL.GL_LUMINANCE_ALPHA,
    #
    'depth_component': GL.GL_DEPTH_COMPONENT,
    'depth_component16': GL.GL_DEPTH_COMPONENT16,
    'depth_component24': GL.GL_DEPTH_COMPONENT24,
    'depth_component32': GL.GL_DEPTH_COMPONENT32,
    'depth_component32f': GL.GL_DEPTH_COMPONENT32F,
    'depth_components': GL.GL_DEPTH_COMPONENTS,
}


def ToOpenGLTextureFormat(
    value: hints.texture_format,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLTextureFormat_data, value, context_version)


_ToOpenGLType_data: dict[hints.opengl_type, int] = {
    'unsigned_byte': GL.GL_UNSIGNED_BYTE,
    'byte': GL.GL_BYTE,
    'bitmap': GL.GL_BITMAP,
    'unsigned_short': GL.GL_UNSIGNED_SHORT,
    'short': GL.GL_SHORT,
    'unsigned_int': GL.GL_UNSIGNED_INT,
    'int': GL.GL_INT,
    'float': GL.GL_FLOAT,
}


def ToOpenGLType(
    value: hints.opengl_type,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLType_data, value, context_version)


_ToOpenGLFramebufferTexture2DTarget_data: dict[hints.framebuffer_texture_2d_target, int] = {
    'draw_framebuffer': GL.GL_DRAW_FRAMEBUFFER,
    'read_framebuffer': GL.GL_READ_FRAMEBUFFER,
    'framebuffer': GL.GL_FRAMEBUFFER,
}


def ToOpenGLFramebufferTexture2DTarget(
    value: hints.framebuffer_texture_2d_target,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLFramebufferTexture2DTarget_data, value, context_version)


_ToOpenGLFramebufferTexture2DAttachment_data: dict[hints.framebuffer_texture_2d_attachment, int] = {
    'color_attachment_0': GL.GL_COLOR_ATTACHMENT0,
    'color_attachment_1': GL.GL_COLOR_ATTACHMENT1,
    'color_attachment_2': GL.GL_COLOR_ATTACHMENT2,
    'color_attachment_3': GL.GL_COLOR_ATTACHMENT3,
    'color_attachment_4': GL.GL_COLOR_ATTACHMENT4,
    'color_attachment_5': GL.GL_COLOR_ATTACHMENT5,
    'color_attachment_6': GL.GL_COLOR_ATTACHMENT6,
    'color_attachment_7': GL.GL_COLOR_ATTACHMENT7,
    'color_attachment_8': GL.GL_COLOR_ATTACHMENT8,
    'color_attachment_9': GL.GL_COLOR_ATTACHMENT9,
    'color_attachment_10': GL.GL_COLOR_ATTACHMENT10,
    'color_attachment_11': GL.GL_COLOR_ATTACHMENT11,
    'color_attachment_12': GL.GL_COLOR_ATTACHMENT12,
    'color_attachment_13': GL.GL_COLOR_ATTACHMENT13,
    'color_attachment_14': GL.GL_COLOR_ATTACHMENT14,
    'color_attachment_15': GL.GL_COLOR_ATTACHMENT15,
    'color_attachment_16': GL.GL_COLOR_ATTACHMENT16,
    'color_attachment_17': GL.GL_COLOR_ATTACHMENT17,
    'color_attachment_18': GL.GL_COLOR_ATTACHMENT18,
    'color_attachment_19': GL.GL_COLOR_ATTACHMENT19,
    'color_attachment_20': GL.GL_COLOR_ATTACHMENT20,
    'color_attachment_21': GL.GL_COLOR_ATTACHMENT21,
    'color_attachment_22': GL.GL_COLOR_ATTACHMENT22,
    'color_attachment_23': GL.GL_COLOR_ATTACHMENT23,
    'color_attachment_24': GL.GL_COLOR_ATTACHMENT24,
    'color_attachment_25': GL.GL_COLOR_ATTACHMENT25,
    'color_attachment_26': GL.GL_COLOR_ATTACHMENT26,
    'color_attachment_27': GL.GL_COLOR_ATTACHMENT27,
    'color_attachment_28': GL.GL_COLOR_ATTACHMENT28,
    'color_attachment_29': GL.GL_COLOR_ATTACHMENT29,
    'color_attachment_30': GL.GL_COLOR_ATTACHMENT30,
    'color_attachment_31': GL.GL_COLOR_ATTACHMENT31,
    #
    'depth_attachment': GL.GL_DEPTH_ATTACHMENT,
    'stencil_attachment': GL.GL_STENCIL_ATTACHMENT,
    'depth_stencil_attachment': GL.GL_DEPTH_STENCIL_ATTACHMENT,
}


def ToOpenGLFramebufferTexture2DAttachment(
    value: hints.framebuffer_texture_2d_attachment,
    context_version: t.Optional[Types.hints.context_version] = None,
) -> int:
    return _GetFromDict(_ToOpenGLFramebufferTexture2DAttachment_data, value, context_version)


_VSyncToInterval_data: dict[hints.vsync, int] = {
    'off': 0,
    'full': 1,
    'half': 2,
}


def VSyncToInterval(value: hints.vsync) -> int:
    return _GetFromDict(_VSyncToInterval_data, value)
