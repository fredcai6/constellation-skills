# Launch Order: `cmdr-562 — W1 race-state fuel-mass model`

Commanders start cold. Paste, don't point.

## Mission
Issue **#562** (under epic #509, tire-age wave W1). Replace the single fixed `MASS_KG = 808.0` constant (`src/physics/longitudinal_fit.py:44`, baked into every force equation) with a real per-context mass model, and **rewire all consumers** to use it. This is the foundation for the whole tire-age epic: race laps at different fuel loads must be comparable before any race fit or tyre-age separation is possible. Fuel-mass is a `[MODEL/ANCHOR]` — known-physics, **NOT fitted**. Deliverable: the mass module + the rewire + tests + a short validation note, landed as a merge-ready PR with a readiness statement.

## Model (the agreed design — implement this)
`m(season, team, lap) = base_min(season) + team_offset(season, team) + fuel(...)`
- **`base_min(season)`** — FIA regulation minimum car+driver mass, **per season**. Verify exact values from the regs (≈ 2022 798, 2023 798, 2024 798, 2025 800 kg) and encode as a per-season config/constant map. Do not hardcode one cross-season value.
- **Quali context** = `base_min(season) + nominal_quali_fuel` where `nominal_quali_fuel` ≈ 10 kg (configurable). This MUST make 2023 quali ≈ 808.0 so the existing 2023-Q estimate pool and the `theta_D = CdA/(2·MASS_KG)` conversions stay comparable. (2025 → ~810, correctly.) **Regression-check this**: 2023 quali fits must be unchanged.
- **Race fuel** = per-circuit **linear** burn with **SC/VSC-aware cumulative** accounting: green-flag laps burn at the full rate, SC/VSC laps at a reduced rate (~half). `fuel_start(circuit) = burn_per_lap × n_race_laps`, capped at the 110 kg regulation max; `burn_per_lap` ≈ 1.8 kg/lap (or `fuel_start / n_laps`). Cumulative burn = sum over elapsed laps of the per-lap (status-dependent) burn.
  - **Data dependency:** per-lap track status (SC/VSC) must be available. FastF1 exposes `TrackStatus`; verify the lap store/DB preserves it. If absent, the smallest honest add is to ingest it (or, if truly unavailable, fall back to pure-linear and **flag it explicitly** — do not silently approximate).
- **`team_offset(season, team)`** — a config lookup, **default 0** (anchor, not fitted); applies to BOTH quali and race contexts. Structure it `(season, team) -> kg`. Ships all-zero.

## Scope
- **Produce + rewire.** Ship the mass module AND thread `m(...)` through the existing fixed-`MASS_KG` consumers. Known consumers (verify each from source before editing): `src/physics/longitudinal_fit.py` (`MASS_KG` def), `src/physics/diagnostics/force_residual.py` (imports `MASS_KG`, `mass_kg` param), `src/physics/layer2/braking_view.py` (`mass_kg` param), `src/physics/layer2/coast_view.py` + `coast_report.py` (`MASS_KG`), `src/physics/layer2/decoupled_braking_input.py` (`MASS_KG`). Grep for all `MASS_KG` importers to be exhaustive.
- The rewire must keep quali behavior identical (quali context resolves to ~808 for 2023). The variable mass matters for the *race* path (which W2 builds) — for quali consumers, the value is the season-aware quali mass.
- New code under `src/physics/`. **DB is the only data source** (no live FastF1 from analysis code).

## Prior-Wave Verdicts (pasted)
None — W1 is the first wave. Context you need is in this order + the design doc.

