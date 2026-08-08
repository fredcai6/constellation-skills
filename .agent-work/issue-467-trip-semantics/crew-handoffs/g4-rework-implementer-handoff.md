# Implementer Handoff — g4 REWORK (attempt 2)

Issue #467 (epic #418), branch `epic-418/a2-467-trip-semantics`, worktree
`C:/Programs/constellation-skills-wt/epic418-a2-467`. Work only in this worktree, absolute paths.

Engine under change: `scripts/checklist_engine.py` **in this worktree** — pin it by hash, not by
size: `git rev-parse HEAD:scripts/checklist_engine.py` -> `c0faef06c41c1ccaa05c62fc6204f3977a614742`
at HEAD `28dd434c`. (A previous handoff quoted a byte size that matched nothing on disk. Use the
hash.) Do **not** run against an installed skill bundle.

## Why you are here

Gate `g4` shipped the trip ledger and its compliance signal. It was then independently reviewed by
attack — 17 defect shapes constructed from scratch, all 19 mutations re-run — and **eight of the
nine close criteria PASSED**. The review returned **BLOCK with exactly one blocking finding**.

This is a **narrow rework of that one finding**. **Do not re-do g4.** The full review is at
`.agent-work/issue-467-trip-semantics/crew-handoffs/g4-reviewer-result.md` (finding **B1**).

## The finding, and it is confirmed twice over

The reviewer found it; the previous Commander then **reproduced it in its own shell with the
reviewer's own probe** rather than accepting it on the report. It is real.

**In one sentence:** the close that the HARD band *orders* an agent to make is guaranteed to clear
the compliance signal, and the shipped line says the opposite.

Three shipped mechanisms compose:

1. At/over hard, `advance --mechanical` is **refused** (g2's no-silent-close rule), so the **only**
   legal close is `advance --why "..."`.
2. `advance --why` **appends a new `why_trail` record**.
3. `begin_over_line_records` (`scripts/checklist_engine.py:1588`) matches an entry only when
   `entry["why_ref"] == _latest_why_record(cl)["id"]`. A new why-record therefore supersedes
   **every** existing entry at once.

Measured on a gauge parked at 0.20 with `hard = 0.15`:

| step | ledger on disk | selector | rendered line |
|---|---|---|---|
| refused BEGIN at g2 | `tl-1` | 1 | present |
| released BEGIN at g2 (work proceeds over the line) | `tl-1`, `tl-2` | 2 | present |
| **the same agent closes g2 with `advance --why`** | `tl-1`, `tl-2` | **0** | **absent** |
| a further refused BEGIN at g3 | `tl-1`, `tl-2`, `tl-3` | 1 | present (count resets to 1) |

Across a 3-gate runaway, **3** over-the-line begins were on disk, the rendered line never claimed
more than **2**, and **at the seam it was ABSENT** — byte-identical to a compliant agent that closed
its gate and stopped. **Green in both worlds, at exactly the place the next reader looks.** That is
the failure this whole issue exists to prevent.

Two shipped statements are falsified by it:

- **The engine's own line** (`scripts/checklist_engine.py:1504-1508`) ends
  `"Closing this gate does not clear the record."` The reviewer closed that exact gate and the line
  disappeared.
- **The doc.** `docs/CHECKLIST_SCHEMA.md` (the "compliance signal" section, ~line 420) says the
  understanding moves on when *"a fresh agent records its own `why`, or a `reopen` appends a
  reopen-marker"*. The mechanism cannot tell a fresh agent from the offender, and the offender's own
  close is the **likeliest** superseder in exactly the runaway the ledger was built for.

And the implementation's own test **certifies the bug as intended behaviour**:
`test_compliance_line_is_absent_once_the_recorded_begin_is_superseded`
(`tests/test_checklist_engine.py:5876`) runs `start g2` -> `advance g2 --why "u2 — a fresh agent's
understanding"` and asserts the line is gone. That is **byte-for-byte the offender's path**; only
the docstring/comment calls it "a fresh agent". **It is a passing test that pins the defect.**

## Task — three changes plus the test that certifies the bug

The Admiral has ruled the fix space, and it is narrow. **Every entry is already on disk, so no new
state is needed.** Do all four:

### 1. Add a HISTORICAL read alongside the live one

Add a second **pure** selector — every `begin-refused`/`begin-released` entry in `trip_ledger`
regardless of `why_ref` — and render it as its own line in the same one place the live line is
rendered. It must render **even when the live list is empty**, because the seam (live 0, historical
3) is the entire point.

Shape of the render at `scripts/checklist_engine.py:1500-1508` (the `ledger_note` block), for
illustration only — the wording is yours to get right:

- when the live list is non-empty: the live line, scoped honestly to the live understanding.
- when **any** begin is on the record: the historical line, naming the total and the latest, and
  saying plainly that no close clears it.

Constraints:

- **Compute each fact exactly once, and render in exactly one place.** Close criterion 6 (extended,
  not duplicated) PASSED on review and must stay passed: `grep 'TRIP LEDGER' scripts/` must still
  find the render site once, and the note must still be computed once above the two HARD returns and
  appended to each.
- **Purity.** No subprocess, no gauge read, no clock, no I/O — it is called from the read-only
  `current` path. It must not raise on a malformed ledger (`None`, a string, a dict, a list holding
  non-dicts): criterion 8 PASSED and must stay passed.
- **Append only to the string.** The pre-existing HARD strings are pinned by **equality** in the
  existing tests and the healthy advisory must remain a strict prefix of the defective one.

### 2. Correct the false sentence

`"Closing this gate does not clear the record."` must be replaced by something that is **true of the
line it sits on**. The live line is cleared by the mandated close; say so, and point at the
historical line that is not. Ambiguity is not acceptable here: a compliance string that is
defensible only under a charitable reading is not a compliance string.

### 3. Declare this limit as plainly as the other three

`docs/CHECKLIST_SCHEMA.md`, the "The limit — what this cannot observe" section (~line 445), already
declares three limits plainly and honestly: the agent that stops without running a verb; "records
begins, not work"; "an empty ledger never means compliant". **Add the fourth in the same voice**:
the live signal is scoped to the live understanding, and the close the HARD band mandates creates a
new understanding, so the live line goes silent at exactly the seam where a fresh reader arrives —
which is why the historical line exists and what it is for.

Also fix the doc half of the finding (review NB1): the supersede narrative in the "compliance
signal" section names only *"a fresh agent"* and *"a reopen"*. The mechanism **cannot distinguish a
fresh agent from the offender**. Say that.

### 4. Fix the test that pins the defect

`test_compliance_line_is_absent_once_the_recorded_begin_is_superseded` must stop certifying the
offender's close as correct behaviour. After your change the honest assertion is: **the live line
goes absent AND the historical line still names the retained begins.** Correct its name, its
docstring and the misleading "a fresh agent's understanding" label so the test says what it actually
exercises — the **offender's own close**.

**Do not delete it.** A test that pinned a defect and was then corrected is a better audit record
than a test that vanished.

## The measurement this rework has to produce

This is the acceptance measurement. Do it **through the real CLI in a subprocess**, on a real
`gauge.json` stamped from the clock — not by calling `_trip_advisory` directly, and with **no mock
in the advisory path** (pass a real `base_dir` holding a real gauge rather than patching
`_read_gauge`).

Build **two worlds** and run `current` at the seam in each:

- **World H (compliant):** the agent is told to wrap up, closes its gate with `advance --why`, stops.
  No begin verb ever runs over the line.
- **World D (runaway):** at least one over-the-line BEGIN happens (ideally the reviewer's 3-gate
  shape: refused begin, released begin, then the same agent closes with `advance --why`).

**The rendered `current` output at the seam MUST DIFFER between H and D, and D's must name the true
total.** Paste both outputs verbatim. Under the shipped code they are byte-identical, which is the
defect; if they are still identical after your change, you have not fixed it.

Then **re-run the reviewer's own probe**, `.agent-work/issue-467-trip-semantics/g4-review/probe_clearing.py`,
and paste its output. Its third row ("the same agent closes g2") is the row that must change. If the
probe needs a mechanical edit to keep running against your new strings, say so and show the edit —
do not quietly rewrite it into agreement.

## Test mode — TDD, and the anti-vacuity rule this gate is about

Write each new test **before** the change and observe it **RED**, then GREEN. Paste both. A test
that has only ever been seen green proves nothing here; that is the exact failure class this whole
gate is about.

Every new test must be a **two-worlds** test that **names the differing field**. An absence-only
assertion (`assertNotIn`) needs a positive control **in the same test** that asserts the signal
**renders** — not merely that the ledger entry exists. The review found (NB4) that two existing
tests carry a control that proves only the entry exists, which does not defend against a dead
selector. Do not repeat that.

**Mutations.** Add mutations for every new branch to
`.agent-work/issue-467-trip-semantics/g4-mutation-log.md`, continuing the existing numbering
(N20, N21, ...), each with its named killing test and its total failure count. Sanctioned route:
edit `scripts/checklist_engine.py` in place, run the test file, revert with `git checkout --`, and
assert `git diff --quiet` is clean **before** the next one. At minimum mutate: the new selector
dead-coded to `return []`; the historical line dropped from one of the two HARD sub-branches; and
the historical selector keyed to the live why-record (i.e. made identical to the live one) — that
last mutant must be **killed at the seam**, because it re-creates B1 exactly.

**A mutation that makes the module raise is a crash, not a kill** (review tc3). If your mutant
produces a `NameError`/`ImportError`, its blast radius is noise — re-cast it as a behavioural
change. And pytest reports subtest failures as `SUBFAILED(param) path::Class::test`: a `FAILED`-only
grep reports **false survivors**, which under this gate's rules would produce a wrong verdict. Match
both.

### Two artifact corrections to fold in

- **`.agent-work/issue-467-trip-semantics/g4-mutation-log.md`, entry N17.** The logged mutant
  appends `ledger_note` to the SOFT return, but `ledger_note` is scoped inside the HARD branch, so
  it is a `NameError` — a crash — and its recorded radius of 23 is crash noise. The behavioural form
  (compute the note in the soft branch) still kills
  `test_compliance_line_never_appears_below_the_hard_band`, with a total of **1**. Correct the entry
  **visibly**, in the g3 precedent: state the kill, name the test, give the true total, and note the
  correction rather than silently rewriting the row.
- **`.agent-work/issue-467-trip-semantics/CHECK_THAT_CANNOT_FAIL.md` line 172** claims *"Every one of
  this gate's 25 tests is written this way"* (two worlds, name the differing field). The
  implementer's own result declares one negative-only test, so the claim is false. This is a
  deliverable of this gate, not an audit record, and it is the same defect class as B1 — an
  overclaim in a shipped artifact. Correct it to what is true.

Do **not** retro-edit the g4 implementer's or reviewer's returned result files, or any earlier
handoff. Those are audit records of what was said. (The review's NB3 — "11 numbered shapes" should
have been 12 — is already correctly recorded in the review and needs no edit.)

## Allowed scope

- `scripts/checklist_engine.py` — the new selector and the render, and nothing else.
- `docs/CHECKLIST_SCHEMA.md` — the trip-ledger/compliance-signal/limit sections.
- `tests/test_checklist_engine.py` — the corrected pinning test and the new tests.
- `.agent-work/issue-467-trip-semantics/g4-mutation-log.md` — new mutations + the N17 correction.
- `.agent-work/issue-467-trip-semantics/CHECK_THAT_CANNOT_FAIL.md` — the line-172 overclaim.
- Your own crew plan under `.agent-work/issue-467-trip-semantics/crew-plans/`.
- A probe/driver of your own anywhere under `.agent-work/issue-467-trip-semantics/`.

## Specific exclusions — read these, the temptation is real

- **DO NOT CHANGE THE KEYING of `begin_over_line_records`.** This is an Admiral pre-ruling. The
  reviewer explicitly declined to ask for it; close criterion (b) is correctly implemented.
  **Widening the live selector to match all why-records is REFUSED IN ADVANCE** — it resurrects
  superseded entries, makes every later `current` re-litigate a closed handoff, and converts a check
  that cannot fail into one that cannot *pass*. That is the mirror defect this gate's own
  `CHECK_THAT_CANNOT_FAIL.md` names. The historical read is **additive and separately labelled**;
  the live line keeps its present-tense meaning.
- **Do not add new state.** Every entry you need is already on disk. No new field, no new key, no
  new verb, no new flag, no config hook.
- **Do not touch `_append_trip_entry`, `_trip_hard_gate`, or the `dispatch` chokepoint.** The
  engine-written-only guarantee (criterion 3) PASSED under an `ast` call-graph audit and must stay
  passed: `_append_trip_entry`'s only caller is `_trip_hard_gate`, whose only caller is `dispatch`.
  Your new selector is a **reader**. It must never write.
- **Do not touch what g2 and g3 shipped** — the bands, the resolver, the clamps, `_PROFILES`, the
  `require_why` plumbing, the no-silent-close rule.
- **Do not do the tc4 refactor** (the band judgment assembled by hand at three sites, and
  `_append_trip_entry`'s seven parameters). It is filed as a triage candidate and is deliberately
  out of scope.
- Do not touch `.agent-work/issue-467-trip-semantics/execute.json`, `spine.json`, `gauge.json` or
  `STATE_NOTE.md` — the Commander holds their lease. **Do not run `checklist_engine.py` against
  `execute.json`.** Build your own fixture spines in your own temp directory.
- Do not commit. The Commander commits.

## Close criteria

1. A pure historical selector exists, renders at the seam when the live list is empty, and never
   writes.
2. The live line's sentence is true of the live line, and it points at the historical line.
3. `docs/CHECKLIST_SCHEMA.md` declares the fourth limit in the same plain voice as the other three,
   and the supersede narrative no longer implies the mechanism can tell a fresh agent from the
   offender.
4. `test_compliance_line_is_absent_once_the_recorded_begin_is_superseded` no longer certifies the
   defect: it asserts the live line goes absent **and** the historical line still names the retained
   begins, and its name/docstring say it is the offender's own close.
5. **The two-worlds seam measurement**: H and D rendered `current` outputs pasted verbatim and
   **different**, produced through the real CLI on a real gauge with no mock in the advisory path.
6. The reviewer's `probe_clearing.py` re-run and pasted, with its third row changed.
7. Every new test seen RED before GREEN, with both outputs pasted; every absence assertion carries a
   render-side positive control in the same test.
8. New mutations logged with named killing tests and totals; the "historical keyed to live" mutant
   killed at the seam; `git diff --quiet` asserted clean between mutations; `scripts/`, `tests/` and
   `docs/` clean at the end (`git status --porcelain` on those paths shows only your intended edits).
9. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` passes. Report the counts and **capture the
   REAL exit code** (redirect to a file and echo `$?`; a piped exit code is the pipe's). The
   pre-rework baseline at HEAD `28dd434c` is **1858 passed, 2 skipped, 821 subtests, exit 0**.
   Explain any delta.
10. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'`
    passes **and collects** — pytest exits 5 on an empty collection, which is a green-looking exit
    that proves nothing.
11. N17 corrected visibly in the mutation log; `CHECK_THAT_CANNOT_FAIL.md` line 172 corrected.
12. `git diff --stat` pasted, and every changed path is inside the allowed scope.

## Standing traps on this run — all seven still apply

1. **Verify on what the agent DOES, never on what it is TOLD.** B1 is this trap one level up.
2. `main()` does **not** save state on `current`, so nothing you observe through `current` persists.
3. **Clock skew / stale gauge.** A reading is discarded when it is >30 min old **or dated in the
   future**. A hand-typed `observed_at` even slightly ahead of the wall clock collapses to `None`,
   the scenario reads as "no gauge", and your test goes **vacuously green**. Generate every
   timestamp from the clock.
4. Prefer a real `base_dir` with a real gauge over patching `_read_gauge` for the seam measurement —
   a mock in the advisory path is the thing the reviewer refused to accept.
5. `SUBFAILED` vs `FAILED` — see above.
6. Pin the engine by hash, not size (given at the top).
7. **CRLF.** `git checkout` of a subset of files can renormalize line endings and dirty
   `test_context_manifest`. Check `git status --porcelain` after every revert.

## Suggested model tier

**Sonnet.** Standing default for implementers on this run. No named Opus reason applies: the target
is measured, reproduced twice, and handed to you with the fix space already ruled; the scope is one
selector, one string, one doc section, one corrected test plus new ones.

## Deliverable path check

All **Committed**; `git check-ignore` exits 1 for each (`.agent-work/` is tracked in this repo).

- `scripts/checklist_engine.py` — Committed, existing.
- `docs/CHECKLIST_SCHEMA.md` — Committed, existing.
- `tests/test_checklist_engine.py` — Committed, existing.
- `.agent-work/issue-467-trip-semantics/g4-mutation-log.md` — Committed, existing.
- `.agent-work/issue-467-trip-semantics/CHECK_THAT_CANNOT_FAIL.md` — Committed, existing.

## Stop conditions

Stop and return **without** completing if:

- **The historical read cannot be made to discriminate at the seam without new state.** Say so with
  the measurement that shows it. **An honest null is a complete deliverable here**; a manufactured
  passing signal is the one unforgivable outcome on this issue.
- The only fix you can find requires changing the live selector's keying. That is refused in
  advance — return and say so; it is the Commander's to route, not yours to take.
- You find that the shipped mechanism is wrong in some **further** way beyond B1. Report it; do not
  widen the rework on your own authority.

Report "this specific check failed", never "this approach is impossible".

## Return format

Return an `IMPLEMENTER_RESULT` to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g4-rework-implementer-result.md` containing: the
diff of each change; the corrected test in full; the RED-then-GREEN output for every new test; the
**two-worlds seam measurement** verbatim; the re-run `probe_clearing.py` output; the new mutation
entries with totals; the N17 correction; the suite runs with real exit codes; `git diff --stat`;
stop conditions hit; out-of-scope observations as triage candidates; and workflow feedback.

**Deliver it via `SendMessage` to `commander-w4-467-h` before ending your turn.**
