shader_type spatial;
render_mode cull_back, diffuse_toon, specular_toon, depth_draw_opaque;

// Palette appliquée via le masque de sommets : R=primaire, G=secondaire, B=accent/métal, reste=peau, A=AO
uniform vec4 c_primary : source_color = vec4(0.6, 0.2, 0.2, 1.0);
uniform vec4 c_secondary : source_color = vec4(0.2, 0.2, 0.3, 1.0);
uniform vec4 c_accent : source_color = vec4(0.9, 0.75, 0.3, 1.0);
uniform vec4 c_skin : source_color = vec4(0.85, 0.65, 0.5, 1.0);
uniform bool use_mask = true;
uniform vec4 flat_color : source_color = vec4(1.0);
uniform vec4 rim_color : source_color = vec4(0.6, 0.8, 1.0, 1.0);
uniform float rim_strength : hint_range(0.0, 2.0) = 0.35;
uniform float rim_power : hint_range(0.5, 8.0) = 3.0;
uniform vec4 flash_color : source_color = vec4(1.0, 1.0, 1.0, 0.0);
uniform float accent_glow : hint_range(0.0, 3.0) = 0.25;
uniform float dissolve : hint_range(0.0, 1.0) = 0.0;
uniform vec4 dissolve_color : source_color = vec4(1.0, 0.5, 0.2, 1.0);
uniform float ghost : hint_range(0.0, 1.0) = 0.0;
uniform float tint_amount : hint_range(0.0, 1.0) = 0.0;
uniform vec4 tint_color : source_color = vec4(0.5, 0.8, 1.0, 1.0);
uniform float metal_amount : hint_range(0.0, 1.0) = 0.55;
uniform float roughness_base : hint_range(0.0, 1.0) = 0.65;

varying vec4 v_col;
varying vec3 v_obj;

float hash(vec3 p) {
	p = fract(p * 0.3183099 + 0.1);
	p *= 17.0;
	return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

void vertex() {
	v_col = COLOR;
	v_obj = VERTEX;
}

void fragment() {
	vec3 col;
	float metal = 0.0;
	float glow = 0.0;
	if (use_mask) {
		vec3 w = clamp(v_col.rgb, 0.0, 1.0);
		float base_w = clamp(1.0 - (w.r + w.g + w.b), 0.0, 1.0);
		col = c_skin.rgb * base_w + c_primary.rgb * w.r + c_secondary.rgb * w.g + c_accent.rgb * w.b;
		float ao = mix(0.5, 1.0, clamp(v_col.a, 0.0, 1.0));
		col *= ao;
		metal = w.b * metal_amount;
		glow = w.b;
	} else {
		col = flat_color.rgb * mix(0.65, 1.0, clamp(v_col.a, 0.0, 1.0));
	}
	col = mix(col, tint_color.rgb * (col * 0.6 + 0.4), tint_amount);
	ALBEDO = col;
	METALLIC = metal;
	ROUGHNESS = mix(roughness_base, 0.35, metal);
	SPECULAR = 0.4;
	float fres = pow(1.0 - clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0), rim_power);
	vec3 em = rim_color.rgb * fres * rim_strength;
	em += c_accent.rgb * glow * accent_glow * 0.35;
	em += flash_color.rgb * flash_color.a;
	if (dissolve > 0.0) {
		float n = hash(floor(v_obj * 18.0));
		float edge = dissolve * 1.2 - n * 0.2;
		if (n < dissolve) discard;
		em += dissolve_color.rgb * smoothstep(0.0, 0.12, (n - dissolve)) * (1.0 - smoothstep(0.12, 0.3, n - dissolve)) * 3.0;
	}
	EMISSION = em;
	if (ghost > 0.0) {
		float ign = fract(52.9829189 * fract(dot(FRAGCOORD.xy, vec2(0.06711056, 0.00583715))));
		if (ign < ghost * 0.75) discard;
	}
}
