import typing as t

from FloriaGF.Graphic.ShaderPrograms.Construct import C, ShaderConstuct
from FloriaGF.Graphic.ShaderPrograms import ShaderProgram


class UIVertexShader(ShaderConstuct):
    vertice = C.AttribVertice('vec2')
    texcoord = C.AttribTexcoord('vec2')

    translation = C.AttribInst('vec3')  # in pixels
    rotation = C.AttribInst('vec3')
    size = C.AttribInst('vec3')  # in pixels
    opacity = C.AttribInst('float')

    screen_size = C.Uniform('vec2', 'vec2(1280, 720)')

    ModelMatrix = C.Function(
        '''
        mat4 ModelMatrix(vec3 translation, vec3 rotation, vec3 size) {
            float pitch = rotation.x;
            float yaw = rotation.y;
            float roll = rotation.z;
            
            float cp = cos(pitch);
            float sp = sin(pitch);
            float cy = cos(yaw);
            float sy = sin(yaw);
            float cr = cos(roll);
            float sr = sin(roll);
            
            mat4 rotation_mat = mat4(
                cy * cr,                -cy * sr,               sy,                0.0,
                sp * sy * cr + cp * sr, -sp * sy * sr + cp * cr, -sp * cy,          0.0,
                -cp * sy * cr + sp * sr, cp * sy * sr + sp * cr, cp * cy,           0.0,
                0.0,                    0.0,                    0.0,               1.0
            );
            
            mat4 scale_mat = mat4(
                size.x,  0.0,      0.0,      0.0,
                0.0,      size.y,  0.0,      0.0,
                0.0,      0.0,      size.z,  0.0,
                0.0,      0.0,      0.0,      1.0
            );
            
            mat4 translation_mat = mat4(
                1.0,  0.0,  0.0,  0.0,
                0.0,  1.0,  0.0,  0.0,
                0.0,  0.0,  1.0,  0.0,
                translation * vec3(screen_size.xy, 1) - vec3(1, 1, 0), 1.0
            );
            
            return translation_mat * rotation_mat * scale_mat;
        }
        '''
    )

    main = C.Main(
        f'''
        {{
            fsh_texcoord = texcoord;
            fsh_opacity = opacity;

            gl_Position =
                (translation, rotation, size) *
                vec4(vertice.xy, 0.0, 1.0);
        }}
        '''
    )


class UIFragmentShader(ShaderConstuct):
    fsh_texcoord = C.ParamIn('vec2')
    fsh_opacity = C.ParamIn('float')
    fsh_anim_current = C.ParamIn('float')

    in_texture = C.Uniform('sampler2DArray')

    result_color = C.ParamOut('vec4')

    main = C.Main(
        '''
        {
            vec4 color = texture(in_texture, vec3(fsh_texcoord.xy, fsh_anim_current));

            if (color.a < 0.5) 
            {
                discard;
            }
            else 
            {
                color.a = 1;
            }
            
            result_color = vec4(
                color.rgb,
                color.a * fsh_opacity
            );
        }
        '''
    )


class UIShaderProgram(ShaderProgram):
    __vertex__ = UIVertexShader
    __fragment__ = UIFragmentShader

    __depth__ = 'less'

    __blend_equation__ = 'func_add'
    __blend_factors__ = ('src_alpha', 'one_minus_src_alpha')
