#!/usr/bin/env python3
"""exp1_spike.py -- EXP1 Part 1 benchmark SPIKE (MEASUREMENT ONLY).

SPIKE records only. This script runs NO sweep training and NO
sweep evaluation. Every job it runs is a spike job: timed
measurements used to project the full sweep's cost (60 trainings
+ 105 eval jobs) against the 4-hour compute threshold. Spike
weights are NEVER written to disk: a trained spike agent lives
in memory only for its own spike eval jobs, then is dropped.
Spike records are never pooled with sweep results and never
count toward sweep completeness.

Design (fixed before running; see exp1_spike_report.md §1):
  trainings (15, 2000 episodes each, 20/10, sweep
      hyperparameters hidden=32, lr=1e-3, cap=200):
    inside W10/W20/W30 x plain/memory/wrapped x seed 0 (9),
    W10 x plain/memory/wrapped x seed 1 (3, seed-variance
      gauge), outside M1/M2/M3 x wrapped x seed 0 (3);
  eval jobs (19, greedy eps=0, weights frozen, 20 phases,
      fresh encoder per job, exactly evaluate_job semantics):
    one trained-world eval per trained spike agent (15),
    plus one held-out eval per wrapped inside agent (4);
  profile jobs (2, 200 episodes each, cProfile only):
    W10/plain/0 and M3/wrapped/0, for the coarse time split
    (learning update vs environment vs encoding/forward).
    Profile times are NOT used for projection.

Resume: records append incrementally to exp1_spike_records.jsonl
(one line per job). A relaunch skips training units whose
training record and all eval records already exist; a unit
whose training exists but whose evals are incomplete is
re-trained (agent weights are never saved) and only the
missing eval records are written, plus a resume_retrain note
line (labeled, not counted in projection).

Usage:
  python3 exp1_spike.py --profile   # 2 short profile jobs only
  python3 exp1_spike.py --run       # 15 training units + 19 evals
  python3 exp1_spike.py --plan      # print the job list, run nothing
"""

import cProfile
import io
import json
import os
import pstats
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from exp1_run import train_loop, evaluate_job
from world_exp1 import make_world, HELDOUT_OF

RECORDS = os.path.join(_HERE, "exp1_spike_records.jsonl")
PROFILE_OUT = os.path.join(_HERE, "exp1_spike_profile.txt")

TRAIN_JOBS = [
    ("plain", "W10", 0), ("memory", "W10", 0), ("wrapped", "W10", 0),
    ("plain", "W20", 0), ("memory", "W20", 0), ("wrapped", "W20", 0),
    ("plain", "W30", 0), ("memory", "W30", 0), ("wrapped", "W30", 0),
    ("plain", "W10", 1), ("memory", "W10", 1), ("wrapped", "W10", 1),
    ("wrapped", "M1", 0), ("wrapped", "M2", 0), ("wrapped", "M3", 0),
]

PROFILE_JOBS = [("plain", "W10", 0), ("wrapped", "M3", 0)]


def grid_of(name):
    return make_world(name).grid_size


def evals_for(arm, train_world):
    """Eval jobs for one trained spike agent: (eval_world, kind)."""
    jobs = [(train_world, "trained")]
    if arm == "wrapped" and train_world in HELDOUT_OF:
        jobs.append((HELDOUT_OF[train_world], "held-out"))
    return jobs


def load_done():
    """Return (done_trainings, done_evals) key sets from RECORDS."""
    done_t, done_e = set(), set()
    if os.path.exists(RECORDS):
        with open(RECORDS) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if r.get("record") != "SPIKE":
                    continue
                if r.get("job_type") == "training":
                    done_t.add((r["arm"], r["world"], r["seed"]))
                elif r.get("job_type") == "eval":
                    done_e.add((r["arm"], r["seed"], r["train_world"],
                                r["eval_world"]))
    return done_t, done_e


def append(rec):
    rec = dict(rec)
    rec["record"] = "SPIKE"
    rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    with open(RECORDS, "a") as f:
        f.write(json.dumps(rec) + "\n")
        f.flush()


