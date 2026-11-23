shader_type spatial;
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, shadows_disabled;
// Zone de télégraphie au sol : 0=cercle, 1=rectangle (UV.y le long), 2=cône
uniform int shape = 0;
uniform vec4 color : source_color = vec4(1.0, 0.4, 0.2, 1.0);
uniform float progress : hint_range(0.0, 1.0) = 0.0;
uniform float intensity = 1.0;
uniform float cone_angle = 1.0;
uniform float time_s = 0.0;
uniform sampler2D rune_tex : source_color, filter_linear_mipmap, repeat_disable;
uniform bool use_rune = false;

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float a = 0.0;
	float edge = 0.0;
	float fillm = 0.0;
	if (shape == 0) {
		float r = length(p);
		if (r > 1.0) discard;
		edge = smoothstep(0.93, 0.985, r) * (1.0 - smoothstep(0.985, 1.0, r));
		fillm = smoothstep(progress, progress - 0.04, r) * 0.38;
		float base = 0.10 + 0.04 * sin(time_s * 6.0 - r * 8.0);
		a = edge * 1.6 + fillm + base * (1.0 - r * 0.4);
		if (use_rune) {
			float ang = atan(p.y, p.x) + time_s * 0.4;
			vec2 ruv = vec2(cos(ang), sin(ang)) * r * 0.5 + 0.5;
			a += texture(rune_tex, ruv).a * 0.35 * smoothstep(0.2, 0.9, r);
		}
	} else if (shape == 1) {
		float ex = abs(p.x);
		if (ex > 1.0) discard;
		float yy = UV.y;
		edge = smoothstep(0.88, 0.97, ex) + smoothstep(0.02, 0.0, yy) * 0.8 + smoothstep(0.98, 1.0, yy) * 0.8;
		fillm = step(yy, progress) * 0.35;
		a = edge * 0.9 + fillm + 0.08;
	} else {
		// cône : sommet en bas (UV.y=1), s'ouvre vers le haut
		float yy = 1.0 - UV.y;
		float half_w = yy * tan(cone_angle * 0.5);
		float d = abs(p.x) / max(half_w * 2.0, 0.0001) * 1.0;
		if (yy > 1.0) discard;
		float inside = step(abs(p.x), half_w);
		if (inside < 0.5) discard;
		edge = smoothstep(0.88, 0.99, abs(p.x) / max(half_w, 0.0001)) + smoothstep(0.95, 1.0, yy);
		fillm = step(yy, progress) * 0.3;
		a = edge * 0.9 + fillm + 0.08;
	}
	ALBEDO = color.rgb * intensity;
	ALPHA = clamp(a, 0.0, 1.0) * color.a;
}
