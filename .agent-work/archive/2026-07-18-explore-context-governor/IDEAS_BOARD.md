# Ideas Board — `explore-context-governor`

The living record of shared understanding and the **source of truth** for this exploration. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history; a mid-exploration shelve files *this file* as the shaped-design issue, loudly marked unconfirmed.

## The point

Constellation agents can't reliably read their own context fill — self-report is confabulation — and the harness only intervenes at ~90% with a lossy emergency auto-compact. The itch: give the fleet a **proactive context governor** so a long-running agent hands off *cleanly at a work seam of our choosing* instead of being summarized under duress or silently losing state mid-session. "Done" feels like: an agent that finishes a bounded unit of work, checks a real fuel gauge, and — if low — reaches **up** to its delegator ("I'm getting full; refresh me and re-send with this handoff"), which re-instantiates a fresh agent from a handoff block rich enough for a cold start. The delegation chain does the refresh: Commander refreshes implementers/reviewers, Admiral refreshes a delegated Commander, and at the top the human does it.

**Kill condition:** if a clean handoff+refresh turns out to lose more effective continuity than auto-compaction preserves (i.e. the cold-start block can never be made "good enough" and every refresh is a productivity cliff), the governor is pointless — better to just ride auto-compact.

## Current candidates

After cycle 1 (shotgun → consolidation), the live candidates are organized as **four strategic axes** the design must take a position on, plus settled component families. Full idea set + culls live in `cycle-1.json`.

**Strategic axes (unresolved — the compare-cycle fuel):**
- **AX1 · Govern vs Prevent — RESOLVED into "both, one mechanism."** Not a choice: the soft "good stopping point?" question governs the filling agent AND prevents overcommit (an agent asked while full naturally stops at the seam before diving into the next big chunk). Prevention is agent-judged, folded into the stop-point call — not a separate upstream issue-sizing strategy. (Human synthesis, cycle 2.)
- **AX2 · Thin vs Rich handoff — RESOLVED by X1 (see Verdicts).** Not binary: mechanical cold-start is mostly FREE already (thin); the governor's real new payload is narrow and identical across tiers — a *live understanding digest* + a *voluntary refresh-seam handoff shape* that exists nowhere today. Reframe: the design isn't "build a rich handoff," it's "capture the 3 missing things + define the voluntary-handoff shape; ride the existing engine state for everything else." Also: X1 flagged a **third resume situation** — today's world has (a) stalled-but-alive → CLI session-continue, (b) confirmed-dead → cold-start from engine state; the governor introduces (c) *voluntary refresh before crash*, a genuinely new case. And LAUNCH_ORDER is already "governor-shaped" but authored once at dispatch, not regenerated at a seam — a strong template to borrow from.
- **AX3 · Reach-up vs Self-relay — RESOLVED by X3 in favor of reach-up.** Self-refresh doesn't exist out-of-the-box on any of Claude Code / Codex CLI / pi.dev, and is *impossible* to build on Claude Code + Codex (no primitive exposed to any tool). Only pi.dev has the primitives to build it. So reach-up (delegator re-instantiates; human at top) is the portable foundation; self-refresh is a pi.dev-only optional optimization. Matches the human's portability driver below.
- **AX4 · Doctrine fork** — D1: amend §Universal-posture ("`/compact` opportunistic, not a gate") or fit under it as opportunistic-at-seam. Must resolve regardless of the other three.

**Crystallizing design (after cycle 2 refine) — one coherent shape, all major forks resolved:**

