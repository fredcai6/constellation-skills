# Plan Candidate A — constraint: SMALLEST-DIFF

## Premise
Minimize new surface. `finish_work` does NOT drive the final `advance` itself — it
requires the terminal gate already advanced (agent's own real evidence stays the
agent's job; only the *release/reap/archive/dispose sequencing ritual* becomes
mechanical). This cuts the riskiest piece (calling `checklist_engine.main()` for
`advance`, which needs a `--why`/`--mechanical` choice and touches gate semantics)
down to just `release`, which takes no such argument.

## Gates

**g1 — `done_refusal` + `finish_work` core (verify, close, archive, dispose)**
- New pure fn `done_refusal(spine, *, tree_clean, episodes_captured, archive_exists)`:
  thin wrapper around existing `closeout_refusal` (unchanged) plus two new checks
  (tree clean/staged, episodes captured). One extra refusal string, same shape.
- New impure fn `finish_work(spine_path, *, root, session_id, today, push=True)`:
  1. Load spine. If `engine_session.status != "released"`: call
     `checklist_engine.main(["--file", spine_path, "release", "--session-id", sid])`
     in-process (mirrors existing pass-through pattern; zero edits to
     checklist_engine.py). If release itself refuses (gate not terminal), surface
     that ONE refusal and stop — no partial mutation.
  2. Re-load spine, run `done_refusal`. Refuse-and-stop on failure.
  3. Call existing `close_work` unmodified (archive-move + commit).
  4. `git push` the branch if `push=True`.
  5. Return `{work_id, branch, head, archive, pushed}` — no `open_pr` call, no new
     helper; the caller decides PR-opening externally (matches the float).
- New thin CLI `scripts/spine_done_cli.py` (new file, not fenced) exposing this as
  one command.
- Tests: `tests/test_spine_lifecycle.py` additions — release-then-close happy path,
  refusal-preserved-through (non-terminal gate still refuses), tree-dirty refusal,
  episodes-missing refusal.

**g2 — child-plan lease release (the #552 mechanism)**
- Extend `finish_work` step 3 (before archive): glob `work_dir/**/*.json` for any
  child spine/plan carrying `engine_session.status == "active"`, and call
  `checklist_engine.main([...,"release",...])` on each via its own session id
  (read from the child's `engine_session.session_id`).
- Test: fixture work dir with a nested active child plan; assert both leases are
  `released` after `finish_work`, and the archive move includes the child.

**g3 — immediate reap trigger**
- New fn `force_reap(project_dir)` calling `spine_rail._binding_transaction(project_dir, lambda reaped: reaped)` as a library import (no edits to spine_rail.py). Called
  from `finish_work` after release, before archive.
- Test: fixture binding-store entry for a spine that is then released; assert
  `force_reap` removes it immediately (not on next unrelated transaction).

## Score

- **Depth**: medium — `finish_work` hides the release/reap/archive/dispose
  sequence behind one call, but the agent still owns the final `advance` and its
  own evidence, so "one door verb" is only 4 of 5 contract-sketch steps. A caller
  still makes two calls (advance, then finish_work) instead of one ("I'm done").
- **Locality**: excellent — everything lands in `spine_lifecycle.py` + one new
  CLI file + tests. Zero touches outside owned files.
- **Seam placement**: good but incomplete — the seam sits right after "gate
  already terminal," which is exactly where today's hand-sequencing already
  breaks (a skipped `advance` before closeout is a real failure mode #574 names).
- **Testability**: excellent — every sub-step is a small, independently
  fixturable function; no live-engine dependency beyond `main(argv)` calls
  already proven safe by mcp_spine_server.py's own pattern.

## Risk
Because `finish_work` does not call `advance`, it does not fully satisfy "the
agent should be able to just say I'm done" (#574's actual ruling) — it only
removes release/reap/archive/dispose, leaving one manual `advance` call. This is
the smallest diff, not the smallest gap.
