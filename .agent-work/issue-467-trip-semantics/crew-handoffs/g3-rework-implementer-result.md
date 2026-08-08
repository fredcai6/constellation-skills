# Implementation Result

## Assigned gate
`g3` REWORK (attempt 2) — issue #467, epic #418: correct reviewer finding B-1, the false M15
"equivalent mutant" declaration in the g3 mutation log.

## Completed slice
One test added that reaches, through public verbs only, the state B-1 identified (a blocked
earlier gate leaving `active_id()` behind the gate actually being closed) and asserts the
no-silent-close rule is not bypassed there. Proved RED under the M15 mutation and GREEN on
shipped code. The M15 mutation-log entry corrected from `EQUIVALENT` to `KILLED`, with the
kill named and a visible correction note. No source change.

## Scope
**Files changed:**
- `tests/test_checklist_engine.py` — new test
  `GateHeadroomOverrideTripTests::test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate`
- `.agent-work/issue-467-trip-semantics/g3-mutation-log.md` — M15 entry corrected; Summary
  section updated from "15 killed / 1 declared equivalent" to "16 killed"
- `.agent-work/issue-467-trip-semantics/crew-plans/g3-rework-implementer-plan.json` (+ `.journal`) —
  my own engine-driven plan

**Specific exclusions touched:** no. `scripts/checklist_engine.py` and `scripts/gauge_reader.py`
are unmodified in the final diff (`block()` was not touched, `blocked` was not added to
`TERMINAL`). The M15 mutation was applied to `scripts/checklist_engine.py` **temporarily**, in
place, to observe the RED run, then reverted; `git diff --stat -- scripts` was empty both
before the mutation and after the revert (checked again at closeout, see Evidence).

## Behavior changed
No. This is a missing-test fix. The shipped engine's behavior is unchanged.

## New test — name and body

```python
def test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate(self):
    """B-1 (g3 rework 2, mutation M15). The no-silent-close rule's band decision
    must be read for the gate NAMED in the `advance`, never for whatever
    `active_id()` reports -- M15's declared-EQUIVALENT reasoning claimed those
    two are always the same gate. They are not: `block()` carries no status
    guard and `blocked` is not in `TERMINAL`, so `active_id()` can sit BEHIND a
    later in-progress gate. Reached through public verbs only -- start/advance/
    start/block/advance -- the same sequence the reviewer reproduced at the
    CLI: g1 (no override) is advanced to complete, then BLOCKED (legal --
    block() has no status guard); g2 (carrying the override) is started while
    g1 is still open and is left in-progress. `active_id(cl)` then reports g1,
    even though the gate being CLOSED is g2."""
    cl = gated(
        g1=gate("g1", "pending", command=PASS_COMMAND, why_exempt=True),
        g2=gate("g2", "pending", command=PASS_COMMAND, why_exempt=True),
    )
    cl["tasks"]["g2"]["context_headroom_tokens"] = self.RESERVE
    # Low fill while g1 is opened/closed and g2 is opened, so neither begin-work
    # guard (start is TRIP_HARD_GUARDED) refuses -- the fill rises to FILL (12%)
    # only AFTER g2 is already under way, exactly as the CLI reproduction did.
    with self._gauge(fill=0.0):
        E.dispatch(cl, _start_ns("g1"), base_dir=Path("."))
        E.dispatch(cl, _advance_ns("g1"), base_dir=Path("."))
        E.dispatch(cl, _start_ns("g2"), base_dir=Path("."))
    with self._gauge():  # FILL=0.12: over g2's overridden hard, under g1's default hard
        E.dispatch(cl, types.SimpleNamespace(
            verb="block", id="g1", blocker="upstream authority", authority="human",
            next_action="wait", session_id=None,
        ), base_dir=Path("."))
        self.assertEqual(cl["tasks"]["g1"]["status"], "blocked")
        # The divergence M15 declared unreachable: the ACTIVE gate is g1, but
        # the gate being CLOSED below is g2.
        self.assertEqual(E.active_id(cl), "g1")
        with self.assertRaises(E.EngineError) as ctx:
            E.dispatch(cl, _advance_ns("g2", mechanical=True), base_dir=Path("."))
        self.assertEqual(cl["tasks"]["g2"]["status"], "in-progress")
    self.assertIn("cannot be closed silently", str(ctx.exception))
```

It reuses `GateHeadroomOverrideTripTests`'s own fixture constants (`RESERVE=50_000`,
`MODEL="claude-opus-5"`, `FILL=0.12`) and its `_gauge()` helper, which patches `_read_gauge`
directly (`mock.patch.object(E, "_read_gauge", return_value=_reading(fill, self.MODEL))`) —
the same pattern that already avoids the fixture trap the handoff flagged (a hand-written
`observed_at` even slightly ahead of the wall clock reads as clock skew and silently collapses
to "no gauge").

## Test mode
**Required:** test-first (TDD): write, observe RED under the mutation, then GREEN on shipped.
**Satisfied:** yes.

## TDD evidence

**RED — M15 mutation applied in place** (`scripts/checklist_engine.py:2857-2858`,
`require_why=_trip_hard_band_reading(cl, base_dir, getattr(args, "id", None))` →
`require_why=_trip_hard_band_reading(cl, base_dir)`):

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate
F                                                                        [100%]
================================== FAILURES ===================================
_ GateHeadroomOverrideTripTests.test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate _
...
>           with self.assertRaises(E.EngineError) as ctx:
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           AssertionError: EngineError not raised

