BLOCK

blocking_findings: 1

# REVIEW_RESULT — g4-review, issue #467 (epic #418)

Survey driven to consolidation at
`.agent-work/issue-467-trip-semantics/g4-review/review.json` (lease `g4rev-467`,
21 items, all visited, `consolidate --verdict BLOCK`).

**Engine I ran:** `scripts/checklist_engine.py` **in this worktree** (161503 bytes on disk,
158377 as the blob; HEAD `70e2d779`) — the copy carrying the #467 fix. Not an installed bundle.
All probe output, all mutation runs and all evidence numbers below come from that copy.

**Verdict in one line:** the mechanism is well built and every claim the implementer makes about
it is true — but the one rendered compliance signal is guaranteed to be cleared by the very close
the HARD band orders the agent to perform, and the shipped line says the opposite.

---

## THE BLOCKING FINDING

### B1 — the mandated close silences the compliance signal, and the shipped line denies it

**Where:** `scripts/checklist_engine.py:1500-1508` (the `ledger_note` render) and
`docs/CHECKLIST_SCHEMA.md`, "The compliance signal" section.

**Reproduce:** `.agent-work/issue-467-trip-semantics/g4-review/probe_clearing.py` — hand-built
spine, real `gauge.json` stamped from the clock, real CLI in a subprocess, no mocks.

Three shipped mechanisms compose into the defect:

