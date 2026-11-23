#!/usr/bin/env python3
"""Génère data/*.json à partir des specs (dump) : 619 compétences classées par archétype,
57 classes, 46 champions, 23 boss/spéciaux, reliques, équipes, quirks.
Usage : tools/.venv/bin/python tools/build_catalog.py"""
import json, re, hashlib, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMP = json.load(open(os.path.join(ROOT, "tools", "eslabong_dump.json")))
OUT = os.path.join(ROOT, "data")
os.makedirs(OUT, exist_ok=True)


def h(s, mod=1000):
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % mod


def pretty(i):
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", i)
    s = s.replace("_", " ").strip()
    return " ".join(w.capitalize() if not w.isupper() else w for w in s.split())


# ----------------------------------------------------------------------------------------------
# 1. Classification des compétences
# ----------------------------------------------------------------------------------------------
ELEMENT_RULES = [
    ("fire", r"fire|flame|ember|burn|blaze|infern|magma|volcan|meteor|cinder|ashen|pyre|bloodfire|combustion|cremation|furnace|phoenix|brand|immolat|baptizedbyfire|darkfyre|cryoflame|hellwake|firebringer|torch|solar|sunburst|sunlit"),
    ("ice", r"\bice|_ice|ice_|frost|freez|blizzard|glacial|arctic|winter|cryo|frozen|icewind|apocalypse_ice|stasis"),
    ("lightning", r"lightning|thunder|storm|volt|electr|static|shock|spark|capacitor|plasma|fulmin|taser|jumper|discharge|induction|mag_lock|magnetic|rail|coil|ball_lightning|arc_|charge_up|defib|heartbeat|flatline|adrenaline|crash_cart|jumpstart"),
    ("void", r"void|rift|singularity|abyss|hollow|breach|fold|mirror|twin|phase|anchor_blade|drifting"),
    ("shadow", r"shadow|dark|dread|curse|hex\b|haunt|necro|spectral|soul|doom|umbral|black_|night|penumbra|mind|profane|corrupt|wither|specter|skeleton|choir|litany|whisper|scripture|psalm|accursed|oxifall|terrify|fear_me|ghost|vanish|lights_out|pocket_sand|nasty|late_fee|time_debt|deadline"),
    ("holy", r"holy|divine|blessed|sacred|heaven|light|righteous|templar|smite|prayer|sanctuary|resurrection|lay_on|last_rites|guiding|mender?|mend\b|god_|hammer_of|zealous|consecrated|purifying|silver|judg|titan_slam|heavenly|desperate_prayer|iron_gate|matriarch|vanguard|aria"),
    ("blood", r"blood|vamp|crimson|scarlet|vein|bat\b|bat_|bleed|reap|wound|rend|sever|throat|open_wound|bloodwing|wingclip|red_hour|crook|parting|reopening|blindside|quarry|feint|hamstring|meat_hook|claw_frenzy|bite|reaver_axe_bleed"),
    ("wind", r"wind|tornado|gale|huracan|twister|crosswind|sonic|bellow|accelerate|sprint|boltspeed|terminal_velocity|convergence|flying|flight|hop|jump|leap|step"),
    ("earth", r"earth|rock|stone|boulder|tectonic|avalanche|ridge|quake|spike|totem|bastion|grudge|pick|mace|crack_the_earth|shard|ward|petrif|first_stone|mannonball"),
    ("arcane", r"arcane|magic|mana|time|chrono|clock|hour|rewind|epoch|star|astral|celestial|cosmic|constellation|orb|invoke|element|refresher|bullet_time|stolen|borrowed|split_second|afterimage|polarity|gravity|manta|blink|the_one|polymorph|tri_|missile|needle|turret"),
    ("nature", r"poison|venom|nature|roots|entangl|rejuven|boar|beast|wolf|wild|hunt|trap|tripwire|caltrop|net_|pounce|trample|frenzy|howl|moonbreaker|fang|heel|scruff|pack|werewolf"),
]
ELEMENT_ORDER = ELEMENT_RULES


def element_of(i, folder):
    s = i.lower()
    for el, rx in ELEMENT_RULES:
        if re.search(rx, s):
            return el
    d = {"Archmage": "arcane", "Celestial": "holy", "Dragon": "arcane", "Elementalist": "fire", "Hellforged": "fire",
         "Necromancer": "shadow", "ShadowPriest": "shadow", "Templar": "holy", "Vampira": "blood", "Voidfist": "void",
         "Warlock": "shadow", "Riftwalker": "void", "Rockguard": "earth", "BloodHarvester": "blood", "Heal": "holy",
         "Monk": "wind", "Bladedancer": "physical", "GoblinAmbusher": "nature"}
    return d.get(folder, "physical")


# (regex, archetype, overrides)  -- ordre = priorité
ARCH_RULES = [
    (r"resurrect|profane_resurrection|last_rites$", "resurrect", {}),
    (r"^swap$|divine_transposition|void_swap|polarity_exchange", "swap", {}),
    (r"rewind|refresher|freeze_time|bullet_time|time_debt|stolen_moment|borrowed_time|hourglass_reversal|split_second|stasis_prison|chrono_deadeye|deadline|final_hour|clockbreaker|clockface", "time", {}),
    (r"ice_block|iron_gate_mandate|dancers_reversal|parry_stance|block_ability|swordmaster_parry|sentinel_parry|parry_counter|rockguard_shield_wall|halberdier_brace", "guard", {}),
    (r"chain_heal|chain_bond|fire_bond|best_friend|matriarch_bond", "heal_chain", {}),
    (r"mass_mend|wave_of_rejuvenation|sanctuary|immolation_blessing|baptizedbyfire|rise_like_the_phoenix|choir|night_communion|ashen_renewal|shockmender_heartbeat|shockmender_second|shockmender_crash|shockmender_clear|arcane_prayer|divine_call|healing_sacrifice", "heal_aoe", {}),
    (r"rejuvenation|trail_mend|regen|vampiric_fortitude|heart_of_the_furnace|boar_mend", "heal_hot", {}),
    (r"heal|mend|lay_on_hands|holy_light|guiding_light|sacred|divine_light|jumpstart|shadow_mend|magic_heal|adrenaline", "heal", {}),
    (r"summon|raise_specter|call_wild_boar|call_of_the_pack|manta_illusions|twin_reflection|arcane_turret|beam_turret|reaper_turret|pointdefense|reaper_point_defense|astral_spray_turret|storm_totem|first_stone_totem|boom_spankcrackle_storm_totem|ember_sparks_blessing", "summon", {}),
    (r"trap|caltrops|tripwire|minefield|lay_trap|bleeding_trap|salt_circle|nasty_surprise|banana_peel|induction_cage|railmark|hunter_mark", "trap", {}),
    (r"meat_hook|whip_pull|whip_lasso|barbed_chain|silver_chain|magnetic_tether|gale_grip|chain_hook|anchor_blade|spearfisher|restraining_stake|net_throw|grasping|abyssal_grasp|mag_lock", "hook", {}),
    (r"lifedrain|life_drain|soul_drain|vampiric_psalm|blood_pact|draining", "drain", {}),
    (r"flamethrower|breath|comet_breath|oxi_breath|dread_howl|fear_me|werewolf_roar|bellow|cone", "cone", {}),
    (r"beam|tri_focus|reaper_beam|overrail|rail_splitter|rail_backblast|mortal_axe|spray|sprayandpray|arc_relay|electrocute", "beam", {}),
    (r"chain_lightning|storm_relay|ricochet|ball_lightning|resonant_lightning|lightning_orb|chain_sweep", "chain", {}),
    (r"execute|throat_cut|mortal_strike|shatter_execute|final_cremation|the_red_hour|deadeye|guillotine|heavens_verdict|coup|the_one", "execute", {}),
    (r"whirlwind|frost_whirlwind|steel_wind|spin|carousel|circle_of_steel|pirouette|blade_defense|hammer_holy_spin|cannonball_roll|iron_carousel|rope_bounce", "melee_aoe", {}),
    (r"nova|bastion|shockwave|discharge|eruption|megameteor|earth_nova|voltaic|catalyst|pulse|void_wave|void_collapse|hollow_explosion|crack_the_earth|body_slam|ground_pound|tectonic|storm_slam|hammerfall|apex|titan_slam|powerbomb|temblor|void_singularity|singularity|ice_apocalypse|arctic_armageddon|thunder_wrath|holy_wrath|combustion|total_fulmination|static_overload|capacitor_burst|celestial_expansion", "nova", {}),
    (r"leap|jump|pounce|hop\b|crossbody|giant_swing|primal_leap|bettoleap|ugshatup_leap|heavenly|falling|hammer_throw|flying|flyingkick|terminal_velocity|astral_flight|bat_flight|acrobatic", "leap", {}),
    (r"charge|rush|ram\b|battering|ram_|shoulder|gore|rushing|bull_|horn|dragon_palm|advance|kick_dash|cannonball_void|cannonball|pounce|stormfang|mannonball|frozen_wake_dash", "charge", {}),
    (r"blink|teleport|vanish|shadow_dash|shadowstep|fold_step|phase_edge|impossible_step|holy_step|thunder_step|return$|body_flicker|blink_strike|passing_lunge|afterimage|vanishing_step|void_dash|chrono_dash|cosmic_dash|spectral_dash", "blink", {}),
    (r"dash|_roll|roll$|step|hop|sprint|advance|icewind_jump|tactical_roll|lunging|duelist_step|wind_step|reaver_hop|light_dash|medium_dash|heavy_dash", "dash", {}),
    (r"stealth|ghost_mode|smoke_bomb|invisib|crimson_veil|penumbra|lights_out", "stealth", {}),
    (r"taunt|challenge|duelist_challenge|rockguard_taunt|battle_shout|super_battle_shout|war_cry", "taunt", {}),
    (r"shield|barrier|ward|armor|aegis|protection|bulwark|iron_skin|stone_|guard|wall|fortitude|blessed|spirit_shield|ice_armor|frost_armor|cinder_armor|capacitor_ward|volt_shield|wolf_hide|iron_resolve|horned_bulwark|thorns", "shield", {}),
    (r"frenzy|rage|bloodlust|blood_frenzy|too_angry|open_the_wound|reckless|hulk_up|ascension|boltspeed|accelerate|inner_|meditation|kinesis|sprint|battle|retaliation|vanguard|hot_tag|firebringer|furnace|moonbreaker|wolf|roar|stormhorn|crown|stormcrown|storm_crown|demon", "buff", {}),
    (r"curse|hex|doom|corruption|withering|haunt|terrify|polymorph|petrification|freeze$|stasis|entangling|wounding|poison|venom|mark|brand|blood_scent|open_vein|open_wounds|hamstring|sever|rend|wingclip|reopening|pocket_sand|sand|late_fee|ensnar|sentinel_hobbling|sentinel_guard_breaker|leeching|dread|mind_eclipse|word_of_dread|black_mass|umbral", "curse", {}),
    (r"volley|multishot|barrage|fan_shot|fan_of_blades|rain_of|shotgun|salvo|pewpewpew|golden_multishot|sunburst|arrow_barrage|double_grenade|needle|shards|ice_shards|spear_flurry|void_flurry|blows_of_furry|claw_frenzy|blade_pirouette|multiball|twister_waves|ice_shard_nova", "volley", {}),
    (r"meteor|rain|storm|blizzard|firestorm|thunder_storm|tornado|huracan|eruption|volcanic|gravity_well|ice_pillar|earth_spike|blood_storm|reap_the_void|spear_of_nassar|thunder_boulder|hammer_of_heaven|doomfall|falling_star|fire_comet|comet|singularity_torpedo|ice_bomb|unstable_ice_bomb|grenade|explosive|holy_fire|infernus|darkfyre|cryoflame|abyssal_slam|black_thread|stormfang", "ground_aoe", {}),
    (r"slash|cleave|strike|swing|smash|sweep|cut|chop|punch|palm|claw|bash|slam|stonk|pick_swing|hook$|club|frostbreaker|maul|glacial|headbutt|suplex|grab|chair|kick|bite|rend_orc|viper|whip_strike|tigercut|crossclaw|heel_bite|apex_cleave|toll|sweeping|omnislash|threefold|feinting|passing|shiv|dagger|stab|reaper", "melee_arc", {}),
    (r"thrust|spear|skewer|impale|lance|halberd|pierce|lunge|javalin|javelin|lunging", "melee_thrust", {}),
]

