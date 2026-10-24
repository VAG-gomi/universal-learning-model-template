# The Universal Learning-Model Template: A Study Paper with Proof

**Status: DRAFT — awaiting owner Step 6 review. No claim of
verification or publication is made here.**

## 1. Title and abstract

**What the template is.** A small, symbolic, inspectable design for
building AI models: a grid world with a periodic door schedule, a
hand-written neural network, three agent types on one shared
learner, and a schedule model that turns observed door transitions
into time features. The full design is in `TEMPLATE/`; the reasons
behind it are in `TEMPLATE/principles.md`.

**What this paper claims (ESTABLISHED, each with a proof pointer
into the workbench).** On one grid task, schedule information helps
a network cross a periodic door; the same agents memorize locations
rather than generalize; a novel door is not crossed without
training on it; fine-tuning buys partial acquisition at near-total
forgetting; noise partly unlocks frozen greedy failures but does not
rescue agents to a pre-stated bar; and a moving-door training
programme returned UNINTERPRETABLE under greedy evaluation. Every
claim below carries its workbench commit and file, its numbers with
denominators and protocol bounds, and what it does **not** prove.

**What this paper does NOT claim.** Generalization to novel doors,
tasks, or domains; language; any second domain built on the
template. "Universal" is a **design intent with a reason**
(simplicity + explicitness + inspectability = liftability), not a
proven result. Until a second-domain build exists, universality is
the design's promise, and this paper says so wherever the word
appears.

## 2. Founding goal

A house for everyday AI creation. Don't hand the model order; let
it be thought, get learned, then act by itself. Substrate before
occupants: build the inspectable world first, and let capabilities
grow on it — the lineage grows into language, not a swap that
brings in a ready-made model from outside. The template is the
foundation layer of that house, kept small enough that every part
of it can be seen, named, and re-derived.

## 3. The substrate

**The world** (`TEMPLATE/world.py`). A 10×10 grid, spawn (0,0),
goal (9,9), a wall covering column x=5 except the door cell (5,5).
The door follows a periodic schedule: open iff
`tick % period < open_len`. The `World` class takes any
period/open_len; the template's training path uses period 20, open
10. A blocked move leaves the agent where it was; an agent caught
in the door cell when the door closes is crushed back to the start
and the episode continues. Rewards: step −0.01, goal +1.0,
crush −1.0.

**The network** (`TEMPLATE/nn/nnet.py`). A hand-written MLP:
fully connected, tanh hidden layers, linear output, float64, numpy
only, no frameworks. Xavier initialization; Adam with bias
correction; a masked mean-squared-error loss that puts error only
on the chosen action's output (Q-learning regression).

**The learner** (`TEMPLATE/nn/agent_nn.py`). Q-learning with
experience replay (buffer 10000, batch 32, target sync 200),
gamma 0.99, Adam lr 1e-3, hidden layer 32 units, 2000 episodes,
episode cap 200 ticks, ε linear 1.0 → 0.05 over 1000 episodes
then flat. Reproducibility discipline: training-start
`random.Random(seed+1000)`, agent `random.Random(seed)`, numpy
`RandomState(seed)`. Greedy evaluation means ε=0, weights frozen,
one deterministic episode per start phase.

**The agent types** (one learner, three encoders).

- **Plain** (`agent_nn.py`, 101 inputs): one-hot position (100) +
  door bit (1). No tick, no period, no history.
- **Memory** (`agent_mem.py`, 102 inputs): plain inputs + the
  previous tick's door bit. One bit of history: enough to detect a
  transition, carrying no schedule model. This arm is the control
  that separates "any memory" from "time structure".
