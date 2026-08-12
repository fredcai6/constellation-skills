# X5 · Design D — distributed-duty (no central authority)

**Constraint:** NO central tutor. Calibration + interleaving is a **cross-cutting discipline every agent applies inline** against the shared ledger. Every agent reads and writes the ledger directly and blends its own explanation into its own message. The tutor exists **only** as the deep-dive-on-pushback escalation. Optimize for *in-flow naturalness* — teaching happens where the work happens.

**Held FIXED (not redesigned):** two policies (teach real-world / neuter internal) over ONE per-concept ledger, each entry tagged real-world-vs-internal + familiarity; expertise-reversal register rule; familiarity observed off the human's own writing, not quizzed; per-project; tutor summoned on miss/pushback; anti-heavy-machinery / anti-condescension. Prior art reused: Pocock learning-records-as-ADRs (append-only), ITS student-model-as-overlay, two-tier short-then-deep, docent freshness stamp, Diátaxis explanation shape.

---

## 0. The load-bearing idea (why D is not just "C without the tutor")

The other candidates put the *behavior* somewhere: C in a tutor agent, B in the map, A in a skill. D has nowhere to put it — by construction there is no owner. So D's whole design turns on one move:

> **Make the ledger a passive, append-only artifact whose interface is a convention, and push all mechanical complexity down into three tiny pure functions every agent calls. The "module" is a *specification* (a data format + a rubric), instantiated by each agent, not a running component.**

This is the inversion of ports-and-adapters. In C the deep module is a *process* behind a call seam. In D the only deep module is the **data layer** — an append-only log plus a fold function — behind a three-verb interface (`observe`, `familiarity`, `unlocked`). The *policy* layer (when to teach, how to interleave) deliberately does **not** hide behind a seam; it runs inside each agent's generation, because that is the only place "teaching in the flow of the work" can physically happen. D therefore accepts a **shallow policy seam in exchange for maximal locality-to-the-work** — and spends its design effort making the shallowness cheap and the data layer bomb-proof.

The two hazards the human flagged — the *giant-dictionary-in-every-context* load problem, and *concurrent writes from parallel agents* — are the two things this design is built around. They are addressed in §2 and §3, not hand-waved.

---

## 1. The ledger: entry shape + home (shared, no single owner)

**Home.** Per project, in-repo: `.shared-understanding/` (sibling to `docs/architecture/`). It is a plain-text, human-legible, git-tracked artifact — no service, no DB, no single writer. "Shared, no owner" is realized as *a file every agent has equal read/write rights to*, not a resource a gatekeeper mediates.

**Two layers, deliberately split by mutability** — this split is what makes concurrency safe (§3):

### 1a. `observations.jsonl` — the append-only event log (authoritative)
The only authoritative state. Never edited in place, only appended — Pocock's learning-records-as-ADRs, taken literally as an event stream. One JSON object per line:

```jsonc
{ "ts":"2026-07-17T15:40:12Z", "concept":"matern-process", "tag":"real-world",
  "agent":"commander/pr-142", "kind":"agent-introduced",
  "evidence":"glossed on first use in the wave-2 summary", "gloss":"a covariance
  family that tunes how smoothly correlation decays with distance" }
{ "ts":"2026-07-17T16:02:55Z", "concept":"matern-process", "tag":"real-world",
  "agent":"implementer/issue-88", "kind":"human-fluent",
  "evidence":"Fred wrote: 'use a Matérn-3/2 so the field isn't C∞-smooth'" }
```

**`kind` is a closed vocabulary** (the rubric is the whole consistency story — §6):
- `agent-introduced` / `agent-taught` — an agent spent explanation on this concept (carries the `gloss`).
- `human-fluent` — the human used the concept correctly/unprompted in their *own* writing (the self-explanation signal; pushes familiarity **up**).
- `human-ask` / `human-stumble` — the human asked what it meant, or used it wrong/hedged (pushes **down**).
- `human-deferred` — the human hit K6's "does this make sense?" and chose *defer* → logs concept-debt, does not raise familiarity.
- `human-pushback` — "no, that doesn't make sense / let's go back" → the tutor-escalation trigger (§5).

Every event is **evidence-bearing** (carries the quote or a pointer). Evidence is what lets a later agent — or the human — re-adjudicate a mis-classification, which is D's only defense against judgment drift.

