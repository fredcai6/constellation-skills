# Implementer Handoff

## Gate
g1-implement

## Task
Fix two defects in `scripts/checklist_engine.py`'s `current`/RAIL projection (issue #420, epic #418
workstream B) and add a regression test for the defect class:

1. **RAIL echo de-duplication, `current` verb only.** When the CLI verb is `current`,
   `render_human()`'s `ACTIVE {id} [{status}] — {imperative}` line already prints the active gate's
   full imperative. The RAIL block appended at the CLI boundary (`_rail_prefix`/`_rail` in
   `dispatch()`) ALSO prints the full imperative a second time, via `_rail_position()`'s mid-flight
   branch substituting `cl["tasks"][active].get("imperative", "")` for the `{imperative}` token in
   `_RAIL_STRINGS["mid-flight"]`. Fix this duplication for the `current` verb specifically. **Do
   NOT** touch the other five `RAIL_VERBS` (`claim`, `start`, `advance`, `attest`, `attach`) — none
   of their outputs include an ACTIVE line, so the RAIL's imperative mention is the ONLY place their
   caller sees "what's next," and must keep the full text unchanged.
2. **Render `anchors` and `constraints`.** `state()` (builds the `active` dict `current()` renders)
   never reads `t.get("anchors")` or `t.get("constraints")` — confirmed live, these fields simply do
   not reach the projection today, even when populated. Both fields are real, populated corpus
   content (not vestigial — verified this run against ~20+ real archived `execute.json` gates), so
   render them when present on the active gate.
3. **Completeness property test.** Enumerate the fields a `Task` may carry (per
   `docs/CHECKLIST_SCHEMA.md`'s Task table, plus `anchors` which is documented only in
   `commander-core.md` prose) and assert, for a fixture gate with every field populated, that every
   populated field's content appears somewhere in `current`'s rendered output. This must be a real
   enumeration a future added-and-forgotten field would fail, not a hardcoded check of only
   `anchors`/`constraints` by name.

## Protected Intent
`current` is the complete state channel every agent in this corpus drives from — every other role's
doctrine says "read `current`, never the raw JSON." This fix must not make `current` lie in a new
way (e.g. dropping the imperative from a verb that needs it, or making the projection less complete
than before) while fixing the two ways it lies today.

## Test Mode
TDD, required by the issue's own acceptance criteria: "goldens written before the change so the
diff asserts the intended delta." Concretely: add/extend tests against the **current, unfixed**
code first, confirm they fail (red) for the right reason, then make the code change and confirm
green. State in your `IMPLEMENTER_RESULT` that you did this in that order (e.g. quote the red
pytest output before the fix, or describe the red run) — a test written after the fix that merely
happens to pass does not satisfy this gate's evidence bar.

## Close Criteria
- On the `current` verb only, the active gate's imperative text appears in the combined output
  exactly once (was twice). Verify with a real mid-flight fixture (3+ gate spine, one gate active
  and not first/last, so the mid-flight RAIL string is in play) — count occurrences of the
  imperative substring in `E.current`'s CLI-wrapped output (i.e. through `dispatch()`, not the bare
  `current()` function, since the duplication only exists at the CLI-boundary RAIL layer).
- On every OTHER railed verb (`claim`, `start`, `advance`, `attest`, `attach`), the mid-flight RAIL
  still carries the full imperative text unchanged — prove this with at least one direct assertion
  (e.g. `E._rail("start", cl)` or `E._rail("advance", cl)` against the same fixture), not just an
  absence of a regression elsewhere.
- `_RAIL_STRINGS` dict values are byte-identical to before this change (frozen, verbatim, a
  measurement precondition for issue #145) — only what fills `{imperative}` changes, and only for
  `point == "current"`.
- When the active gate carries a populated `anchors` and/or `constraints`, `current`'s output
  contains that content; when a gate carries neither (or empty), output is unchanged from today.
- `render_human()`'s existing byte-exact goldens (the `GoldenOutputBriefing` test class,
  `tests/test_checklist_engine.py` ~line 3738 on) stay green or are deliberately extended (not
  broken) to cover the new anchors/constraints rendering.
- A new completeness property test enumerates Task fields and asserts every populated one renders,
  for a fixture gate carrying all of them.
