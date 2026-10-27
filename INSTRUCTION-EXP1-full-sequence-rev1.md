# ISSUANCE NOTE — rev1 ISSUED 2026-10-27 (read first, governs over stale state sections below)

**Status: ISSUED 2026-10-27 — Step 3 sweep AUTHORIZED.**

- Owner Gate 1 + issuance given 2026-10-27 in worker chat, in the owner's own words: proceed with the EXP1 sweep on the current hand-written numpy substrate, no substrate change, despite the verified 12.98-hour projection vs the 4-hour threshold, noting the projection is seed-0-conditional; and "I issue rev1, and rev1 governs going forward."
- Supersession for state purposes only: the body below was drafted 2026-10-26 at main 28a1fca, before Gate 0 confirmation and Step 1 verification. Its "Where things stand" and "Decisions for the owner to confirm" sections are superseded by: Gate 0 confirmed in the instructor conversation 2026-10-26 (0a-0e, 0d spike-executor session, 0e rev1 if issued), Step 1 spike verification PASS recorded at a986bb3, and Gate 1 + issuance given 2026-10-27 (recorded in STATUS.md in the commit following this file). Do not treat Gate 0, Step 1, or Step 2 as pending.
- What governs unchanged: Step 3 sweep substance (60 trainings + 105 evals, frozen SCALES bar, completeness gate, DRAFT report), Step 4 verification, out-of-scope list, reporting norm, and label discipline in the body below. If the body conflicts with WO-TBM-EXP1.md §5 or design note §4, the work order and preregistration govern, per the body.
- Executor: spike-executor session (Gate 0d). Substrate: hand-written numpy, no change.

---
# INSTRUCTION — EXP1 full sequence, REVISED (rev1), for the implementer

**Status (original draft): DRAFT at creation 2026-10-26 — SUPERSEDED for status by the issuance note above; this file as committed is the ISSUED rev1.**

- From: instructor session (independent verifier for EXP1 Step 0 and for the spike/sweep reports).
- To: the implementer session named by the owner in Gate 0 (see Decisions below; until then, no executor is assumed).
- Via: owner ferry (the owner carries files between sessions; never retype).
- Created: 2026-10-26, on the owner's tap "Prepare it, I'll confirm the gates" (owner keeps the authority; the instructor does the preparation).
- This file REVISES the 2026-10-26 full-sequence draft (`INSTRUCTION-EXP1-full-sequence-main-session.md`). That draft is now stale and must NOT be issued as-is: its Next 1 (confirm state) and Next 2 (commit the spike files) are already done, and its main-session executor assumption is outdated for Part 1. This rev1 does not by itself supersede anything — it supersedes the earlier draft ONLY if the owner issues it and states that it governs.

## Where things stand (verified from the remote, 2026-10-26)

- Step 0 is fulfilled and recorded: sibling repo `VAG-gomi/universal-learning-model-template`, Step 0 at `199bd4b`, verification PASS recorded at `f28806e` (§9) and `f940ed7` (STATUS.md). `199bd4b` untouched.
- Sibling main is at `28a1fca` (ls-remote = fresh-clone HEAD, verified by the instructor). Spike files are committed at `20023ef` (5 files: runner, 34-line records, profile, discarded cProfile, report), STATUS at `28a1fca`, 27 files total, design-note §9 still filled.
- Spike report (Part 1, measurement only) is DRAFT, self checked only, NOT instructor-verified, and claims NO proceed authorization. Its claimed projection is 12.98 h vs the 4-hour threshold (face-checked from pasted numbers only; full verification still pending).
- Authorization record is a ferry gap, not yet settled in the instructor chain: the spike-first ruling, the Part 1 executor correction, and the governing file still need the owner's explicit words HERE (Gate 0 below). Do not rewrite history — `a309360` / `11d61dd` / `20023ef` / `28a1fca` stay as committed; any correction goes as new commits on top, as the owner directs.
- All sessions are the same underlying agent (Muse); the record still tracks which chat context did what, because the verifying chat must not be the building chat.

