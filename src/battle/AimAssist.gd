class_name AimAssist
extends RefCounted
## Aide à la visée tactile : choix automatique des cibles, anticipation du mouvement, aimantation douce en visée manuelle.

const SELF_ARCH := ["buff", "guard", "taunt", "stealth", "time", "nova", "melee_aoe", "heal_aoe", "resurrect"]
const ALLY_ARCH := ["heal", "heal_hot", "heal_chain", "swap"]
const MELEE_ARCH := ["melee_arc", "melee_thrust", "execute"]
const PROJ_ARCH := ["projectile", "volley", "curse", "hook", "chain", "beam", "cone", "drain"]
const GROUND_ARCH := ["ground_aoe", "lob", "trap", "vortex", "summon"]
const MOVE_ARCH := ["dash", "blink"]
const JUMP_ARCH := ["leap", "charge"]

static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)

static func assist_level() -> int:
	return Settings.gi("aim_assist")     # 0 = complète, 1 = aimantation seule, 2 = manuelle

static func enemies_visible(f: Fighter) -> Array[Fighter]:
	var out: Array[Fighter] = []
	for o in f.battle.fighters:
		if o.alive and o.team != f.team and not o.is_hidden_from(f.team):
			out.append(o)
	return out

static func los_ok(f: Fighter, t: Fighter) -> bool:
	return f.battle.arena.segment_hits_obstacle(f.global_position, t.global_position, 0.2) == null

static func lead_point(f: Fighter, t: Fighter, speed: float) -> Vector3:
	var d := flat(t.global_position - f.global_position).length()
	var tt := d / maxf(speed, 1.0)
	return t.global_position + t.vel * tt * 0.9

## Meilleure cible ennemie. prefer_dir/cone_deg servent à l'aimantation en visée manuelle.
static func best_target(f: Fighter, rng: float, need_los: bool, sticky: Fighter = null, prefer_dir: Vector3 = Vector3.ZERO, cone_deg: float = 360.0) -> Fighter:
	var best: Fighter = null
	var best_s := -1e9
	for e in enemies_visible(f):
		var rel := flat(e.global_position - f.global_position)
		var d := rel.length()
		if d > rng + e.radius:
			continue
		if need_los and not los_ok(f, e):
			continue
		var s := -d
		var hp := e.hp_pct()
		if hp < 0.5:
			s += (0.5 - hp) * 9.0
		if e == sticky and sticky != null:
			s += 3.5
		if prefer_dir != Vector3.ZERO and d > 0.01:
			var ang := prefer_dir.angle_to(rel / d)
			if ang > deg_to_rad(cone_deg):
				continue
			s -= ang * 22.0
		if s > best_s:
			best_s = s
			best = e
	return best

static func lowest_ally(f: Fighter, rng: float, include_self: bool = true) -> Fighter:
	var best: Fighter = null
	var bs := 2.0
	for a in f.battle.fighters:
		if not a.alive or a.team != f.team or (a == f and not include_self):
			continue
		if flat(a.global_position - f.global_position).length() > rng + a.radius:
			continue
		var p := a.hp_pct()
		if p < bs:
			bs = p
			best = a
	return best

static func cluster_center(f: Fighter, rng: float, radius: float) -> Variant:
	var best: Variant = null
	var best_n := 0
	for e in enemies_visible(f):
		var d := flat(e.global_position - f.global_position).length()
		if d > rng + 2.0:
			continue
		var c := e.global_position + e.vel * 0.45
		var n := 0
		for o in enemies_visible(f):
			if flat(o.global_position - c).length() <= radius:
				n += 1
		if n > best_n or (n == best_n and best != null and d < flat((best as Vector3) - f.global_position).length()):
			best_n = n
			best = c
	return best

static func clamp_range(f: Fighter, p: Vector3, rng: float) -> Vector3:
	var rel := flat(p - f.global_position)
	if rel.length() > rng and rng > 0.0:
		return f.global_position + rel.normalized() * rng
	return p

