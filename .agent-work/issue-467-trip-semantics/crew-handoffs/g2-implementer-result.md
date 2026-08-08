# Implementation Result — g2-implement, issue #467

## Assigned gate
`g2-implement` — issue #467, epic #418. Branch `epic-418/a2-467-trip-semantics`, worktree
`C:/Programs/constellation-skills-wt/epic418-a2-467`.

## Return status
`complete`

## Completed slice

All five parts, in one gate.

- **(a)** `dispatch` no longer calls `_trip_hard_gate` on `advance`. Closing the gate you are
  already inside is never governor-refused.
- **(b)** The guard hangs off `start` and `reopen` instead, through a named set
  `TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}`. #190's identity check is preserved verbatim,
  including the `wid is None` degradation to a gate-only match. `resume` is **not** guarded.
- **(c)** At/over hard, an `advance` that would record NOTHING is refused: `--mechanical` is
  refused and `why_exempt` is suspended, and suspended means the `--why` is actually appended to
  the `why_trail`, not merely demanded. The message names the compliant form.
- **(d)** The HARD advisory is rewritten as a changed instruction, with no alarm language, and
  `_refresh_attach_hint` emits the concrete live why-record id instead of the literal `<why-id>`.
- **(e)** `docs/CHECKLIST_SCHEMA.md`'s Trip section, plus its `start` / `advance` / `reopen` verb
  table rows, describe the shipped behaviour.

### The seam, stated once

The bands still ride the CLI boundary in `dispatch`; only which chokepoint the guard hangs from
moved. `start`, `reopen` and `advance` stay pure — their return values are unchanged, and
`advance` gained one keyword `require_why: bool = False`, so every direct (non-`dispatch`) call in
the suite behaves byte-identically. `dispatch` computes that flag from a new
`_trip_hard_band_reading(cl, base_dir)` — one place that decides "are we at/over hard", so the
begin-work guard and the no-silent-close rule cannot disagree about it. Refusals still raise
before the liveness stamp.

## Scope

**Files changed:**
- `scripts/checklist_engine.py`
- `tests/test_checklist_engine.py`
- `docs/CHECKLIST_SCHEMA.md`
- `.agent-work/issue-467-trip-semantics/g2-mutation-log.md` (new)

Also written, as run evidence rather than deliverables:
`.agent-work/issue-467-trip-semantics/crew-plans/g2-implementer-plan.json` (+ `.journal`) and
`.agent-work/issue-467-trip-semantics/evidence/g2-m{1,2,3}-RED.txt`.

**Specific exclusions touched:** no.
- `resume` (:1999) — untouched and pinned untouched by a test; mutation M12 confirms the pin.
- `gauge_reader._PROFILES` — untouched.
- `attach` — no validation added.
- No mid-gate handoff channel built; raised as a triage candidate below.

**Not committed.** The Commander commits at the gate seam. `execute.json` and `spine.json` were
not touched.

## Behavior changed

Yes. `start` and `reopen` are refused at/over hard without a matching refresh-request; `advance`
never is; `advance` at/over hard requires a real `--why` and records it.

## Test mode

**Required:** test-first (TDD), with mutation testing on every guard shipped.
**Satisfied:** yes. Three red→green cycles, one per slice, each RED run saved. The RED runs are
in `evidence/g2-m{1,2,3}-RED.txt`; twelve mutations are logged in `g2-mutation-log.md`.

---

# Evidence

## 1. The permanent DC2 guard — red against unmodified source, green after

`TripHardGuardsBeginNotClose::test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest`

**The fixture's two load-bearing properties, asserted inside the test itself** (if either ever
stops holding, the test passes on both sides of the change and guards nothing):

```python
cl = self._three_gates()
self.assertEqual(_refresh_requests_anywhere(cl), [])      # NO refresh-request anywhere in the spine
with mock.patch.object(E, "_read_gauge", return_value=_reading(self.over_hard)):
    self.assertGreaterEqual(E._read_gauge(Path(".")).fill_fraction, self.hard)   # fill >= hard
    msg = E.dispatch(cl, _advance_ns("g1", why="handed off at g1: HARD now guards the begin verbs"),
                     base_dir=Path("."))
self.assertTrue(msg.endswith("g1 -> complete"), msg)
self.assertEqual(cl["tasks"]["g1"]["status"], "complete")
self.assertEqual(E._digest(cl), "handed off at g1: HARD now guards the begin verbs")
self.assertEqual(_refresh_requests_anywhere(cl), [])
```

