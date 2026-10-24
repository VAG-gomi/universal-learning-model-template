#!/usr/bin/env python3
"""demo.py -- minimal runnable example for the template.

Trains ONE wrapped agent on the default world and greedily evaluates
it, printing the result. Written fresh for this repository.

Training uses the template's own trainer (train_wrapped from
agent_wrapped.py), which reuses the shared train_neural loop from
agent_nn.py — NOT a copied programme trainer. The training spec is
the established one (see README / paper §3): Q-learning with replay
(buffer 10000, batch 32, target sync 200), gamma 0.99, Adam lr 1e-3,
hidden layer 32 units, 2000 episodes, episode cap 200 ticks,
epsilon linear 1.0 -> 0.05 over 1000 episodes; rewards step -0.01 /
goal +1.0 / crush -1.0; RNG discipline training-start
random.Random(seed+1000), agent random.Random(seed), numpy
RandomState(seed). The training world is period 20, open 10.

Evaluation is greedy (epsilon = 0, weights frozen), one deterministic
episode per start phase (20 phases, period 20), using the SAME
encoder the agent trained with — so the ScheduleModel's schedule
knowledge persists from training into evaluation, exactly as it
would in deployment. The evaluation loop below is written fresh in
this file (it is not a programme evaluator): per episode, reset the
world at the start phase, reset the encoder (episode boundary only;
the model is never cleared), then act greedily on the encoder's
features until the goal, a crush, or the tick cap.

Run from the repository root as:  python3 TEMPLATE/demo.py
(or from TEMPLATE/ as:  python3 demo.py).
Seed 0 is fixed so the run is reproducible. Training 2000 episodes
takes a few minutes on one core; evaluation takes seconds.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.join(_HERE, "nn")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from world import World, ACTIONS
from agent_nn import env_step, EPISODE_CAP
from agent_wrapped import train_wrapped

SEED = 0
EPISODES = 2000
PERIOD = 20
OPEN_LEN = 10


def greedy_eval(agent, encoder):
    """One deterministic episode per start phase. Returns rows of
    (start_phase, reached, crushes, ticks)."""
    rows = []
    for start in range(PERIOD):
        w = World(period=PERIOD, open_len=OPEN_LEN)
        w.reset(start_tick=start)
        encoder.reset(w)
        x = encoder.encode(w)
        ticks = 0
        crushes = 0
        reached = False
        while ticks < EPISODE_CAP:
            a = agent.act(x, 0.0)  # epsilon = 0: greedy, weights frozen
            _r, reached, crushed = env_step(w, a)
            crushes += crushed
            x = encoder.encode(w)
            ticks += 1
            if reached:
                break
        rows.append((start, reached, crushes, ticks))
    return rows


def main():
    print("demo: training one wrapped agent (seed %d, %d episodes, "
          "world %d/%d) ..." % (SEED, EPISODES, PERIOD, OPEN_LEN))
    agent, stats, encoder = train_wrapped(SEED, episodes=EPISODES)
    train_reached = sum(1 for s in stats if s[1])
    print("training: reached %d/%d episodes" % (train_reached, len(stats)))
    m = encoder.model
    print("schedule model after training: period=%r, open_len=%r, "
          "known-fraction=%.3f"
          % (m.period, m.open_len, encoder.frac_known()))
    print("demo: greedy evaluation, one episode per start phase ...")
    rows = greedy_eval(agent, encoder)
    reached = sum(1 for r in rows if r[1])
    crushes = sum(r[2] for r in rows)
    ticks_ok = [r[3] for r in rows if r[1]]
    mean_ticks = (sum(ticks_ok) / len(ticks_ok)) if ticks_ok else None
    print("greedy eval: reached %d/20 phases, crushes %d, mean ticks "
          "over reached %s" % (reached, crushes, mean_ticks))
    print("per-phase reached: %s" % ([int(r[1]) for r in rows],))
    print("demo: DONE")


if __name__ == "__main__":
    main()
