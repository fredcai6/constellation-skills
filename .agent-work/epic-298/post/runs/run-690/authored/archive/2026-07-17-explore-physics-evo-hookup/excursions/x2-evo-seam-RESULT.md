# x2-evo-fp-seam-and-baseline — RESULT

**Question:** Where exactly do FP-derived features enter the live evo sampled runtime today, and what concrete evidence shows those features trailing the naive "just use FP3 order" baseline?

**TL;DR:** FP data enters through two channels — (1) raw practice **pace** (sector times, run classification) reduced by `src/evo_predictor/practice_preprocessor/` into `qs_*`/`lr_*`/`short_run_*`/`long_run_*`/`allfp_best_raw` fields on `DriverFeatures`, consumed by all six `*_from_race_weekend` neural modules; raw `fp1_pos`/`fp2_pos`/`fp3_pos` classification **positions** are stored on `DriverFeatures` but are dead weight — no adapter reads them as a model feature. (2) A post-hoc **anchor blend** (`min(qs_best_raw, lr_best_raw)`, i.e. `allfp_best_raw`) mixed into the trained `race_weekend` quali head's output `pi` before fusion (issue #420, live in the current gold bundle).

The "trails a naive baseline" claim is **real and precisely measured**, but the naive baseline is not literally "FP3 classification order" — it's "FP3-only best-lap pace" vs a rank-blend across FP1/2/3 (`docs/evo/quali_evidence_findings.md`), and the trained model was shown, pre-#420, to trail even that: model `race_weekend` head pairwise sign-accuracy **0.6149 (headline) / 0.5656 (OOS-2025)** vs FP3-only-beating blends at **~0.80/~0.76**. Since #420 shipped (anchor active in the promoted gold bundle), the gap has **mostly closed**: **0.7765 headline / 0.7616 OOS-2025** vs ceilings **0.8061/0.7643** — only ~3pp headline, ~0.3pp OOS remaining. This is the exact headroom a new physics signal would need to move, and issue #601's live status (updated 2026-07-16) explicitly frames the physics bet this way.

---

## (a) Seam map — FP data path into the 12 registered modules

### Registry inventory
`src/evo_predictor/module_adapters/_registry.py:187-266` registers **15** modules (not 12 — see note below): 6 `*_FROM_RACE_WEEKEND` (driver+constructor × quali/race/race_start), 6 `*_FROM_RECENT_HISTORY` (same grid), and 3 `*_FROM_RESIDUAL_HISTORY` (driver-only quali/race_start/race, `supports_training=False`). CLAUDE.md's "12 production modules" = the race_weekend + recent_history sets; the 3 residual_history modules are registered but not production-trained (see below — they are directly relevant to the physics injection question).

### FP-consuming modules (the 6 `*_from_race_weekend` adapters)
All six pull FP-derived pace features from `RaceFeatures.drivers[i]` (a `DriverFeatures`, `src/evo_predictor/models/_features.py`), built by `build_race_features` (`src/evo_predictor/data_adapter/_build.py:478`), which loads FP1/FP2/FP3/SQ/S/Q classifications per weekend (`_load_weekend_classifications`, `_build.py:429-456`) and threads them through `src/evo_predictor/practice_preprocessor/` (lap-hygiene filtering + sector aggregation: `_lap_pipeline.py`, `_compute.py`, `_types.py`) into the `qs_*` (quali-sim), `lr_*` (long-run), `short_run_*`/`long_run_*` (stint-level, compound-adjusted) fields on `DriverFeatures` (`models/_features.py:40-70`), plus `allfp_best_raw = min(qs_best_raw, lr_best_raw)` (`models/_features.py:141`, computed in `practice_preprocessor` / assembled in `data_adapter/_assemble.py`).

