class_name Abilities
extends RefCounted
## Exécuteurs d'archétypes de compétences. Tout est piloté par les données de res://data/abilities.json.

const MELEE_ARCH := ["melee_arc", "melee_thrust", "melee_aoe", "execute", "charge", "leap", "hook"]
const CHANNEL_ARCH := ["beam", "cone", "drain"]

# ----------------------------------------------------------------------------------------------
# Utilitaires
# ----------------------------------------------------------------------------------------------
static func _valid_node(n: Variant) -> Node:
	if n != null and is_instance_valid(n):
		return n
	return null

static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)

static func dir_to(a: Vector3, b: Vector3) -> Vector3:
	var d := flat(b - a)
	return d.normalized() if d.length() > 0.001 else Vector3.ZERO

static func color_of(ab: Dictionary) -> Color:
	return Data.elem_color(String(ab.get("element", "physical")))

static func is_magic(ab: Dictionary) -> bool:
	return String(ab.get("element", "physical")) != "physical" and not (String(ab.get("arch", "")) in MELEE_ARCH)

static func cast_allows_move(c: Dictionary) -> bool:
	var arch := String(c["ab"].get("arch", ""))
	return not (arch in ["resurrect", "time", "summon"]) or bool(c.get("fired", false))

static func cast_move_mult(c: Dictionary) -> float:
	var ab: Dictionary = c["ab"]
	var arch := String(ab.get("arch", ""))
	if bool(ab.get("basic", false)):
		return 0.75
	if arch in CHANNEL_ARCH:
		return 0.4
	if arch in ["resurrect", "time"]:
		return 0.15
	if arch in ["dash", "blink"]:
		return 1.0
	return 0.5

static func enemies_in_circle(f: Fighter, center: Vector3, r: float, include_invisible: bool = true) -> Array[Fighter]:
	var out: Array[Fighter] = []
	for o in f.battle.fighters:
		if o.alive and o.team != f.team:
			if flat(o.global_position - center).length() <= r + o.radius:
				if include_invisible or not o.has_status("invisible"):
					out.append(o)
	return out

static func allies_in_circle(f: Fighter, center: Vector3, r: float, include_self: bool = true) -> Array[Fighter]:
	var out: Array[Fighter] = []
	for o in f.battle.fighters:
		if o.alive and o.team == f.team and (include_self or o != f):
			if flat(o.global_position - center).length() <= r + o.radius:
				out.append(o)
	return out

static func angle_ok(origin: Vector3, fwd: Vector3, p: Vector3, half_angle_rad: float) -> bool:
	var d := dir_to(origin, p)
	if d == Vector3.ZERO:
		return true
	return fwd.angle_to(d) <= half_angle_rad

static func sfx_for(ab: Dictionary, phase: String = "cast") -> String:
	var arch := String(ab.get("arch", ""))
	var el := String(ab.get("element", "physical"))
	if phase == "cast":
		if arch in ["melee_arc", "melee_thrust", "melee_aoe", "execute"]:
			return "swing_heavy" if float(ab.get("dmg", 1.0)) > 2.0 else "swing_light"
		if arch in ["dash"]:
			return "dash_whoosh"
		if arch in ["blink"]:
			return "teleport_blink"
		if arch in ["leap", "charge"]:
			return "dash_whoosh"
		if arch == "summon":
			return "summon"
		if arch in ["heal", "heal_aoe", "heal_hot", "heal_chain", "resurrect"]:
			return "heal_chime"
		if arch in ["buff", "shield", "guard", "taunt", "stealth"]:
			return "buff_up"
		if arch == "projectile" and el == "physical":
			return "arrow_shoot"
		if el == "physical":
			return "swing_light"
		return "spell_" + el
	return "hit_slash"

# ----------------------------------------------------------------------------------------------
# Début de lancer
# ----------------------------------------------------------------------------------------------
static func begin(f: Fighter, slot: int, ab: Dictionary, aim: Vector3, tgt: Fighter) -> Dictionary:
	var arch := String(ab.get("arch", "melee_arc"))
	var rng: float = float(ab.get("range", 0.0))
	var adir := dir_to(f.global_position, aim)
	if adir == Vector3.ZERO:
		adir = f.facing_dir if f.facing_dir.length() > 0.01 else Vector3(1, 0, 0)
	var aim_pt := aim
	# visée au sol bornée par la portée
	if rng > 0.0 and arch in ["ground_aoe", "blink", "leap", "trap", "summon", "charge", "dash", "hook", "chain"]:
		var dist := flat(aim - f.global_position).length()
		if dist > rng:
			aim_pt = f.global_position + adir * rng
	var dur: float = float(ab.get("cast", 0.2))
	if bool(ab.get("ultimate", false)):
		dur += 0.3
	if arch in ["melee_arc", "melee_thrust", "melee_aoe", "execute"]:
		dur = maxf(dur, 0.22)
	var c := {"slot": slot, "ab": ab, "t": 0.0, "dur": dur, "aim": aim_pt, "aim_dir": adir, "target": tgt, "fired": false, "channel_left": 0.0, "tick": 0.0}
	f.pay_and_cooldown(slot)
	f.cast = c
	f.facing_dir = adir
	if f.has_status("invisible") and not (arch in ["stealth"]):
		f.remove_status("invisible")
	# animation
	var m := f.model
	if arch in ["dash"]:
		pass
	elif arch in ["heal", "heal_aoe", "heal_hot", "heal_chain", "resurrect", "buff", "shield", "taunt", "guard", "time", "summon", "nova", "ground_aoe", "curse", "trap", "stealth", "blink"]:
		m.trigger("cast" if arch != "buff" else "buff", maxf(dur * 1.6, 0.5))
	elif arch in CHANNEL_ARCH:
		m.trigger("cast", dur * 1.8)
	elif arch == "leap":
		m.trigger("leap", 0.55)
	elif arch == "charge":
		m.trigger("dash", 0.45)
	elif arch in ["projectile", "volley", "chain", "hook"]:
		if m.weapon_style == "cast" or (not bool(ab.get("basic", false)) and m.weapon_style != "shoot"):
			m.trigger("cast", maxf(dur * 2.0, 0.4))
		elif m.weapon_style == "shoot":
			m.trigger("atk_shoot", maxf(dur * 2.2, 0.38))
		else:
			m.attack_anim(maxf(dur * 2.0, 0.4))
	else:
		m.attack_anim(maxf(dur / 0.5, 0.36))
	if not (arch in ["dash", "blink"]) or true:
		var s := sfx_for(ab, "cast")
		Audio.play_at(s, f.global_position, -4.0)
	# télégraphies
	if arch == "ground_aoe":
		var z := Zone.new()
		f.battle.add_fx(z)
		z.setup_ground(f, ab, aim_pt, dur + float(ab.get("delay", 0.8)))
		c["zone_started"] = true
	elif arch in ["nova", "melee_aoe"] and float(ab.get("radius", 0)) > 3.0 and not bool(ab.get("basic", false)):
		f.battle.vfx.ring(f.global_position, color_of(ab), float(ab.get("radius", 4)) * 0.8, dur + 0.1, "glow_ring", 0.09)
	elif arch in ["cone", "beam"]:
		pass
	return c

