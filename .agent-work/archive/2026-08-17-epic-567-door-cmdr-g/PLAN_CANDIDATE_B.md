# Plan Candidate B — constraint: MOST-TESTABLE + full contract coverage

## Premise
`finish_work` drives the WHOLE sequence, matching Tommy's actual ruling ("the
agent should be able to just say I'm done ... engine automatically closes up the
spine, moves it to archive, turns itself off"): verify -> advance (mechanical) ->
release -> reap -> archive -> dispose, in one call. Each sub-step is a separately
unit-testable pure-ish function; `finish_work` is a thin composer over them so the
composition itself needs no new logic to test beyond ordering.

## Gates

**g1 — verify + close (advance, release) as independently testable steps**
- New pure fn `done_refusal(spine, *, tree_clean, episodes_captured)`: wraps
  `closeout_refusal`'s terminality/lease checks (reused, not re-derived) plus two
  new checks. Returns ONE refusal string or None — same shape as
  `closeout_refusal`, testable with plain dicts, no I/O.
- New impure fn `_advance_and_release(spine_path, session_id, *, mechanical=True)`:
  calls `checklist_engine.main([...,"advance",active_id,"--mechanical",...])` if
  the active gate is not yet terminal, then `checklist_engine.main([...,"release",
  "--session-id",session_id])`, both in-process (existing pass-through pattern,
  zero edits to checklist_engine.py). Returns the two captured (stdout, exit code)
  pairs untouched, so a refusal from EITHER call surfaces verbatim — no
  re-wording, no swallowed exit code.
- Test: fixture spine at its terminal gate but not yet advanced -> asserts
  `_advance_and_release` moves it to `released`; fixture spine with an unmet
  postcondition -> asserts the advance refusal string passes through unchanged
  and release is never attempted (ordering test, mock-counts the release call).

**g2 — reap + child-plan release (the #552 mechanism), independently testable**
- New fn `force_reap(project_dir)`: library call into
  `spine_rail._binding_transaction(project_dir, lambda reaped: reaped)` (no edits
  to spine_rail.py). Pure at the call-boundary: takes a path, returns the reaped
  map or None (transaction abort).
- New fn `_release_child_plans(work_dir)`: walks `work_dir` (excluding the bound
  spine itself) for any JSON with `engine_session.status == "active"`, calls
  `_advance_and_release`'s release half on each via its own session id, returns
  the list of child paths released. Testable standalone against a fixture tree
  with 0, 1, and 2 nested active children.
- Tests: `force_reap` fixture (binding-store entry for a released spine ->
  gone immediately, not deferred); `_release_child_plans` fixture tree.

**g3 — `finish_work` composition + dispose + CLI**
- New impure fn `finish_work(spine_path, *, root, session_id, today, push=True,
  open_pr=False)`: composes g1+g2's functions in order — verify (`done_refusal`
  on the CURRENT state) -> `_advance_and_release` -> re-verify (`done_refusal`
  again, now expecting released+terminal, i.e. `closeout_refusal`'s own check) ->
  `force_reap` -> `_release_child_plans` -> `close_work` (existing, unmodified) ->
  `git push` if `push` -> `open_pr(...)` if `open_pr` (new helper, NOT called by
  default — matches the float; callable independently by an external wrapper
  either way). Returns `{work_id, branch, head, archive, pushed, pr: None|url,
  child_plans_released: [...]}`.
- New thin CLI `scripts/spine_done_cli.py` (new file, not fenced) exposing this
  as one command — the actual "one door verb," reachable today without waiting
  on lane A's mcp_spine_server.py rewrite to land.
- Tests: end-to-end fixture run (claim -> satisfy gates -> finish_work) asserting
  zero active leases before/after census, archive contains child plan, branch
  pushed to a local bare remote fixture (no real network).

## Score
- **Depth**: excellent — one call genuinely replaces the whole hand-sequenced
  ritual named in #574's contract sketch; the caller's mental model shrinks from
  6 ordered steps to 1.
- **Locality**: excellent — same as A: everything in `spine_lifecycle.py` + one
  new CLI file + tests, zero touches to fenced files.
- **Seam placement**: best of the two — the seam sits exactly where the mission
  puts it ("I'm done" -> engine does the rest), not one step short of it.
- **Testability**: excellent, and MORE granular than A — advance/release, reap,
  child-release, and compose are four independently fixturable units instead of
  one monolithic `finish_work`, so a future defect localizes to one function
  instead of one large integration test.

## Risk
More new code than A (one extra sub-step: driving `advance` itself), and the
`--mechanical` advance call is the one piece most exposed to lane A's
checklist_engine.py rewrite landing first (its CLI flag shape could change) —
mitigated by isolating that call inside one small function
(`_advance_and_release`) so a rebase touches one place, not the whole module.
