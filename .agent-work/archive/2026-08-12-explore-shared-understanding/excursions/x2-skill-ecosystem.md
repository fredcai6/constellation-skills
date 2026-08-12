# X2 — The agent-skill teaching/explaining ecosystem (research result)

**Question:** What existing agent skills / tools aim to *teach a user concepts* or *explain code & changes to a human* — and which concrete mechanisms transfer to our setting (agents writing to one **expert-but-learning software architect**, per-user, in-flow)?

**Bottom line for the designer:** The closest existing thing is **Matt Pocock's `teach` skill** — steal its *learning-records-as-ADRs* state mechanism and its *mission-tethering*. Steal the *Socratic gate* from his `grilling` skill and the *freshness stamp* from our own `constellation-docent`. Treat PR-summarizers / IDE "explain" as a **mismatch** (audience-flat, on-demand, no memory). All of **superpowers** teaches the *agent*, not the *human* — a clean scoped null.

---

## 1. Matt Pocock's `teach` and `grill-me` — public structure found

His `.claude` directory is public: **github.com/mattpocock/skills**, `skills/productivity/`. All skills are single `SKILL.md` files with `disable-model-invocation: true` (user-invoked only). Structure confirmed by fetching the repo, not the blog.

**`teach`** (`skills/productivity/teach/SKILL.md`) — *"Teach the user a new skill or concept, within this workspace."* Uses **the current directory as a stateful teaching database** across sessions. Files it maintains:
- `MISSION.md` — the learner's underlying reason for learning; **every lesson must tie back to it**.
- `NOTES.md` — durable user preferences / teaching notes for cross-session consistency.
- `learning-records/NNNN-<name>.md` — sequential, numbered records of *non-obvious insights and decisions that may evolve*, explicitly **"loosely equivalent to architectural decision records."** Used to compute the learner's **zone of proximal development** so each lesson challenges "just enough."
- `lessons/NNNN-<name>.html`, `reference/*.html`, `RESOURCES.md`, `assets/*` — self-contained lesson/reference artifacts.

**`grill-me` / `grilling`** — a relentless one-question-at-a-time interview that walks a **decision tree**, resolving dependencies between decisions one by one. Key rules quoted: *"Ask the questions one at a time… Asking multiple questions at once is bewildering"*; *"If a **fact** can be found by exploring the environment… look it up rather than asking me. The **decisions** are mine"*; and a hard gate: *"Do not act on it until I confirm we have reached a shared understanding."* (`grill-me` itself is a 7-line trigger that just runs `/grilling`.)

