# scripts.install_constellation:probe_host_interpreter
function, scripts/install_constellation.py:390, 19 lines

```python
def probe_host_interpreter(*, candidates: Sequence[str] = INTERPRETER_CANDIDATES, timeout: float = DEFAULT_INTERPRETER_PROBE_TIMEOUT) -> str | None
```

Try each candidate in order via a REAL `<candidate> --version` subprocess

call, accepting the first that exits 0 within `timeout`. Returns `None` if
every candidate fails. A hung/misregistered `py` launcher is a real, observed
Windows failure mode -- the per-candidate timeout is what keeps that from
hanging the whole install run where before a bad guess was harmless.

calls internal: _probe_interpreter_candidate

referenced by: 1 sites, this module only
