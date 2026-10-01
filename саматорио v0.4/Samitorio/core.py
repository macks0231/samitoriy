# -*- coding: utf-8 -*-
"""Samitorio v0.3 - core data: constants, items, recipes, tech, buildings."""
import random
import pygame

TILE, SW, SH, FPS = 32, 1280, 720, 1500

# directions: 0=E 1=S 2=W 3=N
DX = [1, 0, -1, 0]
DY = [0, 1, 0, -1]
OPP = [2, 3, 0, 1]

DARK, MID, LIGHT = (22, 22, 30), (35, 35, 48), (55, 55, 72)
BRD, TXT = (85, 85, 110), (220, 220, 240)
GRN, RED, GLD, BLU = (60, 200, 80), (210, 70, 60), (230, 190, 50), (80, 160, 255)
ORG, CYAN = (255, 150, 50), (80, 220, 255)

# ── Biomes ──────────────────────────────────────────────────────
(BIOME_PLAINS, BIOME_ASHLANDS, BIOME_SWAMP,
 BIOME_WASTELAND, BIOME_PERMAFROST, BIOME_BARREN,
 BIOME_THICKET, BIOME_RIDGE) = range(8)

BIOME_COL = {0: (62, 128, 58), 1: (98, 92, 84), 2: (74, 104, 58),
             3: (78, 72, 64), 4: (170, 200, 220), 5: (190, 170, 118),
             6: (34, 96, 34), 7: (108, 102, 96)}
BIOME_BASE = {0: (48, 108, 46), 1: (84, 78, 70), 2: (60, 90, 46),
              3: (64, 58, 50), 4: (158, 188, 210), 5: (180, 158, 104),
              6: (26, 82, 26), 7: (96, 90, 84)}
BIOME_NAME = {0: "Plains", 1: "Ashlands", 2: "Swamp", 3: "Wasteland",
              4: "Permafrost", 5: "Barren", 6: "Thicket", 7: "Ridge"}
BIOME_RES = {0: ["iron-ore", "copper-ore", "coal", "stone"],
             1: ["coal", "stone", "sulfur", "calcite"],
             2: ["iron-ore", "coal", "wood"],
             3: ["scrap", "iron-ore", "rare-ore"],
             4: ["uranium-ore", "cryo-ore", "stone"],
             5: ["oil", "copper-ore", "rare-ore"],
             6: ["wood", "iron-ore", "coal"],
             7: ["stone", "iron-ore", "rare-ore", "tungsten-ore"]}

