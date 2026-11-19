"""Render the counterexample animation from the real 3x3 simulator.

Run from the repository root:
    PYTHONPATH=src python experiments/make_animation.py

The scenario is the one used by ``test_scripted_blackout_produces_known_counterexample``:
two ground agents on a 3x3 grid, first four broadcast draws blacked out.  The
frames come from ``stc.sim.run`` via ``stc.viz.render_gif``; nothing is invented.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "stc-corridors", "src")))

from stc import AgentSpec, GROUND, SimConfig, World, run  # noqa: E402
from stc.viz import render_gif  # noqa: E402
from stcformal.search import scripted  # noqa: E402


def main() -> None:
    world = World(3, 3, 1)
    specs = [AgentSpec(GROUND, (0, 0, 0), (0, 1, 0)),
             AgentSpec(GROUND, (0, 2, 0), (0, 0, 0))]
    with scripted(lambda i: i < 4):
        result = run(world, specs, SimConfig(loss=0.5, max_ticks=40,
                                             record=True, seed=0))
    out = os.path.join(ROOT, "figures", "demo_counterexample.gif")
    render_gif(world, specs, result, out, fps=3, dpi=80,
               title="3x3 counterexample: 4 blacked-out messages")
    print(f"wrote {out}")
    print(f"collision_events={result.collision_events} arrived={result.arrived}/2")


if __name__ == "__main__":
    main()
