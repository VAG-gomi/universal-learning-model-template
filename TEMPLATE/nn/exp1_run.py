#!/usr/bin/env python3
"""exp1_run.py -- EXP1 Step 0 runner (WO-TBM-EXP1, Step 0).

Additive only. No existing world, trainer, or record file is
edited. This module provides the training and greedy-evaluation
pieces the EXP1 sweep composes; it runs no sweep training and no
sweep evaluation on import. Step 0 exercises only:
  train_loop() -- via nn/exp1_fidelity.py (the W10 fidelity check);
  evaluate_job() -- via the --smoke CLI (one greedy eval job on
      W10, plumbing only).
run_sweep() is DORMANT in Step 0: it is written, not run, and
stays unrun until sweep authorization (after verification,
spike-first gate ruling, spike, and proceed ruling).

Training loop: train_neural() (agent_nn.py) mirrored line-for-line
except for two stated changes:
  (1) the world instantiated per episode comes from the caller's
      world_factory (an EXP1 world or world.World), instead of
      World(period=20, open_len=10);
  (2) the goal is read from the world object (world.goal_pos,
      falling back to agent_nn.GOAL_POS for world.World), instead
      of the module constant.
Everything else -- NeuralQ learner, replay buffer, target sync,
epsilon schedule, rewards, crush handling via the log (the EXP1
worlds log "crushed" in the same format), RNG seeding (agent
stream Random(seed) inside NeuralQ, start-tick stream
Random(seed + 1000)), episode count, cap -- is identical to
train_neural. The encoder is created once per training and
persists across episodes (reset per episode), exactly as in
train_neural / train_wrapped.

Evaluation: one greedy job = 20 episodes, one per start phase
0..19, weights frozen, eps=0. The encoder is FRESH per
(agent, eval world) job and persists across that job's 20
episodes (the post-FT1 standard, cf. md1_run.evaluate):
for wrapped this means the ScheduleModel starts blank at
each eval world and converges during the job's episodes.
Blank-feature warm-up is audited per episode (blank_feature:
any step whose known-flag slot is 0.0; first_known_step: the
first step index with known flag 1.0, else None). For
plain/memory the known slot does not exist, so blank is
always False and first_known_step always None.

Record schema (per episode): kind, world, start_phase, ticks,
crushes, reached, return (accumulated env-step reward total),
blank_feature, first_known_step, steps, arm, seed, period,
open_len, grid_size. Step records carry t, x, y, action,
door, crushed, plus f_phase / f_remaining / f_known for
wrapped arms (the time-feature slots). Training records
carry per-episode (ticks, reached, crushes, mean_loss) --
summaries only, never trajectories, exactly as in all
prior programmes. Eval trajectories ARE recorded (they
are the failure-anatomy material for a scaling test);
at 105 eval jobs x 20 episodes x <=200 steps the
compact volume stays well under the 100 MB/file limit
(MD1's 6600 eval episodes compacted to 93.9 MB; EXP1's
2100 eval episodes are under a third of that), with
gzip as the fallback if a later ruling adds more.

Sweep plan (frozen by the design note, NOT run in Step 0):
  trainings: inside 3 arms x 3 worlds x 5 seeds = 45, plus
      outside wrapped x 3 worlds x 5 seeds = 15  -> 60;
  eval jobs: inside trained 45 + inside held-out 45 +
      outside trained 15 -> 105;
  total 165 arm-runs (trigger FIRES; spike-first gate).
"""

import json
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np

from agent_nn import (NeuralQ, PlainEncoder, EPISODE_CAP, epsilon,
                      ACTION_NAMES, GOAL_POS)
from agent_mem import MemoryEncoder
from agent_wrapped import WrappedEncoder
from world import World
from world_exp1 import (PERIOD, OPEN_LEN, make_world, INSIDE_WORLDS,
                        HELDOUT_OF, OUTSIDE_WORLDS)

ARMS_INSIDE = ["plain", "memory", "wrapped"]
ARMS_OUTSIDE = ["wrapped"]
SEEDS = [0, 1, 2, 3, 4]


def env_step_exp1(world, action_idx):
    """Apply action; return (reward, reached_goal, crushed).

    Mirrors agent_nn.env_step exactly, except the goal is read
    from the world object (world.goal_pos) so bigger worlds
    count their own goal. For world.World, goal_pos is absent
    and GOAL_POS (9, 9) is used -- identical behavior.
    """
    from world import ACTIONS as _ACTIONS
    n_log = len(world.log)
    world.step(_ACTIONS[ACTION_NAMES[action_idx]])
    crushed = any(e[2] == "crushed" for e in world.log[n_log:])
    goal = getattr(world, "goal_pos", GOAL_POS)
    reached = world.agent == goal
    r = -0.01 + (-1.0 if crushed else 0.0) + (1.0 if reached else 0.0)
    return r, reached, crushed


