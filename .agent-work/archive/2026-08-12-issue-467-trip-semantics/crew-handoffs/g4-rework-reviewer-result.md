# Review Result — g4 REWORK re-review (attempt 2), issue #467

APPROVE
blocking_findings: 0

Survey driven through `scripts/checklist_engine.py` at
`.agent-work/issue-467-trip-semantics/g4-rework-review/review.json` (24 items, all recorded
pass, consolidated APPROVE, lease released). Fixtures built in a scratch temp directory
(`tempfile.mkdtemp()`), never in the Commander's leased `execute.json`/`spine.json`/`gauge.json`.

Engine pin confirmed before anything else: `git rev-parse HEAD` = `e33f9eb11a631927e1b4b4e3ec425b87a59f44e0`,
`git rev-parse HEAD:scripts/checklist_engine.py` = `c281cb68eaac65d1169dd6737a6a322728df98eb` — both
match the handoff exactly.

## The deciding question, answered by attack

**Is the new historical line itself a check that cannot fail — in either direction? No — it
discriminates, cannot be silenced while a gate is active, and does not gate any action, so it
cannot "fail to pass" either.**

### Two-world seam test (built independently — `probe_two_worlds.py`, real CLI subprocess, real
gauge.json stamped from the clock, no mocks in the advisory path)

```
=== WORLD H (compliant close, never over the line) ===
  trip_ledger on disk : None
  seam LIVE line      : None
  seam HISTORY line   : None

=== WORLD D (runaway: refused+released BEGIN, then closes the SAME way) ===
  trip_ledger on disk : [('tl-1', 'begin-refused'), ('tl-2', 'begin-released')]
  true total on disk  : 2
  seam LIVE line      : None
  seam HISTORY line   : "TRIP HISTORY: 2 begin(s) at/over the hard line are on the record across
                          this checklist's full history (latest: start g2 -> begin-released).
                          No close clears this line."

=== VERDICT ===
  seam output identical between H and D? False
  World D's seam output names the true total (2)? True
  World H seam is silent on both lines (expected)? True
```

B1's own shape — green-in-both-worlds at the seam — does not recur. The LIVE line is correctly
absent in World D (its keying is untouched, confirmed separately below); the HISTORICAL line is
what makes the two worlds differ, exactly as designed.

### Can it be silenced? (`probe_silencing.py`, 9 attack shapes against a real armed runaway)

| attempt | result |
|---|---|
| `reopen` the just-closed runaway gate | **REFUSED** (reopen is itself a HARD-guarded verb at/over hard) — and the refusal *adds* a 3rd ledger entry, so the historical count grows, not shrinks |
| `block` + `resume` | succeeds; HIST unchanged |
| `skip` | succeeds; HIST unchanged |
| `advance --mechanical` | **REFUSED** by no-silent-close; gate stays in-progress; HIST unchanged |
| `amend --delta` (retext-check) | refused for an unrelated schema reason; amend ops never touch `trip_ledger` regardless of outcome |
| `attach` arbitrary evidence after close | succeeds; HIST unchanged |
| `--dry-run` | not a recognized CLI flag at all (usage error) |
| a `why_exempt` gate with no `why_trail` ever | live selector *also* matches (`None==None`, documented behavior) so both lines render; `--mechanical` is still refused at/over hard regardless of `why_exempt`, so nothing closes and HIST is untouched |
| every remaining gate closed (no active gate left) | **both** lines go silent via `current` — see below, filed separately, not a B1 recurrence |

