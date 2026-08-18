# Review Result

## Assigned Gate
`g2-implement (reviewing)`

## Result
`APPROVE`

## Handoff compliance
Satisfied. `ROLE_MODEL_TIERS` matches the handoff's table exactly: `admiral` -> default `opus`, allowed `{opus}`; `commander`/`implementer`/`reviewer`/`critic`/`cartographer` -> default `sonnet`, allowed `{sonnet, haiku}`; `"codex"`/`"local"` present as empty dicts. `ResolvedModel` is a frozen dataclass with `model: str`, `reason: str | None` (frozen-ness independently confirmed by a mutation attempt raising, both in the existing test and by reading the `@dataclass(frozen=True)` decorator). `resolve_model(role, harness, requested, reason)` implements all five branches in the exact required order: (1) missing role/harness refuses by name before any requested-value check; (2) falsy `requested` resolves the default with no reason; (3) out-of-set `requested` refuses by name; (4) in-set non-default with no `reason` refuses; (5) in-set default-or-reasoned succeeds, reason carried through. Required evidence (full `ResolveModelTests` output, wiring greps, suite delta) all present in `g2-implement-result.md` and independently reproduced (below). No stop condition was hit.

## Scope drift
None. Diff confined to `scripts/run_crew.py` (new table/dataclass/function beside `build_crew_argv`) and `tests/test_crew_launcher.py` (new `ResolveModelTests` class). `CrewLaunchSpec`, `build_parser`, `build_entry`, `main`, `resume_crew` show zero diff — the only appearance of `CrewLaunchSpec` in the diff is a docstring sentence, not an edit to that function. No new file/module created. Fenced paths (`map/INDEX.md`, `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `*SPINE*.template.json`, `specs/`) untouched. Uncommitted changes to `scripts/install_constellation.py`/`tests/test_install_constellation.py` exist in the working tree but are outside this diff's two target files (pre-existing g1-lane work sharing the same uncommitted tree).

## Evidence verdict
Satisfies required evidence and test mode. Independently re-ran `py -m pytest tests/test_crew_launcher.py -q`: **229 passed, 1 failed** — the single failure is `ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`, verified to be the identical pre-existing `CREW_SCRATCH_DIR`-leak failure named in the handoff (same test, same assertion), not a new failure. `py -m pytest tests/test_crew_launcher.py -k ResolveModelTests -v` shows all 13 named tests passing, matching `g2-implement-result.md`'s list exactly. Applied the project's own verification discipline (`docs/agents/CREW_CONTEXT.md` "a check that cannot fail is indistinguishable from one that passed"): mutated `implementer`'s declared default from `sonnet` to `haiku` in `ROLE_MODEL_TIERS`, re-ran `ResolveModelTests` — 4 tests went red (`test_blank_string_requested_also_resolves_to_default`, `test_default_tier_explicit_choice_never_requires_a_reason`, `test_every_populated_claude_role_resolves_to_its_own_default`, `test_non_default_in_set_choice_with_no_reason_is_refused`), confirming the tests assert real behavior rather than passing vacuously; restored the file from a backup copy and confirmed 13/13 green again. Wiring greps re-run independently: `grep -n "resolve_model\|ROLE_MODEL_TIERS" scripts/run_crew.py` and the repo-wide `grep -rn "resolve_model" --include=*.py .` both show zero call sites outside the two definitions and `ResolveModelTests` — additive-only confirmed. Read `resolve_model`'s body directly: only module-level dict lookups and `raise`/`return` statements — no filesystem/subprocess/env access.

## Code/doc quality
Minimal, matches house style. Comment/docstring density and inline decision-anchor citations mirror the surrounding `build_crew_argv` style. `resolve_model`'s parameter order (`role, harness, requested, reason`) and `ROLE_MODEL_TIERS`'s `frozenset` "allowed" values match the handoff's fixed constraints exactly (confirmed by reading the source literal and by `test_role_model_tiers_allowed_values_are_frozenset`). Fowler code-smell pass complete (`.agent-work/567-j/FOWLER_PASS.json`, `scripts/verify_fowler_pass.py` exits 0): 11/12 baseline smells absent, 1 overridden — `speculative-generality` (the `codex`/`local` empty-dict scaffolding), subordinate to `decision:harness-dimension-is-required` (`@grade: settled/human`), with a logged standard + reason. Zero smells flagged as blocking.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the diff and test evidence back the claimed "additive-only, unwired" behavior; no dispatch path calls the new code.
- **Constraints not violated:** Yes — parameter order and `frozenset` type constraints both honored.
- **Notes match the diff:** Yes — `g2-implement-result.md`'s Map Impact notes (new structural anchor beside `build_crew_argv`, no observable capability change, five decision anchors consumed as given) match the diff exactly.
- **Decision candidates surfaced:** N/A this gate — no authority beyond the handoff's fixed decisions was needed; none silently overridden.
- **Durable context routed:** Yes — no architecture map exists in this repo (DEGRADED-UNPARSEABLE, waived by the Admiral, `decision:map-index-is-admiral-owned`); the handoff and result both correctly route map-shaped notes as decision-anchor references instead.

## Reconciliation check
None. All five decision anchors (`decision:ship-todays-tiers`, `decision:fail-closed-cheaper`, `decision:refuse-by-name`, `decision:reason-on-deviation`, `decision:harness-dimension-is-required`) map exactly onto the table values and the five `resolve_model` branches with no contradiction. Nothing here requires Commander reconciliation beyond what the handoff already scoped to g3 (wiring `resolve_model` into `CrewLaunchSpec.__post_init__`).

## Blockers
- none

## Out-of-scope observations
- none

## Workflow Feedback

- **Handoff gaps:** none — task, close criteria, allowed scope, specific exclusions, constraints, map anchors, and stop conditions were all present and sufficient to review without guessing.
- **Context rediscovered:** This crew's `SPINE_FILE`/`SPINE_SESSION` env (inherited unchanged; my own `crew-runs.json` entry records `"spine": null`) pointed at the **Commander's own live `spine.json`** (`work_id: "567-j"`, `type: "gated"`, session `constellation/567-j/lane-j/commander-delegated`) rather than a reviewer-scoped survey — `spine_status` returned the Commander's `execute` gate content, not a refusal. This matches a previously-documented pattern from the same lane's g1-implement crew (see that crew's own Workflow Feedback) and this session's own memory of the same misfit: a handoff-only (`--handoff`/`--result`, no `--spine`) dispatch should not leave the parent's live spine identity ambiently reachable. I built and drove my own `review.json` survey (from `templates/REVIEW_SURVEY.template.json`) through `scripts/checklist_engine.py`'s CLI directly, touching the Commander's spine not at all.
- **Instructions improvised around:** The reviewer `SKILL.md`'s opening instruction assumes "a dispatched crew's spine is bound for you before you start" is always true; it is not, for a handoff-only `run_crew.py` dispatch whose env still carries the parent's `SPINE_FILE`/`SPINE_SESSION`. I fell back to the skill's own documented alternate path (author `REVIEW_SURVEY.json` from the template, drive it via the bundled `checklist_engine.py`) rather than the door.
- **What would have made this easier:** Two concrete fixes: (1) `run_crew.py` should unset/clear `SPINE_FILE`/`SPINE_SESSION` in a handoff-only dispatched child's environment (no `--spine` given) instead of leaving the parent's identity reachable — this is the second independent report of the exact same misfit on this lane. (2) `REVIEW_SURVEY.template.json`'s `r6-fowler` postcondition command carries a `<reviewer-skill-dir>` placeholder that the survey's own instantiation convention (substitute `<work-id>` only) never fills — I hit `REFUSED: command postconditions unmet` on first `record` attempt and had to `amend --delta ... retext-check` the check text to the real path (`scripts/verify_fowler_pass.py` lives at repo root, not under `skills/reviewer/scripts/`) before it would pass. The template should either substitute this placeholder the same way `<work-id>` is substituted, or drop it and hardcode the repo-root-relative path, since every consumer of this template lives in the same repo layout.

## Return status
`complete`
