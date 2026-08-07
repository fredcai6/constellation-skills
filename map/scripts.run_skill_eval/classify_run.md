# scripts.run_skill_eval:classify_run
function, scripts/run_skill_eval.py:336, 66 lines

```python
def classify_run(outcome: LaunchOutcome, *, completion_present: bool, completion_fresh: bool, process_results: list, workspace_unchanged: bool = False, permission_denied: bool = False) -> RunResult
```

Resolve one launch attempt to exactly one class (contract §(i) infra-fence

table). PURE.

  completed-pass (timeout carve-out): a timed-out run whose workspace ALREADY
                         passes every process check — the checks are monotone,
                         so a finished deliverable is a PASS even though the
                         process was killed before its own exit (issue #126);
  inconclusive (fenced): a timeout with any failing/absent process check, or a
                         usage/rate-limit/overloaded/429 marker sniffed in stderr;
  errored (fenced):      launch failure, corpus mismatch, a permission-sandbox
                         block (exited but left the workspace byte-unchanged AND
                         a permission-denial marker), or a non-zero exit with NO
                         marker AND no completion;
  completed-pass:        completed and every process check passed;
  completed-fail:        completed (incl. exit 0 with no spine terminal) but a
                         process check failed.

A run "completed" when its completion artifact is present+fresh OR the agent
exited 0 — so an exit-0 run with no spine terminal is still tallied (as a
fail if a process check failed), never silently fenced. The permission-block
fence (issue #115 tc3) is the ONE deliberate carve-out of that rule: an agent
that exits 0 but was permission-denied every write leaves the workspace
byte-unchanged, which is the ENVIRONMENT blocking a good corpus, not the corpus
failing — so it is FENCED, not tallied. It is gated on BOTH signals (unchanged
workspace AND a denial marker) so an exit-0 run that genuinely produced the
wrong output — which mutates the workspace — still lands completed-fail per the
g2-ratified exit-0-no-terminal rule.

calls internal: RunResult x9, is_infra_marker
calls stdlib: builtins.list x9, builtins.all x2
reads internal: LaunchOutcome.corpus_mismatch, LaunchOutcome.exit_code, LaunchOutcome.launch_error, LaunchOutcome.stderr_text, LaunchOutcome.timed_out
unresolved: 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
