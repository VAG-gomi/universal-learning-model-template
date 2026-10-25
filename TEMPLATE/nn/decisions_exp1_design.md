# EXP1 design note — Wide-scale expanded-world test, Step 0 (DRAFT)

**Status: DRAFT — not yet verified. The verification section (§9)
is left empty for the independent verifier. Nothing in this note
is a verification claim.**
**Programme:** EXP1, Stage 1 of the staged test (confirm-then-modify).
**Work order:** `WO-TBM-EXP1.md`, Step 0 ONLY, ISSUED 2026-10-24
(owner ruling: tap "Add W10 held-out — 165, trigger fires").
**Workbench:** `~/workspace/time-mind-model`, HEAD `5633e2d`,
frozen at tag `freeze-2026-10-24`. Step 0 work is UNCOMMITTED
working-tree changes on top of that commit (new files +
template parameterization edits). Nothing is committed, pushed,
or tagged by the builder.
**Sibling:** `VAG-gomi/universal-learning-model-template`
(announced, `fbd7cb2`) is NOT modified. The tested design is
the workbench's byte-identical template files.

## 1. Purpose

Stage 1 tests whether the template (with ONLY the ruled size
parameterization) generalizes across expanded worlds, before any
modification is discussed. Step 0 builds everything the sweep
needs — parameterized code, new worlds, runner, frozen prereg —
and verifies it. No sweep training or evaluation runs in Step 0
beyond the sanity checks in §7.

## 2. World definitions

All worlds use schedule 20/10 (period=20, open_len=10), start
(0,0), goal (N-1, N-1) for grid N, and world.World's exact
mechanics (same step structure, same log strings, same crush /
block / goal rules). Implementation: `world_exp1.py`
(`Exp1World` + factories); `world.py` is untouched.

| Name | Grid | Walls | Door(s) | Role |
|------|------|-------|---------|------|
| W10  | 10 | x=5 | (5,5) | Inside trained (geometry identical to World) |
| W10h | 10 | x=5 | (5,2) | Inside held-out |
| W20  | 20 | x=10 | (10,10) | Inside trained |
| W20h | 20 | x=10 | (10,5) | Inside held-out |
| W30  | 30 | x=15 | (15,15) | Inside trained |
| W30h | 30 | x=15 | (15,7) | Inside held-out |
| M1   | 20 | x=10 | (10,10) + obstacles | Outside (discovery) |
| M2   | 20 | x=10, x=15 | (10,10), (15,10) | Outside (discovery) |
| M3   | 50 | x=25 | (25,25) | Outside (discovery) |

Held-out pattern: the held-out door row is floor(wall_x / 2)
(W10: 5->2, W20: 10->5, W30: 15->7), matching the MD1
held-out row 2 on the 10x10 grid.

M1 obstacle layout (fixed, 24 cells): vertical x=4, y=2..8;
horizontal y=13, x=2..6; vertical x=14, y=12..18;
horizontal y=6, x=13..17. No obstacle touches the start,
the goal, the door cell, or either door approach cell
(9,10)/(11,10); the row-10 corridor stays open. BFS
verifies a path start -> door -> goal exists (see §7).
Obstacles are unobserved (the agent sees only position +
door bit, exactly as with the wall column); an obstacle is
learned about only by bumping into it.

M2 next-door-bit rule (PINNED): observe() reports the
open state of the NEXT door — the first door whose wall
column the agent has not yet passed (agent.x <= wall_x);
once the agent has passed every wall column, the last
door's state is shown. Region table: x<=10 -> door1
(10,10); 10<x<=15 -> door2 (15,10); x>15 -> door2.
HONEST LIMIT, stated plainly: under the shared 20/10
schedule every door's state coincides at every tick, so
the next-door bit's VALUE equals the shared door bit;
the rule is structural here (which door the bit refers
to, with the switch condition pinned). A future
phase-varied design would exercise the switch; M2 as
built tests two sequential crossings (two staging
decisions, two crush risks), not bit disambiguation.
Crush applies at EITHER door cell while closed.

W10 equivalence: `make_w10()` geometry equals
`world.World` geometry; the mechanics script proves a
scripted walk produces identical logs on both (§7).

## 3. Parameterization (WO §2.1)

Exact changes (all defaults reproduce the original code;
`git diff` on the three files is 57 insertions, 28
deletions, and nothing else):

