# Implementation Result

## Assigned gate
`g1` rework (attempt 2) — open Constellation work in one call (`scripts/spine_lifecycle.py`)

## Completed slice
Fixed the missing `newline="\n"` on `spine_lifecycle.py`'s one write site, added a test layer that can
actually catch the omission on any host, and collapsed `_rollback`'s three inline `subprocess.run` calls
into a small best-effort helper.

## Scope
**Files changed:**
- `scripts/spine_lifecycle.py`
- `tests/test_spine_lifecycle.py`
- `map/INDEX.md` (regenerated — see below)

**Specific exclusions touched:** no. `generate_spine.py:910`'s identical omission was not touched;
`episode_capture.py` was not touched; `checklist_engine.py`, `validate_spine.py`, `settings.json`,
`.mcp.json`, `docs/agents/*`, `skills/**` are all untouched.

## Behavior changed
Yes. `open_work` now writes `spine.json` with `newline="\n"` pinned explicitly, so on Windows the file is
written with LF line endings instead of CRLF. `_rollback`'s observable behavior (still never raises, still
scoped to what the call itself created) is unchanged — only its internal structure changed.

## Map Impact
- **Structural anchors touched:** `scripts.spine_lifecycle:_rollback` — internals only, no signature or
  caller-visible change; `scripts.spine_lifecycle:_best_effort_git` — new private helper, no new caller
  outside `_rollback`.
- **Capabilities added/changed/affected:** none new; `open_work`'s existing "compile and write spine.json"
  capability now produces LF-only bytes on every platform instead of platform-dependent bytes.
- **Constraints/assumptions touched:** `docs/agents/CREW_CONTEXT.md`'s "every write pins
  `encoding='utf-8', newline='\n'`" rule — now honored by this module's one write site (previously
  violated).
- **Claims/evidence produced:** `TestEveryWriteTextPinsNewline` is new durable evidence that the module's
  write sites stay compliant with the newline rule; `map/INDEX.md` regenerated and idempotent (verified: a
  second `python -m scripts.code_map build --root .` after the update produces no further diff).
- **Trust limitations / drift found:** none new. `generate_spine.py:910` carries the identical omission,
  already recorded out-of-scope by the reviewer and this handoff.

## Test mode
**Required:** `test-first` (TDD red→green) for the regression test; `test-after` for the refactor.
**Satisfied:** yes. The regression test's RED step is a real, observed mutation experiment (below); the
refactor was verified against the existing rollback tests, unchanged.

## Evidence

### 1. Diff

```diff
diff --git a/scripts/spine_lifecycle.py b/scripts/spine_lifecycle.py
index 7bca9dbe..05f94d26 100644
--- a/scripts/spine_lifecycle.py
+++ b/scripts/spine_lifecycle.py
@@ -143,14 +143,21 @@ def _git(args: list[str], *, cwd: Path) -> str:
     return proc.stdout.strip()
 
 
+def _best_effort_git(args: list[str], *, cwd: Path) -> None:
+    """Runs a git command and ignores the outcome -- never raises, exit code
+    unchecked. `_rollback`'s only caller: best-effort cleanup must never itself
+    fail the rollback it is part of."""
+    subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
+
+
 def _rollback(worktree: str, branch: str, root: Path) -> None:
     """Best-effort, never raises: removes the worktree this call created and
     deletes the branch this call created. Scoped to what THIS call created --
     a pre-existing unrelated worktree or branch is never touched, because the
     only arguments here are the ones this call itself derived."""
-    subprocess.run(["git", "worktree", "remove", "--force", worktree], cwd=str(root), capture_output=True, text=True)
-    subprocess.run(["git", "worktree", "prune"], cwd=str(root), capture_output=True, text=True)
-    subprocess.run(["git", "branch", "-D", branch], cwd=str(root), capture_output=True, text=True)
+    _best_effort_git(["worktree", "remove", "--force", worktree], cwd=root)
+    _best_effort_git(["worktree", "prune"], cwd=root)
+    _best_effort_git(["branch", "-D", branch], cwd=root)
 
 
 @contextlib.contextmanager
@@ -255,7 +262,7 @@ def open_work(
             raise SpineLifecycleError(f"worktree isolation self-verify failed: {reason}")
 
         spine_path = work_dir / "spine.json"
-        spine_path.write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8")
+        spine_path.write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8", newline="\n")
     except Exception:
         _rollback(worktree, branch, root)
         raise
```

