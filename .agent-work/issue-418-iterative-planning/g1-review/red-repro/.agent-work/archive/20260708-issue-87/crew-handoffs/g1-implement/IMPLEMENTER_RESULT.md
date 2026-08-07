# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
g1 (issue-87) — rekey the lessons-playbook dormancy clock

## Completed slice
Both required behaviors landed in `scripts/apply_lessons_delta.py`, TDD (red→green→refactor):

1. **Once per distinct work-id.** The tick aging block is now gated on the delta's
   `work_id` not already being in a seen-work-ids ring stored in the playbook-state
   header. A repeat tick from the same work-id logs `tick skipped … (no double-aging)`
   and ages nothing (no `runs_since_confirmed` increment, no expiry, no `run_tick`
   bump). Distinct work-ids age as before.
2. **Same-epoch guard.** On a real tick, a non-constellation lesson whose `added` date
   OR `last-confirmed` date equals the tick's stamp date is skipped for expiry even when
   `runs_since_confirmed > dormancy_runs`. Aging still increments; only deletion is
   guarded. A lesson can never die on the same day it was added or last confirmed.

Constellation lessons remain pinned (skipped before the guard, unchanged). Existing
headers (with or without the new field) parse and migrate on first write with no hand
edits.

## Scope
**Files changed:**
- `scripts/apply_lessons_delta.py`
- `tests/test_apply_lessons_delta.py`

**Specific exclusions touched:** no — `.agent-work/LESSONS.md`, `verify_lessons_applied.py`,
`checklist_engine.py`, and docs were untouched. The applier was never run against the real
playbook (all tests use a tmpdir `--file`).

## Behavior changed
Yes. (a) A burst of ticks sharing one `work_id` ages the dormancy clock at most once.
(b) A lesson is never auto-deleted on the same calendar date as its `added`/`last-confirmed`
stamp. No other op semantics changed.

## Map Impact
- **Structural anchors touched:** `struct:scripts/apply_lessons_delta.py` — tick branch
  rewritten (dedup gate + same-epoch guard); `STATE_RE`, `Playbook` dataclass,
  `load_playbook`, `render_playbook`, `_default_preamble` extended for the new header
  field; new pure helper `_stamp_date`. `struct:tests/test_apply_lessons_delta.py` — 10
  new tests; `test_tick_auto_deletes_unconfirmed` reseeded with a prior-dated `added`.
- **Capabilities affected:** `capability:lessons-playbook-dormancy` — dormancy clock now
  keyed by distinct work-ids with a same-day expiry guard, not raw invocation count.
- **Constraints/assumptions touched:** `constraint:constellation-lessons-pinned` honored
  (constellation `continue`s before both new checks); `constraint:backward-compatible-playbook-state`
  honored (optional regex group; silent migration); `constraint:mechanism-not-quality`
  honored (dedup by exact string identity, guard by date-string equality only).
- **Decision anchors:** `decision:dormancy-key=distinct-work-ids+same-epoch-guard`
  implemented as specified; not substituted. Implementer-owned decisions: storage format
  and retention bound (below).
- **Claims/evidence produced:** `claim:dormancy-behavior` (new tests below);
  `claim:test-suite-green` (full pytest run below).

## Test mode
**Required:** test-first (TDD).
**Satisfied:** yes — 7 behavior-gap tests observed RED against the unmodified script
before implementing; all green after.

## Evidence

```bash
python -m pytest tests/test_apply_lessons_delta.py -q
```
**Result:** pass (52 tests: 42 pre-existing + 10 new).

```bash
python -m pytest tests/ -q
```
**Result:** pass — `384 passed, 1 skipped, 18 subtests passed`. Pre-change baseline was
`374 passed, 1 skipped, 18 subtests` (375 total); +10 new tests, no regressions.

New tests:
- `test_tick_same_work_id_ages_lesson_once` — same work-id twice ages once.
- `test_tick_distinct_work_ids_age_each` — two distinct work-ids age twice.
- `test_same_work_id_burst_cannot_expire` — 20 ticks, one work-id, lesson survives (the dogfood bug).
- `test_same_epoch_guard_blocks_expiry_when_added_today` — 11 distinct ticks, born-today lesson survives.
- `test_same_epoch_guard_blocks_expiry_when_confirmed_today` — isolates the last-confirmed branch.
- `test_expires_on_later_dated_tick` — prior-dated lesson still expires on a later-dated tick.
- `test_ticked_work_ids_migrates_and_round_trips` — legacy header gains the field on first write.
- `test_existing_real_header_parses_with_empty_ticked` — the exact close-criteria header parses.
- `test_ticked_work_ids_bounded` — ring caps at 50 (w0 falls off, w59 retained).
- `test_malformed_ticked_work_ids_raises` — empty comma entry raises `LessonsDeltaError`.

