# IMPLEMENTER_RESULT — g4 (pilot Euler scenarios + bar README)

Session: constellation/issue-106/g4/implementer/attempt-1
Worktree: C:\Programs\constellation-wt-106 (branch constellation/issue-106)
Status: COMPLETE — all close criteria met.

## Scenarios authored (3, graded difficulty)

| scenario | Euler # | difficulty | answer (advisory) |
|---|---|---|---|
| `evals/euler-1-multiples` | #1 multiples of 3/5 < 1000 | easy | 233168 |
| `evals/euler-2-even-fibonacci` | #2 even Fibonacci < 4,000,000 | easy–medium | 4613732 |
| `evals/euler-5-smallest-multiple` | #5 divisible by 1..20 | medium | 232792560 |

Each follows the frozen directory-is-schema exactly: `task.md`, `checks/*.py` (3
biting process checks), `checks/answer/answer_matches.py` (advisory), `fixture/README.md`.
No `scenario.toml` (defaults n=2/m=3/model=sonnet/timeout=1800 used).

## Files created (19)

```
evals/README.md
evals/euler-1-multiples/task.md
evals/euler-1-multiples/fixture/README.md
evals/euler-1-multiples/checks/spine_completed.py
evals/euler-1-multiples/checks/artifact_present.py
evals/euler-1-multiples/checks/tests_green.py
evals/euler-1-multiples/checks/answer/answer_matches.py
evals/euler-2-even-fibonacci/{task.md, fixture/README.md, checks/{spine_completed,artifact_present,tests_green}.py, checks/answer/answer_matches.py}
evals/euler-5-smallest-multiple/{task.md, fixture/README.md, checks/{spine_completed,artifact_present,tests_green}.py, checks/answer/answer_matches.py}
```
The three process checks are byte-identical across scenarios; only `answer_matches.py`
(known answer) and `task.md`/`fixture` (problem text) differ.

## _run_once inspection confirmation (where the runner puts things)

Read `scripts/run_skill_eval.py::_run_once` (lines 528–583) + `dry_run_launch` /
`dry_run_fail_launch` (472–498). Confirmed and my checks target exactly these:
- Check invocation: `run_check` → `python checks/<name>.py <run-dir>` where **run-dir =
  `<temp>/run-<index>/`**. So `sys.argv[1]` is the run-dir; the workspace is
  `<run-dir>/workspace/`.
- Corpus is copied to `<run-dir>/workspace/.claude/skills` — my artifact/tests/answer
  checks EXCLUDE `.claude/` (and `.agent-work/`, `.git/`) so bundled corpus `.py`
  files and `*_SPINE.template.json` can never satisfy a check (verified: a template
  spine under `.claude/` did NOT satisfy `spine_completed`).
- Completion sentinel probed at `<run-dir>/workspace/eval-complete.txt`.
- `spine.json` is written by the dry launchers at `workspace.parent/spine.json` =
  **`<run-dir>/spine.json`** (dry-run `{"status":"done"}`; dry-run-fail
  `{"status":"in-progress"}`). `spine_completed` reads that path AND globs
  `<run-dir>/workspace/**/.agent-work/**/spine.json` for a live engine run, parsing
  the status (simple `{"status":...}` OR engine `{"tasks":{id:{status}}}` all-complete).

The two signals that differ between the dry-run pass/fail workspaces are (1) sentinel
presence and (2) spine status; every check keys genuinely off workspace state so each
one bites.

## Per-scenario evidence (pasted)

### evals/euler-1-multiples
```
$ python scripts/run_skill_eval.py --dry-run evals/euler-1-multiples
VERDICT: PASS (exit 0)
  completed=3 passed=3 fenced=0
  corpus_id=sha256:8d454566485c0cb9b32b35e6f3eba4617ebe1d38f8ecd2fe88b0ee5091128ffd
dry-run EXIT=0
$ python scripts/run_skill_eval.py --dry-run-fail evals/euler-1-multiples
VERDICT: FAIL (exit 1)
  completed=3 passed=0 fenced=0
dry-run-fail EXIT=1
```

### evals/euler-2-even-fibonacci
```
$ python scripts/run_skill_eval.py --dry-run evals/euler-2-even-fibonacci
VERDICT: PASS (exit 0)
  completed=3 passed=3 fenced=0
dry-run EXIT=0
$ python scripts/run_skill_eval.py --dry-run-fail evals/euler-2-even-fibonacci
VERDICT: FAIL (exit 1)
  completed=3 passed=0 fenced=0
dry-run-fail EXIT=1
```

### evals/euler-5-smallest-multiple
```
$ python scripts/run_skill_eval.py --dry-run evals/euler-5-smallest-multiple
VERDICT: PASS (exit 0)
  completed=3 passed=3 fenced=0
dry-run EXIT=0
$ python scripts/run_skill_eval.py --dry-run-fail evals/euler-5-smallest-multiple
VERDICT: FAIL (exit 1)
  completed=3 passed=0 fenced=0
dry-run-fail EXIT=1
```

**All 3 scenarios: `--dry-run` EXIT 0, `--dry-run-fail` EXIT 1.** The binding
constraint (checks must bite) is met suite-wide.

## Per-check biting proof (each of the 3 process checks bites individually)