- `nn/agent_nn.py`:
  - `encode_obs(world, grid_size=GRID_SIZE)` (line 54):
    one-hot index y*grid_size+x, door slot
    grid_size^2, size grid_size^2+1.
  - `PlainEncoder` (class line 69): `__init__(self,
    grid_size=GRID_SIZE)` (line 77), instance
    `n_inputs = grid_size^2+1`; `encode` (line 84)
    calls `encode_obs(world, self.grid_size)`.
  - `obs_index(world, grid_size=GRID_SIZE)` (line 88).
  - `TabularQ.__init__` (line 141): `grid_size`
    parameter, table shape (grid_size^2, 2, 5).
  - `NeuralQ` needed no change (it already takes
    `n_inputs`); `train_neural`, `evaluate_policy`,
    `make_greedy_policy` unchanged.
- `nn/agent_mem.py`:
  - `MemoryEncoder` (class line 47): `__init__(self,
    grid_size=GRID_SIZE)` (line 54), instance
    `n_inputs = grid_size^2+2`; `encode` (line 63)
    uses one-hot y*grid_size+x, current door slot
    grid_size^2, previous door slot grid_size^2+1.
  - `train_memory` unchanged (default encoder).
- `nn/agent_wrapped.py`:
  - `WrappedEncoder` (class line 73): `__init__(self,
    model=None, blank_features=False, grid_size=10)`
    (line 83), instance `n_inputs = grid_size^2+4`;
    `encode` (line 98) uses one-hot y*grid_size+x,
    door grid_size^2, phase +1, remaining +2,
    known +3.
  - `ClockEncoder` (class line 149): `__init__(self,
    grid_size=10)` (line 163), instance `n_inputs =
    grid_size^2+2`; `encode` (line 170) uses one-hot
    y*grid_size+x, door grid_size^2, tick/200
    grid_size^2+1.
  - `train_wrapped`, `train_clock` unchanged
    (default encoders).
  - PHASE_SCALE (20.0) and REMAINING_SCALE (10.0)
    UNCHANGED (schedule scales, not grid scales).
  - ClockEncoder is not a sweep arm; it is
    parameterized in the same pattern because it
    lives in the same file and hardcodes the same 10.
- Class attributes (`n_inputs = 101/102/104`) are
  kept for the existing structural checks; instances
  carry the size-derived value. All existing checks
  that use defaults therefore assert the same values
  as before (verified: `agent_mem.py` structural
  check, `agent_wrapped.py` run_checks,
  `test_wrapper.py`, `test_nnet.py` all PASS).
- NOT changed: learner (MLP, Q-learning, replay,
  hyperparameters), encoder slot layouts beyond the
  one-hot size, door-bit contract, RNG streams,
  schedule (20/10), `nn/wrapper.py` (ScheduleModel
  is grid-independent), `nn/nnet.py` (no grid
  references), `world.py` (never edited), the
  sibling repo.

Runner (`nn/exp1_run.py`, additive): `train_loop()`
mirrors `train_neural()` line-for-line except for two
stated changes: (1) the world per episode comes from
the caller's factory; (2) the goal is read from the
world object (`world.goal_pos`, falling back to
`GOAL_POS` for `world.World`). `evaluate_job()` is
one greedy job (20 phases, eps=0, weights frozen)
with a FRESH encoder per (agent, eval world) job,
persisting across the job's 20 episodes (the
post-FT1 standard); for wrapped the ScheduleModel
starts blank per eval world and blank-feature
warm-up is audited per episode (`blank_feature`,
`first_known_step`). Training encoders persist
across episodes within a training (as in
`train_neural` / `train_wrapped`).
Record schema: per-episode summaries + step
trajectories for eval jobs (failure-anatomy
material; 105 jobs x 20 episodes x <=200 steps is
under a third of MD1's eval volume, which
compacted to 93.9 MB, with gzip as fallback);
training records are summaries only.
`run_sweep()` is DORMANT in Step 0 (written, not
run) and executes only after sweep authorization.

## 4. Preregistration (frozen, WO §2.4)

- Primary bar, "SCALES": wrapped held-out pooled
  (W10+W20+W30) >=20% absolute AND >=50% of wrapped
  trained pooled rate (trained pooled over
  W10+W20+W30).
- Secondary contrast (reported, NOT gating): wrapped
  held-out pooled (W10+W20+W30) > plain held-out
  pooled (same set).
- Completeness: all trainings + eval jobs complete,
  0 duplicates, else INCOMPLETE.
