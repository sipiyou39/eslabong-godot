shader_type spatial;
render_mode cull_front, unshaded, depth_draw_opaque;
uniform vec4 outline_color : source_color = vec4(0.04, 0.03, 0.06, 1.0);
uniform float thickness = 0.012;
uniform float alpha : hint_range(0.0, 1.0) = 1.0;
void vertex() {
	VERTEX += NORMAL * thickness;
}
void fragment() {
	ALBEDO = outline_color.rgb;
	if (alpha < 1.0) {
		float ign = fract(52.9829189 * fract(dot(FRAGCOORD.xy, vec2(0.06711056, 0.00583715))));
		if (ign < (1.0 - alpha) * 0.75) discard;
	}
}