### 1b. `concepts.md` — the materialized register (a cache, non-authoritative)
A human-readable table, **derived** by folding the log. It exists for the human to browse and for cheap agent lookups, but it is *never* the source of truth. It carries a **docent-style freshness stamp** — the hash of the log tail it was folded from — so a stale render self-flags:

```md
<!-- built-from: observations.jsonl@sha256:9f3c… (fold v1) -->
| term | tag | familiarity | unlocked | gloss | provenance | last-touched |
|------|-----|-------------|----------|-------|------------|--------------|
| Matérn process | real-world | 🟢 fluent | n/a | covariance family… | ref in seed | 2026-07-17 |
| spine-c5 | internal | 🔴 new | ❌ locked | our term for… | coined in #99 | 2026-07-12 |
```

`familiarity` and `unlocked` are **projections**, not stored fields — see §2. `gloss`/`provenance` are the latest values seen in the log's event payloads. The register is regenerable by any agent at any time (`fold` is idempotent given the same log), so a stale or lost register is a non-event: rebuild it.

**Deep-module framing:** the log is the deep module; the register is a *cached view* over it. All three consumers below read through the narrow interface, never the raw file:
- `observe(event)` — append one line. Total interface for writing.
- `familiarity(concept) → {🔴,🟡,🟢}` — fold the concept's events with the contingency+decay rule.
- `unlocked(concept) → bool` — derived gate predicate for internal terms.

These three verbs are a ≤1-screen shared helper script (`su_fold.py` or equivalent). That is the *entirety* of the mechanical surface every agent depends on. Everything else is prose discipline.

---

## 2. How familiarity updates from the human's writing

**Who writes:** *the agent that is in the conversation at that moment* — whichever Commander / Implementer / Reviewer / Admiral just read the human's message and is about to (or just did) reply. There is no dedicated observer. Observing is step 5 of every agent's inline loop (§4). This is the purest expression of the constraint: the reader model is maintained as a **side effect of normal work**, by everyone, continuously.

**How (the update is a fold, never an edit):** familiarity is not a stored number that gets mutated — it is `familiarity(concept) = fold(events_for_concept, now)`. The fold applies:
- **Contingency rule** (X3): start 🔴; `agent-introduced/taught` nudges toward 🟡; `human-fluent` toward 🟢; `human-ask/stumble` back down. Coarse three-state output, *never a float* — this is the guard against the anti-goal of a scoring engine.
- **Decay** (X1 spaced-repetition intuition, not its math): time-since-last-touch erodes toward 🟡/🔴. A concept fluent six months ago and untouched is re-surfaced, not assumed fresh. Decay is a function of elapsed time in the fold; nothing is scheduled or written.
- **Concept-local** (X3): familiarity is per `concept` slug; expertise on module A never raises familiarity on new concept B.

Because familiarity is *derived at read time*, **there is no cell to overwrite** — which is the entire concurrency story:

### The parallel-agent hazard, and why it dissolves
D's real danger: in an Admiral wave, three Commanders and their Implementers run at once, all wanting to record observations about overlapping concepts. A mutable "familiarity column" would be a classic lost-update race (read 🟡, write 🟢, clobber a concurrent 🔴).

**The append-only representation defines that race out of existence** (Ousterhout: the best fix for an error is to make it impossible, not to handle it):
- Nobody does read-modify-write on shared state. Each agent only **appends its own event**. Appends **commute**: the fold sorts events by `(ts, agent)` before folding, so interleaved or out-of-order arrival yields the same familiarity. The log is effectively a grow-only CRDT (a G-log); merge = set-union of lines, which git itself handles as non-conflicting appends most of the time.
- The one **causal** constraint — an internal term must be `agent-introduced` *before* a `human-fluent` can count toward unlock — is enforced *in the fold by timestamp order*, not by write ordering, so it survives reordering.
- **Write atomicity** is the only genuinely open mechanical point (scoped null §7): single-line `O_APPEND` is atomic under `PIPE_BUF` on POSIX; on Windows a short lockfile or write-tmp-then-append-rename is needed. The *design* guarantees no lost updates; the *implementation* of atomic append is deferred.
- The `concepts.md` register can go stale under a burst of concurrent appends — but it is non-authoritative and freshness-stamped, so staleness is visible, and no *gate decision* is ever taken from a stale cache: the gate (§3) reads the register only after checking its stamp covers the terms in play, else it re-folds the log tail for just those terms (keyed, cheap — §2 of the load story).

