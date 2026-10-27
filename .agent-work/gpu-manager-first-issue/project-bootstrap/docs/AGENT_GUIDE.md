# Agent guide

The human approved docs/DESIGN.md and said "Go for it" on 2026-10-22. Build only
its first read-only GPU status issue. Pi owns the Commander and separate crew sessions.
Sonnet is authorized. See ANTHROPIC_AUTHORIZATION.md for provider/data authorization.

## Scope

Python standard library, small collector/snapshot/CLI, text and JSON views of one
snapshot. Best-effort PID/name attribution; no full command lines or environments.
Container names and exact per-process VRAM are deferred. Handle invalid, missing,
partial, permission-denied and racing observations honestly. A cooperative scan
budget cannot promise that an individual kernel read will never block.

No GPU compute tests, benchmarks, inference requests, model loads, root access,
container lifecycle actions, process signals, scheduler, daemon, driver changes,
GPU configuration writes or existing-service changes. Running GPU users stay untouched.
Only read current GPU state for the final smoke check. Do not use Docker in this issue.

## Work

Use fixture-based unittest tests. A Python executable known to work on this machine:
/home/tommy/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/bin/python
Use it for tests; the shell's default python currently has a broken standard-library path.
Keep packaging minimal and provide an executable gpu entry point usable from the repo.
Use synthetic sysfs/proc roots and a controllable clock or filesystem seam to test
missing metrics, permission errors, process disappearance and budget exhaustion.
Catch expected external-data errors explicitly; programming failures should surface.
Keep tests independent of live GPU state. No dependency installs are needed.

Do not edit this guide, AGENTS.md, docs/DESIGN.md or provider authorization to relax
scope. Implementation may add source, tests, README, packaging, and normal gitignore.
Do not commit, push, or publish; the supervising agent handles local closeout.
Call finish_crew with actual commands/results and limits; reviewer runs tests independently.
