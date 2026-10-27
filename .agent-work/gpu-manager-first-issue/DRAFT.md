# Draft first issue: read-only GPU status

Status: proposed for joint review; not filed or dispatched.

## Intent

Give the human and agents a useful snapshot of GPU occupancy while existing workloads
keep running. This starts the GPU manager's observation layer without introducing
ownership, scheduling, or lifecycle control.

Source intent: `/home/tommy/projects/GPU_MANAGER_HANDOFF.md`. The human chose a
read-only first slice because other GPU users are active, and authorized Sonnet for
real work. The handoff asks for a short design and human review before implementation.

## Current behavior and evidence

The handoff reports no GPU manager implementation. On 2026-10-22, filesystem checks
found neither `~/projects/gpu-manager` nor `~/projects/gpu-box`. GPU services remain
configured in journal-system's Compose file at revision 1540c72.

Read-only observation on this workstation found:

- Docker is available on PATH; amd-smi and rocm-smi are not on this shell's PATH.
- Linux DRM exposes two AMD devices, with approximately 32 GiB and 2 GiB VRAM.
- Device-level total/used VRAM and busy counters are readable through sysfs.
- One busy counter returned 107. The meaning/validity of that reading has not been
  investigated. Do not silently treat every returned number as a valid percentage.

These are local observations, not durable claims about future machine state. No
model was loaded, GPU workload launched, or running service changed for this inspection.

## Proposed behavior

`gpu status` takes one bounded, read-only snapshot and prints:

- Discovered AMD GPU identity, using stable device information where available;
  card/render node names are observations rather than fixed configuration.
- Total, used, and free VRAM, with clear units.
- Utilization when supported and valid; otherwise an explicit unavailable/invalid
  indication. Do not clamp bad data into a plausible measurement.
- Best-effort workload attribution from readable process/device information. Label
  identified PIDs and names as observed device users, not proof of active computation.
  Container association is optional enrichment when it can be established read-only.
- Collection gaps such as permission denial, processes disappearing, unavailable
  metrics, or unavailable Docker. Incomplete attribution must not look like an idle GPU.

`gpu status --json` renders the same snapshot for agents. Both renderings should
distinguish zero from unavailable and partial discovery from an empty complete result.
The command makes no claim that free memory is a reservation or that work is safe to launch.

## Scope boundary

No model loading, benchmarks, inference requests, GPU compute tests, driver changes,
root access, power/clock changes, container lifecycle calls, pause/resume, signals to
workloads, service migration, scheduling, job registry, daemon, proxy, or webpage.

Only read-only observation is allowed on the live machine. Tests should use fixtures
or controlled temporary filesystem/process data. Discovery should finish promptly
even if an optional source hangs or is unavailable.

## Deliverables and verification

1. A short design for this slice and a small draft GPU-usage README section. Keep
   future broker/priority questions explicitly deferred. Human review precedes code.
2. After design approval, a small `gpu-manager` repository with the status command,
   focused tests, and local usage instructions. Python with minimal dependencies is
   the proposed starting point, not an approved architectural commitment.
3. Tests covering multiple devices, valid zero occupancy, unavailable/invalid readings,
   partial process visibility, disappearing processes/devices, and optional container
   discovery being unavailable. No real GPU computation is needed for tests.
4. A read-only live check comparing reported device memory with the source readings,
   allowing for the fact that a live workload changes between reads. Record the
   limits of workload attribution rather than inventing completeness.
5. Separate Pi Implementer and Reviewer results, including commands run, actual
   evidence, changed files, and observed limits. Sonnet is allowed; use bounded calls.

## Decisions to settle before dispatch

- Confirm best-effort workload attribution is enough for this first issue. Exact
  per-process VRAM accounting and complete container attribution would expand it.
- Confirm the proposed local repository name `gpu-manager` and Python starting point,
  or leave these as routine implementation choices within the approved small design.

## Proposed handoff sequence

First send the Pi Commander a design-only task scoped to this issue. It returns the
short design for human review. Then authorize implementation of the agreed slice in
the same project. Do not send the whole historical handoff as authority to build the
broker or alter running GPU workloads.
