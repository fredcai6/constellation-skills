# Review Result

## Assigned Gate
`w3b-461-review / g1-review` (independent reviewer, epic #418 wave 3, PR #490, issue #461)

## Result
`APPROVE`

## Handoff compliance
The change narrows `test_canon_episode_store_untouched` from a single `git status --porcelain
episodes/` read (which conflates worktree-vs-index with index-vs-HEAD) to the named pair from
LO-461's `decision:worktree-vs-index-only` — `git diff --name-only episodes/` (tracked-but-unstaged)
and `git ls-files --others --exclude-standard episodes/` (untracked) — each asserted separately so a
failure names which half tripped. The docstring was rewritten to state the worktree-vs-index property
the code now actually tests. All within the assigned scope; nothing beyond it.

## Scope drift
`git diff c0ad5ecd..fa1378ed --stat` shows exactly two files: `tests/test_episode_negative_control.py`
(the crew's owned file) and `.agent-work/epic-418-redux/notes-461.md` (its own notes file). Nothing
under `episodes/`, nothing in `scripts/apply_episode_delta.py`, nothing in the sibling-owned files
(`skills/constellation-reviewer/**`, `scripts/checklist_engine.py`,
`scripts/hooks/gauge_writer_hook.py`, `tests/test_verify_spec_confirmed.py`,
`tests/test_gauge_writer.py`). Within the owned test file, only the one target test function changed;
the rest of the module (blob-OID checks, the #321 test) is untouched, matching the launch order's
explicit exclusion. Fences held.

## Evidence verdict
Re-derived empirically rather than accepted from the crew's pasted transcript, per the review brief's
explicit instruction ("green is what the broken version already does").

- **Stray unstaged write** to a tracked file under `episodes/active/`: the fixed test **FAILED** —
  `AssertionError: canon episode store has unstaged edits: episodes/active/b433-render-directives-001.md`.
  Reverted via `git checkout --`; confirmed clean.
- **Stray untracked file** under `episodes/active/`: the fixed test **FAILED** —
  `AssertionError: canon episode store has untracked files: episodes/active/reviewer-stray-461.md`.
  Removed; confirmed clean.
- **Staged-but-uncommitted legitimate capture** (`git add episodes/active/reviewer-legit-461.md`, no
  commit): the fixed test **PASSED** (`1 passed`).
- **Regression check against the pre-fix code**: with that exact same staged state left untouched, I
  swapped in the pre-fix test body (`git show c0ad5ecd:tests/test_episode_negative_control.py`) and
  reran — it **FAILED** with `AssertionError: canon episode store is dirty: A  episodes/active/reviewer-legit-461.md`,
  the identical `A  episodes/active/...` shape the issue quotes from #447 g4. This is the decisive
  check: it proves the test is not a no-op fix that passes identically before and after — the old code
  really breaks on exactly this scenario, and the new code doesn't.
- Restored the fixed test file (`git checkout --`), unstaged and removed the capture file;
  `git status --porcelain episodes/` and the test file were empty before, between, and after every
  probe.
- **Full suite**, independently re-run: `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` →
  `1782 passed, 2 skipped, 683 subtests passed in 539.59s (0:08:59)`, **exit 0** (`${PIPESTATUS[0]}`,
  not the pipe's own code). Matches the crew's claim and the wave-2 baseline exactly — no drift.

## Code/doc quality
Docstring and predicate agree: the docstring states "The property is worktree-vs-index, and only
that," names both git reads, and explains why the old single-read predicate over-fired — matching
`decision:docstring-and-predicate-agree`. `decision:preserve-anti-vacuity` untouched: the
`len(tracked) >= 2` and `any(name.endswith(".md"))` non-emptiness asserts are byte-identical to before,
still ordered ahead of the worktree-vs-index checks. Subprocess calls keep `text=True,
encoding="utf-8"` per `CREW_CONTEXT.md`'s Windows-encoding rule.

**Fowler refactoring pass** (`.agent-work/w3b-461-review/g1-review/fowler-pass.json`,
`verify_fowler_pass.py` exit 0): 12 smells rendered, 11 absent, 0 overridden, 1 **flagged
(non-blocking)** — `duplicated-code`: the two new `subprocess.run(...).stdout.strip()` /
`assert ... == ""` blocks share an identical shape. Not blocking: they run genuinely different git
commands answering different halves of the worktree-vs-index question, and keeping them as separate
statements gives each its own assert and its own failure message naming which half tripped — worth
more here than deduplicating four lines into a helper.

## Map impact verdict
Trivial local edit (one test's assertion + docstring); no structural, capability, constraint, or event
impact on the recorded architecture. `episodes/`'s write path (`scripts/apply_episode_delta.py`) and
its governing doctrine (`docs/agents/ORCHESTRATOR_CONTEXT.md`) are untouched. No Map Impact notes were
claimed or required.

## Reconciliation check
None. No architecture-significant change.

## Blockers
- none

## Out-of-scope observations
- Fowler `duplicated-code` on the two new assert blocks (see Code/doc quality) — non-blocking, noted
  for awareness only.
- Carried from the crew's own notes (`notes-461.md`, `tc2`): other call sites in this repo that shell
  out to `git status --porcelain` as a cleanliness gate may carry the same worktree-vs-index /
  index-vs-HEAD conflation this issue fixed. Not searched for in this review — flag for a future sweep.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: `REVIEW-BRIEF-w3.md` and `LO-461.md` together gave
  enough to construct the regression check (swap in the pre-fix test body against the identical staged
  state) without further interrogation.
- **Context rediscovered:** none — confirmed after review: `REPO_ROOT` in the test file resolves via
  `Path(__file__).resolve().parents[1]`, so swapping the pre-fix test body back into the *same* file
  path (rather than copying it elsewhere) was necessary to keep `REPO_ROOT` correct; worth naming
  explicitly in a future brief for reviewers less familiar with the fixture.
- **Instructions improvised around:** the review brief's regression-check instruction says "check out
  the pre-fix version of the test and observe that same state fail" without specifying mechanics on
  Windows; I used `git show c0ad5ecd:tests/test_episode_negative_control.py > tests/test_episode_negative_control.py`
  followed by `git checkout -- tests/test_episode_negative_control.py` to restore, rather than a
  branch/stash dance, since the worktree already sat at the PR head with a clean tree throughout.
- **What would have made this easier:** none.

## Return status
`complete`
