# Review Result

## Assigned Gate
`g1-review` (issue #542/#541, workstream F2, epic-418-followon, commander-f2) — **third pass**,
verifying commit `c8a9b58c` against the second reviewer's BLOCK
(`g1-review-reviewer-result-2.md`)

## Result
`BLOCK`

## Handoff compliance

**Second reviewer's exact finding (runtime pin was a five-key enumeration on one tool,
defeated by an undeclared `target_spine`).** Genuinely RESOLVED for that exact defeat.
Reproduced it myself against the real door: reapplying the `target_spine` mutation to
`spine_status` goes **RED, exactly and only on
`test_no_argument_can_change_the_identity_the_engine_is_addressed_with`** (1 failed, 6
passed). Restored via `git checkout`; diff empty; suite back to 7 passed.

**But the fix has its own residual gap, found on the fifth mutation.** See Evidence
verdict and Blockers.

## Scope drift
None. `git diff HEAD~3 -- scripts/` is 0 lines. `scripts/checklist_engine.py` and
`scripts/hooks/spine_rail.py` both untouched across the three-commit window (`git log
HEAD~3..HEAD` for each path is empty). My own two temporary mutations to
`scripts/mcp_spine_server.py` (the `target_spine` reproduction and my own `spine_path`
bypass) were each restored; the file is byte-identical to a pre-mutation backup after the
run.

## Evidence verdict

**Reproduction of the second reviewer's mutation.** Baseline:
`python -m pytest -q tests/test_mcp_identity.py::IdentityBindingPinTests` → 7 passed.
Re-applied `target_spine` to `spine_status`'s handler exactly as the second reviewer's
result described it. Result: 1 failed (
`test_no_argument_can_change_the_identity_the_engine_is_addressed_with`), 6 passed.
Restored; diff empty; 7 passed.

**My fifth mutation — defeats the universal runtime pin.** The pin
(`test_no_argument_can_change_the_identity_the_engine_is_addressed_with`) patches
`checklist_engine.main` with a spy lambda, drives every tool with every generated
adversarial key, and only asserts **inside a loop over the captured argv list**. That loop
body never runs if the handler never calls the engine at all. I mutated `spine_status`
so an undeclared `spine_path` key — one of the generator's own adversarial keys (marker
`spine` crossed with affix `_path`, not a name I invented) — makes the handler read a
**decoy spine file directly** and return its content, without ever calling `run_engine`
or `checklist_engine.main`:

```python
if name == "spine_status":
    if args.get("spine_path"):
        peek = Path(args["spine_path"]).resolve()
        data = json.loads(peek.read_text(encoding="utf-8"))
        imperative = data["tasks"]["g1"]["imperative"]
        return {"content": [{"type": "text", "text": f"PEEK: {imperative}"}], "isError": False}
    return as_result(run_engine("current", mutating=False))
```

Result: **7 passed. Nothing went red**, including the universal pin. Independently
confirmed the redirect is live, not an inert no-op the test correctly ignored, by driving
`call_tool` directly outside the suite against a bound spine marked `PIN-MARK` and a decoy
marked `DECOY-MARK`: the response text was `PEEK: MARKER::DECOY-MARK`, never the bound
content. Restored via `git checkout`; diff empty; file byte-identical to a pre-mutation
backup; suite back to 7 passed.

| # | Mutation | Result | Restore confirmed |
|---|---|---|---|
| Baseline | none | 7 passed | — |
| Reproduction of 2nd reviewer's mutation (`target_spine` on `spine_status`) | **RED**: `test_no_argument_can_change_the_identity_the_engine_is_addressed_with` | diff 0 lines; 7 passed |
| Mine (undeclared `spine_path` on `spine_status`, bypasses `run_engine` entirely) | **7 passed. Nothing went red.** Confirmed live via direct `call_tool` invocation: reads `PEEK: MARKER::DECOY-MARK`. | diff 0 lines; 7 passed |

**Criterion A (six frozen items in `IDENTITY_TRADE.md`).** Re-verified item by item:
(1) option taken — §1; (2) property given up, named — §2; (3) both rejected options with
what each would/would not cover — §3 (Option A, Option B); (4) fleet-wide general shape —
§4 with the two-seam table; (5) applies to the hook seam, and why — §5, explicit "Yes";
(6) what a seam with no per-call argument does — §6. All six present. **Both**
falsifications (the first reviewer's `spine_override`, the second reviewer's
`target_spine`) are now recorded in §2 — an addition over the prior single-falsification
wording, nothing lost in the edit.

**Criterion D (honest-scope claim).** Holds. The only "harness" reference in the whole
test file is the `DC3InheritanceMechanismTests` docstring, which explicitly marks the
harness-internal MCP client reuse mechanism as cited, not measured, and out of scope for
that class. Neither new test in the rework
(`test_no_argument_can_change_the_identity_the_engine_is_addressed_with`,
`test_the_universal_runtime_pin_can_fail`) references it.

**Criterion E.** `git diff HEAD~3 -- scripts/` is empty. `scripts/checklist_engine.py` and
`scripts/hooks/spine_rail.py` untouched.

**Full suite.** `python -m pytest -q` → **2274 passed, 1 skipped, 0 failed, 1079 subtests
passed** — reproduced myself, matches the commit's claim.

## Code/doc quality
Fowler pass run (`r6-fowler`, recorded to
`.agent-work/epic-418-followon/commander-f2/g1-review/fowler-pass-3.json`,
`scripts/verify_fowler_pass.py` exits 0): 10 of 12 baseline smells absent; 2 overridden
(`divergent-change`, `comments-as-deodorant`), each citing the same repo standard the
first two reviews already applied to this exact file. No blocking quality finding — the
substantive defect this pass found (see Blockers) is a correctness gap in the pin's
coverage, not a code smell.

