# scripts.hooks.gauge_writer_hook:handle_post_tool_use
function, scripts/hooks/gauge_writer_hook.py:528, 136 lines

```python
def handle_post_tool_use(data: dict, project_dir: Path) -> dict
```

Compute the record ONCE, then write it to the session's SOLE bound

spine (#261, decision:gauge-write-skips-on-multiple-bindings -- supersedes
#202's decision:gauge-write-fans-out-on-ambiguity). When two genuinely
different top-level agents share one session_id (confirmed live: an
Agent-tool-dispatched Commander and its own Admiral), find_latest_usage
cannot tell whose activity produced the latest usage record -- fan-out
doesn't fix that misattribution, it SPREADS the same wrong-source record
to every spine the shared session_id happens to be bound to. So 2+
candidates is treated as exactly the same kind of uncertainty the module
already treats a missing binding as: skip-on-uncertainty, write NOTHING
to gauge.json, for both the calibrated-record path and the uncalibrated-
flag path. Only exactly one candidate ever gets a gauge.json/
gauge-uncalibrated.json write.

THREE of the skip causes are now POSITIVELY LOCALIZED with a visible
gauge-skip.json sidecar (two from issue #271, plus
subagent-transcript-missing from #419) -- see _write_skip_flag's docstring
for why this rides a SEPARATE sidecar family rather than reusing
gauge-uncalibrated.json:
  - ambiguous binding (2+ candidates): unlike a gauge.json reading, a
    diagnostic fact about WHY nothing was written is never a fabricated/
    misattributed value, so fan-out carries none of the cross-write risk
    that killed fan-out for readings (#202/#261) -- written to EVERY
    candidate (decision:skip-sidecar-fanout-and-clear).
  - no-usable-record on the single resolved candidate: same treatment,
    one path.
  - subagent-transcript-missing: agent_id resolved but its derived
    transcript is absent. Fails closed -- never the parent's transcript.
The other causes stay silent by design -- there is no known gauge path to
write a sidecar TO: zero candidates (unresolvable binding, which now also
covers a subagent whose identity would not compose a key) and a
missing/unreadable transcript_path (checked first, below, before
gauge_paths is even resolved).

NEVER raises; NEVER blocks; NEVER writes gauge.json/gauge-uncalibrated.json
on uncertainty. Always returns {} (this hook never influences the tool
call).

calls internal: _write_skip_flag x3, _clear_skip_flag x2, _atomic_write_json, _binding_key, _clear_uncalibrated_flag, _write_uncalibrated_flag, compute_record, derive_subagent_transcript, resolve_gauge_path
calls stdlib: time.perf_counter x4, builtins.len x2, os.path.isfile x2, builtins.dict, datetime.datetime.now
reads stdlib: time (module) x4, os (module) x2, os.path x2, builtins.Exception, datetime.datetime, datetime.timezone, datetime.timezone.utc
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
