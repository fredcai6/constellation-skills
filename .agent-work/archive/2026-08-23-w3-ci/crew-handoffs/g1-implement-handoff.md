# Implementer Handoff

## Gate
g1-implement

## Task
Add exactly one `ubuntu-latest` job to `.github/workflows/ci.yml`, then locally demonstrate that
job's commands can produce a real red (a specific failing assertion, not a crash) and revert to
green — never by pushing a broken commit.

## Protected Intent
CI must carry a signal that can actually be trusted. Right now `.github/workflows/ci.yml` runs
only a `windows-latest` job that is red on 12/12 recent runs from Windows-only bugs (autocrlf
`git apply`, Windows temp-path failures) — not real regressions — so nobody looks at it, and PR
#645 turned `main` red while CI (which already tests the merge ref via the `pull_request`
trigger) correctly reported failure and was ignored. Adding a Linux job restores a signal that
already exists; it must not become a second check nobody trusts.

## Test Mode
Inspection-only / local-command-parity — this is CI configuration (YAML), not application code
with its own test suite. "Testing" this gate means: (a) the new job's steps are a faithful mirror
of the existing job's steps (verifiable by diff inspection), and (b) the commands those steps run
are proven able to both fail and pass locally (the red-proof below), since this worktree runs
Linux and can execute the exact commands the `ubuntu-latest` runner would execute.

## Close Criteria
- `.github/workflows/ci.yml` has exactly one new job, `runs-on: ubuntu-latest`, alongside the
  existing `test` job (do not rename or restructure the existing job).
- The new job's steps mirror the existing job's: checkout, `setup-python` at `3.12`, install
  `pytest`+`coverage`, then the same three run steps (MCP-door smoke test, full `pytest tests/ -q
  --junitxml=junit-report.xml`, skip guard, coverage floor) — adapt only what genuinely differs
  on Linux (no `defaults.run.shell: bash` override needed; ubuntu's default shell is already
  bash, so omit that block for the new job rather than copying it needlessly).
- `on:` triggers are byte-for-byte unchanged. No matrix strategy. The `windows-latest` job is
  byte-for-byte unchanged.
- Red-proof performed and captured (see Required Evidence) — locally, uncommitted, then reverted.
  `git diff --quiet -- tests/` confirms a clean revert before this gate closes.
- `git diff --stat` at close shows exactly one file changed: `.github/workflows/ci.yml`.

## Allowed Scope
- `.github/workflows/ci.yml` — add the one new job.
- `tests/` — **transiently only**, for the red-proof mutation (see Required Evidence); it must be
  reverted (uncommitted or `git checkout -- tests/<file>`) before the gate closes. No test file may
  be left changed.

## Specific Exclusions
- Do not touch `on:` triggers, the `env:` block, or the `windows-latest` job's steps.
- Do not add a matrix strategy, a second workflow file, branch protection, or required-checks
  config — those are explicitly "float to the Admiral," not yours to decide (launch order,
  `decision:ci-changes-beyond-this-are-surfaced`).
- Do not push any commit to demonstrate the red-proof. Do it locally, uncommitted.

## Constraints
- File ownership: `.github/workflows/ci.yml` only as a committed deliverable (`tests/` only
  transiently, never committed changed).
- `decision:add-one-job-only` — single `ubuntu-latest` job, no matrix, no trigger changes, no
  workflow restructuring. `@grade: settled/human`
- `decision:windows-stays-red` — do not fix, delete, or disable the `windows-latest` job.
  `@grade: settled/human`
- `decision:ci-changes-beyond-this-are-surfaced` — any other `ci.yml` change is a decision to
  float, not make. `@grade: settled/human`
- `decision:prove-it-can-go-red` — red-proof required; use the local same-OS command-parity
  method (this worktree is Linux), never a pushed broken commit. `@grade: guess/admiral · settle:
  local same-OS command-parity red-proof is the cheapest honest alternative to a pushed/triggered
  Actions run`
- The red-proof mutation must never be committed. Verify with `git diff --quiet -- tests/` (never
  `git status --porcelain` — this repo's `core.autocrlf=true` makes `--porcelain` false-negative
  on a byte-perfect revert).
- A mutation battery must assert the specific named assertion — never a bare non-zero exit and
  never an exception. Pick a mutation you did not just see demonstrated elsewhere in this repo
  (do not reuse an existing documented fault-injection example verbatim).

## Map Anchors (inbound)
No map artifact touches this gate — the repo's map is DEGRADED-UNPARSEABLE (context step,
`.agent-work/w3-ci/map-orientation.json`) and covers Python packages only, not workflow YAML.
- **Map entry point:** none — see `.agent-work/w3-ci/MISSION_FRAME.md` for the substitute used
  (`docs/agents/AGENT_GUIDE.md`), cited for repo orientation only, not for this file's structure.
- **Constraints/assumptions:** `assumption:ci-tests-merge-ref` — `.github/workflows/ci.yml`'s
  `pull_request` trigger already checks out `refs/pull/N/merge` (pasted launch-order measurement).
- **Decision anchors:** see Constraints above; all four carry their `@grade` tags there.

## Deliverable Path Check
- **Committed** — `.github/workflows/ci.yml`; verified via `git check-ignore .github/workflows/ci.yml` exiting 1 (not ignored) before dispatch.
- **Local-only, transient, never committed** — whichever `tests/` file you choose for the red-proof
  mutation; it must be reverted before this gate's close, so it never appears in any commit.

## Required Evidence
1. `git diff -- .github/workflows/ci.yml` (the new job, in full).
2. The red-proof transcript: the exact mutation made (a one-line diff or inline description), the
   exact command run (must be the same command the new job's step runs, e.g.
   `python -m pytest tests/ -q --junitxml=junit-report.xml -k <narrowed selector if needed to keep
   it fast>`), its output showing the SPECIFIC failing assertion text (not just "1 failed"), then
   the revert command and `git diff --quiet -- tests/; echo $?` showing `0`, then the same command
   re-run green.
3. `git diff --stat` at close, confirming exactly one file changed overall.

## Wiring Grep
`none — this gate adds no callable symbol; it adds a CI job definition (YAML), not code.`

## Verification Commands
```bash
git diff -- .github/workflows/ci.yml
git diff --quiet -- tests/ && echo "tests/ clean"
git diff --stat
```

## Suggested Model Tier
simple bounded — mechanical YAML addition mirroring an existing job, plus one local fault-injection
cycle with a clear named-assertion requirement.

## Authority
The job's shape (single job, no matrix, no trigger/windows changes) is already decided by the
launch order (`decision:add-one-job-only`, `decision:windows-stays-red`,
`decision:ci-changes-beyond-this-are-surfaced`) — do not relitigate it. Python version, step
layout, caching, and naming are your latitude. The red-proof method (local, not pushed) is this
Commander's proposed reading of `decision:prove-it-can-go-red`'s settle clause — flag in your
result if you believe a pushed/triggered proof is actually required; do not silently do it anyway.

## Stop Conditions
Stop and return if: the allowed scope must be exceeded, a specific exclusion must be touched, the
red-proof cannot produce a specific named-assertion failure without touching more than one `tests/`
file transiently, or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/w3-ci/crew-handoffs/g1-implement-result.md` before ending your turn.
