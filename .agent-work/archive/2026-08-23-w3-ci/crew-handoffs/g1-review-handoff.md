# Reviewer Handoff

## Gate
g1-review (reviewing g1-implement's work)

## Survey State Location
`.agent-work/w3-ci/g1-review/review.json`

## What Was Implemented
One new `ubuntu-latest` job (`test-linux`) added to `.github/workflows/ci.yml`, mirroring the
existing `windows-latest` job's steps (checkout, setup-python 3.12, install deps, MCP-door smoke
test, full pytest run, skip guard, coverage floor), minus the `defaults.run.shell: bash` override
(unneeded — bash is already ubuntu's default shell). No trigger, matrix, env, or existing-job
change. A local red-proof was performed (uncommitted mutation to one test, captured a specific
failing assertion, reverted, re-ran green) to satisfy the launch order's
`decision:prove-it-can-go-red`.

## How to Inspect the Diff
Review target is the **UNCOMMITTED working tree** at `/home/tommy/projects/569-w3-ci` (branch
`epic-569/w3-ci`). Run `git status --porcelain` then `git diff` (not `--name-only`, which hides
untracked additions). Expect exactly one tracked file changed: `.github/workflows/ci.yml`
(30 insertions, 0 deletions). `.agent-work/w3-ci/` is untracked scratch — expected, not a defect.

## Task Statement
Add exactly one `ubuntu-latest` job to `.github/workflows/ci.yml`, mirroring the existing job's
steps, then locally prove the new job's commands can produce a real red (a specific failing
assertion) and a clean revert to green — full original task in
`.agent-work/w3-ci/crew-handoffs/g1-implement-handoff.md`.

## Close Criteria
- Exactly one new job added, `runs-on: ubuntu-latest`, alongside the unmodified `test` job.
- New job's steps are a faithful mirror of the existing job's steps (same tool versions, same
  three run-commands: full suite, skip guard, coverage floor) — check content, not just step count.
- `on:` triggers, `env:` block, and the `windows-latest` job's steps are byte-for-byte unchanged.
- No matrix strategy, no second workflow file, no branch-protection/required-checks change.
- Red-proof evidence is genuine: names a specific test and assertion (not "1 failed" alone,
  not an exception/crash), shows the mutation, the failing output, the revert command, and
  `git diff --quiet -- tests/; echo $?` → `0`, then a green re-run of the same command.
- `git diff --quiet -- tests/` on the CURRENT working tree (independently, right now) also
  confirms `0` — the mutation must have left no residue.
- `git diff --stat` shows exactly one file changed overall.

## Allowed Scope
`.github/workflows/ci.yml` (committed). `tests/` only transiently for the red-proof (must show
zero diff now).

## Specific Exclusions
Do not expect the implementer to have fixed Windows CI, changed triggers, added a matrix, or
touched branch protection/required checks — all explicitly out of scope this gate (launch order
`decision:windows-stays-red`, `decision:ci-changes-beyond-this-are-surfaced`).

## Constraints the Implementation Must Respect
- `decision:add-one-job-only` — single job, no matrix, no restructuring. `@grade: settled/human`
- `decision:windows-stays-red` — windows-latest job untouched. `@grade: settled/human`
- `decision:ci-changes-beyond-this-are-surfaced` — no other ci.yml change. `@grade: settled/human`
- `decision:prove-it-can-go-red` — red-proof required, local method (never a pushed broken
  commit). `@grade: guess/admiral · settle: local same-OS command-parity red-proof is the cheapest
  honest alternative to a pushed/triggered Actions run`
- `git diff --quiet -- tests/` (never `git status --porcelain` — this repo's `core.autocrlf=true`
  false-negatives `--porcelain` on a byte-perfect revert) must show a clean tests/ tree.

## Map Anchors (inbound)
No map artifact touches this gate (repo map DEGRADED-UNPARSEABLE for workflow YAML; see
`.agent-work/w3-ci/MISSION_FRAME.md`).
- **Constraints/assumptions:** `assumption:ci-tests-merge-ref` — the `pull_request` trigger
  already checks out `refs/pull/N/merge` (pasted launch-order measurement; verify it was not
  silently touched — it should read identically to the pre-change file).
- **Decision anchors:** as listed above, with grades.

## Evidence Produced
See `.agent-work/w3-ci/crew-handoffs/g1-implement-result.md` in full — diff, red-proof transcript
(specific `AssertionError` text captured), and `git diff --stat`. Target postcondition:
`g1-integrate.c1` (full local suite green + tests/ clean) and `g1-integrate.c2` (this review's
APPROVE verdict).

## Suggested Model Tier
simple bounded — a ~30-line YAML diff against a clear mirror-the-existing-job criterion, plus
verifying one fault-injection transcript against the current tree.

## Stop Conditions
Return BLOCK if: the diff cannot be accessed, the red-proof evidence does not reproduce or is not
a specific named assertion, `tests/` shows any current diff, any constraint above is violated, or
a policy decision is required before a verdict is possible.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.

Write the full `REVIEW_RESULT` to `.agent-work/w3-ci/crew-handoffs/g1-review-result.md` before
ending your turn.
