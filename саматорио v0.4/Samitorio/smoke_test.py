# -*- coding: utf-8 -*-
"""Headless smoke test: automated mining -> belt -> inserter -> furnace -> assembler."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

import core
import main

pygame.init()
core.init_fonts()

g = main.G()
main.build_game(g, seed=12345)

g.unlocked.update({"automation", "logistics", "steel-proc", "turrets", "electricity"})

# find iron ore near spawn
sx = g.world.W // 2
sy = g.world.H // 2
ore = None
for r in range(3, 15):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            t = g.world.get(sx + dx, sy + dy)
            if t and t.resource == "iron-ore" and t.amount > 0:
                ore = (sx + dx, sy + dy)
                break
        if ore:
            break
    if ore:
        break
assert ore, "no ore found"
ox, oy = ore

# give materials
big = {"iron-plate", "iron-gear-wheel", "stone", "electronic-circuit",
       "copper-plate", "stone-brick", "coal", "iron-ore", "copper-ore",
       "steel-plate", "firearm-magazine", "conveyor-belt", "inserter"}
for itm in big:
    g.inv.add(itm, 200)

# layout: miner -> belt x3 -> inserter -> furnace -> inserter -> belt
assert g.ent.place("miner", ox, oy, g, d=0) == "ok", "miner"
for i in range(3):
    assert g.ent.place("conveyor-belt", ox + 2 + i, oy, g) == "ok", "belt feed"
assert g.ent.place("inserter", ox + 5, oy, g, d=0) == "ok", "inserter feed"
assert g.ent.place("furnace", ox + 6, oy, g) == "ok", "furnace"
assert g.ent.place("inserter", ox + 8, oy, g, d=0) == "ok", "inserter pull"
assert g.ent.place("conveyor-belt", ox + 9, oy, g) == "ok", "belt out"

# assembler for red science
ax, ay = ox + 2, oy - 5
assert g.ent.place("assembler", ax, ay, g, recipe="automation-science-pack") == "ok", "assembler"

# sim phases, track vein depletion speed
STEPS = int(100 / (1 / 30))
sim_s = 0
vein_phase = []
for i in range(STEPS):
    dt = 1 / 30
    sim_s += dt
    g.t += dt
    g.ent.update(dt, g)
    g.inv.update(dt, g)
vein_phase.append(round(g.world.get(ox, oy).amount, 1))

import entities as ent_mod  # noqa

miner = g.ent.cell_at(ox, oy)
furnace = g.ent.cell_at(ox + 6, oy)
asm = g.ent.cell_at(ax, ay)
out_belt = g.ent.cell_at(ox + 9, oy)
f_plates = furnace.outb.get("iron-plate", 0)
belt_items = sum(1 for s in out_belt.slots if s)

print("vein amount after 100s:", vein_phase[0], "(miner drain 0.5/s)")
print("furnace plates:", f_plates)
print("out belt items:", belt_items)
assert f_plates > 5, "furnace smelted nothing"
assert out_belt.peek() is not None, "output belt got nothing"
assert vein_phase[0] < 3000, "miner did not drain the vein"

# feed assembler directly and verify it produces science packs
for _ in range(40):
    asm.push("iron-gear-wheel")
    asm.push("copper-plate")
for i in range(int(40 / (1 / 30))):
    g.t += 1 / 30
    g.ent.update(1 / 30, g)
asm_packs = asm.outb.get("automation-science-pack", 0)
print("assembler packs:", asm_packs)
assert asm_packs >= 2, "assembler produced too few packs"

# research + assembly test
g.inv.add("automation-science-pack", 30)
r = g.research
assert r.start("automation"), "research start failed"
for _ in range(int(50 / (1 / 30))):
    g.t += 1 / 30
    r.update(1 / 30, g)
    g.ent.update(1 / 30, g)
    g.inv.update(1 / 30, g)
print("automation researched:", r.techs["automation"]["done"])
assert r.techs["automation"]["done"], "automation research did not complete"

# ── save / load round-trip ──────────────────────────────────────────
import saveload
g1 = main.G()
main.build_game(g1, seed=12345)
g1.unlocked.update(g.unlocked)
for itm in big:
    g1.inv.add(itm, 200)
g1.ent.place("miner", ox, oy, g1, d=0)
g1.ent.place("furnace", ox + 6, oy, g1)
g1.inv.add("automation-science-pack", 30)
assert g1.research.start("automation")
for _ in range(int(40 / (1 / 30))):
    g1.t += 1 / 30
    g1.ent.update(1 / 30, g1)
    g1.inv.update(1 / 30, g1)
    g1.research.update(1 / 30, g1)
before = {
    "t": round(g1.t, 2), "hp": g1.player.hp, "inv": dict(g1.inv.items),
    "furnace": g1.ent.cell_at(ox + 6, oy).buf if g1.ent.cell_at(ox + 6, oy) else None,
    "res_done": g1.research.techs["automation"]["done"],
    "slot_items": dict(g1.inv.items),
}
assert saveload.save_game(g1, "slot1"), "save failed"
g2 = main.G()
main.build_game(g2, seed=2233)
assert saveload.load_data("slot1"), "load_data failed"
saveload.apply(g2, saveload.load_data("slot1"))
after = {
    "t": round(g2.t, 2), "hp": g2.player.hp, "inv": dict(g2.inv.items),
    "furnace": g2.ent.cell_at(ox + 6, oy).buf if g2.ent.cell_at(ox + 6, oy) else None,
    "res_done": g2.research.techs["automation"]["done"],
    "slot_items": dict(g2.inv.items),
}
assert round(before["t"], 1) == round(after["t"], 1), "time mismatch"
assert before["hp"] == after["hp"], "hp mismatch"
assert before["inv"] == after["inv"], "inventory mismatch"
assert before["res_done"] == after["res_done"], "research mismatch"
assert g2.seed == 12345, "seed mismatch"
print("SAVE/LOAD ROUND-TRIP PASSED")

print("SMOKE TEST PASSED")
pygame.quit()