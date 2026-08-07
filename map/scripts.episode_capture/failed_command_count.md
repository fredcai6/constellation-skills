# scripts.episode_capture:failed_command_count
function, scripts/episode_capture.py:271, 21 lines

```python
def failed_command_count(task: Mapping[str, Any]) -> int
```

`failed-commands` — how many `command` checks the ENGINE ran and got a non-zero

exit from, for this step.

Read off the evidence the engine writes itself (`type: command-output`, with the
exit code in `payload.exit`), so it counts what actually happened rather than what
anyone remembered to report. It survives a refusal because the evidence item is
appended BEFORE the raise and `main()` persists on the error path.

SUPERSEDED evidence is counted. A command that failed during an attempt later
reopened still failed during this run; `reopen` supersedes evidence to stop it
re-satisfying a gate, which is a statement about gate satisfaction, not history.

calls stdlib: builtins.isinstance x2
reads stdlib: builtins.dict, builtins.int
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
