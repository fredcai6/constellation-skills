# Curator Report — weekly health pass 2026-07-24

Ran both instruments: fleet sweep (`collect_feedback.py` over 6 consuming projects) and corpus health (`curate_corpus.py --root skills`). **Zero mechanical mends this pass** — every fleet finding was either already resolved upstream (clear) or an engine-owner / needs-human design call (route); every corpus-health lint item was a linter false-positive or a triggering-sensitive trade-off (route to tooling). That is the expected shape when the ripe-lesson re-export ceremony keeps stale accumulation alive.

## Instruments

- **Fleet sweep:** 19 candidates across baseball_coaster (12), constellation-skills (8), network_elo (1), tennis_elo (7 — the sweep's positional-path run under-counts; read directly). f1Brainz + story_time already at preamble (nothing new). *Note: the first `collect_feedback.py` run mis-resolved project paths (positional roots, not `--repo`); re-run with absolute roots.*
- **Corpus health:** 73 findings / 52 flagged. Breakdown: invoker-tag missing (most skills, expected seeding), size>400 (orchestration skills, soft budget), duplication shingles (intentional `_shared` refs), description-lint (5 skills).

## Cleared — resolved upstream (verified against repo HEAD + global install)

| Finding | Verification |
|---|---|
| `drill-scenario-decontamination` | Graduated in **#213** — `skills/lessons-auditor/SKILL.md:62` + repro-drill spec. |
| `command-postcondition-cannot-attest` | Graduated in **#213** — EXECUTE_PLAN gN-integrate imperative + checklist-engine.md + repro drill. |
| `config-ref-absent-skill-source` | Graduated in **#213** (same trio; was not exported but closed the class). |
| `delegated-latitude-vs-automode-classifier` | Self-marked RESOLVED 2026-07-19 (baseball epic-15 closeout) + LATITUDE_CONTRACT permission-prerequisites; a live run's `gh pr create`/`gh issue comment` both succeeded first-try under identical latitude. |
| `init_work_area <epic-id>` + spine instantiation | **#114/#154 CLOSED** (PR #173/#203); repo `init_work_area.py` now instantiates spine.json + resolves placeholders, and the fix is present in the global install. Recurrences (network_elo, tennis_elo) were **install-lag**, not a live defect. |
| `stale-installed-corpus-sibling-import-drift` (this cycle's incidents) | #118/#154 fixes present in the install; concrete incidents resolved. Structural claim stays open on **#208** (see comment). |

## Routed — new issues

| # | Cluster | Source lessons |
|---|---|---|
| **#220** | engine + scripts CLI/refusal ergonomics paper-cuts | postcondition-suite-timeout (2×), from-child-gated, attest-preconditions, amend-vocab, rail-banner, attest-no-field, flag-candidate-arg, session-id-position (3× / 0 incidents), apply-lessons-delta-path, run-crew-verify-slash-workid |
| **#221** | admiral launch-order provenance & recipe-completeness | schema-claim-provenance (recur+broaden), paired-guard-and-ci (2×), obs-source-underspecified, schema-nullable-verify-exact, active-config-verification, bounded-crawl-idempotency (vindicated) |
| **#222** | subagent/crew detached-work stall — poll-in-turn + stall-watchdog | long-foreground-op-handoff (2 epics, ~7 data points), crew-resume-via-sendmessage-is-async (3rd), armed-poll-insufficient (2nd), delegated-commander-in-team-synchronous-crew |
| **#223** | reviewer handoff — external-ground-truth + end-to-end assertion | internal-consistency-not-sufficient (vindicated), grammar-layer-test-hides-assembly-bugs (confirmed) |

## Routed — recurrence pressure on existing issues

- **#208** — install-lag / harvest-before-sweep: reconfirmed; install measured 15 commits behind (`467a6b0`, 2026-07-19) though this cycle's specific fixes are present. Structural item stands; human re-sync is the interim mitigation.
- **#117** — corpus-health routing: invoker-tag rollout policy (don't retro-tag) + description-lint precision (explorer/lessons-auditor `Use when` false-positives; cartographer↔scout exclusion clauses; commander-delegated length-vs-confusable-triple).

## Measurement — before/after

- Fleet feedback files cleared to preamble + dated disposition note: baseball_coaster, constellation-skills, network_elo, tennis_elo. f1Brainz + story_time were already clear (untouched). No re-triage of these items next week.
- Corpus health: no mechanical property changed (0 mends); flagged counts unchanged by design — routed to #117 for the tooling/policy calls.

## Notes for the human

- baseball_coaster's `CONSTELLATION_FEEDBACK.md` is git-**tracked**; clearing it is a working-tree edit in that repo (f1Brainz/story_time also tracked but were untouched). constellation-skills/network_elo/tennis_elo are gitignored (local-only).
- Global-install re-sync recommended (15 commits behind, incl. the #213 doctrine graduations) — a human action; not performed by this sweep.
