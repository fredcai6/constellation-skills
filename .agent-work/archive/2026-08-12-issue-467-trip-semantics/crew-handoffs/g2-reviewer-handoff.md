# Reviewer Handoff

## Gate
`g2-review` — issue #467, epic #418. Worktree `C:/Programs/constellation-skills-wt/epic418-a2-467`,
branch `epic-418/a2-467-trip-semantics`.

## Survey State Location

Create your review survey checklist at
`.agent-work/issue-467-trip-semantics/g2-review/review.json` — under the issue workbench, never at
the worktree root.

## What Was Implemented

The Trip HARD guard was moved off the verb that **closes** a gate and onto the verbs that **begin**
work at one, and the trip advisory was rewritten to read as a changed instruction rather than an
alarm. Five parts:

- **(a)** `dispatch` no longer calls `_trip_hard_gate` on `advance`.
- **(b)** The guard hangs off a new `TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}` at the dispatch
  chokepoint. #190's identity check preserved, including the `wid is None` gate-only degradation.
  `resume` is **not** guarded.
- **(c)** At/over hard, `advance --mechanical` is refused and `why_exempt` is suspended — and
  suspended means the `--why` is actually appended to the `why_trail`, not merely demanded.
- **(d)** HARD advisory rewritten; `_refresh_attach_hint` emits the concrete why-record id instead
  of the literal `<why-id>`.
- **(e)** `docs/CHECKLIST_SCHEMA.md` Trip section and the `start`/`advance`/`reopen` verb rows
  updated.

The implementer reports the pure-verb seam held: `advance` gained one keyword
`require_why: bool = False`, and a new `_trip_hard_band_reading` is the single place deciding
"at/over hard", so the begin-guard and the no-silent-close rule cannot drift apart.

## How to Inspect the Diff

The gate is **committed**, at `38f0b448` on `epic-418/a2-467-trip-semantics`. Review that commit:

```bash
git show --stat 38f0b448
git show 38f0b448 -- scripts/checklist_engine.py tests/test_checklist_engine.py docs/CHECKLIST_SCHEMA.md
```

Do **not** use `git diff main...HEAD` — it shows unrelated merged-PR divergence, not this gate's
change. Also run `git status --porcelain` to confirm the tree is clean.

The implementer's own account is at
`.agent-work/issue-467-trip-semantics/crew-handoffs/g2-implementer-result.md` and the mutation log
at `.agent-work/issue-467-trip-semantics/g2-mutation-log.md`. **Read them, then attack them** — your
job is to falsify the claims, not to confirm them.

## Task Statement

The implementer's contract is
`.agent-work/issue-467-trip-semantics/crew-handoffs/g2-implementer-handoff.md`. Read it in full;
it is what the work is judged against.

## The trap that invalidates the obvious check — read before you write a single check

**#431 is an instruction-conformance defect, not a mechanical deadlock.** The `advance` was **never
blocked**: it was demonstrated at g1 running successfully at fill **0.162**, over the hard line of
0.15, because a pending refresh-request lifts the guard.

So any check of the form *"the advance succeeds after the fix"* passes in **both** worlds and
proves nothing. The same goes for *"a handoff artifact appeared"* — true by construction, green
either way. Judge the change on **what the agent is TOLD** and on **whether anyone BEGAN work while
over the line**.

Apply that standard to the implementer's tests too: a test of theirs that would pass against
unmodified source is not a guard, whatever its name.

## Close Criteria

Each becomes a review check. The first is the most important thing you will do in this review.

1. **The permanent DC2 guard is real.** `test_handoff_advance_at_hard_with_no_refresh_request_
   closes_and_freshens_digest` must pin its "not refused" half at `fill >= hard` with **NO pending
   refresh-request anywhere in the spine**. The implementer claims it asserts both preconditions
   inside the test body, via `_refresh_requests_anywhere(cl) == []` walking every task's evidence
   including superseded ones. **Verify that claim by reading the test.** If the fixture has a
   pending request, the test passes on both sides of the fix and is worthless — that is a BLOCK.
