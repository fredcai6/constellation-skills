# Everyone: native CLI engine mechanisms

## Engine-drive compliance

Mandatory, no exceptions: once a role skill is loaded, drive its workflow — checklist, spine, or survey — to
completion through the engine and dispatch each step it names. Within a step (question, check), judgment is
yours — when an instruction does not fit the work, do the closest compliant thing and report the misfit at your
workflow's reporting step (closeout, feedback step, or workflow feedback); reporting misfit is compliance, not
deviation.

How you invoke the engine (the mechanism — controller types, verbs, evidence shape, ordering, the rework and
consolidation guards) is explained once in `references/checklist-engine.md`; each role skill only names
its own spine/survey template and drives it, it never re-explains the engine.

## Engine verbs

- Artifact postconditions (`kind: artifact` — `user-decision`, `review-result`, …): **attach** the evidence
  once, then satisfy a sibling gate's identical artifact postcondition **by reference** — attest that
  gate's postcondition against the evidence id you already attached — instead of re-attaching. E.g.
  attach the APPROVE `review-result` to `gN-review`, then attest `gN-integrate`'s matching
  postcondition against that same evidence id. The engine still verifies
  the referenced artifact exists and matches the required `evidence_type` + `match` (it is not a thin-air
  assert). (`attach`-ing the same artifact to BOTH gates still works — backward compatible.)
- A postcondition whose `check` is `null` is confirmed by **attest** (your manual verification); `attach`
  won't satisfy it. Never hand-edit the checklist JSON to mark a condition satisfied — use `attest` /
  `attach` / `waive`.
- The lease owner is **never blocked by its own staleness**: every mutating verb that **succeeds**
  auto-refreshes `last_heartbeat`, so an actively-working owner never goes stale and a manual `heartbeat` is
  rarely needed. A **refused** verb (ownership gate passed, but the verb itself raised) does **not** refresh —
  a session that only fails can still go stale and be reclaimed. The explicit `heartbeat` verb remains for a
  genuine idle gap. If another session seized the lease during such a gap, recovery is a same-id re-claim
  (idempotent, not a takeover) — free.
- `command` postconditions run under a POSIX shell — author `grep` / `&&` / pipe checks in POSIX form; they
  then behave the same on every platform. On a Windows box without bash/sh the engine **refuses** to run the
  POSIX-form check text through cmd.exe: the check fails **visibly** (returncode 127, marker `no-posix-shell`,
  stderr naming the missing shell) rather than silently passing or being misinterpreted by cmd.exe.

### Completion enforcement (elaboration; canonical source is the engine rail)

This section is prose elaboration, not the enforcement mechanism. The **canonical enforcement source** is
the engine rail string table (`checklist_engine.py`, #140) — the short doctrine block the engine appends to
`claim`, `current`, `start`, `advance`, `attest`, `attach`, and REFUSED responses, keyed to five decision
points (early entry, mid-flight, check-failure, near-terminal, terminal). On any conflict between this prose
and the rail table, **the rail table wins** — it is generated from spine state or the refusal path, not
hand-maintained prose that can drift.

The four transcribed clauses stamped into the high-exposure skills (`references/global-everyone.md`
callers: crew implementer, crew reviewer, `commander-core.md`, admiral, interrogator) are the **measured
transcription** behind this doctrine,
deliberately frozen — do not silently reword them; a wording change re-opens the eval measurement they were
proven under. The six pointer-only skills carry a compressed pointer-with-force sentence instead of the full
four clauses: this is an accepted, untested compression at the getting-IN moment (before any engine call, the
rail cannot yet backstop it) — the rail covers every call from `claim` onward, so the pointer only needs to
survive the pre-first-call window.

**Engine output is the state channel.** Consume engine state via the engine's **output** — `current` is the
complete gate briefing: the full imperative, the open pre/postconditions with their ids and kinds, and the
legal next verbs with the arguments they take. Opening `spine.json` (or a plan/survey JSON) to read state is
a **violation**; hand-editing one to change state is the same violation with consequences, because the engine
owns that file and stamps the provenance — lease, heartbeats, journal — that proves the work was really
driven. If `current` does not tell you what you need, that is an engine defect worth reporting, not a licence
to read around it. Enforcement lint is **deliberately deferred** until post-ship `measure_overread.py`
evidence shows the rule is broken often enough to justify the machinery — its absence is a decision, not an
oversight.