static func update_cast(f: Fighter, c: Dictionary, dt: float) -> void:
	if not f.alive:
		f.cast.clear()
		return
	var ab: Dictionary = c["ab"]
	var arch := String(ab.get("arch", ""))
	if f.has_status("stun") or f.has_status("freeze"):
		end_cast(f, c, true)
		return
	# visée dynamique (joueur / IA)
	if f.player_index >= 0:
		var pa: Vector3 = f.battle.player_aim(f)
		var d := dir_to(f.global_position, pa)
		if d != Vector3.ZERO and (arch in CHANNEL_ARCH or not c["fired"]):
			c["aim_dir"] = d
			c["aim"] = pa
	elif c.get("target") != null and is_instance_valid(c["target"]) and c["target"].alive and (arch in CHANNEL_ARCH or not c["fired"]) and arch != "ground_aoe":
		var tg: Fighter = c["target"]
		if tg.team != f.team or arch in ["heal", "heal_aoe", "heal_hot", "heal_chain", "shield", "swap"]:
			var d2 := dir_to(f.global_position, tg.global_position)
			if d2 != Vector3.ZERO:
				c["aim_dir"] = d2
				c["aim"] = tg.global_position
	c["t"] += dt
	if not c["fired"]:
		if c["t"] >= c["dur"]:
			c["fired"] = true
			fire(f, c)
			if arch in CHANNEL_ARCH:
				c["channel_left"] = float(ab.get("dur", 1.2))
				c["tick"] = 0.0
				f.model.trigger("channel", c["channel_left"] + 0.1)
				_channel_start(f, c)
			else:
				if not f.cast.is_empty():
					end_cast(f, c, false)
	else:
		if arch in CHANNEL_ARCH:
			c["channel_left"] -= dt
			c["tick"] += dt
			channel_tick(f, c, dt)
			if c["channel_left"] <= 0.0 or f.mana <= 0.0 and arch == "drain":
				end_cast(f, c, false)

static func end_cast(f: Fighter, c: Dictionary, interrupted: bool) -> void:
	if c.has("beam_node") and is_instance_valid(c["beam_node"]):
		c["beam_node"].queue_free()
	if c.has("cone_node") and is_instance_valid(c["cone_node"]):
		c["cone_node"].queue_free()
	f.cast = {}
	f.model.channeling = false
	if not interrupted and not bool(c["ab"].get("basic", false)):
		f.post_cast_slow = 0.12

# ----------------------------------------------------------------------------------------------
# Déclenchement
# ----------------------------------------------------------------------------------------------
static func power_of(f: Fighter, ab: Dictionary, key: String = "dmg") -> float:
	return f.power * float(ab.get(key, 1.0))

static func hit_opts(f: Fighter, ab: Dictionary, extra: Dictionary = {}) -> Dictionary:
	var o := {"element": String(ab.get("element", "physical")), "basic": bool(ab.get("basic", false)), "mag": is_magic(ab), "ab": ab}
	o.merge(extra, true)
	return o

static func apply_statuses(f: Fighter, dst: Fighter, ab: Dictionary, scale: float = 1.0) -> void:
	if not dst.alive:
		return
	var is_basic := bool(ab.get("basic", false))
	for s in ab.get("status", []):
		var st: String = s
		if is_basic and st in ["stun", "freeze", "fear", "silence", "root"]:
			continue
		if is_basic and randf() > 0.3:
			continue
		if dst.team == f.team:
			continue
		var dur := 3.0
		var pw := 1.0
		match st:
			"stun": dur = 0.9 if float(ab.get("dmg", 1.0)) < 2.4 else 1.4
			"freeze": dur = 1.2
			"root": dur = 1.6
			"fear": dur = 1.5
			"silence": dur = 2.2
			"slow": dur = 2.8
			"bleed", "burn", "poison": dur = 4.0
			"mark": dur = 6.0
			"weaken": dur = 4.5
			"armor_break": dur = 4.5
		dst.add_status(st, dur * scale, pw, f)

