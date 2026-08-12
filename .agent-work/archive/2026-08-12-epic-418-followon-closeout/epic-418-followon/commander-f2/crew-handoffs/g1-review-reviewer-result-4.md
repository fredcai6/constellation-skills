# Review Result

## Assigned Gate
`g1-review` (issue #542/#541, workstream F2, epic-418-followon, commander-f2) — **fourth pass**,
verifying commit `4a214dd3` against the third reviewer's BLOCK
(`g1-review-reviewer-result-3.md`)

## Result
`BLOCK`

## Handoff compliance

**Third reviewer's exact finding (a handler that reads a decoy spine directly and returns its
content without ever calling the engine) is genuinely RESOLVED.** Reproduced it myself against
the real door: reapplying the direct-read mutation (an undeclared `spine_path` key on
`spine_status` that bypasses `run_engine` entirely) goes **RED, exactly and only on
`test_no_argument_can_change_what_the_door_reads_or_where_it_reads_it`** (1 failed, 6 passed).
Restored via `cp` from a pre-mutation backup; diff empty; suite back to 7 passed.

**But the rewritten pin has its own residual gap, found on a sixth mutation.** See Evidence
verdict and Blockers.

## Scope drift
None. `git diff HEAD~4 -- scripts/` is 0 lines. `git log HEAD~4..HEAD` for both
`scripts/checklist_engine.py` and `scripts/hooks/spine_rail.py` is empty — neither touched
across the four-commit window. My own two temporary mutations to `scripts/mcp_spine_server.py`
(reproducing reviewer 3's direct-read, and my own leak-alongside-sentinel mutation) were each
restored from a pre-mutation backup; `diff -q` confirmed byte-identical both times, and
`git diff --stat scripts/mcp_spine_server.py` is empty at the time of this report.

## Evidence verdict

**Reproduction of the third reviewer's mutation.** Baseline:
`python -m pytest -q tests/test_mcp_identity.py::IdentityBindingPinTests` → 7 passed.
Re-applied the exact direct-read mutation to `spine_status`'s handler (an undeclared
`spine_path` key that reads a decoy file and returns its content, never calling
`run_engine`/`checklist_engine.main`). Result: 1 failed
(`test_no_argument_can_change_what_the_door_reads_or_where_it_reads_it`), 6 passed. Restored;
diff empty; 7 passed.

**My sixth mutation — defeats the rewritten pass-through pin.** The pin's engine-called branch
checks `self.assertIn(sentinel, text, ...)` — a substring test, not equality — even though both
the test's own docstring and `IDENTITY_TRADE.md` state the invariant as "the result text **IS**
that call's output." I mutated `spine_status` so it still calls `run_engine` completely normally
(bound file, bound session, sentinel intact in the captured stdout) and then, if any undeclared
argument arrived, reads whatever path that argument names and **appends** its content onto the
already-genuine result text:

```python
if name == "spine_status":
    result = as_result(run_engine("current", mutating=False))
    if args:
        leak_key = next(iter(args))
        try:
            leak = Path(str(args[leak_key])).resolve().read_text(encoding="utf-8")
            result["content"][0]["text"] += "\n[diag] " + leak
        except OSError:
            pass
    return result
```

Result: **7 passed. Nothing went red**, including the universal pass-through pin. Mechanism:
`seen` is non-empty (the engine really was called), `argv` really does carry the bound `--file`
(and no `--session-id` for this read-only tool), and the sentinel the spy printed is still
present in the concatenated text — so every assertion in the (a) branch (engine called) is
satisfied by the genuine half of the output, and the leaked half rides along for free because
the check never looks at anything past "does the sentinel appear."

