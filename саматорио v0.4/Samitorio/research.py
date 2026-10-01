# -*- coding: utf-8 -*-
"""Samitorio v0.4 - research: flasks consumed, unlocks gated."""
import pygame

import core
import lang
import snd
import tex
from core import F, txt, txt_c, GRN, RED, GLD, BRD, MID, TXT


class ResearchTree:
    def __init__(self, inv, unlocked_set):
        self.inv = inv
        self.unl = unlocked_set
        self.visible = False
        self.techs = {k: {"done": False, "prog": 0.0, "data": v}
                      for k, v in core.TECH.items()}
        self.current = None

    def toggle(self):
        self.visible = not self.visible

    def _deps_ok(self, data):
        return all(self.techs[d]["done"] for d in data["deps"])

    def start(self, name):
        t = self.techs.get(name)
        if not t or t["done"] or self.current is not None:
            return False
        if not self._deps_ok(t["data"]):
            return False
        for flask, amt in t["data"]["cost"].items():
            if not self.inv.has(flask, amt):
                return False
        for flask, amt in t["data"]["cost"].items():
            self.inv.remove(flask, amt)
        self.current = name
        return True

    def update(self, dt, g):
        if not self.current:
            return
        t = self.techs[self.current]
        labs = g.ent.count_type("lab")
        t["prog"] += dt * 0.02 * (1.0 + labs * 0.4)
        if t["prog"] >= 1.0:
            t["done"] = True
            t["prog"] = 1.0
            self.unl.add(self.current)
            self.current = None
            snd.play("research")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            self.toggle()
            return True
        if not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._click(event.pos)
        return True

    def _click(self, pos):
        x0 = (core.SW - 760) // 2
        y0 = (core.SH - 520) // 2
        for i, (name, t) in enumerate(self.techs.items()):
            col = i % 4
            row = i // 4
            if t["done"] or self.current == name:
                continue
            br = pygame.Rect(x0 + 18 + col * 186 + 90, y0 + 40 + row * 130 + 90, 88, 18)
            if br.collidepoint(pos):
                self.start(name)

    def draw(self, screen, g):
        if not self.visible:
            return
        W, H = 760, 520
        x0 = (core.SW - W) // 2
        y0 = (core.SH - H) // 2
        bg = pygame.Surface((W, H), pygame.SRCALPHA)
        bg.fill((20, 20, 35, 226))
        screen.blit(bg, (x0, y0))
        pygame.draw.rect(screen, BRD, (x0, y0, W, H), 2)
        txt(screen, F("b"), lang.t("res.title"), (x0 + 12, y0 + 8), TXT)
        doing = self.current
        if doing:
            t = self.techs[doing]
            txt(screen, F("s"), lang.t("res.ing") %
                (lang.tech(doing), t["prog"] * 100), (x0 + 12, y0 + 28), GLD)
        for i, (name, t) in enumerate(self.techs.items()):
            col = i % 4
            row = i // 4
            bx = x0 + 18 + col * 186
            by = y0 + 46 + row * 130
            can = self._deps_ok(t["data"]) and not t["done"] and self.current is None
            bc = (28, 70, 28) if t["done"] else ((58, 58, 18) if self.current == name else
                                                  (40, 40, 60) if can else (34, 34, 40))
            pygame.draw.rect(screen, bc, (bx, by, 176, 116))
            pygame.draw.rect(screen, BRD, (bx, by, 176, 116), 1)
            txt(screen, F("s"), lang.tech(name), (bx + 6, by + 4), TXT)
            txt(screen, F("n"), lang.tech_desc(name)[:26], (bx + 6, by + 22), (140, 140, 160))
            j = 0
            for flask, amt in t["data"]["cost"].items():
                have = self.inv.items.get(flask, 0)
                c = GRN if have >= amt else RED
                screen.blit(tex.item_tex(flask, 12), (bx + 6, by + 40 + j * 19))
                txt(screen, F("n"), "%d/%d" % (have, amt), (bx + 22, by + 42 + j * 19), c)
                j += 1
            pygame.draw.rect(screen, (40, 40, 40), (bx + 6, by + 98, 164, 10))
            pygame.draw.rect(screen, GRN, (bx + 6, by + 98, int(164 * t["prog"]), 10))
            if not t["done"] and self.current != name:
                if can:
                    pygame.draw.rect(screen, (40, 120, 40), (bx + 116, by + 4, 54, 16))
                    txt(screen, F("n"), lang.t("res.start"), (bx + 124, by + 6), (220, 255, 220))
                else:
                    txt(screen, F("n"), lang.t("res.locked"), (bx + 116, by + 6), (120, 110, 100))