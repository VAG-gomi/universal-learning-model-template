#!/usr/bin/env python3
"""exp1_sweep.py -- EXP1 Step 3 sweep runner (AUTHORIZED 2026-10-27).

Sweep records only. No SPIKE records are read, pooled, or counted
here. No weights are written to disk: a trained agent lives in
memory only for its own eval jobs, then is dropped.

Job grouping (task spec): train an agent, then evaluate its
trained world and (inside only) its held-out world in the same
process/session before discarding its weights, so evals match
the trained agent without saving weights to the repo.

Plan (frozen, from exp1_run.sweep_plan):
  trainings 60: inside W10/W20/W30 x plain/memory/wrapped x
      seeds 0-4 (45) + outside M1/M2/M3 x wrapped x seeds 0-4 (15)
  eval jobs 105: inside trained 45 + inside held-out 45 +
      outside trained 15
  total 165 arm-runs. Held-out: W10h (5,2), W20h (10,5),
      W30h (15,7). Greedy eval only: eps=0, weights frozen,
      20 episodes, one per start phase 0-19.
  Hyperparameters unchanged: 2000 episodes, hidden=32,
      lr=1e-3, schedule 20/10 everywhere, cap=200.

Files (all in this directory, all uncommitted unless the parent
verifies/commits/pushes them):
  exp1_sweep_records.jsonl       job-level, record="SWEEP",
      one line per completed training/eval job (plus
      resume_retrain note lines, which are NOT jobs)
  exp1_sweep_training.jsonl      one line per training, with
      per-episode ticks / reached_flags / crushes lists
      (mirrors exp1_run.run_sweep training record)
  exp1_sweep_eval_episodes.jsonl one line per eval episode,
      with step trajectories from evaluate_job

Resume / consistency (deterministic, no silent duplication):
  - A unit is skipped only if its training job record AND all
    its eval job records already exist.
  - A unit whose training exists but whose evals are incomplete
    is re-trained (weights were never saved); only the missing
    evals are written, plus a resume_retrain note line.
  - At load, any duplicate job record, any training summary
    without a job record, any eval job record without exactly
    20 episode lines, or any episode lines without a job
    record ABORTS the run before any training, so a partial
    write is reported, not silently duplicated or pooled.
  - A restart is disclosed in stdout (and in the run log);
    the cause, if known, is recorded by the operator, not
    invented by this script.

Usage:
  python3 exp1_sweep.py --plan   # print plan, run nothing
  python3 exp1_sweep.py --check  # load files, report counts only
  python3 exp1_sweep.py --run    # run/resume the full sweep
"""

import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from exp1_run import train_loop, evaluate_job, sweep_plan
from world_exp1 import make_world, HELDOUT_OF, PERIOD, OPEN_LEN

RECORDS = os.path.join(_HERE, "exp1_sweep_records.jsonl")
TRAIN_SUM = os.path.join(_HERE, "exp1_sweep_training.jsonl")
EVAL_EP = os.path.join(_HERE, "exp1_sweep_eval_episodes.jsonl")


def grid_of(name):
    return make_world(name).grid_size


def evals_for(arm, train_world):
    """Eval jobs for one trained agent: (eval_world, kind)."""
    jobs = [(train_world, "trained")]
    if train_world in HELDOUT_OF:
        jobs.append((HELDOUT_OF[train_world], "held-out"))
    return jobs


def _load_jsonl(path):
    rows = []
    if os.path.exists(path):
        with open(path) as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    raise SystemExit(
                        "ABORT: %s line %d is not valid JSON "
                        "(partial write?); STOP for parent direction"
                        % (path, i))
    return rows


def load_state():
    """Return (done_t, done_e, resume_notes, checks).

    Aborts on any inconsistency, per the module docstring.
    """
    recs = _load_jsonl(RECORDS)
    done_t, done_e = set(), set()
    notes = 0
    for r in recs:
        if r.get("record") != "SWEEP":
            raise SystemExit("ABORT: non-SWEEP record in %s" % RECORDS)
        jt = r.get("job_type")
        if jt == "training":
            key = (r["arm"], r["world"], r["seed"])
            if key in done_t:
                raise SystemExit("ABORT: duplicate training job %r" % (key,))
            done_t.add(key)
        elif jt == "eval":
            key = (r["arm"], r["seed"], r["train_world"], r["eval_world"])
            if key in done_e:
                raise SystemExit("ABORT: duplicate eval job %r" % (key,))
            done_e.add(key)
        elif jt == "resume_retrain":
            notes += 1
        else:
            raise SystemExit("ABORT: unknown job_type %r in %s" % (jt, RECORDS))
    tsum = _load_jsonl(TRAIN_SUM)
    tsum_keys = set()
    for r in tsum:
        key = (r["arm"], r["world"], r["seed"])
        if key in tsum_keys:
            raise SystemExit("ABORT: duplicate training summary %r" % (key,))
        tsum_keys.add(key)
    if tsum_keys - done_t:
        raise SystemExit(
            "ABORT: training summary without job record: %r; "
            "STOP for parent direction" % sorted(tsum_keys - done_t))
    if done_t - tsum_keys:
        raise SystemExit(
            "ABORT: training job record without summary: %r; "
            "STOP for parent direction" % sorted(done_t - tsum_keys))
    eps = _load_jsonl(EVAL_EP)
    ep_counts = {}
    for r in eps:
        key = (r["arm"], r["seed"], r["train_world"], r["world"])
        ep_counts[key] = ep_counts.get(key, 0) + 1
    for key, n in ep_counts.items():
        if key not in done_e:
            raise SystemExit(
                "ABORT: eval episodes without job record: %r (%d eps); "
                "STOP for parent direction" % (key, n))
        if n != 20:
            raise SystemExit(
                "ABORT: eval job %r has %d episode lines, expected 20; "
                "STOP for parent direction" % (key, n))
    for key in done_e:
        if ep_counts.get(key, 0) != 20:
            raise SystemExit(
                "ABORT: eval job record %r without 20 episode lines; "
                "STOP for parent direction" % (key,))
    return done_t, done_e, notes, {
        "job_lines": len(recs), "train_summaries": len(tsum),
        "eval_episodes": len(eps)}


