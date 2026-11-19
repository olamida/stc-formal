"""Analytic missed-conflict model vs Monte Carlo.

Setup: two agents on an open grid, arms of length L, crossing at the centre.
Agent 0 (high priority) goes west->east along row L; agent 1 goes north->south
down column L. Both reach the centre cell at tick L, so without negotiation
they collide there. Sensing is switched OFF so the only safeguard is the
broadcast of corridors.

Model. Agent 1 can only avoid the conflict if it hears at least one of the
broadcasts of agent 0 sent at ticks 0..L-1 (each broadcast contains the centre
cell as long as it lies within the horizon, i.e. L - t <= H). With independent
per-message loss p, the number of broadcasts that carry the conflict is
n = min(L + a, H) (broadcasts at ticks L-H.. L-1 when L > H; the earliest ones
cannot see it yet), so

    P(collision) ~ p ** min(L + a, H)   (a = 1 if announce_first else 0)

This is an approximation, not a proof: it ignores that agent 1's replan
fallbacks may themselves be imperfect. The experiment measures the gap.
"""
from __future__ import annotations

import math
from typing import Tuple

from stc import GROUND, AgentSpec, SimConfig, World, run


def cross_instance(L: int):
    size = 2 * L + 1
    world = World(size, size, 1)
    specs = [AgentSpec(GROUND, (0, L, 0), (2 * L, L, 0)),
             AgentSpec(GROUND, (L, 0, 0), (L, 2 * L, 0))]
    return world, specs


def predicted(p: float, L: int, H: int, announce_first: bool = True) -> float:
    """p ** min(L + a, H), a = 1 with announce-then-act (the forced first wait
    delays both agents one tick, so the conflict is one tick later and one more
    broadcast carries it). First version of this model used a = 0 and was
    wrong by exactly that factor; see README."""
    return p ** min(L + (1 if announce_first else 0), H)


def wilson(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def measure(L: int, p: float, H: int, n: int, sensing: bool = False,
            announce_first: bool = True):
    world, specs = cross_instance(L)
    k = 0
    for seed in range(n):
        r = run(world, specs, SimConfig(mode="stc", horizon=H, loss=p, sensing=sensing,
                                        announce_first=announce_first, seed=seed, max_ticks=8 * L + 20))
        k += r.collision_events > 0
    return k, n
