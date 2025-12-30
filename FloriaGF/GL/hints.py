import typing as t

if t.TYPE_CHECKING:
    import numpy as np


depth_func = t.Literal[
    'never',
    'less',
    'equal',
    'lequal',
    'greater',
    'notequal',
    'gequal',
    'always',
]

glsl_primitive = t.Literal[
    'float',
    'uint',
    'int',
]

glsl_vec = t.Literal[
    'vec2',
    'vec3',
    'vec4',
]

glsl_mat = t.Literal[
    'mat3',
    'mat4',
]

glsl_sampler = t.Literal[
    'sampler2D',
    'sampler2DArray',
]

glsl_type = t.Union[
    glsl_primitive,
    glsl_vec,
    glsl_mat,
    glsl_sampler,
]


np_type = t.Union[
    'np.float32',
    'np.int32',
    'np.uint32',
    'np.typing.DTypeLike',
]


blend_equation = t.Literal[
    'func_add',
    'func_subtract',
    'func_reverse_subtract',
    'min',
    'max',
]


blend_factor = t.Literal[
    'zero',
    'one',
    'src_color',
    'src_alpha',
    'one_minus_src_color',
    'dst_color',
    'one_minus_src_alpha',
    'dst_alpha',
    'one_minus_dst_alpha',
    'constant_color',
    'one_minus_constant_color',
    'constant_alpha',
    'one_minus_constant_alpha',
    'src_alpha_saturate',
    'src1_color',
    'one_minus_src1_color',
    'src1_alpha',
    'one_minus_src1_alpha',
]


texture_wrap = t.Literal[
    'clamp',
    'repeat',
]


texture_filter = t.Literal[
    'nearest',
    'linear',
]


buffet_data_usage = t.Literal[
    'stream_draw',
    'stream_read',
    'stream_copy',
    'static_draw',
    'static_read',
    'static_copy',
    'dynamic_draw',
    'dynamic_read',
    'dynamic_copy',
]


buffer_type = t.Literal[
    'array_buffer',
    'atomic_counter_buffer',
    'copy_read_buffer',
    'copy_write_buffer',
    'dispatch_indirect_buffer',
    'draw_indirect_buffer',
    'element_array_buffer',
    'pixel_pack_buffer',
    'pixel_unpack_buffer',
    'query_buffer',
    'shader_storage_buffer',
    'texture_buffer',
    'transform_feedback_buffer',
    'uniform_buffer',
]


texture_type = t.Literal[
    'texture_1d',
    'texture_2d',
    'texture_3d',
    'texture_rectangle',
    'texture_buffer',
    'texture_cube_map',
    'texture_1d_array',
    'texture_2d_array',
    'texture_cube_map_array',
    'texture_2d_multisample',
    'texture_2d_multisample_array',
]


primitive = t.Literal[
    'points',
    'lines',
    'line_loop',
    'line_strip',
    'triangles',
    'triangle_strip',
    'triangle_fan',
    'lines_adjacency',
    'line_strip_adjacency',
    'triangles_adjacency',
    'triangle_strip_adjacency',
]


capability = t.Literal[
    'depth',
    'blend',
    'multisample',
]


mask = t.Literal[
    'color',
    'depth',
]


shader_type = t.Literal[
    'vertex',
    'fragment',
]


texture_internal_format = t.Literal[
    'alpha',
    'alpha4',
    'alpha8',
    'alpha12',
    'alpha16',
    'luminance',
    'luminance4',
    'luminance8',
    'luminance12',
    'luminance16',
    #
    'luminance_alpha',
    'luminance4_alpha4',
    'luminance6_alpha2',
    'luminance8_alpha8',
    'luminance12_alpha4',
    'luminance12_alpha12',
    'luminance16_alpha16',
    #
    'intensity',
    'intensity4',
    'intensity8',
    'intensity12',
    'intensity16',
    #
    'r3_g3_b3',
    #
    'rgb',
    'rgb4',
    'rgb5',
    'rgb8',
    'rgb10',
    'rgb12',
    'rgb16',
    #
    'rgba',
    'rgba2',
    'rgba4',
    'rgb5_a1',
    'rgba8',
    'rgb10_a2',
    'rgba12',
    'rgba16',
    #
    'depth_component',
    'depth_component16',
    'depth_component24',
    'depth_component32',
    'depth_component32f',
    'depth_components',
]


texture_format = t.Literal[
    'color_index',
    'red',
    'green',
    'blue',
    'alpha',
    'rgb',
    'rgba',
    'luminance',
    'luminance_alpha',
    #
    'depth_component',
    'depth_component16',
    'depth_component24',
    'depth_component32',
    'depth_component32f',
    'depth_components',
]


texture_pixel_type = t.Literal[
    'unsigned_byte',
    'byte',
    'bitmap',
    'unsigned_short',
    'short',
    'unsigned_int',
    'int',
    'float',
]

opengl_type = t.Union[texture_pixel_type,]


framebuffer_texture_2d_target = t.Literal[
    'draw_framebuffer',
    'read_framebuffer',
    'framebuffer',
]


framebuffer_texture_2d_attachment = t.Literal[
    'color_attachment_0',
    'color_attachment_1',
    'color_attachment_2',
    'color_attachment_3',
    'color_attachment_4',
    'color_attachment_5',
    'color_attachment_6',
    'color_attachment_7',
    'color_attachment_8',
    'color_attachment_9',
    'color_attachment_10',
    'color_attachment_11',
    'color_attachment_12',
    'color_attachment_13',
    'color_attachment_14',
    'color_attachment_15',
    'color_attachment_16',
    'color_attachment_17',
    'color_attachment_18',
    'color_attachment_19',
    'color_attachment_20',
    'color_attachment_21',
    'color_attachment_22',
    'color_attachment_23',
    'color_attachment_24',
    'color_attachment_25',
    'color_attachment_26',
    'color_attachment_27',
    'color_attachment_28',
    'color_attachment_29',
    'color_attachment_30',
    'color_attachment_31',
    #
    'depth_attachment',
    'stencil_attachment',
    'depth_stencil_attachment',
]


vsync = t.Literal[
    'full',
    'half',
    'off',
]
