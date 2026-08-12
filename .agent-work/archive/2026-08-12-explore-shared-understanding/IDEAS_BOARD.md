# Ideas Board — `explore-shared-understanding`

The living record of shared understanding and the **source of truth** for this exploration. Every consolidation updates it. The spec crystallizes from it; a resumed session reads it instead of chat history.

## The point

> **Sharpened after cycle-1 point-questions (human answers, voice).**

**The itch:** We build fast (good) but not *understandably* (bad). Agents run with the user's seed and (1) reach for concepts the user hasn't met, backed by enough proof that the user goes along without owning them; (2) accrete emergent jargon. The Interrogator handles only the front door; drift happens continuously after. **Crucial refinement:** the goal is NOT to ban jargon — the user is expert enough to *want* precise jargon and does not want to be talked down to. The real targets are two: **(a) real-world / industry concepts the user hasn't met yet** (canonical example: a *Matérn process* — the user hit a reference to it, didn't know it, found it super useful, and simply wants to *learn* these); and **(b) internal / project-invented jargon**, which the user is *much less tolerant of* — especially because they run **many projects at once**, so hyper-specific per-project dialect is almost never worth it. Also wanted: **solid, consistent plain-language explainers of what the code is actually doing** (the curator plain-language thread poked at this but it needs to be consistent).

**For whom:** the human architect — an **expert in the domain who lacks formal statistics / engineering-analysis training**, learns by *doing* not by classes (has a master's; resists school-for-school's-sake because these projects take them in more useful, exciting directions). Wants **peer register**, not condescension, but is humble enough to want to learn.

**What "done" feels like:** agents talk at peer level with precise jargon allowed; unfamiliar *real-world* concepts get taught briefly *when the user is in the mood* (an off-ramp, not forced); a running record of what's been discussed and how well the user knows it; natural re-explanation when a concept recurs; durable plain explainers at build milestones; and a **better-than-honor-system** mechanism for plain talk.

**Target grade of understanding:** **B — understand a concept well enough to make the call that rides on it — reaching for C (could explain/rebuild it)** where it matters. Not mere non-surprise (A).

**Kill condition:** **none obvious** (human: no hard kill). Soft anti-goals instead — it's *pointless / wrong* if it (i) becomes heavy machinery for its own sake (scores/dashboards over a light record + discipline), (ii) bans or discourages *precise* jargon, or (iii) talks down to the user.

## Current candidates

> Floated by the user in the raw idea. Recorded as candidates to develop — **not** decisions. Deliberately not yet chosen among.

