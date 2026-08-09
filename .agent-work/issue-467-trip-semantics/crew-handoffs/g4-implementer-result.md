# IMPLEMENTER_RESULT — g4-implement, issue #467 (epic #418)

## Assigned gate

`g4-implement` — make an over-threshold **BEGIN** mechanically observable.

Parent commit `9997c32d`. **Implementation commit `20240f44`** on branch
`epic-418/a2-467-trip-semantics`, worktree `C:/Programs/constellation-skills-wt/epic418-a2-467`.
Every number below was measured in this worktree; each is pinned to the commit it was measured
at.

## Return status

`complete`

## Completed slice

All five things shipped.

**(a) An engine-only, append-only trip ledger.** Optional top-level `trip_ledger`, created
lazily by `setdefault` (the `why_trail` idiom). One entry every time the HARD band is evaluated
at the one **mutating** chokepoint — `_trip_hard_gate` — and found tripped. Both outcomes are
recorded there: `begin-refused` (no keyed refresh-request, so the verb raises) and
`begin-released` (a keyed request was pending, so the verb proceeded **while still over the
line**). Entries are never mutated or removed.

**(b) A pure selector whose emptiness is the predicate.** `begin_over_line_records(cl)` returns
every ledger entry whose `why_ref` is the id of the **live** why-record. It reads
`trip_ledger` and `_latest_why_record` and nothing else — no subprocess, no gauge read, no
clock.

**(c) Surfaced by extending the EXISTING `_trip_advisory` HARD branch**, in **both** of its
sub-branches, as one added line. Exactly one computation of the fact in the engine.

**(d)/(e) `docs/CHECKLIST_SCHEMA.md`** documents the ledger's shape, the selector, and the
scoped limit.

**Plus the required artifact:** `.agent-work/issue-467-trip-semantics/CHECK_THAT_CANNOT_FAIL.md`.

## Scope

**Files changed (all inside allowed scope):**

- `scripts/checklist_engine.py` — `_append_trip_entry` (new), `begin_over_line_records` (new),
  `_trip_hard_gate` (two writes + a `verb` parameter), `_trip_advisory`'s HARD branch (one
  computation, appended to both returns), `dispatch` (passes `verb=v`).
- `tests/test_checklist_engine.py` — 25 new tests in four classes; four pre-existing guards
  reconciled.
- `docs/CHECKLIST_SCHEMA.md` — storage-model line, a new *Trip ledger* section, the limit, two
  verb-table rows, and one line the change **falsified** (see Assumptions).
- `.agent-work/issue-467-trip-semantics/g4-mutation-log.md` — new.
- `.agent-work/issue-467-trip-semantics/CHECK_THAT_CANNOT_FAIL.md` — new.
- `.agent-work/issue-467-trip-semantics/crew-plans/g4-implementer-plan.json` (+ `.journal`) —
  my engine plan, committed by precedent from g1–g3.

**Specific exclusions touched:** none.
`TRIP_HARD_GUARDED_VERBS`, the no-silent-close rule, the advisory's shipped wording, the
per-gate headroom override, `docs/agents/GLOSSARY.md` and `scripts/gauge_reader.py::_PROFILES`
are all untouched. The shipped HARD strings are pinned **by equality** in the new tests, so a
silent edit to them would fail.
No new verb, no new flag; no CLI verb can write an entry. The close side (`advance` /
`require_why`) and the read-only advisory are **not** ledger write sites.

## Behavior changed

Yes, in three ways, all additive:

1. At/over the hard line, `start`/`reopen` now append one `trip_ledger` entry. A **refused**
   begin therefore makes exactly one state change where it previously made none. The gate's own
   status, evidence, manifest and lease liveness are still untouched — asserted, not assumed.
2. The HARD advisory carries one extra line when the live understanding already has a recorded
   begin over the line.
3. Nothing changes below the hard line, on a survey, or on a missing/stale reading.

---

## THE TWO-WORLD TABLE

Every defect shape claimed, its healthy counterpart, and the field that differs. Each row is a
two-world pair: the defective spine, the healthy spine, and the one field that tells them apart.
**No shape is asserted from the defective side alone.**