def make_encoder(arm, grid_size):
    """Fresh encoder for one (arm, world) training or eval job.

    NOTE: keyword args throughout -- WrappedEncoder's first
    positional parameter is `model`, not `grid_size`, so a
    positional call would silently set the model to an int.
    """
    if arm == "plain":
        return PlainEncoder(grid_size=grid_size)
    if arm == "memory":
        return MemoryEncoder(grid_size=grid_size)
    if arm == "wrapped":
        return WrappedEncoder(grid_size=grid_size)
    raise ValueError("unknown arm %r" % (arm,))


def train_loop(arm, seed, world_factory, grid_size, hidden=32,
               episodes=2000, cap=EPISODE_CAP, lr=1e-3):
    """train_neural mirrored for a world factory (see module docstring).

    Returns (agent, stats, encoder) with stats in train_neural
    format: (ticks, reached, crushes, mean_loss) per episode.
    """
    encoder = make_encoder(arm, grid_size)
    agent = NeuralQ(seed, hidden=hidden, lr=lr,
                    n_inputs=encoder.n_inputs)
    start_rng = random.Random(seed + 1000)
    stats = []
    for ep in range(episodes):
        w = world_factory()
        w.reset(start_tick=start_rng.randrange(PERIOD))
        encoder.reset(w)
        x = encoder.encode(w)
        eps = epsilon(ep)
        ticks = 0
        crushes = 0
        reached = False
        losses = []
        while ticks < cap:
            a = agent.act(x, eps)
            r, reached, crushed = env_step_exp1(w, a)
            crushes += crushed
            x2 = encoder.encode(w)
            agent.buffer.add((x, a, r, x2, reached))
            loss = agent.train_step()
            if loss is not None:
                losses.append(loss)
            x = x2
            ticks += 1
            if reached:
                break
        mean_loss = (sum(losses) / len(losses)) if losses else None
        stats.append((ticks, reached, crushes, mean_loss))
    return agent, stats, encoder


def evaluate_job(agent, arm, world_factory, world_name, grid_size):
    """One greedy eval job: 20 episodes, one per start phase.

    Fresh encoder for the job (see module docstring); the
    encoder persists across the job's episodes, reset per
    episode. Returns episode records (without arm / seed /
    period / open_len / grid_size, which the caller adds).
    """
    encoder = make_encoder(arm, grid_size)
    records = []
    for start in range(PERIOD):
        w = world_factory()
        w.reset(start_tick=start)
        encoder.reset(w)
        steps = []
        total = 0.0
        crushes = 0
        reached = False
        ticks = 0
        while ticks < EPISODE_CAP:
            x = encoder.encode(w)
            a = agent.act(x, 0.0)
            (px, py), door = w.observe()
            r, reached, crushed = env_step_exp1(w, a)
            rec = {"t": w.tick - 1, "x": px, "y": py,
                   "action": ACTION_NAMES[a],
                   "door": bool(door), "crushed": bool(crushed)}
            if arm == "wrapped":
                rec.update({"f_phase": float(x[grid_size * grid_size + 1]),
                            "f_remaining": float(
                                x[grid_size * grid_size + 2]),
                            "f_known": float(
                                x[grid_size * grid_size + 3])})
            steps.append(rec)
            total += r
            crushes += int(crushed)
            ticks += 1
            if reached:
                break
        if arm == "wrapped":
            known_steps = [i for i, s in enumerate(steps)
                           if s["f_known"] == 1.0]
            blank = len(known_steps) < len(steps)
            first_known = known_steps[0] if known_steps else None
        else:
            blank = False
            first_known = None
        records.append({
            "kind": "episode", "world": world_name,
            "start_phase": start, "ticks": ticks,
            "crushes": crushes, "reached": reached,
            "return": total, "blank_feature": blank,
            "first_known_step": first_known, "steps": steps})
    return records


def sweep_plan():
    """The full sweep job list (frozen design; NOT run in Step 0).

    Returns (trainings, eval_jobs, counts) where trainings are
    (arm, world, seed) and eval_jobs are (arm, seed, train_world,
    eval_world, kind) with kind in ("trained", "held-out").
    """
    trainings = []
    eval_jobs = []
    for arm in ARMS_INSIDE:
        for world in INSIDE_WORLDS:
            for seed in SEEDS:
                trainings.append((arm, world, seed))
                eval_jobs.append((arm, seed, world, world, "trained"))
                eval_jobs.append((arm, seed, world, HELDOUT_OF[world],
                                  "held-out"))
    for arm in ARMS_OUTSIDE:
        for world in OUTSIDE_WORLDS:
            for seed in SEEDS:
                trainings.append((arm, world, seed))
                eval_jobs.append((arm, seed, world, world, "trained"))
    counts = {"trainings": len(trainings),
              "eval_jobs": len(eval_jobs),
              "arm_runs": len(trainings) + len(eval_jobs)}
    return trainings, eval_jobs, counts


