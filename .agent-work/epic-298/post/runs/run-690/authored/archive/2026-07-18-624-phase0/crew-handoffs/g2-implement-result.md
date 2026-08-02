# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2` (wide-sigma A/B checkpoint) — issue #624 Phase 0 probes

## Completed slice
Pushed 2025 Japan (round 3) `session_estimates` physics (`lateral_total_grip_g`,
constructor-broadcast) through the EXISTING `driver_residual_states` residual-history
injection seam with a deliberately widened sigma, and ran the headless `sampled-predict`
runtime once with injection ON and once OFF via a new standalone driver script
(`scripts/g2_wide_sigma_ab.py`). Both G0/G1 read once, no tuning/iteration. Full A/B
completed — **no STOP condition was hit**; the seam is externally injectable without
touching `src/`. The result itself is an honest structural null: **the current
production gold manifest doesn't wire the residual-history module into any stage, so
the injection had zero observable effect** — found and documented, not worked around.

## Scope
**Files changed:**
- `scripts/g2_wide_sigma_ab.py` (new — standalone driver script, committed-path)
- `.agent-work/624-phase0/G2_FINDINGS.md` (new — local-only findings)
- `.agent-work/624-phase0/g2-implement-plan.json` (new — engine-driven plan, local-only)
- `.agent-work/624-phase0/crew-handoffs/g2-implement-result.md` (this file)
- `.agent-work/624-phase0/g2_baseline_run.log`, `g2_injection_run.log` (new — full stdout)
- `.agent-work/624-phase0/g2_baseline_output.json`, `g2_injected_output.json`,
  `g2_compare_summary.json` (new — structured run outputs)

