# Triage — issue #106 (delegated; recommend-and-defer to Admiral)

Issue-filing is not in this run's Inherited Latitude (the launch order grants latitude on the runner contract, schema, N/M, Euler choices, dry-run design; it does not authorize autonomous issue creation, and the epic Admiral owns cross-cluster triage). So all three candidates are **recommend-and-defer** — surfaced to the Admiral in the Return Shape for epic-closeout routing, not filed here. c2 cites the deferral under LAUNCH_ORDER:Inherited Latitude.

| id | recommendation | priority | rationale |
|---|---|---|---|
| **tc1** | Make `dry_run_launch` synthesize a minimal real `solution.py` + `test_*.py`, then drop the sentinel fallback from `artifact_present.py`/`tests_green.py` so process checks strictly require real deliverables while `--dry-run` still PASSes. | medium | Closes the documented "spine complete + sentinel but no deliverable" vacuous-PASS hole (g4-review). Bounded runner change. |
| **tc2** | Give `launch_agent` an operator-authorized `--permission-mode` passthrough to `claude -p` and document it in `evals/README.md` as a live-run prerequisite. | **high** | The harness is NOT live-runnable as shipped: a headless agent is permission-denied all file creation, so every live run is a false-red (proven at g5). This blocks the harness's core purpose until fixed. |
| **tc3** | Extend the infra-fence: an agent that exits 0 but left the workspace byte-unchanged from the fixture (or was permission-denied all writes) should be `inconclusive`/fenced, not `completed-fail`. | **high** | The fence's job is "environment never fails a good corpus", but a permission-sandbox block currently false-reds a good corpus. Interacts with the g2-ratified "exit-0-no-terminal = completed-fail" rule → route through the contract/review process, not a hot-patch. |

tc2 + tc3 together are the load-bearing finding of this run: **executing the acceptance for real proved the harness machinery works end-to-end but is not yet live-runnable in a permission-restricted headless environment.** That is precisely the kind of signal the harness exists to produce, discovered by self-testing.
