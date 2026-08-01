# Excursion X3 handoff — research (agent self-refresh capability across harnesses)

## The one named question
In each of **Claude Code**, **OpenAI Codex CLI**, and **pi.dev**, can a running agent cause a FRESH instance of ITSELF to continue its work *from within its own execution* — true self-refresh (replace its own full context in place / restart its own session with a handoff) — as opposed to (a) spawning a subordinate child agent that returns to a still-full parent, or (b) the layer above / a human restarting it?

## Why we're asking
We're designing a "context governor": an agent that, near context exhaustion, hands off and gets re-instantiated fresh. A key fork is WHO does the re-instantiation — the agent itself (self-relay) or the layer that dispatched it (reach-up). Reach-up works on any harness; self-refresh is only possible where the runtime lets an agent restart itself. We need the capability facts per harness, and Fred flagged pi.dev as a place he thinks self-refresh IS possible (a long-term plus) — but noted it "doesn't work on a Claude subscription."

## Task — confirm per harness
For EACH of the three, answer: CAN or CANNOT an agent self-refresh, with the exact mechanism (if yes) or the exact structural reason (if no), and whether "spawn a continuation child / new session" exists as a partial substitute.

1. **Claude Code** (CLI + Claude Agent SDK). Consider: the Task/subagent tool (are subagents children that return to the parent, or can they replace the parent?); `--resume`/`--continue` (is that a human/CLI action or agent-invokable?); auto-compaction; any programmatic self-restart in the Agent SDK. Prior finding to verify, not assume: the SDK exposes no self-compaction API and subagents are children.
2. **OpenAI Codex CLI**. Does it support subagents at all? How does it manage context / long sessions? Is there any agent-invokable self-restart or handoff-to-fresh-session mechanism? Cite the Codex CLI docs/repo.
3. **pi.dev**. First: WHAT IS IT (company/product/runtime)? Then: does its agent-loop model let an agent restart/refresh itself (i.e. do you control the run loop, making self-refresh implementable)? Confirm or refute Fred's claim that it cannot run against a Claude *subscription* (Pro/Max) and requires API billing.

## What "answered" looks like (deliverable)
A per-harness verdict table: Harness | Self-refresh CAN/CANNOT | Mechanism or blocking reason | Continuation-child substitute available? | Source. Then one "implication" line: on which of the three does a reach-up design work, and where is self-refresh a genuine bonus. End with scope: what was checked, what was NOT.

## Scope / stop conditions
- Web + official docs; prefer primary sources (Claude Code docs / Agent SDK reference, OpenAI Codex CLI docs/GitHub, pi.dev official site/docs).
- ~6–10 sources; report even if one harness is inconclusive.
- Do NOT design the governor — capability facts only.
- Scoped nulls: a null names exactly what was and was NOT checked per harness; it kills that check, not the question.

## Return format
Write findings to `.agent-work/explore-context-governor/excursion-x3-result.md` (absolute: `C:/Programs/constellation-skills/.agent-work/explore-context-governor/excursion-x3-result.md`). Also return a concise summary (the three verdicts + pi.dev identity + subscription claim) as your final message.
