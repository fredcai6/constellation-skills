## Current planning truth — after boundary w3x-door-binding

**The goal, in the human's words:** make agents use the MCP door instead of the CLI. Cross-platform usability matters but is not this round's problem; being broken on Windows for now is accepted.

**The door is built, correct, and unreachable by any dispatched agent.** It serves properly and returns real engine content, but it binds `SPINE_FILE` at launch and nothing in any shipped launch path sets it, so every dispatch gets the demo example. This — not the Windows launch line — is what has kept adoption at one agent.

**Spines are per task and nest, and this is already real on disk:** `epic-418-followon` → `epic-418-followon/commander-f2` → `epic-418-followon/commander-f2/g2-implement`. Every spine file already carries the `work_id` its identity needs.

**The current wave is one issue, M1:** `run_crew.py` hands each crew `SPINE_FILE` for its own spine and `SPINE_SESSION` as `constellation/<work-id>/<gate>/<role>` — derived from the spine's own `work_id` and the role, with no `attempt-<n>` tail so a respawn resumes rather than force-claims. The engine's lease semantics are not modified; the door's identity guard is not weakened.

**Confirmed ownership doctrine.** A spine belongs to a task, not to an agent or a session; agents are assigned one at a time; the lease keys on the assignment, not the process instance; identity is derived, never typed; conflicts raise the existing refuse-or-force flag rather than being made foolproof.

**Not in this wave, and why.** #555/#553 Windows launch — parked, real, cold review owed. #421 (C) — entry condition restated to "the door is usable by dispatched agents", not merely launchable. #559 — removing the CLI fallback cannot be honest until every dispatch path reaches the door. #423 (E) — out of the epic at the human's direction.

**Unmeasured, and reported as such:** whether role-spine instructions *cause* adoption. Every F2 arm loaded a pre-edit corpus and the accepting arm found the door through `ToolSearch`. Unmeasured is not a negative.
