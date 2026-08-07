# scripts.run_crew:launch_process
function, scripts/run_crew.py:252, 12 lines

```python
def launch_process(argv: list[str], *, stdin: bytes, env: dict[str, str], stdout_path: Path, stderr_path: Path) -> int
```

The ONE place a real crew subprocess is spawned. Tests monkeypatch this to

simulate exit codes and to write (or withhold) the result artifact, so no
test ever launches a real agent CLI.

Foreground/blocking: we feed the supplied (empty) stdin, capture stdout/stderr
to the deterministic files, and return the child's exit code.

calls stdlib: subprocess.run
reads stdlib: subprocess (module)
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
