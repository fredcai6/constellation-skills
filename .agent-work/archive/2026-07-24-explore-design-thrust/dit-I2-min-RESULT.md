# DIT I2 — Candidate: `minimal-interface` fixedness grading

**Constraint:** smallest markup that changes executor behavior — one inline tag, nothing else; every extra field must name the downstream decision it changes or be cut.

**One-line thesis:** grade a decision with a single inline tag whose only job is to *license behavior the executor would otherwise not take*. Provenance and the guess-ledger are not fields — they are, respectively, an optional clause inside the tag and a grep-view over the plan. The default is safe, not settled.

---

## The markup

One inline tag, placed at the end of the line that states the decision:

```
<fixed>            <fixed: because…>
<guess>            <guess: settle-by…>
<placeholder>
```

Grammar (machine-parseable, human-trivial):

```
<(fixed|guess|placeholder)(?:\s*:\s*(.*?))?>
```

- Exactly **one** tag per decision, on the **same line/bullet** as the decision it grades. A tag alone on a line, or two tags on one line, is a lint error. (This is the locality invariant — grading cannot drift from the thing graded because they share a line.)
- The optional trailing clause after `:` is **free text**, and its *meaning is tier-dependent*: for `fixed` it is provenance (why this is settled); for `guess` it is the cheapest experiment that would settle it. Same slot, no second field.

### Realistic snippet (a Commander plan / Admiral `Pre-Rulings` block)

```
## Pre-Rulings
- Access tokens are JWT, 15-min TTL.        <fixed: human ruled, 2026-07-20 security review>
- Sessions live in Redis.                   <guess: settle-by a 1hr latency spike, Redis vs Postgres-JSONB>
- Refresh-token rotation window.            <placeholder>
- Errors return RFC-7807 problem+json.      (untagged)
```

This rides the decision bullets that `LAUNCH_ORDER.template.md` (`Pre-Rulings`, `Inherited Latitude`), the Commander plan, and `DESIGN_SPEC.template.md` (`Chosen design`) **already have**. No new artifact, no new section. The Admiral template's existing prose — *"Ruled in advance, each overridable if evidence contradicts it"* — is literally the `fixed` semantics; the tag only makes it per-decision and machine-checkable.

---

## What each tier changes — the executor's fork

The executor branches on the tag at exactly one moment: **mid-run, a decision contradicts observed reality (or a better option appears).** The tag decides what happens next.

| Tag | Executor behavior on contradiction | Mechanical proof it differs |
|---|---|---|
| `guess` | **Revise in place, note the revision, continue.** No escalation, no reopen — revisiting a guess is *not* a plan violation. | No gate blocks it; the linter never flags it. This is the only tier that *licenses free revision*. |
| `fixed` | **Stop; return-to-reopen with reason.** Revising a settled decision costs an escalation (Admiral float / `user-decision`). | The reopen path is the only way to change it; a silent in-place edit is a review defect. |
| `placeholder` | **Hard block if a step leans on it.** Must be resolved before any step consumes it. | The one tier that can *halt* execution — consuming an unresolved placeholder is the linter's hard error. |
| *(untagged)* | **Treated as `fixed`** — conservative. | See degradation below. |

The load-bearing distinction the human asked for — "settled" vs "current guess, revisit allowed" — is precisely `fixed` vs `guess`, and the "revisit is a normal move" claim is *mechanically true*: nothing in the engine or linter blocks or flags a `guess` revision.

---

## Degradation when a plan is partially graded — the key property

**Untagged decisions are treated as `fixed` by the executor, and as a defect by the linter (if load-bearing).**

This makes partial grading degrade *safe*, with two consequences that fall out for free:

1. **Adding the schema can never make an executor more reckless than today.** An ungraded plan behaves exactly like today's plans: every decision is effectively settled, and revising anything asks up. Grading only ever *buys freedom* — marking something `guess` is the sole act that unlocks in-place revision. There is no way for the tag to license a silent divergence the author didn't ask for.
2. **The costly error is structurally prevented.** The asymmetric risk is *revising-a-settled-thing-silently* (divergence from a real decision) vs *escalating-a-guess* (a needless question). Defaulting untagged→fixed spends the cheap error, never the costly one.

So a half-graded plan is strictly no worse than an ungraded one, and strictly better everywhere a tag exists. Grading is incremental and monotonic — you never have to grade the whole plan for it to help.

---

## The two "fields" the brief names — cut as fields, kept as views

The brief's schema wants (b) provenance and (c) a guess-ledger. Under minimal-interface, each must name a downstream decision it changes or be cut. Neither survives *as a field*:

- **Guess-ledger (idea 7) → a grep-view, not a table.** The "table of things we are knowingly guessing" is `grep '<guess'` over the plan. Storing it separately creates a second place that drifts from the tags. The deep-module move: the ledger is a *view reconstituted on demand*, so it is always exactly consistent with the decisions. The reviewer's query *"is anything load-bearing still a guess?"* is `grep '<guess'` **joined against the diff** (load-bearing = something in the change leaned on it).
- **Provenance (idea 10) → the because-clause, not a column.** Provenance changes exactly one downstream decision — the *reopener's* weighing of a `fixed` decision under challenge — and it reads that as prose regardless of any enum. So it rides as the free-text clause inside `<fixed: …>`. **Enumerated provenance kinds (human/measured/inherited) are cut:** no consumer branches on the kind, so the enum is ceremony.

**One deliberate divergence I'll defend:** idea 10 motivates provenance as *"what is load-bearing vs merely written down."* I replace that with **load-bearing = whatever the steps/diff actually consume**, determined at read time, not by a label. A decision is load-bearing because something depends on it — not because someone typed "load-bearing." This is more honest and removes a field.

**Also cut** (the max-flexibility agent's territory, named here as loud skips): confidence gradations (a 0.7-vs-0.8 scale gives the executor no distinct *action* — the fork is 3-way, not continuous); per-slice scope fields (scope is *where the tag lives* — the slice's section — not a field, locality again); an enumerated machine ledger schema (the grep-view is the ledger).

---

## Invariants

- **I1 (locality):** a tag shares its line with exactly one decision; orphan or double tags are lint errors. Grading cannot drift from what it grades.
- **I2 (safe default):** absence of a tag ≡ `fixed` to the executor. The schema only ever adds freedom, never removes safety.
- **I3 (guess-freedom):** revising a `<guess>` in place is never a gate failure and never a linter finding. This is the whole point; it must be mechanically true.
- **I4 (placeholder-block):** a step that consumes an unresolved `<placeholder>` hard-blocks. Placeholders are the only tier that halts.
- **I5 (single source):** provenance and ledger have no independent storage; they are a clause and a view. Nothing to keep in sync.

## Who writes / who reads

| Element | Written by | Read by |
|---|---|---|
| tier (the tag word) | planning author — explorer (spec), Admiral (launch order), Commander (plan) | executor (behavioral fork), reviewer (honesty), pre-flight linter (completeness) |
| because-clause (`fixed`) | author | the reopener weighing a challenged `fixed` decision; reviewer |
| settle-by clause (`guess`) | author | executor / prototyper choosing whether to spike before leaning on it; reviewer |

## Error / conflict modes

- **Malformed tag** (unknown tier word) → linter error; executor falls back to untagged≡`fixed` (safe).
- **`placeholder` consumed by a step** → hard block (I4).
- **Two `fixed` decisions that cannot both hold** → this is the pre-flight conflict linter (idea 29): surfaced as one upfront objection before execution.
- **A `guess` still live at merge on a decision the diff leaned on** → reviewer signal ("load-bearing guess shipped ungraded-up"), not an error — the honest-grading check.

---

## Self-scores (honest, weaknesses named)

**Depth — 4/5.** The tag carries a real 3-way behavioral fork, and the two reframes (ledger-as-view, provenance-as-consumption) are genuine deep-module moves — each hides a would-be artifact behind a query/clause. *Weakness:* the because-clause is **overloaded** — its meaning flips (provenance vs experiment) with the tier, so a reader must know the tier to interpret the clause. Clever, but a real cognitive cost; a stricter design would split them and pay a field.

**Locality — 5/5.** Single inline tag on the decision's own line; no second artifact; ledger and provenance are view + clause, never independently stored (I5). *Weakness:* the reviewer's "load-bearing guess?" determination is a **join between plan and diff** — it is *not* readable from the plan alone. Honest, but it means one of the three consumers can't answer its question from the schema in isolation.

**Seam placement — 5/5.** Rides existing decision bullets in three templates that already exist; the Admiral `Pre-Rulings` prose already *is* fixed-semantics. Zero new artifact types. *Weakness:* three skills must adopt the identical tag or linter coverage is uneven — needs one shared template line each (small, but a real cross-skill dependency, and the exact "corpus-wide ceremony" surface the exploration fears if the tag ever bloats).

**Testability — 4/5.** The linter half (ungraded-load-bearing found; placeholder-consumed blocks; malformed flagged) is cheap unit-testable with a scripted plan fixture. The executor half (guess→revise-in-place vs fixed→escalate) is greppably falsifiable: run the same contradiction under both tags, observe escalate-or-not. *Weakness:* the executor half is a **behavioral eval** (agent-in-the-loop), which x4 flagged as expensive and not-yet-built — it rides the eval-on-change seam (#136) that doesn't exist yet. So half the design is testable today, half is testable only once that seam lands.

---

## Where this sits vs the panel

This is the floor: if the other two candidates can't show a decision the executor branches on that this tag *cannot* express, the extra fields are ceremony. The honest pressure-test for the synthesizer: is there a consumer that branches on provenance *kind* or a confidence *number*? I found none. If max-flexibility surfaces one, that field earns its place; otherwise this is the schema and the rest is the untaken road.
