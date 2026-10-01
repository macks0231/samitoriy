# -*- coding: utf-8 -*-
"""Samitorio v0.3 - procedural textures + animation helpers."""
import math
import random
import pygame

from core import TILE, BIOME_BASE, icol, iname

_cache = {}


def n(x, y, s):
    """Deterministic hash noise in 0..1."""
    p = x * 374761393 + y * 668265263 + s * 1442695040888963407
    p = (p ^ (p >> 13)) * 1274126177
    return ((p ^ (p >> 16)) & 0x7fffffff) / 0x7fffffff


def jitter(surf, seed, amt):
    w, h = surf.get_size()
    for y in range(h):
        for x in range(w):
            v = (n(x, y, seed) - 0.5) * 2 * amt
            r, g, b, *a = surf.get_at((x, y))
            surf.set_at((x, y), (max(0, min(255, int(r + v))),
                                 max(0, min(255, int(g + v))),
                                 max(0, min(255, int(b + v))), 255))


def _dotted(surf, seed, col, count):
    w, h = surf.get_size()
    for i in range(count):
        x = int(n(i, seed, 7) * w)
        y = int(n(i, seed, 11) * h)
        pygame.draw.rect(surf, col, (x, y, 1 + int(n(i, seed, 3) * 2), 1))


def tile_tex(biome, tx=0, ty=0):
    key = "tile_%d_%d_%d" % (biome, tx, ty)
    if key in _cache:
        return _cache[key]
    surf = pygame.Surface((TILE, TILE))
    base = BIOME_BASE[biome]
    surf.fill(base)
    jitter(surf, 1000 + biome * 77 + (tx * 31 + ty * 17) % 997, 16)
    _dotted(surf, 1001 + biome * 77 + (tx * 13 + ty * 7) % 991,
            tuple(min(255, c + 20) for c in base), 14)
    _dotted(surf, 1002 + biome * 77 + (tx * 7 + ty * 13) % 977,
            tuple(max(0, c - 22) for c in base), 12)
    _biome_detail(surf, biome, tx, ty)
    _cache[key] = surf
    return surf


def _biome_detail(surf, biome, tx, ty):
    W, H = surf.get_size()
    if biome == 0 or biome == 6:  # plains / thicket - grass blades
        for i in range(26):
            x = int(n(tx * 9 + i * 3, 1, 31) * W)
            y = int(n(tx * 5 + i * 7, 2, 32) * H)
            ln = 2 + int(n(tx + i, 3, 33) * 3)
            ang = -1.2 + n(i, 4, 34) * 0.5
            cw = 22 + int(n(i * 3, 5, 35) * 22)
            pygame.draw.line(surf, (0, min(200, cw + 40), max(18, cw - 24)),
                             (x, y), (x + int(math.sin(ang) * ln), y - ln),
                             1 + int(n(i, 6, 36) * 1))
        if biome == 0 and n(tx, ty, 41) > 0.8:
            for i in range(6):
                fx = int(n(tx * 7 + i * 11, ty * 3, 42) * W)
                fy = int(n(tx * 3 + i, ty * 5, 43) * H)
                col = (235, 228, 150) if i % 2 else (220, 235, 255)
                surf.set_at((fx, fy), col)
    elif biome == 1:  # ashlands - ash lumps
        for i in range(18):
            x = int(n(tx * 7 + i * 3, ty * 13, 51) * W)
            y = int(n(tx * 11 + i * 5, ty, 52) * H)
            sh = 1 + int(n(i, 9, 53) * 4)
            pygame.draw.circle(surf, (96, 92, 88), (x, y), sh)
        pygame.draw.line(surf, (120, 114, 106), (2, int(H * 0.35)), (W - 2, int(H * 0.45)), 1)
    elif biome == 2:  # swamp - moss + dark water spots
        _clump(surf, (16, 62, 40), 14, tx, ty, 61)
        _clump(surf, (30, 96, 34), 10, tx, ty, 62)
    elif biome == 3:  # wasteland - rubble
        _clump(surf, (90, 86, 78), 12, tx, ty, 71)
        for i in range(8):
            x = int(n(tx * 3 + i, ty * 5, 72) * W)
            y = int(n(tx + i * 2, ty * 9, 73) * H)
            pygame.draw.rect(surf, (108, 102, 92), (x, y, 3, 2))
    elif biome == 4:  # permafrost - snow sparkle
        for i in range(20):
            x = int(n(tx * 5 + i * 3, ty * 7, 81) * W)
            y = int(n(tx * 9 + i, ty * 2, 82) * H)
            sh = 1 + int(n(i * 5, 13, 83) * 2)
            pygame.draw.circle(surf, (200, 224, 240), (x, y), sh)
    elif biome == 5:  # barren - cracked dry soil
        for i in range(6):
            x = int(n(tx * 3 + i, ty * 5, 91) * W)
            y = int(n(tx * 7 + i * 2, ty, 92) * H)
            pygame.draw.line(surf, (168, 146, 96),
                             (x, y), (x + int(n(i, 2, 93) * 8) - 4, y + 3), 1)
    elif biome == 7:  # ridge - stone fragments
        _clump(surf, (120, 114, 108), 12, tx, ty, 101)
        for i in range(8):
            x = int(n(tx * 5 + i * 3, ty * 3, 102) * W)
            y = int(n(tx * 9 + i, ty * 7, 103) * H)
            pygame.draw.polygon(surf, (132, 126, 118),
                                [(x, y), (x + 3, y + 2), (x + 1, y + 4), (x - 2, y + 3)])


