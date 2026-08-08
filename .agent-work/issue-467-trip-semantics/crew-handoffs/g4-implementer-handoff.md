# Implementer Handoff

## Gate

`g4-implement` — issue #467, epic #418. Work area `.agent-work/issue-467-trip-semantics/`,
branch `epic-418/a2-467-trip-semantics`, worktree `C:/Programs/constellation-skills-wt/epic418-a2-467`.

**Parent commit of your diff: `9997c32d`.** Every baseline number below was measured by me at that
exact commit, in this worktree, minutes before writing this. Do not subtract against any other
commit; if a number disagrees, say which commit you measured at.

## Task

Make an over-threshold **BEGIN** mechanically observable.

**Read the scope carefully — this gate exists because the obvious reading of it is a check that
cannot fail.** "Did a handoff artifact appear before the next advance?" is **true by construction**:
`advance` already refuses a non-exempt gate that carries no `--why`. That check is green in the
healthy world and green in the defective world, so it discriminates nothing. The discriminating
question is the other one:

> **Did anyone BEGIN work while over the line?**

Ship five things.

**(a) An engine-only, append-only trip ledger on the spine.** One entry every time the HARD band is
evaluated at a **mutating** chokepoint and found **tripped**, carrying
`{id, gate, verb, outcome, fill, hard, model, ts}`. `outcome` is exactly one of:

- **`begin-refused`** — no keyed refresh-request was pending, so the verb **raised**.
- **`begin-released`** — a keyed refresh-request **was** present, so the verb **proceeded while
  still over the line**.

**(b) A pure predicate over the spine** reporting whether any `begin-released` or `begin-refused`
entry exists **for the live understanding**. That is the non-compliance signal. **In the healthy
world no ledger entry exists at all**, because the agent that was told to wrap up stopped, and its
successor's gauge reads below the line.

**(c) Surface it by extending the EXISTING `_trip_advisory` HARD branch.** Do not add a second
render computing the same fact.

**(d) Update `docs/CHECKLIST_SCHEMA.md`** — the ledger's shape, the predicate, and (e) below.

**(e) Write the scoped limit into that same doc, plainly.** See "The limit you must not overclaim".

## Where the write site is, and why there is only one

I read these in my own shell at `9997c32d`; they are facts, not guesses, but re-read them before you
build on them.

- `TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}` — `scripts/checklist_engine.py:83`.
- `_trip_hard_gate(cl, iid, base_dir)` — `:1549`. Resolves the reading at `:1565` via
  `_trip_hard_band_reading`, returns early (no-op) for a falsy `iid` or a `None` reading, returns at
  `:1575` when `has_pending_refresh_request(cl, iid, why_ref=wid)`, and otherwise raises.
- The dispatch chokepoint — `:2821`, `if v in TRIP_HARD_GUARDED_VERBS: _trip_hard_gate(...)`.
- `main()` **persists on the `EngineError` path** for any verb that is not `current` and not
  `--dry-run`. That is what makes a `begin-refused` entry durable even though the verb raised. Read
  it yourself before you rely on it.
- The append-only idiom to copy is `_append_why` (`:1105`) — `cl.setdefault("why_trail", [])`, an
  `f"w-{len(trail) + 1}"` id, append only, **never** mutate or remove a prior entry.
- `_latest_why_record` — `:1131`. This is "the live understanding" for (b).

**`_trip_hard_gate` is the only mutating chokepoint where the HARD band is evaluated for a BEGIN.**
Both of the plan's `outcome` values are begin outcomes, so the ledger is a record of begins. Two
places evaluate the same band and are **deliberately not ledger write sites**:

- **`_trip_advisory`** (`:1461`) is reached from `current`, and `main()` does **not** save on
  `current`. A write there would be silently discarded — and would be a lie in a read-only verb.
- **The close side** — the `require_why` flag computed at `:2857` and enforced at `:2026`. That is
  an `advance`, which closes the gate the agent is already inside. Neither `outcome` value fits it,
  and #467's whole point is that closing is not the offence. **Do not ledger it.**