`_refresh_requests_anywhere` walks **every task's** evidence list, superseded or not — it is a
whole-spine check, not a check on the active gate.

**RED, against unmodified source** (`evidence/g2-m1-RED.txt`):

```
scripts\checklist_engine.py:2680: in dispatch
    _trip_hard_gate(cl, getattr(args, "id", None), base_dir)
...
>       raise EngineError(
            f"{iid}: context at {reading.fill_fraction:.0%} is at/over the hard limit — "
            f"advancing is blocked until you request a refresh, ...

FAILED tests/test_checklist_engine.py::TripHardGuardsBeginNotClose::test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest
FAILED tests/test_checklist_engine.py::TripHardGuardsBeginNotClose::test_handoff_digest_names_the_understanding_written_at_the_tripping_gate
FAILED tests/test_checklist_engine.py::TripHardGuardsBeginNotClose::test_trip_begin_reopen_refused_at_hard_without_refresh
FAILED tests/test_checklist_engine.py::TripHardGuardsBeginNotClose::test_trip_begin_stale_why_ref_does_not_release_begin_work
FAILED tests/test_checklist_engine.py::TripHardGuardsBeginNotClose::test_trip_begin_start_refused_at_and_above_hard_without_refresh
5 failed, 6 passed, 349 deselected in 2.25s
```