| # | defect shape | defective world | healthy counterpart | **field that differs** | assertion |
|---|---|---|---|---|---|
| 1 | a begin over the line was **refused** | over hard, agent closes `g1` with a `--why`, then runs `start g2` → raises | **identical** spine, **identical** gauge; agent closes `g1` and stops | `trip_ledger`: `None` vs one entry, `outcome == "begin-refused"` | `test_ledger_begin_refused_is_recorded_and_the_healthy_world_records_nothing` |
| 2 | a begin over the line was **released** — work actually proceeded | keyed refresh-request pending, gauge **over** hard, `start g2` succeeds | **identical** spine, **identical** command, **identical** success (`g2 -> in-progress`); gauge just **below** hard | `trip_ledger`: `None` vs one entry, `outcome == "begin-released"` | `test_ledger_begin_released_is_recorded_when_the_same_verb_runs_over_the_line` |
| 3 | the refused entry **survives the raise**, end to end through the CLI | real `gauge.json` sibling, fresh, over hard; `main(... start g2)` → rc 1 | same file, same command; gauge `observed_at` 2h old, so the reader discards it → rc 0 | `trip_ledger` **on the file reloaded from disk**: absent vs one `begin-refused` entry | `test_ledger_begin_refused_survives_the_raise_through_the_cli` |
| 4 | the recorded line is the **per-gate** hard line, not a constant | `g2` declares `context_headroom_tokens: 30_000` | the same trip with no reserve declared | `entry["hard"]`: tightened value vs the default (`assertNotAlmostEqual` both ways) | `test_ledger_records_the_per_gate_hard_line_not_a_global_constant` |
| 5 | a mark under the **live** understanding vs a **superseded** one | ledger entry `why_ref == "w-1"`, live why-record is `w-1` | **byte-identical ledger** (`assertEqual` on the whole list); a fresh agent recorded `w-2` | `begin_over_line_records(cl)`: length 1 vs 0 | `test_compliance_signal_reads_the_live_understanding_not_a_superseded_one` |
| 5b | the same, via the other supersede path | same entry, live record present | same entry after `reopen` appends a reopen-marker | `begin_over_line_records(cl)`: 1 vs 0, ledger unchanged | `test_compliance_signal_goes_quiet_when_a_reopen_freshens_the_digest` |
| 6 | the **rendered** signal, no pending request | advisory = shipped HARD string **+** the TRIP LEDGER line | advisory == the shipped HARD string, **asserted by equality** | the advisory string | `test_compliance_line_appears_on_the_hard_advisory_only_in_the_defective_world` |
| 6b | the rendered signal, **pending request** (the released case) | advisory = shipped already-requested string **+** the line | advisory == the shipped already-requested string, by equality | the advisory string | `test_compliance_line_also_rides_the_already_requested_hard_advisory` |
| 6c | it reaches the agent through `current` | `current` output contains `TRIP LEDGER` and ends with the line | `current` output does **not** contain `TRIP LEDGER` | presence of `TRIP LEDGER` in `dispatch(current)` | `test_compliance_line_reaches_the_agent_through_current_at_the_cli_boundary` |
| 6d | the mark stops being rendered once superseded | (positive control: 1 entry present) | same retained entry, understanding moved on → advisory == the shipped string for the new gate | the advisory string | `test_compliance_line_is_absent_once_the_recorded_begin_is_superseded` |
| 6e | the signal is a HARD escalation only | (positive control: the entry exists) | below hard: no `TRIP LEDGER` at two fills | presence of `TRIP LEDGER` | `test_compliance_line_never_appears_below_the_hard_band` |
| 7 | **silence is not compliance** | same spine with a live mark, read **with** a gauge over hard → claim rendered | the **same** spine read with **no** reading → advisory `""`, no entry | presence of `TRIP LEDGER` in the advisory, and `"trip_ledger" not in cl` | `test_ledger_a_none_reading_writes_no_entry_and_makes_no_compliance_claim` |
| 8 | only the **begin** verbs write | one begin verb over the line → 1 entry | six non-begin verbs over the **same** real gauge → no key at all, checked after each | presence of `trip_ledger` after each verb | `test_ledger_only_the_begin_verbs_write_an_entry_over_the_line` |
| 9 | surveys never record | gated checklist, same reading → 1 entry (positive control in the same test) | survey, same reading → `start v1` succeeds, no key | presence of `trip_ledger` | `test_ledger_a_survey_never_writes_an_entry` |
| 10 | only the two begin **outcomes** count | the same entry with `begin-refused`, then `begin-released` → length 1 | the same entry with `advance-noted` / `""` / `None` → length 0 | `begin_over_line_records(cl)` length | `test_compliance_signal_counts_both_begin_outcomes_and_nothing_else` |
| 11 | a legacy spine is unchanged | (positive control: a trip creates the key) | drive `advance`/`start`/`advance` below hard → the key is **never created** | presence of `trip_ledger` | `test_ledger_a_spine_with_no_ledger_key_drives_unchanged` |
| 12 | an existing ledger is extended, not replaced | a pre-seeded `tl-1` plus a new trip → 2 entries, `tl-1` byte-identical | — (the prior entry **is** the control) | `len(trip_ledger)` and `trip_ledger[0]` | `test_ledger_an_existing_ledger_is_extended_never_replaced` |