---

## 3. The two policies, applied inline by every agent

Both policies are the *same ledger read* interpreted in opposite directions — the fixed spine. Every agent runs both before emitting human-facing text.

### TEACH (real-world concepts — push familiarity up)
For each real-world concept the draft is about to lean on, read `familiarity(concept)`:
- 🟢 → bare mention, peer register, **no explanation** (expertise-reversal: redundant teaching *harms*).
- 🟡 → one-clause reminder only if it's load-bearing this message.
- 🔴 **and** the human hasn't signalled "not now" → fold in **one** short explanation paragraph (Diátaxis explanation shape: name it, the *delta* from what they already command, the load-bearing consequence; stop). Then `observe(agent-taught)`.
- Always surface the **genuinely-new delta** even at 🟢 (expert-blind-spot counter): the agent states the non-obvious piece rather than assuming the expert holds it.

### NEUTER (internal / coined terms — hold the dialect down)
For each internal-tagged term the draft would use *bare*, read `unlocked(concept)`:

> `unlocked(c) := log has an agent-introduced/taught event for c, AND a later human acknowledgment (human-fluent OR explicit ack) for c.` I.e. **the same familiarity gate applied to internal terms** — an internal term below the acknowledged threshold may not appear bare in human-facing text.

Enforcement is inline and uniform ("no coined term until unlocked" enforced *everywhere*, because every agent runs the same predicate):
- `unlocked = true` → the term may be used bare (it has earned its keep with this reader).
- `unlocked = false` → the agent MUST either (a) substitute plain language, or (b) gloss-on-first-use *and* `observe(agent-introduced)` so the clock starts. It may never emit the bare coined term.

This is a **lint the agent runs on its own draft**, not a gate a service imposes. The neuter policy has no privileged owner, which structurally protects the human's low tolerance for per-project dialect across many concurrent projects — the suppression is everyone's standing duty, not a feature that can be forgotten.

### Solving the "giant dictionary in every agent's context" (T-A2)
The human's explicit worry. D's answer is that **agents never preload the dictionary**. The discipline is a *procedure*, and the lookup is **keyed by the terms already in the draft**:
1. The agent drafts its message normally.
2. It extracts the handful of concept-candidate terms it actually used (real-world unfamiliar + internal coined) — O(terms-in-*this*-message), typically 0–3.
3. It queries the register for *only those slugs* (a grep, or `familiarity`/`unlocked` on just those keys), re-folding the log tail only if the stamp is stale for them.

So the context cost is **O(terms in the current message), not O(all concepts in the project)**. The only thing that rides in every agent's context permanently is the *rubric* (the closed `kind` vocabulary + the register discipline) — a short procedure doc, deliberately kept to well under a screen. The *data* stays external and is pulled keyed-on-demand. This is the same "signal-first, don't Read-all" instinct X2 found in codebase-onboarding, applied to the reader model.

---

## 4. Calibration + interleaving inside a real message (the novel core)

The genuinely-novel problem (per the verdicts): hold a standing per-reader model AND blend one paragraph into a working stream without condescending or cluttering. D's version runs as a **five-step inline loop every agent executes**, with no handoff:

1. **Draft** the working message normally (status, decision, diff summary — the actual work).
2. **Scan** the draft for concept-candidates; keyed-lookup their ledger rows (§3).
3. **Calibrate register** from familiarity: default peer/minimal; add depth *only* where a row says 🔴/🟡-and-load-bearing (TEACH), suppress where a row says locked (NEUTER).
4. **Interleave** at most one explanation paragraph, placed *at the point the concept becomes load-bearing* (just-in-time, situated — X3§4), visually set off so an expert can skip it (two-tier: the paragraph is the "short"; depth is pulled via pushback→tutor, §5).
5. **Observe:** `observe()` any teach/introduce you just did, and any `human-fluent/ask/stumble/deferred/pushback` signal in the human's *latest* message. This is the only maintenance cost, and it is a side effect of replying.

