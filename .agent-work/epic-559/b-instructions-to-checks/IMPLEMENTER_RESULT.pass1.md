# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`epic-559/b-instructions-to-checks / g1-implement`

## Completed slice
Census of all six shipped role templates for "run this script" imperatives and for the #562
statement/check mismatch shape; converted the one remaining unconverted instruction
(`ADMIRAL_SPINE.init`) to a command postcondition; fixed #562
(`EXECUTE_PLAN.g1-implement.c1`) by constraining its check; fixed one more mismatch the sweep
found (`EXPLORER_SPINE.init.c1`) by weakening an overclaiming statement. Full census recorded
verbatim at `.agent-work/epic-559/b-instructions-to-checks/CENSUS.md`.

## Scope
**Files changed:**
- `skills/admiral/templates/ADMIRAL_SPINE.template.json`
- `skills/commander/templates/EXECUTE_PLAN.template.json`
- `skills/explorer/templates/EXPLORER_SPINE.template.json`

**Specific exclusions touched:** no — `checklist_engine.py`, `run_crew.py`, crew skill files,
`settings.json`, and `docs/agents/*` were not touched.

## Behavior changed
Yes.
- `ADMIRAL_SPINE.init.c1` previously had `check: null` (agent-attested only); it now mechanically
  refuses `advance` until `init_work_area.py <work-id>` succeeds **and** `ADMIRAL_LOG.md` exists.
