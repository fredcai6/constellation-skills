# Excursion X2 result — prior art: proactive context-handoff / session-refresh

**Named question:** What existing prior art addresses proactive agent context-handoff / session-refresh — published skills (notably Pocock's handoff skill), agent-framework mechanisms, and documented patterns — and for each, what is borrowable vs what we must differentiate from?

**Method:** Web search + primary-source fetch (GitHub raw files, official docs, one arXiv paper, one closed GitHub issue). ~16 sources, prioritizing primary over blog summaries. No governor design performed — survey only.

---

## 0. The Pocock question — resolved

**Pocock's handoff skill is real and found.** Author: Matt Pocock (`mattpocock`), maintains a public "Skills for Real Engineers — Straight from my .claude directory" repo.

- **Repo:** https://github.com/mattpocock/skills
- **Skill file (primary source):** https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md
- **Third-party characterizations (converge with primary source):** https://agentcookbooks.com/skills/handoff/, https://claudemarketplaces.com/skills/mattpocock/skills/handoff

**What it does:** A manually-invoked Claude Code skill (`/handoff`, or trigger phrases "handoff this conversation" / "compact for the next agent" / "write a handoff doc") that compacts the *current* session into a structured markdown handoff document, written to the OS temp directory (not the repo), for a fresh agent — same tool or a different one (Codex, a parallel worktree) — to pick up.

**Mechanism:**
- **Trigger:** Manual only. No hook, no automatic context-percentage detection. Recommended "when the context window is approaching compaction," but nothing enforces that — it's a judgment call by the user/agent, not a measured gauge.
- **Payload:** Session purpose, a compact synthesis of the conversation, an explicit "suggested skills" section for the next session, and **references (paths/URLs) to existing artifacts (PRDs, diffs, specs, ADRs, issues, commits) rather than duplicating their content** — this reference-not-duplicate discipline is the skill's central design idea. Sensitive data (keys, PII) is redacted.
- **Resume:** A fresh agent (or human) reads the doc and continues; optional user-supplied argument sets "what will the next session focus on."
- **Explicit anti-pattern noted in the skill itself:** don't use it when work "ended cleanly with no outstanding state" (a commit message suffices) or when state is fully captured in artifacts already.

There is a companion/sibling skill in the wider Pocock-adjacent ecosystem worth flagging separately below: **`strategic-compact`** (not itself in mattpocock/skills — it's a different author, `affaan-m/everything-claude-code` — but it is the piece that actually does the proactive, threshold-based *gauge* checking that `/handoff` itself lacks). Also referenced by agentcookbooks as a "related skill" alongside handoff: `context-budget` — searched for but could not locate a primary source under that exact name; treat as **unconfirmed / scoped null** (searched: web search combining "context-budget" with mattpocock and claude, found only strategic-compact under a similar description).

**Verdict: borrow the payload shape (reference-not-duplicate, suggested-skills-for-next-session, redaction) and the "clean exit vs. exhausted collapse" framing. Differentiate hard on trigger: Pocock's skill is manual-only and has no real gauge — our stated goal (checks a real context-fill gauge, hands off proactively) is explicitly the gap this skill leaves open.**

---

## 1. Annotated prior-art list

### A. Published Claude Code / agent skills

**1. Matt Pocock `/handoff`** — see §0 above.
Verdict: **borrow** payload structure and reference-discipline; **differentiate** on trigger (add the gauge it lacks).

**2. `strategic-compact`** (affaan-m/everything-claude-code)
https://github.com/affaan-m/everything-claude-code/blob/main/.agents/skills/strategic-compact/SKILL.md
- What it does: a `PreToolUse` hook script (`suggest-compact.js`) that nudges the user to run `/compact` at logical boundaries instead of waiting for forced auto-compaction.
- Mechanism — **trigger**: reads the `transcript_path` from the hook payload and sums `input_tokens + cache_read_input_tokens + cache_creation_input_tokens` from the latest `usage` record in the session transcript — this is a *client-side reconstruction* of a context-fill gauge, not a native API. Two independent signals: token size (160k/200k window, 250k/1M window, re-fires every +60k) and tool-call count (fires at 50, then every +25). **Payload**: none — it only suggests, does not generate a handoff document. **Resume**: N/A, it doesn't hand off, it just tells the human "now is a good time to `/compact`," and the human decides.
- Verdict: **borrow directly** — this is the concrete, working technique for reading a real(ish) context-fill gauge in Claude Code today (see §2 on why this matters — there's no native API). **Differentiate**: it stops at "suggest," it has no payload/handoff document and no self-driven resume — pairs naturally with Pocock's `/handoff` payload shape, but no one has published the combination.

**3. `claude-mem`** (thedotmack/claude-mem)
https://github.com/thedotmack/claude-mem
- What it does: fully automatic, hook-driven persistent memory across sessions — "no manual intervention required."
- Mechanism — **trigger**: 5 lifecycle hooks (SessionStart, UserPromptSubmit, PostToolUse, Stop, SessionEnd) fire continuously, not threshold-gated. **Payload**: raw tool-use observations are AI-summarized into compressed entries stored in SQLite + Chroma vector embeddings. **Resume**: a 3-layer staged retrieval (search → timeline → get_observations) pulls back only relevant memory (~10x token savings vs. dumping everything), injected automatically at session start.
- Verdict: **borrow** the "don't require a human/agent to remember to invoke handoff" instinct and the staged/filtered retrieval idea (index first, fetch full detail only for what's needed). **Differentiate**: this is continuous background memory, not a bounded-unit-of-work handoff with a clean actor-to-actor resume; it optimizes for "what do I generally remember about this project," not "here is exactly where I left off and what to do next."

**4. `claude-handoff`** (REMvisual/claude-handoff)
https://github.com/REMvisual/claude-handoff
- What it does: `/handoff` and `/handoffplan` commands that mine conversation history + git state into a structured markdown doc (Goal, Where We Are, What We Tried, Key Decisions, Evidence & Data, User Feedback, Where We're Going, Quick Start) with sequence-numbered chaining across sessions.
- Mechanism — **trigger**: manual only, despite the repo's tagline claiming it "survives context compaction." **Contradiction worth flagging explicitly**: on inspection this claim is misleading — there is no automatic detection or proactive firing tied to compaction; it only works if the user remembers to invoke it before compaction happens. **Payload**: richer/more prescriptive template than Pocock's (explicit sections incl. "User Feedback" and rejected approaches). **Resume**: exact paste-prompt with sequence number for chain continuity.
- Verdict: **borrow** the payload template richness (rejected-approaches, evidence) and sequence-numbered chaining across hops. **Differentiate/flag**: the marketing claim ("survives compaction") is not backed by the mechanism — good cautionary example of the gap between a skill's name/pitch and what it actually guarantees. Don't repeat that gap in our own naming.

**5. `continue-claude-work`**
https://skills-anthropic.vercel.app/skill/continue-claude-work
- What it does: reconstructs *actionable* context from local `~/.claude` session artifacts after the fact — explicitly contrasts itself with `claude --resume`/`--continue`, which replay the full transcript (wasteful) instead of selectively pulling the last compact summary, pending work, errors, and subagent completion status.
- Mechanism — **trigger**: invoked when the user names a session ID or asks to continue prior work — reactive/manual, working from disk artifacts rather than a live gauge. **Payload**: last compact summary, pending work, known errors, unresolved tool calls, subagent workflow state, session-end reason, files touched. **Resume**: within a fresh conversation, not a resumed one.
- Verdict: **borrow** the "select, don't replay" principle and the subagent-completion-status extraction (useful for orchestrator-side handoff, not just single-agent). **Ignore** the "just for me later" framing — it's a single-user recovery tool, not a designed actor-to-actor protocol.

**6. `AgentMemory` (rohitg00)** — bundles `/recall /remember /session-history /forget /recap /handoff /commit-context /commit-history` as 8 separate invocable skills.
https://github.com/rohitg00/agentmemory — found via search only, not independently fetched.
Verdict: **not independently verified** (scoped null on mechanism detail — only search-summary level, no primary-source fetch performed); flagged for a follow-up look if the governor design wants a broader menu of memory verbs beyond "handoff."

### B. Anthropic's own native mechanisms (Claude / Claude Code)

**7. Compaction API** (`compact_20260112`, Messages API beta)
https://platform.claude.com/docs/en/build-with-claude/compaction
- What it does: **server-side**, automatic summarization of the whole conversation when input tokens cross a client-configured threshold (default 150k, min 50k).
- Mechanism — **trigger**: reactive, checked at the start of each sampling iteration once the token threshold is crossed; client sets the threshold, server decides the moment. **Payload**: a `compaction` content block (summary text); content before it is auto-dropped on the next request. Custom `instructions` can replace (not append to) the default summarization prompt. Optional `pause_after_compaction: true` lets the client inspect/adjust before continuing. **Resume**: same conversation, same actor — this is *self*-resume via forced summary, not a handoff to a different actor.
- Verdict: **differentiate strongly**. This is exactly the "summarized under duress" failure mode our governor is designed to avoid — it's reactive (crosses a hard threshold), lossy by construction (a single compaction block replaces history), and same-actor. It is the thing we are the alternative to, not something to imitate; the one detail worth **borrowing** is `pause_after_compaction` — the idea of a clean stop-point the client can intervene on before resuming, which is structurally close to "hand off cleanly" if repurposed proactively instead of reactively.

**8. Memory tool + Context Editing API**
https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool , https://platform.claude.com/docs/en/build-with-claude/context-editing
- What it does: memory tool lets the model persist facts to an external store across turns/sessions (client-managed file-like store); context editing auto-clears old tool-use/result pairs and thinking blocks server-side, before token counting, to keep active context lean. Anthropic reports 29% improvement from context editing alone, 39% combined with memory tool, over an uncontrolled baseline.
- Mechanism — **trigger**: context editing is continuous/automatic (clears stale tool output opportunistically); memory tool is agent-driven (the model chooses to write/read memory via tool calls, MemGPT-style). **Payload**: arbitrary agent-chosen memory entries; tool-result clearing removes bulk, not summary. **Resume**: same session, same actor.
- Verdict: **differentiate** on scope (this is intra-session hygiene, not a task-boundary actor handoff) but **borrow** the self-directed "agent chooses what to persist via a memory write" idea if our governor wants the handing-off agent, not an external controller, to decide handoff *contents*.

**9. Claude Code subagent isolation** (native `Agent`/Task tool pattern)
https://www.richsnapp.com/article/2025/10-05-context-management-with-subagents-in-claude-code (secondary, but consistent with documented behavior we already rely on)
- What it does: a subagent gets a **fresh context window**; only its final report returns to the parent, raw tool output and intermediate reasoning stay walled off.
- Mechanism — **trigger**: explicit delegation by the parent, not budget-driven. **Payload**: whatever the subagent chooses to write in its final report (unstructured by default). **Resume**: the parent, not the subagent, continues — this *is* fresh-context spawning, just without any proactive self-triggering.
- Verdict: **borrow** the isolation/report-only shape (this is close to how our own constellation Commander/Admiral delegation already works) — **differentiate** by adding the missing piece: a structured payload contract and a gauge-driven trigger, neither of which the native pattern defines.

**10. "Five-mechanism" Claude Code compaction architecture** (microcompact, tool-output-clearing, full LLM summarization, cross-session cache reuse, Compact Instructions in CLAUDE.md) — reported by https://hyperdev.matsuoka.com/p/how-claude-code-got-better-by-protecting , a third-party analysis, **not independently verified against Anthropic source** — flag as **secondary source, take with appropriate discount**.
Verdict: **informational only** — illustrates that even Anthropic's own product treats compaction as a graduated-severity ladder (cheap mechanical cleanup first, expensive LLM summarization last), which is a shape worth noting but not a documented public contract to build against.

**11. GitHub issue: "Expose context window usage percentage to hooks"** #27969 (closed as duplicate)
https://github.com/anthropics/claude-code/issues/27969 (see also open issue #43431 "Show context window usage percentage / distance to auto-compact," and #34340)
- **This is a load-bearing finding, not a tool**: as of this research, Claude Code does **not** natively expose a real-time context-fill percentage to hooks/skills. The percentage is computed and shown in the UI but not surfaced programmatically. Requested env vars (`CLAUDE_CONTEXT_PERCENT`, `CLAUDE_CONTEXT_TOKENS_USED/MAX`) do not exist yet.
- Consequence: every skill that claims to react to "context usage" (strategic-compact, item 2) is working around this gap by parsing the session transcript file directly and summing token-usage fields from the last recorded API `usage` block — a fragile, undocumented, version-coupled technique, not a stable API.
- Verdict: **critical scoping fact for our own design**, not itself borrow/differentiate/ignore — it means "checks a real context-fill gauge" is currently only achievable via the transcript-parsing workaround (borrowable technique, see #2) or by using the Anthropic Messages API's own token accounting directly if we're not going through Claude Code's hook surface. If the governor is meant to run *inside* Claude Code via hooks, this gap should be named explicitly as a known constraint, not assumed away.

### C. Agent-framework mechanisms

**12. LangGraph checkpointing/persistence**
https://docs.langchain.com/oss/python/langgraph/persistence
- What it does: snapshots full graph state after every node execution, keyed by thread_id, to a pluggable store (Postgres recommended for production).
- Mechanism — **trigger**: after every node, unconditional (not budget-gated) — this is closer to "always be ready to resume" than "proactively hand off when running low." **Payload**: full serialized state (TypedDict/Pydantic), node inputs/outputs, error reason, retry_count, human-handoff status. **Resume**: same or different orchestrator run, from the exact last checkpoint — precise resumption (resume node N, not "somewhere near where we left off").
- Verdict: **borrow** the "checkpoint is a recovery point for interruption/timeout/human-handoff/restart" framing (multi-purpose one mechanism) and the idea of a monotonic, addressable resume point. **Differentiate**: this is state persistence for graph execution, not a context-budget-driven proactive re-instantiation — LangGraph checkpoints don't shrink context, they just make restart cheap; doesn't solve context-fill at all, solves durability.

**13. OpenAI Agents SDK `handoff()`**
https://openai.github.io/openai-agents-python/handoffs/
- What it does: agent-to-agent control transfer — a triage agent hands off to a specialist agent as a tool call.
- Mechanism — **trigger**: the current agent decides to call a `handoff` tool (self-triggered, not budget-driven — it's driven by task/domain fit, e.g. "this is a billing question," not by context fill). **Payload**: by default, the **entire conversation history** passes to the new agent (not summarized) — optionally trimmed via `input_filter`. New (beta, opt-in) **nested-handoff summarization**: `RunConfig.nest_handoff_history` collapses the prior transcript into a single assistant summary wrapped in a "CONVERSATION HISTORY" block, appended to on each subsequent handoff. **Resume**: the new agent, mid-run, same orchestrator/session.
- Verdict: **borrow** the nested-handoff summarization idea (opt-in, explicit collapse-to-summary on each hop, avoiding unbounded transcript growth across many hops) — directly relevant if our governor's agents hand off repeatedly in a chain. **Differentiate**: default behavior (full history passthrough) is the opposite of context-conscious; the trigger is task-routing, not budget — we'd be adding a dimension (budget-triggered) this framework doesn't have.

**14. CrewAI / AutoGen**
(secondary sources only — Medium/DeepWiki summaries, no primary framework doc fetched)
- CrewAI: Hierarchical Process, a manager agent delegates by role/goal/backstory match.
- AutoGen 0.4: `SelectorGroupChat` — dynamically selects next speaker via an LLM-judged `selector_prompt` over conversation history. Both reportedly added "Swarm Patterns" (agent-initiated handoffs) in late 2025.
- Mechanism: task/capability-routing, not context-budget-routing, in both cases.
- Verdict: **ignore** for our specific question — neither addresses proactive context-fill handoff; both are about *which* agent should act next, not *when to refresh because context is full*. Noted only because they're the two most-cited alternatives to OpenAI's `handoff()` and consistently do NOT solve this problem, which itself is a useful negative data point (no major multi-agent framework treats context-budget as a handoff trigger natively).

**15. Letta / MemGPT — virtual context management**
https://www.letta.com/blog/memory-blocks/
- What it does: OS-inspired paging — named memory blocks (`persona`, `human`, `archival_memory`, `recall_memory` by default) sit in a fixed main context; the agent itself decides, via function calls, what to page out to archival/recall storage when a block fills. Blocks can be **shared across multiple agents**.
- Mechanism — **trigger**: per-block token ceiling; when a block fills, the *agent* (not an external controller) decides what to evict/summarize — self-directed, proactive in the sense that it happens before hard overflow, but granular (block-level) rather than whole-session. **Payload**: whatever the agent chooses to write to archival memory (agent-authored, not template-driven). **Resume**: same agent identity persists indefinitely; blocks are the durable substrate, not a one-time handoff document.
- Verdict: **borrow** two ideas: (a) self-directed "the agent decides what's worth keeping" rather than an external summarizer, and (b) shared memory blocks across multiple agents as a lighter-weight alternative to a full handoff document when agents are collaborating live rather than sequentially. **Differentiate**: MemGPT/Letta is architected around one persistent agent identity managing its own memory forever, not a bounded unit-of-work agent that terminates and is replaced by a fresh instantiation — our shape (finish → check gauge → hand off → get re-instantiated fresh) is closer to a *relay* than to Letta's *continuous single runner*.

### D. Documented patterns / academic

**16. "Relentless Agent" continuation loop** — KISS Sorcar (arXiv:2604.23822, UC Berkeley)
https://arxiv.org/abs/2604.23822
- What it does: wraps an agent in a continuation loop explicitly so it can complete tasks exceeding one context window, by breaking work into sub-sessions.
- Mechanism — **trigger**: the agent itself sets `is_continue=True` when it judges its context window or step budget is exhausted — **self-triggered, proactive by construction** (this is the closest published match to our stated design). **Payload**: a *structured, chronologically-ordered* summary of every action taken, with explanations and code snippets — the paper reports that a naive "summarize what happened" instruction produced poor continuations, and that requiring step-by-step chronological structure with code snippets measurably improved coherence across sub-sessions. **Resume**: a brand-new sub-session, fresh context window, prompted with the chronological list of all prior summaries plus an explicit instruction not to redo completed work.
- Verdict: **borrow directly — strongest convergence found**. Self-triggered (agent judges its own exhaustion, not an external reactive threshold), fresh-context resume, and an empirically-tuned payload format (chronological + code snippets beats free-form summary). This is closest published academic validation of our exact shape; worth citing as evidence the approach works, and worth mining for the specific payload-structure lesson (naive summarization underperforms structured chronological summarization).

**17. ContextBudget** (arXiv:2604.01664) — "Budget-Aware Context Management for Long-Horizon Search Agents"
https://arxiv.org/html/2604.01664
- What it does: frames context compression as a budget-constrained sequential decision problem — compression decisions adapt dynamically to *remaining* context capacity through a long task, rather than firing once at a fixed threshold.
- Mechanism: not a shipped tool, a decision-framing. Trigger is continuous/dynamic rather than single-threshold. No concrete payload/resume mechanism reported at search-summary depth (not independently fetched beyond the abstract-level search result — **scoped null**: did not fetch full PDF).
- Verdict: **borrow the framing** ("budget-aware, dynamically adaptive" vs. "single fixed threshold") as a conceptual check on our own design — worth a closer read if the governor's threshold logic needs a name/citation, but not independently verified beyond search summary.

---

## 2. Convergences (patterns multiple systems independently share)

1. **Reference, don't duplicate.** Pocock's `/handoff`, `continue-claude-work`, and LangGraph checkpoints (state, not full replay) all converge on: point at artifacts/state rather than copying content into the handoff payload.
2. **Fresh context window as the resume substrate.** Native Claude Code subagents, Relentless Agent sub-sessions, and (implicitly) every "handoff to a new session" skill agree: the receiving actor gets a *clean* window, not a continuation of the same one — this is structurally different from all of Anthropic's own compaction/context-editing mechanisms, which resume the *same* window/actor.
3. **Structured payload beats free-form summary.** Explicitly measured in Relentless Agent (chronological + code snippets outperforms naive "summarize"); implicitly assumed by every handoff skill's use of fixed markdown sections (Goal / Where We Are / Next Steps, etc.) rather than an open paragraph.
4. **Self-directed trigger, where it exists at all, beats external reactive threshold.** Relentless Agent (agent sets `is_continue`), Letta (agent decides what to evict), OpenAI Agents SDK handoff (agent calls the tool) — all let the acting agent judge exhaustion/fit, vs. Anthropic's compaction API and strategic-compact's hook, which are externally/mechanically triggered by a token count.
5. **No shipped system combines a real proactive gauge with a structured handoff payload and self-triggering.** Every piece exists somewhere (gauge-reading in strategic-compact; payload structure in Pocock/REMvisual; self-triggering in Relentless Agent/Letta) but no surveyed prior art combines all three. That combination is the open space our governor would occupy — surveyed, not designed, here.

## 3. Contradictions / cautionary findings surfaced

- **REMvisual/claude-handoff's tagline ("survives context compaction") is not backed by its mechanism** — it's manual-invoke-only, same as Pocock's skill, despite the framing implying automatic/durable behavior. Worth naming explicitly so we don't repeat the same overclaim in our own naming.
- **Claude Code has no native hook-exposed context-fill percentage** (GitHub issue #27969, closed as duplicate; #43431 still open) as of this research — despite this being obviously wanted (multiple independent feature requests), Anthropic has not shipped it. Any design assuming "read the gauge via a hook" needs the transcript-parsing workaround, not a clean API, or needs to operate above Claude Code (direct Messages API token accounting) instead.
- **Anthropic's own default guidance point in the opposite direction from a proactive per-agent gauge**: their documented recommendation is "use server-side compaction, it needs less integration complexity than client-side bookkeeping" — i.e., Anthropic's stated preference is to let the server handle it reactively, which is exactly the "summarized under duress" pattern our governor is meant to avoid. Worth having an explicit answer for "why not just use server-side compaction" when this design gets reviewed.

## 4. Scoped nulls (named, not blanket)

- **`context-budget` skill** (referenced by agentcookbooks.com as related to Pocock's handoff/strategic-compact) — searched web search for `"context-budget" OR "strategic-compact" skill mattpocock claude`; found strategic-compact's primary source but no independent `context-budget` skill under that name from any author. Not confirmed to exist as a distinct published skill.
- **`AgentMemory` (rohitg00/agentmemory)** — found via search listing only; not independently fetched from GitHub, so its actual trigger/payload/resume mechanics are unverified beyond the search-engine summary.
- **ContextBudget arXiv paper** — read at abstract/search-summary depth only, full PDF not fetched; framing-level claim only, not verified against paper's actual method section.
- **CrewAI / AutoGen** — characterized from secondary sources (Medium, DeepWiki) only; no primary framework documentation page fetched directly. Directional confidence is fine for the "ignore" verdict (neither addresses context-budget triggering) but exact API details are not verified.
- Did **not** search: Cursor/Windsurf/Cline-specific handoff conventions, Aider's `/save`/session mechanisms, Amazon Bedrock agent handoff patterns beyond the one compaction doc surfaced incidentally, or Devin/Cognition's internal architecture beyond the one incidental mention surfaced in a context-engineering search result.

---

## 5. Summary table

| # | Name | Trigger | Payload | Resumes | Verdict |
|---|------|---------|---------|---------|---------|
| 1 | Pocock `/handoff` | manual | structured md, ref-not-dup, redacted | fresh agent (self/cross-tool) | borrow payload, differentiate trigger |
| 2 | strategic-compact | token/tool-count threshold via transcript parsing | none (nudge only) | human decides | borrow gauge technique |
| 3 | claude-mem | continuous hooks | AI-summarized indexed memory | auto-injected at session start | borrow auto-capture instinct, differentiate scope |
| 4 | claude-handoff (REMvisual) | manual (claims auto, isn't) | rich structured md w/ sequence chaining | paste-prompt into fresh session | borrow template, flag overclaim |
| 5 | continue-claude-work | manual/on-demand | selective reconstruction from disk | fresh conversation | borrow "select not replay" |
| 6 | AgentMemory | unverified | unverified | unverified | scoped null |
| 7 | Anthropic Compaction API | server threshold, reactive | single summary block | same actor/session | differentiate — the failure mode we avoid |
| 8 | Memory tool + Context Editing | continuous/agent-driven | agent-authored memory entries | same session | differentiate scope, borrow agent-chooses-payload |
| 9 | Claude Code subagents | explicit delegation | unstructured final report | parent continues | borrow isolation shape |
| 10 | 5-mechanism compaction (3rd-party) | graduated by severity | n/a | n/a | informational, secondary source |
| 11 | Issue #27969 (no gauge API) | n/a | n/a | n/a | constraint, not a tool |
| 12 | LangGraph checkpointing | every node, unconditional | full state snapshot | exact node resume | borrow durability framing, differentiate purpose |
| 13 | OpenAI Agents SDK handoff() | task-routing, self-triggered | full history (default) or nested summary (beta) | new agent, same run | borrow nested-summary idea |
| 14 | CrewAI/AutoGen | task/capability routing | n/a | next selected agent | ignore (no budget dimension) |
| 15 | Letta/MemGPT | per-block fill, agent-directed | agent-authored | same persistent identity | borrow self-direction, differentiate continuity model |
| 16 | Relentless Agent (arXiv) | self-triggered exhaustion judgment | structured chronological + code | fresh sub-session | borrow directly — strongest match |
| 17 | ContextBudget (arXiv) | dynamic, budget-constrained | unverified | unverified | borrow framing only |
