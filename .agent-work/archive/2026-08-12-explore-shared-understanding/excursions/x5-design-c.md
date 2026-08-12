# X5 · Design C — Tutor-as-service (ports-and-adapters)

**Constraint:** a **first-class Tutor agent OWNS** the reader model + calibration + the jargon gate. Every other agent reaches the intelligence through **ONE clean seam** (the *Tutor Port*). Optimize for a clean single-owner seam — one adapter today, but designed so a *second* caller proves the boundary.

**Nothing held FIXED in the handoff is redesigned.** The spine (two policies over one tagged+familiarity ledger), the register rule, observed-not-quizzed familiarity, per-project scope, summon-on-miss, and the anti-goals are all taken as given. This doc only decides *where the intelligence lives and how callers reach it*.

---

## 0. The one-sentence shape

There is exactly one object that knows anything about "what Fred knows": the **Tutor service**. It owns a private per-project ledger and exposes a **deep, narrow port** — four operations. Every other agent is an **adapter** that calls the port; no other agent stores familiarity, judges jargon, or picks teaching depth. The two FIXED policies (teach real-world up / neuter internal down) are **two read-methods on one object over one ledger**, which is the spine realized as literal code structure.

---

## 1. The seam (the Tutor Port) — the whole contract a caller must know

A deep module's interface is *everything a caller must know*: the operations, their invariants, their ordering, and their error modes. Here is the entire port. A caller that has read this section needs to know **nothing** about familiarity ordinals, the contingency rule, unlock thresholds, or expertise-reversal — all of that is behind the seam.

### 1.1 The four operations

```
# --- NEUTER policy (Half B): the jargon gate. Read-only. ---
may_use(term, *, surface="human", dial=None) -> Verdict
    Verdict = ALLOW_BARE
            | ALLOW_WITH_GLOSS(gloss: str)      # use it, but carry this one-line gloss on first use
            | FORBID(reason: str, plain: str)   # do not spend this coinage on the human; say `plain` instead

# --- TEACH policy (Half A): the delta decision. Read-mostly (see invariant I4). ---
teach_delta(concept, *, context, dial=None) -> TeachFragment | NONE
    TeachFragment = { text: str,          # the genuinely-NEW delta, already written at peer register
                      depth: SHORT|DEEP,  # SHORT = one pointer sentence; DEEP = the ~paragraph
                      placement: str,     # hint: "before the decision", "footnote", "inline-parenthetical"
                      debt_token: str }   # opaque handle the caller echoes back if the human defers
    NONE  = the human already commands this concept at register — say nothing (fade).

# --- The ONLY writer of familiarity (observed-not-quizzed). ---
note_usage(human_text, *, context) -> UpdateReceipt
    UpdateReceipt = list of { concept, from_level, to_level, evidence_line }   # every change is traceable

# --- The conversational tutor, summoned not always-on. ---
summon(reason, *, focus_concept=None) -> TutorSession
    reason in { MISS, PUSHBACK, HUMAN_ASKED }   # "no that doesn't make sense" / "let's go back" / explicit
```

### 1.2 Invariants (what the port guarantees, so callers can stay dumb)

