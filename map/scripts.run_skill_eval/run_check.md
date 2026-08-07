# scripts.run_skill_eval:run_check
function, scripts/run_skill_eval.py:297, 19 lines

```python
def run_check(script_path, run_dir, *, is_answer: bool = False) -> CheckResult
```

Execute `python <script> <run-dir>` as a subprocess. Exit 0 => passed;

stdout's first line is the evidence printed verbatim into the verdict. This is
a CHECK subprocess (its only input is a directory, its only output an exit
code) — never an agent launch.

calls internal: CheckResult
calls stdlib: builtins.str x2, pathlib.Path, subprocess.run
reads stdlib: subprocess (module), sys (module), sys.executable
writes internal: run_check.script_path
unresolved: 2 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only
