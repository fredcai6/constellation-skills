# Reviewer Result — g4: the declared dispatch

## Assigned Gate
`g4` — the dispatch is emitted, not remembered

## Verdict
`APPROVE`

## Survey
Driven end to end through `checklist_engine.py` against `.agent-work/epic-559/c3-lifecycle/g4-review/review.json`
(a locally-authored survey — no per-crew spine was bound; `crew-runs.json`'s own entry for this dispatch records
`"spine": null`, and the inherited `SPINE_FILE`/`SPINE_SESSION` env vars point at the Commander's own outer
`execute.json`, not a g4-scoped checklist — see Workflow Feedback). All 7 items (`r0-context` through `r6-fowler`)
recorded `pass`; consolidated `APPROVE`, 0 findings.

## What to verify — answered in the handoff's order

1. **Does the injected postcondition actually refuse a wrong parent? Is the message correct?** Yes, confirmed
   independently, not by re-running the implementer's fixture. I built my own throwaway fake repo
   (`/tmp/g4review_fake_repo`, `scripts/` symlinked to the real tree) and my own fixture spec declaring
   `[[gate.dispatch]]`, ran the real `scripts/generate_spine.py` against it, then ran the exact emitted command
   against a `crew-runs.json` I wrote by hand:
   - Wrong parent (`admiral-epic-418-followon` declared vs. commander parent expected): **exit 1**, message —
     `gate='g4' role='implementer' declared parent='constellation/epic-559/c3-lifecycle/execute/commander/attempt-1' model='sonnet', but no non-abandoned entry matches -- found: constellation/epic-559/c3-lifecycle/g4/implementer/attempt-1 (parent='admiral-epic-418-followon', model='sonnet')`
     — names the right gate, role, and both the declared and actual values.
   - Matching parent: **exit 0**, names the matching entry.
   Both match the implementer's pasted evidence exactly.

2. **Is the injected check `command`-kind, not `artifact`?** Confirmed directly off the compiled spine JSON:
   `{"id": "c-dispatch-0", ..., "check": {"kind": "command", ...}}`. Grounded in `DESIGN_NOTE.md` §6's
   `### CORRECTION` (`record()` on a survey item evaluates only `command`-kind postconditions), which the
   diff's own comments and `LIFECYCLE_CONTRACT.md` §5 cite correctly.

3. **Is `spec-dispatch-undeclared` honestly a textual match?** Yes. `_DISPATCH_MARKERS` is exactly
   `("run_crew.py", "constellation-implementer", "constellation-reviewer")`, matched by plain substring
   containment against `imperative`. `test_imperative_with_none_of_the_three_markers_stays_invisible` proves
   an imperative phrased without any marker compiles clean. Both the fault message in code and
   `LIFECYCLE_CONTRACT.md` §5 state the narrowing plainly ("this narrows the hole, it does not close it") —
   no line found anywhere claiming the hole is closed.

4. **Is `abandoned` respected via the existing predicate?** Yes.
   `scripts/verify_declared_dispatch.py` line 25: `from run_crew import is_abandoned, load_registry,
   registry_path` — a direct import, not a re-implementation. `find_candidates` filters
   `not is_abandoned(e)` before matching. I independently built the `ACCEPTED_FALSE_ALARM` fixture (an
   abandoned wrong-parent entry plus a correctly-parented second attempt) and ran the emitted command myself:
   **exit 0**, names `attempt-2`, correctly ignoring the abandoned wrong-parent `attempt-1`.

5. **Does the emitted command quote its tokens and anchor its `cd`?** Yes. `_compile_dispatch_entry` builds
   the command with `shlex.quote()` around every `--work-id`/`--gate`/`--role`/`--parent`/`--model` value and
   anchors via the same `_REPO_ROOT_TOKEN` (`"<repo-root>"`) every other compiled check in this generator
   uses — not a bespoke token. `test_command_quotes_a_parent_with_shell_metacharacters` proves a `parent`
   containing `; rm -rf /` round-trips through `shlex.split` as one token.

6. **Nothing shipped moved.** `python scripts/validate_spine.py --sweep --root . | grep -cE '^\s+\['` →
   **23**, reproduced myself, matching the pre-change baseline. Neither `specs/implementer.spine.toml` nor
   `specs/reviewer.spine.toml` declares `[[gate.dispatch]]`.

7. **`not_yet_written` left alone.** `cond.get("not_yet_written")` still reads with bare truthiness at
   `generate_spine.py:511` and `:807` (shifted from the handoff's cited `:424`/`:673` by this diff's own
   insertions earlier in the file — same lines, confirmed by reading them). The missing `newline="\n"` on the
   `Path.write_text` at line 1044 is likewise still absent — both untouched, correctly left for g5.

## Handoff compliance
Full compliance. All 11 close criteria in `g4-implementer-handoff.md` are met and independently reproduced
(not merely read): three VIOLATING spec-shape faults (missing `role`, missing `model`, unresolved parent),
one VIOLATING undeclared-dispatch fault, four registry-mismatch VIOLATING cases (wrong parent, wrong model,
no entry), two INNOCENT cases (clean compile, no-dispatch-no-marker), a populated `ACCEPTED_FALSE_ALARM`,
the `command`-kind shape assertion, the unchanged sweep, and a green suite.

## Scope drift
None. `git diff 386d7635..HEAD --stat` shows exactly the 5 files in the handoff's Allowed Scope:
`scripts/generate_spine.py`, `scripts/verify_declared_dispatch.py` (new), `tests/test_declared_dispatch.py`
(new), `tests/test_generate_spine.py`, `map/INDEX.md` (regenerated). Every specific exclusion —
`scripts/spine_lifecycle.py`, `scripts/mcp_spine_server.py`, `scripts/validate_spine.py`, `DESIGN_NOTE.md` —
diffs empty.

