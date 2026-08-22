# Reviewer Handoff

## Gate
g3-implement (work-id: w2-ledger) — reviewing attempt 2's result (attempt 1 landed PARTS A-D and
correctly flagged a real gap as an out-of-scope observation; attempt 2 adds PART E closing it).

## Survey State Location
`.agent-work/w2-ledger/g3-implement-review/review.json`

## What Was Implemented
PART A: `override_summary(cl)` — pure counts-by-kind + id list, reading only `_override_entries`.
PART B: `"overrides"` added to `apply_episode_delta.py`'s `MECHANICAL_ALL_FIELDS` (dict-shaped, not
scalar) with a shape check in `_validate_create`. PART C: `episode_capture.py`'s `mechanical_fields()`
sets `overrides` (absence-is-meaningful) via `override_summary`. PART D: `spine_lifecycle.py`'s
`finish_work` attaches `overrides` to all four return points (verify/advance-release/archive/success).
PART E (attempt 2, rework): the `Episode` dataclass gained an `overrides` dict field;
`render_episode`/`parse_episode` round-trip it (one compact-JSON line, present only when non-empty);
`_apply_create` wires `mech.get("overrides")` through — closing the gap where PART B validated the
field but `_apply_create` silently dropped it before persistence, which attempt 1 itself flagged.

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/569-w2-ledger` (branch `epic-569/w2-ledger`), on
top of g1 (`2895dc8b`) and g2 (`87ea0655`), already committed. `git status --porcelain` then
`git diff -- scripts/checklist_engine.py scripts/apply_episode_delta.py scripts/episode_capture.py scripts/spine_lifecycle.py tests/ map/INDEX.md`.

## Task Statement
Make closeout visibly render the override ledger (#504) — both the immediate `finish_work` return
and the durable persisted episode record — without breaking existing episode-creation or closeout
call sites.

## Close Criteria
- `override_summary(cl)` exists, pure (reads only `_override_entries`), returns
  `{"trip", "force-claim", "force-release", "waive", "waive_authority_mismatch", "ids"}`.
- `"overrides"` in `MECHANICAL_ALL_FIELDS` (not `MECHANICAL_SCALAR_FIELDS`); `_validate_create` has
  a dict-shape check for it.
- **Load-bearing round-trip test** (PLAN_CRITIC.md Finding 1's exact original gap): a fixture whose
  `mechanical_fields()` output (non-empty `overrides`) is round-tripped through
  `apply_episode_delta.py`'s ACTUAL `create`-op validation path does not raise. Read this test in
  full — confirm it drives the real validator, not a mock.
- A fixture with empty/absent `override_ledger` produces `mechanical_fields()` output with NO
  `"overrides"` key. `REQUIRED_MECHANICAL_FIELDS` unchanged.
- `finish_work`'s `overrides` computed via `override_summary`/`_override_entries`, NOT raw
  `trip_ledger`/`outcome` reads — verify with a fixture using non-trip kinds (no `outcome` field).
- All FOUR `finish_work` return points carry `overrides` — read each of the four dedicated tests,
  confirm each actually drives the named return path (don't assume from the test name alone).
- **PART E, the rework's own close criteria:** `Episode.overrides` field exists and is dict-typed
  with a safe default; `render_episode` emits the line only when non-empty; `parse_episode` recovers
  it; `_apply_create` wires it through. The file's own documented invariant
  (`render_episode(parse_episode(text)) == text`) holds for BOTH the overrides-present and
  overrides-absent cases — read both round-trip tests in full and confirm they actually assert
  this exact equality, not just that parsing doesn't crash. A `create` op carrying
  `mechanical.overrides` must produce a persisted `.md` file whose text contains the rendered line —
  read `test_create_op_with_overrides_persists_rendered_line` and confirm it reads the actual
  written file from disk (not an in-memory `Episode` object only).
- Full repo suite green: `python -m pytest -q` — confirm the pass count is at/above 3660 passed, 6
  skipped (this gate's own claimed baseline-plus-additions), run it yourself, do not trust the
  pasted count.
- `map/INDEX.md` is fresh (no stale-entity failures in `test_code_map.py`).

## Allowed Scope
`scripts/checklist_engine.py` (`override_summary` only); `scripts/apply_episode_delta.py`
(`MECHANICAL_ALL_FIELDS`, `_validate_create`, `Episode` dataclass, `render_episode`,
`parse_episode`, `_apply_create` only — confirm no other function in this large file changed, e.g.
amend-assertion/retirement/consolidation logic must show zero diff); `scripts/episode_capture.py`
(`mechanical_fields()` only); `scripts/spine_lifecycle.py` (`finish_work` only); test files;
`map/INDEX.md` (build artifact).

## Specific Exclusions
Flag as BLOCK if touched: anything landed in g1/g2 (`_override_entries`, `_append_override_entry`,
`waive()`, `dispatch()`'s claim/release/waive branches); `REQUIRED_MECHANICAL_FIELDS`;
`close_work`/`open_pr`'s bodies beyond `finish_work`'s own return dict; any part of
`apply_episode_delta.py` outside the five named spots (amend-assertion, retirement, consolidation,
etc.).

## Constraints the Implementation Must Respect
- `overrides` absence-is-meaningful throughout (no `"overrides": {}` or `"overrides": null` written
  when there is nothing to report — the key itself must be absent).
- The `Episode` dataclass field-ordering must respect Python's no-default-before-non-default rule
  (attempt 2 placed `overrides` after `agent_supplied` rather than the handoff's literal suggested
  position — confirm this is a legitimate constraint, not a corner cut, by trying to construct the
  dataclass in the order the original handoff suggested and confirming it would actually fail).

## Map Anchors (inbound)
- **Structural:** `struct:scripts/episode_capture.py#mechanical_fields, function`;
  `struct:scripts/apply_episode_delta.py#_validate_create, function`;
  `struct:scripts/apply_episode_delta.py#Episode, class` (new field);
  `struct:scripts/apply_episode_delta.py#render_episode, function`;
  `struct:scripts/apply_episode_delta.py#parse_episode, function`;
  `struct:scripts/apply_episode_delta.py#_apply_create, function`;
  `struct:scripts/spine_lifecycle.py#finish_work, function`.