**Worked example (real message).** An Implementer reporting a wave result; `matern-process` is 🔴 for this reader, `spine-c5` is a locked internal term:

> Landed the kriging interpolator for the coverage field (issue #88, tests green).
>
> One modelling call worth flagging: I used a **Matérn process** for the spatial covariance rather than a plain squared-exponential. *(New here: a Matérn is a covariance family with a knob for how smoothly correlation decays with distance — squared-exponential forces infinitely-smooth fields, which would have over-smoothed the coverage gaps you care about. Matérn-3/2 keeps the roughness. That's the only reason it's here.)*
>
> This slots into the layer that owns cross-cutting resolution — the interpolator is now the last consumer wired into it.

Note what the loop did: it taught the 🔴 real-world concept in one skip-pable paragraph pitched at peer level (delta + consequence, no build-up); it **neutered** the locked internal term `spine-c5` by writing "the layer that owns cross-cutting resolution" in plain language instead of the coined term; and on the next turn, if Fred replies "yeah Matérn-3/2 is right, keep it," that agent appends `human-fluent` and the concept drifts toward 🟢 — so the *next* agent, keyed-lookup in hand, will drop the gloss entirely. Calibration is emergent from the shared log, achieved with no central model.

---

## 5. The escalation-tutor's trigger and seam

The tutor is **out of the hot path**. It owns no state and does no routine calibration — every agent already does that inline. It is *only* the agent permitted to go long-form, summoned on:

- **Human pushback** (primary): the reply matches "no, that doesn't make sense" / "wait, what are we talking about" / "let's go back." The agent that received it appends `human-pushback` and hands off.
- **Explicit summon:** an `/unpack` or "teach me this" interrupt.

**Seam:** the summoning agent hands the tutor exactly three things — the `concept` slug(s), the path to `.shared-understanding/`, and the offending message. The tutor reads the *same* ledger through the *same* three verbs (no privileged interface), runs a Pocock-style multi-turn deep-dive (mission-tethered, one-question Socratic), and on exit `observe()`s the outcome (`agent-taught`, then `human-fluent` or a residual `human-stumble`/`human-deferred`). It then returns control. So the tutor is a **deep-dive-on-pushback escalation that shares the ledger as a peer**, exactly as the constraint requires — not a coordinator the inline path depends on. Removing it would degrade depth-on-demand but would *not* break routine calibration/neutering, which proves the authority is genuinely distributed.

---

## 6. Honest self-assessment on the five axes

### Depth — *mixed; honest weakest point at the policy layer*
The **data layer is a genuine deep module**: append-only log + fold behind three narrow verbs hides the contingency/decay math, the unlock predicate, and all concurrency handling. Callers say `familiarity("matern-process")` and know nothing of folds or timestamps. **But the policy layer is deliberately shallow** — the interface (a register discipline every agent applies) is nearly as large as the implementation, because calibration/interleaving *executes inside each agent's generation* and cannot be hidden behind a call. This is the structural cost of the constraint: D cannot pull the teaching complexity down into one module the way C can, so that complexity **leaks up into every agent by design**. D's mitigation is to shrink the leaked part to a short rubric + three verb-calls; it cannot eliminate it.

### Locality — *worst of the four, by construction*
Teaching-where-the-work-happens means the change **fans out to every skill that emits human-facing text**. There is no single file that "is" the mechanism. The fan-out is softened to *a reference to one shared discipline doc + three helper calls* rather than N copies of logic, but every human-facing seam is still touched. Low locality is not a flaw to fix here — it is the premise ("in-flow naturalness"). If locality is the dominant axis, pick B or C, not D.

### Seam placement — *right for naturalness, wrong for testing*
The seam sits at the point of generation — precisely where in-flow teaching *must* live and precisely where a test harness *cannot* cleanly intercept. There is no single call site to stub. The data-layer verbs (`observe`/`familiarity`/`unlocked`) are a clean, well-placed seam; the *interleaving judgment* has no seam at all. D optimizes seam placement for the human's reading experience at the cost of the tester's convenience.

### Testability — *bimodal*
- **Fully falsifiable (the important half):** every mechanical pathway is a pure function over a synthetic event log. *Familiarity update* — feed events, assert 🔴→🟡→🟢 monotonicity and decay. *Jargon gate* — assert `unlocked=false` ⇒ no bare coined term (fixture: a locked term must never appear bare; this is a hard, testable invariant). *Concurrency* — replay interleaved/out-of-order appends, assert the fold is order-invariant (the lost-update claim is directly testable). *Teach trigger* — assert a 🔴 load-bearing concept produces exactly one gloss.
- **Only spot-checkable (the soft half):** the *quality* of interleaving and register calibration lives in free generation across many agents; it can be checked by rubric-conformance review or golden-message fixtures, not asserted deterministically. Honest: the falsifiable invariants are exactly the ones that matter for the anti-goals (no un-unlocked jargon leaks; no over-teaching a 🟢 concept), so testability is better than "distributed = untestable" would suggest — but the naturalness itself is not unit-testable.

### Fit to the fixed anti-goals
- **Heavy-machinery risk — LOW.** No scores, no dashboards, no service. The one whiff of machinery is the fold/decay function; guarded by keeping its output a coarse 🔴/🟡/🟢 (never a float) and its code ≤1 screen. Could ship as a plain-text log + a small script.
- **Condescension risk — LOWEST of the four (D's win).** Teaching is inline, peer, at point of need, authored by the same colleague doing the work — it reads as a teammate's aside, not a tutor interrupting to instruct. The expertise-reversal default (minimal, add-on-miss) is baked into step 3 of the loop. Nothing about D structurally invites talking down.
- **Serves BOTH halves equally — YES, most balanced of the four.** The same ledger read drives teach-up and neuter-down; both are standing inline duties with no privileged owner. Crucially, there is **no tutor-shaped gravity** pulling design attention toward the exciting teach half — the human's cycle-3 worry — because there *is* no central tutor to over-invest in. Neuter is as first-class as teach precisely because both are just "what every agent does."

### Where the constraint HURTS (called out plainly)
1. **Consistency of judgment (the core wound).** With no single owner interpreting the contingency rule, two agents can classify the same hedged human sentence differently — one logs `human-fluent`, another `human-stumble`. Familiarity then depends on *which agent happened to be in the room*. Mitigations: a tightly-pinned `kind` rubric with worked examples so classification is mechanical not vibes; evidence-bearing events so mis-classifications are re-adjudicable; periodic curator-style consolidation. **Not eliminated** — see scoped null §7.
2. **The dictionary-load problem is solved for DATA, not fully for DISCIPLINE.** Keyed lookup means no agent preloads all concepts (§3). But the *rubric prose* still rides in every agent's context permanently. Whether that shared procedure is small enough in practice to not be its own context tax is asserted, not proven.
3. **Drift over time.** Independent agents applying an evolving discipline will diverge unless the rubric and helper are frozen and versioned; there is no owner whose job is to hold the line. D leans on periodic consolidation to re-converge, which is a *detective* control, not a *preventive* one.

---

## 7. What I did NOT resolve (scoped nulls)

- **Atomic append cross-platform.** The design *guarantees* no lost updates (no read-modify-write on shared state); the *mechanism* for atomic single-line append on Windows (lockfile vs write-tmp-then-rename) is deferred to build. POSIX `O_APPEND` under `PIPE_BUF` is fine; Windows is the open case.
- **Fold constants.** The *shape* is specified (contingency + time-decay → coarse 🔴/🟡/🟢); the actual thresholds and decay half-life need empirical tuning against real transcripts. Deliberately left as constants, not designed.
- **Judgment-drift bound.** Mitigated (rubric + evidence + consolidation) but I have **no proof** the rubric is tight enough to keep independent agents' classifications consistent. This is D's headline risk and it is unverified — it wants a prototype that replays real multi-agent transcripts and measures classification agreement.
- **Discipline-prose context cost.** Keyed lookup solves the *data* load; whether the standing rubric+helper is acceptably small in every agent's context is asserted, not measured.
- **Pushback detection.** Reliable recognition of "that doesn't make sense / let's go back" (false-positive/negative rate) is left to the harness/pattern; not designed here.
- **Concept identity / slugging.** Who decides two mentions are the *same* concept (intra-project dedup of slugs) is unresolved — a wrong split fragments familiarity across near-duplicate entries.
- **Milestone explainer (K9) interaction.** Out of scope for this excursion; the milestone explainer would consume the same ledger but its trigger/home is designed elsewhere.
