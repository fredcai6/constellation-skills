# Reviewer Handoff — g4-review

**This is the review that matters most in this run.** #467 exists because a check that cannot fail
shipped inside an epic about checks that cannot fail. g4 is the gate that makes non-compliance
observable. If the observable it ships is green in both worlds, the whole issue closes on nothing.

## Gate

`g4-review` — issue #467, epic #418. Work area `.agent-work/issue-467-trip-semantics/`,
branch `epic-418/a2-467-trip-semantics`, worktree `C:/Programs/constellation-skills-wt/epic418-a2-467`.

## Survey State Location

Drive your own review survey at
`.agent-work/issue-467-trip-semantics/g4-review/` — **use exactly that directory name.**

Two review surveys on this run already collided and would have overwritten each other's sidecars;
the previous Commander avoided it only by renaming one by hand. It is filed as triage candidate
`tc6`. **Do not** write into `.agent-work/issue-467-trip-semantics/` root, and do not reuse a `g3-*`
directory.

## How to Inspect the Diff

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-467
git log --oneline 9997c32d..HEAD          # two commits: 20240f44, f74ef422
git diff 9997c32d..HEAD -- scripts/ tests/ docs/
```

**`9997c32d` is the parent commit of this diff.** Every baseline below was measured by me, in this
worktree, at that exact commit. Do not subtract against any other commit — a stated baseline that
was not the parent cost two agents real time earlier in this run. If a number disagrees with mine,
say which commit you measured at.

## What Was Implemented

- **`trip_ledger`** — an optional top-level, append-only list on the spine, created with
  `setdefault`, written **only** inside `_trip_hard_gate`, recording `begin-refused` and
  `begin-released` entries.
- **`begin_over_line_records`** — a pure selector over the spine; **emptiness is the predicate**,
  keyed to the live why-record.
- The **existing** `_trip_advisory` HARD branch extended in both sub-branches, one computation.
- `docs/CHECKLIST_SCHEMA.md` — the ledger shape, the predicate, and the scoped limit.
- `.agent-work/issue-467-trip-semantics/g4-mutation-log.md` — 19 mutations.
- `.agent-work/issue-467-trip-semantics/CHECK_THAT_CANNOT_FAIL.md` — required Admiral-condition
  artifact, 219 lines.

**A ninth entry field, `why_ref`, was added beyond the eight the plan named.** It reverses
critic-panel finding 14. See "Claims to attack".

## Task Statement

**Hunt one failure mode above all others: a compliance signal that is green in both worlds.**

Everything else in this review is subordinate to that. A signal can be correct, tested, documented,
and mutation-killed, and still discriminate nothing.

## Close Criteria

Classify each finding **blocking** or **non-blocking**.

1. **Every defect shape discriminates.** For **EACH** shape in the implementer's two-world table
   (11 numbered shapes plus the `5b`/`6b`–`6e` variants — count them yourself),
   **construct the defective spine YOURSELF** and confirm the signal **actually differs**. Do not
   verify this by reading the test. Build the state and look at the output.
2. **Re-run EVERY mutation in the log — all 19, not a sample.** **Any mutation that leaves its named
   test green is a BLOCK.** The log claims 19/19 killed and declares **no** equivalent mutants.
3. **No CLI verb can write a ledger entry.** Check **every** write site. The implementer asserts the
   write site is unreachable from `_run_verb`, derived off the engine's call graph with `ast` and
   falsified by mutation N18. Verify the claim, and verify the method.
4. **A `None` reading produces neither a compliant nor a non-compliant claim.** Silence must read as
   *neither*. A signal that reads silence as "clean" is the same defect class as the gate's own
   target.
5. **The scoped limit is written into `docs/CHECKLIST_SCHEMA.md` and is not overclaimed** — the
   engine cannot observe an agent that is told to wrap up and simply stops without running another
   verb. Check the doc says so plainly, and check nothing elsewhere in the doc contradicts it.
6. **`_trip_advisory` was extended, not duplicated.** One computation of this fact, not two.
7. **Append-only holds.** No prior entry is ever mutated or removed.
8. **Backward compatibility.** A spine with no ledger key drives unchanged.
9. **`CHECK_THAT_CANNOT_FAIL.md` is a genuine first-class artifact**, not a compressed line. It is a
   frozen Admiral condition. Judge it on substance: does it explain the shape of the defect, why it
   is invisible from the inside, what actually caught it, and what a reader should do differently?

## The claims you are asked to ATTACK, not confirm

**A1 — the ninth field `why_ref`, which reverses critic-panel finding 14.**
Finding 14 dropped it as "recoverable from `why_trail`". The implementer put it back, arguing the
predicate must know which why-record was live *at the moment of the trip*, recoverable otherwise only
by timestamp comparison at second granularity. Mutation N7 claims 12 tests red without it. **Attack
both directions:** is it genuinely irrecoverable, and is N7's 12-test blast radius evidence of
load-bearingness or merely of wide coupling? This is floated to the Admiral in parallel; your
independent read is wanted either way, and you are not bound by my recommendation to confirm it.

**A2 — the four single-test mutations: N6, N8, N15, N16 (total failures 1, 1, 1, 1).**
A one-test kill is either excellent specificity or a test asserting something trivial. Decide which,
per mutation. N8 is the fail-safe (criterion 4) and N6 is the per-gate hard line — both are
load-bearing enough that a weak test there matters.

**A3 — the declared TDD deviation.** The implementer states m2's RED was obtained by **dead-coding
the selector rather than by its absence**, because the selector was authored alongside the m1 writer.
Judge whether that weakens the anti-vacuity guarantee for the tests concerned.

**A4 — the declared negative-only test.** One backward-compatibility test is negative-only and named
as such. g3 proved this class can be worthless: mutation M5 dead-coded a resolver and **all twelve**
negative assertions still passed. Ask of it: *what would this do if the mechanism were deleted?*

**A5 — the implementer used `amend` with `--authority "implementer, self-caught"`** where the schema
describes authority as human ratification. It declared this rather than letting it pass. The
amendment only tightened six of its own checks. Judge whether the record is honest and adequate.

## Sanctioned method for re-running mutations — use this one route

"Do not modify `scripts/`" and "re-run every mutation yourself" are in direct tension, and two
reviewers in a row hit it on this run. **Resolved for you, so you do not have to invent one:**

1. The tree is committed at `f74ef422`. For each mutation: apply the edit directly to
   `scripts/checklist_engine.py`, run the **named** test, record the result.
2. **Revert with `git checkout -- scripts/checklist_engine.py`**, and confirm `git diff --stat` shows
   it clean **before** the next mutation. State that you confirmed it.
3. You may write scratch probe scripts under **your own** `g4-review/` directory — that is the
   preferred route for "is this test vacuous", because it imports the shipped engine directly with no
   missing-`.git` noise.

**Do not** use `git archive` temp trees here: you need no cross-commit baseline, and a tree with no
`.git` produces constant git-oracle failures that cost a previous reviewer real time.

**Modifying `scripts/` under this route is sanctioned and expected.** Leave the tree clean when done.

## Allowed Scope (what the implementation was permitted to touch)

`scripts/checklist_engine.py` (the Trip section), `tests/test_checklist_engine.py`,
`docs/CHECKLIST_SCHEMA.md`, `.agent-work/issue-467-trip-semantics/g4-mutation-log.md`,
`.agent-work/issue-467-trip-semantics/CHECK_THAT_CANNOT_FAIL.md`.

The implementer also committed its own driven plan under `crew-plans/`, by precedent from g1/g2/g3.
Noted, not a scope breach.

## Specific Exclusions (flag if touched)

- Anything g2 or g3 shipped — `TRIP_HARD_GUARDED_VERBS`, the no-silent-close rule, the advisory
  wording, the per-gate headroom override.
- `docs/agents/GLOSSARY.md` — closed at `9997c32d` by the gate before this one.
- `_PROFILES` in `scripts/gauge_reader.py`.
- Any CLI verb, flag, or path that writes a ledger entry.
- A handoff-**quality** judge. Shipped v1 doctrine is that reason quality is not policed; it is a
  triage candidate, not this gate's work.
- The close side (`advance`/`require_why`) and the read-only advisory are **deliberately not** ledger
  write sites. If the implementation ledgers either, that is a finding.

## Standing traps — do not spend your context rediscovering these

1. **#431 is an instruction-conformance defect, not a mechanical deadlock.** A test worded "the
   advance is no longer blocked" passes in **both** worlds. **Verify on what the agent is TOLD.**
2. **DC6's observable is "did anyone BEGIN work while over the line"**, never "did a handoff artifact
   appear" — that second one is true by construction, because `advance` already refuses a non-exempt
   gate without `--why`. That is the defect this gate was corrected away from.
3. **The gauge is discarded if `observed_at` is in the future (clock skew) or older than 30 minutes.**
   It collapses to "no gauge" and any scenario built on it goes **vacuously green**. This cost a
   previous agent a false negative. Generate fixture timestamps from the clock, never by hand.
4. **`main()` does not save on `current`.** Anything written on that path evaporates.
5. **The printed `<why-id>` placeholder is literal** — attaching it verbatim exits 0 and silently does
   nothing. Read the real id from the raw `why_trail`.
6. **Use the engine in THIS worktree** (`scripts/checklist_engine.py`, 156060 bytes, has the fix).
   Both installed bundles are pre-#467 and will mislead you. If you verify engine behaviour, verify
   it against the worktree copy and say which you ran.
7. **`execute.json["tasks"]` is a dict keyed by id; `["items"]` is a list of id strings.** Iterating
   `items` gives you strings, not tasks.

## Evidence Produced (re-run it; do not accept it on the report)

Measured by me at the parent `9997c32d`:

| Command | At parent `9997c32d` |
|---|---|
| `pytest -q tests` | **1833 passed, 2 skipped, 808 subtests** |
| `pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'` | **exit 5**, 384 deselected |