**Nothing in this gate is asserted only on the defective side.** The two closest to it —
shapes 6d/6e, which assert an *absence* — each carry a positive control in the same test
asserting the entry exists first, and both are killed by mutations N9 and N17 respectively.

---

## EVERY LEDGER WRITE SITE, AND THE PROOF EACH IS UNREACHABLE FROM `_run_verb`

**There is exactly one writer function and two call sites, both inside `_trip_hard_gate`.**

```
scripts/checklist_engine.py:1669    _append_trip_entry(cl, iid, verb, "begin-released", ...)   # release branch
scripts/checklist_engine.py:1671    _append_trip_entry(cl, iid, verb, "begin-refused",  ...)   # before the raise
```

Proof, read off the engine's own call graph rather than a hand-maintained list of verbs
(`test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb`, an `ast` scan of
`scripts/checklist_engine.py`; the scan asserts it looked at **more than 50** function
definitions, so it cannot pass over an empty set):

1. Exactly **two** functions in the engine name the `trip_ledger` key at all —
   `_append_trip_entry` (the only write, a `setdefault` + `append`) and
   `begin_over_line_records` (the only read, a `cl.get`). Asserted by equality on the sorted
   list, so a third would fail.
2. `callers_of("_append_trip_entry") == ["_trip_hard_gate"]`.
3. `callers_of("_trip_hard_gate") == ["dispatch"]`.
4. `_run_verb` — the function every CLI verb is dispatched through — calls **neither**.

`dispatch` runs `_trip_hard_gate` at the `TRIP_HARD_GUARDED_VERBS` chokepoint **before**
`_run_verb`. So no verb body can reach the writer, and no code path anywhere mutates or removes
an existing entry.

**Mutation N18 is the falsification test for this claim**: adding a `_trip_hard_gate` call
inside `_run_verb`'s `start` branch turns the guard red (6 failed).

Behavioural twin, over a **real** gauge parked above the line: `current`, `attach`,
`flag-candidate`, `advance --why`, `block`, `resume` — **6 verbs, count asserted in the test** —
leave no key; the seventh, `start`, writes one entry.

---

## ANYTHING I COULD NOT MAKE DISCRIMINATE

Declared, not buried. None of these is a claim I am making and failing to support — each is a
place I am explicitly **not** claiming coverage.

1. **The scoped limit, exactly as handed to me.** The engine **cannot** observe an agent that is
   told to wrap up and simply **stops without running another verb**. `main()` does not save on
   `current`, which is where the band is evaluated read-only, and there is no mid-gate check.
   That case is visible to the invoker only as a stale `DIGEST` at the seam. Written into
   `docs/CHECKLIST_SCHEMA.md` in those words.

2. **The ledger records BEGINS, not WORK.** An agent that keeps working inside the gate it is
   already in, over the line, without running any verb, leaves no mark. Conversely an agent that
   runs `start` over the line and then immediately stops **does** get a mark. Both are stated in
   the schema doc; the signal is "a begin was judged over the line", never "work happened".

3. **`begin-released` records the guard's decision, not the verb's outcome.** The band is
   evaluated before the verb runs, so if the verb subsequently raises for an unrelated reason
   (unmet preconditions, say) the entry still reads `begin-released`. Keeping one write site was
   worth more than this precision; the corner is documented rather than engineered away.

4. **One test in the suite is negative-only and cannot discriminate** —
   `test_compliance_signal_is_empty_on_a_spine_that_never_carried_a_ledger`. It survives N11
   (the selector dead-coded), because "empty" is genuinely its expected value. It is a
   backward-compatibility guard, it is paired with positive controls in the same class, and I
   am not counting it as evidence for the mechanism. Named in the mutation log too.

5. **The None-reading fail-safe is only half closed by a specific mutation.** g2's M11 reported
   that no specific mutation exists for it — deleting or inverting the `reading is None` check
   breaks 47–59 unrelated tests, because no-reading is the path the whole suite takes. I found a
   targeted mutation for the **claim** side (N8: make the advisory report the ledger on silence
   → exactly 1 failure) but **not** for the **guard** side. The guard half remains
   over-determined by the suite and specificity is not claimed for it.

