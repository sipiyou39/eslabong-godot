"""Moteur de composition : partition en code, rendu bouclable (repliement circulaire), mixage + limiteur."""
import re
import numpy as np
from scipy import signal as sg
from dsp import *
import inst

NOTE_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
QUAL = {'': (0, 4, 7), 'm': (0, 3, 7), '7': (0, 4, 7, 10), 'm7': (0, 3, 7, 10), 'maj7': (0, 4, 7, 11),
        'dim': (0, 3, 6), 'sus4': (0, 5, 7), 'sus2': (0, 2, 7), '5': (0, 7), '6': (0, 4, 7, 9),
        'm6': (0, 3, 7, 9), 'add9': (0, 4, 7, 14), 'madd9': (0, 3, 7, 14), 'm9': (0, 3, 7, 10, 14),
        '9': (0, 4, 7, 10, 14), 'maj9': (0, 4, 7, 11, 14), 'mM7': (0, 3, 7, 11)}


def pitch(s):
    s = s.strip()
    pc = NOTE_PC[s[0]]
    i = 1
    while i < len(s) and s[i] in '#b':
        pc += 1 if s[i] == '#' else -1
        i += 1
    return pc + 12 * (int(s[i:]) + 1)


def parse_chord(name):
    m = re.match(r'^([A-G][#b]?)(.*)$', name)
    root = NOTE_PC[m.group(1)[0]] + (1 if '#' in m.group(1) else -1 if 'b' in m.group(1) else 0)
    q = m.group(2)
    return root % 12, QUAL[q]


class Chord:
    def __init__(self, name):
        self.name = name
        self.root, self.iv = parse_chord(name)
        self.pcs = [(self.root + i) % 12 for i in self.iv]

    def tones(self, lo, hi):
        return [p for p in range(lo, hi + 1) if p % 12 in self.pcs]

    def root_in(self, lo, hi):
        c = [p for p in range(lo, hi + 1) if p % 12 == self.root]
        return c[0] if c else lo

    def fifth_in(self, lo, hi):
        pc = (self.root + 7) % 12
        c = [p for p in range(lo, hi + 1) if p % 12 == pc]
        return c[0] if c else lo

    def third_pc(self):
        return self.pcs[1] if len(self.pcs) > 1 else self.root

    def voicing_near(self, center, n=4):
        t = sorted(self.tones(center - 14, center + 14), key=lambda p: abs(p - center))
        out = []
        for p in t:
            if p % 12 not in [q % 12 for q in out] or len(out) >= len(self.pcs):
                out.append(p)
            if len(out) >= n:
                break
        return sorted(out)