- Confirm rule: Stage 1 CONFIRMS iff the primary bar
  is met, labeled "parameterized template scales"
  (within-domain scaling — NOT cross-domain
  universality). If not met, Stage 1 does NOT
  confirm, and no universality-based modification
  unlocks.
- Outside worlds (M1/M2/M3): DISCOVERY ONLY — no bar,
  no verdict. Output is a performance map + a gap
  list.
- Sweep arms/seeds (recorded, NOT run in Step 0):
  inside all three arms (plain, memory, wrapped),
  seeds 0-4; outside wrapped only, seeds 0-4.

## 5. Counts (recomputed from the runner's own definitions)

`python3 nn/exp1_run.py --plan` (from
`nn/exp1_run.py::sweep_plan()`): trainings 60,
eval jobs 105, arm-runs 165. Breakdown: inside
trainings 3 arms x 3 worlds x 5 seeds = 45;
outside trainings wrapped x 3 worlds x 5 seeds =
15; inside trained eval 45; inside held-out eval
45; outside trained eval 15. Total 165 arm-runs >
150 trigger -> spike-first gate applies at the
Step 0 gate (ruling E §5(1)). The spike itself is
NOT authorized by Step 0 issuance. No scope
reduction after seeing the count without an owner
ruling. (The WO's §4 estimate is confirmed exactly;
no difference to report.)

## 6. Gates + sequence (WO §5)

1. Owner issues Step 0 ONLY. ISSUED 2026-10-24.
2. Builder builds §2, delivers DRAFT, UNCOMMITTED,
   UNPUSHED. (This note.)
3. Independent verifier verifies Step 0 (code, W10
   fidelity numbers, world mechanics, prereg,
   counts) and rules PASS/FAIL; on PASS the
   verifier commits + pushes and confirms from the
   remote.
4. Owner gate ruling (spike-first, since the
   trigger fires at 165) — SEPARATE, not granted
   by Step 0 issuance.
5. Spike (MEASUREMENT ONLY) -> owner proceed ruling
   -> sweep runs. Each needs its own ruling.

## 7. Sanity results (WO §2.5 — the ONLY runs in Step 0)

(a) W10 fidelity retrain (`nn/exp1_fidelity.py`):
config A = original trainers on original code
(run BEFORE the §2.1 edits; git HEAD 5633e2d,
template file hashes recorded per run); config D
= runner `train_loop()` + parameterized encoder,
grid_size=10 (run AFTER the edits). Protocol both
sides: original single-door world, period 20,
open_len 10, 2000 episodes, all hyperparameters
unchanged. Arms plain/memory/wrapped, seeds 0-1
(12 trainings total). Comparison: per-episode
stats (ticks/reached/crushes/mean_loss), final
network weights, and 20-phase greedy outcomes
(fresh encoder per job, same convention both
sides) — all compared EXACTLY.

| Arm/seed | A train reached | D train reached | A greedy | D greedy | Verdict |
|----------|----------------|-----------------|----------|----------|---------|
| plain/0  | 1706/2000 | 1706/2000 | 20/20 | 20/20 | MATCH |
| plain/1  | 1647/2000 | 1647/2000 | 6/20 | 6/20 | MATCH |
| memory/0 | 1722/2000 | 1722/2000 | 20/20 | 20/20 | MATCH |
| memory/1 | 1754/2000 | 1754/2000 | 20/20 | 20/20 | MATCH |
| wrapped/0 | 1716/2000 | 1716/2000 | 20/20 | 20/20 | MATCH |
| wrapped/1 | 1698/2000 | 1698/2000 | 20/20 | 20/20 | MATCH |

FIDELITY: PASS (6/6 exact matches, including
weights bitwise). Note the plain/1 greedy 6/20
quirk reproduces exactly on both sides — real
seed variation, not a parameterization artifact.
(Wrapped/0's 1716/2000 also reproduces the
sibling demo's training number, an independent
consistency check.) Fidelity weights are held
under /tmp/exp1_fidelity/ as comparison inputs
only; they are never committed, never records,
and never enter the repo.

(b) Mechanics checks (`nn/exp1_mechanics.py`,
scripted, deterministic, no training): 89/89 PASS,
covering reset/clip/wall/door/crush/goal/observe/
schedule per world, M1 obstacles + BFS, M2 region
rule + second-door crush, W10-vs-World log
equivalence (42/42 identical events), and a full
log audit (0 blocked/closed-door landings).
Two script bugs were found and fixed during this
check (see §8); the worlds themselves needed no
change.

