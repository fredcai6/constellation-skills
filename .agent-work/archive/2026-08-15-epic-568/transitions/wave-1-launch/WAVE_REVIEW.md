## Wave review - boundary wave-1-launch

No wave has run. This is the initial launch boundary, so the evidence classified here is what the latitude interrogation measured rather than what a wave returned.

**Evidence.** Four claims were checked against source, not inherited. The 315 fail-open is present in current main - `checklist_engine.py:787` calls `subprocess.run` with no `cwd=` at all. All 31 member issues are open, so nothing has partially landed. The 441 binding-store gaps are present as filed, and `_save_json_map`'s own docstring records the lock gap as KNOWN, NOT CHASED. The stale-lease population measures 24 active out of 91 tracked spines, not the 43 the issue states.

**Dispositions.** One discrepancy revised the plan: 315's blast radius is corpus-wide, so it is cut as wave 1 alone. One amended the forecast: the 552 denominator mismatch changes wave 2's scope, not wave 1's exit. Two were recorded as evidence only - the Admiral's MCP door is bound to a foreign scratch spine, and `git worktree add` was deliberately left un-precleared, both already covered by sanctioned fallbacks.

**Exit: advance.** The plan is freshly confirmed with the human, no evidence contradicts it, and wave 1's exit criteria are measurable as written.
