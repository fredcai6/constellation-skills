# Implementer Handoff

## Gate
`g2-implement` — Decision-aware `admiral-prelaunch` (issue #506), work-id `w5-gates`, epic #418 wave 5.

Worktree: `C:/Programs/constellation-skills-wt/epic418-w5-gates`, branch `epic-418/w5-bookend-gates`.
Use absolute paths.

## Operational facts — these have cost real time on this run

1. **Use `python`, never `py`.** Different interpreters on this machine; `py` has no pytest, so
   `py -m pytest` exits nonzero and reads exactly like a red suite when the tests never ran.
2. **Never pipe a pytest command into `tail` or `head`.** `$?` then belongs to the pipe, and a
   zero-match `-k` selector — which exits **5** — reads as exit 0. Run the command bare, read its
   own exit code, inspect output separately.
3. **Find code by text, not by line number.** g1 added ~370 lines to the test file and ~40 to the
   script. Every line number in the frozen plan predates that. The ones below I re-measured myself
   at HEAD `6f48ece4`, but re-confirm before you edit.
4. Two files under `.agent-work/epic-418-redux/transitions/close-to-w5/` show `M` in `git status`
   with **empty diffs** — a CRLF stat artifact, blob OIDs identical to HEAD. Verified three times.
   **Leave them unstaged.** Not yours.

## Task Statement

Make `verify_admiral_prelaunch` **decision-aware**, **keeping the mode name `admiral-prelaunch`**.

Today a `stop` packet cannot get through, and **two** clauses block it, not the one the issue names:

- **`_next_wave()`** (`scripts/verify_iterative_role_artifacts.py:186-194`) requires `launch_id` to be
  present *and* a nonempty `SAFE_ID`.
- **`_require(result["decision"] in {"advance", "replan"}, ...)`** (`:222-225`).

**The ordering wrinkle — this is why it must be restructured rather than bolted on.** In
`verify_admiral_prelaunch` (`:207`), `_next_wave(work_area)` runs at **line 208**, but
`result["decision"]` is not read until **line 222**. So the launch-id requirement fires before anyone
knows the decision. Worse, `boundary_id` comes *out* of `_next_wave` and is what locates the
transition directory holding `REPLAN_RESULT.json` — so you cannot simply read the decision first.
Some restructure is needed: `boundary_id` must still be validated unconditionally (it is a path
component and `SAFE_ID` is a path-safety guard, not a policy), while the `launch_id` requirement
becomes conditional on the decision. Choose the shape; that constraint is the fixed part.

**A third `_require` at `:222`** asserts `result["applicable"] is True`. It does **not** block a stop
packet whose `applicable` is true, so it needs **no change** — but know it is there, and do not
"helpfully" relax it.

### The Admiral's ruling on #506

Options 1 and 2 are taken **COMBINED, not as alternatives** — option 1 needs option 2 to be
implementable at all.

Under `stop`:
- the artifact **may** express "no launch authorized";
- the authorization clause is **SKIPPED**;
- G2 validation, the unique-audit-entry match, the render, and the `CURRENT_TRUTH.md` /
  `WAVE_REVIEW.md` writes **ALL still run**.

`repair` **stays refused** — out of scope, and a real authorization question. Do not widen to it.

### The assertion you MUST invert

`tests/test_iterative_planning_doctrine.py:466` currently reads:

```python
self.assertNotEqual(0, refused.returncode, "stop cannot authorize NEXT_WAVE")
```

(The plan cites 461-462; g1 moved it. **Find it by that message text.**)

Fix A inverts exactly that assertion. The file is owned, so the edit is legal — but **state the
inversion explicitly in your IMPLEMENTER_RESULT**. Launch-order pre-ruling 6 forbids changing a
recorded exit to make a check pass; the difference here is that **this inversion IS the fix**, not a
workaround for it. Say so in those terms, and say what the assertion now asserts instead.

## Test Naming Contract — LOAD-BEARING

This gate's close criteria select on these substrings. A `-k` selector matching zero tests exits 5 and
**fails the gate closed**. That is deliberate — it is the remedy for a cold critic's BLOCK finding
that this gate could otherwise have closed with zero work done. **Do not rename around it.**

- Golden-path stop tests **MUST** carry **`stop_boundary`** in their method names.
- The mutation test required by pre-ruling 2 **MUST** carry **`stop_mutation`**.

## Allowed Scope

Exactly two files:

- `scripts/verify_iterative_role_artifacts.py`
- `tests/test_iterative_planning_doctrine.py`

## Specific Exclusions

- `scripts/checklist_engine.py`, `tests/test_checklist_engine.py` — **crew 4 is their sole writer
  this wave.** If your fix appears to need them, that is a **float**, not a decision.
- `scripts/install_constellation.py` — crew 2 (readable, not editable).
- Handoff templates — crew 3. `docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md` — crew 5.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — this crew's, but gate g3's.
- Hooks, any `settings.json`, `docs/agents/*` doctrine.

**Any red outside the ownership scope is a FLOAT, not an edit.** Report it; do not fix it.

## Constraints

- **A separate admiral-boundary mode is DECLINED.** `ADMIRAL_SPINE.template.json` names the mode
  string and is not this run's file. Keep `admiral-prelaunch`.
- **COPY the live stop fixture into your test. NEVER mutate the live epic's packet** at
  `.agent-work/epic-418-redux/transitions/w4-to-close/` (it holds `REPLAN_INPUT.json`,
  `REPLAN_RESULT.json`, `CURRENT_TRUTH.md`, `WAVE_REVIEW.md`). It is the real epic's state.
- **Pre-ruling 6:** you may not change any decision, verdict, or recorded exit to make a check pass.
  If a check cannot pass, that is a **finding**. The one sanctioned inversion is named above.
- Verifier changes owe targeted tests **plus** the relevant broader suite. No no-test-surface
  exception.

## HONEST NULL — read this before you start

If fix A's cheapest shape is **refuted** — say the authorization clause turns out to be load-bearing
for a reason the issue missed — **report that with the evidence and STOP.** Do not build the
expensive version to avoid returning a null. A well-evidenced null is a good outcome here, not a
failure. Scope the null precisely: "this specific shape is refuted because X", never "this approach
is impossible."

## Map Anchors (inbound)

This repo has **no architecture map** — orientation is `DEGRADED-NO-MAP`, so anchors are named by
path and there are no `struct:`/`decision:` ids to cite.

- **Structural:** `scripts/verify_iterative_role_artifacts.py` — `verify_admiral_prelaunch()` at
  `:207`, `_next_wave()` at `:186`, `_verify_transition_audit()` at `:197`.
- **Capability:** Role-artifact verification at the Admiral's wave boundary — a strengthened durable
  system.
- **Decision anchor:** a `stop` transition is a legitimate terminal outcome that must still be
  *verified*, not merely *refused*. Verification and authorization are different jobs, and today the
  verifier conflates them.
  `@grade: settled/human · leans g2-implement,g2-review · (Admiral ruling — options 1+2 combined; a contradiction is a float, not a revision)`
- **Map confidence flags:** the decision-vs-authorization split is this gate's one **unmapped seam**.
  Measure the current behaviour before you change it.

## Evidence Expected

Run each bare, report the exit code you actually saw:

- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k stop_boundary`
- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k stop_mutation`
- Coupled suite:

```bash
python -m pytest tests/test_iterative_planning_doctrine.py tests/test_install_constellation.py tests/test_init_work_area.py tests/test_context_manifest.py tests/test_spine_provenance_check.py tests/test_map_contract_wiring.py tests/test_worktree_precondition_wiring.py tests/test_spine_rail.py -q
```

Baseline at HEAD `6f48ece4` is **387 passed / 480 subtests, exit 0**. Report your delta and account
for it — an unexplained delta is a finding.

Also state, for each selector, **how many tests it collected**. Zero is a gate failure, not a pass.

## Stop Conditions

Return BLOCKED if: the restructure cannot preserve `boundary_id` validation; a non-owned file goes
red; the authorization clause proves load-bearing (the honest null above); or a policy decision is
required before you can proceed.

## Return Format

Write your IMPLEMENTER_RESULT to
`.agent-work/w5-gates/crew-handoffs/g2-implement-RESULT.md`. State clearly whether you are
`COMPLETE` or `BLOCKED`, the inversion statement required above, per-item evidence with real exit
codes, files touched, anything you floated, and workflow feedback.

## Suggested Model Tier

Stronger. The restructure has a genuine ordering constraint and an honest-null branch that needs
judgment rather than persistence.