- **Wrapped** (`agent_wrapped.py`, 104 inputs): plain inputs + 3
  schedule features from the `ScheduleModel` (`wrapper.py`):
  cycle phase (ticks since opening, scaled by 20.0), opening
  remaining (ticks of opening left, scaled by 10.0), and a known
  flag (1.0 iff the time features are available). The model sees
  only `(tick, door_open)` observations, once per observation;
  period and open length come from clean spans only (see
  `TEMPLATE/principles.md` §4); contradictions drop stale events
  and re-estimate, with estimates honestly `None` until supported.
  Deliberately, there is no "safe to cross" bit. The wrapped
  encoder's scales (20.0/10.0) are fixed to the 20/10 training
  schedule and must be re-derived on any other schedule.

**What is not in the template.** No trust machinery: none is part
of the shipped substrate at the source commit (the only "beta"
terms are Adam's optimizer terms). The trust design is a
methodology note in §4 below, not template code. No trained
weights: weights are reproductions of training, and the design is
the product.

## 4. The journey, distilled

Each stage: the question, the verdict, the proof pointer. Depth
stays distilled; the workbench holds the full reports, records,
and analyses. All verdicts below are the workbench programmes'
own verdicts under their own frozen rules.

### B2 — Does the schedule wrapper win?

**Question:** on the pilot task, does a wrapped agent beat the
pre-registered clean-and-fast bar? **Verdict: NO.** Wrapped
5/10 clean-and-fast against a bar of 7/10 — it did NOT win.
The raw-clock control scored 0/10. (Workbench:
`nn/decisions_b2.md` at commit `5633e2d`.)

### Replication — Does schedule information help at all?

**Question:** with more seeds, does the wrapped arm beat plain
and memory arms? **Verdict: YES, schedule information helps.**
Wrapped 26/40 vs plain 0/40 vs memory 7/40. No follow-up
experiment under this line was approved or run: the workbench at
`5633e2d` holds no Experiment B report or records. (Workbench:
`nn/decisions_replication.md` at commit `5633e2d`.)

### Doors — What did the agents actually learn?

**Question:** in a multi-door world, do agents learn a door
concept or a location? **Verdict: a location.** Across 1500
multi-door episodes, 1471 reached the goal, and **all 1471
crossed first at the familiar door (5,5)**. (Workbench:
`nn/decisions_doors.md` at commit `2ad12f7`.)

### P-Db — Do agents divert to an open rival door?

**Question:** when a rival door is open and the familiar door is
not, do agents divert? **Verdict: NO true diversion.** Of 479
conflict episodes: 458 waits at the familiar door, 21 takes of an
open rival, 0 genuine diversions — **all 21 takes arrived at
rival staging cells and were route artifacts**: the agent's route
had already brought it there. (Workbench:
`nn/decisions_doors_sched.md` at commit `8aef7ee`.)

### Luck — What happens when the familiar door is removed?

**Question:** with the familiar door removed and no retraining,
do agents find another door? **Verdict: NO — reached 0/1500.**
H_luck STANDS descriptively. The owner's reading at the time: a
design failure, fixable — a hypothesis then, not a result.
(Workbench: `nn/decisions_luck.md` at commit `a92e8fe`.)

### P-Da — Does retraining in a uniform world generalize?

**Question:** retrained from scratch in a uniform world, do agents
cross a novel door? **Verdict: NO — memorization, not
generalization.** Novel door E3: 0/750 reached (18 entries, 0
reached, no far-side behaviour). An interpolation bound failed
with the rest. (Workbench: `nn/decisions_pda.md` at commit
`085ea27`.)

### P-Db2 — Does schedule-varied training generalize?

**Question:** trained across varied schedules, do agents cross a
held-out novel door? **Verdict: NO, except one per-agent
exception.** Held-out novel door F3: 20/750 reached, **all by
memory/3** — the single per-agent exception. Superiority is
world-relative: the plain arm scored 0/100 in the F0 sanity world
against 70/100 in multi-door worlds, and the memory arm 0/100
against 90/100; overall F0 was 343/750. Preferred-door lock-in
held: 30/30 agents had a modal door. (Workbench:
`nn/decisions_pdb2.md` at commit `35fa992`.)

### FT1 — Does fine-tuning on the novel door transfer?

**Question:** after 200 episodes of fine-tuning on (5,8) alone,
do agents acquire the novel door, and does it transfer to a
second novel door? **Verdict: partial acquisition, zero
transfer, near-total forgetting.** Kept-set F3 (like-for-like
baseline recomputed from P-Db2 records): 20/540 → 237/540
(11/22 agents crossing at least once). Second novel door G1:
0/540 — zero transfer. Meanwhile multi-door worlds collapsed
(F1 540/540 → 76/540, F2 540/540 → 38/540, F4 540/540 →
304/540; F0 253/540 → 38/540). The memory/3 paradox: P-Db2's
only F3-crosser, after fine-tuning 161/200 on (5,8), scored
F3 0/20 — its own fine-tuning world removed its perfection.
(Workbench: `nn/decisions_ft1.md` at commit `9d1d6a0`.)

### PRB1 — Does noise unlock a frozen greedy failure?

**Question:** the memory/3 greedy trap (F3 0/20 after FT1):
does ε=0.05 evaluation unlock it? **Verdict: NEITHER — noise
partly unlocks, world-specifically.** Noisy: 45/100 (entered
47), against greedy 0/20 and fine-tune 161/200. The control
(plain/0 F3 20/20 per rep under noise, 100/100) stayed
interpretable, so the probe is not uninterpretable on control
grounds. (Workbench:
`nn/decisions_prb1.md` at commit `15fc230`.)

### MD1 — Can agents follow a door that moves between episodes?

**Question:** trained with the door row varying between episodes
(fixed within an episode), do agents follow the door to
held-out rows? **Verdict: UNINTERPRETABLE — no conclusion
about following is drawn.** Pooled trained greedy: 388/4800 =
8.08%, below the frozen 20% floor, so precedence stops before
any following verdict; pooled held-out: 4/1200 = 0.33%. This is
not a memorization verdict either: the BIGGER rule was not
reached. Greedy evaluation fell far below training reached for
every arm. (Workbench: `nn/decisions_md1.md` at commit
`f601339`.)

### PRB2 — Does noise rescue the MD1 agents?

**Question:** under ε=0.05 evaluation, do the 6 seed-0 MD1 agents
lift to the pre-stated bar? **Verdict: NEITHER.** Pooled noisy
trained: 780/4800 = 16.25% (2.56× the greedy 6.35%) but below
the 20% absolute floor — the ratio condition passes, the
absolute condition binds. Pooled noisy held-out: 17/1200 =
1.42%; row 8 stayed 0/600 under noise. The lift is uneven, not
uniform: three agents lift from zero greedy, plain and oracle_new
lift strongly, memory lifts only 1.14× — the PRB1 shape repeats
in part, not as a general law. MD1's UNINTERPRETABLE verdict
stands: PRB2 asked a new question under its own bars.
(Workbench: `nn/decisions_prb2.md` at commit `5633e2d`.)

### Trust arc — methodology note (brief)

The learning machinery's history, not template code. Naive
trust slowed learning roughly threefold and learned worse; the
anneal was implicated (PC6); the no-anneal design β≡1.0 was
adopted by owner ruling; and parity against uniform was
established at confirmatory grade: median paired difference
−34.5 episodes, 95% CI [−64, −8], inside the +50-episode
non-inferiority margin. (Workbench:
`nn/decisions_trust15_parity.md` at commit `ba7730e`; the
Layer-1 ~3.2× figure in `nn/decisions_trust15.md` at commit
`5633e2d`.) The
trust design is recorded here so a future builder knows it
exists and where its proof lives; it is not shipped in
`TEMPLATE/` because it is not part of the substrate at the
source commit.

## 5. Claims + proof table

Labels: **ESTABLISHED** = supported by a frozen workbench record
(pointer given). **DESIGN INTENT** = a design property with its
reason, not an empirical result. **NOT ESTABLISHED** = stated as
such; no pointer can support it, and none is claimed.

| # | Claim | Label | Workbench commit + file | Numbers (denominators + protocol bounds) | What it does NOT prove |
|---|---|---|---|---|---|
| C1 | Schedule information helps on the 20/10 grid task | ESTABLISHED | `5633e2d`, `nn/decisions_replication.md` | Wrapped 26/40 vs plain 0/40 vs memory 7/40; seeds 10–49; clean-and-fast protocol | That the wrapper beats every alternative, or that it generalizes |
| C2 | The wrapper did not clear the pilot bar | ESTABLISHED | `5633e2d`, `nn/decisions_b2.md` | Wrapped 5/10 vs pre-registered bar 7/10; clock control 0/10 | That the wrapper is useless (see C1) |
| C3 | Agents learn "go to (5,5)", not a door concept | ESTABLISHED | `2ad12f7`, `nn/decisions_doors.md` | 1471/1471 reached multi-door episodes crossed first at familiar (5,5); 1500 episodes total | That agents cannot learn concepts under any architecture |
| C4 | No true diversion under schedule-varied eval | ESTABLISHED | `8aef7ee`, `nn/decisions_doors_sched.md` | 479 conflicts → 458 waits, 21 takes, 0 genuine diversions; all 21 takes at rival staging cells (route artifacts) | That diversion is impossible in principle |
| C5 | Removing the familiar door without retraining collapses reaching | ESTABLISHED | `a92e8fe`, `nn/decisions_luck.md` | Reached 0/1500; H_luck STANDS descriptively | That retraining cannot recover (see P-Da, P-Db2, FT1) |
| C6 | Retraining in a uniform world memorizes locations, does not generalize | ESTABLISHED | `085ea27`, `nn/decisions_pda.md` | Novel door E3: 0/750 reached (18 entered, 0 reached); 3750/3750 episodes, 150/150 jobs, 50 trainings | That memorization is inevitable for all architectures or tasks |
| C7 | Schedule-varied training: one per-agent exception, world-relative superiority | ESTABLISHED | `35fa992`, `nn/decisions_pdb2.md` | F3 20/750, all memory/3; F0 343/750; plain F0 0/100 vs 70/100 multi-door; memory F0 0/100 vs 90/100 multi-door; modal door 30/30 agents | That the memory arm is generally superior |
| C8 | Fine-tuning buys partial acquisition at near-total forgetting, zero transfer | ESTABLISHED | `9d1d6a0`, `nn/decisions_ft1.md` | Kept-set F3 20/540 → 237/540 (200-episode (5,8) dose); G1 0/540; F1 540/540 → 76/540; F0 253/540 → 38/540 | That fine-tuning always destroys prior skills |
| C9 | Noise partly unlocks a frozen greedy failure, world-specifically | ESTABLISHED | `15fc230`, `nn/decisions_prb1.md` | Memory/3 F3: greedy 0/20 → noisy 45/100 (entered 47); fine-tune 161/200; verdict NEITHER | That noise generally rescues greedy failures (cf. PRB2 memory/0, 1.14×) |
| C10 | Moving-door training under greedy eval is uninterpretable | ESTABLISHED | `f601339`, `nn/decisions_md1.md` | Pooled trained greedy 388/4800 = 8.08% < 20% floor; held-out 4/1200 = 0.33%; precedence stops at UNINTERPRETABLE | Following (not reached) or memorization (BIGGER not reached) |
| C11 | Noise lifts MD1 seed-0 agents substantially but not to the lift bar | ESTABLISHED | `5633e2d`, `nn/decisions_prb2.md` | Noisy trained 780/4800 = 16.25% (2.56× greedy 6.35%) < 20% floor → NEITHER; held-out 17/1200 = 1.42%; R8 0/600; control 95/100 ≥ 75% | That noise rescues all agents, or opens row 8 |
| C12 | No-anneal trust (β≡1.0) is at parity with uniform on the 20/10 trust protocol | ESTABLISHED | `ba7730e`, `nn/decisions_trust15_parity.md` | Median paired difference −34.5 episodes; 95% CI [−64, −8] < +50 margin; seeds 520–549, 60 records | Superiority (design tested non-inferiority, not superiority); speed; generality beyond 20/10 |
| C13 | The template is liftable to other models | DESIGN INTENT | — (reason, not record) | Reason: small, explicit, hand-written, first-principles; every part visible and re-derivable | Reuse demonstrated (NOT ESTABLISHED: no second domain built yet) |
| C14 | The template generalizes across domains | NOT ESTABLISHED | — | No second-domain build exists | Anything — this row exists so the gap is explicit |

No claim in this paper lacks a row above. Numbers are quoted
from frozen records only, never from memory or from another
programme's pooled totals. Where the draft instruction's
distilled line and a frozen record disagreed (P-Db2's
world-relative point), this paper follows the frozen record:
plain/memory F0 collapse figures, not a "kept agents score 0 in
F0" summary.

## 6. Limitations (mandatory, plain language)

- **Memorization, not generalization, on the grid task.** Agents
  learn locations (go to (5,5)), not door concepts. A novel door
  is not crossed without training on it, and an interpolation
  bound failed.
- **No novel-door transfer.** Fine-tuning on one novel door gave
  zero transfer to a second novel door (G1 0/540).
- **Forgetting is the price of acquisition.** The fine-tuning dose
  that partly acquired (5,8) collapsed multi-door worlds
  (F1 540/540 → 76/540) and deepened the F0 collapse.
- **Greedy evaluation understates these networks.** Noise lifts
  results substantially (PRB2 2.56×) without reaching the
  pre-stated bar — so any single-number summary from greedy eval
  alone misleads.
- **No language.** Nothing in this template reads or produces
  language. A language phase would be growth from this lineage,
  not something demonstrated here.
- **No second domain built yet.** Universality is design intent,
  not a proven result. The worked adaptation sketch in
  `IMPLEMENTATION.md` is a pattern, not a run.
- **Narrow protocols.** All numbers above are bounded by their
  protocols: one grid task, stated schedules (20/10 training;
  30/14 in the trust track), stated arms and seeds. Nothing here
  licenses claims beyond them.
- **The wrapped encoder is schedule-tied.** Its feature scales
  (20.0/10.0) are fixed to the 20/10 schedule; adapting to another
  schedule without re-deriving them would silently distort the
  time inputs.

## 7. Why it can be universal (the argument)

This section argues the DESIGN's fitness for reuse. It does not
claim reuse has been demonstrated — that claim would need a
second-domain build, which does not exist yet.

A template must be liftable: a builder in a new domain must be
able to take the whole design over, understand every part, and
re-derive it there — not merely copy weights, which would carry
over nothing but the old task's answers. Three properties of this
design make that possible, and they are the same property seen
three ways:

- **Simplicity.** One world, one network shape, one learner, three
  encoders. The whole design fits in eight files. There is little
  enough here to hold in one head, which is what lets a builder
  re-derive it instead of cargo-culting it.
- **Explicitness.** Every feature is named (position, door bit,
  previous door bit, phase, remaining, known flag). Nothing is
  buried in a learned embedding or an opaque representation. When
  a feature misbehaves in a new domain, the builder can see which
  one and why.
- **Inspectability.** The schedule model exposes its estimates
  and its ignorance (honest `None` until supported; contradictions
  drop stale events rather than defending them). The training loop
  exposes its seeds, its RNG streams, and its hyperparameters. A
  builder can reproduce a training exactly, and can audit a
  failure exactly.

Contrast with a massive black-box model: there, nothing is visible
to lift. The weights encode the old task in a form no builder can
read, adapt, or audit, so every new domain starts from scratch
anyway — the very re-creation this template exists to avoid. Here,
there is nothing hidden, so there is something to lift.

That is the argument, and its limit is stated alongside it: an
argument for fitness is not evidence of transfer. The test of
universality is a real second-domain build, evaluated with
trained worlds held apart from held-out worlds and bars stated
before running — the discipline in `IMPLEMENTATION.md`. Until
that build exists, "universal" stays exactly what §1 says it is:
design intent plus its reason.
