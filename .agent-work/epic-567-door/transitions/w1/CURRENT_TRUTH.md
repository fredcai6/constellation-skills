## Current planning truth — epic 567, boundary w1

### Intent

One interface for agents: the MCP door. The CLI becomes an operator and debug path only. The outcome that must not be violated is that this epic **reduces paths rather than adding mechanism** — every lane ends net-mechanism-negative.

### Measured starting point (`600de02`, 2026-08-16)

| Claim | State |
|---|---|
| CLI-fallback clauses | 15, across 11 files |
| live `<engine>` tokens | 11, across 7 files — the epic body's 9 was stale |
| door vocabulary in `specs/*.spine.toml` | zero; only `implementer` and `reviewer` specs exist |
| verb gap | closed — 11 tools cover every engine verb |
| a role agent reaching its **own** spine through the door | impossible |

### Current wave (launched at this boundary)

- **A** — per-dispatch spine identity: the door reaches the caller's own spine (#559 anchor, plus the bind-own-spine gap, plus #613's `save()`-atomicity half). Opus. Design-it-twice; convergence is human-only.
- **B** — ExternalBackend refuses a spineless success (#432). Sonnet.
- **C** — the rail and HARD refusal read to a cold agent (#442), and the stop-hook-versus-context-trip authority is settled (#595). Sonnet.
- **G** — one-verb mechanical closeout behind the door (#574), and archiving releases the lease (#552). Sonnet.

### Nonbinding forecast

- **D** — the doctrine sweep: delete 15 clauses and 11 tokens, sunset the workbench teaching half, rehome its templates, land the regrowth guard, carry #561/#596/#526. Entry condition: lane A has landed, or has returned an honest null that changes the premise.
- **E** — door rejections captured as episode friction (#541).
- **F** — the spec revealed through the spine rather than the launch order (#535).
- **Closeout disposition** — every accumulated triage candidate paired onto an open issue or recorded as an episode; none minted as a new issue.

### Standing constraints

No lane files an issue during the run. No lane promotes an observation into `docs/agents/*`. Engine and hook changes are validated in a fresh process with explicit paths — an in-session observation is not evidence. Lane A proves the edited engine drives the live spine before merge: read-only `current` on the live spine, mutating verb against a **copy**.

### Open uncertainty

Whether per-dispatch spine identity can be had without adding more mechanism than the sweep removes. Wave 1 exists to settle it; lane A's comparison lands at the W1 checkpoint, where the contract expires.
