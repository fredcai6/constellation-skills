APPROVE

blocking_findings: 0

# Review Result — g2-review, issue #467, epic #418

Reviewed commit `38f0b448` on `epic-418/a2-467-trip-semantics`. Survey driven end to end at
`.agent-work/issue-467-trip-semantics/g2-review/review.json` (16 checks: the 7 template items plus
one per close criterion), engine lease `g2-review-rev467`, consolidated `APPROVE findings=0`.
Fowler-pass record at `.agent-work/issue-467-trip-semantics/g2-review/fowler-pass.json`, rail exit 0.

I attacked rather than confirmed. The single most useful thing I did was not re-reading the
implementer's evidence — it was **running the new test file against the pre-change engine in an
isolated tree**, which is the direct test of "would this test pass in both worlds".

---

## The falsification run — 16 of 25 selector tests are red against unmodified source

Built a scratch tree with `git show 38f0b448^:scripts/checklist_engine.py` (verified: 154 changed
lines vs HEAD, `if v == "advance": _trip_hard_gate(...)` present at :2679-2680) and the **new**
test file byte-identical to HEAD.

```
$ cd /tmp/rev467_probe_old && python -m pytest -q tests/test_checklist_engine.py \
      -k 'trip_begin or begin_work or handoff'
...
FAILED ...TripTwoBandGatePolicy::test_hard_handoff_close_needs_a_why_even_with_a_refresh_request_pending
FAILED ...TripTwoBandGatePolicy::test_hard_refuses_begin_work_at_and_above_hard_without_refresh
FAILED ...TripHardGuardsBeginNotClose::test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest
FAILED ...TripHardGuardsBeginNotClose::test_handoff_digest_names_the_understanding_written_at_the_tripping_gate
FAILED ...TripHardGuardsBeginNotClose::test_handoff_hard_advisory_reads_as_a_changed_instruction
FAILED ...TripHardGuardsBeginNotClose::test_handoff_hard_advisory_with_refresh_already_requested_reads_as_an_instruction
FAILED ...TripHardGuardsBeginNotClose::test_handoff_mechanical_close_refused_at_hard
FAILED ...TripHardGuardsBeginNotClose::test_handoff_refresh_hint_carries_the_concrete_why_id
FAILED ...TripHardGuardsBeginNotClose::test_handoff_unmet_postconditions_still_refuse_before_the_why_demand
FAILED ...TripHardGuardsBeginNotClose::test_handoff_why_exempt_is_suspended_at_hard
FAILED ...TripHardGuardsBeginNotClose::test_trip_begin_refusal_names_the_concrete_why_id
FAILED ...TripHardGuardsBeginNotClose::test_trip_begin_reopen_refused_at_hard_without_refresh
FAILED ...TripHardGuardsBeginNotClose::test_trip_begin_stale_why_ref_does_not_release_begin_work
FAILED ...TripHardGuardsBeginNotClose::test_trip_begin_start_refused_at_and_above_hard_without_refresh
FAILED ...TripRealGaugeFileWiring::test_fresh_hard_gauge_sibling_of_spine_refuses_begin_work_then_passes_with_refresh
FAILED ...TripRealGaugeFileWiring::test_handoff_fresh_hard_gauge_never_refuses_the_closing_advance
16 failed, 9 passed, 346 deselected in 4.55s
```

Red for the right reasons, sampled: the begin-work tests fail with `AssertionError: EngineError not
raised` (the guard did not exist); the no-silent-close tests fail because the old engine raises the
old `advancing is blocked` message instead; the real-file DC2 twin fails with `AssertionError: 1 != 0`.