# ── Items ───────────────────────────────────────────────────────
ITEMS = {
    "iron-ore":        ("Iron Ore",            (150, 150, 160)),
    "copper-ore":      ("Copper Ore",          (200, 110, 55)),
    "coal":            ("Coal",                (45, 45, 45)),
    "stone":           ("Stone",               (155, 145, 125)),
    "uranium-ore":     ("Uranium Ore",         (90, 220, 70)),
    "oil":             ("Crude Oil",           (35, 35, 30)),
    "sulfur":          ("Sulfur",              (225, 225, 50)),
    "calcite":         ("Calcite",             (240, 230, 210)),
    "scrap":           ("Scrap Metal",         (105, 105, 105)),
    "rare-ore":        ("Rare Ore",            (215, 185, 40)),
    "tungsten-ore":    ("Tungsten Ore",        (95, 85, 175)),
    "cryo-ore":        ("Cryo Crystal",        (160, 230, 255)),
    "wood":            ("Wood",                (150, 92, 30)),
    "iron-plate":      ("Iron Plate",          (175, 175, 185)),
    "copper-plate":    ("Copper Plate",        (215, 140, 65)),
    "steel-plate":     ("Steel Plate",         (150, 160, 180)),
    "stone-brick":     ("Stone Brick",         (195, 175, 145)),
    "iron-gear-wheel": ("Iron Gear Wheel",     (168, 168, 172)),
    "iron-stick":      ("Iron Stick",          (160, 160, 170)),
    "copper-cable":    ("Copper Cable",        (225, 150, 65)),
    "electronic-circuit": ("Electronic Circuit", (30, 190, 90)),
    "advanced-circuit":   ("Advanced Circuit",   (210, 65, 65)),
    "processing-unit":    ("Processing Unit",    (55, 95, 215)),
    "plastic-bar":     ("Plastic Bar",         (230, 230, 200)),
    "battery":         ("Battery",             (95, 95, 245)),
    "automation-science-pack": ("Automation Science Pack", (235, 60, 60)),
    "logistic-science-pack":   ("Logistic Science Pack",   (60, 215, 60)),
    "military-science-pack":   ("Military Science Pack",   (90, 90, 215)),
    "chemical-science-pack":   ("Chemical Science Pack",   (90, 215, 235)),
    "production-science-pack": ("Production Science Pack", (175, 60, 215)),
    "utility-science-pack":    ("Utility Science Pack",    (235, 205, 50)),
    "conveyor-belt":   ("Conveyor Belt",       (215, 185, 50)),
    "fast-belt":       ("Fast Belt",           (220, 140, 25)),
    "inserter":        ("Inserter",            (215, 135, 45)),
    "fast-inserter":   ("Fast Inserter",       (70, 190, 70)),
    "gun-turret":      ("Gun Turret",          (175, 50, 50)),
    "laser-turret":    ("Laser Turret",        (50, 175, 235)),
    "wall":            ("Stone Wall",          (175, 165, 150)),
    "lamp":            ("Lamp",                (255, 255, 210)),
    "rail":            ("Rail",                (115, 115, 125)),
    "firearm-magazine":("Firearm Magazine",    (215, 215, 60)),
    "iron-armor":      ("Iron Armor",          (175, 175, 185)),
    "heavy-armor":     ("Heavy Armor",         (115, 125, 145)),
    "power-armor":     ("Power Armor",         (70, 110, 215)),
    "exoskeleton":     ("Exoskeleton",         (90, 215, 130)),
    "night-vision":    ("Night Vision",        (90, 215, 170)),
    "energy-shield":   ("Energy Shield",       (70, 150, 255)),
    "solar-panel":     ("Solar Panel",         (45, 80, 180)),
    "coal-gen":        ("Boiler",              (120, 95, 90)),
    "laser-beam":      ("Laser Beam",          (100, 230, 255)),
}


def iname(k):
    return ITEMS.get(k, (k, None))[0]


def icol(k):
    return ITEMS.get(k, ("?", (180, 180, 180)))[1]


def stack_size(k):
    if k.endswith("ore") or k == "coal" or k == "stone":
        return 200
    if k in ("iron-plate", "copper-plate", "steel-plate", "stone-brick"):
        return 100
    return 50


RAW = {"iron-ore", "copper-ore", "coal", "stone", "uranium-ore",
       "sulfur", "calcite", "scrap", "rare-ore", "tungsten-ore",
       "cryo-ore", "wood", "oil"}

