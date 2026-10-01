# -*- coding: utf-8 -*-
"""Samitorio v0.4 - procedural audio (no external asset files)."""
import array
import math
import struct

import pygame

SR = 22050
_ok = False
_mixer = None

_sounds = {}
_music_sound = None
_music_playing = False
_sfx_vol = 0.7
_music_vol = 0.45
_sfx_on = True
_music_on = True


def _env(i, total):
    """smooth attack/release envelope, 0..1"""
    n = max(1, total)
    a = int(n * 0.02)
    r = int(n * 0.25)
    if i < a:
        return i / a
    if i > n - r:
        return max(0.0, (n - i) / r)
    return 1.0


def _tone(freq, dur, wave="sine", amp=0.4):
    n = int(SR * dur)
    out = array.array("h", [0]) * n
    for i in range(n):
        t = i / SR
        ph = 2 * math.pi * freq * t
        if wave == "sine":
            v = math.sin(ph)
        elif wave == "saw":
            v = 2 * ((freq * t) % 1.0) - 1.0
        elif wave == "square":
            v = 1.0 if math.sin(ph) >= 0 else -1.0
        else:  # triangle
            v = 2 * abs(2 * ((freq * t) % 1.0) - 1.0) - 1.0
        out[i] = int(max(-1.0, min(1.0, v * amp * _env(i, n))) * 32000)
    return out


def _sweep(f0, f1, dur, amp=0.35):
    n = int(SR * dur)
    out = array.array("h", [0]) * n
    for i in range(n):
        t = i / SR
        f = f0 + (f1 - f0) * (i / n)
        ph = (2 * math.pi * (f0 * t + (f1 - f0) * t * t / (2 * dur))) % (2 * math.pi)
        v = math.sin(ph)
        out[i] = int(max(-1.0, min(1.0, v * amp * _env(i, n))) * 32000)
    return out


def _noise(dur, amp=0.3, seed=12345):
    n = int(SR * dur)
    out = array.array("h", [0]) * n
    state = seed
    for i in range(n):
        state = (state * 1664525 + 1013904223) & 0xFFFFFFFF
        v = ((state >> 8) / 16777215.0) * 2 - 1
        out[i] = int(max(-1.0, min(1.0, v * amp * _env(i, n))) * 32000)
    return out


def _mix(*parts):
    maxn = max(len(p) for p in parts)
    out = array.array("h", [0]) * maxn
    for p in parts:
        for i in range(len(p)):
            out[i] = int(max(-1.0, min(1.0, out[i] / 32000 + p[i] / 32000)) * 32000)
    return out


def _append(*parts):
    n = sum(len(p) for p in parts)
    out = array.array("h", [0]) * n
    off = 0
    for p in parts:
        for i in range(len(p)):
            out[off + i] = p[i]
        off += len(p)
    return out


def _make(samples):
    return pygame.mixer.Sound(buffer=samples.tobytes())


def init():
    global _ok, _mixer, _sounds, _music_sound
    _mixer = pygame.mixer.get_init()
    try:
        pygame.mixer.init(SR, -16, 1, 512)
    except Exception:
        _mixer = None
    if pygame.mixer.get_init() is None:
        _ok = False
        return
    _ok = True
    _sounds = {
        "click": _make(_tone(1000, 0.06, "sine", 0.35)),
        "build": _make(_sweep(300, 750, 0.13, 0.4)),
        "deny": _make(_tone(150, 0.18, "square", 0.3)),
        "mine": _make(_tone(240, 0.07, "triangle", 0.4)),
        "pickup": _make(_append(_tone(660, 0.09, "sine", 0.35),
                                _tone(880, 0.13, "sine", 0.35))),
        "shoot": _make(_tone(150, 0.09, "saw", 0.35)),
        "laser": _make(_sweep(1200, 400, 0.11, 0.35)),
        "hit": _make(_mix(_tone(520, 0.07, "square", 0.3),
                          _tone(690, 0.07, "square", 0.25))),
        "explode": _make(_mix(_tone(90, 0.32, "sine", 0.5),
                              _noise(0.3, 0.28))),
        "research": _make(_append(_tone(523, 0.1, "sine", 0.3),
                                  _tone(659, 0.1, "sine", 0.3),
                                  _tone(784, 0.18, "sine", 0.32))),
        "wave": _make(_append(_tone(400, 0.18, "square", 0.3),
                              _tone(320, 0.22, "square", 0.3))),
        "menu_move": _make(_tone(700, 0.04, "sine", 0.3)),
        "menu_select": _make(_tone(880, 0.09, "sine", 0.35)),
    }
    _music_sound = _make(_music_pad())


def _music_pad():
    # 12-second ambient loop: C - Am - F - G, soft sine pad.
    chords = [
        (130.81, 196.00, 329.63),
        (110.00, 164.81, 261.63),
        (87.31, 130.81, 220.00),
        (98.00, 146.83, 246.94),
    ]
    seg = int(SR * 3.0)
    n = seg * 4
    out = array.array("h", [0]) * n
    for ci, chord in enumerate(chords):
        base = ci * seg
        for k in range(seg):
            i = base + k
            t = k / seg
            env = math.sin(math.pi * min(1.0, t * 1.5)) * (1 - 0.35 * (t > 0.5))
            v = 0.0
            for si, f in enumerate(chord):
                det = f * (1.0 + (si - 1) * 0.0016)
                env2 = min(1.0, (1 - t) * 2.2)
                v += math.sin(2 * math.pi * det * t) * 0.09 * env2
            out[i] = int(max(-1.0, min(1.0, v * env * 0.85)) * 32000)
    return out


def apply(settings):
    global _sfx_vol, _music_vol, _sfx_on, _music_on
    _sfx_on = bool(settings.get("sound"))
    _music_on = bool(settings.get("music"))
    _sfx_vol = float(settings.get("sfx_vol") or 0.0)
    _music_vol = float(settings.get("music_vol") or 0.0)
    if _music_on:
        music_play()
    else:
        music_stop()


def play(name):
    if not _ok or not _sfx_on:
        return
    s = _sounds.get(name)
    if s is None:
        return
    s.set_volume(_sfx_vol)
    s.play()


def music_play():
    global _music_playing
    if not _ok or not _music_on or _music_playing:
        return
    _music_sound.set_volume(_music_vol)
    _music_sound.play(loops=-1, fade_ms=800)
    _music_playing = True


def music_stop():
    global _music_playing
    if not _ok:
        _music_playing = False
        return
    if _music_playing:
        _music_sound.fadeout(500)
    _music_playing = False


def shutdown():
    if _ok:
        try:
            pygame.mixer.stop()
        except Exception:
            pass