# scripts.install_constellation:_platform_interpreter
function, scripts/install_constellation.py:338, 9 lines

```python
def _platform_interpreter() -> str
```

Interpreter for installed command strings: the `py` launcher on Windows,

`python3` elsewhere. Installed spine imperatives ship the literal `python <…>`
prefix; rewriting it here spares Windows users the recurring `python`->`py`
hand-patch (the source templates keep `python <…>` to preserve the authoring
contract). This is the os.name-based FALLBACK used only when
`probe_host_interpreter` cannot find any working candidate on the host --
see `resolve_interpreter`.

reads stdlib: os (module), os.name

referenced by: 1 sites, this module only
