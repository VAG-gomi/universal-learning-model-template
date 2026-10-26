# STATUS.md — universal learning-model template (read this first)

**Purpose.** A new session helping on this project should be able to
read this file from GitHub and know where things stand, without the
full conversation history. Keep it current: when the announced state
changes, a gate ruling lands, or the active track changes, update this
file (never rewrite history to do it).

**Last updated:** 2026-10-25.

## 1. What this repo is

- `VAG-gomi/universal-learning-model-template` — the UNIVERSAL
  PAPERS-STUDIES member of the repository family: the universal
  learning-model template + the study paper with proof + the
  implementation instructions. Public.
- **Announced** at `fbd7cb2` (owner Step 6 approval 2026-10-24).
  "Announced" means the repo-internal approved state; no external
  post was made or specified. The announcement does not freeze this
  repo by itself — but nothing here changes by momentum (see §4).
- This repo is NOT the workbench. Do not duplicate the workbench's
  job here (experiments, tests, records, evidence chain).

## 2. Contents

- `TEMPLATE/` — the template itself: `world.py`, `nn/` (hand-written
  MLP, plain/memory/wrapped agents, ScheduleModel wrapper), `demo.py`,
  `principles.md`.
- `PAPER/study-paper.md` — the study paper (7 sections, 12 journey
  stages + trust arc, claims table C1–C14 including DESIGN INTENT and
  NOT ESTABLISHED rows).
- `IMPLEMENTATION.md` — 7 implementation steps, adaptation sketch
  (labeled PATTERN, not a run), pitfalls with pointers.
- `README.md` — entry point and status.

## 3. Identity anchor

- At announcement, all 8 template files were verified byte-identical
  to workbench commit `5633e2d`, and the demo was reproduced exactly
  from a fresh clone (train 1716/2000, schedule model 20/10,
  known-fraction 0.999, greedy eval 20/20 phases, 0 crushes,
  mean ticks 23.5).
- The template's identity is that workbench-anchored code. Any
  divergence between this repo's template and the workbench anchor
  must be stated explicitly, never silent.

## 4. Rules for changing this repo

- EXP1 originally tested this template's design WITHOUT modifying this
  repo — that boundary was OVERRIDDEN 2026-10-25 by explicit owner
  direction: the workbench is frozen/closed, this repo is now the
  current project, and EXP1 Step 0 was moved (cut) from the workbench
  into this repo (commit `199bd4b`). The original WO boundary
  (sibling untouched) no longer holds for EXP1 Step 0; later EXP1
  phases still need their own rulings.
- No template, paper, or implementation change happens on a
  proposal's say-so. Changes need explicit owner authorization.
- Confirm-then-modify: EXP1 Stage 1 must CONFIRM before any
  modification is discussed. A confirm means "parameterized template
  scales" (within-domain scaling) — NOT cross-domain universality.
- "Universal" stays design intent with its reason (simple, symbolic,
  transparent, inspectable, liftable), never a proven result — no
  second domain has been built on it yet.

## 5. Family architecture (one repo, one job)

- (1) PERSONAL CODES = `time-based-mind-model` (workbench: frozen at
  tag `freeze-2026-10-24` on `5633e2d`, now CLOSED — no new work
  there; its own `STATUS.md`, frozen at `9b00849`, holds the programme
  arc but is stale on EXP1's location — this file is the live
  record).
- (2) UNIVERSAL PAPERS-STUDIES = this repo.
- (3) ETC. MATERIALS = future siblings as needs arise. Each new kind
  gets its own repo; repos cross-link instead of duplicating.

## 6. Live work pointer (not in this repo)

- **EXP1 Step 0** (wide-scale expanded-world test, Stage 1): work
  order ISSUED Step 0 ONLY (owner ruling 2026-10-24; W10 held-out
  (5,2), bar pool W10+W20+W30, 165 arm-runs, trigger FIRES).
