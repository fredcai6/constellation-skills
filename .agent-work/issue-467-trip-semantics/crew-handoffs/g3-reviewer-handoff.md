# Reviewer Handoff — g3-review

Issue #467 (epic #418), branch `epic-418/a2-467-trip-semantics`, worktree
`C:/Programs/constellation-skills-wt/epic418-a2-467`. Work only in this worktree.

## Gate
`g3` — DC4: per-gate context-headroom override, tighten-only, exercised exactly once.

## Survey State Location

Create your review survey checklist at
`.agent-work/issue-467-trip-semantics/g3-review/review.json` — under the issue workbench, never at
the worktree root.

**Note on your engine bundle:** the `constellation-reviewer` skill was re-installed from this repo
immediately before this dispatch, so its bundled engine is byte-identical to the repo engine and
**supports `amend` on surveys**. A previous reviewer on this run force-waived a survey postcondition
believing `amend` was refused. If you hit a survey postcondition carrying an unresolved placeholder,
**fill it properly through `amend`; do not force-waive.**

## What Was Implemented

A per-gate, tighten-only context-headroom override for the context governor's Trip bands, in four
parts, committed at **`f9925be6`**:

- **(a)** `gauge_reader.thresholds_for(model, headroom_tokens=0)` subtracts an absolute-token
  reserve from **both** the soft and hard caps before dividing by the window, clamped so an
  override can only TIGHTEN a threshold, never loosen it.
- **(b)** `checklist_engine._gate_headroom_tokens(cl, gate)` — a SINGLE resolver reading
  `tasks.<gate>.context_headroom_tokens` and nothing else. Missing, malformed, or negative resolves
  to 0. No checklist-config tier was shipped.
