# -*- coding: utf-8 -*-
"""Samitorio v0.3 - power grid."""
import core
from entities import Building


class PowerGrid:
    def __init__(self):
        self.total_production = 0.0
        self.total_consumption = 0.0
        self.stored = 0.0
        self.max_stored = 5000.0
        self.sat = 1.0
        self.day_p = 1.0

    def tally(self, g):
        prod = cons = 0.0
        seen = set()
        for (tx, ty), c in g.ent.occ.items():
            if c in seen:
                continue
            seen.add(c)
            if isinstance(c, Building):
                d = c.d
                if c.btype == "solar-panel":
                    prod += d["pw_gen"] * (0.15 + 0.85 * max(0.0, g.day_p))
                else:
                    prod += d["pw_gen"]
                cons += d["pw_use"]
        self.total_production = prod
        self.total_consumption = cons

    def update(self, dt, g):
        self.tally(g)
        net = self.total_production - self.total_consumption
        if net >= 0:
            self.stored = min(self.max_stored, self.stored + net * dt)
            self.sat = 1.0
        else:
            miss = -net * dt
            if self.stored >= miss:
                self.stored -= miss
                self.sat = 1.0
            else:
                self.sat = self.total_production / max(1, self.total_consumption)
                self.stored = 0.0