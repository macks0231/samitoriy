# -*- coding: utf-8 -*-
"""Samitorio v0.4 - save / load (zlib+json), world & entity serialization."""
import json
import os
import zlib

import core
from core import TILE
from world import World
from player import Player
from entities import Belt, Inserter, Building
from combat import Enemy

_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(_DIR, "saves")

NEWGAME_SLOT = "slot1"
AUTOSAVE_SLOT = "autosave"


def _path(name):
    return os.path.join(SAVE_DIR, name + ".sz")


# ── world ───────────────────────────────────────────────────────────
def _world_to_list(w):
    rows = []
    for y in range(w.H):
        row = []
        for x in range(w.W):
            t = w.tiles[y][x]
            row.append([t.biome, t.resource, t.amount, t.rock, t.pollution])
        rows.append(row)
    return rows


def _world_from_list(w, rows):
    for y in range(w.H):
        row = w.tiles[y]
        src = rows[y]
        for x in range(w.W):
            t = row[x]
            b, res, amt, rock, pol = src[x]
            t.biome = b
            t.resource = res
            t.amount = amt
            t.rock = rock
            t.pollution = pol
            t.cell = None


# ── entities ─────────────────────────────────────────────────────────
def _ent_to_list(ent):
    recs = []
    seen = set()
    for (tx, ty), c in ent.occ.items():
        if c in seen:
            continue
        seen.add(c)
        rec = {"btype": c.btype, "x": c.x, "y": c.y, "hp": c.hp}
        if isinstance(c, Belt):
            rec["dir"] = c.dir
            rec["slots"] = c.slots
            rec["anim"] = c.anim
        elif isinstance(c, Inserter):
            rec["dir"] = c.dir
            rec["holding"] = c.holding
            rec["phase"] = c.phase
        else:
            rec["recipe"] = c.recipe
            rec["buf"] = c.buf
            rec["inb"] = c.inb
            rec["outb"] = c.outb
            rec["prog"] = c.prog
            rec["out_dir"] = c.out_dir
            if c.mine_vein is not None:
                rec["vein"] = [c.mine_vein.x, c.mine_vein.y]
        recs.append(rec)
    return recs


def _ent_from_list(ent, world, recs):
    ent.occ.clear()
    for rec in recs:
        btype = rec["btype"]
        x, y = rec["x"], rec["y"]
        if btype in ("conveyor-belt", "fast-belt"):
            c = Belt(x, y, rec["dir"], fast=(btype == "fast-belt"))
            c.slots = list(rec["slots"])
            c.anim = rec.get("anim", 0.0)
        elif btype in ("inserter", "fast-inserter"):
            c = Inserter(x, y, rec["dir"], fast=(btype == "fast-inserter"))
            c.holding = rec["holding"]
            c.phase = rec.get("phase", 0.0)
        else:
            c = Building(x, y, btype, recipe=rec.get("recipe"))
            c.buf = dict(rec.get("buf", {}))
            c.inb = dict(rec.get("inb", {}))
            c.outb = dict(rec.get("outb", {}))
            c.prog = rec.get("prog", 0.0)
            c.out_dir = rec.get("out_dir", 0)
            v = rec.get("vein")
            if v:
                c.mine_vein = world.get(v[0], v[1])
        c.hp = rec.get("hp", c.max_hp)
        for dy in range(c.h):
            for dx in range(c.w):
                ent.occ[(c.x + dx, c.y + dy)] = c
                tile = world.get(c.x + dx, c.y + dy)
                if tile is not None:
                    tile.cell = c


