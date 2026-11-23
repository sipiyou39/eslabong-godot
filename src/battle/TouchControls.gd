class_name TouchControls
extends Control
## Commandes tactiles : joystick flottant à gauche, boutons d'action à droite (appui = lancer auto-visé,
## glisser = visée manuelle avec aimantation, ramener au centre = annuler, maintenir l'attaque = tir continu).

signal cast(slot: int, manual: bool, dir: Vector3, mag: float)
signal aim_changed(slot: int, active: bool, dir: Vector3, mag: float)

const OUTLINE := Color("0a0d1c")
var fighter: Fighter
var move_vec: Vector2 = Vector2.ZERO
var attack_held: bool = false
var stick_idx: int = -1
var stick_origin: Vector2 = Vector2.ZERO
var stick_pos: Vector2 = Vector2.ZERO
var stick_visible: bool = false
var stick_default: Vector2 = Vector2(190, 560)
var buttons: Array[Dictionary] = []     # slot, center, radius
var _state: Dictionary = {}             # slot -> {idx, start, aim_active, vec, held_t, cancelled}
var _tex: Dictionary = {}
var _icons: Dictionary = {}
var pulse: float = 0.0
var ult_flash: float = 0.0
var last_size: Vector2 = Vector2.ZERO
var k: float = 1.0
var display_only: bool = false                  # clavier/souris : simple affichage (recharges, ultime) avec étiquettes de touches
var key_labels: Dictionary = {0: "CLIC", 1: "ESPACE", 2: "CLIC D.", 3: "A", 4: "E", 5: "R"}

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	set_process(true)
	set_process_input(true)

func set_fighter(f: Fighter) -> void:
	fighter = f
	_icons.clear()
	_layout()
	queue_redraw()

func _t(name: String) -> Texture2D:
	if _tex.has(name):
		return _tex[name]
	var p := "res://assets/ui2/hud/%s.png" % name
	var t: Texture2D = load(p) if ResourceLoader.exists(p) else null
	_tex[name] = t
	return t

func _safe() -> Vector2:
	# marges de zone sûre (encoche, coins arrondis)
	var sa := DisplayServer.get_display_safe_area()
	var ws := DisplayServer.window_get_size()
	if ws.x <= 0 or sa.size.x <= 0:
		return Vector2(28, 22)
	var left := float(sa.position.x) / float(ws.x) * size.x
	var bottom := float(ws.y - (sa.position.y + sa.size.y)) / float(ws.y) * size.y
	return Vector2(maxf(28.0, left + 18.0), maxf(22.0, bottom + 14.0))

func _layout() -> void:
	buttons.clear()
	var sz := size if size.x > 10 else get_viewport_rect().size
	last_size = sz
	k = clampf(sz.y / 720.0, 0.8, 2.4)
	var sf := _safe() * k
	# grappe sous le pouce droit : attaque en bas à droite, 4 compétences en arc au-dessus, dash en retrait
	var a := Vector2(sz.x - sf.x - 138.0 * k, sz.y - sf.y - 146.0 * k)
	stick_default = Vector2(sf.x + 140.0 * k, sz.y - sf.y - 128.0 * k)
	buttons.append({"slot": 0, "center": a, "radius": 82.0 * k, "big": true})
	buttons.append({"slot": 2, "center": a + Vector2(-193.0, -27.0) * k, "radius": 50.0 * k})
	buttons.append({"slot": 3, "center": a + Vector2(-145.0, -130.0) * k, "radius": 50.0 * k})
	buttons.append({"slot": 4, "center": a + Vector2(-47.0, -189.0) * k, "radius": 50.0 * k})
	buttons.append({"slot": 5, "center": a + Vector2(67.0, -183.0) * k, "radius": 56.0 * k, "ult": true})
	buttons.append({"slot": 1, "center": a + Vector2(-123.0, 86.0) * k, "radius": 40.0 * k})

func _process(dt: float) -> void:
	pulse += dt
	ult_flash = maxf(0.0, ult_flash - dt)
	for k in _flash.keys():
		_flash[k] = maxf(float(_flash[k]) - dt, 0.0)
	if size != last_size:
		_layout()
	# tir continu : maintien de l'attaque sans visée manuelle
	var st: Dictionary = _state.get(0, {})
	attack_held = not st.is_empty() and not bool(st.get("aim_active", false)) and float(st.get("held_t", 0.0)) > 0.22
	for slot in _state.keys():
		_state[slot]["held_t"] = float(_state[slot].get("held_t", 0.0)) + dt
	queue_redraw()

func _btn_at(p: Vector2) -> int:
	# bouton le plus proche (distance relative au rayon), avec une marge de tolérance au doigt
	var best := -1
	var best_d := 1.22
	for i in buttons.size():
		var b := buttons[i]
		var d := p.distance_to(b["center"]) / float(b["radius"])
		if d <= best_d:
			best_d = d
			best = i
	return best

