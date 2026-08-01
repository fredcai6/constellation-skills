# DIT I2 — guess-grading schema, candidate **max-flexibility**

Author: `dit-I2-flex`. Constraint: design the *richest coherent* fixedness-grading schema, then state honestly the minimum viable subset and name the parts that die unused.

---

## 0. The deep-module bet (the thing that makes "max" not "ceremony")

The whole risk in a rich schema is that it becomes a **shallow module**: many fields, all of them exposed at every read site, so every reader must understand the whole vocabulary. That is exactly the corpus-wide-ceremony failure this exploration exists to avoid.

My candidate is built around one structural move that makes richness survivable:

> **The executor's read-interface is ONE field. The writer's richness is hidden behind an id.**

At the moment that actually matters — an executor mid-gate hits a decision that contradicts observed reality — it reads a single token (`revisit=`) and gets `proceed / revisit-free / reopen / escalate`. It does **not** read provenance, confidence, the settling experiment, or the dependency graph. All of that lives in a **Decision Ledger** keyed by id, pulled only by the *rare* readers (reviewer, pre-flight linter, next-slice regenerator). So the schema can be wide on the write side while staying a narrow, deep module on the hot read path. That is the difference between "rich" and "ceremony," and it is the axis I am spending my max-flexibility budget on.

---

## 1. The full markup (rich form) in a realistic plan snippet

Two encodings, one source of truth:

- **Inline grade tag** `[G:<id> <tier>]` — rides *at the point of use*, wherever a decision is stated (mission frame line, gate `anchors.decision` entry, launch-order pre-ruling, per-slice spec section). Carries only the two things a reader needs at a glance: the **id** (a link into the ledger) and the **tier** (the one hot field, denormalized for locality). Greppable: `\[G:(\S+)\s+(settled|guess|placeholder)\]`.
- **Decision Ledger** — one machine-parseable table per plan artifact, keyed by id, carrying every heavy field. Lives inside the Mission Frame's existing *Decision Anchors & Decision Pressure* section (no new artifact type; the section is formalized into a table).

### 1a. Mission Frame — the Decision Ledger (rich carrier)

```markdown
## Decision Anchors & Decision Pressure

<!-- grade-ledger v1 — machine-parseable; columns fixed; one row per graded decision -->

| id | decision                          | tier        | provenance          | conf | scope    | revisit      | depends-on | settles-by (cheapest experiment / signal)                       | expires        |
|----|-----------------------------------|-------------|---------------------|------|----------|--------------|------------|------------------------------------------------------------------|----------------|
| d1 | engine owns spine state, agents read via stdout | settled | inherited-constraint:decision:engine-authority | high | epic     | reopen-plan  | —          | —                                                                | —              |
| d2 | slot storage = flat pre-sized array | guess     | assumed             | med  | slice-1  | free         | —          | prototype array vs slab-alloc; signal = alloc p99 < 2ms @50k ents | after slice-1  |
| d3 | wave granularity = one vertical slice | working-guess | human-ruled:LAUNCH_ORDER#Pre-Rulings | med | epic  | escalate     | —          | first slice ships end-to-end without a cross-wave reopen          | —              |
| d4 | telemetry sink API shape          | placeholder | —                   | low  | slice-3  | free         | d2         | deferred; re-derive at slice-3 plan from d2's settled result       | stale-by-default |
```

Provenance uses a **closed kind + optional pointer**: `human-ruled:<ref>`, `measured:<ref>`, `inherited-constraint:<node>`, `assumed` (the honest "we picked it, nothing backs it yet"). The `:ref` resolves the "what is actually load-bearing vs merely written down" question (idea 10) — a `human-ruled:LAUNCH_ORDER#Pre-Rulings` decision is load-bearing; an `assumed` one is fair game.

### 1b. Gate `anchors.decision` in `execute.json` — inline tags (hot path)

```json
"anchors": {
  "decision": [
    "[G:d1 settled] engine-authority governs this gate — do NOT hand-edit spine.json",
    "[G:d2 guess] slot storage flat array — revisit is FREE this slice if profiling contradicts it",
    "[G:d4 placeholder] telemetry sink shape unresolved — do not build against it; gate stubs the seam"
  ]
}
```

