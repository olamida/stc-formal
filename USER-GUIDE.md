# USER-GUIDE — stc-formal

End-user manual. You do not need to edit code to follow this guide.

## 1. What you can do with it

Runtime monitor, exhaustive counterexample search and a one-line loss model for `stc-corridors`.

The research question is: *How safe is the decentralized corridor protocol exactly, and what is the smallest failure that breaks it?*

## 2. Install

```bash
git clone https://github.com/olamida/stc-formal.git
cd stc-formal
pip install -r requirements.txt  # needs `stc` installed or ../stc-corridors beside this folder
```

Python 3.10+ is assumed. On Windows use `.venv\Scripts\activate` instead of
`source .venv/bin/activate` if you create a virtual environment.

## 3. Watch the animation

Open `figures/demo_counterexample.gif` directly on GitHub or in any image viewer; GitHub plays
GIFs inline. The animation shows: Replays the smallest documented failure: two agents on a 3x3 grid, first four broadcast draws blacked out, ending in a vertex collision.

To regenerate it from source:

```bash
python experiments/make_animation.py
```

## 4. Verify the installation

```bash
PYTHONPATH=src python -m pytest -q tests
```

A passing run prints a test summary with no failures. If a C compiler is
mentioned as missing, install a system C compiler (gcc on Linux, Xcode command
line tools on macOS, MinGW/MSVC on Windows) and rerun.

## 5. Run the full experiments

```bash
python experiments/run_formal.py 3000 && python experiments/make_figures.py
```

Outputs appear in `results/` (CSV/JSON/Markdown tables) and `figures/`
(PNG/GIF). Re-running with the shipped seeds should reproduce the shipped
numbers; small differences can occur with different library versions.

## 6. How to read the outputs

- All 4104 two-agent 3x3 instances are collision-free and complete when lossless, with and without sensing — `results/exhaustive_3x3.csv`.
- Two blacked-out broadcast ticks cause 384/4104 collisions with sensing and 624/4104 without; the reverse direction causes none — `results/exhaustive_3x3.csv`.
- The loss prediction `p**min(L+a,H)` matches 18 of 19 measured points inside 95% Wilson intervals — `results/loss_bound.csv`.

## 7. Known limitations (please read)

- Exhaustive search covers two-agent instances only; the loss model covers one crossing geometry.
- Blackouts are indexed by message-draw count, which equals ticks only while both agents are active.
- The STL fragment is deliberately tiny (no nesting, no until); it is a monitor, not a model checker.
- The safety filter and Hypothesis tests named in the project ladder are not done.

## 8. Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `ModuleNotFoundError` | Running from the wrong directory or missing `PYTHONPATH=src` | Run from the repository root and use the exact command in section 4. |
| Build fails with "gcc not found" | No system C compiler | Install gcc/Xcode CLT/MinGW; the pure-Python reference is only for the animation. |
| Animation script cannot find sibling repo | `stc-corridors` not beside `stc-formal` | Clone both repositories side by side, or install `stc` into the environment. |
| Numbers differ from README | Different seeds or library versions | Use the command in section 5 and compare against `results/` in the repo. |

## 9. Getting help

Open an issue with the exact command, your OS/Python version and the last 20
lines of output. Please do not attach private or employer data.
