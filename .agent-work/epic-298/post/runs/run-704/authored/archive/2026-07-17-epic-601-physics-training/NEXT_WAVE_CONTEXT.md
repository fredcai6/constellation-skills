# Next-Wave Context - epic-601-physics-training

Updated: 2026-07-15

## Wave 2 Candidate: #513

Launch only after #560 returns a trust/support answer that can be applied to FP sessions.

Current acceptance frame:

- Produce or specify the FP-session physics artifact for predict-time use.
- Keyed by event/session/constructor/driver/as-of.
- Carries relative/specific capability axes, covariance/trust/support, missingness, and provenance.
- Separates short-run session evolution from FP2 long-run degradation.
- Handles HP-calibration attrition and push-lap filtering.
- Keeps normal and sprint weekends separate.
- Must report whether the signal can discriminate P6-P10 pre-quali, not just overall rank quality.

## Wave 3 Candidate: narrow #506 + #450

#506 is not the #560 trust floor. It is the later systematic floor/covariance honesty pass:

- Replace static CdA/Pmax/A0 floors with data-driven propagation where needed.
- Split shared systematic vs session-varying uncertainty so pooling does not shrink shared bias away.
- Use #560/#513 evidence to decide the narrow floor surface needed before #450.

#450 runs only after #513 produces usable pre-quali measurements and #616 makes sampled A/B output reproducible.

Current #450 decision metrics:

- total fantasy points/race against actual results
- FIELD_ORDERING attribution delta, especially P6-P10
- TOP5 attribution delta
- normal vs sprint results where coverage permits

Generic rank/sign/correlation gains without fantasy-channel gain do not clear the #601 capacity gate.

## 2026 Sidecar Dependency

#483/#499 should not block historical 2019-2025 proof unless it finds an artifact-schema issue that changes the FP artifact contract. If active-aero state is not observable in the current DB telemetry channel, the sidecar should recommend ingestion/source discovery or 2026 guardrails, not invented config labels.
