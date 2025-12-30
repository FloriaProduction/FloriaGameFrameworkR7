#version 420 core

in vec2 fsh_texcoord;
in float fsh_opacity;
in float fsh_anim_current;

uniform sampler2DArray in_texture;

out vec4 result_color;


void main()
{
    vec4 color = texture(in_texture, vec3(fsh_texcoord.xy, fsh_anim_current));

    result_color = vec4(
        color.rgb, 
        color.a * fsh_opacity
    );
}