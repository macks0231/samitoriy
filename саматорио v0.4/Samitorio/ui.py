# -*- coding: utf-8 -*-
"""Samitorio v0.4 - HUD, minimap, build toolbar & ghost placement."""
import math
import pygame
import core
import lang
import settings
import tex
from core import TILE, DX, DY, F, txt, txt_c, BRD, TXT, GRN, RED, GLD, BLU, CYAN, ORG


def asm_recipes():
    return [k for k, r in core.RECIPES.items() if r["craft"] == "asm"]


class UI:
    def __init__(self):
        self.selected = "miner"
        self.dirn = {}
        self.asmp_idx = 0
        self.mouse_down = False
        self.ghost_ok = True
        self.ghost_msg = ""
        self._prev_tile = None
        self._mm_surf = None

    # ── handling ─────────────────────────────────────────────────
    def available_buildings(self, g):
        return [k for k in core.BUILD_ORDER if core.bldg_unlocked(k, g.unlocked)]

    def handle_event(self, event, g):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                g.player.build_mode = not g.player.build_mode
                return True
            if event.key == pygame.K_r and g.player.build_mode:
                self._rotate()
                return True
            if event.key in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET) and g.player.build_mode:
                n = len(asm_recipes())
                if n:
                    self.asmp_idx = (self.asmp_idx + (1 if event.key == pygame.K_RIGHTBRACKET else -1)) % n
                return True
            if pygame.K_1 <= event.key <= pygame.K_9:
                av = self.available_buildings(g)
                i = event.key - pygame.K_1
                if i < len(av):
                    self.selected = av[i]
                    g.player.build_mode = True
                return True
        if not g.player.build_mode:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.mouse_down = True
                self._place(g)
                return True
            if event.button == 3:
                g.player.build_mode = False
                self.mouse_down = False
                return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_down = False
        return False

    def _rotate(self):
        k = self.selected
        if k in ("conveyor-belt", "fast-belt", "inserter", "fast-inserter", "miner"):
            self.dirn[k] = (self.dirn.get(k, 0) + 1) % 4
        if k == "assembler":
            n = len(asm_recipes())
            if n:
                self.asmp_idx = (self.asmp_idx + 1) % n

    def _sel_recipe(self):
        r = asm_recipes()
        return r[self.asmp_idx % len(r)] if r else None

    def _mouse_tile(self, g):
        mx, my = pygame.mouse.get_pos()
        return int((mx + g.cam.ox) // TILE), int((my + g.cam.oy) // TILE)

    def _place(self, g):
        tx, ty = self._mouse_tile(g)
        if self._prev_tile == (tx, ty):
            return
        k = self.selected
        d = self.dirn.get(k)
        prev = self._prev_tile
        if prev is not None and k in ("conveyor-belt", "fast-belt", "inserter", "fast-inserter"):
            mdx = tx - prev[0]
            mdy = ty - prev[1]
            if mdx or mdy:
                d = (0 if mdx > 0 else 2) if abs(mdx) >= abs(mdy) else (1 if mdy > 0 else 3)
                self.dirn[k] = d
        recipe = self._sel_recipe() if k == "assembler" else None
        ok, msg = self._valid(k, tx, ty, g)
        self.ghost_ok, self.ghost_msg = ok, msg
        if ok:
            g.ent.place(k, tx, ty, g, d=d, recipe=recipe)
        self._prev_tile = (tx, ty)

    def _valid(self, k, tx, ty, g):
        d = core.BLDG_DEFS[k]
        if not core.bldg_unlocked(k, g.unlocked):
            return False, lang.t("valid.not_researched")
        has_vein = False
        for dy in range(d["h"]):
            for dx in range(d["w"]):
                if g.ent.cell_at(tx + dx, ty + dy) is not None:
                    return False, lang.t("valid.tile_occupied")
                t = g.world.get(tx + dx, ty + dy)
                if t is None:
                    return False, lang.t("valid.out_of_bounds")
                if t.rock:
                    return False, lang.t("valid.boulder")
                if t.resource and t.amount > 0:
                    has_vein = True
        if k == "miner" and not has_vein:
            return False, lang.t("valid.no_vein")
        if k not in ("miner", "conveyor-belt", "fast-belt", "inserter",
                     "fast-inserter", "lamp"):
            for dy in range(d["h"]):
                for dx in range(d["w"]):
                    if g.world.get(tx + dx, ty + dy).resource is not None:
                        return False, lang.t("valid.clear")
        for item, amt in d["cost"].items():
            if not g.inv.has(item, amt):
                return False, lang.t("valid.missing")
        return True, ""

    def update(self, g):
        if not self.mouse_down:
            self._prev_tile = self._mouse_tile(g)
        tx, ty = self._mouse_tile(g)
        ok, msg = self._valid(self.selected, tx, ty, g)
        self.ghost_ok, self.ghost_msg = ok, msg

    # ── drawing ─────────────────────────────────────────────────
    def draw(self, screen, g):
        self._hud(screen, g)
        self._minimap(screen, g)
        self._controls(screen, g)
        if g.player.build_mode:
            self._toolbar(screen, g)
            self._ghost(screen, g)
            if self.mouse_down:
                self._place(g)

    def _hud(self, screen, g):
        pygame.draw.rect(screen, (14, 14, 22), (0, 0, core.SW, 38))
        r = g.player.hp / g.player.max_hp
        pygame.draw.rect(screen, (100, 0, 0), (10, 9, 120, 20))
        pygame.draw.rect(screen, (0, 200, 60), (10, 9, int(120 * r), 20))
        pygame.draw.rect(screen, (255, 255, 255), (10, 9, 120, 20), 1)
        txt(screen, F("n"), lang.t("hud.hp") % (g.player.hp, g.player.max_hp), (14, 14), (255, 255, 255))
        pc = CYAN if g.power.sat >= 1.0 else (RED if g.power.sat < 0.5 else ORG)
        txt(screen, F("n"),
            lang.t("hud.power") % (g.power.total_production, g.power.total_consumption),
            (145, 14), pc)
        wt = g.combat.time_to_next
        wc = RED if wt < 30 else (255, 180, 0)
        wav_txt = (lang.t("hud.wave_in") % int(wt)) if not g.combat.wave_active else lang.t("hud.wave_active")
        txt(screen, F("n"), lang.t("hud.wave") % wav_txt, (330, 14), wc)
        phase = lang.t("hud.day") if g.is_day else lang.t("hud.night")
        txt_c(screen, F("n"), "%s %d%%" % (phase, int(g.todp * 100)),
              (core.SW // 2, 14), (255, 220, 100))
        tile = g.world.get(int(g.player.x // TILE), int(g.player.y // TILE))
        if tile:
            txt(screen, F("n"), lang.biome(tile.biome), (core.SW - 160, 14), (150, 255, 150))
        txt(screen, F("n"), lang.t("hud.score") % g.score, (core.SW - 300, 14), GLD)
        ff = pygame.font.SysFont("Consolas", 12)
        if settings.get("show_fps"):
            fps_col = GRN if g.fps >= 50 else (RED if g.fps < 30 else GLD)
            scr = ff.render(lang.t("hud.fps") % int(g.fps), True, fps_col)
            screen.blit(scr, (core.SW - 70, 26))
        i = 0
        for name, amt in list(g.inv.items.items()):
            if name in core.RAW or name.endswith("science-pack"):
                continue
            if i >= 6:
                break
            screen.blit(tex.item_tex(name, 16), (430 + i * 66, 11))
            txt(screen, F("n"), str(amt), (450 + i * 66, 14), (200, 200, 200))
            i += 1

    def _minimap(self, screen, g):
        MW, MH = 160, 120
        MX, MY = core.SW - MW - 8, core.SH - MH - 8
        w = g.world
        if self._mm_surf is None or self._mm_surf.get_size() != (MW, MH):
            surf = pygame.Surface((MW, MH))
            surf.fill((5, 5, 5))
            sx = MW / w.W
            sy = MH / w.H
            step = max(1, w.W // MW)
            for ty in range(0, w.H, step):
                row = w.tiles[ty]
                for tx in range(0, w.W, step):
                    c = core.BIOME_COL[row[tx].biome]
                    pygame.draw.rect(surf, c,
                                     (int(tx * sx), int(ty * sy),
                                      max(1, int(step * sx) + 1), max(1, int(step * sy) + 1)))
            self._mm_surf = surf
        screen.blit(self._mm_surf, (MX, MY))
        for e in g.combat.enemies:
            ex = int(e.x / (w.W * TILE) * MW)
            ey = int(e.y / (w.H * TILE) * MH)
            pygame.draw.rect(screen, (220, 30, 30), (MX + ex - 1, MY + ey - 1, 3, 3))
        px = int(g.player.x / (w.W * TILE) * MW)
        py = int(g.player.y / (w.H * TILE) * MH)
        pygame.draw.circle(screen, (255, 255, 0), (MX + px, MY + py), 3)
        pygame.draw.rect(screen, (200, 200, 200), (MX, MY, MW, MH), 1)
        txt(screen, F("n"), lang.t("hud.map"), (MX, MY - 14), (140, 140, 140))

    def _controls(self, screen, g):
        t = lang.t("hud.controls")
        if g.player.build_mode:
            t = lang.t("hud.controls_build")
        txt(screen, F("n"), t, (8, core.SH - 15), (110, 110, 110))

    def _toolbar(self, screen, g):
        av = self.available_buildings(g)
        n = len(av)
        per = 8
        rows = (n + per - 1) // per
        tw = per * 58 + 4
        th = rows * 58 + 4
        x0 = (core.SW - tw) // 2
        y0 = core.SH - th - 8
        bg = pygame.Surface((tw, th), pygame.SRCALPHA)
        bg.fill((20, 20, 30, 230))
        screen.blit(bg, (x0, y0))
        pygame.draw.rect(screen, BRD, (x0, y0, tw, th), 2)
        for i, k in enumerate(av):
            col = i % per
            row = i // per
            sx = x0 + 4 + col * 58
            sy = y0 + 4 + row * 58
            d = core.BLDG_DEFS[k]
            ok = core.bldg_unlocked(k, g.unlocked) and \
                all(g.inv.has(it, v) for it, v in d["cost"].items())
            selected = k == self.selected
            pygame.draw.rect(screen, (55, 70, 100) if selected else (38, 38, 55),
                             (sx, sy, 54, 54))
            pygame.draw.rect(screen, GLD if selected else BRD, (sx, sy, 54, 54), 2 if selected else 1)
            mini = self._mini(k)
            if ok:
                screen.blit(mini, (sx + 5, sy + 5))
            else:
                m = mini.copy()
                m.set_alpha(130)
                screen.blit(m, (sx + 5, sy + 5))
                pygame.draw.circle(screen, RED, (sx + 48, sy + 10), 5)
                pygame.draw.line(screen, (255, 255, 255), (sx + 45, sy + 7), (sx + 51, sy + 13), 1)
            txt_c(screen, F("n"), str(i + 1), (sx + 9, sy + 3), (230, 230, 240))
            txt_c(screen, F("n"), k.replace("-", "\n").split("\n")[0][:8],
                  (sx + 27, sy + 40), (200, 200, 210))

    def _mini(self, k):
        key = "mini_" + k
        if key in tex._cache:
            return tex._cache[key]
        d = core.BLDG_DEFS[k]
        s = pygame.Surface((44, 44), pygame.SRCALPHA)
        s.fill((20, 20, 30))
        col = d["col"]
        pygame.draw.rect(s, col, (3, 3, 38, 38))
        pygame.draw.rect(s, tuple(max(0, v - 50) for v in col), (3, 3, 38, 38), 1)
        pygame.draw.rect(s, (255, 255, 255), (3, 3, 38, 38), 1)
        if k == "conveyor-belt" or k == "fast-belt":
            pygame.draw.line(s, (30, 30, 30), (8, 22), (36, 22), 3)
            pygame.draw.polygon(s, (255, 255, 255), [(36, 18), (36, 26), (40, 22)])
        if k == "inserter" or k == "fast-inserter":
            pygame.draw.line(s, (200, 200, 210), (30, 30), (14, 14), 3)
        if k == "wall":
            pygame.draw.rect(s, (200, 190, 175), (10, 10, 24, 24))
            pygame.draw.rect(s, (120, 110, 100), (10, 10, 24, 24), 1)
        if k == "gun-turret":
            pygame.draw.line(s, (60, 60, 70), (22, 22), (36, 12), 4)
        if k == "laser-turret":
            pygame.draw.circle(s, (100, 230, 255), (22, 22), 9)
        if k == "miner":
            pygame.draw.circle(s, (60, 60, 65), (22, 22), 6)
        if k == "solar-panel":
            pygame.draw.line(s, (100, 190, 230), (10, 22), (34, 22), 2)
            pygame.draw.line(s, (100, 190, 230), (22, 10), (22, 34), 2)
        tex._cache[key] = s
        return s

    def _ghost(self, screen, g):
        tx, ty = self._mouse_tile(g)
        k = self.selected
        d = core.BLDG_DEFS[k]
        px = tx * TILE - int(g.cam.ox)
        py = ty * TILE - int(g.cam.oy)
        w, h = d["w"] * TILE, d["h"] * TILE
        ok = self.ghost_ok
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        col = (80, 220, 90) if ok else (230, 80, 70)
        surf.fill((*col, 55))
        pygame.draw.rect(surf, col, (0, 0, w, h), 2)
        screen.blit(surf, (px, py))
        if self.ghost_msg:
            txt(screen, F("s"), self.ghost_msg, (px + 4, py - 18), RED)
        if k in ("conveyor-belt", "fast-belt", "inserter", "fast-inserter", "miner"):
            dd = self.dirn.get(k, 0)
            ax = px + w // 2 + DX[dd] * (w // 2 - 8)
            ay = py + h // 2 + DY[dd] * (h // 2 - 8)
            pygame.draw.polygon(screen, (255, 255, 255),
                                [(ax + DX[dd] * 7, ay + DY[dd] * 7),
                                 (ax - DY[dd] * 4, ay - DX[dd] * 4),
                                 (ax + DY[dd] * 4, ay + DX[dd] * 4)], 2)

