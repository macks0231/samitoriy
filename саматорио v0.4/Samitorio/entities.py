# -*- coding: utf-8 -*-
"""Samitorio v0.3 - cells: belts, inserters, buildings & automation."""
import math

import pygame

import core
import snd
import tex
from core import TILE, DX, DY, OPP

# ──────────────────────────────────────────────────────────────────────
# Base cell
# ──────────────────────────────────────────────────────────────────────
class Cell:
    __slots__ = ["x", "y", "btype", "hp", "max_hp", "w", "h"]

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.btype = "?"
        self.hp = self.max_hp = 100
        self.w = self.h = 1

    # item interface (override where meaningful)
    def accept(self, item, fd):
        return False

    def push(self, item):
        return False

    def peek(self):
        return None

    def pull(self):
        return None

    def update(self, dt, g):
        pass

    def draw(self, screen, cam, g):
        pass

    @property
    def emits_light(self):
        return False

    @property
    def light_r(self):
        return 0

    def screen_pos(self, cam):
        return self.x * TILE - int(cam.ox), self.y * TILE - int(cam.oy)

    def removal(self, g):
        g.ent.remove(self)


# ──────────────────────────────────────────────────────────────────────
# Conveyor belt
# ──────────────────────────────────────────────────────────────────────
GAP = 0.28


class Belt(Cell):
    __slots__ = ["dir", "slots", "anim", "fast"]

    def __init__(self, x, y, d, fast=False):
        super().__init__(x, y)
        self.btype = "fast-belt" if fast else "conveyor-belt"
        self.dir = d
        self.fast = fast
        self.slots = [None] * 4
        self.anim = 0.0
        self.hp = self.max_hp = 170

    # --- item interface ---
    def accept(self, item, fd):
        return self.slots[0] is None

    def push(self, item):
        if self.slots[0] is None:
            self.slots[0] = item
            return True
        return False

    def peek(self):
        return self.slots[3]

    def pull(self):
        i = self.slots[3]
        if i is not None:
            self.slots[3] = None
        return i

    def update(self, dt, g):
        spd = 3.2 if self.fast else 2.2
        self.anim += dt * spd
        steps = int(self.anim)
        self.anim -= steps
        for _ in range(steps):
            dst = g.ent.cell_at(self.x + DX[self.dir], self.y + DY[self.dir])
            if dst is not None and self.slots[3] is not None and dst.accept(self.slots[3], OPP[self.dir]):
                dst.push(self.slots[3])
                self.slots[3] = None
            for i in range(3, 0, -1):
                if self.slots[i] is None and self.slots[i - 1] is not None:
                    self.slots[i] = self.slots[i - 1]
                    self.slots[i - 1] = None

    def draw(self, screen, cam, g):
        px, py = self.screen_pos(cam)
        col = core.icol(self.btype)
        bg = pygame.draw.rect(screen, tuple(max(0, v - 20) for v in col),
                              (px, py, TILE, TILE))
        pygame.draw.rect(screen, col, (px + 2, py + 2, TILE - 4, TILE - 4))
        # lanes
        for k in range(2):
            if self.dir in (0, 2):
                yy = py + 6 + k * (TILE - 12)
                pygame.draw.line(screen, tuple(max(0, v - 45) for v in col),
                                 (px + 2, yy), (px + TILE - 3, yy), 1)
            else:
                xx = px + 6 + k * (TILE - 12)
                pygame.draw.line(screen, tuple(max(0, v - 45) for v in col),
                                 (xx, py + 2), (xx, py + TILE - 3), 1)
        # animated chevrons
        ph = self.anim % 1.0
        n = 4 if self.fast else 3
        for i in range(n):
            f = ((i + ph) / n) - 0.5
            cx = px + TILE / 2 + DX[self.dir] * f * TILE
            cy = py + TILE / 2 + DY[self.dir] * f * TILE
            if self.dir in (0, 2):
                tip = (cx + DX[self.dir] * 3, cy - 0)
                pygame.draw.line(screen, tuple(min(255, v + 15) for v in col),
                                 (cx - DX[self.dir] * 4, cy), tip, 2)
            else:
                pygame.draw.line(screen, tuple(min(255, v + 15) for v in col),
                                 (cx, cy - DY[self.dir] * 4), (cx, cy + DY[self.dir] * 3), 2)
        # items
        for i, item in enumerate(self.slots):
            if item is None:
                continue
            f = (i + 0.5 + self.anim) / 4.0
            ix = px + TILE / 2 + DX[self.dir] * (f - 0.5) * TILE
            iy = py + TILE / 2 + DY[self.dir] * (f - 0.5) * TILE
            screen.blit(tex.item_tex(item, 14), (int(ix) - 7, int(iy) - 7))