**GREEN, after:**

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'trip_begin or begin_work or handoff'
.........................                                                [100%]
25 passed, 346 deselected in 2.56s
```

**Mutation M3** (`advance` put back into the guarded set) turns this exact test red again, with a
total of 6 failures — see the mutation log. That is the deadlock returning and being caught.

There is a second, independent DC2 guard at the real-file tier:
`TripRealGaugeFileWiring::test_handoff_fresh_hard_gauge_never_refuses_the_closing_advance` drives
a REAL `gauge.json` over hard through `main()` and asserts rc 0, `complete`, the fresh digest, and
no refresh-request anywhere. Neither guard depends on the disposable RED repro.

## 2. The mutation log

`.agent-work/issue-467-trip-semantics/g2-mutation-log.md` — twelve mutations, each with the branch
broken, the NAMED test that went red, and the TOTAL failure count. Baseline for the mutated pair:
416 passed, 30 subtests.

| # | branch broken | named test | total failed |
|---|---|---|---|
| M1 | `start` out of the guarded set | `test_trip_begin_start_refused_at_and_above_hard_without_refresh` | 7 |
| M2 | `reopen` out of the guarded set | `test_trip_begin_reopen_refused_at_hard_without_refresh` | 1 |
| M3 | `advance` back in the guarded set | `test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest` | 6 |
| M4 | `advance`'s `require_why` branch disabled | `test_handoff_mechanical_close_refused_at_hard` | 3 |
| M5 | `require_why` unwired at the dispatch seam | `test_handoff_why_exempt_is_suspended_at_hard` | 3 |
| M6 | hint reverted to literal `<why-id>` | `test_handoff_refresh_hint_carries_the_concrete_why_id` | 3 |
| M7 | HARD advisory reverted to alarm wording | `test_handoff_hard_advisory_reads_as_a_changed_instruction` | 2 |
| M8 | below-hard early return removed | `test_trip_begin_start_allowed_just_below_hard` | 5 |
| M9 | #190 identity filter dropped | `test_trip_begin_stale_why_ref_does_not_release_begin_work` | 2 |
| M10 | gated-only fail-safe removed | `test_trip_begin_survey_never_refuses_begin_work` | 1 |
| M11 | None-reading fail-safe | **no specific mutation available** | 0 / 59 / 47 |
| M12 | `resume` guarded (exclusion violated) | `test_trip_begin_resume_is_not_guarded_at_hard` | 1 |

M4 and M5 are deliberately both run: M4 proves the rule exists, M5 proves it is *wired to the
gauge*. Only M5 catches a guard that ships inert.

**M11 is reported as a limitation, not dressed as a pass.** No narrow mutation of the
None-reading fail-safe exists: deleting the check breaks 59 tests, inverting it to fail-unsafe
breaks 47, and a `return reading`-for-`return None` swap is a null mutation. The cause is
structural — nearly every fixture in the suite runs with no gauge file, so `reading is None` is
the path the whole suite takes. The honest claim is that `constraint:fail-safe-on-no-reading` is
massively over-determined and cannot be regressed silently, but no single named test owns it.
Specificity is not claimed for it.

Each mutation was applied to a single unique anchor, run, then reverted from a pristine copy.
Restoration verified: `diff /tmp/engine_pristine.py scripts/checklist_engine.py` → identical, and
a clean 416-passed run afterwards.

## 3. The `--mechanical`-at-hard refusal, quoted exactly

The test asserts this by **equality**, not substring
(`TripHardGuardsBeginNotClose.NO_SILENT_CLOSE`):

```
g2: context is at/over the hard limit, so this gate cannot be closed silently — a mechanical or why-less close records no understanding, and the next agent would cold-start from a digest written before your work. Closing the gate is NOT refused; only the silence is. Run: advance g2 --why "<understanding>"
```

**The digest cannot go stale after the fix**, proved two ways:

- `test_handoff_digest_names_the_understanding_written_at_the_tripping_gate` — g1 closes with
  `"pre-trip understanding"`, the agent starts g2, trips at hard, closes g2; the digest is then
  `"at-g2 handoff understanding"`, not the g1 one.
- The mechanical route to a stale digest is closed outright: `--mechanical` at hard is refused,
  and `why_exempt` is suspended so an exempt gate cannot close silently either
  (`test_handoff_why_exempt_is_suspended_at_hard` asserts the `--why` actually lands on the
  `why_trail`, which is the half that matters — a `--why` accepted but not recorded would leave
  the digest exactly as stale).

Ordering preserved: `test_handoff_unmet_postconditions_still_refuse_before_the_why_demand`
asserts that at/over hard a failing postcondition still yields `g1: postconditions unmet ['c1']`,
so the handoff demand is never a way of buying past unfinished work.

## 4. `reopen` guarded / `resume` NOT guarded — both directions, live

```
## start a genuinely PENDING gate over the line -> REFUSED, gate stays pending
REFUSED: g2: context at 20% is at/over the hard limit, so this is not the moment to BEGIN work here — finish and close the gate you are already in, then request a refresh so a fresh agent starts this one. Run: attach g2 --type refresh-request --field seam=g2 --field why_ref=w-1
g2 status: pending

## reopen a COMPLETE gate over the line -> REFUSED, gate stays complete
REFUSED: g1: context at 20% is at/over the hard limit, so this is not the moment to BEGIN work here — finish and close the gate you are already in, then request a refresh so a fresh agent starts this one. Run: attach g1 --type refresh-request --field seam=g1 --field why_ref=w-1
g1 status: complete

