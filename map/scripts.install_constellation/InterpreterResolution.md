# scripts.install_constellation:InterpreterResolution
class, scripts/install_constellation.py:354, 15 lines

```python
@dataclass(frozen=True)
class InterpreterResolution
```

The interpreter resolved for ONE install run, plus how it was resolved --

carried into both the text-rewrite and the per-skill sidecar so a consumer can
tell a genuinely-probed host from the os.name guess.

```python
interpreter: str
candidates: tuple[str, ...]
resolved_via: str
```

- [as_sidecar](InterpreterResolution.as_sidecar.md) method: HOLE: no docstring

reads stdlib: builtins.str x3, builtins.dict, builtins.tuple
writes internal: InterpreterResolution.candidates, InterpreterResolution.interpreter, InterpreterResolution.resolved_via

referenced by: 5 sites, this module only