```diff
diff --git a/tests/test_spine_lifecycle.py b/tests/test_spine_lifecycle.py
index edff7b33..c28bd25c 100644
--- a/tests/test_spine_lifecycle.py
+++ b/tests/test_spine_lifecycle.py
@@ -13,6 +13,7 @@ state is read only by `TestWorktreePathForRealWorktree`, and never written.
 
 from __future__ import annotations
 
+import ast
 import json
 import shutil
 import subprocess
@@ -449,6 +450,67 @@ class TestOriginRoundTrip:
         )
 
 
+# --------------------------------------------------------------------------- #
+# spine.json is written with newline="\n" -- CREW_CONTEXT.md's "every write"
+# rule. Byte-level (Path.read_bytes()) because a text-mode read translates
+# CRLF back to LF on read, which would pass on Windows regardless.
+# --------------------------------------------------------------------------- #
+
+@requires_git
+class TestSpineFileHasNoCRLF:
+    def test_written_spine_bytes_contain_no_crlf(self, repo, wt_root):
+        result = sl.open_work("w1", _spec("w1"), root=repo, base="HEAD", parent="unknown", wt_root=wt_root)
+        raw = Path(result["SPINE_FILE"]).read_bytes()
+        assert b"\r\n" not in raw
+
+
+# --------------------------------------------------------------------------- #
+# Every write_text call in the module pins newline="\n" explicitly. AST-based
+# (house style: tests/test_mcp_adoption.py::_cli_only_verb_violations) because
+# TestSpineFileHasNoCRLF above cannot go red on Linux: os.linesep here is "\n",
+# so write_text() with no newline= argument produces identical bytes to
+# write_text() with newline="\n" -- the CRLF-producing bug is real only on
+# Windows and invisible to any byte comparison run on this host. This check
+# instead reads the source and can fail on any host, including this one.
+# --------------------------------------------------------------------------- #
+
+def _missing_newline_write_text_calls(source: str, where: str) -> list[str]:
+    """Every `.write_text(...)` call in `source` lacking an explicit
+    `newline=` keyword argument, as `where:lineno` strings."""
+    tree = ast.parse(source, filename=where)
+    violations = []
+    for node in ast.walk(tree):
+        if (
+            isinstance(node, ast.Call)
+            and isinstance(node.func, ast.Attribute)
+            and node.func.attr == "write_text"
+            and not any(kw.arg == "newline" for kw in node.keywords)
+        ):
+            violations.append(f"{where}:{node.lineno}")
+    return violations
+
+
+class TestEveryWriteTextPinsNewline:
+    SOURCE = (ROOT / "scripts" / "spine_lifecycle.py").read_text(encoding="utf-8")
+
+    def test_the_shipped_module_has_no_violations(self):
+        assert _missing_newline_write_text_calls(self.SOURCE, "scripts/spine_lifecycle.py") == []
+
+    def test_violating_a_mutated_copy_missing_newline_is_caught(self):
+        # Positive control: proves the predicate can fail, per the mutated-copy
+        # convention `_cli_only_verb_violations` establishes. Strips exactly the
+        # keyword this check exists to require -- not a stand-in for a different
+        # mutation.
+        mutated = self.SOURCE.replace(', newline="\\n")', ")")
+        assert mutated != self.SOURCE, "the mutation did not change the source -- fixture is stale"
+        violations = _missing_newline_write_text_calls(mutated, "<mutated>")
+        assert violations, "the predicate did not catch a write_text call with newline= stripped"
+
+    def test_innocent_a_write_text_call_with_newline_present_is_not_flagged(self):
+        innocent = "p.write_text(data, encoding='utf-8', newline='\\n')"
+        assert _missing_newline_write_text_calls(innocent, "<innocent>") == []
+
+
 # --------------------------------------------------------------------------- #
 # work-id validator reuse -- never a second implementation
 # --------------------------------------------------------------------------- #
```