- `EXECUTE_PLAN.g1-implement.c1` (#562) previously accepted **any** `implementer-result` evidence,
  including one reporting the work blocked, failed, or partial. It now refuses unless the result's
  `status` field is `complete`.
- `EXPLORER_SPINE.init.c1`'s statement no longer claims "spine.json materialized" — a property its
  bare command check (no `--spine`/`--skill-dir`) never tested. Check text and its pass/fail
  behavior are unchanged; only the statement was corrected to what the check actually proves.

## Before/after (every instruction converted + the sweep)

Full table (22 run-script instructions, 5 statement/check mismatch sites) is in
`.agent-work/epic-559/b-instructions-to-checks/CENSUS.md`. Summary of what actually changed:

| Gate | Before | After | Why |
|---|---|---|---|
| `ADMIRAL_SPINE.init` | Imperative: `"Run: python <admiral-skill-dir>/scripts/init_work_area.py <work-id>. Claim the engine session lease..."`. `c1.check: null`. | Imperative drops the `"Run: ..."` sentence. `c1.check = {"kind":"command","command":"python <admiral-skill-dir>/scripts/init_work_area.py <work-id> && test -f .agent-work/<work-id>/ADMIRAL_LOG.md"}`. | Doctrine already treats it as mandatory-before-proceeding (it's the first sentence of the gate, and everything downstream needs the work area). Commander and Explorer already convert the identical instruction on their own `init` gates — this was the one shipped template that missed the pattern, the same slip shape as #562 itself. |
| `EXECUTE_PLAN.g1-implement.c1` (#562) | `check = {"kind":"artifact","evidence_type":"implementer-result"}` — no `match`, so vacuously true. | `check` gains `"match":{"status":"complete"}`; statement clarified to `"...(return status complete)"`. | Named defect. Constrained rather than weakened: weakening the statement would have left the gate mechanically unable to fail on a blocked/failed implementer-result, which is exactly the defect #562 flags. |
| `EXPLORER_SPINE.init.c1` | `statement: "work area scaffolded and spine.json materialized"`. | `statement: "work area scaffolded"`. | The command check (deliberately run without `--spine`/`--skill-dir`, matching what Commander's own `init.c1` already does) only re-confirms the mkdir'd subdirectories. Weakened rather than constrained: spine.json's existence is a bootstrap invariant of the engine already running this `advance`, not something a fresh command check meaningfully re-proves — adding a tautological `test -f` would just be a check-that-cannot-fail in the other direction. Matches the already-shipped honest pattern at `g1-review.c1`. |

The remaining 19 run-script instructions were already converted (command checks already present,
verified unchanged), or are action/mutator scripts (`run_crew.py`, `apply_episode_delta.py`) that
don't belong as postcondition checks, or are per-dispatch loop invariants (`recover_crews.py`
"before EACH dispatch") that can't be expressed as a single gate-boundary check. The remaining 3
statement/check sites in the #562-shape sweep (the `user-decision` artifact-presence checks at
`understand`/`plan`/`triage`/`review`/`latitude`/`closeout`/`explore`/`confirm`) are presence-only
by explicit design — `commander-core.md` states "The engine only requires the `user-decision`
artifact to be present; the citation rides in the payload for audit" — and 2 more
(`g1-review.c1`, `g1-integrate.c2`) were already correct. Full reasoning per site is in CENSUS.md.

## Every converted command run in a clean checkout, shown passing (and one shown failing)

Ran against a `git worktree add --detach` clean checkout of a `git stash create` snapshot of this
branch (so the checkout carries the edits above with none of this worktree's untracked
`.agent-work` state), never a path hardcoded from this worktree — resolved placeholders exactly as
`init_work_area.resolve_spine` would (`<admiral-skill-dir>`/`<skill-dir>` → `.` in a source repo
with top-level `scripts/`).

**ADMIRAL_SPINE.init.c1**, driven through the real engine end to end (`claim` → `start` →
`advance`) on a scratch `demo-559b` spine instantiated from the template:
```
$ python scripts/checklist_engine.py --file spine.json advance init --mechanical --session-id demo-sess
REFUSED: init: postconditions unmet ['c1', 'c2']
exit: 1
```
(ADMIRAL_LOG.md genuinely did not exist yet — refuses for the right reason.) Then:
```
$ cp skills/admiral/templates/ADMIRAL_LOG.template.md .agent-work/demo-559b/ADMIRAL_LOG.md
$ python scripts/checklist_engine.py --file spine.json advance init --mechanical --session-id demo-sess
init -> complete
exit: 0
```

**EXECUTE_PLAN.g1-implement.c1** (#562), on a scratch single-gate spine built from the live
template's `g1-implement` task:
```
$ python scripts/checklist_engine.py --file spine.json attach g1-implement --type implementer-result --field status=blocked ...
$ python scripts/checklist_engine.py --file spine.json advance g1-implement --mechanical ...
REFUSED: g1-implement: postconditions unmet ['c1']
exit: 1
```
```
$ python scripts/checklist_engine.py --file spine.json attach g1-implement --type implementer-result --field status=complete ...
$ python scripts/checklist_engine.py --file spine.json advance g1-implement --mechanical ...
g1-implement -> complete
exit: 0
```
For contrast, replaying the **pre-fix** check shape (no `match`) against the same `status=blocked`
evidence: `advance` returned `g1-implement -> complete`, exit 0 — reproducing #562 exactly, and
confirming the fix is what closes it.

**EXPLORER_SPINE.init.c1** (statement-only fix, check unchanged): re-instantiated the template into
a fresh scratch work area and re-ran the check command directly — `exit: 0`, unchanged pass
behavior confirmed.

## Test mode
**Required:** evidence-only (template/config edits, not TDD-shaped code).
**Satisfied:** yes — behavior demonstrated live against the real engine, both directions, as above.

## Evidence

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
**Result:** pass — `2532 passed, 1 skipped, 1102 subtests passed in 104.97s`. Re-ran after every
edit; no shipped-template structure test broke.

```bash
python -c "import json; [json.load(open(f)) for f in ['skills/admiral/templates/ADMIRAL_SPINE.template.json','skills/commander/templates/EXECUTE_PLAN.template.json','skills/explorer/templates/EXPLORER_SPINE.template.json']]"
```
**Result:** pass — all three edited templates are still valid JSON after the surgical text edits.

## Docs/contracts touched
- none — the fix stayed inside the three named template files. See Workflow Feedback for a gap
  I found but did not fix (the `implementer-result` payload's `status` field convention is not
  documented anywhere the commander could read it from).

## Assumptions
- The `implementer-result` evidence payload's `status` field mirrors the commander's existing,
  already-shipped convention for `review-result`'s `verdict` field (`EXECUTE_PLAN.g1-integrate.c2`
  already matches `{"verdict":"APPROVE"}`, parsed from `REVIEW_RESULT`'s `## Result` heading) —
  i.e. that when the commander "integrates" an `IMPLEMENTER_RESULT`, it attaches the evidence with
  a `status` field sourced from that document's own `## Return status` heading (`complete | partial
  | blocked | out-of-scope | failed`, per `skills/workbench/references/status-model.md`'s "Crew
  Return Status"). I could not find this convention independently documented anywhere (see
  Workflow Feedback) — I inferred it from the one place a matching convention is already proven in
  production (`g1-integrate.c2`), rather than inventing an unrelated field name.

## Stop conditions hit
- none.

## Out-of-scope observations
- The `implementer-result` attach-fields convention this fix now depends on
  (`skills/commander/references/commander-core.md`, `skills/commander/templates/
  IMPLEMENTER_HANDOFF.template.md`) is not documented anywhere, unlike `review-result`'s `verdict`
  field which is load-bearing and thus forced into the open by `g1-integrate.c2`. Recommend a
  follow-up: state explicitly, next to the existing `gN-implement`/`gN-review` guidance in
  `commander-core.md`, that integrating an `IMPLEMENTER_RESULT` means attaching `implementer-result`
  evidence with `fields={"status": "<Return status>"}` — otherwise a commander that doesn't
  independently reinvent this convention will find `g1-implement.c1` permanently unsatisfiable.
  This touches files outside my named scope (not one of the six templates), so I did not fix it.
- `COMMANDER_SPINE.execute`'s and `EXPLORER_SPINE.explore`'s `recover_crews.py` "before EACH
  dispatch" instructions are mandatory but cannot become a single gate-boundary postcondition
  without changing their meaning (see CENSUS.md #9/#16) — left as prose, flagged rather than
  silently dropped from consideration.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: task, intent, scope, exclusions, required
  evidence, and stop conditions were all present and unambiguous. The handoff's own worked example
  (comparing `g1-review.c1`'s honest statement against `g1-integrate.c2`'s constrained one) was
  enough to derive the right disposition for every mismatch found in the sweep without further
  clarification.
- **Context rediscovered:** the `implementer-result`/`status` field convention (see Out-of-scope
  observations above) — nothing in the six templates, `commander-core.md`, or
  `IMPLEMENTER_HANDOFF.template.md` states what field name the commander should attach when
  integrating an `IMPLEMENTER_RESULT`. I had to reconstruct it by analogy from the one place the
  parallel convention (`review-result`'s `verdict`) is already load-bearing and tested.
  `IMPLEMENTER_HANDOFF.template.md`'s Return Format section instructs the crew to return
  `IMPLEMENTER_RESULT` fields but says nothing about how the commander turns them into engine
  evidence — that gap should be closed so the next person doing this kind of fix doesn't have to
  re-derive it.
- **Instructions improvised around:** the handoff's caution ("show the command actually passing in
  a clean checkout") doesn't distinguish command-kind from artifact-kind checks; for the artifact
  check (#562) I improvised an equivalent demonstration by driving a scratch single-gate spine
  through the real engine's `attach`/`advance` CLI in the same clean checkout, rather than a bare
  shell command, since an artifact check has no shell command to run directly.
- **What would have made this easier:** documenting the `implementer-result` attach-fields
  convention (see above) before this task, so the #562 fix wouldn't have needed inference by
  analogy from a different evidence type.

## Map Impact
No `docs/architecture` map exists in this repo (skill-source repo, no packet map) — nothing to
reconcile against. This is a genuine behavior change to two gate-close checks (ADMIRAL's `init`,
Commander's `g1-implement`), flagged here rather than against map anchors since there are none to
cite.

## Return status
`complete`
