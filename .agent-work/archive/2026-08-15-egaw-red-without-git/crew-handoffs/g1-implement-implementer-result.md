# IMPLEMENTER_RESULT — g1-implement

## Return status: complete

## Completed slice
Rewrote `RedBeforeGreenAfterTests.test_bare_verb_workaround_was_accepted_before_this_change` in
`tests/test_episode_observation_guard_at_write.py` to prove the RED half of the RED/GREEN pair by
neutralizing `load_current()._reject_instruction_shaped` to a no-op (via monkeypatch, restored in a
`finally`), running the identical delta (`create_op(workaround=BARE_VERB_WORKAROUND)`) through the
current writer, and asserting it writes cleanly (rc==0, `egaw-guard-001.md` created). This proves the
GREEN test's rejection (`test_bare_verb_workaround_is_rejected_now`) is caused specifically by the
`_reject_instruction_shaped` guard call, not merely by being on some other code path — with no git
dependency at all.

Deleted the now-dead git-only machinery: the `PRE_CHANGE_REV` constant, the `_git_show` helper, and the
`load_pre_change` function. Removed the now-unused `import subprocess` (confirmed nothing else in the
file used it). Updated the module docstring to add a new "RED/GREEN mechanism" paragraph explaining the
neutralize-and-restore approach in place of the old git-based description, and replaced the
`PRE_CHANGE_REV` code comment (removed, since the constant it explained no longer exists) and the test's
own docstring (now describes "the guard call neutralized" instead of "the pre-change writer").

No other test method, helper, or class in the file was touched.

## Files changed
- `tests/test_episode_observation_guard_at_write.py` (only file changed, per allowed scope)

## Test mode satisfied
TDD not applicable per handoff — this was a rewrite of existing test plumbing, not new production
behavior. All existing tests in the file (the safety net) still pass unchanged, and the rewritten RED
test still asserts real behavior (rc==0 and file-created) rather than being weakened to a no-op or skip.

## Evidence produced

### 1. `python -m pytest -q tests/test_episode_observation_guard_at_write.py`
```
.........                                                                [100%]
9 passed in 0.04s
```
(Note: the file actually contains 9 test methods, not 8 as estimated in the handoff prose — 3 in
`RedBeforeGreenAfterTests`, 2 in `ControlTests`, 1 in `ScopeTests`, 3 in `GrandfatheredExceptionTests`.
All 9 pass; this is a discrepancy in the handoff's count, not a scope deviation — no test was added or
removed by this change.)

### 2. `grep -n "2c46cab8\|import subprocess\|git show\|_git_show\|load_pre_change\|PRE_CHANGE_REV" tests/test_episode_observation_guard_at_write.py`
```
(no output — exit code 1)
```

