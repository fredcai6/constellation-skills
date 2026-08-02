# Launch Order: `cmdr-601-560 - issue #560`

## Mission

Run issue #560 end to end under `constellation-commander-delegated`: investigate whether thin physics fits need a hard acceptance floor, typed-skip reason, or trust profile. This is Wave 1 of `epic-601-physics-training`, serving the bottom-up path: observations must support modeling before any physics signal feeds evo training.

Deliverable: evidence-backed decision plus implementation if warranted. A scoped honest null is valid: if no hard floor is justified, ship the trust/diagnostic representation or document the declined floor with tests and issue-ready evidence.

## Prior-Wave Verdicts (pasted)

No prior wave in this run. The Admiral selected the historical measurement-first route:

`#560 -> #513 -> narrow #506 -> #450`, with #483/#499 running as parallel 2026 active-aero observation discovery.

Key reason: current physics estimates are not yet safe training inputs. We must first characterize support/trust across views and sessions, then build a canonical FP artifact, then A/B it in evo. Do not wire raw absolute physics params into evo before the #560 trust question and the #513 FP artifact shape are resolved.

Current live issue #560 text, refreshed 2026-07-15:

- Sparse single-session fits currently pass as `ok`, e.g. Azerbaijan 2023 Q GAS with 1 flying lap / 412 samples.
- Tension: sparse does not equal broken; flowing/high-speed tracks legitimately have few braking events. Do not add a blanket floor blindly.
- Task: measure relationship between thinness (flying-lap count / sample count) and fit quality; decide with numbers whether a floor is warranted and what form it takes.
- Acceptance: measured relationship across 2023-Q; evidence-backed decision implemented as typed reason/trust field or explicitly declined.
- Comment 2026-07-12: resolve this with FP-session data in scope because #513 FP fits will constantly hit thin-run acceptance.

Relevant #513 FP pilot evidence:

- Raw FP panels are structurally unidentified because tyre age and session time are collinear.
- Two-population design helps: short runs estimate track/session evolution; FP2 long runs estimate degradation kappa.
- Bahrain 2023 FP2: evolution +0.238 +/- 0.081 %/lap; SOFT kappa +0.82 +/- 0.09 vs race +0.305.
- Bahrain 2023 FP3: evolution +0.180 +/- 0.103; no kappa from only 2 long stints.
- HP attrition is severe in fragmented FP running; candidate fallback is same-weekend race-session HPs.
- FP compound fresh-pace offsets need push-lap filtering before use.

Latest #513 target from #606:

- FIELD_ORDERING accounts for about 5.21 fantasy points/race of model-to-winner deficit.
- Preserve physics/covariance done-bar, but determine whether signals can discriminate the tightly grouped P6-P10 drivers pre-quali.
- Normal and sprint weekends should stay separate.

## Pre-Rulings

- Resolve Q and FP trust together. Do not scope to 2023-Q only if the resulting rule would immediately fail FP.
- Prefer per-view support/trust over a blanket global floor unless evidence strongly supports a hard typed skip.
- Explicitly test mass/fuel sensitivity: `src/physics/layer2/session_estimator.py` historically assumes qualifying mass, which can contaminate FP absolute parameters.
- If absolute parameters are not trustworthy under FP fuel/program uncertainty, prefer relative/specific axes, covariance inflation, or typed contextual labels.
- Do not feed outputs into evo in this issue. This issue prepares the measurement/trust foundation for #513/#450.
- If the implementation adds, renames, or repurposes physics model parameters or store columns, update `docs/architecture/reference/physics-unit-conventions.md` in the same gate.

## Honest-Null Clause

A measured negative on a proposed floor is complete: "no hard floor warranted; use support/trust/missingness fields instead" is successful if backed by data and tests.

## Inherited Latitude

Delegated: local code/docs/tests in the #560 worktree; issue comments with measured findings; bounded fix-now triage within physics/preprocessing; lower/default effort subagents; local diagnostics reading DB/artifacts.

