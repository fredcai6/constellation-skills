# Reviewer Handoff — batch A + B

Independently review `efe92791..99a46a08` on `afk/20260821-ab`. Strict APPROVE or
BLOCK. Do not edit source, tests, or any commit.

## Standing criterion

No bad actors. The only adversary is an honest agent about to make a mistake.
**Ease of use is the success measure** — if these changes make the tools harder
to use, that is a finding, not a nitpick.

## What the batch is for

`_is_stale` existed, worked, and was called in four places — none of them a
rendering path. So the engine printed `LEASE active` and `RAIL: ... Run it.` over
plans whose owners had been dead for weeks. All 58 active leases in this
checkout are stale. The batch stops the system instructing honest agents into
that mistake, and removes two pieces of friction.

## Where to spend most of your time

### B2 — `--parent` required. This is the highest-risk change in the batch.

Roughly **75 initial test failures** across four files were repaired using
**three scripted AST patches plus four hand-rewritten tests**. A scripted edit
across a test corpus is exactly where a silently weakened assertion hides, and a
green suite will not tell you.

- Audit the four hand-rewritten tests **individually**, against their base
  versions. Their premise was the old "works with no parent" behavior. Confirm
  each still tests something real, and that the rewrite did not just delete the
  inconvenient assertion.
- Diff every test the AST patches touched. Confirm the patches added a `parent`
  argument and changed nothing else — no assertion removed, weakened, or
  inverted.
- Confirm the new refusal actually fires and its message says what to pass.
- Confirm `--resume`, `--abandon` and `--verify-result` still work; the
  Implementer put enforcement at `CrewSpec.__post_init__` rather than argparse
  specifically to keep those paths intact. Verify that claim.

### B1 — `waive` exempted at the session gate

Three things must all hold, and the second is the trap:

- A cross-session waive now succeeds in one call, not five.
- **The waiver is still journaled.** `waive` had to stay in `MUTATING_VERBS`
  because line 3788 reads that set to decide journaling. If it was removed from
  the set, the audit trail is silently gone — check the set membership directly.
- The `PreToolUse` self-waive denial still works unchanged. It implements a
  verbatim human ruling ("agent cannot waive itself; commander waives crew,
  admiral waives commander").

## The rest

- **A1** — `current` removed from `RAIL_VERBS`. The five `_RAIL_STRINGS` must be
  **byte-identical** to base; they are frozen as a measurement precondition for
  #145. Verify by diff, not by reading.
- **A2** — archived-path banner and rail suppression. It is a path fact and must
  make no liveness claim.
- **A3 / R1** — **two** renderers now share one shape: `checklist_engine._lease_line`
  and `spine_rail.reconstruct_current`. Confirm neither emits a verdict word —
  age only. `_format_age` is deliberately duplicated rather than imported
  because `spine_rail.py` is stdlib-only by documented design; confirm that law
  is real and that the arithmetic genuinely matches. There is a regression
  pinning the two renderers against each other — confirm it would actually fail
  if one drifted.
- **A4** — `next (for the holder):` when a lease is held.
- **A5** — staleness gate on `_scan_active_spine`, so SessionStart stops
  injecting "Pick the run back up..." for dead runs. **Confirm the owner's own
  resume path is not broken by this** — that is the obvious way to get A5 wrong.
- **A6** — `require_session`'s refusal no longer routes callers into #632 and
  #369. Judge the new text as a message an agent must act on, not as prose.
- **Map commit `99a46a08`** — must be `map/INDEX.md` alone, entity counts and
  module listings only, nothing structural.

## Evidence to reproduce

- Full ordinary suite. The Implementer reports **3469 passed, 6 skipped, 1224
  subtests, zero failures**. Base at `efe92791` was 3447/6/1222.
- `git diff --check efe92791..99a46a08` exits 0.
- The before/after render against a stale lease, on both renderers.

## Scope

Allowed: `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
`scripts/run_crew.py`, their tests, `map/INDEX.md`, and `.agent-work/20260821-ab/`.

**BLOCK if anything else moved.** In particular `skills/charter/*`,
`skills/_shared/global-everyone.md`, and `tests/data/store_mentions.approved.txt`
are the human's own uncommitted work in the main checkout and must not appear in
this branch's diff at all.

Also confirm option C (lease demotion) and the R9/R10 leaseless hole were **not**
implemented — both were deliberately excluded.

## Workspace

Worktree `/tmp/constellation-20260821-ab`, branch `afk/20260821-ab`, base
`efe92791`, head `99a46a08`. Do not call any `mcp__spine__*` tool. Do not commit,
push, or open a PR.

## Result

`.agent-work/20260821-ab/crew-handoffs/ab-reviewer-result.md` — verdict, findings
by severity, exact commands and outputs, per-item verdicts for A1-A6 and B1-B2,
your B2 test audit in detail, and workflow feedback.
