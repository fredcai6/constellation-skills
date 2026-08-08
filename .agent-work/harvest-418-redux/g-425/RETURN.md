# RETURN — impl-425-file-defects (issue #425, epic #418 workstream G)

## 1. Verdict

Asked to file the triage-candidate defects the explore-post-phase1 spec pushed out of scope, per issue
#425, plus three additional candidates the Admiral observed live on epic #418's own run and ruled
in-scope for this filing pass. Filed all nine: five new issues (#427–#431) and four comments on
existing issues (#235, #346, #290, #315), each linking back to the spec of record's Out of scope
section. No fix was applied to any of them, per the file-do-not-fix ruling. This is a clean win, not
a measured negative — every named candidate now has a tracker reference, and none turned out to be an
undetected duplicate.

## 2. Evidence

Isolation check (below) exited 0. All nine tracker writes succeeded (`gh issue create` /
`gh issue comment`, real URLs returned, pasted below). No PR: the mission produced no code change, so
there is nothing to open one for, as the launch order anticipated. `git status --short` in the
worktree is empty and the branch is `epic-418/g-425-file-defects` as provisioned.

**New issues filed:**

| Candidate | Source | Issue |
|---|---|---|
| Engine refusals counter records zero for pre-lease refusals | #425 / exc-9 | [#427](https://github.com/fredcai6/constellation-skills/issues/427) |
| `verify_spec_confirmed.py --phase review` unpassable by construction | #425 | [#428](https://github.com/fredcai6/constellation-skills/issues/428) |
| `file_issue_set.py` `--body` WinError 206 on Windows | #425 (checked: not already carried elsewhere) | [#429](https://github.com/fredcai6/constellation-skills/issues/429) |
| `.spine-rail-binding.json` junk key + `_scan_active_spine` first-glob-match stale-lease shadowing | Admiral, live on epic #418 | [#430](https://github.com/fredcai6/constellation-skills/issues/430) |
| HARD trip freezes `DIGEST` the forced handoff depends on | Admiral, live on epic #418 (B/#420 cross-reference pending, Admiral's call) | [#431](https://github.com/fredcai6/constellation-skills/issues/431) |

**Comments posted on existing issues:**

| Candidate | Issue | Comment |
|---|---|---|
| Stop-rail refresh-request blindness (#235 shape) — confirm-seam occurrence + epic #418's own occurrence | [#235](https://github.com/fredcai6/constellation-skills/issues/235) | [comment](https://github.com/fredcai6/constellation-skills/issues/235#issuecomment-5198460001) |
| `constellation-diagnose` registration defect — reproduction | [#346](https://github.com/fredcai6/constellation-skills/issues/346) | [comment](https://github.com/fredcai6/constellation-skills/issues/346#issuecomment-5198460206) |
| 12/19 skills missing `invoker:` tags — re-confirmation | [#290](https://github.com/fredcai6/constellation-skills/issues/290) | [comment](https://github.com/fredcai6/constellation-skills/issues/290#issuecomment-5198460378) |
| Command checks run without a set working directory — confirmation | [#315](https://github.com/fredcai6/constellation-skills/issues/315) | [comment](https://github.com/fredcai6/constellation-skills/issues/315#issuecomment-5198460547) |

**Full candidate table (per the Return Shape's required format), against #425's own list plus the
three live-observed additions and the "already carried?" check:**

| # | Candidate | Disposition | Result |
|---|---|---|---|
| 1 | Engine refusals counter zero pre-lease (exc-9) | new issue | #427 |
| 2 | `verify_spec_confirmed.py --phase review` unpassable | new issue | #428 |
| 3 | `file_issue_set.py` `--body` WinError 206 | new issue | #429 |
| 4 | Stop-rail refresh-request blindness (#235 shape), all occurrences incl. confirm-seam + epic-418's own | comment | #235 |
| 5 | `constellation-diagnose` registration defect | comment | #346 |
| 6 | 12/19 skills missing `invoker:` tags | comment | #290 |
| 7 | Command checks run without set cwd | comment | #315 |
| 8 | `.spine-rail-binding.json` junk key + `_scan_active_spine` glob-order shadowing | new issue | #430 |
| 9 | HARD trip freezes DIGEST | new issue | #431 |

Note on item 3: the launch order separately asked me to "confirm whether #425 already carries this
one" for the WinError 206 candidate — it does; #425's own body names it as one of its three new
issues, so #429 is that filing, not a duplicate check that produced a different answer.

Pre-existing-issue searches run before each new filing (`gh issue list --search ...` /
`gh issue view <n>`) turned up no duplicates for items 1, 2, 3, 8, 9. Item 1 is related to but distinct
from #367 (documented in #427's body: #367 is a cross-session over-count, this is a pre-lease
under-count — same counter, different mechanism, neither fix subsumes the other).

## 3. Isolation proof

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/epic418-g-425
worktree OK: in C:/Programs/constellation-skills-wt/epic418-g-425
EXIT:0
```

## 4. Scope-discipline report

No code was opened for repair at any point — the mandatory "file, not fix" ruling was observed
throughout. Each new issue body states its fix shape in prose (for the maintainer's benefit) but
explicitly notes the fix was not applied, per the ruling. No corner case was chased beyond what each
candidate's own source (spec, issue #425 text, or the Admiral's live-observed ruling) already
specified — nothing in this pass required judgment calls about *what* to file, only *whether* a
duplicate already existed, which was checked by search for every item.

One judgment call, within inherited latitude (issue filing/commenting is delegated): for the
DIGEST-freeze candidate (#431), the launch order flagged that workstream B (#420) might claim it as
already inside its channel-completeness scope. I filed it now regardless — per
`decision:one-ref-per-candidate`, filing is not optional pending another workstream's read — and noted
the pending cross-reference in the issue body itself, leaving the "B claims it → cross-reference
instead of standalone defect" determination explicitly to the Admiral, as the launch order specifies
that channel runs B-to-Admiral, not B-to-G.

## 5. Map impact

None. No source files changed; nothing for an architecture reconcile to pick up.

## 6. Triage candidates

None beyond what was already in scope for this mission. I did not go looking for new defects outside
the two source lists (issue #425 and the launch order's three additions).

## 7. Workflow feedback

- The `_COMMON.md` / launch-order warning about `gh issue create --body` failing with WinError 206 on
  Windows for bodies over ~32K is exactly right, and mildly ironic given that WinError 206 defect
  (#429) is itself one of the candidates this mission filed. All bodies here were short enough that
  `--body-file` was not strictly required to avoid the failure, but I used `--body-file` throughout
  anyway rather than `--body`, both as the documented-safe pattern and to avoid re-deriving the
  workaround under time pressure if a body had turned out longer than expected.
- The launch order's request to "confirm whether #425 already carries this one" for the WinError 206
  candidate was easy to resolve because #425's own issue body is short and directly enumerable — worth
  noting as a positive: #425 was well-formed enough that no ambiguity arose about what it already
  named versus what needed separate confirmation.
- Nothing else fought me. `gh issue create` / `gh issue comment` clearance was in place as promised;
  no permission prompts, no classifier vetoes.
