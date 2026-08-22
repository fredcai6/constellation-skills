# IMPLEMENTER_RESULT (attempt 2)

## Completed slice
PARTS A-D landed exactly as attempt 1 left them (verified via `git diff` before touching
anything — untouched except where PART E required mechanical wiring). This attempt adds
**PART E**, the rework the Commander ordered after attempt 1's out-of-scope observation:
`scripts/apply_episode_delta.py`'s `Episode`/`render_episode`/`parse_episode`/
`_apply_create` were validating `mechanical.overrides` (PART B) but silently dropping it
before it ever reached the persisted `.md` file — the durable half of this gate's
Protected Intent was unmet.

- **`Episode` dataclass**: added `overrides: dict = field(default_factory=dict)`. Placed
  immediately after `agent_supplied`, before `diagnosis` — NOT directly after
  `artifact_refs` as the handoff's prose literally says, because `agent_supplied` is a
  required (no-default) field and Python dataclasses refuse a default-valued field
  followed by a non-default one; `agent_supplied` must stay where it is (right after
  `artifact_refs`), so `overrides` goes immediately after it instead, ahead of the other
  already-defaulted optional fields (`diagnosis`, `status`, etc.) it belongs alongside.
  Flagged as an assumption below.

- **`render_episode`**: after the `artifact-ref` lines, emits
  `- overrides: <json.dumps(ep.overrides, sort_keys=True)>` when `ep.overrides` is
  non-empty; nothing when empty — mirrors `artifact-ref`'s repeatable-line idiom and the
  file's absence-is-meaningful convention.

- **`parse_episode`**: extracts the `overrides` line from the mechanical block (the
  existing `FIELD_RE`/mech-dict loop already captures it as a raw string keyed
  `"overrides"`; a new one-line `json.loads(mech["overrides"]) if "overrides" in mech else
  {}` recovers the dict), passed into the constructed `Episode`.

- **`_apply_create`**: passes `overrides=mech.get("overrides") or {}` into the constructed
  `Episode`.

`json` was already imported at module level — no new import needed.

## Files changed
- `scripts/apply_episode_delta.py` — PART E only: `Episode` dataclass field,
  `render_episode`, `parse_episode`, `_apply_create`. Nothing else in the file touched
  (amend-assertion, retirement, consolidation, etc. left exactly as attempt 1's PART B
  left them).
- `tests/test_episode_store.py` — two new test classes:
  - `OverridesPersistenceTests` (sibling to the existing `OverridesMechanicalFieldTests`):
    a `create` op carrying `mechanical.overrides` produces a persisted `.md` file whose
    text contains the rendered line (present case) and no line at all (absent case); both
    assert `render_episode(parse_episode(text)) == text`.
  - `EpisodeOverridesRoundTripTests`: direct `Episode` → `render_episode` → `parse_episode`
    round trip, independent of the writer, for both the overrides-present and
    overrides-absent cases — the file's own documented invariant
    (`render(parse(text)) == text`), exercised explicitly for the new field per
    PLAN_CRITIC.md Finding 1.
- `map/INDEX.md` — regenerated (`python -m scripts.code_map build --root .`) after the new
  test classes; `test_code_map.py`'s freshness gate failed before the rebuild (stale by 8
  entities) and passes after. Same build-artifact convention attempt 1 already used for
  PARTS A-D.

PARTS A-D's own files (`scripts/checklist_engine.py`, `scripts/episode_capture.py`,
`scripts/spine_lifecycle.py`, `tests/test_checklist_engine.py`, `tests/test_episode_fields.py`,
`tests/test_spine_lifecycle.py`) were re-verified against the handoff's Close Criteria but
not re-touched — they already carried attempt 1's landed work in this worktree.

## Test mode satisfied
Test-after, as specified. Round-trip test (writer-level) plus a direct dataclass-level
round-trip test, covering both the overrides-present and overrides-absent cases as
required.

## Evidence produced

**`pytest tests/test_episode_fields.py -q`**: `40 passed in 5.10s`

**`pytest tests/test_spine_lifecycle.py -q`**: `122 passed, 1 skipped in 1.06s`

**`pytest tests/test_checklist_engine.py -q`** (confirmatory): `516 passed, 147 subtests passed in 5.13s` — no regression.

**`tests/test_episode_store.py`** (validator + PART E persistence coverage):
`139 passed, 50 subtests passed in 1.22s` (full file, includes the two new PART E classes).

