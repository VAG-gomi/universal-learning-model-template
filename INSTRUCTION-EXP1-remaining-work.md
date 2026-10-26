# INSTRUCTION — EXP1 remaining work, for the main session (implementer)

**Status: ISSUED — Part 1 (spike) AUTHORIZED by owner spike-first gate ruling 2026-10-26. Part 2 (sweep) NOT AUTHORIZED — it needs the owner's proceed ruling after the spike report is instructor-verified.**

- From: instructor session (independent verifier for EXP1 Step 0).
- To: main session (implementer/constructor).
- Via: owner ferry (the owner carries files between sessions; never retype).
- Created (as DRAFT): 2026-10-25, on the owner's tap "Draft it gated, gates stay."
- Issued: 2026-10-26, on the owner's order "issue the instruction and rule spike first" (Part 1 only). This issued version supersedes the draft of the same instruction (`DRAFT-INSTRUCTION-EXP1-remaining-work.md`, 2026-10-25) for Part 1; the draft's Part 2 remains unissued.
- Reference point: sibling repo `VAG-gomi/universal-learning-model-template`, main at `f940ed7` (Step 0 PASS recorded: filled §9 as `f28806e`, STATUS.md as `f940ed7`; Step 0 artifact `199bd4b` untouched).

## Read this first: what "gated draft" means

Ferrying this DRAFT to the main session does **not** start any work. Work starts only when the owner issues this instruction **and** gives the gate ruling for that stage:

- The spike starts only after the owner's **spike-first gate ruling** is given (via ferry) and recorded. **— GIVEN 2026-10-26 (Part 1). The spike is authorized.**
- The sweep starts only after the owner's **proceed ruling** is given (via ferry) and recorded, after the spike report has been instructor-verified. **— NOT GIVEN. The sweep is not authorized.**

If either ruling has not been given, STOP and report that you are waiting. Do not run ahead, do not treat this draft as permission, and do not treat the Step 0 PASS as permission for the spike or the sweep. The PASS authorized nothing further.

If this instruction ever conflicts with the issued work order (`WO-TBM-EXP1.md` §5) or the frozen preregistration (design note §4), STOP and ask the owner. Do not resolve a conflict by guessing. The work order and the preregistration govern.

## Background (one paragraph)

EXP1 Step 0 is fulfilled and recorded: the template is parameterized by grid size only (Step 0 commit `199bd4b`), the W10 fidelity gate passed 6/6, the worlds (W10/W20/W30 + held-out variants + M1/M2/M3) and the runner exist, and the preregistration is frozen in design note §4. The remaining work, in order, is: (A) a benchmark spike (measurement only), then (B) the sweep (Steps 1+). All remaining work lives in the **sibling** repo, under `TEMPLATE/` — never in the workbench (`time-based-mind-model`, frozen and closed for this track).

## Part 0 — Before anything (every stage)

1. Clone the sibling fresh. Confirm from the remote that local HEAD equals origin/main before starting (a push is claimed only after confirming it from the remote; a stalled push is reported plainly as local-only).
2. Read the governing inputs: `WO-TBM-EXP1.md` (§5 gates), `TEMPLATE/nn/decisions_exp1_design.md` (§2 worlds, §3 parameterization, §4 preregistration, §9 verification PASS), and the Step 0 files (`TEMPLATE/world_exp1.py`, `TEMPLATE/nn/exp1_run.py`, `exp1_mechanics.py`, `exp1_fidelity.py`, `TEMPLATE/nn/agent_nn.py`, `agent_mem.py`, `agent_wrapped.py`).
3. Never edit `199bd4b` or any frozen commit. New work goes in new commits on top. Never write "instructor-verified" anywhere before the instructor's ruling exists — self-checked results are "self checked only."
4. Work-order norm (binding): you receive outcome specs, not scripts. You may choose a better design or cleaner verification, but you must report every deviation with its reason, lead with anything skipped or not doable, and never hide a failure.

## Part 1 — Spike (MEASUREMENT ONLY, after the spike-first gate ruling)

**Outcome:** a timed measurement that projects the full sweep's cost, so the owner can rule on proceeding with numbers in hand. It produces no sweep results.

