# Lessons Audit — epic-198-burndown

Fresh-context lessons audit of the 2026-07-19 backlog-burndown epic (13 PRs, waves 1–3).
Driven through `LESSONS_AUDIT.json` (survey) via the checklist engine. **Nominations only** —
inbox deltas are applied via `apply_lessons_delta.py`; doctrine graduations are surfaced
`needs-human` and NOT self-applied.

## What was applied autonomously this audit
- **Main inbox delta** (`lessons-delta-main.json`) applied to `.agent-work/LESSONS.md` via `apply_lessons_delta.py` (tick → run 32): 1 confirm + 3 adds + 1 mention. Playbook now 4 active (cap 20).
- **8 constellation exports** appended to `.agent-work/CONSTELLATION_FEEDBACK.md`, each carrying its originating candidate slug as the stable fingerprint.

## Routing table

| # | Candidate (origin) | Scope | Disposition | Home | Authority | Status |
|---|---|---|---|---|---|---|
| 1 | `test-harness-concurrency-failsafe` (existing Active, epic-178) | project | **confirm** (re-validated) + nominate graduate | testing-conventions doc (with #7) | human (graduation) | applied (confirm); graduation needs-human |
| 2 | `verify-launch-order-claims-against-code` (152 + 154 consolidated) | project | **inbox add** (2 data points, mentions=2) | `.agent-work/LESSONS.md` | autonomous | applied |
| 3 | `observe-midprocess-state-not-via-end-output` (130) | handoff | **inbox add** | `.agent-work/LESSONS.md` | autonomous | applied |
| 4 | `verify-harness-field-and-drive-real-writer` (151) | project/testing | **inbox add** (staging for graduation) | `.agent-work/LESSONS.md` | autonomous | applied |
| 5 | `drill-scenario-decontamination` (157, HIGH) | constellation | **export** + graduate | `docs/superpowers/specs/2026-07-07-lesson-repro-drills-design.md` and/or `skills/lessons-auditor/SKILL.md` | human | exported; doctrine needs-human |
| 6 | `delegated-commander-in-team-synchronous-crew` (157, HIGH) | constellation | **export** + graduate | `skills/commander/references/crew-dispatch.md` | human | exported; doctrine needs-human |
| 7 | `command-postcondition-cannot-attest` (117, 3x) | constellation | **export** + graduate | `skills/commander/templates/EXECUTE_PLAN.template.json` gN-integrate + `skills/workbench/references/checklist-engine.md` | human | exported; doctrine needs-human |
| 8 | `from-child-gated-consolidation-refusal` (155) | constellation | **export** (code fix, design call) | `scripts/checklist_engine.py` advance() `--from-child` | human (design) | exported |
| 9 | `engine-attest-preconditions-before-start` (118) | project→constellation | **export** (code fix; reclassified) | `scripts/checklist_engine.py` current/start output | human (design) | exported |
| 10 | `engine-cli-rail-banner-obscures-results` (130) | constellation | **export** (code fix) — *not in brief* | `scripts/checklist_engine.py` | human (design) | exported |
| 11 | `engine-cli-flag-candidate-arg-shape` (130) | constellation | **export** (code fix, low) — *not in brief* | `scripts/checklist_engine.py` | human (design) | exported |
| 12 | `stale-installed-corpus-sibling-import-drift` (116) | constellation | **export** — tracked by #208 + human re-sync | corpus install / harvest doctrine (#208) | human | exported |
| 13 | `config-ref-absent-skill-source` (cg, 4 crews) | commander | **graduate** (doctrine) | commander plan/survey templates `config_ref` + CREW_CONTEXT note for skill-source worktrees | human | needs-human |
| 14 | `reviewer-docs-only-fowler-pass-framing` (118) | review | **graduate** (doctrine) | `skills/reviewer/SKILL.md` Fowler/smell-pass section (+ `FOWLER_PASS.template.json`) | human | needs-human |
| 15 | `doc-handoff-anchor-not-line-number` (cg) | handoff | **drop-with-reason** | — | — | dropped |
| 16 | `handoff-test-assertion-realizable-per-type` (cg) | handoff | **drop-with-reason** | — | — | dropped |
| 17 | `resolver-placeholder-assertion-only-testable-via-mock` (154) | project | **drop-with-reason** | — | — | dropped |

### Drop reasons (recorded, re-file if they recur)
- **15** `doc-handoff-anchor-not-line-number`: understood best-practice (anchor on symbols not line numbers); its own bank-reason says wait for a real miss, not a note. Recorded in cg AGENT_FEEDBACK. Re-file if a stale line-number anchor ever causes an actual miss.
- **16** `handoff-test-assertion-realizable-per-type`: single niche instance (a survey has no why_trail, so a dictated why_ref assertion is unrealizable). Understood, recorded in cg AGENT_FEEDBACK. Re-file if type-blind test-assertion specs recur.
- **17** `resolver-placeholder-assertion-only-testable-via-mock`: single niche defense-in-depth observation; understood, recorded in 154 AGENT_FEEDBACK. Re-file if a second all-mocked hard-check assertion recurs.

## Needs-human doctrine graduations (Admiral → Fred; DO NOT self-apply)

Each is a `.md` / `.template.*` edit — `authority=human` per the auditor skill. Ripe doctrine
edits should ship with a reproduction drill (I did not author drills here since these are
deferred surface-for-acceptance; the editor writes the fix, a fresh auditor writes the drill).

1. **Testing-conventions reference (NEW doc)** — graduate-and-retire BOTH `test-harness-concurrency-failsafe` (epic-178) and `verify-harness-field-and-drive-real-writer` (151). Both bank-reasons explicitly awaited a **second** testing-discipline data point; this epic supplied it (concurrency-failsafe re-applied in #204; the stop-rail harness-field discipline in #151). Proposed home: a new `docs/agents/TESTING_CONVENTIONS.md` (or a reviewer/implementer reference) holding two entries — (a) concurrent-file-I/O test fail-safe (try/except + guaranteed stop-signal in finally + daemon threads); (b) verify harness-supplied fields against the contract AND drive the real writer path, never a hand-injected fixture. Retire both inbox lessons citing that doc. *If Fred prefers to keep observing, the two lessons stay banked (their current state).*
2. **`drill-scenario-decontamination`** → add an anti-contamination rule to the reproduction-drill doctrine (`docs/superpowers/specs/2026-07-07-lesson-repro-drills-design.md` and/or `skills/lessons-auditor/SKILL.md` Reproduction drills section). Exact text in CONSTELLATION_FEEDBACK entry 1. HIGH (two fresh agents rediscovered it in one batch).
3. **`delegated-commander-in-team-synchronous-crew`** → note in `skills/commander/references/crew-dispatch.md` (and/or commander-delegated skill). Exact text in CONSTELLATION_FEEDBACK entry 2. HIGH.
4. **`command-postcondition-cannot-attest`** → reword `skills/commander/templates/EXECUTE_PLAN.template.json` gN-integrate imperative + `skills/workbench/references/checklist-engine.md`: command-kind gates are satisfied by `advance`, not `attest`. Reproduced 3x in one run. HIGH.
5. **`config-ref-absent-skill-source`** → conditionalize the commander plan/survey template `config_ref: docs/agents/engine-config.json` (absent in skill-source repos), or note the absent overlay in CREW_CONTEXT for skill-source worktrees. All 4 cg crews independently rediscovered inline config over the dead ref (strongest corroboration in the epic). Confirmed live this audit — this repo has no `docs/agents/engine-config.json`, and the audit's own survey ran with a config_ref that resolved to nothing.
6. **`reviewer-docs-only-fowler-pass-framing`** → add an explicit "docs-only Fowler pass" clause to `skills/reviewer/SKILL.md` (Fowler/smell-pass section): a genuine all-`absent` per-smell verdict on a prose diff is a COMPLETED pass the rail accepts, not a skip needing a `rail_exception`.

**Code-target design calls (engine owner, not doctrine-blocked but need a decision):** items 8–11 in CONSTELLATION_FEEDBACK are `scripts/checklist_engine.py` ergonomics. Two clusters — refusal-legibility (from-child gated-child; attest-preconditions-before-start) and CLI output/args (RAIL banner masking `tail`; flag-candidate arg shape). A code fix carries its own test suite as proof, so these can proceed autonomously *once the design is chosen*; surfaced for the engine owner rather than applied blind.

## Existing-lesson reconciliation
- `confirm lesson:test-harness-concurrency-failsafe` — ADMIRAL_LOG PR#204: #130 real-process-death test re-applied the concurrency-failsafe pattern (kills a REAL runner process) on a new concurrent-I/O test. Held a second time → confirmed (and now ripe to graduate, see needs-human #1).
- No `disconfirm` — no Active lesson was undermined by this run's evidence.

## Sweep-hygiene note for the curator
The root CONSTELLATION_FEEDBACK.md "Open, tracked as issues" line lists the **resume/unblock verb** (→ #152) as still open. **#152 shipped this epic** (PR #200: resume verb + amend retext-check). It is now fixed-upstream — the curator's next sweep should mark it resolved rather than re-surfacing it. (Not editing the script-owned `.collected.json` sidecar by hand, per its contract.)

## Workflow Feedback
- **Brief gaps:** The named-exports list in the RUN_BRIEF was **under-inclusive** — it omitted two constellation exports actually staged in `staged-feedback/runner-durability-130/CONSTELLATION_FEEDBACK.md` (`engine-cli-rail-banner-obscures-results`, `engine-cli-flag-candidate-arg-shape`). Cross-checking every trio's CONSTELLATION_FEEDBACK.md against the brief (per "don't trust the brief's summaries blindly") caught them. Recommend the brief's export list be generated from a `grep`/enumeration over the trios, not hand-summarized.
- **Artifact gaps:** none material. Staged trios were complete and readable; the 152/154 deltas self-cited each other (which is what let me consolidate them to one slug instead of forking identity). The two 157 CONSTELLATION_FEEDBACK.md copies (drill + drill-worktree-root) are byte-identical duplicates — harmless, but the harvest could dedup.
- **What would have made this audit easier:** a machine-generated manifest of `(trio, lesson-id, scope, op)` tuples across all staged deltas + worktree LESSONS.md, so consolidation/dedup starts from a table rather than reading 13 files. This is the same enumeration gap the brief hit.