The **9 that stay green** are all declared falsifiable-half or fail-safe companions pinning
*unchanged* behaviour — `mechanical_close_still_allowed_below_hard`, `no_silent_close_never_fires_on_a_none_reading`,
`none_reading_never_refuses_begin_work`, `no_base_dir_...`, `survey_never_refuses_begin_work`,
`start_allowed_just_below_hard`, `start_released_by_a_matching_refresh_request`,
`resume_is_not_guarded_at_hard`, `hard_advisory_rides_current_at_the_cli_boundary`. **None is dressed
as a guard for new behaviour**, and the implementer disclosed exactly this in its workflow feedback.
Applying the handoff's own standard: no test of theirs that would pass against unmodified source is
being offered as a guard.

---

## Per-check findings against the nine close criteria

### CC1 — the permanent DC2 guard is real · **PASS** · non-blocking
This was the decisive check and the claim is **true**. Verified three independent ways.

1. **Read the test** (`tests/test_checklist_engine.py:3497-3517`). Both preconditions are asserted
   inside the body, not merely described: line 3507 `assertEqual(_refresh_requests_anywhere(cl), [])`
   before the advance, line 3517 the same after, and line 3510
   `assertGreaterEqual(E._read_gauge(Path(".")).fill_fraction, self.hard)` inside the patch context.
   The fixture `_three_gates()` is freshly constructed with empty `evidence` on every gate.
2. **Audited the helper against the predicate it must dominate.** `_refresh_requests_anywhere`
   (:3234) walks every task's evidence and does **not** filter `superseded`.
   `has_pending_refresh_request` (engine :1155) walks the **same** task-evidence domain and **does**
   skip superseded. The helper is therefore a strict superset of everything that could lift the
   guard — it cannot miss a lifting request. This mattered: a helper narrower than the engine
   predicate would have made the assertion decorative.
3. **Falsified it.** The test is red against the pre-change engine (run above).

A second, independent DC2 guard exists at the real-file tier —
`TripRealGaugeFileWiring::test_handoff_fresh_hard_gauge_never_refuses_the_closing_advance` — driving
a real `gauge.json` through `main()` and asserting rc 0, `complete`, the fresh digest, and no
refresh-request anywhere. It is also red pre-change. Neither depends on the disposable RED repro.

### CC2 — the DC2 test exercises both directions · **PASS** · non-blocking
Not-refused half: CC1 above, plus PROBE D below. Refused half:
`test_trip_begin_start_refused_at_and_above_hard_without_refresh` (at hard **and** above, asserting
`assertEqual(cl, before)`) and `test_trip_begin_reopen_refused_at_hard_without_refresh`; both red
pre-change with `EngineError not raised`. My PROBE D closes the loop the tests do not: after the
tripped agent closes its own gate, its attempt to **begin** the next gate while still over the line
is refused. That answers the DC6 observable — *did anyone begin work over the line* — live, rather
than by construction.

### CC3 — `--mechanical` refused, `why_exempt` suspended, and it RECORDS · **PASS** · non-blocking
The half that matters is that suspension *writes*, not that it *demands*. Confirmed live (PROBE B,
real `gauge.json` at fill 0.20, all gates `why_exempt=True`):

```
exempt gate + silence at hard: rc=1
REFUSED: g1: context is at/over the hard limit, so this gate cannot be closed silently — a
mechanical or why-less close records no understanding, and the next agent would cold-start from a
digest written before your work. Closing the gate is NOT refused; only the silence is.
Run: advance g1 --why "<understanding>"
exempt gate + --why at hard: rc=0, g1=complete
why_trail: [{"id": "w-1", "gate": "g1", "why": "REVIEWER PROBE understanding at g1",
             "mechanical": false, "ts": "2026-08-08T12:44:14.291739+00:00"}]
DIGEST: 'REVIEWER PROBE understanding at g1'
==> RECORDED, not merely demanded: True
CONTROL just below hard: rc=0, why_trail=None
```

The control matters: the rule is gauge-scoped, not always-on. Ordering is intact —
`test_handoff_unmet_postconditions_still_refuse_before_the_why_demand` shows a failing postcondition
still yields `g1: postconditions unmet ['c1']` at hard, so the why demand cannot buy past unfinished
work.

