# -*- coding: utf-8 -*-
"""Samitorio v0.3 - enemies, waves, turrets, projectiles."""
import math
import random

import pygame

import core
import snd
import tex
from core import TILE, DX, DY, OPP


class Enemy:
    def __init__(self, etype, x, y):
        self.etype = etype
        self.x = float(x)
        self.y = float(y)
        d = core.ENEMY_TYPES[etype]
        self.hp = d["hp"]
        self.max_hp = d["hp"]
        self.spd = d["spd"]
        self.dmg = d["dmg"]
        self.sz = d["sz"]
        self.col = d["col"]
        self.cd = 0.0
        self.fly = etype == "flyer"
        self.hit_t = 0.0

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
                c = g.ent.cell_at(tx, ty)
                if c is not None and c.btype == "wall":
                    return True
        return False

    def update(self, dt, g):
        px, py = g.player.x, g.player.y
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        block = None
        if dist > 1:
            vx = dx / dist
            vy = dy / dist
            r = max(7, self.sz * 0.7)
            if not self.fly:
                nx = self.x + vx * self.spd * dt
                ny = self.y + vy * self.spd * dt
                bx = self._hit(g, nx, self.y, r)
                by = self._hit(g, nx if not bx else self.x, ny, r)
                if bx:
                    nx = self.x
                if by:
                    ny = self.y
                if bx or by:
                    tx = int((self.x + vx * self.spd * dt) // TILE)
                    ty = int((self.y + vy * self.spd * dt) // TILE)
                    c = g.ent.cell_at(tx, ty)
                    if c is not None and c.btype == "wall":
                        block = c
                self.x, self.y = nx, ny
            else:
                self.x += vx * self.spd * dt
                self.y += vy * self.spd * dt
        self.cd -= dt
        # attack
        target = block if block is not None else (g.player if dist < 44 else None)
        if target is not None and self.cd <= 0:
            if block is not None:
                block.hp -= self.dmg
                if block.hp <= 0:
                    g.ent.remove(block)
            else:
                g.player.hp = max(0, g.player.hp - self.dmg)
                if g.combat._hit_cd <= 0:
                    snd.play("hit")
                    g.combat._hit_cd = 0.12
            self.cd = 1.2
        if self.hit_t > 0:
            self.hit_t -= dt

    def draw(self, screen, cam, g):
        sx = int(self.x - cam.ox)
        sy = int(self.y - cam.oy)
        pulse = 0.85 + 0.15 * math.sin(g.t * 4 + self.etype.count(""))
        r = int(self.sz * pulse)
        pygame.draw.circle(screen, (0, 0, 0), (sx, sy + self.sz // 2), self.sz)
        col = self.col if self.hit_t <= 0 else (255, 255, 255)
        pygame.draw.circle(screen, col, (sx, sy), r)
        pygame.draw.circle(screen, (255, 255, 255), (sx, sy), r, 1)
        # menacing eyes
        eye = (200, 20, 20)
        if self.fly:
            pygame.draw.line(screen, (200, 200, 230),
                             (sx - r, sy), (sx + r, sy), 1)
            pygame.draw.line(screen, (200, 200, 230),
                             (sx, sy - r), (sx, sy + r), 1)
        else:
            pygame.draw.circle(screen, eye, (sx - 3, sy - 2), 2)
            pygame.draw.circle(screen, eye, (sx + 3, sy - 2), 2)
        bw = self.sz * 2
        fr = self.hp / self.max_hp
        pygame.draw.rect(screen, (150, 0, 0), (sx - self.sz, sy - self.sz - 6, bw, 4))
        pygame.draw.rect(screen, (0, 220, 0), (sx - self.sz, sy - self.sz - 6, int(bw * fr), 4))


class Projectile:
    def __init__(self, x, y, tgt, spd, dmg, col):
        self.x, self.y = float(x), float(y)
        self.tgt = tgt
        self.spd = spd
        self.dmg = dmg
        self.col = col
        self.hit = False

    def update(self, dt):
        if self.tgt is None or self.tgt.hp <= 0:
            self.hit = True
            return
        dx = self.tgt.x - self.x
        dy = self.tgt.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.tgt.sz:
            self.tgt.hp -= self.dmg
            self.tgt.hit_t = 0.15
            self.hit = True
            return
        self.x += dx / dist * self.spd * dt
        self.y += dy / dist * self.spd * dt

    def draw(self, screen, cam):
        sx = int(self.x - cam.ox)
        sy = int(self.y - cam.oy)
        pygame.draw.circle(screen, self.col, (sx, sy), 3)
        pygame.draw.circle(screen, (255, 255, 255), (sx, sy), 3, 1)


class Combat:
    def __init__(self, world, player):
        self.world = world
        self.player = player
        self.enemies = []
        self.projectiles = []
        self.wave_num = 0
        self.wave_active = False
        self.time_to_next = 90.0
        self.interval = 90.0
        self.evolution = 0.0
        self.night_bonus = False
        self.turrets = set()
        self._sfx_cd = 0.0
        self._hit_cd = 0.0

    def _spawn(self):
        self.wave_num += 1
        self.wave_active = True
        snd.play("wave")
        count = 4 + int(self.wave_num * 2 + self.evolution * 16)
        if self.night_bonus:
            count = int(count * 1.5)
            self.night_bonus = False
        WPW = self.world.W * TILE
        WPH = self.world.H * TILE
        for _ in range(count):
            s = random.randint(0, 3)
            if s == 0:
                x, y = random.randint(0, WPW), 10
            elif s == 1:
                x, y = random.randint(0, WPW), WPH - 10
            elif s == 2:
                x, y = 10, random.randint(0, WPH)
            else:
                x, y = WPW - 10, random.randint(0, WPH)
            ev = self.evolution
            if ev < 0.2:
                et = random.choice(["small", "small", "medium"])
            elif ev < 0.5:
                et = random.choice(["small", "medium", "armored", "flyer"])
            else:
                et = random.choice(["medium", "armored", "flyer", "boss"])
            self.enemies.append(Enemy(et, x, y))

    def _turrets(self, g):
        out = []
        seen = set()
        for (tx, ty), c in g.ent.occ.items():
            if c in seen:
                continue
            seen.add(c)
            if c.btype in ("gun-turret", "laser-turret"):
                out.append(c)
        return out

    def update_turrets(self, dt, g):
        for t in self._turrets(g):
            t.aim = None
        shots = 0
        laser = False
        for e in self.enemies:
            if e.hp <= 0:
                continue
            ex = e.x
            ey = e.y
            best = None
            for t in self._turrets(g):
                cx = t.x * TILE + t.w * TILE / 2
                cy = t.y * TILE + t.h * TILE / 2
                d = math.hypot(ex - cx, ey - cy)
                if d < 150:
                    ammo = (t.btype == "gun-turret" and t.buf.get("firearm-magazine", 0) > 0)
                    power_ok = (t.btype == "laser-turret" and g.power.sat >= 0.5)
                    if ammo or power_ok:
                        t.aim = (ex, ey)
                        t.recoil = 1.0
                        if t.btype == "gun-turret":
                            t.buf["firearm-magazine"] -= 1
                            self.projectiles.append(Projectile(cx, cy, e, 420, 12, (255, 200, 60)))
                            shots += 1
                        else:
                            self.projectiles.append(Projectile(cx, cy, e, 900, 20, (120, 230, 255)))
                            laser = True
        if shots and self._sfx_cd <= 0:
            snd.play("shoot")
            self._sfx_cd = 0.15
        elif laser and self._sfx_cd <= 0:
            snd.play("laser")
            self._sfx_cd = 0.15

    def update(self, dt, g, tick):
        self._sfx_cd -= dt
        self._hit_cd -= dt
        total_poll = sum(g.world.tiles[y][x].pollution
                         for y in range(0, g.world.H, 10)
                         for x in range(0, g.world.W, 10)) / 1000.0
        self.evolution = min(1.0, self.evolution + dt * 0.00012 + total_poll * 0.00002)
        if not self.wave_active:
            self.time_to_next -= dt
            if self.time_to_next <= 0:
                self._spawn()
                self.time_to_next = self.interval
        died = False
        for e in self.enemies[:]:
            e.update(dt, g)
            if e.hp <= 0:
                self.enemies.remove(e)
                g.score += 10
                died = True
        if died:
            snd.play("explode")
        if self.wave_active and not self.enemies:
            self.wave_active = False
            self.time_to_next = self.interval
        self.update_turrets(dt, g)
        for p in self.projectiles[:]:
            p.update(dt)
            if p.hit:
                self.projectiles.remove(p)
                if self._hit_cd <= 0:
                    snd.play("hit")
                    self._hit_cd = 0.07

    def draw(self, screen, cam, g):
        for p in self.projectiles:
            p.draw(screen, cam)
        for e in self.enemies:
            e.draw(screen, cam, g)