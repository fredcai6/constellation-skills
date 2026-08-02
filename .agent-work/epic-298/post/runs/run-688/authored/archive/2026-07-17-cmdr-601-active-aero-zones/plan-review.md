# Plan Alternatives And Cold Critic

## Alternatives
- Artifact-backed contract first: add a strict JSON/dataclass loader under physics, source findings, and focused tests. Recommended because event-specific FIA documents are not publicly discoverable yet and generated DB commits are forbidden.
- DB schema first: add canonical season DB tables now. Rejected for this gate because no source-backed event distance rows are available and schema promotion would imply persistence authority not yet needed.

## Cold Critic
- Risk: a nullable-distance interface could let downstream code silently treat source gaps as usable zones.
  - Disposition: tests must require projection helpers to fail closed when distances are missing.
- Risk: naming could drift back toward observed state.
  - Disposition: module/docs use `allowance` and `opportunity`; no `aero_state_observed` surface.
- Risk: event-specific source search may be too shallow.
  - Disposition: source-findings records accepted regulatory source and rejected/unavailable event-document surfaces; verdict remains `reference-interface-built-source-gap` unless public documents are found.

Panel choice: single cold critic, scaled to this one-gate reference-contract task.