### CC4 — `reopen` guarded, `resume` NOT · **PASS** · non-blocking
Proved live through `main()` with a real gauge at fill 0.20, not by reading the diff:

```
reopen a COMPLETE gate over the line: rc=1, g1=complete
  REFUSED: g1: context at 20% is at/over the hard limit, so this is not the moment to BEGIN work
  here — finish and close the gate you are already in, then request a refresh...
start a PENDING gate over the line:  rc=1, g2=pending
resume a BLOCKED gate over the line: rc=0, g1=in-progress
  out: g1 resumed -> in-progress (blocker resolved: ruling arrived)
```

Structurally: `TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}`, and the engine diff contains no
`+def resume` — the body is byte-unchanged.

### CC5 — every mutation reddens its NAMED test, counts stated · **PASS** · non-blocking
See the re-runs section below. Four re-run, zero discrepancies.

### CC6 — the `None`-reading fail-safe survives · **PASS** · non-blocking
The fail-safe is now structural rather than duplicated: both bands read it from the single
`_trip_hard_band_reading` predicate, which returns `None` for a non-`GATED` checklist and for a
`None` reading, and every caller reads `None` as "band inactive". Four named tests cover it,
including `test_handoff_no_silent_close_never_fires_on_a_none_reading` — the one that matters most,
since a missing reading must not conjure a `--why` requirement onto an exempt gate. Specificity is
not claimed for the `None` branch and I confirmed it cannot be (see M11). `M10` does pin the survey
half narrowly at 1 failure.

### CC7 — verb return strings unchanged · **PASS** · non-blocking
Verified by command. Every changed line containing `return` in the engine diff:

```
-            return (f"\nCONTEXT {fill:.0%} (>= hard): refresh already requested for "
-        return (f"\nCONTEXT {fill:.0%} (>= hard): `advance` is BLOCKED until you "
+            return (f"\nCONTEXT {fill:.0%} (>= hard): your instruction has changed, and "
+        return (f"\nCONTEXT {fill:.0%} (>= hard): your instruction has changed. You have "
-        return / +        return None   (x2, the new predicate)
+        return None / +    return reading
```

All inside `_trip_advisory` and `_trip_hard_band_reading` — helpers, not verbs. **Zero** changed
return strings in `start`, `advance`, `reopen`, `resume`. No `+def start` / `+def reopen` /
`+def resume` in the diff; `advance`'s signature changed only by gaining `require_why: bool = False`.
The 1815-passing suite with the pre-existing exact-equality tests untouched is the behavioural
corroboration.

### CC8 — re-aimed count with per-test reason, nothing deleted · **PASS** · non-blocking
The claim (6 re-aimed, 0 deleted, 3 renamed, 3 body-only) is **exactly** right, verified
mechanically rather than by reading the table.

```
old unique test names: 348; new: 370
--- in OLD, ABSENT in NEW (candidate DELETIONS) ---
test_fresh_hard_gauge_sibling_of_spine_refuses_then_passes_with_refresh
test_hard_passes_once_refresh_request_exists
test_hard_refuses_at_and_above_hard_without_refresh
--- names ADDED: 25 ---

pre-existing tests kept under the SAME NAME whose BODY changed: 3
    test_hard_advisory_on_current_points_at_attach
    test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases
    test_hard_refusal_leaves_state_unmutated
```

Each of the 3 "missing" names maps to a rename present in the new set. 25 added − 3 renames = 22 new
tests, reconciling `+22` exactly. **Nothing was deleted.** The re-aims are genuine fixes, not
collateral; the strongest case is #3, whose old claim ("HARD forces until a request exists, then
advance passes") would now be green in **both** worlds and was correctly replaced with a live
question rather than left as a decorative pass.

### CC9 — `docs/CHECKLIST_SCHEMA.md` describes shipped behaviour · **PASS** · one non-blocking nit
Every claim in the new Trip section and the three verb rows checks out against source. The prose
check against the FIXED group — read from the shipped strings, not the tests — the HARD advisory now
reads:

