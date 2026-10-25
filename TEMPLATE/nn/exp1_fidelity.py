#!/usr/bin/env python3
"""exp1_fidelity.py -- W10 fidelity driver (WO-TBM-EXP1 §2.1, §2.5(a)).

Compares the ORIGINAL template code against the PARAMETERIZED
template code on the ORIGINAL 10x10 single-door world (world.World,
period=20, open_len=10, 2000 episodes, same hyperparameters).

Configs:
  A -- original trainers on original code. MUST run BEFORE the
       §2.1 template edits (it imports the code as it stands).
       plain: train_neural(seed, PlainEncoder());
       memory: train_memory(seed); wrapped: train_wrapped(seed).
  D -- the sweep path: exp1_run.train_loop() with the
       parameterized encoder (grid_size=10) on a World factory.
       Runs AFTER the §2.1 edits.
If D == A exactly (per-episode stats, final weights, greedy
outcomes), the parameterization is faithful at size 10 AND the
runner's training loop is faithful. If D != A, the comparison
output localizes the first difference; the builder then runs
the B/C decompositions (original loop + parameterized encoder,
runner loop + original encoder) to isolate the cause -- and the
fidelity gate blocks any sweep trust until resolved.

Greedy comparison convention (same for A and D): a FRESH
encoder per job, 20 start phases, eps=0, weights frozen, cap
200 -- the runner's eval convention. This compares policies,
not eval conventions (the original wrapped eval reused the
training encoder; that convention is NOT used here, for
either side).

Each run records: git HEAD, sha256 of the template files as
imported (proving A ran pre-edit code and D ran post-edit
code), per-episode stats, final network params, and greedy
outcomes. Outputs are sanity artifacts under --outdir
(default /tmp/exp1_fidelity); they are NEVER sweep records
and are NEVER committed.

Usage:
  python3 nn/exp1_fidelity.py --config A --arm plain --seed 0
  python3 nn/exp1_fidelity.py --config D --arm plain --seed 0
  python3 nn/exp1_fidelity.py --compare
"""

import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np

from agent_nn import (EPISODE_CAP, env_step)
from world import World

PERIOD = 20
OPEN_LEN = 10
EPISODES = 2000

TEMPLATE_FILES = ["world.py", "nn/agent_nn.py", "nn/agent_mem.py",
                  "nn/agent_wrapped.py", "nn/wrapper.py", "nn/nnet.py"]


def file_hashes():
    """sha256 of the template files as they stand on disk."""
    root = os.path.dirname(_HERE)
    out = {}
    for rel in TEMPLATE_FILES:
        with open(os.path.join(root, rel), "rb") as f:
            out[rel] = hashlib.sha256(f.read()).hexdigest()
    return out


def git_head():
    try:
        import subprocess
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=os.path.dirname(_HERE)).decode().strip()
    except Exception:
        return None


def greedy_direct(agent, encoder):
    """20-phase greedy eval on World(20, 10), fresh encoder per job.

    Returns [(start_phase, reached, ticks, crushes)].
    """
    outcomes = []
    for start in range(PERIOD):
        w = World(period=PERIOD, open_len=OPEN_LEN)
        w.reset(start_tick=start)
        encoder.reset(w)
        ticks = 0
        crushes = 0
        reached = False
        while ticks < EPISODE_CAP:
            x = encoder.encode(w)
            a = agent.act(x, 0.0)
            _r, reached, crushed = env_step(w, a)
            crushes += crushed
            ticks += 1
            if reached:
                break
        outcomes.append((start, bool(reached), ticks, int(crushes)))
    return outcomes


