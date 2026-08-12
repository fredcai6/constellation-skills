# Reviewer Handoff — g4 REWORK re-review (attempt 2)

Issue #467 (epic #418), branch `epic-418/a2-467-trip-semantics`, worktree
`C:/Programs/constellation-skills-wt/epic418-a2-467`. Work only in this worktree, absolute paths.

**Engine under review — pin it by hash, not by size.** A previous handoff on this run quoted a byte
size that matched nothing on disk, and the reviewer correctly called that out. Confirm you have the
right file with:

```
git rev-parse HEAD                              -> e33f9eb11a631927e1b4b4e3ec425b87a59f44e0
git rev-parse HEAD:scripts/checklist_engine.py  -> c281cb68eaac65d1169dd6737a6a322728df98eb
```

Everything you measure must come from `scripts/checklist_engine.py` **in this worktree**, never an
installed skill bundle.

## Why you are here

`g4` shipped the trip ledger and its compliance signal. The **first** independent review
(`crew-handoffs/g4-reviewer-result.md`) drove a 21-item survey, constructed all 17 defect shapes
from scratch, re-ran all 19 mutations, **passed eight of the nine close criteria**, and returned
**BLOCK on exactly one finding, B1**. The Commander reproduced B1 in its own shell with the
reviewer's own probe rather than accepting it on the report.

A rework then addressed B1 only. **This is the re-review of that rework.** The diff you are
reviewing is commit `e33f9eb1` and nothing else.

**Do not re-review g4.** The eight passed criteria were verified by attack and are settled. Your job
is narrow but it is the most consequential judgement left in this issue.

## B1, so you can judge the fix against the defect

