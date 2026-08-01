# Findings — commander-232 (issue #232, epic-226 item F)

Sole writer: commander-232. Working notes, not the verdict (see
`.agent-work/epic-226/verdicts/commander-232.md` for the formal return).

## PR-7 independent re-verification (understand step, before planning)

All three build items' targets were re-grepped/re-read against
`C:/Programs/constellation-wt-232` at fork point `3283158`, independently
of the launch order's own pasted findings:

- **(a) `_glob_to_regex`** — `scripts/checklist_engine.py:449` (def),
  `:496` (call site). `grep -rn "_glob_to_regex" tests/` returned nothing
  before this run. Confirmed live gap, exactly as stated.
- **(b) #205** — `scripts/run_skill_eval.py:938` `_write_meta` did a
  direct `write_text`, no temp file, no `os.replace`.
  `_adopt_existing_runs` (`:1080`) caught `(OSError, ValueError)` on a
  corrupt `meta.json` and `break`, stopping the resume scan (losing every
  subsequent run-dir), instead of routing through `_adjudicate_orphan`
  (`:1042`) like the sibling `"launched"` branch two lines below already
  did. Confirmed live gap.
- **(c) doc-drift** — `run_skill_eval.py` module docstring (`:12-13`),
  `:555` section header, `:1288` seam-selection comment all still called
  `launch_agent`/`temp_install` "inert stubs" though both are real, live
  implementations (`subprocess.Popen`, `install_constellation.install_skills`
  respectively). `install_constellation.py`'s fingerprint-parity comment
  had drifted from the issue's cited `:430-431` to `:531-533` (post-#228
  insertion) and was confirmed stale: `stable_corpus_id()`
  (`run_skill_eval.py:492`) path-normalizes the eval id (#153) so an eval
  run's id and a real install's `compute_corpus_id()` are deliberately
  non-identical when install paths differ.

No honest null on any of the three items — all confirmed live, ungrafted
work exactly as the launch order stated.

## Baseline (measured, own environment)

`python -m pytest tests/ -q` in `C:/Programs/constellation-wt-232` before
any change: **1037 passed, 2 skipped, 250 subtests passed** (skip-guard
exit 0, both skips allow-listed). Coverage on `scripts/checklist_engine.py`
restricted to `tests/test_checklist_engine.py`: **93%**.

Post-change (all 3 items shipped): **1047 passed, 2 skipped, 250 subtests
passed** (+10 net: +9 from item a, +1 from item b's regression test).
Coverage: **94%**.

## Gate-by-gate crew verification

Each of g1 (item a) and g2 (item b) went through a full
implementer->reviewer->Commander-reverification cycle; both APPROVEd with
every claimed number independently reproduced at least twice (once by the
reviewer, once by me). g2's reviewer additionally reproduced the TDD RED
failure in an isolated scratch tree by reverting the fix, and independently
checked out the true pre-g2 commit to verify the baseline count (catching
a one-off arithmetic error in my own g2-reviewer-handoff.md — the
handoff's cited baseline should have read 1046, not 1047; this was a
prose nit only, the actual code/test evidence was correct throughout).

Item c was run as a reasoning gate (crew-waived: comment-only edit,
context already held) with three pre-authored grep-absence command
postconditions instead of a crew review — all three passed.

## Fencing note

The main checkout carries an ACTIVE Admiral epic-226 lease
(`admiral-epic-226-b`) throughout this run, confirmed at the `context`
step. Per `agent_work_root.py`'s documented exception, this fences the
main checkout's `.agent-work/` read-only for this delegated Commander, so
the `feedback` step's AGENT_FEEDBACK/lessons-delta/CONSTELLATION_FEEDBACK
trio was staged (not applied) under
`C:/Programs/constellation-wt-232/.agent-work/staged-feedback/232/`, with
a `FENCE.md` citing this launch order, for the Admiral to harvest at epic
closeout. Full detail in that staged trio, not duplicated here.
