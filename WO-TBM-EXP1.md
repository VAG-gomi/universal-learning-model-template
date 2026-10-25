# WO-TBM-EXP1 — Wide-scale expanded-world test, Step 0 ONLY (ISSUED)

**Status: ISSUED — Step 0 ONLY (owner ruling 2026-10-24: tap "Add W10 held-out — 165, trigger fires").**
**Issuance amendments:** (1) W10 held-out added, door (5,2); bar pool becomes W10+W20+W30; counts corrected to 165, trigger FIRES; (2) §2.1 pins agent_nn.py asserts too; (3) §2.2 requires M2's next-door-bit rule pinned in the design note. No spike, no sweep runs, no Layer F — those need separate rulings.
**Programme:** EXP1, Stage 1 of the staged test (confirm-then-modify).
**Tested design:** `VAG-gomi/universal-learning-model-template`
(announced, `fbd7cb2`), via the workbench's byte-identical template
files (workbench `5633e2d`). The sibling repo is NOT modified.
**First machine test inside Step 0:** the W10 fidelity check (§2.1) —
the parameterized code runs and is compared against original
single-door behavior. Sweep runs are NOT part of Step 0 (§7).

## 1. Purpose

Stage 1 tests whether the template (with ONLY the ruled size
parameterization) generalizes across expanded worlds, before any
modification is discussed. Step 0 builds everything the sweep
needs — parameterized code, new worlds, runner, frozen prereg —
and verifies it. No sweep training or evaluation runs in Step 0
beyond the sanity checks in §2.5.

## 2. Outcome spec for Step 0 (deliverables)

### 2.1 Parameterized template code + W10 fidelity check

- Parameterize GRID_SIZE: it becomes a world-size parameter;
  the position one-hot size derives from it; the shape asserts
  in `agent_nn.py` (101-input), `agent_mem.py`, and `agent_wrapped.py`
  generalize accordingly.
- NOTHING else changes: no learner change (MLP, Q-learning,
  replay, hyperparameters), no encoder change (slot layout,
  door-bit contract, scales 20.0/10.0), no RNG change, no
  schedule change (20/10 everywhere in this programme).
- W10 fidelity check: retrain with the parameterized code on
  the ORIGINAL 10×10 single-door world and compare against
  original single-door behavior. Step 0 MUST pin the exact
  baseline record set used (commit + file + seeds). If no
  matching single-door record set exists for the chosen seeds,
  Step 0 reports that explicitly and proposes the closest
  baseline, labeled accordingly — it does NOT invent one.
- If the fidelity check does not match, STOP and report: the
  parameterization is not faithful, and no sweep result is
  trusted until that is resolved. Do not proceed past this
  point on assumption.

### 2.2 New world files (additive only)

- `world_exp1.py` (name may differ if the executor chooses a
  cleaner one — report the choice): W20 (20×20, wall x=10,
  door (10,10)), W30 (30×30, wall x=15, door (15,15)),
  M1 (20×20 maze: interior obstacles + door), M2 (20×20 two
  sequential doors; the next-door bit is reported through
  the existing one-door-bit contract), M3 (50×50
  single-door). All on schedule 20/10.
- The design note MUST pin M2's exact next-door-bit rule:
  which door's bit is shown, and the exact switch condition.
- `world.py` is NEVER edited. Template files (`nn/*.py`
  except the parameterization in §2.1) are NEVER edited.
  The sibling repo is NEVER touched.

### 2.3 Runner + evaluation

- Runner for greedy evaluation (same as the original: ε=0,
  weights frozen, one deterministic episode per start phase).
- Inside worlds (W10/W20/W30): trained-world eval + ONE
  held-out variant each: W10 held-out door (5,2); W20
  held-out door (10,5); W30 held-out door (15,7).
- Outside worlds (M1/M2/M3): trained-world eval only.
- Arms/seeds for the sweep (recorded here for the prereg;
  NOT run in Step 0): inside all three arms (plain, memory,
  wrapped), seeds 0–4; outside wrapped only, seeds 0–4.

### 2.4 Frozen preregistration (design note section)

The design note MUST freeze, before any run:
- Primary bar, "SCALES": wrapped held-out pooled (W10+W20+W30)
  ≥20% absolute AND ≥50% of wrapped trained pooled rate
  (trained pooled over W10+W20+W30).
