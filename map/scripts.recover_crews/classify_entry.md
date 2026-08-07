# scripts.recover_crews:classify_entry
function, scripts/recover_crews.py:51, 57 lines

```python
def classify_entry(entry: dict, alive: AlivePredicate, result_present: ResultPredicate) -> str
```

PURE recovery classification of one registry entry.

Decides a single state label from the entry's recorded status, whether its
PID is alive (`alive(pid)`), and whether its result artifact exists
(`result_present(entry)`):

  * abandoned                              -> abandoned (retired; ignore)
  * completed & result exists              -> complete (do not rerun)
  * completed but result missing           -> needs-abandon (claimed done, nothing landed)
  * running & pid alive                    -> active (block duplicate launch)
  * running & pid dead, result exists      -> complete (it finished before dying)
  * running & pid dead, result missing,
    resumable                              -> resumable (resume by session name)
  * running & pid dead, not resumable      -> needs-abandon (explicit abandon/relaunch)
  * resumable & result exists              -> complete
  * resumable, result missing              -> resumable
  * failed & result exists                 -> complete
  * failed, no result                      -> needs-abandon

calls internal: classify_entry.alive, classify_entry.result_present
calls stdlib: builtins.bool x3
reads internal: STATE_COMPLETE x4, STATE_NEEDS_ABANDON x4, STATE_ACTIVE x2, STATE_RESUMABLE x2, STATE_ABANDONED, STATE_CONFLICT
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
