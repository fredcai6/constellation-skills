# Run summary — issue #624 Phase 0 probes (Commander run 624-phase0)

## Gates closed (execute.json, all 10 tasks complete, 1 waived condition)
- **e0-context**: plan/pre-registration loaded.
- **g1 (correlation screen)** — crew gate, implement+review both APPROVE. `scripts/g1_correlation_screen.py` committed. Headline: pre-registered primary axis `lateral_total_grip_g` vs evo's quali error, Pearson r=-0.0923 [-0.1281,-0.0562], n=2923 (small, correctly-signed, CI excludes zero); Spearman rho=+0.0135 (CI includes zero, sign-mismatched — filed as #634).
- **g2 (wide-σ A/B checkpoint)** — crew gate, implement+review both APPROVE. `scripts/g2_wide_sigma_ab.py` committed. Seam confirmed externally injectable, zero `src/` changes. A/B result: confirmed-genuine structural null (bit-identical Brier) — the residual-history module is wired into zero production manifests (filed as #636).
- **g3 (integration tracer)** — reasoning gate. 2025 Japan round-tripped: no error, schema-asserted (`scripts/g3_schema_assert.py`), 3-driver DB spot-check pass. Phase-5's four-record contract confirmed UNBUILT (current shape: single 3-stage-keyed JSON) — informational, not a blocker.
- **g4 (SQ probe)** — reasoning gate. SQ session loads via the existing `session=` override; `estimate_session` runs without modification. 10/11 axes numerically plausible vs same-weekend Q (2023 Austria, Red Bull Racing); 1 flagged (`brake_aero_decel_per_m`, recommend-and-defer). One postcondition (`c3`, an over-broad grep check I authored) waived by me with documented reason after independent verification the real constraint holds.
- **g5 (baseline lock)** — reasoning gate. x4 floor table + x7 five-fracture checklist transcribed verbatim (byte-diff-verified) to `docs/physics/624-phase0-baseline-lock.md`.

## Architecture reconciled
Cartographer updated `docs/architecture/packets/evo_predictor.md` (residual-history seam finding), `packets/physics.md` (baseline-lock doc reference), and an `index.md` reconciliation-log entry. `check_arch_map.py` green (42 nodes/20 packets/12 overlays, unchanged — zero `src/` changes this run). No new structural nodes/edges/decisions (confirmed by both the Cartographer subagent and my own independent re-run of the checker).

## Triage
4 candidates surfaced, all routed: **#634** (Pearson/Spearman mismatch), **#635** (team_canonicalization misjoin risk), **#636** (residual-history seam dormant) filed; 1 (SQ-probe caveat) recommend-and-defer, folded into future #513 work.

## Isolation evidence
`git worktree list`: `C:/Programs/f1Brainz 16c314b9 [main]` / `C:/Programs/f1-624 16c314b9 [feat/624-phase0-probes]` (distinct). `py -c "import src.evo_predictor.run as r; print(r.__file__)"` → `C:\Programs\f1-624\src\evo_predictor\run.py` (worktree-local, confirmed before every run this touched `src.*`).

## What was NOT built (per Pre-Ruling #3, no Phase 1-6 machinery)
No new estimator modeling. No Phase-6 BT injection. No production-default/manifest changes. No merge (Admiral's call).

## Deliverables (committed on branch `feat/624-phase0-probes`)
- `scripts/g1_correlation_screen.py`, `g2_wide_sigma_ab.py`, `g3_schema_assert.py`, `g4_sq_probe.py`
- `docs/physics/624-phase0-baseline-lock.md`
- `docs/architecture/index.md`, `packets/evo_predictor.md`, `packets/physics.md` (reconciled)

## Data-side-effect hygiene
`git checkout -- data/` run in the MAIN checkout after every sampler-touching probe (g2, g3) per known issue #632; confirmed clean each time. No `data/*.db` ever staged/committed.
