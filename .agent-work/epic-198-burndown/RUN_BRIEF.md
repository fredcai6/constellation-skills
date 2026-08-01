# Run Brief — epic-198-burndown (for lessons-auditor)

## Epic intent
Backlog burndown of the 2026-07-19 open-issue triage: bounded bug/doc/engine/test fixes across 3 waves + housekeeping. This repo (constellation-skills) is the SUBJECT — self-maintenance / dogfooding.

## What shipped (13 PRs, main 467a6b0 → 8ba1293, +2721/-128 across 31 files)
- Wave 1: #153 corpus_id install-path invariance (PR#197); #189/#190/#191/#192 Context Governor engine fast-follows + schema doc (PR#199).
- Wave 2: #151 Stop-rail worktree-guard (PR#201); #152 resume verb + amend retext-check + heartbeat-on-mutate honest-null (PR#200); #154 init placeholder resolver-by-pattern + stage_feedback.py (PR#203); #130 runner-durability real-process-death test, mechanism-already-shipped partial-null (PR#204).
- Wave 3: #196 gauge absolute-token caps + verb-doc (PR#206); #118 worktree-aware durable-root + epic-101 template deltas (PR#207); #157 two doctrine graduations + fresh-auditor drills (PR#210); #116 test-hardening + SKILL_INDEX 3-entry fix (PR#209); #155 windows headless-probe + _rail doc (PR#211); #117 curator tooling (PR#212).
- Housekeeping: #93/#114/#163 closed (already-done/dup); epic #178 closed. Filed follow-ups #198/#202/#205/#208. Left open for human: #117 consolidation, #164 uninstall.

## Model tiers used
Commanders: opus for engine/hooks/mechanism (#153,189-192,151,152,130,196,118,157); sonnet for bounded doc/test/tooling (#154,116,155,117). Every commander ran an independent fresh-context reviewer (one, #154, skipped it and the Admiral supplied reviewer-154).

## Artifacts to audit
- ADMIRAL_LOG: `.agent-work/epic-198-burndown/ADMIRAL_LOG.md` (all rulings/incidents/merges + the "Closeout inputs" section).
- Staged trios (9 with lessons-delta.json): `.agent-work/staged-feedback/{corpus-id-153,cg-fastfollows-198,stop-rail-151,152-engine-verbs,154-init-placeholder,runner-durability-130,epic-198-w3-196-gauge,157-drill,117-curate}/` + worktree-root trios for 118-durable-root, 116-tests, 155-docs.
- Commander reports: `.agent-work/epic-198-burndown/wave-{1,2,3}/W*-REPORT.md`.

## Named exports/banks already surfaced during execute (verify + route)
- Constellation exports (both #157 auditors hit): `drill-scenario-decontamination` (high-confidence), `delegated-commander-in-team-synchronous-crew`.
- Banked lessons: `test-harness-concurrency-failsafe` (pre-existing active, epic-178), `config-ref-absent-skill-source` (all 4 cg crews — needs-human doctrine), `engine-attest-preconditions-before-start` + `reviewer-docs-only-fowler-pass-framing` (#118), engine-ergonomics `advance --from-child assumes survey child` (#155), plus each trio's own lessons-delta.json.

## Cross-project sweep
`collect_feedback.py` over f1Brainz/network_elo/story_time = NO new candidates (loop clean).

## Your task
Read the artifacts with fresh context. For every lesson candidate, route a disposition: graduate-and-retire to a named permanent home / template delta / Charter nomination / constellation export (carry originating lesson id) / lesson-inbox delta / drop-with-reason. Doctrine-target graduations (.md/.template.*) need authority=human → surface them as needs-human for the Admiral to present to Fred, do NOT self-apply. Code-target graduations stay autonomous. Apply inbox deltas ONLY via apply_lessons_delta.py --tick. Return your routed dispositions as your report.
