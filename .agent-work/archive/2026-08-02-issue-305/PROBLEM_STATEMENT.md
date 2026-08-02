# Problem statement — issue #305, mechanical episode capture from engine state

Delegated run under `LAUNCH_ORDER-305.md` (frozen). No reachable human; the order is
ratified intent. Reconciled here against the code, per
`lesson:verify-launch-order-claims-against-code` (6 confirms).

## Baseline verified against code before planning

**The order's central claim HOLDS.** `grep -rn "context_manifest" skills/` returns
nothing (exit 0, no output) and `produce()` at `scripts/context_manifest.py:434` has
zero callers repo-wide. #300's AC1 — "a manifest is produced on every deterministic
assembly" — is therefore true definitionally, over zero assemblies. Confirmed, not
assumed.

**The baseline EXCEEDS the order's framing**, in a way that changes what this issue
is. The order describes #305 as wiring the manifest producer. It does not mention that
the episode-capture half is already substantially built:

- `scripts/apply_episode_delta.py` (63K) — the validated writer. `_validate_create`
  already enforces a hard allowlist over the mechanical bin, requires every mechanical
  scalar, and **already refuses a caller-supplied `id`** with the reason
  *"the writer assigns it (EPISODE_STORE.md section 2, zero agent effort)"*.
- `scripts/query_episodes.py` (28K) — retrieval. `_FIELD_READERS` already enumerates
  the mechanical field group exactly: `id`, `run`, `project`, `role`, `spine-step`,
  `context-manifest-ref`, `refusals`, `reopens`, `rework-count`, `failed-commands`,
  `artifact-ref`.

So #305 is not "build capture". It is **"wire capture from engine state into an
existing validated writer, and make manifest emission a byproduct of assembly."** The
field group is not mine to design; it is a frozen contract I must fill from engine
state alone.

**#321 is already fixed at my own base commit.** The order says "the episode store
validates ids it LISTS but not ids it is HANDED. Fix it or work around it deliberately."
My base `967493c` IS the fix: `#309: adversarial coherence sweep + #321 fix
(id-handed-vs-listed validation gap) (#350)`. `resolve_episode_path()` now opens with
`if not ID_RE.fullmatch(episode_id): return None`, with the `..` path-traversal case
named in its docstring. Disposition: **no action needed, inherited fixed**; verified at
source, not taken on the order's word. The order's framing was written before #350
merged.

## What is mechanically capturable, verified in source

Verified in the **repo** engine and re-verified in the **served** engine
(`~/.claude/skills/constellation-commander/scripts/checklist_engine.py`), which is a
different binary (128,889 vs 120,146 bytes) per #344.

| Field | Engine-state source | Status |
|---|---|---|
| `run` / `work_id` | `checklist["work_id"]` | mechanical |
| `project` | repo root basename | mechanical |
| `role` | spine identity | mechanical |
| `spine-step` | `active_id(cl)` — the engine's own selector | mechanical |
| `context-manifest-ref` | the manifest emitted at assembly (below) | mechanical **once wired** |
| `rework-count` | `task["rework_count"]`, set by `reopen` (engine:1851) | mechanical |
| `reopens` | successful `reopen` entries in the journal sidecar | mechanical |
| `failed-commands` | evidence `type: command-output` with `payload.exit != 0` | mechanical |
| `artifact-ref` | evidence payload artifact paths | mechanical |
| **`refusals`** | **nothing** | **NOT mechanical — see below** |

### The one gap: `refusals` has no engine-state representation

This is the sharpest finding of the run and the one the order's Honest-Null Clause
anticipated.

A refusal raises `EngineError`. `main()` catches it at `checklist_engine.py:2556`,
and — importantly — **does persist `cl`** (line 2558-2559: *"state may carry legitimate
mutations (command results, escalation); persist unless read-only/dry-run"*). But
nothing in that path records **that a refusal happened**. It prints `REFUSED:` to
stderr and returns 1.

The journal sidecar cannot cover it either: it is documented and implemented as
*"one line per SUCCESSFUL mutating verb"* (engine:2469, and the `append_journal_entry`
call sits inside the success branch at line 2575-2583, after the `return 1`).

So `refusals` is, today, **secretly agent-dependent**: the only way it gets a value is
an agent remembering how many times it was refused. That is exactly the class
`decision:zero-agent-effort-is-literal` forbids.

Two engine facts confirmed in the served binary, matching what the order relayed from
commander-304 (both verified independently here, not taken on report):
- `_run_check_command` passes **no `cwd=`** — `subprocess.run([shell, "-c", command])`,
  engine:713.
- Command-postcondition **stdout is captured and discarded**: `_check_condition`
  records only `{cmd, exit, shell}` (engine:755). The exit code is the only signal that
  reaches the spine.

The second fact cuts **for** me: because the evidence item is appended *before* the
refusal raises, and `main()` persists on the error path, **a failed check command is
already durably recorded**. `failed-commands` is mechanical today. `refusals` is not.

## Manifest as a byproduct of assembly

The order's sharpest instruction: *the manifest must become a byproduct of assembly,
not a separate act an agent can forget to perform.*

**Assembly is `current`.** `current` is the moment the engine hands the agent the
step's briefing — `render_human(state(cl))` — and `context_refs` already sits on the
task object that briefing is rendered from. Emitting the manifest there means it is
produced by the act of an agent asking what to do, which no agent can skip without
also skipping the instruction it needs.

This is compatible with `current` being read-only for spine state: `main()` deliberately
does not `save(path, cl)` for `current`, but the manifest is a **separate file**
(`<agent_work_root>/<work-id>/context/<step>.json`, `manifest_path()`), so emitting it
mutates no engine-owned state.

The alternative — a capture path that *calls* `produce()` — is exactly the shape the
pre-ruling `decision:manifest-is-a-byproduct` forbids, and exactly the shape that
leaves AC1 vacuous.

## `run.dirty` removal (#327)

Verified: the defect is real and self-caused. `default_repo_state` →
`repo_revision()` runs `git status --porcelain`, which is repo-wide. The producer writes
its manifest **into `.agent-work/`**, and `#326` (`c2e16a8`) made `.agent-work/` tracked.
So producing a manifest dirties the tree and the flag reads its own side effect —
permanently true. Removal, not repair, per `decision:drop-run-dirty`. Per-declared-file
dirtiness stays derivable from content alone (each row's `rev` vs
`git rev-parse <commit>:<path>`), which is strictly better: it is scoped to the declared
set, where the repo-wide flag never was.

## The negative control — the check most at risk

Acceptance: *a run where the agent records nothing must still yield the full mechanical
field group.*

This is the shape that has failed five times in this epic (#337): it passes by never
testing anything. Empty-vs-empty and missing-vs-missing both score green on a naive
check. **Before trusting any green, the control is run against a deliberately incomplete
capture and confirmed RED.** If it legitimately fails, that is the deliverable, not a
run failure — it names which fields are secretly agent-dependent. On today's evidence it
**will** name `refusals` unless the engine is made to record them.

## Scope boundary

Capture is complete for **engine-driven runs** and empty for everything else. An agent
that never drives the engine leaves no engine state to capture from. This is stated
plainly in the shipped record rather than left for a reader to assume the store sees all
work. (The #299 zero-skill-invocation measurement is a property of the measurement rig,
which launched generic agents — not of production, where a Commander run drives the
engine by construction. Premise sound; not re-litigated here.)

## Floats to the Admiral

One, raised before planning: **whether making the engine record refusals is inside this
deliverable, or a scope change.** See the return. Everything else proceeds under the
order.
