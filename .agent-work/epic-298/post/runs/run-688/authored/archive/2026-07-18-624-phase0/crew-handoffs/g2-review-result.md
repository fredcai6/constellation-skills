# Review Result

## Assigned Gate
`g2` (wide-sigma A/B checkpoint) — issue #624 Phase 0 probes

## Result
`APPROVE`

## Handoff compliance
Yes. `scripts/g2_wide_sigma_ab.py` pushes real 2025-Japan `session_estimates` physics (pre-registered
`lateral_total_grip_g`, constructor-broadcast) through the EXISTING `driver_residual_states` residual-history
injection seam with a deliberately widened sigma, runs the headless `sampled-predict` runtime once baseline
(injection off) and once injected, and reports G0/G1 once. No STOP condition was hit; the result is an honest,
well-evidenced structural null.

## Scope drift
None. `git status --short` in `C:/Programs/f1-624` shows only `scripts/g2_wide_sigma_ab.py` (new), the
pre-existing `scripts/g1_correlation_screen.py`, and the local `.agent-work/624-phase0/` workbench — zero `src/`
files touched, zero `params/gold/*` default changed, no Phase 1-6 machinery built.

## Evidence verdict
Present and reproduces the claim. `g2_baseline_run.log` / `g2_injection_run.log` / `g2_baseline_output.json` /
`g2_injected_output.json` / `g2_compare_summary.json` are internally consistent and match my own independent
re-derivation (see close-criteria detail below). Test mode `evidence-only` (probe, not production behavior
change) is correctly satisfied.

## Code/doc quality
Meets project rules: physics DB opened read-only via `file:...?mode=ro` URI (CREW_CONTEXT "Untracked data needs
absolute main-checkout paths"); `SIGMA_INFLATION_FACTOR` is a named module constant, not a hidden literal
(CREW_CONTEXT "Tunable weights... belong in config or named constants"); `print()` confined to the script
(CREW_CONTEXT "Library code logs... print() stays in CLI/scripts/tests"); honest self-critical note on the
baseline run's weaker CPU-sampling methodology (not glossed over). Fowler pass (`r6-fowler`, 12/12 smells
rendered, `verify_fowler_pass.py` exit 0) found two non-blocking observations: `long-method` in `run_stage()`
(~85 lines, one coherent pipeline — acceptable for a disposable probe script) and `duplicated-code`
(`normalize_team`/`match_constructor` reimplemented from `g1_correlation_screen.py` rather than imported — follows
g1's own standalone-script precedent, but no CREW_CONTEXT/GLOSSARY line formally sanctions it, so flagged rather
than silently overridden). Neither rises to a blocker.

## Map impact verdict
- **Evidence supports claimed change:** yes — the claimed capability (external seam injection via
  `predict_from_features(runtime_context=...)`) and the claimed null (residual-history module absent from every
  manifest) are both independently reproduced from source, not just asserted.
- **Constraints not violated:** yes — no `src/` edit, no `params/gold/*` default change, no Phase 1-6 machinery.
- **Notes match the diff:** yes — the implementer's Map Impact notes (structural anchors, capabilities,
  constraints, decision candidates, triage candidates) accurately describe what was read-only-traced vs.
  externally exercised.
- **Decision candidates surfaced:** yes — correctly none authored here (informational probe); the natural
  follow-on decision (wire the module into a manifest to actually test it) is routed to Triage, not decided.
- **Durable context routed:** yes — both the "module dormant in every manifest" finding and the
  `lateral_covariance` within-view-vs-cross-view precision correction are captured for the next probe /
  Cartographer, not dropped.

## Reconciliation check
None needed. The finding CONFIRMS and sharpens the project's own live-architecture note (CLAUDE.md: "12
production neural latent-power modules (6 `*_from_race_weekend` + 6 `*_from_recent_history`)") — the
`*_from_residual_history` variants are registered in `_registry.py` but sit outside that production set and
outside every `params/gold/*.json` manifest. No divergence from recorded architecture to reconcile.

## Close-Criteria Verification (handoff items 1-7)

1. **Root-cause claim** — PASS. `grep -l residual_history params/gold/*.json` → zero matches (only
   `gold_provenance.json` and `sampled_runtime_manifest.json` exist there). Read
   `sampled_runtime_manifest.json` directly: the quali stage's `fusion_order`/`steps`/`modules` are exactly the
   4 `recent_history`/`race_weekend` modules; `driver_quali_power_from_residual_history` is genuinely absent.
   Independently confirmed, not a red herring.

2. **Null is not a script bug** — PASS. Read `g2_wide_sigma_ab.py`'s `build_driver_residual_state()`/`run_stage()`:
   it constructs a **non-empty** `DriverResidualState` with real, varying, non-zero `residual_mean` values (e.g.
   Ferrari `lateral_total_grip_g=3.7399`, Alpine `=2.8427` — 10/10 constructors resolved, not placeholders), and
   threads it via `dataclasses.replace(feature_set.runtime_context, driver_residual_states={"quali": state})`
   into `predict_from_features(runtime_context=...)`. `grep -rn driver_residual_states src/` shows **exactly one**
   consumer in the whole codebase (`_make_runtime_driver_residual_history` via
   `context.driver_residual_states.get(adapter.task)`), and that closure backs only the `*_from_residual_history`
   adapters — provably absent from the loaded manifest's `enabled_stage_module_names(stage)` (which is filtered
   from `fusion_order`/`steps`/`modules`) and absent from `self.modules` (the manifest's top-level `modules` dict
   lists only the 12 wired modules, none of them a residual_history variant). This rules out a wrong field name
   or an unreached injection point — the field name/threading is correct; the zero effect is structural.