On a captured broken run-dir (`--dry-run-fail --keep-temp`), EACH process check
returns non-zero (not just the aggregate):
```
-- spine_completed --  FAIL: found 1 spine(s) but none reached a terminal/complete state   EXIT=1
-- artifact_present -- FAIL: no non-empty solution .py and no completion sentinel           EXIT=1
-- tests_green --      FAIL: no test file written and no completion sentinel                EXIT=1
```
On a captured passing run-dir (`--dry-run --keep-temp`), each returns 0; the advisory
`answer_matches` returned EXIT=1 ("not observed") yet the verdict was still PASS —
confirming answer checks are recorded but non-gating (structural T3).

## Live-run primary-branch proof (checks are not merely sentinel-driven)

Fabricated a live-like run-dir (real `solution.py` + `test_solution.py` + engine-form
terminal spine under `workspace/.agent-work/`, and NO sentinel):
```
-- spine_completed --  PASS: terminal spine at .../workspace/.agent-work/issue-x/spine.json   EXIT=0
-- artifact_present -- PASS: non-empty solution file solution.py                              EXIT=0
-- tests_green --      PASS: pytest green over 1 test file(s)                                  EXIT=0
-- answer_matches --   ADVISORY: known answer 233168 observed (non-gating)                     EXIT=0
NEGATIVE (red test): tests_green FAIL: pytest exit 1 over 1 test file(s)                       EXIT=1
```
The corpus template spine under `.claude/` was correctly ignored; a red test correctly
FAILs `tests_green`.

## Other required evidence

```
$ py -m pytest -q
513 passed, 2 skipped, 152 subtests passed in 15.59s
```
```
$ git check-ignore evals/euler-1-multiples/task.md; echo $?
1                      # evals/ is committed, not ignored
$ git check-ignore evals/euler-1-multiples/_runs/x; echo $?
0                      # _runs/ correctly ignored (defensive .gitignore)
```
`git check-ignore` returns EXIT 1 (committed) for README.md, task.md, a process check,
and an answer check.

## README coverage checklist (evals/README.md)

- [x] Situational bar transcribed **verbatim** ("new skill or behavior-changing
      rewrite → ≥1 scenario execution (itself N sub-runs) before install; mechanical
      edits → existing suite + git review; nothing gates on evals. No Iron Law.")
- [x] How to run (`python scripts/run_skill_eval.py evals/<name>`) + exit-code table
      (0 PASS / 1 FAIL / 2 INCONCLUSIVE / 3 error)
- [x] N-of-M = regression-vs-variance smoke, NOT a statistical guarantee (§(iii))
- [x] Limitation 1: dry-run-fail is a FLOOR not a ceiling (subtle regression can pass)
- [x] Limitation 2: Euler exercises workflow machinery, not architecture judgment →
      portfolio must diversify
- [x] Named next scenario (NOT built): the delegated-commander selection scenario
      (cluster F's first non-Euler pilot)
- [x] Transcripts kept for diagnosis, never judged by the runner

## Assumptions

- **Sentinel-as-dry-run-stub.** The frozen `dry_run_launch` synthesizes only the
  completion sentinel + terminal spine (no solution/test files). So `artifact_present`
  and `tests_green` validate the real deliverable as the PRIMARY branch and accept the
  completion sentinel `eval-complete.txt` as the contract-sanctioned "stub artifact"
  FALLBACK at the agent-free floor. This is required by the frozen runner (a check
  that strictly demanded `solution.py` could not pass `--dry-run`) and is aligned with
  the contract's explicit "floor vs ceiling" split — the residual "sentinel written
  without a real solution" hole is exactly what g5's live broken-variant CEILING
  covers. Documented in each check's docstring and in README limitation 1.
- Live runs are expected to have `pytest` importable; `tests_green` runs pytest only
  against discovered test paths (never the corpus).

## Stop conditions / scope

- No stop condition hit. The run-dir contract was inspectable by plain checks with NO
  runner change — no reopen of g1/g3 required.
- Scope respected: created only under `evals/**` + `evals/README.md`. Did not touch
  the runner, tests, other skills, `_shared/`, or install bundles; did not wire evals
  into pytest collection; did not build the delegated-commander selection scenario
  (only named it).

## Out-of-scope observations (not acted on)

- The dry-run/dry-run-fail launchers only vary the sentinel + spine status, so the
  agent-free floor cannot exercise the `solution.py`/`pytest` primary branches — those
  are proven here by hand-fabricated run-dirs and will be exercised for real at g5.
  If the curator later wants the floor to also cover the primary branches, a future
  runner enhancement could have `dry_run_launch` synthesize a stub `solution.py` +
  passing `test_*.py`. Not needed now; noted for portfolio-growth work.

## Workflow feedback

- The handoff's pointer to read `_run_once` FIRST was decisive: the handoff prose said
  the spine lives "under the workspace's `.agent-work/**`", but the frozen dry-run
  launchers actually write it at `<run-dir>/spine.json`. Reading the code resolved the
  discrepancy; `spine_completed` handles both locations. Worth flagging that the
  handoff prose and the runner's dry-run location differed.
- The biting requirement is genuinely subtle given the fixed dry-run scaffold: the only
  two discriminating signals are sentinel-presence and spine-status. Building all three
  checks to bite (rather than the minimum of one) required keying each on a genuine
  workspace signal. Verified per-check, not just in aggregate.
```