tests\test_checklist_engine.py:3988: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_checklist_engine.py::GateHeadroomOverrideTripTests::test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate
1 failed, 383 deselected in 0.81s
```

Mutation then reverted from a pre-mutation backup; `git diff --stat -- scripts` confirmed
empty immediately after the revert.

**GREEN — shipped (unmutated) code:**

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate
.                                                                        [100%]
1 passed, 383 deselected in 0.66s
```

- Refactor while green: no refactor needed; one method, no source touched.

## Corrected M15 log entry

`.agent-work/issue-467-trip-semantics/g3-mutation-log.md`, M15 section now reads (excerpted):

> ## M15 — advance's `require_why` naming the gate being closed — **KILLED**
>
> - **Branch broken:** `require_why=_trip_hard_band_reading(cl, base_dir, getattr(args, "id", None))`
>   → `require_why=_trip_hard_band_reading(cl, base_dir)`.
> - **NAMED test red:**
>   `GateHeadroomOverrideTripTests::test_no_silent_close_reads_the_gate_being_closed_not_a_blocked_active_gate`
> - **TOTAL: 1 failed**, 383 deselected (frozen `headroom or override` selector).
> - **CORRECTION (g3 rework 2, reviewer finding B-1):** this entry originally declared M15 an
>   **equivalent mutant** on the reasoning that `advance` refuses any gate that is not
>   `in-progress` and `start` refuses to open a gate that is not the active one, so in every
>   reachable state the gate being advanced IS the active gate and `args.id == active_id(cl)`.
>   **That reasoning is false and the fixture is reachable, not manufactured.** It enumerated
>   `start` and `advance` but never `block()` (`checklist_engine.py:2116`), which carries **no
>   status guard**... [full text in the file; also updates the Summary section from "15 killed
>   / 1 declared equivalent" to "16 killed"]

(Full corrected text is in the file itself, not reproduced here in full to avoid duplicating
the audit record in two places.)

## Evidence

```bash
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py tests/test_init_work_area.py tests/test_install_constellation.py
572 passed, 535 subtests passed in 30.42s

$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py tests/test_gauge_reader.py -k 'headroom or override'
21 passed, 413 deselected, 125 subtests passed in 1.17s

$ git diff --stat -- scripts
(no output — scripts/ unchanged)

$ git diff --stat
 .agent-work/issue-467-trip-semantics/g3-mutation-log.md | 54 +++++++++++++-------
 tests/test_checklist_engine.py                          | 38 ++++++++++++++
 (+ my own plan/journal files, +pre-existing crew-runs.json/execute.json/
   execute.json.journal changes that predate this session and were not made by me)
```

**Result:** pass — both required suite selectors green; `scripts/` diff empty.

## Docs/contracts touched
- `.agent-work/issue-467-trip-semantics/g3-mutation-log.md` — the M15 entry, corrected per task.

## Assumptions
- The M15 mutation site's line numbers (`checklist_engine.py:2857-2858`) matched the handoff
  exactly; no drift since the handoff was written.
- `crew-runs.json`, `execute.json`, and `execute.json.journal` were already modified in this
  worktree before I claimed my own plan's lease (confirmed via `git status` at the start of
  this session) — I did not touch them, per the Commander's held lease.

## Stop conditions hit
None. The shipped source code was never found to be genuinely wrong — the RED/GREEN pair
confirms it is correct and the gap was purely a missing test. No source change was needed to
kill M15.

## Out-of-scope observations
None beyond what the handoff already named as pre-existing and filed (that `block()` accepts
a `complete` gate with no status guard). No new out-of-scope finding surfaced while writing or
mutating around this test.

## Workflow Feedback

- **Handoff gaps:** none. The handoff's CLI reproduction, exact mutation line numbers, and the
  fixture-trap warning (patch `_read_gauge`, don't hand-write `observed_at`) all matched what I
  found in the source, and the fixture numbers were directly reusable from
  `GateHeadroomOverrideTripTests`'s own class constants.
- **Context rediscovered:** none beyond the ordinary read of `advance`/`block`/`active_id`/
  `_trip_hard_band_reading`/`dispatch` to confirm the mechanism the handoff described, and
  confirming `start`/`reopen` (not `block`/`advance`) are the only `TRIP_HARD_GUARDED_VERBS` —
  which is why the fixture has to raise the fill only *after* `g2` is already started, not
  before, matching the handoff's own CLI trace (`0.02 -> 0.12` "while g2 is under way").
- **Instructions improvised around:** none. There is no `_block_ns` test helper alongside
  `_start_ns`/`_advance_ns`/`_reopen_ns`/`_resume_ns` in `tests/test_checklist_engine.py`, so I
  built the `block` dispatch call inline with `types.SimpleNamespace(verb="block", ...)` —
  matching the shape `_run_verb`'s `block` branch expects (`args.id`, `args.blocker`,
  `args.authority`, `args.next_action`). Not a gap in the handoff, just a minor missing
  convenience helper in the test file itself, not worth adding for one call site.
- **What would have made this easier:** nothing concrete; this handoff was unusually complete
  (verbatim reproduction, exact line numbers, named fixture trap) and the task was mechanical
  execution against a proven target, as its own model-tier note said.

## Return status
`complete`
