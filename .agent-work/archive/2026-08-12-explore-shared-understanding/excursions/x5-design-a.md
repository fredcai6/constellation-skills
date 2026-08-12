# X5 Design A — **minimal-machinery**: the shared-understanding mechanism as the lightest thing that works

**Constraint (mine):** design the mechanism as the LIGHTEST thing that works. Extend existing artifacts; a plain-text ledger + a register *discipline*; tutor as a thin on-demand skill. NO scoring engine, NO new services, near-zero new infrastructure — "could ship next week." Everything held FIXED in the handoff (two-halves-over-one-ledger spine; expertise-reversal register rule; familiarity-observed-from-writing; per-project; tutor-summoned-on-miss; the anti-goals) is taken as given and built *on*, not redesigned.

**One-line thesis:** the whole mechanism is **one small per-project markdown file + one short doctrine paragraph every agent already loads + one thin summon-only tutor skill.** No component runs when no one is writing to the human. The "engine" is a *discipline*, and its history is *git*.

---

## 0. Deep-module framing (used throughout)

- **Interface = everything a caller must know to use the thing.** A *deep* module hides a lot behind a small interface; a *shallow* one forces callers to know its internals.
- The **caller** here is *any agent about to emit human-facing text* (Commander write-up, Admiral closeout, an inline reply). 
- The **state** is the ledger file. It has no behavior — it is shared data, an *overlay on the domain* (ITS student-model-over-domain-model, X3 §1).
- The **behavior** is split two ways, and this split is the crux of the constraint:
  - the **tutor** is a genuine deep module behind a one-file seam (summon + ledger-writeback);
  - the **calibrate/interleave/gate discipline** is *deliberately NOT a module* — it is a short rule internalized by every caller. Minimal-machinery buys "ships next week" by paying here, in depth. Owned honestly in §7.

---

## 1. The ledger — entry shape + home

### Home
A single per-project file: **`docs/agents/CONCEPTS.md`**, a sibling of the existing **`docs/agents/GLOSSARY.md`**.

Why here, concretely (this is the whole "extend existing artifacts" claim):
- The Charter already compiles a `docs/agents/` bundle (`ORCHESTRATOR_CONTEXT.md`, `CREW_CONTEXT.md`, `GLOSSARY.md`, `AGENT_GUIDE.md`, `PLATFORM_NOTES.md`) and agents already load it for repo orientation. `CONCEPTS.md` joins that bundle — **zero new load path.**
- Prior verdict (IDEAS_BOARD T1): **GLOSSARY = meanings only.** The ledger is the *familiarity overlay* the glossary deliberately excludes. Clean separation: glossary answers "what does this term mean," the ledger answers "how well does Fred hold it, and is it his to keep." Same directory, different jobs.
- **Per-project** (FIXED): the file is local to each repo; no cross-project dedup, re-asking a term in another project is fine.
- **History for free:** the ledger is markdown under git. Every familiarity change is a diff with an author and a date — this *is* the Pocock "learning-records-as-ADRs" append-only trail (X2) and the ADR immutability instinct (X4 §3), with **zero new machinery**: `git blame docs/agents/CONCEPTS.md` is the audit log. No changelog, no DB, no event store.

### Entry shape
One markdown table, one row per concept in play. Human-legible and human-editable (co-authored, not agent-owned):

```markdown
# CONCEPTS — familiarity overlay (per-project). Glossary = meanings; this = how well Fred holds them.
# fam ladder: new < shaky < known < fluent.  Gate line for internal terms = "known".
# familiarity is OBSERVED off Fred's own writing, updated one notch at a time. Do not quiz. Do not guess-jump.

| term            | tag      | fam    | gloss (one line)                                             | provenance            | last-touched | debt |
|-----------------|----------|--------|--------------------------------------------------------------|-----------------------|--------------|------|
| Matérn process  | world    | shaky  | covariance family, tunable smoothness ν; GP kernel between exp & squared-exp | ref in #142 spatial-corr | 2026-07-14   |      |
| two-halves spine| internal | new    | our name for teach+neuter over one ledger                    | coined in this arc    | 2026-07-17   | 🔴   |
| Cholesky factor | world    | fluent | lower-triangular √ of an SPD matrix; how we sample the GP     | #131                  | 2026-07-16   |      |
```