The governor is an **upgrade to how agents log**, not a bolted-on mechanism, plus a near-free trip:
1. **Why-capture at every non-mechanical gate**, enforced by an **engine schema update** (the why-field is part of the gate schema). Prompt mandatory, content optional — "**mechanical / no why**" is a first-class explicit answer (silence is a bug; explicit-nothing is data). Mechanical gates pre-marked why-exempt at template-authoring time.
2. **Self-superseding digest**: each why has 3 cheap parts (why-done / what-I-understand / what's-next); the latest "what I understand" IS the live digest, the trail is history. No separate synthesis machinery. References engine task-state for the *what* (Pocock don't-duplicate).
3. **Free gauge trip at the gate, two bands.** A harness hook writes context-fill to a local file every tool call; the engine (already invoked at each gate) reads it. **SOFT band (PRIMARY) = "just ask the agent."** When fill is high the engine surfaces a plain question — "you've used most of your context; is this a good stopping point?" — and trusts the agent's answer. Clean division of labor: the **engine supplies the fill FACT** (the one thing agents can't self-measure), the **agent supplies the stop-point JUDGMENT** (seam quality — a thing agents CAN do). Not an engine computation — the earlier fill×gates-remaining idea is dropped (gate-count is a bad effort proxy). **Biased toward stopping** — frame so hand-off is the default ("unless you're basically done, stop here"); we don't want an agent grinding on when it's tired. **HARD band = force** — a pure fill backstop that refuses to advance until handoff; rarely fires (we're structurally not hitting auto-compacts). Agent never *measures* fill; it only judges the seam.
4. **Reach-up refresh** (invoker re-instantiates; human at top) — portable across Claude Code/Codex/pi; self-refresh a pi-only later bonus.
5. **Symmetric recovery**: intentional refresh and lost-session resume from the identical trail — so the logging upgrade pays for itself on crash recovery alone (de-risks the project).

Spec-level detail still to settle (not open exploration): schema fields, threshold policy, per-tier exempt gates, handoff artifact format, soft-advise-vs-hard-force teeth, the portable gauge-file seam, missing-gauge fail-safe.

**Settled component families (lead + fallbacks):**
- **Sensing** — S1 hook-injected real number (lead); S2 tool-count / S3 byte-size proxies as fallbacks.
- **Trigger** — R1 seam-primary + R2 N-tool-call backstop for seamless runaways; R4 = R1 at Admiral wave.
- **Threshold** — T1 model-keyed + T4 two-band (soft nudge / hard stop) baseline; T3 predictive as ambitious upgrade.
- **Handoff** — anchored on H3; H1 tier-specific, H4 vitals-line, H2 pre-declared handover as refinements.
- **Enforcement** — E1 Stop-hook artifact-enforce, E2 PreCompact tripwire; E3 (context as first-class spine resource) is the architectural option.

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Agents cannot reliably introspect context fill | Verified against Claude Code capability surface; self-report is confabulation. NOT tested: whether coarse self-estimation is good enough for a very high threshold | pre-exploration (claude-code-guide) |
| Hooks cannot invoke `/compact`; no auto-compact threshold knob; SDK exposes no per-turn token counts | Verified against current Claude Code docs. NOT tested: future/undocumented SDK surfaces | pre-exploration (claude-code-guide) |
| Hooks CAN read `transcript_path`, inject `additionalContext` (UserPromptSubmit/SessionStart), force-stop (`PostToolUse decision:block`), enforce artifacts (Stop), tripwire (PreCompact) | Verified. NOT tested: token-estimate accuracy off the JSONL vs harness's true accounting | pre-exploration (claude-code-guide) |
| **Prior art (X2): the gauge+payload+self-trigger COMBINATION is open space** — no surveyed system combines a real context-fill gauge + structured handoff payload + automatic self-triggering. Pocock's handoff skill (Matt Pocock, `mattpocock/skills`, MIT) is manual-invoke only, no gauge/trigger — its key borrowable discipline is *reference existing artifacts, don't duplicate them* (exactly matches X1's "ride the engine state"). Working gauge technique exists: `strategic-compact` parses `transcript_path` + sums token fields (no native API — GH issue #27969 closed-as-dup). Payload evidence: Relentless Agent / KISS Sorcar (arXiv, UC Berkeley) — agent self-judges exhaustion, hands *structured chronological summary + code snippets*; paper shows naive "just summarize" UNDERPERFORMS structured (validates X1 gaps #1/#2). Anthropic's own recommended path is server-side reactive compaction = the "summarized under duress" mode the governor exists to avoid. | Tested: ~17 sources, primary repos/papers preferred. NOT fully verified (scoped nulls): `context-budget` skill not located as standalone; AgentMemory search-depth only; CrewAI/AutoGen secondary sources; ContextBudget arXiv abstract-only | excursion X2 |
| **AX3 RESOLVED — reach-up is the foundation; self-refresh is a pi.dev-only bonus, not shipped anywhere.** Claude Code: CANNOT self-refresh (subagents are children returning to a still-full parent; `--resume`/`--continue` are shell-only, not agent-callable; auto-compact is in-place; SDK `resume` belongs to the caller's next `query()`). Codex CLI: CANNOT (hierarchical subagents, max depth 1, children return summaries; compaction is in-place). pi.dev (Earendil Inc., MIT, `pi-agent-core`): structurally CAN — its loop is an open library (`terminate:true` tool hint + `AgentHarness.newSession({parentSession})` generate a fresh linked session), so an agent-invocable handoff tool *could* be built, but the shipped `/handoff` is a human slash command. Subscription claim CONFIRMED: pi can OAuth a Claude Pro/Max sub, but Anthropic's ~Apr-2026 billing change routes third-party-OAuth usage into a per-token "extra usage" pool (≈ API billing) — GH issue earendil-works/pi#3372. **Implication: reach-up works unmodified on all three today; self-refresh is genuine near-term headroom only on pi.dev.** | Tested: official docs for Claude Code (via claude-code-guide, not independently re-fetched), Codex CLI, pi.dev repo + handoff.ts + billing issue. NOT tested: no harness driven live; pi loop arch from a DeepWiki secondary summary, not raw source; Codex `/compact` agent-invokability unconfirmed | excursion X3 |
| **AX2 RESOLVED — handoff is MIXED, leaning THIN with one well-scoped RICH gap.** Existing engine/handoff state already reconstructs *most* of a mechanical cold-start at every tier (current step + full imperative via `current`; frozen task/scope/criteria/map-anchors as durable files; completed-step evidence; lease; Commander/Admiral `STATE_NOTE` detach point; ADMIRAL_LOG narrative). The governor's REAL differentiated payload is the same 3 gaps at every tier: (1) in-flight/partial reasoning capture, (2) a running synthesized "current understanding" digest (everything durable is frozen-at-authoring or an append-only log you must re-derive from), (3) a *voluntary refresh-at-a-chosen-seam* artifact — which exists NOWHERE today (all machinery is for normal advance or crash recovery, never "I'm alive and choosing to hand off"). | Tested: doctrine/template read across implementer, reviewer, commander, commander-delegated, admiral, workbench + engine source. NOT tested: no live crash-resume drill executed; relaunch reuse-vs-overwrite of a partial plan file unverified; commander-delegated SKILL.md not read directly | excursion X1 |

## Excursion briefs

### X1 · "Thin-vs-Rich handoff — what does constellation already reconstruct on resume?" (research, cycle 1/2)

- **The one named question:** For a fresh/resumed constellation agent at each tier (implementer, reviewer, commander, admiral), how much of a cold-start "resume block" is ALREADY provided by durable engine + handoff state today (spine.json, IDEAS_BOARD, the *_HANDOFF templates, the crash-resume state note, workbench closeout), and what is MISSING that a context-governor handoff would still have to supply?
- **Type:** research (codebase — this repo). Why: AX2 is answerable from what the skills already write, not from opinion.
- **What "answered" looks like:** a per-tier inventory — "on resume, tier T reconstructs {A,B,C} from {artifact}; it does NOT reconstruct {D,E}; the governor handoff would need to add {D,E}." Verdict on whether the governor is THIN (engine state ≈ sufficient) or RICH (substantial new payload owed), with the scope of what was and wasn't examined.
- **Budget / stop:** read-only; the constellation-skills repo only; ~1 pass over handoff/closeout/spine templates + the resume/crash-resume doctrine; report even if inconclusive. Do NOT design the governor or propose mechanism — inventory only. Scoped null if a tier can't be assessed: say which and why.
- **Result artifact:** `.agent-work/explore-context-governor/excursion-x1-result.md`

### X2 · "Prior art — proactive context handoff / agent refresh" (research, web, cycle 1/2)

- **The one named question:** What existing prior art addresses proactive agent context-handoff / session-refresh — published skills (notably **Pocock's handoff skill**), agent-framework mechanisms, and documented patterns — and for each, what is borrowable vs what we must differentiate from?
- **Type:** research (web + external sources). Why: this is about what others have already built so we don't reinvent or miss a better shape.
- **What "answered" looks like:** an annotated list of prior-art entries — name, source/link, what it does, the mechanism it uses (when to hand off, what the handoff carries, who resumes), and a one-line "borrow / differentiate / ignore" verdict. Explicitly locate and characterize Pocock's handoff skill if it exists; if it can't be found, say so (scoped null) and name what was searched.
- **Budget / stop:** web research; ~6–10 quality sources; primary sources / actual skill repos preferred over blog summaries; surface contradictions. Do NOT design our governor — survey only. Scoped null names what was and wasn't searched.
- **Result artifact:** `.agent-work/explore-context-governor/excursion-x2-result.md`

### X3 · "Can an agent self-refresh? — Claude Code / Codex CLI / pi.dev" (research, cycle 2)

- **The one named question:** In each of Claude Code, OpenAI Codex CLI, and pi.dev, can a running agent cause a FRESH instance of ITSELF to continue its work from within its own execution (true self-refresh — replace its own full context in place / restart its own session), as opposed to (a) spawning a subordinate child that returns to a still-full parent, or (b) the layer above / a human restarting it?
- **Type:** research (web + official docs). Why: settles AX3 (reach-up vs self-relay) and the harness-portability question Fred raised.
- **What "answered" looks like:** a per-harness verdict — Claude Code / Codex CLI / pi.dev — each: CAN or CANNOT self-refresh, the exact mechanism or the exact reason it can't, and whether "spawn a continuation" is available as a partial substitute. Plus: what is pi.dev, and confirm Fred's claim that it can't run on a Claude *subscription* (API-billing only). Implication line: which of the three the reach-up design works on vs where self-refresh is a bonus.
- **Budget / stop:** web/docs research; official sources preferred (Claude Code docs / Agent SDK, OpenAI Codex CLI docs/repo, pi.dev site/docs); ~6–10 sources; report even if a harness is inconclusive (scoped null naming what was checked). Do NOT design anything — capability facts only.
- **Result artifact:** `.agent-work/explore-context-governor/excursion-x3-result.md`

## Open threads

- Does the design require a hook at all, or can the governor live entirely as skill doctrine at the seam (agent asks the delegator, no harness mechanism)? Hook vs doctrine is a load-bearing fork.
- Doctrine conflict: `global-everyone.md` §Universal posture says context headroom is "opportunistic… not its own checkable gate." A governor that gates on fill contradicts this. Does the design amend that doctrine, or fit within it (opportunistic check, not a hard gate)?
- What is the minimum content of a "cold-start-sufficient" handoff block, per tier (implementer vs commander vs admiral)?
- Token-estimate accuracy: how much margin does an imprecise JSONL count force?
- What exactly is a "seam" for each tier, and are there agents with no natural seam before the limit?

## Design considerations (from the human)

- **Harness portability is a first-class factor (Fred).** The design should target the *lowest-common-denominator* capability across the harnesses Fred cares about (Claude Code now; Codex CLI; pi.dev long-term). If self-refresh only works on some, **reach-up refresh is the portable choice** — it works even where an agent can't restart itself. Self-refresh, where available (Fred suspects pi.dev), is a bonus/optimization, not the foundation. Note: pi.dev reportedly can't run on a Claude *subscription* (API-billing only) — a real adoption constraint. **CONFIRMED by X3:** reach-up works on all three; self-refresh is a pi.dev-only bonus (and must be *built*, not shipped); Claude-subscription billing constraint confirmed.

## Rejected ideas (with reasons)

*Culls are scoped verdicts — parked here, reversible.*

- **S4 self-calibration** — adds a feedback-loop subsystem; revive if S1's hook number proves unavailable/too costly.
- **A2 watcher-sidecar agent** — a whole extra agent babysitting fill; YAGNI unless fleet-scale monitoring becomes real.
- **P4 self-`/compact`** — depends on a capability agents don't have; revive if `/compact` becomes agent-invokable.
- **W1 context-bankruptcy breaker** — collapses into T4 hard band + E1; not a separate mechanism.
- **W2 fractional handoff** — high complexity, unclear payoff; park for a later refine cycle.
- **W3 model-tier downshift on refresh** — orthogonal, separable follow-up optimization (ties to no-fable-subagents doctrine).

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | shotgun | 32 ideas across 8 axes (sensing / threshold / trigger / response / handoff / authority / enforcement+doctrine / wild) | Clustered to 8 families; culled 6 (parked); surfaced 4 strategic axes (Govern-vs-Prevent, Thin-vs-Rich-handoff, Reach-up-vs-Self-relay, Doctrine-fork). Not converged. |
| 1x | excursions X1 (handoff inventory) + X2 (prior art / Pocock) | Whether the governor handoff is thin/rich; what prior art to borrow | **X1:** cold-start is mostly FREE from engine state; the only new payload owed is 3 things (in-flight reasoning, running digest, voluntary-refresh-seam shape). **X2:** Pocock = manual reference-don't-duplicate handoff, no gauge/trigger; gauge+payload+self-trigger COMBINATION is open space; structured payload beats naive summary (arXiv). **Convergence:** both point to a THIN governor that rides engine artifacts + adds only the 3 missing pieces + a gauge. AX2 resolved. Not converged to spec — human decides direction. |
| 2x | excursion X3 (self-refresh capability) | Can an agent self-refresh on Claude Code / Codex CLI / pi.dev? | Claude Code CANNOT, Codex CLI CANNOT, pi.dev structurally CAN (build-it-yourself, not shipped). Reach-up works on all three; self-refresh is a pi.dev-only bonus. Subscription-billing constraint confirmed. **AX3 resolved in favor of reach-up.** |
| 2 | refine | Harden the converged direction: what the handoff carries, enforcement, who trips the refresh | Design crystallized (see Crystallizing design above): logging-discipline upgrade (engine-schema-enforced why at every non-mechanical gate; self-superseding digest) + free gauge-advice-at-gate trip (hook writes fill, engine advises) + reach-up refresh; symmetric recovery de-risks it. 9 decisions recorded in cycle-2.json. Remaining = spec detail, not exploration. Not converged — human's call. |
