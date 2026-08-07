# REVIEW_RESULT — issue-106 / g2 (runner core + agent-free unit tests)

Session: `constellation/issue-106/g2/reviewer/attempt-1`
Worktree: `C:\Programs\constellation-wt-106` (branch `constellation/issue-106`)
Review target: the UNCOMMITTED working tree — `scripts/run_skill_eval.py` (new),
`tests/test_run_skill_eval.py` (new), `.gitignore` (+3 lines / one sanctioned rule).

## VERDICT: APPROVE

Every close-criterion reproduced independently. The Commander-flagged `classify_run`
point is ruled INTENDED-BY-CONTRACT (not a deviation); g1 is NOT reopened. One
inbound constraint is recorded for g4/g5 and one non-blocking forward note for g3.

## Evidence I reproduced myself (not taken on trust)
- `py -m pytest tests/test_run_skill_eval.py -q` => **41 passed** in 1.90s.
- `py -m pytest -q` => **508 passed, 2 skipped, 152 subtests passed** in 15.73s
  (matches the Commander's 508/2).
- `git status --porcelain` => only ` M .gitignore`, `?? scripts/run_skill_eval.py`,
  `?? tests/test_run_skill_eval.py`. No out-of-scope file touched.
- `git check-ignore` on both deliverables => exit 1 (NOT ignored) — they will commit.
- `.gitignore` diff = exactly the sanctioned defensive `evals/**/_runs/` rule.
- CLI end-to-end with a *biting* completion check: `--dry-run` => `VERDICT: PASS
  (exit 0)`; `--dry-run-fail` => `VERDICT: FAIL (exit 1)` (completed=3 passed=0
  fenced=0 — a completed-fail, never fenced).
- Agent-free guard BITES: I ran the guard body against `['claude','-p','hi']` and
  `['C:/x/claude.exe','-p','hi']` — both raised AssertionError ("blocked real agent
  subprocess"). The fixture is autouse and wraps the module-global `subprocess.run`
  that `run_check` (and any live seam) uses. No test file executes a claude
  subprocess (the only `subprocess.*` references are inside the guard itself; the
  literal `"claude"` appears only in pure `build_eval_argv` list-construction and in
  the inert-stub NotImplementedError assertion).

## Per-check findings
1. **Pure logic matches the frozen contract — PASS.** directory-is-schema
   (`checks/*.py` globbed non-recursively so `checks/answer/*.py` cannot leak into
   the gate), N=2/M=3/timeout=1800 defaults, sha256 corpus provenance with
   `CORPUS.json` excluded from its own hash, `--dry-run`/`--dry-run-fail` riding the
   same injectable `launch=`/`installer=` seams the unit layer uses. Seams resolve
   at call time (run_crew pattern). `launch_agent`/`temp_install` are inert
   `NotImplementedError("... g3")` stubs.
2. **Tests are AGENT-FREE, mechanically — PASS.** See guard reproduction above.
3. **Known-BAD FAIL / known-GOOD PASS — PASS.** The unit falsification floor
   (`test_dry_run_fail_exits_one`, `test_dry_run_fail_is_completed_fail_not_fenced`)
   uses `PASS_CHECK`, which actually inspects `workspace/eval-complete.txt` and
   exits 1 when absent; `dry_run_fail_launch` omits that artifact, so the check
   genuinely bites. The known-good path scores PASS. This is a *biting* fixture —
   the critical precondition for the ruling below.
4. **Verdict math — PASS.** 2/3=>PASS(0), 1/3=>FAIL(1), 1 completed + 2 fenced =>
   INCONCLUSIVE(2), all-fenced => INCONCLUSIVE. Asserted and green.
5. **Infra-fence — PASS.** timeout and any usage/rate/quota/overloaded/429 stderr
   marker => `inconclusive`, EXCLUDED from the tally; distinct from `completed-fail`.
   Environment flake can only ever yield INCONCLUSIVE, never FAIL a good corpus.
6. **Structural T3 — PASS.** The gate reads ONLY `checks/*.py`; `checks/answer/*.py`
   are executed and recorded but appended AFTER classification so they can never
   move the verdict (`test_answer_only_failure_still_passes`). Zero process checks
   is a hard config error at load AND via CLI (exit 3).
7. **Full suite green — PASS** (508/2, reproduced).

## Ruling on the SPECIFIC REVIEW FOCUS (classify_run / exit_code==0 == "completed")

**APPROVE — this matches the intended contract; it is NOT a deviation. g1 is NOT
reopened.** I reproduced the Commander's finding exactly: a *vacuous* process check
(one that exits 0 without inspecting the workspace) makes `--dry-run-fail` return
`VERDICT: PASS (exit 0)` even though the workspace has no completion artifact. So
the falsification floor is genuinely check-dependent. But the contract intends
precisely this delegated-verification design — interpretation #1 in the handoff —
and I cite the text:

- Contract §(i) infra-fence table, row `completed-fail`: *"agent completed (**incl.
  exit 0 with no spine terminal**), a process check failed → yes → fail."* The
  contract itself classifies an exit-0 run with NO completion/spine terminal as
  **completed**, and makes its pass/fail turn on **a process check**, not on the
  runner's own completion probe. `classify_run` implements this verbatim
  (`completed = (completion_present and completion_fresh) or (exit_code == 0)`; then
  pass iff all process checks pass). The `_probe_completion` result is used only for
  the completed-vs-errored liveness split, exactly as the contract's table draws it.
- Contract §(a): the ONLY structural vacuous-PASS hole the contract closes is
  *"zero process checks is a hard config error"* — it does not promise to catch a
  check that is present-but-non-biting. The plain-scripts design (contract §(b):
  "a script whose only input is a directory and whose only output is an exit code")
  deliberately puts completion/spine verification in the SCENARIO's process checks.
- Contract §"`--dry-run`/`--dry-run-fail`": *"`--dry-run-fail` is the FLOOR and the
  live broken corpus is the CEILING … Neither is a substitute for the live
  acceptance run."* The design explicitly acknowledges the floor is check-dependent
  and defers the real proof to g5's live broken-variant falsification.

Because the runner's completion probe is liveness-only by design, this correctly
APPROVES **only** because precondition (a) holds — the unit known-bad fixture uses
a check that genuinely bites. It does.

### Inbound constraint recorded for g4 / g5 (binding)
- **g4** MUST author at least one process check per scenario that genuinely inspects
  the workspace for completion/spine (e.g. asserts the terminal artifact and/or
  spine.json terminal state exists). A scenario whose process checks do not actually
  inspect the workspace would silently PASS a broken run — the runner will not catch
  it, by contract.
- **g5**'s live broken-variant falsification MUST run against biting checks; a
  vacuous check would make the live falsification meaningless. The g5 acceptance is
  the CEILING that the check-dependent floor cannot substitute for.

## Non-blocking forward note for g3 (not a g2 blocker)
The autouse guard wraps `subprocess.run`. If g3's real `launch_agent` spawns via
`subprocess.Popen` (or `os.exec*`) rather than `subprocess.run`, the current guard
would not intercept it. Adequate for g2 (launch_agent is inert and never called),
but g3 should either implement `launch_agent` on top of `subprocess.run` or extend
the guard to also wrap `Popen`, so the mechanical agent-free guarantee keeps holding
once the live seam exists. (The implementer already flagged the `LaunchOutcome` flag
surface `launch_agent` must populate for the fence to fire — consistent.)

## Out-of-scope observations
None touched. `install_constellation.py`/`run_crew.py` are imported/read only;
`_hash_file`/`_source_commit` reused, never edited. No edits to other skills,
`_shared/`, install bundles, real `evals/<name>/` scenarios, or live launch wiring.
The importlib `sys.modules` pre-registration of `install_constellation` before
`exec_module` is import-only (needed by the 3.12+ dataclass KW_ONLY probe) and does
not mutate the source file.

## Blockers
None.

## Workflow feedback
The handoff's SPECIFIC REVIEW FOCUS was precisely the load-bearing call and pointed
me straight at the contract text that settles it; pre-flagging the empowerment to
reopen g1 (with the two-interpretation fork) made the ruling a citation exercise
rather than a judgment call in the dark. The implementer result's Assumptions
section correctly pre-disclosed the exit-0-completed behavior, which matched what I
reproduced — good honesty. Recommend the Commander carry the g4/g5 biting-check
constraint above into those gates' handoffs verbatim, since the APPROVE is
conditional on it.

Target postcondition satisfied: `g2-integrate.c1` (full suite green, 508/2) +
`g2-integrate.c2` (this APPROVE verdict).