## Evidence verdict
Satisfies the required evidence. Reproduced from scratch in an isolated fixture, not accepted from the
report: the wrong-parent refusal, the abandoned-entry pass-through, a real `generate_spine.py` compile, the
full suite (**2920 passed, 3 skipped, 1121 subtests** — matches claim exactly), and the sweep (**23** —
matches claim exactly, unchanged from the pre-g4 baseline).

## Code/doc quality
Minimal, matches surrounding conventions, and is checked rather than merely documented. Constraints verified
against the diff directly: `checklist_engine.py`/`validate_spine.py` unchanged; `.mcp.json`/`settings.json`/
`docs/agents/*`/`skills/**` untouched; `verify_declared_dispatch.py` performs no writes at all, so the
`encoding="utf-8", newline="\n"` write rule doesn't apply to it, and the diff doesn't touch the file's one
pre-existing write site that still lacks it (line 1044, left for g5). No `git add -A` evidence — the diff is
exactly the 5 allowed files. Fowler pass (below) found nothing to flag.

### Fowler pass
Recorded at `.agent-work/epic-559/c3-lifecycle/FOWLER_PASS.json`; `scripts/verify_fowler_pass.py` exits 0
(`smells=12, flagged=[], overridden=['data-clumps', 'primitive-obsession', 'comments-as-deodorant']`). I spot
-checked the record against the diff myself rather than trusting it outright: `duplicated-code`'s claim (zero
`json.loads` re-parsing) is independently asserted by the diff's own test; `data-clumps`/`primitive-obsession`'s
cited precedent (`run_crew.py`'s `active_duplicate(entries, work_id, gate, role, worktree)` /
`find_entry(entries, name)`) exists exactly as described. No smell was flagged; all three overrides carry a
logged repo standard and a reason specific to this diff, not a shrug.

## Map impact verdict
- **Evidence supports claimed change:** yes — `capability:declared-dispatch` and the new module's 3 entities
  (`find_candidates`, `check_declared_dispatch`, `main`) match what's actually in the file.
- **Constraints not violated:** yes — see Scope drift and Code/doc quality above.
- **Notes match the diff:** yes — no missing or overstated structural claim found.
- **Decision candidates surfaced:** `decision:dispatch-is-checked-data` correctly moved from `@grade: guess`
  to `settled/measured`, pinned by the wrong-parent fixture (a real test, not an assertion).
- **Durable context routed:** the one residual (`spec-dispatch-undeclared`'s textual detection) is named as
  accepted in both `LIFECYCLE_CONTRACT.md` §5 and the implementer's result, not silently dropped, and
  correctly not re-raised as a fresh triage candidate since the contract already owns it.

## Reconciliation check
No structural/contract divergence requiring Commander reconciliation beyond what `LIFECYCLE_CONTRACT.md` §5
already scopes.

## Blockers
- none

## Out-of-scope observations
- none

## The single most likely way this gate produces a green run that is wrong

The injected postcondition's oracle is `crew-runs.json`, and that file's `parent`/`model` fields are written
by whatever *dispatched* the crew, not verified against anything independent — `verify_declared_dispatch.py`
proves the recorded identity matches the *declared* one, never that the recorded identity is *true*. A
dispatcher that types the right `--parent`/`--model` flags but launches into the wrong worktree, or a
`run_crew.py` invocation whose registry write itself has a latent bug, would write a `crew-runs.json` entry
that satisfies this check while still being wrong in a way this gate cannot see — the check closes exactly
the "forgot to pass `--parent`" defect it was built for, and nothing upstream of the registry write.

## Workflow Feedback

- **Handoff gaps:** none blocking. The seven-item verify order mapped cleanly onto independently-reproducible
  fixtures.
- **Context rediscovered:** the inherited `SPINE_FILE`/`SPINE_SESSION` environment (`execute.json` /
  `constellation/epic-559/c3-lifecycle/execute/commander`) is the Commander's own outer spine, not a
  g4-reviewer-scoped checklist — confirmed by reading `crew-runs.json`'s own entry for this dispatch, which
  records `"spine": null"`. Calling `spine_survey_result` against that binding is refused (`"record is for
  survey checklists; use advance"` — `execute.json` is `gated`), and one such refusal was already recorded
  against `execute.json`'s `refusals` counter (3→4) before I understood the binding and switched to
  authoring my own survey via the CLI at `.agent-work/epic-559/c3-lifecycle/g4-review/review.json`, matching
  the g1/g2/g3-review precedent already on disk. That refusal is a harmless side effect (a counter increment
  on the parent's own tracking file, not a content change) but it is a real, self-inflicted modification to a
  tracked file I did not intend — worth a Commander note since the skill's "spine bound vs. author your own"
  branching text does not warn that a *stale, mis-scoped* binding can look bound while actually pointing
  elsewhere.
- **Instructions improvised around:** same as above — the reviewer skill's default posture assumes
  `SPINE_FILE`/`SPINE_SESSION` being set means a crew-scoped spine is genuinely bound; here it was inherited
  parent-process environment. I fell back to the skill's "no spine bound, author `REVIEW_SURVEY.template.json`"
  branch, which was the correct path once recognized.
- **What would have made this easier:** a documented tell (e.g. checking `crew-runs.json`'s own `"spine"`
  field for this dispatch, as I ended up doing) for distinguishing a genuinely-bound crew spine from an
  inherited-but-irrelevant one, before the first engine call rather than after a refused one.

## Return status
`complete`
