# W2-130 Report — runner durability (#130)

**Commander:** commander-runner (delegated) · **Model:** opus · **Date:** 2026-07-19
**Branch:** `fix/runner-durability-130` (base `d524b41`) · **PR:** https://github.com/fredcai6/constellation-skills/pull/204 (open — Admiral merges)

## Verdict
**PARTIAL NULL + one green PR.** The #130 durability *mechanism* was already fully implemented and
unit-tested in the base; the one genuine gap versus the launch order's regression bar — a test that
actually **kills a real runner process** — is delivered by this PR. One green, reviewed (APPROVE) PR
adding a single regression test. No production-code change; `scripts/run_skill_eval.py` untouched;
#197's `stable_corpus_id` untouched.

## Worktree isolation (paste, exit 0)
```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-runner
worktree OK: in C:/Programs/cs-wt-runner
EXIT=0
```

## Reconciliation finding (the load-bearing result)
Base `d524b41` **already ships the full #130 durability machinery**, via two commits in the base:
- `88db7a5 fix(evals): runner durability — resumable meta, orphan watchdog, heartbeats (#130)`
- `a3a4eb8 fix(evals): amend #130 durability — reap-safe drive, pid recording, preserved liveness (round-1 diagnosis)`

Covered vs. still-exposed (per the Honest-Null Clause):

| #130 hardening direction | Status in base | Evidence |
|---|---|---|
| Resumable meta (`launched` before launch, merged finalize) | **SHIPPED** | `_run_once` L991; `test_meta_json_written_incrementally...`, `test_final_meta_preserves_launch_liveness_fields` |
| Heartbeats + `subject_pid` | **SHIPPED** | `launch_agent` L722/L732-747; `test_launch_agent_stamps_heartbeat...`, `test_launch_agent_records_subject_pid` |
| Independent wall-clock watchdog | **SHIPPED** | `_adjudicate_orphan` L1042; `test_adjudicate_orphan_*` |
| Resume / re-adoption | **SHIPPED** | `_adopt_existing_runs` + `run_scenario(resume=True)`; `test_resume_recovers_killed_runner...`, `test_sequential_one_run_resumes...` |
| Per-run isolation | **SHIPPED** | loop try/except L1183; `test_per_run_isolation_one_run_exception...` |
| Reap mitigation (`--max-new-runs`) | **SHIPPED** | `run_scenario` L1173-1178; `test_max_new_runs_caps...` |
| **Test that actually kills a real runner process** | **GAP → THIS PR** | the base's "regression bar" test only *hand-seeds* the post-death disk state |

## Root-cause finding for the original 0-byte-transcript death
Already diagnosed by round-1 (`a3a4eb8`) and documented in-code (`run_scenario` `max_new_runs`
comment): the runner process was **reaped by the environment at ~60 min cumulative lifetime, mid-run**
— NOT by its own 2400s deadline. It died ~12 min into run-2, but runs 0+1 had already consumed the
rest of the ~60-min window; the both-crews run was simply the deepest/slowest so it was in flight when
the reap fired. The 0-byte transcript is consistent with a SIGKILL of the parent before its daemon
drain-threads flushed the subject's buffered stdout to `transcript.txt`. Addressed in base by the reap
mitigation (short-lived `--max-new-runs` invocations) + resumable meta + orphan watchdog. This PR adds
the proving test.

## Durability design + why (smallest design meeting the bar)
Per the pre-ruling ("prefer resumable-meta + watchdog; smallest design; no re-architecture"), the
mechanism already exists, so the deliverable is the missing **real-process-death regression test**,
`test_real_runner_process_death_leaves_resumable_state`:
1. launches a **real** `[sys.executable, RUN_SKILL_EVAL, <scenario>, --keep-temp --worktree <wt>
   --command <hang.cmd> --max-new-runs 1]` subprocess (fake hang subject = a generated `.cmd` running
   `py -c "import time; time.sleep(600)"`, empirically verified spawnable under `Popen(shell=False)`
   on this Windows box);