(c) Runner smoke (`nn/exp1_run.py --smoke`, one
greedy eval job on W10 through `evaluate_job`,
plumbing only, using the D plain/0 trained
weights from /tmp): 20/20 reached, per-phase
ticks 30,29,28,27,26,25,24,23,22,21,20,19,18,18,
18,18,18,18,18,18, crushes 1 (phase 0) else 0 —
identical to the direct-loop greedy for the same
agent. Runner-vs-direct agreement additionally
verified for memory/0 and wrapped/0 (both 20/20,
exact per-phase agreement), so the runner's eval
path is validated on stateful encoders too.

Sanity results are NOT pooled with any sweep result.

## 8. Design decisions pinned (no WO deviations)

- Fidelity baseline construction: no pre-existing
  record set matches the fidelity seeds (0-1).
  Operative baseline = fresh runs of the ORIGINAL
  code at 5633e2d (config A), seeds 0-1, protocol
  2000 episodes 20/10 single-door. Closest
  pre-existing set, labeled: replication
  (`nn/results_replication.jsonl`, code frozen at
  7affcfb, seeds 10-49, same protocol 2000 eps
  20/10 greedy 20 phases); template files are
  byte-identical between 7affcfb and 5633e2d
  (`git diff` empty for world.py + all nn template
  files), so the only baseline difference is seeds.
- Fidelity comparison design: D (runner loop +
  parameterized encoder, size 10) vs A (original
  trainers + original encoders). Exact equality of
  per-episode stats, final weights, and greedy
  outcomes is required. If D != A, B/C
  decompositions (original loop + parameterized
  encoder; runner loop + original encoder) localize
  the cause, and the fidelity gate blocks sweep
  trust until resolved. (Not needed: D == A.)
- Eval encoder rule: fresh encoder per (agent, eval
  world) job (post-FT1 standard), NOT the training
  encoder carried over. Reason: eval worlds are
  self-contained experimental units; blank-prefix
  effects are audited, not hidden. The
  deployment-like same-encoder variant is a
  different design, not used here.
- Record schema: eval trajectories recorded (see
  §3 for the volume reasoning); training summaries
  only. `run_sweep()` dormant until authorization.
- M2 shared schedule + structural next-door rule:
  see §2 honest limit.
- M1 layout: see §2 (solvability BFS-verified).
- ClockEncoder parameterized in-pattern (see §3).
- Builder-caught bug, fixed before any fidelity
  run used it (reported, not hidden): the runner's
  first `make_encoder` and the fidelity script's
  D-path encoder dict called `WrappedEncoder`
  positionally, but its first positional parameter
  is `model`, not `grid_size` — the call would
  have set the model to an int. The structural
  check caught it (assertion failure on
  `WrappedEncoder(30).n_inputs`); both call sites
  were fixed to keyword args and re-verified
  (`make_encoder('wrapped', 20)` -> 404 inputs
  with a real model object). The template code was
  never wrong; the bug was in new calling code.
- Mechanics script bugs, fixed during §7(b)
  (reported, not hidden): the first script version
  walked x-first (straight into wall columns
  along row 0) and crossed doors on phase 9
  (leaving on phase 10 = crush by the world's own
  rule). Fixed to y-first walking (down the start
  column, then along the door row) and phase-8
  crossings (enter phase 8, exit phase 9, still
  open). No world code changed for either fix.

## 9. Verification (independent verifier ruling, 2026-10-25)

**Ruling: PASS — Step 0 is fulfilled.**

- Verifier: independent verifier session (the builder session did not rule on its own build).
- Verified against: sibling repo `VAG-gomi/universal-learning-model-template`, main at `a096dd1` (fresh clone, remote = local HEAD). Step 0 artifact: commit `199bd4b` (8 files). Governing documents: `WO-TBM-EXP1.md` (`8685f99`, ISSUED Step 0 ONLY) and `INSTRUCTION-EXP1-main-session.md` (`a096dd1`), both byte-identical to the issued versions.
- Full ruling: verifier's file `VERIFICATION-EXP1-step0-ruling.md` (delivered to the owner for ferrying). This section is its summary, not a substitute for it.

**Per-item verdicts (WO §5 step 3):**

