# PROTOTYPE_RESULT — x4: hole-prioritization dry run on f1Brainz

**Question:** does centrality over the derived graph, intersected with docstring holes,
reproduce the human-curated map's documentation choices on f1Brainz — and produce a
credible "describe these first" list?

**Answer: no for the signal we planned, yes for a simpler one we didn't.** PageRank
failed to beat a random draw at every K (p >= 0.17; top-10 lift 0.87x, i.e. marginally
worse than chance). HITS authority was anti-correlated. Plain **call count into an entity,
restricted to public entities**, did validate: 60% of its top 10 and 47% of its top 30
are entities the curated map names, against a 19.4% base rate (p=0.005, p=0.0005). The
ranked hole list ships, ordered by the signal that validated.

Artifact: `evidence/x4/hole_priority_list.md`. Scripts and raw data: `evidence/x4/`.

---

## 1. Coverage

**Tool:** `interrogate` 1.7.0. **Command:** `interrogate C:\Programs\f1Brainz\src`
(and once per top-level package). Run from a 3.12.13 venv at `evidence/x4/.venv`.

**Overall: 62.3%** (fails interrogate's default 80% gate).

| package | coverage | | package | coverage |
|---|---:|---|---|---:|
| analysis | 100.0% | | models | 94.9% |
| simulation | 100.0% | | data | 88.2% |
| utils | 84.4% | | preprocessing | 83.7% |
| physics | 81.8% | | calibration | 76.1% |
| common | 75.0% | | publishing | 71.4% |
| strategy | 54.5% | | reporting | 53.0% |
| evo_predictor | 48.3% | | latent_power | 34.9% |
| compound_prior | 30.3% | | fantasy_scoring | 26.1% |

Cross-check against x1's independent AST census (`evidence/x1/docstring_census.json`,
which spans 677 files including tests): module docstrings 95.1%, class 70.1%, function
51.1%, public function 59.4%. The two tools disagree on the headline number because they
weight module/class/function differently, not because either is wrong. The shape agrees:
modules are documented, functions are the hole.

## 2. Centrality ranking

**Graph: symbol-level.** x1's SCIP index was already on disk, so the module-level fallback
was not needed. Nodes are f1Brainz's own definitions decoded from `evidence/x1/defs.jsonl`
(SCIP kinds `method` and `type`, `src/` files only): **4217 nodes**. Edges are
caller -> callee from `evidence/x1/call_edges.jsonl`, weighted by call count, restricted to
edges where *both* ends are internal definitions: **4465 edges**. A further 6655 call edges
were dropped as pointing at stdlib or third-party symbols.

PageRank: `networkx.pagerank(g, alpha=0.85, weight="weight")`. Script: `evidence/x4/centrality.py`,
full ranking in `evidence/x4/centrality_scored.json`.

Top 30 by PageRank (`doc` = has a docstring; `map` = the curated map names this entity):

| # | PageRank | in-deg | doc | map | entity |
|---:|---:|---:|:--:|:--:|---|
| 1 | 0.00364 | 17 | N | – | `reporting.html_reports._primitives._e` |
| 2 | 0.00248 | 13 | N | – | `evo_predictor.gold_module_cycle.finite_float` |
| 3 | 0.00231 | 3 | Y | – | `evo_predictor.sampled_runtime_serialization.sampled_runtime_json_ready` |
| 4 | 0.00230 | 3 | Y | – | `preprocessing.trajectory.dynamics.discretize` |
| 5 | 0.00229 | 7 | Y | – | `preprocessing.trajectory._smoother_query._StintSmootherQueryMixin._state_at` |
| 6 | 0.00226 | 3 | Y | – | `utils.config.Config.load_config` |
| 7 | 0.00219 | 9 | Y | HIT | `utils.config.Config.get` |
| 8 | 0.00202 | 17 | N | – | `fantasy_scoring.league.snapshot_adapter.ArtifactToolReplaySnapshotAdapter._error` |
| 9 | 0.00195 | 2 | N | – | `evo_predictor.fusion_training._helpers._json_ready` |
| 10 | 0.00187 | 2 | N | – | `evo_predictor.run._json_ready` |
| 11 | 0.00182 | 3 | Y | HIT | `physics.wear.panel.cluster_ols` |
| 12 | 0.00172 | 24 | Y | HIT | `utils.constants.get_calendar` |
| 13 | 0.00172 | 3 | N | – | `compound_prior.diagnostics._tables._require_columns` |
| 14 | 0.00170 | 3 | N | – | `latent_power.modules.get_module` |
| 15 | 0.00167 | 17 | Y | – | `latent_power.preprocessor_contract.assert_pair_batch` |
| 16 | 0.00166 | 3 | N | – | `physics.feature_view.store.FeatureViewStore._connect` |
| 17 | 0.00164 | 3 | N | – | `evo_predictor.team_canonicalization._normalize_team` |
| 18 | 0.00163 | 3 | N | – | `evo_predictor.module_adapters._registry.validate_adapter_matches_latent_power` |
| 19 | 0.00160 | 1 | N | HIT | `latent_power.modules.ModuleRegistry.get` |
| 20 | 0.00157 | 2 | Y | – | `evo_predictor.practice_preprocessor._compute._run_bucket_fields` |
| 21 | 0.00156 | 2 | Y | – | `physics.weekend_state.gate_f6._sanitize` |
| 22 | 0.00151 | 2 | Y | – | `physics.segment_map.identity._canonicalize` |
| 23 | 0.00143 | 20 | N | – | `compound_prior.diagnostics._tables._ensure_matplotlib` |
| 24 | 0.00142 | 2 | N | – | `evo_predictor.gold_report_schema._flatten_paths` |
| 25 | 0.00141 | 19 | Y | – | `data.database._metadata_session.DatabaseSessionMetadataMixin.get_session_classification` |
| 26 | 0.00137 | 9 | Y | HIT | `physics.layer2.pooling.pool_random_effects` |
| 27 | 0.00135 | 9 | N | – | `fantasy_scoring.league.normalizer._error` |
| 28 | 0.00133 | 6 | N | – | `evo_predictor.recent_history_adapter._position_or_missing` |
| 29 | 0.00133 | 13 | N | – | `evo_predictor.module_adapters._registry.get_adapter` |
| 30 | 0.00132 | 3 | Y | – | `utils.environment.moist_air_density_from_pressure` |

