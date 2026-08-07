# scripts.install_constellation:main
function, scripts/install_constellation.py:1298, 93 lines

```python
def main(argv: Sequence[str] | None = None, *, env: Mapping[str, str] | None = None, cwd: Path | None = None, out: Callable[[str], object] = print) -> int
```

HOLE: no docstring

calls internal: InstallError x6, write_template_baselines x2, write_template_working_copies x2, build_parser, discover_skills, install_skills, main.out, report_hook_wiring, resolve_interpreter, resolve_target_roots, select_skills, validate_required_references, validate_required_scripts, wire_hooks
calls stdlib: builtins.any, pathlib.Path.cwd
reads internal: HOOK_CAPABLE_AGENT_NAMES x2, HOOK_OWNER_SKILL x2, GAUGE_WRITER_HOOK_SCRIPT, InstallError, SETTINGS_FILENAME
reads stdlib: os (module), os.environ, pathlib.Path
unresolved: 5 calls (dispatch-unknown-base), 29 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
