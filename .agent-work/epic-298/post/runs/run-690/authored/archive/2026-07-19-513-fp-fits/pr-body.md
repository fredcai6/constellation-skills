## #513 Phase 4 — FP-session fits (epic #601, wave 8)

Extends the physics estimator to fit **free-practice sessions** without the silent quali-mass fuel bias, and builds a **falsifiable held-out representativeness gate**. Delegated commander run (Ship I); **not merged — handed back to the Admiral.**

### What landed (5 gates, each reviewer-APPROVED)
- **`mass_model.fp_mass()`** → returns a **distribution** `FpMass(mass_kg, sigma_kg)` — the unobservable FP starting-fuel intercept is carried as σ, never a scalar. New **`fp_lap_latent.py`** (per-lap fuel_est / compound OBSERVED / tyre_life Optional / emergent run_purpose).
- **`fp_representativeness.py`** — continuous per-observation weight w∈[0,1] from the observation's own properties via a transparent logistic — **emergent, no session label**. Passes within-session-orthogonal + cross-session-divergent emergence tests (a track-evolution-only weighting gets them backwards).
- **`estimate_session` FP wiring** — `session_type`/`mass_kg`/`db_path`; FP resolves mass via `fp_mass`; the intercept σ **widens** the mass-consuming longitudinal axes (cda/p_max/b_b/b_t) via the existing #627 machinery — **widens, never shifts a mean**; grip axes untouched; **Q byte-identical**.
- **per-car `cumulative_track_laps`** into `session_estimates` — **unblocks #626** (coordinated with ShipE-626).
- **`fp_gate.py`** — held-out gate harness (leave-one-weekend-out, learned-vs-clock arms, paired bootstrap, divergent-case read, both channels). 36 synthetic tests incl. **positive→PASS, null→HONEST_NULL (structurally non-riggable), leakage-free**.

### G7 — honest-scoped
The falsifiable machinery is **proven correct on synthetic ground truth**. The **powered** real held-out run over the frozen 16-weekend LOWO is **compute-deferred**: measured single-driver apex-extraction = 120 s → full run ≈ **37 h** (infeasible in one session). Handed back as a specified, ETA'd job — see `.agent-work/513-fp-fits/REAL_RUN_HANDBACK.md` (real-extractor spec + resume command). Live-validated: `fp_mass(2023)` mean 835.5 vs `quali_mass` 808.0.

### For the Admiral
- Full verdict: `.agent-work/epic-601/wave8-513-verdict.md`.
- **tc3 is a #646 BLOCKER**: `scripts/backfill_estimate_store.py` has the same missing-`session_type` bug fixed here in `estimate_batch` — must land before any real FP backfill.
- Open float: accept the honest-scoped deliverable, or commission the real extractor + powered run.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01TCVFBhM9kK6MR4jjZVkLzR
