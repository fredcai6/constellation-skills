# Launch Order: `cmdr-601-active-aero-identification - #483/#499`

## Mission
Start a bounded CdA-based identification effort for 2026 active aero.

Wave 5 built the allowed-zone reference interface but found no public event-specific distance rows. Your mission is to prototype the identification layer that will consume those zones when available, using existing CdA/drag views and historical observed DRS as a validation analogue.

Deliver one of:

1. A small tested prototype module/harness that identifies or scores low-drag-vs-corner-mode evidence from longitudinal/CdA data inside source-backed opportunity windows; or
2. A measured design/blocker explaining why current CdA views cannot support the identification yet, with the exact missing inputs.

This is “try stuff out overnight,” not production promotion. Keep claims scoped.

## Prior-Wave Verdicts (pasted)
Wave 2:

- Current persisted 2026 telemetry has no observed active-aero state.
- All-zero DRS now fails closed as `no_drs_lever`.

Wave 3 and Wave 4:

- FastF1 standard objects, raw `.ff1pkl` payloads, and local FastF1 3.8.3 parser/source expose no observed 2026 active-aero state field.

Wave 5:

- Commit `efb45ba37f5174e61e761924396e8f30d018dd4a` added `src/physics/active_aero_zones.py`.
- Verdict: `reference-interface-built-source-gap`.
- The module validates active-aero allowance entries and projects source-backed windows to masks.
- Event-specific distance rows were not found publicly; missing rows intentionally produce all-false masks.
- Guidance: consume `ActiveAeroAllowanceReference` as opportunity/eligibility data only; do not treat it as observed per-car state or `drs_open`.

Relevant local CdA seams:

- `src/physics/layer2/power_drag_view.py`: fits `P_max` + closed CdA and optionally DRS-open CdA from measured `drs_open`; exposes `PowerDragView.fit`.
- `src/physics/layer2/coast_view.py`: lower-envelope coast CdA cross-check.
- `scripts/rescue_cda.py`: diagnostic/pooling pattern for pinned-Pmax CdA rescue.
- `scripts/characterize_decoupled_views.py`: diagnostic extraction patterns for throttle and CdA views.

## Pre-Rulings
- This wave may use historical 2025 or earlier observed DRS as a validation analogue for “known low-drag state,” but must not claim that DRS equals 2026 active aero.
- For 2026, absence of event-specific allowance distances means any real-data active-aero mask must fail closed unless explicitly marked hypothetical/prototype.
- Do not infer production active-aero state from speed/throttle alone.
- A probabilistic/inferred score is acceptable only if named as inferred and lower-trust, not observed.
- Prefer a small pure function/module with unit tests over a heavy batch run.
- Do not commit generated data/plots/DBs. Worktree-local diagnostic outputs are fine.
- No production defaults, issue publication, merge, or PR publication.

## Honest-Null Clause
A measured negative is useful if it answers one concrete question: what additional inputs are needed before CdA can identify active-aero mode? Examples: source-backed zone distances, pinned Pmax prior, sufficient high-speed descent support, coast cross-check, or per-session mass/rho trust.

## Inherited Latitude
Delegated:

- Bounded source/docs/tests/prototype code in `src/physics` or `scripts`.
- Worktree-local diagnostic scripts and small outputs.
- Local commit.

Surface:

- Any production path that changes fitting defaults or labels 2026 state as observed.
- Generated artifact/DB commits.
- GitHub publication.
- Broad active-aero model refactor.

## File Ownership
Sole writer:

- `.agent-work/cmdr-601-active-aero-identification/RESULT.md`
- `.agent-work/cmdr-601-active-aero-identification/NOTES.md` if needed
- Bounded prototype code/tests/docs.

Do not edit Admiral files.

## Workspace
Worktree: `C:\tmp\f1brainz-601-aero-identification`

Branch: `admiral-601-aero-identification`

Base commit: `efb45ba37f5174e61e761924396e8f30d018dd4a`

Intended add command:

```powershell
git worktree add C:\tmp\f1brainz-601-aero-identification -b admiral-601-aero-identification efb45ba37f5174e61e761924396e8f30d018dd4a
```

First step:

```powershell
C:\Programs\f1Brainz\.venv\Scripts\python.exe C:\Users\fredc\.codex\skills\constellation-admiral\scripts\verify_worktree_isolation.py --here C:\tmp\f1brainz-601-aero-identification
```

## Inherited Context
Read:

- `docs/AGENT_GUIDE.md`
- `README.md`
- `TESTING.md`
- `docs/architecture/index.md`
- `docs/DOCUMENTATION.md`
- `docs/physics/active_aero_allowance_zones.md`
- `docs/physics/measurement_model.md`
- `docs/architecture/reference/physics-unit-conventions.md` if adding/renaming physics parameters.

## Pre-empted Steps
Admiral accepted Wave 5 and reran `tests/unit/physics/test_active_aero_zones.py`: 6 passed. Do not re-ask the human.

## Data Locations
Read-only local:

- `C:\Programs\f1Brainz\data\telemetry_store_parquet\`
- `C:\Programs\f1Brainz\data\telemetry_store.db`
- `C:\Programs\f1Brainz\data\f1_data_2026.db`
- `C:\Programs\f1Brainz\data\f1_data_2025.db`
- `C:\Programs\f1Brainz\data\telemetry\`

## Budget
- **Model tier (required):** lower/default effort.
- **Compute/time:** focused prototype and tests; no full-season batch, training, or long detached compute.

## Stop Conditions
Stop when:

- You have a tested identification prototype or a strong blocker.
- You need event-specific official zone distances to proceed.
- You need a decision outside inherited latitude.

## Return Shape
Write `.agent-work/cmdr-601-active-aero-identification/RESULT.md`.

Return:

- Verdict: `identification-prototype-built`, `identification-blocked-inputs`, or `blocked-needs-decision`.
- What the prototype estimates and what it refuses to estimate.
- Changed paths and commit hash if any.
- Tests/checks run.
- Whether the method is ready to consume real activation-zone rows.
- Residual risks before a 2026 baseline can use it.
- Isolation verifier output.
