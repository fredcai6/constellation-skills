# scripts.verify_skill_registered:main
function, scripts/verify_skill_registered.py:146, 16 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: _dry_run_installs, verify_skill_registered
calls stdlib: builtins.print x2, argparse.ArgumentParser
reads internal: SkillRegistrationError
reads stdlib: argparse (module) x2, argparse.RawDescriptionHelpFormatter, builtins.__doc__, sys (module), sys.stderr
reads third-party: install_constellation (module), install_constellation.InstallError
unresolved: 3 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
