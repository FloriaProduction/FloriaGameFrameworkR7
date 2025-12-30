#version 420 core

layout(location = 0) in vec2 vsh_vertex;
layout(location = 1) in vec2 vsh_texcoord;

layout (location = 2) in vec3 translation;
layout (location = 3) in vec3 rotation;
layout (location = 4) in vec3 scale;
layout (location = 5) in float opacity; // [0, 1]

layout (location = 6) in vec2 anim_size; // [0, 1]: width-height on atlas
layout (location = 7) in vec2 anim_offset; // [0, 1]: left-top of atlas
layout (location = 8) in uint anim_count; // [0, ...)
layout (location = 9) in float anim_duration; // (0, ...)
layout (location = 10) in uint anim_loop; // [0, 1]
layout (location = 11) in float anim_start; // [0, ...)
layout (location = 12) in float anim_pause; // [-1, ...)

layout (std140, binding = 0) uniform Camera {
    mat4 projection;
    mat4 view;
} camera;

uniform float current_time = 0;

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
    uint anim_current_frame;
    if (anim_count > 1) {
        float anim_delay = anim_duration / anim_count;
        float anim_past_tense = (anim_pause > 0 ? anim_pause : current_time) - anim_start;

        uint count_frames = uint(max(anim_past_tense / anim_delay, 0));

        if (anim_loop > 0) { // looped
            anim_current_frame = count_frames % anim_count;
        }
        else {
            anim_current_frame = min(count_frames, anim_count - 1);
        }
    }
    else {
        anim_current_frame = 0;
    }
    
    vec2 anim_frame_size = anim_count > 1 ? vec2(
        anim_size.x,
        anim_size.y / float(anim_count)
    ) : anim_size;

    fsh_texcoord = 
        vsh_texcoord * 
        anim_frame_size + 
        anim_offset +
        vec2(
            0, 
            anim_frame_size.y * anim_current_frame
        );
    fsh_opacity = opacity;

    gl_Position = 
        camera.projection * 
        camera.view * 
        ModelMatrix(translation, rotation, scale) * 
        vec4(vsh_vertex.xy, 0.0, 1.0);
}