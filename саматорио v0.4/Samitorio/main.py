# -*- coding: utf-8 -*-
"""Samitorio v0.4 - main loop, scene state machine (menu/game/pause/settings)."""
import random
import traceback

import pygame

import core
from core import SW, SH, FPS

import world as world_mod
import entities
import inventory as inv_mod
import player as player_mod
import power as power_mod
import research as res_mod
import combat as combat_mod
import lighting as light_mod
import ui as ui_mod

import lang
import settings
import snd
import saveload
from menu import Menu

DAY_F, NIGHT_F = 1800, 900


class G:
    def __init__(self):
        self.t = 0.0
        self.tick = 0
        self.fps = 0
        self.world = None
        self.game_over = False


class Camera:
    def __init__(self):
        self.ox = 0.0
        self.oy = 0.0

    def update(self, p):
        self.ox = p.x - SW / 2
        self.oy = p.y - SH / 2


def build_game(g, seed=12345):
    g.world = world_mod.World(192, 192, seed=seed)
    g.unlocked = set()
    g.inv = inv_mod.Inventory(g.unlocked)
    g.player = player_mod.Player(g.world.spawn_x, g.world.spawn_y)
    g.cam = Camera()
    g.power = power_mod.PowerGrid()
    g.ent = entities.Entities(g.world, g.power)
    g.combat = combat_mod.Combat(g.world, g.player)
    g.research = res_mod.ResearchTree(g.inv, g.unlocked)
    g.ui = ui_mod.UI()
    g.lighting = light_mod.Lighting()
    g.is_day = True
    g.tod = 0
    g.clen = DAY_F
    g.todp = 0.0
    g.day_p = 1.0
    g.t = 0.0
    g.tick = 0
    g.fps = 0
    g.score = 0
    g.game_over = False
    g.seed = seed


def new_game(g, seed=None):
    seed = random.randint(0, 2 ** 31 - 1) if seed is None else int(seed)
    build_game(g, seed)
    return seed


def load_saved(g, name=None):
    if name is None:
        name = saveload.latest_slot() or saveload.AUTOSAVE_SLOT
    data = saveload.load_data(name)
    if not data:
        return False
    build_game(g, data.get("seed", 0))
    g.seed = data.get("seed", 0)
    saveload.apply(g, data)
    return True


def save_autosave(g):
    saveload.save_game(g, saveload.AUTOSAVE_SLOT)


