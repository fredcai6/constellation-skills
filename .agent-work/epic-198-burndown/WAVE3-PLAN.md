# Wave 3 plan (prepped while batch-2B + reviewer-154 run)

Dispatch only after wave 2 fully merges (clean main). Two batches, collision- and pool-aware.

## Batch 3A (opus — code/mechanism/drill)
- **#196** — Context Governor v2: gauge_reader thresholds as absolute-token caps (or emit used_tokens+window). Files: `scripts/gauge_reader.py` (+ maybe gauge writer hook). **Last CG issue gating #178 close.**
- **#118** — template/doctrine deltas + **item 4 the real mechanism fix**: durable-root (verify_agent_feedback/verify_lessons_applied/agent_work_root) resolves to MAIN checkout that under-epic fences block → all 4 worktree commanders THIS epic force-waived/hand-staged (live corroboration). Fix: spine postconditions pass `--root .` or agent_work_root honors worktree under active epic lease. Files: `IMPLEMENTER_HANDOFF.template.md`, `LATITUDE_CONTRACT.template.md`, `skills/curator/SKILL.md`, `scripts/agent_work_root.py` + verify scripts. Note: #154 just shipped `stage_feedback.py` (complementary — brief the commander).
- **#157** — drill-required doctrine graduations (spec-prename-adaptations → explorer/DESIGN_SPEC doctrine; latitude pre-clearance for eval missions → admiral latitude practice). Each ships WITH a reproduction drill authored by a FRESH auditor (not the editor). Files: `skills/explorer/*`, `skills/admiral/SKILL.md` or LATITUDE_CONTRACT practice, drills.

## Batch 3B (sonnet — doc/test)
- **#116** — test hardening: SKILL_INDEX pin test, _shared→bundled sync-integrity test, SKILL_NAMES derived from discovery. Files: `tests/test_install_constellation.py` + new tests.
- **#155** — doc batch: windows.md headless-probe recipe; implementer SKILL engine-ref path drift (+ sibling audit); CHECKLIST_ENGINE_DESIGN.md _rail surface; harvest epic-id stamp. Files: `skills/_shared/windows.md`, `skills/implementer/SKILL.md`, `docs/CHECKLIST_ENGINE_DESIGN.md`.
- **#117 (partial)** — MECHANICAL tool fixes only: curate_corpus.py shared status/vocabulary contract fragment + matcher fixes (exclusion 'not ' anywhere; person shortlist 'us' false-positive). DEFER the consolidation run itself to Fred's human-invoked curator (per latitude default). Files: `scripts/curate_corpus.py` + its golden tests.

## Collision notes
- 3A #118 (curator SKILL.md, templates) vs 3B #117 (curate_corpus.py) — different files, OK.
- 3A #157 (admiral SKILL) vs #118 (LATITUDE_CONTRACT.template) — different files, OK.
- 3B #155 (implementer SKILL, windows.md, CHECKLIST_ENGINE_DESIGN.md) — disjoint from others.
- My fix-now doc pass (document #152 resume/amend verbs in docs/CHECKLIST_SCHEMA.md + workbench ref; name stage_feedback.py in docs/RECURSIVE_IMPROVEMENT_DESIGN.md) — CHECKLIST_SCHEMA.md ≠ CHECKLIST_ENGINE_DESIGN.md (#155), so disjoint. Do myself between waves, or give CHECKLIST_SCHEMA verb-doc to #196's commander (same CG/engine area).

## After wave 3
- Fix-now doc pass (above) if not folded.
- Close #178 (all CG fast-follows + #196 done).
- Closeout: batched harvest of all staged trios (.agent-work/staged-feedback/: cg-fastfollows-198, corpus-id-153, stop-rail-151, 152-engine-verbs, 154-init-placeholder, +2B), apply lessons-delta via apply_lessons_delta.py, sweep all cs-wt-* worktrees, lessons audit (fresh subagent + collect_feedback sweep since this is self-maintenance), cartographer reconcile, AGENT_FEEDBACK retrospective, archive ADMIRAL_LOG, present summary + surface #164 uninstall + deferred triage (#202 already filed, rail TC2-4, curate targets).
