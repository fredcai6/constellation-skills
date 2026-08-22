# Reviewer Handoff

## Gate
g1 (g1-review)

## Survey State Location
`.agent-work/w2-reindex/g1-review/review.json`

## What Was Implemented
A precommit library that makes `map/INDEX.md`/`map/ids.jsonl` correct by construction:
`scripts/code_map/build.py` (a plain-importable `build()` seam, with `cli.py`'s `_build` refactored
to delegate to it), `scripts/code_map/precommit.py` (an index-snapshot mechanism — `git write-tree`
→ `git commit-tree` → `git worktree add --detach` at a unique `tempfile.mkdtemp()` path, builds
from that ephemeral worktree, copies the two built files' bytes back into the real working tree via
plain file I/O, stages exactly the paths that changed, cleans up the ephemeral worktree in a
`finally` block, every subprocess call carries an explicit timeout), and
`scripts/hooks/code_map_precommit.py` (a fail-open shim: any exception including a timeout exits 0,
one diagnostic stderr line on the fail-open/fixed paths, silent on true no-op). Plus
`tests/test_code_map_precommit.py`.

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/569-w2-reindex` (a linked worktree of
`constellation-skills`, branch `epic-569/w2-reindex`) — NOT `git diff main...HEAD`. Use
`git status --porcelain` then `git diff` (tracked) plus the listed new files (untracked, shown by
`git status`, not by `git diff --name-only`):
- New: `scripts/code_map/build.py`, `scripts/code_map/precommit.py`,
  `scripts/hooks/code_map_precommit.py`, `tests/test_code_map_precommit.py`
- Modified: `scripts/code_map/cli.py` (one-line `_build` delegation — read the exact diff, confirm
  it is genuinely a one-line/minimal delegation and not a larger rewrite)

## Task Statement
Build the library making `map/INDEX.md`/`ids.jsonl` correct by construction: the `build()` seam,
the index-snapshot mechanism (never build from the live working tree — from exactly what's about to
be committed), and a fail-open shim. Full original task in
`.agent-work/w2-reindex/crew-handoffs/g1-implement-handoff.md` — read it for the complete pinned
mechanism specification (6 numbered steps), the timeout spec, and the fail-open contract; this
handoff summarizes, that one is the contract.

## Close Criteria
- `scripts/code_map/build.py::build()` produces byte-identical output to today's CLI (`cli.main(["build", ...])`) for this repo's own tree — verify by running both yourself, not by trusting the claim.
- `tests/test_code_map.py` has **zero byte changes** — `git diff -- tests/test_code_map.py` empty.
- `scripts/code_map/discovery.py`, `extract.py`, `render.py` internals untouched (read-only).
- The 6-step mechanism (worktree prune → snapshot via write-tree/commit-tree/worktree-add with a
  **unique** tempfile path every invocation → build → plain-file-I/O copy-back → exact-two-path
  `git add` → cleanup in `finally`) matches the handoff's specification precisely — check the actual
  code, not just that tests pass.
- Every subprocess call in `precommit.py` carries an explicit `timeout=`.
- The fail-open contract: any exception (including a forced timeout) → exit 0, exactly one stderr
  diagnostic line on fail-open/fixed paths, silent on true no-op.
- Every case in Required Evidence below is present, real (against disposable scratch repos, never
  this repo's own git state), and passes.

## Allowed Scope
`scripts/code_map/build.py`, `scripts/code_map/precommit.py`, `scripts/hooks/code_map_precommit.py`,
`tests/test_code_map_precommit.py` (new), `scripts/code_map/cli.py` (one mechanical `_build`
delegation only).

## Specific Exclusions
`scripts/install_constellation.py` (gate 2's job — flag as a BLOCK if touched here),
`tests/test_code_map.py` (any byte — flag as a BLOCK if touched), no real `git commit`/install
against this repo's own `.git/hooks/` (gate 3's job), `generate_spine.py`, `specs/`,
`scripts/checklist_engine.py`, any shipped spine template.

## Constraints the Implementation Must Respect
- Every git call in `precommit.py` goes through an injectable `runner` parameter — no bare
  module-level `subprocess.run` call.
- Stdlib only, no new third-party dependency.
- **Independently re-verify, not just re-read**: re-run the concurrent-invocation test and the
  forced-timeout test yourself (not merely inspect that they exist and pass in the implementer's
  transcript) — the launch order names a prior wave-1 lane where a self-reviewed crew asserted two
  properties were fine and an independent review then found real defects in exactly that kind of
  claim. These two tests carry the mechanism's most safety-critical properties (no corruption under
  concurrent sibling-worktree commits, no hang blocking a commit) — confirm them yourself.
- Read the implementer's Workflow Feedback (in `g1-implement-implementer-result.md`): it reports the
  concurrency test was built as two real subprocess `git commit`-shaped invocations against two
  sibling worktrees (not threading against one shared path, which the implementer found would
  manufacture false hazards — module-level global cross-talk and index-lock contention — that a real
  deployment never hits, since real concurrent commits are separate OS processes on separate
  worktrees with per-worktree indexes since git 2.5). Confirm this reasoning holds and the test as
  written actually exercises the real topology (two worktrees sharing one `.git`), not a synthetic
  stand-in for it.

## Map Anchors (inbound)
This repo's map is DEGRADED-UNPARSEABLE — path anchors:
- **Structural:** `scripts/code_map/` (cli.py, discovery.py, extract.py, render.py — the new
  build.py/precommit.py land here), `scripts/hooks/` (gauge_writer_hook.py — the fail-open
  precedent), `tests/test_code_map.py::MapTreeFreshnessTests` (~line 4656, the protected backstop).
- **Constraints/assumptions:** freshness test unweakened (hard); hook must never fail/block a
  commit (hard); staging auditable to exactly two paths (hard).
- **Decision anchors:** index-snapshot mechanism over skip-on-dirty-sibling, because only the
  snapshot approach is correct on every commit shape.
  `@grade: settled/measured · leans g1-implement,g1-review · settle: this gate's independent
  re-verification of the concurrent/timeout tests is the settlement evidence`

## Evidence Produced
From `IMPLEMENTER_RESULT` (`.agent-work/w2-reindex/crew-handoffs/g1-implement-implementer-result.md`):
`python -m pytest tests/test_code_map_precommit.py tests/test_code_map.py -q` → 161 passed, 65
subtests passed (precommit suite alone: 13 passed, 2 subtests). `git diff -- tests/test_code_map.py`
→ empty. Wiring grep: `build()` called from 2 real sites (`cli.py:91`, `precommit.py:111`); the
shim's own `importlib.import_module` is the only precommit-module reference outside the test file
(expected — gate 2 gives it a real caller). Timing: two full-mechanism runs at 3.77s and 3.25s
(build-only baseline was 2.9s). This evidence targets `g1-integrate.c1`.

## Suggested Model Tier
stronger — reason: verifying concurrency/timeout/fail-open correctness claims independently (not
just re-reading) rewards careful reasoning; this is exactly the class of claim the launch order
warns self-review gets wrong.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, the
mechanism deviates from the pinned 6-step specification without a stated reason, or a policy
decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK) to
`.agent-work/w2-reindex/crew-handoffs/g1-review-reviewer-result.md` before ending your turn.