Per-module feature lists (exact contract each PairBatch emits):
- `DRIVER_QUALI_POWER_FROM_RACE_WEEKEND` / `CONSTRUCTOR_QUALI_POWER_FROM_RACE_WEEKEND` — `DRIVER_QUALI_POWER_FEATURE_NAMES` (`src/evo_predictor/quali_power_adapter.py:39-66`) and `CONSTRUCTOR_QUALI_POWER_FEATURE_NAMES` (`constructor_quali_power_adapter.py:16-27`): `qs_expected_adj`, `qs_best_adj`, `qs_variation_adj`, `short_run_q20/40/60/80_adj`, `short_run_best_adj`, `short_run_rep_raw_adjust_gap`, `short_run_rep_spread_adj`, `short_run_support_saturation`, `short_run_super_clean_share`, `qs_sector_available` — each ambiguous field paired with a `_missing` indicator (`_emit_field`, `quali_power_adapter.py:187-236`).
- `DRIVER_RACE_POWER_FROM_RACE_WEEKEND` / `CONSTRUCTOR_RACE_POWER_FROM_RACE_WEEKEND` — `BASE_RACE_POWER_FEATURE_NAMES` (`race_power_adapter.py:58-72`ff): adds `lr_expected_adj`, `long_run_q20/40/60/80_adj`, `long_run_best_adj`, `long_run_rep_raw_adjust_gap`, `long_run_rep_spread_adj`, `*_stint_spread_adj`, `*_support_saturation`, `*_super_clean_share`, `*_stint_count_saturation`, `*_dominant_compound_share` on top of the quali-power set.
- `DRIVER_RACE_START_POWER_FROM_RACE_WEEKEND` / `CONSTRUCTOR_RACE_START_POWER_FROM_RACE_WEEKEND` — `race_start_feature_names()` = `BASE_RACE_POWER_FEATURE_NAMES` + grid-delta features (`race_start_adapter.py:64-71, 408-418`); the grid features are post-quali (not FP), so the FP contribution here is identical to the race-power set.

Raw `fp1_pos`/`fp2_pos`/`fp3_pos` (classification **position**, not pace) are carried on `DriverFeatures` (`models/_features.py:25-27`), packed into arrays (`models/_pack.py:39-41`) and defaulted/zeroed in module contexts (`module_adapters/_common.py:381-383`, `race_capability_features.py:124-126`) — **but grep across every adapter's feature-emission code (`quali_power_adapter.py`, `race_power_adapter.py`, `race_start_adapter.py`, and their constructor counterparts) found zero reads of `fp1_pos`/`fp2_pos`/`fp3_pos` as a model input.** They appear to be plumbed through for display/diagnostics only, not fed to any neural module. **Not examined:** whether `fp1_pos`/etc. are consumed by non-adapter code (e.g. gold reports, `race-week` command display) — out of scope for the seam question.

### Non-FP modules
The 6 `*_from_recent_history` adapters (`recent_history_adapter.py`, `quali_recent_history_adapter.py`, etc.) — grepped their feature-name constants for `qs_/lr_/fp/short_run/long_run`: **zero matches**. They consume only cross-event history (past race/quali results), not current-weekend FP. Confirmed by the `docs/evo/quali_evidence_findings.md`-adjacent measurement: `recent_history` channel standalone accuracy (0.7781–0.7803 headline) is essentially unaffected by the FP-anchor work, which only touches `race_weekend`.

### The residual_history modules — the existing physics-injection shape
`DRIVER_QUALI_POWER_FROM_RESIDUAL_HISTORY`, `DRIVER_RACE_START_POWER_FROM_RESIDUAL_HISTORY`, `DRIVER_RACE_POWER_FROM_RESIDUAL_HISTORY` (`_registry.py:247-264`) skip the PairBatch/NN path entirely: `_make_runtime_driver_residual_history` (`module_adapters/_runtime_builders.py:536`) calls `build_neutral_driver_residual_history_field` (`src/evo_predictor/driver_residual_history_adapter.py:32-115`), which **directly constructs a `ModuleFieldResult`** (`pi=zeros`, `sigma_pi=neutral_sigma**2 * I` when no learned state exists — currently always neutral/no-op, `supports_training=False`). This is architecturally the exact shape a physics-capability module would use for injection without training a network: **build a `ModuleFieldResult` directly** (module_name, task∈{quali,race_start,race}, entity_scope∈{driver,constructor}, evidence_source∈{recent_history,race_weekend}, event_id, entity_ids, `pi` (N,), `sigma_pi` (N,N) symmetric — validated in `src/evo_predictor/runtime_contracts.py:89-133`), skipping the neural-net/field-solve stage.

