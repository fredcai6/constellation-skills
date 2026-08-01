# Ideas Board — `explore-skill-simplification`

The living record of shared understanding and the **source of truth** for this exploration. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history; a mid-exploration shelve files *this file* as the shaped-design issue, loudly marked unconfirmed. Keep it current — it is what survives a reopen cascade.

## The point

Cleanup & simplification pass over the constellation skills. Inspiration: Pocock's skill-authoring rules — (1) intentionally tailor each skill to human-invoked vs agent-invoked, (2) choose wording that resonates with agents / use the right terms, (3) keep skills short and offload to template files. Skills have accumulated layered lessons from usage (PRs #21–#31 fold-back arc, #99/#100 design-it-twice generalization, etc.); expect significant simplification opportunity. Also survey current external best practices for skill authoring.

**Q1 — the itch:** no specific pain. Rapid expansion prompts a periodic touch-up; preventive — clean up before agents start struggling. Corpus hygiene guided by external best practice + measurement, not incident response.

**Q2 — for whom:** primary — the agents loading the skills (token cost per run; duplication-with-drift → stale-wording follows). Secondary — maintainer (patch doctrine once, not 14×). Human decides solved; real judge is downstream runs not tripping.

**Q3 — done feels like:** every SKILL.md reads as one deliberately-written doc, absorbable in one pass; doctrine lives exactly once, skills point rather than restate; each skill visibly invoker-tailored; descriptions do the selection work. **Rejected:** anti-re-accretion conventions as a goal — accrete-then-consolidate is the accepted lifecycle; this is periodic maintenance. Lightweight organizing conventions OK, not a success criterion.

**Q4 — what exists:** the bones are right (`_shared/global-*`, relationship contract, cartographer as factoring exemplar); adherence fell short (lessons landed inline, nothing deleted). **Human amendments:** superpowers skills on this box to be removed — constellation is a competitor; don't lean on their doctrine (tension with ROADMAP's superpowers-imports arc — open thread). Sanctioned idea: a periodic corpus-maintenance skill that applies authoring doctrine to the skills themselves.

**Q5 — kill condition:** broad one already dead (x2: corpus is not lean). Live narrow kill: if consolidating into `_shared` hurts agents at runtime (missing inline doctrine; pointer-chasing > duplication saved), the consolidation half dies, leaving per-skill tightening. Constraint: consolidation must preserve what each role actually sees at runtime — checked, not assumed.

## Current candidates

All 24 shotgun ideas survived human consolidation (cycle 1). Clustered:

- **A — Single-sourcing dedup batch** (ideas 1–10): each duplicated doctrine gets exactly one home (`_shared/global-everyone.md`, fleet-doctrine, or existing shared refs); skills carry pointers. Targets: mandatory-compliance boilerplate (×10), engine-invocation string (×10), FOLLOW-STRICTLY banner (×6, delete outright), scoped-nulls, unchanged-tree shortcut, crew-idle adjudication (×3), delegate-not-replacement, dedup-sibling-ids, world-verification, design-it-twice restatements.
- **B — Per-skill diets** (11–15): commander gets a `references/` dir (crew-backend lore out of body); admiral's 12-bullet field-lessons list folds into fleet-doctrine; interrogator rewritten agent-first; docent HTML-constraints extracted; historical/PR-number framing rewritten as current truth.
- **C — constellation-curator** (23, absorbs 16–20): **CONVERGED (cycle 2): measure-then-mend hybrid** — `curate_corpus.py` script core (deterministic; flags-never-gates enforced in code; baseline drift diff), mechanical mends applied in place (human-invoked, git-reviewed, no engine checklist — triage precedent), design decisions routed to Triage. Human-only invoker; agent-audit mode = untaken road. Full comparison: `excursions/c2-x1-curator-dit.md`.
- **D — Hygiene quick fixes** (21–22): **delete** manifest.json (verified dead — nothing reads it); stray junk file at repo root; typo sweep.
- **E — Skill eval harness** (24): **CONVERGED (cycle 3): autonomous, Euler-piloted.** `scripts/run_skill_eval.py` + `evals/` scenarios: fixture repo, task prompt driving a real workflow (commander on a bounded Project-Euler issue with crew dispatch), mechanical checks executed by the runner (answer correct, tests green, artifacts present, spine JSON completed). Fresh headless agent per run; computed pass/fail; transcript for diagnosis only. Not a skill (deletion test). Curator owns scenario-portfolio curation — downstream failures don't flow back, so autonomous runs are the substitute signal; portfolio stays mixed (Euler alone won't stress architecture judgment). Bar (cycle 2): situational, no Iron Law. Still **tackle last**.
- **F — Entry-split for heavy both-invoked roles** (cycle-2 human-raised): commander and interrogator each become two entry-only skills (human entry + delegated/agent entry) over a **joint core reference** — single source, no competing instructions in one context. Installer supports today (per-skill bundle map or cross-skill absolute-path pointer, precedent `checklist-engine.md`); never mint new `global-*.md` names (test glob pins). Shallow both-skills (cartographer, scout, triage, prototyper) keep a one-line mode note. **Supersedes B13** (interrogator agent-first rewrite).

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Corpus is NOT lean — duplication and layering confirmed with measurements | Tested: all 14 SKILL.md files, grep for signature phrases, sizes. NOT tested: template-body diffs; installed (vs source) skill weight | cycle-1 / x2 |
| External best practice corroborates Pocock's 3 rules + adds description-discipline, length budgets, one-hop disclosure, eval-driven authoring | Tested: Anthropic docs/blog, obra, Pocock written traces, community distillations (~12 sources). NOT tested: deleted video content; deep HN/community sampling | cycle-1 / x1 |
| Accrete-then-consolidate is the accepted lifecycle; no anti-re-accretion machinery | Human decision (q3) — rejects prevention conventions as a goal, open to lightweight organization | cycle-1 / q3 |
| Superpowers is a competitor: remove its skills from this box; don't lean on its doctrine | Human decision (q4). NOT decided: fate of ROADMAP superpowers-imports arc | cycle-1 / q4 |
| Description rule: triggering conditions (what / when / when NOT), never procedure | Adjudicates Anthropic-vs-obra. Applies to all 14 descriptions | cycle-2 / q1 |
| Register rule: rule-plus-why default; emphasis only at rationalization-prone gates AND backed by a mechanical check; free-floating banners deleted | Adjudicates imperatives-vs-why | cycle-2 / q2 |
| Eval bar: situational, no Iron Law — fresh-context eval for new/behavior-changing skills; tests+git review for mechanical edits; curator flags, never gates | Adjudicates eval-rigor contradiction | cycle-2 / q3 |
| Descriptions: precision over pushiness; exclusion clauses only for real confusable pairs (scout/cartographer, explorer/interrogator, admiral/commander, curator/scout+write-a-skill); none for name-dispatched crew | Blanket clause rejected as accretion | cycle-2 / q4 |
| Superpowers resolution: box removal = separate chore; ROADMAP arc reframed as constellation-native items, imports framing dropped | Closes cycle-1 open thread | cycle-2 / q5 |
| Entry-split where heavy: commander + interrogator → two entry skills over joint core reference; shallow both-skills keep a mode line | Supersedes B13. Untaken: entry blocks; uniform split; primary-audience-only | cycle-2 / q6 |
| Curator = measure-then-mend hybrid, human-only | Panel of 3 compared; pure candidates = untaken roads | cycle-2 / c2-x1 |
| Cluster-A dedup GO with bucket rules; append to existing bucket files only; manifest.json dead; handoff templates stay separate | Tested: installer code, installed copies, test pins. NOT tested: byte-identity of inline wordings; suite not executed | cycle-2 / c2-x2 |

## Open threads

- **Eval harness minimal shape** (cluster E): how minimal can Claude-A/Claude-B be? Bar is decided (situational); the harness mechanics are not. Tackle last per human — can be spec'd as its own follow-on if needed.
- **Wording reconciliation per dedup move** (execution detail): inline copies drift; each cluster-A move is reconcile-then-cut, not pure cut-paste. Per-move carrier lists to re-confirm against final wording.
- **Invoker classification ratification**: x2's draft (with workbench/interrogator flagged uncertain) gets ratified when tags are applied.
- *(Closed this cycle: superpowers reconciliation; all four x1 contradictions; curator shape; runtime-context check; manifest.json; handoff-template diff.)*

### Excursion Brief: `c2-x1-curator-dit`

**The one named question:** What is the right interface/shape for `constellation-curator` — the periodic corpus-maintenance skill that applies authoring doctrine (description pass, invoker tagging, terminology sweep, soft word budgets, TOC rule, x2-style measurement) to the constellation skills corpus itself?

**Type:** design-it-twice — compare interfaces under distinct constraints (shared contract: `_shared/references/design-it-twice-brief.md`).

**What "answered" looks like:** an opinionated recommendation or named hybrid — the skill's trigger/description, its checklist spine, its evidence contract, and its seam with existing roles — compared on depth / locality / seam placement / testability, landing at `excursions/c2-x1-curator-dit.md`.

