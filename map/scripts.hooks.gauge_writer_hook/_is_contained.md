# scripts.hooks.gauge_writer_hook:_is_contained
function, scripts/hooks/gauge_writer_hook.py:142, 20 lines

```python
def _is_contained(gauge_path: Path) -> bool
```

True only for the documented shape `<root>/.agent-work/<work_id>/gauge.json`.

The binding is maintained by a sibling hook from whatever `--file` an engine
`claim` command carried, so the spine path it records is UNVALIDATED input as
far as this module is concerned. A claim whose `--file` resolved outside a
work dir (e.g. a bare `spine.json` run from a checkout root) would otherwise
make this hook drop a `gauge.json` into that directory -- untracked repo-root
debris that nothing gitignores, since only `.agent-work/` is ignored.

`<root>` is deliberately unconstrained: under an active Admiral epic lease
`durable_root()` resolves to the WORKTREE root rather than the main checkout
(see scripts/agent_work_root.py), so a legitimate gauge path may sit outside
`project_dir` entirely. What is invariant across both is the trailing
`.agent-work/<work_id>/` shape, which is what this checks.

reads stdlib: builtins.Exception
unresolved: 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
