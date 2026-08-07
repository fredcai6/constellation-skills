# scripts.run_skill_eval:launch_agent
function, scripts/run_skill_eval.py:676, 89 lines

```python
def launch_agent(argv, *, cwd, env, stdout_path, stderr_path, timeout) -> LaunchOutcome
```

The ONE real seam — spawn `claude -p ...` (argv built by build_eval_argv)

with `cwd=<run>/workspace`, capturing stdout/stderr to the given paths and
ENFORCING `timeout` with a hard process-tree kill. Uses `subprocess.Popen` (which
the tests' autouse agent-free guard also wraps) so no `claude` is ever spawned
under test.

Populates LaunchOutcome fully so the pure classify_run infra-fence fires:
  - normal exit  -> exit_code + stderr tail (for usage/rate-limit sniffing);
  - deadline hit -> tree-killed, timed_out=True (fenced inconclusive);
  - spawn failure (FileNotFoundError / OSError, e.g. no `claude` on PATH)
    -> launch_error=True (fenced errored).
Corpus-mismatch is asserted upstream in _run_once, never here.

The wait can never hang on a lingering grandchild pipe handle: we poll for exit
against a monotonic deadline, tree-kill on expiry, and join the daemon drain
threads only for `_DRAIN_GRACE_SECONDS` before abandoning them.

calls internal: LaunchOutcome x4, _read_text_tail x2, _stamp_meta_field, _stamp_meta_heartbeat, _tree_kill
calls stdlib: time.monotonic x5, builtins.str x3, pathlib.Path x3, threading.Thread x2, subprocess.Popen, time.sleep
reads internal: _DRAIN_GRACE_SECONDS x2, _HEARTBEAT_INTERVAL_SECONDS x2, _drain_pipe x2, _POLL_INTERVAL_SECONDS
reads stdlib: time (module) x6, subprocess (module) x5, builtins.OSError x2, subprocess.PIPE x2, threading (module) x2, builtins.FileNotFoundError, subprocess.DEVNULL, subprocess.TimeoutExpired
writes internal: launch_agent.stderr_path, launch_agent.stdout_path
unresolved: 10 calls (dispatch-unknown-base), 7 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
