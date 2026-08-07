# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
g1 (issue-87) — dormancy-clock rekey in `scripts/apply_lessons_delta.py`

## Result
`APPROVE`

## Handoff compliance
All six close criteria independently verified against the diff and re-run tests:

1. **Work-id dedup.** `if work_id in book.ticked_work_ids:` skips aging entirely (no `runs_since_confirmed` bump, no `run_tick` bump). Same work-id twice ages once (`test_tick_same_work_id_ages_lesson_once`); a 20-tick burst on one work-id ages exactly once and cannot expire (`test_same_work_id_burst_cannot_expire`); distinct work-ids age each (`test_tick_distinct_work_ids_age_each`).
2. **Same-epoch guard.** A lesson whose `added` OR `last-confirmed` date equals the tick stamp date is aged but never deleted; a later-dated tick still expires it (`test_same_epoch_guard_blocks_expiry_when_added_today`, `..._when_confirmed_today`, `test_expires_on_later_dated_tick`).
3. **Constellation pinned.** The `if lesson.scope == "constellation": continue` is preserved verbatim, ahead of both new checks.
4. **Backward-compatible parse + migration.** The exact real header `run-tick=20 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3` parses (`test_existing_real_header_parses_with_empty_ticked`); a legacy header gains the field silently on first write (`test_ticked_work_ids_migrates_and_round_trips`).
5. **Fail-visible malformed state.** An empty comma entry raises `LessonsDeltaError` on load (`test_malformed_ticked_work_ids_raises`).
6. **Full suite green.** `python -m pytest tests/ -q` reproduced independently.

Stop conditions: none hit. Diff accessible, evidence reproducible, no policy decision required.

## Scope drift
Clean. `git status --porcelain` shows only `M scripts/apply_lessons_delta.py` and `M tests/test_apply_lessons_delta.py`. Specific exclusions (`.agent-work/LESSONS.md`, `verify_lessons_applied.py`, `checklist_engine.py`, docs) untouched. The applier was never run against the real playbook — every test uses a tmpdir `--file`.

## Evidence verdict
Both required commands re-run by the reviewer, matching the implementer's claim exactly:
- `python -m pytest tests/test_apply_lessons_delta.py -q` -> **52 passed** (42 pre-existing + 10 new).
- `python -m pytest tests/ -q` -> **384 passed, 1 skipped, 18 subtests** (baseline 374 + 10 new, no regressions).

TDD is credible: the 10 new tests are behavior-focused (dedup, burst, both guard branches, later-dated expiry, migration round-trip, bound, malformed). The reseeded `test_tick_auto_deletes_unconfirmed` (now `added="2026-01-01 (seed)"`) still passes in isolation and genuinely exercises dormancy auto-delete — the reseed was required because its original add-then-expire-same-day scenario is exactly what the new guard forbids.

## Code/doc quality
Minimal and consistent with the surrounding file. `TICKED_WORK_ID_RETENTION = 50` is documented with a comment matching the `DEFAULT_*` constant block above it; `_stamp_date` mirrors `_stamp`; the tick-branch refactor preserves the existing structure. `work_id` and `stamp` are both in scope at the tick block (defined at the top of `apply_delta`, lines 381/383), so `tick_date = _stamp_date(stamp)` is well-formed. Since `_stamp` always uses `date.today()`, the guard effectively shields a same-day birth/confirmation — consistent with the criteria.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the new tests and full-suite run back both the dedup and same-epoch-guard behaviors and the migration guarantee.
- **Constraints not violated:** `constraint:constellation-lessons-pinned` (continue intact), `constraint:backward-compatible-playbook-state` (optional regex group + silent migration), and `constraint:mechanism-not-quality` (exact-string dedup, date-string guard, no judgment) all honored.
- **Notes match the diff:** Yes — `STATE_RE`, `Playbook`, `load_playbook`, `render_playbook`, `_default_preamble` extended, `_stamp_date` added, tick branch rewritten. No missing or overstated structural/capability claims.
- **Decision candidates surfaced:** `decision:dormancy-key=distinct-work-ids+same-epoch-guard` implemented as specified, not substituted. Implementer-owned sub-decisions (storage format, retention bound of 50, don't-increment-run_tick-on-skip) are disclosed in the result.
- **Durable context routed:** The comma/whitespace work-id edge is surfaced as a triage candidate (below), not dropped.

**run_tick claim — independently verified.** `grep run_tick` yields only: dataclass field (115), parse (215), construct (244), render (257), increment (527), tick log (551), summary display (596). I read `ripe_lessons` (270) and `_apply_threshold_ripe` (294) directly — both key only on `confirmed`/`recurrences`/`target`/`apply_confirmed`/`apply_recurrences`/`status`/`deferred_at`, never `run_tick`. Per-lesson dormancy uses `runs_since_confirmed`. Nothing reads `run_tick` for a decision, so the rekey changing what it counts (once per distinct aging round rather than per invocation) shifts no documented behavior.

## Reconciliation check
No docs/contracts/structural-baseline concern. `LESSONS.template.md` correctly left untouched (separate docs gate per the handoff exclusions). No architecture divergence beyond the human-sanctioned decision.

## Blockers
- none

## Out-of-scope observations
- The `ticked-work-ids` ring stores work-ids comma-joined; a future work-id containing a comma or whitespace would mis-split on header round-trip. No such work-id exists today (all are identifier-like, matching the `(work_id)` stamp convention), so it is out of scope here. Flagged as triage candidate `tc1`: harden by rejecting comma/whitespace work-ids in `validate_delta` if the work-id shape ever loosens.

## Workflow Feedback
- **Handoff gaps:** The handoff was strong and its explicit "VERIFY the run_tick claim" instruction was well-targeted. One genuine path inconsistency: the survey state location in the handoff (`.agent-work/issue-87/g1-review/review.json`) sits at a different subtree than the result path (`.agent-work/issue-87/crew-handoffs/g1-review/REVIEW_RESULT.md`) — the survey is outside `crew-handoffs/` while the result is inside it. I followed the handoff literally for each. Worth aligning so both artifacts live under one gate directory.
- **Context rediscovered:** None material. The IMPLEMENTER_RESULT's `run_tick` section named the exact functions to check (`ripe_lessons`, `_apply_threshold_ripe`), which made independent verification fast rather than a rediscovery.
- **Instructions improvised around:** The base `REVIEW_SURVEY.template.json` carries `config_ref: docs/agents/engine-config.json`, which does not exist in this repo (handoff confirms no overlay). The engine tolerates it (empty config, default rework cap), so no action needed — noting only that the template's default config_ref is dead in a repo without the overlay.
- **What would have made this easier:** Aligning the survey and result paths under a single `crew-handoffs/g1-review/` directory (see above) would remove the one point of friction in this review.

## Return status
`complete`
