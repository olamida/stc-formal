"""Run the three experiments; write CSVs to results/."""
import csv, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import stcformal  # noqa
from stcformal.loss_model import measure, predicted, wilson
from stcformal.search import search

OUT = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(OUT, exist_ok=True)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000

rows = []
for L, H in [(3, 12), (5, 12), (5, 2), (5, 3), (8, 4)]:
    for p in (0.3, 0.5, 0.7):
        k, n = measure(L, p, H, N)
        lo, hi = wilson(k, n)
        rows.append(dict(L=L, H=H, p=p, n=n, collisions=k, rate=k / n, lo=lo, hi=hi,
                         predicted=predicted(p, L, H)))
        print(rows[-1], flush=True)
# out-of-sample check of the corrected model: announce-then-act OFF (prediction a=0)
for L, H in [(5, 12), (5, 3)]:
    for p in (0.5, 0.7):
        k, n = measure(L, p, H, N, announce_first=False)
        lo, hi = wilson(k, n)
        rows.append(dict(L=L, H=H, p=p, n=n, collisions=k, rate=k / n, lo=lo, hi=hi,
                         predicted=predicted(p, L, H, False), announce=False))
        print(rows[-1], flush=True)
for r in rows:
    r.setdefault("announce", True)
with open(f"{OUT}/loss_bound.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

rows = []
for sensing in (True, False):
    for name, (tot, col, fail, first) in search(sensing).items():
        rows.append(dict(sensing=sensing, pattern=name, instances=tot, collisions=col,
                         incomplete=fail, first=first))
with open(f"{OUT}/exhaustive_3x3.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows:
    if r["pattern"] in ("none", "both_k1", "both_k3", "both_k6", "0to1_k3", "1to0_k3"):
        print(r)
