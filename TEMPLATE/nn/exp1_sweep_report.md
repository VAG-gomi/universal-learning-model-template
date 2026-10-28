# EXP1 Step 3 — Sweep report (DRAFT)

**Status: DRAFT, self checked only — NOT instructor-verified.**
**This report does NOT label Stage 1 as confirmed, does NOT label the
sweep as instructor-verified, and does NOT claim cross-domain
universality. The final Stage 1 statement awaits instructor
verification in Step 4 (rev1).**

**Authorization:** owner Gate 1 proceed ruling + issuance of rev1,
both given 2026-10-27 in the worker chat, in the owner's own words:
proceed with the EXP1 sweep on the current hand-written numpy
substrate, no substrate change, despite the verified 12.98-hour
projection vs the 4-hour threshold, noting the projection is
seed-0-conditional; and "I issue rev1, and rev1 governs going
forward." Recorded at `2ac3d1f` (issued rev1) and `5dcac7c`
(STATUS.md recording Gate 1 + issuance). Executor: spike-executor
session (Gate 0d). Substrate: hand-written numpy, no change.
Governing, in order: owner rulings, WO-TBM-EXP1.md §5, design note
`TEMPLATE/nn/decisions_exp1_design.md` §4 (frozen preregistration),
then issued rev1.

**Code path:** `TEMPLATE/nn/exp1_run.py` `train_loop` /
`evaluate_job` only. No template, schedule, encoder, RNG,
hyperparameter, arm, or substrate change. Hyperparameters
unchanged: 2000 episodes, hidden=32, lr=1e-3, schedule 20/10
everywhere, episode cap 200. Greedy eval only: ε=0, weights
frozen, one deterministic episode per start phase 0–19,
fresh encoder per (agent, eval world) job.

## §0. Skipped / failed / not doable — lead statement

- **Skipped: none.** All 60 trainings and all 105 eval jobs ran.
- **Failed jobs: none.** No training or eval job failed.
- **Duplicates: 0.** Duplicate guard held (see §7).
- **Not doable: none** within the authorized scope.
- **Deviations (reported, with reasons):**
  1. **Delivery form:** rev1 Step 3 says deliver sweep records +
     report committed and pushed. This coordinator delivers them
     UNCOMMITTED in the working tree, for parent verification /
     commit / push, as instructed in the coordinator task (the
     same pattern as the spike delivery). No commit or push was
     made by the coordinator. This is a delivery-route deviation
     only; it does not change any record, number, or bar.
  2. **Runner form:** the sweep was run through a new runner,
     `TEMPLATE/nn/exp1_sweep.py`, following the spike runner's
     pattern (`train_loop` / `evaluate_job`, train-then-eval in
     the same process, weights in memory only, job-level
     SWEEP records with deterministic resume), instead of calling
     `exp1_run.run_sweep()` directly. Reason: `run_sweep()` is
     not resume-safe — it trains every agent unconditionally on
     relaunch and writes a training record unconditionally, so
     a restart would duplicate training records. The sweep's own
     `train_loop` / `evaluate_job` code path is unchanged; only
     the resume / record-writing wrapper differs, and it is
     disclosed here.
  3. **Recorded wall vs spike projection:** recorded job walls
     sum to 15.06 h (trainings 54211.7 s + evals 10.6 s; see §1),
     above the spike point estimate 12.98 h and above the spike
     sensitivity high end 13.98 h. This is NOT a protocol
     deviation and NOT a completeness or bar failure: the spike
     projection was seed-0-conditional by its own qualification
     (only W10 had 2 seeds; the ±7.73% sensitivity range does
     not cover a learning-vs-nonlearning jump), and sweep
     training walls vary by seed (notably W30 / M3 trainings
     that run to the tick cap). Recorded walls exclude the
     incomplete killed trainings listed in §9 (they were never
     recorded as jobs), so elapsed time including restarts is
     higher than the recorded sum; no elapsed total is claimed
     here.
  4. **First launch method:** the first launch used a detached
     nohup process. After the first VM restart it was replaced
     by tracked background exec launches, so completion would
     be delivered back to the coordinator session. Reason:
     tracking / resume delivery. The records are identical in
     form across launches; the first launch's completed units
     were skipped, not re-run, on resume.

