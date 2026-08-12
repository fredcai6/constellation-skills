## Current planning truth — after wave 1 (advance)

**F (#424) is complete.** Six done-conditions, six verdicts, none unmeasured. `scripts/mcp_spine_server.py` and three test files land on PR #533, green and mergeable. `gen_mcp_config.py` was removed on evidence and tombstoned. The measurement is honest about its own mechanism: cost fell, but malformed calls were zero in both arms, so the door removed the need to read a manual rather than absorbing fumbles.

**F2 is the current wave, and it is new scope rather than a repair.** F met what it was scoped against; the owner added these after seeing the result. Two issues, one wave:

- **#542 — adoption.** Nothing drives through the door today. Agents must default to it, measured from a real dispatch's own call record. The CLI stays: a hard constraint of this epic, recorded so adoption is never read as license to remove it.
- **#541 — friction capture.** Behind a typed tool, a schema rejection is absorbed by the client and nobody learns the verb was confusing. The door converts a diagnosable defect into a silent correction, which is the failure shape this epic exists to catch. The episode format already carries `refusals`, `reopens`, `rework-count` and `failed-commands`, so this contributes to the store that exists rather than inventing one.

**C (#421) does not start until F2 completes.** Its entry condition is that agents run the spine through the door rather than the CLI. C relocates gate instructions and the gate imperative rides tool results verbatim, so C must write against a settled substrate.

**E (#423) has left this epic** at the owner's direction and is handled separately.

**The identity question F2 must decide deliberately.** The harness shares one process between a parent and its subagent, and we bind identity to that process — `mcp_spine_server.py:113-115` reads the spine and session from the environment as module constants at import, and no tool takes a spine path argument. DC3's PASS covers the environment seam and its own test class explicitly scopes out the harness's in-process reuse as unobservable from a subprocess test. Moving identity per-call would fix the composition but discard the isolation env-binding buys. F2 chooses, and records which property it gives up.

**Blocking F2:** three tools assume a work-id contains no `/`, and one of the three pairs — `apply_episode_delta.py` and `verify_episode_captured.py` — is mutually unsatisfiable, which is the path #541's capture must write through. Already routed to a side implementer.