# ----------------------------------------------------------------------------------------------
# Lancer rapide (tap) : tout est choisi automatiquement
# ----------------------------------------------------------------------------------------------
static func resolve_quick(f: Fighter, slot: int, sticky: Fighter = null) -> Dictionary:
	var ab: Dictionary = f.kit[slot]
	var arch := String(ab.get("arch", ""))
	var rng: float = float(ab.get("range", 0.0))
	var face := f.facing_dir if f.facing_dir.length() > 0.01 else Vector3(1, 0, 0)
	var level := assist_level()
	if arch in SELF_ARCH:
		return {"ok": true, "aim": f.global_position + face, "target": f}
	if arch in ALLY_ARCH or (arch == "field" and String(ab.get("field_kind", "heal")) == "heal") or (arch == "shield" and not bool(ab.get("aoe", false)) and f.role() in ["healer", "support"]):
		var al := lowest_ally(f, maxf(rng, 12.0), arch != "swap")
		if al != null and (al.hp_pct() < 0.98 or arch in ["swap", "shield", "field"]):
			return {"ok": true, "aim": al.global_position, "target": al}
		if arch in ["heal", "heal_hot", "heal_chain"]:
			return {"ok": f.hp_pct() < 0.98, "aim": f.global_position + face, "target": f}
		return {"ok": true, "aim": f.global_position + face, "target": f}
	if arch == "shield" or arch == "field":
		return {"ok": true, "aim": f.global_position + face, "target": f}
	if arch in MOVE_ARCH:
		var dir := f.move_input.normalized() if f.move_input.length() > 0.2 else face
		return {"ok": true, "aim": f.global_position + dir * maxf(rng, 5.0), "target": null}
	var need_los := arch in PROJ_ARCH
	var look := rng if arch in PROJ_ARCH else (rng if arch in JUMP_ARCH else maxf(rng * 1.25, 4.5))
	if arch in GROUND_ARCH:
		var cc: Variant = cluster_center(f, rng, float(ab.get("radius", 3.5)))
		if cc != null:
			return {"ok": true, "aim": clamp_range(f, cc, rng), "target": null}
		var near := best_target(f, rng + 3.0, false, sticky)
		if near != null:
			return {"ok": true, "aim": clamp_range(f, near.global_position, rng), "target": near}
		return {"ok": true, "aim": f.global_position + face * minf(rng * 0.6, 7.0), "target": null}
	var t: Fighter = best_target(f, look + (2.5 if level == 0 else 0.0), need_los, sticky)
	if t == null:
		# rien à portée : on tire/frappe dans la direction du regard (pas de gaspillage pour les compétences)
		var ok := bool(ab.get("basic", false)) or arch in PROJ_ARCH
		return {"ok": ok, "aim": f.global_position + face * maxf(rng, 4.0), "target": null}
	var aim := t.global_position
	if arch in ["projectile", "volley", "curse"] and level < 2:
		aim = lead_point(f, t, float(ab.get("speed", 25.0)))
	return {"ok": true, "aim": aim, "target": t}

# ----------------------------------------------------------------------------------------------
# Visée manuelle (glisser) : direction + magnitude, avec aimantation douce vers les ennemis proches de la ligne de tir
# ----------------------------------------------------------------------------------------------
static func resolve_manual(f: Fighter, slot: int, dir: Vector3, mag: float, sticky: Fighter = null) -> Dictionary:
	var ab: Dictionary = f.kit[slot]
	var arch := String(ab.get("arch", ""))
	var rng: float = float(ab.get("range", 0.0))
	var level := assist_level()
	if dir.length() < 0.01:
		return resolve_quick(f, slot, sticky)
	dir = flat(dir).normalized()
	if arch in SELF_ARCH:
		return {"ok": true, "aim": f.global_position + dir, "target": f}
	if arch in ALLY_ARCH:
		var al := best_ally_near_line(f, dir, maxf(rng, 12.0))
		return {"ok": true, "aim": (al.global_position if al else f.global_position + dir * 6.0), "target": al}
	if arch in MOVE_ARCH or arch in JUMP_ARCH:
		var dist: float = maxf(rng * clampf(mag, 0.3, 1.0), 2.5)
		return {"ok": true, "aim": f.global_position + dir * dist, "target": null}
	if arch in GROUND_ARCH:
		var p := f.global_position + dir * maxf(rng * clampf(mag, 0.2, 1.0), 2.0)
		if level < 2:
			var snap := best_target_near_point(f, p, 3.2)
			if snap != null:
				p = clamp_range(f, snap.global_position + snap.vel * 0.4, rng)
		return {"ok": true, "aim": p, "target": null}
	var rr: float = rng if rng > 0.0 else 10.0
	var need_los := arch in PROJ_ARCH
	var cone := 0.0
	match level:
		0: cone = 16.0
		1: cone = 9.0
		_: cone = 0.0
	if cone > 0.0:
		var t := best_target(f, rr, need_los, sticky, dir, cone)
		if t != null:
			var aim := t.global_position
			if arch in ["projectile", "volley", "curse"]:
				aim = lead_point(f, t, float(ab.get("speed", 25.0)))
			return {"ok": true, "aim": aim, "target": t}
	return {"ok": true, "aim": f.global_position + dir * maxf(rr, 4.0), "target": null}

static func best_ally_near_line(f: Fighter, dir: Vector3, rng: float) -> Fighter:
	var best: Fighter = null
	var best_a := 999.0
	for a in f.battle.fighters:
		if not a.alive or a.team != f.team or a == f:
			continue
		var rel := flat(a.global_position - f.global_position)
		if rel.length() > rng or rel.length() < 0.1:
			continue
		var ang := dir.angle_to(rel.normalized())
		if ang < best_a and ang < deg_to_rad(40.0):
			best_a = ang
			best = a
	return best

static func best_target_near_point(f: Fighter, p: Vector3, radius: float) -> Fighter:
	var best: Fighter = null
	var bd := radius
	for e in enemies_visible(f):
		var d := flat(e.global_position - p).length()
		if d < bd:
			bd = d
			best = e
	return best