### 1c. Launch-order Pre-Ruling — graded

```markdown
## Pre-Rulings
- [G:d3 working-guess] Decompose the epic as vertical slices. Overridable if the first slice
  cannot ship end-to-end without a cross-wave reopen — float to Admiral before re-deciding (revisit=escalate).
```

The same tag rides in all four artifact families. One vocabulary, four homes, no new file type.

---

## 2. Field catalogue — writers, readers, and what each field *changes downstream*

Every field must name the decision it changes, or it is ceremony. Here is that accounting for the full rich set (the "ceremony" column is my honest self-audit and drives §5):

| field | writer(s) | reader(s) | what it changes downstream | ceremony risk |
|-------|-----------|-----------|----------------------------|---------------|
| **id** | any planning skill | executor (as link), linter, regenerator | the join key; makes locality-via-denormalization checkable | none — load-bearing |
| **tier** `settled\|working-guess\|placeholder` | planner | **executor (hot path)**, reviewer, linter | executor's revisit default; reviewer's honesty check | none — the core |
| **revisit** `free\|reopen-gate\|reopen-plan\|escalate` | planner | **executor (hot path)** | *the* field the executor keys off at a contradiction | none — see §3; this is the real interface |
| **provenance** (closed kind + ref) | planner | reviewer, executor (when deciding to override) | tells executor whether a change is free or needs the ruler's consent; tells reviewer what's load-bearing | **collapses to 3-4 kinds** (§5.4) |
| **scope** (slice/epic) | planner | executor, regenerator | which decisions carry into next slice vs re-derive (rolling-wave, idea 8; regenerate, idea 25) | earns its place *iff* C ships |
| **settles-by** (experiment + signal) | planner | reviewer, prototyper dispatch (idea 11) | names the cheapest experiment that ends the guess; a guess without one is unfalsifiable | **struct collapses to one string** (§5.5) |
| **conf** `high\|med\|low` (or numeric) | planner | reviewer, gauge/curator | reviewer prioritization; cross-epic calibration | **numeric dies (idea 24 culled)**; qual survives thin |
| **depends-on** | planner | linter, executor | reopening a foundational guess cascades to dependents | **mostly dies** (§5.2) |
| **expires** / stale-by-default | planner | executor, regenerator | plan-expiry (idea 9): beyond current slice, re-affirm not obey | **superseded by regenerate** (§5.3) |

---

## 3. Invariants