def save_weights(agent, path):
    """Save a trained agent's network params (sanity artifact only;
    never a sweep record, never committed)."""
    params = agent.net.get_params()
    np.savez(path, **{"w%d" % i: p for i, p in enumerate(params)})


def load_weights(agent, path):
    """Load network params saved by save_weights into `agent`."""
    data = np.load(path)
    params = [data["w%d" % i] for i in range(len(data.files))]
    agent.net.set_params(params)
    agent.target.set_params(params)


def run_sweep(out_dir):
    """DORMANT in Step 0 -- written, not run.

    Executes sweep_plan(): for each training, train on the
    trained world, save the training summary, then run the
    trained-world eval job and (inside only) the held-out
    eval job. Records are JSONL, one line per episode, plus
    one training-summary line per training. Duplicate guard:
    a (kind, arm, seed, world) key already present in the
    output aborts the run instead of appending duplicates.
    This function runs ONLY after sweep authorization.
    """
    trainings, eval_jobs, counts = sweep_plan()
    os.makedirs(out_dir, exist_ok=True)
    eval_path = os.path.join(out_dir, "results_exp1.jsonl")
    train_path = os.path.join(out_dir, "training_exp1.jsonl")
    seen = set()
    if os.path.exists(eval_path):
        with open(eval_path) as f:
            for line in f:
                r = json.loads(line)
                seen.add((r["kind"], r["arm"], r["seed"], r["world"]))
    grid_of = {}
    for name in list(INSIDE_WORLDS) + list(HELDOUT_OF.values()) \
            + list(OUTSIDE_WORLDS):
        grid_of[name] = make_world(name).grid_size
    with open(eval_path, "a") as ef, open(train_path, "a") as tf:
        for arm, world, seed in trainings:
            grid = grid_of[world]
            agent, stats, _enc = train_loop(
                arm, seed, lambda w=world: make_world(w), grid)
            tf.write(json.dumps({
                "kind": "training", "arm": arm, "seed": seed,
                "world": world, "episodes": len(stats),
                "reached": sum(1 for s in stats if s[1]),
                "ticks": [s[0] for s in stats],
                "reached_flags": [bool(s[1]) for s in stats],
                "crushes": [s[2] for s in stats]}) + "\n")
            tf.flush()
            for (a2, s2, tw, ew, kind) in eval_jobs:
                if (a2, s2) != (arm, seed) or tw != world:
                    continue
                key = ("episode", arm, seed, ew)
                if key in seen:
                    raise SystemExit(
                        "duplicate eval job %r; aborting" % (key,))
                recs = evaluate_job(agent, arm,
                                    lambda w=ew: make_world(w), ew,
                                    grid_of[ew])
                for rec in recs:
                    rec.update({"arm": arm, "seed": seed,
                                "period": PERIOD, "open_len": OPEN_LEN,
                                "grid_size": grid_of[ew],
                                "train_world": tw, "eval_kind": kind})
                    ef.write(json.dumps(rec) + "\n")
                    seen.add(key)
                ef.flush()
    return counts


def _smoke(weights_path):
    """Step 0 smoke (c): one greedy eval job on W10, plumbing only.

    Loads a sanity-trained agent's weights (saved by the
    fidelity script to a temp path, never a record) and runs
    one full 20-phase greedy job on W10 through evaluate_job.
    Returns the per-episode (phase, reached, ticks, crushes).
    """
    agent = NeuralQ(0, n_inputs=PlainEncoder(grid_size=10).n_inputs)
    load_weights(agent, weights_path)
    recs = evaluate_job(agent, "plain",
                        lambda: World(period=PERIOD, open_len=OPEN_LEN),
                        "W10", 10)
    return [(r["start_phase"], r["reached"], r["ticks"], r["crushes"])
            for r in recs]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true",
                    help="print the sweep plan counts as JSON")
    ap.add_argument("--smoke", metavar="WEIGHTS",
                    help="run one greedy eval job on W10 from WEIGHTS")
    args = ap.parse_args()
    if args.plan:
        _t, _e, counts = sweep_plan()
        print(json.dumps(counts, sort_keys=True))
    elif args.smoke:
        for row in _smoke(args.smoke):
            print(row)
    else:
        ap.print_help()
