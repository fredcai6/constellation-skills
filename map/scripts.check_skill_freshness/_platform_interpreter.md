# scripts.check_skill_freshness:_platform_interpreter
function, scripts/check_skill_freshness.py:41, 5 lines

```python
def _platform_interpreter() -> str
```

Mirror of install_constellation._platform_interpreter: `py` on Windows,

`python3` elsewhere. Kept here so freshness normalization reverses the same
interpreter rewrite the installer applies to installed copies.

reads stdlib: os (module), os.name

referenced by: 1 sites, this module only
