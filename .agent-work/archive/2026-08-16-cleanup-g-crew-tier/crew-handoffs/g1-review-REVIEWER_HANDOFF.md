# Reviewer Handoff

## Gate
`g1-review`

## Survey State Location
Create your review survey checklist at `.agent-work/cleanup-g-crew-tier/g1-review/review.json`.

## What Was Implemented
`scripts/run_crew.py`: `CrewSpec.__post_init__` now refuses a falsy `self.model` (raises
`CrewLaunchError`), as a third invariant check alongside its two existing ones. `build_crew_argv`
gained an `effort: str | None = None` parameter, emitting `--effort <value>` when truthy, mirroring
the existing `model` line; both `CliBackend.dispatch` and `CliBackend.resume` now pass `effort=`
through. `tests/test_crew_launcher.py` was reconciled for every call site the new mandatory
`--model` invalidated, plus a new `MandatoryModelTests` class and four flipped assertions on the
`--effort` forwarding tests. `map/INDEX.md` was regenerated (mechanical, tool-generated) because the
new tests shifted an entity count the map-freshness suite checks.

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/constellation-skills/.worktrees/cleanup-g-crew-tier`
(a linked worktree — do NOT use `git diff main...HEAD`). Use `git status --porcelain` then
`git diff` (not `--name-only`, which hides untracked additions — there should be none for this
gate; all three changed files are pre-existing and modified in place).

## Task Statement
Full handoff at `.agent-work/cleanup-g-crew-tier/crew-handoffs/g1-implement-IMPLEMENTER_HANDOFF.md`
(read it — it carries the complete task, the ruled sub-decisions, and the Authority section). In
one line: refuse a fresh/relaunch crew dispatch that names no `--model`, fail closed with no
invented default; forward `reasoning_effort` as the launcher's real `--effort` flag on the `cli`
backend, both dispatch and resume.

## Close Criteria
- `CrewSpec.__post_init__` refuses a falsy `model`; the exception is `CrewLaunchError` (matches the
  launcher's existing `REFUSED: {exc}`/exit-1 shape).
- The refusal fires for fresh launch and `--abandon --relaunch` (both construct a `CrewSpec`) and
  does NOT fire for `--resume`/`--verify-result`/a bare `--abandon` (none construct one) — verify
  by reading `CliBackend.resume` and `abandon_crew` yourself, not by trusting the claim.
- `--abandon --relaunch` requires an explicit `--model` with NO fallback to
  `abandoned.get("model")` — verify this is what the code actually does, not just what a test
  asserts (a test can assert the wrong thing and still pass).
- The refusal fires BEFORE `CliBackend.dispatch` reserves scratch/writes the running registry entry
  (issue #525 ordering) — a refused fresh launch leaves no half-written entry. Verify the guard
  clause's placement in `__post_init__` actually runs before any scratch/registry code, not just
  that a test asserts an empty registry (a test can pass by coincidence if nothing writes the
  registry regardless of ordering).
- `--effort` forwards on BOTH `CliBackend.dispatch` and `CliBackend.resume`, from `spec.reasoning_effort`
  and `entry.get("reasoning_effort")` respectively.
- `build_entry`'s existing `if model:`/`if reasoning_effort:` write path is UNCHANGED (only its
  docstring was corrected) — confirm no new/duplicate write path was added.
- `--model` remains OPTIONAL at the `argparse` layer (`build_parser`) — confirm `required=True` was
  NOT added there.
- No crew's effective tier changed as a side effect (`decision:do-not-change-what-anything-runs-at`)
  — confirm nothing outside the refusal/effort-wiring logic changed dispatch behavior.
- `tests/test_crew_launcher.py` full file green: 211 passed, 1 pre-existing environmental failure
  (`ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
  — fails identically on the unmodified baseline per `git stash`; reproduce this claim yourself,
  don't just trust it).
- Caller-list enumeration is complete: independently grep the live tree (not `.agent-work/archive/**`)
  for `CrewSpec(`, `record_external_attempt(`, `.launch_crew(` and confirm the implementer's claim
  that no production (non-test) caller outside `scripts/run_crew.py` constructs one.