- **C1 — Plain-talk mandate.** A rule that human-facing output uses plain talk: no unagreed shorthand, jargon limited and grounded in the user's understanding, patient teaching on first use.
- **C2 — Concepts book (next to the glossary).** A tracked list of the concepts the project is built with, each with an *estimate of the user's familiarity*, so agents can pitch at the user's level and the user can watch their own understanding grow.
- **C3 — Tutor agent.** A dedicated agent that teaches the user the concepts in play (user cites Matt Pocock's work in this space).

### Cycle 1 shotgun — raw divergent ideas (not yet culled)

*Five families. Cheap one-liners; wild entries welcome; nothing chosen.*

**A — Register / talk mandates (how agents phrase things)**
1. Plain-talk-by-default with actual teeth (enforce the existing 2026-07-10 memory, don't just restate it).
2. No unagreed shorthand: an agent can't use a coined term with the user until it's been "unlocked" (introduced + acknowledged).
3. First-use gloss required: every coined term carries a one-line plain gloss the first time it appears in human-facing text.
4. User-set register dial: "explain like I'm new here" ↔ "talk to me as a peer"; agents read it and adjust.
5. Jargon budget: cap undefined coined terms per human-facing message (e.g. ≤2), forcing agents to spend them wisely.

**B — Tracked artifacts (what we write down)**
6. Concepts book *(user's C2)*: concepts in play + familiarity estimate + plain gloss + why-it-matters-here.
7. Familiarity as a dial the *user* sets (🟢 known / 🟡 shaky / 🔴 new), not an agent guess.
8. Extend the existing GLOSSARY with provenance + familiarity columns instead of building a separate book.
9. "Concept debt" list, mirroring tech debt: an unintroduced concept is logged as debt to be taught down later.
10. Split the registry: *industry concepts* (real, teachable from the world) vs *internally-coined terms* (our shorthand, teachable only from our docs) — they need different teaching.

**C — Gates / lints (mechanical enforcement)**
11. Jargon-density lint on human-facing surfaces (already proposed on the roadmap).
12. New-concept understanding-gate: a concept can't become load-bearing until the user acknowledges understanding — a sibling to the confirm gate.
13. Unlock-on-teach: a coined term is unusable bare in human-facing text until a "taught" event is logged for it.

**D — Interactive teaching (the tutor space)**
14. Tutor agent *(user's C3, Pocock-style)*: teaches on demand and/or when a new load-bearing concept lands.
15. Inline micro-teaching: the introducing agent includes a 2–3 sentence "what it is / why it matters here / what you'd lose without it" box — teaching folded into the flow, no separate session.
16. Explain-back checkpoint: the agent asks the user to restate a concept in their own words, and calibrates familiarity from the answer — understanding *observed*, not guessed.
17. On-demand "unpack that" interrupt: a lightweight command that stops the stream and teaches the last concept before continuing.
18. Spaced re-surfacing: 🟡-shaky concepts get lightly re-explained next time they appear, until they graduate to 🟢.

**E — Structural / process**
19. Extend the Interrogator's remit to run a light concept-check at *every* checkpoint, not just at intake — a continuous version of a thing that already exists.
20. Teaching as a first-class deliverable: each epic/spec closes with a "concepts this introduced / what you learned" summary the user signs off — understanding becomes an acceptance criterion.

**Two forks — now RESOLVED by the human (cycle 1):**
- **Familiarity-owner → HYBRID.** Not agent-guessed alone (patronizing/drifts) and not pure user-chore. Combine: a **user-set register dial** (coarse, per-day tolerance) + **observed-from-the-user's-own-writing / a running record** + **light testing** (Pocock `/teach` + `/grill-me` style). Familiarity is co-authored, human-legible.
- **Build-vs-extend → BUILD NEW is warranted.** Human: "we definitely need a tutor agent… this requires new things… this is conceptually just different and that's okay." Extend where natural (curator jargon lint; docent-adjacent), but do not force everything into existing skills.

### Consolidated after cycle 1 — the surviving shape (candidates, NOT a converged spec)

**KEEP (strong human signal):**
- **K1 — Real-world vs internal concept split.** The core organizing distinction. Low tolerance for internal/project-coined jargon (worse because many concurrent projects); real-world concepts (Matérn process) are *welcome to learn*.
- **K2 — No coined term until "unlocked."** Strong yes. Term can't be used bare with the user until introduced + acknowledged.
- **K3 — Plain-talk mechanism > honor system.** Lightweight is enough — even a reminder/nudge ("brief the human, use plain language") beats the current honor system.
- **K4 — User-set register dial.** Peer ↔ teach-me; tolerance varies by day.
- **K5 — Concept book** = familiarity dial (🟢 known / 🟡 shaky / 🔴 new) + **provenance** (where it came from) + **concept debt** (🔴 = "I believe you for now, revisit later") + real-world/internal tag.
- **K6 — Soft "does this make sense?" check-in** with a *defer* option (defer → logs concept debt). A check-in, **not a hard gate**.
- **K7 — Tutor agent (NEW).** On-demand off-ramp: teach a couple seconds *when the user's in the mood*. Keeps a history of what's been discussed + how well known + light testing; naturally re-explains on recurrence; supports the "hold on — what are we talking about?" interrupt.
- **K8 — Jargon-density lint** on human-facing summaries (curator).
- **K9 — Durable build-milestone explainer (NEW).** At the end of a building point, a durable artifact explaining *what's going on* at an undergraduate/freshman-technical level (a capable technical person who doesn't know every field's internals). Gap: docent is map-level/pull-based, no explain-diff skill exists.

**CULL / SOFTEN (kept here with reasons — a cull can come back):**
- Jargon budget (numeric cap) → **culled**; replaced by K6 "does this make sense + defer." Revive if plain-talk still leaks despite K3/K6.
- Hard understanding-gate → **softened** to K6 soft check-in. Human doesn't want to hard-gate on understanding.
- Interrogator concept-check at *every* checkpoint → **rejected**. Human explicitly declined.
- "Here's what I learned" sign-off → **softened**, absorbed into K9 durable explainer (an artifact, not a ritual).

### Design direction (cycle 3, refine) — TWO HALVES over ONE ledger

> Human steer (cycle 3): don't let the exciting *teaching* side eclipse the *other half* — **neutering project-specific/internal jargon**. Both are first-class.

The design has **two halves with opposite goals**, and they must stay balanced:
- **Half A — teach real-world concepts the user WANTS** (e.g. Matérn process). Goal = *learning*. Surface + teach, at expert/peer register (expertise-reversal rule: minimal by default, depth on a miss, always surface the genuinely-new delta). Mechanisms: tutor (near-silent, summoned on miss/pushback), milestone explainer (two-tier), just-in-time surfacing.
- **Half B — neuter internal / project-invented jargon the user does NOT want.** Goal = *suppression/discipline*. Keep the private dialect in agent-to-agent artifacts; don't spend unearned coinage on the human. Mechanisms: **no coined term until "unlocked"** (K2), the acceptable-language reference (T-A2), the jargon-density lint (K8), plain-talk nudge (K3). Low tolerance here, *worse* across many concurrent projects.

**Unifying insight (candidate — the design's spine):** the two halves are **not two systems — they are two policies over ONE shared per-concept ledger** (the concept book / familiarity overlay on the map). Each concept entry carries a **real-world vs internal tag** + a **familiarity level**. 
- Half A reads it to decide *what to teach and how deep* (teach *up*). 
- Half B reads it to decide *what jargon is allowed unglossed* (suppress *down*). 
- "No coined term until unlocked" (K2) is literally the **same familiarity gate applied to internal terms** — an internal term with familiarity below threshold may not be used bare with the human. One ledger, two opposite read-policies. *(To be pressure-tested, not assumed.)*

**Load-bearing interfaces flagged for design-it-twice:** (1) the shared **concept ledger** (schema + where it lives + how familiarity updates from the user's writing); (2) the **calibration + interleaving** core (the genuinely-novel thing); (3) the **tutor's trigger/summon** contract; (4) the **jargon gate** (how "unlocked" is enforced without context bloat — ties T-A2).

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Even the cited authority externalizes the learner model into a **human-co-authored markdown record** (self-reported level; NO numeric mastery score, NO per-concept familiarity vector, NO spaced scheduling in public work). | Tested: Pocock's public `/teach` + `/grill-me` pages & a third-party writeup. NOT tested: `/teach` source/internals (not public). | X1 |
| The only familiarity **observation source that exists in our setting is the human's own writing** (self-explanation effect). Classroom mechanisms (BKT, SM-2, mastery-gating) assume a stream of *graded responses* the architect never emits — borrow their *shape/intuition*, not their math. | Tested: BKT, spaced repetition, mastery learning, self-explanation, vs. a single-human text-agent setting. NOT tested: deep-learning knowledge tracing, FSRS fitted model (same no-observations barrier). | X1 |
| Transferable core = model familiarity **per-concept**, **decay it** over time/inattention, **update from spontaneous writing** — not from tests. | As above. | X1 |
| **T-B REVERSED for the v0 prototype: ledger is GLOBAL (cross-project), not per-project.** Rationale: single user, low risk, wants to see cross-project response patterns. (Earlier per-project call stands as the considered design default; global is a deliberate prototype experiment to revisit — see FEEDBACK.md standing question.) | Tested: nothing yet — a live experiment. NOT tested: whether global familiarity blurs concept-local expertise across projects. | human, cycle 4 |
| **Expertise-reversal effect (DOMINANT):** for an expert wanting peer register, the novice toolkit (worked steps, build-ups, redundant restatement) is *actively harmful* — raises cognitive load, reads as condescension. Default = **minimal/pointer register, add depth only on a detected miss.** Counter: **expert blind spot** — still surface the genuinely-*new* delta. Expertise is **concept-local**. | Tested: cognitive-load / instructional-design literature (Kalyuga, Sweller, Nathan & Koedinger) vs an expert-in-domain learner. NOT tested: whether text register mis-calibration carries the same measured cost as the visual/worked-example studies. | X3 |
| **Two-tier "short-then-deep" is universal** — terse in-flow default, depth *pulled* on demand. The concrete shape for the milestone explainer, the dial, and the tutor. | Tested: Rust `--explain`, tooltips, Diátaxis across dev-tooling. NOT tested: interleaving one explanation paragraph into a working text stream (unsolved by every source). | X4 |
| **Fading via the contingency rule** answers "when to stop explaining a known concept": register *down* on fluent use, *up* on a stumble — a graded dial read off the human's **own writing**, not a quiz. | Tested: scaffolding/ZPD literature vs a prose-emitting learner. NOT tested: the classic elicited probe (doesn't exist here) — substituted by passive reading. | X3 |
| **ITS 4-component architecture = clean skeleton:** concept book = *student model as an overlay on* the architecture map (= domain model); tutor = tutoring model. Borrow the decomposition; drop the instrumented-performance data pipeline. | Tested: ITS architecture literature. NOT tested: model-tracing / constraint-based internals (need a formal domain expert model). | X3 |
| **Pocock's `teach` is public & the closest existing thing** — `MISSION.md` + `NOTES.md` + `learning-records/NNNN.md` **explicitly ADR-like**, driving zone-of-proximal-development. **Steal the learning-records-as-ADRs state layer**; drop the novice HTML *course*. | Tested: his public repo (github.com/mattpocock/skills). NOT tested: nothing hidden — repo is public. | X2 |
| **The personalized-expert-reader-in-flow niche is UNFILLED.** explain-diff tools (Copilot/Cursor) are audience-flat, stateless, no depth decision; all of superpowers teaches the *agent*, not the human. | Tested: marketplaces, superpowers, Copilot/Cursor, GitHub skills. NOT tested: closed/proprietary internal tools. | X2 |
| **THE GENUINELY-NOVEL CORE** (what we'd actually invent): the **calibration + interleaving problem** — hold a *standing per-reader familiarity model* AND blend *one paragraph of explanation into a working text stream* without condescending or cluttering. Every existing tool assumes a mismatched reader/medium (blocked reader / future-absent reader / re-declaring human / rich hover layer); **none matches our case.** | Tested: convergent across X2+X3+X4. NOT tested: it's an unsolved design problem, not a settled fact. | X2·X3·X4 |

## Endorsed direction (post-cycle-3)

The human endorsed the **named hybrid** as the working design direction ("right direction… a solid start") but wants **more refinement before any spec** (explicitly NOT converging yet). Hybrid = D's append-only ledger · A's `docs/agents/` home · C's typed verbs as a helper (not a service) · inline policies · summon-only tutor · B's reconcile-decay graft · curator-lint backstop.

### Starting place + ADVISORY roadmap (human-directed)

Human direction: "define a starting place, then set up a roadmap we can use in an advisory sense." Confidence **decreases** down the list (human: "they get more questionable as we go on"); the roadmap is **non-binding guidance**, and **R1's real-world data re-orders R2–R4.**

> **⚡ SHIPPED 2026-07-17 — human overrode shadow mode: "forget shadow, just go for it… good enough… put it global… I'm the only user, low risk."** R1 v0 is **LIVE and GLOBAL**, not shadow. It drives real behavior; Fred corrects in-flight; corrections → rapid refinement. Deployed files: `~/.claude/CLAUDE.md` (short rubric, loaded every session — the always-on hook) + `~/.claude/shared-understanding/{concepts.md, observations.jsonl, FEEDBACK.md, README.md}`. Disable = delete the CLAUDE.md block/file. **This is a build/deploy step beyond Explorer's lane — done directly at the human's explicit direction for a low-risk single-user prototype; reported as a deliberate misfit, not silent.** The ideas board remains the design source of truth.

**▶ STARTING PLACE (as originally scoped) — R1 prototype (the observation classifier), was to be SHADOW mode; human upgraded to live-global above.**
- **The one question:** can an agent, reading Fred's *actual* prose in real sessions, reliably tell whether he **used a concept fluently vs. stumbled/asked** — and attach it to the **right** concept?  (Root of D's drift wound; punted by all four designs.)
- **Shadow/advisory deployment (human OK'd a real deployment on a long timescale):** stand up the *lightest* slice of the hybrid — a per-project append-only `observations.jsonl` + a tiny `observe` step that, at the end of relevant turns, logs `{concept, kind(fluent|stumble|ask|introduced), evidence-quote}`. It **only records what it *would* classify; it drives NO teaching/neutering yet** — zero risk to live sessions.
- **How we learn:** periodically Fred eyeballs the log and marks where the classifier was wrong (ground truth). Over time this both (a) **measures** classifier-vs-Fred agreement and (b) **seeds a real ledger**. Prototyper branch = **measurement**.
- **What "answered" looks like:** after N sessions, a measured "agrees with Fred X% of the time" + a real observation corpus + named failure modes. Reliable → the hybrid's foundation is sound; unreliable → we learn *how* before building the policy layer on top.
- **Open deployment decision:** *which project to instrument first* (constellation-skills itself? f1brainz? both?) — needs Fred.

**Advisory roadmap (decreasing confidence; revisit as R1 teaches us):**
- **R1 — HIGH confidence, now.** Observation-classifier shadow prototype (above). De-risks the crux; produces real data.
- **R2 — MEDIUM.** The controls Fred touches: register **dial** (levels; per-session vs standing default), **unlock** semantics (introduce-once vs explicit ack — T-C), **concept-debt paydown** (T-E). Design once R1 shows the ledger is trustworthy.
- **R3 — LOWER.** Milestone explainer (K9/T-F): trigger ("building point"), level, explain-*diff* vs docent's explain-*map*. Slots in when a real milestone needs it.
- **R4 — LOWEST / defer.** Tuning: cold-start seeding (concept-local — first mention assumes NEW even if Fred owns it); decay constants/units. **Calibrate from R1's real data, not up front.**

## Open threads

> These seed the NEXT cycle (likely a compare/refine on the architecture). T1/T4 from cycle-0 are resolved (glossary = meanings only, excludes familiarity → concept book is genuinely distinct; this arc completes the 2026-07-10 plain-language thread rather than starting fresh).

- **T-A — Division of labor: inline duty vs. tutor agent. → RESOLVED (cycle 1, human).** Plain talk is **every agent's standing duty** — each judges acceptable jargon inline (K3). The **tutor (K7) is summoned on the user's pushback signal** ("no, that doesn't make sense" / "let's go back and talk about that"), NOT a separate always-on role. Inline = continuous/default; tutor = triggered by confusion/pushback.
- **T-A2 — NEW: the "acceptable language" reference table + context-load problem.** For agents to judge acceptable jargon they'd need a reference table of what's OK vs. not — but loading it into *every* agent bloats context ("a giant dictionary"). Open: how to expose that table without overloading every agent's context. Human will settle the loading approach later. *(Parked, not dropped.)*
- **T-B — Where does the concept book live? → RESOLVED (cycle 1, human).** **No shared/global book.** Projects drift apart; tracking is **per-project**. The user is fine being **re-asked "do you know this term?"** across projects, so cross-project dedup is unnecessary. (Entry schema still open: term, gloss, provenance, familiarity, real-world/internal tag, last-touched, debt flag.)
- **T-C — The "unlocked" mechanism (K2).** How is unlock tracked + enforced lightly (tie to concept book + register lint) without heavy ceremony?
- **T-D — The register dial (K4).** Levels, and how/when set — per-session? a persistent default the user nudges? read by whom?
- **T-E — Concept-debt paydown loop (K5/K6).** How 🔴/deferred debt gets surfaced and paid down — via the off-ramp teach, tutor sessions, or re-surfacing on recurrence.
- **T-F — The build-milestone explainer (K9).** What counts as a "building point" (the trigger), the level, where it lives, and its relation to docent (map-level) — is it explain-*diff* (per change) vs explain-*map* (docent)?
- **T-G — The register/tone contract.** Encode "peer, precise jargon OK, gloss/teach unfamiliar *real-world* concepts, be extra sparing with *internal* coinage" as a *mechanism* agents follow (K3/K8), not just prose that erodes.

## Excursions

- **X1 — Tutor & familiarity-tracking prior art** *(research, **completed & verified fresh**)*. Question: what have Matt Pocock and the ecosystem actually built for AI tutoring and per-concept familiarity tracking, and what transfers to a single-human text-agent setting? Brief: `excursions/x1-handoff.md`. Result → `excursions/x1-tutor-prior-art.md`. Registry: `constellation/explore-shared-understanding/explore/researcher/attempt-1`. Agent-initiated; low-regret (user named Pocock); informs the design regardless of which fork we pick.

### Cycle 2 — prior-art sweep (human-directed, 3 parallel research excursions — **all COMPLETE & verified fresh**)

- **X2 — Agent-skill teaching/explaining ecosystem** *(complete)*. Pocock `/teach`+`/grill-me` structure, explain-diff/change-explainers, superpowers/marketplace/IDE "explain" skills. Brief: `excursions/x2-handoff.md` → `excursions/x2-skill-ecosystem.md`. Registry: `.../researcher-x2/attempt-1`.
- **X3 — Education field for teaching a working expert** *(complete)*. ITS architecture, scaffolding/fading + ZPD, **expertise-reversal effect / expert blind spot**, just-in-time & cognitive apprenticeship, concept/prerequisite maps. Brief: `excursions/x3-handoff.md` → `excursions/x3-education-field.md`. Registry: `.../researcher-x3/attempt-1`.
- **X4 — How dev tools teach in-flow** *(complete)*. Rust `--explain`, Diátaxis explanation quadrant, ADRs/literate programming, IDE/AI "explain this", progressive disclosure. Brief: `excursions/x4-handoff.md` → `excursions/x4-devtool-teaching.md`. Registry: `.../researcher-x4/attempt-1`.

### Cycle 3 — design-it-twice: the shared-understanding mechanism (panel of 4, **COMPLETE & verified fresh**)

Brief: `excursions/x5-handoff.md`. One architecture designed 4 ways. Results: `excursions/x5-design-{a,b,c,d}.md`.

**Axis summary:**
- **A · minimal** — a per-project `docs/agents/CONCEPTS.md` table + a doctrine paragraph + a thin summon-tutor. **Wins** heavy-machinery-avoidance, locality, symmetric halves. **Loses** depth (pedagogy is an inline discipline, no test seam for interleaving; in-flow chat enforced by nothing); hand-waves concurrency + context-load.
- **B · map-overlay** — familiarity annotates Cartographer map nodes; teach = map traversal; signature idea = **reconcile-decay** (knowledge softens when the *code* changes). **Wins** testability. **FAILS serve-both-halves** — internal jargon mostly isn't a map node, so the half the human cares about *more* is served *worst*; and it's **parasitic on a map most projects lack**.
- **C · tutor-service** — a first-class Tutor owns everything behind a 4-verb port (`may_use`/`teach_delta`/`note_usage`/`summon`). **Wins** depth, testability, halves-cannot-drift, central expertise-reversal. **Loses hardest on heavy-machinery** (a service + store = the near-kill anti-goal) + latency + a failure matrix only it needs + silent-no-op coupling. Admits "wins iff the 2nd caller is real."
- **D · distributed** — append-only `observations.jsonl` folded into a derived view; three verbs; policies inline everywhere; tutor only on pushback. **Solves both hazards the human flagged** (concurrency via commuting appends; context-load via keyed lookup — query only the 0–3 terms in *this* message). Lowest condescension, most balanced halves. **Loses** locality; carries the **judgment-drift** wound (distributed classification).

**RECOMMENDATION (defended, not a menu — convergence is the human's): a named HYBRID.** D's append-only ledger + derived legible view, **home per A** (`docs/agents/`, zero new load path), exposed through **C's typed pure-function verbs** (`familiarity`/`unlocked`/`observe`) as a ≤1-screen shared helper — **NOT a running service** (C-as-service trips the heavy-machinery near-kill). Policies **inline per every agent** (D + confirmed T-A) under A's short interleaving contract. **Tutor summon-only** on miss/pushback. **Graft B's reconcile-decay** where a map exists (its best idea, minus its map-dependency). **Curator lint reads the shared `unlocked()` predicate** = the backstop for the "in-flow chat enforced by nothing" hole.

**THE ONE BIGGEST OPEN RISK — punted as a scoped null by ALL FOUR:** the **calibration classifier** ("fluent use vs stumble" from free prose), which is also the crux of D's drift wound. Standardize it tightly (pinned rubric + worked examples) even while policy application stays distributed. Drive down next.

## Rejected ideas (with reasons)

- **Jargon budget (numeric cap per message)** — culled; user prefers "just don't say things that don't make sense" + a "does this make sense?" ask (K6) over a counting rule. Revive if leaks persist.
- **Hard understanding-gate** — softened to a soft check-in (K6); user doesn't want to hard-gate on understanding.
- **Interrogator concept-check at every checkpoint** — rejected outright by user.
- **"Here's what I learned" sign-off ritual** — softened into a durable explainer artifact (K9); user wants an artifact, not a ritual.
- **"Just extend, don't build new" posture** — rejected by user for this arc: a tutor agent + concept book are genuinely new and that's intended.

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 4 | refine / ship | Human overrode shadow mode: ship R1 v0 live + global, good-enough, feedback-driven | **SHIPPED.** `~/.claude/CLAUDE.md` rubric (every session) + `~/.claude/shared-understanding/` ledger. T-B reversed (global for prototype). Build/deploy beyond Explorer's lane — done at explicit human direction, flagged as deliberate misfit. Now live; refine from real feedback. |
| 3 | refine / design-it-twice | Spine confirmed; panel of 4 designs (A minimal / B map / C service / D distributed) verified fresh | **Consolidated.** Recommendation = a named HYBRID (D's append-only ledger + A's existing-artifact home + C's typed verbs-as-helper-not-service + inline policies + summon-only tutor + B's reconcile-decay graft + curator-lint backstop). B rejected as primary (fails both-halves; map-parasitic). C-as-service rejected (heavy-machinery near-kill). Biggest open risk = the calibration classifier (punted by all 4). Awaiting human's next-move call. |
| 2 | research sweep | Human-directed 3-agent prior-art sweep (X2 skill ecosystem / X3 education field / X4 dev-tool in-flow teaching); also resolved T-A (inline duty everywhere; tutor summoned on pushback) + T-B (no shared book; per-project; re-asking OK) | **Consolidated.** 8 new verdicts. DOMINANT: expertise-reversal → tutor defaults near-silent, peer/minimal register, depth on miss (backs "don't talk down"). Two-tier short-then-deep universal. Fading = familiarity observed off the user's own writing. ITS skeleton (concept book = student-model overlay on the map). Pocock learning-records-as-ADRs = stealable state layer. Novel core to invent = **calibration + interleaving**. Reshaped K5/K7/K9. Awaiting human's next-move call. |
| 1 | shotgun | 20 ideas (5 families) + X1 prior-art research; full human reaction to all 20 + both point-questions | **Consolidated.** Point sharpened (real-world-concepts-to-learn vs low-tolerance internal jargon; peer register; grade B→C; no hard kill). 9 KEEP (K1–K9, incl. NEW tutor agent + build-milestone explainer), 4 cull/soften, 1 posture rejected. Both forks resolved (familiarity=hybrid; build-new warranted). 7 open threads (T-A…T-G) seed the next cycle. Awaiting human's next-move call. |