def run_config(config, arm, seed, outdir):
    """Run one fidelity training; save stats, weights, greedy."""
    if config == "A":
        # Original trainers, original encoders (no size argument).
        from agent_nn import train_neural, PlainEncoder
        from agent_mem import train_memory
        from agent_wrapped import train_wrapped
        if arm == "plain":
            agent, stats = train_neural(seed, encoder=PlainEncoder())
            enc = PlainEncoder()
        elif arm == "memory":
            agent, stats = train_memory(seed)
            from agent_mem import MemoryEncoder
            enc = MemoryEncoder()
        elif arm == "wrapped":
            agent, stats, _enc = train_wrapped(seed)
            from agent_wrapped import WrappedEncoder
            enc = WrappedEncoder()
        else:
            raise ValueError("unknown arm %r" % (arm,))
    elif config == "D":
        # Sweep path: runner loop + parameterized encoder, size 10.
        from exp1_run import train_loop
        from agent_nn import PlainEncoder
        from agent_mem import MemoryEncoder
        from agent_wrapped import WrappedEncoder
        agent, stats, _enc = train_loop(
            arm, seed, lambda: World(period=PERIOD, open_len=OPEN_LEN),
            10)
        # Keyword args: WrappedEncoder's first positional is `model`.
        enc = {"plain": PlainEncoder(grid_size=10),
               "memory": MemoryEncoder(grid_size=10),
               "wrapped": WrappedEncoder(grid_size=10)}[arm]
    else:
        raise ValueError("unknown config %r" % (config,))
    greedy = greedy_direct(agent, enc)
    tag = "%s_%s_%d" % (config, arm, seed)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, tag + "_stats.json"), "w") as f:
        json.dump({
            "config": config, "arm": arm, "seed": seed,
            "git_head": git_head(), "file_hashes": file_hashes(),
            "stats": [[s[0], bool(s[1]), int(s[2]),
                       (None if s[3] is None else float(s[3]))]
                      for s in stats],
            "greedy": greedy}, f)
    params = agent.net.get_params()
    np.savez(os.path.join(outdir, tag + "_weights.npz"),
             **{"w%d" % i: p for i, p in enumerate(params)})
    reached = sum(1 for s in stats if s[1])
    greached = sum(1 for g in greedy if g[1])
    print("%s: train reached %d/%d, greedy %d/20"
          % (tag, reached, len(stats), greached))
    return tag


def compare(outdir):
    """Compare A vs D for all (arm, seed); exit 0 iff all match."""
    arms = ["plain", "memory", "wrapped"]
    seeds = [0, 1]
    all_ok = True
    for arm in arms:
        for seed in seeds:
            a_tag = "A_%s_%d" % (arm, seed)
            d_tag = "D_%s_%d" % (arm, seed)
            with open(os.path.join(outdir, a_tag + "_stats.json")) as f:
                a = json.load(f)
            with open(os.path.join(outdir, d_tag + "_stats.json")) as f:
                d = json.load(f)
            ok = True
            reasons = []
            if a["stats"] != d["stats"]:
                ok = False
                diffs = [i for i, (x, y) in enumerate(
                    zip(a["stats"], d["stats"])) if x != y]
                reasons.append("stats differ at episodes %s"
                               % (diffs[:5],))
            if a["greedy"] != d["greedy"]:
                ok = False
                diffs = [i for i, (x, y) in enumerate(
                    zip(a["greedy"], d["greedy"])) if x != y]
                reasons.append("greedy differs at phases %s"
                               % (diffs[:5],))
            aw = np.load(os.path.join(outdir, a_tag + "_weights.npz"))
            dw = np.load(os.path.join(outdir, d_tag + "_weights.npz"))
            if set(aw.files) != set(dw.files):
                ok = False
                reasons.append("weight keys differ")
            else:
                maxdiff = 0.0
                for k in aw.files:
                    if aw[k].shape != dw[k].shape or not np.array_equal(
                            aw[k], dw[k]):
                        ok = False
                        maxdiff = max(
                            maxdiff,
                            float(np.max(np.abs(aw[k] - dw[k]))))
                if not ok:
                    reasons.append("weights differ (max abs diff %g)"
                                   % (maxdiff,))
            print("%s vs %s: %s%s"
                  % (a_tag, d_tag, "MATCH" if ok else "MISMATCH",
                     (" -- " + "; ".join(reasons)) if reasons else ""))
            all_ok = all_ok and ok
    print("FIDELITY: %s" % ("PASS" if all_ok else "FAIL"))
    return all_ok


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", choices=["A", "D"])
    ap.add_argument("--arm", choices=["plain", "memory", "wrapped"])
    ap.add_argument("--seed", type=int)
    ap.add_argument("--outdir", default="/tmp/exp1_fidelity")
    ap.add_argument("--compare", action="store_true")
    args = ap.parse_args()
    if args.compare:
        sys.exit(0 if compare(args.outdir) else 1)
    if args.config is None or args.arm is None or args.seed is None:
        ap.error("--config, --arm, and --seed are required")
    run_config(args.config, args.arm, args.seed, args.outdir)
