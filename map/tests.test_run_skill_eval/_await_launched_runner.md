# tests.test_run_skill_eval:_await_launched_runner
function, tests/test_run_skill_eval.py:1232, 37 lines

```python
def _await_launched_runner(child_tmp: Path, proc: 'subprocess.Popen', *, deadline_s: float)
```

Bounded poll: discover the runner's `--keep-temp` temp dir (created under the

child-scoped TMP/TEMP as `constellation-eval-*`) and wait until its `run-0/meta.json`
reaches `status=="launched"` with `subject_pid` stamped. The `kept temp dir:` stderr
line is unusable for discovery here — the runner prints it only in a `finally` AFTER
run_scenario returns, which never happens while the subject hangs (and not at all
under a hard tree-kill) — so the temp dir is located via the redirected temp root.
Raises a clear assertion (never hangs) if the subject fails to hang or the runner
dies before reaching `launched`.

calls stdlib: builtins.AssertionError x3, time.monotonic x2, builtins.sorted, json.loads, time.sleep
reads stdlib: time (module) x3, builtins.OSError, builtins.ValueError, json (module)
unresolved: 6 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