Field-by-field (each is the *minimal* thing that makes a policy decision possible):
- **term** — canonical surface form.
- **tag** — `world` (real-world/industry; TEACH reads this) or `internal` (project-coined; NEUTER reads this). The FIXED real-world-vs-internal split.
- **fam** — an **ordinal word**, not a number: `new < shaky < known < fluent`. Words, not a score, honor the anti-goal (no scoring engine, no dashboard). Four rungs is enough to drive every policy branch below; fewer would collapse "unlocked?" into "teach?".
- **gloss** — one plain-language line. For `world` it is the *delta pointer* (what's genuinely new); for `internal` it is the *unlock payload* (the plain thing the coinage stands for). Doubles as the milestone-explainer source text.
- **provenance** — where it entered (issue #, paper, "coined in <arc>"). Anti-jargon teeth for `internal` terms: a coinage with no provenance is a red flag.
- **last-touched** — date; drives *lazy* decay (§2). A date, not a scheduler.
- **debt** — `🔴` = "Fred said 'I believe you for now, revisit later'" (K5/K6 concept-debt). The only human-set-in-the-moment flag.

The interface a caller must know to *read* the ledger is exactly these seven columns and the four-rung ladder. That is the entire read-side contract.

---

## 2. How familiarity updates from the human's writing

**Observation source (FIXED, X1/X3 verdict):** the *only* signal that exists is Fred's own prose. No quiz, no self-rating chore, no classifier.

**Minimal-machinery realization:** the update is a **side-effect of the reply the agent is already composing**, governed by the **contingency/fading rule** (X3 §2) written once in doctrine. Before an agent replies, it has just read Fred's last message; while reading it applies:

- Fred **used a ledger concept fluently / correctly in his own words** → nudge fam **up one rung** (shaky→known, known→fluent), stamp `last-touched`.
- Fred **asked about it, mis-used it, or pushed back** ("wait, what's X", "that doesn't sound right") → nudge fam **down one rung** (or set `debt 🔴` if he deferred), stamp.
- Fred **coined/adopted an internal term back** at Fred's initiative → that's the *acknowledgment* half of "unlock" (§4): internal fam shaky→known.
- **No signal** → touch nothing. (Guess/slip intuition from BKT, X1: one noisy signal moves *one* rung; never jump.)

**Decay is lazy, not scheduled** (this is the key no-service move): there is no background job. When a concept is *next surfaced*, the surfacing agent compares `last-touched` to today and, if the gap is large, *reads* it as one rung staler for that message only — it does not rewrite the file on a timer. Decay costs nothing when the project is idle. (Decay constant is a scoped null, §8.)

**Write mechanics:** a one-cell markdown edit + a date bump, committed with whatever change the agent was already making. A *missing* update is visible in review as "the reply clearly showed Fred is now fluent but the ledger still says shaky" — git makes the honor-system-erosion failure *inspectable* without a service to enforce it. This is minimal-machinery's substitute for enforcement: **visibility, not a gate.**

The interface a caller must know to *write* the ledger: the four-arrow contingency rule above, and "one rung, only on real signal." That is the entire write-side contract.

---

## 3. The TEACH policy (real-world concepts; push familiarity *up*)

When an agent is about to reference a **`world`**-tagged concept in human-facing text, it reads `fam` and branches:

- **`fluent` / `known`** → use it **bare, peer register, no gloss.** (Expertise-reversal, X3 §3: re-explaining what he owns *raises* load and reads as condescension. The default is silence.)
- **`shaky`** → weld a **one-clause delta pointer** to the sentence that needed the concept (§5). Not a build-up — just the genuinely-new edge.
- **`new`, or absent from the ledger** → this is the teachable moment. Emit a **minimal pointer**: name + one line of *why it's load-bearing right here* + an explicit **off-ramp** ("want the 2-minute version? — say the word"). Never force the lesson (off-ramp, not gate — K6). If Fred engages, §2 raises fam; if he defers, set `debt 🔴`.
- **New `world` concept not yet in the ledger** → the introducing agent **adds the row** (`tag=world, fam=new, gloss=<one-liner>, provenance=<here>`). *Adding the row is itself the teach-up event.*

TEACH is "push up": every branch either uses the concept at Fred's level or creates the opportunity to raise it, and expert-blind-spot (X3 §3) is guarded by the standing rule *always name the genuinely-new delta even if it feels obvious to you.*

---

## 4. The NEUTER policy (internal jargon; hold the dialect *down*; "no coined term until unlocked")

**Same ledger, opposite read.** When an agent is about to use an **`internal`**-tagged coined term in human-facing text, it reads `fam` against **one gate line: `known`.**

- **fam `< known` (i.e. `new` or `shaky`) → NOT UNLOCKED → the term may not appear bare.** The agent must do one of:
  1. **(preferred) Neuter it** — say the plain thing instead; the coinage stays in agent-to-agent artifacts only. Across many concurrent projects this is almost always right (IDEAS_BOARD K1: low tolerance for per-project dialect).
  2. If the term is genuinely load-bearing, **introduce it with its one-line gloss** — and that introduction *is* the unlock event, flipping fam `new→shaky` ("introduced, acknowledgment pending"). Promotion to `known`/unlocked comes only when §2 sees Fred use it back.
- **fam `known` / `fluent` → unlocked → use bare.**

So **"no coined term until unlocked" (K2) is literally the same fam threshold as TEACH, read in the opposite direction:** TEACH treats `new` as *an opportunity to raise*; NEUTER treats `new`/`shaky` as *forbidden bare, prefer plain*. One ledger, two policies, symmetric — exactly the FIXED spine.

**Backstop without a new service:** the discipline covers in-flow text; for *persisted* human-facing surfaces (closeouts, summaries) the **existing curator jargon-density lint (K8)** is re-pointed to read this same ledger — it flags any `internal` term with fam `< known` appearing bare. That reuses an artifact that already exists; it is not a new gate. (In-flow ephemeral chat has no lint — scoped null §8.1.)

**The T-A2 "giant dictionary in every agent" problem** is answered by scope, not by a loader service: the ledger is *per-project* and holds *only concepts actually in play here*, so it is small; it rides the `docs/agents/` bundle agents already load; and graduated `fluent` concepts get pruned (Fred owns them — re-add if they resurface). Its smallness is a *discipline*, and that it stays small is minimal-machinery's honest weak point (§7, §8.2).

---

## 5. Calibration + interleaving inside a real message (the genuinely-novel core)

This is the thing every source left unsolved (IDEAS_BOARD verdict X2·X3·X4). Minimal-machinery gives it a **register discipline** — a short authoring rule, not an engine. Three moves the agent makes *while composing a normal working message*:

**(1) Calibrate — per concept, per span.** The message default is **minimal / peer across the whole thing** (expertise-reversal default). For each concept the message touches, the ledger `fam` sets the register *for that span only* — expertise is concept-local, so one message is bare-peer on `Cholesky factor` (fluent) and offers a pointer on `Matérn` (shaky) in the same breath. Depth is added *only* at the specific spans the ledger flags `new`/`shaky`. Calibration = a per-span lookup, nothing more.

**(2) Interleave — weld, don't box.** The explanation is **one sentence, at the concept's first load-bearing mention, phrased as a peer aside** — never a boxed "📚 LESSON" callout (a callout is both clutter and condescension). The shape:

> "…so we sample the field with a **Matérn** kernel — *a covariance family whose smoothness you can tune, sitting between exponential and squared-exponential* — which is why ν shows up in the config."

The gloss rides the sentence that needed the concept anyway; it costs **one clause, not a paragraph** (X4 §5: in a linear channel a gloss is never zero-cost, so spend exactly one). **Budget: ≤1 inline gloss per message.** If two+ `new` concepts land, weld the highest-load-bearing one inline and demote the rest to a single trailing off-ramp line: *"new here too: X, Y — say the word to unpack."*

**(3) Surface the delta + leave the pull-handle.** Always name the genuinely-new thing even if it feels obvious (expert-blind-spot guard), and always end teachable messages with **one** off-ramp line pointing at the tutor. The off-ramp never blocks.

**The interleaving contract (the whole novel core, stated as an interface):**
> *Default peer/minimal. Per-concept register from the ledger. ≤1 inline gloss, welded to its triggering sentence, no boxes. ≤1 trailing off-ramp line. Always surface the new delta; never force the lesson.*

That is short enough to live in doctrine and be applied by every agent inline — which is the point of the constraint, and also its cost (§7 Depth/Testability).

---

## 6. The tutor's trigger / seam

**The tutor is a thin, summon-only skill** (Pocock `/teach` shape, `disable-model-invocation`-style — never always-on). Not a service, not a running agent.

**Triggers (all FIXED as "summoned on miss/pushback"):**
- Fred's **pushback/confusion** signal ("no, that doesn't make sense", "wait — what's X", "let's go back") — the standing discipline recognizes it and *offers* the summon.
- Fred **takes an off-ramp** an interleave offered.
- Explicit **`/tutor <concept>`** or **"unpack that"** (teach the last concept).

**Seam (the tutor's full interface — everything a caller must know):**
> **Summon** with a concept name (or *"the last thing"*). The tutor teaches it at the register the ledger records (two-tier: terse first, deeper only on ask — X4), then **writes back**: bump `fam`, stamp `last-touched`, clear `debt`, refine `gloss`. On exit the ledger is current.

Callers need to know *only* the trigger and that the ledger is left updated — **not** how the tutor teaches. The tutor and every inline agent are coupled through **exactly one thing: `CONCEPTS.md`.** No RPC, no shared code, no protocol. That single-file coupling is what keeps the tutor a *deep* module (rich teaching behavior, one-file seam) while the rest of the system stays a discipline.

**Milestone explainer (K9), minimal form:** at a build milestone, the durable explainer is a markdown artifact pitched from the ledger's glosses and stamped with **docent's existing `docent_freshness.py` SHA stamp** (X2) so a stale explainer self-flags. Reuse, not build. (Its trigger — "what counts as a milestone" — is out of my scope here; T-F.)

---

## 7. Honest self-assessment (five axes) — incl. where minimal-machinery HURTS

**Depth — WEAK-to-MEDIUM. This is where the constraint hurts most.** The *state* is cleanly hidden behind one file. But the *pedagogy* — calibration + interleaving + the gate — is **not hidden behind a seam; it is a discipline every agent runs inline.** So the interface a caller must carry is *bigger* than in a tutor-as-service design: every agent must hold the contingency rule, the `known` gate line, and the interleaving contract. Minimal-machinery trades a **deep module for a shared shallow discipline.** Mitigation: the discipline is *small* and the ledger is a *single* source of truth, so it is "shallow-but-shared," not "duplicated logic that drifts." But an honest reviewer should score depth *below* constraint C (tutor-as-service), which is exactly the axis C optimizes and A concedes.

**Locality — STRONG.** One new file per project (`docs/agents/CONCEPTS.md`), one short doctrine delta in the *already-fanned-out* global-everyone/AGENT_GUIDE layer, one thin tutor skill, plus reuse of the curator lint and docent stamp. No new services, no new load paths. The behavioral fan-out ("every agent applies the discipline") rides the doctrine layer that *already* reaches every agent, so it adds **zero new fan-out surface** — the change is contained to files that already exist or sit beside them.

**Seam placement — MEDIUM (deliberately asymmetric).** The seam callers actually want for the **tutor** (summon + ledger-writeback) is well placed and genuinely thin. But there is **no seam for the calibration/gate itself** — a `may_use(term)?` / `note_usage(text)` call (constraint C's optimization) would sit better for both single-owner reasoning and testing. Minimal-machinery *declines* that seam on purpose, to avoid standing up a service. Verdict: right seam for the tutor; a **deliberately-absent seam** for the gate, which is a real cost paid for "ships next week."

**Testability — MIXED, and honestly the softest axis.**
- *Cheaply testable today:* the **NEUTER gate** — the curator lint is a pure function over (text, ledger); assert "no `internal` term with fam `< known` appears bare" against fixtures. The **familiarity-update rule** — a golden table: (human message, prior fam) → (new fam, last-touched). The **ledger schema** — a shape lint like the existing template checks.
- *Hard/nearly untestable:* **interleaving quality** — "was this one-sentence gloss non-condescending and non-cluttering?" has no cheap oracle. Minimal-machinery gives the novel core **no test seam** — only the discipline and Fred's reaction. The single most valuable, most novel pathway is the least falsifiable one. That is the constraint biting: constraint C could at least unit-test `may_use`; here the gate is inlined and the interleave is a judgment.

**Fit to anti-goals — STRONG on two, one honest residual risk.**
- *Heavy machinery:* **best-in-class** — near-zero infrastructure, reuses artifacts, git-as-history, nothing runs at idle. The constraint's home turf; it wins this axis outright.
- *Condescension:* the discipline is *built* against it — expertise-reversal default (minimal/peer), ≤1 gloss, no boxes, off-ramp-not-gate, "surface the new delta don't restate the owned." Strong.
- *Serves BOTH halves equally:* **yes** — one ledger, symmetric read; TEACH and NEUTER are the same `fam` threshold read in opposite directions. NEUTER is arguably *better* served here than in heavier designs, because the gate collapses to "a lint reads a table."
- *Residual risk unique to minimal-machinery:* because the familiarity update and the gate are **disciplines, not a service**, they can **silently erode** — the exact honor-system failure K3 was reacting to. Minimal-machinery's answer is teeth that need no service: the **curator lint** (mechanical backstop on persisted surfaces) and **git-visible ledger edits** (a missing/laggy update is inspectable in review). But **in-flow ephemeral chat is linted by nothing** and relies on discipline alone. That hole is the price of the constraint, stated plainly.

---

## 8. Scoped nulls — what I did NOT resolve

1. **In-flow chat enforcement.** The curator lint backstops *persisted* surfaces; ephemeral chat messages have no lint. Whether discipline-alone holds there, or needs a lightweight pre-send self-check the agent runs, is unresolved. (Report "this specific surface is unlinted," not "unenforceable" — a pre-send self-check is a plausible variant I didn't design.)
2. **Ledger-size discipline.** The whole T-A2 answer rests on the table *staying small* (per-project + pruning graduated concepts). Nothing *enforces* pruning; if it bloats, the context-load problem returns. Pruning cadence (curator pass? tutor exit? a git-size trigger?) unresolved.
3. **Concurrent writes.** Two background agents both editing `fam` on `CONCEPTS.md` in one wave. Git makes it visible and last-writer-wins is probably fine at this scale, but real merge semantics for one-cell edits are undesigned.
4. **Decay constant + unit.** "Stale after a large gap" — the threshold and whether the unit is *sessions* or *wall-clock days* is a guess. Fred runs many projects and may not touch one for weeks without forgetting, so wall-clock decay could over-fire. Lazy read-time decay is proposed; the threshold is not calibrated.
5. **Interleaving-quality oracle.** No cheap test for "condescending / cluttering." Left to Fred's reaction + tutor pushback. The novel core is under-instrumented *by design* under this constraint.
6. **Cold-start seeding.** First appearance of a `world` concept is seeded `fam=new`, but expertise is concept-local and an agent can't know Fred may already own it — so the first mention may cost one unnecessary pointer before §2 promotes it on his first fluent use. Acceptable, not elegant; flagged.
7. **Milestone-explainer trigger (K9/T-F).** I reuse docent's freshness stamp and pitch from the ledger, but "what counts as a build milestone" is out of scope here and unresolved.

---

**Confirmation:** written to `C:\Programs\constellation-skills\.agent-work\explore-shared-understanding\excursions\x5-design-a.md`.