## file the refresh-request the message names (concrete id), then start is released
attached e-g2-1 (refresh-request) to g2
g2 -> in-progress
```

`resume` at the same fill returns the gate to its pre-block status without refusal
(`test_trip_begin_resume_is_not_guarded_at_hard`, asserted on the exact return string
`g1 resumed -> in-progress (blocker resolved: ruling arrived)`). Mutation M12 shows that adding
`resume` to the guarded set is caught by exactly that one test.

## 5. Re-aimed existing tests — count 6, none deleted

Three were renamed because the old name had become a false statement; three kept their names and
changed only their body. `git diff` shows 3 removed `def test_` lines and 25 added (22 new tests
plus the 3 renames).

| # | test | change | why this is the fix, not collateral |
|---|---|---|---|
| 1 | `TripTwoBandGatePolicy::test_hard_refuses_at_and_above_hard_without_refresh` → `...test_hard_refuses_begin_work_at_and_above_hard_without_refresh` | verb `advance` → `start`; gate asserted `pending` | Its acceptance was "does HARD ever let you pass without a refresh-request? → NO". That question is unchanged; only the verb it is asked of moved. Renamed because the old name now asserts the opposite of the ruling. |
| 2 | `TripTwoBandGatePolicy::test_hard_refusal_leaves_state_unmutated` | verb `advance` → `start`; name kept | It pins the ordering property — refusal before mutation and before the liveness stamp — which is a constraint of this handoff. The property is unchanged; it just has to be asserted on a verb that can still be refused. |
| 3 | `TripTwoBandGatePolicy::test_hard_passes_once_refresh_request_exists` → `...test_hard_handoff_close_needs_a_why_even_with_a_refresh_request_pending` | rewritten | Its old claim ("HARD forces until a request exists, then advance passes") no longer says anything — HARD never refuses an advance now, so it would be green in both worlds. Re-aimed to the live question in its place: a pending refresh-request must not buy SILENCE at the close. Its gate is `why_exempt`, so it also pins that the suspension holds on the already-requested path. |
| 4 | `TripTwoBandGatePolicy::test_hard_advisory_on_current_points_at_attach` | dropped the `assertIn("BLOCKED")`, added `assertIn("your instruction has changed")`, `assertNotIn("BLOCKED")`, and the exact `<why-id>` fallback string; name kept | The `BLOCKED` assertion asserted the defect. Its surviving half — the advisory routes to the exact remedy — is kept and strengthened. This fixture's gates carry no `why_trail`, so it is now also the pin for the `<why-id>` fallback. |
| 5 | `RefreshRequestIdentity::test_hard_coattails_fixed_stale_why_ref_refused_then_fresh_releases` | verb `advance` → `start` on a pending g3; name kept | This is #190's own regression test. The identity check moved sites unchanged, so the test follows it. Mutation M9 confirms it still defends that branch. |
| 6 | `TripRealGaugeFileWiring::test_fresh_hard_gauge_sibling_of_spine_refuses_then_passes_with_refresh` → `..._refuses_begin_work_then_passes_with_refresh` | verb `advance` → `start`, two-gate spine | The real-file wiring proof (gauge as sibling of the spine, read by the real reader through `main()`) is orthogonal to which verb is guarded; it just has to point at the guarded one. Renamed for the same reason as #1. |

No test was deleted.

## 6. Fail-safe on a `None` reading survives at the new guard sites

`test_trip_begin_none_reading_never_refuses_begin_work` (both `start` and `reopen` succeed),
`test_trip_begin_no_base_dir_never_refuses_begin_work`,
`test_trip_begin_survey_never_refuses_begin_work`, and
`test_handoff_no_silent_close_never_fires_on_a_none_reading` (a missing reading must not conjure a
`--why` requirement onto an exempt gate). Both no-ops live in one predicate,
`_trip_hard_band_reading`, so both bands inherit them.

## 7. Verb return strings unchanged

The existing exact-equality tests staying green is the proof: `tests/test_checklist_engine.py`
went from 349 passed to 371 passed with **no** pre-existing test failing for a return-string
reason. `advance`'s new `require_why` defaults to `False`, so the many direct
`E.advance(cl, "g1", why=...)` calls in the suite are unaffected.

## 8. Wiring grep — 3 production call sites, zero inert symbols

```bash
for sym in _trip_hard_band_reading TRIP_HARD_GUARDED_VERBS require_why; do
  grep -rn "$sym" --include=*.py . | grep -v "^./.agent-work/" | grep -v "def $sym" \
    | grep -v self_test | grep -v "^./tests/"