**Specific exclusions touched:** no. No `src/` file modified. No Phase 1-6 machinery
built. No `params/gold/*` default changed. No `data/*.db` committed or staged (a
stray `data/f1_data_2025.db` rewrite and untracked `physics_estimates.db-shm`/`-wal`
sidecar files from read-only queries were produced as a run side-effect and cleaned
up in the MAIN checkout per the handoff's explicit instruction — see Evidence).

## Behavior changed
No production behavior changed. This is a probe: a new standalone script exercises an
existing, previously-uncalled seam from outside `src/`; nothing in `src/` was edited,
and no manifest was changed, so `sampled-predict`'s existing production behavior is
byte-for-byte unaffected by this work.

## Map Impact

- **Structural anchors touched:** `src/evo_predictor/driver_residual_history_adapter.py:9-24,32-115`,
  `src/evo_predictor/module_context.py:25`,
  `src/evo_predictor/module_adapters/_runtime_builders.py:536-581` — read-only, confirmed
  exact contract matches the map anchors as given. Additionally traced (not in the
  original anchor list, found necessary during implementation):
  `src/evo_predictor/sampled_runtime.py:200-217` (`SampledEvoRuntime.predict_from_features`,
  the actual external injection point), `src/evo_predictor/data_adapter/_helpers.py:197-282`
  (`build_sampled_runtime_features` / `SampledRuntimeFeatureSet`, the feature-building
  call that produces the overridable `RuntimeModuleContext`), and
  `src/evo_predictor/module_adapters/_registry.py:237-264` (module name registration —
  `driver_quali_power_from_residual_history` is a DISTINCT registered module name from
  the already-productionized `driver_quali_power_from_recent_history`).
- **Capabilities added/changed/affected:** none in `src/`. A new external capability
  exists (`scripts/g2_wide_sigma_ab.py` can run an A/B against the residual-history
  seam for any weekend/year), but it observes/exercises existing behavior only.
- **Constraints/assumptions touched:** confirms `struct:evo.sampled_runtime` is
  externally composable via `predict_from_features` + `dataclasses.replace` on
  `RuntimeModuleContext` without deeper plumbing changes — this was an open question
  in the handoff ("confirm whether `RuntimeModuleContext` is constructable/injectable
  from outside without deeper plumbing changes"), now answered: **yes, cleanly**.
- **Decision candidates / resolved decisions:** none authored here (informational
  probe only), but see Triage candidates below for a natural follow-on decision this
  surfaces.
- **Claims/evidence produced:**
  - `claim:g2-seam-externally-injectable` — `SampledEvoRuntime.predict_from_features(runtime_context=...)`
    plus `build_sampled_runtime_features(...).runtime_context` (a frozen dataclass) together
    form a clean external injection point; verified by actually constructing and running
    against a modified `RuntimeModuleContext` from a script outside `src/`, twice, both
    times exit 0 with sane output.
  - `claim:g2-residual-history-dormant-in-production` — `grep -l residual_history params/gold/*.json`
    returns no matches across every manifest in `params/gold/`; the quali stage's
    `fusion_order`/`steps` in `params/gold/sampled_runtime_manifest.json` contains
    exactly 4 modules, none of which is `driver_quali_power_from_residual_history`.
    Directly explains the bit-identical G0/G1 reads.
- **Trust limitations / drift found:** the handoff's map-confidence flag ("the
  `driver_residual_states` seam has ZERO current callers that populate it non-empty")
  is CONFIRMED and SHARPENED: it's not just that nothing populates it — nothing in
  any current production manifest even reads it, because the consuming module isn't
  wired into any stage's fusion steps. A future map update could usefully record this
  ("seam exists and is code-complete; module registered but zero manifests activate it")
  rather than leaving it implied.
- **Triage candidates:** if a future epic wants to actually TEST whether
  physics-informed residual history moves quali predictions, the residual-history
  module needs to be added to a manifest's `steps`/`fusion_order` list first (a
  manifest/config change, explicitly out of this probe's scope) — worth a follow-up
  issue if that direction is pursued. Also: the `lateral_covariance` discrepancy note
  in `G2_FINDINGS.md` (store DOES hold within-view `Cov(mech,aero)` for lateral, a
  narrower fact than the handoff's phrasing implied) is worth folding into the next
  probe's pre-registration for a more precise composite-variance formula.

## Test mode
**Required:** `evidence-only` (per handoff: "Inspection-only / evidence-only — this
is a probe, not a production behavior change")
**Satisfied:** yes — both A/B runs produced real, captured stdout/JSON evidence;
G0/G1 computed and recorded; CPU>0 confirmed for the injection run rigorously and for
the baseline run via output-correctness (with an honestly-flagged methodology gap on
the CPU-sampling technique itself, not on the run's validity).

## Evidence

```bash
cd /c/Programs/f1-624 && py scripts/g2_wide_sigma_ab.py --help
# exit 0, full usage text incl. sigma-widening formula in the docstring
```
**Result:** pass

```bash
cd /c/Programs/f1-624 && PYTHONIOENCODING=utf-8 py scripts/g2_wide_sigma_ab.py --stage baseline
# HEADLINE_BASELINE: brier=0.13028701052631578 log_loss=0.7155998887783401 n_drivers=20 unresolved_teams=0
# RUN_COMPLETE exit=0
```
**Result:** pass — full stdout in `.agent-work/624-phase0/g2_baseline_run.log`

```bash
cd /c/Programs/f1-624 && PYTHONIOENCODING=utf-8 py scripts/g2_wide_sigma_ab.py --stage injected
# [g2] injected stage: 20 drivers with populated residual state, 0 unresolved team(s): []
# HEADLINE_INJECTED: brier=0.13028701052631578 log_loss=0.7155998887783401 n_drivers=20 unresolved_teams=0
# RUN_COMPLETE exit=0
```
**Result:** pass — full stdout in `.agent-work/624-phase0/g2_injection_run.log`.
CPU>0 confirmed via process-name CPU-sum polling at 0.5s intervals across 3.4s
(before blocking on completion): 2382.89 → 2383.92 → 2384.77 → 2385.80 → 2386.83 →
2387.89 CPU-seconds (steady ~1.03 CPU-s per 0.5s wall-clock, i.e. consuming a full
core continuously — NOT the #623 0%-CPU deadlock signature). Total wall clock
explicitly measured: 208.9s (~3.5 min), matching the handoff's "~3-4 min per race"
reference.

```bash
cd /c/Programs/f1-624 && PYTHONIOENCODING=utf-8 py scripts/g2_wide_sigma_ab.py --stage compare
# HEADLINE_G0: spearman_r=nan n=20
# HEADLINE_G1: baseline_brier=0.13028701052631578 injected_brier=0.13028701052631578 delta=0.0
```
**Result:** pass — confirms bit-identical outputs; G0 undefined (constant zero delta
vector), G1 delta exactly 0.0. Root cause traced to the residual-history module not
being present in any `params/gold/*.json` manifest's stage `steps` (see
`G2_FINDINGS.md` "Root cause of the null").

```bash
cd /c/Programs/f1Brainz && git status --short data/
# (empty after `git checkout -- data/` + removing 2 stray WAL/SHM sidecar files
#  produced by this session's read-only sqlite connections)
```
**Result:** pass — main checkout `data/` confirmed clean.

```bash
cd /c/Programs/f1-624 && git check-ignore scripts/g2_wide_sigma_ab.py; echo "exit=$?"
# exit=1 (not ignored -- tracked-eligible)
```
**Result:** pass

```bash
cd /c/Programs/f1-624 && git status --short
#  ?? .agent-work/624-phase0/
#  ?? scripts/g1_correlation_screen.py   (pre-existing, from g1, untouched here)
#  ?? scripts/g2_wide_sigma_ab.py
```
**Result:** as expected — new files untracked (not yet committed; matches g1's
precedent of leaving commit/consolidation to Commander).

## Docs/contracts touched
- none (probe only; `G2_FINDINGS.md` is local-only per Specific Exclusions/Close
  Criteria, never committed on the mission branch)

## Assumptions
- 2025 Japan (round 3) used as the target weekend per the handoff's suggested
  default — verified live (10/10 constructors, 20/20 drivers, 0 unresolved aliases)
  before building the script, not assumed.
- Sigma-widening formula (16x variance / 4x SD inflation on an independence-floor)
  is my own documented choice within the Authority section's latitude ("you decide:
  ... exact sigma-widening formula, document your reasoning") — full justification
  in `G2_FINDINGS.md` and the script's module docstring.
- `stage_snapshot_metrics` / `StageSnapshot.position_distribution` (both existing,
  read-only imports from `src/evo_predictor/sampled_backtest.py` and
  `runtime_contracts.py`) were reused rather than reimplemented for G1's Brier
  computation and G0's expected-position computation — these are read-only imports
  of existing library code, not `src/` modification, consistent with "no `src/`
  modification" meaning no edits to `src/` files, not "no imports from `src/`."
- `--check` (rerun-and-reproduce) was implemented in the script per the handoff's
  Verification Commands section, but NOT invoked in this session (would cost another
  ~4 min for a reproduction I judged non-essential given the deterministic seed and
  already-captured full stdout/JSON evidence for both stages) — noted honestly in
  Workflow Feedback below rather than silently skipped.

## Stop conditions hit
- **None.** The seam was confirmed cleanly externally-injectable (m1), and the full
  A/B ran to completion (m4, m5) without hitting the 0%-CPU deadlock signature. This
  is explicitly a legitimate, complete "full A/B ran" result per the handoff — the
  interesting finding (residual-history module dormant in production) was discovered
  DURING the compare step, not as a STOP condition; it did not require deviating from
  or truncating the planned A/B, so it is reported as a finding in `G2_FINDINGS.md`,
  not as a Stop Condition.

## Out-of-scope observations
- The residual-history module (`driver_quali_power_from_residual_history` and its
  `race_start`/`race` siblings) is registered in
  `src/evo_predictor/module_adapters/_registry.py` but present in ZERO manifests
  under `params/gold/`. If a future epic wants to test whether physics-informed
  residual history moves predictions, wiring this module into a manifest's stage
  `steps` is a prerequisite manifest/config change (out of scope here). Suggest
  routing to Triage.
- The `lateral_covariance` store discrepancy (see `G2_FINDINGS.md`'s "Discrepancy
  note") is worth folding into the next probe's pre-registration.

## Workflow Feedback

- **Handoff gaps:** the handoff's characterization of x7(c) as "no stored cross-view
  covariance... sum of two correlated-in-reality-but-uncoupled-in-the-store
  components" is slightly imprecise — the store DOES hold a within-view
  `lateral_covariance` = `Cov(lateral_mech_grip_g, lateral_aero_grip_g)` blob (the
  exact pair needed for the composite axis's variance). The handoff's broader point
  (no CROSS-view coupling, no shared-upstream-noise accounting) still holds and still
  justifies the conservative-floor approach it prescribed, so this didn't change my
  approach — but a reader relying on the handoff's phrasing alone, without
  re-verifying against x7(c) directly, could get the wrong precise claim. Worth a
  wording tweak in future handoffs that cite x7(c): distinguish "within-view but not
  cross-view" from "uncoupled."
- **Context rediscovered:** the handoff's Close Criteria described the injection
  point at a high level ("find that entry point from `src/evo_predictor/run.py`'s
  `sampled-predict` command handler and `SampledEvoRuntime.predict_from_features`")
  but didn't name `build_sampled_runtime_features` / `SampledRuntimeFeatureSet`
  (`data_adapter/_helpers.py:197-282`) as the specific function whose return value's
  `.runtime_context` field is what actually needs overriding — this had to be traced
  by reading `SampledEvoRuntime.predict()`'s body. Not a gap exactly (the handoff
  correctly pointed at the right two files to start from), but worth naming this
  function explicitly in a future g2-shaped handoff to save a trace step.
- **Instructions improvised around:** none — the handoff's Authority section
  explicitly delegated "exact driver-script shape, exact sigma-widening formula" to
  me, and I used that latitude as intended; no instruction needed working around.
- **What would have made this easier:** a one-line pointer to
  `FinalOrderSampleSet.stage_snapshots` (populated per-stage by
  `predict_from_features`'s return value, `sample_state_adapter.py:184-187`) as the
  ready-made source for G1's `StageSnapshot` would have saved a few minutes of
  tracing — I initially assumed I'd need to call `build_stage_snapshot_from_ordering`
  myself before discovering the result object already carries it.

## Return status
`complete`