1. **Parameterization — PASS.** Agent diffs `8a98522..199bd4b` exactly 57 insertions, 28 deletions, three agent files only; all other TEMPLATE files unchanged. Size parameter only; defaults 101/102/104 at N=10; no learner, RNG, schedule, or scale change. Note: the WO's "asserts" wording is imprecise for `agent_nn.py` (no asserts there); hardcoded asserts live only in N=10 test/self-check functions, never in the sweep path.
2. **W10 fidelity gate — PASS.** Verifier re-ran all 12 trainings independently (original code from `8a98522`, parameterized code from `199bd4b`). Driver result: 6/6 MATCH, "FIDELITY: PASS", exit 0. Independently re-derived: per-episode stats exactly equal, greedy outcomes exactly equal, final weights bitwise equal for all 6 pairs. Numbers: plain/0 1706/2000, 20/20; plain/1 1647/2000, 6/20 (quirk reproduces exactly); memory/0 1722/2000, 20/20; memory/1 1754/2000, 20/20; wrapped/0 1716/2000, 20/20; wrapped/1 1698/2000, 20/20. Baseline pinning: operative baseline is fresh original-code runs; recorded file hashes prove the A side was original code (A hashes match announced-template files; A-vs-D differ only in the three agent files). The replication set (7affcfb, seeds 10–49) is labeled closest pre-existing set only, not operative, not pooled.
3. **New worlds — PASS.** W10/W10h/W20/W20h/W30/W30h/M1/M2/M3 as defined, all 20/10; M1 = 24 obstacles; M2 next-door-bit rule pinned (first unpassed door, else last door) with the disclosed limit that under the shared schedule the bit's value equals the shared door bit; `TEMPLATE/world.py` unmodified.
4. **Runner — PASS.** `train_loop` mirrors `train_neural` except the two stated changes (caller factory world; goal from `world.goal_pos`); greedy eval ε=0, weights frozen, 20 phases; held-out variants W10 (5,2), W20 (10,5), W30 (15,7); `run_sweep` dormant (CLI exposes only `--plan` and `--smoke`).
5. **Preregistration — PASS.** §4 matches issued WO §2.4 exactly (primary bar SCALES; secondary contrast reported, not gating; completeness; confirm rule labeled "parameterized template scales"; outside worlds discovery only).
6. **Counts — PASS.** Recomputed from `sweep_plan`: 60 trainings + 105 eval jobs = 165 arm-runs. 165 > 150, so the arm-run trigger FIRES; the spike-first gate applies.
7. **Sanity only — PASS.** Mechanics re-run by the verifier: 89/89 PASS (W10-vs-World logs 42/42, log audit 0 violations). Both unit suites PASS; structural checks PASS. Smoke check (verifier's own D_plain_0 weights): 20/20, ticks 30,29,28,27,26,25,24,23,22,21,20,19,18,18,18,18,18,18,18, crushes 1 (phase 0) else 0 — exactly as claimed. No sweep trainings/evals ran; no sweep records in the repo.
8. **Labels — PASS.** Design note DRAFT; §9 was empty until this ruling; no "instructor-verified" claim in any Step 0 file; §7 "FIDELITY: PASS" is the builder's sanity claim, not a verification claim.

**Verification runs:** the 12 fidelity trainings were verifier runs, held outside the repo (`~/workspace/verify-exp1-work/out/`), never pooled with any sweep result. A runtime restart killed the first fidelity run after 9 of 12 trainings (files intact, numbers matching); the verifier relaunched only the 3 missing trainings plus the comparison. The final comparison covers all 12 pairs.

**Notes (not defects, no edits made):** (N1) This note's header describes the workbench build origin ("UNCOMMITTED… sibling NOT modified") — superseded in the sibling context by the owner-directed port (`199bd4b`); any header clarification belongs in a later commit, never by editing `199bd4b`. (N2) WO §5's "executor delivers uncommitted, verifier commits on PASS" model was superseded by the owner's direction to commit Step 0 to the sibling before verification; the content ruling is unaffected. (N3) The verification brief's file paths omitted the `TEMPLATE/nn/` prefix; actual paths are under `TEMPLATE/nn/`. (N4) The workbench-side replication set was not re-derived from the workbench, per the brief's boundary; nothing in Step 0 depends on it.

**What remains gated (not authorized by this ruling):** owner gate ruling (expected spike-first) → spike (MEASUREMENT ONLY) → owner proceed ruling → sweep runs (Steps 1+). Each needs its own ruling. No Layer F world, schedule change, further template change, or tag/freeze/announcement action is authorized here.
