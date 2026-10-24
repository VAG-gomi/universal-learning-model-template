# Implementation: How to Build Around the Template

Standalone instructions. Followable from the template alone, plus
proof pointers into the workbench where the paper's evidence lives.
You do not need workbench knowledge to follow these steps — except
for the proof pointers, which resolve into
[`VAG-gomi/time-based-mind-model`](https://github.com/VAG-gomi/time-based-mind-model)
at the commits given.

## Step 1. Take the template

Clone this repository, run the demo, and confirm it reproduces
(trains + evaluates) before changing anything:

```sh
python3 TEMPLATE/demo.py
```

The demo trains one wrapped agent (seed 0, 2000 episodes, 20/10
world) and greedily evaluates one deterministic episode per start
phase, printing training reached, the schedule model's estimates,
and greedy eval reached/20. If the demo does not run, stop: fix
the environment (Python 3, numpy) before adapting anything. A
template you have not seen run is a template you do not
understand yet.

## Step 2. Define your world

States, actions, rewards — and, if time matters in your task,
state its time structure explicitly (periods, openings,
durations), the way the default world states its schedules. The
default world is a 10×10 grid, spawn (0,0), goal (9,9), wall
column x=5 except the door cell (5,5), door open iff
`tick % period < open_len`, crush back to start when caught in
the door cell at closing, rewards step −0.01 / goal +1.0 /
crush −1.0.

Your world need not be a grid. It must be explicit: what the
agent can be in, what it can do, what happens on each action,
and — if anything in it changes with time — the exact rule by
which it changes. A time structure stated only as "the door
sometimes opens" is not a specification; "period 20, open 10,
open iff tick % 20 < 10" is. If your task has no time structure,
say so and use the plain or memory agent; do not invent one to
justify the wrapper.

## Step 3. Choose features

Explicit, symbolic, named — what the agent can sense, nothing
hidden. If a feature cannot be named, it does not go in. The
template's feature sets are the pattern:

- Plain: one-hot position + door bit.
- Memory: plain + previous tick's door bit.
- Wrapped: plain + phase (ticks since opening) + opening
  remaining + known flag, all from a schedule model fed only
  `(tick, door_open)` observations.

When you add a feature, write down what it is, what feeds it, and
what it must never see (the schedule model must never see
position, reward, actions, or any episode counter — otherwise
your "time" features are contaminated with task answers). When
you adapt the wrapped encoder to another schedule, re-derive its
scales: the template's 20.0/10.0 are fixed to the 20/10 schedule
and will silently distort inputs on any other schedule.

## Step 4. Choose agent type

- **Plain** (no memory): the baseline. If plain solves your task,
  you do not have a time problem, and the wrapper adds nothing.
- **Memory** (one-step memory control): the control that
  separates "any memory" from "time structure". If memory matches
  the wrapped arm, the wrapper adds nothing beyond one-step
  history.
- **Wrapped** (schedule-as-experience features): for tasks where
  time structure itself must be sensed — periods, countdowns,
  openings — and learned from reward rather than handed over.

Warning, from the journey: more features do not by themselves
mean better agents. In schedule-varied training, the plain arm
scored 0/100 in the F0 sanity world against 70/100 in
multi-door worlds, and the memory arm 0/100 against 90/100 —
superiority flipped by world (workbench `nn/decisions_pdb2.md`
at commit `35fa992`). And separated agents included oracle ones
in the fine-tuning study. Choose the agent type by what your
task's structure demands, then let the held-out evaluation
judge it — not the feature count.

## Step 5. Train

The template spec (see also the paper §3):

- Q-learning with experience replay: buffer 10000, batch 32,
  target sync 200, gamma 0.99, Adam lr 1e-3, hidden layer 32.
- 2000 episodes, episode cap 200 ticks, ε linear 1.0 → 0.05
  over 1000 episodes, then flat 0.05.
- Rewards: step −0.01, goal +1.0, crush −1.0.
- RNG discipline: training-start `random.Random(seed+1000)`,
  agent `random.Random(seed)`, numpy `RandomState(seed)`.

Record seeds, RNG streams, and episode counts so any training
reproduces exactly. A training you cannot reproduce is a
training you cannot learn from: when it behaves unexpectedly,
you will not know whether the design, the seed, or a bug is
responsible. Never retune per seed to rescue a result; report
every seed and every failure.

## Step 6. Evaluate

- **Trained worlds vs held-out worlds kept apart from the
  start.** Decide which worlds are held out before training,
  and never train on them — not even "just to check". A held-out
  world the training ever touched is not held out.
- **Greedy AND noisy evaluation.** Greedy (ε=0, weights frozen,
  one deterministic episode per start phase) tests the frozen
  policy. Noisy evaluation (small ε, e.g. 0.05, with a fresh
  RNG stream per rep) tests whether a greedy failure is frozen
  or fragile. Run both: a greedy-only test hid failures that
  noise partly unlocked, and a noisy-only test would hide that
  the policy itself is broken.
- **Bars stated BEFORE running, and frozen.** Commit the bar,
  the rule, and the verdict precedence before results exist.
  Never move them after. A bar moved after results is not a
  bar; it is a description of the results wearing a bar's name.
- **Verdicts from the frozen rules.** If the pooled number
  misses the bar, the verdict is what the rule says — including
  UNINTERPRETABLE (the test cannot answer the question) and
  NEITHER (between lift and no lift). Those are answers, not
  failures to answer. Do not upgrade them in prose.
- **Controls.** Include a control that would expose a broken
  test: a healthy policy that must pass under both greedy and
  noisy evaluation. If the control fails, the probe is
  uninterpretable on control grounds, whatever the headline
  numbers say.

## Step 7. Report

Reconciliations first, then numbers, then verdict:

1. **Reconciliations:** record completeness (every job, every
   rep, every phase present exactly once), duplicates (zero),
   determinism checks (retrainings reproduce frozen records
   exactly before evaluating), RNG compliance (every random
   draw from the specified stream, nothing else).
2. **Numbers:** with denominators and protocol bounds, from
   frozen records only. Never a number from memory, never a
   number borrowed from another programme's pooled totals.
3. **Verdict:** from the frozen rule, written by the verifier —
   never pre-claimed by the executor. A draft that claims its
   own verification is corrupt by construction. Leave the
   verdict section for the verifying session to write, and
   flip title, status, and commit message to the ruled verdict
   together, at commit time, not before.

## Worked adaptation sketch (PATTERN, not a claimed run)

Adapting the template to a second tiny domain, step by step.
This sketch is a **pattern for the reader to follow; it is NOT
claimed as an executed build**. A real second-domain build is
future work, and only it can test universality.

Suppose a second domain: a corridor with two doors on different
schedules (say 12/5 and 30/14), one agent, one goal beyond both.

1. **World (Step 2):** grid as in the template, but two door
   cells, each with its own period/open_len, each with the same
   crush rule. State both schedules explicitly; state which
   door must be crossed first (if any ordering constraint
   exists) or that either order is allowed.
2. **Features (Step 3):** position one-hot + two door bits +
   two schedule-feature triples (phase, remaining, known) from
   two schedule-model instances, each fed only its own door's
   `(tick, door_open)` observations. Name every feature; the
   models must never see position or reward.
3. **Agent (Step 4):** start with plain (baseline) and memory
   (control) before wrapped — if plain solves it, there is no
   time problem to solve. The wrapped arm carries two schedule
   models, not one; its feature scales are re-derived per door
   (12.0/5.0 and 30.0/14.0), not carried over from 20.0/10.0.
4. **Train (Step 5):** the template spec unchanged (2000
   episodes, same hyperparameters, same RNG discipline), seeds
   recorded. Note where the sketch bites: the training world
   must randomize start phases for both doors, or the agent
   memorizes one phase alignment.
5. **Evaluate (Step 6):** trained door schedules vs held-out
   schedules (e.g. a 20/10 pair never trained on) kept apart
   from the start; greedy AND noisy eval; bars stated before
   running (e.g. held-out reached ≥ 20% absolute AND ≥ 50% of
   trained — stated here only as an example bar shape, not a
   result). Verdict from the frozen rule.
6. **Report (Step 7):** reconciliations first (both schedule
   models' convergence reported separately — a model that never
   converged is a different finding from an agent that never
   learned), then numbers, then verdict.

Where each instruction bites is the point: Step 2 bites on the
two schedules (state them, don't gesture at them); Step 3 bites
on the per-door models (no cross-contamination); Step 4 bites on
the baselines (run plain and memory first); Step 6 bites on the
held-out schedules (decide them before training, not after the
first promising run).

## Pitfalls, from the journey (each with its workbench pointer)

- **Memorization vs concepts (test held-out from the start).**
  Agents learned "go to (5,5)", not a door concept: 1471/1471
  reached multi-door episodes crossed first at the familiar
  door (workbench `nn/decisions_doors.md` at `2ad12f7`). If
  your evaluation has no held-out world, you are measuring
  memorization and calling it learning.
- **Greedy traps (test noisy eval too).** A frozen greedy
  failure partly unlocked under noise (memory/3 F3: greedy
  0/20 → noisy 45/100; workbench `nn/decisions_prb1.md` at
  `15fc230`), and noise lifted MD1 seed-0 agents 2.56× without
  reaching the bar (workbench `nn/decisions_prb2.md` at
  `5633e2d`). Greedy-only evaluation hides both facts.
- **Moving bars after results.** Every verdict in the paper
  comes from a rule frozen before results existed. Move a bar
  after results and the verdict is void, however good the new
  bar looks.
- **Pooling across programmes.** MD1's pooled numbers cover
  30 fresh agents; PRB2's cover 6 seed-0 retrains. Pooling
  them would fabricate a sample that never ran. Never pool
  across programmes, protocols, or seeds that were not run
  together.
- **Pre-claims of verification.** The executor's report is a
  draft until the verifier writes the verdict section. Title,
  status, and commit message change together, at commit time.
  Anything else is a pre-claim, and pre-claims have corrupted
  this project's reports before.
- **Confusing training performance with eval competence.**
  MD1 training reached 21.4–29.2% per arm (plain 21.4%,
  wrapped 29.0%), while frozen greedy eval on trained rows fell
  to 1.75% (plain) and 5.00% (wrapped), pooled 8.08%
  (workbench `nn/decisions_md1.md` at `f601339`). Training
  curves are not competence; frozen greedy eval from uniform
  start phases is the competence test, and noisy eval is its
  complement — run both, report both.
- **Treating UNINTERPRETABLE or NEITHER as failure.** They are
  verdicts. MD1's UNINTERPRETABLE stopped a following claim
  that the evidence could not support; PRB2's NEITHER recorded
  a real, partial lift. A programme that returns either has
  answered its question honestly.
