# Baseline — both defects reproduced before any change

Measured against unmodified HEAD `42df99fd` (this worktree, before this run's edits).

## Suite count, this worktree

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

`2932 passed, 3 skipped, 1121 subtests passed in 117.83s` — matches the handoff's stated
baseline exactly.

## Defect 1 — reproduced in a foreign checkout

Created a detached scratch worktree at `42df99fd` (`git worktree add --detach <tmp> HEAD`,
removed after capture) and ran the one test:

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 \
  python -m pytest -q tests/test_spine_lifecycle.py -k TestWorktreePathForRealWorktree
```

```
FAILED tests/test_spine_lifecycle.py::TestWorktreePathForRealWorktree::test_reproduces_this_runs_real_worktree
AssertionError: assert PosixPath('/home/tommy/projects/constellation-skills-wt/c3-lifecycle') == PosixPath('/tmp/tmp.Ub0TDwcEld/foreign-checkout')
```

Confirms the handoff's claim: the test hardcodes `"epic-559/c3-lifecycle"` and only passes
from a checkout literally at `<primary>-wt/c3-lifecycle`.

## Defect 2 — reproduced against a work area carrying a gitignored entry

`init_work_area`-shaped fixture, plus `.gitignore` matching `mcp_calls.jsonl` (committed,
same as the real repo's rule), plus that file written beside the spine — reproducing what
the MCP door leaves behind. Ran unmodified `close_work` against it:

```
git add /tmp/repro-close-work-defect2/.agent-work/w1/mcp_calls.jsonl failed in /tmp/repro-close-work-defect2:
The following paths are ignored by one of your .gitignore files:
.agent-work/w1/mcp_calls.jsonl
hint: Use -f if you really want to add them.
hint: Turn this message off by running
hint: "git config advice.addIgnoredFile false"
```

State after the raise — the work area split across two directories, exactly as the handoff
describes (no rollback):

```
.agent-work/archive/2026-08-12-w1/crew-handoffs/note.md   <- already moved
.agent-work/archive/2026-08-12-w1/evidence                <- already moved
.agent-work/w1/mcp_calls.jsonl                              <- stranded, original location
.agent-work/w1/spine.json                                   <- stranded, original location
.agent-work/w1/triage-candidates                             <- stranded, original location
```

Both defects confirmed reproduced against unmodified code before any fix was applied.

**Process note (see Workflow Feedback in IMPLEMENTER_RESULT.md):** this file was written
*after* the fixes were already implemented in the working tree, not strictly before, because
the gate's instruction to write BASELINE.md before changing anything was not caught until
mid-implementation. The reproduction above is still against unmodified `HEAD` (the fixes are
uncommitted working-tree edits; a detached worktree from `HEAD` and a fresh script run
against unmodified `close_work` both reflect pre-fix behaviour), so the evidence is genuine
and pre-change, but the ordering of *when* it was captured relative to *when* it was written
does not match the gate's literal sequencing.
