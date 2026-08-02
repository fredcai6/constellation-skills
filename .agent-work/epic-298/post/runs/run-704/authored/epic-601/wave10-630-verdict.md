# Wave 10 Verdict — Issue #630, Phase 6 (epic #601): prototype BT injection behind manifest toggle

**Commander:** Phase6Cmdr (delegated, Sonnet)
**Worktree:** `C:/Programs/f1-phase6`, branch `feat/phase6-bt-injection`, base `2e4fd5ef`
**PR:** https://github.com/fredcai6/f1Brainz/pull/658 (OPEN, MERGEABLE, clean-room reviewed APPROVE)

## 1. Verdict: gate PASS

| Gate requirement | Status |
|---|---|
| Injection wiring exists (`read_feature_view` → `ModuleFieldResult` → joined via `FusionStepConfig`) | ✓ |
| Unit-tested (wiring, toggle on/off, shape/contract) | ✓ |
| Toggle OFF by default everywhere (dataclasses + gold/walkforward template) | ✓ |
| Bit-identical-off PROVEN (exact-equality evidence) | ✓ — at TWO levels: fusion-math (`np.testing.assert_array_equal`) and call-site (call-count spy + `fusion_config is stage.fusion` object identity) |

**A measured "wiring is inert when off, and the toggle-on path is correctly shaped and ready
for Phase 7" is the complete deliverable this phase — no predictive/value claim is made or
expected.** That is exactly what this run produced.

## 2. What was built

