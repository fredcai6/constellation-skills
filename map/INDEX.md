# constellation-skills map

## packages
conftest: 1 modules, 3 entities
evals: 12 modules, 54 entities
examples: 1 modules, 4 entities
scripts: 63 modules, 1316 entities
skills: 1 modules, 22 entities
tests: 103 modules, 5723 entities

## conftest (1 modules, 3 entities)

- [conftest](conftest/INDEX.md) (3 entities, 2 holes): Repo-wide pytest configuration.

## evals (12 modules, 54 entities)

### evals.euler-1-multiples (4 modules, 18 entities)

- [evals.euler-1-multiples.checks.answer.answer_matches](evals.euler-1-multiples.checks.answer.answer_matches/INDEX.md) (3 entities, 3 holes): ADVISORY answer check -- NEVER gates the verdict (structural T3).
- [evals.euler-1-multiples.checks.artifact_present](evals.euler-1-multiples.checks.artifact_present/INDEX.md) (3 entities, 3 holes): PROCESS check (gating): the workflow produced a non-empty solution deliverable.
- [evals.euler-1-multiples.checks.spine_completed](evals.euler-1-multiples.checks.spine_completed/INDEX.md) (9 entities, 2 holes): PROCESS check (gating): a constellation ENGINE spine reached a terminal state WITH engine-written provenance -- not merely agent-written JSON (issue #127).
- [evals.euler-1-multiples.checks.tests_green](evals.euler-1-multiples.checks.tests_green/INDEX.md) (3 entities, 3 holes): PROCESS check (gating): tests were WRITTEN and PASS in the workspace.

### evals.euler-2-even-fibonacci (4 modules, 18 entities)

- [evals.euler-2-even-fibonacci.checks.answer.answer_matches](evals.euler-2-even-fibonacci.checks.answer.answer_matches/INDEX.md) (3 entities, 3 holes): ADVISORY answer check -- NEVER gates the verdict (structural T3).
- [evals.euler-2-even-fibonacci.checks.artifact_present](evals.euler-2-even-fibonacci.checks.artifact_present/INDEX.md) (3 entities, 3 holes): PROCESS check (gating): the workflow produced a non-empty solution deliverable.
- [evals.euler-2-even-fibonacci.checks.spine_completed](evals.euler-2-even-fibonacci.checks.spine_completed/INDEX.md) (9 entities, 2 holes): PROCESS check (gating): a constellation ENGINE spine reached a terminal state WITH engine-written provenance -- not merely agent-written JSON (issue #127).
- [evals.euler-2-even-fibonacci.checks.tests_green](evals.euler-2-even-fibonacci.checks.tests_green/INDEX.md) (3 entities, 3 holes): PROCESS check (gating): tests were WRITTEN and PASS in the workspace.

### evals.euler-5-smallest-multiple (4 modules, 18 entities)

- [evals.euler-5-smallest-multiple.checks.answer.answer_matches](evals.euler-5-smallest-multiple.checks.answer.answer_matches/INDEX.md) (3 entities, 3 holes): ADVISORY answer check -- NEVER gates the verdict (structural T3).
- [evals.euler-5-smallest-multiple.checks.artifact_present](evals.euler-5-smallest-multiple.checks.artifact_present/INDEX.md) (3 entities, 3 holes): PROCESS check (gating): the workflow produced a non-empty solution deliverable.
- [evals.euler-5-smallest-multiple.checks.spine_completed](evals.euler-5-smallest-multiple.checks.spine_completed/INDEX.md) (9 entities, 2 holes): PROCESS check (gating): a constellation ENGINE spine reached a terminal state WITH engine-written provenance -- not merely agent-written JSON (issue #127).
- [evals.euler-5-smallest-multiple.checks.tests_green](evals.euler-5-smallest-multiple.checks.tests_green/INDEX.md) (3 entities, 3 holes): PROCESS check (gating): tests were WRITTEN and PASS in the workspace.

## examples (1 modules, 4 entities)

### examples.mcp-interactive-demo (1 modules, 4 entities)

- [examples.mcp-interactive-demo.make_demo_spine](examples.mcp-interactive-demo.make_demo_spine/INDEX.md) (4 entities, 2 holes): Generate this directory's throwaway demo spine.

## scripts (63 modules, 1316 entities)

### scripts.code_map (10 modules, 137 entities)

- [scripts.code_map](scripts.code_map/INDEX.md) (0 entities): code_map — derive a code map for this repository from its own source.
- [scripts.code_map.__main__](scripts.code_map.__main__/INDEX.md) (0 entities): `python -m scripts.code_map` — the package's executable form.
- [scripts.code_map.build](scripts.code_map.build/INDEX.md) (1 entities): scripts/code_map/build.py -- the plain-importable build() seam.
- [scripts.code_map.checks](scripts.code_map.checks/INDEX.md) (34 entities, 10 holes): Checks over the built map that CAN FAIL.
- [scripts.code_map.cli](scripts.code_map.cli/INDEX.md) (9 entities, 7 holes): The code_map command line: one entrypoint in front of the whole pipeline.
- [scripts.code_map.discovery](scripts.code_map.discovery/INDEX.md) (3 entities): Enumerate the mappable corpus: the source files the map is derived from.
- [scripts.code_map.extract](scripts.code_map.extract/INDEX.md) (58 entities, 33 holes): Pure-AST statement extractor with its own cross-file name resolution.
- [scripts.code_map.precommit](scripts.code_map.precommit/INDEX.md) (6 entities, 1 holes): scripts/code_map/precommit.py -- the index-snapshot pre-commit mechanism.
- [scripts.code_map.render](scripts.code_map.render/INDEX.md) (26 entities, 10 holes): Full-repo derived map -- one page per entity, agent-lean.
- [scripts.code_map.thresholds](scripts.code_map.thresholds/INDEX.md) (0 entities): The numbers gate `gb` commits, and the one-line action for when each fires.

### scripts.hooks (3 modules, 92 entities)

- [scripts.hooks.code_map_precommit](scripts.hooks.code_map_precommit/INDEX.md) (3 entities, 2 holes): scripts/hooks/code_map_precommit.py -- fail-open git pre-commit hook shim.
- [scripts.hooks.gauge_writer_hook](scripts.hooks.gauge_writer_hook/INDEX.md) (22 entities, 4 holes): gauge_writer_hook.py -- Claude Code PostToolUse hook: Context Governor gauge WRITER (Module 2, write side; issue #180).
- [scripts.hooks.spine_rail](scripts.hooks.spine_rail/INDEX.md) (67 entities, 22 holes): spine_rail.py -- Claude Code hook suite for the Constellation spine rail.

- [scripts.agent_work_root](scripts.agent_work_root/INDEX.md) (6 entities, 1 holes): Resolve the DURABLE `.agent-work` root that survives `git worktree remove`.
- [scripts.apply_episode_delta](scripts.apply_episode_delta/INDEX.md) (57 entities, 25 holes): Deterministically apply structured episode-delta operations to the episode store.
- [scripts.build_architecture_map](scripts.build_architecture_map/INDEX.md) (16 entities, 15 holes): HOLE: no docstring
- [scripts.check_corpus_freshness](scripts.check_corpus_freshness/INDEX.md) (11 entities, 7 holes): Report whether an installed constellation corpus is current with upstream main.
- [scripts.check_role_spine_bookends](scripts.check_role_spine_bookends/INDEX.md) (6 entities, 4 holes): Lint: every role spine template declares at least one bookend, and the repo's declaration matches what is actually installed.
- [scripts.check_skill_freshness](scripts.check_skill_freshness/INDEX.md) (10 entities, 5 holes): Report template drift for a project against its installed-skill baseline.
- [scripts.check_template_overlay_freshness](scripts.check_template_overlay_freshness/INDEX.md) (5 entities, 3 holes): Guard: a project's `.agent-work/templates/` overlay must never be STALE.
- [scripts.checklist_engine](scripts.checklist_engine/INDEX.md) (124 entities, 23 holes): Workbench checklist engine: work one gated/survey plan through its gates.
- [scripts.collect_feedback](scripts.collect_feedback/INDEX.md) (38 entities, 15 holes): Sweep consuming projects' CONSTELLATION_FEEDBACK.md exports into one report.
- [scripts.context_manifest](scripts.context_manifest/INDEX.md) (14 entities): Deterministic projection substrate: what was made available to an agent, and at which revision.
- [scripts.curate_corpus](scripts.curate_corpus/INDEX.md) (18 entities, 4 holes): Curator MEASUREMENT pass over the skills corpus (mechanical-only, flags-never-gates).
- [scripts.docent_freshness](scripts.docent_freshness/INDEX.md) (9 entities, 5 holes): docent_freshness — deterministic staleness check for a docent explainer site.
- [scripts.episode_capture](scripts.episode_capture/INDEX.md) (15 entities): Assembly seam: the context manifest as a **byproduct of starting a step**.
- [scripts.file_issue_set](scripts.file_issue_set/INDEX.md) (44 entities, 41 holes): File only the runnable current wave from a verified initial issue set.
- [scripts.gauge_reader](scripts.gauge_reader/INDEX.md) (14 entities): Gauge reader -- fail-safe read of the context-fullness gauge file.
- [scripts.generate_spine](scripts.generate_spine/INDEX.md) (31 entities, 13 holes): Compile a `specs/<role>.spine.toml` spec into an engine-native spine JSON, and refuse to emit anything `scripts/validate_spine.py` would reject.
- [scripts.grade_lint](scripts.grade_lint/INDEX.md) (32 entities, 24 holes): Lint `@grade:` decision tags — a plan decision's fixedness as an inline, greppable property of the decision itself, so no second hand-maintained ledger ever has
- [scripts.init_work_area](scripts.init_work_area/INDEX.md) (7 entities, 2 holes): Scaffold a Constellation work area: .agent-work/<work-id>/ and its subdirs.
- [scripts.install_constellation](scripts.install_constellation/INDEX.md) (97 entities, 32 holes): HOLE: no docstring
- [scripts.map_orient](scripts.map_orient/INDEX.md) (61 entities, 17 holes): Orient an agent against a repo's architecture map -- or REPORT that it cannot.
- [scripts.mcp_spine_server](scripts.mcp_spine_server/INDEX.md) (40 entities, 3 holes): MCP front door for the checklist engine (issue #424, workstream F of epic #418).
- [scripts.measure_overread](scripts.measure_overread/INDEX.md) (10 entities, 2 holes): measure_overread.py -- count STRUCTURAL READS per agent run in a transcript.
- [scripts.query_episodes](scripts.query_episodes/INDEX.md) (22 entities, 7 holes): Deterministic retrieval over the episode store (docs/EPISODE_STORE.md section 8).
- [scripts.recover_crews](scripts.recover_crews/INDEX.md) (8 entities, 3 holes): Recovery classifier over the durable crew-run registry.
- [scripts.run_crew](scripts.run_crew/INDEX.md) (86 entities, 23 holes): Safe crew launcher with a durable session-recovery registry.
- [scripts.run_skill_eval](scripts.run_skill_eval/INDEX.md) (42 entities, 10 holes): Corpus skill-eval runner — the PURE, agent-free core (#106, gate g2).
- [scripts.spine_done_cli](scripts.spine_done_cli/INDEX.md) (3 entities, 2 holes): Thin CLI wrapping `spine_lifecycle.finish_work` -- the reachable-today "one door verb" (#574 g3): "I'm done" as one call, usable today without waiting on `mcp_s
- [scripts.spine_lifecycle](scripts.spine_lifecycle/INDEX.md) (28 entities, 3 holes): Open and close Constellation work in one call each: `open_work` builds a worktree, a branch, a scaffolded work area, and a compiled, origin-stamped spine; `clos
- [scripts.validate_spine](scripts.validate_spine/INDEX.md) (24 entities, 10 holes): Refuse a spine or spine template the engine cannot read, or that carries a check which cannot fail.
- [scripts.verify_context_declaration](scripts.verify_context_declaration/INDEX.md) (7 entities, 1 holes): Lint: every declared `context_refs` path must appear verbatim in its own task's `imperative` prose.
- [scripts.verify_coverage_ledger](scripts.verify_coverage_ledger/INDEX.md) (6 entities, 2 holes): Verify the removability coverage ledger against the installed-externals manifest.
- [scripts.verify_cycles](scripts.verify_cycles/INDEX.md) (4 entities, 3 holes): Verify a work area's exploration cycles are consolidated before explore closes.
- [scripts.verify_declared_dispatch](scripts.verify_declared_dispatch/INDEX.md) (3 entities, 1 holes): Refuse to advance a gate whose declared `[[gate.dispatch]]` (LIFECYCLE_CONTRACT.md section 5) was not actually recorded.
- [scripts.verify_diagnosis](scripts.verify_diagnosis/INDEX.md) (10 entities, 3 holes): Refuse an unreproduced diagnosis — the constellation-diagnose RAIL.
- [scripts.verify_epic_418_demo](scripts.verify_epic_418_demo/INDEX.md) (29 entities, 28 holes): Generate or verify the hash-pinned, fully offline Epic #418 demonstration.
- [scripts.verify_episode_captured](scripts.verify_episode_captured/INDEX.md) (6 entities, 2 holes): Capture gate: refuse to advance until THIS run left an episode in the store.
- [scripts.verify_episode_observations](scripts.verify_episode_observations/INDEX.md) (14 entities, 8 holes): Guard: refuse a store whose records read as instructions instead of observations.
- [scripts.verify_fowler_pass](scripts.verify_fowler_pass/INDEX.md) (9 entities, 3 holes): Refuse a skipped smell or a silent override — the reviewer Fowler-pass RAIL.
- [scripts.verify_installed_bundles](scripts.verify_installed_bundles/INDEX.md) (8 entities, 6 holes): Compare every installed skill bundle against the source it was built from.
- [scripts.verify_interrogation](scripts.verify_interrogation/INDEX.md) (9 entities, 3 holes): Refuse a self-answered or unsigned interrogation — the interrogator RAIL.
- [scripts.verify_issue_set](scripts.verify_issue_set/INDEX.md) (18 entities, 14 holes): Verify and render the strict v1 initial-cut contract.
- [scripts.verify_iterative_planning_acceptance](scripts.verify_iterative_planning_acceptance/INDEX.md) (6 entities, 5 holes): Verify all ten frozen iterative-planning acceptance items offline.
- [scripts.verify_iterative_role_artifacts](scripts.verify_iterative_role_artifacts/INDEX.md) (20 entities, 11 holes): Verify installed iterative-planning role artifacts without tracker/network I/O.
- [scripts.verify_retirement](scripts.verify_retirement/INDEX.md) (19 entities, 3 holes): Guard the #403 retirement: scan the tracked tree and NAME what is still wrong.
- [scripts.verify_skill_registered](scripts.verify_skill_registered/INDEX.md) (6 entities, 2 holes): Refuse a mechanically-broken or unregistered skill — the constellation-write-a-skill RAIL.
- [scripts.verify_skip_guard](scripts.verify_skip_guard/INDEX.md) (5 entities, 2 holes): Verify no undocumented pytest skip slipped into a run's --junitxml report.
- [scripts.verify_spec_confirmed](scripts.verify_spec_confirmed/INDEX.md) (11 entities, 5 holes): Verify a shaped-design spec's Confirmation block and findings table.
- [scripts.verify_state_note](scripts.verify_state_note/INDEX.md) (6 entities, 3 holes): Verify a crash-resume state note exists and is filled, before detached work.
- [scripts.verify_worktree_isolation](scripts.verify_worktree_isolation/INDEX.md) (10 entities, 4 holes): Verify git worktree isolation is real before — and inside — a parallel wave.
- [scripts.wire_mcp_interpreter](scripts.wire_mcp_interpreter/INDEX.md) (3 entities, 3 holes): Resolve THIS machine's Python interpreter into `.mcp.json` (M2 job 2).

## skills (1 modules, 22 entities)

### skills.replan (1 modules, 22 entities)

- [skills.replan.scripts.verify_replan](skills.replan.scripts.verify_replan/INDEX.md) (22 entities, 14 holes): Verify and render strict offline v1 wave-replanning packets.

## tests (103 modules, 5723 entities)

### tests.fixtures (3 modules, 6 entities)

- [tests.fixtures.bom_corpus.bom_sample](tests.fixtures.bom_corpus.bom_sample/INDEX.md) (1 entities): A module with a BOM prefix to test handling.
- [tests.fixtures.comment_tags_corpus.corpus](tests.fixtures.comment_tags_corpus.corpus/INDEX.md) (3 entities): Fixture corpus for gate g7's comment-tag negative tests (issue #456).
- [tests.fixtures.spine_lint.fixture_tests](tests.fixtures.spine_lint.fixture_tests/INDEX.md) (2 entities, 2 holes): HOLE: no docstring

- [tests.test_agent_work_root](tests.test_agent_work_root/INDEX.md) (38 entities, 33 holes): Tests for the durable-root resolution helper and its wiring into the four recursive-improvement scripts.
- [tests.test_build_architecture_map](tests.test_build_architecture_map/INDEX.md) (8 entities, 8 holes): HOLE: no docstring
- [tests.test_bytecode_cache_provenance](tests.test_bytecode_cache_provenance/INDEX.md) (14 entities, 4 holes): #597 — a bytecode cache built in a different tree must be named, not suffered.
- [tests.test_check_corpus_freshness](tests.test_check_corpus_freshness/INDEX.md) (15 entities, 14 holes): HOLE: no docstring
- [tests.test_check_role_spine_bookends](tests.test_check_role_spine_bookends/INDEX.md) (11 entities, 7 holes): #567 lane L: the role-spine-template bookend lint.
- [tests.test_check_script_registration](tests.test_check_script_registration/INDEX.md) (13 entities, 8 holes): Registration lint + vocabulary rule for issue #345 ("built but not wired").
- [tests.test_check_skill_freshness](tests.test_check_skill_freshness/INDEX.md) (13 entities, 7 holes): Coverage for `_resolved_interpreter()`'s sidecar-missing/malformed fallback (issue #532).
- [tests.test_check_template_overlay_freshness](tests.test_check_template_overlay_freshness/INDEX.md) (14 entities, 3 holes): The overlay-freshness guard `scripts/check_template_overlay_freshness.py` was written to catch exactly what `tests/test_cli_retirement_guard.py`'s own docstring
- [tests.test_checklist_engine](tests.test_checklist_engine/INDEX.md) (735 entities, 561 holes): HOLE: no docstring
- [tests.test_checklist_engine_atomic_save](tests.test_checklist_engine_atomic_save/INDEX.md) (39 entities, 22 holes): #613 (atomicity half): `checklist_engine.save()` must install the new document by ATOMIC RENAME, never by writing over the live target in place.
- [tests.test_clamp_presence](tests.test_clamp_presence/INDEX.md) (3 entities, 3 holes): Presence test for issue #142 clamp restoration.
- [tests.test_cli_retirement_guard](tests.test_cli_retirement_guard/INDEX.md) (38 entities, 24 holes): Regrowth guard for issue #559 -- the door is the interface, not a second path.
- [tests.test_code_map](tests.test_code_map/INDEX.md) (348 entities, 191 holes): Tests for scripts/code_map/ — the derived code map (issue #456, gate g0).
- [tests.test_code_map_precommit](tests.test_code_map_precommit/INDEX.md) (32 entities, 27 holes): Tests for scripts/code_map/precommit.py and scripts/hooks/code_map_precommit.py (epic #569 gate g1-implement) -- the index-snapshot pre-commit mechanism and its
- [tests.test_code_map_precommit_e2e](tests.test_code_map_precommit_e2e/INDEX.md) (33 entities, 23 holes): tests/test_code_map_precommit_e2e.py -- gate g3-implement (epic #569): end-to-end proof that gates 1-2's shipped code (the index-snapshot pre-commit mechanism a
- [tests.test_commander_evidence_convention](tests.test_commander_evidence_convention/INDEX.md) (8 entities, 8 holes): Pin the g1-implement evidence convention (epic-559/b-instructions-to-checks, rework).
- [tests.test_context_declaration_lint](tests.test_context_declaration_lint/INDEX.md) (22 entities, 18 holes): Tests for `scripts/verify_context_declaration.py` -- the mechanical lint pinning every declared `context_refs` path against the step's own imperative prose.
- [tests.test_context_determinism](tests.test_context_determinism/INDEX.md) (25 entities, 21 holes): The acceptance test for issue #300: the projection manifest's *content* is identical across environments.
- [tests.test_context_manifest](tests.test_context_manifest/INDEX.md) (97 entities, 85 holes): Tests for `scripts/context_manifest.py` — the deterministic projection substrate.
- [tests.test_crew_delivery_addressing](tests.test_crew_delivery_addressing/INDEX.md) (11 entities, 7 holes): Relaunch acceptance test for #507 / #370 / #413 (crew delivery addressing).
- [tests.test_crew_dispatch_doctrine](tests.test_crew_dispatch_doctrine/INDEX.md) (3 entities, 2 holes): #611 (cleanup-g-crew-tier) g2-doctrine: crew-dispatch.md must name the 'Suggested Model Tier' handoff field as the thing a Commander resolves --model from, conn
- [tests.test_crew_launcher](tests.test_crew_launcher/INDEX.md) (359 entities, 275 holes): HOLE: no docstring
- [tests.test_crew_worktree_cwd](tests.test_crew_worktree_cwd/INDEX.md) (19 entities, 13 holes): A dispatched crew runs in ITS OWN worktree (issue #568, the g1b delta).
- [tests.test_curate_corpus](tests.test_curate_corpus/INDEX.md) (40 entities, 23 holes): Golden-fixture suite for scripts/curate_corpus.py.
- [tests.test_declared_dispatch](tests.test_declared_dispatch/INDEX.md) (14 entities, 14 holes): Tests for scripts/verify_declared_dispatch.py -- the oracle the generator's injected `[[gate.dispatch]]` postcondition (LIFECYCLE_CONTRACT.md section 5) shells 
- [tests.test_diagnose](tests.test_diagnose/INDEX.md) (32 entities, 27 holes): Tests for the constellation-diagnose skill's rail (scripts/verify_diagnosis.py).
- [tests.test_docent_freshness](tests.test_docent_freshness/INDEX.md) (18 entities, 17 holes): Unit tests for scripts/docent_freshness.py.
- [tests.test_engine_survey_retext_and_newlines](tests.test_engine_survey_retext_and_newlines/INDEX.md) (10 entities, 4 holes): Issue #465: the engine must not churn a file's line endings, and `amend`'s `retext-check` op must be usable on a SURVEY checklist.
- [tests.test_epic_418_demo](tests.test_epic_418_demo/INDEX.md) (6 entities, 6 holes): Focused tests for the frozen, offline Epic #418 demonstration contract.
- [tests.test_episode_capture](tests.test_episode_capture/INDEX.md) (41 entities, 20 holes): Tests for `scripts/episode_capture.py` — the assembly seam that makes the context manifest a *byproduct* of starting a spine step.
- [tests.test_episode_fields](tests.test_episode_fields/INDEX.md) (98 entities, 61 holes): Tests for the MECHANICAL FIELD COMPOSER — `episode_capture.mechanical_fields()` and the snapshot it emits at the g1 seam (#305 gate g2).
- [tests.test_episode_negative_control](tests.test_episode_negative_control/INDEX.md) (49 entities, 17 holes): #305 gate g3 — the NEGATIVE CONTROL for `zero agent effort is literal`.
- [tests.test_episode_observation_guard_at_write](tests.test_episode_observation_guard_at_write/INDEX.md) (18 entities, 8 holes): Tests for the write-time instruction-shaped-statement guard in scripts/apply_episode_delta.py (episode-guard-at-write).
- [tests.test_episode_observations](tests.test_episode_observations/INDEX.md) (32 entities, 12 holes): Tests for scripts/verify_episode_observations.py — the guard that keeps episode records reading as observations rather than instructions (issue #460).
- [tests.test_episode_store](tests.test_episode_store/INDEX.md) (227 entities, 137 holes): Tests for the episode store (docs/EPISODE_STORE.md): scripts/apply_episode_delta.py, the validated all-or-nothing writer (gate g2), and scripts/query_episodes.p
- [tests.test_explorer_templates](tests.test_explorer_templates/INDEX.md) (43 entities, 42 holes): Verifier<->template cross-check for the constellation-explorer engine artifacts.
- [tests.test_feedback_tooling](tests.test_feedback_tooling/INDEX.md) (61 entities, 59 holes): HOLE: no docstring
- [tests.test_force_claim_occupancy](tests.test_force_claim_occupancy/INDEX.md) (14 entities, 9 holes): #369 (resume side): a force takeover reports what the artifacts around the spine say about who else has been here, as counts and ages, with no verdict.
- [tests.test_fowler_pass](tests.test_fowler_pass/INDEX.md) (37 entities, 31 holes): Tests for the constellation-reviewer sharpening rail (scripts/verify_fowler_pass.py).
- [tests.test_gauge_chain_writer_to_trip](tests.test_gauge_chain_writer_to_trip/INDEX.md) (35 entities, 1 holes): The Context Governor chain, traversed end to end with REAL OS subprocesses:
- [tests.test_gauge_reader](tests.test_gauge_reader/INDEX.md) (105 entities, 80 holes): HOLE: no docstring
- [tests.test_gauge_writer](tests.test_gauge_writer/INDEX.md) (103 entities, 26 holes): Unit tests for scripts/hooks/gauge_writer_hook.py.
- [tests.test_generate_spine](tests.test_generate_spine/INDEX.md) (191 entities, 190 holes): Tests for scripts/generate_spine.py -- the spine spec compiler and generator.
- [tests.test_grade_lint](tests.test_grade_lint/INDEX.md) (50 entities, 35 holes): Tests for scripts/grade_lint.py — the @grade: inline-tag linter (issue #230, epic-226).
- [tests.test_implementer_vocab](tests.test_implementer_vocab/INDEX.md) (7 entities, 7 holes): Light vocabulary assertion for the constellation-implementer sharpening (DESIGN_SPEC Section D2 — vertical-slice vocabulary).
- [tests.test_in_harness_crew_isolation](tests.test_in_harness_crew_isolation/INDEX.md) (11 entities, 7 holes): #632: an in-harness subagent shares its dispatcher's harness session id, so the checklist engine's MCP door resolves to the DISPATCHER's spine. The guard is a d
- [tests.test_init_work_area](tests.test_init_work_area/INDEX.md) (41 entities, 35 holes): HOLE: no docstring
- [tests.test_initial_issues](tests.test_initial_issues/INDEX.md) (27 entities, 27 holes): Contract tests for the canonical constellation-to-initial-issues seam.
- [tests.test_install_constellation](tests.test_install_constellation/INDEX.md) (322 entities, 181 holes): HOLE: no docstring
- [tests.test_interpreter_portability](tests.test_interpreter_portability/INDEX.md) (21 entities, 6 holes): HOLE: no docstring
- [tests.test_interrogation](tests.test_interrogation/INDEX.md) (40 entities, 36 holes): Tests for the constellation-interrogator sharpening rail (scripts/verify_interrogation.py).
- [tests.test_iterative_planning_acceptance](tests.test_iterative_planning_acceptance/INDEX.md) (5 entities, 5 holes): Focused tests for the ten-item iterative-planning acceptance verifier.
- [tests.test_iterative_planning_doctrine](tests.test_iterative_planning_doctrine/INDEX.md) (90 entities, 58 holes): Parsed role-doctrine invariants for the G1 -> G2 iterative planning chain.
- [tests.test_map_contract_wiring](tests.test_map_contract_wiring/INDEX.md) (36 entities, 11 holes): The map-first contract as it is actually SERVED to a Commander run.
- [tests.test_map_orient](tests.test_map_orient/INDEX.md) (125 entities, 91 holes): The falsification floor for scripts/map_orient.py.
- [tests.test_mcp_adoption](tests.test_mcp_adoption/INDEX.md) (69 entities, 29 holes): Adoption gate for the MCP door (issue #542 criterion 1, epic-418-followon g4a).
- [tests.test_mcp_door_engine_cwd](tests.test_mcp_door_engine_cwd/INDEX.md) (24 entities, 15 holes): The door stands in the bound spine's own worktree for an engine call (issue #568, the g1b delta).
- [tests.test_mcp_door_telemetry](tests.test_mcp_door_telemetry/INDEX.md) (18 entities, 4 holes): The MCP door's telemetry writes must never fail a call or kill the server (issue #604, cleanup-a-door gate g1).
- [tests.test_mcp_door_unbound](tests.test_mcp_door_unbound/INDEX.md) (34 entities, 20 holes): The MCP door must fail CLOSED when nothing usable is bound (issue #603, cleanup-a-door gate g3).
- [tests.test_mcp_friction_capture](tests.test_mcp_friction_capture/INDEX.md) (23 entities, 12 holes): Tests for the MCP door's own rejection capture (issue #541, epic-418-followon wave 2, gate g2).
- [tests.test_mcp_identity](tests.test_mcp_identity/INDEX.md) (68 entities, 23 holes): DC2 (separation) and DC3 (inheritance fails closed) acceptance tests for the MCP front door (issue #424, workstream F, gate g3).
- [tests.test_mcp_imperative_equivalence](tests.test_mcp_imperative_equivalence/INDEX.md) (23 entities, 12 holes): DC4 acceptance test for the MCP front door (issue #424, workstream F, gate g2): the CLI projection and the MCP tool result carry the SAME imperative text for EV
- [tests.test_mcp_lifecycle](tests.test_mcp_lifecycle/INDEX.md) (48 entities, 28 holes): Tests for the MCP lifecycle door -- `spine_open`/`spine_close` (`scripts/mcp_spine_server.py`'s `call_lifecycle_tool`, issue #559, C3/g3).
- [tests.test_mcp_rejection_episode_capture](tests.test_mcp_rejection_episode_capture/INDEX.md) (38 entities, 27 holes): Unit-level tests for the door-own rejection -> `episodes/` capture path (issue #541, epic #567 lane E).
- [tests.test_mcp_spine_bind](tests.test_mcp_spine_bind/INDEX.md) (121 entities, 57 holes): `spine_bind` -- binding the door to a spine that ALREADY EXISTS (epic #567 lane A, gate `g2-implement`).
- [tests.test_mcp_spine_server](tests.test_mcp_spine_server/INDEX.md) (67 entities, 42 holes): Tests for scripts/mcp_spine_server.py (issue #424, workstream F: the MCP front door on the checklist engine).
- [tests.test_measure_overread](tests.test_measure_overread/INDEX.md) (23 entities, 23 holes): Unit tests for scripts/measure_overread.py.
- [tests.test_mutation_floor](tests.test_mutation_floor/INDEX.md) (32 entities, 18 holes): EXECUTED falsifiability for scripts/map_orient.py.
- [tests.test_next_verbs_record_gate_comment](tests.test_next_verbs_record_gate_comment/INDEX.md) (16 entities, 12 holes): Issue #437: `_next_verbs()`'s comments must not restate a premise #422/#328 killed.
- [tests.test_plan_step_contract](tests.test_plan_step_contract/INDEX.md) (30 entities, 15 holes): The `plan` step's ordering and coverage rules, as SERVED to a Commander run.
- [tests.test_prose_deletions](tests.test_prose_deletions/INDEX.md) (16 entities, 12 holes): Pin the issue-#304 prose deletions in BOTH directions.
- [tests.test_prototyper_templates](tests.test_prototyper_templates/INDEX.md) (13 entities, 11 holes): Verifier<->template cross-check for the PROTOTYPE_RESULT.template.md gate.
- [tests.test_record_postcondition_wiring](tests.test_record_postcondition_wiring/INDEX.md) (29 entities, 26 holes): Tests for #422 (epic-418 workstream D, gate g2): `record()`'s new command-kind postcondition check (`scripts/checklist_engine.py`).
- [tests.test_replan](tests.test_replan/INDEX.md) (37 entities, 35 holes): Strict public-interface tests for evidence-driven wave replanning.
- [tests.test_retirement_guard](tests.test_retirement_guard/INDEX.md) (22 entities, 3 holes): Red-proofs for `scripts/verify_retirement.py` — the #403 retirement guard.
- [tests.test_role_tier_coverage](tests.test_role_tier_coverage/INDEX.md) (19 entities, 11 holes): Coverage guard for #567 lane N -- `ROLE_MODEL_TIERS` must declare every role live doctrine actually hands a model-tier-bearing dispatch artifact.
- [tests.test_run_skill_eval](tests.test_run_skill_eval/INDEX.md) (121 entities, 106 holes): Agent-free unit layer for scripts/run_skill_eval.py (#106, gate g2).
- [tests.test_shipped_check_commands_resolve](tests.test_shipped_check_commands_resolve/INDEX.md) (14 entities, 10 holes): Every shipped command check must actually run after instantiation (epic-559/b-instructions-to-checks, rework r3).
- [tests.test_shipped_examples_are_portable](tests.test_shipped_examples_are_portable/INDEX.md) (19 entities, 6 holes): A shipped example must run for the person who installed it.
- [tests.test_shipped_template_gates_satisfiable](tests.test_shipped_template_gates_satisfiable/INDEX.md) (8 entities, 7 holes): Prove the shipped EXECUTE_PLAN.template.json's g1-implement gate is actually satisfiable by a real drive of the real engine (epic-559/b-instructions-to-checks, 
- [tests.test_spine_lifecycle](tests.test_spine_lifecycle/INDEX.md) (220 entities, 194 holes): Tests for scripts/spine_lifecycle.py -- open and close Constellation work in one call each.
- [tests.test_spine_origin_isolation](tests.test_spine_origin_isolation/INDEX.md) (32 entities, 17 holes): The `origin` stamp is PROVENANCE: written, and read by nothing (#315/#568/#609).
- [tests.test_spine_provenance_check](tests.test_spine_provenance_check/INDEX.md) (34 entities, 32 holes): Provenance hardening for the eval `spine_completed` process check (issue #127).
- [tests.test_spine_rail](tests.test_spine_rail/INDEX.md) (239 entities, 104 holes): Unit tests for scripts/hooks/spine_rail.py.
- [tests.test_spine_session_id](tests.test_spine_session_id/INDEX.md) (7 entities, 3 holes): `spine_lifecycle.session_id_for` -- the ONE definition of the lease identity a spine for a `work_id` is driven under (epic #567 lane A, gate g2-implement).
- [tests.test_state_note](tests.test_state_note/INDEX.md) (15 entities, 15 holes): HOLE: no docstring
- [tests.test_subtest_failures_are_greppable](tests.test_subtest_failures_are_greppable/INDEX.md) (8 entities, 3 holes): A failing subtest must be findable by searching for `FAILED`.
- [tests.test_validate_spine](tests.test_validate_spine/INDEX.md) (108 entities, 98 holes): Tests for scripts/validate_spine.py (epic-559/c1-spine-lint, #518, #562).
- [tests.test_verify_coverage_ledger](tests.test_verify_coverage_ledger/INDEX.md) (12 entities, 12 holes): HOLE: no docstring
- [tests.test_verify_cycles](tests.test_verify_cycles/INDEX.md) (11 entities, 11 holes): HOLE: no docstring
- [tests.test_verify_episode_captured](tests.test_verify_episode_captured/INDEX.md) (32 entities, 17 holes): Tests for scripts/verify_episode_captured.py — the WRITE-side capture gate that replaces the retiring `.agent-work/LESSONS.md` / `.agent-work/AGENT_FEEDBACK.md`
- [tests.test_verify_installed_bundles](tests.test_verify_installed_bundles/INDEX.md) (18 entities, 11 holes): Tests for scripts/verify_installed_bundles.py -- the copy-vs-source check.
- [tests.test_verify_spec_confirmed](tests.test_verify_spec_confirmed/INDEX.md) (37 entities, 32 holes): HOLE: no docstring
- [tests.test_verify_spec_confirmed_cli](tests.test_verify_spec_confirmed_cli/INDEX.md) (7 entities, 6 holes): CLI-level regression coverage for verify_spec_confirmed.py's confirm-gate refusal.
- [tests.test_verify_worktree_isolation](tests.test_verify_worktree_isolation/INDEX.md) (40 entities, 39 holes): HOLE: no docstring
- [tests.test_wire_mcp_interpreter](tests.test_wire_mcp_interpreter/INDEX.md) (32 entities, 22 holes): Tests for scripts/wire_mcp_interpreter.py (M2 job 2, widened M2 g4-repair).
- [tests.test_work_id_nesting](tests.test_work_id_nesting/INDEX.md) (43 entities, 16 holes): A work-id may NEST, and four tools used to disagree about that.
- [tests.test_worktree_derivation](tests.test_worktree_derivation/INDEX.md) (8 entities, 1 holes): The case table that SPECIFIES the worktree-derivation rule, and drives it.
- [tests.test_worktree_precondition_wiring](tests.test_worktree_precondition_wiring/INDEX.md) (15 entities, 13 holes): Deliberate-breakage tests for a worktree-isolation precondition (#329/#422).
- [tests.test_write_a_skill](tests.test_write_a_skill/INDEX.md) (20 entities, 17 holes): Tests for constellation-write-a-skill's mint RAIL (scripts/verify_skill_registered.py) and the shared skill-goodness criteria seam.