### 3. `git diff -- tests/test_episode_observation_guard_at_write.py`
```diff
diff --git a/tests/test_episode_observation_guard_at_write.py b/tests/test_episode_observation_guard_at_write.py
index c7056677..6039d23a 100644
--- a/tests/test_episode_observation_guard_at_write.py
+++ b/tests/test_episode_observation_guard_at_write.py
@@ -24,13 +24,19 @@ patching apply_episode_delta.store_root() to a throwaway directory and never ove
 it with an explicit --store-root -- the writer then treats that throwaway directory
 exactly as it would treat the genuine tracked one, without ever touching the genuine
 tracked one.
+
+RED/GREEN mechanism: rather than resurrecting a historical revision of the writer via
+git (fragile under shallow clones and hardcoded-SHA drift), the RED half of the pair
+below runs the CURRENT writer with its _reject_instruction_shaped() call neutralized to
+a no-op, then restores it. This proves the rejection the GREEN half exercises is caused
+by that guard call specifically -- not merely by being on some other code path -- while
+never touching git.
 """
 
 import contextlib
 import importlib.util
 import io
 import json
-import subprocess
 import sys
 import tempfile
 import unittest
@@ -39,18 +45,6 @@ from pathlib import Path
 ROOT = Path(__file__).resolve().parents[1]
 WRITER_SCRIPT = ROOT / "scripts" / "apply_episode_delta.py"
 
-# main at the branch point named in LAUNCH_ORDER.md — scripts/apply_episode_delta.py at
-# this revision has no write-time guard at all, which is what makes it the RED half of
-# the RED-before/GREEN-after pair below.
-PRE_CHANGE_REV = "2c46cab8"
-
-
-def _git_show(rev: str, path: str) -> str:
-    return subprocess.run(
-        ["git", "show", f"{rev}:{path}"],
-        cwd=ROOT, capture_output=True, text=True, check=True,
-    ).stdout
-
 
 def load_current():
     spec = importlib.util.spec_from_file_location("apply_episode_delta_egaw_current", WRITER_SCRIPT)
@@ -60,18 +54,6 @@ def load_current():
     return module
 
 
-def load_pre_change():
-    """The writer's source AS OF the pre-change revision, executed under the CURRENT
-    file's own path (so any relative-to-__file__ resolution inside it, e.g.
-    store_root()'s default, still means what it meant at that revision)."""
-    source = _git_show(PRE_CHANGE_REV, "scripts/apply_episode_delta.py")
-    spec = importlib.util.spec_from_file_location("apply_episode_delta_egaw_pre_change", WRITER_SCRIPT)
-    module = importlib.util.module_from_spec(spec)
-    sys.modules[spec.name] = module
-    exec(compile(source, str(WRITER_SCRIPT), "exec"), module.__dict__)
-    return module
-
-
 def create_op(run="egaw-guard", **statements):
     """One well-formed create op. Every agent-supplied statement is overridable by
     keyword, using the field name with '-' spelled '_' (mirrors
@@ -137,10 +119,15 @@ class RedBeforeGreenAfterTests(_RealStoreCase):
     entry point, before and after this lane's change."""
 
     def test_bare_verb_workaround_was_accepted_before_this_change(self):
-        """RED (before): the pre-change writer had no opinion about statement content
-        at all — the delta this suite now refuses used to write cleanly."""
-        pre = load_pre_change()
-        rc, out, root = self._run(pre, create_op(workaround=BARE_VERB_WORKAROUND))
+        """RED (before): with the guard call neutralized, the writer has no opinion about
+        statement content at all -- the delta this suite now refuses used to write cleanly."""
+        cur = load_current()
+        original = cur._reject_instruction_shaped
+        cur._reject_instruction_shaped = lambda kind, statement, where: None
+        try:
+            rc, out, root = self._run(cur, create_op(workaround=BARE_VERB_WORKAROUND))
+        finally:
+            cur._reject_instruction_shaped = original
         self.assertEqual(0, rc, out)
         self.assertTrue((root / "active" / "egaw-guard-001.md").is_file())
```

## Assumptions used
- The handoff's suggested test body (verbatim) was used as-is; it matched the existing helpers
  (`load_current()`, `self._run()`, `create_op()`, `BARE_VERB_WORKAROUND`) exactly with no adaptation
  needed.
- Confirmed `_reject_instruction_shaped(kind: str, statement: str, where: str) -> None` at
  `scripts/apply_episode_delta.py:996` before writing the monkeypatch lambda, per the handoff's allowance
  to read (not modify) that file.
- Treated the handoff's "8 tests" figure as an approximation; the file has 9 test methods both before and
  after this change (no test added or removed), all passing.

## Stop conditions hit
None. The guard seam behaved exactly as described: neutralizing `_reject_instruction_shaped` was
sufficient on its own to make the delta write cleanly (rc==0, file created) — no second seam needed
patching.

## Out-of-scope observations
None found. `scripts/apply_episode_delta.py` was read-only (per allowed scope) to confirm the guard
function's signature; it was not modified.

## Workflow feedback
None — the handoff's suggested test body was directly usable verbatim, and the close criteria/grep
command were unambiguous and matched the actual file state after edits.
