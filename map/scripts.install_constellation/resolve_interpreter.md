# scripts.install_constellation:resolve_interpreter
function, scripts/install_constellation.py:411, 17 lines

```python
def resolve_interpreter(*, candidates: Sequence[str] = INTERPRETER_CANDIDATES, timeout: float = DEFAULT_INTERPRETER_PROBE_TIMEOUT) -> InterpreterResolution
```

Resolve the interpreter to stamp into installed skill bodies for ONE

install run: probe the host once, falling back to `_platform_interpreter`'s
os.name guess only if every candidate fails (never raises). Call this ONCE
per run and thread the result through -- never re-probe per skill. Caching
prevents INTRA-run drift only; cross-run determinism (#197's
`stable_corpus_id`, which compares two separate install invocations) rests on
the probe being naturally stable given a static host PATH, the same basis
today's pure os.name read relies on.

calls internal: InterpreterResolution x2, _platform_interpreter, probe_host_interpreter
calls stdlib: builtins.tuple x2

referenced by: 2 sites, this module only