If you believe a sixth site must write, that is a plan question. **Stop and return it** rather than
widening the ledger.

## Protected Intent

An agent that was told to wrap up and instead **began** new work must leave a mark the engine wrote,
which the next reader can find without taking anyone's word for it. The healthy world leaves **no
mark at all** — so the signal's value is entirely in whether it differs between the two worlds.

## Test Mode

**TDD required**, with mutation testing on every guard shipped.

### Test naming — load-bearing, the gate cannot close without it

`g4-integrate` runs this exact command as a closeout postcondition:

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'
```

I ran it at `9997c32d`: **exit 5, "384 deselected in 0.17s"** — pytest exits 5 on an empty
collection, so this check is genuinely failable today. **Every new test must have a name matching
`ledger`, `compliance`, or `trip_log`**, and they must live in `tests/test_checklist_engine.py`.
Frozen selector, not a style preference.

## THE DISQUALIFIER — read this before you write a line of test

**A compliance signal whose output is identical in the healthy and the defective world cannot
discriminate, however correctly it runs.**

For **each** defect shape you claim to catch, you must:

1. **Construct the defective spine** — the actual JSON state in which the defect is present.
2. **Construct the healthy counterpart** — same fixture, defect absent.
3. **Name the field that differs** between the two outputs, and assert on it.

A test that only asserts the defective side is a negative-only test and **cannot fail**. g3 proved
this the hard way: mutation M5 dead-coded the resolver and **all twelve** negative assertions still
passed. Ask of every test you write: *what would this do if the mechanism were deleted?* If the
answer is "still pass", the test is the defect.

## Sanctioned method for re-running mutations — use this one route

Two reviewers in a row hit the tension between "do not modify `scripts/`" and "re-run the mutations
yourself". You are the implementer, so `scripts/` and `tests/` are **yours** this gate. The route,
so your reviewer can repeat it exactly:

1. **Commit your implementation first.** Mutation testing against an uncommitted tree is how work
   gets lost.
2. For each mutation: apply the edit directly to `scripts/checklist_engine.py`, run the **named**
   test, record `(branch broken, named test that failed, TOTAL failure count)`.
3. **Revert with `git checkout -- scripts/checklist_engine.py`** and confirm `git diff --stat` shows
   the file clean **before** applying the next one. State that you confirmed it.

Do not use `git archive` snapshots here — you need no cross-commit baseline, and a temp tree with no
`.git` produces constant git-oracle noise.

## Close Criteria

- **(a)** The ledger exists, is append-only, records all eight fields, and records **both**
  outcomes. `begin-refused` survives the raise (because `main()` persists on the error path) —
  prove it end to end through the CLI, not by calling the function directly.
- **(b)** The predicate is **pure** (reads stored state only; no subprocess, no gauge read, no
  clock) and is keyed to the **live understanding**, so a stale entry from a superseded
  understanding does not read as current non-compliance.
- **(c)** `_trip_advisory`'s HARD branch was **extended**. Show there is exactly one render of this
  fact — a `grep` proving no second computation.
- **(d)/(e)** `docs/CHECKLIST_SCHEMA.md` documents the ledger, the predicate, and the limit.
- **Engine-written only.** No CLI verb creates, edits, or deletes an entry. **Prove it: name every
  write site and show each is unreachable from `_run_verb`.**
- **Fail-safe survives.** A `None` reading produces **no ledger entry AND no compliance claim** —
  silence must read as *neither compliant nor non-compliant*. A signal that reads silence as "clean"
  is the same defect class as a check that cannot fail.
- **Backward compatible.** A spine with no ledger drives unchanged (`setdefault` on first write,
  the `why_trail` idiom).
- **Every guard that loops asserts what it looped over — state the count.** A guard that passes on an
  empty set has not run.
- Every mutation turns its **named** test red, with **total** failure counts stated.
- The verification commands below are green.

## The limit you must not overclaim

Write this into `docs/CHECKLIST_SCHEMA.md` in plain words:

> The engine **cannot** observe an agent that is told to wrap up and simply **stops without running
> another verb**. `main()` does not save on `current`, which is where the band is evaluated
> read-only, and there is no mid-gate check. That case is visible to the invoker only as a stale
> `DIGEST` at the seam.

Say it plainly. **Do not claim coverage you do not have.** An honest declared limit is worth more
here than a boundary quietly left fuzzy.

## REQUIRED DELIVERABLE — `CHECK_THAT_CANNOT_FAIL.md`

**Admiral condition, wave-4 ruling. This is a required deliverable of this gate, not an appendix.**

Write `.agent-work/issue-467-trip-semantics/CHECK_THAT_CANNOT_FAIL.md` as a **first-class artifact**,
properly, **not compressed to a line**.

What happened: this run's Commander authored a DC6 observable that was **a check that cannot fail** —
true by construction, because `advance` already refuses a non-exempt gate without `--why`, so it was
green in both worlds. **Two cold critics found it independently.** An epic about checks that cannot
fail, whose own Commander nearly shipped one **inside the fix for it**, and whose own cold panel
caught it, is the most valuable thing this run can produce.

Source material already in the work area: `CRITIC_TRIAGE.md` (the two critics' findings),
`g2-mutation-log.md` and `g3-mutation-log.md` (M5's twelve green negative assertions; M15's false
`EQUIVALENT` declaration), `STATE_NOTE.md`. Cover at least: the shape of the defect, why it is
invisible from the inside, what actually caught it, and what a reader should do differently. **You
are not required to agree with the framing above** — if the evidence reads differently to you, write
what the evidence says and flag the disagreement.

## Allowed Scope

- `scripts/checklist_engine.py` — the Trip section: `_trip_hard_gate`, `_trip_advisory`'s HARD
  branch, the new ledger writer and predicate.
- `tests/test_checklist_engine.py` — new tests, and minimal reconciliation of existing tests.
- `docs/CHECKLIST_SCHEMA.md` — the ledger, the predicate, the limit.
- `.agent-work/issue-467-trip-semantics/g4-mutation-log.md` — the mutation log.
- `.agent-work/issue-467-trip-semantics/CHECK_THAT_CANNOT_FAIL.md` — the required artifact.

## Specific Exclusions

- **Do not re-open anything g2 or g3 shipped** — `TRIP_HARD_GUARDED_VERBS`, the no-silent-close
  rule, the advisory wording, the per-gate headroom override. All closed and reviewed.
- **Do not touch `docs/agents/GLOSSARY.md`.** g3b closed it at `9997c32d`; it is not yours.
- **Do not edit `_PROFILES`** in `scripts/gauge_reader.py`.
- **Do not let any CLI verb write a ledger entry.** No new verb, no flag, no `--ledger` anything.
- **Do not build a handoff-quality judge.** See the triage note below.
- **Do not ledger the close side** (`advance`/`require_why`) or the read-only advisory. Reasons above.

## Triage candidate — do NOT build here

Decision pressure this gate may surface: **whether handoff QUALITY (as opposed to presence) is
observable at all.** It carries no grade. Shipped v1 doctrine is that **reason quality is not
policed**. If it surfaces, **return it as an out-of-scope observation**; do not build a quality
judge in this gate.

## Standing traps — do not spend your context rediscovering these

1. **The gauge is discarded if `observed_at` is even slightly in the future (clock skew) or older
   than 30 minutes.** It collapses to "no gauge", and any scenario built on it goes **vacuously
   green**. This cost a previous agent a false negative. **Generate timestamps from the clock in
   your fixtures, never by hand.**
2. **The engine's printed `<why-id>` placeholder is literal.** Attaching it verbatim **exits 0 and
   silently does nothing**. Read the real id from the raw `why_trail`.
3. **A negative-only test cannot fail** — see THE DISQUALIFIER.
4. **`main()` does not save on `current`.** Anything you write on that path evaporates.

## Deliverable Path Check

I ran `git check-ignore` on each; **all five exit 1** (committable — `.agent-work/` is tracked in
this repo).

- **Committed** — `scripts/checklist_engine.py`, `tests/test_checklist_engine.py`,
  `docs/CHECKLIST_SCHEMA.md`
- **Committed, new** — `.agent-work/issue-467-trip-semantics/g4-mutation-log.md`,
  `.agent-work/issue-467-trip-semantics/CHECK_THAT_CANNOT_FAIL.md`. Untracked until staged, so they
  appear in `git status` rather than `git diff`.

## Required Evidence

**Load-bearing — prove rigorously:**

1. **The two-world demonstration, per defect shape.** For each shape: the defective spine, the
   healthy counterpart, and the **named field that differs**. This is the gate's central evidence.
2. **`begin-refused` survives the raise** — driven through the CLI end to end, showing the entry
   persisted after a refused verb.
3. **`begin-released` is recorded** — the verb proceeded while still over the line, and the ledger
   says so.
4. **No CLI verb can write an entry** — every write site named, each shown unreachable from
   `_run_verb`.
5. **The `None`-reading fail-safe** — no entry *and* no compliance claim. Assert both.
6. **The mutation log**, with per-mutation **total** failure counts and the revert confirmed
   between mutations.

**Confirmatory — spot-check:**

7. Backward compatibility: a spine with no ledger key drives unchanged.
8. `_trip_advisory` extended, not duplicated (the grep).
9. The schema doc carries the limit verbatim in substance.

Quote exact expected strings so tests assert equality. Derive any failure distribution
**mechanically**, from a command, never by eye:

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests 2>&1 | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
```