static func fire(f: Fighter, c: Dictionary) -> void:
	var ab: Dictionary = c["ab"]
	var arch := String(ab.get("arch", "melee_arc"))
	var b := f.battle
	var col := color_of(ab)
	var origin := f.global_position
	var fwd: Vector3 = c["aim_dir"]
	var aim: Vector3 = c["aim"]
	match arch:
		"melee_arc", "execute":
			var rng: float = float(ab.get("range", 2.8))
			var half := deg_to_rad(float(ab.get("angle", 120.0))) * 0.5
			var hits := 0
			for e in enemies_in_circle(f, origin, rng):
				if angle_ok(origin, fwd, e.global_position, half) or flat(e.global_position - origin).length() < 1.0:
					var mult := 1.0
					if arch == "execute" and e.hp_pct() < 0.35:
						mult = 2.0
					var o := hit_opts(f, ab, {"kb": 2.5 if float(ab.get("dmg", 1.0)) > 1.8 else 1.0, "kb_dir": fwd})
					b.deal_damage(f, e, power_of(f, ab) * mult, o)
					apply_statuses(f, e, ab)
					hits += 1
			var sz := rng * 1.25
			b.vfx.slash_arc(origin + fwd * rng * 0.4 + Vector3(0, 0.9, 0), atan2(fwd.x, fwd.z), col.lerp(Color.WHITE, 0.35), sz, 0.22)
			if hits > 0:
				b.vfx.shake(0.12 + 0.05 * hits)
			_after_basic_echo(f, ab)
		"melee_thrust":
			var rng2: float = float(ab.get("range", 4.0))
			var wid: float = float(ab.get("radius", 0.9))
			for e in enemies_in_circle(f, origin + fwd * rng2 * 0.5, rng2 * 0.5 + 0.5):
				var rel := flat(e.global_position - origin)
				var along := rel.dot(fwd)
				var side := absf(rel.cross(fwd).y)
				if along > -0.3 and along < rng2 + e.radius and side < wid + e.radius:
					b.deal_damage(f, e, power_of(f, ab), hit_opts(f, ab, {"kb": 1.5, "kb_dir": fwd}))
					apply_statuses(f, e, ab)
			b.vfx.slash_arc(origin + fwd * rng2 * 0.5 + Vector3(0, 0.9, 0), atan2(fwd.x, fwd.z), col.lerp(Color.WHITE, 0.4), rng2 * 1.1, 0.18, 4)
			b.vfx.burst(origin + fwd * rng2 * 0.9 + Vector3(0, 0.9, 0), col, 5, 3.0, 0.2, 0.25, "spark_star4", 0.0, 40.0, fwd)
			_after_basic_echo(f, ab)
		"melee_aoe":
			var r: float = float(ab.get("radius", 3.6))
			for e in enemies_in_circle(f, origin, r):
				b.deal_damage(f, e, power_of(f, ab), hit_opts(f, ab, {"kb": 3.0, "kb_dir": dir_to(origin, e.global_position)}))
				apply_statuses(f, e, ab)
			b.vfx.ring(origin, col, r * 1.15, 0.4)
			b.vfx.slash_arc(origin + Vector3(0, 0.9, 0), randf() * TAU, col.lerp(Color.WHITE, 0.3), r * 2.0, 0.28, 2)
			b.vfx.shake(0.3)
		"nova":
			var rn: float = float(ab.get("radius", 5.0))
			for e in enemies_in_circle(f, origin, rn):
				b.deal_damage(f, e, power_of(f, ab), hit_opts(f, ab, {"aoe": true, "kb": 3.5, "kb_dir": dir_to(origin, e.global_position)}))
				apply_statuses(f, e, ab)
			for a in allies_in_circle(f, origin, rn, false):
				b.deal_damage(f, a, power_of(f, ab), hit_opts(f, ab, {"aoe": true, "ff": true}))
			b.vfx.element_burst(origin, String(ab.get("element", "physical")), rn)
		"projectile", "curse":
			_fire_projectile(f, c, ab, fwd, 0.0)
		"volley":
			var n: int = int(ab.get("count", 5))
			var spread := deg_to_rad(float(ab.get("spread", 36.0)))
			for i in n:
				var ang := (float(i) - (n - 1) * 0.5) * (spread / maxf(n - 1, 1))
				_fire_projectile(f, c, ab, fwd.rotated(Vector3.UP, ang), 0.0)
		"hook":
			_fire_projectile(f, c, ab, fwd, 0.0, {"hook": true})
		"ground_aoe":
			pass   # la zone gère elle-même sa détonation
		"chain":
			_do_chain(f, c, ab)
		"leap":
			var dest: Vector3 = b.arena.clamp_point(aim, f.radius)
			f.forced = {"type": "leap", "from": f.global_position, "to": dest, "t": 0.0, "dur": 0.5, "ab": ab, "height": 3.0}
			b.vfx.ring(f.global_position, col, 2.0, 0.3)
			Audio.play_at("dash_whoosh", f.global_position)
		"charge":
			var dist := minf(flat(aim - origin).length(), float(ab.get("range", 9.0)))
			f.forced = {"type": "charge", "dir": fwd, "t": 0.0, "dur": clampf(dist / 24.0, 0.2, 0.45), "speed": 24.0, "ab": ab, "hit": []}
			f.model.trigger("dash", 0.4)
		"dash":
			var d := f.move_input.normalized() if f.move_input.length() > 0.2 else fwd
			if f.player_index < 0 and c.get("target") != null:
				d = fwd
			f.forced = {"type": "dash", "dir": d, "t": 0.0, "dur": 0.2, "speed": float(ab.get("range", 6.0)) / 0.2, "ab": ab}
			f.model.trigger("dash", 0.3)
			f.vel = Vector3.ZERO
			if f.mods.has("dash_def_perc"):
				f.add_status("dash_def", 3.0, 1.0, f)
			if f.mods.has("echo_dash"):
				f.echo_ready_until = f.battle.time + 4.0
			b.vfx.burst(origin + Vector3(0, 0.3, 0), col.lerp(Color.WHITE, 0.5), 8, 2.5, 0.4, 0.5, "dust_puff", 0.0, 90.0, -d)
		"blink":
			var dest2: Vector3 = b.arena.push_out(b.arena.clamp_point(aim, f.radius), f.radius)
			b.vfx.element_burst(origin, String(ab.get("element", "arcane")), 1.8)
			f.global_position = dest2
			f.vel = Vector3.ZERO
			b.vfx.element_burst(dest2, String(ab.get("element", "arcane")), 1.8)
			Audio.play_at("teleport_blink", dest2)
			if float(ab.get("dmg", 0.0)) > 0.0 or String(ab.get("id", "")).contains("strike"):
				for e in enemies_in_circle(f, dest2, 2.6):
					b.deal_damage(f, e, power_of(f, ab, "dmg") if float(ab.get("dmg", 0.0)) > 0.0 else f.power * 1.2, hit_opts(f, ab))
		"summon":
			_do_summon(f, ab, aim)
		"trap":
			var z := Zone.new()
			b.add_fx(z)
			z.setup_trap(f, ab, aim)
		"drain", "beam", "cone":
			pass  # géré en canalisation
		"heal":
			var t := _pick_heal_target(f, c, float(ab.get("range", 15.0)))
			if t:
				b.heal(f, t, power_of(f, ab, "heal"), {"element": "holy", "ab": ab})
				b.vfx.burst(t.global_position + Vector3(0, 0.3, 0), Color("7affb0"), 10, 2.0, 0.9, 0.35, "heal_plus", 3.0, 30.0)
				if t != f:
					b.vfx.lightning(f.model.hand_world(), t.global_position + Vector3(0, 1.0, 0), Color("9affc0"), 0.12, 0.2, 0.2)
		"heal_aoe":
			var rr: float = float(ab.get("radius", 6.0))
			for a in allies_in_circle(f, origin, rr):
				b.heal(f, a, power_of(f, ab, "heal"), {"ab": ab})
				b.vfx.burst(a.global_position + Vector3(0, 0.3, 0), Color("7affb0"), 6, 2.0, 0.9, 0.3, "heal_plus", 3.0, 30.0)
			b.vfx.ring(origin, Color("7affb0"), rr * 1.1, 0.6, "glow_ring")
			b.vfx.ring(origin, Color("ffffff"), rr * 0.8, 0.45, "shock_ring")
		"heal_hot":
			var th := _pick_heal_target(f, c, float(ab.get("range", 15.0)))
			if th:
				th.add_status("regen", float(ab.get("dur", 6.0)), power_of(f, ab, "heal") / float(ab.get("dur", 6.0)) * 0.5 * 2.0, f)
				b.vfx.burst(th.global_position + Vector3(0, 0.3, 0), Color("7affb0"), 8, 2.0, 0.9, 0.3, "heal_plus", 3.0, 30.0)
		"heal_chain":
			var t1 := _pick_heal_target(f, c, float(ab.get("range", 15.0)))
			var done: Array[Fighter] = []
			var cur := t1
			var amt := power_of(f, ab, "heal")
			var hops: int = int(ab.get("bounces", 3))
			var src_pos := f.model.hand_world()
			for i in hops + 1:
				if cur == null:
					break
				b.heal(f, cur, amt, {"ab": ab})
				b.vfx.lightning(src_pos, cur.global_position + Vector3(0, 1.0, 0), Color("9affc0"), 0.14, 0.3, 0.3)
				src_pos = cur.global_position + Vector3(0, 1.0, 0)
				done.append(cur)
				amt *= 0.8
				var nxt: Fighter = null
				var best := 9999.0
				for a in allies_in_circle(f, cur.global_position, float(ab.get("radius", 7.0))):
					if a in done:
						continue
					var sc := a.hp_pct()
					if sc < best:
						best = sc
						nxt = a
				cur = nxt
		"resurrect":
			var dead: Fighter = null
			for o in b.fighters:
				if o.team == f.team and not o.alive and not o.is_summon:
					if dead == null or flat(o.global_position - origin).length() < flat(dead.global_position - origin).length():
						dead = o
			if dead:
				dead.revive(float(ab.get("heal", 0.5)))
				f.st["res"] += 1
				b.vfx.burst(dead.global_position + Vector3(0, 0.3, 0), Color("ffe9a0"), 24, 5.0, 1.2, 0.6, "light_ray", 4.0, 30.0)
				b.vfx.ring(dead.global_position, Color("ffe9a0"), 4.0, 0.9, "glow_ring")
				b.vfx.light_flash(dead.global_position, Color("ffe9a0"), 4.0, 8.0, 0.6)
				Audio.play_at("resurrect", dead.global_position)
				b.hud_event_text("%s ressuscite %s" % [f.display_name, dead.display_name], Color("ffe9a0"))
		"swap":
			var ts := _pick_heal_target(f, c, float(ab.get("range", 18.0)), true)
			if ts and ts != f:
				var pa := f.global_position
				f.global_position = ts.global_position
				ts.global_position = pa
				b.vfx.element_burst(pa, "holy", 1.5)
				b.vfx.element_burst(f.global_position, "holy", 1.5)
				ts.add_status("shield", 4.0, ts.max_hp * 0.15, f)
		"shield":
			var amt2: float = f.max_hp * float(ab.get("absorb", 0.22)) * (1.0 + f._m("healing_done_perc") / 100.0)
			var tsh: Fighter = f
			if c.get("target") != null and is_instance_valid(c["target"]) and c["target"].team == f.team and c["target"].alive:
				tsh = c["target"]
				amt2 = f.max_hp * float(ab.get("absorb", 0.22))
			tsh.add_status("shield", float(ab.get("dur", 5.0)), amt2, f)
			b.vfx.ring(tsh.global_position, Color("9fd8ff"), 2.5, 0.5, "glow_ring")
			b.vfx.burst(tsh.global_position + Vector3(0, 0.9, 0), Color("9fd8ff"), 10, 2.0, 0.7, 0.4, "shield_hex", 0.0, 180.0)
			b.hud_hint_status(tsh, "Barrière")
		"guard":
			if String(ab.get("guard_kind", "parry")) == "invuln":
				f.add_status("invulnerable", float(ab.get("dur", 2.0)), 1.0, f)
			else:
				f.add_status("armor_up", float(ab.get("dur", 2.5)) * 1.5, 1.0, f)
				f.add_status("thorns", float(ab.get("dur", 2.5)) * 1.5, 1.0, f)
				f.add_status("invulnerable", 0.35, 1.0, f)
			b.vfx.ring(origin, Color("ffffff"), 2.2, 0.4)
		"buff":
			var kind := String(ab.get("buff", "empower"))
			f.add_status(kind, float(ab.get("dur", 7.0)), 1.0, f)
			if kind == "haste":
				f.add_status("haste", float(ab.get("dur", 7.0)), 1.0, f)
			b.vfx.ring(origin, col, 2.5, 0.5, "glow_ring")
			b.vfx.burst(origin + Vector3(0, 0.3, 0), col, 14, 3.0, 0.8, 0.35, "spark_star4", 2.0, 80.0)
			b.hud_hint_status(f, String(Data.STATUS_INFO.get(kind, {}).get("name", kind)))
		"taunt":
			var rt: float = float(ab.get("radius", 9.0))
			for e in enemies_in_circle(f, origin, rt):
				e.add_status("taunted", float(ab.get("dur", 3.0)), 1.0, f)
			f.add_status("armor_up", float(ab.get("dur", 3.5)) + 1.0, 1.0, f)
			b.vfx.ring(origin, Color("ff5a3c"), rt * 0.9, 0.5)
			b.vfx.shake(0.2)
		"stealth":
			f.add_status("invisible", float(ab.get("dur", 4.0)), 1.0, f)
			b.vfx.smoke(origin + Vector3(0, 0.4, 0), Color(0.2, 0.2, 0.25, 0.7), 8, 1.0)
		"time":
			_do_time(f, ab)
	if f.player_index >= 0 or arch in ["projectile"]:
		pass

