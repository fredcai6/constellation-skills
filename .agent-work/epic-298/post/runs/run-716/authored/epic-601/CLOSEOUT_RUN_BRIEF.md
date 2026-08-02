# Lessons-audit run brief — epic-601 (Admiral session `admiral-601-20260717`)

## What the run was

The **stage-1 physics-as-feature-engine** program under epic #601: eight dispatched waves
(Phases 0–6 plus the F12 stability rework and the headless-deadlock repair), one Commander per
issue, each in its own provisioned worktree. Phases 0–6 are **all merged and closed**
(#624, #625, #638, #626, #627, #628, #513, #629, #630, plus #623 and #644 as enabling repairs).
Phase 7 (#450, the physics→evo A/B value test) is **deferred by owner ruling** — superseded by a
newly confirmed design spec that reformulates the payload (reference lap + driver utilization)
before any value A/B is worth running.

One long compute job is still live at audit time: the **powered F10 held-out run** (PID 36016,
worktree `C:/Programs/f1-fp-powered`), which is why that worktree is deliberately NOT yet swept.

## Inputs to read (all paths relative to C:/Programs/f1Brainz)

1. `.agent-work/epic-601/ADMIRAL_LOG.md` — the full audit trail: every wave launch, ruling,
   incident, merge, and owned error. This is the primary input.
2. `.agent-work/epic-601/STAGED_CLOSEOUT_LESSONS.md` — lessons staged during the run, already
   written up but never routed.
3. `.agent-work/epic-601/STATE_NOTE.md` — the crash-resume note; its "PENDING closeout items"
   line names the candidate themes the Admiral itself flagged.
4. `.agent-work/epic-601/POWERED_F10_STATE.md` — contains a documented launch-mechanism defect
   worth auditing (PowerShell `-ArgumentList` multi-word argv tokenization).
5. `.agent-work/staged-feedback/*/` — per-worktree staged trios from fenced Commanders
   (624-phase0, 625-segmentation-substrate, 627-unified-basis, 630-phase6-bt-injection,
   638-f12-stability-rework, wave4-626). Check each for un-harvested lesson deltas.
6. `.agent-work/LESSONS.md` — the current inbox. **It is at/near the cap of 20**; the
   playbook-state header carries the live counters. Any `add` must be paired with a `retire`.
7. `.agent-work/AGENT_FEEDBACK.md` — the append-only log the inbox derives from.

## Candidate themes the Admiral already flagged (audit them, do not just accept them)

- **Reap-trap (recurrence, not a new slug):** long single detached completion-watchers get
  harness-reaped mid-run; the fix is bounded chained waiters, each under the reap threshold.
  A sibling lesson already exists — this is a `confirm`, not an `add`.
- **False-stall diagnosis:** two independent sightings this run (Ship H's batch-poll false-stuck;
  Ship I's monitoring-artifact false-stall). Candidate to merge into ONE monitoring-doctrine
  lesson rather than two slugs.
- **Stale map reconcile:** a cartographer reconcile authored against a PR's original base goes
  stale when the PR later takes post-review expansion commits; it must be re-verified against
  the FINAL merged commit.
- **Admiral-steered implementer** and **G5 double-writer** — see the ADMIRAL_LOG.
- **CI-infra failure camouflages a gate miss** — a red CI run whose cause is infrastructure can
  mask a genuine gate failure underneath it.
- **Frozen-methodology compute estimates must factor the thread cap** (#644's blanket
  single-threading roughly doubled per-case fit time against an estimate that predated it).
- **Launch-mechanism argv tokenization:** PowerShell `Start-Process -ArgumentList` did not
  preserve a multi-word element as one argv token, silently splitting `"Great Britain"` into two
  weekend ids. The mitigation used was to omit the argument entirely and let the script's own
  Python-tuple default apply.

## What to return

For **every** candidate, a routed disposition — no candidate may be left unrouted:
graduate-and-retire to a named permanent home / template delta / Charter nomination /
constellation export / lesson-inbox delta / drop-with-reason.

Apply the counting rules faithfully: sibling ids raised from **different worktrees for the same
defect** are `confirm`s of the existing lesson (or an `amend` to reword it), **never** new `add`s
— a new slug for the same defect forks its identity.

Hard constraints:
- Lesson-inbox deltas are written **only** via `apply_lessons_delta.py` — never hand-edit
  `.agent-work/LESSONS.md`.
- Every graduation needs its paired `retire` op in the same delta.
- If an op edits a shipped compact-format JSON template, edit the raw text **surgically**; never
  round-trip through `json.load`/`json.dump` (it reflows the file and destroys blame). Re-validate
  with `json.load` afterward.
- Python is invoked as `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`
  (bare `py` resolves to a wrong runtime in this session).
- **Never** `git add -A` / `git add .`, and never commit `data/*.db`, `.db-shm`, or `.db-wal`.