- Time representative trainings across arms (plain, memory, wrapped) and across world sizes — including the larger grids, not only W10, because cost grows with grid size (input size and path length). Time a representative set of greedy eval jobs the same way. State your spike design (which arms, worlds, seeds, and how many jobs) in the spike report before presenting its numbers.
- Project the full sweep (60 trainings + 105 eval jobs) from the measurements, with a range, and compare it against the 4-hour compute threshold. The arm-run trigger has already fired (165 > 150); the spike does not re-decide that — it measures time.
- Record where the time goes at a coarse level (learning update vs. environment/encoding), measured, not assumed. Do not claim any speedup for any substrate change: no JIT/vectorized candidate exists, and none is to be built or tested here.
- Spike trainings are **SPIKE records only**: label every spike file, output, and commit as SPIKE; discard spike weights (or keep them clearly marked as spike-only, never as sweep records); never pool spike results with sweep results; never count a spike training toward sweep completeness.
- If a runtime restart kills a spike run, relaunch deterministically, skipping completed jobs, with no duplicates, and disclose the restart in the report.
- Deliverable for this stage: a spike report (design, timed jobs, projection with range, threshold comparison, profile note, restarts/disclosures) committed and pushed, then reported back via the owner for independent instructor verification. The spike report must not claim proceed authorization. **After delivering the spike report, STOP and wait for the proceed ruling.**

## Part 2 — Sweep, Steps 1+ (ONLY after the proceed ruling)

**Outcome:** the full sweep, run exactly as preregistered, with a report that compares results against the frozen bar.

- Run the sweep through `TEMPLATE/nn/exp1_run.py` (or an equivalent you justify, with deviations reported): **60 trainings** (inside 45: W10/W20/W30 × plain/memory/wrapped × seeds 0–4; outside 15: M1/M2/M3 × wrapped × seeds 0–4) + **105 eval jobs** (inside trained 45 + inside held-out 45 + outside trained 15). Greedy eval only (ε=0, weights frozen, one deterministic episode per start phase 0–19). Held-out variants: W10 (5,2), W20 (10,5), W30 (15,7).
- Completeness is a gate, not a summary: all trainings and eval jobs complete, 0 duplicates, else the sweep is INCOMPLETE. The runner's duplicate guard must hold; any restart must resume deterministically with no duplicates, disclosed in the report.
- Analysis against the **frozen** preregistration (design note §4, unchanged): primary bar SCALES — wrapped held-out pooled (W10+W20+W30) ≥20% absolute AND ≥50% of wrapped trained pooled rate (trained pooled over W10+W20+W30); secondary contrast (wrapped held-out pooled > plain held-out pooled, same set) reported, NOT gating; outside worlds M1/M2/M3 DISCOVERY ONLY (no bar, no verdict; output = performance map + gap list).
- Report: per-world and per-arm results with denominators and protocols, bar comparison, completeness statement, and a Stage 1 statement in exactly the preregistered terms: CONFIRMS (labeled "parameterized template scales" — within-domain scaling only) iff the primary bar is met, otherwise DOES NOT CONFIRM (and no universality-based modification unlocks). Never claim cross-domain universality from this sweep. Never present a draft report's own verification labels as verification.
- Deliverable for this stage: sweep records + report, committed and pushed, then reported back via the owner for independent instructor verification. **Do not label the sweep verified before the instructor's ruling.**

## Out of scope (explicit — none of this is authorized by this instruction)

- All Layer F worlds (F1–F6 runnable candidates are scoped separately; F7–F8 are conceptual only).
- Any schedule change (20/10 everywhere); any template change beyond the Step 0 parameterization; any new arm; any hyperparameter, encoder, or RNG change.
- Any substrate change (no JIT, no vectorization, no framework swap; substrate stays hand-written numpy).
- Any workbench work; any tag, freeze, or announcement action; any modification justified by a Stage 1 confirm (a confirm unlocks discussion of modifications, not edits — each modification still needs its own approval).

## Return path

Everything returns via the owner ferry. The instructor verifies each stage independently from the remote and rules PASS/FAIL. On FAIL at any stage, everything stops until the owner directs a fix or revert. Lead every report with anything skipped, not doable, or failed — before any totals.

---

**Footer (status):** ISSUED for Part 1 (benchmark spike, measurement only) by owner spike-first gate ruling 2026-10-26. Part 2 (sweep) is NOT issued by this ruling — it needs the owner's proceed ruling after the spike report has been instructor-verified. Nothing in this file authorizes the sweep.
