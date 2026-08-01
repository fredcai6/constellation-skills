# DIT I2 candidate — constraint: **common-caller-first**

Schema name: **inline decision grade** (`@grade:`). One tag, welded to the decision it grades. The "guess ledger" is not an artifact — it is a grep over these tags.

I designed the two consuming moments first, then kept only the fields those two moments actually read. Everything else was cut.

---

## Ideal moment (a) — executor mid-gate, decision contradicts observed reality

The executor is inside `g1-implement`. It was told to reuse the WAL. It observes the WAL is append-only-unsafe for this write path. It reads the decision anchor **right there** and needs, in five lines, to know: proceed, revisit, or escalate — and if revisit, revisit *toward what*.

What it reads at the anchor (this is the whole experience — no second file opened):

```
decision:dedup-wal — dedup writes reuse the existing WAL, not a new journal.
  @grade: guess · leans g1-implement · settle: 20-line spike appends 2 records, assert ordering survives a crash
  → contradiction lands inside a guess the slice leans on: revisiting is FREE, not a plan violation.
    run the settle-experiment (or cheaper), then log the ruling; the guess becomes settled/measured.
    no reopen, no float — you are inside the blast radius the plan already granted you.
```

Contrast — same shape, a *settled/human* decision instead:

```
decision:error-envelope — public error shape is {code,msg,retriable}.
  @grade: settled/human · leans g1-implement,g1-review
  → contradiction against a human ruling: STOP. you may not silently revisit.
    float to the Admiral with the observation; only the tier that ruled it can unsettle it.
```

The load-bearing insight of common-caller-first: **the tier is not a label, it is an index into an action.** The five lines the executor reads are (1) the decision, (2) tier + why it holds that tier, (3) the decision rule *keyed to the tier*, (4) for a guess, the experiment to revisit *toward*, (5) where the ruling goes. A bare `fixed/guess` tag with none of (3)–(5) would make the executor stop and think about mechanics — the exact failure this exploration exists to kill.

## Ideal moment (b) — reviewer / pre-flight linter asks "is anything load-bearing still a guess?"

