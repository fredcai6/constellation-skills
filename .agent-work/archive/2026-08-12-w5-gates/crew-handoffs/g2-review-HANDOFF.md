# Reviewer Handoff

## Gate
`g2-review` — Decision-aware `admiral-prelaunch` (issue #506), work-id `w5-gates`, epic #418 wave 5.

Worktree: `C:/Programs/constellation-skills-wt/epic418-w5-gates`, branch `epic-418/w5-bookend-gates`.
Use absolute paths.

## Operational facts — these have cost this run real time

1. **Use `python`, never `py`.** Different interpreters here; `py` has no pytest, so `py -m pytest`
   exits nonzero and reads exactly like a red suite when the tests never ran.
2. **Never pipe a pytest command into `tail` or `head`.** `$?` then belongs to the pipe, and a
   zero-match `-k` selector — which exits **5** — reads as exit 0. Run bare, read the real exit code.
3. **Find code by text, not by line number.** g1 and g2 both grew these files; every line number in
   the frozen plan is stale. This includes the assertion discussed below.
4. Two files under `.agent-work/epic-418-redux/transitions/close-to-w5/` show `M` in `git status`
   with **empty diffs** — a CRLF stat artifact, blob OIDs identical to HEAD. **Leave them unstaged.**

## How to Inspect the Diff — a resolvable ref

The change is **committed**. The g1 reviewer lost time because its handoff claimed the target was the
uncommitted working tree when it was not; this one names a real ref.

```bash
cd C:/Programs/constellation-skills-wt/epic418-w5-gates
git show --stat 57048457
git diff 6f48ece4 57048457 -- scripts/verify_iterative_role_artifacts.py tests/test_iterative_planning_doctrine.py
```

`6f48ece4` is g1's commit (the pre-g2 baseline); `57048457` is the change under review.

The implementer's result is at `.agent-work/w5-gates/crew-handoffs/g2-implement-RESULT.md`, and its
handoff — the contract the diff is judged against — is at
`.agent-work/w5-gates/crew-handoffs/g2-implement-HANDOFF.md`. **Read both, then reproduce rather
than trust.** Everything under `.agent-work/` is local-only and correctly absent from the tracked diff.

## Survey State Location

Create your review survey checklist at `.agent-work/w5-gates/g2-review/review.json` — under the run
workbench, never at the worktree root.

## What Was Implemented

`verify_admiral_prelaunch` now verifies a `stop` transition instead of refusing it, keeping the mode
name `admiral-prelaunch`. Verification and authorization were split into two functions because the
ordering was structural, not cosmetic: `_next_wave()` ran *before* the decision was read, yet
`boundary_id` comes out of `_next_wave()` and is what locates the `REPLAN_RESULT.json` holding that
decision.

- `_next_wave()` now checks only the decision-independent part: exact key set, `boundary_id` as a
  nonempty `SAFE_ID`, and `trigger`.
- A new `_require_launch_authorization(next_wave, decision)` carries the policy and runs **after**
  `REPLAN_RESULT` is read.

## Close Criteria

Each becomes a review check. Criteria 1 and 2 are the reason this gate exists — a cold critic panel
BLOCKed the original plan because gates like this one could close with **zero work done**.

1. **The stop path is not a hole.** Independently confirm that a stop-shortcut which bypasses **G2
   validation**, the **unique-audit-entry match**, or the **render** makes the `stop_mutation` test go
   **RED**. Build each shortcut yourself — do not read the implementer's test and call it confirmed.
   A stop path that skips any of those three is a hole, however green the suite is.
2. **An ungated null-`launch_id` allowance on the ADVANCE path must also go red.** Confirm the
   relaxation is genuinely conditional on the decision and did not simply weaken `launch_id`
   everywhere. This is the single most likely way this fix is wrong.
3. **The mode name is unchanged** — still `admiral-prelaunch`. A separate admiral-boundary mode was
   explicitly DECLINED because `ADMIRAL_SPINE.template.json` names the mode string and is not this
   run's file.
4. **`repair` is still refused.** It was ruled out of scope and is a real authorization question.
   Confirm a `repair` packet does not get through.
5. **`boundary_id` validation stayed unconditional.** It is a path component and `SAFE_ID` is a
   path-safety guard, not a policy. If it became conditional on the decision, that is a finding.
6. **State explicitly in your REVIEW_RESULT** that the inversion of the existing negative assertion —
   originally `assertNotEqual(0, refused.returncode, "stop cannot authorize NEXT_WAVE")`, **find it by
   that message text, its line has moved** — **is the fix itself and not a check bent to pass.**
   Launch-order pre-ruling 6 forbids changing a recorded exit to make a check pass, so this must be
   reasoned about on the record, not assumed. If you conclude it *is* a bent check, that is a BLOCK.
7. **Under `stop`, all four survivors still run**: G2 validation, the unique-audit-entry match, the
   render, and the `CURRENT_TRUTH.md` / `WAVE_REVIEW.md` writes. Measure each.
8. **Both `-k` selectors collect a nonzero number of tests**, unpiped, and the coupled suite is green.

## Allowed Scope

The implementation was permitted to touch exactly:

- `scripts/verify_iterative_role_artifacts.py`
- `tests/test_iterative_planning_doctrine.py`

Flag any tracked file outside that pair. `git diff --numstat 6f48ece4 57048457` should show only those
two (+45/−7 and +187/−2 by my own measurement).

## Specific Exclusions

Off-limits to the implementation; flag if touched:

- `scripts/checklist_engine.py`, `tests/test_checklist_engine.py` — **crew 4 is their sole writer.**
- `scripts/install_constellation.py` — crew 2 (readable, not editable).
- Handoff templates — crew 3. `docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md` — crew 5.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — this crew's, but gate g3's.
- Hooks, any `settings.json`, `docs/agents/*` doctrine.

## Constraints the Implementation Must Respect

- **The live epic packet at `.agent-work/epic-418-redux/transitions/w4-to-close/` must be COPIED,
  never mutated.** It is the real epic's terminal transition. Verify it is byte-unchanged.
- **Pre-ruling 6:** no decision, verdict, or recorded exit changed to make a check pass, except the
  one sanctioned inversion in criterion 6.
- Verifier changes owe targeted tests **plus** the relevant broader suite.
- **Test naming contract, load-bearing:** golden-path stop tests carry `stop_boundary`; the mutation
  test carries `stop_mutation`. A zero-match selector exits 5 and fails the gate closed — deliberate.

## Map Anchors (inbound)

This repo has **no architecture map** — orientation is `DEGRADED-NO-MAP`, so anchors are named by path
and there are no `struct:`/`decision:` ids to cite.

- **Structural:** `scripts/verify_iterative_role_artifacts.py` — `verify_admiral_prelaunch()`,
  `_next_wave()`, the new `_require_launch_authorization()`, `_verify_transition_audit()`.
- **Capability:** Role-artifact verification at the Admiral's wave boundary — a strengthened durable
  system.
- **Decision anchor:** a `stop` transition is a legitimate terminal outcome that must still be
  *verified*, not merely *refused*. Verification and authorization are different jobs; the verifier
  conflated them.
  `@grade: settled/human · leans g2-implement,g2-review · (Admiral ruling — #506 options 1+2 COMBINED, not alternatives; a contradiction is a float, not a revision)`
- **Map confidence flags:** the decision-vs-authorization split is this gate's one **unmapped seam**.
  Measure it; do not reason from structure.

## Evidence Produced

From the implementer, and re-run by me (the Commander) before dispatching you. Reproduce it:

- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k stop_boundary` → **2 passed,
  25 deselected, exit 0** (the implementer reports **2 failed, exit 1** before its fix).
- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k stop_mutation` → **1 passed,
  26 deselected, 7 subtests, exit 0.**
- Coupled suite → **390 passed, 487 subtests, exit 0** (387 at g1, so +3, fully attributed).

```bash
python -m pytest tests/test_iterative_planning_doctrine.py tests/test_install_constellation.py tests/test_init_work_area.py tests/test_context_manifest.py tests/test_spine_provenance_check.py tests/test_map_contract_wiring.py tests/test_worktree_precondition_wiring.py tests/test_spine_rail.py -q
```

One thing the implementer reported against itself, which you should confirm rather than assume: one
of its own mutations was initially a **no-op** — emptying `revised_forecast` keeps a *stop* packet
G2-valid, because an epic that stops forecasts nothing. It swapped to blanking `revised_epic_body`.
It says that idiom is used elsewhere in the file and will silently prove nothing on any stop fixture.
**Check whether any surviving mutation in this diff has the same problem.**

Your verdict is recorded against engine postcondition **`g2-review.c1`**, and `g2-integrate` matches on
`verdict: APPROVE`.

## Suggested Model Tier

Stronger. The gate turns on telling a real conditional relaxation apart from a blanket one, and on a
pre-ruling-6 judgment that has to be reasoned rather than pattern-matched.

## Stop Conditions

Return BLOCK if: the diff cannot be accessed; evidence is absent or unverifiable; a stop-shortcut
survives with green tests; the `launch_id` relaxation turns out to be unconditional; `repair` gets
through; the mode name changed; the live epic packet was mutated; the inversion is a bent check; or a
policy decision is required before a verdict is possible.

## Return Format

Write your REVIEW_RESULT to `.agent-work/w5-gates/crew-handoffs/g2-review-RESULT.md` — that file is
the deliverable and the gate verifies it exists and is fresh. It must state, on its own line,
`verdict: APPROVE` or `verdict: BLOCK`. Include per-check findings keyed to the numbered close
criteria, the criterion-6 statement in your own words, blockers, out-of-scope observations, and
workflow feedback.
