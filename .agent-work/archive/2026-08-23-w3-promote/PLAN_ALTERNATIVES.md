# Plan Alternatives Brief — w3-promote

## The one thing being designed twice
How to sequence promoting bucket-2 `check: null` conditions (locator expressible, no new engine
mechanism) across the corpus's 8 checklist templates (65 null conditions total) into real
`command`/`artifact`/`git-change-policy` checks — per template, or by measured risk.

## Count and panel — a surfaced choice
N=2, not a 3-lens panel: this is a re-derivation of an already-panel-tested constraint space
(w2-basis ran N=3 on the same "convert to existing check kinds" question for one template and its
`artifact-conversion` leg is direct prior art for this wave's own approach), scaled to two axes
that actually differ for THIS run's new decision — ordering (per-template vs measure-first) — not
the underlying check-kind question w2-basis already triangulated. Untaken road: a third
"per-check-kind" constraint (group all `command`-kind promotions across every template into one
gate, all `artifact`-kind into another) was considered and rejected before dispatch — it has worse
locality than either candidate below with no compensating benefit, since check kind is already a
sub-classification within each condition's bucket-2 assessment, not an independent ordering axis.

## The constraints (one per agent)
- **template-sequential** (`.agent-work/w3-promote/plan-candidate-template-sequential.md`) — one
  gate per template, in file-ownership/priority order, each bundling assess+promote+red-proof+docs
  for that file before the next.
- **assess-then-promote-by-risk-tier**
  (`.agent-work/w3-promote/plan-candidate-assess-then-promote-by-risk-tier.md`) — decouple
  measurement (one consolidated pass, all 8 templates) from mutation (promote by risk tier:
  low-risk = check kind already live in that template, high-risk = first use or ambiguous locator).

## Compared on
Depth, locality, seam placement, testability — each candidate's own §Tradeoffs, both dispatched
blind to each other (parallel Agent-tool calls, no shared context).

## Framing block (presented ahead of convergence)
- **Dependencies held fixed for both**: `decision:no-new-check-kinds`, `decision:no-basis-backfill`,
  `decision:record-the-partition-per-condition`, `decision:blocking-where-adjudicated`,
  `decision:red-proof-each-promotion`; target only the 8 real checklist templates (65 null
  conditions, measured fresh, matches the launch order's ~65 extrapolation); never edit
  `checklist_engine.py`.
- **Illustrative sketch (NOT a proposal)**: "promote every condition that has ANY file path
  mentioned in its imperative." Offered only to prime thinking about why raw mention-detection
  overclaims — most mentioned paths back a judgment claim (`plan.c2`-shaped), not a real locator.

## Independent convergence — both candidates measured the same facts, differently ordered
Both independently confirmed the corpus-wide null count (65 across 8 templates) and both
independently found `tests/test_validate_spine.py` already exists with a corpus sweep — a material
correction to the launch order's framing that **"nobody calls validate_spine.py on the shipped
templates"**. Verified directly, fresh, this run:

```
$ grep -n "class TestShapeAcceptsEveryShippedTemplate\|class TestCorpusSweepFindings" tests/test_validate_spine.py
233:class TestShapeAcceptsEveryShippedTemplate:
687:class TestCorpusSweepFindings:
```

`TestShapeAcceptsEveryShippedTemplate::test_no_shape_faults` is **already blocking, zero-tolerance,
corpus-wide** on shape faults, parametrized over `vs.discover_checklist_templates(ROOT)` — a
function that **already correctly excludes** the 10 non-checklist "data payload" templates
(`FINDING`, `REPLAN_*`, etc.) that a naive `skills/*/templates/*.json` glob would false-positive
on (confirmed: `discover_checklist_templates` filters to `type in ("gated","survey")`, matching my
own fresh 11-template count exactly). `TestCorpusSweepFindings::test_measured_finding_totals` is
**already wired, but as an inverted floor** — it asserts `falsifiable-all-null >= 15` (not `== 0`):
its job is proving the *checker* still finds what it exists to find, not that the corpus is clean.
**This means my own promotions will make this exact test go RED** if they drop the corpus's
all-null-gate count below 15 — the floor's pinned numbers (15, 2, "measured 21 at authoring time")
must be updated in the same PR that promotes conditions, or the suite breaks on success. Neither
candidate's own text flags this consequence explicitly enough to skip restating it here: this is
the single most concrete, testable throughline connecting every template gate to `g9`/wiring-scope,
and it changes `decision:validate-spine-wiring-is-in-scope`'s question from "should we wire it" (it
is already partly wired) to "how much of the existing floor do we tighten, and do we update the
already-pinned counts truthfully."

## Cold critic findings & disposition
See `PLAN_CRITIC.md`. Summary of disposition below; full findings and reasoning live there.

## Output — recommendation (hybrid, not a menu)

**Winner: TEMPLATE-SEQUENTIAL as the backbone, with ONE gate borrowed from
assess-then-promote-by-risk-tier inserted first.**

Reasoning: this is explicitly the epic's **final wave**, and every prior wave in epic-569 has had
at least one relaunch-from-refresh-request (confirmed against this run's own trip at the `plan`
gate) — template-sequential's core property, that every gate boundary ships a complete,
independently-mergeable, revertible story for one file, is worth more here than early
divergence-detection, because a partially-completed run under this shape degrades gracefully (the
Admiral can accept g1-gN and defer the rest) where a partially-completed risk-tier run leaves
promotions scattered across files with no single file cleanly done. This directly matches
`decision:blocking-where-adjudicated`'s spirit (ship what is adjudicated, don't block everything on
the riskiest unresolved piece) and the launch order's own explicit sequencing hint (COMMANDER_SPINE
named as "your first targets").

