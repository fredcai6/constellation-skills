# Implementer Handoff

## Gate
`g3` — instrument panel over the FULL 2023 corpus (#670 season-scale run)

## Task
Build `scripts/run_season_panel_670.py` (a bounded read-adapter extension of the landed `scripts/instrument_panel_668_report.py`) that runs ALL FOUR instruments over the CONSOLIDATED season slice produced by G2, and emits a season panel report (md + machine-readable json) to an ISOLATED out-dir. This is a READ-ADAPTER/scaling change, NOT a new instrument or model.

**Inputs (on disk, read-only):**
- Consolidated slice: `.agent-work/670-season-run/artifacts/scratch/refutil_season_2023.db` (`driver_class_observables` + `reference_laps` — same schema the #668 panel reads).
- Official laps for instrument 4: the scratch f1 DB `.agent-work/670-season-run/artifacts/scratch/f1_data_2023_scratch.db` (NEVER the tracked `data/f1_data_2023.db`).
- Covered-round set: `.agent-work/670-season-run/artifacts/season_results.json` (`rounds[*].status == "covered"`).

## The ONE thing to generalize: the cross-circuit SPLIT SCHEME (Admiral-refined)
The #668 read-adapter's `enumerate_2v2_partitions` hard-requires EXACTLY 4 circuits. Over the corpus (20 covered circuits) you must generalize ONLY how the circuits are PARTITIONED, re-applying every frozen decision rule unchanged. The Admiral has RULED the exact shape:
- Do **NOT** use a single 11v11 (here 10v10) split — a single split loses the variance-reduction the landed exhaustive-2v2-**AVERAGED** scheme had and noisily mis-sizes replication.
- Use a **DETERMINISTIC, SEED-FREE** balanced split-half scheme: a FIXED subsample of balanced (equal-size) half/half partitions of the covered circuits (e.g. circuits sorted by round, then a fixed deterministic construction of K balanced partitions — a stride/rotation rule, NOT `random`), AVERAGE r over those partitions, then re-apply the SAME registered decision rule to the averaged r (exactly as the #668 adapter's `decide_channel_from_mean_r` does over its 3 partitions).
- Report the EXACT scheme in the output: how many partitions K, and precisely how they are constructed (so it is reproducible and auditable).
- Re-apply the SAME imported frozen rules BYTE-UNCHANGED: `r_floor`, `channel_tie_margin`, `out_of_sample_coverage`, `frozen_replication_thresholds`, the double-centering (`grand_two_way_center`), `main_effect_margin_uncertainty`, `widen_sigma_for_margin_uncertainty` — all IMPORTED from `src/physics/instrument_panel/replication.py`, never re-minted or re-derived.

## Circuit / driver set (important)
- Derive the circuit list from the **COVERED** rounds that have real `severity:*` observables — the 20 covered circuits. The slice's `driver_class_observables` ALSO contains Bahrain `__error__` rows (from its parked round-1 E) and Saudi is absent; EXCLUDE the parked/error-only circuits (filter to circuits that actually carry `severity:2023:v1:c*` rows, or intersect with season_results covered set). Do NOT hardcode the #668 4-circuit / 4-driver constants for the corpus run.
- Drivers = the drivers actually present per circuit in the slice (the grid varies per round). Instruments 1/2/3 already operate generically over the (driver, class) grid; instrument 4's official-lap lookup must use the drivers present per circuit, read from the scratch f1 DB.

## Instruments (all 4, over the corpus)
- **Instrument 1** (variance decomposition): consume the corpus severity rows directly.
- **Instruments 2+3** (split-half replication + per-class channel comparison): the generalized deterministic-averaged split scheme above.
- **Instrument 4** (composed-sector scorecard + whole-lap calibration): consume the corpus slice `reference_laps` (constructor rows) + official best laps from the SCRATCH f1 DB. The #668 `instrument4_whole_lap_calibration` is already driven by its arguments (not module constants) — reuse it.

## Close Criteria
- `run_season_panel_670.py` runs all 4 instruments over the 20-covered-circuit corpus and writes `season_panel_670_report.md` + `.json` to `.agent-work/670-season-run/artifacts/` (isolated) — NOT the committed `docs/physics/instrument_panel_668_*` paths.
- The split scheme is DETERMINISTIC (no `random`/seed), balanced, AVERAGED over K>1 fixed partitions, and the report states K + the exact construction.
- Every frozen replication rule/threshold is IMPORTED from `replication.py`/`frozen_constants.py` — none re-minted or re-derived. No new instrument/model.
- OFFLINE; Student-t σ preserved; the committed #668 report is untouched.
- `tests/unit/physics/instrument_panel/test_panel_corpus.py`: the split scheme is balanced + deterministic (same partitions on repeat runs; each partition splits the circuits into equal halves covering all circuits once); frozen rules are imported-not-reimplemented; the panel runs on a small SYNTHETIC multi-circuit slice (≥6 circuits so multiple balanced partitions exist); reproduce-identical (two runs → byte-identical JSON, mirroring the #668 `--check-reproduce`).
- All existing instrument_panel tests still pass; pyright-0 on new code.

## Allowed Scope
NEW: `scripts/run_season_panel_670.py`, `tests/unit/physics/instrument_panel/test_panel_corpus.py`. You MAY import freely from `scripts/instrument_panel_668_report.py` and `src/physics/instrument_panel/*` (read-adapter reuse). Do NOT edit `src/physics/instrument_panel/*`, `frozen_constants.py`, or the committed #668 report/script.

## Specific Exclusions
- Do NOT re-mint or re-derive any frozen threshold or decision rule (r_floor, tie margin, coverage, double-centering).
- Do NOT use `random`/a seed for the split (the Admiral ruled deterministic + seed-free).
- Do NOT overwrite the committed #668 report. Do NOT touch docs/architecture/*. Do NOT run FastF1/online.

## Constraints
- OFFLINE; read-only on all inputs; never write a tracked `data/f1_data_*.db` (use the scratch f1 DB for official laps); Student-t σ preserved; pinned 3.14 interpreter (`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`, NEVER `py`); worktree-first sys.path guard.

## Map Anchors (inbound)
- **Structural:** `scripts/instrument_panel_668_report.py::run_panel` (4-instrument read-adapter; CIRCUITS/DRIVERS module constants — generalize for the corpus), `enumerate_2v2_partitions` (4-circuit split — replace with the deterministic-averaged N-circuit scheme), `src/physics/instrument_panel/replication.py::{compare_channels_by_class, r_floor, out_of_sample_coverage, frozen_replication_thresholds, grand_two_way_center, main_effect_margin_uncertainty, widen_sigma_for_margin_uncertainty}` (import unchanged).
- **Capability:** cross-circuit replication meaningful over the full corpus (the deliverable's premise).
- **Constraints:** frozen rules byte-unchanged; no new method; offline.
- **Decision anchors:** decision:panel-corpus-split-scheme — deterministic balanced split-half, AVERAGED over K fixed partitions, seed-free, frozen rules unchanged.
  `@grade: guess · leans g3-implement · settle: document K + construction; Admiral-endorsed as a scaling read-adapter PROVIDED frozen rules byte-unchanged; if you find yourself changing a decision rule, STOP and return.`
- **Evidence expectations:** cross-circuit replication over 20 circuits; reproduce-identical; frozen rules imported.

## Deliverable Path Check
- **Committed** — `scripts/run_season_panel_670.py`, `tests/unit/physics/instrument_panel/test_panel_corpus.py` (both tracked; check-ignore exit 1 verified). The season panel report md/json land under `.agent-work/670-season-run/artifacts/` = **Local-only** (regenerable; not committed — the committed deliverable is the G5 season report which will fold in these numbers).

## Required Evidence
- LOAD-BEARING: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_panel_corpus.py -q` passes (paste); `... -m pytest tests/unit/physics/instrument_panel -q` (existing) passes; a real run of `run_season_panel_670.py` over the actual slice produces the report (paste the summary + confirm all 4 instruments produced + the reported K/scheme).
- CONFIRMATORY: pyright-0 on new files; a one-line confirmation no frozen rule was re-implemented (grep your file for local re-definitions of r_floor/thresholds → none).

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel/test_panel_corpus.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/instrument_panel -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/run_season_panel_670.py
```

## Suggested Model Tier
`stronger` — reason: the split-scheme generalization must faithfully preserve frozen statistical rules while scaling; a subtle re-derivation would cross into forbidden new-method territory.

## Authority
The split-scheme SHAPE is Admiral-ruled (deterministic, seed-free, balanced, AVERAGED over K fixed partitions). You choose the exact construction + K and DOCUMENT it. You must NOT: change any frozen decision rule (if a rule seems to need changing, STOP and return — it will be floated to the Admiral), overwrite the #668 report, or build a new instrument.

## Stop Conditions
Stop and return if: preserving the frozen rules while scaling the split forces you to re-derive/modify a decision rule; the slice lacks a table/column the panel needs; a deliverable would require touching src/physics/instrument_panel or a frozen set.

## Return Format
Write IMPLEMENTER_RESULT to `.agent-work/670-season-run/crew-results/g3-implementer-result.md` (slice, files changed, the exact split scheme K+construction, evidence with pasted pass lines + the real-run summary, assumptions, workflow feedback). Then SendMessage cmdr-670 a thin pointer before ending your turn.
