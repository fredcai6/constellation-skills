# Prototype Result: `per-agent identity for the context governor (exc-6)`

## Question
Can the context governor track a dispatched subagent's engine work under the subagent's OWN identity — the prototype agent creates its own subagents whose activity is gauged separately (not accumulated onto the parent's binding), with terminal work releasing its binding — or is the fix pernicious as suspected?

## Verdict
`answered-yes`

**Answer:** Yes, and it is not pernicious. The fix does not need a new identity to be invented — one already exists and the governor is simply not keyed on it. As of Claude Code **2.1.220** the harness writes every subagent its **own transcript file** at
`~/.claude/projects/<slug>/<session_id>/subagents/agent-<agentId>.jsonl`,
and every line in it carries a distinct top-level **`agentId`** alongside the shared `sessionId`. Keying the binding on `<session_id>#<agentId>` instead of the bare `session_id` makes separation fall straight out: three live agents each held exactly one binding, each got a gauge reading computed from its own transcript, the parent's binding never accumulated, and a terminal agent's release removed its key entirely.

Demonstrated live in the worktree, with real dispatched subagents (`general-purpose`, model `sonnet`) driving the calls:

| agent | identity key (suffix) | bindings held | gauge written to | reading |
|---|---|---|---|---|
| me (parent of the crew) | `#aexc-6-governor-prototype-e73c…` | 1, throughout | `.agent-work/proto-exc6-self/gauge.json` | `claude-opus-5`, fill `0.3648` |
| crew gamma (non-terminal) | `#ae74482d2c869d84c` | 1 | `.agent-work/proto-gamma/gauge.json` | `claude-sonnet-5`, fill `0.1656` → `0.2038` |
| crew delta (terminal) | `#a3a53e12ab1a7d000` | 1 → **0 after release** | `.agent-work/proto-delta/gauge.json` | `claude-sonnet-5`, fill `0.1658` |

Every clause of the stop condition is covered by that table: separate bindings, a clean parent, per-agent gauge files with each agent's **own model and own fill** (opus vs sonnet, and gamma's reading advancing `0.1656 → 0.2038` after it burned context), and a terminal agent's key disappearing from the binding file while the other two survived.

For contrast, the live failure in the main checkout, measured at the start of this run: **47 bindings across 3 session keys, 36 of them under a single session id.** Under today's rule every one of those 36 is "ambiguous" and the gauge writes nothing — which is exactly the zero-readings symptom in #383.

## What was tested AND what was NOT tested

- **Tested:**
  - **The premise of #383, confirmed:** subagents do share the parent's `sessionId` (env `CLAUDE_CODE_SESSION_ID` is identical for parent and child; `CLAUDE_CODE_CHILD_SESSION=1` is the only env-level hint, and it is a boolean, not an identity).
  - **Timing linchpin:** a tool call's own command string is persisted to the acting agent's transcript **before** the tool executes. Probed with a nonce mid-command: the nonce was present in my own subagent transcript and absent from the parent's, while the command was still running. This is what lets a plain subprocess self-identify with no hook at all.
  - **Variant 1 — env only:** resolves the parent correctly, cannot resolve any child. No per-agent id is exported to the subprocess environment. Failed as a discriminator, by design not by accident.
  - **Variant 2a — naive argv substring search:** **failed live, and instructively.** Both crew agents came back `UNRESOLVED`. Cause, confirmed by nonce grep: a dispatching agent writes the child's command **verbatim** into the Agent-tool prompt, so the parent's transcript contains the probe too, and the search sees two hits. Since verbatim dispatch is precisely the Constellation pattern, this variant is contaminated by construction.
  - **Variant 2b — structured match on a Bash `tool_use.input.command`:** works. The dispatcher's copy lives in an Agent/Task `tool_use.prompt`, never in a Bash `tool_use.command`, so matching the structured field cleanly separates who *ran* the command from who merely *talked about* running it. All three agents resolved; re-running the same call under variant `a` on the same agent still refused, so the two variants were compared on identical input.
  - **Fail-closed behaviour:** every unresolved case refused to bind and refused to write a gauge, rather than guessing. No wrong record was ever produced.
  - **Nested dispatch:** subagents spawned *by* a subagent get their own transcript in the *same* flat `subagents/` directory. Depth does not complicate the lookup.