## Allowed Scope
`scripts/run_crew.py`, `tests/test_crew_launcher.py`. `map/INDEX.md` was touched but is NOT in the
handoff's Allowed Scope by name — evaluate whether the implementer's justification (mechanical,
tool-generated, entity-count-only diff, required by the "full suite green" close criterion, verified
stale-before/fresh-after via `git stash`) holds, rather than treating the touch itself as a scope
violation. If you can reproduce that it's tool-generated and mechanical, this is compliant; if you
find hand-editing or scope creep in that file, BLOCK.

## Specific Exclusions
- `skills/commander/references/crew-dispatch.md`, `IMPLEMENTER_HANDOFF.template.md`,
  `REVIEWER_HANDOFF.template.md` — gate `g2`, not this gate. Confirm untouched.
- Fenced, confirm untouched: `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
  `scripts/spine_lifecycle.py`, their tests, `skills/commander/templates/COMMANDER_SPINE.template.json`,
  `skills/admiral/templates/LAUNCH_ORDER.template.md`, `skills/admiral/references/fleet-doctrine.md`,
  `skills/_shared/**`, `scripts/install_constellation.py`.
- `#607`'s `_parent_lease_heartbeat` thread start/stop/join ordering — confirm untouched (it is not
  near the edited code, but confirm the diff doesn't graze it).

## Constraints the Implementation Must Respect
- `CrewLaunchError`, exit 1, `REFUSED: {exc}` — no new exception type or exit code invented.
- No invented default for a missing tier anywhere.
- Two out-of-owned-files test files (`tests/test_crew_worktree_cwd.py`,
  `tests/test_work_id_nesting.py`) are EXPECTED to now fail (6 tests total) — this is the deliberate
  caller-list deliverable, not a defect the implementer should have silently fixed or silently
  ignored. Confirm the implementer reported them (they should be named explicitly in
  IMPLEMENTER_RESULT's caller-list survey) rather than leaving them undiscovered.

## Map Anchors (inbound)
Map DEGRADED-UNPARSEABLE — no packet map; anchors are direct file:line citations.
- **Structural:** `scripts/run_crew.py:1350-1364` (`CrewSpec.__post_init__`), `:755-818`
  (`build_crew_argv`), `:1490-1638` (`CliBackend`), `:1092-1199` (`build_entry`).
- **Decision anchors:**
  - `decision:refuse-a-tierless-dispatch` — fail closed, no invented default; report legitimately-tierless callers.
    `@grade: settled/human · leans g1-implement,g1-review`
  - `decision:do-not-change-what-anything-runs-at` — explicit choice only, no side-effect retiering.
    `@grade: settled/human · leans g1-implement,g1-review`
  - `decision:reasoning-effort-follows-tier` — forward as `--effort`; confirmed present on the real `claude` CLI.
    `@grade: settled/measured · leans g1-implement,g1-review`

## Evidence Produced
Full `IMPLEMENTER_RESULT` at `.agent-work/cleanup-g-crew-tier/crew-handoffs/g1-implement-implementer-result.md`
— read it in full; it contains the wiring-grep output, the full clean-env suite run (7 failed / 3163
passed, with the failure-cause breakdown), and the complete caller-list survey. Target postcondition:
`g1-integrate.c2` (`review-result` with `verdict: APPROVE`).

## Suggested Model Tier
Stronger — reason: this reviews a control-flow change to the crew-dispatch launcher every
implementer/reviewer in this corpus routes through, including a fail-closed refusal whose scoping
(fresh/relaunch only, not resume) is easy to get subtly wrong and easy to review superficially.
Dispatch at `sonnet`, this run's tier.

## Stop Conditions
Stop and return BLOCK if: the refusal fires on `--resume` or bare `--abandon` (scoping bug); the
refusal can be bypassed (e.g. `model=""` vs `model=None` inconsistency); `--effort` forwarding is
asymmetric between dispatch and resume; a fenced/out-of-ownership file was touched; `#607`'s
heartbeat thread was disturbed; the pasted test evidence does not reproduce.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.

**Delivery.** Write the full `REVIEW_RESULT` to
`.agent-work/cleanup-g-crew-tier/crew-handoffs/g1-review-reviewer-result.md` before ending your turn.
