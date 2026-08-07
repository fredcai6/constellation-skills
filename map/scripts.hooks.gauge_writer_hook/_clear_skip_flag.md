# scripts.hooks.gauge_writer_hook:_clear_skip_flag
function, scripts/hooks/gauge_writer_hook.py:497, 27 lines

```python
def _clear_skip_flag(gauge_path: Path) -> None
```

Mirror _clear_uncalibrated_flag exactly: drop a stale skip sidecar once

this path resolves to a real outcome again (a clean gauge.json write, or
the uncalibrated-flag write -- both are called from the single-candidate
branch below, the only place a path can go from 'skipped' to 'resolved').

CLEARING SCOPE (decision:skip-sidecar-fanout-and-clear, cold-critic
finding #1): only the path that is LATER resolved back to a single
candidate ever gets cleared here. A candidate that drops out of an
ambiguous binding set without ever again being the SOLE resolved
candidate keeps a stale gauge-skip.json indefinitely -- there is no code
path that revisits a former candidate this hook has no further reason to
touch, so closing that gap would mean building cross-path bookkeeping
(out of scope, decision:no-repair). This is an ACCEPTED, bounded
residual: it self-heals the moment anyone actually resumes and drives
that spine again (the very next single-candidate call clears/overwrites
it), and while nobody resumes it, nobody is reading that spine's
`current` either. checklist_engine.py's advisory always renders the
flag's own age, never a threshold judgment on it, so even in the
residual window a reader sees exactly how old the diagnosis is rather
than trusting a silently-aging claim.

calls internal: _skip_path
reads stdlib: builtins.FileNotFoundError, builtins.OSError
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
