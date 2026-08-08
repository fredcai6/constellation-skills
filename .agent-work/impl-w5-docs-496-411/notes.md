# Working notes — impl-w5-docs-496-411

Crew 5, wave 5 (epic #418). Two documentation corrections: #496 and #411. No launch order file
existed at `.agent-work/epic-418-redux/launch-orders/LO-w5-c5-docs.md` when this run started —
the team-lead's dispatch message supplied task/scope/exclusions directly instead. Reported this
gap in Workflow Feedback.

## #496 — CREW_CONTEXT.md's newline rule doesn't name save()'s exception

**Verdict: HOLDS.**

- `docs/agents/CREW_CONTEXT.md` "Writing Files On Windows" (before edit): "Pass
  `encoding='utf-8', newline='\n'` explicitly on **every** write." — no exception named.
- `scripts/checklist_engine.py` `save()` (lines 191-209): docstring says it writes
  "PRESERVING the line ending the file already uses, and write BYTES so nothing translates
  them again." It does not call `open(..., newline=...)` at all — `Path(path).write_bytes(payload)`
  after replacing `\n` with the file's own dominant EOL (LF for new/mixed files).

**Fix applied:** added one sentence to CREW_CONTEXT.md naming `save()`'s byte-preserving write
as the sanctioned exception (`docs/agents/CREW_CONTEXT.md`, "Writing Files On Windows" section).

**Not touched:** `scripts/checklist_engine.py`, `tests/test_checklist_engine.py` — crew 4's
territory this wave. No code-change conclusion was reached; the doc now matches the code as it
stands.

## #411 — TREND_SNAPSHOT.md lists `_shared` as a 20th role

**Verdict: HOLDS.**

- `.agent-work/archive/2026-08-02-issue-304/TREND_SNAPSHOT.md` §2 (before edit) listed
  `_shared   6 files   6729 words` as the first of 20 rows in a "per-role surface" table.
- `scripts/install_constellation.py:268`: `if path.is_dir() and not path.name.startswith("_")
  # _shared holds bundled refs, not a skill` — confirms `_shared` is excluded from skill
  enumeration.
- `README.md`: `skills/_shared/` is **not a skill** — it is shared doctrine.

Note: the live corpus has since grown to 20 real skills (README now correctly says "The corpus
is **20 skills**" after #463/#466) — that is a separate, already-fixed fact from #411's actual
target, which is the historical snapshot's own mis-categorization of `_shared` as a peer role at
the commit (`fc1685a`) it was taken.

**Fix applied:** dropped the `_shared` row from the per-role table; added a note stating the
role count at that snapshot was 19 (derived from the installer's exclusion rule) and explaining
`_shared` as bundled shared surface rather than a role's own surface.

**Deliberately not done:** recomputing each role's individual bundled-`_shared` word-count
attribution (`SKILL_REFERENCE_BUNDLES`) — the issue's third suggested-fix bullet. That is a new
derived measurement, not a documentation correction, and doing it without running the actual
install/measure pipeline risks fabricating numbers. Left as an open item in the doc, pointing at
#411 for a future successor — this is TREND_SNAPSHOT.md's own established convention (it already
declares itself a baseline for successors to extend).

## Test mode

No test surface for either fix (pure prose corrections to documentation/archived-snapshot
files) — inspection evidence per `global-crew.md`: "No test surface → review/inspection
evidence, not a skipped check." Ran the full suite as a sanity check that nothing broke.