def append_jsonl(path, rec):
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")
        f.flush()


def append_job(rec):
    rec = dict(rec)
    rec["record"] = "SWEEP"
    rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    append_jsonl(RECORDS, rec)


def run_unit(arm, world, seed, done_t, done_e, record_training):
    grid = grid_of(world)
    t0 = time.perf_counter()
    agent, stats, _enc = train_loop(
        arm, seed, lambda w=world: make_world(w), grid)
    wall = time.perf_counter() - t0
    reached = sum(1 for s in stats if s[1])
    ticks_total = sum(s[0] for s in stats)
    crushes_total = sum(s[2] for s in stats)
    if record_training:
        append_jsonl(TRAIN_SUM, {
            "record": "SWEEP", "kind": "training", "arm": arm,
            "seed": seed, "world": world, "episodes": len(stats),
            "reached": reached,
            "ticks": [s[0] for s in stats],
            "reached_flags": [bool(s[1]) for s in stats],
            "crushes": [s[2] for s in stats], "wall_s": wall})
        append_job({"job_type": "training", "arm": arm, "world": world,
                    "seed": seed, "episodes": len(stats), "wall_s": wall,
                    "reached": reached, "ticks_total": ticks_total,
                    "crushes_total": crushes_total,
                    "period": PERIOD, "open_len": OPEN_LEN,
                    "hidden": 32, "lr": 1e-3, "grid_size": grid})
        print("SWEEP training %s/%s/%d wall=%.1fs reached=%d/%d"
              % (arm, world, seed, wall, reached, len(stats)), flush=True)
    else:
        append_job({"job_type": "resume_retrain", "arm": arm,
                    "world": world, "seed": seed,
                    "episodes": len(stats), "wall_s": wall,
                    "note": "re-train after restart to recover evals; "
                            "NOT a training job, NOT counted"})
        print("SWEEP resume_retrain %s/%s/%d wall=%.1fs (evals only)"
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
        for rec in recs:
            rec = dict(rec)
            rec.update({"record": "SWEEP", "arm": arm, "seed": seed,
                        "period": PERIOD, "open_len": OPEN_LEN,
                        "grid_size": egrid, "train_world": world,
                        "eval_kind": kind})
            append_jsonl(EVAL_EP, rec)
        append_job({"job_type": "eval", "arm": arm, "seed": seed,
                    "train_world": world, "eval_world": eval_world,
                    "eval_kind": kind, "episodes": len(recs),
                    "wall_s": ewall,
                    "reached": sum(1 for r in recs if r["reached"]),
                    "ticks_total": sum(r["ticks"] for r in recs),
                    "crushes_total": sum(r["crushes"] for r in recs),
                    "protocol": "greedy eps=0 weights frozen 20 phases",
                    "period": PERIOD, "open_len": OPEN_LEN,
                    "grid_size": egrid})
        print("SWEEP eval %s/%s/%d -> %s (%s) wall=%.1fs reached=%d/20"
              % (arm, world, seed, eval_world, kind, ewall,
                 sum(1 for r in recs if r["reached"])), flush=True)
    del agent


def run_all():
    trainings, _eval_jobs, counts = sweep_plan()
    done_t, done_e, _notes, checks = load_state()
    print("SWEEP resume state: trainings=%d evals=%d "
          "(existing job lines=%d train summaries=%d eval episodes=%d)"
          % (len(done_t), len(done_e), checks["job_lines"],
             checks["train_summaries"], checks["eval_episodes"]),
          flush=True)
    for arm, world, seed in trainings:
        need_evals = [(arm, seed, world, ew)
                      for ew, _k in evals_for(arm, world)]
        train_done = (arm, world, seed) in done_t
        evals_done = all(k in done_e for k in need_evals)
        if train_done and evals_done:
            print("SWEEP skip %s/%s/%d (already recorded)"
                  % (arm, world, seed), flush=True)
            continue
        run_unit(arm, world, seed, done_t, done_e,
                 record_training=not train_done)
        done_t, done_e, _n, _c = load_state()
    print("SWEEP run complete: plan %s" % (counts,), flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.plan:
        _t, _e, counts = sweep_plan()
        print(json.dumps(counts, sort_keys=True))
    elif args.check:
        done_t, done_e, notes, checks = load_state()
        print(json.dumps({"trainings": len(done_t), "evals": len(done_e),
                          "resume_retrain_notes": notes, **checks},
                         sort_keys=True))
    elif args.run:
        run_all()
    else:
        ap.print_help()