But `assess-then-promote-by-risk-tier`'s `g1-consolidated-assessment` + `g2-divergence-check` gates
are cheap (read-only, no file touched) and directly implement
`decision:record-the-partition-per-condition`'s hard requirement — a materially different partition
on some other template is a stop-and-float, and template-sequential's own verdict admits it
discovers that late (possibly at g7/g8, several templates of committed work in). Grafting a
**lightweight version** of the measure-first gate at the front — record the bucket for all 65
conditions across all 8 templates in one pass, compare each template's fraction to 9/19, flag
material exceptions — costs one read-only gate and forecloses the exact risk
`decision:record-the-partition-per-condition` was written to catch, without adopting risk-tier's
weaker-locality promotion-by-tier structure for the actual edits.

**The converged gate sequence** (full detail in `execute.json`, authored next):
1. `g0-consolidated-bucket-survey` (grafted from risk-tier's g1+g2, read-only) — bucket every one
   of 65 conditions across all 8 templates, compare each template's bucket-2 fraction to 9/19
   (~47%), float any material exception. Also captures the `test_validate_spine.py` existing-floor
   finding above as a named fact this survey carries forward.
2. `g1-commander-spine` + `g2-red-proof-commander-spine` (template-sequential, as designed) —
   COMMANDER_SPINE first per the launch order's own naming.
3. `g3-execute-plan`, `g4-admiral-spine`, `g5-explorer-spine`, `g6-charter`,
   `g7-implementer-plan`, `g8-cartographer-and-scout` (template-sequential's priority order and
   gate bodies, largely as designed — re-verify each against g0's survey rather than re-deriving
   bucket assignments from scratch).
4. `g9-validate-spine-wiring` — corrected per the finding above: not "decide whether to wire," but
   "update the already-existing floor's pinned counts to this run's post-promotion measurement, and
   decide with the Admiral whether to additionally tighten to zero-tolerance for the 8
   lane-owned templates."
5. `g10-integrate` — commit, full suite, PR, RESULT.md.

Within each per-template gate, risk-tier's **tiering language** (a check kind already live in that
SAME template = ship blocking; first use of that kind in that template, or an ambiguous locator =
ship report-only with a named trigger, or demote to `check: null` if the kind has no real
report-only shape — e.g. `artifact`) is adopted as the **blocking-vs-report-only decision rule
inside each gate**, not as a separate corpus-wide partition gate. This keeps locality (one gate,
one file) while keeping risk-tier's genuinely more rigorous blocking/report-only discipline.

## Untaken-road record
- **Full risk-tier structure (promote-by-tier across all 8 files in two gates, g4/g5)** — not
  adopted: locality loss (a reviewer cannot audit "did CARTOGRAPHER's promotions land correctly"
  without filtering an 8-file diff by tier) outweighs its earlier divergence-detection, once a
  cheap `g0` survey gate captures that same detection at near-zero cost.
- **A third "per-check-kind" candidate** (group all `command`-kind promotions across templates,
  all `artifact`-kind separately) — rejected before dispatch, see "Count and panel" above.
- **Running a 3-lens critic panel** — not run; single critic, see Panel-vs-single record below.

## Panel-vs-single record
N=2 (not 3) for plan-alternatives, per "Count and panel" above — the underlying check-kind
question was already panel-tested (N=3) by w2-basis; this wave's genuinely new axis (ordering) is
adequately covered by two orthogonal candidates. Single critic (not a panel) for the cold-critic
step below: this is a converged synthesis of two already-thorough, already-grounded candidates
(not a first-draft proposal), so one adversarial cold read is proportionate — mirroring w2-basis's
own panel-vs-single reasoning for its cold-critic step.