### Two paths to join fusion — the contract
1. **Trained-NN path** (what the 12 production modules do): adapter builds a `PairBatch` (`src/latent_power/models.py:53-65`: `pair_index` (P,2) int64, `features` (P,F) float32, `dqi` (P,) float32, `outcome`/`target_mu` (P,) optional) → NN forward → `PairwiseOutput` (`mu`,`sigma`,`f_theta_raw`, each (P,), `models.py:102-113`) → `src/latent_power/field_solve.py:solve()` (GLS aggregation, handles disconnected pair graphs via union-find) → `FieldSolution` (`pi` (N,), `sigma_pi` (N,N), `models.py:124-136`) → wrapped as `ModuleFieldResult`.
2. **Direct-field path** (what residual_history does, and what #601's Wave-8 plan names explicitly — see (b)): construct `ModuleFieldResult` directly, no PairBatch/NN/field_solve needed.

Either way, joining fusion requires: (i) a `ModuleFieldResult` satisfying `runtime_contracts.py` validation, (ii) a registry entry (`ModuleAdapter` in `_registry.py`, or a bespoke call site if bypassing the registry pattern), (iii) a `FusionStepConfig` (`covariance_scale`, `mean_scale`, `covariance_tension_inflation`, `enabled`) added to the task's `FusionLayerConfig.fusion_order`/`steps` (`src/evo_predictor/fusion.py:23-78`) — `fuse_module_fields_ordered` (`fusion.py:256-316`) does sequential Gaussian precision-weighted assimilation (each module's `sigma_pi` sets its precision/weight; smaller `sigma_pi` = more trusted = pulls the posterior harder), with constructor-scope results projected to drivers via `project_constructor_field_to_drivers` (`src/evo_predictor/constructor_projection.py`, imported at `fusion.py:17`). **Not examined:** `constructor_projection.py` internals, or the (experimental, non-production per its own docstring at `fusion.py:426`) `fuse_module_fields_correlated` GLS-with-cross-module-correlation variant.

---

## (b) The artifact behind "FP features trail the naive baseline" — this DOES exist, with real numbers

This is not impressionistic — it's one of the most heavily measured claims in the repo, spanning issues #379/#380/#381/#408/#414/#420/#425/#451 and living in `docs/evo/prediction_ceiling_and_priorities.md` §7.6–7.6.5 and `docs/evo/quali_evidence_findings.md`.

### The naive-baseline definition and its actual result (`docs/evo/quali_evidence_findings.md`, harness `scripts/diagnose_quali_evidence.py`)
Data-only pairwise sign-accuracy (fraction of driver pairs whose order agrees between a source ordering and the official Q result), pooled 2018–2025, 148 normal-weekend events:

| predictor | sign-acc | events | pairs |
|---|---:|---:|---:|
| **FP3-only** (best_lap, the literal "just use FP3 order" baseline) | **0.7896** | 131 | 23364 |
| blend_rank (equal-weight rank blend, FP1+FP2+FP3) | **0.8088** | 131 | 24468 |
| best_across_fp (min aggregate across sessions) | 0.7999 | 131 | 24836 |
| Best overall (blend_rank of theo_best, all 148 events) | **0.8029** | 148 | 27433 |

Finding: the "FP3-only is best because early sessions dilute the signal" hypothesis is **refuted** — the equal-weight rank blend beats FP3-only by ~1.9pp on matched events. So the correct naive-data ceiling is ~0.80–0.81, not exactly the 0.79 FP3-only number, but they're close (within 2pp).

