# Crash-resume state note — issue-305

- **step:** execute · gate g1-implement (assembly seam: emit the context manifest from `start()`/`reopen()`)
- **slug:** issue-305 · branch `epic-298/305` · worktree `C:/Programs/constellation-skills-wt/e298-305` · base `967493c` · WIP commit `fba7fae`
- **next command:** `cd "C:/Programs/constellation-skills-wt/e298-305" && python scripts/checklist_engine.py --file .agent-work/issue-305/execute.json current`
- **pid:** none — crew dispatched as an Agent-tool subagent (`backend: external`), registry entry `constellation/issue-305/g1-implement/implementer/attempt-2`
- **expected artifact:** `.agent-work/issue-305/crew/g1-implement-result.md` (IMPLEMENTER_RESULT), then `scripts/episode_capture.py` wired into **both** `checklist_engine.start()` and `reopen()`

**Resume context a fresh agent needs and cannot get from `current` alone:**

Engine lease on the spine is `commander-305-e298`; pass `--session-id commander-305-e298` on every
mutating engine call against `spine.json`. Spine: `.agent-work/issue-305/spine.json`. Gate plan:
`.agent-work/issue-305/execute.json`. The g1 crew's own gated plan:
`.agent-work/issue-305/crew/g1-implement-plan.json` (lease `impl-305-g1`).

**Drive the WORKTREE engine (`scripts/checklist_engine.py`), not the installed one.** The predecessor's
state note pointed at the installed copy; this run is modifying the engine, so mixing binaries mid-run
is the hazard. Consistency matters more than which copy.

Read `PLAN_CRITIC_DISPOSITION.md` **before** `CONVERGENCE.md` — the disposition reverses the
convergence's seam choice and voids its negative control. Where they disagree the disposition wins.

**All three predecessor floats are now ANSWERED by the Admiral** (superseding the STATE_NOTE that
listed them open): (1) `refusals` **is in scope**, additive only, with `docs/CHECKLIST_SCHEMA.md`
updated in the same PR, a proof the counter can be wrong, and the #344 latency stated; (2) seam is
`start()`+`reopen()`, write-if-absent — **confirmed**; (3) **mechanical snapshot, not auto-created
episodes** — and `docs/EPISODE_STORE.md:781` is a defect to correct in this change.

**Crew attempt-1 died with the predecessor** (session usage limit), mid-`m3-seam`. It left real work:
`scripts/episode_capture.py` complete, `start()` wired, `reopen()` **not** wired, and two red tests.
Abandoned and relaunched as attempt-2 into the **same** job file — job-file-not-agent-file.

_Updated: 2026-08-02T02:15:00Z_
