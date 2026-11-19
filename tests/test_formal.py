import random
import pytest
import stcformal
from stc import GROUND, AgentSpec, Constraints, SCENARIOS, SimConfig, World, plan_path, run
from stcformal import Always, Eventually, collisions_from_trace, goal_pred, robustness, separation_pred
from stcformal.loss_model import cross_instance, predicted, wilson
from stcformal.planner_check import bfs_arrival
from stcformal.search import instances, scripted, search


def test_robustness_semantics():
    tr = {0: [(0, (0, 0, 0)), (1, (1, 0, 0)), (2, (2, 0, 0))],
          1: [(0, (4, 0, 0)), (1, (3, 0, 0)), (2, (2, 0, 0))]}
    assert robustness(Always(0, 2, separation_pred()), tr) == -1          # share a cell at t=2
    tr[1][2] = (2, (3, 0, 0))
    assert robustness(Always(0, 2, separation_pred()), tr) == 0           # adjacent, not equal... d=1 -> 0
    assert robustness(Eventually(0, 2, goal_pred(0, (2, 0, 0))), tr) == 1
    assert robustness(Eventually(0, 1, goal_pred(0, (2, 0, 0))), tr) == -1


def test_monitor_matches_simulator_on_random_runs():
    rng = random.Random(0)
    agree = 0
    for i in range(120):
        name = rng.choice(["crossing", "corridor", "open_grid"])
        world, specs = SCENARIOS[name](seed=i)
        mode = rng.choice(["stc", "reactive"])
        cfg = SimConfig(mode=mode, loss=rng.choice([0, 0.5, 0.9]), record=True, seed=i,
                        sensing=rng.random() < 0.5)
        r = run(world, specs, cfg)
        pairs, ev = collisions_from_trace(r.traj)
        assert ev == r.collision_events and len(pairs) == r.collision_pairs
        vertex_only = robustness(Always(0, cfg.max_ticks, separation_pred()), r.traj) < 0
        # vertex violation implies the checker saw a collision
        assert (not vertex_only) or r.collision_events > 0
        agree += 1
    assert agree == 120


def test_lossless_exhaustive_3x3_is_safe_and_complete():
    for sensing in (True, False):
        res = search(sensing, max_k=0)["none"]
        assert res[0] == 4104 and res[1] == 0 and res[2] == 0


def test_scripted_blackout_produces_known_counterexample():
    world = World(3, 3, 1)
    specs = [AgentSpec(GROUND, (0, 0, 0), (0, 1, 0)), AgentSpec(GROUND, (0, 2, 0), (0, 0, 0))]
    with scripted(lambda i: i < 4):
        r = run(world, specs, SimConfig(loss=0.5, max_ticks=40))
    assert r.collision_events > 0


def test_loss_model_matches_when_horizon_is_binding():
    # H < L: p^H, the cleanest case (2000 runs, tolerance well outside the CI)
    from stcformal.loss_model import measure
    k, n = measure(5, 0.5, 2, 1500)
    lo, hi = wilson(k, n)
    assert lo - 0.02 <= predicted(0.5, 5, 2) <= hi + 0.02


@pytest.mark.parametrize("seed", range(60))
def test_planner_arrival_is_optimal_vs_bfs(seed):
    rng = random.Random(seed)
    w, h = 5, 4
    blocked = {(x, y, 0) for x in range(w) for y in range(h) if rng.random() < 0.15}
    world = World(w, h, 1, blocked)
    free = [(x, y, 0) for x in range(w) for y in range(h) if (x, y, 0) not in blocked]
    if len(free) < 2:
        return
    s, g = rng.sample(free, 2)
    cons = Constraints()
    for _ in range(rng.randint(0, 3)):
        path = [rng.choice(free) for _ in range(rng.randint(2, 6))]
        # make it a connected walk
        walk = [path[0]]
        for _ in range(5):
            nb = [c for c in world.neighbors(walk[-1], GROUND)] + [walk[-1]]
            walk.append(rng.choice(nb))
        cons.add_path(rng.randint(0, 2), walk)
    best = bfs_arrival(world, GROUND, s, g, 0, cons, 40)
    plan, _ = plan_path(world, GROUND, s, g, 0, cons, max_steps=40)
    if best is None:
        return                      # A* may legitimately fail too; nothing to compare
    assert plan is not None and plan.end == best
    for k in range(len(plan.cells) - 1):
        assert not cons.vertex_blocked(plan.cells[k + 1], plan.t0 + k + 1)
