# Problem statement — issue #419, epic-418 workstream A

Delegated Commander `cmdr-419-governor-identity`. Principal: the frozen launch order
`.agent-work/epic-418/launch-orders/A-419.md` + `_COMMON.md` (epic-418 Admiral). No reachable human.

## The ask, reconciled

Sources read: `gh issue view 419`; the spec of record
`.agent-work/archive/2026-08-03-explore-post-phase1/DESIGN_SPEC.md` §A; the launch order.

**No conflict between the issue and the spec.** The issue is a faithful compression of §A. Where the
issue is terser (it does not restate the "reading's consumer is the live trip mechanic" rationale), the
spec supplies it, and the spec's done-condition — *a trip fires from a per-agent reading on a live run* —
is stated identically in both. Nothing to adjudicate.

## What is broken today (verified in code, not from the issue's framing)

`scripts/hooks/spine_rail.py:308` keys `.agent-work/.spine-rail-binding.json` on the harness
`session_id` alone. Agent-tool subagents **share the parent's `session_id`**, so every crew `claim`
adds another entry under one key. `scripts/hooks/gauge_writer_hook.py:439` resolves the gauge path
from that key, and at `len(gauge_paths) > 1` it writes **nothing** (`ambiguous-binding`) — correctly,
because it cannot tell whose reading it holds.

Measured live in the main checkout at the moment of this run: **6 session keys, 54 bindings**, one
session holding **36**, and the session dispatching this very epic holding **5**. So the governor is
blind for exactly the runs that matter — every wave an orchestrator dispatches.

Second, independent defect: even with the binding fixed, the reading itself would be wrong.
`find_latest_usage` (`gauge_writer_hook.py:206`) *skips* `isSidechain` lines. **Every line in a
subagent's own transcript is `isSidechain: true`** — so the filter must invert for a subagent, and
`docs/GAUGE_WRITER_HOOK.md`'s field table is wrong in a load-bearing place today.

## The pre-build probe — the recorded branch point

Run before anything was built, per `decision:a-probe-branch`. A dump hook was wired into a **real**
headless `claude -p` session (`--settings`, `PostToolUse` matcher `*`) which ran a parent Bash call,
dispatched **two concurrent subagents** each running a distinct Bash command, then ran a second parent
Bash call. Six real payloads captured. Harness **2.1.222**.

**Result:**

| fact | observed |
|---|---|
| `transcript_path` on a **subagent's** tool call | the **parent's** transcript, always |
| `agent_id` on a subagent's tool call | **present** — `a8f0a946eaaa2fe6c`, `adb52b4ec6c7dbd40`, distinct per agent |
| `agent_type` on a subagent's tool call | present (`general-purpose`) |
| `agent_id` on a **parent** tool call | **absent** — the field does not appear at all |
| `agent_id` on the parent's own `Agent`-tool dispatch call | absent (the dispatch is the parent's act) |
| derived path `<slug>/<session_id>/subagents/agent-<agent_id>.jsonl` | **exists**, one per agent, every line `isSidechain: true`, each carrying its own `agentId` equal to the payload's `agent_id` |

**Branch selected: RE-KEY. The matcher does not ship.**

This needs stating precisely, because the outcome is not exactly either shape the spec anticipated.
By the letter of the taxonomy this is the *second* branch — the payload carries the parent's path. But
the taxonomy's two conditions were proxies for one question: **does the payload identify the acting
agent?** It does, directly, via `agent_id`. The prototype's ~250-line `agent_identity.py` exists only
to *discover* an identity the payload now hands over for free, and every hazard that module was built
around — the verbatim-dispatch prompt contamination, the identical-command race — is unreachable when
the id comes from the harness rather than from matching. Shipping the matcher here would be building a
search for a value already in the argument list.

So: the branch point resolves to the **cheaper mechanism the spec already blessed**, for a better
reason than either branch anticipated. This is not the out-of-taxonomy "neither shape" case (a shape
*is* present) and it is not a third invented mechanism (re-key is branch one). It **is** a fact the
frozen order did not have, so it is floated to the Admiral in `RETURN.md` rather than absorbed silently.

Consequences that follow from the payload carrying `agent_id`:

- Identity is O(1) from the payload — no transcript scan to resolve *who*, so the 100ms
  identity-resolution budget is not in danger and the identical-command race cannot arise
  (the issue's own words: "if the re-key branch ships, the race cannot arise").
- The subagent's own transcript is *derived*, not searched:
  `Path(transcript_path).with_suffix("") / "subagents" / f"agent-{agent_id}.jsonl"`.
- Fail-closed has a sharp definition: `agent_id` present but its derived transcript absent ⇒ write
  nothing. No fallback to the parent's transcript — that is precisely the misattribution #202/#261
  already ruled against.

## What must be true when this is done

1. A subagent's binding lives under `session_id#agent_id`; the parent keeps its bare `session_id`.
2. Each agent's gauge reading comes from **its own** transcript, with the sidechain filter inverted.
3. An unresolved identity binds nothing and writes nothing.
4. `docs/GAUGE_WRITER_HOOK.md` is corrected (sidechain inversion + `agent_id`/`agent_type` in the
   field table).
5. The ~54 stale bare-key bindings are swept (dry-run + recorded before-state, then real, then the
   sweeper is deleted).
6. **A trip fires from a per-agent reading on a live run.** Not "readings appear". Observed.

## Validation constraint that shapes the whole plan

`CLAUDE_PROJECT_DIR` is fixed at session launch (#269), so an agent dispatched into this worktree
still runs the **main checkout's** hook code. This change cannot be validated from inside the worktree
that contains it. The vehicle is a fresh headless `claude -p` whose `--settings` names **this
worktree's** hook by absolute path — already proven to work end to end by the probe above (the hook
fired, subagents dispatched, real payloads landed). No fixture may hand-inject `agent_id`; the point
is to prove the harness delivers it.

## Out of scope (issue's own words, and the Admiral's scope ruling)

Metrics methodology; any consumer beyond the live trip mechanic; the parent-orchestrator
multi-binding coverage gap that survives this fix (an orchestrator legitimately holding N spines is
still ambiguous — that is #202/#261's known cost, not this issue's).