The failure is legible by eye before any statistics: `_e`, `_json_ready` (twice), `_error`
(twice), `_require_columns`, `_ensure_matplotlib`, `finite_float`, `_flatten_paths`.
**50% of the top 30 are underscore-prefixed private helpers**, against a 48% share in the
population — so PageRank is not even *preferring* public API; it is indifferent to the
distinction that matters most to a reader.

A module-level graph was also built for comparison (376 nodes, 858 edges from
`evidence/x1/module_deps.jsonl`; `evidence/x4/centrality_modules_scored.json`). Its top
entries look far more like architecture — `utils.constants`, `physics.layer2.pooling`,
`compound_prior.baseline`, `models.data_models`, `latent_power.preprocessor_contract` —
but see §3 for why that ranking cannot be validated against this ground truth.

**HITS** ran but is degenerate on this graph: authority scores are ~0 to four decimals
across the board, because the internal call graph is sparse and near-acyclic. Its ranking
is reported below for completeness but should be read as noise, not as a tuned competitor.

## 3. Validation against the curated map

**Ground truth.** `C:\Programs\f1Brainz\docs\architecture\index.md` + `packets/*.md` (16
files) + `overlays/*.yml` (2 files) — 19 files, 521,262 characters. From these, 5871
distinct identifier tokens and 1866 dotted paths were extracted. Extraction counts a token
only if it appears **inside backticks or inside a dotted path**, so ordinary English prose
cannot manufacture a hit. Script: `evidence/x4/validate_vs_map.py`.

**Base rates (this is the load-bearing part).**

- **11.5%** of the 4217 symbol entities have their own name mentioned by the map.
- **19.4%** of the 2202 *public* entities do.
- **95.2%** have their *module* mentioned by the map.

That last number kills the module-level test outright. f1Brainz's map names essentially
every module, so "does the map mention this module?" is at ceiling and has no discriminating
power — module-level PageRank scores 90% at K=10 against a 93.6% base rate, a **lift of
0.96x**, which means nothing. Any module-level validation on this repo is uninformative by
construction, and that is a property of the ground truth, not of the ranking.

**Symbol-level results.** Baseline is empirical: 20,000 random draws of size K from the
same pool, p = fraction of draws scoring at least as well as the signal.

