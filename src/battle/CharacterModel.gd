class_name CharacterModel
extends Node3D
## Personnage 3D modulaire animé procéduralement. Utilise les pièces du kit Blender si présentes, sinon des primitives.

const TOON := preload("res://src/shaders/toon_character.gdshader")
const OUTLINE := preload("res://src/shaders/outline.gdshader")
const GLOBAL_SCALE := 1.5

var mats: Array[ShaderMaterial] = []
var outline_mats: Array[ShaderMaterial] = []
var species: String = "human"
var tpl: Dictionary = {}
var weapon_style: String = "slash"
var use_kit: bool = false

var j_body: Node3D
var j_pelvis: Node3D
var j_torso: Node3D
var j_head: Node3D
var j_sh_l: Node3D
var j_sh_r: Node3D
var j_hip_l: Node3D
var j_hip_r: Node3D
var socket_r: Node3D
var socket_l: Node3D
var back_node: Node3D
var weapon_r: Node3D
var weapon_l: Node3D
var weapon_l_is_shield := false
var head_top_y: float = 1.7

# animation
var loco: float = 0.0
var phase: float = 0.0
var os_name: String = ""
var os_t: float = 0.0
var os_dur: float = 0.5
var channeling: bool = false
var stunned: bool = false
var dead: bool = false
var flash_t: float = 0.0
var hit_t: float = 0.0
var _rot := {}
var _idle_t: float = 0.0
var _scale_mul: float = 1.0
var accent_color: Color = Color.WHITE
var _cape_phase: float = 0.0

func build(template: Dictionary, palette_override: Array = [], variant_seed: int = 0, shiny: bool = false) -> void:
	tpl = template
	species = template.get("species", "human")
	Kit.ensure_loaded()
	use_kit = Kit.has_part("body_%s_torso" % species)
	var pal: Array = palette_override if not palette_override.is_empty() else template.get("palette", ["#aa4444", "#444455", "#ddbb55", "#ddaa88"])
	var cols: Array[Color] = []
	for h in pal:
		cols.append(Color(str(h)))
	while cols.size() < 4:
		cols.append(Color.GRAY)
	if shiny:
		cols[0] = _hue_shift(cols[0], 0.5)
		cols[1] = _hue_shift(cols[1], 0.5)
	accent_color = cols[2]
	weapon_style = _style_of(template.get("weapon_main", ""))
	_scale_mul = float(template.get("scale", 1.0)) * GLOBAL_SCALE
	j_body = Node3D.new()
	j_body.name = "Body"
	add_child(j_body)
	if use_kit:
		_build_kit(cols)
	else:
		_build_fallback(cols)
	scale = Vector3.ONE * _scale_mul
	for k in ["pelvis", "torso", "head", "sh_l", "sh_r", "hip_l", "hip_r"]:
		_rot[k] = Vector3.ZERO

static func _hue_shift(c: Color, amt: float) -> Color:
	var h := c.h + amt
	h = h - floor(h)
	return Color.from_hsv(h, c.s, c.v)

const GUNS := ["blaster", "rifle_plasma", "railgun", "med_gun"]

static func _style_of(w: String) -> String:
	if w.begins_with("bow") or w.begins_with("crossbow") or w in GUNS:
		return "shoot"
	if w.begins_with("staff") or w in ["wand", "orb", "tome", "censer", "paddles", "lantern", "plasma_staff", "thunderbolt", "caduceus", "lyre", "controller"]:
		return "cast"
	if w in ["spear", "halberd", "rapier", "trident", "bident", "spear_greek"]:
		return "thrust"
	if w in ["fists", "claws", "whip", "gauntlet"]:
		return "punch"
	if w in ["hammer_great", "axe_great", "axe_double", "sword_great", "pick", "wrench"]:
		return "smash"
	return "slash"

func _make_mat(cols: Array[Color], mask: bool, flat: Color = Color.WHITE) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = TOON
	m.set_shader_parameter("use_mask", mask)
	m.set_shader_parameter("c_primary", cols[0])
	m.set_shader_parameter("c_secondary", cols[1])
	m.set_shader_parameter("c_accent", cols[2])
	m.set_shader_parameter("c_skin", cols[3])
	m.set_shader_parameter("flat_color", flat)
	m.set_shader_parameter("rim_color", cols[2].lerp(Color(0.7, 0.85, 1.0), 0.5))
	if Settings.gb("unit_outlines_enabled"):
		var om := ShaderMaterial.new()
		om.shader = OUTLINE
		om.set_shader_parameter("thickness", 0.014)
		m.next_pass = om
		outline_mats.append(om)
	mats.append(m)
	return m