static func _after_basic_echo(f: Fighter, ab: Dictionary) -> void:
	if bool(ab.get("basic", false)) and f.mods.has("echo_dash") and f.echo_ready_until > f.battle.time and f.echo_cd <= 0.0:
		f.echo_cd = 6.0
		f.echo_ready_until = 0.0
		var pct := f._m("echo_dash") / 100.0
		for e in enemies_in_circle(f, f.global_position, float(ab.get("range", 3.0)) + 0.8):
			f.battle.deal_damage(f, e, power_of(f, ab) * pct, {"element": String(ab.get("element", "physical")), "relic": true})

static func _pick_heal_target(f: Fighter, c: Dictionary, rng: float, exclude_self: bool = false) -> Fighter:
	var t: Variant = c.get("target")
	if t != null and is_instance_valid(t) and t.alive and t.team == f.team and (not exclude_self or t != f):
		return t
	var best: Fighter = null
	var best_s := 2.0
	for a in allies_in_circle(f, f.global_position, rng, not exclude_self):
		var s := a.hp_pct()
		if f.player_index >= 0:
			# joueur : l'allié le plus proche de la visée
			s = flat(a.global_position - c["aim"]).length() * 0.1
		if s < best_s:
			best_s = s
			best = a
	return best if best else (f if not exclude_self else null)