### The model-vs-ceiling comparison (`scripts/diagnose_quali_same_pairs.py`, archived run `.agent-work/archive/2026-06-06-issue-414-quali-head-scoping/evidence/g1_baseline_repro.txt`; canonicalized in `docs/evo/prediction_ceiling_and_priorities.md` §7.6.2, lines 540-576)

Pre-#420 (the trained `race_weekend` quali head **as originally trained**, no anchor):

| regime | channel | model sign-acc | ceiling (best_across_fp) | ceiling (blend_rank) | gap |
|---|---|---:|---:|---:|---:|
| headline 2018-2024 (LOSO) | `race_weekend` | **0.6149** | 0.8061 | 0.8078 | **+0.1912** (~19pp) |
| headline 2018-2024 (LOSO) | `recent_history` | 0.7803 | 0.8061 | 0.8078 | +0.0258 (~2.6pp) |
| OOS 2025 | `race_weekend` | **0.5656** | 0.7643 | 0.7709 | **+0.1987** (~20pp) |
| OOS 2025 | `recent_history` | 0.7515 | 0.7643 | 0.7709 | +0.0128 (~1.3pp) |

**This is the concrete artifact: the trained `race_weekend` quali head was measurably worse than even FP3-only (0.615 vs 0.790 FP3-only, 0.565 vs 0.790 OOS) — the model was not just failing to reach a sophisticated blend ceiling, it was underperforming the dumbest single-session heuristic by ~17-22pp.** `recent_history` (which doesn't touch current-weekend FP at all — it's pure prior-history) was already close to ceiling.