# ──────────────────────────────────────────────────────────────────────
# Inserter
# ──────────────────────────────────────────────────────────────────────
class Inserter(Cell):
    __slots__ = ["dir", "holding", "phase", "fast", "swing_t"]

    def __init__(self, x, y, d, fast=False):
        super().__init__(x, y)
        self.btype = "fast-inserter" if fast else "inserter"
        self.dir = d
        self.fast = fast
        self.holding = None
        self.phase = 0.0
        self.swing_t = 0.0
        self.hp = self.max_hp = 150

    def src(self, g):
        return g.ent.cell_at(self.x + DX[OPP[self.dir]], self.y + DY[OPP[self.dir]])

    def dst(self, g):
        return g.ent.cell_at(self.x + DX[self.dir], self.y + DY[self.dir])

    def update(self, dt, g):
        if core.BLDG_DEFS[self.btype]["pw_use"] and g.power.sat < 0.4:
            return
        T = 0.5 if self.fast else 1.0
        if self.holding is None:
            src = self.src(g)
            dst = self.dst(g)
            if src is not None and dst is not None:
                it = src.peek()
                if it is not None and dst.accept(it, OPP[self.dir]):
                    src.pull()
                    self.holding = it
                    self.phase = 0.0
        else:
            self.phase += dt / T
            if self.phase >= 0.5:
                dst = self.dst(g)
                if dst is not None and dst.accept(self.holding, OPP[self.dir]):
                    if dst.push(self.holding):
                        self.holding = None
                        self.phase = 0.0
                else:
                    self.phase = 0.5

    def draw(self, screen, cam, g):
        px, py = self.screen_pos(cam)
        cx, cy = px + TILE // 2, py + TILE // 2
        base = core.BLDG_DEFS[self.btype]["col"]
        pygame.draw.rect(screen, tuple(max(0, v - 30) for v in base),
                         (px + 6, py + 6, TILE - 12, TILE - 12))
        pygame.draw.rect(screen, (40, 40, 50), (px + 6, py + 6, TILE - 12, TILE - 12), 1)
        pygame.draw.circle(screen, (70, 70, 85), (cx, cy), 5)
        # arm angle: from pickup (pointing back) to drop (pointing forward)
        p = min(1.0, self.phase * 2)
        if self.holding is not None:
            a0 = math.radians(self.dir * 90 + 180)
            a1 = math.radians(self.dir * 90)
        else:
            a0 = a1 = math.radians(self.dir * 90)
        ang = a0 + (a1 - a0) * p
        if self.holding is not None and p > 0.5:
            ang = a1
        ax = cx + math.cos(ang) * 13
        ay = cy + math.sin(ang) * 13
        pygame.draw.line(screen, (160, 160, 175), (cx, cy), (ax, ay), 3)
        pygame.draw.circle(screen, (120, 120, 140), (int(ax), int(ay)), 4)
        if self.holding is not None:
            hx = cx + math.cos(ang) * 18
            hy = cy + math.sin(ang) * 18
            screen.blit(tex.item_tex(self.holding, 12), (int(hx) - 6, int(hy) - 6))