- `python -m pytest tests/test_checklist_engine.py tests/test_spine_rail.py -q` is green after the
  change (388 passed, 24 subtests passed on the pre-change baseline this session — the new tests add
  to that count, nothing existing silently disappears from the count without a stated reason).

## Allowed Scope
- `scripts/checklist_engine.py`: `state()` (~line 1548), `render_human()` (~line 1587),
  `_RAIL_STRINGS` (~225-241, value substitution logic only — see constraints), `_rail_position()`
  (~244-263), `_rail()`/`_rail_prefix()` (~266-294), and the `dispatch()` call site that invokes them
  (~2464) if verb-awareness requires threading the verb name through.
- `tests/test_checklist_engine.py`: add new tests; extend `GoldenOutputBriefing` for
  anchors/constraints; **deliberately update** `DoctrineRail.test_rail_mid_flight` (~line 1825) to
  assert the new `current`-only dedup behavior, and add a sibling assertion proving a non-`current`
  railed verb still gets the full imperative — this test targets exactly the bug being fixed, so
  changing it is expected, not a violation of "don't touch existing tests."
- `tests/test_spine_rail.py`: read it first; touch only if it also exercises the mid-flight RAIL
  substitution and needs the same verb-aware update (pre-authorized if so — do not treat it as
  out-of-scope just because it wasn't named above).
- Fix-if-convenient: `render_human()`'s docstring (~line 1591) currently cites
  `tests/test_checklist_engine.py:818` as the byte-exact ACTIVE-line pin; verified live this run
  that citation is stale (line 818 is an unrelated `require_session` lease test). The real pin is
  the `GoldenOutputBriefing` class (~3738 on). Fix the docstring's citation while you're already
  touching this function's neighborhood; if it doesn't fit naturally, skip it and name it in your
  `IMPLEMENTER_RESULT`'s workflow feedback instead — do not spend a separate pass hunting for other
  stale citations.

## Specific Exclusions
- Do **not** touch `_check_condition` or any postcondition/invariant-evaluation code anywhere in
  `checklist_engine.py` — that is workstream D's (#422) owned path this wave (shared-file fence). If
  you find you genuinely need to touch it to land this fix, STOP and report it as a blocker rather
  than editing it.
- Do **not** touch workstream C's relocation work or anything about moving instruction text into
  spine templates — separate workstream, separate worktree.
- Do **not** investigate or fix the "DIGEST goes stale after a HARD governor trip" observation from
  the Admiral's live run — judged separate from this issue's scope; if you happen to notice it while
  reading `why_trail`/Trip code, just don't touch it.
- Do **not** try to settle whether RAIL-echo removal is behavior-neutral for compliance — that's
  workstream C's end-of-tranche tracer's job, not testable from this gate.

## Constraints
- The five `_RAIL_STRINGS` dict VALUES (the literal doctrine text, including their `{token}`
  placeholders) stay 100% byte-unchanged. Only the *value substituted* for the `{imperative}` token
  changes, and only when the triggering point is `"current"`.
- `state()` must stay a PURE projection (INV-2, `docs/CHECKLIST_ENGINE_DESIGN.md`) — reading
  `anchors`/`constraints` off the task dict must add no side effect and re-run no check.
- Keep the change minimal and localized — this is a rendering fix, not a refactor. Don't restructure
  `state()`/`render_human()` beyond what's needed to add the two new fields and thread verb-awareness
  through to the RAIL substitution.
- A negative/partial result on any ONE of the three deliverables is reportable as a scoped, honest
  finding (comment it at the code site, note it in your result) — do not silently drop a deliverable
  or silently expand scope to force all three through if one turns out harder than expected. If that
  happens, stop and report rather than guessing past it.

## Map Anchors (inbound)
- **Structural:** `scripts/checklist_engine.py`: `state()` (~1548), `render_human()` (~1587),
  `_RAIL_STRINGS` (~225-241), `_rail_position()` (~244-263), `_rail()`/`_rail_prefix()` (~266-294),
  `dispatch()`'s `RAIL_VERBS` call site (~2464).
- **Capability:** the `current` projection's completeness contract —
  `docs/CHECKLIST_ENGINE_DESIGN.md` "Answerability: `current` as a complete briefing" (INV-1:
  `current` is a superset of what the caller needs).
- **Constraints/assumptions:** the five RAIL strings are frozen verbatim (measurement precondition
  for #145); `state()` purity (INV-2: no side effects, no re-run of checks); the fix must be
  verb-aware (dedup only on `point == 'current'`).
- **Decision anchors:** vestigial-fields question is closed — anchors/constraints are real corpus
  content, render them, do not delete them.
  `@grade: settled/measured · leans g1-implement · settle: already settled by this run's grep
  inventory across ~20+ archived execute.json gates`
- **Evidence expectations:** on `current`, the imperative appears exactly once post-fix; on the
  other 5 railed verbs, the imperative still appears in full post-fix; anchors/constraints, when
  populated, appear in `current`'s output post-fix; the completeness property holds for a
  fully-populated fixture gate.
- **Map confidence flags:** none — this repo has no architecture map (skill-source repo); the
  backing docs (`docs/CHECKLIST_ENGINE_DESIGN.md`, `docs/CHECKLIST_SCHEMA.md`) were read in full
  this run and are current.

## Deliverable Path Check
- **Committed** — `scripts/checklist_engine.py`; verified via `git check-ignore scripts/checklist_engine.py` exiting 1 (not ignored), run this session.
- **Committed** — `tests/test_checklist_engine.py`; verified via `git check-ignore tests/test_checklist_engine.py` exiting 1 (not ignored), run this session.
- **Committed** — `tests/test_spine_rail.py`, if touched; verified via `git check-ignore tests/test_spine_rail.py` exiting 1 (not ignored), run this session.

## Required Evidence
- The RED run: paste the pytest output (or the specific failing assertions) from your new/extended
  tests run against the pre-fix code, proving they fail for the right reason before your fix lands.
- The GREEN run: `python -m pytest tests/test_checklist_engine.py tests/test_spine_rail.py -q` full
  output after the fix, with the final summary line (pass/fail/subtest counts) — this is
  **load-bearing**, reproduce it exactly, do not summarize from a glance.
- A `git diff --stat` (or equivalent) showing exactly which files changed and by how much — this is
  **confirmatory**, a spot-check is enough.
- One `current`-through-`dispatch()` sample output, mid-flight, post-fix, with the active gate's
  imperative substring counted (state the count) — this is **load-bearing**, must be exact.
- One `_rail("start", cl)` (or `advance`/`attest`/`claim`/`attach`) sample, same fixture, post-fix,
  showing the full imperative is still present — **load-bearing**.

## Wiring Grep
`none — this is a fix to existing rendering functions already called from dispatch()/current(); no
new public symbol is added that needs a caller-reachability check. If your fix DOES add a new
helper function, name it here with a grep proving dispatch()/render_human()/state() actually calls
it.`

## Verification Commands
```bash
python -m pytest tests/test_checklist_engine.py tests/test_spine_rail.py -q
```
```bash
git check-ignore scripts/checklist_engine.py tests/test_checklist_engine.py tests/test_spine_rail.py
```

## Suggested Model Tier
Sonnet — bounded, well-scoped, single-file rendering fix with a clear existing test harness; no
open-ended design ambiguity (the launch order caps model tier at Sonnet for this whole run anyway).

## Authority
- The vestigial-fields question is already decided (render, don't delete) — not yours to revisit.
- The verb-aware dedup shape (only `current`, not the other 5 verbs) is already decided by the
  Commander after a cold-critic review — not yours to revisit; if you find evidence it's wrong,
  stop and report rather than silently reverting to a blanket dedup.
- Anything about workstream C, D, or G's scope is not yours to decide — report and stop if you hit
  a genuine boundary question.

## Stop Conditions
Stop and return if: the fix requires touching `_check_condition`/invariant-check code (D's fence);
a required test cannot be made to fail red before the fix for a legitimate reason; you find the
verb-aware dedup shape is actually wrong (e.g. some other verb's output DOES already show the
imperative elsewhere and would newly duplicate); or any decision outside the Authority section above
is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied (with the red-then-
green evidence), evidence produced, assumptions used, stop conditions hit, out-of-scope observations
(log as triage candidates — e.g. the `anchors` field's absence from `CHECKLIST_SCHEMA.md`'s Task
table), workflow feedback. **Deliver this via SendMessage to your dispatcher before ending your
turn** — do not just end idle with the result only in your final text.
