shader_type canvas_item;
// Post-traitement léger : vignette, aberration chromatique d'impact, grain, flash
uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform sampler2D grain_tex : repeat_enable, filter_linear;
uniform float vignette : hint_range(0.0, 1.5) = 0.55;
uniform float aberration : hint_range(0.0, 0.05) = 0.0;
uniform float grain : hint_range(0.0, 0.2) = 0.03;
uniform vec4 flash : source_color = vec4(1.0, 1.0, 1.0, 0.0);
uniform vec4 tint : source_color = vec4(1.0, 0.0, 0.0, 0.0);
uniform float time_s = 0.0;
uniform float saturation = 1.05;
void fragment() {
	vec2 uv = SCREEN_UV;
	vec2 c = uv - 0.5;
	float d = length(c);
	vec2 dir = c * aberration * (0.4 + d);
	vec3 col;
	col.r = texture(screen_tex, uv + dir).r;
	col.g = texture(screen_tex, uv).g;
	col.b = texture(screen_tex, uv - dir).b;
	float g = dot(col, vec3(0.299, 0.587, 0.114));
	col = mix(vec3(g), col, saturation);
	float v = smoothstep(0.85, 0.2, d * (1.0 + vignette * 0.6));
	col *= mix(1.0 - vignette * 0.55, 1.0, v);
	float n = texture(grain_tex, uv * vec2(6.0, 3.4) + vec2(fract(time_s * 7.3), fract(time_s * 3.7))).r - 0.5;
	col += n * grain;
	col = mix(col, tint.rgb, tint.a * smoothstep(0.2, 0.8, d));
	col = mix(col, flash.rgb, flash.a);
	COLOR = vec4(col, 1.0);
}