`map/INDEX.md` diff omitted (mechanical regeneration, `scripts.spine_lifecycle` and `tests.test_spine_lifecycle`
entity counts shifted by the new helper and new test classes); confirmed idempotent — a second
`python -m scripts.code_map build --root .` after committing produces no further diff.

### 2. Audit of every other write in the module

`scripts/spine_lifecycle.py` has exactly one write call in the whole file:

```
$ grep -n "write_text\|open(" scripts/spine_lifecycle.py
258:        spine_path.write_text(json.dumps(compiled, indent=2) + "\n", encoding="utf-8", newline="\n")
```

Confirmed before the fix (the pre-fix grep for `write_text` also returned exactly this one line) and after.
No second write site existed to miss.

### 3. The regression test, and the mutation experiment

Added `TestSpineFileHasNoCRLF` (byte-level, `Path.read_bytes()`, asserts no `b"\r\n"`) and
`TestEveryWriteTextPinsNewline` (AST-based source check, house style of
`tests/test_mcp_adoption.py::_cli_only_verb_violations`, with a mutated-copy positive control).

Both new tests pass with the real fix in place:

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_spine_lifecycle.py -k "CRLF or PinsNewline" -v
collected 32 items / 28 deselected / 4 selected
tests/test_spine_lifecycle.py ....                                       [100%]
4 passed, 28 deselected in 0.04s
```

**Mutation experiment — real, run on this host, not simulated.** Removed `, newline="\n")` from
`spine_lifecycle.py:258` (restoring exactly the pre-fix line), re-ran the same 4 tests:

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_spine_lifecycle.py -k "CRLF or PinsNewline" -v
tests/test_spine_lifecycle.py .FF.                                       [100%]

___ TestEveryWriteTextPinsNewline.test_the_shipped_module_has_no_violations ____
    def test_the_shipped_module_has_no_violations(self):
>       assert _missing_newline_write_text_calls(self.SOURCE, "scripts/spine_lifecycle.py") == []
E       AssertionError: assert ['scripts/spine_lifecycle.py:258'] == []

_ TestEveryWriteTextPinsNewline.test_violating_a_mutated_copy_missing_newline_is_caught _
    mutated = self.SOURCE.replace(', newline="\\n")', ")")
>       assert mutated != self.SOURCE, "the mutation did not change the source -- fixture is stale"
E       AssertionError: the mutation did not change the source -- fixture is stale

2 failed, 2 passed, 28 deselected in 0.06s
```

Read exactly: `TestSpineFileHasNoCRLF` (the byte-level check) and
`test_innocent_a_write_text_call_with_newline_present_is_not_flagged` **stayed green** even with the bug
back in place — this is the proof the handoff asked for. On this Linux host, `os.linesep` is `"\n"`, so
`write_text()` with no `newline=` argument produces byte-identical output to `write_text(newline="\n")` —
no translation ever happens either way, so a byte comparison cannot distinguish the buggy code from the
fixed code here. **The byte-level test cannot go red on Linux**, exactly as the handoff anticipated.

`test_the_shipped_module_has_no_violations` **went red** (`AssertionError: ['scripts/spine_lifecycle.py:258'] == []`)
— this is the layer that can fail on any host, because it reads the source text rather than comparing
translated bytes. (`test_violating_a_mutated_copy_missing_newline_is_caught` also failed, but for an
uninteresting reason: its own mutation is idempotent against an already-buggy file, so its self-check
`mutated != self.SOURCE` correctly caught that the second mutation was a no-op — this is the guard working
as designed, not a second defect.)