- Secondary contrast (reported, NOT gating): wrapped
  held-out pooled (W10+W20+W30) > plain held-out pooled
  (same set).
- Completeness: all trainings + eval jobs complete,
  0 duplicates, else INCOMPLETE.
- Confirm rule: Stage 1 CONFIRMS iff the primary bar is met,
  labeled "parameterized template scales" (within-domain
  scaling — NOT cross-domain universality). If not met,
  Stage 1 does NOT confirm, and no universality-based
  modification unlocks.
- Outside worlds: DISCOVERY ONLY — no bar, no verdict.
  Output is a performance map + a gap list.

### 2.5 Sanity checks (the ONLY runs in Step 0)

- (a) W10 fidelity retrain (§2.1) — comparison numbers kept,
  weights discarded (sanity, not a record).
- (b) Mechanics checks for all five new worlds (reset, step,
  wall/door behavior, observe contract) — scripted,
  deterministic, no training.
- (c) Runner smoke: one greedy eval job on W10, plumbing only.
- No other trainings or eval jobs in Step 0. Sanity results
  are reported in the design note; they are NOT pooled with
  any sweep result.

### 2.6 Design note

`nn/decisions_exp1_design.md`: purpose, world definitions,
parameterization (exact files/lines changed), W10 baseline
records pinned, prereg (§2.4), counts (§3), gates (§4),
sanity results, and a verification section LEFT EMPTY for
the instructor. The note is DRAFT until the instructor
verifies it (§5).

## 3. Scope

**In scope (Step 0 only):** §2.1–§2.6. **Out of scope
(explicit):** all sweep trainings and evals; all Layer F
fictional-scenario worlds (F1–F6 runnable candidates are
scoped SEPARATELY after the core sweep design is verified
— they are not built in Step 0); any schedule change;
any sibling-repo change; any new arm; any hyperparameter
or RNG change; any template change beyond §2.1; any tag,
freeze, or announcement action.

## 4. Counts + trigger (Step 0 confirms the exact count)

From the §2 design (as amended at issuance): trainings 60
(inside 45 + outside 15) + eval jobs 105 (inside trained 45
+ inside held-out 45 + outside trained 15) = 165 arm-runs.
This EXCEEDS the 150 trigger → a spike-first gate applies
(ruling E §5(1)) at the Step 0 gate. The spike itself is NOT
authorized by this issuance; it needs its own gate ruling
after Step 0 verification. Step 0 MUST recompute the exact count
from its own runner/world definitions and state it; if
the exact count differs, the design note says so plainly.
Larger grids run slower per step (bigger one-hot dot
products) — Step 0 does NOT promise wall-clock; the spike
measures it. No scope reduction after seeing the count
without an owner ruling.

## 5. Gates + sequence (nothing beyond Step 0 is authorized here)

1. Owner issues this WO (Step 0 ONLY, with or without
   amendments — amendments are part of issuance).
   **ISSUED 2026-10-24 — see header.**
2. Executor builds §2 and delivers DRAFT, UNCOMMITTED,
   UNPUSHED (see §6).
3. Instructor verifies Step 0 independently (code, W10
   fidelity numbers, world mechanics, prereg, counts) and
   rules PASS/FAIL; on PASS the instructor commits +
   pushes and confirms from the remote.
4. Owner gate ruling (spike-first, since the trigger fires
   at 165) — a SEPARATE ruling, not granted by
   Step 0 issuance.
5. Spike (MEASUREMENT ONLY) → owner proceed ruling →
   Steps 1+ (sweep runs). Each of these needs its own
   ruling; none is authorized by this document.

## 6. Label + reporting norms (binding)

- The design note stays DRAFT until the instructor's
  verification ruling exists. NEVER write
  "instructor-verified" (in the note, in a commit message,
  or anywhere) before that ruling exists — this pre-claim
  has recurred in past programmes and must not recur here.
- The executor receives outcome specs, not scripts: it may
  choose a better design or cleaner verification, but MUST
  report every deviation with its reason, MUST lead with
  anything skipped or not doable, and MUST never hide
  failures.
- A flagged defect is not a work order: findings return as
  proposals with exact scope, not edits.
- Deliverables are files, never retyped prose: the design
  note, the world file, the runner, and the prereg are
  delivered as files for ferrying.

**End of Step 0 work order (ISSUED — Step 0 ONLY).**