### Root cause and the fix that shipped (§7.6.3–7.6.5, issues #414/#420/#425/#451)
- §7.6.5 localization (issue #451): a linear readout of the head's own 23-dim `qs_*/short_run_*_adj` feature vector only reaches 0.6513 (~15pp short of ceiling) — the cross-channel "who is generally fast" pace ordering is **not linearly present** in those features at all. Adding `min(qs_best_raw, lr_best_raw)` as an explicit 24th **input** feature and retraining closes OOS-2025 from 0.5868 → 0.7700 (≈ ceiling 0.7643) — confirmed **representational**, not an optimization/capacity problem.
- The shipped fix (issue #420, PR #421, merged 2026-06-07) is a **post-hoc blend**, not the representational retrain: `blend_quali_pace_anchor(pi, anchor, alpha)` (`src/evo_predictor/quali_pace_anchor.py`, called `sampled_runtime.py:495`) mixes the trained head's `pi` with the `allfp_best_raw` anchor (`sampled_runtime.py:486-489`) at `alpha=0.5`, gated by `quali_pace_anchor_enabled`. **This is active in the current gold pipeline default** — `src/evo_predictor/walkforward/pipeline.py:186-187` bakes `quali_pace_anchor_enabled = true, quali_pace_anchor_alpha = 0.5` into the gold-cycle TOML template (code-level dataclass defaults elsewhere are `False` — e.g. `gold_cycle/config.py:76`, `sampled_runtime_manifest_assembly.py:36` — but the walk-forward pipeline that actually produces gold bundles overrides to `True`).
- **Post-#420 numbers** (`prediction_ceiling_and_priorities.md:757`, promoted bundle `gold_cycle_260608_043414_2018thru2024`): α=0.5 LOSO overall **0.7765**, EASY 0.9058; OOS-2025 overall **0.7616**, EASY 0.9004 — vs ceilings 0.8061/0.7643. **The gap the naive-baseline finding exposed has mostly closed: ~3pp headline, ~0.3pp OOS remain.** This matches the `fantasy-league-push-601` memory's "quali head ~0.776 LOSO / ~0.762 OOS-2025 vs ceilings ~0.806/~0.764" almost exactly — confirmed current as of the cited gold bundle.
- **Important caveat found in this excursion:** the §7.6.5 *representational* fix (adding `allfp_best_raw` as a genuine 24th trained-NN input feature) is **not what's live**. Grep of `quali_power_adapter.py`'s `DRIVER_QUALI_POWER_FEATURE_NAMES` (39-66) confirms `allfp_best_raw` is absent from the trained feature set; it is used **only** as the post-hoc anchor value at `sampled_runtime.py:486-495`. The doc itself flags this as "the stage-1 working approximation; #425/#375 are the principled path" (line 816) — so there is still a known, not-yet-executed, more-durable fix on the table, separate from any new physics injection.

**Not examined:** whether a later gold cycle (memory says live gold is `gold_cycle_260612_054059`, PR #469, later than the `gold_cycle_260608_043414` bundle cited in §7.6.4) changed these numbers further — I did not locate or run a reproduction against that specific bundle; the §7.6.4/§7.6.5 numbers are the last **documented** measurement I found. Also not examined: sprint-weekend (SQ) evidence handling in the live pipeline vs the `quali_evidence_findings.md` §B finding that SQ→Q (0.759) is a stronger signal than FP1→Q (0.676) and may still be under-used on sprint weekends — the doc flags this as a live open question ("If the preprocessor currently feeds only FP1 on sprint weekends, that is the single highest-value fix") that I did not verify against current `practice_preprocessor` code.

### Issue #601/#606 content specific to this claim
- Issue #601 (`gh issue view 601`), live status banner updated **2026-07-16** (one day before this excursion): explicitly frames the physics bet as testing "whether physics helps *now*, cheaply" via an **as-of-round join on prior-round quali fits** (leak-free, `*_from_recent_history`-pattern), with a **Wave 7A go/no-go gate** ("does the as-of-round physics pace axis correlate with what evo gets wrong?") before any fusion wiring, and **Wave 8** described as "inject the physics estimate as a Bradley-Terry field directly into the existing fusion (skip the neural module for v1), as-of-round join, A/B by toggling it, scored on fantasy pts/race. Null over the ~0.80 data-only ceiling is a reportable result." — i.e. the plan already targets the direct-`ModuleFieldResult` injection path identified in (a), and already anchors success against the same ~0.80 ceiling this excursion re-derived.
- The issue body's confirmed-spec section states "quali headroom baseline corrected against ceiling doc §7.6.4 (#420 anchor live in gold)" — i.e. the owner has already accounted for the post-#420 narrowed gap when scoping the epic; no stale ~19pp number is being used to justify the physics push.
- Issue #606 (league decomposition) — checked but contains no FP3-baseline content; it's about fantasy-scoring normalization/rules-as-fixture, not quali evidence.

---

## (c) Where quali prediction quality is measured today

1. **Data-only evidence ceiling** — `scripts/diagnose_quali_evidence.py` (pairwise sign-accuracy over `session_classifications`, no trained model involved), documented in `docs/evo/quali_evidence_findings.md`. This defines the achievable ceiling any feature (physics or FP) is compared against.
2. **Model-vs-ceiling localization** — `scripts/diagnose_quali_same_pairs.py` + `scripts/scope_quali_anchor_414.py` (records dir `.agent-work/issue-414-quali-head-scoping/records`, historically archived at `.agent-work/archive/2026-06-06-issue-414-quali-head-scoping/`), and `scripts/accept_quali_anchor_420.py` for production-path reproduction. All score **pairwise sign-accuracy** on a fixed "same-pairs" population per channel/regime.
3. **Standing per-run metric in gold-cycle reports** — `src/evo_predictor/gold_cycle/reports.py`: every module gets a `pairwise_sign_accuracy` entry (`reports.py:267`, tabulated per module/task/scope/evidence at `reports.py:461-477`), with a quality flag if it drops below 0.55 (`reports.py:787`). This is the mechanism by which any new module (including a future physics module) would be scored module-by-module in a gold run, per the memory note "Brier stays primary for module-level gold comparisons" (pairwise sign-accuracy and Brier appear to be companion metrics in these reports — **not examined in full**: I did not confirm where Brier itself is computed in `reports.py`, only that `pairwise_sign_accuracy` is present).
4. **Decision-metric overlay (fantasy push #601/#605/#606)** — the epic's stated top-level gate is **fantasy pts/race vs actual results** (not pairwise accuracy directly), with league placement as an informational-only overlay. Issue #601's Wave 8 plan explicitly says any physics injection is "scored on fantasy pts/race," with the ~0.80 quali ceiling as a secondary/diagnostic reference ("null over the ~0.80 data-only ceiling is a reportable result"). **Not examined:** `src/fantasy_scoring/` internals or whether a scoreboard artifact (#605) already exists and runs — CLAUDE.md lists the module paths but I did not open them in this excursion; out of the brief's named source list.

---

## Scoped nulls — explicitly NOT examined

- `src/fantasy_scoring/` module internals (beam_search.py, scoring_rules.py, season.py, lineup_evaluator.py) — named in CLAUDE.md but not opened; relevant to (c)'s decision-metric claim but not to the FP-seam/baseline question directly.
- `src/evo_predictor/constructor_projection.py` internals (constructor→driver field projection used in fusion).
- The experimental `fuse_module_fields_correlated` path (`fusion.py:400-478`) — confirmed non-production by its own docstring, not traced further.
- Reproduction against the current LIVE gold bundle (`gold_cycle_260612_054059` per memory, later than the `gold_cycle_260608_043414` bundle the §7.6.4/7.6.5 numbers are pinned to) — did not re-run any diagnostic script against it; all cited numbers are from the last **documented** measurement in the repo, not a fresh run.
- Sprint-weekend (SQ) practice-preprocessor wiring — flagged as a live open question in `quali_evidence_findings.md` §B but not verified against current code.
- `gh issue view 606` full body — checked only for FP3-baseline content (none found); did not read its full decomposition-methodology content.
- Whether `fp1_pos`/`fp2_pos`/`fp3_pos` are consumed anywhere outside `src/evo_predictor/` adapters (e.g. display/CLI/report code) — grep was scoped to adapter feature-emission code only.
- No training runs, no code changes, no DB queries beyond `gh`/grep/read — per budget.

---

## Cited files (for quick navigation)

- `src/evo_predictor/module_adapters/_registry.py:187-266` — registry
- `src/evo_predictor/models/_features.py:25-27,40-70,141-144` — DriverFeatures FP fields
- `src/evo_predictor/quali_power_adapter.py:39-66,180-236` — quali-head PairBatch contract
- `src/evo_predictor/race_power_adapter.py:26-72` — race-head PairBatch contract
- `src/evo_predictor/race_start_adapter.py:64-71,408-418` — race-start grid+FP contract
- `src/evo_predictor/driver_residual_history_adapter.py` — direct-ModuleFieldResult injection shape
- `src/evo_predictor/runtime_contracts.py:89-133` — ModuleFieldResult contract
- `src/evo_predictor/fusion.py:23-78,213-316` — fusion config + precision-weighted update
- `src/latent_power/models.py:53-65,102-136` — PairBatch/PairwiseOutput/FieldSolution shapes
- `src/latent_power/field_solve.py:19-47` — GLS solve
- `src/evo_predictor/quali_pace_anchor.py`, `sampled_runtime.py:444,486-495` — production anchor blend
- `src/evo_predictor/walkforward/pipeline.py:186-187` — anchor default ON in gold-cycle template
- `docs/evo/quali_evidence_findings.md` — naive-baseline data (FP3-only vs blends)
- `docs/evo/prediction_ceiling_and_priorities.md` §7.6.2-7.6.5 (lines 540-818) — model-vs-ceiling numbers
- `.agent-work/archive/2026-06-06-issue-414-quali-head-scoping/evidence/g1_baseline_repro.txt` — raw pre-#420 measurement
- `src/evo_predictor/gold_cycle/reports.py:267,461-477,787` — standing per-run metric
- GitHub issue #601 (live status banner, updated 2026-07-16) — physics-injection plan naming the same fusion contract
- GitHub issue #420 (closed, PR #421) — production anchor