def _clump(surf, col, count, tx, ty, seed):
    W, H = surf.get_size()
    for i in range(count):
        x = int(n(tx * 7 + i * 3, ty * 13 + i, seed) * W)
        y = int(n(tx * 11 + i * 5, ty * 3, seed + 1) * H)
        sh = 1 + int(n(i, i * 3, seed + 2) * 3)
        pygame.draw.circle(surf, col, (x, y), sh)


def ore_tex(res, variant):
    key = "ore_%s_%d" % (res, variant)
    if key in _cache:
        return _cache[key]
    base = icol(res)
    dark = tuple(max(0, v - 50) for v in base)
    hi = tuple(min(255, v + 42) for v in base)
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    for i in range(5):
        ang = (variant + i) * 1.9
        cx = 16 + int(math.cos(ang) * (6 + (i % 2) * 4))
        cy = 16 + int(math.sin(ang * 1.3) * (5 + (i % 3) * 4))
        r = 4 + int(n(variant * 3 + i, i * 2 + 1, 501) * 4)
        # shadow facet
        pygame.draw.polygon(surf, dark, _poly(cx, cy, r, ang + 0.0, 5))
        pygame.draw.polygon(surf, base, _poly(cx, cy, r, ang + 0.7, 5))
        pygame.draw.polygon(surf, hi, _poly(cx, cy, r, ang + 2.4, 5))
        pygame.draw.polygon(surf, (0, 0, 0, 90), _poly(cx, cy, r, 0.0, 5), 1)
    _cache[key] = surf
    return surf


def _poly(cx, cy, r, a0, n):
    pts = []
    for i in range(n):
        a = a0 + i * (6.283 / n)
        rr = r * (0.7 + 0.5 * (((i * 37) % 10) / 10.0))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return pts


def rock_tex(variant):
    key = "rock_%d" % variant
    if key in _cache:
        return _cache[key]
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    cx, cy = TILE // 2, TILE // 2 - 2
    r = 10 + int(n(variant, 1, 601) * 4)
    base = (98, 92, 86)
    dark = (58, 55, 52)
    hi = (142, 136, 128)
    pts = [_poly(cx, cy, r + int(n(variant, i, 602 + i) * 4) - 2,
                 n(variant, i, 612) * 6.28, 7) for i in range(1)]
    core_pts = pts[0]
    # body
    pygame.draw.polygon(surf, dark, core_pts)
    pygame.draw.polygon(surf, base, core_pts)
    # top light facet
    top = [_poly(cx, cy - 3, r * 0.8, 3.3, 4)]
    pygame.draw.polygon(surf, hi, top[0])
    # cracks
    for i in range(3):
        x1 = int(n(variant * 2 + i, 7, 620 + i) * TILE)
        y1 = int(n(variant * 5 + i, 3, 630 + i) * TILE)
        pygame.draw.line(surf, (40, 38, 36),
                         (x1, y1), (x1 + int(n(i, 1, 640) * 7) - 3, y1 + 4), 1)
    # bottom moss/shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 60), (cx - r, cy + 2, r * 2, r))
    pygame.draw.ellipse(surf, (0, 0, 0, 70), (cx - r - 2, TILE - 5, r * 2 + 4, 5))
    pygame.draw.circle(surf, (60, 56, 52), (cx - r + 2, TILE - 3), 2)
    pygame.draw.circle(surf, (70, 66, 62), (cx + r - 3, TILE - 4), 2)
    pygame.draw.polygon(surf, hi, [(v[0], v[1]) for v in _poly(cx - r + 2, cy + 2, 2, 0, 3)])
    _cache[key] = surf
    return surf