At/over hard, `advance --mechanical` is refused (g2's no-silent-close rule), so the **only** legal
close is `advance --why`. That appends a new `why_trail` record. `begin_over_line_records` matches an
entry only when `entry["why_ref"] == _latest_why_record(cl)["id"]`. Therefore **the close the HARD
band orders an agent to make was guaranteed to empty the only rendered compliance signal**, and the
shipped line said `"Closing this gate does not clear the record."`

Measured before the rework, across a 3-gate runaway: 3 over-the-line begins on disk, the rendered
line never claimed more than 2, and **at the seam it was absent** — byte-identical to a compliant
agent that closed its gate and stopped. Green in both worlds, at the exact place the next reader
looks.

## What the rework claims to have done

Read `crew-handoffs/g4-rework-implementer-result.md` (726 lines) and
`crew-handoffs/g4-rework-implementer-handoff.md` for the ruled fix space. In summary it claims:

1. A second **pure, unkeyed** selector `begin_over_line_records_historical` over the same
   `trip_ledger` entries — no new state, nothing keyed to a why-record, so nothing supersedable.
2. A second rendered line, **`TRIP HISTORY`**, computed once and appended to **both** HARD
   sub-branches, which renders whenever anything is on record — including when the live line has
   gone silent.
3. The false sentence corrected; the **fourth limit** declared in `docs/CHECKLIST_SCHEMA.md`
   alongside the other three; the supersede narrative no longer implying the mechanism can tell a
   fresh agent from the offender.
4. `test_compliance_line_is_absent_once_the_recorded_begin_is_superseded` — a **passing test that
   certified the bug** — renamed and corrected to assert the live line goes absent **and** the
   historical line still names the retained begin.
5. Mutations N20–N22 added; N17 corrected as crash-noise; `CHECK_THAT_CANNOT_FAIL.md`'s "every one
   of this gate's 25 tests" overclaim corrected to 24.

## The one question that decides this review

**Is the new historical line itself a check that cannot fail — in either direction?**

This whole issue exists to make that discrimination, so make it by attack, not by reading.

- **Does it discriminate?** Build **both worlds yourself** and run `current` at the seam in each:
  World H, a compliant agent told to wrap up that closes its gate with `advance --why` and stops;
  World D, a runaway with at least one over-the-line BEGIN that then closes the same way. **The
  rendered output must differ, and D must name the true total.** If they are byte-identical you have
  found the fix failing at the only place it matters.
- **Can it be silenced?** Try to make it go quiet while an over-the-line begin is on disk. Try every
  close verb, `reopen`, `block`/`resume`, `skip`, `waive`, `amend`, `attach`, `--dry-run`, a
  `why_exempt` spine, a spine with no `why_trail` at all. If any legal sequence clears it, that is
  B1 again in a new coat.
- **Can it fail to pass?** The mirror defect. The Admiral refused widening the live selector in
  advance precisely because it "converts a check that cannot fail into one that cannot pass".
  Confirm the **live** line still behaves as close criterion (b) intends — that a genuinely fresh
  understanding stops reading as present-tense non-compliance — and that the historical line is
  labelled and worded as a **historical fact**, not as a present-tense verdict that can never be
  cleared. A permanent red badge that no correct behaviour can ever clear is its own defect.
- **Is the keying untouched?** `git diff 28dd434c..e33f9eb1 -- scripts/checklist_engine.py` must show
  **zero** change inside `begin_over_line_records`. Verify it; do not take the claim.

## Two checks the Admiral named explicitly — these are the ways this fix can be wrong while looking right

**A. The pinned test must now DISCRIMINATE, not merely pass.**
`test_compliance_line_is_absent_once_the_recorded_begin_is_superseded` ran the offender's path
byte-for-byte and called it "a fresh agent". **Adding a historical line does not by itself unpin
that.** A renamed test that still asserts only absence is the same defect with a better name. Prove
the corrected test discriminates: dead-code the historical selector and confirm the test goes red. If
it stays green, it is still certifying the defect.

**B. Mutation-test the new line at the seam.** Break `begin_over_line_records_historical` and confirm
the **seam measurement** goes red — not merely that some unit test fails. *A second observable added
to fix an unobservable one is exactly where a check that cannot fail gets introduced*, and this issue
already has one specimen that arrived that way. Treat the new line with the same suspicion the first
review brought to the old one.

## Also verify, by attack

1. **The corrected test really stops pinning the defect.** Read it. Would it still pass if the
   historical line were dead-coded away? (It should not — check by doing it.) Does its name and
   docstring now say it is the **offender's own close** rather than "a fresh agent"?
2. **One computation, one render site** (close criterion 6, previously PASS). `grep 'TRIP LEDGER'`
   and `grep 'TRIP HISTORY'` over `scripts/` must each find exactly one render site; each fact must
   be computed once above the two HARD returns and appended to each.
3. **Purity and the read-only path** (criterion 8, previously PASS). The new selector must read only
   `trip_ledger` — no subprocess, gauge read, clock or I/O — and must not raise on a malformed
   ledger (`None`, a string, a dict, a list holding non-dicts).
4. **Engine-written-only still holds** (criterion 3, previously PASS, proved by an `ast` call-graph
   audit). The new function is a **reader**. Re-run the call-graph proof yourself: confirm
   `_append_trip_entry`'s only caller is `_trip_hard_gate`, whose only caller is `dispatch`, and that
   the new selector's only caller is `_trip_advisory`.
5. **The pre-existing HARD strings are unaltered.** They were pinned by equality; confirm the healthy
   advisory is still a strict prefix of the defective one, so the delta is exactly the added lines.
6. **Re-run N20, N21 and N22 yourself**, authoring your own anchors from the source rather than
   copying the driver. N22 (historical selector keyed to the live record) re-creates B1 exactly and
   **must be killed at the seam**. You do not need to re-run N1–N19 — the first review already did,
   19/19 killed — but **do** re-run any mutation whose named test the rework touched.
   *Note the revert protocol:* the rework is now **committed** at `e33f9eb1`, so `git checkout --`
   plus `git diff --quiet` works again. Assert the tree clean before each next mutation.
7. **The sentence is actually true now.** Read the live line's replacement wording aloud against the
   behaviour you measured. The first review's standard applies: a compliance string that is
   defensible only under a charitable reading is not a compliance string. Judge the **wording**, not
   just the mechanism — B1 was half a wording finding.
8. **The declared limit reads like the other three.** Compare it to the three already in
   `docs/CHECKLIST_SCHEMA.md`'s "The limit — what this cannot observe" section. Is it as plain? Does
   it overclaim in the other direction?
9. **The artifact corrections are honest.** N17 corrected visibly rather than silently rewritten;
   the `CHECK_THAT_CANNOT_FAIL.md` line-172 correction states what was false and what is true.
10. **The implementer's own declared discrepancies.** It reports a full suite of 1867 passed / 2
    skipped / 828 subtests / exit 0 against a stated baseline of 1858 / 2 / 821 — so **+9 passed,
    +7 subtests** — and says the +7 does not reconcile against its own count of +8. Judge whether
    that gap matters. (The spine already carries a triage candidate that `test_context_manifest`
    filters to files clean in the working tree, so a dirty tree moves the subtest count by one. Check
    that hypothesis rather than assuming it.) It also reports finding and fixing a **self-reference
    bug in its own first-draft wording** — the live line's text literally contained the substring
    `TRIP HISTORY`, so a substring search matched the wrong line. Confirm the shipped wording no
    longer does that.

## Evidence to re-measure (do not accept the report)

- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — capture the **real** exit code (redirect to a
  file and echo `$?`; a piped exit code is the pipe's). Explain any delta from 1867 / 2 / 828.
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'ledger or compliance or trip_log'`
  — must pass **and collect**. pytest exits **5** on an empty collection, which is a green-looking
  exit that proves nothing.
- The seam measurement, built by you, through the **real CLI in a subprocess**, on a real
  `gauge.json` **stamped from the clock**, with **no mock in the advisory path** (pass a real
  `base_dir` holding a real gauge rather than patching `_read_gauge`). The first review held this
  standard and it is what made its finding stick.
- `.agent-work/issue-467-trip-semantics/g4-review/probe_clearing.py` — your own probe from the first
  review, now carrying a declared mechanical edit. Re-run it and judge whether the edit is honest or
  whether it weakens the probe's detection.

## Standing traps on this run — all seven still apply

1. **Verify on what the agent DOES, never on what it is TOLD.** B1 was this trap one level up.
2. `main()` does **not** save state on `current`.
3. **Clock skew / stale gauge.** A reading is discarded when >30 min old **or dated in the future**.
   A hand-typed `observed_at` slightly ahead of the wall clock collapses to `None`, the scenario
   reads as "no gauge", and the test goes **vacuously green**. Generate every timestamp from the
   clock.
4. No mock in the advisory path for the seam measurement.
5. **`SUBFAILED` vs `FAILED`.** pytest reports subtest failures as
   `SUBFAILED(param) path::Class::test`. A `FAILED`-only grep reported two **false survivors** in the
   first review and would have produced a wrong BLOCK. Match both.
6. Pin the engine by hash (given above), never by byte size.
7. **CRLF.** `git checkout` of a subset of files can renormalize line endings and dirty
   `test_context_manifest`. Check `git status --porcelain` after every revert.

## Scope

- **In:** commit `e33f9eb1` in full — `scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`,
  `tests/test_checklist_engine.py`, `g4-mutation-log.md`, `CHECK_THAT_CANNOT_FAIL.md`, and the
  `probe_clearing.py` edit.
- **Out:** everything the first review already passed; g2's and g3's shipped mechanisms; the `tc4`
  refactor (band judgment assembled at three sites, `_append_trip_entry`'s seven parameters) which is
  filed as a triage candidate and deliberately deferred.
- Do **not** touch `.agent-work/issue-467-trip-semantics/execute.json`, `spine.json`, `gauge.json` or
  `STATE_NOTE.md` — the Commander holds their lease. Do **not** run `checklist_engine.py` against
  them. Drive your own survey at
  `.agent-work/issue-467-trip-semantics/g4-rework-review/review.json` and build fixture spines in
  your own temp directory.
- Do not commit.

## Verdict discipline — read this before you write anything

Return **exactly one** of `APPROVE` or `BLOCK` as the first line, followed by
`blocking_findings: <n>`.

- **Do not invent a third verdict string** and do not soften one to fit. The Commander is under
  standing orders to float any other verdict to the Admiral rather than reword it, so a
  non-conforming verdict stalls the gate rather than passing it.
- **BLOCK only for something that actually blocks.** A finding that does not falsify a close
  criterion is an observation. Say so and let it be one.
- **APPROVE if it holds.** The rework is narrow and was ruled narrow by the Admiral. Do not manu-
  facture a blocking finding to justify the review, and do not expand the fix space on your own
  authority — if you believe the fix space itself was wrong, say that as a finding addressed to the
  Commander and let it route upward.
- Out-of-scope finds go in a **triage candidates** section, not the verdict.

## Suggested model tier

**Sonnet.** Standing default for reviewers on this run. No named Opus reason applies: the defect is
already characterised, the fix space was ruled, and the review is a bounded attack on one added
mechanism against a criterion list you are handed.

## Stop conditions

Stop and return without a verdict only if you cannot reach a defensible one — for example if the
diff does not match the stated commit, or if answering the deciding question would require changing
the live selector's keying (refused in advance by the Admiral, and the Commander's to route). Report
"this specific check failed", never "this approach is impossible".

## Return format

Return a `REVIEW_RESULT` to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g4-rework-reviewer-result.md`, first line
`APPROVE` or `BLOCK`, second line `blocking_findings: <n>`, then: your answer to the deciding
question with the measurements behind it; the two-worlds seam output verbatim; the silencing attempts
you tried and what each did; the mutation re-runs with totals; the re-measured evidence; per-item
findings against the criteria above; non-blocking findings; triage candidates; and workflow feedback.

**Deliver it via `SendMessage` to `commander-w4-467-h` before ending your turn.**
