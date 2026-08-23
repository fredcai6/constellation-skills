# Review Result

## Assigned Gate
`g1-review` (reviewing `g1-implement`'s work)

## Result
`APPROVE`

## Handoff compliance
Verified independently, not from the implementer's transcript alone. `git status --porcelain`
shows one modified tracked file (`.github/workflows/ci.yml`) and one untracked scratch dir
(`.agent-work/w3-ci/`, expected). `git diff --stat` shows exactly one file changed, 30
insertions, 0 deletions. The new `test-linux` job:
- `runs-on: ubuntu-latest`, alongside the unmodified `test` (windows-latest) job — confirmed
  via `yaml.safe_load` (`jobs: ['test', 'test-linux']`).
- Mirrors the existing job's 7 steps step-for-step: programmatically compared `uses`/`with`/`run`
  content for every step pair — all matched exactly except the MCP-door step's display name
  (dropped "on Windows," reasonable since the job now runs on Linux) and the intentional,
  handoff-sanctioned omission of `defaults.run.shell: bash` (unneeded — ubuntu's default shell
  is already bash).
- Task statement, close criteria, and required evidence in `g1-implement-handoff.md` were all
  satisfied.

## Scope drift
None. `.github/workflows/ci.yml` is the only committed file touched. `tests/` shows a clean
diff right now: `git diff --quiet -- tests/; echo $?` → `0` (independently re-run, not just
trusted from the transcript). No matrix strategy, no second workflow file, no branch-protection
or required-checks change — confirmed by reading the full current `ci.yml` and diffing the first
72 lines against `git show HEAD:.github/workflows/ci.yml` (byte-identical). `on:` and `env:`
blocks are byte-for-byte unchanged; the `windows-latest` job's steps are byte-for-byte unchanged.

## Evidence verdict
Required evidence is present and genuine.
1. **Diff** — matches what `git diff` independently shows right now.
2. **Red-proof** — independently reproduced, not just read. Applied the identical mutation to
   `tests/test_agent_work_root.py::DurableRootEpicLeaseTests::test_no_lease_resolves_to_main`
   (`_norm(self.main)` → `_norm(self.linked)`), ran the exact claimed command
   (`python3 -m pytest tests/ -q --junitxml=junit-report.xml -k test_no_lease_resolves_to_main`),
   and got the identical specific `AssertionError` (`'/tmp/.../main' != '/tmp/.../linked'`) —
   a named assertion, not a bare failure or crash. Reverted with `git checkout --`, confirmed
   `git diff --quiet -- tests/; echo $?` → `0`, then re-ran the same command and got `1 passed`.
   No residue left afterward (`git status --porcelain` clean of `tests/`).
3. **`git diff --stat`** — reproduced independently, matches the claimed one-file, 30-insertion
   diff.
4. Also independently ran the **full local suite** (`python3 -m pytest tests/ -q
   --junitxml=...`): `3729 passed, 9 skipped, 1277 subtests passed` — green, satisfying the
   "full local suite green" half of the target postcondition `g1-integrate.c1`. (See
   "Reconciliation check" below for a caveat on the skip-guard step specifically.)

`assumption:ci-tests-merge-ref` (the `pull_request` trigger already checks out
`refs/pull/N/merge`) was correctly left untouched and unre-verified, as the handoff scoped it
out of this gate.

## Code/doc quality
Fowler refactoring/code-smell pass run per `constellation-reviewer` SKILL.md, recorded to
`.agent-work/w3-ci/g1-review/FOWLER_PASS.json`, verified clean by
`scripts/verify_fowler_pass.py` (exit 0; `smells=12, flagged=[], overridden=['duplicated-code']`).
- **duplicated-code** — present (the new job's steps are a near-verbatim copy of the existing
  job's) but **overridden**: `decision:add-one-job-only` (`@grade: settled/human`) explicitly
  excludes a matrix strategy — the mechanism that would remove the duplication — and the
  handoff's own close criteria require the new job's steps to mirror the existing job's. The
  duplication is the mandated shape, not an implementer shortcut; a human-graded decision already
  weighed and rejected the alternative.
- All other 11 baseline smells: absent (no code with method/class/parameter/message-chain
  structure was touched — this is a declarative YAML addition).
No other quality issues. Step ordering, naming (`test-linux`), and the MCP-door step's renamed
title are within the implementer's stated latitude ("Python version, step layout, caching, and
naming are your latitude").

## Map impact verdict
Implementer's "Map Impact" notes say "Skipped — trivial ... no structural, capability,
constraint, or decision impact beyond what the handoff's Map Anchors already named." Consistent
with the diff: this is a CI-config addition with no Python-package/module surface, and the repo
map is documented DEGRADED-UNPARSEABLE for workflow YAML. No durable-context or decision-routing
gap. Skipped correctly per this section's own "skip for trivial local edits" guidance.

## Reconciliation check
One finding worth flagging strongly, though it does not block this gate (see below):
running the exact "Skip guard -- no undocumented skips" step the new job mirrors
(`python scripts/verify_skip_guard.py junit-report.xml`) against a full-suite run **on the
current tree, right now**, returns `REFUSED` (exit 1) — 8 of 9 skips are not on the documented
allow-tuple. All 8 are self-decaying, pinned-to-a-specific-HEAD tests in
`tests/test_checklist_engine.py` (`CommanderSpineBasisFields`, pinned to
`9d5aac6daa58a72fc6a665cb39879ee5705f7f71`) and two related `verify_spec_confirmed`/
`mcp_adoption` cases, whose skip messages explicitly say "HEAD is now
135c34eb0b0a10bc5cebb0e6e3869b124e63735e -- this test's assumptions ... need re-verifying." I
confirmed the repo's current `HEAD` is exactly `135c34eb...`, so this is **not** an artifact of
anything in this diff — `tests/` and `scripts/` both show zero diff — it is pre-existing
repository state (main has simply moved past the last-pinned revision).

Why this is out of scope for `g1-review` rather than a blocker: it is not introduced by, or
fixable within, the allowed scope of this gate (`.github/workflows/ci.yml` and transient
`tests/` only); it applies identically to whichever job runs the skip-guard step, mirrored
job or not; and it is a routine, self-decaying-by-design test pattern (see
`test_checklist_engine.py`'s `_skip_if_head_moved`), not a defect in the new job's mirroring.

Why it matters anyway, and should go to Commander/Triage promptly: the g1-implement handoff's
own **Protected Intent** states the new job must "restore a signal that already exists; it must
not become a second check nobody trusts." As things stand, the new `test-linux` job would go red
on its very first real CI run — not from a real regression, but from this stale pin — which is
exactly the "second check nobody trusts" outcome the gate exists to avoid. The fix (bump
`PINNED_HEAD` in the three `CommanderSpineBasisFields` tests, and re-check the other two skip
sources) is a small, mechanical, unrelated maintenance action, but it should land before or
immediately alongside this PR, not be discovered after the job merges red.

## Blockers
- none for this gate's scope.

## Out-of-scope observations
- **Triage candidate (elevated):** `tests/test_checklist_engine.py`'s `CommanderSpineBasisFields`
  tests (and two other skip sources) are pinned to a stale `HEAD` and currently fail
  `scripts/verify_skip_guard.py`'s allow-tuple check on the full suite, independent of this diff.
  Recommend bumping `PINNED_HEAD` (and re-verifying the pinned assumptions against current
  `HEAD`) before relying on the new `test-linux` job's skip-guard step, or the job launches red
  for a reason unrelated to real regressions — directly undermining this gate's own stated
  Protected Intent ("must not become a second check nobody trusts").
- Everything else flagged as floated by the launch order (matrix strategy, branch protection,
  required-checks config, actually fixing `windows-latest`) remains untouched, as intended —
  none of it was considered or needed here.

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: task, evidence, close criteria, allowed scope,
  exclusions, all four graded decision constraints, map anchors, and stop conditions were present
  and unambiguous. One residual gap: the handoff's "target postcondition"
  (`g1-integrate.c1`, "full local suite green + tests/ clean") does not say whether "green" means
  bare pytest exit status or also the downstream skip-guard/coverage-floor steps the mirrored job
  runs — I read it as the former (satisfied) but ran the latter anyway and found the
  pre-existing skip-guard REFUSED state described above; a one-line clarification of what "green"
  covers would have made that check explicit rather than a judgment call.
- **Context rediscovered:** none beyond what the implementer already logged about the
  spine-null/CLI-direct dispatch pattern; this review's own dispatch instructions named that
  pattern up front and explicitly authorized skipping the full engine-driven survey for this
  bounded review, which matched the actual situation cleanly (no `mcp__spine__*` tools present).
- **Instructions improvised around:** ran the review directly (independent diff/red-proof
  reproduction, plus a standalone Fowler pass recorded to
  `.agent-work/w3-ci/g1-review/FOWLER_PASS.json` and verified with
  `scripts/verify_fowler_pass.py`) rather than claiming a full `checklist_engine.py`-driven
  `review.json` survey lease, per this dispatch's explicit "a full engine-driven survey is not
  required for this bounded review" instruction, which overrides the skill's default
  engine-first framing.
- **What would have made this easier:** nothing further; the handoff's four independently-listed
  verification points (exactly one file, mirrored steps, `tests/` zero diff, named-assertion
  red-proof) mapped cleanly onto concrete, reproducible commands.

## Return status
`complete`