## Decisions for the owner to confirm (NOT confirmed yet — confirming Gate 0 does NOT authorize the sweep)

- **Gate 0a — Spike-first ruling:** does the owner confirm, in their own words here, that they issued the instruction for Part 1 only and ruled spike first? If yes, state the words and date. If no, state what was actually ruled.
- **Gate 0b — Part 1 executor:** does the owner confirm Part 1 was executed by the spike-executor session (per STATUS `28a1fca`), not the main session?
- **Gate 0c — Spike record:** does the owner confirm `20023ef` / `28a1fca` are the spike record the instructor is to verify?
- **Gate 0d — Sweep executor:** who executes the sweep (Part 2)? The owner names one session (spike-executor session, main session, or another) — the instruction's addressee follows this choice.
- **Gate 0e — Governing file:** which instruction governs going forward — this rev1 (if issued), or the issued Part 1 instruction already in the repo (`INSTRUCTION-EXP1-remaining-work.md` at `a309360`)? The owner states one file; two governing drafts must not run side by side.
- **Gate 1 (later, after spike verification) — Proceed ruling:** does the owner rule proceed on the current hand-written numpy substrate, hold, or change scope (including any decision on the over-4-hour projection)? The sweep starts ONLY after Gate 1 AND issuance of this rev1 (or the governing file named in Gate 0e).

## How to use this instruction

Work through the steps in order. Do not skip ahead past a WAIT step. Each step states its Trigger, what to Do, what to Deliver, and when to Stop.

- **Trigger not met → STOP and report that you are waiting.** Do not run ahead.
- **Conflict → STOP and ask the owner.** If this instruction ever conflicts with `WO-TBM-EXP1.md` §5 or the frozen preregistration (design note §4), the work order and the preregistration govern. Do not guess.
- **Reporting norm (binding at every step):** outcome specs, not scripts — the executor may choose a better design or cleaner verification, but must report every deviation with its reason, lead with anything skipped, not doable, or failed, and never hide a failure.
- **Label discipline (binding at every step):** never write "instructor-verified" before the instructor's ruling exists. Self-checked results are "self checked only." Spike records are labeled SPIKE, never pooled with sweep records, never counted toward sweep completeness.

## Step 1 — Instructor verification of the spike (executor does nothing)

- **Trigger:** Gate 0a–0c confirmed by the owner here.
- **Do (instructor):** verify the spike report from the remote (fresh clone at `28a1fca`, already obtained): re-derive counts (15 trainings + 19 evals = 34 records), uniqueness and 0 duplicates, resume-retrain lines, per-job walls and ticks, projection arithmetic from the raw records (point, observed range, sensitivity range) vs the 4-hour threshold, profile numbers, restart disclosures (2 SIGTERM kills, attempt durations), label compliance (SPIKE labeling, 0 weights saved, no bar analysis, no proceed claim). Carry the seed-0-conditional qualification into the ruling (only W10 has 2 seeds; large-grid time is driven by trainings that never learn; ±7.73% sensitivity does not cover the learning-vs-nonlearning jump).
- **Do (executor):** nothing. Wait for the ruling, delivered via the owner.
- **Deliver (instructor):** PASS/FAIL ruling on the spike report, with per-item evidence.
- **Stop if:** the ruling is FAIL. Everything stops until the owner directs a fix or revert. Verification alone never authorizes the sweep.

## Step 2 — Owner proceed ruling + issuance (executor does nothing until both land)

- **Trigger:** Step 1 ruling exists (PASS).
- **Do (owner):** give Gate 1 (proceed / hold / scope change) and issue this rev1 (or the governing file named in Gate 0e), stating the sweep executor from Gate 0d.
- **Do (executor):** nothing until BOTH the proceed ruling AND the issued instruction are recorded via the owner.
- **Stop if:** no proceed ruling, or the ruling is HOLD. The sweep stays unauthorized. A verified spike report alone never authorizes the sweep.

## Step 3 — Sweep, Steps 1+ (ONLY after Step 2)