3. **Seam-injectability claim** — PASS. `SampledEvoRuntime.predict_from_features` (`sampled_runtime.py:200-210`)
   has `runtime_context: RuntimeModuleContext | None = None` as a keyword parameter, defaulting to
   `RuntimeModuleContext()` when omitted and used as-is when supplied — the same method `predict()` calls
   internally. `git diff --stat -- src/` is empty; `git status --short` shows zero `src/` changes. Genuinely
   externally injectable with zero `src/` modification.

4. **CPU>0 / #623 regression check** — PASS (not re-run; no genuine doubt after code-level confirmation). The
   injection run's CPU evidence (steady ~1.03 CPU-s per 0.5s wall-clock across 6 samples, i.e. a full core, not
   the #623 0%-CPU deadlock signature) plus 208.9s total wall-clock matching the prior wave's independently
   verified ~3-4min/race reference is plausible. Both runs additionally produced real, non-degenerate
   Brier=0.1303 output over 20/20 resolved drivers, which is itself decisive against a deadlock (a hang produces
   no output). The implementer's own honest flag that the baseline run's CPU-sampling was methodologically weaker
   doesn't undermine the conclusion.

5. **Sigma-widening formula** — PASS. `widened_variance = (lateral_mech_grip_g_sigma**2 +
   lateral_aero_grip_g_sigma**2) * 16.0` — an independence-floor times an explicit 16x-variance/4x-SD inflation,
   justified by two named reasons (within-view-only covariance per `x7-basis-map-RESULT.md` §c; no calibration
   between the physics store's g-units and the model's latent `pi`/`sigma_pi` scale). Confirmed NOT a
   single-view diagonal copy-paste: per-constructor `floor_variance` genuinely varies (0.0427–0.4535 across the
   10 constructors in `g2_injected_output.json`), reflecting real per-constructor sigma inputs, not one fixed
   number reused everywhere.

6. **No `src/` modification, no dirty `data/`** — PASS. `git status --short` in `C:/Programs/f1-624`: only
   `.agent-work/624-phase0/`, `scripts/g1_correlation_screen.py` (pre-existing), `scripts/g2_wide_sigma_ab.py`
   (new) — zero `src/` changes. `git status --short data/` in `C:/Programs/f1Brainz`: empty, confirming the
   claimed cleanup. (Note: I found and removed a stray empty file named `0` in the worktree root, created by my
   own malformed shell command mid-review — unrelated to the implementer's work, cleaned up before this
   verdict.)

7. **G0/G1 read discipline** — PASS. `g2_baseline_run.log`/`g2_injection_run.log` each show exactly one
   `HEADLINE_*` line per invocation (`run_stage()` called once per `--stage` flag); `run_compare()` reads the two
   persisted output JSONs once and computes G0 (Spearman) and G1 (Brier delta) once each. No iteration or tuning
   loop visible anywhere in the script's control flow.

## Blockers
- none

## Out-of-scope observations
- Triage candidate (confirmed, already surfaced by implementer): wiring `driver_quali_power_from_residual_history`
  (and `race_start`/`race` siblings) into a `params/gold` manifest's `steps`/`fusion_order` is the correct and
  only prerequisite to actually testing whether physics-informed residual history moves predictions — a
  manifest/config change, correctly out of Phase-0 scope.
- Minor: `scripts/g2_wide_sigma_ab.py` duplicates `normalize_team`/`match_constructor` from
  `scripts/g1_correlation_screen.py` rather than importing it. Both scripts independently justify this as
  deliberate standalone-ness, but no `CREW_CONTEXT.md`/`GLOSSARY.md` line formally sanctions it. If a g3 probe
  repeats the pattern, worth extracting a shared `scripts/_phase0_common.py` helper.

## Workflow Feedback

- **Handoff gaps:** none material. The handoff didn't state an explicit "Survey State Location" field (the
  skill's own instruction expects one); I used `.agent-work/624-phase0/g2-review/review.json` by convention,
  matching the sibling `g1-review/` directory already present in the same workbench — worth naming this path
  explicitly in future reviewer handoffs to remove the guess.
- **Context rediscovered:** none beyond what the handoff's Map Anchors already pointed at — the anchors
  (`sampled_runtime.py:200-217`, `_helpers.py:197-282`, `_registry.py:237-264`) were accurate and sufficient; I
  only had to add one grep (`grep -rn driver_residual_states src/`) to fully rule out the script-bug hypothesis
  by confirming there's exactly one consumer in the whole tree.
- **Instructions improvised around:** none.
- **What would have made this easier:** the handoff could have named the exact `grep -rn driver_residual_states
  src/` single-consumer check directly (it's the single strongest piece of evidence for criterion 2 — "is there
  any OTHER place this field could silently misroute to") rather than leaving me to derive it; would have saved
  a minute of tracing, though the anchors given were enough to get there directly.

## Return status
`complete`