6. **`fill` and `hard` are rounded to 4 decimal places** on write. Under this repo's currently
   empty threshold table the recorded `hard` and a freshly resolved one agree to well within
   that, but the ledger's numbers are a record, not an oracle: a reader should not do arithmetic
   with them expecting bit-equality with `thresholds_for`.

---

## Test mode

**Required:** `test-first (TDD), with mutation testing on every guard shipped`
**Satisfied:** `yes — with one declared deviation on the RED for m2.`

- **m1 (writer) — clean RED:** 7 tests written, run, **7 failed / 384 deselected**, every
  failure a `KeyError`/`None` on the absent key. Then green.
- **m2 (selector) — RED by dead-coding, declared.** I authored `begin_over_line_records` in the
  **same edit** as the m1 writer, so its absence could not produce the red. Rather than attest a
  red I had not seen, I dead-coded the selector to `return []`, ran (**6 failed, 2 passed**),
  removed the stub (`grep 'TEMP RED'` exits 1) and re-ran (**6 passed**). This is the m2 red I
  attested, in those words, in the plan's evidence. It is also mutation **N11**, run again
  formally after the commit.
- **m3 (render) — clean RED:** **4 failed, 2 passed, 397 deselected**; the 2 that passed are the
  two absence guards, which are negative by design and carry positive controls.
- **m4 (guards)** — written after the mechanism, and covered by mutations N8/N18/N3 rather than
  by a red observation. Stated plainly rather than described as TDD.

## Evidence

### The three verification commands

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py
```
**Result:** `409 passed, 120 subtests passed` (at `20240f44`).

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'
```
**Result:** `25 passed, 384 deselected, 13 subtests passed`. **It collects.** At `9997c32d` this
exact command was `exit 5, "384 deselected in 0.17s"` — the frozen `g4-integrate` closeout
selector no longer exits 5. (No test name uses the `trip_log` token; `ledger` and `compliance`
carry all 25.)

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
**Result:** `1858 passed, 2 skipped, 821 subtests passed` at `20240f44` with a renormalized
checkout. See the delta below — including a measurement trap this gate walked into and out of.

### The full-suite delta, explained against `9997c32d`

Baseline handed to me, measured by the Commander at `9997c32d`: **1833 passed, 2 skipped, 808
subtests**.

- **`+25 passed`** — exactly my 25 new tests. Confirmed mechanically, not by counting by eye:
  `pytest -k '<my four class names>'` → `25 passed`.
- **`+13 subtests`** — exactly my 13. Getting to that number took two corrections, both
  reported because the intermediate readings are the kind of thing a reviewer will re-measure:

  - **Before the commit I measured `+12`, one short.** The missing subtest is not mine.
    `tests/test_context_manifest.py::test_rev_equals_git_rev_parse_head_for_tracked_clean_files`
    filters its targets to files whose working tree matches HEAD, and
    `scripts/checklist_engine.py` is one of those targets — so while my change was uncommitted
    that target was skipped and the file reported **61** subtests instead of 62. Measured, not
    inferred: with my three source files stashed the file reports **62**, with them applied
    **61**; and `tests/test_checklist_engine.py` reports **384 passed / 107 subtests** at the
    parent-commit content versus **409 / 120** with mine. The stash was popped and
    `git diff --stat` verified identical before and after.
  - **After the commit it was STILL `+12`, and that one is worth a triage candidate.** I had
    rewritten the engine file with LF line endings; this checkout holds CRLF under
    `.gitattributes`' `* text=auto`. The content was **byte-identical to HEAD after
    normalization** — `git diff --quiet` exited **0** — but `git status --porcelain` still
    reported ` M`, and that test's cleanliness filter uses `status`. So a committed, unmodified
    file read as dirty and the target stayed skipped. `git checkout -- <the three files>`
    restores the CRLF checkout (blob unchanged, verified byte-identical after normalization) and
    the file reports **62** again.

  **Final: `1858 passed, 2 skipped, 821 subtests` = the baseline's `1833 / 2 / 808` plus exactly
  my 25 tests and 13 subtests.**

### Mutation testing

**19 mutations, all 19 killed by their named test.** Full log with per-mutation branch, named
test, TOTAL failure count and blast-radius commentary:
`.agent-work/issue-467-trip-semantics/g4-mutation-log.md`.

