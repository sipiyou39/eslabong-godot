class_name ClubBackdrop
extends Node3D
## Décor 3D du quartier général (menu principal + hub) : salle Blender, lumière, caméra orbitale lente, combattants en pose idle.

var arena: Arena
var vfx: Vfx
var cam: Camera3D
var fx_root: Node3D
var t: float = 0.0
var orbit_center: Vector3 = Vector3(0, 1.4, 0)
var orbit_radius: float = 9.5
var orbit_height: float = 4.2
var orbit_speed: float = 0.06
var orbit_phase: float = -1.3
var orbit_amp: float = 0.35
var models: Array[CharacterModel] = []
var fight_root: Node3D
var focus_offset: Vector3 = Vector3.ZERO
var target_offset: Vector3 = Vector3.ZERO
var pan_x: float = 0.0
var theme_id: String = "club"

func setup(theme: String = "club") -> void:
	theme_id = theme
	fx_root = Node3D.new()
	add_child(fx_root)
	vfx = Vfx.new()
	vfx.root = fx_root
	add_child(vfx)
	arena = Arena.new()
	add_child(arena)
	cam = Camera3D.new()
	cam.fov = 38.0
	cam.current = true
	add_child(cam)
	vfx.camera = cam
	arena.setup(theme, vfx)
	fight_root = Node3D.new()
	add_child(fight_root)
	var attrs := CameraAttributesPractical.new()
	attrs.dof_blur_far_enabled = true
	attrs.dof_blur_far_distance = 16.0
	attrs.dof_blur_far_transition = 14.0
	attrs.dof_blur_amount = 0.05
	cam.attributes = attrs

## Place les combattants (Array de dictionnaires de mercenaires) en demi-cercle devant la caméra
func show_mercs(mercs: Array) -> void:
	for m in models:
		if is_instance_valid(m):
			m.get_parent().queue_free()
	models.clear()
	var n := mercs.size()
	for i in n:
		var m: Dictionary = mercs[i]
		var holder := Node3D.new()
		fight_root.add_child(holder)
		var ang := PI * 0.5 + (float(i) - (n - 1) * 0.5) * 0.52
		var r := 4.2
		holder.position = Vector3(cos(ang) * r * 1.2 - 0.0, 0, -sin(ang) * r * 0.6 + 0.8)
		holder.position = Vector3((float(i) - (n - 1) * 0.5) * 2.1, 0, -1.0 + abs(float(i) - (n - 1) * 0.5) * 0.45)
		var cm := CharacterModel.new()
		holder.add_child(cm)
		cm.build(MercLogic.tpl_for(m), [], int(m.get("variant", 0)), bool(m.get("shiny", false)))
		holder.rotation.y = atan2(-holder.position.x * 0.12, 1.0)
		models.append(cm)

func _process(dt: float) -> void:
	t += dt
	var a := orbit_phase + sin(t * orbit_speed * 3.0) * orbit_amp
	focus_offset = focus_offset.lerp(target_offset, 1.0 - exp(-dt * 2.5))
	var c := orbit_center + focus_offset
	cam.global_position = c + Vector3(sin(a) * orbit_radius + pan_x, orbit_height, cos(a) * orbit_radius)
	cam.look_at(c, Vector3.UP)
	for i in models.size():
		var m := models[i]
		if is_instance_valid(m) and fmod(t + i * 1.7, 9.0) < dt:
			m.trigger("cast" if i % 2 == 0 else "buff", 1.0)

func set_view(center: Vector3, radius: float, height: float) -> void:
	orbit_center = center
	orbit_radius = radius
	orbit_height = height