# ----------------------------------------------------------------------------------------------
# Projectiles
# ----------------------------------------------------------------------------------------------
static func _fire_projectile(f: Fighter, c: Dictionary, ab: Dictionary, dir: Vector3, y_off: float, extra: Dictionary = {}) -> void:
	var p := Projectile.new()
	f.battle.add_fx(p)
	var spd: float = float(ab.get("speed", 24.0))
	if bool(ab.get("basic", false)):
		spd += f._m("projectile_speed_flat")
	var start := f.model.hand_world(true)
	start.y = 1.1
	start += dir * 0.4
	var params := {"owner": f, "ab": ab, "pos": start, "dir": dir, "speed": spd, "range": float(ab.get("range", 16.0)), "radius": float(ab.get("radius", 0.45)),
		"pierce": int(ab.get("pierce", 0)), "homing": float(ab.get("homing", 0.0)), "explode": float(ab.get("explode", 0.0)), "bounces": int(ab.get("bounces", 0)),
		"returning": bool(ab.get("returning", false)), "target": c.get("target")}
	params.merge(extra, true)
	p.setup(params)

static func _do_chain(f: Fighter, c: Dictionary, ab: Dictionary) -> void:
	var b := f.battle
	var col := color_of(ab)
	var first: Fighter = null
	var t: Variant = c.get("target")
	if t != null and is_instance_valid(t) and t.alive and t.team != f.team:
		first = t
	else:
		var best := 9999.0
		for e in enemies_in_circle(f, c["aim"], 6.0):
			var d := flat(e.global_position - c["aim"]).length()
			if d < best:
				best = d
				first = e
	if first == null:
		for e in enemies_in_circle(f, f.global_position, float(ab.get("range", 14.0))):
			first = e
			break
	if first == null:
		b.vfx.lightning(f.model.hand_world(), f.global_position + c["aim_dir"] * float(ab.get("range", 14.0)) + Vector3(0, 1.0, 0), col, 0.2, 0.2)
		return
	var hit: Array[Fighter] = []
	var cur: Fighter = first
	var src := f.model.hand_world()
	var amt := power_of(f, ab)
	var bounces: int = int(ab.get("bounces", 4))
	for i in bounces + 1:
		if cur == null:
			break
		b.vfx.lightning(src, cur.global_position + Vector3(0, 1.0, 0), col, 0.2, 0.28, 0.5)
		b.deal_damage(f, cur, amt, hit_opts(f, ab, {"kb": 0.5}))
		apply_statuses(f, cur, ab, 0.6)
		b.vfx.hit_fx(cur.global_position, String(ab.get("element", "lightning")), false, 0.8)
		hit.append(cur)
		src = cur.global_position + Vector3(0, 1.0, 0)
		amt *= 0.85
		var nxt: Fighter = null
		var bd := 9999.0
		for e in enemies_in_circle(f, cur.global_position, float(ab.get("radius", 7.0))):
			if e in hit:
				continue
			var d := flat(e.global_position - cur.global_position).length()
			if d < bd:
				bd = d
				nxt = e
		cur = nxt
	Audio.play_at("spell_lightning", first.global_position)

