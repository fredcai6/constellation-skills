# scripts.query_episodes:_envelope
function, scripts/query_episodes.py:448, 18 lines

```python
def _envelope(query: str, root: Path, episodes: list, include_retired: bool) -> dict
```

The CLI's answer shape. `pid` names the OS process that produced this answer —

provenance, and the thing that makes a cross-SESSION retrieval exercise able to
prove it really crossed a process boundary instead of calling a function twice.

`include_retired` states which universe the answer came from. Without it a caller
could mistake an archive-excluding answer for a complete one — a silent omission that
happens at the consumer's end rather than this module's, and is no less silent for
it.

calls internal: episode_to_dict
calls stdlib: builtins.len, builtins.str, os.getpid
reads stdlib: os (module)
unresolved: 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
