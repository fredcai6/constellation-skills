# Reviewer Handoff

## Gate
g1 (g1-review)

## Survey State Location
Create your review survey checklist at `.agent-work/w2-basis/g1-review/review.json`.

## What Was Implemented
A new, report-only `basis` sibling field on `Condition` in `scripts/checklist_engine.py`, so a `check: null` postcondition can declare a resolvable locator (`file` or `evidence_ref`) at plan-authoring time. Three parts: (1) `render_human` emits an indented `basis:` sub-line under an open condition only when populated and non-abstain; (2) `attest()` gains a new guard that resolves the locator and **always** attaches a `basis-check` evidence item (pass or fail), never blocking; (3) `docs/CHECKLIST_SCHEMA.md` documents the new field, the two locator kinds, and the always-attached evidence. Full implementer account: `.agent-work/w2-basis/crew-handoffs/g1-implementer-result.md`.

## How to Inspect the Diff
Uncommitted working tree in this same worktree (`/home/tommy/projects/569-w2-basis`) — use `git status --porcelain` then `git diff` (untracked-safe; nothing here is untracked, but follow the convention). Expect exactly three files: `scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`, `tests/test_checklist_engine.py`.

## Task Statement
Add `basis` (locator_kind: file/evidence_ref/abstain) as an optional sibling field of `check` on `Condition`. Render it (populated-only) on `current`/`render_human`. At `attest`, when a `check: null` condition carries a populated non-abstain `basis`, resolve the locator and always attach a `basis-check` evidence item recording the outcome — report-only, never raise. No existing shipped template carries this field yet, so no observable behavior change for any condition without one.

## Close Criteria
- `basis` field threads through as a plain dict sibling of `check`; absent/abstain = provably unchanged legacy `attest` behavior (byte-identical `satisfied_by`, no evidence attached).
- `render_human` emits the `basis:` sub-line only when `basis` is populated and `locator_kind != "abstain"`.
- `attest()`'s new guard never raises on an unresolved locator (report-only, confirmed — this is genuinely new attest code, so `ruling-widening-live-refusal-report-only` requires it not block).
- A `basis-check` evidence item is attached on **every** attest of a basis-bearing, non-abstain condition, pass or fail, with payload `{locator_kind, locator, resolved, problem}`.
- Only `file` and `evidence_ref` locator kinds exist — confirm `state_field`/`command` were NOT implemented anywhere (grep for those strings as check.kind or locator_kind literals; they should appear only in prose/comments referencing the untaken roads, never as executable dispatch branches).
- INV-2 purity honored: the render path (`_condition_view`/`render_human`/`state()`) reads only the stored `basis` dict — never calls `_resolve_basis_locator` or does any filesystem/state probing. Resolution happens exclusively inside `attest()`.
- `GoldenOutputBriefing` and `TemplateOnlyFieldAllowlist` test classes stay green — proof that no existing shipped template's `current` output or field-shape assumptions changed.
- TDD evidence is real: each of the two slices (render, attest guard) was observed failing before implementation and passing after — verify the pasted red/green transcripts in the IMPLEMENTER_RESULT are internally consistent (test names in the failure list match test names in the passing list; failure messages are the kind you'd expect from the described missing code, e.g. `KeyError: 'basis'`, `TypeError: unexpected keyword argument 'base_dir'`).
- Full `tests/test_checklist_engine.py` suite passes (implementer claims 511 passed, 145 subtests — reproduce this yourself, don't take the number on faith).
- `docs/CHECKLIST_SCHEMA.md` documents `basis` in the Condition table and `basis-check` in the Evidence type/payload documentation.

## Allowed Scope
`scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`, `tests/test_checklist_engine.py` — nothing else.

## Specific Exclusions
- `skills/commander/templates/COMMANDER_SPINE.template.json` or any other shipped template (g2's scope, not this gate's).
- `scripts/generate_spine.py`, `specs/` (whole-epic exclusion).
- `checklist_engine.py`'s `waive()`, forced claim/release, `consolidate --override-reason`, `trip_ledger` code (w2-ledger lane fence — flag if touched, but this is a real BLOCK-worthy finding if it happened, not merely a note, since it risks colliding with a sibling lane's in-flight evidence).

## Constraints the Implementation Must Respect
- Report-only, unconditionally — no config/flag toggles the new guard to blocking.
- Populated-only rendering (no output for absent/abstain basis).
- Two locator kinds only.
- `_resolve_basis_locator` should be pure for `evidence_ref` (no side effects, reads `cl` only); `file` resolution touches the filesystem, isolated to that function.

## Map Anchors (inbound)
- **Structural:** `scripts/checklist_engine.py:render_human` (~2679-2749), `scripts/checklist_engine.py:attest` (~3404-3472) — confirm the implementer's actual line numbers in the diff, which may have shifted from these mission-frame-authored estimates.
- **Constraints/assumptions:** `ruling-decorative-basis-is-a-failure` (authored+rendered+required-report-only, together) | `ruling-widening-live-refusal-report-only` (new attest code, must be report-only) | INV-2 purity (`docs/CHECKLIST_SCHEMA.md`, render path never probes).
- **Decision anchors:** locator-kind vocabulary narrowed to `file`/`evidence_ref` only, ratified in `.agent-work/w2-basis/PLAN_ALTERNATIVES.md`.
  `@grade: settled/human — not open for re-litigation at review time; flag as a decision candidate only if the implementation contradicts it, don't relitigate the choice itself`
- **Evidence expectations:** `.agent-work/w2-basis/PLAN_CRITIC.md` findings 5 (promotion trigger must be auditable — the always-attached `basis-check` evidence is the mechanism; confirm it really is unconditional) and 6 (the field's honest value is rollout safety, not expressiveness — nothing to verify here beyond confirming the mechanism matches what was designed).

## Evidence Produced
Full IMPLEMENTER_RESULT at `.agent-work/w2-basis/crew-handoffs/g1-implementer-result.md`: pytest run (511 passed, 145 subtests), red/green transcripts for both slices, quoted `basis-check` payload examples, wiring grep (1 production call site for `_resolve_basis_locator`, confirmed no orphan symbol), diff-stat (3 files, 408 insertions/5 deletions). This gate's target postcondition for your verdict is `g1-integrate.c2` (reviewer verdict = APPROVE) in `.agent-work/w2-basis/execute.json`.

## Suggested Model Tier
stronger — reason: verifying an engine-purity invariant (INV-2) and a never-raise guarantee across a new code path needs careful adversarial reading, not just running the tests and trusting green.

## Stop Conditions
Return BLOCK if: the diff touches any excluded file, `state_field`/`command` locator kinds are implemented anywhere, the render path probes live state, the attest guard raises under any condition, the pytest suite does not actually reproduce the claimed pass count, or the red/green TDD transcripts don't hold up under inspection.

## Return Format
Return REVIEW_RESULT to `.agent-work/w2-basis/crew-handoffs/g1-reviewer-result.md` before ending your turn.