FOLDER_DEFAULT = {
    "Archmage": "projectile", "Basic": None, "Bladedancer": "melee_arc", "BloodHarvester": "melee_arc", "Boss": "melee_aoe",
    "Buffs": "buff", "Celestial": "projectile", "Champions": "projectile", "Class": "melee_arc", "Defense": "shield",
    "Dragon": "projectile", "Elementalist": "projectile", "FutureClasses": "melee_arc", "GoblinAmbusher": "melee_arc",
    "Heal": "heal", "Hellforged": "melee_arc", "Melee": "melee_arc", "Monk": "melee_arc", "Necromancer": "summon",
    "Ranged": "projectile", "Riftwalker": "blink", "Rockguard": "melee_arc", "Rolls": "dash", "ShadowPriest": "curse",
    "Spell": "projectile", "Templar": "melee_arc", "Utility": "stealth", "Vampira": "melee_arc", "Voidfist": "melee_arc",
    "Warlock": "curse",
}

# Archétypes de base : paramètres par défaut
ARCH_DEFAULTS = {
    #  range  radius  cd   mana sta  dmg   cast  extra
    "melee_arc":   dict(range=2.8, radius=2.8, angle=120, cd=5.0,  mana=0,  sta=10, dmg=1.5, cast=0.25),
    "melee_thrust": dict(range=4.0, radius=0.9, cd=5.0, mana=0, sta=10, dmg=1.55, cast=0.25),
    "melee_aoe":   dict(range=0, radius=3.6, cd=9.0, mana=0, sta=22, dmg=1.7, cast=0.3),
    "nova":        dict(range=0, radius=5.0, cd=12.0, mana=30, sta=0, dmg=2.4, cast=0.45),
    "projectile":  dict(range=16, radius=0.45, speed=24, cd=5.0, mana=12, sta=0, dmg=1.9, cast=0.3),
    "volley":      dict(range=14, radius=0.4, speed=26, cd=9.0, mana=20, sta=0, dmg=0.85, count=5, spread=36, cast=0.35),
    "ground_aoe":  dict(range=14, radius=3.6, cd=12.0, mana=32, sta=0, dmg=3.0, delay=0.8, cast=0.45),
    "beam":        dict(range=12, radius=0.9, cd=10.0, mana=28, sta=0, dmg=3.6, dur=1.3, cast=0.3),
    "cone":        dict(range=7.5, radius=7.5, angle=65, cd=10.0, mana=26, sta=0, dmg=3.2, dur=1.4, cast=0.3),
    "chain":       dict(range=15, radius=7, cd=9.0, mana=24, sta=0, dmg=2.2, bounces=4, cast=0.35),
    "leap":        dict(range=10, radius=3.2, cd=11.0, mana=0, sta=26, dmg=2.4, cast=0.2),
    "charge":      dict(range=9, radius=1.6, cd=10.0, mana=0, sta=28, dmg=2.0, cast=0.15),
    "dash":        dict(range=6.0, cd=4.5, mana=0, sta=26, dmg=0.0, cast=0.0),
    "blink":       dict(range=8.5, cd=8.0, mana=16, sta=0, dmg=0.0, cast=0.1),
    "summon":      dict(range=7, count=2, cd=20.0, mana=42, sta=0, dur=14, cast=0.6),
    "trap":        dict(range=9, radius=2.4, cd=12.0, mana=16, sta=0, dmg=2.2, dur=20, cast=0.3),
    "hook":        dict(range=15, radius=0.7, speed=36, cd=11.0, mana=14, sta=10, dmg=1.0, cast=0.25),
    "execute":     dict(range=3.2, radius=2.6, angle=100, cd=12.0, mana=0, sta=20, dmg=3.0, cast=0.35),
    "drain":       dict(range=10, cd=12.0, mana=30, sta=0, dmg=0.9, dur=2.6, cast=0.3),
    "curse":       dict(range=15, radius=0.5, speed=22, cd=9.0, mana=20, sta=0, dmg=0.9, dur=6, cast=0.3),
    "heal":        dict(range=15, cd=7.0, mana=26, sta=0, heal=2.6, cast=0.4),
    "heal_aoe":    dict(range=0, radius=6.0, cd=14.0, mana=42, sta=0, heal=1.8, cast=0.5),
    "heal_hot":    dict(range=15, cd=11.0, mana=30, sta=0, heal=3.0, dur=6, cast=0.3),
    "heal_chain":  dict(range=15, radius=7, cd=10.0, mana=34, sta=0, heal=1.8, bounces=3, cast=0.35),
    "resurrect":   dict(range=15, cd=45.0, mana=80, sta=0, heal=0.5, cast=1.2),
    "swap":        dict(range=18, cd=14.0, mana=20, sta=0, cast=0.2),
    "shield":      dict(range=0, cd=14.0, mana=22, sta=10, dur=5.0, absorb=0.22, cast=0.2),
    "guard":       dict(range=0, cd=16.0, mana=0, sta=20, dur=2.2, cast=0.1),
    "buff":        dict(range=0, cd=18.0, mana=22, sta=0, dur=7.0, cast=0.2),
    "taunt":       dict(range=0, radius=9.0, cd=16.0, mana=0, sta=18, dur=3.5, cast=0.2),
    "stealth":     dict(range=0, cd=16.0, mana=20, sta=0, dur=4.0, cast=0.1),
    "time":        dict(range=0, radius=0, cd=24.0, mana=50, sta=0, dur=3.0, cast=0.2),
}

ARCH_ICON_GLYPH = {  # indication pour l'agent 2D (glyphe principal)
    "melee_arc": "slash", "melee_thrust": "thrust", "melee_aoe": "whirl", "nova": "burst", "projectile": "bolt",
    "volley": "volley", "ground_aoe": "meteor", "beam": "beam", "cone": "cone", "chain": "chain", "leap": "leap",
    "charge": "charge", "dash": "dash", "blink": "blink", "summon": "summon", "trap": "trap", "hook": "hook",
    "execute": "skull_blade", "drain": "drain", "curse": "curse", "heal": "cross", "heal_aoe": "cross_aura",
    "heal_hot": "cross_pulse", "heal_chain": "cross_chain", "resurrect": "ankh", "swap": "swap", "shield": "shield",
    "guard": "parry", "buff": "arrow_up", "taunt": "horn", "stealth": "eye_slash", "time": "hourglass"}


