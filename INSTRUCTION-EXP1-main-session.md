# INSTRUCTION — for the main session (implementer): EXP1 Step 0

**Role split.** You (the main session) are the implementer. The
instructor session (side chat) wrote the work order and will verify
your build. The owner ferries files between us. Do NOT verify your
own work as "instructor-verified" — verification comes from the
instructor session after delivery, never from the builder.

**Task.** Implement `WO-TBM-EXP1.md`, Step 0 ONLY, exactly as written.
That WO file is ferried together with this note: the WO is the full
spec, this note is the handoff. If this note and the WO ever
disagree, the WO governs — and report the disagreement.

**Deliverables — all DRAFT, UNCOMMITTED, UNPUSHED.**
Do not commit, push, or tag anything.

1. Parameterized template code (size parameter ONLY, §2.1 of the
   WO) + the W10 fidelity comparison.
2. New world file (W20, W30, M1, M2, M3) — `world.py` untouched.
3. Runner + greedy evaluation (trained + held-out as specified).
4. Design note (`nn/decisions_exp1_design.md`) with the prereg,
   counts, sanity results, and the verification section left
   EMPTY for the instructor.
5. Completion report: what was built, every deviation with its
   reason, anything skipped or not doable (lead with this),
   and the sanity results.

**Boundaries (hard).** Step 0 ONLY. NO sweep trainings or evals
beyond the WO §2.5 sanity checks. NO spike. NO Layer F worlds.
NO sibling-repo changes. NO commits, pushes, or tags. NO
hyperparameter, RNG, or schedule changes. NO template change
beyond the size parameterization.

**Fidelity gate.** If the W10 check does not match, STOP and
report — do not proceed past it on assumption.

**Label rule.** NEVER write "instructor-verified" anywhere (note,
commit message, report) before the instructor's ruling exists.
This pre-claim has recurred in past programmes and must not
recur here.

**Reporting norm.** You receive outcome specs, not scripts: you
may choose a better design or cleaner verification, but you MUST
report every deviation with its reason, MUST lead with anything
skipped or not doable, and MUST never hide failures. A flagged
defect is not a work order: findings return as proposals with
exact scope, not edits.

**Return path.** Deliver all files + the report back through the
owner (ferry) to the instructor session for independent
verification. On PASS, the instructor commits + pushes and
confirms from the remote. Gate rulings, spike, and sweep runs
follow separately — none is authorized by this instruction.

**If anything in the WO is unclear or not doable,** say so in the
report — do not silently substitute, and do not expand scope to
resolve it.
