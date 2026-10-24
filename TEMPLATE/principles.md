# Principles — the methodology in prose

The "why" behind the code in this directory. The code is the design;
this file states the reasons the design is shaped that way. Where this
file and the code disagree, the code is what runs — report the
disagreement rather than silently following either one.

## 1. Time as experience, not handed order

The founding goal, in the owner's words: *don't give the model order,
let it be thought, get learned, then act by itself.* The model is
never told the schedule. It observes a door opening and closing, tick
by tick, and builds its own estimate of the period and the open
length from those observations alone. Time enters the agent as
experience — features derived from what it has seen — never as a
handed clock, a handed phase, or a handed decision.

That is why the wrapped agent has deliberately **no "safe to cross"
bit**. Handing it the decision the work is testing would make the
result meaningless. The agent must learn the crossing margin from
reward: entering on one tick and exiting on the next needs both ticks
open, and the penalty for being caught in the door teaches exactly
that.

## 2. Substrate before occupants

Build the inspectable world first; capabilities grow on it rather
than being swapped in. The grid world, the network, and the agents
are the foundation layer of the house, not the finished rooms. A
later language capability, if it comes, grows out of this same
lineage — the model grows up into language — rather than arriving
as a ready-made guest model bolted on from outside. Nothing in this
template assumes an occupant more capable than the substrate can
support.

## 3. Small and explicit

Every feature is named, and nothing is buried in an opaque
representation:

- **Position:** a one-hot over the 10×10 grid (100 inputs).
- **Door bit:** 1.0 if the door is open now, else 0.0.
- **Previous door bit** (memory agent only): the door bit of the
  previous tick — one bit of history, enough to detect a transition,
  carrying no schedule model.
- **Schedule features** (wrapped agent only): cycle phase
  (ticks since opening, scaled by the period), opening remaining
  (ticks of opening left, scaled by the open length), and a known
  flag that disambiguates 0.0 = "just opened / 0 left" from
  0.0 = "unknown".

This explicitness is what makes the design liftable. A massive
black-box model cannot be a template, because there is nothing
visible to lift. This one can, because every part is visible and
re-derivable: the world, the network, the features, the schedule
idea, the training loop. If a feature cannot be named, it does not
go in.

## 4. Schedule-as-experience

The wrapper idea, in one sentence: time structure enters as input
features, not as handed order. The `ScheduleModel` consumes only
`(tick, door_open)` observations — never position, reward, actions,
or any episode counter — and maintains an estimate of the door's
periodic schedule:

- **Period:** the most recent *clean* opening-to-opening gap.
- **Open length:** the most recent *clean* opening-to-closing span.
- **Clean** means observed without gaps or episode boundaries, so a
  missed opening across an episode boundary can never become a wrong
  period: a dirty gap is simply not trusted.
- **Contradictions** (an observation that disagrees with the model's
  prediction) drop the stale events and re-estimate from recent
  events; until new transitions arrive, the estimates are honestly
  `None` rather than wrong.
- **Partial knowledge:** as soon as the open length and a cleanly
  observed opening are known, the remaining-ticks feature is exact
  without waiting for two openings — the agent becomes actionable
  early.

This is a **feature wrapper first**: the schedule enters the
network's inputs, and the network learns what to do with it. A
veto/shield variant — where the schedule model blocks unsafe
actions directly — is a later design, not part of this template.
And one boundary to respect when adapting: the wrapped encoder's
feature scales (20.0 for phase, 10.0 for open remaining) are fixed
to the 20/10 training schedule. They keep the time inputs in
[0, 1], commensurate with the one-hot and door inputs. On a
different schedule, re-derive the scales — do not silently carry
20.0/10.0 over.

## 5. Evaluation discipline (summary)

The full discipline is in `IMPLEMENTATION.md`. In brief, because
this project learned each rule the hard way:

- **Greedy AND noisy evaluation.** A greedy-only test can hide a
  frozen failure that noise partly unlocks; a noisy-only test can
  hide that the policy itself is broken. Run both.
- **Trained worlds vs held-out worlds kept apart from the start.**
  A held-out world the training ever touched is not held out.
- **Bars stated BEFORE running, and frozen.** Commit the bar and
  the rule before results exist; never move them after.
- **Verdicts from frozen rules, never from impressions.** If the
  pooled number misses the bar, the verdict is what the rule says
  — including UNINTERPRETABLE and NEITHER, which are answers, not
  failures to answer.
- **Reconciliations first.** Record completeness, duplicates,
  determinism checks — then numbers, then verdict.
- **Never pre-claim verification.** The verifier writes the verdict
  section. A draft that claims its own verification is corrupt by
  construction.

## 6. What this template is not

- Not a trained model. No weights are shipped as the product;
  weights are reproductions of training. The design is the product.
- Not a claim of generality. Universality here is design intent
  plus its reason (small, explicit, inspectable — see the paper's
  argument), not a demonstrated result. No second domain has been
  built on it yet.
- Not a trust system. The canonical trust design (β≡1.0) belongs
  to the learning machinery's history and is described in the paper
  as a methodology note with a proof pointer. It is not template
  code, because it is not part of the shipped substrate at the
  source commit.
