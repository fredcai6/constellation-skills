# Agent Feedback

## 2026-07-19 — runner-durability-130 (delegated commander, #130 runner durability)

**Run shape.** Delegated commander under a frozen Admiral launch order, no reachable human. Drove
the full spine (init → context → understand → plan → execute → reconcile → triage → review →
feedback → archive) through the engine. One crew gate (implementer + reviewer), both opus.

**Followed the skills closely.** The gated spine, crew dispatch via `run_crew.py --backend external`
+ `--verify-result`, mission frame, design-it-twice (compressed) and cold-critic-skip-as-named-road,
and the delegated `user-decision`-cites-launch-order mechanism all worked as written.

**The load-bearing moment was the baseline reconciliation.** The launch order framed #130 as
largely unimplemented (runner-death case "PR #125 does not cover"). Reading `run_skill_eval.py`
against git log showed the FULL #130 mechanism already shipped in the base via `88db7a5`
(resumable meta, orphan watchdog, heartbeats) + `a3a4eb8` (reap-safe drive, pid recording,
preserved liveness). The delegated-commander doctrine's "reconcile the order's assumed baseline
against the actual code before planning" is exactly what caught this, and the launch order's
Honest-Null Clause anticipated it. The genuine in-scope gap was the one thing the base lacked
against the regression bar: a test that actually KILLS a real runner process — the base's
"THE regression bar" test (`test_resume_recovers_killed_runner_mid_measurement`) only HAND-SEEDS
the post-death disk state. Delivered that real-kill test; no production-code change needed.

**Crew workflow feedback harvested (from the two IMPLEMENTER/REVIEW results).**
- Implementer friction 1: the handoff cited `rse.RUN_SKILL_EVAL`, but `RUN_SKILL_EVAL` is a
  module-level constant in the TEST file (`tests/test_run_skill_eval.py`), not an attribute of the
  imported `rse` module — cost one red run. Handoff-authoring lesson: when naming a symbol the crew
  must reuse, verify WHERE it is defined, not just that it exists.
- Implementer friction 2: the handoff said "discover the kept temp dir by parsing the runner's
  `kept temp dir:` stderr line." That is structurally impossible here — the line prints in a
  `finally` only AFTER `run_scenario` returns, which never happens while the subject hangs and is
  skipped entirely under a hard tree-kill. The implementer correctly pivoted to a child-scoped
  `TMP`/`TEMP` env to locate the temp dir. Lesson: do not instruct a crew to observe a MID-process
  state via END-of-process output; the observation channel must survive the very kill being tested.
- Reviewer: independently reproduced 89 passed + a tasklist orphan scan (0 orphaned subjects,
  corroborating the concurrency-failsafe), and corroborated the atomic-write triage candidate. One
  non-blocking nit: the new test's top-level `v.status in ("PASS","INCONCLUSIVE")` is looser than
  its strict orphan-adjudication asserts — acceptable.

**Engine-CLI ergonomics (minor).** The `RAIL:` banner prints to stderr on EVERY engine call, so a
`... 2>&1 | tail -1` grabs the banner rather than the result line — had to filter `grep -v '^RAIL'`
or inspect the spine JSON directly to confirm outcomes. And `flag-candidate` takes `--from` +
`--statement` (not the `--field` shape the other verbs use); first attempt errored. Both are minor;
noted in CONSTELLATION_FEEDBACK.

**Nothing was blocked; no float needed** — the Honest-Null Clause + Inherited Latitude covered the
"mechanism already shipped, deliver the missing test" case squarely.

**Friction / unclear**
- The launch order framed #130 as largely unimplemented, but the base already shipped the full
  mechanism (`88db7a5` + `a3a4eb8`). The delegated-commander "reconcile assumed baseline vs actual
  code" step + the Honest-Null Clause resolved it, but the framing gap cost real reconciliation time.
- Engine `RAIL:` banner prints to stderr on every call, so `2>&1 | tail -1` reads the banner, not the
  result — had to `grep -v '^RAIL'` or read the spine JSON to confirm each op landed.
- `flag-candidate` uses `--from` + `--statement`, not the `--field k=v` shape of sibling verbs;
  first attempt errored.

**Crew-reported friction**
- Implementer: handoff cited `rse.RUN_SKILL_EVAL`, but `RUN_SKILL_EVAL` is a constant in the TEST
  file, not on the `rse` module — cost one red run.
- Implementer: handoff's "discover the temp dir via the `kept temp dir:` stderr line" is impossible
  under hang + hard tree-kill (the line prints in a `finally` after return, which never happens);
  crew pivoted to a child-scoped `TMP`/`TEMP` env. Banked as `observe-midprocess-state-not-via-end-output`.
- Reviewer: one non-blocking nit — the new test's top-level `v.status in ("PASS","INCONCLUSIVE")` is
  looser than its strict orphan-adjudication asserts.

**Improvement signals**
- The reconciliation-first discipline (git log of the target file vs the order's framing) is what
  turned a would-be redundant reimplementation into an honest, minimal, bar-meeting deliverable —
  worth reinforcing in delegated launch orders (state the assumed baseline as a claim to verify).
- Atomic-meta-write + corrupt-meta resilience surfaced by BOTH crews independently (triage tc1) —
  a real #130 follow-up, recommended to the Admiral.
