# scripts.run_skill_eval:load_scenario
function, scripts/run_skill_eval.py:192, 60 lines

```python
def load_scenario(scenario_dir) -> Scenario
```

Parse a scenario directory into a Scenario. PURE and total: it reads only

the directory, never launches anything, and raises EvalConfigError (never a
bare error) on any schema violation.

Structural T3: `checks/*.py` are PROCESS checks and carry the verdict;
`checks/answer/*.py` are advisory and never gate. A scenario with ZERO process
checks is a hard config error — you cannot pass on answer checks alone, and
you cannot pass with no process check.

calls internal: EvalConfigError x4, Scenario
calls stdlib: builtins.int x3, builtins.sorted x2, builtins.max, builtins.str, pathlib.Path, tomllib.loads
reads internal: DEFAULT_M, DEFAULT_MODEL, DEFAULT_N, DEFAULT_TIMEOUT_SECONDS, SCENARIO_TIMEOUT_FLOOR_SECONDS
reads stdlib: tomllib (module) x2, builtins.dict, tomllib.TOMLDecodeError
writes internal: load_scenario.scenario_dir
unresolved: 15 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
