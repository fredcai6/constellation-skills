# Reviewer Handoff — issue-304 gate g4: dogfood the edited spine, then close out

## What was implemented

**Demonstration, not construction.** `git diff` outside `.agent-work/` is empty — zero product-code
changes. The gate materialized the **edited** `COMMANDER_SPINE.template.json` through
`scripts/init_work_area.py` into a scratch work-id in this repo (the degraded common case: `docs/agents/`
present, `docs/architecture/` absent), drove it through the engine until the new context command check
fired end to end, and ran the full suite.

## How to inspect

```
cd C:/Programs/constellation-skills-wt/e298-304
git log --oneline 4f9c6d1..HEAD
git diff 4f9c6d1..HEAD
```

`4f9c6d1` is the g3 close — **g1, g2 and g3 are all reviewed and APPROVED. Do not re-review them.**
Implementer report: `.agent-work/issue-304/crew-handoffs/g4-result.md`. Handoff it was built against:
`g4-implementer-handoff.md`. Prior run evidence: `.agent-work/issue-304/TRIPWIRE_OUTCOMES.md`.

## THE QUESTION THIS HANDOFF EXISTS TO ASK

**CAN THIS CHECK FAIL?**

Asked because #300 shipped an acceptance test that survived two independent reviewer rounds while being
structurally unable to falsify the property it existed to falsify. *"A reviewer given a handoff checks
conformance to that handoff, and no handoff asked 'can this test fail?'"*

**Answer by execution.** Devise at least one mutation of your own that is NOT among the nine in
`tests/test_mutation_floor.py` and not among the four the g3 reviewer aimed at the template, apply it,
run the suite, report red/green with real output.

**This gate's hazard differs from the earlier ones, and you should aim there:** g4's deliverable is
*evidence*, not code, so its failure mode is a **demonstration that would have looked the same if the
contract did nothing**. Attack that. Break the wiring — point the check at a subcommand that does not
exist, or neuter `verify-orientation`'s refusal — re-run the dogfood, and confirm the engine **stops
advancing**. If the spine reaches `context -> complete` either way, the demonstration proved nothing and
this is a BLOCK.

## The three claims to verify by re-running, not by reading

1. **It reports rather than silently passing.** Claimed exit path `12 -> 10 -> 10 -> 0`:
   `RECEIPT-MISSING` with no receipt, then — a stage g3 never isolated — a receipt **present but
   undischarged** still refusing at exit `10`, with all three absent map candidates enumerated by path.
   Reproduce the middle stage; it carries the new information.
2. **No deadlock, no `--force`, no waiver.** Claimed proof: the scratch spine's journal verbs are exactly
   `advance`, `attest`, `start` — no `waive`, no forced override. **Check the journal yourself.** Note
   that stdout is discarded and the **exit code is the only signal reaching the spine**.
3. **Placeholders resolved.** Claimed: zero resolver-family tokens survive in the materialized
   `spine.json`. Note the implementer's own stated caveat — `<commander-skill-dir>/scripts` resolved to
   the **relative** `scripts` via `init_work_area.py`'s source-repo auto-detect branch. The token is
   gone, but the path is relative. Confirm that is the documented branch and not a resolution failure
   wearing a plausible explanation. Its fragility is **#341 and out of scope** — do not re-file it.

## The full suite

Claimed: **1538 passed, 2 skipped, 481 subtests passed in 202.12s**, exit 0, local python 3.14.3, run
twice. Re-run it (about 3.5 minutes — it has not hung) and report your own number. A local green is
**not** the merge gate; CI pins 3.12 and the Commander gates on the CI status read at source.

## Deviations to judge

1. **`git add -A .agent-work/issue-304/` in `a90262e` swept in the Commander's own in-flight engine
   writes** (`execute.json`, `crew-runs.json`). The implementer owned this unprompted. Confirm nothing
   was **altered or lost** — a crew committing its orchestrator's state is a contamination risk even
   when benign. Later commits named explicit paths.