In every in-scope attempt, `trip_ledger` is genuinely append-only (confirmed by reading
`_append_trip_entry` and `reopen`'s cascade code: neither mutates nor removes an entry) and no
legal verb sequence cleared or reduced the historical line while a gate remained active.

The one case that *does* silence both lines — closing every remaining gate so
`active_id(cl)` is `None` — is pre-existing `_trip_advisory` behavior (`gate is None` → `""`
immediately), unrelated to this diff, and does not delete the underlying `trip_ledger` data; it
remains directly readable (as this review does). Filed as **triage candidate tc2**, not a B1
recurrence, since B1 was specifically about the record vanishing while a *next reader is still
being advised about an active gate*.

### Can it fail to pass? (the mirror defect)

The live line's behavior is unchanged (see keying-untouched below): a genuinely fresh
understanding still reads the live line as absent, so close criterion (b) still holds. The
historical line is worded in explicit historical framing ("are on the record across this
checklist's **full history**") distinct from the live line's present-tense framing ("are on the
record **under this understanding**"), and it gates nothing mechanically — no verb is refused, no
postcondition depends on it, it is pure advisory text on the read-only `current` path. It is an
immutable audit fact by design, not a per-understanding compliance gate that could become "a
permanent red badge no correct behaviour can ever clear" in the mechanism sense the handoff
warned against.

### Is the keying untouched?

`git diff 28dd434c..e33f9eb1 -- scripts/checklist_engine.py`: the hunk touching
`begin_over_line_records` shows **only** its unchanged `def` line as context; every added line
sits inside the new `begin_over_line_records_historical` function that follows it. Read the live
selector's current full body directly — identical to pre-rework: still keyed to
`_latest_why_record`, same loop, same filter. Zero change inside `begin_over_line_records`,
confirmed by reading, not by taking the claim.

## Two Admiral-named checks — verified by mutation, both pass

**A. The pinned test must DISCRIMINATE, not merely pass.** Dead-coded
`begin_over_line_records_historical` to `return []` (reviewer mutation; reverted after, tree
confirmed clean via `git diff --quiet`). `pytest -k "historical or test_live_line_is_absent"`:
**9 failed / 3 passed / 6 subtests passed**, including
`test_live_line_is_absent_after_the_offenders_own_close_but_the_historical_line_still_names_it`
(the renamed, corrected pinned test) and
`test_historical_line_renders_at_the_seam_even_when_the_live_line_is_absent`. The corrected test
is not still certifying the defect — it goes red when the fix is removed.

**B. Mutation-test the new line at the seam, not just a unit test.** With the same dead-code
mutation still in place, re-ran my own `probe_two_worlds.py` (subprocess CLI, no mocks): "seam
output identical between H and D" flipped to **True**, "D names the true total" flipped to
**False** — the **seam measurement itself** goes red, not merely a pytest assertion. Reverted;
tree confirmed clean.

## Mutations N20–N22, re-authored from source (not the implementer's driver)

Each mutation applied by hand-editing the source, tested, then reverted with
`git diff --quiet` confirmed clean before the next:

- **N20** (dead-code historical selector to `[]`): `pytest -k historical` → **9 failed / 3 passed
  / 6 subtests**. My seam probe also failed to discriminate under this mutation.
- **N21** (drop `historical_note` from the already-requested HARD sub-branch, line 1539):
  `pytest -k already_requested` → **1 failed**
  (`test_compliance_line_also_rides_the_already_requested_hard_advisory`), matching the log's
  named test.
- **N22** (key the historical selector to `_latest_why_record`, re-creating B1 exactly):
  `pytest -k "historical or test_live_line_is_absent"` → **4 failed / 6 passed / 8 subtests**,
  matching the log's stated total. Independently, my own seam probe *also* re-detects B1's exact
  shape under N22 (seam identical=True, true-total-named=False) — the mutation that would
  silently reintroduce B1 is caught both by unit tests and by an independent seam measurement.

## Also verified, by attack

- **One computation, one render site (criterion 6).** `grep -rn 'TRIP LEDGER' scripts/` and
  `grep -rn 'TRIP HISTORY' scripts/` each find exactly one source-level match (the only other hit
  in each case is the compiled `__pycache__` binary, not a second source site). Both facts
  computed once above the two HARD sub-branch returns, appended via `+` at both.
- **Purity and read-only path (criterion 8).** Direct reading of the new selector's body: only
  `cl.get("trip_ledger", []) or []`, `isinstance`/`.get`, no subprocess/gauge/clock/I/O. Ran it
  directly against `None`, `"not-a-list"`, `{"x": 1}`, and a list mixing non-dict entries with a
  valid one — degrades to `[]` or skips non-dicts in every case, never raises.
- **Engine-written-only (criterion 3).** Independent `ast` call-graph audit (my own script):
  `_append_trip_entry`'s only caller is `_trip_hard_gate`; `_trip_hard_gate`'s only caller is
  `dispatch`; `dispatch`'s only caller is `main`. `begin_over_line_records_historical`'s only
  caller is `_trip_advisory` — a reader, never reachable from a CLI verb.
- **Pre-existing HARD strings unaltered (criterion 5).** `_expected_hard(...)` /
  `_expected_hard_already_requested(...)` in the test file are the base sentences with no notes;
  every defective-world expectation is literally `_expected_hard(...) + _expected_note(...)` —
  concatenation, pinned by `assertEqual` throughout, not `assertIn`. The healthy string is a
  strict prefix of the defective one by construction.
- **The sentence is actually true now.** "Closing THIS gate clears this line; the line below, if
  present, is not." — measured true (live goes `None`, historical persists after the offender's
  own close). "No close clears this line." — measured true against all 9 silencing shapes above.
- **The declared limit reads like the other three.** `docs/CHECKLIST_SCHEMA.md`'s "The fourth: the
  live signal goes silent at exactly the close it mandates" states the mechanism plainly and names
  the mitigation without overclaiming it as a complete substitute — as plain and unhedged as the
  first three, no more, no less.
- **Artifact corrections are honest.** `g4-mutation-log.md`'s N17 correction is visibly labeled
  and technically verified against the source (`live_note`/`historical_note` are locals scoped
  inside `if fill >= hard:`, undefined in the sibling SOFT branch — the logged mutation really is
  unreachable as originally written). `CHECK_THAT_CANNOT_FAIL.md`'s correction states the false
  claim verbatim ("every one of this gate's 25 tests...") and the true count (24 of 25), naming
  the exception and its fix. Neither is silently rewritten.
- **The implementer's declared discrepancies.** Full-suite re-measurement (below) landed at
  **829 subtests**, not the implementer's reported 828 — one *more*, which is exactly **+8** over
  the pre-rework baseline of 821, matching the implementer's own stated count of +8 and not their
  reported +7. This independently confirms the dirty-tree hypothesis:
  `test_context_manifest.py::test_rev_equals_git_rev_parse_head_for_tracked_clean_files` filters
  its `subTest` targets to files with an empty `git status --porcelain`, so its subtest count is
  mechanically sensitive to exactly which files are dirty at run time — verified by reading the
  test source, not assumed. Self-reference substring bug: grepped the shipped `live_note`/
  `historical_note` text for the substring `"TRIP HISTORY"` inside the *live* line's own wording —
  absent, confirming the fix.

## Re-measured evidence (not accepted from the report)

- **Full suite:** `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`, redirected to a file with
  `echo $?` appended to the same file (real exit code, not a piped one):
  **`1867 passed, 2 skipped, 829 subtests passed in 461.90s`**, `REAL_EXIT_CODE:0`.
- **Targeted selector:** `python -m pytest -q tests/test_checklist_engine.py -k 'ledger or
  compliance or trip_log'` → **`34 passed, 384 deselected, 21 subtests passed`**, real exit 0 —
  collects and passes, not the empty-collection pytest-exit-5 false green.
- Grepped both output files for `SUBFAILED` and `FAILED`: zero matches in either.
- Re-ran `.agent-work/issue-467-trip-semantics/g4-review/probe_clearing.py` (first reviewer's own
  probe, carrying its declared mechanical edit). The edit is purely additive — two new print lines
  reading the historical selector/line — and does not touch any prior assertion or logic; honestly
  commented in the source explaining why. Its own step-by-step output independently reproduces the
  seam finding: after the offender's own close, `RENDERED LINE` (live) is `None` while
  `RENDERED HISTORY` persists naming the true count. The edit strengthens, not weakens, the
  probe's detection.

## Per-item findings against the criteria (r0–r6, d1–d17)

All 24 survey items recorded `pass`; full findings text is in
`.agent-work/issue-467-trip-semantics/g4-rework-review/review.json`. Summary:

- **r0–r5** (context, handoff compliance, scope, evidence, quality, reconciliation): pass. Scope
  held exactly to the allowed file set; `begin_over_line_records`'s keying — the one thing ruled
  out of the fix space — is untouched (confirmed by diff read, not claim).
- **r6-fowler**: pass. 12 baseline smells walked (`fowler-pass.json`,
  `verify_fowler_pass.py` exit 0). **duplicated-code**: flagged (see non-blocking findings).
  **primitive-obsession**: overridden — the module has no enum tier anywhere and uses plain
  string literals pervasively for verb/status/outcome values (grep-confirmed, 4 occurrences of the
  outcome tuple across the file); `global-crew.md`'s naming-convention rule wins. All other 10
  smells: absent.
- **d1–d17**: pass, detailed above.

## Non-blocking findings

- **Duplicated code** between `begin_over_line_records` and `begin_over_line_records_historical`
  — the historical selector's loop is a near-total textual clone of the live one minus the
  `why_ref` filter. A shared filter-and-collect helper would remove it. Not blocking: this is a
  quality question, not a correctness defect (both selectors independently proven correct by
  mutation testing above); the Admiral ruled this rework's fix space narrow; and the two loops'
  textual independence is arguably deliberate defense-in-depth against a future edit silently
  coupling the two signals — exactly the failure shape N22 exists to catch. Filed as **tc1**.

## Triage candidates

- **tc1** — consolidate the two selectors' shared filter loop into one helper (pure
  simplification, no behavior change), separately scoped from this rework.
- **tc2** — once a checklist has no active gate at all (fully DONE), `current`'s trip advisory
  goes silent for both lines by design (pre-existing, unrelated to this diff). The `trip_ledger`
  data is never deleted and remains directly readable, but no verb currently surfaces it at
  closeout. Worth a Commander/Admiral-tier decision: should an archive/closeout gate surface
  `trip_ledger` history, or is "read the JSON directly" the intended audit path?

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: the handoff's B1 recap, deciding question, two
  named Admiral checks, and the "also verify" list mapped cleanly onto a driveable survey with no
  ambiguity about what "attack" meant in each case.
- **Context rediscovered:** the exact spine/gauge fixture shape (gate dict fields, `gauge.json`
  schema) wasn't itself in the handoff — I found it by reading the first review's
  `probe_clearing.py`, which the handoff did point me at for a different reason (evidence
  re-measurement). Worked out fine since that file was already in scope to re-run, but a
  one-line pointer to it as "also the reference fixture shape for building your own probes"
  would have saved a beat.
- **Instructions improvised around:** the full pytest suite took ~7.5 minutes and the Bash tool's
  default 2-minute timeout killed the first attempt; re-ran it via a backgrounded command and
  polled for completion instead. Not a handoff gap, just worth noting for future full-suite
  evidence asks on this repo.
- **What would have made this easier:** none beyond the above — the handoff's own listed traps
  (SUBFAILED vs FAILED, clock skew, CRLF, pytest exit 5) were all real and all worth having named
  up front.

## Return status
complete