**Transfers:** (a) **learning-records-as-ADRs** — a persisted, append-only, numbered ledger of what the human already understands, so the agent calibrates depth instead of re-explaining or over-explaining; this is the single most reusable idea for an *expert-but-learning* audience. (b) **Mission-tethering** — anchor every explanation to *why this human cares*, not generic pedagogy. (c) **Fact/decision split** — look up facts, surface only genuine decisions to the human (already native to constellation's Commander posture). (d) **Shared-understanding confirmation gate**.
**Does NOT transfer:** the *multi-session HTML lesson course* framing — heavyweight, out-of-flow, and pitched at a *novice* learning a new domain from scratch. Our setting is **in-flow, expert audience, incremental** (explaining *this change/decision*), not a curriculum. The `.html` lesson/reference machinery is overkill.

## 2. "explain-diff" / change-explaining tools

**GitHub Copilot PR summaries** (docs.github.com/en/copilot/how-tos/…/create-a-pr-summary) — a workflow feeds **raw diffs of summarizable files into a single generic-LLM prompt** ("simple-prompt flow, no additional trained models") and returns a **two-part output: a prose overview paragraph + a bulleted list of changes keyed to files.** "Ask about this diff" does the same per-hunk. **Depth decision: essentially none** — fixed template, same output regardless of reader.
**Cursor / IDE "explain"** — select code, `Cmd+L`, type "explain"; **context-aware** (current file, cursor, project) but **manual, on-demand, no persistence, no audience model**. There isn't even a dedicated command (open feature request).

**Transfers:** the **prose-overview + file-keyed bullets** two-part shape is a good default rendering for "what this change does," and **diff-as-primary-context** is the right input. Copilot's *responsible-use* framing (summaries can be wrong; human verifies) matches docent's freshness ethos.
**Does NOT transfer:** these are **audience-flat and stateless** — they explain the *artifact* to *anyone*, never model *this* reader's prior knowledge, never remember what was already explained, and don't decide depth. For a per-user expert who is *learning the system over time*, a memoryless summarizer is the wrong altitude; it re-explains basics forever and never goes deep where the expert is actually reaching.

## 3. Broader ecosystems — concrete examples + mechanism

- **`codebase-onboarding` skill** (github.com/affaan-m/everything-claude-code, also widely forked) — four phases: **reconnaissance → architecture mapping → convention detection → artifact generation** (an onboarding guide + starter `CLAUDE.md`). Depth heuristic: **signal-based, not exhaustive** — *"reconnaissance should use Glob and Grep, not Read on every file,"* verify against code when config conflicts. Some forks (alirezarezvani/claude-skills) add explicit **audience framing (junior vs. senior lead)**; the affaan-m base version does **not** — single "scannable in 2 minutes" target. *Transfers:* signal-first recon and the audience-framing idea. *Does not:* it's a **one-shot orientation for a newcomer to an unfamiliar repo**, not incremental teaching of an owner who already knows the system.
- **`constellation-docent` (local, ours)** — generates a **self-contained static HTML explainer site from Cartographer map truth**, one page per packet, with a **SHA-256 freshness stamp** embedded in every page (`docent_freshness.py stamp|check`) so a stale site self-flags. *Transfers strongly:* **"a stale explanation that looks authoritative while lying is worse than none"** — any teaching artifact we persist needs a freshness/provenance stamp tied to source truth. *Does not:* docent is **on-demand, whole-map, read-only, one human broadly** — not per-change, in-flow, or personalized to one reader's knowledge state.
- **superpowers plugin** (`~/.claude/plugins/.../superpowers/6.1.1/skills/`) — inventory (brainstorming, TDD, systematic-debugging, writing-plans, executing-plans, subagent-driven-development, writing-skills w/ `persuasion-principles.md`, verification-before-completion, code-review pair). **Scoped null: every one teaches the *agent* a process; none explains code or a change *to the human*.** The nearest adjacency is `writing-skills/persuasion-principles.md` (how to make instructions land) — a rhetoric reference for *authoring*, not a per-reader teaching mechanism. Evaluated, does not transfer as a teaching tool.
- **Marketplaces (claudemarketplaces.com, tonsofskills/ccpi, mhattingpete)** — thousands of skills; the teaching-relevant cluster is uniformly **"onboarding / codebase-explainer / doc-generator"** — batch documentation artifacts for *a team / new hires*, audience-generic, stateless. None found that models *one named reader's evolving understanding in-flow.* (Scoped null: searched marketplace + GitHub for "tutor/onboarding/codebase explainer"; the personalized-expert-reader niche appears unfilled — Pocock's `teach` is the lone state-carrying tutor, and it's novice-course-shaped.)

## 4. Steal / mismatch / closest-existing summary

| Mechanism | Source | Verdict for our setting |
|---|---|---|
| **learning-records/NNNN.md as ADRs → compute what to explain & how deep** | Pocock `teach` | **Steal.** Best fit for expert-but-learning; solves depth calibration + no-re-explain. |
| **Mission-tethering** (every explanation → why *this* human cares) | Pocock `teach` | **Steal.** |
| **One-question Socratic gate; fact/decision split; shared-understanding confirm** | Pocock `grilling` | **Steal** (already congruent with Commander). |
| **Freshness/provenance stamp on any persisted explainer** | our `docent` | **Steal.** Prevents authoritative-but-stale teaching. |
| **prose overview + file-keyed bullets, diff-as-context** | Copilot PR summary | **Steal the shape** for per-change explanation. |
| **Signal-first recon (Glob/Grep not Read-all)** | `codebase-onboarding` | Steal for cost control. |
| **Audience-flat, stateless, on-demand summarizing** | Copilot / Cursor / marketplace explainers | **Mismatch** — no per-reader memory, no depth decision, out-of-flow. |
| **Multi-session HTML lesson *course*; whole-map site** | Pocock `teach`; `docent` | **Mismatch** — novice/broad framing, too heavy for in-flow incremental expert teaching. |
| **Agent-process skills** | all of superpowers | **Null** — teach the agent, not the human. |

**Closest existing thing to what we want:** Pocock's `teach` skill's **state layer** (`MISSION.md` + `learning-records/` ADRs driving zone-of-proximal-development), re-pointed from a novice HTML course to **in-flow, per-change explanation for one expert architect**, with a docent-style freshness stamp on whatever we persist.

### Sources
- https://github.com/mattpocock/skills (repo root; `skills/productivity/` index)
- https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md (+ `grill-me/SKILL.md`)
- https://docs.github.com/en/copilot/how-tos/copilot-on-github/copilot-for-github-tasks/create-a-pr-summary and .../responsible-use/pull-request-summaries
- https://forum.cursor.com/t/feature-request-dedicated-explain-code-command/147925 (Cursor "explain": manual, context-aware, no dedicated command)
- https://github.com/affaan-m/everything-claude-code/blob/main/skills/codebase-onboarding/SKILL.md ; https://claudemarketplaces.com/skills/alirezarezvani/claude-skills/codebase-onboarding
- Local: `C:\Users\fredc\.claude\skills\constellation-docent\SKILL.md`
- Local: `C:\Users\fredc\.claude\plugins\cache\claude-plugins-official\superpowers\6.1.1\skills\` (inventory — all agent-facing; scoped null)
