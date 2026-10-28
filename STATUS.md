# STATUS.md — universal learning-model template (read this first)

**Purpose.** A new session helping on this project should be able to
read this file from GitHub and know where things stand, without the
full conversation history. Keep it current: when the announced state
changes, a gate ruling lands, or the active track changes, update this
file (never rewrite history to do it).

**Last updated:** 2026-10-28.

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
- **Gate 0 CONFIRMED in the instructor conversation (owner,
  own words, 2026-10-26):** 0a issued instruction for Part 1
  only + ruled spike first 2026-10-26 (Part 2 not authorized);
  0b Part 1 executor = spike-executor session, not main
  session; 0c spike record = `20023ef` + `28a1fca` for
  instructor verification; 0d sweep executor =
  spike-executor session; 0e governing file = rev1
  full-sequence instruction, IF ISSUED. Gate 0 alone does
  NOT issue rev1; issuance still comes with Gate 1.
- **Step 1 SPIKE VERIFICATION — PASS (independent verifier
  ruling 2026-10-26, from a fresh clone at `28a1fca`).**
  The spike report is verified as a measurement deliverable
  for Part 1 only. The verifier re-derived, from the
  committed records at `20023ef` (parent `11d61dd`): 15
  trainings + 19 evals = 34 records, 0 duplicates, 0 resume
  lines, trained-eval coverage exact, 4 held-out evals as
  designed, all SPIKE-labeled; all 15 training rows match
  report §2 (wall sum 9655.3 s) and all 19 eval walls match
  §2 (sum 1.56 s); projection training point 46711.8 s,
  observed [46667.8, 46755.7] s, sensitivity [43099.2,
  50324.4] s via 7.73%, eval total 9.59 s, sweep total
  46721.4 s = **12.98 h vs the 14400 s (4 h) threshold,
  excess 32321.4 s** — the sweep as designed does NOT fit
  in 4 hours sequential on this VM; profile matches §4
  exactly (learning update 87.7% W10/plain, 94.7%
  M3/wrapped); runner uses the sweep's own `train_loop` /
  `evaluate_job`, no weights saved, no `.npz`, no sweep
  records. The full ruling text is held by the owner
  (local file `VERIFICATION-EXP1-spike-ruling.md`, not
  committed to this repo). Limitations carried: restart
  history is disclosed, not independently proven (no
  attempt logs; timestamps consistent with kill/relaunch,
  including a ~49-minute gap before M3); projection is
  seed-0-conditional (only W10 has 2 seeds; the ±7.73%
  sensitivity range does not cover a learning-vs-
  nonlearning jump); report §7 saying the spike files are
  "UNCOMMITTED" is now stale (they were committed at
  `20023ef` for verification, numbers unaffected). The
  ruling performs NO bar analysis and pools nothing with
  any sweep result (none exists).
- **Gate 1 + issuance — BOTH GIVEN 2026-10-27 (owner, worker
  chat, own words):** Gate 1 proceed ruling — proceed with
  the EXP1 sweep on the current hand-written numpy
  substrate, no substrate change, despite the verified
  12.98-hour projection vs the 4-hour threshold, noting
  the projection is seed-0-conditional; AND issuance —
  "I issue rev1, and rev1 governs going forward."
  Rev1 issued at `2ac3d1f`
  (`INSTRUCTION-EXP1-full-sequence-rev1.md`, body verbatim
  from the 2026-10-26 draft except an issuance note +
  status/footer updates clarifying that Gate 0, Step 1,
  and Step 2 are complete). **Step 3 sweep is now
  AUTHORIZED** (executor: spike-executor session, Gate
  0d). Step 4 (instructor verification of the sweep +
  Stage 1) remains pending after Step 3 delivery.
- **Step 3 SWEEP COMPLETE, delivered 2026-10-28 (coordinator,
  spike-executor session), parent-verified from the records
  before commit — commit `8ac0a22` (6 files, DRAFT report
  only, self checked only).** Parent re-derived, independently
  of the coordinator's self-check: 165 job lines (60 trainings
  + 105 evals), 2100 eval episodes, 0 duplicates, training
  and eval sets exactly as preregistered (inside 45 + outside
  15 trainings; inside trained 45 + inside held-out 45 +
  outside trained 15 evals), hyperparameters unchanged
  (2000 episodes, hidden=32, lr=1e-3, 20/10), training
  summaries match job reached totals (0 mismatches), eval
  episode blocks match job reached totals (0 mismatches),
  appendix per-seed evals match records (0 mismatches),
  no `.npz`, no tracked file modified, spike files untouched.
  Recorded job walls sum to 15.06 h (trainings 54211.7 s +
  evals 10.6 s), above the spike point 12.98 h and sensitivity
  high end 13.98 h — NOT a protocol, completeness, or bar
  failure, because the spike projection was seed-0-conditional;
  recorded walls exclude incomplete killed trainings, so
  elapsed time including restarts is higher, and no elapsed
  total is claimed. Deviations, all disclosed in the DRAFT
  report §0: delivery uncommitted by the coordinator (parent
  verified/committed/pushed instead, spike pattern); new
  runner `exp1_sweep.py` using the sweep's own `train_loop` /
  `evaluate_job` instead of `run_sweep()` directly, because
  `run_sweep()` is not resume-safe; first launch detached
  nohup, then tracked launches after the first VM restart.
  Restarts disclosed (7 VM SIGTERM restarts, all mid-training,
  all incomplete units re-ran from scratch, 0 resume_retrain
  notes) — disclosed, not independently proven by the parent,
  as with the spike.