**Parallel agents (3, distinct constraints):** (1) **minimal-interface** — smallest possible skill, maximum lean on existing roles/refs; (2) **scout-analog** — mirror the established audit-role pattern (map-first evidence, ranked report, triage handoff); (3) **measurement-first** — the skill is built around the metrics/checks, prose is secondary.

**Budget / stop conditions:** design only, no implementation; each agent reads x1/x2 excursion results + 2–3 exemplar SKILL.md files; report even if a constraint produces a degenerate design (scoped nulls).

### Excursion Brief: `c2-x2-runtime-context`

**The one named question:** What does each role actually see at runtime after install — and would cluster-A dedup (moving doctrine to `_shared`) change what any role sees?

**Type:** research — codebase verification (installer/bundling behavior).

**What "answered" looks like:** a verified statement per tier (orchestrator/crew/everyone) of which reference files get bundled into which installed skills; whether `manifest.json` is read by anything; and a body-diff of IMPLEMENTER_HANDOFF vs REVIEWER_HANDOFF templates — landing at `excursions/c2-x2-runtime-context.md`.

**Budget / stop conditions:** read-only; check `scripts/` installer code + manifest consumers + installed copies under `C:\Users\fredc\.claude\skills\`; no edits; scoped nulls apply.

## Excursion results (on-ramp)

- **c2-x1-curator-dit** — LANDED (panel of 3 + comparison, `excursions/c2-x1-curator-dit*.md`). Candidates: minimal-interface (human-only, no engine, edits in place), scout-analog (audit-only spine, routes to Triage), measurement-first (deterministic script, flags-never-gates in code, baseline diff). Agent recommendation: hybrid **"measure-then-mend"** — script core + in-place mechanical mends + Triage routing for design decisions; no engine checklist; human-only invoker (agent-audit mode = untaken road). **Human pick pending.**
- **c2-x2-runtime-context** — LANDED, `excursions/c2-x2-runtime-context.md`. Installer bundles `_shared` per `SKILL_REFERENCE_BUNDLES` (install_constellation.py:98–113). **All cluster-A moves GO** with bucket rules: cross-tier doctrines (mandatory-boilerplate, engine string, scoped-nulls, world-verification) → `global-everyone.md`; orch-only pairs (unchanged-tree, crew-idle, delegate-not-replacement) → `global-orchestrator.md`. q5 kill condition defused — no role loses doctrine. Tests pin bundle sets via `global-*.md` glob → append to existing bucket files, never new `global-*.md` names. `manifest.json` is dead (nothing reads it) → delete. IMPLEMENTER/REVIEWER handoff templates genuinely differ → leave separate (idea 25-adjacent uncertainty resolved). Not checked: byte-identity of inline wordings (dedup = reconcile near-duplicates, not pure cut-paste).

- **x2-corpus-survey** — LANDED, `excursions/x2-corpus-survey.md`. Corpus is bimodal: commander (113 ln / 2580 w), explorer (99 / 1695), docent (152 / 1110) heavy; other 11 skills lean (24–72 ln). 9 duplication clusters, top three: mandatory-compliance boilerplate verbatim in **10** SKILL.md files; engine-invocation string restated in ~10 with drift; "FOLLOW THIS SKILL STRICTLY…" in 6. Layering epicenter: commander (unchanged-tree shortcut, crew-idle adjudication stated in 3 places, 250-word crew-backend paragraph) and admiral's 12-bullet "learned from field fleets" list. Mis-tailoring: interrogator written human-first but mostly agent-loaded; manifest.json lists 11/14 skills (explorer, prototyper, docent missing). Uncertain: which tier-local restatements are deliberate; template bodies not diffed (IMPLEMENTER/REVIEWER_HANDOFF ~equal size, unconfirmed).

- **x1-best-practices** — LANDED, `excursions/x1-best-practices.md`. 12 cited themes. Key levers beyond Pocock's three: description field is the dominant lever (3rd person, what+when, exclusion clause); "context window is a public good" — <500 lines hard, obra: <200–500 *words*; progressive disclosure one hop deep, TOCs on >100-line references; degrees-of-freedom matched to task fragility; workflow checklists + feedback-loop gates; consistent terminology, no time-sensitive text, gotchas section; eval-driven authoring (Claude-A/Claude-B loop, test across model tiers); named anti-patterns (option menus, nested refs, generic labels). Scoped null: Pocock's deleted video content not recovered — three rules corroborated in writing; video-only extras unconfirmed, not disproven.

## Excursion briefs

### Excursion Brief: `x1-best-practices`

**The one named question:** What do current (mid-2026) authoritative and community sources say makes an agent skill effective — description wording, human- vs agent-invoked tailoring, length/progressive disclosure, structure — beyond Pocock's three rules?

**Type:** research — facts and prior art from primary sources.

**What "answered" looks like:** a cited findings list (each claim carries its source) of concrete skill-authoring rules/heuristics, with contradictions surfaced, landing at `excursions/x1-best-practices.md`.

**Budget / stop conditions:** ~10–15 sources max; web only; do not audit our skills (that is x2); report even if inconclusive. Scoped nulls apply.

**Sources:** Anthropic docs/blog (Agent Skills authoring guidance), Matt Pocock (aihero.dev, X posts — the video is deleted, look for its written traces), obra/superpowers writing-skills doctrine, community posts (HN, Reddit, engineering blogs).

### Excursion Brief: `x2-corpus-survey`

**The one named question:** Where, concretely, is the constellation skills corpus heavy, layered, duplicated, or mis-tailored to its invoker (human vs agent)?

**Type:** research — codebase survey, measurement-driven.

**What "answered" looks like:** a table per skill (SKILL.md line/word count, template/reference/script counts and sizes, invoker classification human/agent/both, top redundancy findings) plus a cross-cutting duplication list, landing at `excursions/x2-corpus-survey.md`.

**Budget / stop conditions:** read-only survey of `skills/` (+ installed copies only if needed for parity checks); no edits; no proposals beyond flagging (shotgun ideas are the main session's job); report measurements even where judgment is uncertain. Scoped nulls apply.

**Sources:** `skills/` tree in this repo, `docs/CONSTELLATION_OVERVIEW.md` relationship contract, git log for layering history.

## Triage candidates (future work, not this pass)

- **Canonize the issues/specs ↔ architecture interplay** (human, 2026-07-09): how shaped specs, cut issues, and the Cartographer architecture map relate is currently un-canonized; human has strong feelings, deliberately deferred. Record in `docs/ROADMAP.md` (rides cluster D).
- **Interrogator closes too aggressively** (human, 2026-07-09): interrogation runs need an explicit human sign-off that the questioning is actually finished — the agent currently decides it's done too eagerly. Roadmap item; folds into a larger evaluation of Pocock's 1.1 skills release for importable lessons. Record in `docs/ROADMAP.md` (rides cluster D).
- **Permanent base rigor rules; simpler charter setup** (human, 2026-07-09, during critic triage): Constellation was originally designed to vary rules of rigor per project, but the real user is its author, who wants rigor and accepts its cost. Candidate: promote the author's base rules from per-project charter configuration to permanent defaults, and simplify initial project setup (charter interrogation) accordingly — fewer knobs, faster onboarding. Record in `docs/ROADMAP.md` (rides cluster D's roadmap edit).

## Rejected ideas (with reasons)

- Anti-re-accretion conventions/machinery — human: accrete-then-consolidate is the lifecycle; prevention over-constrains and loses lessons. Revive only if consolidation cadence proves insufficient.
- Blanket exclusion clause in every description — boilerplate accretion; clauses only where a confusable neighbor exists.
- Iron-Law TDD-for-skills (obra) — over-machinery for this corpus; situational eval bar instead.
- Pushy/over-eager descriptions — suite siblings would steal each other's triggers; precision instead.
- Entry blocks in one SKILL.md (option B) and uniform entry-split (option A) — human prefers no competing instructions in context; split only where heavy. Revive B if skill-count growth becomes a real cost.
- Interrogator agent-first single-audience rewrite (B13) — superseded by entry-split.
- Factoring IMPLEMENTER/REVIEWER handoff templates into a shared base — verified genuinely different; dedup would fight role-specific wording.
- ROADMAP "superpowers imports" framing — competitor; ideas kept as constellation-native items.

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | shotgun | Starting questions + 2 research excursions (x1 best practices, x2 corpus survey) + 24-idea sweep | All 24 kept; clustered A–E; 23 absorbs 16–20; E last. Open: superpowers reconciliation, x1 contradictions, curator shape. |
| 2 | refine | 4 contradiction adjudications + superpowers + human-raised entry-split (q6); excursions: curator design-it-twice panel (c2-x1), runtime-context verification (c2-x2) | All decided: description/register/eval/exclusion rules; curator = measure-then-mend; cluster F entry-split-where-heavy added (supersedes B13); cluster A verified GO; manifest dead. Open: eval-harness mechanics, per-move wording reconciliation, invoker-tag ratification. |
