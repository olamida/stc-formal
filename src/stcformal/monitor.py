"""A small Signal-Temporal-Logic-style runtime monitor (restricted fragment).

Traces are ``traj[agent_id] = [(t, (x, y, z)), ...]`` as recorded by
``stc.run(..., SimConfig(record=True))``. An agent *vanishes* after its last
sample (it reached its goal).

Formulas:  Pred(f)        atomic predicate, f(trace, t) -> real (>= 0 means true)
           Always(a, b, phi)       G_[a,b] phi   robustness = min over t in [a, b]
           Eventually(a, b, phi)   F_[a,b] phi   robustness = max over t in [a, b]

Robustness is the usual quantitative semantics: positive = satisfied with
margin, negative = violated by that much. The two predicates below implement
the safety and liveness requirements of the corridor protocol:

    G_[0,T]  separation >= 1      no two agents in the same cell
    F_[0,T]  at_goal(i)           agent i arrives
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Dict, List, Set, Tuple

Trace = Dict[int, List[Tuple[int, Tuple[int, int, int]]]]


def _positions_at(trace: Trace, t: int) -> Dict[int, Tuple[int, int, int]]:
    out = {}
    for i, samples in trace.items():
        for tt, c in samples:
            if tt == t:
                out[i] = c
                break
    return out


@dataclass
class Pred:
    f: Callable[[Trace, int], float]
    name: str = "pred"

    def rho(self, trace: Trace, t: int) -> float:
        return self.f(trace, t)


@dataclass
class Always:
    a: int
    b: int
    phi: object

    def rho(self, trace: Trace, t: int = 0) -> float:
        return min(self.phi.rho(trace, tt) for tt in range(t + self.a, t + self.b + 1))


@dataclass
class Eventually:
    a: int
    b: int
    phi: object

    def rho(self, trace: Trace, t: int = 0) -> float:
        return max(self.phi.rho(trace, tt) for tt in range(t + self.a, t + self.b + 1))


def robustness(formula, trace: Trace) -> float:
    return formula.rho(trace, 0)


def separation_pred() -> Pred:
    """min over agent pairs of (L1 distance - 1): negative iff two agents share a cell."""
    def f(trace: Trace, t: int) -> float:
        pos = _positions_at(trace, t)
        best = 1e9
        for (i, a), (j, b) in combinations(sorted(pos.items()), 2):
            d = abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
            best = min(best, d - 1)
        return best
    return Pred(f, "separation>=1")


def goal_pred(agent: int, goal: Tuple[int, int, int]) -> Pred:
    """+1 at the time the agent stands on its goal, -1 otherwise."""
    def f(trace: Trace, t: int) -> float:
        c = _positions_at(trace, t).get(agent)
        return 1.0 if c == goal else -1.0
    return Pred(f, f"at_goal({agent})")


def collisions_from_trace(trace: Trace) -> Tuple[Set[Tuple[int, int]], int]:
    """Independent re-derivation of the simulator's collision check from the trace.

    Returns (set of colliding agent pairs, number of collision events), counting
    vertex collisions (same cell, same tick) and head-on swaps.
    """
    t_max = max((t for s in trace.values() for t, _ in s), default=0)
    pairs: Set[Tuple[int, int]] = set()
    events = 0
    prev = _positions_at(trace, 0)
    for t in range(1, t_max + 1):
        cur = _positions_at(trace, t)
        by_cell: Dict[Tuple[int, int, int], List[int]] = {}
        for i, c in cur.items():
            by_cell.setdefault(c, []).append(i)
        for ids in by_cell.values():
            for p in combinations(sorted(ids), 2):
                pairs.add(p)
                events += 1
        for i, j in combinations(sorted(cur), 2):
            if i in prev and j in prev and prev[i] == cur[j] and prev[j] == cur[i] \
                    and prev[i] != prev[j]:
                pairs.add((i, j))
                events += 1
        prev = cur
    return pairs, events