- **Status: VERIFIED — PASS, Step 0 FULFILLED (independent verifier
  ruling 2026-10-25, recorded in this repo at `f28806e`).**
  Step 0 was ported to this repo at `199bd4b` (DRAFT, built in the
  workbench, then cut from there — workbench tree restored, no
  workbench commit; the workbench is closed). The verifier checked
  the committed sibling copy against the issued work order (WO
  §5 step 3): all 8 items PASS — parameterization (57 insertions /
  28 deletions, three agent files only), W10 fidelity 6/6 (verifier
  re-ran all 12 trainings; plain/1 greedy 6/20 quirk reproduces
  exactly), the nine worlds incl. the pinned M2 next-door-bit rule,
  the runner (sweep dormant), the frozen prereg, the 165 count
  (trigger FIRES), sanity-only scope (mechanics 89/89), and labels.
  Design-note §9 is now FILLED (commit `f28806e`); the full ruling
  text is held by the owner (local file
  `VERIFICATION-EXP1-step0-ruling.md`, not committed to this repo).
  Notes N1–N4 in the ruling are non-defects; the design note's
  header still describes the workbench build origin — any header
  clarification belongs in a later commit, never by editing
  `199bd4b`.
- **Next, in order:** the remaining-work instruction is ISSUED
  (`INSTRUCTION-EXP1-remaining-work.md`, commit `a309360`), and
  the owner gave the **spike-first gate ruling 2026-10-26 — Part 1
  (benchmark spike, MEASUREMENT ONLY) is AUTHORIZED**.
  **Executor correction (owner direction 2026-10-26): Part 1 was
  executed by THIS session (same implementer behaviour as the
  previous programme work), not the main session — the
  instruction's To: field is superseded for execution; its
  substance governed.**
- **Part 1 SPIKE COMPLETE (DRAFT report, commit `20023ef`).**
  15 trainings + 19 evals, all SPIKE-labeled, 0 duplicates, no
  sweep records, no weights saved, 2 runtime kills recovered
  via designed resume logic (disclosed in the report). The
  report projects the full sweep (60 trainings + 105 evals)
  at **12.98 h point estimate (observed range 12.97–12.99 h,
  sensitivity range 11.97–13.98 h) vs the 4-hour threshold** —
  the sweep as designed does not fit in 4 hours of sequential
  compute on this VM. Time goes to the learning update
  (87.7% W10/plain, 94.7% M3/wrapped, measured). The report
  is DRAFT, self checked only: it claims NO proceed
  authorization and performs NO bar analysis.
- **Still gated:** independent instructor verification of the
  spike report → owner proceed ruling → sweep runs (Part 2).
  Part 2 is NOT authorized until both land.
- Scope guard: the spike produces no sweep results (spike records
  only, never pooled, never counted toward completeness). No
  sweep, no Layer F fictional-scenario worlds, no schedule or
  template change, no substrate change, no tag/freeze/announcement
  action — each needs its own ruling.

## 7. Standing rules for any session working here

- Guardrails stand until narrowly lifted; a lift expires at its
  scope edge. A paste, draft, or verified report alone never
  authorizes new work — the next step needs an explicit owner word
  naming it.
- Gates run in sequence; no step authorizes the next. Work orders
  are outcome specs, not scripts: report every deviation with its
  reason, lead with anything skipped or not doable, never hide
  failures.
- NEVER write "instructor-verified" before an independent ruling
  exists. The verifier never rules on its own build.
- A push is claimed only after confirming it from the remote
  (`git ls-remote`); a stalled or failed push is reported plainly
  as local-only.
- No causal language from experiments: interpretations stay at the
  strongest explanation among the tested alternatives, bounded to
  task and protocol.

## 8. How to resume

1. Read this file, then `README.md`, `PAPER/study-paper.md`, and
   `IMPLEMENTATION.md`.
2. For programme detail, read the workbench's `STATUS.md` and the
   current design note (`TEMPLATE/nn/decisions_exp1_design.md` in
   this repo — §9 filled, PASS ruling 2026-10-25, Step 0 fulfilled).
3. Ask the owner for the next ruling; do not start the next step
   by momentum.
