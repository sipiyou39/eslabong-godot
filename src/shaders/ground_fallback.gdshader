shader_type spatial;
render_mode diffuse_lambert, specular_disabled;
uniform vec4 base_a : source_color = vec4(0.72, 0.58, 0.38, 1.0);
uniform vec4 base_b : source_color = vec4(0.58, 0.44, 0.28, 1.0);
uniform vec4 line_color : source_color = vec4(0.95, 0.85, 0.55, 1.0);
uniform vec2 half_extents = vec2(26.0, 16.0);
varying vec3 wpos;
float hash21(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
float noise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash21(i), hash21(i + vec2(1, 0)), f.x), mix(hash21(i + vec2(0, 1)), hash21(i + vec2(1, 1)), f.x), f.y);
}
void vertex() { wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
	vec2 p = wpos.xz;
	float n = noise(p * 0.8) * 0.5 + noise(p * 3.1) * 0.3 + noise(p * 12.0) * 0.2;
	vec3 col = mix(base_a.rgb, base_b.rgb, n);
	float r = length(p);
	float ring = smoothstep(0.12, 0.0, abs(r - 6.0)) + smoothstep(0.1, 0.0, abs(r - 9.0)) * 0.6;
	float mid = smoothstep(0.1, 0.0, abs(p.x));
	float teamline = smoothstep(0.1, 0.0, abs(abs(p.x) - 18.0));
	col = mix(col, line_color.rgb, clamp(ring + mid + teamline, 0.0, 1.0) * 0.55);
	float edge = smoothstep(half_extents.x - 4.0, half_extents.x + 1.0, abs(p.x)) + smoothstep(half_extents.y - 3.0, half_extents.y + 1.0, abs(p.y));
	col *= 1.0 - clamp(edge, 0.0, 1.0) * 0.45;
	ALBEDO = col;
	ROUGHNESS = 0.95;
}