# ----------------------------------------------------------------------------------------------
# Canalisation
# ----------------------------------------------------------------------------------------------
static func _channel_start(f: Fighter, c: Dictionary) -> void:
	var ab: Dictionary = c["ab"]
	var arch := String(ab.get("arch", ""))
	var col := color_of(ab)
	if arch in ["beam", "drain"]:
		var bm := f.battle.vfx.beam_mesh(0.9 if arch == "beam" else 0.35, col)
		f.battle.add_fx(bm)
		c["beam_node"] = bm
	elif arch == "cone":
		var cn := f.battle.vfx.burst(f.global_position + Vector3(0, 1.0, 0), col, 40, 9.0, 0.6, 0.8, "fire_tongue_0" if String(ab.get("element")) == "fire" else "soft_glow", 0.0, 22.0, c["aim_dir"])
		cn.one_shot = false
		cn.explosiveness = 0.0
		cn.amount = 60
		c["cone_node"] = cn
	Audio.play_at("beam_loop", f.global_position, -6.0)

static func channel_tick(f: Fighter, c: Dictionary, dt: float) -> void:
	var ab: Dictionary = c["ab"]
	var arch := String(ab.get("arch", ""))
	var b := f.battle
	var col := color_of(ab)
	var dir: Vector3 = c["aim_dir"]
	f.facing_dir = dir
	var origin := f.global_position
	var total_dur: float = float(ab.get("dur", 1.2))
	var per_sec: float = power_of(f, ab) / maxf(total_dur, 0.3)
	var interval := 0.2
	var do_tick: bool = c["tick"] >= interval
	if do_tick:
		c["tick"] -= interval
	match arch:
		"beam":
			var rng: float = float(ab.get("range", 12.0))
			var end_pt := origin + dir * rng
			var hit_obs: Variant = b.arena.segment_hits_obstacle(origin, end_pt)
			if hit_obs != null:
				end_pt = hit_obs
			var bn: MeshInstance3D = _valid_node(c.get("beam_node")) as MeshInstance3D
			if bn and is_instance_valid(bn):
				var len := flat(end_pt - origin).length()
				bn.global_position = f.model.hand_world() if f.model else origin
				bn.global_position.y = 1.1
				bn.look_at(bn.global_position + dir, Vector3.UP)
				bn.scale = Vector3(1.0 + sin(Time.get_ticks_msec() * 0.05) * 0.15, 1.0, len)
			if do_tick:
				for e in enemies_in_circle(f, origin + dir * rng * 0.5, rng * 0.5 + 0.5):
					var rel := flat(e.global_position - origin)
					var along := rel.dot(dir)
					if along > 0.0 and along < flat(end_pt - origin).length() + e.radius and absf(rel.cross(dir).y) < float(ab.get("radius", 0.9)) + e.radius:
						b.deal_damage(f, e, per_sec * interval, hit_opts(f, ab, {"tick": true}))
						apply_statuses(f, e, ab, 0.5)
						b.vfx.burst(e.global_position + Vector3(0, 1.0, 0), col, 2, 3.0, 0.2, 0.25, "spark_star4", 0.0, 180.0)
		"cone":
			var cn: CPUParticles3D = _valid_node(c.get("cone_node")) as CPUParticles3D
			if cn and is_instance_valid(cn):
				cn.global_position = f.model.hand_world() if f.model else origin
				cn.global_position.y = 1.0
				cn.direction = dir
			if do_tick:
				var rng2: float = float(ab.get("range", 7.5))
				var half := deg_to_rad(float(ab.get("angle", 65.0))) * 0.5
				for e in enemies_in_circle(f, origin, rng2):
					if angle_ok(origin, dir, e.global_position, half):
						b.deal_damage(f, e, per_sec * interval, hit_opts(f, ab, {"tick": true, "aoe": true}))
						apply_statuses(f, e, ab, 0.5)
				for a in allies_in_circle(f, origin, rng2, false):
					if angle_ok(origin, dir, a.global_position, half):
						b.deal_damage(f, a, per_sec * interval, hit_opts(f, ab, {"tick": true, "aoe": true, "ff": true}))
		"drain":
			var tg: Variant = c.get("target")
			var victim: Fighter = null
			if tg != null and is_instance_valid(tg) and tg.alive and tg.team != f.team:
				victim = tg
			else:
				var best := 9999.0
				for e in enemies_in_circle(f, origin, float(ab.get("range", 10.0))):
					var d := flat(e.global_position - origin).length()
					if d < best:
						best = d
						victim = e
				c["target"] = victim
			var bn2: MeshInstance3D = _valid_node(c.get("beam_node")) as MeshInstance3D
			if victim == null or flat(victim.global_position - origin).length() > float(ab.get("range", 10.0)) + 3.0:
				c["channel_left"] = 0.0
				return
			if bn2 and is_instance_valid(bn2):
				var p0 := f.model.hand_world()
				var p1 := victim.global_position + Vector3(0, 1.0, 0)
				bn2.global_position = p0
				bn2.look_at(p1, Vector3.UP)
				bn2.scale = Vector3(1, 1, p0.distance_to(p1))
			if do_tick:
				var dmg := per_sec * interval
				b.deal_damage(f, victim, dmg, hit_opts(f, ab, {"tick": true}))
				b.heal(f, f, dmg * 0.6, {"ab": ab})
				b.vfx.burst(victim.global_position + Vector3(0, 1.0, 0), col, 2, 2.0, 0.3, 0.25, "soft_glow", 0.0, 180.0)

