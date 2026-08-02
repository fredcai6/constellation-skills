# Triage candidates — issue #373 run

Background run: no live human to approve issue creation. These are RECORDED for the human's
decision (surfaced in the final report + the #373 issue comment). NOT auto-filed.

## 1. (LOW) Pre-existing simplification violations in `fuse_module_fields_ordered`
`src/evo_predictor/fusion.py:fuse_module_fields_ordered` is over the limits on the committed HEAD
(cyclomatic_complexity=20 vs <20; function_lines=118 vs <100). PREDATES #373; production code under
a do-not-touch ruling this issue. Candidate: a focused refactor (extract the precision-update loop /
validation helpers) to bring it under limits without behaviour change.
- Source: commander observation during G2 simplification check.
- Scope: small, isolated, production.

## 2. (MEDIUM) Confirm the verdict under TRAINED per-task covariance scales
The #373 measurement used a fixed unit-scale FusionLayerConfig (covariance_scale=1.0) to isolate R's
effect cleanly. The ordering-vs-calibration verdict is robust to this choice (the A−baseline delta is
taken under one shared config), but a confirmation run under the trained per-task scales (from
`fusion_training` / `params/gold/fusion/`) would close the loop and is cheap (the harness already
accepts any FusionLayerConfig).
- Source: documented follow-up in docs/evo/fusion_rework_findings.md.
- Scope: small (build trained config, re-run scorecard).

## 3. (MEDIUM) Constructor-lineage naming drift between DB and module records
The scorecard needed a collision-guarded lineage normaliser because the per-year DB stores
season-accurate team names (AlphaTauri, Alfa Romeo, Red Bull, ...) while gold module records collapse
each lineage to one canonical name (RB, Kick Sauber, Red Bull Racing, ...) AND records mix FastF1
naming vintages across rounds/years. Today only the offline harness needs this; if other consumers
join DB teams to record constructors, a shared canonical constructor-lineage mapping (or normalising
at record-write time) would prevent silent drops.
- Source: commander diagnosis during G3 (87->173 event recovery).
- Scope: medium (decide canonical layer + where it lives).

## 4. (MEDIUM) Adopt correlated-covariance fusion as a CALIBRATION improvement (NOT for ordering)
The verdict: variant A tightens posterior calibration (coverage toward nominal) without improving
ordering. If/when calibrated posterior uncertainty becomes a goal (e.g. feeding a Monte-Carlo race
sim per the arch-refactor vision), adopting `fuse_module_fields_correlated` (with the R estimator) in
production behind a flag is a candidate — a SEPARATE decision from #373's measurement, and distinct
from #374's ordering/interaction work. Would need: production R estimation/caching, a calibration
acceptance gate, and the trained-scale config (candidate 2).
- Source: verdict implication in docs/evo/fusion_rework_findings.md.
- Scope: larger; depends on downstream calibration need.

## 5. (LOW) Architecture map node for offline harness tooling (optional)
`scripts/fusion_replay/` is documented as packet prose (per the repo's "scripts are not map nodes"
convention). If the harness becomes a long-lived, depended-on measurement surface for later epic
steps, consider promoting it to a tracked structural element.
- Source: reconcile (cartographer) decision note.
- Scope: trivial (doc).