## Pre-Rulings
Ruled in advance, each overridable if evidence contradicts it — say so when overriding.
- New code lands as new module(s) under `src/physics/`; rewiring existing files is in-scope and expected (this is a "produce + rewire" mission).
- Quali context preservation (2023 ≈ 808) is **mandatory** — do not re-baseline the quali pool.
- Fuel-mass is an anchor, **not fitted**. No optimization/fitting of fuel or mass parameters.
- `team_offset` ships default-0; do NOT attempt to estimate it (that's a separate future issue).
- Validation tier is **(b)**: formula + bounds + a physical sanity check (illustrative plot), **no pace-fit validation** (that's a separate future issue).
- 2022+ era is the eventual scope, but the mass model itself is era-general (per-season base) — implement per-season for all seasons present.

## Honest-Null Clause
A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win. **Posture: build a solid, expandable baseline; the first build is not the final answer. Take any null/surprising result in stride — stay confident, don't thrash.**

## Inherited Latitude
- **Delegated to you:** module placement under `src/physics/`, the config representation (constants vs YAML), test layout, fit hyperparameters (n/a here), routine implementation choices.
- **Float to the Admiral:** any need to change the quali-mass reference away from ~808-for-2023; any architecture/boundary change; any scope change (dropping the rewire, adding fitting); anything outside `src/physics/` + tests + docs; if `TrackStatus` is unavailable and you must change the fuel model materially.

## File Ownership
You are the sole writer this wave for: the new mass module(s), the `MASS_KG` consumers listed above, their tests, and any touched docs. No other commander touches `src/physics/` this wave. **Do NOT commit** `.agent-work/LESSONS.md`, `.agent-work/AGENT_FEEDBACK.md`, `.agent-work/CONSTELLATION_FEEDBACK.md`, or your own `.agent-work/<id>/` work area on the mission branch (return lessons-delta + feedback in your report; the Admiral applies them centrally).

## Workspace
Worktree: **`C:/Programs/f1Brainz-562`**, branch **`feat/562-mass-fuel-model`**, base **`origin/main` `770b5f1a`**. Created via `git worktree add C:/Programs/f1Brainz-562 -b feat/562-mass-fuel-model origin/main`.
First step, before any git op: confirm isolation — run `git -C C:/Programs/f1Brainz-562 rev-parse --show-toplevel` and `git worktree list`; verify your toplevel is `C:/Programs/f1Brainz-562` (NOT the shared `C:/Programs/f1Brainz`). Paste the output in your return. *(Note: the template's `verify_worktree_isolation.py` is not vendored in this repo — use this `rev-parse` check instead; this substitution is sanctioned by the Admiral.)*

## Inherited Context
Active lessons + invariants (from `.agent-work/LESSONS.md` + project playbook):
- **Python is `py`, never `python`.** Engine command-checks may hard-code `python` — use `py` throughout; the contradiction is a known standing one, navigate it.
- **Crew dispatch:** there is no `claude` CLI binary in this harness — dispatch implementer/reviewer crews via the **Agent tool**, recording each attempt through `run_crew.py`'s registry functions; run `recover_crews.py` before each dispatch. (lesson:run-crew-cli-launcher-misfit)
- **Engine artifact postconditions** (review-result/user-decision) are **attached, not attested**; attach review-result to BOTH gN-review and gN-integrate. (lesson:engine-artifact-attest)
- **Compact step:** skip with reason (harness auto-compaction). (lesson:compact-step-skip)
- **Cite exact seams from source** (signature + who else consumes) before relying on them. (lesson:handoff-cite-exact-seam-signature) — e.g. `MASS_KG: float = 808.0` at `longitudinal_fit.py:44`; consumers import it as a module constant AND accept `mass_kg: float = MASS_KG` params.
- **State-note-before-detach**; **shared-files-not-on-mission-branch**; **diagnose-first** if a premise looks uncertain.
- Evidence required (physics): `py -m src.utils.simplification_limits` on touched paths; region suite green; truth-anchored where applicable (units/bounds/invariants explicit).

## Data Locations (absolute — worktrees lack untracked inputs)
- Per-year DBs (lap data, classifications, `tyre_life`/`compound`, lap_number, track status): `C:/Programs/f1Brainz/data/f1_data_<year>.db`.
- Telemetry store (Parquet mirror, all sessions 2018–2026): `C:/Programs/f1Brainz/data/telemetry_store.db` (its `DEFAULT_STORE_PATH` is already this absolute path; reachable from your worktree).
- Quali estimate/fit stores: `C:/Programs/f1Brainz/data/physics_estimates.db`, `physics_fits.db`.
- Do not delete or mutate anything under `C:/Programs/f1Brainz/data/` — read-only from here.

## Budget
Model tier **Sonnet** (commander + crews). This is a bounded, well-specified module + rewire — keep crew tasks tight. Session-window aware: verify crew completion from artifacts (branch/commit/result file), not liveness.

## Stop Conditions
Stop and return when: scope would exceed `src/physics/` + tests + docs; a decision outside your inherited latitude is needed (e.g. changing the quali reference, `TrackStatus` truly unavailable forcing a material model change); the quali-preservation regression cannot be met; or you need context this order doesn't cover and cannot safely proceed — return-and-query the Admiral (it answers and continues you). Asking up is always sanctioned.

## Return Shape
Final report: **readiness statement** (built / tested / quali-preserved Y-N) + evidence (test output, bounds checks, the sanity plot path, the 2023-quali-unchanged regression result) + the PR URL + map-impact notes (new module, rewired consumers) + triage candidates + workflow feedback (lessons-delta ops + friction). Include your `rev-parse --show-toplevel` isolation confirmation. Post the verdict in your return + as a comment on #562.
When you open the PR on Windows, write the body to a temp file and use `gh pr create -F <file>` — never a heredoc or PowerShell here-string `--body`.
