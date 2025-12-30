#version 420 core

layout(location = 0) in vec2 vsh_vertex;
layout(location = 1) in vec2 vsh_texcoord;

layout (location = 2) in vec3 translation;
layout (location = 3) in vec3 rotation;
layout (location = 4) in vec3 scale;
layout (location = 5) in float opacity; // [0, 1]

layout (location = 6) in vec2 anim_size; // [0, 1]: width-height on atlas
layout (location = 7) in vec2 anim_offset; // [0, 1]: left-top of atlas

layout (std140, binding = 0) uniform Camera {
    mat4 projection;
    mat4 view;
} camera;

out vec2 fsh_texcoord;
out float fsh_opacity;


mat4 ModelMatrix(vec3 translation, vec3 rotation, vec3 scale) {
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
        scale.x,  0.0,      0.0,      0.0,
        0.0,      scale.y,  0.0,      0.0,
        0.0,      0.0,      scale.z,  0.0,
        0.0,      0.0,      0.0,      1.0
    );
    
    mat4 translation_mat = mat4(
        1.0,  0.0,  0.0,  0.0,
        0.0,  1.0,  0.0,  0.0,
        0.0,  0.0,  1.0,  0.0,
        translation.x, translation.y, translation.z, 1.0
    );
    
    return translation_mat * rotation_mat * scale_mat;
}


void main() {
    fsh_texcoord = 
        vsh_texcoord * 
        anim_size + 
        anim_offset;
    fsh_opacity = opacity;

    gl_Position = 
        camera.projection * 
        camera.view * 
        ModelMatrix(translation, rotation, scale) * 
        vec4(vsh_vertex.xy, 0.0, 1.0);
}