2. bounded-polls until `run-0/meta.json` is `launched` with `subject_pid`;
3. **kills the live runner tree via the module's own `rse._tree_kill` (`taskkill /PID <pid> /T /F`)** —
   Windows process APIs, not a POSIX `kill -9`;
4. asserts the real death left the resumable contract (`run-0` meta still `launched`, `subject_pid`,
   `skills/CORPUS.json` present);
5. proves in-process `run_scenario(resume=True, installer=<refuses reinstall>, launch=<fake pass>)`
   adjudicates the orphan to `completed-pass` (`adjudicated_orphan is True`) and reaches a verdict.

Design-it-twice: chose this over "a second real subprocess for the resume leg" (rejected — doubles
subprocess/concurrency fragility, proves nothing the in-process resume path doesn't). Concurrency-
failsafe lesson applied: the runner is wrapped in `try/finally` that **always** tree-kills it, bounded
waits only, stdio file-redirected (no reader threads).

## Evidence
- Runner-death simulation test: **`test_real_runner_process_death_leaves_resumable_state` — 1 passed (~3s)**,
  proving resumable/adjudicable state after a real `_tree_kill`.
- Full suite: **89 passed in ~21s** (was 88; +1), including `test_corpus_id_install_path_invariant` (#197).
- `git diff --stat`: **only `tests/test_run_skill_eval.py` (+156)**; `scripts/` unchanged.
- Independent reviewer (opus) reproduced all three + a tasklist scan showing **0 orphaned subjects**
  (corroborating the failsafe). Verdict **APPROVE**, no blockers.
- Engine drove the full spine init→archive; both leases released after the terminal advance.

## Map impact
None. Skill-source repo with no packet map; the change is test-only, touching no schema, design doc,
or production structure. Reconcile recorded a reasoned structural no-op (compliant).

## Triage candidates (recommend-and-defer — Admiral's call to file)
- **tc1 — atomic meta write + corrupt-meta resilience** in `scripts/run_skill_eval.py`: `_write_meta`
  is a non-atomic `write_text`, and `_adopt_existing_runs` `break`s on a corrupt meta (silently
  truncating resume of later runs). A runner killed *mid-write* of `meta.json` could hit this.
  Verdict-safe today (degrades to redoing one run, no false FAIL), so out of scope for the smallest-
  design bar. Recommend atomic temp+`os.replace` write and treating a corrupt orphan meta as
  adjudicable rather than a scan-halt. Surfaced independently by both crews. Filing is FLOAT-reserved
  to the Admiral per Inherited Latitude — not filed. Full recommendation:
  `C:/Programs/cs-wt-runner/.agent-work/archive/2026-07-19-runner-durability-130/TRIAGE_tc1.md`.

## Workflow feedback — fenced trio staged (Admiral: harvest before sweeping the worktree)
Path: **`C:/Programs/cs-wt-runner/.agent-work/staged-feedback/runner-durability-130/`**
- `AGENT_FEEDBACK.md` — run retrospective (reconciliation-first was load-bearing; two crew frictions).
- `lessons-delta.json` — tick + one `handoff`-scope add `observe-midprocess-state-not-via-end-output`
  (don't instruct a crew to observe a mid-process state via end-of-process output; it never fires under
  hard tree-kill).
- `CONSTELLATION_FEEDBACK.md` — two non-blocking engine-CLI ergonomics notes (RAIL banner on stderr
  masks result lines; `flag-candidate` arg shape differs from sibling verbs).
- `FENCE.md` — cites this launch order as the fence basis.

## Notes for the Admiral
- No float was needed; the Honest-Null Clause + Inherited Latitude covered the "mechanism already
  shipped, deliver the missing test" case. If you'd prefer the PR title track the honest scope, a
  more literal title would be `test(evals): real-process-death regression for runner durability (#130)`
  (the commit uses that); I kept the launch-order-specified PR title verbatim.
- Merge is yours. tc1 is the natural #130 follow-up if you want the mid-write window closed too.