# ----------------------------------------------------------------------------------------------
# Invocations, temps
# ----------------------------------------------------------------------------------------------
static func _do_summon(f: Fighter, ab: Dictionary, aim: Vector3) -> void:
	var b := f.battle
	var n: int = int(ab.get("count", 2))
	var kind := String(ab.get("summon_kind", "spirit"))
	var role := String(ab.get("summon_role", "melee"))
	var col := color_of(ab)
	# limite de 4 invocations actives par invocateur
	var mine: Array[Fighter] = []
	for o in b.fighters:
		if o.is_summon and o.owner_f == f and o.alive:
			mine.append(o)
	while mine.size() + n > 5 and not mine.is_empty():
		mine[0].die(null, true)
		mine.remove_at(0)
	for i in n:
		var ang := TAU * float(i) / maxf(n, 1)
		var pos: Vector3 = b.arena.push_out(b.arena.clamp_point(aim + Vector3(cos(ang), 0, sin(ang)) * 1.4, 0.5), 0.5)
		var stats := {"hp": maxf(f.max_hp * 0.25, 140.0), "mana": 50, "stamina": 100, "power": f.power * 0.5, "defense": 6.0 + f.defense * 0.3, "mres": 6.0, "speed": 5.6}
		var tpl: Dictionary = Data.template("Merc_Necromancer").duplicate(true)
		var kit_ids: Array = ["slash_warrior_fighter"]
		tpl["weapon_main"] = "sword_short"
		tpl["weapon_off"] = ""
		tpl["scale"] = 0.8
		tpl["head"] = "none"
		tpl["torso"] = "none"
		tpl["shoulder"] = "none"
		tpl["back"] = "none"
		tpl["palette"] = ["#5a6a5a", "#2a2a30", col.to_html(false), "#d8d4c0"]
		tpl["species"] = "skeleton"
		tpl["display_name"] = "Serviteur"
		var visual := "humanoid"
		match kind:
			"turret":
				tpl["species"] = "human"
				kit_ids = ["magic_missile"] if role == "turret" else ["shoot"]
				stats["speed"] = 0.0
				stats["hp"] = maxf(f.max_hp * 0.18, 90.0)
				stats["power"] = f.power * 0.55
				visual = "turret"
			"beast":
				tpl["species"] = "beast"
				tpl["weapon_main"] = "claws"
				kit_ids = ["werewolf_claw"]
				stats["speed"] = 7.2
				tpl["scale"] = 0.75
			"illusion":
				tpl = f.tpl.duplicate(true)
				tpl["scale"] = float(f.tpl.get("scale", 1.0)) * 0.95
				kit_ids = [String(f.kit[0].get("id", "shoot"))]
				stats["hp"] = f.max_hp * 0.15
				stats["power"] = f.power * 0.35
				stats["speed"] = f.base_speed
			"spirit":
				tpl["palette"] = [col.to_html(false), "#1a1a28", "#ffffff", col.lightened(0.4).to_html(false)]
				kit_ids = ["shaman_bolt"] if role == "ranged" else ["slash_orc"]
		if role == "ranged" and kind != "turret":
			tpl["weapon_main"] = "bow_short"
			kit_ids = ["shoot"]
		elif role == "healer":
			tpl["weapon_main"] = "staff_wood"
			kit_ids = ["mend"]
		var spec := {"name": String(tpl.get("display_name", "Serviteur")), "tpl": tpl, "kit": kit_ids, "stats": stats, "is_summon": true, "level": f.level, "visual": visual, "summon_role": role}
		var s: Fighter = b.spawn_fighter(spec, f.team, pos)
		s.owner_f = f
		s.life_time = float(ab.get("dur", 14.0))
		b.vfx.burst(pos + Vector3(0, 0.3, 0), col, 14, 4.0, 0.6, 0.4, "soft_glow", -1.0, 160.0)
		b.vfx.ring(pos, col, 1.6, 0.4)
	Audio.play_at("summon", aim)