> `CONTEXT 20% (>= hard): your instruction has changed. You have taken this as far as this context
> can carry it — now close THIS gate carrying your handoff (`advance g2 --why "<understanding>"`),
> request a refresh, and stop. A fresh agent picks up from your DIGEST; do not begin work at another
> gate. Request the refresh with: attach g2 --type refresh-request --field seam=g2 --field why_ref=w-1`

That is a changed instruction, not an alarm: no alarm word, no claim that `advance` is blocked, and
it names the one thing to do plus the concrete why-id. A missing reading still forces nothing, and
the reading is pushed by the engine on the verb, never fetched.

**NON-BLOCKING NIT.** The new sentence *"A refusal is raised before the liveness stamp, so it never
refreshes the lease and never mutates state"* is true of the `start`/`reopen` guard but the
"never mutates state" half is not strictly true of the no-silent-close refusal inside `advance` — see
finding NB4. Suggest scoping the sentence to the pre-verb guard.

---

## Independent re-runs

### Full suite (re-measured post-commit)

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
1815 passed, 2 skipped, 683 subtests passed in 325.40s (0:05:25)
EXIT=0
$ grep -E '^FAILED' /tmp/rev467_full.txt | sed 's/::.*//' | sort | uniq -c
(empty)
```

### Closeout selector

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py \
      -k 'trip_begin or begin_work or handoff'
25 passed, 346 deselected in 3.25s
EXIT=0
```

### Mutation re-runs — four, chosen as the most falsifiable

Not the first two in the log. I picked **M3** (the deadlock restored — if its count or named test
were wrong, the permanent guard's whole mutation defence collapses), **M5** (the *only* evidence the
no-silent-close rule is wired to the gauge rather than shipped inert), **M2** (the strongest
specificity claim in the log: exactly 1), and **M8** (the one whose blast radius is explained away as
"red for the correct reason"). Clean scratch tree, baseline reproduced exactly at **416 passed, 30
subtests passed**; each anchor asserted unique before applying; restored from a pristine copy and
diffed `IDENTICAL` afterwards.

```
=== M2 :: TRIP_HARD_GUARDED_VERBS = {"start", "reopen"} -> {"start"}
SUMMARY: 1 failed, 415 passed, 30 subtests passed
FAILED (1):
    TripHardGuardsBeginNotClose::test_trip_begin_reopen_refused_at_hard_without_refresh

=== M3 :: -> {"start", "reopen", "advance"}
SUMMARY: 6 failed, 410 passed, 30 subtests passed
FAILED (6):
    TripHardGuardsBeginNotClose::test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest
    TripHardGuardsBeginNotClose::test_handoff_digest_names_the_understanding_written_at_the_tripping_gate
    TripHardGuardsBeginNotClose::test_handoff_mechanical_close_refused_at_hard
    TripHardGuardsBeginNotClose::test_handoff_unmet_postconditions_still_refuse_before_the_why_demand
    TripHardGuardsBeginNotClose::test_handoff_why_exempt_is_suspended_at_hard
    TripRealGaugeFileWiring::test_handoff_fresh_hard_gauge_never_refuses_the_closing_advance

=== M5 :: require_why=_trip_hard_band_reading(cl, base_dir) is not None) -> require_why=False)
SUMMARY: 3 failed, 413 passed, 30 subtests passed
FAILED (3):
    TripHardGuardsBeginNotClose::test_handoff_mechanical_close_refused_at_hard
    TripHardGuardsBeginNotClose::test_handoff_why_exempt_is_suspended_at_hard
    TripTwoBandGatePolicy::test_hard_handoff_close_needs_a_why_even_with_a_refresh_request_pending

=== M8 :: if reading.fill_fraction < hard: return None  (deleted)
SUMMARY: 5 failed, 411 passed, 30 subtests passed
FAILED (5):
    TripHardGuardsBeginNotClose::test_handoff_mechanical_close_still_allowed_below_hard
    TripHardGuardsBeginNotClose::test_trip_begin_start_allowed_just_below_hard
    TripRealGaugeFileWiring::test_fresh_soft_gauge_advises_on_current_but_advance_passes
    TripTwoBandGatePolicy::test_hard_never_refuses_below_hard
    TripTwoBandGatePolicy::test_soft_never_forces_advance

=== restoration check ===
IDENTICAL
```