# ── Recipes ─────────────────────────────────────────────────────
# craft: "hand" | "furnace" | "asm"
RECIPES = {
    "iron-gear-wheel":  {"in": {"iron-plate": 2}, "out": 1, "t": 0.5, "craft": "hand"},
    "iron-stick":       {"in": {"iron-plate": 1}, "out": 2, "t": 0.5, "craft": "hand"},
    "copper-cable":     {"in": {"copper-plate": 1}, "out": 2, "t": 0.5, "craft": "hand"},
    "electronic-circuit": {"in": {"iron-plate": 1, "copper-cable": 3},
                          "out": 1, "t": 0.5, "craft": "hand"},
    "conveyor-belt":    {"in": {"iron-plate": 1, "iron-gear-wheel": 1},
                         "out": 2, "t": 0.5, "craft": "hand", "req": "automation"},
    "inserter":         {"in": {"iron-plate": 1, "iron-gear-wheel": 1, "electronic-circuit": 1},
                         "out": 1, "t": 0.5, "craft": "hand", "req": "automation"},
    "firearm-magazine": {"in": {"iron-plate": 4}, "out": 1, "t": 1.0, "craft": "hand"},
    "wall":             {"in": {"stone-brick": 5}, "out": 1, "t": 0.5,
                         "craft": "hand", "req": "turrets"},
    "stone-brick":      {"in": {"stone": 2}, "out": 1, "t": 3.0, "craft": "furnace"},
    "iron-plate":       {"in": {"iron-ore": 1}, "out": 1, "t": 3.5, "craft": "furnace"},
    "copper-plate":     {"in": {"copper-ore": 1}, "out": 1, "t": 3.5, "craft": "furnace"},
    "steel-plate":      {"in": {"iron-plate": 5}, "out": 1, "t": 16.0,
                         "craft": "furnace", "req": "steel-proc"},
    "fast-belt":        {"in": {"iron-gear-wheel": 5, "iron-plate": 1},
                         "out": 1, "t": 0.5, "craft": "asm", "req": "logistics"},
    "fast-inserter":    {"in": {"electronic-circuit": 2, "inserter": 1},
                         "out": 1, "t": 0.5, "craft": "asm", "req": "logistics"},
    "advanced-circuit": {"in": {"electronic-circuit": 2, "copper-cable": 4, "plastic-bar": 2},
                         "out": 1, "t": 6.0, "craft": "asm", "req": "advanced"},
    "plastic-bar":      {"in": {"coal": 1}, "out": 2, "t": 1.0, "craft": "asm"},
    "battery":          {"in": {"iron-plate": 1, "copper-plate": 1, "sulfur": 1},
                         "out": 1, "t": 4.0, "craft": "asm", "req": "advanced"},
    "processing-unit":  {"in": {"electronic-circuit": 20, "advanced-circuit": 2},
                         "out": 1, "t": 10.0, "craft": "asm", "req": "advanced"},
    "gun-turret":       {"in": {"iron-plate": 10, "iron-gear-wheel": 5, "copper-plate": 10},
                         "out": 1, "t": 8.0, "craft": "asm", "req": "turrets"},
    "laser-turret":     {"in": {"steel-plate": 12, "advanced-circuit": 10, "battery": 4},
                         "out": 1, "t": 12.0, "craft": "asm", "req": "military"},
    "rail":             {"in": {"stone": 1, "steel-plate": 1, "iron-stick": 1},
                         "out": 2, "t": 0.5, "craft": "asm", "req": "railways"},
    "automation-science-pack": {"in": {"iron-gear-wheel": 1, "copper-plate": 1},
                                "out": 1, "t": 20.0, "craft": "hand"},
    "logistic-science-pack":   {"in": {"inserter": 1, "conveyor-belt": 1},
                                "out": 1, "t": 6.0, "craft": "asm", "req": "automation"},
    "military-science-pack":   {"in": {"firearm-magazine": 1, "wall": 1},
                                "out": 1, "t": 6.0, "craft": "asm", "req": "turrets"},
    "solar-panel":     {"in": {"copper-plate": 5, "steel-plate": 5, "electronic-circuit": 5},
                        "out": 1, "t": 4.0, "craft": "asm", "req": "electricity"},
}

SMELT = {"iron-ore": "iron-plate", "copper-ore": "copper-plate",
         "stone": "stone-brick", "iron-plate": "steel-plate"}