# ── save ─────────────────────────────────────────────────────────────
def save_game(g, name=AUTOSAVE_SLOT):
    data = {
        "version": "0.4",
        "seed": getattr(g, "seed", 0),
        "meta": {
            "t": g.t, "tick": g.tick, "tod": g.tod, "clen": g.clen,
            "is_day": g.is_day, "score": g.score,
        },
        "player": {"x": g.player.x, "y": g.player.y,
                   "hp": g.player.hp, "max_hp": g.player.max_hp,
                   "build_mode": bool(g.player.build_mode)},
        "inv": {"items": dict(g.inv.items), "craft_q": list(g.inv.craft_q)},
        "research": {
            "techs": {k: {"done": t["done"], "prog": t["prog"]}
                      for k, t in g.research.techs.items()},
            "current": g.research.current,
        },
        "unlocked": sorted(g.unlocked),
        "combat": {
            "wave_num": g.combat.wave_num,
            "wave_active": g.combat.wave_active,
            "time_to_next": g.combat.time_to_next,
            "interval": g.combat.interval,
            "evolution": g.combat.evolution,
            "night_bonus": g.combat.night_bonus,
            "enemies": [[e.etype, e.x, e.y, e.hp] for e in g.combat.enemies],
        },
        "power": {"stored": g.power.stored},
        "world": {"W": g.world.W, "H": g.world.H, "tiles": _world_to_list(g.world)},
        "ent": _ent_to_list(g.ent),
    }
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        tmp = _path(name) + ".tmp"
        with open(tmp, "wb") as f:
            f.write(zlib.compress(raw, 6))
        os.replace(tmp, _path(name))
        return True
    except OSError:
        return False


def has_save(name=AUTOSAVE_SLOT):
    return os.path.exists(_path(name))


def latest_slot():
    """Return the most recently saved slot (by mtime), or None."""
    best, best_t = None, -1
    for slot in (AUTOSAVE_SLOT, "slot1"):
        p = _path(slot)
        if os.path.exists(p):
            t = os.path.getmtime(p)
            if t > best_t:
                best, best_t = slot, t
    return best


def load_data(name=AUTOSAVE_SLOT):
    try:
        with open(_path(name), "rb") as f:
            raw = zlib.decompress(f.read())
        return json.loads(raw.decode("utf-8"))
    except (OSError, zlib.error, ValueError):
        return None


def apply(g, data):
    """Overwrite a freshly built game g with a full snapshot."""
    g.seed = data.get("seed", 0)
    w = g.world
    _world_from_list(w, data["world"]["tiles"])
    g.spawn_x, g.spawn_y = w.spawn_x, w.spawn_y

    p = data["player"]
    g.player.x, g.player.y = float(p["x"]), float(p["y"])
    g.player.hp = p["hp"]
    g.player.max_hp = p["max_hp"]
    g.player.build_mode = bool(p["build_mode"])

    g.inv.items = dict(data["inv"]["items"])
    g.inv.craft_q = [dict(j) for j in data["inv"]["craft_q"]]

    rs = data["research"]
    for k, t in g.research.techs.items():
        st = rs["techs"].get(k, {})
        t["done"] = st.get("done", False)
        t["prog"] = st.get("prog", 0.0)
    g.research.current = rs.get("current")

    g.unlocked.clear()
    g.unlocked.update(data.get("unlocked", []))

    _ent_from_list(g.ent, w, data["ent"])

    cb = data["combat"]
    g.combat.wave_num = cb["wave_num"]
    g.combat.wave_active = cb["wave_active"]
    g.combat.time_to_next = cb["time_to_next"]
    g.combat.interval = cb["interval"]
    g.combat.evolution = cb["evolution"]
    g.combat.night_bonus = cb["night_bonus"]
    g.combat.enemies = []
    for etype, ex, ey, hp in cb["enemies"]:
        e = Enemy(etype, ex, ey)
        e.hp = hp
        g.combat.enemies.append(e)

    g.power.stored = data["power"]["stored"]

    m = data["meta"]
    g.t = m["t"]
    g.tick = m["tick"]
    g.tod = m["tod"]
    g.clen = m["clen"]
    g.is_day = m["is_day"]
    g.score = m["score"]
    return True