def voice_lead(prev, ch, lo, hi, n=4, center=None):
    if prev is None:
        return ch.voicing_near(center if center else (lo + hi) // 2, n)
    out = []
    used = set()
    for p in prev:
        cand = sorted(ch.tones(lo, hi), key=lambda x: (abs(x - p), x))
        for c in cand:
            if c not in used:
                out.append(c)
                used.add(c)
                break
    # couverture : fondamentale et tierce
    need = [ch.root, ch.third_pc()] if len(ch.pcs) > 1 else [ch.root]
    for pc in need:
        if pc not in [x % 12 for x in out]:
            cand = sorted([x for x in ch.tones(lo, hi) if x % 12 == pc], key=lambda x: abs(x - np.mean(out)))
            if cand:
                # remplace la voix dont le pc est le plus dupliqué
                pcs = [x % 12 for x in out]
                dup = [i for i, x in enumerate(pcs) if pcs.count(x) > 1]
                idx = dup[-1] if dup else int(np.argmax([abs(x - cand[0]) for x in out]) if False else len(out) - 1)
                out[idx] = cand[0]
    return sorted(out)


def parse_melody(text):
    """'D5:1.5 C5:.5 R:1 D4+F4:2' -> [(midis|None, start, dur)] ; un token '~' après prolonge le précédent."""
    ev = []
    t = 0.0
    for tok in text.split():
        nm_, d = tok.split(':')
        d = float(d)
        if nm_ == 'R':
            ev.append((None, t, d))
        else:
            ev.append(([pitch(x) for x in nm_.split('+')], t, d))
        t += d
    return ev, t


# ---------------------------------------------------------------- morceau
class Song:
    def __init__(self, name, bpm, bars, bpb=4, seed=1):
        self.name = name
        self.bpm = bpm
        self.bars = bars
        self.bpb = bpb
        self.spb = 60.0 / bpm
        self.L = N(bars * bpb * self.spb)
        self.buses = {}
        self.cfg = {}
        self.rng = np.random.default_rng(seed)
        self.prog = {}
        self.lint = []
        self.sections = []

    # -- bus
    def bus(self, name, gain_db=0.0, hall=0.2, room=0.0, pan_=0.0, hp_hz=0.0, lp_hz=0.0):
        self.cfg[name] = dict(gain=dbv(gain_db), hall=hall, room=room, pan=pan_, hp=hp_hz, lp=lp_hz)
        self.buses[name] = np.zeros((self.L, 2))

    def t_of(self, bar, beat=0.0):
        return ((bar - 1) * self.bpb + beat) * self.spb

    def add(self, busname, x, t, pan_=0.0, gain=1.0):
        """Ajoute x (mono ou stéréo) à l'instant t (s) avec repliement circulaire."""
        b = self.buses[busname]
        if x.ndim == 1:
            x = pan(x, pan_) * gain
        else:
            x = x * gain
        i = int(round(t * SR)) % self.L
        n = len(x)
        if n > self.L:
            x = x[:self.L]
            n = self.L
        a = min(n, self.L - i)
        b[i:i + a] += x[:a]
        if a < n:
            b[:n - a] += x[a:]

    def note(self, busname, fn, midi, bar, beat, dur_beats, vel=0.8, pan_=0.0, gain=1.0, human=0.006, **kw):
        t = self.t_of(bar, beat) + (self.rng.normal(0, human) if human else 0.0)
        v = float(np.clip(vel * (1 + self.rng.normal(0, 0.05)), 0.05, 1.0)) if human else vel
        x = fn(midi_hz(midi), dur_beats * self.spb, v, rng=self.rng, **kw)
        self.add(busname, x, t, pan_, gain)

    def hit(self, busname, fn, bar, beat, vel=0.8, pan_=0.0, gain=1.0, human=0.002, **kw):
        t = self.t_of(bar, beat) + (self.rng.normal(0, human) if human else 0.0)
        x = fn(vel=vel, rng=self.rng, **kw)
        self.add(busname, x, t, pan_, gain)

    # -- harmonie
    def set_prog(self, start_bar, names):
        for i, nm_ in enumerate(names.split()):
            self.prog[start_bar + i] = Chord(nm_)

    def chord(self, bar):
        return self.prog[bar]

    # -- parties
    def pad(self, busname, fn, bars, lo=48, hi=72, n=4, vel=0.6, center=None, pan_=0.0, gain=1.0, dur_bars=1.0,
            lead_in=0.0, **kw):
        prev = None
        for b in bars:
            ch = self.chord(b)
            prev = voice_lead(prev, ch, lo, hi, n, center)
            for k, p in enumerate(prev):
                self.note(busname, fn, p, b, -lead_in, dur_bars * self.bpb + lead_in, vel, pan_ + 0.0 * k, gain, **kw)

    def melody(self, busname, fn, text, bar, vel=0.8, pan_=0.0, gain=1.0, lintbus=None, transpose=0, vel_curve=None,
               legato=1.0, **kw):
        ev, total = parse_melody(text)
        for idx, (ps, st, d) in enumerate(ev):
            if ps is None:
                continue
            b = bar + int(st // self.bpb)
            beat = st % self.bpb
            v = vel if vel_curve is None else vel * vel_curve(idx, len(ev))
            for p in ps:
                self.note(busname, fn, p + transpose, b, beat, d * legato, v * (1.0 if beat in (0.0, 2.0) else 0.9), pan_,
                          gain, **kw)
            self._lint(busname, ps, b, beat, d)
        return total / self.bpb

    def _lint(self, busname, ps, bar, beat, d):
        ch = self.prog.get(bar)
        if ch is None:
            return
        for p in ps:
            pc = p % 12
            if pc in ch.pcs:
                continue
            dist = min(min((pc - c) % 12, (c - pc) % 12) for c in ch.pcs)
            strong = beat in (0.0, 2.0)
            if dist == 1 and (d >= 1.0 or strong):
                self.lint.append(f"{self.name} bar{bar} b{beat} {busname} pitch {p} vs {ch.name}: semitone clash (d={d})")
            elif dist == 6 % 12:
                pass

    def pattern(self, busname, fn_hit, bars, pat, vel=0.8, pan_=0.0, gain=1.0, steps=16, accent=None, human=0.002,
                **kw):
        """pat : chaîne de 16 pas/mesure (par ex. 'X...x...x...x...') ; ou liste de chaînes (une par mesure, cyclique)."""
        pats = pat if isinstance(pat, (list, tuple)) else [pat]
        stp = self.bpb / steps
        for bi, b in enumerate(bars):
            p = pats[bi % len(pats)]
            for i, c in enumerate(p):
                if c in '. -|':
                    continue
                lv = {'X': 1.0, 'x': 0.7, 'o': 0.45, 'g': 0.28}.get(c, 0.6)
                self.hit(busname, fn_hit, b, i * stp, vel * lv, pan_, gain, human, **kw)

    # -- mixage
    def master(self, hall=(2.6, 0.5), room=(0.7, 0.4), target_peak_db=-1.0, verbose=True, sat_drive=1.1, thr=0.9, target_rms_db=-17.0):
        dry = np.zeros((self.L, 2))
        hall_in = np.zeros((self.L, 2))
        room_in = np.zeros((self.L, 2))
        stats = {}
        for nme, b in self.buses.items():
            c = self.cfg[nme]
            y = b
            if c['hp']:
                y = _circ(lambda z: hp(z, c['hp'], 2), y)
            if c['lp']:
                y = _circ(lambda z: lp(z, c['lp'], 2), y)
            y = y * c['gain']
            if c['pan']:
                y = y * np.array([np.cos((c['pan'] + 1) * np.pi / 4), np.sin((c['pan'] + 1) * np.pi / 4)]) * 1.414
            dry += y
            hall_in += y * c['hall']
            room_in += y * c['room']
            stats[nme] = to_db(rms(y)) if rms(y) > 0 else -120
        wet = np.zeros((self.L, 2))
        for c in range(2):
            ir_h = make_ir(hall[0], 0.025, 0.55, 5, 1.6, c)
            ir_r = make_ir(room[0], 0.008, 0.5, 9, 0.9, c)
            wet[:, c] = _conv_wrap(hall_in[:, c], ir_h, self.L) * hall[1] + _conv_wrap(room_in[:, c], ir_r, self.L) * room[1]
        x = dry + wet
        x = _circ(lambda z: hp(z, 28, 2), x)
        # normalisation sur le niveau efficace, saturation douce, limiteur circulaire
        x = x / (rms(x) + 1e-9) * dbv(target_rms_db)
        x = sat(x * 0.9, sat_drive) / 0.9 if sat_drive > 1 else x
        pk0 = peak(x)
        x = limiter(x, thr, look=0.004, hold=0.04, circular=True)
        x = x * (dbv(target_peak_db) / peak(x))
        if verbose:
            print(f"  [{self.name}] {self.L/SR:.1f}s pre-limit peak {to_db(pk0):.1f} dBFS | final peak {to_db(peak(x)):.1f} rms {to_db(rms(x)):.1f} dBFS")
            if self.sections:
                for sn, a, b in self.sections:
                    row = {}
                    for nme, bb in self.buses.items():
                        seg = bb[int(self.t_of(a) * SR):int(self.t_of(b + 1) * SR)] * self.cfg[nme]['gain']
                        row[nme] = round(to_db(rms(seg)) if rms(seg) > 0 else -99, 0)
                    print(f"     {sn:8s} bars {a}-{b}:", row)
        return x


def _circ(fn, x):
    """Filtrage causal appliqué de façon circulaire (aucune couture à la jonction de boucle)."""
    L = len(x)
    return fn(np.concatenate([x, x, x]))[L:2 * L]


def _conv_wrap(x, ir, L):
    y = sg.fftconvolve(x, ir)
    out = np.zeros(L)
    k = 0
    while k * L < len(y):
        seg = y[k * L:(k + 1) * L]
        out[:len(seg)] += seg
        k += 1
    return out


# ---------------------------------------------------------------- aides de partition
def bars_range(a, b):
    return list(range(a, b + 1))


def bass_pattern(song, busname, fn, bars, pat, lo=34, hi=50, vel=0.8, gain=1.0, pan_=0.0, **kw):
    """pat : liste (beat, dur, 'r'|'5'|'o'|'3'|'7', vel_mult)."""
    for b in bars:
        ch = song.chord(b)
        r_ = ch.root_in(lo, hi)
        for beat, d, deg, vm in pat:
            if deg == 'r':
                p = r_
            elif deg == 'o':
                p = r_ + 12
            elif deg == '5':
                p = ch.fifth_in(lo, hi + 7)
            elif deg == '3':
                p = [x for x in ch.tones(r_, r_ + 12) if x % 12 == ch.third_pc()][0]
            elif deg == '7':
                p = r_ + 10
            elif deg == 'l':
                p = r_ - 12 if r_ - 12 >= 28 else r_
            else:
                p = r_
            song.note(busname, fn, p, b, beat, d, vel * vm, pan_, gain, **kw)


def arp_pattern(song, busname, fn, bars, steps, step_beats=0.5, lo=52, n_oct=2, vel=0.6, gain=1.0, pan_=0.0,
                dur_mult=1.1, from_root=False, accent=(1.0, 0.65, 0.8, 0.65), **kw):
    """steps : indices dans les notes d'accord montantes (cyclique, un par pas).
    from_root : la 1re note montante est la fondamentale (cherchée entre lo et lo+11)."""
    for b in bars:
        ch = song.chord(b)
        base = ch.root_in(lo, lo + 11) if from_root else lo
        tones = [p for p in range(base, base + 12 * n_oct + 1) if p % 12 in ch.pcs]
        nb = int(round(song.bpb / step_beats))
        for i in range(nb):
            idx = steps[i % len(steps)]
            p = tones[idx % len(tones)] + 12 * (idx // len(tones))
            v = vel * accent[i % len(accent)]
            song.note(busname, fn, p, b, i * step_beats, step_beats * dur_mult, v, pan_ * (1 if i % 2 else -1), gain, **kw)


def ostinato(song, busname, fn, bars, pat, lo=36, hi=52, vel=0.8, gain=1.0, pan_=0.0, **kw):
    """pat : liste (beat, dur, intervalle_depuis_fondamentale, vel_mult) ; l'intervalle peut être négatif."""
    for b in bars:
        ch = song.chord(b)
        r_ = ch.root_in(lo, hi)
        for beat, d, iv, vm in pat:
            song.note(busname, fn, r_ + iv, b, beat, d, vel * vm, pan_, gain, **kw)
