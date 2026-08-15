## Current planning truth — epic #568

Wave 1 substrate and two wave-2 lanes are on `main`: spine origin and worktree isolation (`0448275e`), Codex crew tier/reasoning metadata (`e0c998b6`), and spine-rail binding derived from the spine path (`c23c3d0f`).

#510 is open under a changed approach. It was cut as a pending-gate handoff text fix; measurement found the shipped advisory instructs a `start` the engine refuses, and the compliance ledger then penalises the agent for obeying. The human ruled to make the engine permit that start, so #510 is now an engine-core implementation holding the serialized `checklist_engine.py` lane and closes on a red/green over engine behavior, not over prose.

#441 stays fenced by an external Codex quota until 2026-08-20T06:19Z, holding its own spine and lease. Lease lifecycle remains ruled but deferred.

Two infrastructure defects are filed and unimplemented: bytecode caches from the wave-1 worktree relocation can fabricate failures, and crew dispatch does not bind the child's MCP spine door, making the MCP-only constraint unenforceable. Neither is authorized work under the current contract, which expires when the wave-2 items are dispositioned.