static func _do_time(f: Fighter, ab: Dictionary) -> void:
	var b := f.battle
	var kind := String(ab.get("time_kind", "slow"))
	var col := Color("7affd8")
	match kind:
		"rewind":
			if f.hist.size() >= 4:
				var h: Dictionary = f.hist[maxi(f.hist.size() - 12, 0)]
				f.global_position = h["pos"]
				f.hp = maxf(f.hp, minf(h["hp"], f.max_hp))
			b.vfx.ring(f.global_position, col, 3.0, 0.6, "glow_ring")
		"refresh":
			for i in f.cds.size():
				if i != 1 or true:
					f.cds[i] = 0.0
			f.mana = f.max_mana
			b.vfx.ring(f.global_position, col, 3.0, 0.6, "glow_ring")
		"stasis":
			for e in enemies_in_circle(f, f.global_position, 9.0):
				e.add_status("freeze", float(ab.get("dur", 3.0)) * 0.5, 1.0, f)
			b.vfx.ring(f.global_position, col, 9.0, 0.7)
		_:
			for e in enemies_in_circle(f, f.global_position, 10.0):
				e.add_status("slow", float(ab.get("dur", 3.0)) * 1.5, 1.5, f)
			f.add_status("haste", float(ab.get("dur", 3.0)) * 1.5, 1.0, f)
			b.vfx.ring(f.global_position, col, 10.0, 0.7)
	b.vfx.burst(f.global_position + Vector3(0, 1.0, 0), col, 20, 4.0, 1.0, 0.4, "rune_circle_0", 0.0, 180.0)
	Audio.play_at("spell_arcane", f.global_position)

# ----------------------------------------------------------------------------------------------
# Mouvement forcé (dash, charge, saut)
# ----------------------------------------------------------------------------------------------
static func update_forced(f: Fighter, dt: float) -> void:
	var fd := f.forced
	var ab: Dictionary = fd["ab"]
	var col := color_of(ab)
	fd["t"] += dt
	var b := f.battle
	match String(fd["type"]):
		"dash", "charge":
			var d: Vector3 = fd["dir"]
			var sp: float = float(fd["speed"])
			f.global_position += d * sp * dt
			f.facing_dir = d
			var gp := f.global_position
			if Engine.get_frames_drawn() % 2 == 0:
				b.vfx.burst(gp + Vector3(0, 0.6, 0), col.lerp(Color.WHITE, 0.4), 2, 0.5, 0.35, 0.5, "soft_glow", 0.0, 180.0)
			if String(fd["type"]) == "charge":
				for e in enemies_in_circle(f, gp, float(ab.get("radius", 1.6)) + 0.4):
					if not (e in fd["hit"]):
						fd["hit"].append(e)
						b.deal_damage(f, e, power_of(f, ab), hit_opts(f, ab, {"kb": 5.0, "kb_dir": d}))
						apply_statuses(f, e, ab)
						b.vfx.hit_fx(e.global_position, String(ab.get("element", "physical")), true, 1.2)
						b.vfx.shake(0.25)
			if fd["t"] >= fd["dur"]:
				f.forced = {}
				f.vel = d * sp * 0.15
		"leap":
			var u: float = clampf(fd["t"] / fd["dur"], 0.0, 1.0)
			var from: Vector3 = fd["from"]
			var to: Vector3 = fd["to"]
			var p := from.lerp(to, u)
			f.global_position = Vector3(p.x, 0.0, p.z)
			f.model.position.y = sin(u * PI) * float(fd["height"])
			f.facing_dir = dir_to(from, to) if dir_to(from, to) != Vector3.ZERO else f.facing_dir
			if u >= 1.0:
				f.model.position.y = 0.0
				f.forced = {}
				var r: float = float(ab.get("radius", 3.0))
				for e in enemies_in_circle(f, to, r):
					b.deal_damage(f, e, power_of(f, ab), hit_opts(f, ab, {"kb": 4.0, "kb_dir": dir_to(to, e.global_position)}))
					apply_statuses(f, e, ab)
				b.vfx.element_burst(to, String(ab.get("element", "physical")), r)
				b.vfx.shake(0.4)
				Audio.play_at("leap_land", to)
		"pulled":
			var tg: Vector3 = fd["to"]
			var dd := flat(tg - f.global_position)
			var step: float = float(fd["speed"]) * dt
			if dd.length() <= step + 0.1 or fd["t"] >= fd["dur"]:
				f.forced = {}
			else:
				f.global_position += dd.normalized() * step
		"knock":
			var kd: Vector3 = fd["dir"]
			var ks: float = float(fd["speed"]) * (1.0 - fd["t"] / fd["dur"])
			f.global_position += kd * ks * dt
			if fd["t"] >= fd["dur"]:
				f.forced = {}