- **(c)** That same resolver feeds BOTH threshold call sites: `_trip_advisory` (the number the agent
  is SHOWN) and `_trip_hard_band_reading` (the number it is JUDGED against, which backs both g2's
  begin-work guard and g2's no-silent-close rule).
- **(d)** Exactly one gate in the shipped templates carries an override: the commander spine's
  `execute` gate, `context_headroom_tokens: 30000`.

## How to Inspect the Diff

The gate's source change is **committed**, not sitting in the working tree:

```
git show f9925be6 -- scripts tests skills
git diff f9925be6^..f9925be6 -- scripts tests skills
```

`git status --porcelain` will show a few `.agent-work/` files modified by the Commander's own engine
driving (`execute.json`, its journal, `spine.json`, `crew-runs.json`) plus an untracked
`evidence/tc1-amend-delta.json`. **Those are mine, not the implementer's — they are not part of your
review target.** Do NOT use `git diff main...HEAD`: it shows unrelated merged-PR divergence.

The implementer's own account is at
`.agent-work/issue-467-trip-semantics/crew-handoffs/g3-implementer-result.md`, and its mutation log
at `.agent-work/issue-467-trip-semantics/g3-mutation-log.md`. Read them, then verify against the
code — they are claims, not evidence.

## Task Statement

The frozen `g3-implement` imperative the implementer was given:

> Ship the per-gate override: (a) `gauge_reader.thresholds_for(model, headroom_tokens=0)` subtracts
> an absolute-token reserve from BOTH caps before dividing by the window, clamped at 0 so an
> override can only TIGHTEN, never loosen; (b) `checklist_engine` resolves the reserve with a SINGLE
> reader from `tasks.<gate>.context_headroom_tokens` only — there is no checklist-config tier,
> because it would have zero users and one adapter is a hypothetical seam; a missing, malformed or
> negative value resolves to 0; (c) the SAME resolver feeds both the advisory and the guard; (d)
> exactly one gate carries an override.

The full handoff it worked from is at
`.agent-work/issue-467-trip-semantics/crew-handoffs/g3-implementer-handoff.md`.

## Close Criteria

Each becomes a review check. **Re-run at least two of the mutations yourself** — do not take the
mutation log on report.

1. **Tighten-only is genuinely unreachable to violate.** *Try to loosen a threshold through the
   override and show that you cannot.* A test asserting the clamp's happy path is not this. The
   implementer claims two independent layers (a validating resolver and two clamps in
   `thresholds_for`). Attack both.
2. **The malformed/negative test carries a POSITIVE assertion through the same resolver in the same
   test**, so it cannot pass with the mechanism dead-coded. This is the load-bearing anti-vacuity
   property of this gate: twelve negative assertions all pass with the resolver returning a constant
   0. Confirm the positive control is what catches it (the implementer's M5 claims exactly this).
3. **The neighbour-isolation test asserts BOTH sides by name** — the overridden gate's behaviour
   changes AND a named neighbour's does not, at the same fill, on the same model, in the same test.
   "It trips the overridden gate" alone does not satisfy DC4.
4. **`_PROFILES` is untouched.** `scripts/gauge_reader.py` — the graded production default table is
   out of scope and must be byte-identical to its pre-change state.
5. **There is no checklist-config tier.** The key resolves from `tasks.<gate>` only; parking it at
   the checklist root or in `config` must be ignored.
6. **The advisory and the guard read the same resolved number** — demonstrated, not asserted in
   prose. Shown and judged must not be able to diverge.
7. **Exactly one gate in the shipped templates carries an override.** Not zero (the mechanism would
   be unexercised), not many (that invents ungraded placeholders — the failure DC4 exists to guard).
8. **Every mutation in the log turns its NAMED test red.** Re-run at least two yourself and paste
   the output. Where the log declares a mutant EQUIVALENT (M15), judge that declaration: is it
   honest, or is it covering a genuinely unkilled branch?
9. **The suite is green and any delta is explained.** Stated post-change: 1832 passed, 2 skipped,
   806 subtests. Stated pre-change baseline: 1815 passed, 2 skipped, 683 subtests, measured at
   `d376b786`. The implementer reports the passed-count delta (+17) as exact and fully attributed,
   and reports the **subtest count as off by one** (it measured 682, not 683, with its diff
   stashed) — flagged as a pre-existing tree property, not this diff. Confirm the +17 attribution
   yourself; the ±1 subtest is a known triage candidate (`tc3`) and is **not** a blocker.

## The two claims you are asked to ATTACK, not confirm

1. **`claim:dc4-neighbour-isolation`** — that an override tightens its own gate and leaves every
   other gate exactly as it was. The strongest form the implementer shipped is a byte-identical
   advisory assertion on the neighbour. Try to find a surface where the reserve leaks.
2. **`constraint:tighten-only`** — that no authored value, however hostile, can raise a threshold.
   The implementer swept `-1`, `-1e308`, `-inf`, `nan`, `True`, `-0.0`. Find a value or a path it
   did not.

## Allowed Scope (what the implementation was permitted to touch)

- `scripts/gauge_reader.py` — `thresholds_for` and its docstring.
- `scripts/checklist_engine.py` — the Trip section's threshold call sites, and the new resolver.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — the `execute` gate only.
- `tests/test_gauge_reader.py`, `tests/test_checklist_engine.py`.
- `tests/test_init_work_area.py`, `tests/test_install_constellation.py` — pre-authorized for
  minimal reconciliation only. The implementer reports it did not need to touch either.
- `.agent-work/issue-467-trip-semantics/g3-mutation-log.md` and its own crew plan.

Anything outside this list appearing in `f9925be6`'s source diff is a scope violation — flag it.

## Specific Exclusions (flag if touched)

- `_PROFILES` and `_DEFAULT_PROFILE` in `scripts/gauge_reader.py`.
- Any checklist-config tier for the override key.
- An override authored on more than one gate.
- Threshold arithmetic computed inside the engine (the engine passes a token count to
  `gauge_reader` and reads fractions back; it computes no thresholds itself).
- Anything g2 shipped: `TRIP_HARD_GUARDED_VERBS`, the no-silent-close rule, the advisory wording.
  g2 is closed and independently reviewed. If you believe g2 is wrong, that is an out-of-scope
  observation for me to carry up, **not** a BLOCK on this gate.

## Constraints the Implementation Must Respect

- `constraint:no-threshold-values` — the engine does not COMPUTE thresholds.
- `constraint:tighten-only` — no override may raise a threshold.
- `constraint:global-default-untouched` — `_PROFILES` is the production default and is out of scope.

## Map Anchors (inbound)

Inherited from `g3-implement`; review against the same anchors, with particular weight on
`constraint:tighten-only` and `claim:dc4-neighbour-isolation`.

- **Structural:** `scripts/gauge_reader.py` — `thresholds_for` (:124-165), `_PROFILES` (:76),
  `_DEFAULT_PROFILE` (:98). `scripts/checklist_engine.py` — `_gate_headroom_tokens` (:1277),
  `_trip_advisory` (:1485), `_trip_hard_band_reading` (:1520-1543), `_trip_hard_gate` (:1565),
  `dispatch`'s advance (:2857). `skills/commander/templates/COMMANDER_SPINE.template.json` — the
  `execute` gate.
- **Capability:** Trip thresholds — were global-per-model, now global-per-model tightened by an
  optional per-gate absolute-token reserve.
- **Constraints/assumptions:** the three above.
- **Decision anchors:**
  - `decision:gate-headroom-absolute-tokens` — the override is an absolute-token reserve, not a fill
    fraction, because context-rot degradation tracks absolute token count.
    `@grade: settled/measured · leans g3-implement,g3-review`
  - `decision:headroom-not-cap` — the override states what the GATE needs, so it survives a change
    to the production default. `@grade: settled/measured · leans g3-implement`
  - `decision:no-config-tier` — gate-level only. `@grade: settled/measured · leans g3-implement`
  - `decision:execute-gate-reserve-value` — **30000**, authored by the implementer.
    `@grade: guess · leans g3-implement · settle: read fill_fraction across completed commander runs
    at the moment execute was started`

  The first three are `settled/measured` — **not yours to revise**; if you find a contradiction,
  stop and return it as a decision candidate rather than editing around it. The fourth is a
  `guess`. **Its authored settle experiment is NOT RUNNABLE and this is already established** —
  `gauge.json` keeps only the latest reading, and the per-gate context manifests carry no fill
  value. Both the implementer and two Commanders confirmed this independently. **Do not BLOCK on
  the reserve value being a guess, and do not re-derive the un-runnability.** A cheaper replacement
  experiment (log `(gate, fill_fraction)` at each gate boundary) is already routed to the Admiral.
  What IS in your scope: whether the reasoning is honestly presented AS a guess and recorded beside
  the value where a later run can revise it.
- **Evidence expectations:** `claim:dc4-neighbour-isolation` — asserted on both sides by name, at
  one fill, on one model.
- **Map confidence flags:** the launch order's role-blindness reading (crews trip at 17-21%, the
  Admiral ran to 44% untripped) is **CONFOUNDED and formally RETRACTED by the Admiral**. An
  orchestrator holding several spines under one key writes no reading at all. The implementer states
  it used this for nothing. **Do not act on it, and do not accept it as supporting evidence for
  anything.**

## Evidence Produced

From the `IMPLEMENTER_RESULT` — treat as claims to verify, and paste your own re-runs:

```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
  -> 1832 passed, 2 skipped, 806 subtests passed

FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py -k 'headroom or override'
  -> 20 passed, 413 deselected, 125 subtests passed

FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py tests/test_init_work_area.py tests/test_install_constellation.py
  -> 571 passed, 535 subtests passed
```

Mutation log: 16 mutations, 15 killed by a named test, 1 declared equivalent (M15).

## The standing trap on this run — read it before you write a single check

**#431 is an instruction-conformance defect, not a mechanical deadlock.** The pre-fix engine
*permits* the advance while telling the agent not to run it. A test worded *"the advance is no
longer blocked"* verifies something that was never blocked and **passes in both worlds**. Verify on
**what the agent is TOLD**, and on **whether anyone BEGAN work over the line**.

This gate's own version of the same trap: **a negative-only test cannot fail.** It passes with the
mechanism dead-coded. That is not hypothetical here — the implementer proved it empirically (M5).
Check criteria 1, 2 and 3 with that in mind: for each, ask *"what would this test do if the
mechanism were deleted?"*

The g2 reviewer set the standard on this run by rebuilding the pre-change engine from
`git show 38f0b448^` and running the new tests against it, rather than trusting saved output files.
Hold that standard where it applies.

## Suggested Model Tier

**Stronger (Opus).** Named reason: adversarial review, where the job is to attack a claim rather
than build to a spec — the Admiral's explicit carve-out from the standing Sonnet default. This
gate's central risk is a test that passes for the wrong reason, which is exactly what a confirming
read misses.

## Stop Conditions

Stop and return `BLOCK` if: the diff cannot be accessed, evidence is absent or unverifiable, or a
policy decision is required before a verdict is possible.

**Do NOT modify `scripts/` or `tests/` yourself.** You verify; rework is the implementer's. If you
find a defect, return `BLOCK` with the reproduction.

## Return Format

Return REVIEW_RESULT. **Your verdict must be exactly `APPROVE` or `BLOCK`**, on the **first line**
of your result, with the reasoning under it. No other verdict vocabulary — the engine matches on
that literal string, and a gate whose reviewer invents a third word cannot close.

`APPROVE` means **zero blocking findings**. Non-blocking findings are welcome and expected alongside
an APPROVE; report them, classified. If you have even one blocking finding, the verdict is `BLOCK`.

Also state, on its own line, **`blocking_findings: <N>`** — I carry it into the engine payload for
audit.

Include: per-check findings against the nine close criteria (each classified blocking /
non-blocking), your independent re-runs with pasted output, the two claims you were asked to attack,
the at-least-two mutations you re-ran yourself, blockers, anything you could not verify and why,
out-of-scope observations, and workflow feedback (what in this handoff or the workflow made the
review harder than it needed to be).

Write your result to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g3-reviewer-result.md`.

**Deliver your REVIEW_RESULT via `SendMessage` to `commander-w4-467-f` before ending your turn.**