def status_for(i, element, arch):
    s = i.lower()
    st = []
    if re.search(r"freez|frost|ice|glacial|blizzard|cryo|frozen|arctic|winter|chill", s): st.append("slow")
    if re.search(r"freeze$|stasis|petrif|ice_block|frozen|ice_pillar", s): st.append("freeze")
    if re.search(r"burn|fire|flame|ember|inferno|infernus|magma|volcan|meteor|cinder|combustion|immolat|firestorm|darkfyre|cryoflame|hellwake", s): st.append("burn")
    if re.search(r"poison|venom|toxic|corrupt|blight", s): st.append("poison")
    if re.search(r"bleed|wound|open_vein|rend|sever|hamstring|reopening|throat|wingclip|barbed|nail|bite|fang|impale|skewer|caltrop|shiv|knife|blade|dagger|claw", s): st.append("bleed")
    if re.search(r"stun|bash|slam|headbutt|shockwave|electrocute|shock|taser|stonk|titan|petrif|polymorph|suplex|powerbomb|crossbody|hammerfall|thunder_boulder|ram\b|battering|gore|horn|storm_slam|ground|slamm", s): st.append("stun")
    if re.search(r"fear|terrify|dread|howl|roar|bellow|boo\b|scare|panic", s): st.append("fear")
    if re.search(r"root|entangl|net_|restrain|lasso|stake|chain|cage|web|snare|tether|grasp|anchor|tripwire|grip", s): st.append("root")
    if re.search(r"slow|hobbl|wingclip|caltrop|sand|trail|mud|bog|gravity|tornado|whirl", s): st.append("slow")
    if re.search(r"silence|hex|mind_eclipse|polymorph|dread|word_of", s): st.append("silence")
    if re.search(r"mark|brand|hunter_mark|railmark|expos|blood_scent|nail|witch_hunter_the_nail", s): st.append("mark")
    if re.search(r"weaken|wither|curse|doom|late_fee|time_debt|corruption", s): st.append("weaken")
    seen = []
    for x in st:
        if x not in seen: seen.append(x)
    # une compétence ne reçoit que 2 statuts max
    if arch in ("melee_arc", "melee_thrust", "projectile") and len(seen) > 1:
        seen = seen[:1]
    return seen[:2]


BUFF_KINDS = [
    (r"rage|frenzy|bloodlust|blood_frenzy|angry|wound|hulk|reckless|roar|demon|crown|storm", "empower"),
    (r"sprint|accelerate|boltspeed|speed|haste|wind|kinesis|flight|step", "haste"),
    (r"thorn|retaliation|vanguard|counter|iron_resolve|resolve", "thorns"),
    (r"vamp|blood|drain|lifesteal|wolf|moonbreaker", "lifesteal"),
    (r"shout|war_cry|battle", "empower"),
    (r"firebringer|furnace|ember", "empower"),
    (r"fort|iron_skin|armor|hide|stone", "armor_up"),
]


def buff_kind(i):
    s = i.lower()
    for rx, k in BUFF_KINDS:
        if re.search(rx, s):
            return k
    return "empower"


def classify(i, folder, idx_in_folder, total_in_folder):
    s = i.lower()
    arch = None
    for rx, a, ov in ARCH_RULES:
        if re.search(rx, s):
            arch = a
            break
    if folder == "Rolls":
        arch = "dash" if not re.search(r"blink|vanish|shadow|chrono|cosmic|spectral|epoch", s) else "blink"
        if re.search(r"hop|jump", s): arch = "leap_dash"
    if folder == "Heal" and arch not in ("heal", "heal_aoe", "heal_hot", "heal_chain", "resurrect", "swap"):
        arch = "heal"
    if folder == "Defense" and arch not in ("shield", "guard"):
        arch = "shield"
    if folder == "Buffs":
        arch = "buff" if arch not in ("shield", "taunt") else arch
    if folder == "Basic":
        # attaques de base : mêlée => arc/thrust ; sinon projectile
        if re.search(r"thrust|spear|halberdier_thrust", s): arch = "melee_thrust"
        elif re.search(r"slash|smash|cleave|chop|claws|strike_|whip|shiv|club|sweep|reap$|pendulum|paddle", s) and not re.search(r"bolt|shoot|beam|spark|fireball|lightning", s): arch = "melee_arc"
        elif re.search(r"beam", s): arch = "beam"
        else: arch = "projectile"
        if "reaver_throwing_axe" in s or "witch_hunter_crossbow" in s: arch = "projectile"
        if "lightning_strike" in s or "thunder_attack" in s: arch = "projectile"
    if arch is None:
        arch = FOLDER_DEFAULT.get(folder) or "melee_arc"
    if arch == "leap_dash":
        arch = "leap"
    element = element_of(i, folder)
    base = dict(ARCH_DEFAULTS[arch])
    # variation déterministe selon l'id
    rnd = random.Random(h(i, 10**6))
    tier = 1 + (h(i + "tier", 100) / 100.0) * 0.5  # 1.0 .. 1.5
    is_basic = folder == "Basic"
    d = {
        "id": i, "name": pretty(i), "folder": folder, "arch": arch, "element": element,
        "icon_glyph": ARCH_ICON_GLYPH.get(arch, "bolt"), "basic": is_basic,
    }
    for k, v in base.items():
        d[k] = v
    if is_basic:
        # attaque de base : cooldown court, pas de coût (mana/sta mineur)
        d["cd"] = round(0.55 + rnd.random() * 0.45, 2) if arch.startswith("melee") else round(0.7 + rnd.random() * 0.5, 2)
        d["dmg"] = 0.55 + rnd.random() * 0.2
        d["mana"] = 0
        d["sta"] = 0
        d["cast"] = 0.12
        if arch == "beam":
            d["dur"] = 0.5; d["cd"] = 1.4; d["dmg"] = 1.0
    else:
        v = 0.85 + rnd.random() * 0.3
        d["cd"] = round(d["cd"] * v * (0.9 + (tier - 1.0) * 0.4), 1)
        for k in ("dmg", "heal", "absorb"):
            if k in d:
                d[k] = round(d[k] * (0.85 + (tier - 1.0) * 0.5 + rnd.random() * 0.15), 2)
        for k in ("range", "radius"):
            if k in d and d[k]:
                d[k] = round(d[k] * (0.92 + rnd.random() * 0.2), 1)
        if "mana" in d and d["mana"]:
            d["mana"] = int(d["mana"] * (0.9 + rnd.random() * 0.3))
    # statuts
    sts = status_for(i, element, arch)
    if arch in ("curse", "debuff_aoe", "trap", "hook", "cone") and not sts:
        sts = [{"ice": "slow", "fire": "burn", "shadow": "weaken", "lightning": "stun", "blood": "bleed", "nature": "poison",
                "void": "root", "holy": "silence", "earth": "slow", "wind": "slow", "arcane": "mark"}.get(element, "slow")]
    d["status"] = sts
    if arch == "buff":
        d["buff"] = buff_kind(i)
    if arch == "time":
        d["time_kind"] = ("rewind" if re.search(r"rewind|reversal|stolen|borrowed", s) else
                          "refresh" if re.search(r"refresher|hour|final", s) else
                          "stasis" if re.search(r"stasis|freeze_time|chrono_deadeye|split", s) else "slow")
    if arch == "guard":
        d["guard_kind"] = "invuln" if re.search(r"ice_block|mandate|reversal", s) else "parry"
    if arch == "summon":
        d["summon_kind"] = ("turret" if re.search(r"turret|totem|pointdefense", s) else
                            "skeleton" if re.search(r"skeleton|archer|knight|vanguard|priest|mage|specter|raise", s) else
                            "beast" if re.search(r"boar|wolf|pack|wild", s) else
                            "illusion" if re.search(r"manta|twin|reflection|illusion", s) else "spirit")
        if re.search(r"skeleton_mage|archer|mage", s): d["summon_role"] = "ranged"
        elif re.search(r"priest", s): d["summon_role"] = "healer"
        elif re.search(r"turret|totem", s): d["summon_role"] = "turret"
        else: d["summon_role"] = "melee"
    if re.search(r"pierce|impaler|rail|spear|javalin|lance|phantom|beam|multishot|arrow_barrage", s) and arch == "projectile":
        d["pierce"] = 3
    if re.search(r"grenade|fireball|explosive|bomb|meteor|nail|boulder|torpedo|mortar|missile|comet|orb", s) and arch in ("projectile", "volley"):
        d["explode"] = round(2.4 + rnd.random() * 1.2, 1)
    if re.search(r"homing|guided|seek|missile|boomerang|spinning_blade|ricochet|multiball", s) and arch in ("projectile", "volley"):
        d["homing"] = 0.6
    if re.search(r"ricochet|bounc", s):
        d["bounces"] = 3
    if re.search(r"boomerang|spinning_blade|shuriken|whip_lasso", s):
        d["returning"] = True
    if arch == "volley":
        d["count"] = 3 + h(i + "c", 5)
    if re.search(r"turret|totem", s) and arch == "summon":
        d["dur"] = 12
    if re.search(r"ultimate|apocalypse|armageddon|megameteor|singularity|the_red_hour|final|the_one|total_|heavens_verdict|storm_crown|tornado", s):
        d["ultimate"] = True
        d["cd"] = round(max(d["cd"], 30.0), 1)
        if "dmg" in d: d["dmg"] = round(d["dmg"] * 1.5, 2)
        if "mana" in d: d["mana"] = max(d.get("mana", 0), 55)
    # channel
    if arch in ("beam", "cone", "drain") or re.search(r"channel|flamethrower|beam|breath", s):
        d["channel"] = True
    d["desc_key"] = arch
    return d


abilities = []
for folder, ids in DUMP["abilities_by_folder"].items():
    for idx, i in enumerate(ids):
        abilities.append(classify(i, folder, idx, len(ids)))
assert len(abilities) == 619, len(abilities)
AB = {a["id"]: a for a in abilities}

# ----------------------------------------------------------------------------------------------
# 2. Classes (57)
# ----------------------------------------------------------------------------------------------
ROLE_BASE = {
    #            hp   mana sta  pow def mres spd
    "tank":     (1000, 80, 130, 24, 38, 22, 5.5),
    "bruiser":  (820, 80, 120, 34, 26, 14, 6.1),
    "assassin": (560, 90, 140, 40, 14, 10, 7.2),
    "ranged":   (520, 110, 100, 38, 10, 10, 6.0),
    "mage":     (470, 180, 90, 44, 8, 22, 5.8),
    "healer":   (500, 200, 90, 30, 8, 26, 5.8),
    "support":  (620, 150, 100, 28, 14, 18, 6.0),
    "summoner": (480, 190, 90, 36, 8, 20, 5.7),
}

# (id, nom, espèce, rôle, élément, [armes main, off], tête, torse, épaules, dos, palette(primary, secondary, accent, skin), échelle, kit[basic, dash, s1..s4], note)
C = []


