# Excursion X2 handoff — research (web / external prior art)

## The one named question
What existing prior art addresses proactive agent context-handoff / session-refresh — published skills (notably **Pocock's handoff skill**), agent-framework mechanisms, and documented patterns — and for each, what is borrowable vs what we must differentiate from?

## Context (why we're asking)
We're designing a "context governor" for a multi-agent system: an agent, on finishing a bounded unit of work, checks a real context-fill gauge and — if low on headroom — hands off cleanly and gets re-instantiated fresh (by its delegator or itself) rather than being summarized under duress by emergency auto-compaction. We want to know what others have already built so we borrow good shapes and differentiate from the rest.

## Task — find and characterize prior art
Search the web and primary sources for:
1. **Pocock's handoff skill** specifically — find it (Claude Code / agent "handoff" skill by someone named Pocock, possibly on GitHub, a blog, or a skills marketplace). Characterize exactly what it does and how.
2. Claude Code / Claude Agent SDK community **handoff, continuation, session-resume, and memory skills**.
3. Agent-framework mechanisms for context management & handoff: LangGraph checkpointing/state, CrewAI/AutoGen handoffs, OpenAI Swarm/Agents SDK "handoffs", Letta/MemGPT context paging, Claude's own compaction, "context engineering" continuation patterns.
4. Documented **patterns**: proactive summarization at task boundaries, sub-agent spawning with a fresh window, "memory blocks" / scratchpads that survive a reset, budget-aware orchestration.

## What "answered" looks like (the deliverable)
An annotated prior-art list. For each entry:
- **Name + source/link**
- **What it does** (one or two lines)
- **Mechanism**: when it hands off (trigger), what the handoff carries (payload), who resumes (self / orchestrator / human)
- **Verdict**: borrow / differentiate / ignore — one line why

Call out convergences (patterns multiple systems share) and any idea that beats our current direction. Explicitly resolve the Pocock question: what it is, or a scoped null naming what you searched if you can't find it.

## Scope / stop conditions
- Web research; ~6–10 quality sources; prefer primary sources / actual repos over blog summaries.
- Surface contradictions; don't smooth them.
- Do NOT design our governor — survey prior art only.
- Scoped nulls: a null names what was and was NOT searched; it kills that search, not the question.

## Return format
Write findings to `.agent-work/explore-context-governor/excursion-x2-result.md` (absolute: `C:/Programs/constellation-skills/.agent-work/explore-context-governor/excursion-x2-result.md`). Also return a concise summary (top borrowable entries + the Pocock verdict) as your final message.