# ── Tech ────────────────────────────────────────────────────────
TECH = {
    "automation": {"cost": {"automation-science-pack": 20}, "deps": [],
                   "desc": "Belts, inserters, miners, assemblers"},
    "logistics":  {"cost": {"automation-science-pack": 30}, "deps": ["automation"],
                   "desc": "Fast belts, fast inserters"},
    "steel-proc": {"cost": {"automation-science-pack": 30}, "deps": ["automation"],
                   "desc": "Steel smelting"},
    "electricity": {"cost": {"automation-science-pack": 40, "logistic-science-pack": 20},
                    "deps": ["automation"], "desc": "Solar panels, lamps"},
    "turrets":    {"cost": {"automation-science-pack": 40, "logistic-science-pack": 20},
                   "deps": ["automation"], "desc": "Walls and gun turrets"},
    "advanced":   {"cost": {"automation-science-pack": 40, "logistic-science-pack": 40},
                   "deps": ["logistics"], "desc": "Advanced circuits, batteries"},
    "military":   {"cost": {"logistic-science-pack": 40, "military-science-pack": 30},
                   "deps": ["turrets"], "desc": "Laser turrets"},
    "railways":   {"cost": {"automation-science-pack": 60, "logistic-science-pack": 40},
                   "deps": ["steel-proc"], "desc": "Rails"},
}

ITEM_REQ = {}
for _r, _d in RECIPES.items():
    if "req" in _d:
        ITEM_REQ[_r] = _d["req"]


def unlocked(item, uset):
    return ITEM_REQ.get(item) is None or ITEM_REQ[item] in uset

# ── Buildings ───────────────────────────────────────────────────
BLDG_DEFS = {
    "miner":     {"col": (175, 150, 60), "w": 2, "h": 2,
                  "cost": {"iron-plate": 6, "iron-gear-wheel": 2},
                  "poll": 0.6, "pw_use": 90, "pw_gen": 0, "light": False, "lr": 0,
                  "req": "automation", "cat": "production", "hp": 220},
    "furnace":   {"col": (210, 95, 40), "w": 2, "h": 2,
                  "cost": {"stone": 10},
                  "poll": 1.0, "pw_use": 20, "pw_gen": 0, "light": True, "lr": 40,
                  "req": None, "cat": "production", "hp": 180},
    "assembler": {"col": (70, 110, 190), "w": 3, "h": 3,
                  "cost": {"iron-plate": 9, "iron-gear-wheel": 5, "electronic-circuit": 3},
                  "poll": 0.3, "pw_use": 150, "pw_gen": 0, "light": False, "lr": 0,
                  "req": "automation", "cat": "production", "hp": 260},
    "lab":       {"col": (130, 45, 170), "w": 3, "h": 3,
                  "cost": {"iron-plate": 10, "iron-gear-wheel": 10, "electronic-circuit": 5},
                  "poll": 0, "pw_use": 60, "pw_gen": 0, "light": True, "lr": 30,
                  "req": "automation", "cat": "production", "hp": 200},
    "conveyor-belt": {"col": (215, 185, 50), "w": 1, "h": 1,
                  "cost": {"iron-plate": 1, "iron-gear-wheel": 1},
                  "poll": 0, "pw_use": 0, "pw_gen": 0, "light": False, "lr": 0,
                  "req": "automation", "cat": "logistics", "hp": 120},
    "fast-belt": {"col": (220, 140, 25), "w": 1, "h": 1,
                  "cost": {"iron-plate": 1, "iron-gear-wheel": 5},
                  "poll": 0, "pw_use": 0, "pw_gen": 0, "light": False, "lr": 0,
                  "req": "logistics", "cat": "logistics", "hp": 120},
    "inserter":  {"col": (215, 135, 45), "w": 1, "h": 1,
                  "cost": {"iron-plate": 1, "iron-gear-wheel": 1, "electronic-circuit": 1},
                  "poll": 0, "pw_use": 13, "pw_gen": 0, "light": False, "lr": 0,
                  "req": "automation", "cat": "logistics", "hp": 120},
    "fast-inserter": {"col": (70, 190, 70), "w": 1, "h": 1,
                  "cost": {"electronic-circuit": 2, "inserter": 1},
                  "poll": 0, "pw_use": 23, "pw_gen": 0, "light": False, "lr": 0,
                  "req": "logistics", "cat": "logistics", "hp": 120},
    "coal-gen":  {"col": (120, 95, 90), "w": 3, "h": 2,
                  "cost": {"stone": 10, "iron-plate": 10},
                  "poll": 3.0, "pw_use": 0, "pw_gen": 500, "light": True, "lr": 35,
                  "req": "automation", "cat": "power", "hp": 220},
    "solar-panel": {"col": (45, 80, 180), "w": 3, "h": 3,
                  "cost": {"copper-plate": 5, "steel-plate": 5},
                  "poll": 0, "pw_use": 0, "pw_gen": 60, "light": False, "lr": 0,
                  "req": "electricity", "cat": "power", "hp": 140},
    "lamp":      {"col": (255, 255, 200), "w": 1, "h": 1,
                  "cost": {"iron-plate": 1, "electronic-circuit": 1},
                  "poll": 0, "pw_use": 5, "pw_gen": 0, "light": True, "lr": 55,
                  "req": "electricity", "cat": "power", "hp": 100},
    "wall":      {"col": (175, 165, 150), "w": 1, "h": 1,
                  "cost": {"stone-brick": 5},
                  "poll": 0, "pw_use": 0, "pw_gen": 0, "light": False, "lr": 0,
                  "req": "turrets", "cat": "defense", "hp": 600},
    "gun-turret": {"col": (175, 50, 50), "w": 2, "h": 2,
                  "cost": {"iron-plate": 10, "iron-gear-wheel": 5, "copper-plate": 10},
                  "poll": 0, "pw_use": 0, "pw_gen": 0, "light": True, "lr": 25,
                  "req": "turrets", "cat": "defense", "hp": 300},
    "laser-turret": {"col": (50, 175, 235), "w": 2, "h": 2,
                  "cost": {"steel-plate": 12, "advanced-circuit": 10, "battery": 4},
                  "poll": 0, "pw_use": 25, "pw_gen": 0, "light": True, "lr": 30,
                  "req": "military", "cat": "defense", "hp": 320},
}