def cls(cid, name, species, role, element, wpn, head, torso, shoulder, back, pal, scale, kit, mods=None, note=""):
    C.append(dict(id=cid, name=name, species=species, role=role, element=element, weapon_main=wpn[0],
                  weapon_off=wpn[1] if len(wpn) > 1 else "", head=head, torso=torso, shoulder=shoulder, back=back,
                  palette=pal, scale=scale, kit=kit, mods=mods or {}, note=note))


# palette hex: primary, secondary, accent, skin
cls("Merc_Archer_Bowman", "Bowman", "human", "ranged", "physical", ["bow_long"], "hat_feathered", "vest_ranger", "leather", "quiver",
    ["#3f6b3a", "#6b4a2a", "#d9b24c", "#e0b48f"], 1.0, ["shoot", "light_dash", "multishot", "rain_of_arrows", "archer_wounding_arrow", "fan_shot"])
cls("Merc_Archer_Crossbowman", "Crossbowman", "human", "ranged", "physical", ["crossbow"], "helm_nasal", "leather", "leather", "quiver",
    ["#7a4b2b", "#46505c", "#c9a24a", "#d9a982"], 1.0, ["heavy_shoot", "medium_dash", "deadeye_shot", "impaler_bolt", "caltrops", "pewpewpew"])
cls("Merc_Archer_Goblin", "Goblin Archer", "goblin", "ranged", "nature", ["bow_short"], "bandana", "ragged", "leather", "quiver",
    ["#6e5b2f", "#3d4a2b", "#c35a2a", "#7fae45"], 0.82, ["shoot", "light_dash", "poison_knife", "slingshot", "burning_arrow", "entangling_shot"])
cls("Merc_Archmage", "Archmage", "human", "mage", "arcane", ["staff_crystal", "orb"], "hat_wizard", "robe_long", "mantle", "cape_long",
    ["#4a2f8f", "#d6b44a", "#7ee0ff", "#e4bfa0"], 1.0, ["magic_missile", "mage_dash", "archmage_element_1", "archmage_element_2", "archmage_element_3", "archmage_invoke"])
cls("Merc_Astralwing", "Astralwing", "human", "mage", "arcane", ["staff_crystal"], "circlet", "robe", "mantle", "wings_astral",
    ["#243a7a", "#e8e0ff", "#ffd86b", "#e8d0c0"], 1.0, ["astral_missile", "cosmic_dash", "falling_star", "lesser_star", "comet_breath", "astral_flight"])
cls("Merc_Bladedancer", "Bladedancer", "human", "assassin", "physical", ["sword_short", "sword_short"], "mask_bandit", "wraps", "none", "cape_short",
    ["#7a1f4a", "#1d1a24", "#e8e0d0", "#d8b090"], 1.0, ["bladedancer_slash", "blade_pirouette", "bladedancer_razor_waltz", "black_thread", "midnight_draw", "kiss_of_the_eclipse"])
cls("Merc_Blood_Harvester", "Blood Harvester", "human", "bruiser", "blood", ["scythe"], "hood_rogue", "coat", "spiked", "wings_bat",
    ["#6b0f1a", "#1a1015", "#d6403c", "#c9b0a8"], 1.0, ["blood_harvester_reap", "bat_flight", "open_vein", "crimson_veil", "blood_quarry", "the_red_hour"])
cls("Merc_Elementalist", "Elementalist", "human", "mage", "fire", ["staff_wood"], "hair_long", "robe", "mantle", "none",
    ["#b8431f", "#2a6fb0", "#f4d35e", "#e2b898"], 1.0, ["elementalist_bolt", "elementalist_dash", "catalyst_nova", "resonant_lightning", "unstable_ice_bomb", "fire_nova"])
cls("Merc_EmberPriest", "Ember Priest", "human", "healer", "fire", ["censer"], "hat_mitre", "robe_long", "mantle", "cape_short",
    ["#a8321c", "#e8c35a", "#ff9a3c", "#d8b090"], 1.0, ["emberfall_basic_attack", "light_dash", "ember_sparks", "emberpriest_nova", "immolation_blessing", "baptizedbyfire"])
cls("Merc_Goblin_Ambusher", "Goblin Ambusher", "goblin", "assassin", "shadow", ["dagger", "dagger"], "hood_rogue", "ragged", "none", "none",
    ["#2c2f3a", "#4b5a2a", "#e0c040", "#7aa844"], 0.8, ["goblin_ambusher_shiv", "rogue_dash", "goblin_vanish", "pocket_sand", "shank_and_run", "lights_out"])
cls("Merc_Halberdier", "Halberdier", "human", "bruiser", "physical", ["halberd"], "helm_plume", "scale", "plate", "none",
    ["#8c7a52", "#3a3f4a", "#c0392b", "#d9b08c"], 1.05, ["halberdier_thrust", "halberdier_lunging_step", "halberdier_heavy_sweep", "halberd_impale", "halberdier_iron_carousel", "halberdier_sky_splitter"])
cls("Merc_Healer_Cleric", "Cleric", "human", "healer", "holy", ["mace", "shield_buckler"], "hat_mitre", "tabard", "plate", "cape_short",
    ["#e8e2c8", "#4a74b8", "#f3d36a", "#e0b898"], 1.0, ["divine_light", "light_dash", "holy_light", "mass_mend", "sanctuary", "lay_on_hands"])
cls("Merc_Healer_Priest", "Priest", "human", "healer", "holy", ["staff_holy"], "hood_cowl", "robe_long", "mantle", "none",
    ["#f0ead8", "#8a6fc0", "#f3d36a", "#e8c8a8"], 1.0, ["divine_light", "mage_dash", "magic_heal", "rejuvenation", "wave_of_rejuvenation", "resurrection"])
cls("Merc_Hellforged", "Hellforged", "demon", "bruiser", "fire", ["axe_great"], "helm_demon", "plate", "flame", "tail_demon",
    ["#3a1a14", "#e0561c", "#ffb347", "#8a2a1c"], 1.12, ["hellforged_cleave", "hellforged_advance", "branding_axe", "cinder_armor", "bloodfire", "combustion"])
cls("Merc_Hierophant", "Hierophant", "human", "support", "holy", ["staff_holy", "tome"], "crown", "robe_long", "mantle", "cape_long",
    ["#f4f0e0", "#c9a227", "#6ad0ff", "#e4c4a4"], 1.0, ["guided_hand", "light_dash", "guiding_light", "holy_wrath", "blessed_protection", "chain_heal"])
cls("Merc_Hunter", "Hunter", "human", "ranged", "nature", ["bow_long"], "hood_cowl", "vest_ranger", "fur", "quiver",
    ["#5a6b3a", "#3b2c20", "#c78a3c", "#d0a278"], 1.0, ["hunter_shoot", "wind_step", "hunter_mark", "hunter_bleeding_trap", "lay_trap", "arrow_barrage"])
cls("Merc_Luchador", "Luchador", "human", "bruiser", "physical", ["fists"], "mask_luchador", "wraps", "none", "cape_short",
    ["#d62f3a", "#2a60c0", "#f2d046", "#c8946c"], 1.12, ["luchador_chop", "kick_dash", "luchador_crossbody", "luchador_german_suplex", "luchador_powerbomb", "luchador_hulk_up"])
cls("Merc_Mage_Chronomaster", "Chronomaster", "human", "mage", "arcane", ["staff_crystal"], "hat_wizard", "robe", "mantle", "cape_short",
    ["#1d6b73", "#c9a64a", "#a8f0e8", "#e0bc9c"], 1.0, ["chronomaster_basic", "chrono_dash", "rewind", "freeze_time", "chrono_needle_barrage", "refresher"])
cls("Merc_Mage_Conjurer", "Conjurer", "human", "summoner", "arcane", ["wand", "tome"], "hat_wizard", "robe", "mantle", "tome_chained",
    ["#5b2a86", "#2a1a44", "#f070ff", "#e2c0a4"], 1.0, ["multiball", "conjurer_dash", "arcane_turret", "manta_illusions", "beam_turret", "gravity_well"])
cls("Merc_Mage_Fire", "Pyromancer", "human", "mage", "fire", ["staff_fire"], "hat_wizard", "robe", "mantle", "cape_short",
    ["#c0391b", "#3a1a1a", "#ffb347", "#e0b898"], 1.0, ["fireball", "firemage_dash", "fire_wave", "meteor_rain", "flamethrower", "megameteor"])
cls("Merc_Mage_Ice", "Cryomancer", "human", "mage", "ice", ["staff_ice"], "hood_cowl", "robe", "mantle", "cape_short",
    ["#3a78b8", "#e8f4ff", "#9fe8ff", "#e6ccb8"], 1.0, ["ice_bolt", "ice_dash", "ice_shards", "blizzard", "ice_pillar", "ice_apocalypse"])
cls("Merc_Mage_Lightning", "Stormcaller", "human", "mage", "lightning", ["staff_storm"], "hair_spiky", "robe", "mantle", "none",
    ["#2f3f8f", "#f2e14a", "#8ad0ff", "#dfbb9c"], 1.0, ["lightning_strike", "thunder_dash", "chain_lightning", "ball_lightning", "thunder_storm", "storm_crown"])
cls("Merc_Mage_Railcaster", "Railcaster", "human", "ranged", "lightning", ["staff_storm"], "goggles", "coat", "plate", "backpack",
    ["#3b4658", "#e0a030", "#6af0ff", "#d4b090"], 1.0, ["coil_spark", "thunder_dash", "railmark", "rail_splitter", "overrail", "rail_backblast"])
cls("Merc_Mage_Reaper", "Reaper", "human", "mage", "shadow", ["scythe"], "helm_skull", "robe", "bone", "cape_long",
    ["#1d1a2a", "#5ad08a", "#b8ffd0", "#c8d4c0"], 1.0, ["reaper_beam", "reaper_dash", "reaper_salvo", "reaper_turret", "reaper_minefield", "reap_the_void"])
