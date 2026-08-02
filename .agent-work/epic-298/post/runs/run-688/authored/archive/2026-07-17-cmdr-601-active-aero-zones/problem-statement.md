# Problem Statement

Build a source-backed reference layer for 2026 Driver Adjustable Bodywork allowance zones.

The layer represents event/session/track opportunity windows and lines published by FIA/F1 or official event documents. It must not claim per-car active-aero state, because prior waves found no observed per-car 2026 active-aero state in local FastF1/cache/telemetry surfaces.

In scope:
- Discover and record FIA/F1 public sources for Driver Adjustable Bodywork activation zones, low-grip partial zones, detection lines, activation lines, and related allowance limits.
- Add a bounded code/data contract with strict input validation, provenance, and trust fields.
- Seed only source-backed facts or source-backed fixtures; if public event-specific documents are unavailable, produce the interface and document the source gap.
- Add tests and docs for downstream CdA-identification consumers.

Out of scope:
- Per-car aero-state inference.
- Generated DB/parquet commits.
- Physics fitting, default flips, or broad model promotion.

Ratifying source: LAUNCH_ORDER Mission, Pre-Rulings, Honest-Null Clause, and Inherited Latitude.