- **NOT tested:**
  - **The real `PostToolUse` hook payload.** Wiring a hook was excluded by the handoff, so I never saw what `transcript_path` a hook receives for a *subagent's* tool call. This is the single most important open question and it cuts **in favour** of the fix: if the payload already carries the subagent's own transcript path (plausible, now that per-subagent transcripts exist), then variant 2b is unnecessary and the production change is roughly a one-line re-key. If it carries the parent's path, 2b is the fallback that makes it work anyway. **Check this first** — it decides how small the real fix is.
  - Two agents running a **byte-identical** command concurrently. The probe would see two hits and fail closed (no wrong write), but this specific race was not exercised. Distinct work-ids made it a non-issue here.
  - Anything through the **real** `checklist_engine.py` / `spine_rail.py` — the prototype stands in for both writers. Lease semantics, force-takeover, `SessionStart` resume/compaction rebinding, and the existing `gauge-skip.json` sidecar were not touched.
  - **Migration** of the 47 live bindings, transcript-format drift, and long-run performance of the tail scan across many transcripts.
  - No `python -m pytest` run: per prototyper doctrine this is throwaway code and carries no tests.

- **Next variant (if null):** n/a — the run is a positive result, not a null.

## What it taught beyond the question

1. **The suspicion of perniciousness was aimed at the wrong layer.** Nothing about subagent tracking is intrinsically hard; the difficulty was a missing field that the harness has since started emitting. The governor's "ambiguous binding → skip" rule (#202/#261) was a correct response to a genuine ambiguity that **no longer exists**. It is now a conservative rule firing on a solved problem, and it is costing every reading.

2. **`docs/GAUGE_WRITER_HOOK.md` is now wrong in a load-bearing place.** It states that subagent turns are "a different context window and are skipped" via the `isSidechain` filter. For a subagent's own transcript, **every** line is `isSidechain: true` — those are exactly the lines you want. The filter must invert when reading on behalf of a subagent, and the doc's field table needs `agentId` added.

3. **The ambiguity rule and the accumulation bug are one bug, not two.** Re-keying fixes both at once: bindings stop piling under one key (so `release` can actually find and remove its own entry — this is why terminal spines never released), and each key holds exactly one spine (so the gauge stops calling everything ambiguous). #383's two symptoms have a single cause.

4. **A stale-binding sweep is still needed and is now cheap.** The 36 accumulated entries will not clean themselves. With per-agent keys, a sweeper can test each key's transcript for liveness, which the shared key made impossible.

5. **Self-identification is a reusable capability.** "Which agent am I?" answerable from inside an arbitrary subprocess, with no hook and no cooperation from the agent, is useful well beyond the gauge — per-agent budgets, attribution of engine refusals, and per-agent lease ownership all become expressible.

## Surviving pure module

`proto_governor/agent_identity.py` (~250 lines, no engine or hook imports, side-effect-free apart from reading transcripts). Validated pieces worth lifting:

- `transcript_root` / `subagent_transcripts` / `parent_transcript` — the 2.1.220 on-disk layout, including the project-slug derivation.
- `AgentIdentity` + `resolve()` — the `<session_id>#<agentId>` key, with the parent keeping its bare `session_id` so existing parent behaviour is unchanged.
- `_bash_probe_hit` — the structured self-identification matcher (only needed if the hook payload turns out not to carry the subagent's transcript path).
- `read_fill` — the same X2 sum as production, with the sidechain filter inverted for subagents.

In real code this belongs beside `scripts/hooks/spine_rail.py` as a shared identity module imported by both `spine_rail.py` (binding key) and `gauge_writer_hook.py` (which transcript to read).

## Disposition
`captured-to-worktree`

**Detail:** Worktree `C:/Programs/.proto-exc6-governor-subagent-identity`, branch `proto/exc6-governor-subagent-identity`, commit `75f684c`. Owning issue: **#383** (subagents share the parent session id; stale bindings; zero gauge readings) — this result should be linked from there. Kept until the human disposes it; re-affirm or dispose at epic close per the accumulation cap. Nothing was landed on `main`, no `settings.json` was touched, and no hook was wired.

## One command to run (if not yet deleted)
```
cd C:/Programs/.proto-exc6-governor-subagent-identity && python proto_governor/proto_bind.py claim --work-id demo --variant b
```
(then `gauge` / `release` / `dump` with the same `--work-id`; `--variant a` reproduces the contaminated matcher failing closed)
