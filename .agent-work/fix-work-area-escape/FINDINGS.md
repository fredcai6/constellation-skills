# Findings — fix/work-area-escape

## What was fixed

- **Task 1**: `scripts/episode_capture.py::manifest_root` no longer falls back to
  `base.parent` unconditionally. It still strips a matching (possibly nested)
  work-id exactly as before; when that strip doesn't apply AND `base_dir` has no
  `.agent-work` ancestor to anchor a "parent of a work area" guess to, it now
  raises `ValueError` instead of silently climbing out. The legitimate
  scratch-spine case (`base_dir` under `.agent-work` but not ending in its own
  work-id) is unchanged — same historical `base.parent` answer, pinned by an
  existing test and a new positive control beside the new refusal.
- **Task 2**: `scripts/agent_work_root.py`'s module docstring no longer calls
  `.agent-work/` "(gitignored, disposable)". It now says what's true: tracked on
  the worktree's own branch, not gitignored, holding transportable work in
  progress.

## What was NOT fixed, and why

- **The four existing stray directories** (`.worktrees/s`, `/t`, `/probe`, and
  the pair under `constellation-skills-wt/`) are untouched, per the handoff's OUT
  list. Left in place as both preserved evidence and this regression's own
  real-world reference.
- **`.worktrees/epic-568-441`**: not touched.
- **`durable_root`'s redirect semantics, the active-epic-lease exception, the
  lexical-vs-git spine ownership question, and `origin_worktree_refusal`'s
  containment predicate**: all out of scope, none touched.
- **The primary checkout's `.agent-work/` archives**: not gitignored, nothing
  built that depends on them becoming so.
- **The fail-soft/fail-silent split in `episode_capture.py`'s wider design**
  (broad `except`, the failure-stub contract): unchanged. One consequence is
  worth flagging explicitly rather than leaving implicit: when `manifest_root`
  now refuses because `base_dir` has no `.agent-work` ancestor, that refusal is
  caught by `emit_step_manifest`'s own broad `except` *and* by
  `_write_failure_stub`'s attempt to locate somewhere to write a failure record —
  which calls `manifest_root` again and is refused a second time, for the same
  reason. The net effect in that one case is **silence**: no manifest, no stub,
  `emit_step_manifest` returns `None`. Every other fail-soft path in this module
  still leaves a stub (that invariant is pinned by
  `test_failsoft_an_arbitrary_producer_crash_leaves_a_stub_not_silence` in
  `tests/test_episode_capture.py`). This one case is a deliberate, narrower
  exception: there is no known work area to put even a failure record in, so
  writing a stub via the old unconditional `base.parent` would just be the
  escape again, one level indirect. This is covered by a new test
  (`test_a_base_dir_outside_any_work_area_writes_nothing_at_all`) rather than by
  a docstring rewrite of `_write_failure_stub`, to keep this diff scoped to the
  escape itself.

## Open lead: who invoked the manifest tooling with `probe`/`s`/`t`?

Not identified, and I'm saying so plainly rather than guessing.

What's checkable from disk: each stray manifest (e.g.
`.worktrees/probe/context/g1.json`) records `run.roots.*` and `run.host.cwd`, all
pointing at `/home/tommy/projects/constellation-skills/.worktrees/epic-568-510`,
and a `generated_at` timestamp (`probe`: `2026-08-15T00:30:32Z`). That worktree no
longer exists on this machine (removed since), so there is nothing left to
inspect there directly. The manifest schema itself (`context_manifest.py`)
doesn't capture a pid, argv, or session id — only the roots, host platform/python
version, and cwd — so even with the worktree still present there would be no
recorded trail back to the specific command or process that called
`episode_capture`'s functions directly (rather than through
`checklist_engine start`/`reopen`, which is the only path real production code
takes today; see `manifest_root`'s docstring). The placeholder names (`s`, `t`,
`probe`) read like ad hoc manual exercise of the manifest/mechanical-snapshot
functions rather than anything a real checklist would name a work-id — consistent
with someone testing `episode_capture` by hand — but that's a plausible reading
of the evidence, not a finding. I did not find anything in this repository (shell
history is outside a repo's scope and wasn't available to check) that names the
caller.
