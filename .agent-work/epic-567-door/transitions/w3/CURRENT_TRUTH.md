## Current planning truth — epic 567, boundary w3

### Intent

One interface for agents: the MCP door. The CLI becomes an operator and debug path only. The outcome that must not be violated: **this epic reduces complexity by removing a redundant path.** Judge a change by whether it reduces work on agents by moving it into mechanisms.

### Measured state (`de8ef4ea`)

| Claim | State |
|---|---|
| full suite, Linux, clean detached worktree | **3374 passed, 0 failed** (3191 at epic start) |
| `CLI fallback` in `skills/`, `specs/`, tracked overlay | **zero**, guarded by a 718-line regrowth test |
| a dispatched crew driving its own spine through the door | **yes** — five lanes did, and a cartographer dispatched at closeout used no CLI at any gate |
| a role driving its **own authored plan** through the door | **no** — the remaining gap, filed as #634 |
| a launcher taking declared rather than machine-local defaults | **no** — #619 and #633 |

### Current wave (launched at this boundary)

- **J** — #619 + #633. A launcher takes declared defaults, not machine-local ones: no probed interpreter in a tracked file, no touching the calling repo, and a crew model resolved from a per-role, per-harness table with an allowed set and a recorded reason. Sonnet.
- **K** — #634. One spine per agent: frozen bookends, mutable middle, for every planning role. Opus, design-it-twice, convergence human-only, self-hosting proof against a copy before merge.

### Nonbinding forecast

Closeout re-runs after wave 3 — its hygiene half genuinely must, since new branches and worktrees exist. #559 and #565 close once a role's own plan is door-reachable.

### Standing constraints

No lane files an issue. No lane promotes doctrine into `docs/agents/*`. No lane regenerates `map/INDEX.md` (#544). No design work goes to a fork. **Every dispatch and every crew passes `--model` explicitly — the default is wrong until #633 lands.** The merge gate is the full suite green on Linux in a clean detached worktree of the branch, and `main` is re-verified after each merge.

### Open uncertainty

What `spine_advance --from_child` was built for. Whether a gated spine can grow its middle without breaking `why_trail`, the trip ledger or postcondition evaluation. Whether an agent can detect its own harness or must be told.
