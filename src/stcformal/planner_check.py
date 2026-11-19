"""Brute-force oracle for the space-time A*: time-expanded BFS over (cell, t)."""
from __future__ import annotations

from collections import deque
from typing import Optional

from stc import Constraints, World


def bfs_arrival(world: World, kind: str, start, goal, t0: int,
                cons: Constraints, max_steps: int) -> Optional[int]:
    """Earliest arrival tick of any constraint-respecting wait/move sequence."""
    seen = {(start, t0)}
    q = deque([(start, t0)])
    while q:
        cell, t = q.popleft()
        if cell == goal:
            return t
        if t - t0 >= max_steps:
            continue
        for nxt in [cell, *world.neighbors(cell, kind)]:
            if not world.is_free(nxt, kind) or (nxt, t + 1) in seen:
                continue
            if cons.vertex_blocked(nxt, t + 1):
                continue
            if nxt != cell and cons.swap_blocked(t, cell, nxt):
                continue
            seen.add((nxt, t + 1))
            q.append((nxt, t + 1))
    return None