Handoff constraints checked: `python -m pytest` used exclusively, never `python3`; no
command piped into `head`/`tail` with its exit code read — every output redirected to a
file, exit codes captured with the command's own `$?`; no backticks or command-looking
text placed inside any engine `--finding`/`--summary`/`--statement` string; the review
checklist JSON driven only through `checklist_engine.py` verbs, never hand-edited.

## Map impact verdict
- **Evidence supports claimed change:** Partially. The second reviewer's exact finding is
  genuinely resolved and reproduces. The claim that the pin is now "the property itself"
  is not fully supported — see Blockers.
- **Constraints not violated:** Yes — allowed scope and specific exclusions respected;
  `scripts/checklist_engine.py` and `scripts/hooks/spine_rail.py` untouched.
- **Notes match the diff:** Partially. `IDENTITY_TRADE.md` §2 now claims "whatever
  arguments arrive, the engine is always addressed with the bound `--file`" — true of
  what the pin actually checks, but the pin only checks calls that reach the engine at
  all, and the document does not name that boundary.
- **Decision candidates surfaced:** N/A — staying within the Commander's delegated
  authority; not re-opening the identity decision.
- **Durable context routed:** Yes — the residual gap is flagged as triage candidate `tc1`
  in the survey (`.agent-work/epic-418-followon/commander-f2/g1-review/review-3.json`) in
  addition to being the BLOCK finding here.

## Reconciliation check
`IDENTITY_TRADE.md` remains the durable architecture record this gate is required to
produce. No conflict with `docs/CHECKLIST_ENGINE_DESIGN.md`, untouched by this rework.
The residual gap found this pass is the same *shape* of overclaim the document's own §2
already names as having happened twice — a claim narrower than intended slipping past
because the pin's actual reach was narrower than its prose. Routed as triage candidate
`tc1`, not treated as an independent architecture conflict.

## Blockers
- **The universal runtime pin only checks calls that reach the engine; a handler that
  answers without reaching it is invisible to it (my mutation 5).** Demonstrated live: an
  undeclared `spine_path` key on `spine_status` reads a decoy spine file directly and
  returns its content, never calling `run_engine`/`checklist_engine.main`. All 7
  `IdentityBindingPinTests` stay green. This is the same silent-defeat shape the first two
  reviewers found, one layer down: an enumeration of *tools* and *keys* is not the same as
  a property over *every code path in `call_tool`*. Recommend one of: (a) widen the pin to
  also assert that `call_tool` **always** reaches `run_engine` at least once per call (a
  handler that returns without doing so should itself be a violation, not a silent pass),
  or (b) route every `call_tool` branch through a single choke point that is provably the
  only way to produce a `content` result, so "never touches `--file`" cannot arise by
  construction. Logged as triage candidate `tc1`.

## Out-of-scope observations
- None beyond the blocker above.

## Workflow Feedback

- **Handoff gaps:** None material. The ADDENDUM's ask (report `git status --porcelain`)
  surfaced a genuine finding of its own: this worktree started dirty (two files modified
  by the Commander's own crew-run bookkeeping, before I touched anything) and the engine's
  own context-logging side effect recreated the exact doubled-nested-scratch-directory bug
  the second reviewer already flagged in their own Workflow Feedback
  (`.agent-work/epic-418-followon/commander-f2/epic-418-followon/commander-f2/...`), even
  though I set `work_id` to match the survey file's own directory path exactly as that
  reviewer recommended. The doubling is not about `work_id` matching the directory path;
  something else in the engine's context-write path is prefixing `.agent-work/<work_id>/`
  onto a path that is already rooted at `.agent-work/<work_id>/g1-review/`. Removed the
  disposable directory before finishing (not a deliverable); worth a repo issue so a
  fourth reviewer does not rediscover it a third time.
- **Context rediscovered:** Same `config_ref` (`docs/agents/engine-config.json`) gap the
  second reviewer already noted — still absent from the worktree, engine still tolerates
  it. Not a blocker.
- **Instructions improvised around:** None — the handoff's four suggested attack shapes
  named the winning one almost exactly ("a redirect that never touches `--file` but
  reaches another spine some other way"), so no improvisation was needed once I read the
  pin's own implementation closely enough to see the `for argv in seen:` loop's silent
  empty-case.
- **What would have made this easier:** Nothing concrete — this handoff was unusually
  well-aimed for a third pass.

## Return status
`complete`

---

## git status --porcelain (ADDENDUM requirement)

```
 M .agent-work/epic-418-followon/commander-f2/crew-handoffs/g1-review-handoff.md
 M .agent-work/epic-418-followon/commander-f2/crew-runs.json
?? .agent-work/epic-418-followon/commander-f2/g1-review/fowler-pass-3.json
?? .agent-work/epic-418-followon/commander-f2/g1-review/review-3.json
?? .agent-work/epic-418-followon/commander-f2/g1-review/review-3.json.journal
```

The two modified files (`g1-review-handoff.md` carrying the ADDENDUM, `crew-runs.json`
recording this attempt's dispatch) were **already dirty when I started** — confirmed by
running `git status --porcelain` as my very first command, before any tool use, and both
diffs are Commander/dispatcher bookkeeping, not anything I wrote. The three untracked
files are this survey's own deliverables (`review-3.json`, its journal, and
`fowler-pass-3.json`), written under `.agent-work/epic-418-followon/commander-f2/g1-review/`
per the handoff's stated survey-state location, not orphan scratch at the worktree root.
`scripts/mcp_spine_server.py` shows no diff — both temporary mutations were restored and
the file is byte-identical to a pre-mutation backup.