cls("Merc_Minotaur_Bullbreaker", "Bullbreaker", "minotaur", "tank", "earth", ["hammer_great"], "none", "plate", "big", "none",
    ["#5b4636", "#9a8a6a", "#d04030", "#6a4a38"], 1.35, ["slash_minotaur", "bull_rush_dash", "gore_charge", "HornRush", "horned_bulwark", "headbutt_titan"])
cls("Merc_Minotaur_Stormhorn", "Stormhorn", "minotaur", "bruiser", "lightning", ["axe_double"], "none", "scale", "spiked", "none",
    ["#2b3558", "#8aa8d8", "#f2e14a", "#4a5a78"], 1.35, ["slash_minotaur", "bull_rush_dash", "stormfang", "stormhorn_sanguine_brand", "storm_slam", "huracan"])
cls("Merc_Monk", "Monk", "human", "bruiser", "wind", ["fists"], "headband", "wraps", "none", "none",
    ["#d9822b", "#7a3a1c", "#f2e0b0", "#d3a57c"], 1.0, ["slash_monk", "wind_step", "dragon_punch", "flyingkick_monk", "blows_of_furry", "inner_meditation"])
cls("Merc_Orc_Berserker", "Orc Berserker", "orc", "bruiser", "blood", ["axe_double"], "none", "fur", "bone", "none",
    ["#6a3d2a", "#a82a20", "#e8d8b0", "#5f8a3a"], 1.18, ["berserker_club_smash", "berserker_dash", "berserker_bloodrush", "berserker_reckless_swing", "bloodrage_orc", "berserker_crack_the_earth"])
cls("Merc_Orc_Shaman", "Orc Shaman", "orc", "healer", "nature", ["staff_totem"], "none", "fur", "bone", "totem_stick",
    ["#4a6a3a", "#8a5a2a", "#6ae0a0", "#5a8a40"], 1.12, ["shaman_bolt", "light_dash", "chain_heal", "orc_shaman_mortal_life", "storm_totem", "rejuvenation"])
cls("Merc_Orc_Warrior", "Orc Warrior", "orc", "tank", "physical", ["axe_great"], "helm_horned", "plate", "spiked", "none",
    ["#4a4f58", "#a03020", "#d8c070", "#5f8a3a"], 1.2, ["slash_orc", "heavy_dash", "Rend_orc", "war_cry", "shield_bash", "mortal_strike"])
cls("Merc_Paladin_Crusader", "Crusader", "human", "tank", "holy", ["sword_long", "shield_kite"], "helm_great", "plate", "plate", "cape_long",
    ["#d8d4c8", "#2f5ea8", "#e8c860", "#dcb594"], 1.05, ["paladin_slash", "shield_charge", "shield_bash", "holy_protection", "hammer_holy_spin", "heavens_verdict"])
cls("Merc_Paladin_Matriarch", "Matriarch", "human", "tank", "holy", ["hammer_war", "shield_round"], "helm_knight", "plate", "plate", "cape_long",
    ["#e0dccf", "#7a2a6a", "#f0d070", "#e6c4a4"], 1.05, ["paladin_slash", "shield_charge", "hammer_holy_spin_matriarch", "hammer_throw_matriarch", "matriarch_bond", "blessed_protection"])
cls("Merc_Paladin_Templar", "Templar", "human", "tank", "holy", ["sword_great"], "helm_great", "plate", "big", "cape_long",
    ["#e8e4d8", "#c0392b", "#f4d35e", "#d8b090"], 1.08, ["paladin_slash", "shield_charge", "holy_strike_templar", "god_smite_templar", "heavenly_jump_templar", "divine_vortex_templar"])
cls("Merc_Razorblade", "Razorblade", "human", "assassin", "physical", ["katana"], "hair_ponytail", "wraps", "none", "none",
    ["#2a2f44", "#c8c8d8", "#e0344a", "#d6b090"], 1.0, ["slash_razor", "rogue_dash", "fan_of_blades", "shuriken_blade", "steel_wind", "blade_leap"])
cls("Merc_Reaver", "Reaver", "human", "bruiser", "physical", ["axe_hand", "axe_hand"], "hair_spiky", "fur", "fur", "none",
    ["#8a5a2a", "#3b2c20", "#d09a40", "#cfa07c"], 1.08, ["reaver_throwing_axe", "reaver_hop", "reaver_primal_leap", "reaver_axe_volley", "reaver_ricochet_axe", "reaver_tnt_axe"])
cls("Merc_Riftwalker", "Riftwalker", "human", "assassin", "void", ["sword_short", "dagger"], "hood_rogue", "coat", "mantle", "cape_short",
    ["#2a1f4a", "#7a4ad0", "#d8a8ff", "#c8b4c8"], 1.0, ["thrust_assassin", "fold_step", "rift_needle", "cross_cut", "phase_edge", "steel_constellation"])
cls("Merc_Rockguard", "Rockguard", "human", "tank", "earth", ["pick", "shield_tower"], "helm_great", "plate", "big", "none",
    ["#6b6a62", "#a07a3a", "#e0c070", "#c8a07c"], 1.15, ["rockguard_pick_swing", "shield_charge", "rockguard_shield_wall", "rockguard_taunt", "rockguard_tectonic_fault", "rockguard_counter_avalanche"])
cls("Merc_Rogue_Assasin", "Assassin", "human", "assassin", "shadow", ["dagger", "dagger"], "hood_rogue", "leather", "none", "cape_short",
    ["#26242e", "#5a2a3a", "#c0c0d0", "#d0a888"], 1.0, ["rogue_assassin_slash", "rogue_dash", "rogue_ghost_mode", "throat_cut", "poison_knife", "blink_strike"])
cls("Merc_Rogue_Spellblade", "Spellblade", "human", "assassin", "fire", ["rapier"], "hair_long", "coat", "mantle", "cape_short",
    ["#7a2a6a", "#e0a030", "#ff7a3c", "#e0b898"], 1.0, ["slash_rogue_spellblade", "blazing_dash_spellblade", "ember_sparks_blessing_spellblade", "demon_ascension_spellblade", "blazing_blink", "fire_barrier"])
cls("Merc_Sentinel", "Sentinel", "human", "bruiser", "physical", ["sword_long"], "helm_nasal", "scale", "plate", "cape_short",
    ["#4a5a78", "#c0c0cc", "#e8c860", "#d8b090"], 1.05, ["sentinel_longsword_slash", "sentinel_duelist_step", "sentinel_cross_slash", "sentinel_guard_breaker", "sentinel_omnislash", "sentinel_iron_resolve"])
cls("Merc_Shadow_Priest", "Shadow Priest", "human", "healer", "shadow", ["staff_skull"], "hood_cowl", "cult_robe", "mantle", "none",
    ["#2a1a3a", "#8a3ac0", "#d08aff", "#c4b4c8"], 1.0, ["shadow_touch", "spectral_dash", "shadow_mend", "vampiric_psalm", "grasping_litany", "black_mass"])
cls("Merc_Shockmender", "Shockmender", "human", "healer", "lightning", ["paddles"], "goggles", "coat", "plate", "backpack",
    ["#e0e4ea", "#d03a3a", "#6af0ff", "#d8b090"], 1.0, ["shockmender_paddle_zap", "light_dash", "shockmender_jumpstart", "shockmender_heartbeat", "shockmender_crash_cart", "shockmender_flatline"])
cls("Merc_Swordmaster", "Swordmaster", "human", "assassin", "physical", ["katana"], "hair_ponytail", "tabard", "none", "cape_short",
    ["#d6d6e0", "#2a3a6a", "#e0b040", "#dab494"], 1.0, ["swordmaster_slash", "swordmaster_dash", "swordmaster_threefold_cut", "swordmaster_circle_of_steel", "swordmaster_passing_lunge", "swordmaster_parry"])
cls("Merc_Thunderclaw", "Thunderclaw", "beast", "assassin", "lightning", ["claws"], "none", "none", "none", "tail_beast",
    ["#3a3a58", "#f2e14a", "#8ad0ff", "#5a5a7a"], 1.12, ["slash_thunderclaw", "thunderclaw_dash", "thunderclaw_pounce", "fulminating_strike", "storm_counter", "total_fulmination"])
cls("Merc_Timesworn", "Timesworn", "human", "bruiser", "arcane", ["sword_great"], "helm_knight", "plate", "plate", "banner",
    ["#4a3f2a", "#c9a64a", "#7affd8", "#c8b494"], 1.1, ["timesworn_pendulum_cleave", "timesworn_epoch_step", "timesworn_pendulum_sweep", "timesworn_afterimage_lunge", "timesworn_clockbreaker", "timesworn_final_hour"])
cls("Merc_Vampira", "Vampira", "human", "assassin", "blood", ["claws"], "hair_long", "coat", "mantle", "wings_bat",
    ["#4a0f2a", "#1a1015", "#e0344a", "#e8dcd8"], 1.0, ["velvet_claws", "wind_step", "vampire_bite", "claw_frenzy", "cloud_of_bats", "last_dance"])
cls("Merc_Voidfist", "Voidfist", "human", "bruiser", "void", ["fists"], "headband", "wraps", "none", "none",
    ["#2a1a4a", "#8a5ad8", "#d0a8ff", "#c8b4d0"], 1.0, ["slash_void", "void_dash", "void_flurry", "void_wave", "void_collapse", "void_singularity"])
cls("Merc_Warlock", "Warlock", "demon", "mage", "shadow", ["staff_void", "tome"], "helm_demon", "robe", "bone", "tail_demon",
    ["#2a1030", "#8a2a8a", "#7aff9a", "#7a3a5a"], 1.05, ["accursed_bolt", "necro_dash", "corruption", "withering_curse", "blood_pact", "doomfall"])
cls("Merc_Warrior_Barbarian", "Barbarian", "human", "bruiser", "physical", ["axe_great"], "hair_spiky", "fur", "fur", "none",
    ["#8a5a3a", "#5a3a2a", "#d8c8a0", "#cc9a74"], 1.12, ["slash_warrior_barbarian", "berserker_dash", "whirlwind", "leap_smash", "bloodrage", "execute"])
