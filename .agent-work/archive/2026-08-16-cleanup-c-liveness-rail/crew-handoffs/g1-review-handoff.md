# Reviewer Handoff

## Gate
g1 (issue #599)

## Survey State Location
`.agent-work/cleanup-c-liveness-rail/g1-review/review.json`

## What Was Implemented
`scripts/run_crew.py`'s `active_duplicate()` used to block/free a crew launch off a raw `status` string alone (`running`/`resumable`), with no corroboration. A new pure function `entry_liveness(entry, now, alive=None) -> "active"|"stale"|"unknown"` was added, and `active_duplicate` was wired to call it: a corroborated-dead entry (`"stale"`) now frees the slot; an uncorroborated one (`"active"` or `"unknown"`) still blocks. Tests were added to `tests/test_crew_launcher.py`. Committed as `cbd18faf` on branch `cleanup/c-liveness-rail`.

## How to Inspect the Diff
`git show cbd18faf` (or `git show cbd18faf -- scripts/run_crew.py` / `-- tests/test_crew_launcher.py` separately) — this is a linked worktree at `/home/tommy/projects/constellation-skills/.worktrees/cleanup-c-liveness-rail`, and the change is already committed (not uncommitted working-tree state), so review the commit directly rather than `git diff`.

## Task Statement
Replace `active_duplicate()`'s raw status-string check with a corroborated three-state liveness query, so a corroborated-dead entry stops blocking a fresh crew launch while an uncorroborated one still blocks (fail-toward-active). Full original task in `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g1-implement-handoff.md`.

## Close Criteria
- `entry_liveness` returns exactly one of `"active"`, `"stale"`, `"unknown"` — verify by reading the function body, not just its docstring.
- The three-bucket rule is **literally three buckets, not two**: (1) pid truthy → `process_alive(pid)`; (2) pid falsy AND `entry_backend(entry) == BACKEND_EXTERNAL` → heartbeat-age vs `HEARTBEAT_STALE_SECONDS`; (3) pid falsy AND NOT external → `"unknown"` directly, with **no** heartbeat lookup attempted for bucket 3. Confirm bucket 3 does **not** fall through to the heartbeat branch.
- Bucket 3 must **not** silently reuse `recover_crews.classify_entry`'s `pid=None` mapping (there, `alive(None)` is always `False`, routing away from "active") — that is the opposite of this repo's fail-toward-active rule. Confirm `entry_liveness` never imports or calls anything from `recover_crews.py`.
- `active_duplicate`'s policy: `"stale"` → `continue` (frees); `"active"` or `"unknown"` → `return entry` (blocks). Confirm both `"active"` and `"unknown"` block — this is the fail-toward-active non-negotiable, and a bug here (e.g. only blocking on `"active"`) would silently free slots for unknown entries, which is exactly the failure this gate exists to prevent.
- No write path sets `entry["abandoned"] = True` or `entry["status"] = "abandoned"` anywhere in this diff — `entry_liveness`/`active_duplicate` only ever READ; a `"stale"` verdict changes what is reported, never mutates the registry (no-abandonment-by-inference).
- `HEARTBEAT_STALE_SECONDS = 28800` (8h) is present as a named module constant with its evidence cited in a comment (not a bare magic number).
- `scripts/recover_crews.py` — zero diff. Run `git diff --stat cbd18faf~1 cbd18faf -- scripts/recover_crews.py` yourself and confirm empty output.
- No fenced file touched: `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/mcp_spine_server.py`, `.mcp.json` — confirm via `git show cbd18faf --stat` showing only `scripts/run_crew.py` and `tests/test_crew_launcher.py`.
- `process_alive`'s own `def` block, docstring, and body are byte-identical to before this commit (it is reused, not modified) — confirm via `git show cbd18faf -- scripts/run_crew.py | grep -A2 "^-.*def process_alive"` showing nothing (no removal of its definition line).

## Allowed Scope
`scripts/run_crew.py` (the new function/constant + `active_duplicate`'s signature/body), `tests/test_crew_launcher.py` (new tests only, existing tests must be unmodified).

## Specific Exclusions
`scripts/recover_crews.py` (read-only precedent, must show zero diff), `scripts/hooks/spine_rail.py` (a separate gate, g2), and every fenced file listed above.

## Constraints the Implementation Must Respect
- `entry_liveness` must be genuinely pure: `now` and `alive` are always caller-supplied, no real `datetime.now()`/PID reads inside its body.
- Existing callers of `active_duplicate` (the CLI at `:1800`-ish, `tests/test_crew_launcher.py::test_duplicate_active_lock_is_refused`) must need zero code changes — only the *return value* for a corroborated-dead entry changes.
- `test_duplicate_active_lock_is_refused` and the existing `process_alive` tests must be unmodified in the diff (their assertions and fixtures identical to before) and must still pass.

## Map Anchors (inbound)
Map orientation is DEGRADED-UNPARSEABLE at baseline (zero authored map anchors corpus-wide) — no map artifact to check against; use file:line citations instead.
- **Structural:** `scripts/run_crew.py` — `active_duplicate()`, `process_alive()` (unchanged), `ACTIVE_STATUSES`, the external-backend `pid=None` construction, the launch-refusal call site.
- **Capability:** Crew launch-refusal / duplicate guard.
- **Constraints/assumptions:** `recover_crews.py` read-only, its pid=None mapping must not be ported.
- **Decision anchors:**
  - fail-toward-active — uncorroborated liveness reports `active`, never free. `@grade: settled/human · leans g1-implement`
  - three-states-not-two — the query returns active/stale/unknown, never a collapsed boolean. `@grade: settled/measured · leans g1-implement`
  - pidless-means-heartbeat — 8h (28800s) window, measured from the corpus. `@grade: settled/measured · leans g1-implement`
  - no-abandonment-by-inference — reporting stale is the deliverable, no side-effect writes. `@grade: settled/human · leans g1-implement`
- **Evidence expectations:** `tests/test_crew_launcher.py::test_duplicate_active_lock_is_refused` must keep passing unmodified.
- **Map confidence flags:** none (DEGRADED, discharged).

## Evidence Produced
Full IMPLEMENTER_RESULT at `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g1-implement-result.md` — 6 evidence items (4 load-bearing before/after pairs using the real `epic-568-441` archived phantom shape, 1 regression guard, 1 confirmatory full-suite run: 181 passed). Independently reproduced by the Commander before this dispatch: `find . -name __pycache__ -type d -exec rm -rf {} + ; env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py` → `181 passed`. Reproduce it yourself as well. This evidence targets `g1-integrate.c1` (the test-suite postcondition) and `g1-review.c1` (this review's own `review-result` artifact).

## Suggested Model Tier
Simple bounded — a focused diff against a fully-specified three-bucket contract; verification is mostly reading the function body against the close criteria above and reproducing the test run.

## Stop Conditions
Stop and return BLOCK if: the three-bucket rule is not literally three buckets, `recover_crews.py` or any fenced file shows a non-empty diff, `process_alive`'s own definition was touched, any test was weakened/deleted rather than added, or the suite does not reproduce green.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.

Write the full REVIEW_RESULT to `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g1-review-result.md` before ending your turn.
