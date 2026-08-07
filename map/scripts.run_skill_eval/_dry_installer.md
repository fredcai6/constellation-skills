# scripts.run_skill_eval:_dry_installer
function, scripts/run_skill_eval.py:912, 11 lines

```python
def _dry_installer(worktree, temp_root) -> Path
```

Fake installer for --dry-run/--dry-run-fail: materializes a minimal, valid

skill tree under temp_root so corpus provenance (id + marker + assert) runs
end-to-end with zero agent cost. This is dry-run scaffolding, NOT temp_install
(the real installer) — it deliberately avoids installing the full corpus so a
dry run stays instant and agent-free.

calls stdlib: pathlib.Path
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
