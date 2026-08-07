# scripts.checklist_engine:_run_check_command
function, scripts/checklist_engine.py:736, 25 lines

```python
def _run_check_command(command: str) -> tuple[subprocess.CompletedProcess, str]
```

Run a `command`-kind check. Route it through a POSIX shell when one is found

(so authored grep/&&/pipe checks behave the same on Windows as on POSIX);
when NO POSIX shell is available, FAIL VISIBLY instead of routing the POSIX-form
check text through the platform shell (cmd.exe on Windows) — a silent cmd.exe run
would misinterpret grep/&&/pipe checks and could false-pass or false-fail. In that
case we do not call subprocess.run at all: we return a synthetic failed result
(returncode 127) whose stderr names the missing shell. Returns (completed process,
marker) where marker is "posix" or "no-posix-shell"; POSIX-form text is never run
through cmd.exe.

calls internal: _find_posix_shell
calls stdlib: subprocess.CompletedProcess, subprocess.run
reads stdlib: subprocess (module) x2

referenced by: 1 sites, this module only
