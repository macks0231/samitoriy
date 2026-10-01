# -*- coding: utf-8 -*-
"""Samitorio v0.35 - player: movement (slides past rocks), full-body animation."""
import math

import pygame

import core
import snd
import tex
from core import TILE


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.hp = 100
        self.max_hp = 100
        self.speed = 190
        self.dir = 0.0
        self.mine_tgt = None
        self.mine_prog = 0.0
        self.moving = False
        self.step = 0.0
        self.build_mode = False
        self._hit_t = 0.0

    # ── collision ────────────────────────────────────────────────
    def _hit(self, g, px, py, r):
        t0x = int((px - r) // TILE)
        t1x = int((px + r) // TILE)
        t0y = int((py - r) // TILE)
        t1y = int((py + r) // TILE)
        for ty in range(t0y, t1y + 1):
            for tx in range(t0x, t1x + 1):
                t = g.world.get(tx, ty)
                if t is not None and t.rock:
                    return True
        return False

    def _slide(self, g, nx, ny):
        r = 7.0
        x, y = nx, ny
        if self._hit(g, x, self.y, r):
            x = self.x
        if self._hit(g, x, y, r):
            y = self.y
        return x, y

    def update(self, keys, g, dt):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
        self.moving = bool(dx or dy)
        if self.moving:
            ln = math.sqrt(dx * dx + dy * dy)
            dx /= ln
            dy /= ln
            self.dir = math.degrees(math.atan2(dy, dx))
            self.step += dt * 10
        nx = max(18, min(g.world.W * TILE - 18, self.x + dx * self.speed * dt))
        ny = max(18, min(g.world.H * TILE - 18, self.y + dy * self.speed * dt))
        self.x, self.y = self._slide(g, nx, ny)
        if self._hit_t > 0:
            self._hit_t -= dt
        # manual mining
        if pygame.mouse.get_pressed()[0] and not self.build_mode:
            mx, my = pygame.mouse.get_pos()
            tx = int((mx + g.cam.ox) // TILE)
            ty = int((my + g.cam.oy) // TILE)
            ptx = int(self.x // TILE)
            pty = int(self.y // TILE)
            if math.hypot(tx - ptx, ty - pty) <= 5:
                tile = g.world.get(tx, ty)
                if tile and tile.resource and tile.amount > 0:
                    if self.mine_tgt == (tx, ty):
                        self.mine_prog += dt
                        if self.mine_prog >= 0.35:
                            n = min(2, tile.amount)
                            tile.amount -= n
                            g.inv.add(tile.resource, n)
                            snd.play("mine")
                            self.mine_prog = 0.0
                            if tile.amount <= 0:
                                tile.resource = None
                                self.mine_tgt = None
                    else:
                        self.mine_tgt = (tx, ty)
                        self.mine_prog = 0.0
                else:
                    self.mine_tgt = None
            else:
                self.mine_tgt = None
        else:
            self.mine_tgt = None

    def draw(self, screen, g, is_day):
        sx = int(self.x - g.cam.ox)
        sy = int(self.y - g.cam.oy)
        t = g.t
        a = math.radians(self.dir)
        fa = math.cos(a)
        fb = math.sin(a)
        # shadow
        pygame.draw.ellipse(screen, (0, 0, 0),
                            (sx - 11, sy + 8, 22, 7))
        bob = abs(math.sin(self.step)) * 2.2 if self.moving else 0
        sy -= bob
        swing = math.sin(self.step) * (0.7 if self.moving else 0)
        # ── legs (trousers + boots, alternating gait) ──
        for sgn in (-1, 1):
            hip = sy + 8
            foot_off = swing * 5 * sgn
            fx = sx + sgn * 5 + foot_off * fa
            fy = hip + (6 if self.moving else 4)
            pygame.draw.line(screen, (48, 52, 66),
                             (sx + sgn * 5, hip - 4),
                             (int(fx), int(fy)), 4)
            pygame.draw.circle(screen, (30, 32, 44),
                               (int(fx + fa * 2), int(fy + fb * 2)), 3)
        # ── backpack ──
        pygame.draw.rect(screen, (150, 120, 40),
                         (sx - 9, sy - 12, 18, 16), border_radius=3)
        pygame.draw.rect(screen, (110, 86, 30),
                         (sx - 9, sy - 12, 18, 16), 1, border_radius=3)
        pygame.draw.line(screen, (200, 180, 110), (sx - 5, sy - 10), (sx + 5, sy - 10), 1)
        # ── torso (engineer suit) ──
        tw = 20 - int(abs(fa) * 4)
        pygame.draw.rect(screen, (42, 86, 130),
                         (sx - tw // 2, sy - 8, tw, 16), border_radius=6)
        pygame.draw.rect(screen, (30, 62, 96),
                         (sx - tw // 2, sy - 8, tw, 16), 1, border_radius=6)
        # orange harness
        pygame.draw.line(screen, (230, 130, 40),
                         (sx - tw // 2 + 2, sy - 6), (sx + tw // 2 - 2, sy + 2), 2)
        pygame.draw.line(screen, (230, 130, 40),
                         (sx - tw // 2 + 2, sy + 2), (sx + tw // 2 - 2, sy - 6), 2)
        pygame.draw.rect(screen, (230, 130, 40), (sx - 2, sy - 4, 4, 4), border_radius=1)
        # ── arms (swing opposite to legs; tool in right hand) ──
        a_swing = -swing
        for sgn, swat in ((-1, a_swing), (1, -a_swing)):
            shx = sx + sgn * 7
            shy = sy - 4
            ex = shx + swat * 5 * fa - 2 * fa
            ey = shy + 6 - swat * 5 * fb
            pygame.draw.line(screen, (36, 70, 104),
                             (int(shx), int(shy)), (int(ex), int(ey)), 3)
            pygame.draw.circle(screen, (222, 178, 146), (int(ex), int(ey)), 2)
        # tool in right hand
        if self.mine_tgt and self.mine_prog >= 0:
            self._draw_pick(screen, sx - 1, sy + 2, g)
        elif self.build_mode:
            ph = (t * 3) % 1.0
            bx = sx + 10 + int(math.sin(ph * 6.28) * 4)
            by = sy + 4 - ph * 6
            pygame.draw.line(screen, (150, 120, 60), (sx + 7, sy + 1), (bx, by), 2)
            pygame.draw.rect(screen, (180, 220, 180), (bx - 2, by - 5, 5, 5))
        # ── head + helmet ──
        hx = sx + int(fa * 2)
        hy = sy - 16 + int(fb * 2)
        pygame.draw.circle(screen, (222, 178, 146), (hx, hy), 6)
        # helmet (yellow hard hat with brim)
        pygame.draw.circle(screen, (235, 156, 50), (hx, hy), 7)
        pygame.draw.arc(screen, (205, 128, 34), (hx - 7, hy - 8, 14, 14),
                        a + 2.6, a - 2.6, 2)
        pygame.draw.circle(screen, (200, 120, 30), (hx, hy - 2), 2)
        # eyes toward facing
        for sgn in (-1, 1):
            ex = hx + int(fa * 3 + fa * sgn * 4 - fb * sgn * 2)
            ey = hy + int(fb * 3 + fb * sgn * 4 + fa * sgn * 2)
            pygame.draw.circle(screen, (30, 30, 40), (ex, ey), 1)
        # helmet lamp
        if not is_day:
            fl = tex.pulse(t * 4, 1)
            pygame.draw.circle(screen,
                               (120 + int(120 * fl), 230, 255),
                               (hx + int(fa * 8), hy + int(fb * 8)), 3)
            glow = tex.disc("pglow", 18, (140, 230, 255))
            glow.set_alpha(int(70 * (0.5 + 0.5 * fl)))
            screen.blit(glow, (hx + int(fa * 8) - 18, hy + int(fb * 8) - 18))
        # hit flash
        if self._hit_t > 0:
            limb = pygame.Surface((24, 30), pygame.SRCALPHA)
            limb.fill((255, 255, 255, 70))
            screen.blit(limb, (sx - 12, sy - 20))
        # hp bar
        r = self.hp / self.max_hp
        pygame.draw.rect(screen, (150, 0, 0), (sx - 17, sy - 30, 34, 5))
        pygame.draw.rect(screen, (0, 200, 60), (sx - 17, sy - 30, int(34 * r), 5))
        pygame.draw.rect(screen, (255, 255, 255), (sx - 17, sy - 30, 34, 5), 1)
        if self.mine_tgt:
            pygame.draw.rect(screen, (255, 200, 0),
                             (sx - 15, sy - 38, int(30 * self.mine_prog), 3))

    def _draw_pick(self, screen, sx, sy, g):
        t = g.t
        # pick swings with a chopping motion
        base = math.radians(-70 + 80 * abs(math.sin(t * 5)))
        handle_len = 14
        hx = sx + math.cos(base) * handle_len
        hy = sy + math.sin(base) * handle_len
        pygame.draw.line(screen, (120, 90, 50), (sx, sy), (hx, hy), 3)
        # iron head
        px = hx + math.cos(base + 1.2) * 6
        py = hy + math.sin(base + 1.2) * 6
        pygame.draw.line(screen, (150, 150, 160), (hx, hy), (px, py), 2)