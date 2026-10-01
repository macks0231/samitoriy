# -*- coding: utf-8 -*-
"""Samitorio v0.4 - main menu, pause menu, settings screen (mouse driven)."""
import math

import pygame

import core
import lang
import settings
import snd
import tex
from core import SW, SH, F, txt, txt_c, BRD, TXT, GRN, RED, GLD, BLU, MID, DARK


class Menu:
    def __init__(self):
        self.mode = "main"  # "main" | "settings" | "pause"
        self._btns = []
        self._hover = None
        self._msg = ""
        self._msg_t = 0.0
        self._t = 0.0
        self._bg = None

    def set_mode(self, mode):
        self.mode = mode
        self._btns = []

    def toast(self, msg):
        self._msg = msg
        self._msg_t = 2.0

    # ── actions ─────────────────────────────────────────────────
    def handle_event(self, event, g):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.mode == "settings":
                    snd.play("click")
                    self.set_mode("main")
                    return ("back", None)
                if self.mode == "pause":
                    snd.play("click")
                    return ("resume", None)
                if self.mode == "main":
                    return ("quit", None)
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                had = self._hover_active()
                if had is not None:
                    return self._run(had)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for rect, key in self.layout():
                if rect.collidepoint(pos):
                    if key in ("vol_sfx", "vol_music"):
                        delta = 0.1 if pos[0] > rect.centerx else -0.1
                        self._bvol(key, delta)
                        snd.play("menu_select")
                        return ("vol", key)
                    snd.play("menu_select")
                    return self._run(key)
        return None

    def _hover_active(self):
        mx, my = pygame.mouse.get_pos()
        for rect, key in self.layout():
            if rect.collidepoint((mx, my)):
                return key
        return None

    def layout(self):
        rows = self._rows_for_mode()
        if self.mode == "main":
            w = 360
            y0 = SH - len(rows) * 54 - 60
            return [(pygame.Rect(SW // 2 - w // 2, y0 + i * 54, w, 44), key)
                    for i, (key, _l) in enumerate(rows)]
        w = 360
        y0 = SH - len(rows) * 52 - 90
        return [(pygame.Rect(SW // 2 - w // 2, y0 + i * 52, w, 42), key)
                for i, (key, _l, *_v) in enumerate(rows)]

    def _rows_for_mode(self):
        if self.mode == "main":
            rows = [("continue", lang.t("menu.continue")),
                    ("new", lang.t("menu.new")),
                    ("settings", lang.t("menu.settings")),
                    ("quit", lang.t("menu.quit"))]
            if not has_save():
                rows = [("new", lang.t("menu.new")),
                        ("settings", lang.t("menu.settings")),
                        ("quit", lang.t("menu.quit"))]
            return rows
        if self.mode == "pause":
            return [("resume", lang.t("pause.resume")),
                    ("save", lang.t("pause.save")),
                    ("settings", lang.t("menu.settings")),
                    ("save_menu", lang.t("pause.save_menu")),
                    ("quit_desk", lang.t("pause.quit"))]
        return [
            ("toggle_lang", lang.t("set.lang"), lang.get().upper()),
            ("toggle_sound", lang.t("set.sound"),
             lang.t("set.on") if settings.get("sound") else lang.t("set.off")),
            ("toggle_music", lang.t("set.music"),
             lang.t("set.on") if settings.get("music") else lang.t("set.off")),
            ("vol_sfx", lang.t("set.sfx_vol"), "%.0f%%" % (settings.get("sfx_vol") * 100)),
            ("vol_music", lang.t("set.music_vol"), "%.0f%%" % (settings.get("music_vol") * 100)),
            ("toggle_fps", lang.t("set.fps"),
             lang.t("set.on") if settings.get("show_fps") else lang.t("set.off")),
            ("back", lang.t("set.back"), ""),
        ]

    def _run(self, key):
        if key == "toggle_lang":
            settings.set("lang", lang.other())
            lang.set(settings.get("lang"))
            return ("changed", None)
        if key == "toggle_sound":
            settings.set("sound", not settings.get("sound"))
            return ("changed", None)
        if key == "toggle_music":
            settings.set("music", not settings.get("music"))
            return ("changed", None)
        if key == "toggle_fps":
            settings.set("show_fps", not settings.get("show_fps"))
            return ("changed", None)
        if key in ("vol_sfx", "vol_music"):
            return None
        return (key, None)

    def _bvol(self, key, delta):
        k = "sfx_vol" if key == "vol_sfx" else "music_vol"
        v = max(0.0, min(1.0, settings.get(k) + delta))
        settings.set(k, round(v, 2))
        return ("changed", None)

    # ── drawing ─────────────────────────────────────────────────
    def draw(self, screen, g):
        self._t += 0.016
        if self._msg_t > 0:
            self._msg_t -= 0.016
        if self.mode == "pause":
            self._draw_pause(screen, g)
            return
        if self.mode == "settings":
            self._draw_settings(screen)
        else:
            self._draw_main(screen)
        self._draw_toast(screen)

    def _draw_bg(self, screen):
        if self._bg is None:
            surf = pygame.Surface((SW, SH))
            for y in range(SH):
                f = y / SH
                r = int(6 + 26 * f)
                c = int(8 + 16 * f)
                col = (r, int(12 + 12 * f), c)
                pygame.draw.line(surf, col, (0, y), (SW, y))
            self._bg = surf
        screen.blit(self._bg, (0, 0))
        # ambient bubbles drifting up
        for i in range(14):
            ph = (self._t * 0.3 + i * 0.61) % 1.0
            x = int((i * 197 + self._t * 12) % SW)
            y = int(SH - ph * (SH + 120))
            a = max(0, int(18 * (0.4 + 0.6 * math.sin(ph * 6.28))))
            col = (80, 110, 150, a)
            surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            surf.fill(col)
            screen.blit(surf, (x, y))

    def _draw_main(self, screen):
        self._draw_bg(screen)
        txt_c(screen, F("b"), lang.t("menu.title"), (SW // 2, 120), (235, 230, 200))
        txt_c(screen, F("s"), "Factorio - like  |  " + lang.t("menu.version"),
              (SW // 2, 146), (150, 150, 170))
        strip = [k for k in ("iron-ore", "copper-ore", "coal", "stone",
                             "iron-plate", "copper-plate", "electronic-circuit")]
        for i, k in enumerate(strip):
            screen.blit(tex.item_tex(k, 40),
                        (SW // 2 - (len(strip) * 46) // 2 + i * 46, 178))
        has = has_save()
        rows = [("continue", lang.t("menu.continue")),
                ("new", lang.t("menu.new")),
                ("settings", lang.t("menu.settings")),
                ("quit", lang.t("menu.quit"))]
        if not has:
            rows = [("new", lang.t("menu.new")),
                    ("settings", lang.t("menu.settings")),
                    ("quit", lang.t("menu.quit"))]
        self._draw_rows(screen, rows)
        if not has:
            txt_c(screen, F("s"), lang.t("menu.no_save"), (SW // 2, SH - 40), (120, 120, 135))

    def _draw_rows(self, screen, rows):
        self._btns = []
        mx, my = pygame.mouse.get_pos()
        for i, (rect, key) in enumerate(self.layout()):
            label = rows[i][1]
            hover = rect.collidepoint((mx, my))
            col = (58, 74, 100) if hover else (34, 40, 62)
            pygame.draw.rect(screen, col, rect, border_radius=6)
            pygame.draw.rect(screen, GLD if hover else (90, 100, 130), rect, 2, border_radius=6)
            txt_c(screen, F("m"), label, rect.center, (255, 245, 220) if hover else (200, 200, 215))
            txt_c(screen, F("s"), str(i + 1), (rect.x - 20, rect.centery - 4), (120, 120, 140))
            self._btns.append((rect, key))

    def _draw_pause(self, screen, g):
        ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ov.fill((6, 8, 14, 170))
        screen.blit(ov, (0, 0))
        txt_c(screen, F("b"), lang.t("menu.title"), (SW // 2, 120), (235, 230, 200))
        rows = [("resume", lang.t("pause.resume")),
                ("save", lang.t("pause.save")),
                ("settings", lang.t("menu.settings")),
                ("save_menu", lang.t("pause.save_menu")),
                ("quit_desk", lang.t("pause.quit"))]
        self._btns = []
        label_by_key = {k: l for k, l in rows}
        mx, my = pygame.mouse.get_pos()
        for rect, key in self.layout():
            hover = rect.collidepoint((mx, my))
            col = (58, 74, 100) if hover else (34, 40, 62)
            pygame.draw.rect(screen, col, rect, border_radius=6)
            pygame.draw.rect(screen, GLD if hover else (90, 100, 130), rect, 2, border_radius=6)
            txt_c(screen, F("m"), label_by_key[key], rect.center,
                  (255, 245, 220) if hover else (200, 200, 215))
            self._btns.append((rect, key))
        if getattr(g, "seed", None) is not None:
            txt_c(screen, F("s"), lang.t("set.seed") % g.seed, (SW // 2, 96), (120, 120, 140))
        self._draw_toast(screen)

    def _draw_settings(self, screen):
        self._draw_bg(screen)
        txt_c(screen, F("b"), lang.t("set.title"), (SW // 2, 90), (235, 230, 200))
        rows = self._rows_for_mode()
        self._btns = []
        mx, my = pygame.mouse.get_pos()
        for rect, key in self.layout():
            row = next(r for r in rows if r[0] == key)
            label, val = row[1], (row[2] if len(row) > 2 else "")
            hover = rect.collidepoint((mx, my))
            col = (58, 74, 100) if hover else (34, 40, 62)
            pygame.draw.rect(screen, col, rect, border_radius=6)
            pygame.draw.rect(screen, GLD if hover else (90, 100, 130), rect, 2, border_radius=6)
            txt(screen, F("m"), label, (rect.x + 14, rect.centery - 8), (230, 228, 215))
            if val:
                txt_c(screen, F("m"), val, (rect.right - 16, rect.centery - 8), (200, 230, 255))
            self._btns.append((rect, key))
        self._draw_toast(screen)

    def _draw_toast(self, screen):
        if self._msg_t > 0 and self._msg:
            a = min(1.0, self._msg_t)
            s = pygame.Surface((SW, 40), pygame.SRCALPHA)
            s.fill((24, 30, 44, int(200 * a)))
            screen.blit(s, (0, 16))
            txt_c(screen, F("m"), self._msg, (SW // 2, 16 + 12), (230, 245, 220))


def has_save():
    import saveload
    return saveload.latest_slot() is not None