func _joint(parent: Node3D, pos: Vector3, nm: String) -> Node3D:
	var j := Node3D.new()
	j.name = nm
	j.position = pos
	parent.add_child(j)
	return j

# ----------------------------------------------------------------------------------------------
# Construction avec le kit Blender
# ----------------------------------------------------------------------------------------------
func _add_part(part_name: String, joint: Node3D, mat: ShaderMaterial) -> MeshInstance3D:
	var mi := Kit.make_part(part_name)
	if mi == null:
		return null
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	joint.add_child(mi)
	return mi

func _build_kit(cols: Array[Color]) -> void:
	var mat := _make_mat(cols, true)
	var P := Kit.pivots
	j_pelvis = _joint(j_body, P["pelvis"], "Pelvis")
	j_torso = _joint(j_pelvis, P["torso"] - P["pelvis"], "Torso")
	j_head = _joint(j_torso, P["head"] - P["torso"], "Head")
	j_sh_l = _joint(j_torso, P["shoulder_l"] - P["torso"], "ShoulderL")
	j_sh_r = _joint(j_torso, P["shoulder_r"] - P["torso"], "ShoulderR")
	j_hip_l = _joint(j_pelvis, P["hip_l"] - P["pelvis"], "HipL")
	j_hip_r = _joint(j_pelvis, P["hip_r"] - P["pelvis"], "HipR")
	var sp := species
	_add_part("body_%s_pelvis" % sp, j_pelvis, mat)
	_add_part("body_%s_torso" % sp, j_torso, mat)
	_add_part("body_%s_head" % sp, j_head, mat)
	_add_part("body_%s_arm_l" % sp, j_sh_l, mat)
	_add_part("body_%s_arm_r" % sp, j_sh_r, mat)
	_add_part("body_%s_leg_l" % sp, j_hip_l, mat)
	_add_part("body_%s_leg_r" % sp, j_hip_r, mat)
	# équipement
	var head: String = tpl.get("head", "none")
	if head != "none" and head != "":
		var hmi := _add_part(head, j_head, mat)
		if hmi != null and sp == "alien":
			hmi.scale = Vector3(1.12, 1.18, 1.12)       # couvre-chefs modélisés pour un crâne humain
	var torso: String = tpl.get("torso", "none")
	if torso != "none" and torso != "":
		_add_part("armor_" + torso, j_torso, mat)
		_add_part("armor_%s_skirt" % torso, j_pelvis, mat)
	var sh: String = tpl.get("shoulder", "none")
	if sh != "none" and sh != "":
		_add_part("shoulder_%s_l" % sh, j_sh_l, mat)
		_add_part("shoulder_%s_r" % sh, j_sh_r, mat)
	var back: String = tpl.get("back", "none")
	if back != "none" and back != "":
		var holder := _joint(j_torso, Vector3.ZERO, "BackHolder")
		_add_part("back_" + back, holder, mat)
		back_node = holder
	_make_sockets()
	_attach_weapons(mat)
	head_top_y = P["head"].y + 0.5

func _make_sockets() -> void:
	var P := Kit.pivots
	socket_r = _joint(j_sh_r, P["hand_r"] - P["shoulder_r"], "SocketR")
	socket_l = _joint(j_sh_l, P["hand_l"] - P["shoulder_l"], "SocketL")

func _attach_weapons(mat: ShaderMaterial) -> void:
	var main: String = tpl.get("weapon_main", "")
	var off: String = tpl.get("weapon_off", "")
	weapon_r = _spawn_weapon(main, true, mat)
	if off != "":
		weapon_l = _spawn_weapon(off, false, mat)
	elif main in ["claws", "fists", "paddles", "energy_dagger", "gauntlet"]:
		weapon_l = _spawn_weapon(main, false, mat)

