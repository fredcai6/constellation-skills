Three checks at the two ends of a Constellation run could not close. Each is an instance of the epic's central finding: **a check whose signal is identical in the healthy and the defective world.** Two were its mirror — a check that cannot *pass*, which invites a waiver or a doctored verdict. The third turned out to be at risk of becoming **a check that cannot fail** if fixed the way its own issues suggested.

Closes #439
Closes #446
Closes #468
Closes #484
Closes #501
Closes #506

## The three fixes

**A — the Admiral boundary that exits `stop` (#506).** `verify_replan_result` demanded a launch authorization at a boundary whose correct outcome is `stop`, so a run that finished properly could never close its own execute gate. A stop transition is now verified rather than refused, and the relaxation is scoped so `repair` cannot inherit it.

**B — the installed-bundle guard (#501, #468).** `_installed_skills_root()` decided "is this an installed corpus" by asking whether a directory is *named* `constellation-*`. The source repo is named `constellation-skills`, so the guard passed from the repo and resolved to the wrong root; and because a worktree directory is *not* named `constellation-*`, the same guard refused outright in every Commander worktree. Neither answer was about whether an installed corpus is reachable. The decision is now **structural, not nominal**.

**C — the archive PR-reachability check (#439, #484, #446).** The shipped `COMMANDER_SPINE` template's `archive.c2b` carried an unsubstituted `<branch>` placeholder, so it could never pass, and it accepted only an `--state open` PR, so a well-run epic was forced onto `--force`. The token is now resolved at instantiation and the query asks "is there a pull request carrying this work", not "is there an open one".

### One thing we did *not* do

Both #439 and #484 suggest a replacement command that **has a defect verbatim**: `gh pr list --head '<branch>' --state open --json number --jq 'length > 0'` prints `false` and **exits 0**, so a branch with no PR at all sails straight through. Adopting the suggested fix would have converted a check that cannot pass into a check that cannot fail. Instead the exit code carries the verdict, and the `-gt 0` → `-ge 0` mutation is proven to go red.

## Evidence

Four gates, each with an implementer and an independent reviewer. **Two gates blocked and were repaired** — g2 on a mutation leg whose mutated field was legitimately empty, g3 on a stub that answered unmodelled flags instead of refusing. Both are stronger for it.

Every fix carries a **mutation floor**: the fix is reverted and the test must go red. The final gate adds three **composition tests** that run the real shipped artifacts end to end — the real installer lays down a real bundle, the real `init_work_area.py` entrypoint instantiates *that bundle's own* spine template as a subprocess, and the bundle's own verifier runs with `HOME`/`USERPROFILE` pointed at an empty directory so the developer's machine cannot leak in.

The reviewer rebuilt all six broken inputs itself rather than accepting them, asserting each mutation applied **in bytes** before believing any red — this repo is CRLF, and an LF literal silently matches nothing, "succeeds", and certifies a no-op.

The sharpest result: reverting `_is_installed_bundle` to the name test makes the **real installed bundle** return **exit 0** for a `constellation-`-named directory containing no `SKILL.md`. That is #501 reproduced live against the artifact a user actually installs, not against a repo-side fixture. Its second polarity landed in the same run — the `constellation-skills`-named checkout went red *for the wrong reason*, which is itself the proof that asserting the refusal **reason** is load-bearing where an exit-code-only assertion would have passed.

## Suite numbers

| | passed | skipped | subtests | collected | exit |
|---|---|---|---|---|---|
| fork point `aa2038d9` | 1867 | 2 | 829 | 1869 | 0 |
| this branch | 1891 | 2 | 872 | 1893 | 0 |
| `main` (Admiral's measurement) | 1896 | 2 | 829 | 1898 | 0 |

**Delta: +24 passed, +43 subtests, skips unchanged at 2, 0 tests removed.** Attribution — 12 guard (g1), 3 stop (g2), 6 archive (g3), 3 composition (g4). The reviewer re-derived this independently: it cut a throwaway worktree at the fork point and measured 1867 itself, then AST-counted test methods per class at each gate commit; that method validates because its count at `764a2728` is 36, exactly pytest's 1 + 35.

**Expected total after merge: 1898 + (1893 − 1869) = 1922 collected.** This branch merges first, ahead of the held PR.

Coupled suite: 399 passed / 506 subtests, exit 0.

The run's own closure check now passes from the worktree — `verify_iterative_role_artifacts.py commander --work-id w5-gates --skills-root ...` exits 0. Before fix B it *could not*, which was this run's own finding and appears in none of the six issues. The explicit `--skills-root` is load-bearing: without it the check validates against whatever corpus happens to be installed on the machine rather than the branch under review, and would go green or red on machine state no reviewer can see.

## Selector hygiene

Six selectors are load-bearing close criteria across the four gates — `guard_location`, `guard_mutation`, `stop_boundary`, `stop_mutation`, `archive_c2b`, `archive_mutation` — split apart precisely so **no gate's floor can be satisfied by a sibling gate's test**. The reviewer re-derived all six by matched node **identity**, not merely by count, and confirmed no new test matches an old selector.

## Deferred, with reasons

- **#501's boundary-freshness sub-ask is deferred with a falsification, not a shrug.** The stateless variant is *green in exactly the world it was written to catch*: run early, the new boundary has not been logged yet, so the stale boundary **is** the last entry. The only sound variant needs the caller to pass the expected `boundary_id`, and that is inert unless the Admiral spine passes it — which this run does not own. #501's stated Acceptance is met without it.
- After fix A, the **Admiral** spine template's execute prose and directives block still describe `repair` as an enforced exit. Not this run's file; flagged rather than edited, so no cross-crew merge hazard is introduced.

Thirteen triage candidates are recorded in the work area for the Admiral to route.

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01TTKPTbD6nnMt7jFWw9GtjX