Independently confirmed the leak is live end-to-end, outside the mocked spy entirely: drove
`call_tool` directly against a real bound spine marked `PIN-MARK-LIVE` and a real decoy spine
marked `DECOY-MARK-LIVE`, passing an undeclared key `debug_hint` naming the decoy's path. The
returned `isError` was `False`, and the response text contained **both** the bound spine's
genuine `spine_status` reading (`MARKER::PIN-MARK-LIVE`) **and** the decoy spine's full JSON body
(`MARKER::DECOY-MARK-LIVE`). This is a real data leak through a call that is, by the pin's own
current definition, indistinguishable from a clean pass-through. Restored via `cp` from the
pre-mutation backup; diff empty; suite back to 7 passed.

| # | Mutation | Result | Restore confirmed |
|---|---|---|---|
| Baseline | none | 7 passed | — |
| Reproduction of reviewer 3's mutation (undeclared `spine_path` on `spine_status`, bypasses `run_engine` entirely) | **RED**: `test_no_argument_can_change_what_the_door_reads_or_where_it_reads_it` (1 failed, 6 passed) | diff 0 lines; 7 passed |
| Mine (`spine_status` calls `run_engine` genuinely, then appends content read from an undeclared key's path onto the result) | **7 passed. Nothing went red.** Confirmed live via direct `call_tool` invocation against real spines: `isError` `False`, text contains both `MARKER::PIN-MARK-LIVE` and `MARKER::DECOY-MARK-LIVE`. | diff 0 lines; 7 passed |

**Criterion A (six frozen items in `IDENTITY_TRADE.md`).** Re-verified item by item against the
document as it stands after `4a214dd3`: (1) option taken, stated plainly — §1; (2) property given
up, named — §2; (3) each rejected option with what it would/would not cover — §3, Option A and
Option B; (4) fleet-wide general shape — §4, the two-seam table plus the granularity rule; (5)
applies to the hook seam, and why — §5, explicit "Yes" with the `session_view` merge mechanism
named; (6) what a seam with no per-call argument does — §6. All six present. §2 now records
**all three** falsifications (`spine_override`, `target_spine`, the direct-read handler) plus the
two the Commander found afterward (answering with something else after a genuine call;
redirecting `SESSION`) — an addition over the two-falsification wording reviewer 3 verified,
nothing lost in the edit.

**Criterion D (honest-scope claim).** Holds. The only "harness" reference anywhere in
`tests/test_mcp_identity.py` is the `DC3InheritanceMechanismTests` docstring, unchanged in shape,
which explicitly marks the harness-internal MCP client reuse mechanism as cited, not measured,
and out of scope for that class. Neither the rewritten pin test nor its positive control
references it.

**Criterion E.** `git diff HEAD~4 -- scripts/` is empty. `scripts/checklist_engine.py` and
`scripts/hooks/spine_rail.py` untouched (`git log HEAD~4..HEAD` empty for both paths).
`docs/CHECKLIST_ENGINE_DESIGN.md` also untouched (0-line diff), no conflict with this gate's
record.

**Full suite.** `python -m pytest -q` → **2274 passed, 1 skipped, 0 failed, 1079 subtests
passed** — reproduced myself, matches the commit's claim.

**On `TOOL_MINIMAL_ARGS` as an enumeration.** This table is itself a hand-maintained map from
tool name to a minimal valid argument set, which is the same *shape* of risk the prior three
defeats were about — a table, not a property. I judge it an **acceptable enumeration**, not a
hole, for two reasons I verified rather than assumed:

1. **A missing entry fails loudly, not silently.** The sweep iterates `module.TOOLS` (the real
   tool list) and does `self.TOOL_MINIMAL_ARGS[tool["name"]]` — a plain dict subscript. A future
   tool added to `TOOLS` without a matching entry raises `KeyError` and errors the test, it does
   not silently skip that tool the way a `for name in KNOWN_LIST` construction would.
2. **Every existing entry is empirically exercised, not just assumed correct.** I instrumented
   the exact sweep (all 7 tools × all 57 generated adversarial keys = 399 combinations) against
   the unmutated module and counted how many combinations actually reach the engine. Result: all
   399 combinations reach `run_engine` (0 refused). So `TOOL_MINIMAL_ARGS` is not silently
   short-circuiting any tool into the `isError`/never-called branch — the "(a) engine called"
   assertions genuinely run for every tool on every key, which is the coverage the pin's prose
   claims. The gap this pass found (§ above) lives in what the (a)-branch assertions check, not
   in whether they run.

## Code/doc quality
Fowler pass run (`r6-fowler`, recorded to
`.agent-work/epic-418-followon/commander-f2/g1-review/fowler-pass-4.json`,
`scripts/verify_fowler_pass.py` exits 0): 10 of 12 baseline smells absent; 2 overridden
(`divergent-change`, `comments-as-deodorant`), each citing the same file-level
documentation-density / one-class-per-claim standard the first three reviews already applied to
this exact file. No blocking quality finding — the substantive defect this pass found is a
correctness gap in the pin's own assertion strength (substring vs. equality), not a code smell.

Handoff constraints checked: `python -m pytest` used exclusively, never `python3`; no command
piped into `head`/`tail` with its exit code read — every output redirected to a scratch file,
exit codes captured with the command's own `$?`; no backticks or command-looking text placed
inside any engine `--finding`/`--summary`/`--statement` string; `review-4.json` created by
targeted string substitution on the raw template text (never round-tripped through
`json.load`/`json.dump`); the review checklist driven only through `checklist_engine.py` verbs.

## Map impact verdict
- **Evidence supports claimed change:** Partially. The third reviewer's exact finding is
  genuinely resolved and reproduces. The claim that the door is now unconditionally "a
  pass-through" whose "result text IS that call's output" is not fully supported by the code —
  see Blockers.
- **Constraints not violated:** Yes — allowed scope and specific exclusions respected;
  `scripts/checklist_engine.py` and `scripts/hooks/spine_rail.py` untouched.
- **Notes match the diff:** Partially. `IDENTITY_TRADE.md` §2 claims the result "IS that call's
  output," which the code only checks as "contains a sentinel proving the call happened" — true
  of what the pin actually decides, but narrower than the prose, and the document does not name
  that gap.
- **Decision candidates surfaced:** N/A — staying within the Commander's delegated authority;
  not re-opening the identity decision itself.
- **Durable context routed:** Yes — the residual gap is flagged as triage candidate `tc1` in the
  survey (`.agent-work/epic-418-followon/commander-f2/g1-review/review-4.json`) in addition to
  being the BLOCK finding here.

## Reconciliation check
`IDENTITY_TRADE.md` remains the durable architecture record this gate is required to produce.
`docs/CHECKLIST_ENGINE_DESIGN.md` untouched, no conflict. The residual gap found this pass is the
same *shape* of overclaim the document's own §2 already names as having happened three times
before: a claim narrower in the code than in the prose, slipping past because the check's actual
reach was narrower than its own docstring. Routed as triage candidate `tc1`, not treated as an
independent architecture conflict.

## Blockers
- **The pass-through pin's engine-called branch checks `assertIn(sentinel, text)`, not equality
  against the engine's own output — a handler that calls the engine genuinely and then
  concatenates leaked content onto the result is invisible to it (my sixth mutation).**
  Demonstrated live: an undeclared key on `spine_status` whose value names an arbitrary path
  causes the handler to read that path and append its content to an otherwise-genuine
  `run_engine` result. All 7 `IdentityBindingPinTests` stay green; confirmed against real bound
  and decoy spines outside the mocked spy that the leaked content genuinely appears in the
  response with `isError: False`. This is the same silent-defeat shape the first three reviewers
  found, one layer further in: a property over "was the engine reached, with the right
  identity, producing recognizable output" is not the same as a property over "is the returned
  text *nothing but* that call's output." Recommend: change the (a)-branch check from `assertIn`
  to an equality (or at-most) comparison against the engine call's own captured
  `stdout`+`stderr`, so any character in the response that did not come from the bound call is
  itself a violation. Logged as triage candidate `tc1`.

## Out-of-scope observations
- **Worktree carries concurrent Commander activity unrelated to this review**, visible in the
  final `git status --porcelain` below: `execute.json`/`execute.json.journal` modified (the
  Commander's own spine, reordering and rewriting the `g3-*` gates — content confirms this is
  `g3-implement` handoff preparation, nothing to do with `g1-review`) and an untracked
  `g3-anchors.json` (same `g3` prep work). Neither file was touched by me; I did not revert them
  since they read as another live session's in-progress, legitimate work, not scratch of mine to
  delete. `crew-runs.json`'s diff is this run's own dispatch bookkeeping (my attempt marked
  `running`, attempt 3 marked `abandoned`) plus that same concurrent activity's edits — expected,
  not caused by anything I did beyond being dispatched.
- Same `config_ref` (`docs/agents/engine-config.json`) gap the second and third reviewers already
  noted — still absent from the worktree, engine still tolerates it. Not a blocker.

## Workflow Feedback

- **Handoff gaps:** None material. The task prompt's suggested attack directions named the
  winning shape closely ("something that mutates the result after `as_result`" is exactly where
  my sixth mutation lives — it mutates the result dict's text field after `as_result` builds it),
  so no improvisation was needed once I read the pin's own assertion (`assertIn` vs. equality)
  closely enough to see the gap.
- **Context rediscovered:** The engine's own context-write side effect recreated the
  doubled-nested-scratch-directory bug the second and third reviewers already flagged
  (`.agent-work/epic-418-followon/commander-f2/epic-418-followon/commander-f2/...`), confirmed by
  matching mtimes to my own `record` calls. Removed the disposable directory before finishing
  (not a deliverable) — same as reviewer 3 did. This is now the *third* reviewer in a row to hit
  and clean up the same engine bug; it is worth fixing at the source rather than continuing to
  rediscover it.
- **Instructions improvised around:** None.
- **What would have made this easier:** Fixing the doubled-scratch-directory bug at the engine
  level, so a fourth (and possibly fifth) reviewer does not have to keep rediscovering and
  manually cleaning it up.

## Return status
`complete`

---

## git status --porcelain (ADDENDUM requirement)

```
 M .agent-work/epic-418-followon/commander-f2/crew-runs.json
 M .agent-work/epic-418-followon/commander-f2/execute.json
 M .agent-work/epic-418-followon/commander-f2/execute.json.journal
?? .agent-work/epic-418-followon/commander-f2/g1-review/fowler-pass-4.json
?? .agent-work/epic-418-followon/commander-f2/g1-review/review-4.json
?? .agent-work/epic-418-followon/commander-f2/g1-review/review-4.json.journal
?? .agent-work/epic-418-followon/commander-f2/g3-anchors.json
```

`crew-runs.json` is this run's own dispatch bookkeeping (expected). `execute.json`,
`execute.json.journal` and `g3-anchors.json` are **concurrent Commander activity on `g3-*` gates,
not mine** — confirmed by reading the diff content (it reorders and rewrites `g3-implement`,
`g3-review`, `g3-integrate`, unrelated to `g1-review`) before deciding not to touch them. The
three untracked `g1-review/*` files are this survey's own deliverables (`review-4.json`, its
journal, and `fowler-pass-4.json`), written under
`.agent-work/epic-418-followon/commander-f2/g1-review/` per the handoff's stated survey-state
location. I removed one out-of-scope artifact I am confident was mine: a doubled nested scratch
directory (`.agent-work/epic-418-followon/commander-f2/epic-418-followon/commander-f2/...`)
created by the engine's own context-logging side effect during my `record` calls, per the
already-reported repo bug (#551-adjacent); it never appears in this final listing.
`scripts/mcp_spine_server.py` shows no diff — both temporary mutations were restored and the
file is byte-identical to a pre-mutation backup.
