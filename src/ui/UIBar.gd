class_name UIBar
extends Control
## Barre de ressource dessinée (dégradé, reflet, traînée de dégâts, texte optionnel).

var value: float = 1.0
var max_value: float = 1.0
var color: Color = Color("e8505a")
var trail: float = 1.0
var show_text: bool = false
var text_override: String = ""
var radius: float = 4.0
var bg_color: Color = Color(0.04, 0.03, 0.08, 0.85)
var border_color: Color = Color(0, 0, 0, 0.9)
var segments: int = 0
var shield: float = 0.0

func _init(c: Color = Color("e8505a"), h: float = 12.0) -> void:
	color = c
	custom_minimum_size = Vector2(60, h)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

func set_values(v: float, mx: float) -> void:
	value = v
	max_value = maxf(mx, 0.001)
	queue_redraw()

func _process(dt: float) -> void:
	var frac := clampf(value / max_value, 0.0, 1.0)
	if trail > frac:
		trail = maxf(frac, trail - dt * 0.5)
		queue_redraw()
	elif trail < frac:
		trail = frac

func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var frac := clampf(value / max_value, 0.0, 1.0)
	_rounded(r, bg_color)
	if trail > frac:
		_rounded(Rect2(Vector2.ZERO, Vector2(size.x * trail, size.y)), Color(1, 1, 1, 0.55))
	if frac > 0.0:
		var fr := Rect2(Vector2.ZERO, Vector2(size.x * frac, size.y))
		_rounded(fr, color.darkened(0.25))
		_rounded(Rect2(fr.position + Vector2(0, 0), Vector2(fr.size.x, fr.size.y * 0.55)), color.lightened(0.2))
		_rounded(Rect2(fr.position + Vector2(0, 1), Vector2(fr.size.x, maxf(fr.size.y * 0.22, 1.0))), Color(1, 1, 1, 0.35))
	if shield > 0.0:
		var sf := clampf(shield / max_value, 0.0, 1.0)
		_rounded(Rect2(Vector2(0, 0), Vector2(size.x * sf, 3.0)), Color("bfe8ff"))
	if segments > 0:
		for i in range(1, segments):
			var x := size.x * float(i) / segments
			draw_line(Vector2(x, 0), Vector2(x, size.y), Color(0, 0, 0, 0.6), 1.0)
	draw_rect(r, border_color, false, 1.0)
	if show_text:
		var t := text_override if text_override != "" else "%d / %d" % [int(round(value)), int(round(max_value))]
		var f := Game.font_bold()
		var fs := int(size.y * 0.78)
		var ts := f.get_string_size(t, HORIZONTAL_ALIGNMENT_CENTER, -1, fs)
		draw_string_outline(f, Vector2((size.x - ts.x) * 0.5, size.y * 0.5 + fs * 0.35), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, 4, Color(0, 0, 0, 0.9))
		draw_string(f, Vector2((size.x - ts.x) * 0.5, size.y * 0.5 + fs * 0.35), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color.WHITE)

func _rounded(r: Rect2, c: Color) -> void:
	if radius <= 1.0:
		draw_rect(r, c)
		return
	var sb := StyleBoxFlat.new()
	sb.bg_color = c
	sb.set_corner_radius_all(int(minf(radius, r.size.y * 0.5)))
	sb.draw(get_canvas_item(), r)
