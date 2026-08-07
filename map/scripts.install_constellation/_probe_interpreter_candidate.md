# scripts.install_constellation:_probe_interpreter_candidate
function, scripts/install_constellation.py:371, 17 lines

```python
def _probe_interpreter_candidate(candidate: str, *, timeout: float) -> bool
```

Whether `<candidate> --version` exits 0 within `timeout`. A missing

candidate, a non-zero exit, and a timeout are ALL treated as this candidate
failing -- never a raise, never a hang past `timeout`.

calls stdlib: builtins.dict, subprocess.run
reads stdlib: subprocess (module) x2, builtins.OSError, os (module), os.environ, subprocess.TimeoutExpired
unresolved: 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
