# scripts.install_constellation:install_skills
function, scripts/install_constellation.py:885, 74 lines

```python
def install_skills(skills: Sequence[Skill], target_root: Path, *, dry_run: bool, force: bool, full_set: bool, restart_message: str, out: Callable[[str], object], interpreter: InterpreterResolution | None = None) -> None
```

HOLE: no docstring

calls internal: install_skills.out x4, InstallError, _source_commit, ensure_target_is_inside_root, remove_existing_constellation_set, resolve_interpreter, rewrite_installed_skill_paths, script_source_path, write_corpus_marker
calls stdlib: shutil.copy2 x2, builtins.len, shutil.copytree, shutil.rmtree
reads internal: CORPUS_MARKER, REPO_ROOT, SHARED_REFERENCE_ROOT
reads stdlib: shutil (module) x4
unresolved: 7 calls (dispatch-unknown-base), 9 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
