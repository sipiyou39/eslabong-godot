class_name Kit
extends RefCounted
## Bibliothèque de pièces modulaires importées des GLB (kit_bodies/gear/weapons/props).

const FILES := [
	"res://assets/models/kit/kit_bodies.glb", "res://assets/models/kit/kit_gear.glb",
	"res://assets/models/kit/kit_weapons.glb", "res://assets/models/kit/kit_props.glb",
	"res://assets/models/kit/kit_scifi.glb", "res://assets/models/kit/kit_greek.glb",
]
static var _loaded := false
static var _index: Dictionary = {}     # nom -> {node, xform (vers racine)}
static var _roots: Array[Node] = []
static var contract: Dictionary = {}
static var pivots: Dictionary = {}

static func ensure_loaded() -> void:
	if _loaded:
		return
	_loaded = true
	var f := FileAccess.open("res://data/kit_contract.json", FileAccess.READ)
	if f:
		contract = JSON.parse_string(f.get_as_text())
	var pv: Dictionary = contract.get("pivots", {})
	for k in pv:
		var a: Array = pv[k]
		pivots[k] = Vector3(a[0], a[1], a[2])
	for path in FILES:
		if not ResourceLoader.exists(path):
			continue
		var ps: Variant = load(path)
		if ps is PackedScene:
			var inst: Node = (ps as PackedScene).instantiate()
			_roots.append(inst)
			_collect(inst, inst, Transform3D.IDENTITY)
	print("[Kit] ", _index.size(), " pièces chargées")

static func _collect(root: Node, node: Node, parent_xf: Transform3D) -> void:
	var xf := parent_xf
	if node is Node3D and node != root:
		xf = parent_xf * (node as Node3D).transform
	if node is MeshInstance3D and node != root:
		var nm := String(node.name)
		if not _index.has(nm):
			_index[nm] = {"node": node, "xform": xf}
	for c in node.get_children():
		_collect(root, c, xf)

static func has_part(name: String) -> bool:
	ensure_loaded()
	return _index.has(name)

static func part_count() -> int:
	ensure_loaded()
	return _index.size()

static func part_origin(name: String) -> Vector3:
	ensure_loaded()
	if not _index.has(name):
		return Vector3.ZERO
	return (_index[name]["xform"] as Transform3D).origin

## Duplique une pièce ; la transformation locale est remise à l'identité (rotation conservée si le nœud en portait une)
static func make_part(name: String) -> MeshInstance3D:
	ensure_loaded()
	if not _index.has(name):
		return null
	var src: MeshInstance3D = _index[name]["node"]
	var xf: Transform3D = _index[name]["xform"]
	var mi := MeshInstance3D.new()
	mi.mesh = src.mesh
	mi.name = name
	mi.transform = Transform3D(xf.basis, Vector3.ZERO)
	return mi

static func pivot(name: String) -> Vector3:
	ensure_loaded()
	return pivots.get(name, Vector3.ZERO)