The query is one command, run before execution (this **is** idea 29's batched plan-conflict pre-flight — the guess ledger and the pre-flight scan are the same artifact viewed once):

```
$ py scripts/grade_lint.py .agent-work/execute.json --slice g1
```

The answer:

```
LOAD-BEARING GUESSES (2) — slice g1 leans on these, still unsettled:
  decision:dedup-wal        guess   settle ✓   leans g1-implement
  decision:flush-batch-size guess   settle ✗   leans g1-implement      ← guess with no experiment
UNGRADED (1) — in a decisions block, no @grade → read as placeholder, FAIL:
  decision:retry-policy     —       —          appears in g1-implement.imperative
SETTLED (4): error-envelope(human) wal-path(inherited) codec(measured) tls(human)
lint: FAIL — 1 ungraded load-bearing decision; 1 guess missing settle-by
```

That table is the entire "guess ledger." It is never written by hand and never drifts, because it is generated from the inline tags every time it is asked for. The reviewer reads the same command's output as the acceptance check: zero ungraded load-bearing decisions, every guess carries an experiment.

---

## The schema — derived from exactly what those two moments consume

One inline tag on the decision, four fields, each traceable to a moment that reads it:

| field | grammar | who reads it | dies if cut |
|---|---|---|---|
| **tier** | `settled` \| `guess` \| `placeholder` | (a) picks the decision rule; (b) buckets the report | the whole thing |
| **why** (provenance) | on `settled`: `/human` \| `/measured` \| `/inherited` | (a) routes the revisit of a settled decision to who can unsettle it | (a)'s settled-branch collapses to "all settled → escalate" (safe, coarse) |
| **leans** | gate/item ids in *this* plan | (b) makes "load-bearing" a query; (a) tells the executor "is this mine now?" | (b) degrades to "is anything a guess" (loses *load-bearing*); rolling-wave loses its is-it-my-slice signal |
| **settle** | one line: the cheapest experiment | (a) what to revisit *toward*; (b) presence is the guess's validity check | a guess becomes an ungrounded guess — the exact thing being prevented |

**Markup — identical across both surfaces**, so there is one grammar to learn and one parser:

Markdown (Pre-Rulings, Decision Anchors, latitude Pre-Rulings) — a child line under the decision bullet:

```
- Dedup writes reuse the existing WAL, not a new journal.
  `@grade: guess · leans g1-implement · settle: 20-line spike, assert crash-ordering`
```

JSON (`EXECUTE_PLAN` `anchors.decision[]`) — appended to the decision string, so grade and decision cannot separate:

```json
"decision": ["decision:dedup-wal — reuse WAL not new journal @grade: guess · leans g1-implement · settle: 20-line spike, assert ordering"]
```

`@grade:` is the sole greppable anchor. `·` separates fields; only `@grade: <tier>` is hard-required — every other field's absence degrades gracefully (below), never errors.

---

## Invariants

1. **One grade per decision.** A decision line inside a recognized decisions block (`## Pre-Rulings`, `Decision Anchors`, `anchors.decision[]`) carries exactly one `@grade:`. Absent → readers treat it as `placeholder`; linter FAILs.
2. **tier is exactly one of** `{settled, guess, placeholder}`.
3. **settled ⇒ provenance present** (`/human|/measured|/inherited`); absent → WARN (advisory to the executor; load-bearingness isn't at stake).
4. **guess ⇒ `settle:` present and non-empty** → else FAIL. A guess with no experiment is the ungrounded guess we exist to prevent.
5. **leans ids resolve** to real gate/item ids in *this* plan; a dangling id → FAIL (a lying load-bearing query is worse than none). `leans` may be empty (future/unattached decision).
6. **placeholder ⇒ no provenance, no settle** (either would mean it is really a mis-tagged guess/settled).
7. **Locality is enforced, not hoped.** The grade is textually adjacent to its decision (md child line / same JSON string). **There is no separate ledger file.** Idea 7's "guess ledger" is the `grade_lint.py` view, never a maintained second place — this kills the tag-here/ledger-there drift the brief's *Locality* axis warns about.

## Writers / readers

- **Writers** (grade written at the same keystroke as the decision — no separate grading pass): Admiral → launch-order & latitude Pre-Rulings; Commander → Mission Frame Decision Anchors + `EXECUTE_PLAN.anchors.decision`; explorer / to-issues → spec decisions.
- **Readers**: executor mid-gate (a); reviewer + `grade_lint.py` pre-flight (b); the next-slice regenerator (reads which guesses settled and which placeholders crystallized — feeds regenerate-don't-reread).

## Degradation when a plan is partially graded — stated per consumer

- **Executor** on an ungraded decision → **treats it as `placeholder`** (undecided; unsafe to silently lean on). This inverts today's implicit "everything written is fixed" — the human's whole settled-vs-guess ask. The default only *bites* when the slice leans on it or reality contradicts it; un-leaned-on ungraded decisions stay silent future-work (rolling-wave).
- **Linter**: ungraded-in-a-decisions-block → FAIL; guess missing `settle:` → FAIL; load-bearing `placeholder` on the current slice → FAIL; settled missing provenance → WARN; dangling `leans` → FAIL. A plan with *zero* grades reports every decision as placeholder (loud, honest migration signal — see weaknesses).

## Executor decision rules, per tier, at a reality-contradiction

- **settled/human** → STOP; float to the Admiral/human. Only the ruling tier unsettles it. (Maps to latitude Decision Classes: surfaced / out-of-taxonomy.)
- **settled/measured** → you may re-measure. If the new measurement contradicts, that *is* evidence: revisit, log the new measurement as the new provenance, note it in your return. Measured decisions are honestly falsifiable by better measurement.
- **settled/inherited** → a constraint from outside this run (prior-wave verdict, latitude pre-ruling). You cannot unsettle it; float to the tier that owns it.
- **guess** → revisit FREELY (the human's rule: revisiting a guess is a normal move, not a violation). Run `settle:` (or cheaper) if the slice leans on it; log the ruling; the guess becomes `settled/measured`. No reopen, no float.
- **placeholder** → never decided. If the slice **leans** on it: decide now within latitude → log → regrade `settled`; if the decision is beyond latitude (architecture/scope), float. If the slice does **not** lean on it: leave it — a later slice crystallizes it (rolling-wave / regenerate-don't-reread).

The depth here: **a settled decision's provenance IS its unsettle-routing key**, and it reuses the latitude contract's existing escalation machinery rather than inventing a parallel one.

---

## Self-scores (honest, weaknesses named)

- **Depth — 5/5.** The tier indexes an action, not a label; `provenance` sub-types route the revisit; `leans` doubles as the rolling-wave "is-it-mine-now" signal. No field is decorative.
- **Locality — 5/5.** Grade welded to decision; ledger is a derived view; invariant 7 forbids a second place. *Weakness:* in JSON the grade rides inside a free-text string, so JSON-schema validation can't catch a malformed grade — only `grade_lint.py` can. The parser must be the source of truth, and it's hand-rolled.
- **Seam placement — 4.5/5.** Rides decision bullets in templates that already exist; no new artifact; the one new script (`grade_lint.py`) doubles as idea 29's pre-flight, a real consolidation. *Weakness:* the linter recognizes decisions only inside known blocks — a decision written as loose prose outside a `Decision Anchors`/`Pre-Rulings` section escapes the ungraded-catch. Convention-dependent hole.
- **Testability — 4.5/5.** Moment (b) is rock-solid and mechanical: feed a plan with an ungraded load-bearing decision → assert FAIL; fully graded → PASS. Moment (a) — "executor revisits a guess but floats a settled/human" — is behavioral/eval-shaped (softer; connects x4's eval-on-change seam), only testable if the executor actually consults the grade. The linter is falsifiable today; the executor behavior needs one scripted-principal scenario.

### Named weaknesses / untaken forks
- **Cross-artifact `leans` is unresolved.** A latitude Pre-Ruling that a *commander gate* later leans on can't be linked by a single-file linter — `leans` resolves only within one plan. Cross-plan load-bearing needs a compile step the schema doesn't specify.
- **Migration cost is real.** Legacy plans with zero grades read as all-placeholder. Mitigated by the leaned-on/contradiction gating (silent otherwise), but the first graded epic pays an authoring tax.
- **`leans` needs gate ids at authoring time.** Launch-order/latitude pre-rulings authored before the spine exists carry empty `leans` until the plan compiles — those decisions aren't slice-linkable up front.
- **Minimum viable subset:** irreducible floor is `@grade: <tier>` (3 tiers) + `settle:` required on `guess`. That alone lights moment (a)'s proceed/revisit/escalate and a coarse moment (b). `leans` sharpens (b) to *load-bearing*; `provenance` sharpens (a)'s settled-revisit routing. Ship the floor first; the two sharpening fields are the fast-follow.