Measured by me at `f74ef422` (the head of this diff), re-running the implementer's claims myself:

| Command | At `f74ef422` |
|---|---|
| `pytest -q tests` | **1858 passed, 2 skipped, 821 subtests**, exit 0, zero `FAILED` lines |
| `pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'` | **25 passed, 384 deselected, 13 subtests**, exit 0 |

The delta is **+25 passed, +13 subtests** — exactly the selector's own collection, and the 384
deselected is unchanged from the parent, so all 25 tests are genuinely new. **Confirm this
independently.**

Derive any failure distribution **mechanically**, from a command, never by eye:

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests 2>&1 | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
```

## Constraints the Implementation Must Respect

- Engine-written only; append-only; the two `outcome` values; `_trip_advisory` extended not
  duplicated; fail-safe on a missing reading; backward compatible; the scoped limit declared rather
  than engineered away.
- **Any guard that loops must assert what it looped over — the count.** A guard that passes on an
  empty set has not run. Check this of the implementation's guards **and of your own**.

## Suggested Model Tier

**Opus** — the adversarial-review carve-out under the Admiral's model ruling. Both g3 reviews ran
this way and both earned it: the first found a real blocking defect, the second falsified the
rework's own numbers.

## Stop Conditions

Stop and return if: you cannot construct a defective spine for a shape the implementer claims to
catch; a mutation cannot be re-run; the tree cannot be returned to a clean state; or a decision
outside your authority is needed.

## Return Format

Return **REVIEW_RESULT**. **Your verdict must be exactly `APPROVE` or `BLOCK`**, on the **first
line** of your result, with the reasoning under it. No other verdict vocabulary — the engine matches
on that literal string, and a gate whose reviewer invents a third word cannot close.

`APPROVE` means **zero blocking findings**. Non-blocking findings are welcome and expected alongside
an APPROVE; report them, classified. If you have even one blocking finding, the verdict is `BLOCK`.

Also state, on its own line, **`blocking_findings: <N>`** — I carry it into the engine payload.

Include: per-check findings against the nine close criteria (each classified), **your own two-world
construction for every defect shape**, **all 19 mutation re-runs with their totals**, the five claims
you were asked to attack (A1–A5), blockers, anything you could not verify and why, out-of-scope
observations, and workflow feedback — specifically, anything in this handoff that made the review
harder than it needed to be.

Write your result to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g4-reviewer-result.md`.

**Deliver your REVIEW_RESULT via `SendMessage` to `commander-w4-467-g` before ending your turn.**