BUILD_ORDER = ["miner", "furnace", "assembler", "lab",
               "conveyor-belt", "fast-belt", "inserter", "fast-inserter",
               "coal-gen", "solar-panel", "lamp", "wall",
               "gun-turret", "laser-turret"]


def bldg_unlocked(k, uset):
    d = BLDG_DEFS[k]
    return d["req"] is None or d["req"] in uset

# ── Enemies ─────────────────────────────────────────────────────
ENEMY_TYPES = {
    "small":  {"hp": 40, "spd": 78, "dmg": 5, "sz": 8, "col": (215, 55, 55), "xp": 10},
    "medium": {"hp": 120, "spd": 55, "dmg": 15, "sz": 12, "col": (215, 85, 40), "xp": 25},
    "armored": {"hp": 300, "spd": 35, "dmg": 25, "sz": 15, "col": (105, 55, 185), "xp": 50},
    "flyer":  {"hp": 60, "spd": 120, "dmg": 10, "sz": 9, "col": (55, 185, 205), "xp": 30},
    "boss":   {"hp": 2000, "spd": 25, "dmg": 60, "sz": 28, "col": (190, 0, 190), "xp": 500},
}

# ── Font helpers ───────────────────────────────────────────────────
_fn = _fs = _fm = _fb = None


def init_fonts():
    global _fn, _fs, _fm, _fb
    _fn = pygame.font.SysFont("Arial", 10)
    _fs = pygame.font.SysFont("Arial", 12)
    _fm = pygame.font.SysFont("Arial", 14, bold=True)
    _fb = pygame.font.SysFont("Arial", 17, bold=True)


def txt(surf, font, text, pos, col):
    surf.blit(font.render(text, True, col), pos)


def txt_c(surf, font, text, pos, col):
    r = font.render(text, True, col)
    surf.blit(r, (pos[0] - r.get_width() // 2, pos[1]))


def F(s):
    return {"n": _fn, "s": _fs, "m": _fm, "b": _fb}[s]