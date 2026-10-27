# Sonnet proposal — GPU status

Model: anthropic/claude-sonnet-4-6. Two bounded invocations. Reported total cost: $0.124862.
Status: proposal for human review, not implementation approval.

# Design: `gpu status` — read-only GPU snapshot (Issue #1)

## Goal
One CLI command: a bounded, honest snapshot of AMD GPU occupancy. No workload changes.

## Device discovery
Enumerate `/sys/class/drm/render*/device/`. Deduplicate by resolving each entry's backing PCI device path via `os.path.realpath`; skip aliases already seen. No card numbers hard-coded.

## Data sources
| Source | Provides | Error handling |
|---|---|---|
| `mem_info_vram_total` / `mem_info_vram_used` (sysfs) | Total/used VRAM (bytes→MiB) | Catch `OSError`/`ValueError`; mark field absent |
| `gpu_busy_percent` (sysfs) | Utilisation integer | Catch `OSError`/`ValueError`; outside 0–100 → `"invalid"` |
| `/proc/PID/fdinfo/*` matching `drm-pdev` | PIDs with open DRM handles | Catch `FileNotFoundError`/`PermissionError` per entry; skip vanished processes |
| `/proc/PID/comm` | Process name (no args, no secrets) | Catch `OSError`; fall back to PID-only label |

No `docker inspect`, no process environments, no cmdline. Container enrichment deferred.

## Semantics
- Free VRAM shown only when total and used were read in the same pass; otherwise absent.
- Busy: integer if 0–100, `"invalid"` if outside range, `"unavailable"` if unreadable.
- JSON: `null` = unavailable, `0` = confirmed zero, `"partial": true` when budget expired.
- Text: explicit note for every absent or invalid field.
- No claim that free VRAM is safe to allocate.

## Collection budget
A single monotonic deadline at entry (`time.monotonic() + BUDGET_SECONDS`, default 5 s). Each read checks remaining time; if exhausted, results so far are returned with `partial: true`. No silent hang.

## Architecture
```
gpu_manager/
  collector.py   # device discovery, dedup, sysfs + proc reads, budget enforcement
  snapshot.py    # DeviceSnapshot/ProcessRecord dataclasses; render_text(); render_json()
  cli.py         # argparse; --json flag; sets budget; calls collect(); renders; exits
tests/
  fixtures/      # synthetic sysfs trees, proc stubs
  test_status.py # multi-device, dedup, zero occupancy, invalid busy,
                 # missing fields, vanished process, budget exhaustion
```
Python standard library only. No daemon, no network, no writes.

## Non-goals (explicit)
Container enrichment, scheduling, broker, eviction, CRIU, power/clock changes, exact per-process VRAM, service migration, web page.

## Verification
1. Fixture-based unit tests cover all edge cases; no real GPU required.
2. Live read-only smoke check: compare output to raw sysfs values; note delta from live workload activity between reads.
3. Budget-exhaustion path tested; `partial` flag must appear in output.

---

## Draft README paragraph — GPU usage

> **GPU status.** Run `gpu status` for a read-only snapshot of each AMD GPU: device identity (deduplicated by PCI address), total/used/free VRAM in MiB, and a utilisation percentage when the driver reports a value in the valid 0–100 range. Process attribution lists PIDs and names (from `/proc/PID/comm`) that held a DRM handle at the moment of the read; arguments are never inspected. A field shown as *unavailable* or *invalid* was not readable or failed a range check; free VRAM is only reported when total and used were read in the same pass. Collection runs within a fixed time budget and reports partial results honestly if that budget expires. The command takes one snapshot and exits; it does not reserve memory or modify any workload. Container enrichment, scheduling, and eviction are deferred to later issues.
