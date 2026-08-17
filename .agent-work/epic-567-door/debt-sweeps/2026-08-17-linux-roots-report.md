# Constellation Feedback Sweep — 2026-08-17

10 new candidate(s) (2 recurring, 0 of them across multiple projects), 0 previously collected and still unresolved.

## New — recurring (validated, >= 2 occurrences)

### powershell-heredoc-use-here-string (constellation) (716eccf60f43)
- occurrences: 3 across 1 project(s): story_time
- observed: On Windows, crews repeatedly hit silent failures using bash heredoc for commit messages / PR bodies.
- proposal: the launch-order / commander templates should prescribe `@'...'@` PowerShell here-strings on Windows

### engine-session-id-flag-position-still-unfixed (740c063ddad5)
- occurrences: 2 across 1 project(s): baseball_coaster
- observed: -

## New — single-project (scope tag is a claim, verify)

### worktree-isolation-not-guaranteed (constellation) (6bb389f5baad)
- occurrences: 1 across 1 project(s): story_time
- observed: Agent-tool `isolation:"worktree"` did not create separate working directories on this harness — three parallel subagents shared the main checkout and collided on `git checkout -b` (one commit landed on a sibling's branch).
- proposal: make Agent worktree isolation real (distinct dirs), or have Admiral/dispatch doctrine hard-require serialized worktree commanders plus a `git worktree list` distinct-path precheck before any parallel dispatch

### commander-spine-mismatch-for-autonomous-dispatch (constellation) — caught at audit, not during the run (eac9d27ffad8)
- occurrences: 1 across 1 project(s): story_time
- observed: `constellation-commander` is a human-facing scaffold: its `understand` step's interrogator "must reach the human", it pauses for `user-decision` checkpoints, and it launches nested implementer/reviewer crews via `run_crew.py`. None of that fits an autonomous subagent under a run-to-completion Admiral contract on a harness where subagents cannot reach the human. The Admiral right-sized each Commander to a plan-driven single-agent implementer.
- proposal: the commander skill (or Admiral dispatch guidance) should document a sanctioned autonomous mode and when to use it, rather than leaving every Admiral to re-derive the right-sizing

### admiral-verifies-from-artifacts-on-commander-idle (constellation/harness) — NEW (ca39203530c9)
- occurrences: 1 across 1 project(s): story_time
- observed: An Agent-tool commander sometimes ends with only an `idle_notification` (`idleReason: available`) and never delivers its final verdict text to the dispatching Admiral, even when explicitly instructed to "return your verdict in your final message." Hit 2 of 4 reporting commanders this run (Slices 2/#20, 4/#22); work was complete each time (artifacts were ground truth), so no impact — but a future Admiral could hang waiting on a verdict that never arrives.
- proposal: if the Agent harness is dropping a subagent's final message on idle, fix delivery; otherwise the Admiral/dispatch doctrine should codify "verify from the artifact set (branch/commit/PR/files) + clean-room on commander idle; never block on a verdict message."

### engine-could-auto-heartbeat-on-mutating-verbs (constellation/engine) — NEW (6833b64e2340)
- occurrences: 1 across 1 project(s): story_time
- observed: On a long autonomous Admiral run, the engine session lease went stale (>1800s since last heartbeat) at the execute→closeout boundary and refused the next mutating verb until an idempotent same-id re-claim. Recovery was free, but the staleness was discovered reactively at a gate.
- proposal: the checklist engine could refresh `last_heartbeat` automatically on any successful mutating verb by the lease-holding session (start/advance/attest/attach), so an actively-working session never goes stale; reserve explicit `heartbeat` for genuinely idle waits. Until then, Admiral doctrine carries operator discipline

### crew-resume-async-armed-poll-insufficient (ed02254a1af6)
- occurrences: 1 across 1 project(s): baseball_coaster
- observed: -

### amend-op-field-name-is-op-not-kind (8e502a34f822)
- occurrences: 1 across 1 project(s): baseball_coaster
- observed: -

### run-crew-verify-slash-workid — 1st export (recurrence confirmed, no new facet) (501026ab656b)
- occurrences: 1 across 1 project(s): baseball_coaster
- observed: -

### delegated-latitude-vs-automode-classifier — counter-evidence to the "still open" read (53a9f90e874e)
- occurrences: 1 across 1 project(s): baseball_coaster
- observed: -