Route, exactly as the handoff mandated: implementation **committed first** (`20240f44`); each
mutation applied **directly** to `scripts/checklist_engine.py` (anchor asserted unique, and the
file asserted actually changed); the named test run; then reverted and
`git diff --quiet -- scripts/checklist_engine.py` **asserted clean before the next mutation** —
`reverted_clean=True` on all nineteen, and the battery aborts on the first dirty revert. Final
state clean. No `git archive`, no temp tree.

Totals: N1 23 · N2 5 · N3 3 · N4 2 · N5 2 · N6 1 · N7 12 · N8 1 · N9 3 · N10 3 · N11 11 ·
N12 2 · N13 2 · N14 3 · N15 1 · N16 1 · N17 23 · N18 6 · N19 11.
Three wide radii (N1, N7, N17) are declared in the log with their cause; **no equivalent mutants
were declared** — after g3's M15 was found to be a false `EQUIVALENT`, a claim of equivalence
needs evidence, and none of these needed one.

### The wiring grep

```bash
grep -rn "_append_trip_entry\|begin_over_line_records\|trip_ledger" --include=*.py . \
  | grep -v "def _append_trip_entry\|def begin_over_line_records" | grep -v self_test
```

**External call sites: `_append_trip_entry` = 2, `begin_over_line_records` = 1. Non-zero, so no
stop condition.** Both writer call sites are in `_trip_hard_gate`; the single selector call site
is in `_trip_advisory`'s HARD branch. The remaining hits are the definitions' own docstrings and
the two key accesses (`setdefault`, `cl.get`).

### One render, not two

```bash
grep -rn "begin_over_line_records" --include=*.py scripts/   # 3 lines: 1 def, 1 call, 1 docstring
grep -rn "TRIP LEDGER" --include=*.py scripts/ | wc -l       # 1
grep -rn "trip_ledger" --include=*.py scripts/               # 2 code lines: setdefault, cl.get
```

### The failure distribution, derived from a command

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py 2>&1 \
  | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
```
Ran mid-gate, after the ledger landed and before reconciliation: **`4 FAILED
tests/test_checklist_engine.py`** — all four the pre-existing "a refusal mutates nothing"
guards, which I then reconciled. Empty after reconciliation.

## Docs/contracts touched

- `docs/CHECKLIST_SCHEMA.md` — storage model, a new **Trip ledger** section (shape, field table,
  both outcomes, the `begin-released` honesty note, the two deliberate non-write-sites, the
  selector, the fail-safe, backward compatibility, engine-written-only, the limit), and two verb
  table rows.
- **One line the change falsified.** The Trip section said a HARD refusal "never mutates state".
  That is no longer true — it now appends exactly one ledger entry — so I corrected it in place
  rather than leaving a doc that contradicts the engine.

## Map Impact

- **Structural anchors touched:** `scripts/checklist_engine.py`, the Trip section — two new
  module-level functions (`_append_trip_entry`, `begin_over_line_records`), one changed
  signature (`_trip_hard_gate` gains `verb`), one changed call at the `dispatch` chokepoint.
- **Capabilities added:** an engine-written, append-only record of BEGINs judged at/over the
  hard line, and a pure predicate over it keyed to the live understanding.
- **Constraints touched:** *a HARD refusal mutates no state* is now **narrowed** — it mutates no
  gate state, and appends exactly one ledger entry. Doc and tests both updated.
  *fail-safe-on-no-reading* is **relied on again** and now covers the claim side as well as the
  guard side. *constraint:no-threshold-values* is honored: the engine records the fraction
  `gauge_reader.thresholds_for` returned; it computes no threshold.
- **Decision candidates:** the ninth entry field `why_ref` (below) — needs a Commander/Admiral
  ruling because it reverses a critic-panel disposition.
- **Claims produced:** the ledger's write site is unreachable from `_run_verb`, asserted off the
  engine's own call graph and falsified by mutation N18.
- **Triage candidates:** two, below.

## Assumptions

1. **I added a ninth entry field, `why_ref`, beyond the eight the handoff named — and this
   reverses critic-panel finding 14.** That finding dropped `why_ref` on the reasoning that it
   is "recoverable from `why_trail`". It is not recoverable in the sense the predicate needs:
   close criterion (b) requires the signal be keyed to the **live understanding**, which means
   knowing which why-record was live **at the moment of the trip**. Without the field, that can
   only be re-derived by comparing timestamps against `why_trail` — fragile at second
   granularity and a re-derivation rather than a record. The handoff lists "the entry field
   encoding" as mine to author, so I authored it; but the two instructions are in tension and
   the Commander should confirm or reverse. **Mutation N7 is the evidence for its
   load-bearingness: removing it turns 12 tests red, including every selector and render test.**
2. **I drove my own implementer plan with the INSTALLED implementer engine**
   (`C:/Users/fredc/.claude/skills/constellation-implementer/scripts/checklist_engine.py`),
   deliberately **not** the worktree engine — I mutate the worktree engine nineteen times in
   this gate and must not drive my own provenance through a mutated binary. The installed bundle
   is pre-#467, which is irrelevant to driving a plan that uses no #467 feature.
3. **I used the `amend` verb with `--authority "implementer, self-caught; Commander notified in
   the same turn"`** where the schema describes authority as human ratification. There was no
   reachable human and the amendment only tightened six of my own checks. Notified in the same
   turn. Flagging it rather than letting it pass as routine.
