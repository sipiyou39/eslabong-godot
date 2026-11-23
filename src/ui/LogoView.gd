class_name LogoView
extends Control
## Logo d'équipe composé d'une recette d'héraldique (écu + partition + meuble, teintés). Repli vectoriel si les textures sont absentes.

var recipe: Dictionary = {}
var _tex_cache: Dictionary = {}

func _init(r: Dictionary = {}, size_px: float = 64.0) -> void:
	recipe = r
	custom_minimum_size = Vector2(size_px, size_px)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

func set_recipe(r: Dictionary) -> void:
	recipe = r
	queue_redraw()

func _tex(path: String) -> Texture2D:
	if _tex_cache.has(path):
		return _tex_cache[path]
	var t: Texture2D = load(path) if ResourceLoader.exists(path) else null
	_tex_cache[path] = t
	return t

func _col(key: String, def: String) -> Color:
	return Color(String(recipe.get(key, def)))

func _draw() -> void:
	if recipe.is_empty():
		return
	var s := minf(size.x, size.y)
	var r := Rect2((size - Vector2(s, s)) * 0.5, Vector2(s, s))
	var sh := int(recipe.get("shield", 0)) % 8
	var dv := int(recipe.get("division", 0)) % 16
	var ch := int(recipe.get("charge", 0)) % 64
	var base := _col("base_color", "#1a1a22")
	var field := _col("field_color", "#f2ead0")
	var chg := _col("charge_color", "#c0392b")
	var dcol := _col("division_color", "#2f5ea8")
	var t_shield := _tex("res://assets/ui/heraldry/shield_%02d.png" % sh)
	if t_shield:
		draw_texture_rect(t_shield, r, false, field)
		var t_div := _tex("res://assets/ui/heraldry/division_%02d.png" % dv)
		if t_div:
			draw_texture_rect(t_div, r, false, dcol)
		var t_ch := _tex("res://assets/ui/heraldry/charge_%03d.png" % ch)
		if t_ch:
			draw_texture_rect(t_ch, Rect2(r.position + r.size * 0.18, r.size * 0.64), false, chg)
		var t_ol := _tex("res://assets/ui/heraldry/shield_%02d_outline.png" % sh)
		if t_ol:
			draw_texture_rect(t_ol, r, false, base)
		return
	# repli : écu vectoriel
	var c := r.position + r.size * 0.5
	var w := r.size.x * 0.42
	var h := r.size.y * 0.48
	var pts := PackedVector2Array([c + Vector2(-w, -h), c + Vector2(w, -h), c + Vector2(w, h * 0.2), c + Vector2(0, h), c + Vector2(-w, h * 0.2)])
	draw_colored_polygon(pts, field)
	var half := PackedVector2Array([c + Vector2(0, -h), c + Vector2(w, -h), c + Vector2(w, h * 0.2), c + Vector2(0, h)])
	if dv % 2 == 0:
		draw_colored_polygon(half, dcol)
	else:
		draw_colored_polygon(PackedVector2Array([c + Vector2(-w, -h * 0.1), c + Vector2(w, -h * 0.1), c + Vector2(w, h * 0.2), c + Vector2(0, h), c + Vector2(-w, h * 0.2)]), dcol)
	# meuble : étoile / disque / croix selon l'index
	match ch % 4:
		0: draw_circle(c + Vector2(0, -h * 0.05), w * 0.4, chg)
		1:
			draw_rect(Rect2(c + Vector2(-w * 0.12, -h * 0.6), Vector2(w * 0.24, h * 1.2)), chg)
			draw_rect(Rect2(c + Vector2(-w * 0.5, -h * 0.15), Vector2(w, h * 0.3)), chg)
		2:
			var star := PackedVector2Array()
			for i in 10:
				var a := -PI * 0.5 + i * PI / 5.0
				var rr := w * (0.55 if i % 2 == 0 else 0.24)
				star.append(c + Vector2(cos(a), sin(a)) * rr + Vector2(0, -h * 0.05))
			draw_colored_polygon(star, chg)
		3: draw_colored_polygon(PackedVector2Array([c + Vector2(0, -h * 0.55), c + Vector2(w * 0.5, h * 0.35), c + Vector2(-w * 0.5, h * 0.35)]), chg)
	draw_polyline(PackedVector2Array(pts + PackedVector2Array([pts[0]])), base, maxf(r.size.x * 0.05, 2.0), true)
