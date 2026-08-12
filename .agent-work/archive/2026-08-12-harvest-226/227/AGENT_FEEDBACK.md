# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Each Commander run appends one entry at the `feedback` step, just before archive/commit. Purpose: capture where the workflow, skills, templates, or context made the work harder than it needed to be, so the doctrine improves over time.

This is workflow-improvement signal, not project truth. It accumulates across work-ids and is **never** archived or moved with a single run — it lives at the root of the agent work area and persists. Recurring entries are evidence for a Charter refresh or a template change. Distill a concrete interface/field/doctrine fix into a lesson carrying a `target`, settled at the Commander `feedback` step's forced apply-or-defer gate; use this log for the broader "how did the run actually go" retrospective.

Be honest. An entry that only says "went fine" teaches nothing. The useful entries name the exact step, field, or instruction that was ambiguous, missing, contradictory, or routinely improvised around. A `none` bullet requires a run-specific reason (`none — confirmed after review: <what you checked>`); entries whose signal sections are all bare `none` fail the feedback invariant check.

Newest entries on top.

---

## `2026-07-24` — `issue-227`

**Run shape:** `commander (delegated, Admiral launch order)` · spine init→archive + 12 execute gates closed (3 crew gates, 2 reasoning gates) · Commander opus, all crew sonnet, no Fable

**Instruction adherence:** `fully followed`
- Engine driven from the first command: spine claimed before any problem-solving, `current` consulted at every step, every deliverable produced inside a gated step. Two checklists driven (`spine.json`, `execute.json`), both leases released in order.
- PR-7 (verify-before-plan) was run BEFORE planning and materially changed the plan — item 1 turned out half-shipped, so effort moved to the real gap.
- Improvised in one place the instructions did not cover: `Agent(run_in_background: true)` is rejected at this tier ("In-process teammates cannot spawn background agents"), so the skill's "poll the crew's result artifact in a loop" guidance was implemented with synchronous dispatch plus in-turn polling on `SendMessage` reworks. Not a deviation from intent, but the skill assumes a capability this tier lacks.

**Friction / unclear:**
- **The launch order carried a factual error**: it stated `.agent-work/archive/` holds prior-epic transcripts usable as `measure_overread` corpus material. No raw JSONL transcripts exist there at all. This cost gate g1 a real corpus and forced a synthetic-but-labelled one. Real transcripts live outside the repo under `~/.claude/projects` and carry user conversation content that must not enter a public repo.
- **Two in-turn polling loops hit the 10-minute Bash ceiling** and had to be re-issued. With a 3-rework gate this was a recurring tax.
- **The rework cap counts rounds, not root causes.** Gate g3's four defects were four symptoms of ONE cause (fixture blindness) and consumed the entire 3/3 budget. A fifth symptom would have escalated a gate whose underlying problem was already understood.
- `py` vs `python`: `py` resolves to a pytest-less runtime on this box while `python` works. Every template that says `py scripts/...` is a latent false-red.

**Crew-reported friction:**
- g1 implementer: the handoff's "prior-epic transcripts" language implied raw JSONL logs live under `.agent-work/archive/`; none do. It had to independently locate the epic's own x1-overread excursion to learn the transcript schema.
- g2 implementer: the archived design-it-twice panel's exhibits use `attest --id t-3 …`, but the shipped CLI takes `id` POSITIONALLY. An implementer following the panel verbatim writes non-runnable commands. It also self-reported reading the handoff and beginning design before claiming its plan's engine lease, and corrected it via `git stash` to recover a genuine RED observation rather than fabricating one — an honest disclosure worth noting.
- g3 implementer: the handoff's recovery table did not say whether recovery keys off ACTUAL status or ATTEMPTED verb (it resolved to actual status, since that is what guarantees a runnable command), and did not cover `resume`-on-blocked-with-no-restorable-prior or `skipped`-status refusals.
- g3 reviewer (round 3): flagged that `Inv3ExclusionCheck` claimed totality while exercising only 4 of 10 excluded verbs — a self-confirming test shape that survived two rounds.

**What worked:**
- **The cold plan critic was the highest-leverage step of the run.** It caught, before any crew was dispatched, that g3's over-read baseline would be unproducible once g1/g2 overwrote the engine — a defect that would have invalidated item 5's acceptance entirely. It also pre-empted three self-confirming-test traps. All 10 findings were accepted and the plan was rewritten before freezing.
- **The rework loop did its job.** Three crew BLOCKs caught four real defects that I had not caught myself, in a surface where my own 640-combination sweep had returned clean — because my fixtures shared the same blind spot the tests did.
- **Design-it-twice was correctly pre-empted.** The archived panel settled both the `StateView` shape and its five invariants, so the "run it for a new load-bearing interface" clause did not fire. Reading all three candidates cost minutes and saved a panel.
- **The engine dogfooded its own fix mid-run**: after g3 landed I began piping engine calls through `tail -1` and it worked; after g2 the conditions block answered what I had been dumping `spine.json` to learn.

**Improvement signals:**
- A test that asserts on GENERATED ADVICE must EXECUTE that advice, over fixtures parameterized on every dimension the advice depends on (status AND position, here). → disposition: `distilled to a lesson with a target — deferred 'needs human' (doctrine apply requires authority=human; this Commander is delegated)`
- Strike or correct the launch-order template's claim that `.agent-work/archive/` holds usable transcripts. → disposition: `route to Admiral as a triage candidate (recommend-and-defer); constellation-scoped, exported`
- Make the cold plan critic MANDATORY (not bias-to-yes) for any gate plan whose acceptance depends on a before/after measurement. → disposition: `needs user decision`
- Correct the archived design-it-twice panel's CLI syntax, or note the divergence. → disposition: `distilled to a triage candidate`

---

## `<date>` — `<work-id>`

**Run shape:** `<commander | charter | ad-hoc>` · `<gates closed / steps run>` · `<subagent model tier(s) used>`

**Instruction adherence:** `<fully followed | minor deviations | material deviations>`
- `<where a skill / handoff / checklist was followed exactly, or where you had to improvise and why the instructions did not cover it>`

**Friction / unclear:**
- `<step, template field, context doc, or engine behavior that was ambiguous, missing, contradictory, or slowed the run>`

**Crew-reported friction:**
- `<lesson candidates harvested from Implementer/Reviewer Workflow Feedback sections at each gN-integrate — handoff gaps, rediscovered context, improvised instructions; or none reported>`

**What worked:**
- `<part of the workflow that carried its weight and should be kept as-is>`

**Improvement signals:**
- `<concrete change to a skill, template, context doc, or the engine that would have helped>` → disposition: `<none | distilled to a lesson with a target (applied or deferred at feedback) | route to Charter refresh | needs user decision>`

---