def run_training_unit(arm, world, seed, done_t, done_e, record_training):
    """One training unit: train + its eval jobs. Weights in memory
    only, dropped on return. record_training=False on resume
    re-trains (weights were never saved) without writing a second
    training record; a resume_retrain note line records that."""
    grid = grid_of(world)
    t0 = time.perf_counter()
    agent, stats, _enc = train_loop(
        arm, seed, lambda w=world: make_world(w), grid)
    wall = time.perf_counter() - t0
    reached = sum(1 for s in stats if s[1])
    ticks_total = sum(s[0] for s in stats)
    crushes_total = sum(s[2] for s in stats)
    if record_training:
        append({"job_type": "training", "arm": arm, "world": world,
                "seed": seed, "episodes": len(stats), "wall_s": wall,
                "reached": reached, "ticks_total": ticks_total,
                "crushes_total": crushes_total})
        print("SPIKE training %s/%s/%d wall=%.1fs reached=%d/%d"
              % (arm, world, seed, wall, reached, len(stats)), flush=True)
    else:
        append({"job_type": "resume_retrain", "arm": arm, "world": world,
                "seed": seed, "episodes": len(stats), "wall_s": wall,
                "note": "re-train after restart to recover evals; "
                        "NOT a projection input, NOT a sweep record"})
        print("SPIKE resume_retrain %s/%s/%d wall=%.1fs (evals only)"
              % (arm, world, seed, wall), flush=True)
    for eval_world, kind in evals_for(arm, world):
        key = (arm, seed, world, eval_world)
        if key in done_e:
            continue
        egrid = grid_of(eval_world)
        t0 = time.perf_counter()
        recs = evaluate_job(agent, arm,
                            lambda w=eval_world: make_world(w),
                            eval_world, egrid)
        ewall = time.perf_counter() - t0
        append({"job_type": "eval", "arm": arm, "seed": seed,
                "train_world": world, "eval_world": eval_world,
                "eval_kind": kind, "episodes": len(recs),
                "wall_s": ewall,
                "reached": sum(1 for r in recs if r["reached"]),
                "ticks_total": sum(r["ticks"] for r in recs),
                "crushes_total": sum(r["crushes"] for r in recs)})
        print("SPIKE eval %s/%s/%d -> %s (%s) wall=%.1fs reached=%d/20"
              % (arm, world, seed, eval_world, kind, ewall,
                 sum(1 for r in recs if r["reached"])), flush=True)
    del agent


def run_all():
    done_t, done_e = load_done()
    for arm, world, seed in TRAIN_JOBS:
        need_evals = [(arm, seed, world, ew)
                      for ew, _k in evals_for(arm, world)]
        train_done = (arm, world, seed) in done_t
        evals_done = all(k in done_e for k in need_evals)
        if train_done and evals_done:
            print("SPIKE skip %s/%s/%d (already recorded)"
                  % (arm, world, seed), flush=True)
            continue
        run_training_unit(arm, world, seed, done_t, done_e,
                          record_training=not train_done)
        done_t, done_e = load_done()
    print("SPIKE run complete", flush=True)


def bucket_stats(pr):
    """Coarse time split from a cProfile profile: cumulative seconds
    bucketed into learning update / environment / encoding+forward /
    other, by function name. Proportions only (profiling overhead
    inflates absolute times, so these runs never feed projection)."""
    st = pstats.Stats(pr)
    buckets = {"learning_update": 0.0, "environment": 0.0,
               "encoding_forward": 0.0, "other": 0.0}
    for (fn, ln, name), (_cc, _nc, _tt, ct, _cm) in st.stats.items():
        if "train_step" in name or "buffer" in name.lower():
            buckets["learning_update"] += ct
        elif name in ("step", "observe") or "world" in fn:
            buckets["environment"] += ct
        elif "encode" in name or name == "act":
            buckets["encoding_forward"] += ct
        else:
            buckets["other"] += ct
    total = sum(buckets.values())
    return buckets, total