- **Step 3 result, in preregistered terms only (parent
  re-derived, DRAFT report §4/§8, NOT the final Stage 1
  statement):** inside greedy eval pooled (300 episodes per
  arm): plain trained 126/300 (42.00%), held-out 0/300;
  memory trained 169/300 (56.33%), held-out 0/300; wrapped
  trained 219/300 (73.00%), held-out **1/300 (0.33%)** — the
  single held-out reached episode is wrapped/W10 seed 3,
  1/20. Per-world wrapped: trained W10 100/100, W20 99/100,
  W30 20/100; held-out W10 1/100, W20 0/100, W30 0/100.
  Frozen SCALES bar: absolute ≥20% **NOT MET** (0.33% < 20%);
  relative ≥50% of wrapped trained pooled (36.50%) **NOT MET**
  (0.33% < 36.50%); **primary bar SCALES: NOT MET (both
  parts fail). Stage 1 comparison, in preregistered terms:
  DOES NOT CONFIRM.** Secondary contrast (reported, NOT
  gating): wrapped held-out 1/300 > plain held-out 0/300,
  arithmetically true, changes nothing. Outside worlds,
  DISCOVERY ONLY, no bar, no verdict: wrapped trained M1
  100/100, M2 54/100, M3 0/100. Completeness: COMPLETE
  (all jobs complete, 0 duplicates). No universality-based
  modification unlocks on this comparison; the final Stage 1
  statement awaits Step 4 instructor verification.
- **Step 4 SWEEP VERIFICATION — PASS (verification),
  instructor ruling 2026-10-28, from a fresh clone at
  `03614a0`.** The ruling file
  `VERIFICATION-EXP1-sweep-ruling.md` is held locally by the
  owner and is NOT committed to this repo. This recording
  covers the verification ruling only; it authorizes nothing
  further.
- **Stage 1, in preregistered terms: DOES NOT CONFIRM.**
  Wrapped trained pooled 219/300 (73.00%); wrapped held-out
  pooled 1/300 (0.33%, single held-out success wrapped/W10
  seed 3, 1/20). Frozen SCALES bar: absolute ≥20% NOT MET
  (0.33% < 20%); relative ≥50% of wrapped trained pooled
  (36.50%) NOT MET (0.33% < 36.50%). Primary bar NOT MET on
  both parts. Label "parameterized template scales" does NOT
  apply. No cross-domain universality is claimed.
- Secondary contrast (reported, NOT gating): wrapped
  held-out 1/300 > plain held-out 0/300, arithmetically true,
  changes nothing.
- Outside worlds, DISCOVERY ONLY, no bar, no verdict:
  wrapped trained M1 100/100, M2 54/100, M3 0/100.
- Completeness: COMPLETE (60 trainings + 105 evals = 165
  jobs, 2100 eval episodes, 0 duplicates). Recorded job
  walls 15.06 h (trainings 54211.7 s + evals 10.6 s) — above
  the spike projection, NOT a protocol, completeness, or bar
  failure.
- Limitations carried: restart cause (7 disclosed VM
  restarts) is disclosed and internally consistent, NOT
  independently proven; Gate 1 + issuance were given in the
  worker chat, and verification takes authorization as
  recorded (`2ac3d1f` → `5dcac7c` before the sweep).
- **What remains gated:** nothing further is authorized by
  this recording — no modification, re-run, next experiment,
  Layer F, substrate change, tag/freeze/announcement action.
  Any next step needs its own owner ruling. This recording
  does not change the DOES NOT CONFIRM verdict.
- Scope guard: the spike produces no sweep results (spike records
  only, never pooled, never counted toward completeness).
  Sweep runs are now authorized under issued rev1 only; no
  Layer F fictional-scenario worlds, no schedule or
  template change, no substrate change, no tag/freeze/
  announcement action — each needs its own ruling.

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