**Zero discrepancies.** Every count matches the log, and so does every failure *set* — not just the
totals. M8's blast radius is genuinely the guard's own surface: the three "unrelated" SOFT-band tests
are red because with the threshold gone the SOFT band is swallowed by HARD, exactly as logged.

---

## The two claims I was asked to attack

### M11 — is a narrow mutation genuinely unavailable? · **The declared limitation is HONEST and it holds.**

First I reproduced the implementer's two numbers, then I built two narrower candidates it did **not**
try:

```
=== M11b  (their run: delete `if reading is None: return None` in _trip_hard_band_reading)
SUMMARY: 59 failed, 360 passed          <- log says 59. matches.

=== M11c  (their run: invert to a synthetic fill_fraction=1.0 Reading)
SUMMARY: 47 failed, 372 passed          <- log says 47. matches.

=== M11d  (MINE: delete the SECOND None check, the one inside _trip_hard_gate — affects only
           the two guarded verbs, not advance)
SUMMARY: 37 failed, 382 passed

=== M11e  (MINE: require_why=_trip_hard_band_reading(...) is not None  ->  require_why=True,
           i.e. fail-unsafe on the advance side only)
SUMMARY: 23 failed, 393 passed
```

Both of mine are narrower and both still fail this gate's own standard — 37 and 23 unrelated
failures is squarely the "breaks forty unrelated tests" pattern the rule rejects. M11e is also not a
clean mutation of the `None` branch at all: forcing `require_why=True` simultaneously removes the
below-hard early-out, so it conflates M8 with M11.

The structural cause the implementer gives is correct and I confirmed it: nearly every fixture in the
suite runs with no gauge file, so `reading is None` is the path the whole suite takes, and any
mutation to it changes the behaviour of everything. **A narrow mutation is genuinely unavailable, not
available-and-missed.** Reporting it as a limitation rather than dressing a 47-failure run as a pass
is the right call, and I am recording it as honest, not as a defect. The one thing I would add to the
log: M11d is a slightly narrower demonstration than M11b and worth a line, but it changes nothing.

### The −1 subtest · **The explanation holds. Re-measured post-commit, the count is back to 683.**

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
1815 passed, 2 skipped, 683 subtests passed in 325.40s
```

Baseline was `1793 / 2 / 683`; the gate is now `1815 / 2 / 683`. `+22` is the new tests (25 added
names − 3 renames, reconciled independently under CC8) and the subtest count is **restored**, exactly
as predicted for a working-tree-cleanliness artifact. No real finding here.

---

## Adversarial probes (mine)

All four run end to end through `main()` against a **real** `gauge.json` on disk — no mocks, the path
a live agent actually takes. Sources: `%TEMP%/rev467_probe.py`, `rev467_probe2.py`, `rev467_probe3.py`.

**PROBE A/A2 — does the new in-`advance` refusal mutate state or refresh the lease?**
It found a state delta, so I ran a control against the pre-change engine before calling it anything:

```
[CONTROL] PRE-#467 engine, fill 0.02 (band inactive), why-less advance -> the OLD why-capture refusal
  rc=1   top-level keys changed: ['refusals', 'tasks']
    g1.evidence:       [] -> [{"id": "e-g1-1", "type": "command-output", ...}]
    g1.postconditions: satisfied False -> True
  engine_session.last_heartbeat refreshed by the refusal: False

[NEW] POST-#467 engine, fill 0.20, --mechanical -> the NEW no-silent-close refusal
  rc=1   top-level keys changed: ['refusals', 'tasks']   <- IDENTICAL SHAPE
    g1.evidence:       [] -> [{"id": "e-g1-1", "type": "command-output", ...}]
    g1.postconditions: satisfied False -> True
  engine_session.last_heartbeat refreshed by the refusal: False

