# Commander notes — 567-e

## Understand (reconciled against LAUNCH_ORDER, no reachable human)

**Mission (#541):** a door refusal currently vanishes -- it never lands anywhere a later
reader can find it. Make it land in the run's episode record instead.

**Baseline reconciliation (code vs. order's framing).** The order frames this as
"the friction currently vanishes." Reading `scripts/mcp_spine_server.py` directly (map
degraded, packet absent -- logged at context) shows this is *half* true:

- The door already has `_log_rejection()` / `_rejectionlog()`, which appends one JSONL
  line per **door-own** rejection (unknown tool, missing arg, unbound door, and --
  since issue #567 -- the two `_spine_bind` containment refusals) to
  `mcp_rejections.jsonl` **beside the spine**. This already exists; it is not the gap.
- That destination is a local telemetry side-channel, resolved via `_telemetry_path()`,
  not `episodes/`. It is not git-tracked, not durable past worktree teardown, and never
  goes through `apply_episode_delta.py`. So the actual gap matches the order's framing
  at the layer that matters: a refusal is discoverable *during* the run (if someone
  greps the sidecar) but does not survive as project history the way an episode does.
- Engine-native refusals (a postcondition check failing, `claim` refused because another
  session holds the lease, etc.) reach the caller through `run_engine()` -> `as_result()`
  and are logged only in the plain call log (`mcp_calls.jsonl`), not `_log_rejection` at
  all -- they carry no `rejection_class`. So today there are two refusal populations, one
  partially captured (door-own) and one not captured as "a rejection" at all (engine-native),
  and neither reaches `episodes/`.

**The real gap, stated precisely:** wire a path from "a refusal happened at the door" to
"an episode records it," durable in `episodes/` via `apply_episode_delta.py
--store-root episodes`, provable by triggering a refusal in a fresh process and reading
it back with `query_episodes.py` / `verify_episode_captured.py`.

**Load-bearing constraint found in `docs/EPISODE_STORE.md` section 10, that the order does
not name:** `apply_episode_delta.py`'s `create` op validates that all five agent-supplied
assertions (`task-intent`, `expected-behavior`, `observed-behavior`, `impact-cost`,
`workaround`) are non-empty, and the doc is explicit that **nothing should auto-create an
episode**, because "an auto-created one could only carry fabricated assertions." A naive
design -- the door itself shells out to `apply_episode_delta.py create` on every refusal,
synthesizing prose for all five fields -- collides head-on with this standing doctrine.

This is why `decision:capture-filter-is-yours` exists in the order. Resolution, mine to
make and stated here before building it: every synthesized field must be a **literal
derivation from data the refusal itself already produced**, never invented narrative.
Concretely: `observed-behavior` is the refusal's own verbatim message; `task-intent` is
the tool name and arguments actually supplied; `workaround` quotes the refusal's own
named escape hatch (every refusal in this module already ends with one --
`_HOW_TO_BIND`, `_THE_CLI_IS_PER_CALL`, etc.); `impact-cost` is the mechanical fact that
the call did not proceed. Nothing is guessed about intent or root cause -- that is what
keeps this a mechanical capture rather than a fabricated one. If evidence at plan/execute
time shows this reasoning does not hold up, it floats to the Admiral rather than being
pushed through.

**Second item, inherited from lane D1's sweep, same file:** replace the CLI-recommending
refusal-tail `_THE_CLI_IS_PER_CALL` ("...or use the CLI, which is per-call by
construction.") used at the two `_spine_bind` containment refusal sites
(`scripts/mcp_spine_server.py:1396,1437`). Confirmed while reading: the module's own
docstring already records that issue #559 overturned any "leave it on the CLI" escape
clause fleet-wide ("the agents should not know about the cli. period. anything that we
can only do via the cli is a defect") -- so this fix is squarely consistent with existing,
already-ratified doctrine in this same file, not a new call.

**Decisions inherited as fixed, not reopened:** no-inode-containment (hardlink hole),
no-net-deletion-rule, no-issue-filing-mid-run, no-doctrine-promotion, records-are-not-
instruction, map-index-is-admiral-owned, no-fork-for-design.

**Local unknowns from the order, addressed here:**
- nested-work-id pair (`apply_episode_delta.py` / `verify_episode_captured.py`) satisfiable
  from inside the server process -- yes in principle (it's a subprocess call with
  `--store-root episodes`), to be proven at execute.
- a refusal with no bound spine has no work-id to attribute to -- true, and this bounds the
  filter (see capture-filter, to be finalized after counting a real run's refusals at plan/
  execute): an unbound-door refusal cannot be captured as a *spine-attributed* episode
  because there is no run id. Candidates: skip capture for the unbound case (it already has
  nowhere durable to attribute to), or attribute it to a fixed sentinel run id. Leaning
  toward skip-and-say-so, decided at plan.
