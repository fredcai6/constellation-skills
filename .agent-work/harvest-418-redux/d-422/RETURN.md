# RETURN — cmdr-422-wire-invariants (issue #422, epic-418 workstream D)

## 1. Verdict

**Win.** Asked: wire two prose-only invariants (#329 worktree isolation, #328's two `record()`-survey
checks) into real, mechanically-enforced engine checks, per epic-418's LAUNCH_ORDER `D-422.md` and
`DESIGN_SPEC.md` section D. Did: added a real command precondition to `COMMANDER_SPINE.template.json`'s
`init` gate (`verify_worktree_isolation.py --here <repo-root>`) plus a new enumeration script
(`scripts/verify_worktree_precondition_coverage.py`) that fails, naming the offender, if a
worktree-entering template ships without that precondition; extended `checklist_engine.py`'s survey verb
`record()` to actually evaluate `command`-kind postconditions and refuse `--result pass` on failure
(previously it ignored postconditions entirely), then wired `zc-consolidate`
(`INTERROGATION.template.json`) and `r6-fowler` (`REVIEW_SURVEY.template.json`) to the existing
`verify_interrogation.py`/`verify_fowler_pass.py` rail scripts. Both conversions carry deliberate-breakage
tests, landed in the automated suite, proving the checks actually refuse when broken — not just that they
pass when correct. Reconciled two doctrine docs whose "survey never blocks" claim went stale. Full spine
driven to a terminal `archive` through the engine; PR #438 open.

**Spec deviation, pre-authorized and disclosed, not floated:** #329's own issue text also asks about a
PreToolUse-hook feasibility investigation and a `fleet-doctrine.md` sentence correction. `DESIGN_SPEC.md`'s
T13 critique (Tommy-approved 2026-08-03) redefined the build to this cheaper spine-precondition +
enumeration-check design instead, and `D-422.md`'s Mission mirrors that redefinition, not the hook. Per the
launch order's own tie-breaker ("where the tracker and the spec differ, the spec wins, say so"), I built the
spec's design. #329 is **commented, not closed**, for its remaining, unbuilt scope.

## 2. Evidence

Commits on `epic-418/d-422-wire-invariants` (base `990712f`):
- `569e845` — #329 wiring (COMMANDER_SPINE.template.json + verify_worktree_precondition_coverage.py + tests)
- `b02ed0f` — #328 wiring (checklist_engine.py record() + INTERROGATION/REVIEW_SURVEY templates + tests)
- `b7af492` — reconcile: CHECKLIST_SCHEMA.md + CHECKLIST_ENGINE_DESIGN.md
- `477c7fc` — feedback log entry
- `12d8f4f`, `2d94fcc` — archive: work area moved to `.agent-work/archive/2026-08-06-issue-422-wire-invariants/`

**PR:** #438, `gh pr view 438 --json state` → `{"number":438,"state":"OPEN","title":"FINAL: wire #329 worktree isolation + #328 record()-postcondition checks (epic-418 D/#422)"}`

**Tests that gate the claim** (all re-run by me independently, not trusted from crew reports; both crew
gates also independently re-ran and reported the same numbers):
```
$ python -m pytest tests/test_worktree_precondition_wiring.py -q
2 passed
$ python -m pytest tests/test_record_postcondition_wiring.py -q
10 passed
$ python -m pytest tests/test_checklist_engine.py -q
330 passed, 24 subtests passed
$ python -m pytest tests/ -q
1633 passed, 2 skipped, 549 subtests passed
```
(Both `g1-integrate` and `g2-integrate` also independently re-ran their respective test commands as real
engine `command`-kind postconditions at `advance` time — exit 0 both times, not asserted.)

**Deliberate-breakage evidence** (the heart of this mission, per the launch order):
- #329: `git stash push -- skills/commander/templates/COMMANDER_SPINE.template.json`, re-ran
  `tests/test_worktree_precondition_wiring.py` → `1 failed, 1 passed` (named `AssertionError: real template
  unexpectedly missing the precondition before stripping`), `git stash pop`, re-ran → `2 passed`.
  Independently reproduced by the g1 reviewer as well.
- #328: `git stash push -- scripts/checklist_engine.py`, re-ran `tests/test_record_postcondition_wiring.py`
  → `3 failed, 7 passed` (the exact 3 refusal-dependent tests, `AssertionError: EngineError not raised`),
  `git stash pop`, re-ran → `10 passed`. Independently reproduced by the g2 reviewer, who also confirmed the
  shared-file fence held by diffing the FULL `checklist_engine.py` file (not just the reported hunk) —
  `render_human`/`_why_suffix`/`current()` byte-identical to before.

## 3. Isolation proof

First command of this run, before any git operation:
```
worktree OK: in C:/Programs/constellation-skills-wt/epic418-d-422
```
(exit 0)

## 4. Scope-discipline report