[NEW] the BEGIN-work guard on `start` at fill 0.20
  rc=1   top-level keys changed: ['refusals']            <- zero task mutation
  engine_session.last_heartbeat refreshed by the refusal: False
```

Verdict: the lease is **never** refreshed by any of the three refusal paths — the constraint the
handoff actually names is honoured. The task-state delta on a refused `advance` is the engine's
long-standing behaviour for any refusal landing after the postcondition check, byte-identical between
the two engines, **not a #467 regression**. The pre-verb guard mutates nothing but a counter. Recorded
as NB4 only because the new doc sentence now spans both refusals.

**PROBE B** — `why_exempt` suspension records rather than merely demands (output under CC3).

**PROBE C** — `reopen` refused / `resume` allowed at the same fill (output under CC4).

**PROBE D — the whole of #431, side by side against the pre-change engine.** This is the probe I
would keep:

```
[POST-#467] what the agent is TOLD at the trip:
  CONTEXT 20% (>= hard): your instruction has changed. You have taken this as far as this context
  can carry it — now close THIS gate carrying your handoff (`advance g2 --why "<understanding>"`),
  request a refresh, and stop. A fresh agent picks up from your DIGEST; do not begin work at another
  gate. Request the refresh with: attach g2 --type refresh-request --field seam=g2 --field why_ref=w-1
  close the gate it is INSIDE: rc=0, g2=complete
  DIGEST handed to the fresh agent: 'AT-TRIP understanding written at g2'
  ==> FRESH, not the pre-trip one: True
  refresh-requests anywhere in the spine: 0   (0 => the guard was NEVER lifted)
  same agent tries to BEGIN g3 still over the line: rc=1  -- refused

[PRE-#467] the SAME moment:
  CONTEXT 20% (>= hard): `advance` is BLOCKED until you request a refresh.
  Run: attach g2 --type refresh-request --field seam=g2 --field why_ref=<why-id>  — then hand off.
  close the gate it is INSIDE: rc=1, g2=in-progress, DIGEST='PRE-TRIP understanding from g1'
```

Old: told it is blocked, handed a placeholder, gate stuck, digest stale. New: told what to do, handed
a working command, gate closes, digest fresh, and the *next* gate is still protected. That is the
issue, resolved, with the guard demonstrably never lifted.

**PROBE E — execute the advice, don't string-match it.** Inherited crew doctrine
(`global-crew.md`, Required evidence): *"generated advice/hint/recovery text → EXECUTE the advice and
assert it does not refuse, over fixtures parameterized on every dimension the advice depends on —
string-matching the rendered text is not evidence."* #467(d) **is** that failure mode, so I took the
string the engine actually emits, `shlex.split` it, and ran it, across both surfaces × both
why-record states:

```
A. REFUSAL  surface, live why-record : attach g2 ... --field why_ref=w-1        -> rc=0, released=True
B. ADVISORY surface, live why-record : attach g2 ... --field why_ref=w-1        -> rc=0, released=True
C. REFUSAL  surface, NO why-record   : attach g2 ... --field why_ref=<why-id>   -> rc=0, released=True
D. ADVISORY surface, NO why-record   : attach g2 ... --field why_ref=<why-id>   -> rc=0, released=True
```

Worth stating why C and D are safe rather than a surviving instance of the bug: the `<why-id>`
fallback is emitted **only** when there is no live why-record, which is exactly the condition under
which `wid is None` degrades #190's identity filter to a gate-only match. The placeholder cannot be a
silent no-op, because the only state that produces it is the state that disables the check it would
have failed. That is a coherent design, not a leftover.

---

## Non-blocking findings

**NB1 — `docs/agents/GLOSSARY.md:13` still teaches the belief #431 came from.** Confirmed by my own
blast-radius grep, independent of the implementer's:

```
| `trip` | — | ... | — | HARD blocks `advance` until the agent requests a context refresh. |
```

Now false at source, and it is the glossary every constellation agent reads. **Not blocking for this
gate**: it is outside the allowed scope (which named `docs/CHECKLIST_SCHEMA.md`'s Trip section only)
and the implementer correctly escalated instead of editing it — blocking would punish the right
behaviour. **Must-fix before epic #418 closes**; one line, one file. Commander decision. Flagged as
triage candidate `tc1`.

**NB2 — no test EXECUTES the emitted refresh hint; the guard for #467(d) is a string match.** The
shipped behaviour is correct (PROBE E), but `test_handoff_refresh_hint_carries_the_concrete_why_id`
and `test_trip_begin_refusal_names_the_concrete_why_id` assert on the *rendered text*. Both the
inherited doctrine and this repo's own CREW_CONTEXT ("Assert against behaviour, never against text
that describes it") point the same way. A future change that preserves the string and breaks the
execution stays green. Recommend one execute-the-hint test. Triage candidate `tc2`.

To be clear about a distinction I checked rather than assumed: the *advisory* tests asserting exact
prose are **not** an instance of this. There the text **is** the behaviour — #431 is an
instruction-conformance defect and what the agent is told is the observable. Asserting it by equality
is correct.

**NB3 — three Fowler smells flagged** (record: `.agent-work/issue-467-trip-semantics/g2-review/fowler-pass.json`,
rail exit 0; flagged `long-method`, `duplicated-code`, `shotgun-surgery`; overridden with logged
standards+reasons `data-clumps`, `primitive-obsession`, `long-parameter-list`, `divergent-change`,
`comments-as-deodorant`). The sharpest is **shotgun-surgery** and it is the root cause of NB1: the
single fact "HARD blocks `advance`" was mirrored in four hand-maintained places — the engine's Trip
module header, the schema's Trip section, the schema's verb rows, and the glossary. Three were
updated, one was missed. It will recur on the next Trip change unless the mirrored prose gets a
single source or a freshness check. Also: `advance()` is now ~110 lines with three mutually exclusive
recording branches, and `_append_why(cl, iid, why=why.strip(), mechanical=False)` now appears twice —
if a future change adds a field to the why record and updates one site, the failure mode is a
silently absent understanding, which is #431 again one level down.

**NB4 — one new doc sentence slightly overstates.** *"A refusal is raised before the liveness stamp,
so it never refreshes the lease and never mutates state."* The lease half is true of every refusal
path (measured). The "never mutates state" half is true of the pre-verb `start`/`reopen` guard but not
of the no-silent-close refusal inside `advance`, which lands after the postcondition check has stamped
`satisfied` and attached command-output. Pre-existing behaviour, not a regression — but the sentence
is new and now covers both. Suggest scoping it to the pre-verb guard.

**NB5 — `--from-child` advances at hard now require a `--why`.** A parent `advance --from-child` over
the line with no `--why` is refused by the new rule. I judge this intended (it is a close, and closes
must not be silent at hard), and it is consistent with the decision anchor — recording it so the
Commander sees it was considered rather than missed.

## Blockers

None.

## Out-of-scope observations

- **Triage candidate `tc3`** (raised by the implementer as instructed, confirmed by me in source): a
  gate that trips with **unmet** postconditions has nowhere to leave a mid-gate handoff note.
  `block --next` exists but `current` does not render its text. Carries no grade.
- The implementer's third observation — that the `--mechanical` refusal and the begin-work refusal
  both hang off the *reading*, so a run with a silent gauge gets neither protection — is correct and
  is the intended fail-safe direction. Worth an explicit decision somewhere now that HARD governs what
  gets **recorded**, not only what is refused.
- No contradiction found with either `settled/measured` decision anchor
  (`decision:hard-guards-begin-not-close`, `decision:no-silent-close-at-hard`). Both are implemented
  as given and neither was re-opened. The Map Impact notes match the diff line by line.

## Anything I could not verify

- **M1, M4, M6, M7, M9, M10, M12 were not re-run** (I re-ran M2/M3/M5/M8 plus M11b–e). Given four
  exact matches out of four on both counts and failure sets, I judge the log reliable; a Commander
  wanting full coverage can re-run the rest with `/tmp/rev467_mut/mutate.py`.
- **Nothing else.** Every claim in the implementer's result that I set out to check, I reproduced.

## Workflow feedback

- **The handoff was unusually good and the trap warning earned its place.** Stating three times that
  the obvious check passes in both worlds is what made me build the run-new-tests-against-old-engine
  probe instead of just reading the RED files. Keep it verbatim. The one addition I would make: the
  handoff told me to re-run *at least two* mutations but did not tell me the mutation log's own method
  (pristine copy, unique-anchor assertion, restore-and-diff) — I rebuilt that harness from the log's
  Method paragraph. A pointer to a re-runnable mutation script would have saved ~20 minutes.
- **The reviewer skill's installed engine bundle is STALE, and it cost the previous reviewer a
  waiver.** `r6-fowler`'s imperative says to fill the postcondition's `<fowler-pass-record-path>`
  placeholder before recording. The engine bundled at
  `~/.claude/skills/constellation-reviewer/scripts/checklist_engine.py` refuses with
  `amend applies to gated checklists`, so the g1 reviewer concluded no verb could do it and forced a
  waiver. That conclusion was correct **for that bundle** but wrong about the engine: the repo's
  current `scripts/checklist_engine.py:2276` reads `amend applies to gated and survey checklists`,
  and the amend succeeded first try. Two consequences worth acting on: (1) re-run
  `install_constellation.py` so reviewers stop hitting a phantom wall; (2) the template should ship
  the postcondition with a fillable path rather than a shell-hostile `<placeholder>` — as written,
  a POSIX shell reads `<fowler-pass-record-path>` as a redirect from a nonexistent file. I drove the
  survey with the installed bundle up to `r6-fowler` and the repo engine from the amend onward; both
  wrote the same file, the lease is continuous and the journal hash chain is intact (46 entries).
- **"Do not modify any source or test file" and "re-run the mutations" are in tension** and the
  handoff does not say how to resolve it. I resolved it by copying `scripts/ tests/ docs/ skills/`
  into a scratch tree, `git init`-ing it so the two `RepoRevision` oracle tests have a repo to compare
  against, and mutating there — which reproduced the 416-passed baseline exactly. Worth one line in
  the handoff, because the naive reading (mutate in place, restore after) risks leaving the worktree
  dirty if the run is interrupted.
- **The two review surveys collide on their mechanical sidecars.** `g1-review` and `g2-review`
  instantiate from the same template, so both carry item ids `r0-context`…`r6-fowler`, and the
  engine's mechanical sidecar path is keyed by **item id alone**:
  `.agent-work/issue-467-trip-semantics/issue-467-trip-semantics/mechanical/r0-context.json` etc. My
  run overwrote g1's seven files. No information was lost here (the diff is timestamps only —
  `generated_at` 10:50 → 12:34), but if the two surveys' items ever diverge, the second reviewer
  silently destroys the first's mechanical record. Namespacing the sidecar by gate would fix it. Note
  also the doubled `issue-467-trip-semantics/issue-467-trip-semantics/` segment in that path — a
  work-root resolution quirk that predates this gate.
- **The `Evidence Produced` section listed the RED run as `5 failed, 6 passed, 349 deselected`**,
  which is the *implementer's* narrower selector. My full-selector run against the pre-change engine
  gives `16 failed, 9 passed` — a much stronger number that was available and unreported. Suggest the
  implementer handoff ask for the pre-change run of the **whole closeout selector**, not just the new
  class: it converts "my new tests are red" into "here is exactly which of the shipped tests
  distinguish the two worlds", which is the number a reviewer actually wants.
