# Reviewer Handoff

## Gate
g3-implement (reviewing)

## Survey State Location
`.agent-work/567-j/g3-review/review.json`

## What Was Implemented
`resolve_model` (from g2) wired into `CrewSpec.__post_init__` — the single
choke point every `CrewSpec` construction site passes through — replacing the
flat `if not self.model: raise CrewLaunchError(...)` check. `--reason` threaded
end-to-end: CLI flag → `CrewSpec.reason` field → `build_entry` (both backends)
→ both `main()` construction sites (fresh-launch and abandon-relaunch,
symmetric). Two rounds: attempt 1 wired the choke point and rewrote the two
handoff-named tests but correctly stopped when 3 more pre-existing tests broke
for the same underlying reason; the Commander ruled (within file ownership) to
fix all three preserving their original test intent, plus fix an asymmetry
where only the fresh-launch path threaded `--reason`. Attempt 2 applied both
rulings.

## How to Inspect the Diff
Uncommitted working tree. `git status --porcelain` then
`git diff scripts/run_crew.py tests/test_crew_launcher.py`. Note the working
tree also carries g1's and g2's uncommitted changes (shared tree, not yet
committed) — scope your review to hunks inside `CrewSpec`, `build_entry`,
`build_parser`, `main`'s two `CrewSpec(...)` sites, and the named test classes.

## Task Statement
See `.agent-work/567-j/crew-handoffs/g3-implement-handoff.md` (original) and
`g3-implement-rework-handoff.md` (the two rulings) for the exact spec.

## Close Criteria
- `CrewSpec.__post_init__` calls `resolve_model(role=self.role, harness=self.launcher, requested=self.model, reason=self.reason)`
  exactly once, and the flat `if not self.model: raise` check is gone (replaced,
  not duplicated alongside).
- **Every** `CrewSpec(` construction site in the file (grep for it — expect 4:
  `launch_crew()`, `record_external_attempt()`, `main()`'s abandon-relaunch
  path, `main()`'s fresh-launch path) goes through `__post_init__` and
  therefore `resolve_model` — confirm this is true by Python's own semantics,
  not by testing each site individually (there is no way to skip
  `__post_init__` short of an `object.__new__` bypass, which nothing here
  does).
- `resume_crew()`, `CliBackend.resume()`, `ExternalBackend.resume()` show
  **zero** diff — verify by reading `git diff`'s hunk headers against each
  function's line range, not by trusting the claim.
- Both `main()` `CrewSpec(...)` construction sites (fresh-launch and
  abandon-relaunch) now pass `reason=args.reason` — symmetric.
- An old-shape `crew-runs.json` entry (a `model` key, no `reason` key at all)
  round-trips through `resume_crew`/`CliBackend.resume` without error.
- The three tests the Commander authorized rewriting in attempt 2 preserve
  their **original testing intent**, not just "made to pass":
  - `MandatoryModelTests::test_crew_spec_refuses_falsy_model_directly` now
    asserts resolved-default behavior for `role="reviewer"`.
  - `ExternalDispatchTests::test_cli_parser_persists_model_and_reasoning_effort_to_external_registry`
    still tests "an explicit --model/--reasoning-effort pair persists to the
    registry" — now using an in-table value (`"haiku"` for `"implementer"`,
    non-default, with a `--reason`) instead of an arbitrary string; verify the
    persisted `reason` is also asserted, not just `model`.
  - `BackendEquivalenceTests::test_external_dispatch_records_without_spawning_returns_none`
    still tests "external backend spawns nothing, returns None" — now using
    `model="sonnet"` (implementer's default, needs no reason) instead of
    `"opus"`; verify the no-spawn/`None`-return assertion is unchanged.
- Full suite: `py -m pytest tests/test_crew_launcher.py -q` → 236 passed, 1
  failure (the pre-existing `ScratchDirResumeTests` `CREW_SCRATCH_DIR`-leak
  case named in the launch order's own Inherited Context — verify it is the
  **same single failure**, not a new one).

## Allowed Scope
- `scripts/run_crew.py` — `CrewSpec` (field + `__post_init__`),
  `build_parser`, `build_entry`, `main()`'s two `CrewSpec(...)` sites.
- `tests/test_crew_launcher.py` — the rewritten/new tests named across both
  handoffs.

## Specific Exclusions
- `resume_crew()`, `CliBackend.resume()`, `ExternalBackend.resume()` — must
  show zero diff.
- `map/INDEX.md`, `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
  any `*SPINE*.template.json`, `specs/` — fenced to lane K.

## Constraints the Implementation Must Respect
- `resolve_model`'s signature/behavior from g2 is unchanged (g3 wires it, does
  not modify it — diff `scripts/run_crew.py`'s `resolve_model`/`ROLE_MODEL_TIERS`
  region and confirm zero changes there this gate).

## Map Anchors (inbound)
No architecture map exists in this repo (DEGRADED-UNPARSEABLE, waived by the
Admiral, evidence `e-plan-1`, `decision:map-index-is-admiral-owned`).
- **Decision anchors:** same set as g2, plus `decision:refuse-a-tierless-dispatch`
  (#611) — superseded in scope (an absent `--model` no longer hard-refuses
  when the role/harness pair has a table entry; still refuses when no table
  entry exists). `@grade: settled/human`

## Evidence Produced
See `g3-implement-result.md` (attempt 2): wiring grep (1 real call site),
all 4 `CrewSpec(` construction sites listed, `resume_crew()` zero-diff
confirmation via hunk-header line ranges, old-shape round-trip test, full
suite tally (236 passed, 1 known-unrelated). Targets `g3-integrate.c1`.

## Suggested Model Tier
sonnet — moderate risk (shared choke point + rewritten tests), well-specified
by two handoffs.

## Stop Conditions
Stop and return BLOCK if: any `CrewSpec(` construction site bypasses
`resolve_model`, `resume_crew()`/either backend's `resume()` shows any diff,
or a rewritten test's assertion no longer tests what its name claims.

## Return Format
Return REVIEW_RESULT per the standard shape, including Workflow Feedback.
Write it to `.agent-work/567-j/crew-handoffs/g3-reviewer-result.md` before
ending your turn.