## §1. Plan, counts, protocol

- Plan verified before any training (from
  `exp1_run.sweep_plan()`): trainings 60, eval jobs 105,
  arm-runs 165. Unique trainings 60, unique eval jobs 105.
- Trainings: inside 45 (W10/W20/W30 × plain/memory/wrapped ×
  seeds 0–4) + outside 15 (M1/M2/M3 × wrapped × seeds 0–4).
- Eval jobs: inside trained 45 + inside held-out 45 +
  outside trained 15 = 105. Each eval job = 20 episodes.
  Total eval episodes = 2100.
- Held-out variants: W10h door (5,2), W20h door (10,5),
  W30h door (15,7). All worlds schedule 20/10.
- Job grouping: train an agent, then evaluate its trained
  world and (inside only) its held-out world in the same
  process/session before discarding its weights. No `.npz`
  weights were saved to the repo (0 `.npz` files found).
- No SPIKE records were read, pooled, or counted here.
  Spike records remain in `exp1_spike_records.jsonl`,
  untouched (no diff to spike files).
- Files delivered (all uncommitted, in `TEMPLATE/nn/`):
  - `exp1_sweep.py` — runner (this report's §0 deviation 2)
  - `exp1_sweep_records.jsonl` — 165 job lines, record="SWEEP"
  - `exp1_sweep_training.jsonl` — 60 training summaries
    (per-episode ticks / reached_flags / crushes lists)
  - `exp1_sweep_eval_episodes.jsonl` — 2100 eval episode
    records, with step trajectories from `evaluate_job`
  - `exp1_sweep.log` — per-job stdout log
  - `exp1_sweep_report.md` — this report
- Independent re-derivation (self check only): eval job
  reached totals match eval episode reached totals for all
  105 eval jobs (0 mismatches); training job reached totals
  match training summary reached totals for all 60 trainings
  (0 mismatches); eval episode count per eval job = 20 for
  all 105 jobs.

## §2. Training results (reached / 2000 episodes, pooled over seeds 0–4)

Protocol: 2000 episodes per training, as in §1. Denominators
are 10000 per (arm, world) cell (5 seeds × 2000).

| Arm | World | Training reached | Rate |
|-----|-------|------------------|------|
| plain | W10 | 8480 / 10000 | 84.80% |
| plain | W20 | 7265 / 10000 | 72.65% |
| plain | W30 | 943 / 10000 | 9.43% |
| memory | W10 | 8693 / 10000 | 86.93% |
| memory | W20 | 7048 / 10000 | 70.48% |
| memory | W30 | 750 / 10000 | 7.50% |
| wrapped | W10 | 8600 / 10000 | 86.00% |
| wrapped | W20 | 6811 / 10000 | 68.11% |
| wrapped | W30 | 2004 / 10000 | 20.04% |
| wrapped | M1 | 7069 / 10000 | 70.69% |
| wrapped | M2 | 3495 / 10000 | 34.95% |
| wrapped | M3 | 0 / 10000 | 0.00% |

Training reached is reported here as a training outcome only;
it is not the bar. The bar (§4) uses greedy eval outcomes.

## §3. Eval results — inside worlds (greedy, ε=0, 20 phases per job)

Denominators: 100 episodes per (arm, train world, eval kind)
cell (5 seeds × 20 phases). Held-out eval worlds are W10h /
W20h / W30h respectively.

### Trained-world eval

| Arm | W10 trained | W20 trained | W30 trained | Trained pooled (W10+W20+W30) |
|-----|-------------|-------------|-------------|------------------------------|
| plain | 86 / 100 (86.00%) | 40 / 100 (40.00%) | 0 / 100 (0.00%) | 126 / 300 (42.00%) |
| memory | 100 / 100 (100.00%) | 50 / 100 (50.00%) | 19 / 100 (19.00%) | 169 / 300 (56.33%) |
| wrapped | 100 / 100 (100.00%) | 99 / 100 (99.00%) | 20 / 100 (20.00%) | 219 / 300 (73.00%) |

### Held-out eval

| Arm | W10 held-out | W20 held-out | W30 held-out | Held-out pooled (W10+W20+W30) |
|-----|--------------|--------------|--------------|-------------------------------|
| plain | 0 / 100 (0.00%) | 0 / 100 (0.00%) | 0 / 100 (0.00%) | 0 / 300 (0.00%) |
| memory | 0 / 100 (0.00%) | 0 / 100 (0.00%) | 0 / 100 (0.00%) | 0 / 300 (0.00%) |
| wrapped | 1 / 100 (1.00%) | 0 / 100 (0.00%) | 0 / 100 (0.00%) | 1 / 300 (0.33%) |

The single wrapped held-out reached episode is wrapped/W10
seed 3, held-out W10h, 1/20 for that job; all other wrapped
held-out jobs are 0/20 (see Appendix).

## §4. Frozen SCALES bar comparison (preregistered terms only)

Preregistration (design note §4, unchanged):
primary bar "SCALES" = wrapped held-out pooled (W10+W20+W30)
≥20% absolute AND ≥50% of wrapped trained pooled rate
(trained pooled over W10+W20+W30).

- Wrapped held-out pooled: **1 / 300 = 0.33%**
- Absolute bar (≥20%): **NOT MET** (0.33% < 20%)
- Wrapped trained pooled: **219 / 300 = 73.00%**
- 50% of wrapped trained pooled rate: **36.50%**
- Relative bar (≥50% of trained pooled): **NOT MET**
  (0.33% < 36.50%)
- **Primary bar SCALES: NOT MET** (both parts fail).

No other bar analysis is performed here, per the
preregistration. No claim is made beyond this comparison.

## §5. Secondary contrast (reported, NOT gating)

Preregistration: wrapped held-out pooled (W10+W20+W30) >
plain held-out pooled (same set), reported, NOT gating.

- Wrapped held-out pooled: 1 / 300 (0.33%)
- Plain held-out pooled: 0 / 300 (0.00%)
- Contrast: 1 / 300 > 0 / 300, arithmetically true.
- This contrast does NOT gate anything, does NOT change
  the §4 result, and does NOT by itself license any
  further claim. It is reported here only because the
  preregistration requires reporting it.

## §6. Outside worlds — DISCOVERY ONLY (no bar, no verdict)

Preregistration: M1/M2/M3 are DISCOVERY ONLY — no bar,
no verdict. Output is a performance map + a gap list.

Performance map (wrapped, trained-world greedy eval,
5 seeds × 20 phases = 100 episodes per world):

| World | Reached | Rate |
|-------|---------|------|
| M1 | 100 / 100 | 100.00% |
| M2 | 54 / 100 | 54.00% |
| M3 | 0 / 100 | 0.00% |

Gap list (descriptive, in preregistered terms only):
- M1 trained eval is at ceiling in this sweep (100/100);
  M2 trained eval is partial (54/100); M3 trained eval
  is zero (0/100), matching its training reached
  (0/10000 in §2).
- No verdict is attached to any outside world, and no
  bar is applied to any outside world.

## §7. Completeness statement

**COMPLETE.** All 60 trainings complete, all 105 eval jobs
complete, 0 duplicates. Had any job been incomplete or
any duplicate appeared, the statement would be INCOMPLETE
per the preregistration; neither condition holds.

Evidence (re-derived from the delivered records, self
check only):
- Job lines: 165 (60 training + 105 eval), 0
  `resume_retrain` note lines (see §9 for why: all kills
  were mid-training, so incomplete units re-ran as fresh
  training jobs, not as resume re-trains).
- Unique trainings: 60 / 60. Unique eval jobs: 105 / 105.
- Training summaries: 60. Eval episodes: 2100
  (105 jobs × 20), each job with exactly 20 episodes.
- Eval crushes total across eval episodes: 13 (reported
  for completeness; crushes are not part of the bar).

## §8. Stage 1 comparison — in exactly the preregistered terms

Preregistration confirm rule (design note §4, unchanged):
Stage 1 CONFIRMS iff the primary bar is met, labeled
"parameterized template scales" (within-domain scaling —
NOT cross-domain universality). If not met, Stage 1 does
NOT confirm, and no universality-based modification unlocks.

- Primary bar (§4): NOT MET.
- **Stage 1 comparison, in preregistered terms:
  DOES NOT CONFIRM.** (Self checked only; this is the
  comparison, not the final Stage 1 statement. The final
  Stage 1 statement awaits instructor verification in
  Step 4.)
- No universality-based modification unlocks on this
  comparison. No cross-domain universality is claimed
  from this sweep. Any modification discussion remains
  gated on the Step 4 ruling, and each modification
  would still need its own approval.

## §9. Restart disclosures (all restarts, causes if known)

All restarts were VM/system restarts (SIGTERM to the
sweep process; on relaunch, system uptime was 0–1 min
and systemd start time matched the restart). No job
failure, no duplicate, and no partial job record
resulted from any restart; the runner's load-time
consistency check passed on every relaunch (training
summaries match job records; eval jobs have exactly
20 episodes; no summary/episode without a job record).

1. **Restart 1 — VM restart ~19:07 UTC 2026-10-27.**
   Completed at kill: 5 trainings / 10 evals.
   Killed mid-training: plain/W20/0 (incomplete, NOT
   recorded; re-ran from scratch on relaunch).
2. **Restart 2 — VM restart ~23:45 UTC 2026-10-27.**
   Completed at kill: 29 trainings / 58 evals.
   Killed mid-training: memory/W30/4 (incomplete, NOT
   recorded; re-ran from scratch).
3. **Restart 3 — VM restart ~01:45 UTC 2026-10-28.**
   Completed at kill: 43 trainings / 86 evals.
   Killed mid-training: wrapped/W30/3 (incomplete, NOT
   recorded; re-ran from scratch).
4. **Restart 4 — VM restart ~04:40 UTC 2026-10-28.**
   Completed at kill: 48 trainings / 93 evals.
   Killed mid-training: wrapped/M1/3 (incomplete, NOT
   recorded; re-ran from scratch).
5. **Restart 5 — VM restart ~06:47 UTC 2026-10-28.**
   Completed at kill: 56 trainings / 101 evals.
   Killed mid-training: wrapped/M3/1 (incomplete, NOT
   recorded; re-ran from scratch).
6. **Restart 6 — VM restart ~08:52 UTC 2026-10-28.**
   Completed at kill: 57 trainings / 102 evals.
   Killed mid-training: wrapped/M3/2 (incomplete, NOT
   recorded; re-ran from scratch).
7. **Restart 7 — VM restart ~10:52 UTC 2026-10-28.**
   Completed at kill: 59 trainings / 104 evals.
   Killed mid-training: wrapped/M3/4 (incomplete, NOT
   recorded; re-ran from scratch).
8. **Final launch — completed, exit 0, 2026-10-28.**
   Final unit wrapped/M3/4 trained (wall 3147.7 s,
   reached 0/2000) and evaluated (0/20). Runner printed
   "SWEEP run complete: plan {'trainings': 60,
   'eval_jobs': 105, 'arm_runs': 165}".