def run_profile():
    lines = ["SPIKE profile jobs (200 episodes each; proportions only, "
             "never projection inputs)"]
    for arm, world, seed in PROFILE_JOBS:
        grid = grid_of(world)
        pr = cProfile.Profile()
        pr.enable()
        _agent, stats, _enc = train_loop(
            arm, seed, lambda w=world: make_world(w), grid, episodes=200)
        pr.disable()
        buckets, total = bucket_stats(pr)
        lines.append("")
        lines.append("job: %s/%s/%d episodes=200 reached=%d/%d"
                     % (arm, world, seed,
                        sum(1 for s in stats if s[1]), len(stats)))
        for k in ("learning_update", "environment",
                  "encoding_forward", "other"):
            pct = (100.0 * buckets[k] / total) if total else 0.0
            lines.append("  %-17s %8.2fs %5.1f%%"
                         % (k, buckets[k], pct))
        lines.append("  %-17s %8.2fs" % ("profile_total", total))
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
        ps.print_stats(15)
        lines.append("  top cumulative functions:")
        for ln in s.getvalue().splitlines():
            lines.append("    " + ln)
        print("SPIKE profile %s/%s/%d done" % (arm, world, seed),
              flush=True)
    with open(PROFILE_OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("SPIKE profile written to %s" % PROFILE_OUT, flush=True)


def run_components():
    """Direct component timing (replaces the cProfile attempt).

    The --profile cProfile bucketing summed CUMULATIVE times across
    the call tree, double-counting shared ancestors (its
    'profile_total' exceeded the job's wall time) -- invalid, and
    its file is preserved as exp1_spike_profile_cprofile_DISCARDED
    .txt. This mode instead times each per-step component
    separately on a live setup, plus one full-step loop for the
    residual. All times are wall clock, per call, microseconds.
    Setups mirror the training path exactly (make_encoder,
    NeuralQ, env_step_exp1); buffer pre-filled with 1000 real
    steps so train_step runs full batch-32 updates.
    """
    from agent_nn import NeuralQ
    from exp1_run import make_encoder, env_step_exp1
    from world import ACTIONS

    def timed(fn, n):
        t0 = time.perf_counter()
        for _ in range(n):
            fn()
        return (time.perf_counter() - t0) / n

    lines = ["SPIKE component timing (direct per-call measurement; "
             "shares from measured components + full-loop residual)"]
    for arm, world in [("plain", "W10"), ("wrapped", "M3")]:
        grid = grid_of(world)
        w = make_world(world)
        w.reset(start_tick=0)
        enc = make_encoder(arm, grid)
        enc.reset(w)
        agent = NeuralQ(0, n_inputs=enc.n_inputs)
        x = enc.encode(w)
        # Warm-up + buffer fill: 1000 real steps.
        for i in range(1000):
            a = agent.act(x, 0.5)
            r, reached, _c = env_step_exp1(w, a)
            x2 = enc.encode(w)
            agent.buffer.add((x, a, r, x2, reached))
            x = x2
        assert len(agent.buffer) >= agent.batch
        # Components (each timed alone, same setup).
        t_env = timed(lambda: env_step_exp1(w, 0), 2000)
        t_enc = timed(lambda: enc.encode(w), 2000)
        t_act = timed(lambda: agent.act(x, 0.0), 2000)
        t_add = timed(
            lambda: agent.buffer.add((x, 0, -0.01, x, False)), 5000)
        t_train = timed(lambda: agent.train_step(), 1000)

        def full_step():
            xx = enc.encode(w)
            aa = agent.act(xx, 0.0)
            rr, _rch, _cr = env_step_exp1(w, aa)
            xx2 = enc.encode(w)
            agent.buffer.add((xx, aa, rr, xx2, False))
            agent.train_step()
        t_full = timed(full_step, 1000)
        parts = {"environment": t_env, "encoding": t_enc,
                 "act_forward": t_act, "buffer_add": t_add,
                 "learning_update": t_train}
        s = sum(parts.values())
        resid = t_full - s
        lines.append("")
        lines.append("setup: %s/%s grid=%d (per-call microseconds)"
                     % (arm, world, grid))
        for k, v in parts.items():
            lines.append("  %-16s %9.1f us  share %5.1f%%"
                         % (k, v * 1e6, 100.0 * v / t_full))
        lines.append("  %-16s %9.1f us  share %5.1f%%"
                     % ("loop_residual", resid * 1e6,
                        100.0 * resid / t_full))
        lines.append("  %-16s %9.1f us  (sum of parts %9.1f us)"
                     % ("full_step", t_full * 1e6, s * 1e6))
        print("SPIKE components %s/%s done (full step %.1f us)"
              % (arm, world, t_full * 1e6), flush=True)
    with open(PROFILE_OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("SPIKE components written to %s" % PROFILE_OUT, flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--components", action="store_true")
    ap.add_argument("--plan", action="store_true")
    args = ap.parse_args()
    if args.plan:
        for arm, world, seed in TRAIN_JOBS:
            print("training %s %s %d" % (arm, world, seed))
            for ew, kind in evals_for(arm, world):
                print("  eval -> %s (%s)" % (ew, kind))
        print("trainings: %d, eval jobs: %d"
              % (len(TRAIN_JOBS),
                 sum(len(evals_for(a, w)) for a, w, _s in TRAIN_JOBS)))
    elif args.profile:
        run_profile()
    elif args.components:
        run_components()
    elif args.run:
        run_all()
    else:
        ap.print_help()
