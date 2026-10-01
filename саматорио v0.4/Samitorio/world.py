# -*- coding: utf-8 -*-
"""Samitorio v0.3 - world: biomes, tiles, resources, pollution."""
import math
import random

import pygame

import core
import tex


class Tile:
    __slots__ = ["biome", "resource", "amount", "rock", "cell", "pollution"]

    def __init__(self, biome, res=None, rock=False):
        self.biome = biome
        self.resource = res
        self.amount = random.randint(300, 3000) if res else 0
        self.rock = rock
        self.cell = None
        self.pollution = 0.0


class World:
    def __init__(self, W=192, H=192, seed=12345):
        self.W, self.H = W, H
        self.spawn_x = W * core.TILE // 2
        self.spawn_y = H * core.TILE // 2
        self.tiles = []
        random.seed(seed)
        for y in range(H):
            row = []
            for x in range(W):
                b = self._biome(x, y)
                pool = core.BIOME_RES[b]
                res = random.choices(pool, [3, 2, 1, 1][:len(pool)])[0] \
                    if random.random() < 0.055 else None
                rock = self._rock(x, y, b, res)
                row.append(Tile(b, res, rock))
            self.tiles.append(row)

    def _rock(self, x, y, biome, res):
        if res is not None:
            return False
        cx, cy = self.W // 2, self.H // 2
        if math.hypot(x - cx, y - cy) < 7:
            return False
        v = self._smooth(x, y, 77, 22)
        n2 = self._noise(x, y, 313)
        more = biome in (core.BIOME_RIDGE, core.BIOME_WASTELAND, core.BIOME_BARREN, core.BIOME_ASHLANDS)
        thr = 0.68 if more else 0.78
        return v > thr and n2 > 0.2

    def _noise(self, x, y, s):
        p = x + y * 57 + s * 131
        p = (p << 13) ^ p
        return 1.0 - ((p * (p * p * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0

    def _smooth(self, x, y, s, sc=40):
        fx, fy = x / sc, y / sc
        ix, iy = int(fx), int(fy)
        rx, ry = fx - ix, fy - iy
        v = lambda a, b: self._noise(a, b, s)
        return (v(ix, iy) * (1 - rx) + v(ix + 1, iy) * rx) * (1 - ry) + \
               (v(ix, iy + 1) * (1 - rx) + v(ix + 1, iy + 1) * rx) * ry

    def _biome(self, x, y):
        v = (self._smooth(x, y, 42, 40) + self._smooth(x, y, 137, 30)) / 2
        cx, cy = self.W // 2, self.H // 2
        if math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / (self.W // 2) < 0.15:
            return core.BIOME_PLAINS
        if v > 0.40: return core.BIOME_RIDGE
        if v > 0.20: return core.BIOME_THICKET
        if v > 0.00: return core.BIOME_PLAINS
        if v > -0.15: return core.BIOME_ASHLANDS
        if v > -0.30: return core.BIOME_SWAMP
        if v > -0.45: return core.BIOME_BARREN
        if v > -0.60: return core.BIOME_WASTELAND
        return core.BIOME_PERMAFROST

    def inb(self, tx, ty):
        return 0 <= tx < self.W and 0 <= ty < self.H

    def get(self, tx, ty):
        if self.inb(tx, ty):
            return self.tiles[ty][tx]
        return None

    def cell_at(self, tx, ty):
        t = self.get(tx, ty)
        return t.cell if t else None

    def spread_pollution(self):
        T = self.tiles
        for y in range(1, self.H - 1):
            for x in range(1, self.W - 1):
                t = T[y][x]
                if t.pollution > 0.1:
                    sp = t.pollution * 0.002
                    T[y - 1][x].pollution += sp
                    T[y + 1][x].pollution += sp
                    T[y][x - 1].pollution += sp
                    T[y][x + 1].pollution += sp
                    if t.biome in (core.BIOME_THICKET, core.BIOME_PLAINS):
                        t.pollution = max(0, t.pollution - 0.05)

    def draw(self, screen, cam):
        x0 = max(0, int(cam.ox // core.TILE))
        y0 = max(0, int(cam.oy // core.TILE))
        x1 = min(self.W, x0 + core.SW // core.TILE + 2)
        y1 = min(self.H, y0 + core.SH // core.TILE + 2)
        t_now = pygame.time.get_ticks() / 1000.0
        for ty in range(y0, y1):
            for tx in range(x0, x1):
                t = self.tiles[ty][tx]
                px = tx * core.TILE - int(cam.ox)
                py = ty * core.TILE - int(cam.oy)
                surf = tex.tile_tex(t.biome, tx, ty)
                if t.pollution >= 2.0:
                    p = min(1, t.pollution / 120)
                    tmp = surf.copy()
                    sh = pygame.Surface((core.TILE, core.TILE))
                    sh.fill((55, 75, 15))
                    sh.set_alpha(int(200 * p))
                    tmp.blit(sh, (0, 0))
                    screen.blit(tmp, (px, py))
                else:
                    screen.blit(surf, (px, py))
                self._decor(screen, t, tx, ty, px, py, t_now)
                if t.rock:
                    self._draw_rock(screen, t, tx, ty, px, py)
                if t.resource and t.amount > 0:
                    self._draw_res(screen, t, tx, ty, px, py)

    def _decor(self, screen, t, tx, ty, px, py, t_now):
        if t.rock or t.resource or t.cell:
            return
        b = t.biome
        h = tex.n(tx * 3, ty * 7, 555)
        if b in (core.BIOME_PLAINS, core.BIOME_THICKET):
            # grass tufts
            if h > 0.45:
                n2 = tex.n(px, ty, 901)
                for i in range(3):
                    gx = px + int(tex.n(tx * i + 7, ty * i + 3, 777) * core.TILE)
                    gy = py + core.TILE - 2 - int(tex.n(tx * i + 5, ty * i, 888) * 4)
                    lean = math.sin(t_now * 3 + tx + ty + i) * 2
                    pygame.draw.line(screen, (38, 96, 30),
                                     (gx - lean, gy), (gx, gy - (3 + int(h * 6))), 1)
            # occasional swaying tree
            if h > 0.96:
                tr = 14 if b == core.BIOME_THICKET else 11
                sway = math.sin(t_now * 1.6 + tx * 1.7 + ty * 2.3) * 2
                base = px + 16 + int(sway * 0.6)
                pygame.draw.rect(screen, (70, 52, 30), (base - 1, py + 24, 4, 8))
                pygame.draw.circle(screen, (24, 74, 24),
                                   (base + int(sway), py + 22 - tr // 2), tr)
                pygame.draw.circle(screen, (38, 96, 30),
                                   (base - 4 + int(sway * 1.3), py + 26 - tr // 2), tr - 3)
                pygame.draw.circle(screen, (40, 104, 32),
                                   (base + 4 + int(sway * 0.8), py + 24 - tr // 2 + 2), tr - 4)
            elif h > 0.88 and b == core.BIOME_THICKET:
                pygame.draw.rect(screen, (24, 90, 24), (px + 6, py + 18, 20, 10))
                pygame.draw.rect(screen, (20, 74, 20), (px + 6, py + 18, 4, 10))
        elif b == core.BIOME_ASHLANDS:
            pass  # texture already rich

    def _draw_rock(self, screen, t, tx, ty, px, py):
        v = int(tex.n(tx, ty, 400) * 5.99)
        screen.blit(tex.rock_tex(v), (px, py))
        # debris around base
        for i in range(2):
            dx = int(tex.n(tx * i + 11, ty * i + 5, 202) * core.TILE)
            dy = py + core.TILE - 3 - int(tex.n(tx * i + 3, ty * i, 303) * 2)
            col = (70, 66, 62)
            pygame.draw.rect(screen, col, (px + dx - 2, dy, 5, 3))
            pygame.draw.rect(screen, (40, 38, 36), (px + dx - 2, dy, 5, 1))

    def _draw_res(self, screen, t, tx, ty, px, py):
        amt = t.amount
        s = min(1.0, 0.4 + amt / 3000.0)
        v = tex.n(tx * 2, ty * 3, 1300)
        img = tex.ore_tex(t.resource, int(v * 7.99))
        side = int(img.get_width() * s)
        if side < 8:
            return
        img = pygame.transform.smoothscale(img, (side, side))
        screen.blit(img, (px + core.TILE // 2 - side // 2,
                          py + core.TILE // 2 - side // 2))
        # sparkle animation on rich nodes
        if amt > 800:
            f = tex.pulse(pygame.time.get_ticks() / 1000.0, 2.0)
            cx = px + core.TILE // 2 + int(f * 7) - 3
            cy = py + core.TILE // 2 + int(f * 5) - 2
            pygame.draw.circle(screen, (255, 255, 220), (cx, cy), 1)