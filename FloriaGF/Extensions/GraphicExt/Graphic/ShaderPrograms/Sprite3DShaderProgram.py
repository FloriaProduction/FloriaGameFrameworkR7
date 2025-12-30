import typing as t

from FloriaGF.Graphic.ShaderPrograms import CameraShaderProgram, CameraVertexShader
from FloriaGF.Graphic.ShaderPrograms.Construct import C, ShaderConstuct


class Sprite3DVertexShader(CameraVertexShader):
    vertice = C.AttribVertice('vec2')
    texcoord = C.AttribTexcoord('vec2')

    model_matrix = C.AttribInst('mat4')
    opacity = C.AttribInst('float')
    frame = C.AttribInst('uint')

    fsh_texcoord = C.ParamOut('vec2')
    fsh_opacity = C.ParamOut('float')
    fsh_frame = C.ParamOut('uint')

    main = C.Main(
        '''
        {      
            fsh_texcoord = texcoord;
            fsh_opacity = opacity;
            fsh_frame = frame;

            gl_Position =
                camera.projection *
                camera.view *
                model_matrix *
                vec4(vertice.xy, 0.0, 1.0);
        }
        '''
    )


class Sprite3DFragmentShader(ShaderConstuct):
    fsh_texcoord = C.ParamIn('vec2')
    fsh_opacity = C.ParamIn('float')
    fsh_frame = C.ParamIn('uint')

    in_texture = C.Uniform('sampler2DArray')

    result_color = C.ParamOut('vec4')

    main = C.Main(
        '''
        {
            vec4 color = texture(in_texture, vec3(fsh_texcoord.xy, float(fsh_frame)));
            
            if (fsh_opacity < 1) {
                color.a *= max(0, fsh_opacity);
            }
            
            if (color.a < 0.5) 
            {
                discard;
            }
            else 
            {
                color.a = 1;
            }  
            
            result_color = color;
        }
        '''
    )


class Sprite3DShaderProgram(CameraShaderProgram):
    __vertex__ = Sprite3DVertexShader
    __fragment__ = Sprite3DFragmentShader

    __depth__ = 'less'

    __blend_equation__ = 'func_add'
    __blend_factors__ = ('src_alpha', 'one_minus_src_alpha')