- **I1 · Single-writer familiarity.** Only `note_usage` (and a `summon` session's outcome) may change a familiarity level. `may_use` and `teach_delta` **never** mutate familiarity. Consequence a caller can rely on: querying the gate or the delta is *free of side effects* — an agent may call `may_use` on ten candidate terms while drafting without perturbing the reader model. This is what makes the dependency safe to reach through mid-draft.
- **I2 · One ledger, two reads (the spine, enforced structurally).** `may_use` and `teach_delta` read the **same** `familiarity` field of the **same** entry. "No coined term until unlocked" (K2) is *literally* `may_use` returning non-`ALLOW_BARE` while `familiarity < WORKING` on an `internal`-tagged entry. The two halves cannot drift apart because they are two methods dispatching on one field.
- **I3 · Monotone legibility.** Every familiarity change appends one human-readable `evidence_line` to the entry's observation log and is reported in the `UpdateReceipt`. There is no silent drift and no number the agent invents (honors observed-not-quizzed + the no-heavy-machinery anti-goal).
- **I4 · Query provenance exception, narrowly scoped.** `teach_delta` on a concept absent from the ledger MAY append a `first-surfaced` **provenance** line (creating a stub entry at level `NEW`) — because "this concept just became load-bearing" is itself an honest observation. It still may **not** set familiarity above `NEW`. This is the one documented crack in I1, called out so no caller is surprised.
- **I5 · Register parity.** `teach_delta` will never return novice scaffolding (worked-up build, redundant restatement) for a concept at `WORKING`+. Expertise-reversal is enforced **once, centrally** — a caller physically cannot condescend by mistake, because it does not choose the register; the tutor does.
- **I6 · Caller owns its own voice.** The tutor authors the *teaching fragment*; the **caller** authors its own message and performs the final stitch (see §5). The port never rewrites the caller's status/reference prose.

### 1.3 Ordering (the contract's temporal rules)

- **O1 · Inbound before draft.** On a human turn, the agent calls `note_usage(human_text)` **before** it drafts its reply, so the reply is pitched against the *just-updated* reader model. Skipping this means teaching against stale familiarity.
- **O2 · Gate-and-delta at draft time.** While drafting a human-facing message: for each candidate coined term call `may_use`; for each load-bearing *new* concept call `teach_delta`; then stitch; then send. (`note_usage` is inbound-only — the agent's own outbound prose is not evidence of *Fred's* familiarity.)
- **O3 · Summon supersedes serving.** A `summon` session is the only path that produces multi-turn teaching and the richest observations; its outcome is written last and wins over passive `note_usage` for the concepts it touched in that turn.

### 1.4 Error modes (the honest part — a central dependency must define failure)

Because *every* human-facing message now reaches through one service, the port must specify per-operation behavior when the tutor is slow or unreachable. Each operation fails toward the anti-goals, not away from them:

- `may_use` **fails CLOSED for `internal` terms** (unknown/unavailable → treat as not-unlocked → return `FORBID`/plain): if we can't confirm coinage is earned, don't spend it. **Fails OPEN for `real-world` terms** (→ `ALLOW_BARE`): a precise real-world term is never the harm.
- `teach_delta` **fails to `NONE`**: when in doubt, say nothing rather than teach blindly (a wrong teach is condescension; silence is not).
- `note_usage` **fails by queueing**: the human's text is buffered for replay so an observation is never lost — familiarity may lag, but it does not silently corrupt.
- `summon` **fails loud**: if the tutor can't come up, the caller tells the human plainly ("let me pull up the tutor — one sec / it's unavailable"), never fakes a teaching turn.

This failure matrix is *itself* a cost of the constraint (see §8) — a distributed design (D) would have no such matrix because there is no service to be down.

---

## 2. The ledger entry — shape + home (owned by the tutor)

**Home:** the tutor's own private store, per-project, append-only, learning-records-as-ADRs (Pocock X1/X2, docent freshness X2). Not a shared global book (T-B: per-project, re-asking across projects is fine). Concretely `<<project>>/.tutor/ledger/NNNN-<concept>.md`, one file per concept, plus a thin `index.md`. Callers **never read this directory** — they only see it through the port. That opacity is the whole point of the constraint: the storage can change (flat files → sqlite) without touching a single caller.

**Entry shape** (deliberately ordinal, no numeric score — anti-goal guard):

```
id:            0042
concept:       "Matérn process"
kind:          real-world | internal        # the FIXED real-world-vs-internal tag
familiarity:   NEW | SHAKY | WORKING | FLUENT   # 🔴🟡🟢🟢+ — an ORDINAL, derived, not guessed
gloss:         "a covariance kernel with a tunable smoothness knob"   # one-line plain gloss
provenance:    "surfaced by Implementer in kriging spike, 2026-07-14"  # where it came from
unlock:        locked | unlocked            # internal terms only: introduced + acknowledged
last_touched:  2026-07-14                    # for time-since-contact decay
debt:          false | "believe-you-for-now @2026-07-12"   # K5/K6 deferred concept debt
freshness:     <sha of the source truth this gloss was written against>   # docent-style stamp
observations:  |                             # append-only ADR-like log — the audit trail for I3
  - 2026-07-14 first-surfaced (NEW)          # I4 provenance line
  - 2026-07-15 asked "wait, smoothness of what?" -> hold at SHAKY
  - 2026-07-16 used "Matérn nu=3/2" correctly in own message -> WORKING
```

**`familiarity` is a pure function of `observations`, not an independent stored guess.** The tutor derives the ordinal by folding the observation log through the contingency rule. This keeps it human-legible (Fred can read *why* he's marked WORKING) and falsifiable in a test (feed observations → assert level). It is the ITS "student model as an overlay" (X3 §1) made concrete: the ledger is an overlay whose nodes correspond to real-world/internal concepts, and familiarity is the annotation.

---

## 3. How familiarity updates from Fred's writing (`note_usage`)

The *only* observation source that exists in this setting is Fred's own prose (X1 self-explanation; X3 §2 contingency). `note_usage(human_text)` is where that signal enters, and it is the **single writer** (I1).

Mechanism the tutor runs privately (callers never see it):
1. **Detect** which ledger concepts appear in `human_text` (name match + gloss-synonym match, scoped to this project's ledger).
2. **Classify the contact** per the contingency/fading rule (X3 §2): *fluent correct use* → step the level **down** in explanation-need (up in familiarity: SHAKY→WORKING→FLUENT); *a stumble, a question, a mis-use, "wait / what's that"* → step **up** in explanation-need (hold or drop the level); *no contact for N sessions* → **decay** one step (time-since-`last_touched`, X1 spaced-repetition *intuition*, not the math).
3. **Append** one `evidence_line` per change and return the `UpdateReceipt` (I3).

What I deliberately do **not** solve: the *classifier* that decides "fluent use" vs "stumble" from free prose. That is the genuinely-novel calibration core (IDEAS_BOARD, X2·X3·X4 verdict) and mining intent from unstructured text is unsolved by every source. I specify its **interface, its single-writer invariant, and its ordinal output** — not the NLP inside. Scoped null (§9).

---

## 4. How TEACH and NEUTER are served through the seam

Both halves are just reads of the same entry (I2) — this is the spine.

**NEUTER (Half B) = `may_use`.** Before an agent puts a coined term in human-facing text it asks the gate. For an `internal` term still `locked` (familiarity < WORKING): `FORBID(reason, plain)` — the agent says the plain thing instead, keeping the private dialect in agent-to-agent artifacts. For an `internal` term just being introduced: `ALLOW_WITH_GLOSS` — allowed once, carrying its gloss, which is exactly the "unlock" event (the agent then feeds Fred's acknowledgement back through `note_usage`, flipping `unlock: unlocked`). For a `real-world` term Fred commands: `ALLOW_BARE`. The T-A2 context-bloat problem is *solved by the constraint*: no agent carries "a giant dictionary" — it asks the one service per term, on demand.

**TEACH (Half A) = `teach_delta`.** When a concept becomes load-bearing, the agent asks the tutor whether (and how deep) to teach. The tutor reads familiarity and returns: `NONE` if Fred commands it (fade — expertise reversal, I5); a `SHORT` pointer if it's at the edge of what he holds; a `DEEP` ~paragraph only on a real gap or an explicit dial-up. Crucially the fragment contains the **genuinely-new delta only** (expert blind spot, X3 §3), written at peer register — never a from-first-principles build.

Because both are methods on one object reading one field, they **cannot** disagree about how well Fred knows something. That structural guarantee is this design's best answer to "serve BOTH halves equally."

---

## 5. Calibration + interleaving in a real message — who writes the blended paragraph?

This is the crux the constraint forces me to answer. Options under a central service:

- **(a) Tutor returns a fully-blended message.** Caller passes its whole draft in; tutor stitches teaching into it and returns finished prose. → Rejected as primary. It makes the tutor a bottleneck on *every human-facing sentence*, forces the caller to surrender authorship of its own voice (I6 violated), and pushes the whole draft across the seam each turn (latency + coupling).
- **(b) Tutor authors the teaching fragment; caller does the final stitch.** → **Chosen.**

**Division of ownership (the answer):**
- The **tutor owns the calibration decision and the fragment content**: *whether* to teach, *how deep*, and *the exact delta text at the right register*. That is the hard, reader-modelling, expertise-reversal-sensitive part — it belongs behind the seam.
- The **caller owns placement and its own voice**: it already holds the surrounding status/reference sentences and knows where a `"before the decision"` fragment drops in naturally. It splices the `TeachFragment.text` at the `placement` hint and sends.

So: **the calling agent writes the blended paragraph, but every teaching word in it was authored by the tutor at a register the caller cannot downgrade.** The seam carries a small typed fragment, not the whole message — cheap, and it keeps each agent's voice its own while guaranteeing the teaching is calibrated once, centrally.

Concrete trace (Implementer reporting a spike, dial = peer):
1. `note_usage("...why Matérn and not RBF?...")` → receipt bumps "Matérn process" SHAKY→WORKING, "RBF kernel" stays NEW.
2. Draft the status message normally.
3. `may_use("kriging", surface="human")` → `internal`-ish, locked → `FORBID(plain="Gaussian-process interpolation")`. Caller writes "Gaussian-process interpolation."
4. `teach_delta("RBF kernel", context=spike)` → Fred at NEW but it's a real-world concept at the edge → `SHORT` fragment: *"(RBF assumes infinitely-smooth fields; Matérn's ν knob lets you dial that smoothness down to match real terrain — that's the whole reason to prefer it here.)"* placement `inline-parenthetical`.
5. Caller splices the parenthetical into its sentence about the kernel choice, sends one clean message. No separate lesson, no condescension, one blended paragraph.

**Honest wrinkle:** interleaving *quality* is therefore **co-owned** — the tutor guarantees the fragment's register/depth; the caller guarantees it reads naturally in place. That is the one spot where the "single owner" claim is softened (see §8 seam-placement). An optional richer call `interleave(draft, concepts) -> blended_draft` (option (a) as an opt-in "batteries-included" adapter) is left as a boundary-proving experiment, not built (§9).

---

## 6. Trigger / summon contract

Two altitudes, matching the FIXED "tutor summoned on miss, not always-on":

- **Serving (near-silent, always-reachable).** `may_use` / `teach_delta` / `note_usage` are cheap, single-shot, non-conversational. The service is *always reachable* for these — but reachable ≠ talking. The tutor never fronts the human here; it just hands verdicts to callers. This is the continuous, inline duty (T-A) realized as "every agent calls the port," without every agent carrying the logic.
- **Summoning (conversational, triggered).** `summon(reason)` spins up the tutor as an actual agent that talks to Fred, on exactly the FIXED triggers: `MISS` (an agent detected Fred didn't follow a concept), `PUSHBACK` ("no, that doesn't make sense" / "let's go back"), or `HUMAN_ASKED` ("hold on — what are we talking about?"). Only summon produces a real teaching turn; its outcome writes the richest observations back to the ledger (O3) and can pay down concept debt (T-E).

The distinction *reachable-service vs summoned-agent* is what lets this honor "not always-on" while still being a first-class service. The service is infrastructure; the tutor-as-interlocutor is an event.

---

## 7. The second caller (proving the boundary)

The constraint demands the seam be designed so a second caller proves it. Today's **one adapter**: the working agent (Commander/Implementer) drafting human-facing messages. Designed-for additional callers, each of which must get identical behavior *without knowing the reader model*:

- **Milestone explainer (K9, X4 Diátaxis + docent).** Calls `teach_delta` to pitch each concept in a durable build-milestone explainer at the *same* reader model, and stamps `freshness` from the same field. Proves `teach_delta` is caller-agnostic (in-flow message vs durable artifact get the same calibration).
- **Curator jargon-density lint (K8).** Calls `may_use` over a finished human-facing summary to flag unglossed locked coinage. Proves `may_use` is a pure predicate usable by a *linter*, not just a drafter.
- **Interrogator front door.** Calls `note_usage` on intake answers to seed familiarity. Proves `note_usage` is the single writer regardless of *which* agent observed the text.

Three callers, one port, no shared state outside the tutor — that is the ports-and-adapters payoff and the falsification test for the seam.

---

## 8. Honest self-assessment on the five axes (incl. where the constraint HURTS)

**Depth — STRONG (this constraint's headline win).** Everything hard — the reader model, the contingency update, decay, expertise-reversal register selection, the unlock threshold, the fragment authoring — is hidden behind four operations. A caller knows verbs (`may_use`, `teach_delta`, `note_usage`, `summon`) and typed returns; it knows *nothing* about ordinals or thresholds. Maximum complexity hidden, minimum surface exposed. This is the deepest of the four constraints by construction.

**Locality — MIXED, and honestly the weak axis.** The *intelligence* is maximally local — one owner, one store, change the update rule in one place. **But the *call sites* fan out**: every human-facing agent grows a dependency edge to the tutor and must insert `note_usage`/`may_use`/`teach_delta` calls at the right points in its draft flow (O1–O2). So the *logic* is contained while the *wiring* is distributed — the inverse of constraint D, where the logic is distributed but there is no wiring to a service. If callers forget to call the port, the whole mechanism silently no-ops. That coupling is the price of central ownership.

**Seam placement — STRONG for three of four operations, CONTESTED for one.** `may_use` (a pure predicate), `note_usage` (the single writer), and `summon` (an event) sit exactly where callers and tests want them — clean verbs, obvious boundaries. The contested boundary is **interleaving**: authorship of the blended paragraph straddles the seam (tutor writes the fragment, caller places it, §5). It is a defensible split, but it is the one place a reviewer can reasonably argue the line is in the wrong spot — and where a future `interleave()` call might move it. I flag this rather than hide it.

**Testability — STRONG (the constraint's second win).** Each pathway is an isolated, typed, mostly-pure operation falsifiable against a fixture ledger: *familiarity update* (`note_usage(text)` → assert `UpdateReceipt`), *teach trigger* (`teach_delta` → assert `NONE` vs `SHORT` vs `DEEP`), *jargon gate* (`may_use` → assert `Verdict`), *summon* (assert session on the three triggers). Because familiarity is a pure fold of the observation log (I3), a test feeds observations and asserts the ordinal with no mocking of NLP. This is the best-tested of the four designs.

**Fit to the FIXED anti-goals:**
- *Serves BOTH halves equally — BEST of the four.* `may_use` (neuter) and `teach_delta` (teach) are sibling methods on one object reading one field (I2). The spine isn't a convention here, it's the class structure; the halves *cannot* drift.
- *Condescension risk — LOW.* Expertise-reversal is enforced once (I5); no caller can talk down by accident because no caller picks the register.
- *Heavy-machinery risk — HIGHEST of the four (this is where the constraint HURTS most).* A first-class service with its own store *is* machinery — precisely the silhouette the anti-goal warns against ("no new services for their own sake"). I mitigate with a plain-text ADR-like store and a strictly ordinal familiarity (no scores, no dashboards), but the constraint structurally pushes toward the thing we're told to fear. A minimal-machinery design (A) buys most of the same behavior with none of this apparatus; this design must *justify the service by the second-caller payoff*, and if that second caller never materializes, the machinery is unearned.

**Where the central-service constraint HURTS — collected honestly:**
1. **Latency / round-trips.** Every human-facing message now makes several port calls (one `note_usage`, N `may_use`, M `teach_delta`) before it can send. In an agent setting these are model-mediated, not microseconds — real turn-latency the other designs avoid.
2. **A dependency every agent reaches through.** One service in the hot path of all human-facing output → an availability and failure-mode surface that *only this design has to define* (the fail-open/closed matrix, I1.4). That matrix is design work the anti-goals would rather we not need.
3. **Cold-start.** An empty ledger means every early query returns `NEW`, so the tutor over-teaches until it calibrates — the busiest teaching is exactly when the model is worst.
4. **Silent no-op coupling.** The mechanism only works if callers remember to call; a missed call site fails quietly (locality cost, restated as a runtime hazard).
5. **The authorship straddle** (§5) — the one un-clean part of an otherwise clean seam.

**Net:** best on Depth, Testability, and equal-halves; worst on heavy-machinery risk; genuinely mixed on Locality. It wins *if and only if* the second caller is real — the constraint is bought by the boundary, not by today's single adapter.

---

## 9. What I did NOT resolve (scoped nulls)

- **The contingency classifier.** How `note_usage` actually decides "fluent use" vs "stumble" from free prose. Interface + single-writer invariant + ordinal output are specified; the NLP inside is the unsolved calibration core (X2·X3·X4 verdict) and I did not solve it.
- **Whether `interleave(draft)` (full-stitch, option (a)) earns its keep** over the chosen fragment-stitch. Left as a boundary-proving experiment; picking it would move the contested seam (§8).
- **Decay schedule concretely.** "Time-since-`last_touched`, one step per N idle sessions" is named as intuition (X1); N is untuned.
- **Summon vs passive reconciliation.** O3 says the summon outcome wins for concepts it touched; the *merge* when a passive `note_usage` and a summon session disagree on an *untouched* neighbor concept is unspecified.
- **Ledger concurrency.** Two agents calling `note_usage` in the same session — single-writer-*per-op* is assumed; real locking/serialization on the store is not designed.
- **Register dial (K4) plumbing.** `dial` appears as an optional parameter on `may_use`/`teach_delta` (Fred's coarse per-day tolerance), but whether it's a per-call arg, a session global, or a ledger-level bias — and who sets it when — is left open.
- **Cross-project boundary at the service level.** Per-project is honored by a per-project `.tutor/` store, but whether one running tutor process serves multiple projects (with strict partition) or one-per-project is not decided.

---

*Design only; nothing built. One constraint (tutor-as-service, ports-and-adapters), one candidate.*
