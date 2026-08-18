# Reviewer Handoff

## Gate
g2-implement (reviewing)

## Survey State Location
`.agent-work/567-j/g2-review/review.json`

## What Was Implemented
A pure, zero-I/O role×harness model-tier resolver added to `scripts/run_crew.py`:
`ROLE_MODEL_TIERS` (module-level table, populated only for harness `"claude"`,
with `"codex"`/`"local"` present as empty dicts), `ResolvedModel` (frozen
dataclass), and `resolve_model(role, harness, requested, reason)` implementing
five branches. Additive-only — nothing in the module calls it yet (wiring is
g3).

## How to Inspect the Diff
Uncommitted working tree. `git status --porcelain` then
`git diff scripts/run_crew.py tests/test_crew_launcher.py`.

## Task Statement
See `.agent-work/567-j/crew-handoffs/g2-implement-handoff.md` Close Criteria
for the exact table values and the five branches in their required order.

## Close Criteria
- `ROLE_MODEL_TIERS["claude"]` matches exactly: `admiral` → default `opus`,
  allowed `{opus}`; `commander`/`implementer`/`reviewer`/`critic`/`cartographer`
  → default `sonnet`, allowed `{sonnet, haiku}`. `"codex"` and `"local"` keys
  exist and are empty dicts — no invented model identifiers anywhere.
- `resolve_model`'s five branches match the handoff's exact order and
  semantics (missing role/harness refuses by name before any requested-value
  check runs; falsy requested resolves default with no reason; out-of-set
  requested refuses by name; in-set non-default with no reason refuses;
  in-set default-or-reasoned succeeds).
- `resolve_model`/`ROLE_MODEL_TIERS` are referenced **only** inside their own
  definitions and the new test file — confirm by reading the grep output, not
  by trusting the IMPLEMENTER_RESULT's claim.
- `resolve_model` performs no filesystem/subprocess/env access (read the
  function body directly).
- Full existing suite unaffected: the IMPLEMENTER_RESULT claims 216
  pre-existing + 13 new = 229 passed, 1 pre-existing unrelated failure
  (`ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`,
  a documented pre-existing failure from `CREW_SCRATCH_DIR` leaking into this
  crew's own dispatched-process environment — named in the launch order's own
  Inherited Context as a known, unrelated, do-not-fix failure). Verify this is
  the **same single failure**, not a new one, by re-running the suite yourself.

## Allowed Scope
- `scripts/run_crew.py` — only the new table, dataclass, function beside
  `build_crew_argv`.
- `tests/test_crew_launcher.py` — only the new `ResolveModelTests` class.

## Specific Exclusions
- `CrewLaunchSpec`, `build_parser`, `build_entry`, `main`, `resume_crew` — must
  show zero diff. Flag if any of these five names appear in the diff at all.
- `map/INDEX.md`, `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
  any `*SPINE*.template.json`, `specs/` — fenced to lane K.

## Constraints the Implementation Must Respect
- No new file/module created.
- `resolve_model`'s parameter order is `role, harness, requested, reason`.
- `ROLE_MODEL_TIERS`'s `"allowed"` values are `frozenset`, not `list`/`set`.

## Map Anchors (inbound)
No architecture map exists in this repo (DEGRADED-UNPARSEABLE, waived by the
Admiral, evidence `e-plan-1`, `decision:map-index-is-admiral-owned`).
- **Decision anchors:** `decision:ship-todays-tiers`, `decision:fail-closed-cheaper`,
  `decision:refuse-by-name`, `decision:reason-on-deviation`,
  `decision:harness-dimension-is-required` — all `@grade: settled/human` or
  `settled/doctrine`; flag any contradiction as a decision candidate rather
  than silently accepting a deviation.

## Evidence Produced
See `.agent-work/567-j/crew-handoffs/g2-implement-result.md`: full
`ResolveModelTests` output (13 tests, individually named), a TDD red/green
proof, two wiring greps confirming additive-only. This evidence targets
`g2-integrate.c1`.

## Suggested Model Tier
sonnet — bounded verification of pure logic against a fixed spec.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, the table values or
branch semantics deviate from the handoff without a surfaced reason, or
`resolve_model`/`ROLE_MODEL_TIERS` has any call site outside its own
definition and the new test file.

## Return Format
Return REVIEW_RESULT per the standard shape, including Workflow Feedback.
Write it to `.agent-work/567-j/crew-handoffs/g2-reviewer-result.md` before
ending your turn.