Must float to Admiral: merge, issue close/reopen, production/gold default changes, large generated artifacts or DB commits, direct physics-to-evo coupling, non-DB analysis source, long detached compute, store migration requiring artifact promotion.

## File Ownership

Own #560 implementation files in `src/physics/**`, `src/preprocessing/**`, related focused tests under `tests/unit/physics/**` / `tests/unit/preprocessing/**`, and docs only where required. Avoid writing `.agent-work/epic-601-physics-training/**` in the main checkout. Stage Commander feedback locally under `.agent-work/staged-feedback/cmdr-601-560/` in your worktree if fenced from shared root.

## Workspace

Absolute worktree path: `C:\tmp\f1brainz-601-560`

Branch: `admiral-601-physics-560`

Base commit: `5e8e92d7db79c0d29b6833008aece195128d0ac3`

Created by:

```powershell
git worktree add C:\tmp\f1brainz-601-560 -b admiral-601-physics-560 5e8e92d7db79c0d29b6833008aece195128d0ac3
```

First step before any git operation:

```powershell
C:/Programs/f1Brainz/.venv/Scripts/python.exe C:/Users/fredc/.codex/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here C:\tmp\f1brainz-601-560
```

Paste its output into your return report.

## Inherited Context

Repo constraints:

- Read `docs/AGENT_GUIDE.md`, `README.md`, `TESTING.md`, `docs/architecture/index.md`, `docs/DOCUMENTATION.md`, `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`.
- DB is canonical. No direct FastF1 calls from analysis/model/adapter code.
- Physics/preprocessing rigor requires truth-anchored tests and explicit units/bounds.
- Physics imports no evo package; do not create a physics-to-evo dependency.
- `py` is the documented launcher, but this sandbox may lack it; use `C:/Programs/f1Brainz/.venv/Scripts/python.exe` where needed and report that substitution.
- Artifact evidence must be source-verified, not merely asserted.

Relevant architecture:

- `src/physics/layer2/session_estimator.py` estimates five-view session parameters and currently has qualifying-session assumptions.
- `src/physics/mass_model.py` owns `quali_mass` and `race_mass`.
- `src/physics/fit_store.py` / estimate stores are standalone artifacts, not canonical season DBs.
- The evo pipeline consumes DB-backed practice/session features through adapters; physics currently has no prediction-path consumer.

## Pre-empted Steps

The Admiral has already selected the issue order, confirmed latitude, refreshed issue text for #560/#513, and provisioned the worktree.

## Data Locations

Use the main checkout for untracked/local data artifacts if absent from the worktree:

- Main checkout: `C:\Programs\f1Brainz`
- Season DBs: `C:\Programs\f1Brainz\data\f1_data_*.db`
- Telemetry store: `C:\Programs\f1Brainz\data\telemetry_store.db` and `C:\Programs\f1Brainz\data\telemetry_store_parquet\`
- Physics stores: `C:\Programs\f1Brainz\data\physics_fits.db`, `C:\Programs\f1Brainz\data\physics_estimates.db`, `C:\Programs\f1Brainz\data\race_stint_estimates.db`

Do not modify main-checkout data files from this worktree.

## Budget

- Model tier: inherited/default.
- Compute/time: focus on 2023-Q plus FP representative slices first; broaden only if cheap and necessary. No multi-hour detached batch without floating to Admiral.

## Stop Conditions

Stop and query Admiral if: a store migration/artifact promotion is needed; non-DB source is required; the evidence says #513 must be rescoped; mass/fuel uncertainty requires a broader model decision; tests require long retraining; or implementation would cross into evo.

## Return Shape

Return:

- verdict and scoped evidence
- changed files and rationale
- tests/diagnostics run with key outputs
- whether #560 should be commented/closed and exact suggested issue comment
- map/doc impact
- staged feedback path
- isolation verifier output

Write a local result artifact at `.agent-work/cmdr-601-560/RESULT.md` in your worktree before final response.
