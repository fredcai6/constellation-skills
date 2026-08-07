# scripts.verify_skill_registered:verify_skill_registered
function, scripts/verify_skill_registered.py:76, 57 lines

```python
def verify_skill_registered(skill: str, root: Path | str = 'skills', *, reference_bundles: dict | None = None, script_bundles: dict | None = None) -> None
```

Raise SkillRegistrationError if `skill` (a source directory name under

`root`) is mechanically broken or unregistered; return None if it is clean.

`reference_bundles` / `script_bundles` default to the live registration maps
in install_constellation; tests inject their own to exercise the gate.

calls internal: _require x4, _gating_findings
calls stdlib: pathlib.Path x2
calls third-party: install_constellation.script_source_path
reads third-party: install_constellation (module) x4, install_constellation.REPO_ROOT, install_constellation.SKILL_REFERENCE_BUNDLES, install_constellation.SKILL_SCRIPT_BUNDLES
writes internal: verify_skill_registered.reference_bundles, verify_skill_registered.root, verify_skill_registered.script_bundles
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