## Wiring Grep

Required. One command naming every symbol this slice adds, showing a call site **outside** its own
definition and outside any `--self-test` path. **State the count. Zero external call sites is a stop
condition.**

```bash
grep -rn "<each new symbol>" --include=*.py . | grep -v "def <symbol>" | grep -v self_test
```

## Verification Commands

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

The second is the frozen `g4-integrate` closeout selector — run it and confirm it **collects** your
tests (it must no longer exit 5).

**Full-suite baseline, measured by me at the parent commit `9997c32d`:**

```
1833 passed, 2 skipped, 808 subtests passed
```

Explain any delta against **that** number and **that** commit.

## Suggested Model Tier

**Opus.** Named reason, per the Admiral's model ruling: an engine-only append-only trip ledger at
mutating chokepoints is **engine-semantics work where being subtly wrong is invisible** — the
failure mode is a signal that runs correctly and discriminates nothing.

## Authority

**Settled, do not re-open:** engine-written only; append-only; the two `outcome` values; extend
`_trip_advisory` rather than duplicate it; fail-safe on a missing reading; backward compatibility;
the scoped limit is declared rather than engineered away.

**Yours to author:** the ledger key name and entry field encoding, the predicate's name and exact
return shape, the advisory's extended wording, and the structure of `CHECK_THAT_CANNOT_FAIL.md`.

**You must not decide alone:** adding a ledger write site beyond `_trip_hard_gate`; letting any verb
write an entry; reading a `None` gauge as compliant; building a handoff-quality judge; or weakening
the two-world demonstration to a one-sided assertion.

## Stop Conditions

Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required
evidence cannot be produced, a decision outside the given authority is needed, or **any defect shape
you claim to catch turns out to produce identical output in both worlds** — that last one is a
finding, not a failure, and I want it.

## Return Format

Return **IMPLEMENTER_RESULT**: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

**State explicitly, in their own sections:**

- **The two-world table** — every defect shape, its differing field, and the assertion that reads it.
- **Every ledger write site**, and the proof each is unreachable from `_run_verb`.
- **Anything you could NOT make discriminate.** A declared limit is a good outcome here; a quiet one
  is the failure this gate exists to prevent.

Write your result to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g4-implementer-result.md`.

**Deliver your result via `SendMessage` to `commander-w4-467-g` before ending your turn.**
