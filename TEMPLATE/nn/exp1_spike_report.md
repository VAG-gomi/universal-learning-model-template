# EXP1 Part 1 — Benchmark SPIKE Report (MEASUREMENT ONLY)

**Status: DRAFT — self checked only. NOT verified by any independent
party. This report claims NO proceed authorization.**

- Spike implementer session; base: sibling repo
  `VAG-gomi/universal-learning-model-template`, HEAD `11d61dd`
  (local = remote, confirmed before and after the runs).
- Authorization basis (as tasked): Part 1 (benchmark spike,
  measurement only) per the owner correction of 2026-10-26
  (this session executes Part 1; the issued instruction's
  substance governs). Part 2 (sweep) is NOT authorized by this
  report or by Part 1, and needs a separate proceed ruling.
- All spike files are NEW and UNCOMMITTED (see §7). No existing
  file was modified, nothing was committed or pushed, no sweep
  training or eval ran, no spike weight was saved to disk.

## 0. Skipped / not doable / failed — leading (before any totals)

- **Skipped: nothing in the spike design was skipped.** All 15
  training jobs and all 19 eval jobs ran to completion (see §2).
  No job was shortened, cut, or dropped for running long.
- **Not doable: nothing proved not doable.**
- **Failed, recovered, disclosed:**
  1. **Two runtime kills (SIGTERM).** Run attempt 1 was killed
     after ~64 min (through memory/W30/0's eval); attempt 2 was
     killed after ~93 min (through wrapped/M2/0's eval).
     Attempt 3 completed (~53 min). Recovery was deterministic:
     records write only on job completion, so no partial record
     exists; the relaunch skipped every completed unit and ran
     only the remainder. Final record state: 15 unique trainings,
     19 unique evals, 0 duplicates, 0 resume-retrain lines.
     Partial progress of the unit in flight at each kill was
     lost by design (it leaves no record) and that unit re-ran
     from scratch in the next attempt; no completed job ran
     twice. See §5.
  2. **First profiling method invalid, discarded.** The cProfile
     bucketing summed CUMULATIVE times across the call tree,
     double-counting shared ancestors — its "profile total"
     (1,394 s) exceeded the jobs' actual wall time (~366 s).
     That file is preserved as
     `exp1_spike_profile_cprofile_DISCARDED.txt` and was NOT
     used. It was replaced by direct per-call component timing
     (§4), which is the only profile evidence in this report.
- **Not a failure, stated so it is not misread:** several spike
  trainings reached ~0/2000 (M3/wrapped 0, W30/plain 1,
  W30/wrapped 1, M2/wrapped 3). Those jobs completed and timed
  normally; their low reached counts are timing diagnostics
  (failed trainings run every episode to the 200-tick cap —
  see §2/§3), NOT sweep results, NOT analyzed against the
  SCALES bar, and never pooled with anything. No bar analysis
  is performed in a spike report.

## 1. Spike design (stated before any numbers)

- **Trainings (15, 2000 episodes each, 20/10, sweep
  hyperparameters: hidden=32, lr=1e-3, cap=200, same
  `train_loop` the sweep uses):**
  inside W10/W20/W30 x plain/memory/wrapped x seed 0 (9);
  W10 x plain/memory/wrapped x seed 1 (3, seed-variance
  gauge); outside M1/M2/M3 x wrapped x seed 0 (3).
- **Eval jobs (19, greedy eps=0, weights frozen, 20 episodes
  one per start phase 0..19, fresh encoder per job — exactly
  `evaluate_job` semantics):** one trained-world eval per
  trained spike agent (15), plus one held-out eval per
  wrapped inside agent (4: W10 seed 0/1, W20 seed 0, W30
  seed 0). Held-out evals for plain/memory were NOT run;
  their cost is proxied by the same world's trained-eval
  time (see §3 assumption — evals total ~10 s either way,
  so the proxy cannot move the threshold comparison).
- **Timing:** wall clock (`time.perf_counter`) around each
  job, recorded per job in `exp1_spike_records.jsonl`
  (JSONL, one line per job, appended on completion).
  Weights were never written to disk: each trained spike
  agent lived in memory only for its own eval jobs, then
  was dropped (0 `.npz` files in the tree, verified).
- **Resume:** a relaunch reads the records file first and
  skips any unit whose training record and all eval records
  already exist; a unit with a training record but missing
  evals would re-train (weights are never saved) and write
  only the missing evals plus a resume-retrain note line.
  No such case occurred (0 resume-retrain lines).
- **Profile (proportions only, never projection inputs):**
  direct per-call component timing on two live setups
  (W10/plain, M3/wrapped): environment step, encoding,
  act-forward, buffer-add, learning update, plus one
  full-step loop for the residual (§4).
- **Projection method (§3):** per (arm, world) training cell,
  sweep cost = 5 seeds x measured per-training time (W10
  cells: mean of seeds 0/1; other cells: single seed-0
  measurement). Eval cost = 5 seeds x measured per-job
  time per cell (with the held-out proxy above). Total =
  trainings + evals, sequential execution on this VM.
  Range: (a) observed range — each cell at its measured
  min / max (only W10 cells vary); (b) sensitivity range —
  the largest W10-observed relative seed spread applied
  to every cell (assumption, stated in §3).

## 2. Timed jobs (all SPIKE records, never sweep records)

### 2a. Trainings (2000 episodes each)

| Arm | World | Seed | Wall (s) | Reached | Ticks |
|-----|-------|------|----------|---------|-------|
| plain | W10 | 0 | 107.4 | 1706 | 135656 |
| plain | W10 | 1 | 116.0 | 1647 | 146427 |
| memory | W10 | 0 | 99.1 | 1722 | 125836 |
| memory | W10 | 1 | 96.6 | 1754 | 123012 |
| wrapped | W10 | 0 | 100.2 | 1716 | 124734 |
| wrapped | W10 | 1 | 106.6 | 1698 | 132668 |
| plain | W20 | 0 | 313.0 | 1559 | 189526 |
| memory | W20 | 0 | 355.9 | 1371 | 215943 |
| wrapped | W20 | 0 | 336.0 | 1425 | 196017 |
| plain | W30 | 0 | 1352.8 | 1 | 399994 |
| memory | W30 | 0 | 1111.4 | 747 | 327252 |
| wrapped | W30 | 0 | 1364.4 | 1 | 399971 |
| wrapped | M1 | 0 | 330.9 | 1436 | 196771 |
| wrapped | M2 | 0 | 675.2 | 3 | 399841 |
| wrapped | M3 | 0 | 3189.8 | 0 | 400000 |

Reading (diagnostic only, not a finding): trainings that
learn run ~123k–216k ticks; trainings that do not learn run
every episode to the 200-tick cap (~400k ticks). W30/plain,
W30/wrapped, M2/wrapped, and M3/wrapped all sit at the cap.
That tick volume, times the per-step cost in §4, is why
large-grid trainings are slow — measured, not assumed.

### 2b. Eval jobs (20 greedy episodes each; wall times in seconds)

| Arm | Train world | Eval world | Kind | Wall (s) |
|-----|-------------|------------|------|----------|
| plain | W10 | W10 | trained | 0.01, 0.05 (seeds 0, 1) |
| memory | W10 | W10 | trained | 0.01, 0.02 |
| wrapped | W10 | W10 | trained | 0.01, 0.01 |
| wrapped | W10 | W10h | held-out | 0.09, 0.08 |
| plain | W20 | W20 | trained | 0.09 |
| memory | W20 | W20 | trained | 0.09 |
| wrapped | W20 | W20 | trained | 0.03 |
| wrapped | W20 | W20h | held-out | 0.11 |
| plain | W30 | W30 | trained | 0.21 |
| memory | W30 | W30 | trained | 0.05 |
| wrapped | W30 | W30 | trained | 0.14 |
| wrapped | W30 | W30h | held-out | 0.14 |
| wrapped | M1 | M1 | trained | 0.02 |
| wrapped | M2 | M2 | trained | 0.10 |
| wrapped | M3 | M3 | trained | 0.27 |

Eval jobs are fractions of a second each; all 19 together
took 1.6 s of recorded wall time. Evals are irrelevant to
the threshold comparison (§3).

## 3. Projection vs the 4-hour threshold

Sweep composition (frozen design): 60 trainings (inside 45 =
3 arms x 3 worlds x 5 seeds; outside 15 = wrapped x 3 worlds
x 5 seeds) + 105 eval jobs (inside trained 45 + inside
held-out 45 + outside trained 15) = 165 arm-runs. The
arm-run trigger already fired (165 > 150); this spike does
not re-decide that — it measures time.

Per-cell training times (seconds; W10 = mean of 2 seeds):

| Cell | Per training | x5 seeds | Subtotal (s) |
|------|-------------|----------|--------------|
| W10 plain | 111.7 | 5 | 558.5 |
| W10 memory | 97.9 | 5 | 489.3 |
| W10 wrapped | 103.4 | 5 | 517.0 |
| W20 plain | 313.0 | 5 | 1565.0 |
| W20 memory | 355.9 | 5 | 1779.5 |
| W20 wrapped | 336.0 | 5 | 1680.0 |
| W30 plain | 1352.8 | 5 | 6764.0 |
| W30 memory | 1111.4 | 5 | 5557.0 |
| W30 wrapped | 1364.4 | 5 | 6822.0 |
| M1 wrapped | 330.9 | 5 | 1654.5 |
| M2 wrapped | 675.2 | 5 | 3376.0 |
| M3 wrapped | 3189.8 | 5 | 15949.0 |

- Sweep trainings, point estimate: **46,711.8 s (12.98 h)**.
- Observed range (each cell at measured min/max; only W10
  cells vary): **[46,667.8, 46,755.7] s (12.97–12.99 h)**.
- W10 seed spread: plain 7.73%, memory 2.54%, wrapped
  6.25%; largest = 7.73%. Sensitivity range (that spread
  applied to every cell, assumption stated): **[43,099.2,
  50,324.4] s (11.97–13.98 h)**.
- Sweep evals, point estimate: **9.6 s** (observed range
  [9.3, 9.9] s) — negligible.
- **Total, point estimate: 46,721.4 s = 12.98 h.**
- **Total, observed range: [46,677.1, 46,765.6] s =
  12.97–12.99 h. Sensitivity range: [43,108.8, 50,334.0] s
  = 11.97–13.98 h.**
- **Threshold comparison: the 4-hour threshold is 14,400 s.
  The point estimate exceeds it by 32,321.4 s (8.98 h).
  Even the sensitivity low end (43,108.8 s, 11.97 h)
  exceeds it by ~3x.** The full sweep as designed does
  not fit in 4 hours of sequential compute on this VM.

Shares of the training total (point): M3/wrapped 34.1%,
W30 cells 41.0% (plain 14.5%, memory 11.9%, wrapped
14.6%), W20 cells 10.8%, M2/wrapped 7.2%, M1/wrapped
3.5%, W10 cells 3.3%. Inside worlds 55.1%, outside
worlds 44.9%. Two cells dominate: M3 (a 50x50 world
that never learns in 2000 episodes, so all 400k ticks
run at the largest per-step cost) and W30 (plain and
wrapped never learn either, so all ~400k ticks run).

Assumptions and bounds (stated, not hidden):
- Sequential execution on this VM, same code path the
  sweep uses (`train_loop` / `evaluate_job`, identical
  hyperparameters) — the spike ran that exact path, so
  this is a measurement of the sweep's own code, not of
  a proxy.
- Seed variation beyond W10 is unmeasured (spike used
  seed 0 elsewhere, seeds 0/1 on W10 only). The
  sensitivity range covers it by applying the largest
  W10-observed spread (7.73%) to every cell; the
  conclusion (over threshold) survives even that range.
- Held-out eval times for plain/memory are proxied by
  same-world trained-eval times; wrapped held-out vs
  trained evals differ by <=0.1 s per job, and evals
  total ~10 s, so no proxy choice moves the comparison.
- This projection is a wall-clock projection for this
  VM. Parallel execution would change wall time, but
  no parallel design is authorized or assumed here;
  prior programmes ran sequentially, as did this spike.

## 4. Profile note (where the time goes — measured)

Direct per-call component timing on live setups (the
cProfile attempt in §0 was invalid and is not used):

| Setup | Full step | Learning update | Env | Encode | Act fwd | Buffer | Residual |
|-------|-----------|-----------------|-----|--------|---------|--------|----------|
| W10/plain | 753.3 us | 660.8 us (87.7%) | 3.1 us (0.4%) | 0.7 us (0.1%) | 12.7 us (1.7%) | 0.4 us (0.0%) | 75.5 us (10.0%) |
| M3/wrapped | 8868.2 us | 8398.7 us (94.7%) | 3.1 us (0.0%) | 2.9 us (0.0%) | 59.0 us (0.7%) | 0.3 us (0.0%) | 404.2 us (4.6%) |

- The time goes to the **learning update** (batch-32
  Q-learning update: sample, target forward, net forward,
  masked-MSE gradient, backward, optimizer step): 87.7%
  on W10/plain, 94.7% on M3/wrapped. Environment stepping
  and encoding are negligible (<1% combined) at both
  sizes.
- The learning-update cost grows with input size:
  660.8 us at 101 inputs (W10/plain) vs 8,398.7 us at
  2,504 inputs (M3/wrapped) — 12.7x for 24.8x inputs.
  Combined with tick volume (§2a), that is the measured
  mechanism of the size scaling: bigger grids cost more
  per step AND run more ticks (when they fail to learn).
- No speedup is claimed for any substrate change: no
  JIT/vectorized candidate exists, none was built or
  tested here, and this profile is a measurement of the
  current hand-written numpy substrate only.

## 5. Restarts, disclosures, deviations

- **Restarts (2, both SIGTERM kills by the runtime):**
  attempt 1 killed after ~64 min (last recorded job:
  memory/W30/0 eval); attempt 2 killed after ~93 min
  (last recorded job: wrapped/M2/0 eval); attempt 3
  completed in ~53 min ("SPIKE run complete", exit 0).
  Recorded job wall sum across all attempts: 9,656.8 s
  (trainings 9,655.3 s + evals 1.6 s). The gap between
  attempt durations and recorded job walls is the lost
  partial progress of the in-flight units at each kill
  (unrecorded by design) plus skip-checking overhead.
- **Deviations from the spike design: two, both reported
  here.** (a) Profiling method changed from cProfile
  bucketing to direct component timing, because the
  cProfile bucketing was invalid (see §0/§4); the
  discarded file is preserved, not hidden. (b) Three
  attempts instead of one, because the runtime killed
  the first two; recovery used the designed resume
  logic, no design change. No other deviation: job
  list, seeds, hyperparameters, eval semantics, and
  record schema are exactly as designed in §1.
- **Label compliance:** every spike file, output line,
  and record line is labeled SPIKE. No spike record is
  a sweep record; no spike training counts toward sweep
  completeness; no spike result is pooled with any sweep
  result (no sweep result exists). No spike weight was
  saved (0 `.npz` files, verified).

## 6. What this report does and does not authorize

- This report is a measurement deliverable for Part 1
  only. It does NOT authorize the sweep, does NOT claim
  proceed authorization, and does NOT analyze anything
  against the frozen SCALES bar.
- Next steps, each needing its own ruling: independent
  verification of this spike report (by the parent
  session, from the remote) -> owner proceed ruling ->
  sweep runs (Steps 1+). Until the proceed ruling exists,
  the sweep remains unauthorized.
- No Layer F world, schedule change, template change,
  new arm, hyperparameter/encoder/RNG change, substrate
  change, workbench work, or tag/freeze/announcement
  action is authorized or performed by this report.

## 7. Files delivered (all NEW, UNCOMMITTED, in the sibling working tree)

- `TEMPLATE/nn/exp1_spike.py` — spike runner (train +
  eval timing, resume logic, component timing).
- `TEMPLATE/nn/exp1_spike_records.jsonl` — 34 SPIKE
  record lines (15 trainings, 19 evals, 0 resume-retrain
  lines, 0 duplicates).
- `TEMPLATE/nn/exp1_spike_profile.txt` — component
  timing results (§4).
- `TEMPLATE/nn/exp1_spike_profile_cprofile_DISCARDED.txt`
  — the invalid cProfile attempt, preserved (not used).
- `TEMPLATE/nn/exp1_spike_report.md` — this report.

Verification state: DRAFT, self checked only (record
counts, uniqueness, and projection arithmetic re-derived
from the records file by script before writing). No
independent ruling exists on this report.