Restored the fix (`git diff` confirmed no change against the committed file before restoring), re-ran:

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_spine_lifecycle.py -k "CRLF or PinsNewline" -v
tests/test_spine_lifecycle.py ....                                       [100%]
4 passed, 28 deselected in 0.04s
```

All 4 pass again.

### 4. Suite green, sweep still 23

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2856 passed, 3 skipped, 1121 subtests passed in 114.25s (0:01:54)
```

Baseline was **2852 passed, 3 skipped, 1121 subtests**; this run adds the 4 new tests → **2856**, exceeding
baseline as required. (`map/INDEX.md` needed regeneration — `python -m scripts.code_map build --root .` —
because the new helper and new test classes shifted entity counts; `test_map_tree_freshness_root_index_matches_a_fresh_build`
would otherwise fail. Regenerated, committed here, confirmed idempotent.)

```
$ python scripts/validate_spine.py --sweep --root . 2>&1 | grep -cE '^\s+\['
23
```

Sweep unchanged at **23**.

### 5. Non-blocking refactor verified unchanged behavior

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_spine_lifecycle.py -k "Rollback or SelfVerifyForcesRollback" -v
tests/test_spine_lifecycle.py ....                                       [100%]
4 passed, 28 deselected in 0.09s
```

**Result:** pass — full suite green above baseline, sweep unchanged, all rework-specific tests pass.

## TDD evidence, if required
- Failing test observed: yes — see the mutation transcript above (`test_the_shipped_module_has_no_violations`
  went red with the bug reintroduced).
- Passing test observed: yes — both before mutation and after restoring the fix (see above).
- Refactor while green: yes — the `_rollback` refactor (item 5 above) was applied and verified after the
  regression test was already green.

## Docs/contracts touched
- None.

## Assumptions
- None.

## Stop conditions hit
- None.

## Out-of-scope observations
- None new. `generate_spine.py:910`'s identical omission and `episode_capture.py`'s path-doubling defect
  remain out of scope, per the handoff and the reviewer's own record.

## Workflow Feedback

- **Handoff gaps:** none of substance — the handoff was precise about scope, evidence shape, and the exact
  test-mode fallback (byte-level → source/AST-level) to use if the byte check cannot go red on Linux, which
  is exactly what happened.
- **Context rediscovered:** the same disambiguation the g1 implementer and reviewer both already reported —
  `SPINE_FILE`/`SPINE_SESSION` inherited from the environment point at the Commander's own `execute.json`,
  not a dedicated checklist for this dispatch (per-gate MCP door binding is this epic's own g3 deliverable).
  Confirmed via `spine_status`, whose imperative was unmistakably Commander-level content (dispatch
  subagents via `run_crew.py`, write `REPLAN_INPUT.json`), and via `mcp_server_started`, which names
  `execute.json` explicitly. Built and drove my own `IMPLEMENTER_PLAN.json` via the CLI
  (`scripts/checklist_engine.py`) instead, per `constellation-workbench/references/checklist-engine.md`'s
  own guidance for this case. This is the third crew in this gate (implementer attempt 1, reviewer, this
  rework) to hit and independently re-derive the same disambiguation — naming it explicitly in the handoff
  (as this run's own reviewer already suggested for the next reviewer) would save a fourth detour.
- **Instructions improvised around:** none for the task itself. One tooling snag, self-contained: my first
  `m1-newline-fix` postcondition check command was over-escaped through JSON-to-shell and never matched the
  literal `newline="\n"` text even after the fix landed; fixed via the engine's own `amend --delta
  ... retext-check` verb rather than hand-editing the plan file.
- **What would have made this easier:** nothing beyond the SPINE_FILE-disambiguation note above.

## Return status
`complete`