- **Trigger:** Gate 1 proceed ruling recorded AND the governing instruction issued (both via the owner).
- **Do:** run the sweep through `TEMPLATE/nn/exp1_run.py` (or an equivalent you justify, with deviations reported): **60 trainings** (inside 45: W10/W20/W30 × plain/memory/wrapped × seeds 0–4; outside 15: M1/M2/M3 × wrapped × seeds 0–4) + **105 eval jobs** (inside trained 45 + inside held-out 45 + outside trained 15). Greedy eval only (ε=0, weights frozen, one deterministic episode per start phase 0–19). Held-out variants: W10 (5,2), W20 (10,5), W30 (15,7). Sequential execution (no parallel design is authorized or assumed here).
- **Completeness is a gate:** all trainings and eval jobs complete, 0 duplicates, else the sweep is INCOMPLETE. The runner's duplicate guard must hold. Any runtime restart resumes deterministically (skip completed, no duplicates) and is disclosed in the report.
- **Analysis against the frozen preregistration (design note §4, unchanged):** primary bar SCALES — wrapped held-out pooled (W10+W20+W30) ≥20% absolute AND ≥50% of wrapped trained pooled rate (trained pooled over W10+W20+W30); secondary contrast (wrapped held-out pooled > plain held-out pooled, same set) reported, NOT gating; outside worlds M1/M2/M3 DISCOVERY ONLY (no bar, no verdict; output = performance map + gap list).
- **Deliver:** sweep records + sweep report (DRAFT, self checked only), committed and pushed, then reported back via the owner for instructor verification. The report gives per-world and per-arm results with denominators and protocols, the bar comparison, the completeness statement, and the Stage 1 comparison in exactly the preregistered terms — but does NOT label Stage 1 as confirmed or the sweep as verified before the instructor's ruling. Never claim cross-domain universality from this sweep.
- **Stop if:** any job fails, any duplicate appears, or the completeness gate fails. Report it first, before any totals, and wait for owner direction.

## Step 4 — Instructor verification of the sweep + Stage 1 (final step in this sequence)

- **Trigger:** Step 3 delivered (sweep records + report pushed and confirmed from the remote).
- **Do (executor):** nothing. Wait for the instructor's verification ruling, delivered via the owner.
- **Do (instructor):** verify the sweep report from the remote and rule PASS/FAIL, with the Stage 1 statement in preregistered terms.
- **After a PASS ruling:** Stage 1 stands as ruled (CONFIRMS, labeled "parameterized template scales" — within-domain scaling only — iff the primary bar is met, otherwise DOES NOT CONFIRM). A confirm unlocks DISCUSSION of modifications, not edits — each modification still needs its own approval. No further work starts on this instruction.

## Out of scope (explicit — none of this is authorized by this instruction, at any step)

- Re-running the spike; re-committing the spike files; issuing the stale full-sequence draft as-is; rewriting pushed history.
- All Layer F worlds (F1–F6 runnable candidates are scoped separately; F7–F8 are conceptual only).
- Any schedule change (20/10 everywhere); any template change beyond the Step 0 parameterization; any new arm; any hyperparameter, encoder, or RNG change.
- Any substrate change (no JIT, no vectorization, no framework swap; substrate stays hand-written numpy).
- Any workbench work; any tag, freeze, or announcement action; any self-issuance or self-ruling.

## Governing documents (in order, if anything conflicts)

1. The owner's rulings (given in the owner's own words, via ferry, and confirmed at Gate 0 / Gate 1).
2. `WO-TBM-EXP1.md` §5 (gates) and design note §4 (frozen preregistration) + §9 (Step 0 PASS).
3. This instruction (DRAFT until the owner issues it; on issuance, the owner states the governing file from Gate 0e and the sweep executor from Gate 0d).

---

**Footer (status):** ISSUED 2026-10-27 by owner Gate 1 proceed ruling + issuance (worker chat). Gate 0, Step 1, and Step 2 are complete. Step 3 sweep is AUTHORIZED. Step 4 verification remains pending after Step 3 delivery.