**Round-trip test, individually** (load-bearing, PART B/C — pre-existing from attempt 1,
re-verified):
```
tests/test_episode_fields.py::ZeroAgentEffortTests::test_overrides_field_survives_the_create_op_validation_path PASSED
```

**PART E persistence tests, individually:**
```
tests/test_episode_store.py::OverridesPersistenceTests::test_create_op_with_overrides_persists_rendered_line PASSED
tests/test_episode_store.py::OverridesPersistenceTests::test_create_op_without_overrides_renders_no_overrides_line PASSED
tests/test_episode_store.py::EpisodeOverridesRoundTripTests::test_non_empty_overrides_round_trips PASSED
tests/test_episode_store.py::EpisodeOverridesRoundTripTests::test_empty_overrides_renders_no_line_and_round_trips PASSED
```

**Four `finish_work` return-point tests, individually** (PART D — pre-existing from
attempt 1, re-verified):
```
tests/test_spine_lifecycle.py::TestFinishWorkOverrides::test_verify_refusal_carries_overrides PASSED
tests/test_spine_lifecycle.py::TestFinishWorkOverrides::test_advance_release_refusal_carries_overrides PASSED
tests/test_spine_lifecycle.py::TestFinishWorkOverrides::test_archive_refusal_carries_overrides PASSED
tests/test_spine_lifecycle.py::TestFinishWorkOverrides::test_success_carries_overrides PASSED
```

**Wiring grep** (`grep -rn "override_summary" --include=*.py . | grep -v "def override_summary"`):
non-test call sites unchanged from attempt 1: exactly 2 — `scripts/episode_capture.py:457`
(`mechanical_fields`) and `scripts/spine_lifecycle.py:1114` (`finish_work`). PART E does not
call `override_summary` (it operates on `mechanical["overrides"]`, already a plain dict by
the time it reaches `apply_episode_delta.py`), so the count is unaffected by this attempt's
change.

**Full repo suite** (`python -m pytest -q`, after the `map/INDEX.md` rebuild):
`3660 passed, 6 skipped, 1274 subtests passed` — clean, including `test_code_map.py`'s
freshness gate. (Run once before the rebuild — 1 failure, exactly the stale-map gate, 3659
passed; rerun after `python -m scripts.code_map build --root .` — fully clean.)

**Deliverable path check** — `git check-ignore <path>` exit code 1 (not ignored) for
`scripts/apply_episode_delta.py`, `scripts/checklist_engine.py`,
`scripts/episode_capture.py`, `scripts/spine_lifecycle.py`, `map/INDEX.md`, and every test
file touched.

## Assumptions used
- `overrides` field placement in the `Episode` dataclass: the handoff says "after
  `artifact_refs`, before `agent_supplied`" but `agent_supplied` has no default and must
  stay adjacent to `artifact_refs` (dataclass field-ordering rule: no default-valued field
  may precede a non-default one). Placed `overrides` immediately after `agent_supplied`
  instead — still ahead of `diagnosis`/`status`/etc., still grouped with the other
  optional/defaulted fields the handoff explicitly compares it to (`retired_reason`).
- Reused attempt 1's PART A-D work as-is (per the rework note's explicit instruction not to
  re-touch A-D except where E requires mechanical wiring) rather than re-deriving it —
  verified it matches every Close Criterion before proceeding, not merely trusted.

## Stop conditions hit
None. The round-trip invariant held for both cases without needing any change beyond
`Episode`/`render_episode`/`parse_episode`/`_apply_create`; no PART B change was needed
(the shape check already accepted a dict, PART E just stopped discarding it after
validation).

## Out-of-scope observations
None new. Attempt 1's out-of-scope observation (the exact gap this attempt closes) is
resolved.

## Workflow feedback
The rework note's precise pointer to the untouched code path (`_apply_create`/`Episode`/
`render_episode`/`parse_episode`, named individually) made this a small, well-bounded
addition — no exploration needed beyond reading those four spots. One friction: the
handoff's suggested dataclass field position ("after `artifact_refs`, before
`agent_supplied`") isn't achievable given `agent_supplied`'s no-default status; worth a
one-line caveat in the next handoff that names a field-insertion point.

Wrote this file at `.agent-work/w2-ledger/crew-handoffs/g3-implement-implementer-result.md`.
