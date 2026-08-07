# scripts.run_crew:crew_env
function, scripts/run_crew.py:266, 7 lines

```python
def crew_env(base_env: dict[str, str] | None = None) -> dict[str, str]
```

UTF-8-safe environment defaults for the child (without clobbering an

explicit caller value).

calls stdlib: builtins.dict
reads stdlib: os (module), os.environ
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
