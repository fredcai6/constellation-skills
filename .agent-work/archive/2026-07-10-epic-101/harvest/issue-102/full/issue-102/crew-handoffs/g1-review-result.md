# Review Result

## Assigned Gate
`g1-review` (issue #102, Move 1 — consolidate compliance boilerplate into global-everyone.md)

## Result
`APPROVE`

## Handoff compliance
Move 1 executed as specified. The mandatory-compliance / engine-drive boilerplate was single-sourced
into a new `## Engine-drive compliance` subsection of `skills/_shared/global-everyone.md`, and the
inline paragraph in all 10 carriers (admiral, cartographer, charter, commander, implementer,
interrogator, lessons-auditor, reviewer, scout, workbench) was replaced by a one-line pointer to
`references/global-everyone.md`. Drove the review as a `survey` through the bundled engine
(`.agent-work/issue-102/g1-review/review.json`); all 14 checks recorded pass, consolidated APPROVE,
0 findings. Every stop condition checked and none tripped.

## Scope drift
None. `git status --porcelain` shows exactly 11 modified files: `global-everyone.md` + the 10 carrier
`SKILL.md`. No untracked files. Specific exclusions verified untouched: FOLLOW-THIS-SKILL-STRICTLY
banners, prototyper, the engine-invocation operational string (g2), and manifest.json / ROADMAP /
repo-root strays (#105) — none appear in the diff.

## Evidence verdict
Independently reproduced, not accepted from the report:
- Before (HEAD), case-insensitive `mandatory, no exceptions` = 1 in each of the 10 carriers (10 total).
- After (working tree) = 0 in all 10 carriers; 10 pointer lines (`Compliance/engine-drive rule:
  inherited — see references/global-everyone.md`) present, one per carrier; canonical section count
  in `global-everyone.md` = 1.
- `py -m pytest tests/ -q` re-run here: **442 passed, 2 skipped, 26 subtests passed in 12.95s** —
  matches IMPLEMENTER_RESULT. Includes the `test_install_constellation` bundle glob (196-208).

## Code/doc quality
Canonical (global-everyone.md lines 10-16) reads cleanly once, un-bolded, dense agent-facing register.
It generalizes correctly: covers `checklist, spine, or survey` and the per-role reporting steps
(`closeout, feedback step, or workflow feedback`), subsuming every carrier variant including
workbench's meta-framing ("once a role skill is loaded"). Role-specific tails were preserved only
where genuinely role-specific — admiral's closeout, commander's "you never do another role's work
yourself," implementer/reviewer's "workflow feedback." No meaning dropped in the reconcile-then-cut.
Appended into the existing file (no new `global-*.md`), each carrier retains a pointer.

## Map impact verdict
Skipped in depth — pure documentation consolidation with no structural, capability, constraint, or
decision impact. The `install_constellation.py` bundle (94-113) still globs `global-*.md`; the
canonical stays in the same file, so the install manifest and the guarding test are unaffected
(confirmed green).

## Reconciliation check
No divergence from recorded architecture requiring Commander reconcile. No contract or structural
baseline concern.

## Blockers
- none

## Out-of-scope observations
- none — no triage candidates. Scope was clean.

## Workflow Feedback
- **Handoff gaps:** The "before=10 inline" grep claim is only reproducible **case-insensitively**.
  Commander's carrier phrased the rule "**This is mandatory, no exceptions**" (capital T, embedded),
  so an exact-case `grep "Mandatory, no exceptions"` catches only 9 of 10. The evidence still holds
  (case-insensitive count = 10; diff removes 10 inline paragraphs), but a future handoff should
  specify the case-insensitive grep so the "before=10" number reproduces without a second attempt.
- **Context rediscovered:** `config_ref` in the survey template points to
  `docs/agents/engine-config.json`, which does not exist in this repo (constellation-skills is the
  meta-repo, not a project consuming it). The engine tolerates the absent config, and prior
  checklists (spine.json, execute.json) use the same ref, so this is benign — but it is a self-hosting
  quirk worth a one-line note in a future handoff so a reviewer does not chase it.
- **Instructions improvised around:** The base `r4-quality` check is an umbrella for "append a check
  per inherited rule"; I appended `q-append-only`, `q-register`, `q-reconcile-meaning` as siblings and
  recorded r4 as a roll-up. Engine still required r4 be visited — handled, no misfit of consequence.
- **What would have made this easier:** Handoff could state the exact case-insensitive grep command
  it wants reproduced (see Handoff gaps).

## Return status
`complete`
