# Implementation Result

## Assigned gate
`g1-implement`

## Completed slice
Added exactly one new `ubuntu-latest` job (`test-linux`) to `.github/workflows/ci.yml`,
alongside the existing `test` (windows-latest) job, mirroring its steps — checkout,
`setup-python` at `3.12`, install `pytest`+`coverage`, the MCP-door smoke test, the full
`pytest tests/ -q --junitxml=junit-report.xml` run, the skip guard, and the coverage floor
— omitting the `defaults.run.shell: bash` block (unneeded on ubuntu's default bash shell).
Then performed and captured a local red-proof: an uncommitted, deliberately-broken mutation
to one test in `tests/`, ran the exact command the new job's "Run full test suite" step runs
(narrowed with `-k` to keep it fast), captured the specific failing assertion text, reverted
the mutation, verified the revert with `git diff --quiet -- tests/`, and re-ran the same
command green.

## Scope
**Files changed:**
- `.github/workflows/ci.yml`

**Specific exclusions touched:** no — `on:` triggers, the `env:` block, and the
`windows-latest` job's steps are byte-for-byte unchanged (confirmed by `git diff`, which
shows only an addition after the existing job, no deletions/modifications elsewhere). No
matrix strategy, second workflow file, branch protection, or required-checks config was
added.

## Behavior changed
Yes — CI now also runs the full test/skip-guard/coverage-floor gate on `ubuntu-latest`, in
addition to the existing `windows-latest` job. No trigger, gating, or existing-job behavior
changed.

## Map Impact
Skipped — trivial, well-scoped CI-config addition mirroring an existing job; no structural,
capability, constraint, or decision impact beyond what the handoff's Map Anchors already
named (the repo map is DEGRADED-UNPARSEABLE for workflow YAML and does not cover this file).

## Test mode
**Required:** `evidence-only` (inspection-only / local-command-parity, per the handoff's Test
Mode — CI configuration, not application code with its own test suite).
**Satisfied:** yes — (a) diff inspection confirms the new job is a faithful mirror of the
existing job's steps, minus the unneeded shell override; (b) the new job's commands were
proven able to both fail (with a specific named assertion) and pass locally, since this
worktree is Linux and can execute what the `ubuntu-latest` runner would execute.

## Evidence

1. New job in full (`git diff -- .github/workflows/ci.yml`):

```diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 30c6865e..117af6f9 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -70,3 +70,33 @@ jobs:
         run: |
           python -m coverage run --include="*/checklist_engine.py" -m pytest tests/test_checklist_engine.py -q && python -m coverage report
           python -m coverage report --fail-under=90
+
+  test-linux:
+    runs-on: ubuntu-latest
+    steps:
+      - name: Check out repository
+        uses: actions/checkout@v4
+
+      - name: Set up Python
+        uses: actions/setup-python@v5
+        with:
+          python-version: "3.12"
+
+      - name: Install dependencies
+        run: |
+          python -m pip install --upgrade pip
+          python -m pip install pytest coverage
+
+      - name: MCP door launches and answers a real tool call
+        run: python -m pytest tests/test_mcp_spine_server.py tests/test_wire_mcp_interpreter.py -v -k "McpJsonVarExpansionLaunch or McpJsonTests or GitTrackedRefusal or ExpandMcpVar"
+
+      - name: Run full test suite
+        run: python -m pytest tests/ -q --junitxml=junit-report.xml
+
+      - name: Skip guard -- no undocumented skips
+        run: python scripts/verify_skip_guard.py junit-report.xml
+
+      - name: Coverage floor -- scripts/checklist_engine.py
+        run: |
+          python -m coverage run --include="*/checklist_engine.py" -m pytest tests/test_checklist_engine.py -q && python -m coverage report
+          python -m coverage report --fail-under=90
```

Also confirmed by `python3 -c "import yaml; d=yaml.safe_load(open('.github/workflows/ci.yml')); print(list(d['jobs'].keys()))"` → `['test', 'test-linux']`.

2. Red-proof transcript:

**Mutation** (`tests/test_agent_work_root.py`, transient/uncommitted):

```diff
--- a/tests/test_agent_work_root.py
+++ b/tests/test_agent_work_root.py
@@ -140,7 +140,7 @@ class DurableRootEpicLeaseTests(unittest.TestCase):
     def test_no_lease_resolves_to_main(self):
         # `.agent-work` present but holding no spine lease -> unchanged (main).
         (self.main / ".agent-work").mkdir()
         resolved = self.mod.durable_root(self.linked)
-        self.assertEqual(_norm(resolved), _norm(self.main))
+        self.assertEqual(_norm(resolved), _norm(self.linked))
```