2. **The full suite was run twice**, deliberately, because the engine discards stdout.
3. **Mis-scoped exit values in the first transcript block** (the pipeline tail was `grep`), caught
   mid-run; stage A was re-run with codes captured before any pipe, a note written at the boundary, and
   the uncorrected lines **left in place rather than edited out**. Judge whether every exit code quoted
   in the result comes from the corrected runs. Leaving the bad lines visible is the honest choice;
   silently rewriting them would not have been.

## Two findings the implementer reported and did NOT fix — confirm they are real, do not fix them

- The `context` imperative says *"append `--report-only` to the command below"*, but the engine's
  `current` never renders command text. An agent following `current` alone — which doctrine requires,
  and which a cold-started refresh agent has — cannot act on that sentence without reading `spine.json`,
  which the same doctrine calls a violation. Verify `current` really does not render it.
- A substitute present on disk and hash-pinned (`docs/agents/ORCHESTRATOR_CONTEXT.md`) is labelled
  *"not corroborated by the filesystem."* The classification is correct and test-pinned; the **wording**
  overclaims — the accurate phrase is "not in the fixed fallback set." **This one matters more than its
  size:** this issue's headline deliverable is *honest reported degraded mode*, and a report line
  calling a present, hash-pinned file uncorroborated undercuts exactly that. Give it a severity.

## The stated scope gap — verify it is stated, not papered over

g4 exercises the **degraded** arm only. The mapped (`RESOLVED`) arm is untested here: no
`docs/architecture/` in this repo, and f1Brainz is off-limits because `orient` writes a receipt into its
`--root`. T3's mapped-repo clause remains unfalsified and unconfirmed. Confirm the result says this
plainly rather than letting the degraded demonstration read as full coverage.

## Cleanup claims

Scratch removed; `TRIPWIRE_OUTCOMES.md`, `TREND_SNAPSHOT.md`, `g3-result.md`, the g3 transcript,
`g3-implementer-plan.json`, `spine.json` and `TRIPWIRES.md` all unchanged **by blob OID**, and
`TRIPWIRES.md` byte-identical to its pre-registration `1662b90`. **Only claim a cleanup you have
verified** — an earlier result on this issue asserted a removal that had not happened. Re-check these.

## Allowed scope / exclusions

Review `4f9c6d1..HEAD` only. Out of scope, do not flag: g1/g2/g3; #341 (relative command checks); #342;
#344; #363; #364; a bootstrap/`CLAUDE.md` stanza (**ruled OUT** by the human). Do not fix anything.

## Known limitations — not novel finds

Measured sensitivity **0/4**, specificity **0/1**; ships as a **regression floor**, not the fix for
map-lateness. The degraded check is partly self-attested. Both ratified. **Do flag any overclaim.**

## Constraints

- `python -m pytest`, never `py -m pytest`. Flag any 3.13+-only API as a BLOCK.
- Compare normalized content or blob OIDs, **never raw bytes** — `git status --porcelain` shows a
  phantom `M` from CRLF while `git diff --quiet HEAD` returns 0. Five agents in this epic have hit this.
- **Do not point any tooling at `C:/Programs/f1Brainz`.** Never touch `C:/Programs/constellation-skills`
  or `C:/Programs/constellation-skills-wt/e298-331`. Do not rewrite `TRIPWIRES.md`.

## Required evidence

Paste actual output for: **your own mutation** (the diff, and the engine's behaviour under it); the
undischarged-receipt refusal stage; the scratch spine's journal verbs; the full suite; and your
re-verification of the cleanup blob OIDs.

## Return format

Write `REVIEW_RESULT` to `.agent-work/issue-304/crew-handoffs/g4-review-result.md`, verdict exactly
**APPROVE** or **BLOCK**, findings by severity, evidence pasted. Return thin.
