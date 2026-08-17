# Review Result

## Assigned Gate
`g1` — door-refusal episode capture (issue #541) + refusal-text swap (issue #559)

## Result
`APPROVE`

## Handoff compliance
Both tasks from the handoff are present in the diff and match the Task Statement:
Task A (`_capture_refusal_episode` wired into `_log_rejection` as a second side
effect alongside the existing JSONL sidecar append) and Task B (`_THE_CLI_IS_PER_CALL`
retext at both `_spine_bind` sites, plus the third, not-explicitly-named occurrence
in `_identity_violation` — a reasonable, disclosed reading of the file-wide grep
Close Criterion). All Close Criteria were independently re-derived rather than
read off the implementer's transcript: a self-authored fresh-process trigger
(`/tmp/reviewer_trigger_567e.py`) produced `episodes/active/567-e-004.md` with
all 9 mechanical fields and all 5 agent-supplied assertions, read back cleanly
with `query_episodes.py fetch` (exit 0), and a self-run negative control
(temporarily bypassing the capture call, then restoring it cleanly) produced
zero new files under `episodes/active/`. `grep -n "per-call by construction"
scripts/mcp_spine_server.py` returns nothing. The `spine_bind` `TOOLS`
description's second-person rewording is disclosed as an implementer judgment
call, is meaning-preserving, and was necessary for the mandated acceptance
population (`spine_bind`) to complete the write→read-back loop at all —
reasonable latitude, properly flagged rather than made silently.

## Scope drift
None. `git status --porcelain` confirms only `scripts/mcp_spine_server.py` is
modified; `tests/test_mcp_rejection_episode_capture.py` is the only new test
file; `episodes/active/567-e-001.md`..`003.md` (implementer's acceptance runs)
plus `567-e-004.md` (this review's own independent trigger, the same allowed
byproduct category) are the only episode files. None of the fenced files
(`scripts/checklist_engine.py`, `scripts/run_crew.py`, `docs/**` outside
`CREW_CONTEXT.md`) appear in the diff. `_own_checkout_for_binding`'s
containment body (`scripts/mcp_spine_server.py:1176-1241`) is untouched — only
a new caller references it; the hardlink containment hole remains open, as
required.

## Evidence verdict
Required evidence present and independently reproduced, not merely trusted:
- Fresh-process trigger + negative control: reproduced myself (see Handoff
  compliance above), not read from the implementer's result.
- All five `agent_supplied` fields inspected directly in `567-e-004.md`: `a2`
  (expected-behavior) is a literal `TOOLS`-description quote, `a3`
  (observed-behavior) is the literal refusal message, `a5` (workaround) is the
  literal trailing-sentence extraction of that same message — all three
  verified byte-for-byte against source. `a1` (task-intent) and `a4`
  (impact-cost) are fixed, always-true-for-the-population template sentences
  with the real tool name interpolated, not composed narrative or invented
  judgment — matches the code's own stated design and the `capture-is-literal-
  derivation-only` decision anchor. None reads as invented.
- Exception-handling shape inspected directly, not just the "never crashes"
  claim: narrow per-step guards inside `_capture_refusal_episode` (spine
  read, `mechanical_fields()`, checkout resolution, delta write, subprocess
  launch), plus one outer broad `except Exception` at the `_log_rejection`
  call site. One gap in the narrow guards was found — `json.dumps(delta, ...)`
  inside the delta-write `try` is only guarded by `except OSError`, so a
  `TypeError` there would not be caught by that inner guard — but it is still
  caught by the outer `except Exception` in `_log_rejection`, so nothing
  escapes past `_log_rejection`. This matches the handoff's own instruction
  to consider whether any path between the try and the writes could escape;
  it can escape the inner guard but not the outer one, which is the
  documented design.
- Full required suite re-run independently: 291 passed, 64 subtests passed,
  0 failed.

## Code/doc quality
Minimal, maintainable, matches this file's own established conventions
(heavy design-rationale docstrings, sequential narrow-guard-clause functions,
fail-visibly `stderr` diagnostics) already present at `_own_checkout_for_binding`,
`_write_amend_delta`, and `_derivable_work_id` before this diff. Test coverage
(`tests/test_mcp_rejection_episode_capture.py`, 291 total suite passes) covers
the happy path, dedup, distinct-key non-dedup, incomplete-mechanical-bin skip,
unknown-tool skip, non-zero-exit and `OSError`-on-launch subprocess failure,
and the outer-guard-never-crashes case directly. Fowler baseline pass run and
verified (`scripts/verify_fowler_pass.py` exits 0): `long-method`,
`duplicated-code`, and `comments-as-deodorant` are `overridden` against this
same file's own pre-existing convention (logged reason + specific precedent
cited for each); the remaining nine baseline smells are `absent`; none
`flagged`.

## Map impact verdict
- **Evidence supports claimed change:** yes — the capability claim (door-own
  rejections durably captured into `episodes/`) is backed by the independently
  reproduced fresh-process trigger and negative control.
- **Constraints not violated:** yes, checked directly against the diff —
  single-write-path via `apply_episode_delta.py` (no hand-write into
  `episodes/`), absolute `--store-root` (`_own_checkout_for_binding()` returns
  a resolved absolute path), `--delta` as a file path (mirrors
  `_write_amend_delta`), mechanical bin sourced from `mechanical_fields()`
  with the one stated `_derivable_work_id()` exception for `run` (verified
  the two helpers cannot disagree in a case `mechanical_fields()` would have
  succeeded — `_derivable_work_id()` is strictly the more general one),
  in-process dedup, `SPINE is None` skip, and `_tool_error`'s unchanged return
  shape.
- **Notes match the diff:** yes — the implementer's Map Impact structural
  anchors, new symbols, and capability/constraint claims all match what
  `git diff` shows.
- **Decision candidates surfaced:** yes — `capture-is-literal-derivation-only`
  implemented as specified and judged directly (see Evidence verdict); the
  `spine_bind` description rewording is flagged prominently as a judgment
  call a disagreeing reviewer could revert independently of everything else.
- **Durable context routed:** yes — three triage candidates named by the
  implementer (checklist_engine.py's blind `refusals` counter, engine-native
  refusals uncovered by this seam, four more `TOOLS` descriptions with
  second-person pronouns) are routed out, not silently fixed or dropped. This
  review additionally re-flagged the third of those into its own survey's
  `triage_candidates` (`tc1`) since it is a real latent gap: those tools'
  door-own rejections will silently skip capture (fail-safe, not a crash) the
  moment anyone captures them.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconciliation
beyond what the implementer already surfaced (the `EPISODE_STORE.md` §10
tension, correctly left for the Admiral rather than decided locally).

## Blockers
- none

## Out-of-scope observations
- Four more `TOOLS` descriptions (`spine_status`, `spine_lease`, `spine_halt`,
  and originally `spine_bind` itself) still carry second-person pronouns and
  will hit `verify_episode_observations.py`'s guard the moment any of their
  door-own rejections are captured — fails safe (stderr `SKIPPED`
  diagnostic), never crashes, but silently drops the episode. Flagged as
  triage candidate `tc1` in this review's own survey
  (`.agent-work/567-e/g1-review/review.json`).

## Workflow Feedback

- **Handoff gaps:** None material. The Close Criteria's file-wide
  `grep -n "per-call by construction"` check combined with Task B's
  site-scoped description (naming only the two `_spine_bind` sites) left
  genuine room to read the third `_identity_violation` occurrence as
  in-scope or out — the implementer's choice to fix it and flag the
  ambiguity was the right call, but the handoff should have named that third
  site explicitly to remove the ambiguity at handoff time rather than leaving
  it for implementer judgment.
- **Context rediscovered:** none — confirmed after review: the handoff's Map
  Anchors section named every file (`episode_capture.py`, `apply_episode_delta.py`)
  and function needed to verify the `_derivable_work_id()` vs
  `mechanical_fields()` precedence claim directly; nothing had to be dug up
  beyond what the anchors pointed at.
- **Instructions improvised around:** My process's MCP door was UNBOUND per
  the dispatch instructions, so I built my own `REVIEW_SURVEY.json` at
  `.agent-work/567-e/g1-review/review.json` (per skill guidance: "building
  REVIEW_SURVEY.template.json and claiming a lease is only for the case where
  nothing is bound") rather than driving the inherited `SPINE_FILE`/
  `SPINE_SESSION` env — those belong to the parent per the standing ruling
  that a crew's inherited `SPINE_*` env is not its own to drive. Driving my
  own survey via the CLI `checklist_engine.py` (not the MCP door) worked
  cleanly end-to-end.
- **What would have made this easier:** none beyond the one handoff gap
  named above.

## Return status
`complete`