- **Capability:** `capability:closeout-episode-capture`; `capability:closeout-finish-work`.
- **Constraints/assumptions:** `constraint:no-unwired-checker`;
  `constraint:mechanical-fields-and-episode-delta-allowlist-travel-together`;
  `constraint:render-parse-round-trip-invariant` — `render_episode(parse_episode(text)) == text`,
  the file's own pre-existing documented contract, must hold for the new field too.
- **Decision anchors:** `decision:closeout-render-target-is-both` (`@grade: settled/human`) — now
  fully satisfied by both `finish_work`'s immediate return AND the durable persisted episode text,
  not just the former.
- **Evidence expectations:** re-confirm the round-trip invariant yourself by constructing an
  `Episode` with non-empty `overrides`, rendering it, parsing it back, and comparing — don't only
  trust the pasted test names.

## Evidence Produced
IMPLEMENTER_RESULT (attempt 2) at
`.agent-work/w2-ledger/crew-handoffs/g3-implement-implementer-result.md`. Target postconditions:
`g3-integrate.c1` (tests-pass command) and `g3-integrate.c2` (this review's verdict).

**Note:** neither attempt 1 nor attempt 2's IMPLEMENTER_RESULT includes a "## Return status" line
(a template-compliance gap in both attempts) — the Commander is treating this as `complete` based
on the documented content (all close criteria met, no stop conditions, no blockers stated). Flag in
your own Workflow Feedback if you agree or disagree with that reading.

## Suggested Model Tier
stronger — sonnet, reasoning-effort medium. The round-trip invariant and the "validated but not
persisted" class of gap both reward reading the actual test bodies, not trusting green output alone.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed; the full suite does not show green when you
run it yourself; the round-trip invariant does not actually hold when you construct your own test
case; any Allowed-Scope file shows an unexpected diff outside the five named spots.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.

Write the full `REVIEW_RESULT` to
`.agent-work/w2-ledger/crew-handoffs/g3-implement-reviewer-result.md` before ending your turn.
