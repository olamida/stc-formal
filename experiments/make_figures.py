import csv, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = os.path.join(os.path.dirname(__file__), "..", "results"); F = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(F, exist_ok=True)
rows = [r for r in csv.DictReader(open(f"{R}/loss_bound.csv"))]
fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
for r in rows:
    pred, obs, lo, hi = (float(r[k]) for k in ("predicted", "rate", "lo", "hi"))
    ok = lo <= pred <= hi
    ax[0].errorbar(pred, obs, yerr=[[obs - lo], [hi - obs]], fmt="o" if ok else "s",
                   color="#1b7f5c" if ok else "#c0392b", capsize=2)
ax[0].plot([1e-3, 1], [1e-3, 1], "k--", lw=1)
ax[0].set_xscale("log"); ax[0].set_yscale("log")
ax[0].set_xlabel("predicted  p^min(L+a, H)"); ax[0].set_ylabel("measured collision rate (95% Wilson)")
ax[0].set_title("Missed-conflict model vs simulation\n(green = prediction inside CI)")
ex = [r for r in csv.DictReader(open(f"{R}/exhaustive_3x3.csv")) if r["pattern"].startswith("both_k") or r["pattern"] == "none"]
for s, c in (("True", "#1b7f5c"), ("False", "#c0392b")):
    xs = [0] + [int(r["pattern"][6:]) for r in ex if r["sensing"] == s and r["pattern"] != "none"]
    ys = [int(next(r for r in ex if r["sensing"] == s and r["pattern"] == "none")["collisions"])] + \
         [int(r["collisions"]) for r in ex if r["sensing"] == s and r["pattern"] != "none"]
    ax[1].plot(xs, ys, "o-", color=c, label="sensing on" if s == "True" else "sensing off")
ax[1].set_xlabel("blackout length k (broadcast ticks lost, both directions)")
ax[1].set_ylabel("instances with a collision (of 4104)")
ax[1].set_title("Exhaustive 3x3, 2 agents:\nsafe when lossless, 2-tick blackout breaks it")
ax[1].legend(); plt.tight_layout(); plt.savefig(f"{F}/fig_formal.png", dpi=160)