2. **The DC2 test genuinely exercises both directions** — an advance carrying a handoff is not
   refused at/over hard with no pending request, AND beginning new work at/over hard IS refused.
3. **`--mechanical` at hard is genuinely refused**, so the digest cannot go stale after the fix.
   Confirm `why_exempt` is suspended too, and that the suspension actually **records** a why rather
   than only demanding one — a demand that records nothing reproduces #431 after the fix.
4. **`reopen` is guarded and `resume` is NOT.** Both directions, live.
5. **EVERY mutation in the log turns its NAMED test red, and the failure counts are stated.**
   **Re-run at least two yourself** — pick ones you consider most likely to be overclaimed, not the
   first two. A mutation that reddens forty unrelated tests does not demonstrate that its test
   defends that branch.
6. **The fail-safe on a `None` reading survives** at the new guard sites (and for surveys).
7. **Verb return strings are unchanged.** The implementer claims every direct `E.advance(...)` call
   in the suite is byte-identical.
8. **The count of re-aimed existing tests is stated with a per-test reason.** Claim: 6 re-aimed, 0
   deleted, 3 renamed and 3 body-only. Confirm nothing was deleted to make a red go away.
9. **`docs/CHECKLIST_SCHEMA.md` describes shipped behaviour**, not the old refusal.

## Two claims I want you to attack specifically

- **M11.** The implementer states it could **not** produce a narrow mutation for the None-reading
  fail-safe (delete → 59 failures, invert → 47, swap → null mutation) and therefore explicitly does
  **not** claim specificity for it. I read that as honest rather than evasive. **Test that reading.**
  Is a narrow mutation genuinely unavailable, or was one available and missed? Either answer is
  useful; only a wrong one is a problem. If genuinely unavailable, say so plainly — do not treat an
  honestly-declared limitation as a defect.
- **The −1 subtest.** Suite is `1815 passed, 2 skipped, 682 subtests` against a baseline of
  `1793 / 2 / 683`. `+22` is the new tests. The `−1` was bisected to
  `test_context_manifest.py::test_rev_equals_git_rev_parse_head_for_tracked_clean_files`, which
  filters to files clean in the working tree — and `scripts/checklist_engine.py` was dirty at
  measurement time. **The gate is now committed, so re-measure it yourself.** If the subtest count
  is back to 683, the explanation holds. If it is not, that is a real finding.

## Allowed Scope

The implementer was permitted `scripts/checklist_engine.py` (named functions only),
`tests/test_checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`'s Trip section, and
`.agent-work/issue-467-trip-semantics/g2-mutation-log.md`. Work-area run artifacts under
`.agent-work/issue-467-trip-semantics/` (plan, journal, evidence, context) are expected in the
commit.

## Specific Exclusions — flag if touched

- **`resume` must NOT be guarded** (`scripts/checklist_engine.py:1999`).
- **`gauge_reader._PROFILES`** must be unchanged.
- **No validation added to `attach`** — a dangling `why_ref` already fails CLOSED.
- **No mid-gate handoff channel built.**
- **No existing Trip test deleted.**

## Constraints the Implementation Must Respect

- **Pure verbs.** `start`, `reopen`, `advance` return values unchanged; the bands ride the CLI
  boundary in `dispatch`.
- **A refusal must not mutate state and must not refresh the lease.** The existing ordering comment
  at `:2681-2683` says a refused verb raises before the liveness stamp. Confirm the new guard
  preserves that.
- **FIXED, not renegotiable:** a missing or failed reading never forces a handoff; HARD means "wrap
  up", never "you are unsafe"; the reading is PUSHED by the engine, never fetched by the agent.
  Judge the new advisory text (d) against that last group — this is a prose check, and suite-green
  is not assurance for it. Read the shipped strings.
