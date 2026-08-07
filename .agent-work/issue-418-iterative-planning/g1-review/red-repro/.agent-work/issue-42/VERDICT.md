# VERDICT — issue-42 (lessons apply-or-defer)

## 1. VERDICT: done

Landed the in-flight `constellation/lessons-apply-or-defer` branch. Task 7 (bundle
`verify_lessons_applied.py` + Commander/Admiral spine postconditions + latitude decision
class + install test) was committed as its own commit from the uncommitted working tree;
Task 8 (three workbench-template docs reconcile) followed as a separate commit. Full suite
green, independent fresh-context review APPROVE, PR #57 opened against main and left unmerged
for the human's wave-checkpoint decision.

## 2. PR URL
https://github.com/fredcai6/constellation-skills/pull/57  (Closes #42)

Commits added this run:
- `3a9589c` feat(lessons): bundle verify_lessons_applied and wire apply-or-defer gates (5 Task-7 files)
- `883fed0` docs(lessons): document apply-or-defer; retire the advisory closeout table (3 Task-8 files)

## 3. Test evidence tail
```
........................................................................ [ 79%]
....................................s...............                  [100%]
255 passed, 1 skipped, 15 subtests passed in 9.03s
EXIT: 0
```
Run independently by the reviewer subagent (matched my own local run). All skill JSON parses.

## 4. Isolation note (why --here was skipped)
Skipped `verify_worktree_isolation.py --here` per the launch order's SPECIAL (PR-1) workspace
ruling: the uncommitted Task-7 work lived only in the MAIN checkout `C:/Programs/constellation-skills`
on the existing branch, so I deliberately worked in the shared checkout rather than an isolated
worktree. No branch switch. My spine/work area stayed under `.agent-work/issue-42/`; I never
touched `.agent-work/20260706-dogfood-audit/` (the Admiral's area). Nothing under `.agent-work/`
was committed (gitignored).

## 5. Map impact
No structural drift. The change matches the spec's declared "Files touched" list exactly. New
public surface (`ripe_lessons()`, `--ripe`, `verify_lessons_applied.py`, two new engine
postconditions, two new `SKILL_SCRIPT_BUNDLES` entries) is all spec-declared. No new authority
grabbed; all-or-nothing delta validation preserved.

## 6. Triage candidates (future work found out of scope)
- **Stale docs reference (recommend issue):** `docs/RECURSIVE_IMPROVEMENT_DESIGN.md:18,134` still
  describe the retired "Template Update Candidates" table. NOT in the spec/plan Task-8 files-touched
  list and adjacent to the #49 charter/platform fence, so left untouched deliberately.
- **Test-coverage gaps (low risk, follow-up):** constellation-scope `defer` count branch;
  `exported`-suppression path in `ripe_lessons()`; verifier corrupt-playbook error path. Each is
  logic-mirrored by a tested sibling path.
- **Out-of-scope by design:** upstream metabolize of exported constellation lessons
  (`collect_feedback.py` -> `skills/_shared/global-*.md`) — explicitly deferred in the spec.

## 7. Workflow Feedback
See the SendMessage return to "main"; the AGENT_FEEDBACK entry text is included there for the
Admiral to append durably.
