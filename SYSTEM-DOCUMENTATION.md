# SYSTEM-DOCUMENTATION — stc-formal

Deep technical / developer documentation. For running instructions see
`USER-GUIDE.md`; for the work ledger see `PENDING-TASKS.md`.

## 1. Purpose and scope

Runtime monitor, exhaustive counterexample search and a one-line loss model for `stc-corridors`.

Research question: **How safe is the decentralized corridor protocol exactly, and what is the smallest failure that breaks it?**

This is a simulation study. No hardware measurements, external datasets or
proprietary data are involved. The repository is intentionally small enough to
be read end-to-end by a reviewer in one sitting.

## 2. Architecture

| Component | Responsibility |
|---|---|
| `src/stcformal/monitor.py` | Tiny STL fragment, robustness values, collision re-derivation from traces. |
| `src/stcformal/search.py` | Deterministic blackout patterns and exhaustive 3x3 instance generator. |
| `src/stcformal/loss_model.py` | Closed-form prediction, Wilson intervals, Monte Carlo measurement. |
| `src/stcformal/planner_check.py` | Time-expanded BFS arrival oracle. |
| `src/stcformal/__init__.py` | Public API plus sibling-checkout fallback for `stc`. |

Dependencies flow one way: configuration/scenario → model/algorithm →
experiment runner → results → figures/animation. The simulator does not read
its own results; results are an output only.

## 3. Data flow

1. A seeded scenario, task set, signal or topology is constructed.
2. The core model advances in discrete steps (ticks or control steps).
3. Metrics are accumulated independently of the decision logic where possible
   (for example, a ground-truth collision checker rather than the agents' beliefs).
4. `experiments/` writes machine-readable results under `results/`.
5. `make_figures.py` and `make_animation.py` read those results or re-run the
   seeded simulator to produce visual artefacts.

## 4. Algorithms / numerical methods

See `README.md` for the high-level description and, where present,
`docs/DESIGN.md` or `DEVELOPMENT_GUIDE.md` for the full derivation. The
implementation is the authoritative reference: start at the module table in
section 2 and follow the entry point used by `PYTHONPATH=src python -m pytest -q tests`.

Reproducibility rules:
- Every stochastic component is driven by an explicit seed.
- Experiment parameters are recorded in the result rows.
- A change to a result number requires regenerating the CSV/JSON, not editing prose.

## 5. Results and evidence

- All 4104 two-agent 3x3 instances are collision-free and complete when lossless, with and without sensing — `results/exhaustive_3x3.csv`.
- Two blacked-out broadcast ticks cause 384/4104 collisions with sensing and 624/4104 without; the reverse direction causes none — `results/exhaustive_3x3.csv`.
- The loss prediction `p**min(L+a,H)` matches 18 of 19 measured points inside 95% Wilson intervals — `results/loss_bound.csv`.

## 6. Animation pipeline

`python experiments/make_animation.py` renders `figures/demo_counterexample.gif`. It uses the project's own simulator
(or an explicitly documented pure-Python reference of the same controller) and
Matplotlib's Pillow writer. Frames are subsampled to keep the GIF small; the
underlying trajectory is not resampled or smoothed. Replays the smallest documented failure: two agents on a 3x3 grid, first four broadcast draws blacked out, ending in a vertex collision.

## 7. Build, test and CI

```bash
pip install -r requirements.txt  # needs `stc` installed or ../stc-corridors beside this folder
PYTHONPATH=src python -m pytest -q tests
python experiments/run_formal.py 3000 && python experiments/make_figures.py
python experiments/make_animation.py
```

CI (`.github/workflows/ci.yml`) runs on push and pull request. Jobs install the
documented dependencies, set `PYTHONPATH=src` where required, and run the test
suite. Repositories that call C code install a system compiler in CI; footprint
measurement with cross-compilers is deliberately optional.

## 8. Extension points

- Add a new scenario/policy by extending the corresponding factory or registry
  and a seeded test, then re-run the full experiment suite.
- Add a new metric by writing it into the result row and updating
  `experiments/summarize.py` and the README table together.
- Add a new animation by recording the relevant simulator state (prefer an
  optional `record` flag over duplicating the stepping logic) and saving via
  `FuncAnimation`/`PillowWriter` in `experiments/`.

## 9. Known limitations

- Exhaustive search covers two-agent instances only; the loss model covers one crossing geometry.
- Blackouts are indexed by message-draw count, which equals ticks only while both agents are active.
- The STL fragment is deliberately tiny (no nesting, no until); it is a monitor, not a model checker.
- The safety filter and Hypothesis tests named in the project ladder are not done.

## 10. Relation to the rest of the portfolio

Depends on `stc-corridors`; complements `rtos-sched-lab` on verification.

## 11. Release metadata

`CITATION.cff` carries title, author (Yusuf Ndanusa Yahaya), version 0.1.0,
release date, repository URL and MIT license. No DOI or ORCID is claimed.
