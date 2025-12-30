import typing as t
from contextlib import contextmanager

from ... import Abc, Types
from .ShaderProgram import ShaderProgram
from .Construct.ShaderConstuct import ShaderConstuct, C

if t.TYPE_CHECKING:
    from ..Objects.FBO import FBO


class ComposeVertexShader(ShaderConstuct):
    vertice = C.AttribVertice('vec2')
    texcoord = C.AttribTexcoord('vec2')

    fsh_texcoord = C.ParamOut('vec2')

    main = C.Main(
        '''
        {
            fsh_texcoord = texcoord;
            gl_Position = vec4(vertice.xy, 0.0, 1.0);    
        }
        '''
    )


class ComposeFragmentShader(ShaderConstuct):
    fsh_texcoord = C.ParamIn('vec2')

    result_color = C.ParamOut('vec4')

    layer_texture = C.Uniform('sampler2D')

    main = C.Main(
        '''
        {
            result_color = texture(layer_texture, fsh_texcoord);
        }
        '''
    )


class ComposeShaderProgram(
    ShaderProgram,
    Abc.ComposeShaderProgram,
):
    __vertex__ = ComposeVertexShader
    __fragment__ = ComposeFragmentShader

    __depth__ = 'less'
    __blend_equation__ = 'func_add'
    __blend_factors__ = ('src_alpha', 'one_minus_src_alpha')

    @contextmanager
    def Bind(self, fbo: 'FBO', *args: t.Any, **kwargs: t.Any):
        with super().Bind():
            with fbo.texture.Bind():
                yield self