done
```

```
=== _trip_hard_band_reading ===
./scripts/checklist_engine.py:1514:    reading = _trip_hard_band_reading(cl, base_dir)
./scripts/checklist_engine.py:2806:                       require_why=_trip_hard_band_reading(cl, base_dir) is not None)
=== TRIP_HARD_GUARDED_VERBS ===
./scripts/checklist_engine.py:83:TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}
./scripts/checklist_engine.py:1221:#     `start` and `reopen` (TRIP_HARD_GUARDED_VERBS) — until a `refresh-request`
./scripts/checklist_engine.py:2770:        if v in TRIP_HARD_GUARDED_VERBS:
```

`require_why` shows its declaration at :1921, its use inside `advance` at :1975, and the
load-bearing external pass from `_run_verb` at :2806.

**Count: 3 distinct production call sites** (`:1514`, `:2770`, `:2806`) covering all three new
symbols, every one outside its own definition and outside any `--self-test` path. No symbol is
shipped-inert. Mutation M5 is the behavioural twin of this grep: unwiring `:2806` turns three
named tests red.

## 9. Verification commands

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
1815 passed, 2 skipped, 682 subtests passed in 285.87s (0:04:45)

FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py
416 passed, 30 subtests passed in 10.70s

FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k 'trip_begin or begin_work or handoff'
25 passed, 346 deselected in 2.56s
```

The frozen closeout selector **collects 25 tests** and exits 0. Before this gate it collected 0
and exited 5 (measured: `349 deselected in 0.20s`, `EXIT=5`).

### Delta against the baseline, explained

Baseline at `d376b786`, reproduced by this run before any edit: **1793 passed, 2 skipped, 683
subtests**. Now: **1815 passed, 2 skipped, 682 subtests**.

- **+22 passed** — 22 new tests in `tests/test_checklist_engine.py` (349 → 371 passed for that
  file): 21 in the new `TripHardGuardsBeginNotClose` class plus
  `TripRealGaugeFileWiring::test_handoff_fresh_hard_gauge_never_refuses_the_closing_advance`. The
  6 re-aimed tests are re-aimed, not added, so they do not change the count.
- **−1 subtest** — located by bisection to `tests/test_context_manifest.py`
  (`ContentAddressedRev::test_rev_equals_git_rev_parse_head_for_tracked_clean_files`). That test
  filters its `TARGETS` list to files that are **clean** in the working tree — "cleanliness is
  measured, never assumed", per its own comment — and `scripts/checklist_engine.py` is one of the
  four targets. With the engine dirty it emits 3 subtests instead of 4. Measured both ways: with
  my engine edit reverted the file reports **62 subtests**, with it present **61**; reverting the
  docs edit instead changes nothing (that file is not a target). **This delta disappears the
  moment the Commander commits at the gate seam** — it is an artifact of an uncommitted working
  tree, not a lost assertion.
- Failure distribution derived mechanically, not read off the tail:
  `grep -E '^FAILED' /tmp/full.txt | sed 's/::.*//' | sort | uniq -c` → empty (no failures).

## 10. Docs

`docs/CHECKLIST_SCHEMA.md`'s Trip section is retitled "SOFT advisory / HARD guards the BEGIN
verbs" and now states: which verbs HARD refuses and why; that `advance` and `resume` are not
refused; the no-silent-close rule and the #431 mechanism behind it; that HARD means "wrap up",
never "you are unsafe"; and the seam (`require_why` passed in from `dispatch`, verbs stay pure).
The `start`, `advance` and `reopen` rows of the verb table carry the same facts inline.

**Blast-radius sweep, by command, not by memory:**

```bash
grep -rln "refuse-advance\|pre-\`advance\` guard\|advance\` is BLOCKED" \
  --include=*.md --include=*.py --include=*.json . | grep -v "^./.agent-work/"
```

Count: **1** — `scripts/checklist_engine.py` (the Trip module header comment at :1228, now
rewritten in place). A broader sweep for `HARD` across `docs/` and `skills/` returned four files;
three are still accurate (`docs/GAUGE_WRITER_HOOK.md` quotes a fill vs a threshold,
`skills/workbench/references/checklist-engine.md` describes #190's identity filter, which is
unchanged). The fourth is stale and is **out of my allowed scope** — see below.

---

## Map Impact

