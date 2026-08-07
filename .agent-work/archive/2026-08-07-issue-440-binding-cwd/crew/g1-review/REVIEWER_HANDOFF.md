# Reviewer Handoff

## Gate
`g1` (issue #440, epic-418 workstream A2). Worktree `C:/Programs/constellation-skills-wt/epic418-a2-440`, branch `epic-418/a2-440-binding-cwd`, base `cbd9aee`. Use absolute paths — your shell's cwd resets between calls.

## What was implemented

`scripts/hooks/spine_rail.py` used to resolve a relative `--file` by joining it onto the hook
payload's `cwd` and trusting the result. The payload's `cwd` is the **session launch directory** and
is identical for a parent and all its subagents, so an agent working in a git worktree bound a
same-named path inside the **main checkout** — measured 2026-08-05 as **60 of 64 live entries**. The
gauge writer then wrote its context reading into a phantom `.agent-work/<work_id>/` there while the
engine read the worktree's copy, and the context governor never fired.

It now walks an ordered ladder of candidate roots and takes the first that **validates as a
checklist**, recording which rung won in a new `path_source` field:

| Rung | Base | `path_source` |
|---|---|---|
| 0 | `--file` already absolute | `absolute` |
| 1 | absolute `--worktree <dir>` in the observed command | `worktree_opt` |
| 2 | last `cd` / `pushd` / `Set-Location` target in the command text | `cd_target` |
| 3 | payload `cwd` (the old behaviour) | `payload_cwd` |
| 4 | a git worktree root registered against `project_dir` | `git_worktree` |
| 5 | `project_dir` | `project_dir` |

No candidate validates → **bind nothing**. `release` resolves against its own recorded binding first,
so it still removes what its claim wrote even after the spine file is gone.

## How to inspect the diff

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440
git diff --stat
git diff scripts/hooks/spine_rail.py
git diff tests/test_spine_rail.py
```
Two files: `scripts/hooks/spine_rail.py` (+294/−13), `tests/test_spine_rail.py` (+614). Nothing is
committed yet. The implementer's own account is at
`.agent-work/issue-440-binding-cwd/crew/g1-implement/IMPLEMENTER_RESULT.md` — read it, but **do not
take it as evidence.** Reproduce.

## Task statement (what the gate was asked to achieve)

An agent working in a git worktree must bind **its own worktree's** spine, and the store must never
record a confident wrong path. The full handoff is at
`.agent-work/issue-440-binding-cwd/crew/g1-implement/IMPLEMENTER_HANDOFF.md`.

## What to attack — this is the substance of the review

Four questions. Answer each from evidence you produced yourself, and say which command produced it.

**1. Can the new tests actually fail?** This is the highest-value question in the review. The defect
being fixed is one where the old code returned a *plausible-looking wrong answer*, which makes it
very easy to write a test that could never have failed. The implementer claims it demonstrated RED
by `git stash`-ing the fix and running the new tests against the pre-change code. **Reproduce that
yourself**: stash `scripts/hooks/spine_rail.py` back to `cbd9aee` (leave the new tests in place),
run the new tests, and confirm they fail — and that they fail for the *right reason* (the binding
naming the main-checkout path), not because of an import error or a missing symbol. Restore
afterwards and confirm the tree is back. **A test that passes both before and after is a finding.**

This epic has filed three separate issues in the can't-fail-test family (#432, #446, and a finding
inside #419's own run). Check specifically that **no test hand-injects the root it claims to prove
the hook derives** — not via a payload field, not a fixture attribute, not an env var. The rung-4
integration test is the one that matters most here: it should use a real `git init` + `git worktree
add` on disk and run the hook in a **fresh subprocess**.

**2. Can "first validating candidate wins" pick the WRONG root?** Construct the adversarial case
yourself rather than reasoning about it: two roots that both hold a valid checklist at the same
relative path. Which wins, and is that the right one? Consider in particular that the *old bug has
been seeding phantom `.agent-work/<work_id>/` directories inside the main checkout* — check whether
one of those can decoy the ladder. Check what "validates as a checklist" actually tests and whether
something that is not a checklist can pass it.

**3. Can any new code path raise, block, or hang inside PostToolUse?** `handle_post_tool_use` must
return `{}` on every path and never raise. New failure surfaces include the git subprocess (absent
`git`, locked index, network path, `dubious ownership` refusal), JSON parsing of candidate files,
and path normalization on malformed input. Confirm the git probe is bounded by a timeout, that it
does **not** run on the common path, and that both `TimeoutExpired` and `OSError` are handled.

**4. Were 14 existing tests weakened?** The implementer reports that 14 pre-existing tests had
fixtures that never actually wrote a spine file to disk, so validate-or-bind-nothing broke them, and
it reseeded those fixtures to write real files. **Verify that claim directly.** For each existing
test the diff touches, decide: was the *fixture* strengthened (now writes a real file), or was an
*assertion* weakened / a case deleted to make the new code pass? The second would be a BLOCK. Read
`git diff tests/test_spine_rail.py` for deletions, not just additions.

## Close criteria the gate must meet

- A worktree-dispatched agent's relative-`--file` claim binds the **worktree's** spine.
- Rung 4 is proven against a real `git worktree` on disk in a fresh subprocess, with no injected root.
- No candidate validates → no entry written, store byte-unchanged.
- `release` removes its own entry, including when the spine file was deleted in between.
- `handle_post_tool_use` returns `{}` on every path and never raises.
- The git probe is off the common path and bounded.
- `python -m pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q` green; no existing
  assertion weakened.

## Allowed scope of the change (anything outside this is a finding)

`scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`, and — only if the additive `path_source`
field tripped a fixture — a minimal reconciliation of `tests/test_gauge_writer.py` (the implementer
reports it did not need this).

## Specific exclusions the change must NOT have touched

- The binding **key** shape: `session_id` / `session_id#agent_id` / `None`, and `binding_key()`
  itself (owned by #419; a load-bearing interface).
- `scripts/hooks/gauge_writer_hook.py`'s read side; `scripts/checklist_engine.py`'s trip bands.
- Anything requiring #269 (fixed `CLAUDE_PROJECT_DIR`) to change.
- The three other known limits in `docs/GAUGE_WRITER_HOOK.md` (no reaper for abandoned keys, no lock
  around load-modify-save, no validation of a shell-mangled `--file`).
- The live main checkout's `.agent-work/.spine-rail-binding.json` and any real `.claude/settings*.json`.

Confirm each of these is untouched; do not just take the implementer's word.

## Constraints on you

- Use `python`, **never** `py` — `py` on this box resolves to a runtime with no pytest and produces
  fake failures.
- Do **not** run the full suite (7 minutes); the Commander runs it at g3.
- Do **not** modify `scripts/hooks/spine_rail.py` or the tests. You review; you do not fix. If you
  stash to reproduce RED, **restore the tree and verify it is restored** (`git status`, `git diff --stat`).
- Do **not** touch the live main checkout's binding store or any real `.claude/settings*.json`.
- Do not commit.

## Map anchors (inbound)

No architecture map exists in this repo (`DEGRADED-NO-MAP`). The hash-pinned substitute is
`docs/GAUGE_WRITER_HOOK.md` — read "Known limits of the binding store itself (#419)"; its first
bullet is this defect. Note the doc is now **stale by design** (it still states the defect as live);
the Commander fixes it at a later gate, so **staleness of that doc is not a finding for you**.

Decision anchors governing this gate:
- `fix-the-resolution-not-the-caller` `@grade: settled/measured` — the fix belongs in the resolution.
- `not-fixing-269` `@grade: settled/human` — out of scope, do not propose it.
- `existence-verified-resolution` `@grade: guess · settle: the two-arm live fire at g2` — the ladder
  itself is still a guess and this review is part of what tests it. Attack it freely.

## Evidence the implementer produced (reproduce, do not trust)

- Rung-4 real-worktree fresh-subprocess test: binding named the worktree spine, `path_source:
  "git_worktree"`; against the stashed pre-change hook, 4 failed with the phantom main-tree path.
- A worktree-dispatched claim demo binding `path_source: "cd_target"` and avoiding a same-named decoy.
- `python -m pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q` → `169 passed`, exit 0.
  `test_spine_rail.py` 74 → 102 tests.
- Wiring grep: every new symbol has ≥1 external production call site; `_resolve_abs` deleted.

## Return format

Write `REVIEW_RESULT` to
`C:/Programs/constellation-skills-wt/epic418-a2-440/.agent-work/issue-440-binding-cwd/crew/g1-review/REVIEW_RESULT.md`
**before you go idle**, and also deliver it as your final message. It must carry:

- **Verdict: APPROVE or BLOCK** (one of those two words, exactly).
- A per-question answer to the four attack questions above, each naming the command you ran.
- Findings, each with severity and file:line.
- Anything out of scope you noticed (for the Commander's triage), kept separate from findings.
- Workflow feedback: what in this handoff or the workflow made the review harder than it needed to be.
