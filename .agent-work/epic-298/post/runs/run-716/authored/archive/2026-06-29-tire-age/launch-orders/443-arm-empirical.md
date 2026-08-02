# Launch Order: `cmdr-443 — empirical degradation-sensor (productionize)`

Commanders start cold. Paste, don't point.

## Mission
Issue **#443** (under epic #509, tire-age parallel arm). **Productionize the already-validated** compound-degradation recipe out of throwaway `scratch/` experiments into a proper, tested module: an **empirical `μ_tyre(compound, age)` estimator** + a **neutral within-race pairwise-ordering-accuracy (`P`) metric harness**. This is the independent **cross-check / comparator** for the physics tyre-age work (W3 #511) — it is NOT the physics path. The survey is DONE; this is engineering, not research. Deliverable: the estimator module + the metric harness + tests, as a merge-ready PR with a readiness statement reproducing the validated numbers.

## The validated recipe (from #443's survey — implement this, don't re-derive)
Feature = within-race **relative-rank** compound degradation of the **DRS-clean corner/straight telemetry contrast** `log(corner_q15 / full-throttle-DRS-closed straight)`, on **committed laps**, tyre-age ≥ 3, raw tyre-age, **2022+ only** (the signal is genuinely absent pre-2022 — ground-effect era), weighted toward high-deg circuits; fuel-correct via the straight-speed proxy for absolute s/lap. The best simple production gate (P4 verdict): a global ridge `{relrank, cc_prior, lateral, longitudinal}` with the **lateral sensor gated by era + deg-severity + absolute within-race sensor-confidence** ("trust telemetry when it cleanly separates the compounds this race"). Validated evidence to reproduce: pooled within-race pairwise `P` ≈ 0.74 (vs naive absolute-C# ≈ 0.55), monotone-up relative ladder, permutation +5.5σ, holds across 2022–2025.

## Prior-Wave Verdicts (pasted)
None (parallel arm, wave 1). Full survey record: `FINDINGS.md` committed at git `dfd8862a` (path `.agent-work/compound-deconfound/FINDINGS.md`) — read the "PRODUCTION RECIPE" + P1–P4 + W-series sections. Scratch experiments archived at `C:/Programs/f1Brainz/.agent-work/archive/2026-06-10-compound-deconfound/scratch/` (read via the main checkout; the `exp_*.py` are the reference implementations; the `*.pkl` feature caches are gitignored — regenerate from the telemetry store).

## Pre-Rulings
Each overridable if evidence contradicts it — say so when overriding.
- **Productionize only.** The two deferred threads (per-regime gate composition; investigating NEW sensors) are **OUT of scope** → they go to the closeout research-plan. Exception: only if making the comparator *fair* strictly requires it (float to Admiral first).
- **2022+ scope** (signal absent earlier — do not chase pre-2022).
- The **pairwise-`P` metric harness must be a NEUTRAL eval utility** usable by BOTH this evo module AND physics-W3, placed so it creates **no `physics → evo` import** (e.g. `src/common/` or an equivalently neutral home). This is an architecture call — confirm placement with the Admiral if unsure.
- Reproduce the validated numbers as the acceptance bar; if they don't reproduce, that's a finding to surface (honest-null), not a reason to re-tune.

## Honest-Null Clause
A measured negative is a complete, successful deliverable — report it with full rigor. **Posture: solid, expandable baseline; first build is not the final answer; take nulls in stride, stay confident, don't thrash.**

## Inherited Latitude
- **Delegated to you:** module placement within the evo region (e.g. `src/compound_prior` vs `src/evo_predictor`), the estimator's internal structure, test layout, how you regenerate features from the telemetry store.
- **Float to the Admiral:** the neutral-metric-harness placement if it risks a region-boundary violation; any scope change (pursuing threads); any cross-region coupling; anything touching the physics region (`src/physics/` is off-limits to this arm — W1 owns it this wave).

## File Ownership
Sole writer this wave for: the new empirical-sensor module (evo region), the neutral metric harness, their tests. **Do NOT touch `src/physics/`** (W1/cmdr-562 owns it this wave). Do NOT commit `.agent-work/LESSONS.md` / `AGENT_FEEDBACK.md` / `CONSTELLATION_FEEDBACK.md` / your own `.agent-work/<id>/` on the mission branch (return them in your report; Admiral applies centrally).

## Workspace
Worktree: **`C:/Programs/f1Brainz-443`**, branch **`feat/443-empirical-deg-sensor`**, base **`origin/main` `770b5f1a`**. Created via `git worktree add C:/Programs/f1Brainz-443 -b feat/443-empirical-deg-sensor origin/main`.
First step, before any git op: confirm isolation — `git -C C:/Programs/f1Brainz-443 rev-parse --show-toplevel` must be `C:/Programs/f1Brainz-443` (NOT the shared `C:/Programs/f1Brainz`); `git worktree list`. Paste output in your return. *(The template's `verify_worktree_isolation.py` is not vendored here — this `rev-parse` check substitutes, sanctioned by the Admiral.)*

## Inherited Context
- **Python is `py`, never `python`** (navigate the standing engine-imperative contradiction).
- **Crew dispatch via the Agent tool** (no `claude` CLI binary); record attempts via `run_crew.py` registry fns; `recover_crews.py` before each dispatch. (lesson:run-crew-cli-launcher-misfit)
- **Engine artifact postconditions attached, not attested**; attach review-result to both gN-review and gN-integrate. (lesson:engine-artifact-attest)
- **Compact step:** skip with reason. **State-note before any detach. Diagnose-first** if a premise looks shaky.
- **Cite exact seams from source** before relying on them. (lesson:handoff-cite-exact-seam-signature)
- Evidence (evo/probability change): evo unit suite + the within-race pairwise-`P` metric against the absolute-C# baseline; `py -m src.utils.simplification_limits` on touched paths; **DB/telemetry-store is the only data source** (no live FastF1 from analysis code).
- Region boundary: this is **evo region**; do not import from / couple to `src/physics/`. The compound C-number axis is **relative-rank**, not absolute (absolute pooling across races is why the prior `compound_prior` gamma fit underperformed).

## Data Locations (absolute — worktrees lack untracked inputs)
- Telemetry store (race telemetry 2022+, the corner/straight contrast inputs): `C:/Programs/f1Brainz/data/telemetry_store.db` (+ its sibling parquet tree; `DEFAULT_STORE_PATH` is already this absolute path).
- Per-year DBs (laps, `compound`, `tyre_life`, sector times, weather/track-temp): `C:/Programs/f1Brainz/data/f1_data_<year>.db`.
- Reference scratch experiments (read-only): `C:/Programs/f1Brainz/.agent-work/archive/2026-06-10-compound-deconfound/scratch/exp_*.py`.
- Do not delete/mutate anything under `C:/Programs/f1Brainz/data/` or the archive — read-only.

## Budget
Model tier **Sonnet** (commander + crews). Bounded productionization of a validated recipe — keep crew tasks tight; verify completion from artifacts, not liveness.

## Stop Conditions
Stop and return when: scope would exceed the evo module + neutral harness + tests; the neutral-harness placement needs an architecture ruling; a thread (gate composition / new sensors) seems required; the validated numbers don't reproduce (return the finding); or you need context this order doesn't cover — return-and-query the Admiral. Asking up is always sanctioned.

## Return Shape
Final report: **readiness statement** (estimator built / numbers reproduced Y-N with the actual pooled `P`) + evidence (test output, the reproduced ladder/`P`, metric-harness tests) + PR URL + map-impact (new evo module, neutral harness placement) + triage candidates (incl. the deferred threads for the research plan) + workflow feedback (lessons-delta + friction) + your `rev-parse` isolation confirmation. Post the verdict in your return + as a comment on #443.
When you open the PR on Windows, write the body to a temp file and use `gh pr create -F <file>`.