1. At/over hard, `advance --mechanical` is **refused** (g2's no-silent-close rule). I ran it:
   `REFUSED: g2: context is at/over the hard limit, so this gate cannot be closed silently`.
   So the **only** legal way to close a gate over the line is `advance --why "..."`.
2. `advance --why` appends a new `why_trail` record.
3. `begin_over_line_records` matches an entry only when `entry["why_ref"] == _latest_why_record(cl)["id"]`.
   A new why-record therefore supersedes **every** existing ledger entry at once.

So the close the HARD advisory *orders* the agent to make is **guaranteed** to empty the selector
and remove the rendered line. There is no path that closes a gate over the line without silencing
the mark.

Measured, on a gauge parked at 0.20 with `hard = 0.15` for the whole run:

| step | ledger on disk | selector | rendered line |
|---|---|---|---|
| refused BEGIN at g2 | `tl-1` | 1 | present |
| released BEGIN at g2 (work proceeds over the line) | `tl-1`, `tl-2` | 2 | present |
| **the same agent closes g2 with `advance --why`** | `tl-1`, `tl-2` | **0** | **absent** |
| a further refused BEGIN at g3 | `tl-1`, `tl-2`, `tl-3` | 1 | present (count resets to 1) |

Across that 3-gate runaway, **3** over-the-line begins were recorded; the rendered line never
claimed more than **2**, and at the seam — where a fresh agent or the Commander runs `current` —
it was **absent**. A compliant agent that closed its gate and stopped produces the same absence.
**Green in both worlds.** That is the failure mode this gate exists to prevent.

Two shipped statements are falsified by this:

- **The engine's own line.** The single rendered compliance line ends
  `"Closing this gate does not clear the record."` I closed that exact gate and the line
  disappeared. Under the charitable reading ("the record" = the append-only list) the sentence is
  true — the entries do persist — but the clause it sits in has already scoped everything to
  *"under this understanding"*, and closing the gate is precisely what changes the understanding.
  A compliance string that is ambiguous between "true" and "false" is not a compliance string, and
  an agent that wants the line gone learns from the engine's own behaviour that closing the gate
  removes it.
- **The doc.** `docs/CHECKLIST_SCHEMA.md` says the understanding moves on when *"a fresh agent
  records its own `why`, or a `reopen` appends a reopen-marker"*. The mechanism cannot tell a fresh
  agent from the offender; the offender's own close is the likeliest superseder in exactly the
  runaway scenario the ledger was built for. This is the "verify on what the agent is TOLD" trap
  (standing trap 1) reappearing one level up.

The implementation's own test agrees with me and calls it correct:
`test_compliance_line_is_absent_once_the_recorded_begin_is_superseded` executes
`start g2` → `advance g2 --why "u2 — a fresh agent's understanding"` and asserts the line is gone.
That is byte-for-byte the offender's path; only the comment says "a fresh agent". The test **pins
the defect as intended behaviour**.

**Why this is blocking rather than an observation.** Close criterion 5 asks that the scoped limit be
written down and **not overclaimed**. The declared limits (an agent that stops without running a
verb; "records begins, not work"; "an empty ledger never means compliant") are all present and
honest. This one is not declared, is contradicted in two places, and is the limit that decides
whether the observable survives to the seam at all. The handoff's own framing settles it: *"if the
observable it ships is green in both worlds, the whole issue closes on nothing."*

**Not prescribing the fix** — but the finding is narrow, and at least three cheap exits exist:
correct the sentence to what is true; render live and historical marks separately (the entries are
all still on disk, so no new state is needed); or declare this limit as plainly as the other three
are declared. Any of them is a small edit. I am not asking for the keying to change — the keying
was handed down as close criterion (b) and is correctly implemented.

---

## PER-CHECK FINDINGS AGAINST THE NINE CLOSE CRITERIA

### 1. Every defect shape discriminates — **PASS (non-blocking)**

I counted **17** shapes, not the 16 the handoff implies: the table has **12** numbered rows (1–12),
not 11, plus `5b`/`6b`/`6c`/`6d`/`6e`. I constructed **every one myself** in
`g4-review/probe_two_worlds.py` — spines hand-built in the probe, `gauge.json` written from the
clock, CLI shapes driven through a real subprocess, and **no mock anywhere in the advisory path**
(I pass a real `base_dir` holding a real gauge instead of patching `_read_gauge`).

**17 constructed, 17 discriminate, 0 identical.** The sharp ones:

- **Shape 2** — both worlds run the identical command on the identical spine and both return
  `rc=0` with the identical stdout `g2 -> in-progress`. `trip_ledger` is the *only* difference.
- **Shape 3** — the refused entry survives the raise, read back off the file on disk: `rc=1` with
  `tl-1/begin-refused` vs `rc=0` with no key when the gauge is 2h stale.
- **Shapes 5 / 5b** — I asserted the two ledgers **equal** before measuring, so only the keying can
  be what differs: 1 vs 0 both ways.
- **Shape 6** — the healthy advisory is a **strict prefix** of the defective one (verified), so the
  shipped string is provably unaltered and the delta is exactly the added line.
- **Shape 8** — 6 non-begin verbs over a real over-hard gauge, count asserted, none leaves a key;
  `start` writes one.

### 2. All 19 mutations re-run — **PASS**

Sanctioned route exactly: edit `scripts/checklist_engine.py` in place, run the test file, revert
with `git checkout --`, assert `git diff --quiet` clean **before** the next. **`reverted_clean=True`
on all 19; `scripts/`, `tests/` and `docs/` are clean now** (`git status --porcelain` on those paths
is empty). Anchors were authored by me from the source, not copied from the implementer's driver.
Driver: `g4-review/mutate.py`; raw results: `g4-review/mutation-rerun.json`.

**19/19 killed by their named test. No survivors. No equivalent mutants needed.**

| # | named test red | my total | log's total |
|---|---|---|---|
| N1 | yes | 23 | 23 |
| N2 | yes | 5 | 5 |
| N3 | yes | 3 | 3 |
| N4 | yes | 2 | 2 |
| N5 | yes | 2 | 2 |
| N6 | yes | 1 | 1 |
| N7 | yes | 12 | 12 |
| N8 | yes | 1 | 1 |
| N9 | yes | 3 | 3 |
| N10 | yes (SUBFAILED ×3) | 3 | 3 |
| N11 | yes | 11 | 11 |
| N12 | yes | 2 | 2 |
| N13 | yes | 2 | 2 |
| N14 | yes | 3 | 3 |
| N15 | yes | 1 | 1 |
| N16 | yes | 1 | 1 |
| N17 | yes (SUBFAILED ×1) | **1** | 23 |
| N18 | yes | 6 | 6 |
| N19 | yes | 11 | 11 |

My first pass reported N10 and N17 as survivors; that was **my** regex failing to parse pytest's
`SUBFAILED(param) path::Class::test` line format. I re-ran both and dumped every failure line
verbatim (`g4-review/mutate_raw.py`) — in each case every failure is a `SUBFAILED` on exactly the
named test. Recording that here because a `FAILED`-only grep would have produced a false BLOCK, and
the mutation log warns about precisely this.

**N17 is the one number I do not reproduce, and the difference favours the implementation.** The
log's N17 appends `+ ledger_note` to the SOFT return, but `ledger_note` is scoped inside the HARD
branch — so that mutation is a `NameError`, i.e. a crash, not a behaviour change, and its blast
radius of 23 is crash noise. I implemented the behavioural form (compute the note in the soft
branch). It still kills `test_compliance_line_never_appears_below_the_hard_band`, with a **total of
1**. The guard is *more* specific than the log claims. Filed as `tc3`.

### 3. No CLI verb can write a ledger entry — **PASS**

Claim **and** method verified. My own `ast` scan (100 function defs; guard asserts >50):

```
functions naming 'trip_ledger' : ['_append_trip_entry', 'begin_over_line_records']
callers_of(_append_trip_entry) : ['_trip_hard_gate']
callers_of(_trip_hard_gate)    : ['dispatch']
_run_verb calls _append_trip_entry: False    _run_verb calls _trip_hard_gate: False
```

Plus: no `pop`, no `del`, no reassignment of the key anywhere in the file; exactly **1**
`TRIP LEDGER` render site in `scripts/`. Behavioural twin reproduced (shape 8). N18 falsifies the
claim as advertised (6 failed). The `ast` route is the right method — it reads the engine's own
call graph rather than a hand-maintained verb list, so it cannot drift as verbs are added, and it
asserts what it looped over.

One scoping note, not a finding: `_append_trip_entry` is an ordinary module-level Python name, so an
external *importer* could call it. The claim under review is about CLI verbs, and that holds.

### 4. A `None` reading claims neither — **PASS**

With **no gauge at all**: `start` over the line returns `rc=0`, no `trip_ledger` key is created, and
`_trip_advisory` returns `""`. With a **future** `observed_at` (clock skew, handoff trap 3): the
reading is discarded, `rc=0`, no key, and the advisory is the `CONTEXT GAUGE SILENT` text with no
`TRIP LEDGER` line. Silence is neither a compliant nor a non-compliant claim. N8 is a genuine
targeted kill from the claim side (1 failure), and the guard-side gap it does not close is declared
honestly by the implementer rather than papered over.

### 5. The scoped limit is written and not overclaimed — **FAIL (blocking)**

See **B1**. The three declared limits are present, plainly worded, and uncontradicted elsewhere in
the doc. The fourth — the one that decides whether the observable reaches the seam — is undeclared
and contradicted in two places.

### 6. `_trip_advisory` extended, not duplicated — **PASS**

One computation, verified three ways: `grep 'TRIP LEDGER' scripts/` = 1; `callers_of(begin_over_line_records) == ['_trip_advisory']`;
and in source `ledger_note` is computed once above the two HARD returns and appended to each. N13
and N14 each kill one sub-branch independently, so neither is dead code. The pre-existing HARD
strings are pinned by **equality** in the new tests, so they could not have been silently rewritten
— I confirmed this independently by observing that the healthy advisory is a strict prefix of the
defective one.

### 7. Append-only holds — **PASS**

`reopen`'s cascade (which supersedes *evidence*) leaves the prior entry byte-identical and the
ledger only grows (1 → 2). A pre-seeded `tl-1` survives a new trip byte-identical. `--dry-run`
persists nothing. No code path mutates or removes an entry. N3 and N4 both killed.

### 8. Backward compatibility — **PASS**

A spine with no ledger key driven through `advance`/`start`/`advance` below hard never acquires the
key (3 verbs, count asserted). A `why_exempt` spine with no `why_trail` at all writes
`why_ref: None` and the selector still matches it — the mechanism degrades correctly rather than
going silent. A malformed `trip_ledger` (`None`, a string, a dict, a list containing non-dicts)
never raises on the read-only `current` path.

### 9. `CHECK_THAT_CANNOT_FAIL.md` is a genuine artifact — **PASS**

219 lines, and it earns them. It names the defect as a **missing contrast** with five concrete
sub-forms; explains the invisibility with three compounding reasons (green stops inquiry / the
author supplies the contrast from memory / expertise confers no immunity); gives a cost table of
what caught each of four specimens and states plainly that careful self-review caught none of them;
and ends with a concrete, cost-ordered list of what a reader does differently. It then argues
*against* the framing it was handed — that the "irony" reading makes this filable as a story about
one issue, where the evidence says four actors, all forewarned, is a base rate — and closes with an
honest limit on its own self-inspection claim. This is not a compressed line. Non-blocking
inconsistency at NB4.

---

## THE FIVE CLAIMS I WAS ASKED TO ATTACK

### A1 — the ninth field `why_ref` — **CONFIRM the field; REJECT the evidence offered for it**

**Is it genuinely irrecoverable?** Yes, and for a better reason than the one given. The implementer
argued timestamp granularity; I measured `_now()` and it is **microsecond**-precision, not second,
so ordering is rarely ambiguous — that argument is weak. The real reason is that
`_latest_why_record` is not a function of ordering at all: a record is live only if **no later
reopen-marker names its gate**, so reopens appended *after* the trip change what an "as of now"
derivation returns, and reconstructing "as of then" means truncating the trail by timestamp and
re-running the supersede rule. Critic finding 14's *"recoverable from `why_trail`"* is wrong on the
supersede rule, not merely on granularity. A recorded fact is also auditable where a derived one
silently drifts if `_latest_why_record`'s semantics ever change.

**Is N7's 12-test radius evidence of load-bearingness?** **No.** N7 sets `why_ref` to `None`, which
makes every entry fail the keying — behaviourally the same as dead-coding the selector (N11, 11
tests, largely the same set). N7 proves the **keying** is load-bearing. It cannot distinguish
"record the field" from "derive the field", which is the actual question. The load-bearing argument
is the replay argument above, and it was not offered.

**My independent recommendation: keep `why_ref`.** I am not bound by the Commander's recommendation
and I reach the same place by a different route.

### A2 — the four single-test mutations — **all four are specificity, not triviality**

- **N6** — killed by `test_ledger_records_the_per_gate_hard_line_not_a_global_constant`, which
  carries `assertNotAlmostEqual` against the **default** hard. That is exactly the positive control
  a trivial `hard == default` test would lack, and a dropped reserve produces the default.
- **N8** — killed by `test_ledger_a_none_reading_writes_no_entry_and_makes_no_compliance_claim`,
  which asserts **both halves** (no entry AND no claim) and ends with an explicit positive control
  re-reading the same spine *with* a gauge. Without that last line the test would survive a
  dead-coded advisory. This is the load-bearing fail-safe and the test is strong.
- **N15 / N16** — both killed by `test_compliance_line_names_the_count_and_the_latest_begin`, whose
  fixture is deliberately **three entries of two kinds** and which asserts full string **equality**
  plus `assertNotIn("1 begin(s)")`. A single-entry or uniform fixture would have survived both.
  Non-blocking NB5: the two shapes share one test, so they have a single point of coverage (`tc2`).

### A3 — the declared TDD deviation on m2 — **does NOT weaken the guarantee; it strengthens it**

TDD's anti-vacuity value is "the assertions fail when the mechanism is absent". *Deleting*
`begin_over_line_records` would have produced an `AttributeError` — a red that proves nothing about
what the assertions measure. Dead-coding it to `return []` keeps the API and removes only the
behaviour, which is a strictly sharper red and is literally mutation N11 (which I re-ran: 11 failed,
named test red). It was declared in the implementer's own words rather than attested as a red it had
not seen. Correct call.

### A4 — the declared negative-only test — **honestly declared; a related claim is looser than stated**

I asked the question by running it. Under N11 I dumped every failure line:
`test_compliance_signal_is_empty_on_a_spine_that_never_carried_a_ledger` **does not appear** — it
stays green, exactly as declared. It is a 3-line legacy-shape guard whose expected value genuinely
is `[]`, it is declared in both the result and the log, and it is explicitly not counted as
evidence. This is not the g3-M5 failure mode.

**NB4 (non-blocking):** two *further* absence tests also survive N11 —
`test_compliance_line_is_absent_once_the_recorded_begin_is_superseded` and
`test_compliance_line_never_appears_below_the_hard_band`. The implementer's table says both "carry a
positive control in the same test". They do, but that control asserts **the ledger entry exists**,
not **that the signal renders**, so it does not defend against a dead selector. Both are killed by
other mutations (N9 and N17 — I re-ran both), so the coverage is real; the claim about their
positive controls is looser than stated, and the log's "one test stays green" is scoped to one class
in a way that reads as more complete than it is.

### A5 — the `amend` authority — **honest and adequate**

One amendment in the plan's audit log. Its `--reason` names the exact defect, the proof (*"piped
exit 0, bare exit 5 on a no-match selector"*), and why the fix restores the signal. Its
`--authority` string **declares** the non-human source rather than asserting "human". Six
`retext-check` ops, all on its own postconditions, all tightening. I confirmed the pipe is gone from
the plan file. Doctrine gap filed as `tc1`: the engine accepts any `--authority` string, so "human
ratification" is a convention nothing enforces.

---

## EVIDENCE RE-MEASURED (all in this worktree, engine `scripts/checklist_engine.py`)

| command | my measurement | handoff's |
|---|---|---|
| `pytest -q tests` at HEAD `70e2d779` | 1858 passed, 2 skipped, 821 subtests, exit 0 | 1858 / 2 / 821 ✓ |
| `pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'` at HEAD | 25 passed, 384 deselected, 13 subtests | 25 / 384 / 13 ✓ |
| `pytest -q tests/test_checklist_engine.py` at HEAD | 409 passed, 120 subtests | 409 / 120 ✓ |
| same, with `scripts/checklist_engine.py` + `tests/test_checklist_engine.py` at parent `9997c32d` | 384 passed, 107 subtests | 384 / 107 ✓ |
| the selector, same parent content | 384 deselected, no tests collected | exit 5 ✓ |

**Delta = +25 passed, +13 subtests, with `384 deselected` unchanged** — so all 25 tests are genuinely
new, confirmed independently. I derived this by checking out the two changed source files at the
parent rather than by running the whole tree twice, because those are the only files in the diff
that any test reads; the tree was restored with `git checkout` (no CRLF renormalization, so I did
not walk into the implementer's `test_context_manifest` trap). Zero `FAILED` lines at HEAD, so the
mechanical failure-distribution command has an empty result.

---

## OUT-OF-SCOPE OBSERVATIONS (triage candidates, recorded in the survey)

- **tc1** — the engine accepts any `--authority` string on `amend`/`waive`, so "human ratification"
  is a convention nothing enforces; an agent can self-authorize by typing a string.
- **tc2** — N15 and N16 have a single point of coverage (one shared test).
- **tc3** — a mutation that makes the module raise is a crash, not a kill; the g4 log's N17 is one,
  and its 23-failure radius is crash noise. A rule that a mutation must leave the module importable
  would have caught it.
- **tc4** — the Trip section now assembles the same band judgment (fill, hard, model, gate) by hand
  at three sites and passes it as seven loose parameters. A later Trip-section consolidation
  candidate, deliberately not done here.
- **tc5 (new, from the Fowler pass)** — `outcome` is a bare string whose two legal values live in
  three places that must agree by convention; a named constant would make N10's defect shape
  structurally impossible rather than test-caught.

## NON-BLOCKING FINDINGS

- **NB1** — `docs/CHECKLIST_SCHEMA.md`'s supersede narrative names only "a fresh agent" and
  "a reopen". Folded into B1 because it is the doc half of the same defect.
- **NB2** — the mutation log's N17 total (23) is crash noise; the honest behavioural total is 1.
- **NB3** — the handoff and the implementer's table say "11 numbered shapes"; there are 12.
- **NB4** — `CHECK_THAT_CANNOT_FAIL.md` line 172 claims *"Every one of this gate's 25 tests is
  written this way"* (two worlds, name the differing field), which the implementer's own result
  contradicts by declaring one negative-only test. Also the looser positive-control claim under A4.
- **NB5** — N15/N16 single point of coverage (`tc2`).

## FOWLER REFACTORING PASS

Record: `.agent-work/issue-467-trip-semantics/g4-review/fowler-pass.json`;
`python scripts/verify_fowler_pass.py <record>` exits **0**
(`smells=12, flagged=['data-clumps','primitive-obsession','long-parameter-list'], overridden=['large-class','comments-as-deodorant']`).

**Flagged (all observations, none blocking):** data-clumps and long-parameter-list — the band
judgment is assembled by hand at a third site and `_append_trip_entry` takes 7 parameters; the
natural refactor is a value object, but it would touch what g2/g3 shipped, which this handoff
excludes. primitive-obsession — the `outcome` string vocabulary.

**Overridden with logged standards:** *large-class* — the engine is deliberately one self-contained
vendored file, which is the skill-distribution model (`references/checklist-engine.md`); splitting
it would break every installed bundle. *comments-as-deodorant* — the high comment ratio records
issue-numbered **why**, which is this file's documented house style and the durable-context
requirement in `global-crew.md`, not cover for unclear code.

**Absent:** long-method, duplicated-code (actively and verifiably avoided — one computation, one
render site), feature-envy, shotgun-surgery, divergent-change, message-chains,
speculative-generality (no new verb, no flag, no config hook, closed outcome vocabulary).

## WHAT I COULD NOT VERIFY

Nothing material. Two notes:

- I did not re-run the **full** suite at the parent commit (6m41s per run, and it would have required
  checking out the whole tree). I derived the +25/+13 delta from the only two source files in the
  diff that any test reads, which is a tighter measurement than the full-tree subtraction and is not
  exposed to the CRLF/`git status` hazard the implementer documented.
- The implementer's own driver and raw results live outside the repo
  (`%TEMP%/g4_mutate.py`). I did not read them — I authored my own anchors from source, which is why
  the N17 discrepancy surfaced at all.

## WORKFLOW FEEDBACK

- **The one thing that genuinely helped:** naming the sanctioned mutation route, the tree-cleanliness
  protocol, and the seven standing traps. Trap 3 (clock-skew/stale gauge) and trap 4 (`main()` does
  not save on `current`) would each have cost me a false result; I generated every fixture timestamp
  from the clock because of it.
- **The shape count is wrong.** "11 numbered shapes plus the `5b`/`6b`–`6e` variants" — the table has
  **12** numbered rows. I was told to count them myself, which I did, but a reviewer who trusted the
  number would have under-constructed by one and never known.
- **The engine byte-size in trap 6 does not match anything.** The handoff says 156060 bytes; the file
  is 161503 on disk (CRLF) and 158377 as a blob. The *intent* — "use this worktree's copy, not an
  installed bundle" — is right and I followed it, but the number cannot be used to confirm you have
  the right file, which is what a size is for. A `git rev-parse HEAD:scripts/checklist_engine.py`
  hash would be checkable.
- **The `SUBFAILED` format is a trap that deserves to be a standing trap.** The mutation log warns
  about it in prose, but the handoff's stop conditions do not, and a `FAILED`-only grep reports two
  false survivors — which under close criterion 2 ("any mutation that leaves its named test green is
  a BLOCK") would have produced a wrong BLOCK. Recommend it be added to the standing-traps list for
  any gate that re-runs mutations.
- **Two survey-directory collisions were prevented; a third artifact family was not.** Driving the
  survey at `g4-review/review.json` also caused the engine to create
  `.agent-work/issue-467-trip-semantics/issue-467-trip-semantics-g4-review/{context,mechanical}/`
  from the `work_id`, a sibling of the directory I was told to use. Harmless here, but it is a second
  path derived from a different field, and it is the same collision hazard as `tc6` from one level up.
- **The tension the handoff resolved for me was real and the resolution was correct.** `scripts/`,
  `tests/` and `docs/` are clean; all 19 reverts were asserted clean before the next mutation.