4. **My plan file is committed**, by precedent from the g1/g2/g3 implementer plans, though the
   handoff's Deliverable Path Check did not list it.

## Stop conditions hit

**None.** Allowed scope was sufficient, no specific exclusion needed touching, every piece of
required evidence was producible, and no defect shape I claim to catch produced identical output
in both worlds. Every limit above is a declared non-claim, not a failed claim.

## Out-of-scope observations (triage candidates)

1. **A lint for the `| tail` class of unfailable command check.** I shipped six of them in my
   own plan for this gate (see `CHECK_THAT_CANNOT_FAIL.md`, specimen 4): piping `pytest` into
   `tail` makes the shell's exit status `tail`'s, so the check passes on a failing run **and**
   on an empty collection — silently defeating the anti-vacuity device the Commander froze into
   the closeout selector. A cheap mechanical guard exists: refuse, or warn on, a `command` check
   whose text pipes a test runner into anything. This is a **tooling** candidate on the engine or
   on plan authoring, not a doctrine essay.
2. **`git status` and `git diff` disagree about a renormalized file, and one test silently
   loses coverage because of it.** A tracked file rewritten with LF in this CRLF checkout is
   `git diff --quiet`-clean but ` M` to `git status --porcelain`. `test_context_manifest`'s
   clean-file filter uses `status`, so it drops that target and its own subtest count shrinks by
   one **without any assertion failing** — a guard quietly narrowing rather than going red. It
   is the CREW_CONTEXT.md working-tree-bytes hazard showing up inside a test's own selection
   step. Candidate: have that filter compare blob OIDs (`git hash-object` vs `rev-parse HEAD:`)
   rather than `status`, and assert the number of targets it kept.
3. **`docs/CHECKLIST_SCHEMA.md` has no mechanical link to the engine.** I found and fixed a line
   my own change falsified ("a HARD refusal … never mutates state") only because I happened to
   read the paragraph above where I was inserting. The next engine change may not be so lucky.
4. **The handoff-quality question did NOT surface as decision pressure**, so there is nothing to
   return on it. It never came up: the discriminating observable is a begin, and a begin is
   observable without reading any handoff's content. Reported as a non-event rather than
   silently omitted.

## Workflow Feedback

- **Handoff gaps.** The **entry-field list in (a) and close criterion (b) are in tension.** (a)
  names eight fields; (b) requires the predicate be keyed to the live understanding, which needs
  a ninth. The handoff did not say which wins, and it inherits critic finding 14, which had
  explicitly dropped that ninth field. I resolved it under "the entry field encoding is yours to
  author" and flagged it — but a future handoff that specifies both a field list and a keying
  requirement should say which is authoritative.
- **Context rediscovered.** That four existing tests assert `assertEqual(cl, before)` after a
  refused begin — the ledger is precisely a new mutation on that path, so the reconciliation was
  guaranteed the moment (a) was specified. The handoff's "minimal reconciliation of existing
  tests" allowed it, but naming the four (lines 3341, 3439, 3542, 3552 at `9997c32d`) would have
  saved a diagnostic pass. I found them by prediction and confirmed by running.
- **Instructions improvised around.** The frozen selector names three tokens (`ledger`,
  `compliance`, `trip_log`) and no test needed the third. Harmless, but a frozen selector with a
  dead token invites a future author to think a naming convention exists that does not.
- **What would have made this easier.** One line in the handoff: *"a refused begin currently
  asserts a byte-identical spine in four tests; reconciling them is expected and in scope"*. And
  a note that the mutation route requires committing first — which the handoff **did** say, and
  which was correct: `git checkout -- scripts/checklist_engine.py` is only a safe revert once
  the implementation is a commit.
