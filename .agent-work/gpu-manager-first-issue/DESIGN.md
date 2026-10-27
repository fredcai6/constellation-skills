# First issue: read-only GPU status

Status: design for human review; no implementation authorized yet.
Prepared from the Pi/Sonnet proposal with coordinator clarifications below.
Standing Anthropic authorization is recorded separately in AUTHORIZATION.md.

## Deliverable

A small Python standard-library project, gpu-manager, with one command:

- gpu status: human-readable snapshot.
- gpu status --json: the same snapshot for agents.

Discover AMD devices through Linux DRM/sysfs, deduplicating aliases by backing
device/PCI identity rather than hard-coding card numbers. Read total/used VRAM and
busy counters. Identify observable device-user PIDs through readable DRM fdinfo,
with process names from /proc/PID/comm. Defer container labels and exact per-process
VRAM accounting. Never inspect process environments or full command-line arguments.

## Honest output

Distinguish measured zero, unavailable, invalid, and partial collection. Free VRAM
requires valid consistent nonnegative readings with used <= total; two reads in
one pass are not atomic. Utilization outside 0..100 is invalid, not clamped.
Permission gaps, disappearing files/processes, and budget exhaustion must be visible;
limited process visibility is not evidence the GPU is idle. Observed DRM handles
identify device users, not proof of active computation or authorization to launch work.

## Small implementation and verification

Start with a collector, snapshot/renderers, and CLI. Use a shared monotonic collection
budget (proposed default five seconds), checking it throughout scanning and returning
partial results on exhaustion. This is a cooperative budget, not a guarantee that
an individual kernel read cannot block. Handle expected I/O and parse failures
explicitly; unexpected programming errors must remain visible.

Use fixtures for multiple devices/aliases, zero usage, inconsistent/invalid readings,
missing metrics, permission gaps, disappearing entries, and budget exhaustion.
A final live check reads existing state only; it launches no GPU work.

## Draft GPU-usage paragraph

GPU status reports current observations without reserving capacity or modifying
workloads. Missing or partial observations are shown explicitly. Existing workloads
and services remain under their current operators. Scheduling, preemption, model
loading, container management, service migration, and the webpage are later issues.

## Scope of this design pass

Pi Commander used Sonnet for two bounded invocations, costing $0.124862
in reported API usage. It read only the prepared project documents, saved a design
proposal, and stopped at the plan approval gate. No GPU probes or code changes were
dispatched. The coordinator tightened range validation, partial-visibility semantics,
and the collection-budget claim while preparing this review version.