1. **Every inline `[G:id tier]` resolves to exactly one ledger row, and the tiers agree.** This is the denormalization contract that buys locality without a single source-of-truth. Lint-enforced (§4, linter check L1). Violation = dangling/contradictory tag.
2. **Silence is not settled.** An ungraded decision is treated by every reader as `working-guess, revisit=escalate` — the *conservative* default. Grading omission therefore fails loud (the linter's prime target, idea 29), never silently hardens into a fixed decision. This is the single most important invariant: it makes "did they forget to grade this?" and "is this deliberately a guess?" the *same safe state* until a human distinguishes them.
3. **`revisit` is derivable from `tier` unless overridden.** Default map: `settled→reopen-plan`, `working-guess→escalate`, `placeholder→free`. A planner may override per-decision (e.g. a settled-but-cheap decision gets `revisit=free`), and the override is the *only* reason `revisit` is a separate column rather than a pure function of tier. If overrides prove rare, `revisit` folds back into `tier` (a named simplification path, not a wart).
4. **A `working-guess` or `placeholder` in the current slice's scope MUST have a `settles-by` entry** (or an explicit `deferred` marker with a re-derive pointer, as d4 shows). A load-bearing guess with no experiment is unfalsifiable and the linter rejects it (idea 7 made enforceable).
5. **`settled` requires a non-empty provenance with a ref.** You cannot mark something settled on `assumed`. Settled-on-nothing is the exact dishonesty the reviewer is hunting; the invariant makes it structurally impossible to write.
6. **Ledger id space is per-artifact and stable within a run.** Regeneration (idea 25) of a later slice mints fresh ids for re-derived decisions but *carries forward* `scope=epic` settled rows verbatim — the ledger is the thing that survives a regenerate, so epic-scope settled rows are the plan's durable spine.

---

## 4. How executor / reviewer / linter key off the schema

**Executor, mid-gate, hits reality contradicting a decision** (common-caller moment (a)):
1. Find the decision's inline `[G:id tier]` — it's right there in the gate anchors it's already reading.
2. Read `revisit` (from the tag override, else the tier default). Branch:
   - `free` → revisit in place, note it, proceed. *No reopen, no escalation.* This is the human's core ask: revisiting a guess is a normal move, not a plan violation.
   - `reopen-gate` / `reopen-plan` → use the engine `amend`/`reopen` verb; surface to principal.
   - `escalate` → float to Admiral / ask the human (delegate-not-replacement).
3. Only if it needs *more* (who ruled this? what would settle it?) does it pull the ledger row by id. The heavy fields are lazy-loaded, not on the hot path.

**Reviewer, "is anything load-bearing still a guess?"** (common-caller moment (b)):
- Query the ledger: rows where `tier ∈ {working-guess, placeholder}` **and** `scope` intersects the shipped slice **and** some gate's anchors cite the id → these are load-bearing guesses. Check each has a `settles-by`. Check no `settled` row rests on thin provenance. This is a *table query*, which is why the ledger is machine-parseable — the reviewer's job becomes falsifiable (testability §6).

**Pre-flight linter** (idea 29, future `verify_plan_grading.py` — the `verify_*.py` family is the precedent seam):
- **L1** every inline tag resolves + tiers agree (invariant 1).
- **L2** every ungraded decision-shaped line flagged (invariant 2) — surfaced as ONE upfront batch, not a mid-run trickle.
- **L3** every current-slice guess/placeholder has `settles-by` (invariant 4).
- **L4** every `settled` has provenance+ref (invariant 5).
- **L5** contradiction scan: two ledger rows asserting incompatible things, or an inline tag contradicting a `constraint:` anchor.
- Output: a single pre-execution objection list (the batched-plan-conflict surface).

---

## 5. Honest minimum viable subset, and the parts I expect to die

### 5.1 Minimum viable subset (what alone changes executor behavior)
**Inline `[G:id tier]` with three tiers, plus the tier→revisit default map (invariant 3), plus invariant 2 (silence≠settled).** That is the whole floor. It delivers the human's stated ask — settled-vs-guess is a normal distinction, revisiting a guess is free — with one greppable tag and zero new artifacts. No ledger required; the ledger is pure enrichment. **If the panel ships only this, the exploration's goal is met.**

### 5.2 `depends-on` — **expect it to die.** Cascade-reopen is elegant, but slice plans carry a handful of decisions and the executor sees the dependency by reading the plan. The maintenance cost (keeping the edge list correct) exceeds the payoff except in unusually large specs. Keep the *column* optional; expect it empty in ~all real plans.

### 5.3 `expires` / stale-by-default — **expect it to die, superseded by package C.** Regenerate-don't-reread (idea 25, human's "full agreement") makes staleness *structural*: the next slice's plan is regenerated fresh, so nothing stale exists to carry an expiry. An explicit `expires` field is redundant with the regeneration model. It survives only if C does *not* ship and plans persist across slices — i.e. it's a hedge against C, not a real field.

### 5.4 Arbitrary/open provenance kinds — **the open vocabulary dies to a closed 3-4 enum.** The useful set collapses to exactly idea 10's three: `human-ruled / measured / inherited-constraint`, plus `assumed` as the honest null. "derived / convention / external-mandate" all fold into those or into "it's a guess." Max-flex says *allow* arbitrary kinds; honesty says nobody will mint a fourth that earns its keep.

### 5.5 `settles-by` as a structured object (cost/owner/deadline/signal sub-fields) — **the struct dies; the string survives.** Idea 7's real content is "name the cheapest experiment" — a free-text `experiment; signal` string does that. The machine sub-fields (numeric cost, owner, deadline) are ceremony a planner won't maintain. Keep one string column.

### 5.6 Numeric confidence — **dies (idea 24 already culled).** No per-decision outcome metrics at volume under this harness, so calibration is unmeasurable. Qualitative `high/med/low` survives *thin* as a reviewer-prioritization hint and nothing more; drop it if reviewers ignore it.

### 5.7 Per-decision `contradiction-guard` predicates — **die except where cheap.** A machine-checkable assertion per decision is expensive to author, and the executor mostly notices contradiction by observation, not by a pre-written predicate. Survives only for the naturally-machine-checkable few (a version pin, a file count) — the linter's L5 leans on `constraint:` anchors it already has, not on new per-decision predicates.

### 5.8 The subset I'd actually recommend (the "medium" between my max and I2-min's floor)
`id` + `tier` + `revisit` (with override) + closed `provenance` (3-4) + `scope` (slice tag) + free-text `settles-by`, carried inline for the hot path and in a ledger table for the reviewer/linter. Six columns, all with a named downstream reader in §2. This is max-flex *after* the deaths above are honestly subtracted — and it's what I'd put in the spec.

---

## 6. Self-score (honest, weaknesses named)

**Depth — 4/5.** Real decision-changing meaning: the executor's proceed/revisit/reopen/escalate branch is driven by actual fields (`revisit`, provenance-ref), not labels-for-labels. The deep-module move (one hot field, rich fields lazy behind an id) is where the depth lives. *Weakness:* the full rich form's depth is front-loaded onto the writer — a planner must understand more than a reader does, and an over-eager planner filling every column *is* the ceremony risk the schema is one lint-rule away from becoming.

**Locality — 3/5.** Grade lives with the decision via the inline tag (good), but the heavy fields live in a *separate* ledger table — a real second place. I defend this with invariant 1 (lint-enforced tier agreement) and by denormalizing only the one hot field, so drift is *detectable* rather than *prevented*. *Weakness, named:* two-place encoding is a genuine locality cost; a reviewer must trust the linter ran. I2-min's single-inline-tag candidate will beat me on this axis and that is the honest trade — I buy machine-queryability with a locality hit.

**Seam placement — 5/5.** Zero new artifact types: the ledger is the Mission Frame's existing *Decision Anchors* section formalized into a table; inline tags ride in `anchors.decision`, launch-order Pre-Rulings, and per-slice spec sections that already exist. The machine reader is a new `verify_plan_grading.py`, but that slots into the established `verify_*.py` / `curate_corpus.py` family — a known seam, not a new kind of thing.

**Testability — 4/5.** The two target behaviors are both falsifiable: (a) "executor treats guess vs fixed differently" — a scripted scenario where a gate hits a `revisit=free` guess must proceed-in-place, and the *same* scenario with a `settled` decision must reopen/escalate; the branch in §4 is directly exercisable. (b) "linter finds ungraded load-bearing decisions" — feed a plan with an ungraded decision cited by a gate anchor, assert L2 fires; feed a guess with no `settles-by`, assert L3 fires. The ledger being a fixed-column table is what makes these assertions clean. *Weakness:* "graded *honestly*" (settled-on-thin-provenance) is only partly machine-checkable — invariant 5 catches settled-without-ref, but settled-on-*weak*-ref is a human reviewer call the linter can't falsify.

---

## 7. One-para positioning for the orchestrator

Spend the flexibility budget on **one axis only** — separating the executor's narrow hot-path read (`tier`/`revisit`, inline, local) from the reviewer/linter's rich queryable ledger (provenance, settling experiments, scope) behind an id. That single move is what lets a wide schema stay a deep module instead of becoming corpus-wide ceremony. Everything else in the rich form is honestly enrichment that mostly dies (§5): `depends-on`, `expires`, open provenance, the settles-by struct, and numeric confidence are all named deaths. Ship the §5.8 six-column medium; keep the inline-tag floor (§5.1) as the guaranteed-valuable core that meets the human's ask on its own.
