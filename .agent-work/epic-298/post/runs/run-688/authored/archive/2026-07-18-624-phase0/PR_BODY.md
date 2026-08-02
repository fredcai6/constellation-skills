## Summary

Phase 0 of the confirmed physics-as-feature-engine spec (epic #601): five informational probes on EXISTING data/estimates, per issue #624 and Admiral launch order `ShipB-624`. No new estimator modeling, no production-default changes, no merge (this is the Admiral's call).

- **g1 correlation screen**: pre-registered primary axis `lateral_total_grip_g` (= `lateral_mech_grip_g + lateral_aero_grip_g`, registered in writing at `.agent-work/archive/2026-07-18-624-phase0/PRE_REGISTRATION.md` before any correlation code existed) vs evo's own quali error (actual Q pace gap minus the driver's own trailing-mean recent-history baseline — a semi-partial correlation by construction). Result: Pearson r=-0.0923 [-0.1281,-0.0562], n=2923 — small, correctly-signed, CI excludes zero. Spearman rho=+0.0135 (CI includes zero, sign-mismatched — filed as #634 for Phase 7). Crew-reviewed, APPROVE, independently reproduced.
- **g2 wide-σ A/B checkpoint**: pushed 2025 Japan's five-view physics estimates through the existing `driver_residual_states` injection seam with a deliberately widened σ. Confirmed the seam is externally injectable with zero `src/` changes. Result: a confirmed-genuine structural null (bit-identical Brier baseline vs injected) — the residual-history module is registered but wired into zero `params/gold/*.json` manifests (filed as #636, prerequisite for any future test). Crew-reviewed, APPROVE.
- **g3 integration tracer**: 2025 Japan round-trips cleanly through the live `sampled-predict` path (schema-asserted + 3-driver DB spot-check). Confirms the DESIGN_SPEC's Phase-5 four-record contract is UNBUILT — current shape is a single 3-stage-keyed JSON, not four separately-typed as-of records (informational, expected, not a blocker).
- **g4 SQ probe**: the Q estimator (`estimate_session`) loads and runs on a real SQ-typed session via the existing `session=` override (bypassing the internal hardcoded `"Q"` load), still applying `quali_mass()` unconditionally (known gap). 10/11 axes numerically plausible vs the same-weekend Q estimate (2023 Austria, Red Bull Racing); 1 flagged (`brake_aero_decel_per_m`, recommend-and-defer, likely just that axis's known noise-sensitivity).
- **g5 baseline lock**: `docs/physics/624-phase0-baseline-lock.md` freezes x4's per-axis relative-normalization floor and x7's five-fracture checklist — transcribed verbatim (byte-diff-verified) from the already-reviewed prior exploration wave, as durable "beat this" targets for Phases 1-4.

Architecture reconciled by Cartographer: `docs/architecture/packets/evo_predictor.md` (residual-history seam finding), `packets/physics.md` (baseline-lock doc reference), `index.md` (reconciliation-log entry). `check_arch_map.py` green (42 nodes/20 packets/12 overlays, unchanged — zero `src/` changes this run).

## Test plan
- [x] `py scripts/g1_correlation_screen.py --check` — exit 0, reproduces headline
- [x] `py scripts/g3_schema_assert.py --check` — exit 0, schema-asserts + 3-driver spot-check
- [x] `py scripts/check_arch_map.py` — OK, map consistent
- [x] Both crew gates (g1, g2) independently reviewed and APPROVED by a separate subagent, re-verified by the Commander
- [x] `data/` in the main checkout confirmed clean after every sampler-touching probe (no `*.db` committed)

## Triage
Filed: #634 (Pearson/Spearman mismatch), #635 (team_canonicalization year-agnostic misjoin risk), #636 (residual-history seam dormant in every manifest). Recommend-and-defer: SQ probe's flagged axis (folds into future #513 work).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01TCVFBhM9kK6MR4jjZVkLzR