cls("Merc_Warrior_Blackguard", "Blackguard", "human", "tank", "shadow", ["sword_great", "shield_kite"], "helm_horned", "plate", "spiked", "cape_long",
    ["#1c1c24", "#7a1f2a", "#c0c0c8", "#d0aa88"], 1.08, ["thrust", "shield_charge", "blackguard_shield_bash", "dark_aegis", "abyssal_slam", "apex_cleave"])
cls("Merc_Warrior_Fighter", "Fighter", "human", "bruiser", "physical", ["sword_long", "shield_round"], "helm_nasal", "plate", "plate", "cape_short",
    ["#8a8f9c", "#a83a2a", "#e0c070", "#dcb492"], 1.02, ["slash_warrior_fighter", "medium_dash", "shield_bash", "whirlwind_strike", "battle_shout", "sever"])
cls("Merc_Warrior_FrostKnight", "Frost Knight", "human", "tank", "ice", ["hammer_war"], "helm_frost", "plate", "frost", "cape_long",
    ["#b8d8f0", "#2a5a98", "#e8faff", "#d8e0ec"], 1.1, ["frost_knight_smash", "frozen_wake_dash", "frostbreaker_maul", "glacial_bash", "frost_armor", "frost_whirlwind"])
cls("Merc_Warrior_Lancero", "Lancero", "human", "bruiser", "physical", ["spear"], "helm_plume", "scale", "plate", "cape_short",
    ["#a8322a", "#e0b040", "#f4f0e0", "#d8ac86"], 1.05, ["spear_thrust", "medium_dash", "SpearSweep", "SpearGo", "spear_flurry", "Skewer"])
cls("Merc_Werewolf", "Werewolf", "beast", "bruiser", "nature", ["claws"], "none", "none", "none", "tail_beast",
    ["#5a4a3a", "#8a7a68", "#e0d070", "#6a5a48"], 1.22, ["werewolf_claw", "werewolf_charge", "werewolf_pounce", "werewolf_roar", "werewolf_frenzy", "werewolf_vampire_strike"])
cls("Merc_Wind_Twister", "Wind Twister", "human", "mage", "wind", ["staff_wood"], "headband", "robe", "mantle", "cape_short",
    ["#5ab8a0", "#e8f4f0", "#b8fff0", "#d4b08c"], 1.0, ["mini_tornado", "wind_step", "tornado", "twister_waves", "wind_twister_crosswind", "wind_convergence"])
cls("Merc_Witch_Hunter", "Witch Hunter", "human", "ranged", "holy", ["crossbow", "dagger"], "hat_witch_hunter", "coat", "leather", "cape_long",
    ["#3a2f2a", "#a08040", "#e8e0c8", "#d4ac88"], 1.0, ["witch_hunter_crossbow_shot", "witch_hunter_tactical_roll", "witch_hunter_hex_bolt", "witch_hunter_purifying_flame", "witch_hunter_silver_chain", "witch_hunter_smoke_bomb"])
cls("Merc_Necromancer", "Necromancer", "skeleton", "summoner", "shadow", ["staff_skull"], "helm_skull", "cult_robe", "bone", "cape_long",
    ["#1c1a28", "#5a8a6a", "#9affb8", "#d8d4c0"], 1.0, ["shadow_touch", "necro_dash", "SummonSkeleton", "SummonSkeletonMage", "LifeDrainChannel", "SummonKnight"], note="res://Data/Mercenaries/Necromancer/Merc_Necromancer.tres")

assert len(C) == 57, len(C)
ALL_IDS = set(AB.keys())
_miss=[(c["id"],a) for c in C for a in c["kit"] if a not in ALL_IDS]
_miss+=[(k,v[3]) for k,v in champ_defs_pre.items() if v[3] not in ALL_IDS] if False else []
if _miss: raise SystemExit("MISSING kit ids: %r" % _miss)
for c in C:
    base = ROLE_BASE[c["role"]]
    c["base"] = dict(hp=base[0], mana=base[1], stamina=base[2], power=base[3], defense=base[4], mres=base[5], speed=base[6])
    c["path"] = "res://Data/Mercenaries/" + ("Necromancer/" if c["id"] == "Merc_Necromancer" else "") + c["id"] + ".tres"
    # petites variations de classe
    r = random.Random(h(c["id"], 10**6))
    c["base"]["hp"] = int(c["base"]["hp"] * (0.92 + r.random() * 0.16) * (1.0 + (c["scale"] - 1.0) * 0.5))
    c["base"]["power"] = round(c["base"]["power"] * (0.94 + r.random() * 0.12), 1)
    c["base"]["speed"] = round(c["base"]["speed"] * (0.97 + r.random() * 0.06) / (1.0 + (c["scale"] - 1.0) * 0.35), 2)
    # statut de ressource: les classes cac/mêlée ont plus d'endurance
    c["ai"] = {
        "aggression": {"tank": 0.7, "bruiser": 0.75, "assassin": 0.85, "ranged": 0.35, "mage": 0.3, "healer": 0.2, "support": 0.3, "summoner": 0.3}[c["role"]],
        "preferred_range": {"tank": 2.6, "bruiser": 3.0, "assassin": 2.6, "ranged": 13.0, "mage": 12.0, "healer": 11.0, "support": 10.0, "summoner": 11.0}[c["role"]],
    }

# ----------------------------------------------------------------------------------------------
# 3. Champions nommés (46), boss (18) et spéciaux (5) : classe de base + gimmick
# ----------------------------------------------------------------------------------------------
CLASS_BY_ID = {c["id"]: c for c in C}
champ_defs = {
    # id: (nom affiché, classe de base, couleur aura, capacité signature)
    "AlphaEsther": ("Alpha Esther", "Merc_Werewolf", "#7aa8ff", "werewolf_roar"),
    "Angelitus": ("Angelitus", "Merc_Astralwing", "#ffe9a0", "celestial_expansion"),
    "Aria": ("Aria", "Merc_Paladin_Matriarch", "#ffd0f0", "aria_vanguard_of_retaliation"),
    "AsterTheVoidborne": ("Aster the Voidborne", "Merc_Voidfist", "#a070ff", "void_singularity"),
    "Beeu": ("Beeu", "Merc_Mage_Conjurer", "#ffe14a", "manta_illusions"),
    "BoomSpankcrackle": ("Boom Spankcrackle", "Merc_Orc_Shaman", "#6af0ff", "boom_spankcrackle_storm_totem"),
    "Brunt": ("Brunt", "Merc_Orc_Warrior", "#ff7050", "bloodrage_orc"),
    "Cadooty": ("Cadooty", "Merc_Archer_Goblin", "#c8ff60", "pocket_sand"),
    "Calciforsaken": ("Calciforsaken", "Merc_Necromancer", "#d8f0d0", "SummonSkeletonGuard"),
    "ChokiOldfinger": ("Choki Oldfinger", "Merc_Rogue_Assasin", "#c0c0d0", "poison_knife"),
    "Crixtorta": ("Crixtorta", "Merc_Mage_Fire", "#ff8030", "firestorm"),
    "GuraCaine": ("Gura Caine", "Merc_Vampira", "#ff4060", "last_dance"),
    "Hellscar": ("Hellscar", "Merc_Hellforged", "#ff5a1c", "hellscar_shield_throw"),
    "HetuxoTheUnstoppable": ("Hetuxo the Unstoppable", "Merc_Minotaur_Bullbreaker", "#e0c070", "HornRush"),
    "IchiVonChai": ("Ichi von Chai", "Merc_Swordmaster", "#a0e0ff", "swordmaster_threefold_cut"),
    "Ignatius": ("Ignatius", "Merc_EmberPriest", "#ffb040", "holy_fire"),
    "Johan": ("Johan", "Merc_Warrior_Fighter", "#e0e0f0", "battle_shout"),
    "Kanguin": ("Kanguin", "Merc_Luchador", "#ff6aa0", "luchador_three_count"),
    "Kokutenko": ("Kokutenko", "Merc_Monk", "#ffd070", "dragon_palm_rush"),
    "Kreeshawn": ("Kreeshawn", "Merc_Rogue_Spellblade", "#ff60c0", "demon_ascension_spellblade"),
    "Lam": ("Lam", "Merc_Healer_Priest", "#a0ffd0", "mass_mend"),
    "Leo": ("Leo", "Merc_Paladin_Crusader", "#ffd24a", "holy_wrath"),
    "Leonaldo": ("Leonaldo", "Merc_Hunter", "#80ff90", "arrow_barrage"),
    "LordGidengard": ("Lord Gidengard", "Merc_Warrior_Blackguard", "#8060c0", "dark_aegis"),
    "LordOfTheLash": ("Lord of the Lash", "Merc_Blood_Harvester", "#ff2040", "whip_strike"),
    "Lord_Bentlant": ("Lord Bentlant", "Merc_Sentinel", "#90a8ff", "sentinel_omnislash"),
    "Manny": ("Manny", "Merc_Rockguard", "#d0b080", "rockguard_bastion_nova"),
    "Oximofe": ("Oximofe", "Merc_Mage_Ice", "#80f0ff", "oximofe_oxi_breath"),
    "Pochus": ("Pochus", "Merc_Goblin_Ambusher", "#d8ff50", "tripwire"),
    "Prei": ("Prei", "Merc_Shockmender", "#60ffff", "shockmender_capacitor_burst"),
    "RobertTheResolute": ("Robert the Resolute", "Merc_Paladin_Templar", "#fff0a0", "god_smite_templar"),
    "ShockyShock": ("Shocky Shock", "Merc_Mage_Lightning", "#ffff60", "total_fulmination"),
    "Simo": ("Simo", "Merc_Razorblade", "#ff9090", "steel_wind"),
    "SleepyGiant": ("Sleepy Giant", "Merc_Minotaur_Stormhorn", "#8090ff", "stormhorn_sanguine_brand"),
    "SoupAnatomist": ("Soup Anatomist", "Merc_Mage_Reaper", "#70ffa0", "reaper_minefield"),
    "StrongBadia": ("Strong Badia", "Merc_Warrior_Barbarian", "#ff9050", "super_battle_shout"),
    "Sulzer": ("Sulzer", "Merc_Archer_Crossbowman", "#ffb060", "double_grenade"),
    "TayTay": ("Tay Tay", "Merc_Bladedancer", "#ff70d0", "last_dance"),
    "TheOddMan": ("The Odd Man", "Merc_Riftwalker", "#c0a0ff", "twin_knockdown"),
    "TheOffsong": ("The Offsong", "Merc_Wind_Twister", "#a0fff0", "huracan"),
    "ThomasKopv": ("Thomas Kopv", "Merc_Halberdier", "#d0d0a0", "halberd_toll"),
    "TristanThunder": ("Tristan Thunder", "Merc_Thunderclaw", "#ffff80", "storm_counter"),
    "UgZormak": ("Ug Zormak", "Merc_Orc_Berserker", "#ff8040", "berserker_crack_the_earth"),
    "UkernanTheScout": ("Ukernan the Scout", "Merc_Archer_Bowman", "#a0ff80", "golden_multishot"),
    "VakiHyEh": ("Vaki Hy-Eh", "Merc_Timesworn", "#80ffd0", "timesworn_hourglass_reversal"),
    "ZeroTheInfernalKnight": ("Zero the Infernal Knight", "Merc_Warlock", "#ff4020", "doomfall"),
}
champions = []
for k, (nm, base, aura, sig) in champ_defs.items():
    assert base in CLASS_BY_ID, (k, base)
    assert sig in ALL_IDS, (k, sig)
    champions.append(dict(id="Named_Champion_" + k, key=k, name=nm, kind="champion", base_class=base, aura=aura, signature=sig,
                          stat_mult=1.35, scale_mult=1.1, path="res://Data/Mercenaries/Champions/Named_Champion_%s.tres" % k))
