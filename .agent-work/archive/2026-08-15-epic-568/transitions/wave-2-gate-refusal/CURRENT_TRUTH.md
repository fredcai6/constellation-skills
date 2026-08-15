## Current planning truth — epic #568

Wave 1 is merged: spine origin and worktree isolation are on `main` at `0448275e`.

Wave 2 has landed nothing. #530, #510, and Codex tier routing are implemented, reviewed, and APPROVEd, but each fails its own full Linux suite in a cache-clean worktree while `main` is green, so the gate refuses all three. Each failure is bounded and sits in code the lane already owns: #510's three stale advisory assertions, #530's episode-guard violation, and a stale generated map in all three. The wave is in repair, not advance; launched identities and fixed intent are unchanged.

#441 leaves the active wave until 2026-08-20T06:19Z, fenced by an external Codex quota, holding its own spine and lease.

Two process changes carry forward. Bytecode caches are cleared before any gate measurement, because stale `.pyc` files from the wave-1 worktree relocation can fabricate failures that look like defects. And a launch order's review criteria must state that the reviewer runs the lane's full Linux suite — APPROVE on targeted tests alone is what let three red lanes believe they were finished.

Nonbinding forecast: #441 resumes after the quota lifts, then the ruled lease-lifecycle package. No consumer package beyond the authorized items is in scope.