- **`_next_verbs`'s stale comment** (`scripts/checklist_engine.py:1505`/`1536-1538`, "record() carries no
  precondition/postcondition gate at all" — now partially outdated post-#328) was **not** fixed now, despite
  being a trivially bounded, otherwise fix-now-eligible diff, because `_next_verbs` is inside the exact
  rendering-path function this wave's shared-file fence with workstream B/#420 named off-limits. Both the
  g2 implementer and reviewer independently declined it for the same reason. Filed as **#437**.
- **`decision:worktree-entering-membership`'s `settle:` experiment is only half-exercised** — proven by
  stripping the one existing entry from a copy, not by adding a genuinely new second worktree-entering
  template (none exists yet). Noted in the mission frame at authoring time, confirmed still true at
  closeout. Filed as **#436**.
- **`null`/`artifact`-kind postconditions on a survey item remain unevaluated by `record()`** — commented
  explicitly at the code site (`checklist_engine.py`, inside `record()`'s new block); no current template
  needs it, so it was not built. This is Tommy's scope ruling applied directly, not a discovered gap.
- **Issue #315** (command-check `cwd` inheritance) was left unfixed, as pre-scoped; the two new command
  checks use repo-root-relative invocations, inheriting the same accepted fragility every other shipped
  command-check in the corpus already carries.
- **#329's PreToolUse-hook feasibility question and the `fleet-doctrine.md` sentence correction** were not
  built — out of this mission's spec-redefined scope (see Verdict above). Commented on #329, issue left
  open.

## 5. Map impact

No packet map exists in this repo (`docs/architecture` absent — `map_orient.py orient` returns
`DEGRADED-NO-MAP`). Reconciled directly per the Commander spine's `reconcile` step: `docs/CHECKLIST_SCHEMA.md`
and `docs/CHECKLIST_ENGINE_DESIGN.md` each asserted survey items are "recorded, never blocks" as an
absolute; both now carry the `command`-kind-postcondition exception `record()` implements (3 sites total,
commit `b7af492`). No other doc/schema needed a fold-in for #329's change (the schema already documented
command-kind preconditions generically; nothing there went stale).

## 6. Triage candidates

- **#436** (filed) — enumeration check's refusal-on-omission needs re-confirming against a real second
  worktree-entering template once one ships.
- **#437** (filed) — stale `_next_verbs` comment, deliberately not fixed now due to the active B/#420 fence.
- **#439** (filed, discovered live at this run's own `archive` gate) — `COMMANDER_SPINE.template.json`'s
  `archive.c2b` postcondition carries a literal, never-resolved `<branch>` placeholder
  (`init_work_area.py`'s resolver only handles `work-id`/`repo-root`/`*-skill-dir`/`*-session-id` tokens),
  so `gh pr list --head <branch> ...` always returns empty and the check always fails regardless of
  reality. **This affects every delegated Commander run reaching `archive`, not just this one.** Worked
  around this run via `waive --force` (no `override_policy` was declared on `c2b`), documented with the
  independently-verified real fact (`gh pr list --head epic-418/d-422-wire-invariants --state open` → PR
  #438). Recommend prioritizing #439 above #436/#437 — it is corpus-wide, not workstream-D-local.
- **#329** — commented (not filed as new), left open for its own remaining scope (PreToolUse-hook
  feasibility + `fleet-doctrine.md` sentence correction), per the spec-vs-tracker divergence in the Verdict.

## 7. Workflow feedback

- **`init_work_area.py --spine <path>` accepted the GLOBAL installed template path** even with
  `--skill-dir <worktree-root>` passed correctly, because `--skill-dir` only resolves `<commander-skill-dir>`
  TOKENS inside whichever template text is fed to it — it does not care which template FILE `--spine` names.
  My own spine ended up with every `<commander-skill-dir>`-resolved command (`run_crew.py`,
  `verify_agent_feedback.py`, `apply_lessons_delta.py`, `map_orient.py`, `verify_state_note.py`) pointing at
  the global install rather than this worktree's vendored `scripts/`. Did not unwind six completed gates
  over it — none of those scripts were this issue's deliverable, so it did not corrupt the fix — but it is a
  real dogfooding-hygiene gap worth a loud check in the script. Recorded in `AGENT_FEEDBACK.md`, not
  separately filed.
- **`py` vs `python` PATH split**: this environment's `py` launcher resolved to a Python with no `pytest`
  installed; bare `python` had it. Cost real time on first discovery; every subsequent crew handoff named
  the fallback explicitly and none hit it again.
- **The archive gate's `c2b` bug (#439, above) is the single most important finding of this run outside its
  stated mission** — it means every delegated Commander before this one either force-waived it silently or
  never actually reached a real `advance archive`. Worth checking whether other closed runs' archives show
  the same waive.
- Full retrospective, including what worked (the shared-file fence holding, deliberate-breakage-via-git-stash
  being far more convincing than synthetic-only fixtures) is in `.agent-work/AGENT_FEEDBACK.md`'s
  `2026-08-06 — issue-422-wire-invariants` entry.
