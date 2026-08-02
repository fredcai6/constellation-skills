# Launch Order: `cmdr-7b-2026-aero` — basic 2026 aero capability (#483)

You are a delegated Commander under Admiral `epic-601-physics-training`. Run the full Commander spine in your worktree. No reachable human — float to the Admiral via your return report.

## Mission
Deliver a **basic, defensible per-team 2026 aero capability** the sim/evo can consume — despite the confirmed null that no observed active-aero (movable-wing) state exists in 2026 data. Two ordered parts:
1. **Integrity first — fix the `RegulationEra` 2026 mislabel.** `src/physics/regulation_era.py` currently models only `drs_enabled = season≥2011` and `mguk_regen = season≥2014`, so 2026 evaluates as a 2024-style season: it thinks a DRS lever exists (2026 DRS is all-zeros) and applies the 2014-era MGU-K assumption to a PU that dropped the MGU-H. Add a 2026 regime distinction so the DRS-split drag path fails closed / is not silently mis-applied to 2026, and the power model isn't wrong. Then **sanity-check the existing 77 fitted 2026 rows** for era-bias: because the PowerDrag descent deconfounds P_max from CdA via the power curve, a wrong 2026 power assumption biases CdA through the P_max↔CdA covariance — check whether the 2026 fits' `power_drag_covariance` / degeneracy widens versus 2025, and report it.
2. **Pool + expose the 2026 aero axis.** Using `pool_driver` over the EXISTING 2026 `session_estimates` rows, emit a **per-constructor pooled `drag_area_closed_m2` with σ_μ + covariance**, published **state-agnostic (single-config)** per the `source-missing-guarded` ruling. The 5 degenerate teams (CdA hit the 0-bound — short-straight identifiability, e.g. Ferrari/Red Bull at Australia) get a **low-trust flag / 2025-carry-forward fallback**, reusing the trust-metadata primitive already on your base branch (#560, `estimate_store.py` support/trust fields). Output a small committed artifact (JSON/CSV) — NOT a large DB write.

## Prior-Wave Verdicts / Recon (pasted)
- **No observed 2026 active-aero state** anywhere FastF1 reaches (DB/parquet/raw session/.ff1pkl/FastF1 source/docs); 2026 exposes only `DRS`, all-zeros; 2025 has nonzero DRS. So the axis is modeled/prior, never observed-state.
- **The drag number already exists without DRS:** `src/physics/layer2/power_drag_view.py` fits the full-throttle power-limited descent `P_max/(mv) − CdA·ρv²/2m` on the straights — DRS not required. `data/physics_estimates.db` already holds **77 fitted 2026 rows, all fit_status='ok', 72 with usable `drag_area_closed_m2`+σ, 5 degenerate**. Sample (2026 Australia Q, m²): Cadillac 0.919, Alpine 0.722, McLaren 0.677, Mercedes 0.625, Williams 0.511; Ferrari & Red Bull degenerate.
- **Pooling primitive:** `src/physics/layer2/pool_driver.py` `pool_store` / `pool_random_effects` (DerSimonian–Laird → μ, σ_μ, τ) already yields per-constructor pooled params; CdA is `_PARAMS[0]`.
- **Prior:** CdA is circuit/setup-conflated, fine-margin (frac_team ≤ 3%) — ship covariance, treat the per-team number as a RELATIVE prior, not a gate.
- **#483 prior comments:** Wave-2 pinned an all-zero-DRS guardrail (`no_drs_lever`) on branch `admiral-601-active-aero` commit `370704442f` (12 tests pass) — you may reference/reuse its approach but your base is local main; re-implement cleanly here. Ruling stands: 2026 baseline proceeds state-agnostic only.

## Pre-Rulings (overridable with evidence)
- **State-agnostic single-config only.** Do NOT generalize the DRS fit into named 2026 aero regimes from heuristics (that is the SHELVED #499 `AeroDragSet` path, blocked at source). One closed-config CdA per team is the deliverable.
- Do NOT build on the shelved `active_aero_zones.py` / `active_aero_identification.py` allowance-zone modules — they fail closed (no public FIA event distances).
- Integrity fix precedes pooling: no 2026 axis ships if the era check reveals the 2026 CdA fits are power-model-biased beyond usability — in that case report the blocker instead of shipping a biased axis (honest-null).
- Degenerate teams: low-trust flag / 2025-carry-forward, NOT a hard drop (the #560 trust-field pattern).
- Any write to a `.db` (not a small text artifact) is SURFACED — float to Admiral first.

## Honest-Null Clause
"The 2026 CdA fits are too power-model-biased / too degenerate to form a usable per-team axis" is a complete, successful deliverable if evidenced. Report with full rigor.

## Inherited Latitude
Delegated: subagent dispatch (Sonnet), bounded edits to `src/physics/regulation_era.py` + a pooling helper + a small committed artifact, same-gate tests/docs, local runs against the main-checkout DB. Float/surface: any `.db` write or store migration, store-parameter schema changes beyond additive, issue close, merges, production-default flips.

## File Ownership
You own `src/physics/regulation_era.py`, any new pooling/exposure helper you add, your artifact file, and `.agent-work/cmdr-7b-2026-aero/RESULT.md`. **Do NOT edit `src/physics/layer2/estimate_store.py`'s σ/`SYSTEMATIC_FLOOR`** (reserved for a later #506 task) — you may READ its trust fields (already on your branch via #560). No contention with 7A (analysis-only) or 7C (git-reconcile).

## Workspace
Worktree: `C:/tmp/f1brainz-601-7b-aero`, branch `wave7b-2026-aero`, base `ed57bccc` (= #560 branch tip, so you inherit the trust-metadata fields). Created via `git worktree add -b wave7b-2026-aero C:/tmp/f1brainz-601-7b-aero ed57bccc`.
FIRST STEP: `py scripts/verify_worktree_isolation.py --here C:/tmp/f1brainz-601-7b-aero` — must exit 0; paste output.

## Inherited Context (invariants)
- Python `py` (3.14); tests `py -m pytest tests/...`. Editable-install `.pth` trap: pin worktree `src/` on `sys.path` for bespoke scripts (pytest safe).
- DB is single source of data; no direct FastF1 calls from model/analysis code.
- The `physics_estimates.db` with real 2026 rows is in the MAIN checkout (see Data Locations).
- Windows: PR/GH bodies via `gh ... -F <tempfile>`.

## Data Locations (main checkout)
- `C:/Programs/f1Brainz/data/physics_estimates.db` (the `session_estimates` store with 2026 rows)
- `C:/Programs/f1Brainz/data/f1_data_2026.db` (2026 classifications: 9 rounds Australia→Great Britain)

## Budget
- **Model tier (required):** Sonnet. Escalate only for ambiguous physics numerics (e.g. the era-bias covariance interpretation) or a failed lower-effort attempt.
- Local runs only; no long detached training.

## Stop Conditions
Stop/return when: the era fix + 2026 pooled axis artifact are built and tested (or the honest-null blocker is evidenced); OR you'd need a `.db` write / store migration / schema change to proceed; OR you need uncovered context. Ask up freely.

## Return Shape
Write `.agent-work/cmdr-7b-2026-aero/RESULT.md` before idle. Include: verdict; the `RegulationEra` change + its test; the 2026 era-bias sanity-check result (covariance/degeneracy vs 2025); the per-team 2026 pooled CdA axis (values + σ_μ + covariance) and its artifact path; degenerate-team handling; tests run; changed paths; the `verify_worktree_isolation.py --here` output; map-impact note (new `regulation_era` behavior + new artifact); triage candidates. Open a PR (base local `main`; `gh pr create -F <file>`) and report its number, or if you cannot push, report the branch/commit for Admiral pickup.