| signal | pool | K | hits | rate | lift | p |
|---|---|---:|---:|---:|---:|---:|
| PageRank | all | 10 | 1 | 10.0% | 0.87x | 0.709 |
| PageRank | all | 20 | 4 | 20.0% | 1.73x | 0.195 |
| PageRank | all | 30 | 5 | 16.7% | 1.44x | 0.260 |
| PageRank | public | 10 | 3 | 30.0% | 1.55x | 0.306 |
| PageRank | public | 20 | 6 | 30.0% | 1.55x | 0.171 |
| PageRank | public | 30 | 8 | 26.7% | 1.38x | 0.212 |
| HITS authority | all | 10 | 1 | 10.0% | 0.87x | 0.703 |
| HITS authority | all | 20 | 1 | 5.0% | 0.43x | 0.915 |
| HITS authority | all | 30 | 2 | 6.7% | 0.58x | 0.878 |
| PageRank, classes only | classes | 30 | 4 | 13.3% | 0.77x | – |
| **in-degree (distinct callers)** | public | 20 | 8 | 40.0% | 2.06x | **0.028** |
| **in-degree (distinct callers)** | public | 30 | 13 | 43.3% | 2.23x | **0.002** |
| **in-weight (total call count)** | public | 10 | 6 | 60.0% | 3.09x | **0.005** |
| **in-weight (total call count)** | public | 20 | 8 | 40.0% | 2.06x | **0.027** |
| **in-weight (total call count)** | public | 30 | 14 | 46.7% | 2.41x | **0.0005** |

**Reading.** The lift column alone would have been misleading — PageRank's 1.73x at K=20
looks like a result until you see p=0.195 and the random draw's p95 of 23.3% at K=30. With
K this small, lifts under ~2x are indistinguishable from luck, and every PageRank and HITS
figure sits in that band. Restricting PageRank to public entities helps (0.87x -> 1.55x at
K=10) but still never reaches significance. Ranking classes only makes it worse (0.58x).

The two signals that clear the bar are the two dumbest ones: how many distinct places call
this, and how many times it is called in total. Both beat their baselines at every K >= 20,
and total call count also clears at K=10.

**So: centrality did not validate; call frequency did.** The distinction matters because
the exploration's plan named PageRank specifically, and PageRank is the part that failed.
What survives is weaker than "centrality predicts documentation choices" — it is "the
entities called most often are about 2.4x more likely than chance to be ones the map names,"
which still leaves roughly half of any top-30 list being things the map felt no need to name.

**Why PageRank loses to raw call count here.** PageRank redistributes score through paths,
so a helper called once by each of twenty already-important functions accumulates more than
a genuine subsystem entry point called directly by three callers. On an architecture map,
that is backwards: `_json_ready` is called everywhere *because* it is beneath notice.
Raw in-degree does not propagate, so it cannot manufacture that kind of importance.

## 4. The artifact — "needs a description first"

**Full list: `evidence/x4/hole_priority_list.md`** (692 public holes, 1727 including private).

Holes: **1727 of 4217** graph entities have no docstring (41%); **692 of 2202** public ones
(31%). Docstring presence is confirmed by AST-parsing the live source, not by trusting the
SCIP flag. `file:line` comes from the same AST walk (4201 of 4217 entities matched; the 16
misses are properties and class fields the walker does not resolve to a `def`).

The shipped list is ordered by **in-weight over public entities** — the signal that
validated — with PageRank rank carried as a column rather than as the ordering. Top 15:

| # | entity | calls in | callers | PR rank | map names it? | file:line |
|---:|---|---:|---:|---:|:--:|---|
| 1 | `evo_predictor.gold_module_cycle.finite_float` | 39 | 13 | 2 | no | `src/evo_predictor/gold_module_cycle.py:43` |
| 2 | `evo_predictor.data_adapter._helpers.…race_features.values` | 26 | 1 | 953 | yes | `src/evo_predictor/data_adapter/_helpers.py` |
| 3 | `evo_predictor.models._genomes.ResidualParams.v` | 24 | 1 | 103 | yes | `src/evo_predictor/models/_genomes.py` |
| 4 | `evo_predictor.models._genomes.WeekendGenome.v` | 23 | 1 | 104 | yes | `src/evo_predictor/models/_genomes.py` |
| 5 | `evo_predictor.module_adapters._registry.get_adapter` | 21 | 13 | 29 | no | `src/evo_predictor/module_adapters/_registry.py:272` |
| 6 | `evo_predictor.team_canonicalization.canonicalize_team_name` | 18 | 11 | 49 | no | `src/evo_predictor/team_canonicalization.py:30` |
| 7 | `compound_prior.runtime_normalization.load_time_safe_compound_prior` | 14 | 7 | 165 | no | `src/compound_prior/runtime_normalization.py:211` |
| 8 | `evo_predictor.module_training_orchestration.get_training_adapter` | 13 | 7 | 339 | no | `src/evo_predictor/module_training_orchestration.py:101` |
| 9 | `physics.layer2.params.GaussianPrior2.cold` | 12 | 6 | 385 | yes | `src/physics/layer2/params.py:44` |
| 10 | `compound_prior.baseline.effective_sample_size` | 12 | 8 | 120 | no | `src/compound_prior/baseline.py:205` |
| 11 | `evo_predictor.latent_power_bundle.load_latent_power_module_bundle` | 11 | 6 | 345 | yes | `src/evo_predictor/latent_power_bundle.py:91` |
| 12 | `evo_predictor.gold_cycle.reports.repo_rel` | 11 | 3 | 940 | no | `src/evo_predictor/gold_cycle/reports.py:511` |
| 13 | `physics.physics_simulator.PhysicsSimulator.simulate_lap` | 10 | 6 | 297 | yes | `src/physics/physics_simulator.py:50` |
| 14 | `evo_predictor.module_training_orchestration.build_labeled_batches_for_module` | 10 | 5 | 255 | no | `src/evo_predictor/module_training_orchestration.py:529` |
| 15 | `compound_prior.diagnostics._plots_solver.filter_compound_prior_diagnostics` | 10 | 6 | 255 | no | `src/compound_prior/diagnostics/_plots_solver.py:70` |