Changed test: `test_tick_auto_deletes_unconfirmed` reseeded with `added="2026-01-01 (seed)"`
so it still exercises dormancy auto-delete (its original add-then-expire-same-day scenario
is exactly what the new guard now forbids).

## TDD evidence, if required
- Failing test observed: `python -m pytest tests/test_apply_lessons_delta.py -q` → `7 failed, 45 passed`
  (the dedup/guard/field tests) before touching the script.
- Passing test observed: same command → `52 passed` after implementation.
- Refactor while green: minor — extracted `_stamp_date` helper for single-source date parsing; suite stayed green.

## Seen-work-ids storage format & bound (implementer decision)
- **Format:** a new optional header field `ticked-work-ids=<id1>,<id2>,…` appended to the
  `playbook-state` comment after `apply-confirmed`, comma-joined, most-recent-last. Parsed
  via an optional `(?:\s+ticked-work-ids=(\S*))?` group in `STATE_RE`; absent field or empty
  value → empty ring. Work-ids are compared as opaque strings by exact identity.
- **Bound:** `TICKED_WORK_ID_RETENTION = 50` (documented at the constant). On each real tick
  the ring is `(existing + [work_id])[-50:]`. A work-id aged out of the ring simply ages once
  more if it re-ticks — harmless.
- **Fail-visible:** a corrupt field with an empty comma entry (e.g. `a,,b`) raises
  `LessonsDeltaError` on load; no silent fallback.
- **Migration:** `_default_preamble` and `render_playbook` always emit the field, so a header
  lacking it gains `ticked-work-ids=` (empty) on the next write with nothing else rewritten.

## run_tick / ripeness confirmation
Ripeness is unaffected. `ripe_lessons()` and `_apply_threshold_ripe()` key only off
`confirmed`/`recurrences`/`target`/`apply_*` thresholds — never `run_tick`. `run_tick` is a
display/state counter (header + log + summary line) with no role in ripeness or per-lesson
dormancy (which uses `runs_since_confirmed`). The rekey does change *what run_tick counts* — it
now increments once per distinct aging round rather than once per tick invocation (a deduped
repeat tick no longer bumps it) — but because nothing reads `run_tick` for a decision, no
documented behavior shifts. All 8 `test_ripe_*`/`test_apply_ripe_*` tests remain green.

## Docs/contracts touched
- None. The `LESSONS.template.md` dormancy bullet documents the rekey but is covered by a
  separate docs gate per the handoff exclusions; left untouched.

## Assumptions
- Work-ids are identifier-like (no commas/whitespace), consistent with every observed work-id
  in the repo and the `(work_id)` stamp convention. The header stores them comma-joined; a
  work-id containing a comma would be a corruption case (surfaced as an out-of-scope note).
- "Bounded retention ~50" satisfied with an exact cap of 50.

## Stop conditions hit
- None.

## Out-of-scope observations
- The seen-work-ids ring assumes work-ids are free of commas/whitespace (true for all current
  callers). If a future caller passes a work-id containing a comma, the header round-trip would
  mis-split it. A hardened version could reject such work-ids in `validate_delta` or encode
  them; out of scope here (mechanism-not-quality, and no such work-id exists). Triage candidate
  if work-id shape ever loosens.

## Workflow Feedback
- **Handoff gaps:** The handoff was thorough. The one genuine tension it did not call out: the
  same-epoch guard directly contradicts the *existing* `test_tick_auto_deletes_unconfirmed`,
  which adds and expires a lesson within the same real-world day. The close criteria imply the
  test must change, but the handoff's "Full suite green (375 tests pre-change)" line reads as
  "don't touch existing tests", which momentarily conflicts. A one-line note ("expect to reseed
  the same-day auto-delete test") would have removed the ambiguity.
- **Context rediscovered:** Whether `run_tick` should still increment on a deduped repeat tick
  was left to me (Protected Intent only asked me to *verify* ripeness, not to decide run_tick's
  increment policy). I chose "don't increment on a skipped tick" so run_tick stays a clean
  aging-round counter. Naming it explicitly as an implementer decision in the handoff would have
  saved a reasoning step.
- **Instructions improvised around:** None. The engine, plan template, and result template all
  fit. The gated plan drove cleanly (m0 attest → m1 red-attest → m2 command-green → m3 command-suite).
- **What would have made this easier:** In the handoff's Required Evidence, ask explicitly for
  the empty-vs-populated header round-trip check — I added it as a sanity step, and it is the
  single most load-bearing migration guarantee.

## Return status
complete