func _input(ev: InputEvent) -> void:
	if not visible or fighter == null or display_only:
		return
	if ev is InputEventScreenTouch:
		var t := ev as InputEventScreenTouch
		var p := _to_local(t.position)
		if t.pressed:
			var bi := _btn_at(p)
			if bi >= 0:
				var slot: int = buttons[bi]["slot"]
				if not _state.has(slot):
					_state[slot] = {"idx": t.index, "start": p, "aim_active": false, "vec": Vector2.ZERO, "held_t": 0.0, "cancelled": false}
					get_viewport().set_input_as_handled()
				return
			if stick_idx == -1 and p.x < size.x * 0.46 and p.y > size.y * 0.22:
				stick_idx = t.index
				stick_origin = p
				stick_pos = p
				stick_visible = true
				move_vec = Vector2.ZERO
				get_viewport().set_input_as_handled()
		else:
			if t.index == stick_idx:
				stick_idx = -1
				stick_visible = false
				move_vec = Vector2.ZERO
				get_viewport().set_input_as_handled()
			for slot in _state.keys():
				if int(_state[slot]["idx"]) == t.index:
					_release(slot)
					get_viewport().set_input_as_handled()
					break
	elif ev is InputEventScreenDrag:
		var d := ev as InputEventScreenDrag
		var p2 := _to_local(d.position)
		if d.index == stick_idx:
			var v := p2 - stick_origin
			var maxr := 74.0 * k
			if v.length() > maxr:
				stick_origin += v.normalized() * (v.length() - maxr)   # joystick « suiveur »
				v = p2 - stick_origin
			stick_pos = stick_origin + v
			var m := clampf(v.length() / maxr, 0.0, 1.0)
			var dead := Settings.gf("controller_move_deadzone")
			move_vec = v.normalized() * (0.0 if m < dead else clampf((m - dead) / (1.0 - dead), 0.0, 1.0)) if v.length() > 0.5 else Vector2.ZERO
			get_viewport().set_input_as_handled()
			return
		for slot in _state.keys():
			var s: Dictionary = _state[slot]
			if int(s["idx"]) == d.index:
				var center := Vector2.ZERO
				var rad := 50.0
				for b in buttons:
					if int(b["slot"]) == slot:
						center = b["center"]
						rad = float(b["radius"])
				var v2 := p2 - center
				if v2.length() > rad * 0.45 or bool(s["aim_active"]):
					s["aim_active"] = true
					s["vec"] = v2
					s["cancelled"] = v2.length() < rad * 0.3
					var dirw := Vector3(v2.x, 0.0, v2.y).normalized()
					aim_changed.emit(slot, not bool(s["cancelled"]), dirw, clampf(v2.length() / (rad * 2.4), 0.0, 1.0))
				get_viewport().set_input_as_handled()
				break

func _release(slot: int) -> void:
	var s: Dictionary = _state[slot]
	_state.erase(slot)
	aim_changed.emit(slot, false, Vector3.ZERO, 0.0)
	if bool(s["aim_active"]):
		if bool(s["cancelled"]):
			return
		var v: Vector2 = s["vec"]
		var rad := 50.0
		for b in buttons:
			if int(b["slot"]) == slot:
				rad = float(b["radius"])
		cast.emit(slot, true, Vector3(v.x, 0.0, v.y).normalized(), clampf(v.length() / (rad * 2.4), 0.0, 1.0))
	else:
		cast.emit(slot, false, Vector3.ZERO, 0.0)

func _to_local(p: Vector2) -> Vector2:
	# en mode « canvas_items » les événements arrivent déjà dans le repère du viewport
	return p

# ----------------------------------------------------------------------------------------------
# Dessin
# ----------------------------------------------------------------------------------------------
func _icon(slot: int) -> Texture2D:
	if _icons.has(slot):
		return _icons[slot]
	var t: Texture2D = null
	if fighter and slot < fighter.kit.size():
		t = UI.ability_icon(fighter.kit[slot])
	_icons[slot] = t
	return t

func _draw() -> void:
	if fighter == null or not is_instance_valid(fighter) or not fighter.alive:
		return
	if not display_only:
		_draw_stick()
	for b in buttons:
		_draw_button(b)
		if display_only:
			_draw_key_label(b)

func _tex_at(t: Texture2D, c: Vector2, diameter: float, tint: Color = Color.WHITE) -> void:
	if t:
		draw_texture_rect(t, Rect2(c - Vector2(diameter, diameter) * 0.5, Vector2(diameter, diameter)), false, tint)

