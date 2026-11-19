# APP-GUIDE — stc-formal

**Question:** How safe is the decentralized corridor protocol exactly, and what is the smallest failure that breaks it?

**One-line summary:** Runtime monitor, exhaustive counterexample search and a one-line loss model for `stc-corridors`.

This guide records what the application/project has already done and what is still
to be done. It is the session-to-session entry point: read this first, then
`USER-GUIDE.md` to run it, `SYSTEM-DOCUMENTATION.md` to change it, and
`PENDING-TASKS.md` for the live work ledger.

## Work already executed

- Implemented a small STL-style monitor (`Always`, `Eventually`, quantitative robustness) over recorded traces and an independent re-derivation of the simulator collision count.
- Enumerated all 4104 two-agent 3x3 instances, lossless and under scripted message blackouts, with and without adjacent-cell sensing.
- Found that one blacked-out broadcast tick is always safe but two already produce collisions (384/4104 with sensing, 624/4104 without).
- Derived and checked the missed-conflict estimate `p ** min(L + a, H)` with `a = 1` for announce-then-act; corrected an earlier off-by-one-factor model after seeing the data.
- Added a time-expanded BFS oracle that checks the space-time A* planner returns the earliest arrival.
- Wrote 65 tests (including 60 randomized planner-vs-BFS cases) and a CI workflow that checks out the sibling `stc-corridors` repository.
- Rendered the documented counterexample as `figures/demo_counterexample.gif` with `experiments/make_animation.py`.

## Work to be executed (next)

- Add the control-barrier-function safety filter (explicitly NOT yet implemented) and Hypothesis property-based tests (also NOT yet implemented).
- Extend exhaustive search beyond two agents / 3x3 grids.
- Generalise the loss model beyond the single crossing geometry and validate it out of sample on more geometries.
- Model scripted blackouts by tick index rather than message-draw count once both agents stay active.

## High-level flow

1. Configure a seeded scenario / task set / signal.
2. Run the simulator or experiment script in this repository.
3. Metrics are written to `results/`; figures to `figures/`.
4. The animation in `figures/demo_counterexample.gif` is rendered from the same simulator state.

## Commands at a glance

| Purpose | Command |
|---|---|
| Install | `pip install -r requirements.txt  # needs `stc` installed or ../stc-corridors beside this folder` |
| Verify | `PYTHONPATH=src python -m pytest -q tests` |
| Experiments | `python experiments/run_formal.py 3000 && python experiments/make_figures.py` |
| Animation | `python experiments/make_animation.py` |

## Where this connects

Depends on `stc-corridors`; complements `rtos-sched-lab` on verification.

## Honesty notes

All numbers quoted in this repository come from files under `results/`.
Simulation-only results are not hardware measurements, and the documented
limitations in `README.md` are part of the deliverable.
