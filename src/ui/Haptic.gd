class_name Haptic
extends RefCounted
## Retour haptique centralisé (vibration légère sur mobile).

static func buzz(ms: int, amplitude: float = 0.5) -> void:
	if Settings.gb("haptics") and OS.has_feature("mobile"):
		Input.vibrate_handheld(ms, amplitude)

static func tap(strength: float = 0.3) -> void:
	buzz(int(8.0 + strength * 30.0), clampf(strength, 0.1, 1.0))

static func hit() -> void:
	buzz(24, 0.7)

static func big() -> void:
	buzz(70, 1.0)