def item_tex(name, size=16):
    key = "item_%s_%d" % (name, size)
    if key in _cache:
        return _cache[key]
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = icol(name)
    pygame.draw.rect(surf, tuple(max(0, v - 30) for v in c), (1, 1, size - 2, size - 2))
    pygame.draw.rect(surf, c, (1, 1, size - 2, size - 2), min(2, size // 6))
    pygame.draw.line(surf, tuple(min(255, v + 40) for v in c), (2, 2), (size - 3, 2), 1)
    pygame.draw.line(surf, tuple(min(255, v + 40) for v in c), (2, 2), (2, size - 3), 1)
    pygame.draw.rect(surf, (0, 0, 0), (0, 0, size, size), 1)
    _cache[key] = surf
    return surf


# ── generic plate builder for buildings (upright look) ──────────
def plate_tex(name, w, h, base, edge=None, deco=None):
    """Cached upright plate with bevel + panel lines + shadow."""
    key = "plate_%s_%dx%d" % (name, w, h)
    if key in _cache:
        return _cache[key]
    bw, bh = w * TILE, h * TILE
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    edge = edge or tuple(max(0, v - 55) for v in base)
    # soft drop shadow under the plate
    for i in range(3):
        pygame.draw.rect(surf, (0, 0, 0, 26), (2 + i, 2 + i, bw - 3 - i, bh - 3 - i))
    pygame.draw.rect(surf, edge, (1, 1, bw - 2, bh - 2))
    pygame.draw.rect(surf, base, (4, 4, bw - 8, bh - 8))
    # vertical sheen gradient
    sheen = pygame.Surface((max(1, bw - 8), max(1, bh - 8)), pygame.SRCALPHA)
    for y in range(sheen.get_height()):
        f = y / max(1, sheen.get_height() - 1)
        a = int(26 * math.sin(f * 3.14159))
        sheen.fill((255, 255, 255, a), (0, y, sheen.get_width(), 1))
    surf.blit(sheen, (4, 4))
    # top-left light, bottom-right shade
    pygame.draw.line(surf, tuple(min(255, v + 42) for v in base),
                     (4, 4), (bw - 5, 4), 2)
    pygame.draw.line(surf, tuple(min(255, v + 42) for v in base),
                     (4, 4), (4, bh - 5), 2)
    pygame.draw.line(surf, tuple(max(0, v - 52) for v in base),
                     (bw - 5, 4), (bw - 5, bh - 5), 2)
    pygame.draw.line(surf, tuple(max(0, v - 52) for v in base),
                     (4, bh - 5), (bw - 5, bh - 5), 2)
    # inner panel line
    pygame.draw.rect(surf, tuple(max(0, v - 34) for v in base),
                     (8, 8, bw - 16, bh - 16), 1)
    if deco is not None:
        deco(surf, bw, bh)
    _cache[key] = surf
    return surf


def rivets(surf, w, h, col=(46, 46, 56)):
    for yy in range(7, h, 12):
        for xx in range(7, w, 12):
            pygame.draw.circle(surf, (16, 16, 20), (xx + 1, yy + 1), 2)
            pygame.draw.circle(surf, col, (xx, yy), 2)


# ── animation helpers ────────────────────────────────────────────
def wave(t, speed=1.0, lo=0.0, hi=1.0):
    return lo + (hi - lo) * (0.5 + 0.5 * math.sin(t * speed))


def pulse(t, speed=1.0):
    return (math.sin(t * speed) + 1) * 0.5


def flicker(t, seed=0):
    return 0.6 + 0.4 * n(int(t * 12), int(seed), 5)


def gradient_h(w, h, c1, c2):
    surf = pygame.Surface((w, h))
    for y in range(h):
        f = y / max(1, h - 1)
        pygame.draw.line(surf, (int(c1[0] + (c2[0] - c1[0]) * f),
                                int(c1[1] + (c2[1] - c1[1]) * f),
                                int(c1[2] + (c2[2] - c1[2]) * f)), (0, y), (w, y))
    return surf


def disc(name, r, col, rim=None):
    """Cached soft-edged disc used for lights / glow."""
    key = "disc_%s_%d" % (name, r)
    if key in _cache:
        return _cache[key]
    surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for rr in range(r, 0, -1):
        a = int(200 * (1 - rr / r))
        pygame.draw.circle(surf, (*col, a), (r, r), rr)
    if rim:
        pygame.draw.circle(surf, (*rim, 255), (r, r), max(2, r // 6))
    _cache[key] = surf
    return surf