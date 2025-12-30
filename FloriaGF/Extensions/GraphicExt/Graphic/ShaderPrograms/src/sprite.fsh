#version 420 core

in vec2 fsh_texcoord;
in float fsh_opacity;


uniform sampler2D in_texture;


out vec4 result_color;


void main()
{
    vec4 color = texture(in_texture, fsh_texcoord);

    result_color = vec4(
        color.rgb, 
        color.a * fsh_opacity
    );
}