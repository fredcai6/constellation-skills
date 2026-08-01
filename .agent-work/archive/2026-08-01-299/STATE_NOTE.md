# Crash-resume state note — 299

- **step:** execute · gate g1-capture (five measured baseline runs at the pin)
- **slug:** 299, branch `epic-298/299`, worktree `C:/Programs/constellation-skills-wt/e298-299`
- **next command:** `py .agent-work/epic-298/baselines/verify_capture.py` — it names exactly which of the five runs is missing or unverified; re-run `py .agent-work/epic-298/baselines/capture_baseline.py --issue <N> --worktree C:/Programs/f1bwt/b<N> --out .agent-work/epic-298/baselines/runs/run-<N> --skills <corpus> --corpus-id <id>` for each one it names, then `py .agent-work/epic-298/baselines/extract_ordering.py .agent-work/epic-298/baselines/runs/run-<N>`
- **pid:** none — foreground (captures run in-turn, polled, never detached)
- **expected artifact:** `.agent-work/epic-298/baselines/runs/run-<N>/{stream.ndjson,meta.json,ordering.json}` for N in 690 688 698 716 704, then `BASELINE_RECORD.md`

_Updated: 2026-08-01T21:00:00+00:00_

## Resume notes

- The rubric is frozen at commit `a226642b` and **must not be edited** after that commit —
  a rubric changed after results exist grades the results. If a fresh agent believes the
  rubric is wrong, it floats to the Admiral; it does not edit.
- The pin is `3541d2929b19de37107ae13e56776b7162d07255`. `capture_baseline.py` refuses to
  launch into a worktree that is not at the pin, and refuses a non-pristine worktree.
- f1Brainz is READ-ONLY. No push, no PR, no issue comment, no commit. A forbidden operation
  in any transcript is a stop condition — `verify_capture.py` fails and names the call.
- Corpus install root and id are recorded in each run's `meta.json`; re-derive with
  `run_skill_eval.temp_install` + `write_stable_corpus_marker` if the temp root is gone.
