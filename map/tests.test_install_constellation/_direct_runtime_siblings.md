# tests.test_install_constellation:_direct_runtime_siblings
function, tests/test_install_constellation.py:1176, 29 lines

```python
def _direct_runtime_siblings(module_path: Path, scripts_root: Path) -> set[str]
```

Sibling modules under scripts/ that `module_path` can reach at runtime.

Two reach mechanisms exist in this tree and BOTH have to be seen:

1. dynamic path load -- `Path(__file__).parent / "x.py"` + importlib
   (`checklist_engine._load_gauge_reader()`).
2. `sys.path.insert(0, <own parent>)` followed by a PLAIN
   `import x` / `from x import ...` (`checklist_engine` -> `episode_capture`,
   #305). Deferred imports written inside a function to break an import
   cycle (`episode_capture.emit_step_manifest` -> `context_manifest`) count
   too, which is why this walks the AST rather than matching top-of-file
   lines.

Mechanism 2 is the one the original regex-only detector was blind to, so the
#305 sidecar could be imported by the engine and shipped by nobody. A name
counts only if `scripts/<name>.py` actually exists -- that single test is
what separates a co-located sibling from stdlib/third-party without a
hand-kept denylist that could rot.

calls stdlib: builtins.isinstance x2, ast.parse, ast.walk, builtins.set, re.findall
reads stdlib: ast (module) x4, ast.Import, ast.ImportFrom, re (module)
unresolved: 6 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