- **Structural anchors touched:** `scripts/checklist_engine.py` — `dispatch` (:2760 area, the
  chokepoint; guard set swapped), `_trip_hard_gate` (:1500, re-aimed and re-worded), new
  `_trip_hard_band_reading` (:1481), new module constant `TRIP_HARD_GUARDED_VERBS` (:83),
  `_trip_advisory` HARD branch (:1455), `_refresh_attach_hint` (:1277, signature gained
  `why_id`), `advance` (:1919, gained `require_why`), `_run_verb` advance arm (:2802).
  `has_pending_refresh_request`, `resume`, `start`, `reopen` bodies unchanged.
  `docs/CHECKLIST_SCHEMA.md` Trip section + three verb-table rows refreshed.
- **Capabilities changed:** Trip two-band gate policy, HARD band — enforcement point moved from
  the close verb to the begin verbs, plus a new no-silent-close rule on the close verb. SOFT band
  unchanged. why-capture / reach-up unchanged in shape and now genuinely reachable at a trip.
- **Constraints honored:** `constraint:fail-safe-on-no-reading` (both bands still no-op on a None
  reading — now from one shared predicate), `constraint:gated-only` (both bands empty for
  surveys), `constraint:gate-boundaries-only` (no mid-gate check added),
  `constraint:pure-verbs` (return strings unchanged; `require_why` defaults False).
- **Decisions implemented as given:** `decision:hard-guards-begin-not-close`,
  `decision:no-silent-close-at-hard`. Neither re-opened.
- **Claims/evidence produced:** `claim:dc2-two-way` — both directions tested, the
  not-refused half standing as the permanent guard at two tiers (mocked and real-file).
  `claim:dc3-digest-fresh` — tested directly.
- **Trust limitations / drift found:** `docs/agents/GLOSSARY.md` line 13 is now false. See below.
- **Triage candidates:** two, below.

---

## Assumptions

1. **The no-silent-close rule was implemented inside `advance` behind a `dispatch`-supplied
   flag**, rather than as a second pre-verb guard in `dispatch`. Reason: suspending `why_exempt`
   requires the understanding to actually be *recorded*, and only `advance` can append to the
   `why_trail` — a pre-verb refusal in `dispatch` would demand a `--why` that `advance` would then
   discard on an exempt gate, leaving the digest exactly as stale. The band decision still lives
   at the CLI boundary; only the recording does not. The handoff's allowed scope names "`advance`
   (:1854 and its why/mechanical branch at :1899)", so I read this as in scope. If the reviewer
   reads `constraint:pure-verbs` more strictly than "return values unchanged", this is the line to
   look at.
2. **The Trip guard on `start` fires before `start`'s own status check.** So an over-the-line
   `start` against an already-`in-progress` gate now reports the Trip refusal rather than
   `"g2 is 'in-progress', cannot start"`. That ordering is required by the constraint that a
   refusal must raise before the liveness stamp. It is a message-precedence change only; no state
   differs.
3. The `<why-id>` placeholder is kept as the fallback when a checklist has no live why-record
   (e.g. an all-`why_exempt` spine), since there is no real id to name. Pinned by
   `test_handoff_refresh_hint_carries_the_concrete_why_id` and by the re-aimed
   `test_hard_advisory_on_current_points_at_attach`.

## Stop conditions hit

None. Allowed scope was not exceeded, no exclusion was touched, every piece of required evidence
was produced, no decision outside the given authority was needed, and the permanent DC2 guard was
red-then-green for the right reason.

One item came close and is reported instead of acted on — see the first out-of-scope observation.

## Out-of-scope observations

1. **`docs/agents/GLOSSARY.md` line 13 is now false, and it is not in my allowed scope.** It
   reads:

   > `| `trip` | — | The event where a gauge reading crosses a band (SOFT or HARD) and the engine
   > restricts what the agent may do next. | — | HARD blocks `advance` until the agent requests a
   > context refresh. |`

   HARD no longer blocks `advance`. This is the glossary every agent in the constellation reads,
   and it now teaches the exact belief #431 came from — so I rate it must-fix before the epic
   closes, not a nicety. My allowed scope names `docs/CHECKLIST_SCHEMA.md` **Trip section only**,
   so I did not edit it. Suggested replacement for the example cell: *"HARD refuses `start` and
   `reopen` until the agent requests a context refresh; it never refuses the `advance` that closes
   the gate you are in."* One line, one file. **Commander decision.**

