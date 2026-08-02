# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3` — instrument panel over the full 2023 corpus (#670)

## Result
`APPROVE`

## New-method adjudication (Admiral-delegated, central judgment)
**VERDICT: legitimate read-adapter generalization of the landed exhaustive-2v2-averaged scheme — does NOT cross into new statistical method.**

Reasoning:
1. **The estimator/decision machinery is imported and byte-unchanged.** `compare_channels_by_class`, `grand_two_way_center` (double-centering), `r_floor`, `channel_tie_margin` (via `frozen_replication_thresholds`), `main_effect_margin_uncertainty`, `widen_sigma_for_margin_uncertainty`, `out_of_sample_coverage`, and — critically — `decide_channel_from_mean_r` (the F12-registered average-then-decide rule) all enter `scripts/run_season_panel_670.py` only as imports. Independently confirmed: `git diff --stat` shows **zero diff** on `src/physics/instrument_panel/*` and `scripts/instrument_panel_668_report.py`; grep for local `def`/reassignment of any of these names in the new script found none; the implementer's own `test_no_local_reimplementation_of_frozen_rule_names` asserts the same.
2. **The only new logic is `enumerate_rotating_half_partitions`**, which replaces `enumerate_2v2_partitions` (hard-coded to exactly 4 circuits, producing the 3 *exhaustive* 2v2 partitions). This is a partition-**enumeration**/sampling-design function, not a statistic — it feeds the identical downstream averaging-then-decide pipeline (`_combine_class_verdict` → `decide_channel_from_mean_r`) that #668 already used over its 3 exhaustive partitions. Only the source and count of partitions changed (K=10 fixed deterministic rotating-block partitions vs. K=3 exhaustive), not what is computed *from* those partitions or how the final decision is made.
3. **The construction is a standard systematic/circular sampling design** (sort to canonical order, slide a contiguous half-window, K=n/2 distinct partitions — akin to a round-robin/circular block design), not an invented statistic. No new probability model, no new tunable threshold, no new formula for r or sigma.
4. **Every element of the Admiral's pre-ruled shape is satisfied, independently verified, not just claimed:**
   - Deterministic: two independent calls with different input orderings (`SIX_CIRCUITS` vs its reverse) produce byte-identical partitions (implementer's test, and I re-derived the same on the real 20-circuit corpus).
   - Seed-free: grep + the implementer's structural test confirm no `random`/`np.random`/`seed` anywhere in the module.
   - Balanced: every partition splits into two equal n/2 halves whose union is the full circuit set and whose intersection is empty (independently re-checked on the 6-circuit synthetic fixture and reasoned through the real 20-circuit case).
   - Averaged over K>1 fixed partitions: K=10 on the real corpus, independently reproduced via a direct interactive call to `enumerate_rotating_half_partitions` on the real 20-circuit list.
   - Exact construction stated in the report: `SPLIT_SCHEME_NOTE`, read directly.
5. The Admiral's ruling explicitly delegated *only* the exact construction choice to the implementer while freezing everything else. Rotating-block is a reasonable, fully-disclosed instantiation of that delegated choice — not an unauthorized expansion of latitude.
6. **One nuance, not a blocker** (routed as a triage candidate, tc2 below): unlike #668 where K=3 was *exhaustive* (no correlation-among-samples question), the rotating-block's stride-1 sliding window makes adjacent k-partitions differ by only one circuit, so the K=10 samples are structurally correlated rather than independent or exhaustive. This is a legitimate open question about how well this specific systematic design's variance-reduction property matches the exhaustive case — worth a follow-up sensitivity check (e.g. a coprime-stride design) — but it is a **design-quality** question about the partitioning choice, not evidence that a new statistic or decision rule was introduced.

**No BLOCK, no float to Admiral required on the new-method question.**

## Handoff compliance
Fully satisfied. `run_season_panel_670.py` runs all 4 instruments over the 20 covered circuits; `tests/unit/physics/instrument_panel/test_panel_corpus.py` covers split-scheme determinism/balance/K-count, corpus-panel end-to-end + reproduce-identical, exclusion of parked circuits, and no-reimplementation. Task statement (generalize only the split scheme, re-apply frozen rules byte-unchanged, no new instrument) honored.

## Scope drift
None. `git status --porcelain` shows only the two allowed new files (plus this gate's own `.agent-work` scratch). `src/physics/instrument_panel/*`, `scripts/instrument_panel_668_report.py`, and `docs/architecture/*` all show zero diff. `git check-ignore -v` on both new files exits 1 (trackable, not accidentally ignored).

Out-of-scope note (not a g3 violation): `git status` also shows ` M data/f1_data_2023.db` (binary-identical size, 0 insertions/0 deletions — a WAL/journal artifact, not opened by this script per grep) and ` M src/physics/pilot/pipeline.py` (adds `budget_s`/`refutil_db` params to `run_circuit` — g1/g2 season-pipeline scaffolding; `run_season_panel_670.py` does not import from `pipeline.py` at all). Both predate and are unrelated to g3's two-file scope.

## Evidence verdict
All required and confirmatory evidence independently re-run and matched exactly:
- `pytest tests/unit/physics/instrument_panel/test_panel_corpus.py -q` → **10 passed**.
- `pytest tests/unit/physics/instrument_panel -q` → **67 passed** (57 pre-existing + 10 new, zero regressions).
- `pyright scripts/run_season_panel_670.py tests/.../test_panel_corpus.py` → **0 errors/0 warnings/0 informations**.
- Real run over the actual scratch corpus (`--no-write`) → instrument1 numbers matched exactly (utilization `car_reference_share=0.692648`, energy `=0.819744`, n=1524 both).
- `--check-reproduce` → **PASS**.
- Direct interactive calls (not just trusting the report text): `read_covered_circuits_with_severity` + `intersect_with_covered_season_results` → 20 circuits, Bahrain and Saudi both absent; `enumerate_rotating_half_partitions` on the real 20-circuit list → K=10.

Test mode (`test-after`) is correctly applied for a read-adapter/wiring layer over already-TDD'd pure instrument modules — matches the #668 script's own precedent.

## Code/doc quality
Minimal, maintainable, project-rule compliant. OFFLINE (no FastF1/network import beyond docstring mentions), pinned interpreter used throughout this review, frozen rules byte-unchanged (verified above), Student-t σ preserved (`src.common.student_t.predictive_t` underlies `out_of_sample_coverage`/`widen_sigma_for_margin_uncertainty`, both imported unchanged).

**Fowler refactoring pass** (`.agent-work/670-season-run/g3-review/fowler_pass.json`, `verify_fowler_pass.py` exits 0): 12 baseline smells rendered, 1 flagged, 0 overridden.
- **Flagged — duplicated-code:** `build_half_cells`/`half_cell_sem`/`_metric_field` are duplicated verbatim from the #668 script's unexported private helpers (confirmed byte-identical logic). Disclosed by the implementer; pure aggregation arithmetic, not a decision rule, so it does not touch the new-method line — routed as triage candidate tc3, not a blocker.
- All other baseline smells (long-method, large-class, feature-envy, data-clumps, primitive-obsession, long-parameter-list, shotgun-surgery, divergent-change, message-chains, speculative-generality, comments-as-deodorant): **absent**.

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim independently reproduced (see Evidence verdict).
- **Constraints not violated:** yes — OFFLINE, frozen rules, Student-t σ, pinned interpreter all independently confirmed.
- **Notes match the diff:** yes — Map Impact's structural anchors (`enumerate_rotating_half_partitions`, `run_season_panel`) match the handoff's Map Anchors (which named `enumerate_2v2_partitions` as the thing to replace).
- **Decision candidates surfaced:** yes — the implementer correctly stopped short of unsettling `decision:panel-corpus-split-scheme` and left the new-method adjudication to review, per the handoff's authority split.
- **Durable context routed:** yes — three triage candidates flagged (below), not silently dropped.

## Reconciliation check
No un-reconciled architecture divergence. `decision:panel-corpus-split-scheme`'s grade (`guess`, leans `g3-implement`) is consistent between the implementer and reviewer handoffs — no silent re-grading.

## Blockers
- none

## Out-of-scope observations
- **tc1:** Season-scale replication verdict is mostly `unresolved`/`unmeasurable` (only `severity:c1` fully unmeasurable; others `unresolved` — no channel clears `r_floor` after double-centering at 20-circuit scale). Honest small-signal result per no-frame-kill doctrine, not a defect — routes a real question to the G5 season report/Admiral: genuine season-scale null, or does double-centering remove too much signal at this N? Independently confirmed via the real run (e.g. severity:c0 mean_r util=0.278 vs r_floor=0.500).
- **tc2:** The rotating-block (stride-1) construction makes adjacent k-partitions differ by only one circuit, so the K=10 samples are structurally correlated (not independent, and — unlike #668's K=3 — not exhaustive either). Worth a follow-up sensitivity check (e.g. a coprime-stride design) before the season-scale verdict is treated as tightly calibrated. Not a new-method issue — a design-quality question about the partitioning choice.
- **tc3:** `scripts/instrument_panel_668_report.py`'s `build_half_cells`/`half_cell_sem`/`_resolved_grid` are private, unexported helpers, forcing this read-adapter to duplicate ~35 lines of pure aggregation arithmetic. Candidate: export as public API (or move into `src/physics/instrument_panel/replication.py` as pure injectable utilities) so a future corpus-scale adapter imports rather than duplicates.

## Workflow Feedback

- **Handoff gaps:** none material. The reviewer handoff's Close Criteria doubled as a de facto extra survey item (the new-method adjudication) beyond the standard `REVIEW_SURVEY` template's 7 items — I appended a sibling item (`r4a-new-method`) via the engine's `append` verb to hold it explicitly rather than folding it into `r4-quality`'s free-text finding, since the handoff called it out as the single most important judgment. Worked cleanly; future gate-specific reviewer handoffs with one dominant judgment call could name the extra survey item directly (e.g. suggest an id) to save that one small decision.
- **Context rediscovered:** none beyond what the implementer already flagged — the implementer's Workflow Feedback (round-order ambiguity → alphabetical order choice; DB fixture schema mismatch → `DatabaseManager` seam) was accurate and needed no rediscovery on my part.
- **Instructions improvised around:** the engine's `append` verb adds a new leaf as a flat sibling at the *end* of `items`, not adjacent to `r4-quality` where I appended it from — `current` visited `r5-reconciliation` and `r6-fowler` before returning to the newly-appended `r4a-new-method`. This is documented engine behavior (`checklist-engine.md`'s append note), not a defect, but it means the survey's on-disk item order does not reflect logical grouping — worth knowing going in rather than being surprised mid-run.
- **What would have made this easier:** none — the handoff's evidence list and Map Anchors were precise enough that every claim could be re-derived from first principles (direct function calls) rather than only re-running the packaged CLI commands, which gave stronger independent confirmation than command-output matching alone.

## Return status
`complete`
