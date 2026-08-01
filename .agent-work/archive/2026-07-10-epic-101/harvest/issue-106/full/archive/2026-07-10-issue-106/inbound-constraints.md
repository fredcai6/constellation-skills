# Inbound constraints carried forward (from crew reviews)

## From g2-review (APPROVE, binding on g4/g5)
- **g4:** every pilot scenario MUST include at least one process check (`checks/*.py`) that genuinely INSPECTS the workspace for completion/spine terminal. A present-but-non-biting check silently PASSes a broken run — the runner delegates completion-verification to scenario checks by contract (§(i) completed-fail row), so a vacuous check defeats the falsification. This is the APPROVE's condition.
- **g5:** the live broken-variant falsification MUST run against biting checks; a vacuous check makes the live falsification meaningless.

## From g4-review (APPROVE-conditional, BINDING on g5)
- **g5 falsification must include TWO variants, not one:**
  1. the contract's named variant (spine template removed → `spine_completed` fails) — proves gross-breakage detection;
  2. a **sentinel-hole variant**: a run that drives the spine terminal AND writes `eval-complete.txt` BUT produces no real solution/test. This is the ONLY thing that exercises the `artifact_present`/`tests_green` sentinel-fallback. Without it, the "g5 covers the fallback hole" rationale is hollow. The expected result: with the current lenient checks this variant PASSES (documenting the floor's limit); it is the evidence that the hole is real and bounded, and the trigger for the deferred triage fix below.

## Triage candidate (from g4-review, deferred)
- Make `dry_run_launch` synthesize a minimal real `solution.py` + `test_*.py` (not just the sentinel), then drop the sentinel fallback from `artifact_present.py`/`tests_green.py` so the process checks strictly require real deliverables while `--dry-run` still PASSes. Closes the vacuous-PASS hole ("spine complete + sentinel but no deliverable"). Bounded runner change; deferred to a follow-up issue.

## From g2-review (forward note for g3)
- The agent-free autouse guard wraps `subprocess.run`. If g3's real `launch_agent` spawns via `subprocess.Popen` / `os.exec*` instead of `subprocess.run`, the guard will not intercept it. g3 should implement `launch_agent` on `subprocess.run`, OR extend the guard to also wrap `Popen`, so the agent-free guarantee stays mechanically enforced.
