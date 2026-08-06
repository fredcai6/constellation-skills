# Reviewer Handoff

## Gate
g1 (issue #329, workstream D of epic #418)

## Survey State Location
Create your review survey checklist at
`.agent-work/issue-422-wire-invariants/g1-review/review.json`.

## What Was Implemented
`skills/commander/templates/COMMANDER_SPINE.template.json`'s `init` gate gained a `c0` command
precondition running `python scripts/verify_worktree_isolation.py --here <repo-root>` — a Commander
instantiated from this template can no longer `start` its `init` gate without that check passing. A new
standalone script `scripts/verify_worktree_precondition_coverage.py` holds an explicit, commented list of
"worktree-entering" templates (today: this one template only) and fails, naming the offender, if any listed
template's designated gate lacks the wired precondition. `tests/test_worktree_precondition_wiring.py` lands
two deliberate-breakage tests.

## How to Inspect the Diff
Uncommitted working tree in this worktree (`C:/Programs/constellation-skills-wt/epic418-d-422`):
`git status --porcelain`, then `git diff -- skills/commander/templates/COMMANDER_SPINE.template.json`
for the modified file, and read the two new files directly (`scripts/verify_worktree_precondition_coverage.py`,
`tests/test_worktree_precondition_wiring.py`) since `git diff --name-only` hides untracked additions.

## Task Statement
Wire the prose-only worktree-isolation invariant (#329) as a real engine precondition, ship an enumeration
check that catches a worktree-entering template left unwired, and prove both with deliberate-breakage
tests landed in the automated suite — not manual scratch demonstrations, and not a PreToolUse-hook
mechanism (that alternative was explicitly out of scope per the confirmed spec).

## Close Criteria
- `COMMANDER_SPINE.template.json`'s `init` gate carries a new precondition whose `check.command` invokes
  `verify_worktree_isolation.py --here <repo-root>`; valid JSON; no other gate touched.
- `scripts/verify_worktree_precondition_coverage.py` exists, exits 0 against the real tree, states the
  count of templates checked, and its membership list + rationale are documented in its own docstring.
- `tests/test_worktree_precondition_wiring.py` exists, passes, and **genuinely** proves both deliberate
  breakages: re-run each test's breakage path yourself (do not trust the report) — the #392 shape (a check
  that still passes once its guard is deleted) is exactly what this review exists to catch. The
  implementer's reported method was reverting the real template via `git stash` and observing a failure
  before the fix, then popping the stash back — verify this claim independently: `git stash push --quiet --
  skills/commander/templates/COMMANDER_SPINE.template.json`, re-run the enumeration test, confirm it fails
  and names the missing precondition, then `git stash pop --quiet` and confirm the tree is back to the
  reviewed state (`git diff --stat` matches what you started with).
- Full suite green: `python -m pytest tests/ -q` (use the `python` binary on PATH that has pytest
  installed — some environments have a `py` alias pointing at an interpreter without pytest; verify with
  `python -m pytest --version` first if in doubt).

## Allowed Scope
`skills/commander/templates/COMMANDER_SPINE.template.json` (`init` gate's `preconditions` array only),
new file `scripts/verify_worktree_precondition_coverage.py`, new file
`tests/test_worktree_precondition_wiring.py`.

## Specific Exclusions
`scripts/checklist_engine.py` (workstream B/#420's fence this wave — confirm untouched: `git diff --stat`
must not list it), `scripts/verify_worktree_isolation.py` (must be byte-identical — confirm with
`git diff scripts/verify_worktree_isolation.py` showing nothing), any other gate in
`COMMANDER_SPINE.template.json`, any PreToolUse-hook code.

## Constraints the Implementation Must Respect
- `<repo-root>` is resolved by the existing `resolve_spine()`/`instantiate_spine()` in
  `scripts/init_work_area.py` — no new placeholder token should have been introduced.
- The deliberate-breakage constructions must run in temp/scratch fixtures only (pytest `tmp_path`, a
  throwaway `tempfile.TemporaryDirectory` git repo, or a stash-and-pop of the tracked file that fully
  restores) — never leave the shared checkout/worktree in a broken state after the test suite finishes.
  Confirm post-test-run: `git status --porcelain` shows only the three intended changed/new files, nothing
  else dirty or missing.

## Map Anchors (inbound)
Inherited from g1-implement (same as the mission frame's g1 anchors):
- **Structural:** `scripts/checklist_engine.py:1635 start()` — unchanged, the existing precondition-check
  mechanism this rides.
- **Capability:** Commander spine `init` gate proves worktree isolation before any git operation.
- **Constraints/assumptions:** only `COMMANDER_SPINE.template.json`'s role is dispatched into an isolated
  worktree via a `LAUNCH_ORDER` today — confirm the enumeration list has exactly one entry, no more, no
  fewer.
- **Decision anchors:** `decision:worktree-entering-membership` — explicit maintained list, not a
  heuristic. `@grade: guess · leans g1-implement · settle: confirm refusal-on-omission fires when a second
  worktree-entering spine ships` (only half-provable today — the implementer flagged this as a triage
  candidate; confirm that flag is reasonable, not a cover for weak test evidence).
- **Evidence expectations:** `claim:no-template-wires-isolation` — re-confirm
  `grep -rln verify_worktree_isolation skills/*/templates/*.json` returns exactly
  `skills/commander/templates/COMMANDER_SPINE.template.json`.

## Evidence Produced
See `.agent-work/issue-422-wire-invariants/crew-handoffs/g1-implement-result.md` for the implementer's full
pasted command output (json validation, coverage script run, targeted test run, full suite run, grep for
call sites, and the git-stash red/green demonstration). Target postcondition this evidence backs:
`g1-integrate.c1` (test command) and `g1-integrate.c2` (this review's verdict).

## Suggested Model Tier
Sonnet — bounded verification of a well-precedented, already-tested wiring change.

## Stop Conditions
Stop and return BLOCK if: the deliberate-breakage tests do not actually fail when you strip the fix
yourself; `checklist_engine.py` or `verify_worktree_isolation.py` show any diff; the full suite is not
green; the enumeration script's membership list is wrong or undocumented.

## Return Format
Return REVIEW_RESULT (verdict APPROVE/BLOCK, per-check findings, blockers, out-of-scope observations,
workflow feedback). Report it as your final message text; also write it to
`.agent-work/issue-422-wire-invariants/crew-handoffs/g1-review-result.md`.