This test file was not used in any other documented fault-injection example in this repo
(the only fault-injection example cited from this gate's context is `ci.yml`'s comment
pointing at issue #229's proofs, which used a different mechanism/file entirely).

**Command run** (same command the new job's "Run full test suite" step runs, narrowed with
`-k` to keep it fast, per the handoff's example form):

```bash
python3 -m pytest tests/ -q --junitxml=junit-report.xml -k test_no_lease_resolves_to_main
```

**Output — specific failing assertion, not a bare non-zero exit or crash:**

```
F                                                                        [100%]
=================================== FAILURES ===================================
___________ DurableRootEpicLeaseTests.test_no_lease_resolves_to_main ___________

self = <test_agent_work_root.DurableRootEpicLeaseTests testMethod=test_no_lease_resolves_to_main>

    def test_no_lease_resolves_to_main(self):
        # `.agent-work` present but holding no spine lease -> unchanged (main).
        (self.main / ".agent-work").mkdir()
        resolved = self.mod.durable_root(self.linked)
>       self.assertEqual(_norm(resolved), _norm(self.linked))
E       AssertionError: '/tmp/tmpv1n1h5ll/main' != '/tmp/tmpv1n1h5ll/linked'
E       - /tmp/tmpv1n1h5ll/main
E       ?                  ^^
E       + /tmp/tmpv1n1h5ll/linked
E       ?                  ^  +++

tests/test_agent_work_root.py:144: AssertionError
=========================== short test summary info ============================
FAILED tests/test_agent_work_root.py::DurableRootEpicLeaseTests::test_no_lease_resolves_to_main
1 failed, 3737 deselected in 1.36s
```

**Revert:**

```bash
$ git checkout -- tests/test_agent_work_root.py
$ git diff --quiet -- tests/; echo $?
0
```

**Re-run, green:**

```bash
$ python3 -m pytest tests/ -q --junitxml=junit-report.xml -k test_no_lease_resolves_to_main
.                                                                        [100%]
1 passed, 3737 deselected in 0.87s
```

(The transient `junit-report.xml` produced by both local runs was deleted after use; it is
gitignored/untracked either way.)

3. Final `git diff --stat` (exactly one file changed):

```
$ git diff --stat
 .github/workflows/ci.yml | 30 ++++++++++++++++++++++++++++++
 1 file changed, 30 insertions(+)
```

## TDD evidence, if required
Not applicable (this gate's Test Mode is inspection-only/local-command-parity, not TDD on
application code) — the red→green cycle above is the required red-proof, not a TDD cycle on
new source.

- Failing test observed: see red-proof output above (`AssertionError: '/tmp/.../main' !=
  '/tmp/.../linked'`).
- Passing test observed: see re-run output above (`1 passed, 3737 deselected`).
- Refactor while green: n/a.

## Docs/contracts touched
- none — no doc or contract file was touched; `.github/workflows/ci.yml`'s own header comment
  (lines 1-11) already documents the gate and was left untouched.

## Assumptions
- Used `assumption:ci-tests-merge-ref` as given (not re-verified — it was pasted as a launch-
  order measurement, out of this gate's scope to re-check).
- Named the new job `test-linux` (job key). The handoff specifies `runs-on: ubuntu-latest`
  and step content, not a job key name; this was latitude per "Python version, step layout,
  caching, and naming are your latitude" in Authority.
- Kept the MCP-door smoke-test step's name without the "on Windows" qualifier (it runs on
  Linux here), since the underlying assertion (the door launches and answers a real tool
  call under `${CONSTELLATION_PYTHON:-python3}` on this OS) still holds; did not copy the
  Windows-specific commentary block above that step since it documents Windows-specific
  history (`python3` interpreter alias issues) that does not apply to the Linux job.

## Stop conditions hit
None. Scope was not exceeded, no specific exclusion was touched, the red-proof produced a
specific named-assertion failure using exactly one `tests/` file, and no decision outside
this task's authority was needed.

## Out-of-scope observations
None beyond what the handoff and launch order already flag as floated (matrix strategy,
branch protection, required-checks config, windows-latest fixes) — none of that was
considered or touched here.

## Workflow Feedback

- **Handoff gaps:** none — confirmed after review: task, protected intent, test mode, close
  criteria, allowed scope, exclusions, all four graded decision constraints, map anchors,
  required evidence, verification commands, authority, and stop conditions were all present
  and unambiguous.
- **Context rediscovered:** the dispatch message stated this crew's tool list deliberately
  omits `mcp__spine__*` and that `SPINE_FILE`/`SPINE_SESSION` in this process's environment
  resolve to the parent Commander's own spine (`SPINE_SESSION=constellation/w3-ci/commander/
  commander`), not a spine bound to this gate — confirming the "spine:null" crew-dispatch
  case rather than a dispatch defect. Per `references/checklist-engine.md`'s "MCP door:
  default path, and who it is NOT for" section, the correct move was to author a local
  `IMPLEMENTER_PLAN.json` and drive it directly through `scripts/checklist_engine.py`'s CLI
  (never the MCP door, which stays bound to the Commander's `spine.json`). This worked
  cleanly once identified, but the skill's own default framing ("A dispatched crew's spine
  is bound for you before you start... `spine_status` is your first call") reads as though
  an MCP door is always available to a dispatched crew; a one-line pointer earlier in the
  skill to the exact detection check (`SPINE_SESSION` naming a role other than your own, or
  the harness omitting `mcp__spine__*` tools entirely ⇒ author your own plan via the CLI)
  would save re-deriving this from `checklist-engine.md`'s longer MCP-door section each time.
- **Instructions improvised around:** used `python3 scripts/checklist_engine.py --file
  .agent-work/w3-ci/crew-handoffs/g1-implement-plan.json <verb> ...` directly via Bash in
  place of `mcp__spine__*` tool calls, since the latter were absent from this dispatch's tool
  list by design. Chose a plan-file location beside the handoff
  (`.agent-work/w3-ci/crew-handoffs/g1-implement-plan.json`) rather than overwriting or
  touching the Commander's `spine.json`.
- **What would have made this easier:** a one-line early pointer in
  `constellation-implementer/SKILL.md`'s "Start here" section to the exact spine-null
  detection signal (mismatched `SPINE_SESSION` role and/or missing `mcp__spine__*` tools)
  and the CLI-direct fallback, ahead of the MCP-door-first framing.

## Return status
`complete`