## secteur de texture (sens horaire depuis le haut) : sert à la jauge de l'ultime
func _wedge_tex(t: Texture2D, c: Vector2, diameter: float, frac: float, tint: Color = Color.WHITE) -> void:
	if t == null or frac <= 0.0:
		return
	var steps := maxi(int(56.0 * minf(frac, 1.0)), 2)
	var pts := PackedVector2Array([c])
	var uvs := PackedVector2Array([Vector2(0.5, 0.5)])
	for i in steps + 1:
		var a := -PI * 0.5 + TAU * minf(frac, 1.0) * float(i) / steps
		var dv := Vector2(cos(a), sin(a))
		pts.append(c + dv * diameter * 0.5 * 0.995)
		uvs.append(Vector2(0.5, 0.5) + dv * 0.4975)
	draw_polygon(pts, PackedColorArray([tint]), uvs, t)

func _sweep(c: Vector2, radius: float, frac: float, col: Color) -> void:
	if frac <= 0.0:
		return
	var steps := maxi(int(48.0 * minf(frac, 1.0)), 2)
	var pts := PackedVector2Array([c])
	var a0 := -PI * 0.5
	for i in steps + 1:
		var a := a0 + TAU * minf(frac, 1.0) * float(i) / steps
		pts.append(c + Vector2(cos(a), sin(a)) * radius)
	draw_colored_polygon(pts, col)

func _text_c(txt: String, c: Vector2, fs: int, col: Color = Color.WHITE) -> void:
	var f2 := Game.font_bold()
	var ts := f2.get_string_size(txt, HORIZONTAL_ALIGNMENT_CENTER, -1, fs)
	var pos := c + Vector2(-ts.x * 0.5, fs * 0.34)
	draw_string_outline(f2, pos, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, 8, OUTLINE)
	draw_string(f2, pos, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)

func _draw_stick() -> void:
	var base := stick_origin if stick_visible else stick_default
	var knob := stick_pos if stick_visible else stick_default
	var alpha := 0.92 if stick_visible else 0.42
	var tb := _t("joystick_base")
	var tk := _t("joystick_knob")
	if tb:
		_tex_at(tb, base, 188.0 * k, Color(1, 1, 1, alpha))
	else:
		draw_circle(base, 82.0, Color(OUTLINE, 0.55 * alpha), true, -1.0, true)
		draw_arc(base, 76.0, 0, TAU, 48, Color(1, 1, 1, 0.55 * alpha), 3.0, true)
	if tk:
		_tex_at(tk, knob + Vector2(0, 4.0 * k), 96.0 * k, Color(0, 0, 0, 0.28 * alpha))
		_tex_at(tk, knob, 92.0 * k, Color(1, 1, 1, alpha) if stick_visible else Color(0.85, 0.85, 0.95, alpha))
	else:
		draw_circle(knob, 40.0, Color(OUTLINE, alpha), true, -1.0, true)
		draw_circle(knob, 35.0, Color(1.0, 0.82, 0.25, alpha), true, -1.0, true)

