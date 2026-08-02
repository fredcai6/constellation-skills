# Plan Approval — issue #446

Approved on the Admiral's delegated authority (LAUNCH_ORDER_446.md inherited latitude).

## Plan shape (3 gates)

- **g1** — Scoring primitives (sector-anchor gate w/ co-estimated anchors, covariance-
  consistency chi-square, cross-residual diagnostic) + JSON report schema + schema doc.
  Pure core, truth-anchored L1/L2 unit tests. No IO.
- **g2** — Offline raw-stream loader + DB truth loader + strawman candidate (wraps merged
  get_telemetry) + runner. Integration-tested on one cached session.
- **g3** — ≥3-session strawman run (≥1 race, ≥1 quali, 2022-2025) via a scripts/ driver;
  machine-readable reports to evidence dir; VERDICT.md with key numbers + discrimination /
  honest-null conclusion.

## Why this is within latitude (no Admiral float needed)

- Module placement in `src/preprocessing/` — pre-ruling 3.
- JSON schema + `docs/report_schemas/` doc together — pre-ruling 7 + repo policy.
- Anchors co-estimated as calibration parameters with uncertainty — pre-ruling 5.
- Session selection (Commander latitude) — pre-ruling 8.
- Honest null accommodated as a first-class g3 outcome — honest-null clause.
- No data/physics/evo boundary crossing; no deliverable added or dropped; PR opened not
  merged (allowed). The single durable-structure choice — the committed report schema as a
  future Phase 0b/1 contract — is flagged in the mission frame as a reconcile-stage decision
  candidate for the Cartographer, which is the correct (non-floated) handling.

## Sequencing rationale

Primitives first (fast pure tests, the testable heart), then IO wiring (integration on one
session), then the real-data discrimination run last (depends on both). Each gate the
smallest reasonable bite with its own close criteria and evidence.