2. **Triage candidate, raised not built (as instructed):** whether the gate that trips with UNMET
   postconditions needs a mid-gate handoff channel. `block --next` exists but `current` does not
   render its text, so an agent that trips mid-gate with a failing check has nowhere to leave the
   "here is where I got to" note that the next agent needs. Carries no grade.

3. **Triage candidate (new, found while implementing):** the `--mechanical` refusal and the
   begin-work refusal both fire on the *reading*, so a run whose gauge is silent for any of the
   three localizable reasons (`_no_reading_advisory`'s branches) gets no protection at all. That
   is the correct fail-safe and I did not change it, but the pairing means the advisories in
   `_no_reading_advisory` are the only thing standing between a blind run and a stale digest.
   Worth an explicit decision somewhere that the fail-safe direction is still right now that HARD
   also governs what gets *recorded*, not just what is refused.

---

## Workflow Feedback

- **Handoff gaps.** Two, both in *Allowed Scope*.
  - **The scope list did not include the artifacts that assert things about the code it did
    include.** `docs/CHECKLIST_SCHEMA.md` was scoped to its Trip section, but the same claim
    ("HARD blocks `advance`") also lives in `docs/agents/GLOSSARY.md` and in a module-header
    comment in the file I was editing. I found them by running the blast-radius grep on my own
    initiative; the handoff did not ask for it and would not have caught the glossary if I had
    not. A one-line *"run the blast-radius grep and report every artifact that asserts the old
    behaviour"* line in Required Evidence would make that reliable rather than lucky.
  - **`Wiring Grep` says "one command naming every symbol this slice adds", but the slice's
    symbols are not knowable at handoff time**, so I had to choose them and then justify the
    choice. That worked, but the instruction reads as if the list were given. Naming the *rule*
    ("every new module-level name and every new parameter that crosses a seam") instead of
    implying a list would remove the guesswork.
- **Context rediscovered.** The exact test-helper vocabulary (`gated`, `gate(why_exempt=...)`,
  `_reading`, `_advance_ns`) and the exact return strings of `reopen` and `resume` — I burned two
  test-run cycles discovering that `reopen` returns
  `"g1 reopened (rework 1/3); cascade-reset downstream [...]"` rather than `"g1 -> in-progress"`.
  The Map Anchors carried line numbers for the *source* symbols but nothing about the test
  fixtures, which is where the friction actually was. A one-line pointer to the fixture helpers in
  the anchors would have paid for itself.
- **Instructions improvised around.** The test mode says *"each new test must be red against
  today's code for the right reason"*, which is impossible for the falsifiable-half and fail-safe
  companions — a test that pins what must NOT change is green in both worlds by construction.
  I wrote them anyway, marked which were RED-first and which were companions in each engine
  attest, and defended the companions by mutation instead. Recommend the test mode say so
  explicitly: *"every test pinning NEW behaviour must be red first; companions pinning unchanged
  behaviour are defended by mutation."* Without that, an implementer either omits the companions
  or misreports them as red-first.
- **The mutation-count rule needs an escape hatch for structurally load-bearing branches.** The
  rule as written ("a mutation that breaks forty unrelated tests demonstrates the opposite")
  gives no sanctioned way to report a branch that genuinely cannot be mutated narrowly. The
  None-reading fail-safe is such a branch, and the only honest options were to report a
  47-failure mutation as if it proved something, or to say plainly that specificity is not
  claimed. I did the latter (M11 in the log). The rule should name that outcome as acceptable so
  the next implementer does not feel pushed toward the former.
- **What would have made this easier.** The three-times-repeated warning about the obvious test
  was genuinely load-bearing and I would keep it verbatim. The single highest-value addition
  would be a **"stale claims to sweep"** field in the handoff, listing the greps to run over
  docs and skills before calling the change done — the authoring-side blast radius is exactly the
  thing the author is worst positioned to notice, and it is currently left to initiative.
