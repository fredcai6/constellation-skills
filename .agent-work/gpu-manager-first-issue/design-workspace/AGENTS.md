# GPU manager design workspace

This is a design-only workspace. Read ISSUE.md for the agreed first slice and
HISTORICAL_HANDOFF.md for history. The human agreed that read-only status and
best-effort workload attribution are the first issue. Sonnet is authorized.

No implementation, GPU probes, shell commands, services, model loads, installations,
container changes or workload changes are authorized in this task. The Commander
has read-only tools and propose_plan. Use propose_plan to return the short design
for human review. The design is the plan artifact, not authority to implement it.

Favor Python standard library and small modules. Keep scheduling, migration,
management and exact per-process VRAM accounting out of scope. Container association
is optional enrichment, not a condition for the first useful status result.
