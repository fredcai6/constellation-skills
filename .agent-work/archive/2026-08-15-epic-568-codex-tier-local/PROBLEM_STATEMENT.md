# Problem statement

The crew launcher already persists an optional `model` for fresh launches and
uses a nullable lookup while resuming an existing registry entry. The bounded
gap is that an external Codex caller cannot persist or recover an optional
`reasoning_effort` alongside that model.

The launch order fixes the approach: thread nullable metadata through the CLI,
`CrewSpec`, durable registry creation, and recovery/relaunch paths. External
dispatch remains record-only. Claude's command line must remain unchanged, so
`reasoning_effort` is registry metadata only and never becomes a Claude flag.

The map is degraded because this repository has no citable architecture map for
`scripts/run_crew.py`; the recorded README substitution and launch order supply
the governing frame. No migration, default change, external launcher behavior,
or files beyond the assigned launcher, focused tests, and this work area are in
scope.