assert len(champions) == 46, len(champions)

boss_defs = [
    ("Named_Blackguard_Boss_ValdrakTheGilded", "Valdrak the Gilded", "Merc_Warrior_Blackguard", "#e8c050", "abyssal_slam"),
    ("Named_Firemage_Boss_Scorchus", "Scorchus", "Merc_Mage_Fire", "#ff6020", "volcanic_eruption"),
    ("Named_Goblin_Boss_ChukiTheKing", "Chuki the King", "Merc_Goblin_Ambusher", "#d8ff40", "tripwire"),
    ("Named_Minotaur_Boss_GorrWildhorn", "Gorr Wildhorn", "Merc_Minotaur_Bullbreaker", "#d09040", "HornRush"),
    ("Named_OrcShaman_Boss_GoomGoom", "Goom Goom", "Merc_Orc_Shaman", "#60ff90", "storm_totem"),
    ("Named_Orc_Boss_UgDunath", "Ug Dunath", "Merc_Orc_Warrior", "#ff5030", "Dunath_riches"),
    ("Named_Orc_Boss_UgShatup", "Ug Shatup", "Merc_Orc_Berserker", "#ff3020", "UgShatupLeap"),
    ("Named_Paladin_Boss_Giganton", "Giganton", "Merc_Paladin_Templar", "#fff0a0", "titan_slam"),
    ("Named_Paladin_Boss_Shiroba", "Shiroba", "Merc_Paladin_Crusader", "#ffffff", "holy_wrath"),
    ("Named_Priest_Boss_LinaLeFranc", "Lina le Franc", "Merc_Healer_Priest", "#80ffc0", "resurrection"),
    ("Named_Priest_Boss_StellaRox", "Stella Rox", "Merc_Shadow_Priest", "#d070ff", "black_mass"),
    ("Named_Rogue_Boss_Betto", "Betto", "Merc_Rogue_Assasin", "#ffd060", "BettoLeap"),
    ("Named_Rogue_Boss_FaustynHighFlame", "Faustyn High-Flame", "Merc_Rogue_Spellblade", "#ff8030", "blazing_dash"),
    ("Named_Thunderclaw_Boss_CoopyDarkstorm", "Coopy Darkstorm", "Merc_Thunderclaw", "#6060ff", "total_fulmination"),
    ("Named_Warrior_Boss_DalbuTheJurist", "Dalbu the Jurist", "Merc_Warrior_Fighter", "#c0c0ff", "thejudgement"),
    ("Named_Warrior_Boss_DonDiego", "Don Diego", "Merc_Swordmaster", "#ff4060", "swordmaster_duelist_challenge"),
    ("Named_Warrior_Boss_KarmFirstSpear", "Karm First-Spear", "Merc_Warrior_Lancero", "#ffcf60", "SpearGo"),
    ("Named_Warrior_Boss_Kragor", "Kragor", "Merc_Warrior_Barbarian", "#ff6040", "orc_boss_smash"),
]
special_defs = [
    ("Named_Batum_Fatfury", "Batum Fatfury", "Merc_Luchador", "#ff80a0", "giant_swing"),
    ("Named_Hydrax_Veyr", "Hydrax Veyr", "Merc_Astralwing", "#60ffc0", "astral_spray_turret"),
    ("Named_Lord_Innervision", "Lord Innervision", "Merc_Archmage", "#c070ff", "innervision_barrage"),
    ("Named_Lord_Kanishka", "Lord Kanishka", "Merc_Hierophant", "#ffe080", "holy_wrath"),
    ("Named_StefanRoses", "Stefan Roses", "Merc_Vampira", "#ff2060", "cloud_of_bats"),
]
bosses = []
for (i, nm, base, aura, sig) in boss_defs:
    assert base in CLASS_BY_ID and sig in ALL_IDS, (i, base, sig)
    bosses.append(dict(id=i, name=nm, kind="boss", base_class=base, aura=aura, signature=sig, stat_mult=2.6, scale_mult=1.35,
                       path="res://Data/Mercenaries/%s.tres" % i))
specials = []
for (i, nm, base, aura, sig) in special_defs:
    assert base in CLASS_BY_ID and sig in ALL_IDS, (i, base, sig)
    specials.append(dict(id=i, name=nm, kind="special", base_class=base, aura=aura, signature=sig, stat_mult=1.9, scale_mult=1.2,
                         path="res://Data/Mercenaries/%s.tres" % i))
assert len(bosses) == 18 and len(specials) == 5

# ----------------------------------------------------------------------------------------------
# 4. Reliques
# ----------------------------------------------------------------------------------------------
relic_names = ["ApprenticesTome", "ArcaneWhisper", "BriskAnklet", "BristleGuard", "BrokenHourglass", "BucklerSigil", "CenteringStone", "Cometspur",
               "DeepwellPendant", "EmberFlask", "EnduringGirdle", "FeatherstepCharm", "FletchersPin", "GhostglassWard", "GlassComet", "HealersThimble",
               "IronLung", "LastingStitch", "LongshotLocket", "MendersPin", "MercyBand", "MessisFarewellLetter", "RedhideWrap", "SafeStep", "SteadyFooting",
               "SunlitCharm", "SwiftSole", "TinLocket", "VanguardCrest", "VitalSip", "WarmBandage", "WellspringSigil", "WhettedFang", "WomboCombo",
               "MirrorbreakerGlove", "SecondString", "SiegeBell", "WindCharm"]
