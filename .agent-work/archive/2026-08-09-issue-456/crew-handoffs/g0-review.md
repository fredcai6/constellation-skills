# Reviewer Handoff — gate `g0`

Issue #456. Gate `g0`: package, CLI and discovery — the prototype behind a real
entrypoint. First of eleven gates.

## Task statement

Review the `g0` implementation: does it meet the gate's close criteria, honor its
constraints, and stay inside its scope? Return `APPROVE` or `BLOCK` with
findings.

The gate was delivered across **three implementer passes** against one job file.
Passes 1 and 2 each stopped at a context trip and filed a refresh-request rather
than pushing through; pass 3 closed it. That is expected shape, not a defect —
do not treat the multi-pass delivery as a finding.

## How to inspect the diff

```bash
cd C:/Programs/constellation-skills/.claude/worktrees/issue-456
git log --oneline 6ae6193..HEAD
git diff 6ae6193..HEAD -- scripts/ tests/ .gitignore
```

`6ae6193` is the last commit before this gate began. Restrict the diff to
`scripts/`, `tests/` and `.gitignore` — the `.agent-work/` churn is run
bookkeeping and is not under review.

**Two things in history you must not mistake for defects:**

1. **The `map/` tree appears in commit `d236f22e` and is removed in the very next
   commit.** That was the Commander's own mistake — a `git add -A` swept the
   3,636-page tree in, and it was untracked again immediately with
   `git rm -r --cached` rather than by rewriting pushed history. **Current state
   is correct: `git ls-tree -r HEAD -- map/` returns nothing, and `map/` is
   untracked on disk.** It is staged at gate `gs`, deliberately last, so the
   intermediate gate diffs stay reviewable.
2. **`tests/test_mutation_floor.py` changed** and is *not* part of this gate's
   feature scope. It is a two-line fix for a false red (`tc3`) that blocked the
   "full suite green" constraint at every gate boundary. Ruled a fix-now by the
   Commander and surfaced to the human. In scope to sanity-check, not to
   re-litigate.

## The three implementer results

- `.agent-work/issue-456/crew-handoffs/g0-implement-RESULT.md` (pass 1)
- `.agent-work/issue-456/crew-handoffs/g0-implement-RESULT-pass2.md`
- `.agent-work/issue-456/crew-handoffs/g0-implement-RESULT-pass3.md`

Handoffs that governed them: `g0-implement.md`, then `g0-implement-ADDENDUM.md`
and `g0-implement-ADDENDUM-2.md`.

## Close criteria to check

1. The CLI runs **extract → render end to end** on this repo and exits 0.
2. The discovery layer enumerates **exactly the mappable corpus** with
   `.agent-work/` excluded.
3. **A test fails if the exclusion is removed.** Load-bearing.
4. The **bundling question is resolved on the record**, not deferred.
5. The **full suite is green** at the gate boundary.

## Constraints to check

- **Stdlib only.** CI installs pytest and coverage and nothing else. A single
  third-party import means the tool cannot run at all. Check every new module.
- **Nothing committed carries a position.**
- **The run report carries no timings** (so a determinism diff can cover it).
- `.gitignore` entries are **narrow, one file per line** — not a blanket
  `.code-map/` rule, because `map/` IS committed later and a later gate may add a
  store that must be reviewed.
- **No defect fixes and no schema changes in this gate.** D1 (line base) is `g3`,
  D2 (symbol identity) is `g2`, D3 and BOM are `g8`.
- `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are **READ-ONLY**.

## Evidence already produced — reproduce it, do not take it on trust

The Commander already re-ran all of this independently. **Your job is to check it
again in your own hands**, and to look for what neither of us checked.

| Claim | Where |
|---|---|
| Full suite `1706 passed, 2 skipped, 0 failed` (baseline was 1688) | pass-3 result |
| Exclusion mutation turns **4** tests red, green when restored | pass-3 result |
| 76 new symbols, 178 external call sites, 75 of 76 wired | pass-3 result |
| End-to-end build → `.code-map/statements.jsonl` (24 MB) + 3,635 pages | verified by Commander |
| 112 files / 3,523 entities vs a 103-file baseline (+9 = this gate's own new `.py` files) | verified by Commander |
| No timings in any of the three run reports | verified by Commander |

**Two environment traps that will waste your time if you do not know them:**

- The shell exports **`FORCE_COLOR=3`**. Pass `--color=no` to pytest whenever you
  intend to grep its output, or your greps silently match nothing.
- The shell exports **`PYTHONIOENCODING=utf-8:surrogateescape`**, which makes
  `tests/test_crew_launcher.py::LaunchTests::test_records_entry_before_launch_and_completes`
  fail. That is filed as `tc7` and is **not this gate's doing** — `run_crew.py`
  deliberately honors an ambient value and the test fails to isolate it. Clear
  the variable to get the honest full-suite number.

## Already ruled — CHECK these, do not re-raise them as findings

The Commander decided each of these on the record. If you disagree, say so as a
**noted disagreement with reasoning**, not as a blocking finding.

1. **`NON_INSTALLABLE_PACKAGES` has zero production call sites** — only the four
   guard tests reference it. **Accepted** (`e-execute-6`): it is a policy
   declaration whose enforcement point is the test suite by design. The correct
   runtime behavior for a non-installable package is to do nothing, so no
   production path *could* consult it. It satisfies the repo's two-bin rule
   (checked by a command), and it is falsifiable — emptying it turns 3 of the 4
   guards red. **Verify the falsifiability claim; do not re-argue the ruling.**
2. **Four prototype modules ported, not six.** `render.py` and `render_fn.py` are
   superseded by `render_map.py`, whose own header states it is a self-contained
   adaptation of `render_fn.py`. Porting them would create symbols nothing calls.
3. **Artifact paths:** stores to `.code-map/`, page tree to `map/`. Render does
   `rmtree(map/)`, so intermediates must not live under it.
4. **Two store ignore entries, not three** — no gate produces a position cache,
   and an ignore rule for a file nothing creates is the stale line `g3` exists to
   remove. Plus three run-report entries.

## What I most want your eyes on

The Commander verified the *claims*. Look for what neither pass checked:

- **Stdlib-only, mechanically.** Actually grep the imports of all 8 new modules.
  This is the constraint that silently kills the tool in CI.
- **Does the ported extractor behave like the prototype**, or did something drift
  in the move? The prototype hardcoded an external `ROOT`; there is no prior
  behavior to diff against, so this needs reading, not diffing.
- **Is the discovery exclusion the *only* thing separating corpus from scratch?**
  If a second path can leak scratch in, the falsifier passes while the rule is
  incomplete.
- **Do the guard tests actually hold every `scripts/` subdirectory**, or only the
  ones that exist today? A guard that enumerates one side never sees what exists
  only on the other.
- **Anything that looks like a check that cannot fail** — a test whose output is
  identical in the healthy and the defective world.

## Return format

Return `REVIEW_RESULT`: verdict (`APPROVE` / `BLOCK`), findings with severity and
file:line, close criteria assessed one by one, constraints assessed, evidence you
reproduced (with output), out-of-scope observations, and workflow feedback.

Write it to `.agent-work/issue-456/crew-handoffs/g0-review-RESULT.md`.

**Return thin, write fat** — your message is the verdict, the deciding evidence,
and the path. **Deliver it via `SendMessage` before ending your turn.**

**A `BLOCK` is a legitimate, welcome outcome.** This is the first of eleven gates
and everything downstream builds on it; a defect caught here is far cheaper than
one caught at `gs`. Do not soften a real finding to be agreeable.
