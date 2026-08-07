# scripts.hooks.gauge_writer_hook:compute_record
function, scripts/hooks/gauge_writer_hook.py:357, 41 lines

```python
def compute_record(transcript_path, agent_id=None)
```

Build the four required fields of the record for this transcript.

Four is what THIS function returns, always. The optional fifth field
`identity_resolution_ms` is added by `handle_post_tool_use` on the
dispatched-agent path only -- see the module docstring.

`agent_id` is forwarded verbatim to `find_latest_usage` -- see there for
what it does to the sidechain polarity. One parameter, not two.

Returns `(record, uncalibrated)`. At most one is non-None:

- `(record, None)` -- a usable reading.
- `(None, {"model": ..., "observed_at": ...})` -- a usable token count for
  a model absent from MODEL_WINDOWS. There is no window to divide by, so
  there is no honest fill to report; the model and the sampled moment come
  back so the caller can flag it.
- `(None, None)` -- nothing usable found (no transcript record, no
  timestamp, unparseable usage). Write nothing, say nothing.

"Write nothing" never means "write a placeholder" -- a fabricated fill
reads as a genuine measurement downstream.

calls internal: find_latest_usage
calls stdlib: builtins.max, builtins.min
reads internal: MODEL_WINDOWS, SCHEMA_VERSION
reads stdlib: builtins.Exception
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
