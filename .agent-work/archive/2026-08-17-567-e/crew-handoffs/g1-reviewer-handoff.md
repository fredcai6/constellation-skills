# Reviewer Handoff

## Gate
g1 (`.agent-work/567-e/execute.json`)

## Survey State Location
`.agent-work/567-e/g1-review/review.json`

## What Was Implemented
Two changes in `scripts/mcp_spine_server.py` (issue #541):
1. `_capture_refusal_episode()` — writes a real episode into the tracked `episodes/` store
   (via `scripts/apply_episode_delta.py --store-root episodes`) whenever a door-own rejection
   fires with a spine bound, as a second side effect alongside the existing
   `_log_rejection()` JSONL sidecar append. Every one of the five agent-supplied assertion
   fields is a literal derivation from the refusal's own data (never invented narrative), and
   capture is skipped (never fabricated) when `episode_capture.mechanical_fields()` cannot
   derive a complete mechanical bin, when the tool has no registered `TOOLS` description, or
   when no spine is bound.
2. `_THE_CLI_IS_PER_CALL`'s text (used at the two `_spine_bind` containment-refusal sites, plus
   a third occurrence in `_identity_violation`) no longer recommends the CLI to an agent —
   replaced with text naming the actual working path (a dispatched crew's spine is already
   bound via `run_crew.py --backend cli --spine`), consistent with this module's own
   already-ratified issue #559 doctrine.
Plus: a one-word rewording of `spine_bind`'s own registered `TOOLS` description (removing a
second-person pronoun that tripped `apply_episode_delta.py`'s pre-existing
`verify_episode_observations.py` no-second-person guard) — meaning preserved, disclosed by
the implementer as a judgment call. New test file `tests/test_mcp_rejection_episode_capture.py`.

## How to Inspect the Diff
Working tree is UNCOMMITTED — inspect with `git status --porcelain` then
`git diff scripts/mcp_spine_server.py` (not `--name-only`, which hides untracked additions),
plus `git status --porcelain tests/ episodes/` for the new files. Do not use
`git diff main...HEAD`.