func _draw_button(b: Dictionary) -> void:
	var slot: int = b["slot"]
	var c: Vector2 = b["center"]
	var r: float = b["radius"]
	var ab: Dictionary = fighter.kit[slot] if slot < fighter.kit.size() else {}
	var st: Dictionary = _state.get(slot, {})
	var held := not st.is_empty()
	var elem: Color = Data.elem_color(String(ab.get("element", "physical")))
	var cdf := fighter.cd_frac(slot)
	var cd_left: float = fighter.cds[slot] if slot < fighter.cds.size() else 0.0
	var is_big := bool(b.get("ult", false))
	var afford := fighter.can_pay(slot)
	var ready := cdf <= 0.0 and afford
	var aiming := held and bool(st.get("aim_active", false))
	var cancelled := aiming and bool(st.get("cancelled", false))
	var press := 0.93 if held else 1.0
	var pop := 1.0 + (sin(pulse * 7.0) * 0.03 if (is_big and ready) else 0.0)
	var rr := r * press * pop
	var cc := c + Vector2(0, 3.0 * k if held else 0.0)
	# ombre portée douce
	draw_circle(c + Vector2(0, 8.0 * k), r * 1.0, Color(0, 0, 0, 0.16), true, -1.0, true)
	draw_circle(c + Vector2(0, 6.0 * k), r * 0.94, Color(0, 0, 0, 0.2), true, -1.0, true)
	var dim := Color(1, 1, 1, 1) if (ready or held) else Color(0.82, 0.82, 0.88, 1)
	if slot == 0:
		_tex_at(_t("btn_attack"), cc, rr * 2.1, Color(1.08, 1.08, 1.08, 1) if held else Color.WHITE)
		if attack_held:
			draw_arc(c, rr * 1.12 + sin(pulse * 10.0) * 3.0 * k, 0, TAU, 56, Color(1, 0.8, 0.4, 0.55), 4.0 * k, true)
	elif slot == 1:
		_tex_at(_t("btn_dash"), cc, rr * 2.1, dim)
		if cdf > 0.0:
			_sweep(cc, rr * 0.93, cdf, Color(0.05, 0.04, 0.1, 0.62))
			_text_c("%.1f" % cd_left, cc, int(rr * 0.62))
	else:
		# fond d'icône teinté par l'élément, puis icône, puis anneau
		var hole := rr * 0.80
		draw_circle(cc, hole, elem.darkened(0.62), true, -1.0, true)
		draw_circle(cc + Vector2(0, -hole * 0.06), hole * 0.9, elem.darkened(0.42), true, -1.0, true)
		var ic := _icon(slot)
		if ic:
			_tex_at(ic, cc, hole * 2.02, Color(1, 1, 1, 1) if ready else Color(0.62, 0.62, 0.7, 1))
		if is_big:
			_tex_at(_t("btn_ult_ring_empty"), cc, rr * 2.2)
			if ready:
				var g := 0.5 + 0.5 * (0.5 + 0.5 * sin(pulse * 6.0))
				_tex_at(_t("btn_skill_ready_glow"), cc, rr * 2.8, Color(1, 1, 1, g))
				_tex_at(_t("btn_ult_ring_ready"), cc, rr * 2.2)
			else:
				_wedge_tex(_t("btn_ult_ring_full"), cc, rr * 2.2, 1.0 - cdf if cdf > 0.0 else 1.0)
		else:
			_tex_at(_t("btn_skill_ring"), cc, rr * 2.14)
		if cdf > 0.0:
			_sweep(cc, hole * 0.98, cdf, Color(0.04, 0.03, 0.1, 0.66))
			_text_c("%.1f" % cd_left, cc, int(rr * 0.7))
		elif not afford:
			_sweep(cc, hole * 0.98, 1.0, Color(0.04, 0.03, 0.1, 0.55))
			_text_c(String("PM" if fighter.mana < fighter.cost_mana(slot) else "END"), cc, int(rr * 0.42), Color("ffd9a0"))
		if _was_cd.get(slot, false) and cdf <= 0.0:
			_flash[slot] = 0.35
		if ready and _flash.get(slot, 0.0) > 0.0:
			var fr: float = _flash[slot]
			draw_arc(c, r * (1.15 + (0.35 - fr) * 1.4), 0, TAU, 40, Color(1, 0.95, 0.6, fr * 2.4), 4.0 * k, true)
	_was_cd[slot] = cdf > 0.0
	# visée manuelle : portée max, zone d'annulation, tige et réticule
	if aiming:
		var v: Vector2 = st["vec"]
		var maxd := r * 2.4
		draw_arc(c, maxd, 0, TAU, 72, Color(1, 1, 1, 0.14), 3.0 * k, true)
		draw_arc(c, r * 0.32, 0, TAU, 28, Color(1, 0.35, 0.35, 0.8 if cancelled else 0.35), 3.0 * k, true)
		var tip := c + v.limit_length(maxd)
		var col := Color(1, 0.4, 0.4, 0.95) if cancelled else Color(1, 1, 1, 0.95)
		draw_line(c, tip, Color(OUTLINE, 0.5), 8.0 * k, true)
		draw_line(c, tip, col, 4.0 * k, true)
		draw_circle(tip, 13.0 * k, Color(OUTLINE, 0.9), true, -1.0, true)
		draw_arc(tip, 9.0 * k, 0, TAU, 24, col, 4.0 * k, true)
		if cancelled:
			draw_circle(cc, rr * 0.98, Color(0.4, 0.05, 0.05, 0.55), true, -1.0, true)
			_text_c("✕", cc, int(rr * 0.9), Color(1, 0.8, 0.8))

func _draw_key_label(b: Dictionary) -> void:
	var c: Vector2 = b["center"]
	var r: float = b["radius"]
	var txt := String(key_labels.get(int(b["slot"]), ""))
	if txt == "":
		return
	var f2 := Game.font_bold()
	var fs := 22
	var ts := f2.get_string_size(txt, HORIZONTAL_ALIGNMENT_CENTER, -1, fs)
	var w := ts.x + 22.0
	var rect := Rect2(c + Vector2(-w * 0.5, r * 0.78), Vector2(w, 30))
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.04, 0.05, 0.1, 0.92)
	sb.border_color = Color("e6bd5c")
	sb.set_border_width_all(2)
	sb.set_corner_radius_all(15)
	sb.anti_aliasing = true
	sb.draw(get_canvas_item(), rect)
	draw_string(f2, rect.position + Vector2(11, 22), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color("f4ecda"))

var _was_cd: Dictionary = {}
var _flash: Dictionary = {}