func _spawn_weapon(wname: String, right: bool, mat: ShaderMaterial) -> Node3D:
	if wname == "":
		return null
	var holder := Node3D.new()
	holder.name = "Wpn" + ("R" if right else "L")
	var sock := socket_r if right else socket_l
	var side := "_r" if right else "_l"
	var part := "wpn_" + wname
	var mi: MeshInstance3D = null
	if Kit.has_part(part + side):
		mi = Kit.make_part(part + side)
	elif Kit.has_part(part):
		mi = Kit.make_part(part)
	if mi == null:
		mi = _fallback_weapon(wname)
	else:
		mi.material_override = mat
	holder.add_child(mi)
	sock.add_child(holder)
	var is_shield := wname.find("shield") >= 0
	if not right:
		weapon_l_is_shield = is_shield
	_apply_grip(holder, wname, right, is_shield)
	return holder

func _apply_grip(holder: Node3D, wname: String, right: bool, is_shield: bool) -> void:
	# rotation de prise : l'arme pointe vers l'avant quand le bras est levé
	var deg := Vector3(100, 0, 0)
	var style := _style_of(wname)
	if is_shield:
		deg = Vector3(70, 0, 0)
		holder.position = Vector3(0.1 if not right else -0.1, 0.0, 0.08)
	elif style == "cast":
		deg = Vector3(30, 0, 0)
	elif wname.begins_with("bow") or wname.begins_with("crossbow") or wname in GUNS:
		deg = Vector3(90, 0, 0)
	elif wname in ["tome", "orb", "lantern"]:
		deg = Vector3(70, 0, 0)
	elif style == "punch":
		deg = Vector3(90, 0, 0)
	holder.rotation_degrees = deg

func _fallback_weapon(wname: String) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var col := Color(0.75, 0.75, 0.8)
	var m: Mesh
	if wname.begins_with("shield"):
		var c := CylinderMesh.new()
		c.top_radius = 0.34
		c.bottom_radius = 0.34
		c.height = 0.07
		m = c
		mi.rotation_degrees = Vector3(90, 0, 0)
		col = Color(0.5, 0.35, 0.25)
	elif wname.begins_with("bow") or wname.begins_with("crossbow"):
		var b := BoxMesh.new()
		b.size = Vector3(0.05, 0.9, 0.08)
		m = b
		col = Color(0.5, 0.35, 0.2)
	elif wname.begins_with("staff") or wname == "wand":
		var cc := CylinderMesh.new()
		cc.top_radius = 0.03
		cc.bottom_radius = 0.035
		cc.height = 1.5 if wname != "wand" else 0.5
		m = cc
		mi.position = Vector3(0, 0.45, 0)
		col = Color(0.45, 0.3, 0.2)
	elif wname in ["spear", "halberd"]:
		var cs := CylinderMesh.new()
		cs.top_radius = 0.025
		cs.bottom_radius = 0.025
		cs.height = 2.0
		m = cs
		mi.position = Vector3(0, 0.6, 0)
	elif wname.begins_with("hammer") or wname.begins_with("mace") or wname.begins_with("axe") or wname == "pick":
		var bx := BoxMesh.new()
		bx.size = Vector3(0.28, 0.3, 0.14)
		m = bx
		mi.position = Vector3(0, 0.6, 0)
	else:
		var bl := BoxMesh.new()
		bl.size = Vector3(0.07, 1.0, 0.025)
		m = bl
		mi.position = Vector3(0, 0.5, 0)
	mi.mesh = m
	var mm := StandardMaterial3D.new()
	mm.albedo_color = col
	mm.metallic = 0.6
	mm.roughness = 0.4
	mi.material_override = mm
	return mi