No other restarts, failures, or retrains occurred.
`resume_retrain` notes in the records: 0, for the reason
stated in §7 (all kills were mid-training).

## §10. Limitations and qualifications (carried, not hidden)

- This report is DRAFT, self checked only. Its numbers
  were re-derived from the delivered records by the
  coordinator (job/episode/training-summary cross-checks
  in §1 and §7, 0 mismatches), but they have NOT been
  independently verified by the instructor. Step 4
  verification may correct them.
- Recorded job walls sum to 15.06 h (§0 deviation 3).
  That sum excludes incomplete killed trainings, so it
  is not an elapsed-time claim.
- Eval outcomes are greedy (ε=0, weights frozen, fresh
  encoder per eval job) per the frozen protocol. No
  other eval protocol was run, and no result here
  should be read under a different protocol.
- Outside worlds are discovery only (§6). Inside
  held-out outcomes are the bar inputs (§4); training
  outcomes (§2) are not the bar.

## Appendix — Per-seed eval reached (greedy, /20 per job)

Format: arm, train world, seed, trained reached/20,
held-out reached/20 (— = no held-out job for outside).

| Arm | Train world | Seed | Trained | Held-out |
|-----|-------------|------|---------|----------|
| plain | W10 | 0 | 20 | 0 |
| plain | W10 | 1 | 6 | 0 |
| plain | W10 | 2 | 20 | 0 |
| plain | W10 | 3 | 20 | 0 |
| plain | W10 | 4 | 20 | 0 |
| plain | W20 | 0 | 0 | 0 |
| plain | W20 | 1 | 0 | 0 |
| plain | W20 | 2 | 0 | 0 |
| plain | W20 | 3 | 20 | 0 |
| plain | W20 | 4 | 20 | 0 |
| plain | W30 | 0 | 0 | 0 |
| plain | W30 | 1 | 0 | 0 |
| plain | W30 | 2 | 0 | 0 |
| plain | W30 | 3 | 0 | 0 |
| plain | W30 | 4 | 0 | 0 |
| memory | W10 | 0 | 20 | 0 |
| memory | W10 | 1 | 20 | 0 |
| memory | W10 | 2 | 20 | 0 |
| memory | W10 | 3 | 20 | 0 |
| memory | W10 | 4 | 20 | 0 |
| memory | W20 | 0 | 0 | 0 |
| memory | W20 | 1 | 12 | 0 |
| memory | W20 | 2 | 20 | 0 |
| memory | W20 | 3 | 18 | 0 |
| memory | W20 | 4 | 0 | 0 |
| memory | W30 | 0 | 19 | 0 |
| memory | W30 | 1 | 0 | 0 |
| memory | W30 | 2 | 0 | 0 |
| memory | W30 | 3 | 0 | 0 |
| memory | W30 | 4 | 0 | 0 |
| wrapped | W10 | 0 | 20 | 0 |
| wrapped | W10 | 1 | 20 | 0 |
| wrapped | W10 | 2 | 20 | 0 |
| wrapped | W10 | 3 | 20 | 1 |
| wrapped | W10 | 4 | 20 | 0 |
| wrapped | W20 | 0 | 20 | 0 |
| wrapped | W20 | 1 | 19 | 0 |
| wrapped | W20 | 2 | 20 | 0 |
| wrapped | W20 | 3 | 20 | 0 |
| wrapped | W20 | 4 | 20 | 0 |
| wrapped | W30 | 0 | 0 | 0 |
| wrapped | W30 | 1 | 20 | 0 |
| wrapped | W30 | 2 | 0 | 0 |
| wrapped | W30 | 3 | 0 | 0 |
| wrapped | W30 | 4 | 0 | 0 |
| wrapped | M1 | 0 | 20 | — |
| wrapped | M1 | 1 | 20 | — |
| wrapped | M1 | 2 | 20 | — |
| wrapped | M1 | 3 | 20 | — |
| wrapped | M1 | 4 | 20 | — |
| wrapped | M2 | 0 | 0 | — |
| wrapped | M2 | 1 | 20 | — |
| wrapped | M2 | 2 | 15 | — |
| wrapped | M2 | 3 | 19 | — |
| wrapped | M2 | 4 | 0 | — |
| wrapped | M3 | 0 | 0 | — |
| wrapped | M3 | 1 | 0 | — |
| wrapped | M3 | 2 | 0 | — |
| wrapped | M3 | 3 | 0 | — |
| wrapped | M3 | 4 | 0 | — |

End of DRAFT report. No commit or push was made by the
coordinator. Parent verification / commit / push pending.