# ──────────────────────────────────────────────────────────────────────
# Buildings
# ──────────────────────────────────────────────────────────────────────
class Building(Cell):
    __slots__ = ["btype", "d", "buf", "inb", "outb", "prog",
                 "recipe", "out_dir", "aim", "recoil", "mine_vein"]

    def __init__(self, x, y, btype, recipe=None):
        super().__init__(x, y)
        self.btype = btype
        self.d = core.BLDG_DEFS[btype]
        self.w, self.h = self.d["w"], self.d["h"]
        self.max_hp = self.hp = self.d["hp"]
        self.buf = {}
        self.inb = {}
        self.outb = {}
        self.prog = 0.0
        self.recipe = recipe
        self.out_dir = 0
        self.aim = None
        self.recoil = 0.0
        self.mine_vein = None

    @property
    def emits_light(self):
        return self.d["light"]

    @property
    def light_r(self):
        return self.d["lr"]

    # --- generic item interface ---
    def accept(self, item, fd):
        if item in self._inputs():
            L = core.stack_size(item)
            return self.inb.get(item, 0) < L and self._out_free()
        if self.btype in ("gun-turret",) and item == "firearm-magazine":
            return self.buf.get(item, 0) < 2
        return False

    def push(self, item):
        if self.accept(item, None):
            if item in self._inputs():
                self.inb[item] = self.inb.get(item, 0) + 1
            else:
                self.buf[item] = self.buf.get(item, 0) + 1
            return True
        return False

    def peek(self):
        for it in list(self.outb):
            if self.outb[it] > 0:
                return it
        return None

    def pull(self):
        for it in list(self.outb):
            if self.outb[it] > 0:
                self.outb[it] -= 1
                if self.outb[it] <= 0:
                    del self.outb[it]
                return it
        return None

    def _inputs(self):
        if self.btype == "miner":
            return set()
        if self.btype == "furnace":
            return set(core.SMELT.keys())
        if self.btype == "assembler" and self.recipe:
            return set(core.RECIPES[self.recipe]["in"].keys())
        if self.btype == "lab":
            return {"automation-science-pack", "logistic-science-pack",
                    "military-science-pack", "chemical-science-pack"}
        return set()

    def _out_free(self):
        if self.btype == "miner":
            return sum(self.buf.values()) < 100
        if self.btype == "furnace":
            return all(self.outb.get(k, 0) < 100 for k in self.outb)
        if self.btype == "assembler" and self.recipe:
            return self.outb.get(self.recipe, 0) < 100
        if self.btype == "lab":
            return True
        return False

    # --- behavior ---
    def _vein_tile(self, g):
        tiles = []
        for dy in range(self.h):
            for dx in range(self.w):
                t = g.world.get(self.x + dx, self.y + dy)
                if t and t.resource and t.amount > 0:
                    tiles.append((abs(dx - (self.w // 2)) + abs(dy - (self.h // 2)), dx, dy, t))
        tiles.sort()
        return tiles[0][3] if tiles else None

    def update(self, dt, g):
        if self.btype == "miner":
            self._update_miner(dt, g)
        elif self.btype == "furnace":
            self._update_furnace(dt, g)
        elif self.btype == "assembler":
            self._update_asm(dt, g)
        elif self.btype == "lab":
            pass
        if self.recoil > 0:
            self.recoil -= dt * 6

    def _update_miner(self, dt, g):
        t = self._vein_tile(g)
        if t is None:
            self.prog = 0.0
            return
        res = t.resource
        t.amount -= dt / 2.0
        self.prog = min(1.0, self.prog + dt / 1.0)
        if self.prog >= 1.0:
            self.prog = 0.0
            if t.amount > 0 and sum(self.buf.values()) < 100:
                self.buf[res] = self.buf.get(res, 0) + 1
        # push out along out_dir
        for item in list(self.buf):
            if self.buf[item] <= 0:
                continue
            placed = False
            if self.out_dir in (0, 2):
                tx0 = self.x + (self.w if self.out_dir == 0 else -1)
                for dy in range(self.h):
                    c = g.ent.cell_at(tx0, self.y + dy)
                    if c is not None and c.accept(item, OPP[self.out_dir]):
                        if c.push(item):
                            placed = True
                            break
            else:
                ty0 = self.y + (self.h if self.out_dir == 1 else -1)
                for dx in range(self.w):
                    c = g.ent.cell_at(self.x + dx, ty0)
                    if c is not None and c.accept(item, OPP[self.out_dir]):
                        if c.push(item):
                            placed = True
                            break
            if placed:
                self.buf[item] -= 1
                if self.buf[item] <= 0:
                    del self.buf[item]

    def _update_furnace(self, dt, g):
        recipe = None
        for k in core.SMELT:
            if self.inb.get(k, 0) > 0:
                recipe = k
                break
        if recipe is None:
            self.prog = 0.0
            return
        out = core.SMELT[recipe]
        if self.outb.get(out, 0) >= 100:
            self.prog = 0.0
            return
        spd = (0.5 + 0.5 * g.power.sat) if core.BLDG_DEFS["furnace"]["pw_use"] else 1.0
        t = core.RECIPES[out]["t"]
        self.prog += dt * spd / t
        if self.prog >= 1.0:
            self.prog = 0.0
            self.inb[recipe] -= 1
            if self.inb[recipe] <= 0:
                del self.inb[recipe]
            self.outb[out] = self.outb.get(out, 0) + 1

    def _update_asm(self, dt, g):
        if not self.recipe or self.recipe not in core.RECIPES:
            self.prog = 0.0
            return
        r = core.RECIPES[self.recipe]
        ready = all(self.inb.get(k, 0) >= v for k, v in r["in"].items())
        if not ready or (self.outb.get(self.recipe, 0) >= 50 and r["out"] == 1):
            self.prog = 0.0
            return
        spd = 0.5 + 0.5 * g.power.sat if core.BLDG_DEFS["assembler"]["pw_use"] else 1.0
        self.prog += dt * spd / r["t"]
        if self.prog >= 1.0:
            self.prog = 0.0
            for k, v in r["in"].items():
                self.inb[k] -= v
                if self.inb[k] <= 0:
                    del self.inb[k]
            self.outb[self.recipe] = self.outb.get(self.recipe, 0) + r["out"]

    # ── drawing ──────────────────────────────────────────────────────
    def draw(self, screen, cam, g):
        px, py = self.screen_pos(cam)
        w = self.w * TILE
        h = self.h * TILE
        m = getattr(self, "_draw_" + self.btype.replace("-", "_"), None)
        if m is not None:
            m(screen, px, py, w, h, g)
        else:
            pygame.draw.rect(screen, self.d["col"], (px, py, w, h))
            pygame.draw.rect(screen, (255, 255, 255), (px, py, w, h), 1)
        if self.hp < self.max_hp * 0.98:
            frac = self.hp / self.max_hp
            pygame.draw.rect(screen, (150, 0, 0), (px + 4, py + 4, w - 8, 5))
            pygame.draw.rect(screen, (0, 220, 0), (px + 4, py + 4, int((w - 8) * frac), 5))

    def _draw_miner(self, screen, px, py, w, h, g):
        base = self.d["col"]
        mining = self.prog > 0
        vib = int(math.sin(g.t * 30) * 1.5) if mining else 0
        screen.blit(tex.plate_tex("miner", self.w, self.h, base,
                                  deco=lambda s, W, H: tex.rivets(s, W, H)), (px + vib, py))
        pygame.draw.rect(screen, (50, 50, 45), (px + w // 2 - 7, py + h // 2 - 7, 14, 14), 1)
        pygame.draw.circle(screen, (60, 60, 65), (px + w // 2, py + h // 2), 5)
        a = g.t * 4.0
        if mining:
            a *= 2.2
        for i in range(3):
            an = a + i * 2.094
            x1 = px + w // 2 + math.cos(an) * 6
            y1 = py + h // 2 + math.sin(an) * 6
            x2 = px + w // 2 + math.cos(an + 0.5) * 11
            y2 = py + h // 2 + math.sin(an + 0.5) * 11
            pygame.draw.line(screen, (150, 150, 130), (int(x1), int(y1)),
                             (int(x2), int(y2)), 2)
        if mining:
            # flying dust + sparks
            mx = px + w // 2 + DX[self.out_dir] * (w // 2 - 6)
            my = py + h // 2
            for i in range(2):
                ph = ((g.t * 2.4 + i * 0.5) % 1.0)
                ddx = ph * (w // 2) * (DX[self.out_dir] or 1)
                ddy = math.sin(g.t * 9 + i * 4) * 6 - ph * 12
                pygame.draw.circle(screen, (130, 126, 118),
                                   (int(mx + ddx), int(my + ddy)), int(2 + ph * 2))
                pygame.draw.circle(screen, (235, 225, 160),
                                   (int(mx + ddx), int(my - ddy)), 1)
        # output arrow
        d = self.out_dir
        ax = px + w // 2 + DX[d] * (w // 2 - 8)
        ay = py + h // 2 + DY[d] * (h // 2 - 8)
        pygame.draw.polygon(screen, (60, 60, 70),
                            [(ax + DX[d] * 5, ay + DY[d] * 5),
                             (ax + DX[d] * -3 + DY[d] * 4, ay + DY[d] * -3 + DX[d] * 4),
                             (ax + DX[d] * -3 - DY[d] * 4, ay + DY[d] * -3 - DX[d] * 4)])
        if self.buf:
            n = sum(self.buf.values())
            fr = core.icol(next(iter(self.buf)))
            pygame.draw.rect(screen, (20, 20, 30), (px + 4, py + 4, 22, 10))
            pygame.draw.rect(screen, fr, (px + 4, py + 4, int(22 * min(1, n / 100)), 10))

    def _draw_furnace(self, screen, px, py, w, h, g):
        screen.blit(tex.plate_tex("furnace", self.w, self.h, self.d["col"],
                                  deco=lambda s, W, H: tex.rivets(s, W, H)), (px, py))
        fx = px + w // 2 - 6
        fy = py + h // 2 + 2
        f = tex.flicker(g.t * 5, self.x * 3 + self.y)
        heat = int(90 + 150 * f)
        pygame.draw.rect(screen, (30, 30, 35), (fx - 2, fy - 2, 16, 20))
        pygame.draw.rect(screen, (heat, heat // 3, 0), (fx, fy, 12, 16))
        # flame wobble
        pyo = int(math.sin(g.t * 11) * 1.5)
        pygame.draw.polygon(screen, (255, 200, 70),
                            [(fx + 2, fy + 14), (fx + 4, fy + 5 + pyo),
                             (fx + 6, fy + 14), (fx + 9, fy + 8 - pyo), (fx + 11, fy + 15)])
        pygame.draw.rect(screen, (255, 220, 120), (fx + 3, fy + 5, 6, 6))
        if self.prog > 0:
            c = tex.disc("furnace_glow", 14, (255, 140, 30))
            c.set_alpha(int(60 * (1 - self.prog)))
            screen.blit(c, (fx - 2, fy - 2))
            # rising embers
            ex = fx + int(math.sin(g.t * 7) * 3)
            ey = fy + 4 - int(((g.t * 0.9) % 1.0) * 18)
            pygame.draw.circle(screen, (255, 180 + int(70 * f), 40), (ex, ey), 1)
        # input/output dots
        for i, ins in enumerate(self.inb):
            screen.blit(tex.item_tex(ins, 10), (px + 4 + i * 14, py + 4))
        for i, out in enumerate(self.outb):
            screen.blit(tex.item_tex(out, 10), (px + w - 4 - 10 - i * 14, py + 4))

    def _draw_asm(self, screen, px, py, w, h, g):
        base = self.d["col"]
        screen.blit(tex.plate_tex("assembler", self.w, self.h, base), (px, py))
        bob = (math.sin(g.t * 6) + 1) / 2
        # pistons
        for cx2, cy2, ang in ((px + 12, py + h // 2, math.pi / 2),
                              (px + w - 12, py + h // 2, math.pi / 2),
                              (px + w // 2, py + 12, 0),
                              (px + w // 2, py + h - 12, 0)):
            pygame.draw.circle(screen, (45, 45, 60), (cx2, cy2), 5)
            px2 = cx2 + math.cos(ang) * (4 + bob * 6)
            py2 = cy2 + math.sin(ang) * (4 + bob * 6)
            pygame.draw.circle(screen, (120, 120, 150), (int(px2), int(py2)), 3)
        # animated lid
        lid = int(abs(math.sin(g.t * 2.2)) * 3 * min(1, self.prog * 4 + 0.001))
        pygame.draw.rect(screen, (70, 70, 90), (px + w // 2 - 12, py + 6 - lid, 24, 6))
        if self.prog > 0:
            col = (60, 220, 90)
        elif self.recipe and any(self.inb.get(k, 0) >= v for k, v in core.RECIPES[self.recipe]["in"].items()):
            col = (255, 200, 40)
        else:
            col = (120, 40, 40)
        pygame.draw.circle(screen, (30, 30, 40), (px + w // 2, py + h // 2 + 8), 5)
        pygame.draw.circle(screen, col, (px + w // 2, py + h // 2 + 8), 3)
        if col[0] > 200:
            blink = tex.disc("asm_blink", 10, (255, 210, 60))
            blink.set_alpha(int(60 + 60 * math.sin(g.t * 6)))
            screen.blit(blink, (px + w // 2 - 10, py + h // 2 - 2))
        for i, ins in enumerate(self.inb):
            screen.blit(tex.item_tex(ins, 10), (px + 4 + i * 14, py + h - 14))
        for i, out in enumerate(self.outb):
            screen.blit(tex.item_tex(out, 10), (px + w - 4 - 10 - i * 14, py + 4))

    def _draw_lab(self, screen, px, py, w, h, g):
        screen.blit(tex.plate_tex("lab", self.w, self.h, self.d["col"],
                                  deco=lambda s, W, H: tex.rivets(s, W, H)), (px, py))
        for i in range(3):
            fx = px + w // 2 - 18 + i * 18
            lvl = 8 + int(6 * tex.pulse(g.t * 1.5 + i, 1))
            bottle = (170, 205, 235) if g.power.sat >= 0.4 else (120, 140, 160)
            pygame.draw.rect(screen, bottle, (fx, py + h // 2 - lvl // 2, 10, lvl))
            pygame.draw.circle(screen, (150, 190, 220), (fx + 5, py + h // 2 - lvl // 2), 6)
            pygame.draw.circle(screen, (80, 220, 180), (fx + 5, py + h // 2 - lvl // 2 - 7), 3)
            if g.power.sat >= 0.4:
                bp = (py + h // 2 + lvl // 2 - 4) - int(((g.t * 2.2 + i) % 1.0) * lvl)
                pygame.draw.circle(screen, (140, 240, 200), (fx + int(math.sin(g.t * 5 + i) * 2), bp), 1)
        if self.prog > 0 and self.prog > 0.92:
            c = tex.disc("lab_glow", 12, (120, 240, 200))
            c.set_alpha(int(90 * ((1.0 - self.prog) * 12)))
            screen.blit(c, (px + w // 2 - 12, py + 4))

    def _draw_coal_gen(self, screen, px, py, w, h, g):
        screen.blit(tex.plate_tex("boiler", self.w, self.h, self.d["col"],
                                  deco=lambda s, W, H: tex.rivets(s, W, H)), (px, py))
        pygame.draw.rect(screen, (60, 60, 70), (px + w // 2 - 7, py + 2, 14, 8))
        # smoke
        for i in range(3):
            ph = (g.t * 0.7 + i / 3.0) % 1.0
            sx = px + w // 2 + int(math.sin((i + g.t) * 2) * 6)
            sy = py + int(ph * 18) - int(ph * 40 * 0.2)
            pygame.draw.circle(screen, (140, 140, 150, 0), (sx, sy),
                               int(2 + ph * 5))

    def _draw_solar(self, screen, px, py, w, h, g):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pygame.draw.rect(surf, (15, 25, 60), (5, 5, w - 10, h - 10))
        for yy in range(9, h - 9, 10):
            pygame.draw.line(surf, (40, 110, 200), (5, yy), (w - 5, yy), 1)
        for xx in range(9, w - 9, 10):
            pygame.draw.line(surf, (40, 110, 200), (xx, 5), (xx, h - 5), 1)
        sh = tex.pulse(g.t * 2, 2)
        ov = pygame.Surface((w, h), pygame.SRCALPHA)
        ov.fill((120, 200, 255, int(40 * sh)))
        surf.blit(ov, (0, 0))
        pygame.draw.rect(surf, (200, 220, 255), (0, 0, w, h), 2)
        screen.blit(surf, (px, py))

    def _draw_lamp(self, screen, px, py, w, h, g):
        pygame.draw.rect(screen, (90, 90, 100), (px + 14, py + TILE - 8, 4, 8))
        glow = tex.disc("lamp", 7, (255, 240, 150), rim=(255, 255, 220))
        pulse = tex.pulse(g.t * 5, 1)
        sh = max(0.4, pulse)
        s = int(6 * sh)
        screen.blit(glow, (px + 8 - s // 4, py + 6 - s // 4))
        pygame.draw.circle(screen, (255, 250, 200), (px + 9, py + 7), int(3 * sh + 0.5))

    def _draw_wall(self, screen, px, py, w, h, g):
        base = self.d["col"]
        pygame.draw.rect(screen, tuple(max(0, v - 25) for v in base),
                         (px, py, TILE, TILE))
        for yy in range(0, TILE, 8):
            off = 4 if (yy // 8) % 2 else 0
            for xx in range(-off, TILE, 8):
                pygame.draw.rect(screen, base, (px + xx + 1, py + yy + 1, 6, 6))
        pygame.draw.rect(screen, (60, 60, 55), (px, py, TILE, TILE), 2)
        if self.hp < self.max_hp * 0.6:
            pygame.draw.line(screen, (40, 40, 40), (px + 6, py + 6), (px + TILE - 6, py + TILE - 6), 2)

    def _draw_gun_turret(self, screen, px, py, w, h, g):
        screen.blit(tex.plate_tex("turret", self.w, self.h, self.d["col"],
                                  deco=lambda s, W, H: tex.rivets(s, W, H)), (px, py))
        cx, cy = px + w // 2, py + h // 2
        pygame.draw.circle(screen, (70, 70, 80), (cx, cy), 10)
        if self.aim is not None:
            ang = math.atan2(self.aim[1] - (self.y * TILE + h / 2),
                             self.aim[0] - (self.x * TILE + w / 2))
        else:
            ang = 0
        bx = cx + math.cos(ang) * 22
        by = cy + math.sin(ang) * 22
        pygame.draw.line(screen, (55, 55, 60), (cx, cy), (bx, by), 5)
        pygame.draw.circle(screen, (80, 80, 90), (int(bx), int(by)), 3)

    def _draw_laser_turret(self, screen, px, py, w, h, g):
        base = self.d["col"]
        screen.blit(tex.plate_tex("laser", self.w, self.h, base), (px, py))
        cx, cy = px + w // 2, py + h // 2
        pygame.draw.circle(screen, (30, 30, 45), (cx, cy), 12)
        pygame.draw.circle(screen, (100, 230, 255), (cx, cy), 8)
        if self.aim is not None:
            ang = math.atan2(self.aim[1] - (self.y * TILE + h / 2),
                             self.aim[0] - (self.x * TILE + w / 2))
            pygame.draw.line(screen, (60, 200, 255), (cx, cy),
                             (cx + math.cos(ang) * 16, cy + math.sin(ang) * 16), 3)
        if self.recoil > 0:
            pygame.draw.circle(screen, (180, 240, 255), (cx, cy), 10 + int(self.recoil * 8), 2)


# ──────────────────────────────────────────────────────────────────────
# Manager
# ──────────────────────────────────────────────────────────────────────
class Entities:
    def __init__(self, world, power):
        self.world = world
        self.power = power
        self.occ = {}

    def cell_at(self, tx, ty):
        return self.occ.get((tx, ty))

    def count_type(self, btype):
        return sum(1 for c in self.occ.values() if c.btype == btype and c.x == c.y and True)

    def place(self, kind, tx, ty, g, d=None, recipe=None):
        r = self._place(kind, tx, ty, g, d, recipe)
        snd.play("build" if r == "ok" else "deny")
        return r

    def _place(self, kind, tx, ty, g, d=None, recipe=None):
        df = core.BLDG_DEFS[kind]
        if not core.bldg_unlocked(kind, g.unlocked):
            return "lock"
        w, h = df["w"], df["h"]
        # check footprint
        has_vein = False
        for dy in range(h):
            for dx in range(w):
                t = self.world.get(tx + dx, ty + dy)
                if t is None:
                    return "edge"
                if t.rock:
                    return "rock"
                if self.occ.get((tx + dx, ty + dy)) is not None:
                    return "occupied"
                if t.resource and t.amount > 0:
                    has_vein = True
        if kind == "miner" and not has_vein:
            return "novein"
        if kind != "miner" and kind not in ("conveyor-belt", "fast-belt", "inserter",
                                            "fast-inserter", "lamp"):
            for dy in range(h):
                for dx in range(w):
                    if self.world.get(tx + dx, ty + dy).resource is not None:
                        return "resource"
        # cost
        for item, amt in df["cost"].items():
            if not g.inv.has(item, amt):
                return "cost"
        if kind in ("conveyor-belt", "fast-belt"):
            if d is None:
                d = self._auto_dir(tx, ty)
            cell = Belt(tx, ty, d, fast=(kind == "fast-belt"))
        elif kind in ("inserter", "fast-inserter"):
            if d is None:
                d = self._auto_ins_dir(tx, ty)
            cell = Inserter(tx, ty, d, fast=(kind == "fast-inserter"))
        else:
            cell = Building(tx, ty, kind, recipe=recipe)
        for item, amt in df["cost"].items():
            g.inv.remove(item, amt)
        for dy in range(h):
            for dx in range(w):
                self.occ[(tx + dx, ty + dy)] = cell
        return "ok"

    def _auto_dir(self, tx, ty):
        for d in range(4):
            c = self.occ.get((tx + DX[d], ty + DY[d]))
            if isinstance(c, Belt) and OPP[c.dir] == d:
                return c.dir
        return 0

    def _auto_ins_dir(self, tx, ty):
        for d in range(4):
            c = self.occ.get((tx + DX[d], ty + DY[d]))
            if isinstance(c, Building):
                return d
        for d in range(4):
            c = self.occ.get((tx + DX[d], ty + DY[d]))
            if isinstance(c, Belt):
                return OPP[d]
        return 1

    def remove(self, cell, refund=True):
        for dy in range(cell.h):
            for dx in range(cell.w):
                self.occ.pop((cell.x + dx, cell.y + dy), None)

    def update(self, dt, g):
        seen = set()
        for (tx, ty), c in list(self.occ.items()):
            if c in seen:
                continue
            seen.add(c)
            if c.hp <= 0:
                self.remove(c)
                continue
            c.update(dt, g)

    # solar production depends on daylight
    def day_power_factor(self, g):
        return g.day_p

    def draw(self, screen, cam, g):
        x0 = max(0, int(cam.ox // TILE) - 2)
        y0 = max(0, int(cam.oy // TILE) - 2)
        x1 = min(self.world.W, x0 + core.SW // TILE + 4)
        y1 = min(self.world.H, y0 + core.SH // TILE + 4)
        seen = set()
        for ty in range(y0, y1):
            for tx in range(x0, x1):
                c = self.occ.get((tx, ty))
                if c is None or c in seen:
                    continue
                seen.add(c)
                c.draw(screen, cam, g)