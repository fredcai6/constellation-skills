# Wave-3 context-fill series — what this data is, and what it is not

`w3-gauge-series.tsv` — `observed_at · dispatch · model · fill`, sampled roughly once a minute by the
Admiral's monitor from each crew's own `gauge.json`.

This is the **first per-crew fill series this epic has produced.** Wave 2's evidence for the
governor's trip band was four dispatch counts and no fill numbers at all, collected while the
orchestrator's own gauge was dark.

## Four caveats, recorded now rather than discovered later

1. **The `dispatch` column is not an agent.** `488-489` covers **two** agent instances: the first
   tripped at `0.162` and filed a `refresh-request`; its replacement started fresh at `0.041`. Read
   as one series it looks like fill *fell*, which never happens. Any min/max grouped by `dispatch`
   alone is wrong — split on the discontinuity.
2. **Sampling is event-driven, not periodic.** The gauge only refreshes when the agent uses a tool,
   and the monitor only emits on change, so gaps mean "quiet", not "steady". Do not infer a rate.
3. **The population is one laptop.** These readings exist because `.claude/settings.local.json`
   wires `gauge_writer_hook.py` on `PostToolUse`. That file is **untracked** — tracked
   `.claude/settings.json` wires `spine_rail.py` only. On a fresh clone none of this is measured
   (#458).
4. **The Admiral is absent from the series and that absence is itself the finding.** Every crew here
   holds exactly one binding and produces readings. The Admiral holds two bindings that resolve to
   one gauge path and produces none — same hook, same machine, same minute (#488).

## What it is good for

Comparing **where in a run** a trip lands, per model tier, against the ~17–21% HARD band. W3-C's
first instance tripped on its *wrap-up* gate with the work already complete — which is the shape
worth arguing about, since the cost of that trip was a relaunch to open a PR, not lost work.
