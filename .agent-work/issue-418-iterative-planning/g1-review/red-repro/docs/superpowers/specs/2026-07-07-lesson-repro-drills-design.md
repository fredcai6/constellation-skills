# Reproduction drills for applied lessons — design

Date: 2026-07-07
Issue: #55 (TDD-for-doctrine)
Status: ratified (Admiral wave-2/3 checkpoint; human ratifies at the epic return boundary)

## Problem

When a lesson is *applied* as a prose edit to a `SKILL.md` or template, nothing
verifies the edit actually changes agent behavior. Dead doctrine reads as progress
until the failure recurs. Dogfood evidence: the PowerShell `gh ... --body` hazard
recurred across three `story_time` epics *after* it was written down. An `apply` op
today deletes the paid lesson on the mere presence of an `applied_evidence` string —
a citation that the edit was made, not evidence that it works.

This is the process-documentation analogue of shipping a bugfix with no regression
test. Superpowers' `writing-skills` doctrine already frames the cure: TDD for process
docs — baseline an agent *without* the fix under pressure, capture the failure, apply
the minimal fix, re-test that the failure no longer fires.

## Ratified knobs

Two knobs were settled at the wave-2/3 checkpoint:

- **Who runs drills: the fresh-context `lessons-auditor`**, at Admiral closeout /
  Commander feedback — *not* the commander who made the edit. Independence: the editor
  must not grade its own fix. This mirrors the existing separation where the auditor
  nominates and never applies.
- **When required: on recurrence**, anchored to the *existing* ripeness rule
  (`ripe_lessons()` / the threshold logic in `apply_lessons_delta.py`): a
  non-constellation lesson is ripe at `confirmed >= apply-confirmed` (default 3) with a
  `target`; a constellation lesson at `recurrences >= apply-recurrences` (default 1).
  Constellation lessons cannot be applied in-project (they export upstream), so the
  drill gate only ever sees non-constellation applies.

**Rule:** applying a **ripe** lesson whose `target` is a **doctrine artifact**
(a skill / template / prose-doctrine file) requires a **reproduction drill** referenced
in the apply op. Non-ripe applies and **code-targeted** fixes are exempt — a code fix
sits at form-ladder rung 1, where a test suite already proves the behavior.

## Doctrine-vs-code taxonomy (mechanical)

The check must distinguish a doctrine target from a code target with a pure path rule —
the script never inspects file contents or judges quality. A target is **doctrine** when
its path:

- ends in `.md` (a `SKILL.md`, `_shared/*.md`, `docs/**` prose doctrine), or
- contains `.template.` (a spine / checklist / handoff template — `*.template.json`,
  `*.template.md` — which is doctrine even when its extension is `.json`, because an
  agent reads it and no unit test grades the prose change).

Everything else (`.py`, `.js`, …) is a **code target** and is exempt: its behavioral
proof is its test suite, not an agent reading it.

Verified clean against the real corpus of `target` strings: `skills/_shared/windows.md`,
`skills/commander/SKILL.md`, `docs/agents/CREW_CONTEXT.md` (doctrine);
`skills/commander/templates/COMMANDER_SPINE.template.json` (doctrine, via `.template.`);
`scripts/run_crew.py`, `tests/test_*.py` (code, exempt). No target in the corpus is
ambiguous under this rule, so the taxonomy does not need to be escalated.

## Drill-reference carrier

The drill reference rides on the apply op as a **dedicated `drill` field**, checked for
presence only (non-empty string). This reconciles the launch order's phrasing ("a drill
reference in `applied_evidence`"): the drill is a *component* of the apply's evidence
bundle, and a dedicated field is the cleanest, most auditable field-presence check —
it mirrors the existing dedicated op fields (`target`, `reason`, `grounding`,
`applied_evidence`) rather than requiring the script to substring-scan a prose string.
The field's value is the committed drill-record path, e.g.
`docs/superpowers/drills/gh-body-multiline-windows.md`.

## Drill methodology

A drill is the lesson's failure scenario run against a **throwaway** subagent twice:

- **Before-arm** — arm the subagent with the *old* doctrine text (the state that let the
  failure recur) and the failure scenario under its real combined pressures; observe the
  failure reproduce and **capture it verbatim**.
- **After-arm** — arm a fresh subagent with the *edited* doctrine text and the same
  scenario; observe the failure no longer fire.

Keep it lightweight: one scenario, combined pressures where they are load-bearing,
verbatim capture in the before-arm. The auditor (not the editor) writes the drill record.

**Decontaminate the scenario.** State the drill scenario positively / by-outcome; never
pre-itemize or alarm-flag the failure trigger — a scenario that names what the doctrine is
supposed to make the author notice makes the *before*-arm pass too, collapsing the variable
under test and proving nothing. Describe the roles/mission the subagent occupies, not the
divergent clauses or harness/fixtures the fix is meant to surface; the failure trigger must
stay latent for the before-arm to have a chance to fail on its own.
The scenario + record are committed under `docs/superpowers/drills/<lesson-id>.md` so a
corpus accumulates (future evals seed).

**Honest-null clause.** A before-arm that will not reproduce is itself a complete,
reportable finding — it says the lesson may already be internalized, mis-scoped, or that
the pressure was wrong. Report what the null says; do not force a reproduction.

## Mechanical validation

`apply_lessons_delta.py` enforces the field-presence check in the `apply` branch of
`apply_delta` (where the playbook is in hand, so ripeness is computable — `validate_delta`
sees only the delta and cannot judge ripeness). When the applied lesson is ripe *and* its
effective target is a doctrine artifact, a missing/empty `drill` field refuses the whole
delta (all-or-nothing) with a message naming the requirement. Field-presence only: the
script never opens the drill record or judges its quality — same doctrine as the engine.

Backward compatible: deltas without applies, applies of non-ripe lessons, and applies of
code-targeted lessons are all unaffected. `verify_lessons_applied.py` does **not** change —
it already forces apply-or-defer over ripe lessons; the drill rides inside the apply op's
evidence, so no new gate is needed.

## Out of scope

The ripeness thresholds, `verify_lessons_applied.py`, any quality judgment of a drill, and
the in-flight-fenced spine/template files (#48/#52/#53/#54).
