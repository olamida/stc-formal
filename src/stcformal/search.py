"""Exhaustive counterexample search on 3x3 two-agent instances.

Every (start0, goal0, start1, goal1) with distinct starts, distinct goals and
start != goal is run under a family of *scripted* loss patterns (no randomness):
a blackout of the first k broadcast slots, in both directions or in one.
"""
from __future__ import annotations

import contextlib
import types
from itertools import product
from typing import Callable, Iterator, List, Tuple

import stc.sim as _sim
from stc import GROUND, AgentSpec, SimConfig, World, run


class ScriptedRandom:
    """Stands in for random.Random: random() returns 0.0 (dropped when loss=0.5)
    or 1.0 (delivered) according to drop(draw_index)."""

    drop: Callable[[int], bool] = staticmethod(lambda i: False)

    def __init__(self, seed=None):
        self.i = 0

    def random(self):
        i, self.i = self.i, self.i + 1
        return 0.0 if type(self).drop(i) else 1.0


@contextlib.contextmanager
def scripted(drop: Callable[[int], bool]):
    saved = _sim.random
    cls = type("S", (ScriptedRandom,), {"drop": staticmethod(drop)})
    _sim.random = types.SimpleNamespace(Random=cls)
    try:
        yield
    finally:
        _sim.random = saved


def patterns(max_k: int = 6):
    """Name -> drop(draw_index). Draw order per tick is 0->1 then 1->0, so even
    indices are agent0->agent1 (the one the low-priority agent needs)."""
    out = {"none": lambda i: False}
    for k in range(1, max_k + 1):
        out[f"both_k{k}"] = (lambda k: lambda i: i < 2 * k)(k)
        out[f"0to1_k{k}"] = (lambda k: lambda i: i < 2 * k and i % 2 == 0)(k)
        out[f"1to0_k{k}"] = (lambda k: lambda i: i < 2 * k and i % 2 == 1)(k)
    return out


def instances(n: int = 3) -> Iterator[List[Tuple[int, int, int]]]:
    cells = [(x, y, 0) for x in range(n) for y in range(n)]
    for s0, g0, s1, g1 in product(cells, repeat=4):
        if s0 != s1 and g0 != g1 and s0 != g0 and s1 != g1:
            yield s0, g0, s1, g1


def search(sensing: bool, max_k: int = 6, n: int = 3, horizon: int = 12):
    """Returns {pattern: (n_instances, n_collide, n_fail, first_counterexample)}."""
    world = World(n, n, 1)
    results = {}
    for name, drop in patterns(max_k).items():
        total = bad_col = bad_fail = 0
        first = None
        with scripted(drop):
            for s0, g0, s1, g1 in instances(n):
                specs = [AgentSpec(GROUND, s0, g0), AgentSpec(GROUND, s1, g1)]
                r = run(world, specs, SimConfig(mode="stc", horizon=horizon, loss=0.5,
                                                sensing=sensing, max_ticks=60))
                total += 1
                col = r.collision_events > 0
                fail = (not col) and r.arrived < 2
                bad_col += col
                bad_fail += fail
                if (col or fail) and first is None:
                    first = (s0, g0, s1, g1)
        results[name] = (total, bad_col, bad_fail, first)
    return results
