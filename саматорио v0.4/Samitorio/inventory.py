# -*- coding: utf-8 -*-
"""Samitorio v0.4 - player inventory, manual crafting, statistics."""
import pygame

import core
import lang
import snd
import tex
from core import DARK, MID, BRD, TXT, GRN, RED, GLD, BLU
from core import F, txt, txt_c

SLOT = 40


class Inventory:
    def __init__(self, unlocked_set):
        self.items = {}
        self.visible = False
        self.tab = 0
        self.search = ""
        self.selected = None
        self.craft_q = []
        self._scroll = 0
        self._typing = False
        self.unl = unlocked_set

    # ── item ops ────────────────────────────────────────────────
    def add(self, item, n=1):
        self.items[item] = self.items.get(item, 0) + n

    def remove(self, item, n=1):
        if self.items.get(item, 0) >= n:
            self.items[item] -= n
            if self.items[item] <= 0:
                del self.items[item]
            return True
        return False

    def has(self, item, n=1):
        return self.items.get(item, 0) >= n

    def count(self, item):
        return self.items.get(item, 0)

    def toggle(self):
        self.visible = not self.visible
        self._typing = False

    def start_craft(self, name):
        if len(self.craft_q) >= 12:
            return False
        if not (name in core.RECIPES and core.RECIPES[name]["craft"] == "hand"):
            return False
        r = core.RECIPES[name]
        for it, v in r["in"].items():
            if not self.has(it, v):
                return False
        for it, v in r["in"].items():
            self.remove(it, v)
        self.craft_q.append({"name": name, "total": r["t"], "e": 0.0})
        return True

    def update(self, dt, g):
        if self.craft_q:
            j = self.craft_q[0]
            j["e"] += dt
            if j["e"] >= j["total"]:
                out = core.RECIPES[j["name"]]["out"]
                self.add(j["name"], out)
                self.craft_q.pop(0)
                snd.play("pickup")

    def handle_event(self, event, g):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.toggle()
            return True
        if not self.visible:
            return False
        if event.type == pygame.KEYDOWN:
            if self._typing:
                if event.key == pygame.K_BACKSPACE:
                    self.search = self.search[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self._typing = False
                    self.search = ""
                elif event.unicode and event.unicode.isprintable():
                    self.search += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._click(event.pos, g)
        if event.type == pygame.MOUSEWHEEL:
            self._scroll = max(0, self._scroll - event.y * 2)
        return True

    def _tabs(self):
        return (lang.t("inv.items"), lang.t("inv.craft"),
                lang.t("inv.stats"), lang.t("inv.equip"))

    def _click(self, pos, g):
        mx, my = pos
        W, H = 1000, 600
        x0 = (core.SW - W) // 2
        y0 = (core.SH - H) // 2
        for i, lbl in enumerate(self._tabs()):
            if pygame.Rect(x0 + 12 + i * 148, y0 + 32, 140, 24).collidepoint(mx, my):
                self.tab = i
                self._scroll = 0
        if pygame.Rect(x0 + 12, y0 + 62, 300, 22).collidepoint(mx, my):
            self._typing = True
        if self.tab == 1:
            self._click_craft(mx, my, x0, y0)
        if self.tab == 0:
            self._click_item(mx, my, x0, y0)

    def _click_item(self, mx, my, x0, y0):
        filt = self._filtered()
        cols = (1000 - 240 - 20) // SLOT
        vis = (600 - 40 - 34) // SLOT
        for idx in range(len(filt)):
            rr = idx // cols - self._scroll
            cc = idx % cols
            if not (0 <= rr < vis):
                continue
            sx = x0 + 14 + cc * SLOT
            sy = y0 + 94 + rr * SLOT
            if pygame.Rect(sx, sy, SLOT - 2, SLOT - 2).collidepoint(mx, my):
                self.selected = filt[idx][0]

    def _click_craft(self, mx, my, x0, y0):
        rows = self._craft_list()
        for i, name in enumerate(rows[:8]):
            bx = x0 + 20
            by = y0 + 250 + i * 40
            ok = all(self.has(it, v) for it, v in core.RECIPES[name]["in"].items())
            if ok and pygame.Rect(bx + 600, by + 4, 80, 24).collidepoint(mx, my):
                self.start_craft(name)

    def _filtered(self):
        q = self.search.lower()
        return [(k, v) for k, v in sorted(self.items.items())
                if q in k or q in core.iname(k).lower() or q in lang.item(k).lower()]

    def _craft_list(self):
        out = []
        for name, r in core.RECIPES.items():
            if r["craft"] == "hand" and core.unlocked(name, self.unl):
                out.append(name)
        out.sort(key=lambda k: tuple(sorted(core.RECIPES[k]["in"].items())))
        return out

    # ── drawing ─────────────────────────────────────────────────
    def draw(self, screen, g):
        if not self.visible:
            return
        W, H = 1000, 600
        x0 = (core.SW - W) // 2
        y0 = (core.SH - H) // 2
        bg = pygame.Surface((W, H), pygame.SRCALPHA)
        bg.fill((*DARK, 248))
        screen.blit(bg, (x0, y0))
        pygame.draw.rect(screen, BRD, (x0, y0, W, H), 2)
        pygame.draw.rect(screen, (28, 28, 42), (x0, y0, W, 30))
        txt(screen, F("b"), lang.t("inv.title"), (x0 + 14, y0 + 5), TXT)
        txt(screen, F("s"), lang.t("inv.close"), (x0 + W - 90, y0 + 8), (120, 120, 140))
        for i, lbl in enumerate(self._tabs()):
            tx = x0 + 12 + i * 148
            ty = y0 + 32
            pygame.draw.rect(screen, (50, 80, 130) if self.tab == i else MID,
                             (tx, ty, 140, 24))
            pygame.draw.rect(screen, BRD, (tx, ty, 140, 24), 1)
            txt_c(screen, F("s"), lbl, (tx + 70, ty + 5),
                  TXT if self.tab == i else (150, 150, 170))
        pygame.draw.line(screen, BRD, (x0, y0 + 58), (x0 + W, y0 + 58), 1)
        cy = y0 + 60
        if self.tab == 0:
            self._t_items(screen, x0, cy, W, H - 62, g)
        elif self.tab == 1:
            self._t_craft(screen, x0, cy, W, H - 62, g)
        elif self.tab == 2:
            self._t_stats(screen, x0, cy, W, H - 62)
        else:
            self._t_equip(screen, x0, cy, W, H - 62)

    def _t_items(self, screen, x0, y0, W, H, g):
        pygame.draw.rect(screen, MID, (x0 + 12, y0 + 4, 300, 22))
        pygame.draw.rect(screen, BLU if self._typing else BRD,
                         (x0 + 12, y0 + 4, 300, 22), 1)
        ph = self.search if self.search else (lang.t("inv.search") if not self._typing else "")
        txt(screen, F("s"), ph, (x0 + 18, y0 + 7),
            TXT if self.search else (90, 90, 110))
        filt = self._filtered()
        cols = (W - 250) // SLOT
        vis = (H - 30) // SLOT
        max_sc = max(0, (len(filt) + cols - 1) // cols - vis)
        self._scroll = min(self._scroll, max_sc)
        # detail panel
        self._detail(screen, x0 + W - 246, y0 + 8, 240, H - 20)
        for idx, (name, amt) in enumerate(filt):
            rr = idx // cols - self._scroll
            cc = idx % cols
            if not (0 <= rr < vis):
                continue
            sx = x0 + 14 + cc * SLOT
            sy = y0 + 32 + rr * SLOT
            sel = name == self.selected
            bg = (65, 90, 65) if sel else MID
            pygame.draw.rect(screen, bg, (sx, sy, SLOT - 2, SLOT - 2))
            screen.blit(tex.item_tex(name, 24), (sx + 4, sy + 4))
            pygame.draw.rect(screen, GLD if sel else BRD,
                             (sx, sy, SLOT - 2, SLOT - 2), 1)
            as2 = str(amt) if amt < 1000 else (f"{amt // 1000}k" if amt < 1000000 else f"{amt // 1000000}M")
            txt(screen, F("n"), as2, (sx + 3, sy + SLOT - 15), (255, 255, 255))

    def _detail(self, screen, x0, y0, W, H):
        pygame.draw.rect(screen, MID, (x0, y0, W, H))
        pygame.draw.rect(screen, BRD, (x0, y0, W, H), 1)
        if not self.selected or self.selected not in self.items:
            txt(screen, F("s"), lang.t("inv.select"), (x0 + 10, y0 + 10), (90, 90, 110))
            return
        name = self.selected
        amt = self.items[name]
        col = core.icol(name)
        disp = lang.item(name)
        is2 = 56
        ix = x0 + W // 2 - is2 // 2
        pygame.draw.rect(screen, (40, 40, 58), (ix - 2, y0 + 8, is2 + 4, is2 + 4))
        screen.blit(tex.item_tex(name, is2), (ix - 1, y0 + 9))
        pygame.draw.rect(screen, (200, 200, 220), (ix - 2, y0 + 8, is2 + 4, is2 + 4), 1)
        txt_c(screen, F("m"), disp, (x0 + W // 2, y0 + 70), TXT)
        txt_c(screen, F("b"), str(amt), (x0 + W // 2, y0 + 88), GLD)
        txt(screen, F("n"), lang.t("inv.stack") % core.stack_size(name), (x0 + 10, y0 + 112), (120, 120, 140))
        r = core.RECIPES.get(name)
        if r:
            txt(screen, F("m"), lang.t("inv.recipe"), (x0 + 10, y0 + 138), TXT)
            yy = y0 + 158
            for it, v in r["in"].items():
                have = self.items.get(it, 0)
                c = GRN if have >= v else RED
                screen.blit(tex.item_tex(it, 14), (x0 + 10, yy))
                txt(screen, F("s"), "%s  %d/%d" % (lang.item(it), have, v),
                    (x0 + 28, yy + 2), c)
                yy += 20

    def _t_craft(self, screen, x0, y0, W, H, g):
        qh = 96
        pygame.draw.rect(screen, MID, (x0 + 10, y0 + 4, W - 20, qh))
        pygame.draw.rect(screen, BRD, (x0 + 10, y0 + 4, W - 20, qh), 1)
        txt(screen, F("m"), lang.t("inv.queue"), (x0 + 18, y0 + 8), TXT)
        if not self.craft_q:
            txt(screen, F("s"), lang.t("inv.idle"), (x0 + 18, y0 + 28), (90, 90, 110))
        for i, job in enumerate(self.craft_q[:5]):
            jx = x0 + 18 + i * 190
            jy = y0 + 26
            pct = min(1, job["e"] / max(job["total"], 0.001))
            pygame.draw.rect(screen, (38, 38, 55), (jx, jy, 182, 66))
            screen.blit(tex.item_tex(job["name"], 40), (jx + 4, jy + 4))
            pygame.draw.rect(screen, BRD, (jx, jy, 182, 66), 1)
            txt(screen, F("n"), lang.item(job["name"])[:18], (jx + 50, jy + 6), TXT)
            txt(screen, F("n"), lang.t("inv.left") % int(job["total"] - job["e"]),
                (jx + 50, jy + 20), (160, 160, 160))
            pygame.draw.rect(screen, (25, 25, 38), (jx + 50, jy + 34, 126, 9))
            pygame.draw.rect(screen, GRN, (jx + 50, jy + 34, int(126 * pct), 9))
        # recipe list
        txt(screen, F("m"), lang.t("inv.craft_recipes"), (x0 + 14, y0 + qh + 10), TXT)
        rows = self._craft_list()
        hd = y0 + qh + 30
        for i, name in enumerate(rows):
            if i >= 8:
                break
            r = core.RECIPES[name]
            ok = all(self.has(it, v) for it, v in r["in"].items())
            by = hd + i * 40
            pygame.draw.rect(screen, (34, 38, 52) if ok else (44, 34, 34),
                             (x0 + 14, by, W - 28, 36))
            pygame.draw.rect(screen, BRD, (x0 + 14, by, W - 28, 36), 1)
            screen.blit(tex.item_tex(name, 24), (x0 + 20, by + 4))
            txt(screen, F("s"), lang.item(name), (x0 + 50, by + 4), TXT)
            ix = x0 + 220
            for it, v in r["in"].items():
                have = self.items.get(it, 0)
                c = GRN if have >= v else RED
                screen.blit(tex.item_tex(it, 14), (ix, by + 5))
                txt(screen, F("n"), "%d/%d" % (have, v), (ix + 18, by + 8), c)
                ix += 62
            txt(screen, F("s"), "x%d  %.1fs" % (r["out"], r["t"]), (ix, by + 5), (150, 150, 170))
            cb = (x0 + W - 104, by + 6)
            pygame.draw.rect(screen, (40, 100, 40) if ok else (70, 55, 45), (cb[0], cb[1], 80, 22))
            pygame.draw.rect(screen, BRD, (cb[0], cb[1], 80, 22), 1)
            txt_c(screen, F("s"), lang.t("inv.craft"), (cb[0] + 40, cb[1] + 5),
                  (220, 255, 220) if ok else (150, 130, 120))

    def _t_stats(self, screen, x0, y0, W, H):
        pygame.draw.rect(screen, MID, (x0 + 10, y0 + 4, W - 20, H - 8))
        pygame.draw.rect(screen, BRD, (x0 + 10, y0 + 4, W - 20, H - 8), 1)
        txt(screen, F("m"), lang.t("inv.storage"), (x0 + 18, y0 + 10), TXT)
        items = sorted(self.items.items(), key=lambda kv: -kv[1])
        for i, (k, v) in enumerate(items[:30]):
            yy = y0 + 36 + (i % 10) * 24
            xx = x0 + 18 + (i // 10) * (W // 4 - 30)
            screen.blit(tex.item_tex(k, 14), (xx, yy))
            txt(screen, F("s"), "%s: %d" % (lang.item(k), v), (xx + 18, yy + 2), TXT)

    def _t_equip(self, screen, x0, y0, W, H):
        pygame.draw.rect(screen, MID, (x0 + 10, y0 + 4, W - 20, H - 8))
        pygame.draw.rect(screen, BRD, (x0 + 10, y0 + 4, W - 20, H - 8), 1)
        txt(screen, F("m"), lang.t("inv.equip_title"), (x0 + 18, y0 + 10), TXT)
        ss = 54
        gx, gy = x0 + 40, y0 + 36
        for row in range(5):
            for col in range(5):
                pygame.draw.rect(screen, (38, 38, 54),
                                 (gx + col * (ss + 4), gy + row * (ss + 4), ss, ss))
                pygame.draw.rect(screen, BRD,
                                 (gx + col * (ss + 4), gy + row * (ss + 4), ss, ss), 1)
        eq = ["iron-armor", "heavy-armor", "power-armor", "exoskeleton",
              "night-vision", "energy-shield"]
        ex = gx + 5 * (ss + 4) + 20
        txt(screen, F("s"), lang.t("inv.available"), (ex, gy - 2), (140, 140, 160))
        i = 0
        for name in eq:
            if name in self.items:
                ix, iy = ex, gy + i * 52
                pygame.draw.rect(screen, (38, 38, 54), (ix, iy, 44, 44))
                screen.blit(tex.item_tex(name, 36), (ix + 4, iy + 4))
                pygame.draw.rect(screen, BRD, (ix, iy, 44, 44), 1)
                txt(screen, F("n"), lang.item(name), (ix + 50, iy + 4), TXT)
                txt(screen, F("n"), "x%d" % self.items[name], (ix + 50, iy + 20), GLD)
                i += 1