- **`refresh-request` payloads stay POINTERS ONLY**: `{seam, why_ref}`, no copies of state.

## Map Anchors (inbound)

- **Structural:** `scripts/checklist_engine.py` — `dispatch` (:2649), `_trip_hard_gate` (:1439),
  `_trip_advisory` (:1399), `_refresh_attach_hint` (:1254), `has_pending_refresh_request` (:1146),
  `start` (:1821), `reopen` (:2058), `resume` (:1999), `advance` (:1854, why/mechanical branch
  :1899), `_latest_why_record` (:1121). Line numbers are pre-change.
- **Capability:** Trip two-band gate policy, HARD band — enforcement point moves; SOFT unchanged.
- **Constraints/assumptions:** `constraint:fail-safe-on-no-reading`, `constraint:gated-only`,
  `constraint:gate-boundaries-only`, `constraint:pure-verbs`.
- **Decision anchors:**
  - `decision:hard-guards-begin-not-close` — HARD refuses `start` and `reopen`, never `advance`.
    `@grade: settled/measured · leans g2-implement,g2-review,g4-implement`
  - `decision:no-silent-close-at-hard` — at/over hard, `--mechanical` refused and `why_exempt`
    suspended. `@grade: settled/measured · leans g2-implement`

  Both are `settled/measured`. A contradiction you find is **not** yours to revise and **not** the
  implementer's — flag it as a decision candidate and return it.
- **Evidence expectations:** `claim:dc2-two-way`, `claim:dc3-digest-fresh`.
- **Map confidence flags:** none.

## Evidence Produced

From the IMPLEMENTER_RESULT, all of which you re-verify rather than accept:

- Permanent DC2 guard: RED against unmodified source (`5 failed, 6 passed, 349 deselected`), GREEN
  after (`25 passed, 346 deselected`). RED runs saved at
  `.agent-work/issue-467-trip-semantics/evidence/g2-m{1,2,3}-RED.txt`.
- Mutation log, 12 mutations with total counts: M1 7, M2 1, M3 6, M4 3, M5 3, M6 3, M7 2, M8 5,
  M9 2, M10 1, M12 1, M11 declared a limitation.
- The `--mechanical`-at-hard refusal message, asserted by equality.
- Wiring grep: 3 production call sites (`:1514`, `:2770`, `:2806`), zero inert symbols. **Re-run
  this** — a guard nothing calls is exactly the failure this gate exists to fix.
- Closeout selector: `25 collected, exit 0` (was `0 collected, exit 5`).

The `g2-integrate` postconditions this feeds are **`g2-integrate.c1`** (full suite),
**`g2-integrate.c2`** (the `-k 'trip_begin or begin_work or handoff'` selector), and
**`g2-integrate.c3`** (your verdict artifact).

## Verification Commands

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'trip_begin or begin_work or handoff'
```

## Suggested Model Tier

**Stronger.** This changes a governor every constellation agent runs under, the obvious check
passes in both worlds, and the failure mode is silent.

## Stop Conditions

Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a
policy decision is required before a verdict is possible.

## Return Format

Return REVIEW_RESULT. **Your verdict must be exactly `APPROVE` or `BLOCK`**, on the **first line**
of your result, with the reasoning under it. No other verdict vocabulary — the engine matches on
that literal string, and a gate whose reviewer invents a third word cannot close.

`APPROVE` means **zero blocking findings**. Non-blocking findings are welcome and expected
alongside an APPROVE; report them, classified. If you have even one blocking finding, the verdict
is `BLOCK`.

Also state, on its own line, **`blocking_findings: <N>`** — I carry it into the engine payload for
audit.

Include: per-check findings against the nine close criteria (each classified blocking /
non-blocking), your independent re-runs with pasted output, the two claims you were asked to
attack, blockers, anything you could not verify and why, out-of-scope observations, and workflow
feedback (what in this handoff or the workflow made the review harder than it needed to be).

Write your result to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g2-reviewer-result.md`.
