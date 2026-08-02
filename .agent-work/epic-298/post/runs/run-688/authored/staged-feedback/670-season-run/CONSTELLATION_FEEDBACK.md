# Constellation feedback export — 670-season-run (2026-07-27)

## Recurrence: git-bash PID-liveness is unreliable for detached processes
- **Lesson:** crew-idle-strands-deliverable
- **Recurrence (670):** a completion watcher that used git-bash `tasklist /FI "PID eq <pid>"` to check liveness of an OS-detached process (Start-Process -WindowStyle Hidden) returned "GONE" for a process that PowerShell `Get-Process` confirmed ALIVE with accumulating CPU. This cost one false-"died" watcher cycle before re-arming with a PowerShell-liveness watcher. The existing lesson already says "verify liveness via PowerShell `Get-Process` CPU accumulation (NOT git-bash `ps`)"; this run confirms the same trap bites `tasklist` in git-bash too, not only `ps`. Worth folding "tasklist in git-bash" explicitly into the lesson's unreliable-liveness list, and worth a doctrine note that detached-process completion watchers should key liveness on PowerShell Get-Process (or the result-artifact appearing), never a git-bash process-table query.

No other constellation-level exports this run. Project-level lesson (season-batch per-round fault isolation) is staged in lessons-delta.json for the Admiral to apply to the project playbook.
