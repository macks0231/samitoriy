# -*- coding: utf-8 -*-
"""Samitorio v0.3 - day/night lighting with soft glow."""
import math

import pygame

import core
import tex
from entities import Building


class Lighting:
    def __init__(self):
        self.ov = pygame.Surface((core.SW, core.SH), pygame.SRCALPHA)

    def draw(self, screen, is_day, prog, g):
        if is_day:
            if 0.12 <= prog <= 0.88:
                dark = 0
            else:
                dark = int(150 * min(1, (0.12 - prog) / 0.12)) if prog < 0.12 \
                    else int(150 * ((prog - 0.88) / 0.12))
        else:
            dark = 170 if 0.12 <= prog <= 0.88 else \
                int(170 * (prog / 0.12)) if prog < 0.12 else int(170 * (1 - (prog - 0.88) / 0.12))
        if dark <= 0:
            return
        self.ov.fill((0, 0, 26, dark))
        self._light(int(g.player.x - g.cam.ox), int(g.player.y - g.cam.oy), 150, dark)
        for (tx, ty), c in g.ent.occ.items():
            if isinstance(c, Building) and c.emits_light and c.x == tx and c.y == ty:
                self._light(int(c.x * core.TILE + c.w * core.TILE / 2 - g.cam.ox),
                            int(c.y * core.TILE + c.h * core.TILE / 2 - g.cam.oy),
                            c.light_r, dark)
        screen.blit(self.ov, (0, 0))

    def _light(self, cx, cy, r, dark):
        for i in range(6, 0, -1):
            rr = int(r * i / 6)
            a = int(min(255, dark * (1 - (i / 6) ** 0.6) * 1.6))
            pygame.draw.circle(self.ov, (0, 0, 0, a), (cx, cy), rr)