EFFECTS = [
    ("atk_perc", "+{v}% Power", (3, 9)), ("msp_perc", "+{v}% Speed", (3, 8)), ("hp_perc", "+{v}% max HP", (4, 12)),
    ("def_perc", "+{v}% DEF", (4, 12)), ("man_perc", "+{v}% maximum mana.", (8, 24)), ("sta_perc", "+{v}% maximum stamina.", (8, 24)),
    ("healing_done_perc", "+{v}% healing done.", (6, 18)), ("healing_received_perc", "+{v}% healing received.", (6, 18)),
    ("mana_cost_reduction_perc", "Costes de mana -{v}%.", (6, 18)), ("stamina_cost_reduction_perc", "-{v}% ability stamina costs.", (6, 18)),
    ("basic_damage_perc", "Basic attacks deal +{v}% damage. Does not affect damage over time or reflected damage.", (6, 18)),
    ("ability_damage_perc", "Non-basic abilities deal +{v}% direct damage. Does not affect damage over time, reflected damage or relic effects.", (6, 18)),
    ("projectile_speed_flat", "+{v} basic attack projectile speed.", (2, 6)), ("dash_stamina_reduction_perc", "Basic dashes cost {v}% less stamina.", (10, 30)),
    ("first_mana_reduction_perc", "Once per round, the first ability with an upfront mana cost costs {v}% less mana.", (20, 60)),
    ("first_cooldown_reduction_perc", "La première utilisation de chaque compétence éligible par manche a un cooldown réduit de {v}%.", (15, 40)),
    ("start_speed_perc", "+{v}% Speed for the first 6 s of each round.", (10, 30)),
    ("glass_cannon", "+{v}% Power, +{v}% Speed, but takes +{v}% damage.", (8, 16)),
    ("start_barrier_perc", "Au début de chaque manche : barrière de {v}% max HP pendant 5 s.", (8, 20)),
    ("kill_reset", "Al rematar a un enemigo, reinicia todos los cooldowns activos (max une fois / 8s).", (1, 1)),
    ("distance_dmg", "Projectiles deal up to +{v}% damage with distance, reaching maximum at 75% of projectile range.", (8, 22)),
    ("heal_low_perc", "Heals other allies below 50% HP for {v}% more.", (10, 30)),
    ("dash_def_perc", "After a dash, gains +{v}% DEF for 3s. Repeated dashes refresh the duration without stacking.", (8, 24)),
    ("shield_def_flat", "+{v} DEF while a shield is active on the wearer.", (6, 16)),
    ("echo_dash", "Après un dash, la prochaine attaque de base dans 4s répète {v}% de ses dégâts. CD interne 6s. Les dashes coûtent 15% de ressources en plus.", (40, 80)),
]
relics = []
RARITIES = [("common", 0.5, 0.8), ("uncommon", 0.28, 1.0), ("rare", 0.14, 1.25), ("epic", 0.06, 1.55), ("legendary", 0.02, 2.0)]
rr = random.Random(777)
for n in range(81):
    rid = "rel_c_%03d" % (n + 1) if n < 70 else ("rel_r_%03d" % (n - 69) if n < 80 else "rel_l_012")
    name_key = relic_names[n % len(relic_names)]
    eff = EFFECTS[(n * 7 + h(rid, 50)) % len(EFFECTS)]
    # rareté dépend du préfixe
    if rid.startswith("rel_l"): rar = "legendary"
    elif rid.startswith("rel_r"): rar = "epic" if n % 2 else "rare"
    else:
        x = rr.random()
        acc = 0
        rar = "common"
        for nm, p, m in RARITIES[:3]:
            acc += p
            if x < acc:
                rar = nm
                break
    mult = {"common": 0.8, "uncommon": 1.0, "rare": 1.25, "epic": 1.55, "legendary": 2.0}[rar]
    lo, hi = eff[2]
    val = round(lo + (hi - lo) * min(1.0, 0.35 * mult + rr.random() * 0.4), 1)
    if lo == hi: val = lo
    price = int({"common": 220, "uncommon": 420, "rare": 800, "epic": 1500, "legendary": 3200}[rar] * (0.85 + rr.random() * 0.3))
    suffix = ["", " II", " III", " of Dawn", " of Dusk", " of Embers", " of the Deep", " of Echoes", " of Thorns", " of Storms"][(n // len(relic_names)) % 10]
    relics.append(dict(id=rid, key=name_key, name=pretty(name_key) + suffix, rarity=rar, effect=eff[0], value=val, desc=eff[1].replace("{v}", str(int(val) if val == int(val) else val)),
                       price=price, icon=name_key))
# 4 ressources .tres connues
resource_relics = {"MirrorbreakerGlove": "res://Data/Relics/MirrorbreakerGlove.tres", "SecondString": "res://Data/Relics/SecondString.tres",
                   "SiegeBell": "res://Data/Relics/SiegeBell.tres", "WindCharm": "res://Data/Relics/WindCharm.tres"}

# ----------------------------------------------------------------------------------------------
# 5. Équipes (23 + générées), quirks, médailles, facilities, staff
# ----------------------------------------------------------------------------------------------
team_ids = [p.split("/")[-1].replace(".tres", "") for p in DUMP["other_data"]["Teams"]]
team_names = {
    "Fullbetto": "Full Betto", "FuryUnited": "Fury United", "GoldenChop": "Golden Chop", "Hammerborne": "Hammerborne",
    "HyperHydras": "Hyper Hydras", "IronvaleWardens": "Ironvale Wardens", "KanishkaAcademy": "Kanishka Academy",
    "Oldfingers": "Oldfingers", "OrderInnervision": "Order of Innervision", "StarFlame": "Star Flame",
    "Team_Aconcagua": "Aconcagua", "Team_BandOfTheThorn": "Band of the Thorn", "Team_BinaryOrcs": "Binary Orcs",
    "Team_BlackRavens": "Black Ravens", "Team_DonDiamonds": "Don Diamonds", "Team_DunathWarriors": "Dunath Warriors",
    "Team_GlitchedHand": "Glitched Hand", "Team_ShadowSun": "Shadow Sun", "Team_TheJurists": "The Jurists",
    "Team_ThePowerBallad": "The Power Ballad", "Team_TheStaticStorm": "The Static Storm", "TheCovenant": "The Covenant",
    "WildhornClan": "Wildhorn Clan"}
extra_team_names = ["Obsidian Skulls", "Bloodthirsty Wasps", "Dark Order", "Savage Mantis", "Condemned", "Utopia Hunters", "Mercenary Union",
                    "Cinder Sentinels", "Ghost Outlaws", "Skvell D", "Iron Wolves", "Crimson Tide", "Ashen Vanguard", "Frostfang Pack",
                    "Gilded Vipers", "Hollow Kings", "Stormbreakers", "Ember Court", "Pale Lanterns", "Rustborn", "Gravewind", "Thornguard",
                    "Brass Phalanx", "Nightingale Guild", "Sundered Oath", "Copper Crows", "Harrow Company", "Vesper Legion", "Ironbark Boars"]
teams = []
for tid in team_ids:
    teams.append(dict(id=tid, name=team_names.get(tid, pretty(tid)), path="res://Data/Teams/%s.tres" % tid, named=True,
                      lean=random.Random(h(tid, 10**6)).choice(["tank", "bruiser", "assassin", "ranged", "mage", "balanced", "balanced"])))
for n in extra_team_names:
    teams.append(dict(id="gen_" + re.sub(r"\W+", "_", n.lower()), name=n, named=False,
                      lean=random.Random(h(n, 10**6)).choice(["tank", "bruiser", "assassin", "ranged", "mage", "balanced", "balanced"])))

quirks = [
    ("glass_jaw", "Mâchoire de verre", "+8% dégâts infligés, +10% dégâts subis", {"atk_perc": 8, "damage_taken_perc": 10}),
    ("iron_will", "Volonté de fer", "-12% durée des contrôles", {"cc_reduction": 12}),
    ("showboat", "Frimeur", "+6% vitesse en début de manche, -4% défense", {"start_speed_perc": 6, "def_perc": -4}),
    ("second_wind", "Second souffle", "Récupère 15% PV à 25% PV (1x/manche)", {"second_wind": 15}),
    ("lone_wolf", "Loup solitaire", "+10% dégâts sans allié proche", {"lone_wolf": 10}),
    ("team_player", "Esprit d'équipe", "+8% soins reçus et donnés", {"healing_done_perc": 8, "healing_received_perc": 8}),
    ("marathoner", "Marathonien", "+15% endurance max", {"sta_perc": 15}),
    ("arcane_battery", "Batterie arcanique", "+15% mana max", {"man_perc": 15}),
    ("bloodthirsty", "Assoiffé de sang", "Soigne 4% PV max par élimination", {"kill_heal": 4}),
    ("coward", "Poltron", "+8% vitesse, -6% dégâts", {"msp_perc": 8, "atk_perc": -6}),
    ("sharpshooter", "Tireur d'élite", "Projectiles +10% dégâts à distance", {"distance_dmg": 10}),
    ("stubborn", "Têtu", "+10% défense, -5% vitesse", {"def_perc": 10, "msp_perc": -5}),
    ("clumsy", "Maladroit", "-6% dégâts, +6% PV max", {"atk_perc": -6, "hp_perc": 6}),
    ("prodigy", "Prodige", "Croissance +10%", {"growth_perc": 10}),
    ("late_bloomer", "Éveil tardif", "Croissance -5% jusqu'au niv. 10, +15% après", {"late_bloomer": 1}),
]
medals = [
    ("iron_wall", "Mur de fer", "Encaisser des dégâts en match", 3), ("wrecking_hand", "Main destructrice", "Infliger des dégâts en match", 3),
    ("clutch_player", "Joueur décisif", "Gagner un match en dernier survivant", 1), ("lifesaver", "Sauveur", "Soigner / ressusciter des alliés", 1)]
staff = [
    ("coach", "Entraîneur", "Bonus d'XP des combattants du banc", "barracks_bench_xp"),
    ("scout", "Recruteur", "Meilleurs tirages sur le marché", "scouting"),
    ("medic", "Médecin", "Réduit le risque et la durée des blessures", "injury"),
    ("shiny_catcher", "Chasseur de shiny", "Augmente la probabilité de trouver des shiny", "shiny"),
    ("legendary_expert", "Expert légendaire", "Meilleure pitié des capacités légendaires", "legendary"),
    ("tactician", "Tacticien", "Déverrouille des ordres tactiques avancés", "tactics"),
    ("quartermaster", "Intendant", "Réduit les salaires et prix des reliques", "economy"),
]
facilities = [
    ("club_house", "Maison du club", "Revenus, sponsors, capacité de roster", 5),
    ("scouting_office", "Bureau des recruteurs", "Qualité et nombre de recrues sur le marché", 5),
    ("barracks", "Caserne", "XP du banc, entraînement, récupération", 5),
    ("training_grounds", "Terrain d'entraînement / Académie", "Respec ciblé, renaissance, développement", 5),
]

json.dump(abilities, open(os.path.join(OUT, "abilities.json"), "w"), indent=1, ensure_ascii=False)
json.dump(C, open(os.path.join(OUT, "classes.json"), "w"), indent=1, ensure_ascii=False)
json.dump(dict(champions=champions, bosses=bosses, specials=specials), open(os.path.join(OUT, "named.json"), "w"), indent=1, ensure_ascii=False)
json.dump(dict(relics=relics, resource_relics=resource_relics, names=relic_names), open(os.path.join(OUT, "relics.json"), "w"), indent=1, ensure_ascii=False)
json.dump(dict(teams=teams, quirks=[dict(id=a, name=b, desc=c, mods=d) for a, b, c, d in quirks],
               medals=[dict(id=a, name=b, desc=c, tiers=d) for a, b, c, d in medals],
               staff=[dict(id=a, name=b, desc=c, stat=d) for a, b, c, d in staff],
               facilities=[dict(id=a, name=b, desc=c, max_level=d) for a, b, c, d in facilities]),
          open(os.path.join(OUT, "meta.json"), "w"), indent=1, ensure_ascii=False)

# rapports
from collections import Counter
print("abilities:", len(abilities), Counter(a["arch"] for a in abilities).most_common())
print("elements:", Counter(a["element"] for a in abilities).most_common())
print("classes:", len(C), "champions:", len(champions), "bosses:", len(bosses), "specials:", len(specials), "relics:", len(relics), "teams:", len(teams))