**Call-site pattern chosen: bespoke, not registry.** Investigated the residual-history
registry/`ModuleAdapter` path first (the launch order's own template) and found it infeasible
for a bundle-less direct-field module: `sampled_runtime_from_config` (`sampled_runtime.py:668-690`)
calls `load_latent_power_module_bundle` for every module in `enabled_stage_module_names(stage)`
across all stages — any module whose `FusionStepConfig.enabled=True` needs a real NN checkpoint
at `manifest_path`. This is exactly why the 3 `*_FROM_RESIDUAL_HISTORY` modules stay
production-dormant (never appear in any manifest stage). **Ruling (self-adjudicated under
inherited latitude, ratified without change by the Admiral):** a bespoke call site in
`SampledEvoRuntime._run_stage`, mirroring the `quali_pace_anchor` call-site SHAPE (a
config-gated block after the per-module loop, before `fuse_module_fields_ordered`), which
when enabled builds a real `ModuleFieldResult` and `dataclasses.replace`s `stage.fusion` to
append one `FusionStepConfig`/`fusion_order` entry **in-memory only** — never touching the
static manifest-schema `stage.modules`/`RuntimeModuleRef` machinery. When disabled, `_run_stage`
executes the identical code path as today.

**Toggle name:** `physics_feature_injection_enabled`. **Every location its default is set:**
- `PhysicsFeatureInjectionConfig.enabled: bool = False` (`pipeline_manifest_v4.py`)
- `GoldCycleRuntimeConfig.physics_feature_injection_enabled: bool = False` (`gold_cycle/config.py`)
- `assemble_sampled_runtime_manifest(..., physics_feature_injection_enabled: bool = False, ...)` (`sampled_runtime_manifest_assembly.py`)
- `run.py`'s CLI passthrough `getattr(args, "physics_feature_injection_enabled", False)` — no new argparse flag (verified `quali_pace_anchor_enabled` has none either, mirrored exactly)
- `configs/evo/gold_defaults.toml`: explicit `physics_feature_injection_enabled = false`
- `src/evo_predictor/walkforward/pipeline.py`: **no override line at all** — deliberately, unlike `quali_pace_anchor_enabled = true` at line 186 of the same file. Verified via grep both by the implementer and independently by the reviewer.

**Task scope: quali-only.** `FeatureViewRow` is per-constructor and sits naturally alongside
`driver_quali_power_from_race_weekend` the same way the anchor does; race_start/race are
identical extension points for Phase 7.

**How physics σ maps into `sigma_pi`:** a diagonal matrix — `axis_sigma[axis_name]**2 *
covariance_scale` per constructor, off-diagonal 0.0 (v1 models no cross-constructor covariance,
stated explicitly in diagnostics). **`axis_name` is a REQUIRED runtime-config field with NO
production default** — researched the real physics axis vocabulary
(`build_car_basis.PHYSICAL_AXES`, 11 names: drag/braking/traction/power/lateral-grip/coasting
component measures) and found **no canonical "pace" axis exists** among them, so the wiring
does not guess one; whoever enables the toggle (Phase 7) must make an explicit, informed axis
choice. A constructor with no feature-view row, a missing axis, or `transition_axis_status ==
"unresolved"` for that axis falls back to neutral (`pi=0.0`, large `sigma_pi`), recorded in
diagnostics, never silently imputed or dropped from `entity_ids`.

## 3. Evidence

**Commits (5, each its own logical unit):**
- `2e505f11` — `read_feature_view_at` production entry point (Phase-5 seam completion, Admiral-ratified one-time exception)
- `f852000d` — `physics_feature_injection_enabled` manifest toggle plumbing (1 rework cycle for a `simplification_limits` violation)
- `9f5c7ace` — runtime wiring + dual bit-identical-off proof (1 honest-stop-condition follow-up for an axis_name assembly-layer gap)
- `2fcb9d15` — architecture map reconciliation
- `54ad1c3a` — triage fix-now: regex anchor tightening

**Test names + pytest output** (pinned interpreter `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`):
- `tests/unit/evo_predictor/test_sampled_runtime.py::test_fuse_module_fields_ordered_bit_identical_physics_step_present_disabled_vs_absent` — `fuse_module_fields_ordered` called directly (bypassing `_run_stage`) once with the physics step present-but-disabled, once entirely absent from `fusion_order`/`steps`; `np.testing.assert_array_equal` on `.pi` and `.sigma_pi`. PASS.
- `tests/unit/evo_predictor/test_sampled_runtime.py::test_physics_feature_injection_toggle_off_is_true_noop_at_call_site` — call-count spy on `build_physics_feature_field` (asserts `== 0`) + `fusion_config is stage.fusion` by Python `is`. PASS.
- Full suites, independently re-run by the Commander (not trusted from crew reports) at every integrate: `tests/unit/evo_predictor/` → **1983 passed, 19 skipped, 0 failed**; `tests/unit/physics/feature_view/` → **87 passed**.
- `py -m src.utils.simplification_limits --paths src/evo_predictor/physics_feature_injection.py src/evo_predictor/sampled_runtime.py src/evo_predictor/pipeline_manifest_v4.py src/evo_predictor/sampled_runtime_manifest_assembly.py` → **PASS (4 files checked)**.
- `tests/unit/physics/feature_view/test_evo_import_boundary.py` → green throughout; `physics_feature_injection.py` imports exactly `ModuleFieldResult` and `read_feature_view_at`.
- `py scripts/check_arch_map.py` → OK, 43 catalog nodes / 21 packets / 13 overlay nodes, consistent.

**`py scripts/verify_worktree_isolation.py --here C:/Programs/f1-phase6` output** (first action taken, before any git operation):
```
worktree OK: in C:/Programs/f1-phase6
```
(run via the pinned interpreter, since the bare `py` launcher on this machine shadows to a
pytest-less codex runtime — documented as a platform hazard in the launch order and confirmed
again this run.)

**PR:** https://github.com/fredcai6/f1Brainz/pull/658 — pushed, opened, independently
clean-room reviewed by a fresh subagent with no prior context on this work: **APPROVE**,
reproducing every claimed test count and re-deriving the bit-identical-off proof from source
rather than trusting the PR description.

## 4. RULINGs and floats

**Float (round-tripped, resolved before building anything):** `read_feature_view`'s signature
requires a `FeatureViewStore` instance, but `test_evo_import_boundary.py` forbids
`src/evo_predictor/**` from importing anything from `src.physics.feature_view` except
`read_feature_view` itself — no sanctioned way for evo to construct the store object the
function needs. Confirmed via source read (`read.py`, `store.py`) and the Phase-5 verdict
(which explicitly scoped this as "#630 out of scope"), so this was a genuine deferred gap, not
something I could resolve unilaterally without touching the frozen seam. Declined an
`importlib`-based dodge as bad-faith test-gaming. **Admiral ruling:** approved as in-scope
Phase-6 seam completion (not a frozen-seam violation, since Phase 5 itself deferred it here);
authorized `read_feature_view_at(db_path, ...)` as a thin delegation, added to `read.py`'s
`__all__` and the boundary test's allow-list, as a one-time exception, own commit. Built
exactly as ratified.

**RULINGs (self-adjudicated under inherited latitude, all ratified without change by the
Admiral in the same round-trip):**
- Bespoke call-site over registry path (§2 above), citing the concrete bundle-loading
  infeasibility finding.
- Quali-only v1 scope.
- 3-gate plan structure (Candidate B over Candidate A in `PLAN_CANDIDATES.md`) — chosen for
  locality/reviewability (the regression-safety gate is the whole point of this phase; isolating
  config-schema changes (G2) from runtime-logic changes (G3) keeps the bit-identical-off
  evidence trail clean) over fewer-dispatch-round-trips.
- `axis_name` no-production-default (§2 above), a Commander ruling with zero bearing on the
  gate since it never executes when the toggle is off.
- Mid-run: authorized a Commander-level (not Admiral-level) small rework fixing G3's
  discovered `axis_name`-threading gap in `sampled_runtime_manifest_assembly.py` — judged
  mechanical/same-pattern, not a design/latitude question, so handled without a second float.
- Triage tc3 (extract `_run_stage`'s physics block to a helper): technically clears the
  fix-now ladder, but deferred (filed as #657 instead) since the reviewer's own finding
  explicitly conditioned it on "if/when a third stage-toggle is proposed" — a future
  conditional that hasn't occurred; avoided speculative churn on already-reviewed, working code.

No unresolved floats remain.

## 5. Map impact, triage, and workflow feedback

**Map impact:** yes, reconciled (commit `2fcb9d15`) — a genuine architectural first: the
initial `struct:evo -> struct:physics` edge (dormant, toggle off in every shipped manifest),
plus `docs/architecture/packets/physics.md`'s now-outdated "nothing outside `src/physics/`
imports it" claim corrected. Cartographer subagent did the work; independently re-ran
`scripts/check_arch_map.py` myself (OK).

**Triage candidates** (`.agent-work/630-phase6-bt-injection/TRIAGE_RECOMMENDATIONS.md` in the
worktree, full ladder-check reasoning there):
- tc1 — `test_evo_import_boundary.py` regex anchor looseness → **fixed-now**, commit `54ad1c3a`.
- tc2 — test suite dirties real `data/f1_data_*.db` files (a test opens the real default DB
  path instead of an isolated fixture; confirmed independently by 3 different crew agents
  across this run, each restoring via `git checkout`) → **filed**, issue [#656](https://github.com/fredcai6/f1Brainz/issues/656).
- tc3 — extract `_run_stage`'s physics-injection block to a helper → **filed**, issue [#657](https://github.com/fredcai6/f1Brainz/issues/657) (deferred, see §4).
- tc4 — thread `axis_name` end-to-end through `gold_cycle`/CLI so the enabled path is usable
  from real entrypoints → **recommend-and-defer**. This is the natural Phase-7 activation
  prerequisite; whether it becomes its own issue or folds into whatever charters Phase 7 is an
  epic-level sequencing call outside a single-issue Commander's latitude. **Admiral: please
  route at epic closeout.**

**Workflow feedback** (harvested from every `gN-integrate`, distilled — none banked as a new
LESSONS.md entry; all either applied this run or already covered by existing lessons):
- The `quali_pace_anchor_enabled` precedent was an excellent worked example — every layer it
  touches has a direct structural mirror in this run's toggle, which made handoff-authoring
  fast and low-ambiguity. Confirms `handoff-cite-exact-seam-signature`'s value (exact
  line-number pointers + verified ground truth, e.g. "no argparse flag exists" checked before
  writing the handoff, saved a round-trip).
- Two genuine "stop condition hit, reported not papered over" moments (G2's `simplification_limits`
  regression, G3's `axis_name` assembly gap) both resolved cleanly in one focused follow-up
  each — the honest-null/stop-condition doctrine worked exactly as intended: crews reported
  precisely rather than guessing or silently expanding scope.
- One crew (g2 rework reviewer) briefly experienced an identity-confusion artifact from a
  system reminder claiming its own name was "Phase6Cmdr" — self-corrected without incident,
  noting it in its report. Not actionable, just recording it happened.
- `py -m src.utils.simplification_limits` is real, inherited project doctrine
  (`ORCHESTRATOR_CONTEXT.md`'s Evidence Requirements table) that my G1/G2/G3 handoffs did not
  proactively name in their Required Evidence sections until after G2's rework taught the
  lesson the hard way; G3's handoff then named it explicitly upfront and needed no rework for
  it. Worth a standing habit for future physics/evo handoffs in this repo: always name
  `simplification_limits` as a verification command for any `src/`-touching gate, not just
  pytest.
- No lesson met the bar for a new LESSONS.md bank entry — everything above is either a
  one-off, already covered by existing lessons (`handoff-cite-exact-seam-signature`,
  `diagnose-first-decide-fix`), or resolved within this run.

## 6. PR

**https://github.com/fredcai6/f1Brainz/pull/658** — OPEN, MERGEABLE, clean-room reviewed
**APPROVE**. Admiral merges server-side per standing instruction; I did not local-merge to main.