Two things to note in that table. The list is qualitatively credible in a way the PageRank
ordering was not — `PhysicsSimulator.simulate_lap`, `load_latent_power_module_bundle`,
`effective_sample_size`, `canonicalize_team_name` are all things a reader would reasonably
want described, and they sit at PageRank ranks 297, 345, 120 and 49 respectively, i.e. the
PageRank ordering buries them. And the ranking is still not clean: `finite_float` and
`repo_rel` are trivia, and rows 2–4 are single-caller accessors inflated by repeated calls
from one site, which is a specific weakness of in-weight that in-degree does not share.

**Also worth flagging separately:** entities the curated map *does* name but which have no
docstring are a distinct and probably higher-value target than raw centrality — the map has
already certified them as worth explaining, so no ranking signal has to be trusted at all.
That set is **130 entities, out of the 487 the map names** (27% of what the map considered
worth naming has no docstring). It is computable from the shipped data
(`leaf_hit == true and has_docstring == false` in `centrality_scored.json`); its top entries
by call count are `PhysicsSimulator.simulate_lap`, `load_latent_power_module_bundle`,
`EstimateStore.load`, `GaussianPrior2.cold` and `latent_power.modules.list_modules`. It was
not ranked as its own artifact here.

## 5. Scoped nulls — what was NOT tested

- **PageRank is disconfirmed only as a symbol-level call-graph ranking on one repo.**
  Not tested: other alphas (only 0.85), personalized/seeded PageRank, undirected or reversed
  edge direction, or PageRank over an import graph rather than a call graph.
- **HITS is reported but not fairly tested.** Scores were degenerate (~0) on this sparse
  near-acyclic graph. Its anti-correlated numbers should be read as "HITS did not run
  meaningfully here", not "HITS is a bad signal."
- **Module-level centrality is untested, not refuted.** Its ranking was computed and looks
  qualitatively strong, but this repo's ground truth names 95.2% of modules, so the overlap
  test is at ceiling and cannot separate a good module ranking from a bad one. Validating
  module-level ranking needs a different ground truth — e.g. which modules the map gives a
  *dedicated section* to, rather than merely mentions.
- **Text-based ranking was not tried at all.** No TF-IDF, embedding, name-salience, or
  LLM-judged ranking was run against the same ground truth. **The McBurney contradiction
  stays open** — nothing here bears on whether generated descriptions read as useful; x4
  measured only *which* entities to describe, never the quality of a description.
- **Other structural signals not tried:** betweenness, fan-in/fan-out ratio, module-boundary
  crossing count, churn or co-change from git history, test coverage as a proxy for
  importance. Betweenness in particular is the natural "this sits on a boundary" measure and
  is untested.
- **Single repo, single ground truth.** n=1. f1Brainz's map is unusually complete (it names
  nearly every module), which is itself a strong prior — a repo with a sparser map could
  give centrality more room to discriminate. The result does not generalize past this repo
  without a second trial.
- **The ground truth is "mentioned by the map", not "worth documenting".** A curated map
  omits things for reasons other than unimportance (recently added, obvious from the name,
  covered in a decision doc). `docs/architecture/decisions/` — 16 further files — was not
  included in the mention set, so entities documented only in a decision record count as
  misses here.
- **Docstring presence is not docstring quality.** A one-line restatement of the function
  name counts as covered throughout.

## Disposition

Keep the measurement scripts and the ranked list; both live under `evidence/x4/` and the
list is directly usable. Retire the PageRank framing of hole-prioritization. If the
exploration wants a defensible "describe these first" signal, the cheap next step is the
130 map-named-but-undocumented entities — that set needs no ranking signal to justify it —
and the informative next step is betweenness plus a module-boundary-crossing count against
a stricter ground truth than "mentioned."

f1Brainz was not modified. All writes landed under `evidence/x4/`.