def run(max_frames=None, start_state="menu", g=None):
    try:
        pygame.mixer.pre_init(snd.SR, -16, 1, 512)
    except Exception:
        pass
    pygame.init()
    core.init_fonts()
    snd.init()
    settings.load()
    lang.set(settings.get("lang"))
    snd.apply(settings)

    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption("Samitorio v0.4")
    clock = pygame.time.Clock()

    if g is None:
        g = G()
    menu = Menu()
    state = start_state if start_state in ("menu", "game") else "menu"
    prev_state = "menu"
    if state == "game":
        if not hasattr(g, "world"):
            new_game(g)
        menu.set_mode("pause")
    else:
        menu.set_mode("main")

    running = True
    autosave_min = -1
    while running:
        dt = min(0.05, clock.tick(FPS) / 1000.0)
        g.fps = clock.get_fps()
        in_scene = state in ("menu", "settings", "pause")

        # ── events ───────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if not in_scene and state == "game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    snd.play("click")
                    state = "pause"
                    menu.set_mode("pause")
                    continue
                handled = g.inv.handle_event(event, g)
                if not handled:
                    handled = g.research.handle_event(event)
                if not handled and not g.inv.visible and not g.research.visible:
                    g.ui.handle_event(event, g)
            else:
                action = menu.handle_event(event, g)
                if action:
                    act = action[0]
                    if act == "new":
                        new_game(g)
                        save_autosave(g)
                        state, prev_state = "game", "menu"
                        menu.set_mode("pause")
                    elif act == "continue":
                        if load_saved(g):
                            state, prev_state = "game", "menu"
                            menu.set_mode("pause")
                    elif act == "settings":
                        prev_state, state = state, "settings"
                        menu.set_mode("settings")
                    elif act == "back":
                        state = prev_state
                        menu.set_mode("pause" if state == "pause" else "main")
                        if state == "menu":
                            prev_state = "menu"
                    elif act == "resume":
                        state = "game"
                    elif act == "save":
                        if saveload.save_game(g, "slot1"):
                            menu.toast(lang.t("set.saved"))
                    elif act == "save_menu":
                        saveload.save_game(g, "slot1")
                        state, prev_state = "menu", "menu"
                        menu.set_mode("main")
                    elif act == "quit_desk" or act == "quit":
                        running = False
                    elif act == "changed":
                        lang.set(settings.get("lang"))
                        snd.apply(settings)
                    elif act in ("vol", "vol_sfx", "vol_music"):
                        snd.apply(settings)

        # ── updates (game only) ──────────────────────────────────
        if state == "game":
            keys = pygame.key.get_pressed()
            if not g.inv.visible and not g.research.visible:
                g.player.update(keys, g, dt)
            g.cam.update(g.player)
            g.t += dt
            g.tick += 1
            g.todp = g.tod / g.clen
            g.day_p = 1.0 if g.is_day else 0.1

            g.ent.update(dt, g)
            g.combat.update(dt, g, g.tick)
            g.power.update(dt, g)
            g.research.update(dt, g)
            g.inv.update(dt, g)
            g.ui.update(g)
            if snd._ok and settings.get("music") and not snd._music_playing:
                snd.music_play()

            g.tod += 1
            if g.tod >= g.clen:
                g.tod = 0
                g.is_day = not g.is_day
                g.clen = DAY_F if g.is_day else NIGHT_F
                if not g.is_day:
                    g.combat.night_bonus = True
                    snd.play("wave")

            if g.tick % (FPS * 5) == 0:
                g.world.spread_pollution()

            am = int(g.t) // 60
            if am != autosave_min:
                autosave_min = am
                save_autosave(g)

        # ── drawing ──────────────────────────────────────────────
        screen.fill((0, 0, 0))
        if state in ("game", "pause"):
            g.world.draw(screen, g.cam)
            g.ent.draw(screen, g.cam, g)
            g.combat.draw(screen, g.cam, g)
            if not g.game_over:
                g.player.draw(screen, g, g.is_day)
            g.lighting.draw(screen, g.is_day, g.todp, g)
            g.ui.draw(screen, g)
            g.inv.draw(screen, g)
            g.research.draw(screen, g)
            if state == "pause":
                menu.draw(screen, g)
        else:
            menu.draw(screen, g)

        if max_frames is not None and g.tick >= max_frames and state == "game":
            running = False

        pygame.display.flip()

    if state in ("game", "pause"):
        save_autosave(g)
    snd.shutdown()
    pygame.quit()


def main():
    try:
        run()
    except SystemExit:
        raise
    except Exception:
        err = traceback.format_exc()
        pygame.init()
        core.init_fonts()
        screen = pygame.display.set_mode((900, 460))
        pygame.display.set_caption("Samitorio - Error")
        screen.fill((20, 0, 0))
        y = 10
        fbig = pygame.font.SysFont("Courier New", 13)
        fa = pygame.font.SysFont("Arial", 12)
        for line in err.splitlines():
            screen.blit(fbig.render(line[:118], True, (255, 120, 120)), (10, y))
            y += 17
            if y > 420:
                break
        screen.blit(fa.render("Press any key to exit.", True, (200, 200, 200)), (10, 430))
        pygame.display.flip()
        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type in (pygame.QUIT, pygame.KEYDOWN):
                    waiting = False
        pygame.quit()
        raise SystemExit(1)


if __name__ == "__main__":
    main()