# Roadmap notes

Forward-looking threads deliberately not yet cut into issues. Each entry names its origin so the context is recoverable when it's picked up.

## Execution-discipline hardening

Origin: 2026-07-09 research synthesis behind #99 (design-it-twice generalization). The design phase is now constellation's strength — parallel alternatives + cold critic panels, both mechanized. What's left is sharpening the **execution** phase; each candidate below is evaluated against the deletion test (if we removed this, would something concrete break?) before it gets cut into an issue:

- **Durable progress ledger** that survives compaction/session death, layered onto our STATE_NOTE + crew registry, which today records process state rather than per-task outcomes.
- **File-based handoff hygiene** for controller-context economy (task-brief/report/review-package scripts keeping the orchestrator context clean).
- **Explicit model-tier selection per role** (cheap implementers, strongest model for the final broad review) — we say "pick tier from complexity" but don't mechanize it.
- **Pre-flight plan-conflict scan** before executing a frozen plan.

Related unshipped-elsewhere idea already landed here instead: competitive-critic mode (opt-in) in the critical-review standard.

## Permanent base rigor rules + simplified charter setup

Origin: 2026-07-09 epic-101 hygiene pass (#105). The author is the real user of these rules, not a hypothetical broader audience; rigor is worth the cost it imposes, so the default should assume it rather than make it opt-in.

- Fold the currently scattered rigor expectations into a small set of permanent base rules rather than per-project configuration.
- Simplify constellation-charter's setup path to fewer knobs — reduce the number of choices a fresh repo has to make before it can adopt the doctrine.

## Canonize issues/specs ↔ architecture interplay

Origin: 2026-07-09 epic-101 hygiene pass (#105). Deliberately deferred: the human has strong feelings about how issue/spec authoring and the architecture map (`docs/architecture/`) should check each other, and wants to weigh in directly before this is designed rather than have an agent propose a shape first.

- Decide which of issues/specs and the architecture map leads and which follows as both evolve, and where each one is allowed to override the other.

## Interrogator finish-gate

Origin: 2026-07-09 epic-101 hygiene pass (#105).

- Add an explicit human sign-off step confirming constellation-interrogator's questioning is actually complete, not just that the loop terminated.
- Fold this gate into the Pocock 1.1-release evaluation rather than shipping it as a standalone mechanism.

## LESSONS.md is an inbox, not a playbook — graduate-and-delete

Origin: 2026-07-10 epic-101 closeout (human direction, superseding the earlier "aggressive clearing" phrasing). Characterizing LESSONS.md as a "playbook" was the mistake: it implies long-term residence, so lessons hang around as a quasi-permanent doc. Lessons are transitory by nature — an audited lesson should be ENDED: anything useful is categorized and moved into the permanent doc that owns it (a template, a skill's doctrine section, a reference, or a code-fix issue); everything else is deleted with a reason. The cap and dormancy clock become largely moot once residence is short by design.

- Reframe LESSONS.md's header + the lessons-auditor and admiral closeout doctrine from "playbook" to "inbox/staging": audit = graduate-or-delete, never leave-active. **Done (#119):** lessons-auditor SKILL.md, admiral SKILL.md + ADMIRAL_SPINE closeout imperative, and fleet-doctrine.md now carry the inbox / graduate-and-retire framing; the live LESSONS.md header is reframed by the Admiral at delta-apply time.
- First graduation pass over the current 20 active lessons is immediate work (issue filed at closeout). **Done (#119):** all 20 graduated to their permanent homes (commander-core, the handoff/reviewer/launch-order/admiral-spine templates, checklist-engine.md, CHECKLIST_SCHEMA.md) or cited to a code-fix issue (#118); the ready-to-apply retire delta is staged for the Admiral to apply post-merge.
- Standing feedback-log grooming (AGENT_FEEDBACK / CONSTELLATION_FEEDBACK) moves to the curator's periodic run — the learning logs are corpus too.
- Ties into the queued dormancy-mechanism note (tick-burst culling); that machinery may shrink or disappear under this model. **Assessment (#119):** under short-by-design residence the active cap (20) is rarely approached and the tick-based dormancy auto-delete mostly never fires — audits retire lessons well before the dormancy horizon, and the tick clock already caused one false-cull (the re-added `verify-launch-order-baseline-vs-code`). Keep the `retire` op (it *is* the deletion path) and the grounding/counter enforcement; the tick-based auto-delete is now vestigial and can be removed in a follow-up rather than here.

## Plain-language register — rein in the project sub-dialect

Origin: 2026-07-10 epic-101 closeout (human direction). Sessions have grown jargony: a technical human reports the project-specific sub-dialect (spines, gates, waves, harvests, durable trios, honest nulls...) is blowing past them. The vocabulary is load-bearing for agents but must not price the human out of their own project.

- Human-facing surfaces (checkpoint summaries, reports, epic summaries, interrogator/commander human entries) should default to plain language, with the term of art in parentheses on first use at most.
- Consider a small glossary the docent/curator maintains, and a register rule: project dialect is for agent-to-agent artifacts; human-facing text explains itself.
- Curator lint candidate: flag doc surfaces tagged human-facing whose density of coined terms exceeds a heuristic.

## Cross-harness compatibility: Codex as well as Claude

Origin: 2026-07-10 epic-101 closeout (human direction). Skills today assume the Claude Code harness (Skill tool, Agent-tool subagents, `claude -p` headless, permission classifier behaviors). Constellation should be loadable from Codex-family agents too.

- Audit hard Claude-isms: harness-specific tool names in doctrine, `claude` CLI invocations in scripts (run_crew backends, run_skill_eval launch seam), permission-model assumptions.
- The eval runner's injectable launch seam is the right shape — extend the backend pattern (cli/external) to a codex backend where dispatch is needed.
- Keep SKILL.md bodies harness-neutral; isolate harness bindings in per-harness reference files (precedent: `_shared/windows.md` for platform quirks).

## Engine-carried guidance — the rail reminds, not just the skill

Origin: 2026-07-11, #126/#129 wording arc (human direction: "use the engine response itself to remind the agent what the next step is and why it's important... keep pulling that thread"). Round-1/round-2 wording clamps the START hard, but mid-run wander and quit-early remain exposures: skill-load-time text decays over a long run, while engine output arrives exactly at each decision point.

- Candidate: `advance`/`current` responses carry the next step's imperative plus a one-line WHY (completion stakes), e.g. "execute advanced. NEXT: reconcile — a run that stops here has failed; N steps remain to terminal archive."
- Candidate: terminal-distance in every mutating response ("3 steps from archive") — cheap progress pressure.
- Measure with the #129 harness: wording-only vs wording+engine-nudges at the low tier.
- See also #134 (fold into the same engine design pass if cut together).

## Morale doctrine — single source, machine-delivered

Origin: 2026-07-11 (human direction). The catalogued cheap-exit failures — skip, quit-early, give-up-after-one-null, fabricate — are one family; the counter-doctrine must live in ONE canonical text ("pep talk"), not scatter across skills. A "don't give up" SKILL is the wrong container: an agent won't voluntarily load discipline at its weakest moment — delivery must be machinery.

- One canonical block: process defines done; a failed variant is a scoped null (try another); asking up is ALWAYS legitimate; the two forbidden exits are quiet abandonment and fabrication. (Perseverance without the ask-up clause breeds fabrication.)
- Delivery channels: (1) engine responses — advance carries next-step + why + distance-to-done; check-failure responses carry the scoped-null/ask-up line (the give-up moment interceptor); (2) re-injection on compaction — mid-run "you are mid-spine, N steps remain" + pep talk (the epic-101 diet stripped load-time clamping from skill bodies; it returns machine-delivered, not as boilerplate); (3) skills keep one-line pointers (single-sourcing pattern).
- Measure per channel with the #129 harness: wording-only vs +engine-nudges vs +compact-reinjection.
- See also: "Engine-carried guidance" section above, #134.