## Task Statement
Wire an MCP door refusal so it lands in the durable `episodes/` store instead of vanishing
(issue #541), proven by a real refusal triggered through the door in a fresh process and read
back from the store, with a negative control. Plus the inherited lane-D1-sweep item: replace
the CLI-recommending refusal text.

## Close Criteria
- A real `_spine_bind` (or equivalent door-own) refusal, triggered in a genuinely fresh
  `python3` subprocess (never imported into the reviewing process's own interpreter — verify
  this by re-running the trigger yourself, not by reading the implementer's transcript),
  produces a new episode under `episodes/active/` with all 9 `MECHANICAL_SCALAR_FIELDS` and
  all 5 agent-supplied assertions present, no field missing or placeholder.
- `scripts/query_episodes.py fetch <id>` reads that episode back cleanly (exit 0, all fields
  present).
- With the capture call bypassed, the identical trigger produces NO new file under
  `episodes/active/` (negative control) — the implementer's own claim, re-verify it.
- `grep -n "per-call by construction" scripts/mcp_spine_server.py` returns nothing.
- Every one of the five `agent_supplied` fields, inspected directly in the produced episode
  file, is a literal quotation/extraction of real data — not composed narrative. This is the
  load-bearing check for the design's `capture-is-literal-derivation-only` decision anchor
  (graded `guess`, not yet settled) — read each field and judge whether it reads as invented.
- `_capture_refusal_episode` never raises past `_log_rejection` — inspect the exception
  handling shape (narrow guards inside + one outer broad guard at the call site) rather than
  only trusting the "never crashes" claim; consider whether any code path between the try and
  the writes could still escape.
- Full suite for the touched area green:
  `python3 -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_spine_bind.py tests/test_mcp_identity.py tests/test_mcp_lifecycle.py tests/test_episode_store.py tests/test_mcp_rejection_episode_capture.py`

## Allowed Scope
`scripts/mcp_spine_server.py`, new test file(s) under `tests/`, `episodes/active/*.md` files
produced by the implementer's own acceptance-trigger runs.

## Specific Exclusions
`scripts/checklist_engine.py` (lane H), `docs/**` except `docs/agents/CREW_CONTEXT.md` (lane
D1), `scripts/run_crew.py` (lane F) — confirm none of these appear in the diff. The
`spine_bind` hardlink hole must remain unclosed — confirm the diff does not touch
`_own_checkout_for_binding`'s containment logic itself (only new callers/imports around it
are in scope).

## Constraints the Implementation Must Respect
- Never hand-edit `episodes/**` — only `apply_episode_delta.py --store-root episodes` writes
  it. Grep the diff for any direct write into `episodes/` outside a subprocess call to that
  script.
- `--store-root` passed to the subprocess must be an ABSOLUTE path (via
  `_own_checkout_for_binding() / "episodes"`), never relative — a relative one silently
  resolves against a moving cwd in this module. Verify this in the diff directly.
- `--delta` must be a FILE PATH (this door writes a temp JSON file, mirroring
  `_write_amend_delta`'s existing pattern) — `apply_episode_delta.py` has no inline-JSON mode.
- The `## Mechanical` bin must come from `episode_capture.mechanical_fields()`, not
  hand-constructed field-by-field (the one stated exception: `run`, additionally sourced from
  `_derivable_work_id()` when it returns non-`None` — the implementer's own Workflow Feedback
  explains why; judge whether that reasoning holds).
- In-process dedup: at most one capture per `(tool, rejection_class)` pair per door-process
  lifetime.
- Skip capture (no sentinel run id) when `SPINE is None`.
- `_tool_error`'s exact return shape must be unchanged (the module's own
  `IdentityBindingPinTests` pin) — capture must be a side effect, never a second return path.

## Map Anchors (inbound)
- **Structural:** `scripts/mcp_spine_server.py:_tool_error:797`, `_log_rejection:761`,
  `_capture_refusal_episode` (new), `_own_checkout_for_binding:946`, `_derivable_work_id:1014`,
  `_write_amend_delta:815`, `_THE_CLI_IS_PER_CALL`, `_spine_bind` refusal sites,
  `_identity_violation`; `scripts/episode_capture.py:mechanical_fields:407`;
  `scripts/apply_episode_delta.py:_validate_create:1043`.
- **Capability:** MCP door rejection capture (issue #541); episode store single write path.
- **Constraints:** episode-store-single-write-path; refuse-never-fabricate; no-inode-containment.
- **Decision anchors:** `capture-is-literal-derivation-only` — every synthesized field is a
  literal quotation/extraction, never invented judgment.
  `@grade: guess · leans g1-implement,g1-review · settle: inspect a real captured episode's
  five fields directly and judge whether any reads as invented rather than quoted`
- **Evidence expectations:** the three acceptance-proof items in Close Criteria above.

## Evidence Produced
Full `IMPLEMENTER_RESULT` at `.agent-work/567-e/crew-handoffs/g1-implementer-result.md` —
read it in full. Summary: real refusal triggered in a fresh subprocess produced
`episodes/active/567-e-002.md` (all fields present), read back via `query_episodes.py fetch`,
negative control showed zero new files with capture bypassed, grep confirms the retired
phrase is gone from all 3 sites, 291 passed / 64 subtests / 0 failed on the targeted suite.
Target this gate's evidence at `g1-implement.c1` (the `implementer-result` artifact already
attached) — your own review-result attaches to `g1-review.c1`.

## Suggested Model Tier
stronger — reason: verifying a doctrine-sensitive design (refuse-never-fabricate,
literal-derivation-only) requires judgment about whether specific text reads as "invented"
versus "quoted," not just running commands.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed; the fresh-process trigger or negative
control cannot be reproduced; any agent-supplied field reads as invented rather than literal;
a fenced/excluded file was touched; the suite does not reproduce green.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK). Write it to
`.agent-work/567-e/crew-handoffs/g1-reviewer-result.md` before ending your turn.
