# Universal Learning-Model Template — DRAFT

**Status: DRAFT — awaiting owner Step 6 review. This repository is not
announced, and no claim of verification or publication is made here.
It was created public per the owner's approval decision; announcement
is gated on owner Step 6 review, not on visibility.**

## One job

This repository holds one thing: a **universal learning-model
template** — a small, symbolic, inspectable design for building AI
models — together with the **study paper** that shows, with proof
pointers, what that design has actually demonstrated, and the
**implementation instructions** for building a new model around it.
Nothing else lives here: no programme runners, no record files, no
probe notes. Those stay in the workbench and are linked, never copied.

## The family

One job per repository; repositories point to each other instead of
duplicating each other.

- **Personal codes (the workbench):**
  [`VAG-gomi/time-based-mind-model`](https://github.com/VAG-gomi/time-based-mind-model)
  — experiments, tests, records, the full evidence chain. It stays
  exactly as it is. Its load is not a defect; it is what a workbench
  looks like. Every proof pointer in this repository's paper resolves
  into it.
- **Universal papers-studies (this repository):** the template, the
  study paper with proof, the implementation instructions.
- **Etc. materials (future):** whatever comes next, each in its own
  repository when the need actually arises. A model built around the
  template gets its own home; a tool gets its own home.

This repository is a **sibling** of the workbench, not a replacement
and not a cleanup of it. The workbench remains the evidence; this
repository distills it and makes it reusable. Neither swallows the
other.

## Honest status (read this before using the template)

**What the template is.** A 10×10 grid world with a periodic door
schedule; a hand-written numpy network (observations → 32 hidden
units → 5 action Q-values, no frameworks); three agent types built
on one shared learner (plain, one-step-memory, schedule-wrapped);
and a schedule model that turns observed door openings and closings
into time features (ticks since opening, ticks of opening
remaining). Every feature is named; nothing is buried in an opaque
representation. See `TEMPLATE/principles.md` for the why, and
`PAPER/study-paper.md` for the evidence.

**What has been established about it (on the grid task only).**
Schedule information helps: in the replication, the wrapped arm
reached 26/40 against plain 0/40 and memory 7/40. The same body of
work also establishes the template's limits, plainly: on the grid
task the agents **memorize locations rather than generalize** — a
novel door is not crossed without training on it, fine-tuning buys
partial acquisition at near-total forgetting of other worlds, and
no novel-door transfer was observed. See the paper's limitations
section; do not skip it.

**What is NOT established.** Generalization to novel doors, tasks,
or domains; language; any second domain built on the template.
"Universal" here is a **design intent with a reason** (simplicity +
explicitness + inspectability = liftability), **not a proven
result**. No second domain has been built on it yet. Future builds
around the template are what would test universality, and they are
future work, not claims made here. No reader may leave this README
believing more than the evidence supports.

## Provenance

Template code is taken from
[`VAG-gomi/time-based-mind-model`](https://github.com/VAG-gomi/time-based-mind-model)
at commit `5633e2d`, byte-identical, with no adaptations:

- `TEMPLATE/world.py`
- `TEMPLATE/nn/nnet.py`
- `TEMPLATE/nn/agent_nn.py`
- `TEMPLATE/nn/agent_mem.py`
- `TEMPLATE/nn/wrapper.py`
- `TEMPLATE/nn/agent_wrapped.py`
- `TEMPLATE/nn/test_nnet.py`
- `TEMPLATE/nn/test_wrapper.py`

Written fresh for this repository (not taken from the workbench):

- `TEMPLATE/demo.py` — the minimal runnable example (trains one
  wrapped agent on the default world, greedily evaluates it).
- `TEMPLATE/principles.md` — the methodology in prose.
- `PAPER/study-paper.md` — the study paper with proof pointers.
- `IMPLEMENTATION.md` — how to build around the template.
- This `README.md`.

No trust machinery is shipped as template code, because none is
part of the shipped substrate at the source commit: the only
"beta" terms in the substrate are Adam's `beta1`/`beta2`
optimizer terms, and one comment word ("trusted"). The canonical
trust design (β≡1.0) is described in the paper as a methodology
note with a proof pointer, not as template code.

## How to use it

1. Start with the template: clone this repository, run
   `python3 TEMPLATE/demo.py`, and confirm it trains and
   evaluates before changing anything.
2. Read the paper for why the template is shaped the way it is,
   and what it has and has not demonstrated.
3. Follow `IMPLEMENTATION.md` to build around it: define your
   world, choose named features, choose an agent type, train
   under the stated spec, evaluate trained worlds against
   held-out worlds with bars stated before running, and report
   reconciliations first, then numbers, then verdict.

## Layout

- `TEMPLATE/` — the reusable design: code, demo, principles.
- `PAPER/` — the study paper (distilled progress + proof).
- `IMPLEMENTATION.md` — standalone build instructions.
