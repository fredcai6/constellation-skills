# scripts.hooks.gauge_writer_hook:find_latest_usage
function, scripts/hooks/gauge_writer_hook.py:291, 64 lines

```python
def find_latest_usage(transcript_path, agent_id=None)
```

Scan the transcript tail for the most recent assistant message carrying

a usage record. Returns (model, total_tokens, observed_at), or None if
nothing usable is found in the scanned window.

`agent_id` INVERTS the sidechain polarity, and it is deliberately ONE
parameter rather than an `expect_sidechain` + `expect_agent_id` pair:
"this is agent X's own transcript" is a single fact, and a pair would let
a caller set an incoherent combination.

- `None` (a top-level agent): today's filter exactly -- skip anything
  `isSidechain` truthy, because a subagent's turns are a different context
  window entirely.
- set (a dispatched agent, reading its OWN derived transcript): the line
  must be `isSidechain` TRUTHY *and* carry a top-level `agentId` EQUAL to
  it. Every line of a subagent's own transcript is `isSidechain: true`
  (measured; docs/GAUGE_WRITER_HOOK.md's field table states both
  polarities), so the polarity has to flip; the `agentId` equality is what
  makes a WRONG derived path fail closed rather than produce a confidently
  misattributed number.

calls internal: _iter_tail_lines_reverse
calls stdlib: builtins.isinstance x5, json.loads
reads stdlib: builtins.dict x3, builtins.Exception x2, builtins.bool, builtins.float, builtins.int, json (module)
unresolved: 9 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