# ----------------------------------------------------------------------------------------------
# Repli en primitives
# ----------------------------------------------------------------------------------------------
func _prim(mesh: Mesh, parent: Node3D, pos: Vector3, col: Color, rot: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.position = pos
	mi.rotation = rot
	var cols: Array[Color] = [col, col, col, col]
	mi.material_override = _make_mat(cols, false, col)
	parent.add_child(mi)
	return mi

func _capsule(r: float, h: float) -> CapsuleMesh:
	var c := CapsuleMesh.new()
	c.radius = r
	c.height = h
	c.radial_segments = 16
	c.rings = 6
	return c

func _build_fallback(cols: Array[Color]) -> void:
	var P := {
		"pelvis": Vector3(0, 0.74, 0), "torso": Vector3(0, 0.78, 0), "head": Vector3(0, 1.20, 0),
		"shoulder_l": Vector3(0.30, 1.10, 0), "shoulder_r": Vector3(-0.30, 1.10, 0),
		"hip_l": Vector3(0.13, 0.72, 0), "hip_r": Vector3(-0.13, 0.72, 0),
		"hand_l": Vector3(0.34, 0.62, 0.02), "hand_r": Vector3(-0.34, 0.62, 0.02),
	}
	Kit.pivots = P
	var skin := cols[3]
	var cloth := cols[0]
	var trim := cols[1]
	j_pelvis = _joint(j_body, P["pelvis"], "Pelvis")
	j_torso = _joint(j_pelvis, P["torso"] - P["pelvis"], "Torso")
	j_head = _joint(j_torso, P["head"] - P["torso"], "Head")
	j_sh_l = _joint(j_torso, P["shoulder_l"] - P["torso"], "ShoulderL")
	j_sh_r = _joint(j_torso, P["shoulder_r"] - P["torso"], "ShoulderR")
	j_hip_l = _joint(j_pelvis, P["hip_l"] - P["pelvis"], "HipL")
	j_hip_r = _joint(j_pelvis, P["hip_r"] - P["pelvis"], "HipR")
	var wide := 1.0
	match species:
		"orc", "minotaur", "beast": wide = 1.2
		"goblin": wide = 0.85
	_prim(_capsule(0.19 * wide, 0.5), j_pelvis, Vector3(0, 0.0, 0), trim)
	_prim(_capsule(0.25 * wide, 0.62), j_torso, Vector3(0, 0.22, 0), cloth)
	_prim(_sphere(0.24 if species != "goblin" else 0.3), j_head, Vector3(0, 0.22, 0), skin)
	# yeux / museau selon espèce
	var eye_col := Color(1, 0.9, 0.5) if species in ["demon", "skeleton", "beast"] else Color(0.1, 0.1, 0.12)
	_prim(_sphere(0.045), j_head, Vector3(0.09, 0.26, 0.2), eye_col)
	_prim(_sphere(0.045), j_head, Vector3(-0.09, 0.26, 0.2), eye_col)
	if species == "minotaur" or species == "demon":
		var horn := CylinderMesh.new()
		horn.top_radius = 0.0
		horn.bottom_radius = 0.06
		horn.height = 0.3
		_prim(horn, j_head, Vector3(0.18, 0.42, 0), cols[2], Vector3(0, 0, -0.5))
		_prim(horn, j_head, Vector3(-0.18, 0.42, 0), cols[2], Vector3(0, 0, 0.5))
	if species == "orc" or species == "goblin":
		var ear := CylinderMesh.new()
		ear.top_radius = 0.0
		ear.bottom_radius = 0.07
		ear.height = 0.25
		_prim(ear, j_head, Vector3(0.28, 0.25, 0), skin, Vector3(0, 0, -1.4))
		_prim(ear, j_head, Vector3(-0.28, 0.25, 0), skin, Vector3(0, 0, 1.4))
	_prim(_capsule(0.075 * wide, 0.5), j_sh_l, Vector3(0.02, -0.24, 0.0), skin if tpl.get("torso", "") in ["wraps", "none", ""] else cloth)
	_prim(_capsule(0.075 * wide, 0.5), j_sh_r, Vector3(-0.02, -0.24, 0.0), skin if tpl.get("torso", "") in ["wraps", "none", ""] else cloth)
	_prim(_capsule(0.09 * wide, 0.74), j_hip_l, Vector3(0, -0.36, 0), trim)
	_prim(_capsule(0.09 * wide, 0.74), j_hip_r, Vector3(0, -0.36, 0), trim)
	# couvre-chef simplifié
	var head: String = tpl.get("head", "none")
	if head.begins_with("helm"):
		_prim(_sphere(0.27), j_head, Vector3(0, 0.27, 0), cols[1].lightened(0.2))
	elif head.begins_with("hat_wizard") or head.begins_with("hat_witch") or head == "hat_mitre":
		var cone := CylinderMesh.new()
		cone.top_radius = 0.02
		cone.bottom_radius = 0.24
		cone.height = 0.5
		_prim(cone, j_head, Vector3(0, 0.55, 0), cols[0])
	elif head.begins_with("hood"):
		_prim(_sphere(0.27), j_head, Vector3(0, 0.22, -0.03), cols[0])
	var sh: String = tpl.get("shoulder", "none")
	if sh != "none" and sh != "":
		_prim(_sphere(0.15), j_sh_l, Vector3(0.05, 0.02, 0), cols[1].lightened(0.15))
		_prim(_sphere(0.15), j_sh_r, Vector3(-0.05, 0.02, 0), cols[1].lightened(0.15))
	var back: String = tpl.get("back", "none")
	if back.begins_with("cape"):
		var qb := BoxMesh.new()
		qb.size = Vector3(0.5, 0.8 if back == "cape_long" else 0.5, 0.04)
		var holder := _joint(j_torso, Vector3(0, 0.35, -0.2), "BackHolder")
		_prim(qb, holder, Vector3(0, -0.3, 0), cols[0].darkened(0.1))
		back_node = holder
	elif back.begins_with("wings"):
		var holder2 := _joint(j_torso, Vector3(0, 0.35, -0.22), "BackHolder")
		var wq := BoxMesh.new()
		wq.size = Vector3(0.9, 0.7, 0.04)
		_prim(wq, holder2, Vector3(0.5, 0.1, 0), cols[1], Vector3(0, 0.4, 0.3))
		_prim(wq, holder2, Vector3(-0.5, 0.1, 0), cols[1], Vector3(0, -0.4, -0.3))
		back_node = holder2
	_make_sockets()
	var mat := mats[0]
	_attach_weapons(mat)
	head_top_y = 1.75

func _sphere(r: float) -> SphereMesh:
	var s := SphereMesh.new()
	s.radius = r
	s.height = r * 2.0
	s.radial_segments = 20
	s.rings = 10
	return s

# ----------------------------------------------------------------------------------------------
# Matériaux dynamiques
# ----------------------------------------------------------------------------------------------
func set_param(p: String, v: Variant) -> void:
	for m in mats:
		m.set_shader_parameter(p, v)

func flash(col: Color = Color(1, 1, 1, 0.9), t: float = 0.12) -> void:
	flash_t = t
	set_param("flash_color", col)

func set_ghost(v: float) -> void:
	set_param("ghost", v)
	for om in outline_mats:
		om.set_shader_parameter("alpha", 1.0 - v)

func set_tint(c: Color, amt: float) -> void:
	set_param("tint_color", c)
	set_param("tint_amount", amt)

func set_glow(v: float) -> void:
	set_param("accent_glow", v)

func set_outline_color(c: Color) -> void:
	for om in outline_mats:
		om.set_shader_parameter("outline_color", c)

# ----------------------------------------------------------------------------------------------
# Animation
# ----------------------------------------------------------------------------------------------
func trigger(anim: String, dur: float = 0.5) -> void:
	os_name = anim
	os_t = 0.0
	os_dur = maxf(dur, 0.05)

func attack_anim(dur: float) -> void:
	var a := "atk_" + weapon_style
	if weapon_style == "punch" and randi() % 2 == 0:
		a = "atk_punch2"
	trigger(a, dur)

func hit_react() -> void:
	hit_t = 0.22

func die() -> void:
	dead = true
	os_name = "death"
	os_t = 0.0
	os_dur = 0.9

func revive() -> void:
	dead = false
	os_name = ""
	set_param("dissolve", 0.0)

func _lerp_rot(key: String, target: Vector3, k: float) -> Vector3:
	var cur: Vector3 = _rot.get(key, Vector3.ZERO)
	cur = cur.lerp(target, k)
	_rot[key] = cur
	return cur

func _process(dt: float) -> void:
	if j_body == null:
		return
	_idle_t += dt
	if flash_t > 0.0:
		flash_t -= dt
		if flash_t <= 0.0:
			set_param("flash_color", Color(1, 1, 1, 0))
	if hit_t > 0.0:
		hit_t -= dt
	var k := 1.0 - exp(-dt * 16.0)
	phase += dt * (6.0 + 8.0 * loco) * (1.0 if loco > 0.05 else 0.0)
	var ar := Vector3.ZERO      # bras droit
	var al := Vector3.ZERO      # bras gauche
	var tr := Vector3.ZERO      # torse
	var hd := Vector3.ZERO
	var lr := Vector3.ZERO      # jambe droite
	var ll := Vector3.ZERO
	var pr := Vector3.ZERO      # bassin
	var root_off := Vector3.ZERO
	var root_rot := Vector3.ZERO
	var squash := 0.0
	# --- idle de combat (arme levée)
	var breathe := sin(_idle_t * 2.6)
	var guard := 0.0 if dead else 1.0
	ar.x = -0.55 * guard + breathe * 0.03
	al.x = -0.45 * guard - breathe * 0.03
	ar.z = 0.12
	al.z = -0.12
	if weapon_l_is_shield:
		al.x = -1.05
		al.z = 0.0
	if weapon_style == "shoot" and not dead:
		ar.x = -1.1
		al.x = -1.25
	elif weapon_style == "cast" and not dead:
		ar.x = -0.9
		ar.z = 0.05
	tr.x = 0.02 + breathe * 0.015
	hd.x = -breathe * 0.02
	root_off.y = breathe * 0.008
	# --- locomotion
	if loco > 0.02:
		var s := sin(phase)
		var c := cos(phase)
		lr.x = s * 0.85 * loco
		ll.x = -s * 0.85 * loco
		ar.x += -s * 0.55 * loco * 0.8
		al.x += s * 0.55 * loco * 0.8
		tr.x += 0.12 * loco
		tr.y = c * 0.12 * loco
		root_off.y += abs(s) * 0.07 * loco
		root_rot.z = c * 0.04 * loco
		pr.y = -c * 0.1 * loco
	# --- action ponctuelle
	if os_name != "":
		os_t += dt
		var t := clampf(os_t / os_dur, 0.0, 1.0)
		match os_name:
			"atk_slash", "atk_smash":
				var big := os_name == "atk_smash"
				if t < 0.38:
					var u := t / 0.38
					ar.x = lerpf(ar.x, -2.9 if big else -2.5, ease(u, 0.4))
					ar.z = lerpf(ar.z, 0.4, u)
					tr.y = lerpf(tr.y, -0.55, u)
					tr.x += -0.15 * u
					root_off.z = -0.06 * u
				elif t < 0.62:
					var u2 := (t - 0.38) / 0.24
					ar.x = lerpf(-2.5 if not big else -2.9, -0.35, ease(u2, 0.25))
					ar.z = lerpf(0.4, -0.1, u2)
					tr.y = lerpf(-0.55, 0.65, u2)
					tr.x += lerpf(-0.15, 0.3, u2)
					root_off.z = lerpf(-0.06, 0.25, u2)
					if big: root_rot.x = 0.18 * u2
				else:
					var u3 := (t - 0.62) / 0.38
					ar.x = lerpf(-0.35, ar.x, u3)
					tr.y = lerpf(0.65, tr.y, u3)
					root_off.z = lerpf(0.25, 0.0, u3)
				al.x = lerpf(al.x, -1.2, 0.5)
			"atk_thrust":
				if t < 0.4:
					var u := t / 0.4
					ar.x = lerpf(ar.x, -1.2, u)
					ar.z = lerpf(ar.z, 0.5, u)
					tr.y = lerpf(tr.y, -0.5, u)
					root_off.z = -0.14 * u
				elif t < 0.6:
					var u2 := (t - 0.4) / 0.2
					ar.x = lerpf(-1.2, -1.55, u2)
					ar.z = lerpf(0.5, 0.0, u2)
					tr.y = lerpf(-0.5, 0.3, u2)
					root_off.z = lerpf(-0.14, 0.45, u2)
				else:
					var u3 := (t - 0.6) / 0.4
					root_off.z = lerpf(0.45, 0.0, u3)
					ar.x = lerpf(-1.55, ar.x, u3)
				al.x = lerpf(al.x, -0.9, 0.5)
			"atk_shoot":
				ar.x = -1.5
				al.x = -1.55
				ar.z = 0.0
				al.z = 0.0
				tr.y = -0.25
				if t > 0.35 and t < 0.6:
					root_off.z = -0.12 * sin((t - 0.35) / 0.25 * PI)
					tr.x -= 0.1
			"atk_punch", "atk_punch2":
				var r_is := os_name == "atk_punch"
				var u4 := sin(t * PI)
				if r_is:
					ar.x = lerpf(ar.x, -1.6, u4)
					tr.y = 0.5 * u4
					al.x = lerpf(al.x, -0.9, 0.4)
				else:
					al.x = lerpf(al.x, -1.6, u4)
					tr.y = -0.5 * u4
					ar.x = lerpf(ar.x, -0.9, 0.4)
				root_off.z = 0.18 * u4
			"cast":
				var u5 := ease(minf(t * 2.2, 1.0), 0.5)
				ar.x = lerpf(ar.x, -2.35, u5)
				al.x = lerpf(al.x, -2.1, u5)
				ar.z = lerpf(ar.z, 0.35, u5)
				al.z = lerpf(al.z, -0.35, u5)
				tr.x += -0.2 * u5
				hd.x = -0.25 * u5
				root_off.y += 0.04 * u5
			"channel":
				ar.x = -1.55 + sin(_idle_t * 30.0) * 0.03
				al.x = -1.55
				ar.z = 0.0
				al.z = 0.0
				tr.x += 0.1
			"hit":
				pass
			"dash":
				root_rot.x = 0.75 * sin(minf(t * 1.6, 1.0) * PI * 0.6 + 0.4)
				lr.x = 1.0
				ll.x = -1.0
				ar.x = 0.8
				al.x = 0.8
				squash = 0.12
			"leap":
				var up := sin(t * PI)
				root_off.y += up * 0.5
				ar.x = -2.7 * up
				al.x = -2.7 * up
				lr.x = -0.8 * up
				ll.x = 0.5 * up
				root_rot.x = -0.2 * up
			"buff":
				var u6 := sin(t * PI)
				ar.x = lerpf(ar.x, -2.9, u6)
				al.x = lerpf(al.x, -2.9, u6)
				tr.x += -0.3 * u6
				hd.x = -0.35 * u6
				root_off.y += 0.08 * u6
			"victory":
				ar.x = -2.9 + sin(_idle_t * 9.0) * 0.3
				al.x = -2.9 - sin(_idle_t * 9.0) * 0.3
				root_off.y += abs(sin(_idle_t * 6.0)) * 0.15
			"death":
				var u7 := ease(t, 0.35)
				root_rot.x = lerpf(0.0, -1.45, u7)
				root_off.y = lerpf(0.0, -0.55, u7)
				ar.x = lerpf(ar.x, -2.2, u7)
				al.x = lerpf(al.x, -1.0, u7)
				lr.x = lerpf(lr.x, 0.3, u7)
		if t >= 1.0 and os_name != "death" and os_name != "victory":
			os_name = ""
	if stunned and not dead:
		hd.z = sin(_idle_t * 9.0) * 0.25
		tr.z = sin(_idle_t * 7.0) * 0.12
		ar.x = -0.2
		al.x = -0.2
	if hit_t > 0.0 and not dead:
		var h := hit_t / 0.22
		root_rot.x += -0.28 * h
		squash += 0.1 * h
		root_off.z -= 0.12 * h
	# --- application avec lissage
	j_sh_r.rotation = _lerp_rot("sh_r", ar, k)
	j_sh_l.rotation = _lerp_rot("sh_l", al, k)
	j_torso.rotation = _lerp_rot("torso", tr, k)
	j_head.rotation = _lerp_rot("head", hd, k)
	j_hip_r.rotation = _lerp_rot("hip_r", lr, k)
	j_hip_l.rotation = _lerp_rot("hip_l", ll, k)
	j_pelvis.rotation = _lerp_rot("pelvis", pr, k)
	j_body.position = j_body.position.lerp(root_off, k)
	j_body.rotation = j_body.rotation.lerp(root_rot, k)
	j_body.scale = Vector3(1.0 + squash * 0.5, 1.0 - squash, 1.0 + squash * 0.5)
	# bouclier garde l'orientation vers l'avant
	if weapon_l and weapon_l_is_shield:
		weapon_l.rotation.x = -j_sh_l.rotation.x
		weapon_l.position.z = 0.1
	if back_node:
		_cape_phase += dt * (3.0 + loco * 8.0)
		back_node.rotation.x = 0.08 + loco * 0.35 + sin(_cape_phase) * (0.04 + 0.08 * loco)

func hand_world(right: bool = true) -> Vector3:
	var s := socket_r if right else socket_l
	if s and s.is_inside_tree():
		return s.global_position
	return global_position + Vector3(0, 1.0, 0)

func head_world() -> Vector3:
	if j_head and j_head.is_inside_tree():
		return j_head.global_position + Vector3(0, 0.25 * _scale_mul, 0)
	return global_position + Vector3(0, 1.6, 0)

func height() -> float:
	return head_top_y * _scale_mul
