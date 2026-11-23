extends Node
## Audio : SFX poolés avec variantes (_1,_2,…), musiques avec fondu enchaîné. Tolère l'absence de fichiers.

const SFX_DIR := "res://assets/audio/sfx/"
const MUSIC_DIR := "res://assets/audio/music/"

var _sfx_cache: Dictionary = {}     # base -> Array[AudioStream]
var _players: Array[AudioStreamPlayer] = []
var _players3d: Array[AudioStreamPlayer3D] = []
var _music_a: AudioStreamPlayer
var _music_b: AudioStreamPlayer
var _music_active: AudioStreamPlayer
var _current_music: String = ""
var _loops: Dictionary = {}          # nom -> AudioStreamPlayer
var _missing: Dictionary = {}
var master_mult: float = 1.0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in 24:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_players.append(p)
	for i in 24:
		var p3 := AudioStreamPlayer3D.new()
		p3.max_distance = 60.0
		p3.unit_size = 14.0
		add_child(p3)
		_players3d.append(p3)
	_music_a = AudioStreamPlayer.new()
	_music_b = AudioStreamPlayer.new()
	add_child(_music_a)
	add_child(_music_b)
	_music_active = _music_a
	apply_volumes()

func apply_volumes() -> void:
	var m: float = Settings.gf("master_volume")
	master_mult = m
	AudioServer.set_bus_volume_db(0, linear_to_db(maxf(m, 0.0001)))
	if _music_active and _music_active.playing:
		_music_active.volume_db = linear_to_db(maxf(_music_target_linear(), 0.0001))

func _music_target_linear() -> float:
	return Settings.gf("combat_music_volume") if _current_music.begins_with("music_battle") else Settings.gf("music_volume")

func _load_variants(base: String) -> Array:
	if _sfx_cache.has(base):
		return _sfx_cache[base]
	var arr: Array = []
	var single := SFX_DIR + base + ".wav"
	if ResourceLoader.exists(single):
		arr.append(load(single))
	for i in range(1, 9):
		var p := SFX_DIR + base + "_%d.wav" % i
		if ResourceLoader.exists(p):
			arr.append(load(p))
	if arr.is_empty():
		for ext in ["ogg", "mp3"]:
			var p2: String = SFX_DIR + base + "." + str(ext)
			if ResourceLoader.exists(p2):
				arr.append(load(p2))
	_sfx_cache[base] = arr
	return arr

func has_sfx(base: String) -> bool:
	return not _load_variants(base).is_empty()

func play(base: String, vol_db: float = 0.0, pitch: float = 1.0, ui: bool = false) -> void:
	var arr := _load_variants(base)
	if arr.is_empty():
		return
	var vol_lin: float = Settings.gf("ui_volume") if ui or base.begins_with("ui_") else Settings.gf("combat_volume")
	for p in _players:
		if not p.playing:
			p.stream = arr[randi() % arr.size()]
			p.volume_db = vol_db + linear_to_db(maxf(vol_lin, 0.0001))
			p.pitch_scale = pitch * randf_range(0.96, 1.04)
			p.play()
			return

func play_at(base: String, pos: Vector3, vol_db: float = 0.0, pitch: float = 1.0) -> void:
	var arr := _load_variants(base)
	if arr.is_empty():
		return
	for p in _players3d:
		if not p.playing:
			p.stream = arr[randi() % arr.size()]
			p.global_position = pos
			p.volume_db = vol_db + linear_to_db(maxf(Settings.gf("combat_volume"), 0.0001))
			p.pitch_scale = pitch * randf_range(0.94, 1.06)
			p.play()
			return

func ui(base: String) -> void:
	play(base, 0.0, 1.0, true)

func loop_start(base: String, vol_db: float = -6.0) -> void:
	if _loops.has(base):
		return
	var arr := _load_variants(base)
	if arr.is_empty():
		return
	var p := AudioStreamPlayer.new()
	p.stream = arr[0]
	p.volume_db = vol_db
	add_child(p)
	p.finished.connect(func(): if is_instance_valid(p): p.play())
	p.play()
	_loops[base] = p

func loop_stop(base: String) -> void:
	if _loops.has(base):
		var p: AudioStreamPlayer = _loops[base]
		if is_instance_valid(p):
			p.queue_free()
		_loops.erase(base)

func music(name: String, fade: float = 1.2) -> void:
	if name == _current_music:
		return
	var path := MUSIC_DIR + name + ".ogg"
	if not ResourceLoader.exists(path):
		if not _missing.has(name):
			_missing[name] = true
		_stop_music(fade)
		_current_music = name
		return
	_current_music = name
	var stream: AudioStream = load(path)
	if stream is AudioStreamOggVorbis:
		(stream as AudioStreamOggVorbis).loop = true
	var nxt: AudioStreamPlayer = _music_b if _music_active == _music_a else _music_a
	var prev: AudioStreamPlayer = _music_active
	nxt.stream = stream
	nxt.volume_db = -60.0
	nxt.play()
	var target_db: float = linear_to_db(maxf(_music_target_linear(), 0.0001))
	var tw := create_tween().set_parallel(true)
	tw.tween_property(nxt, "volume_db", target_db, fade)
	if prev.playing:
		tw.tween_property(prev, "volume_db", -60.0, fade)
		tw.chain().tween_callback(prev.stop)
	_music_active = nxt

func _stop_music(fade: float) -> void:
	if _music_active and _music_active.playing:
		var p := _music_active
		var tw := create_tween()
		tw.tween_property(p, "volume_db", -60.0, fade)
		tw.tween_callback(p.stop)

func stinger(name: String, vol_db: float = 0.0) -> void:
	play(name, vol_db, 1.0, true)
