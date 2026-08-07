# Lessons: apply-or-defer — close the bank-but-never-apply gap

Status: design for review · 2026-06-27

## Context

The recursive-improvement loop has a write path, a queue, and a nag — but no trigger to **act**:

- `apply_lessons_delta.py` banks lessons into `LESSONS.md` with scope-split counters. For most scopes a
  `confirm` is *trust* (`+confirmed`); for a `constellation` lesson it is the opposite — a recurrence of an
  unfixed shared-machinery defect (`+recurrences`, status `recurrence-debt`, **pinned**, never auto-deleted).
- The script even prints a nag — *"recurrence-debt: N constellation lesson(s), M unfixed recurrence(s) —
  fix upstream, don't keep confirming"* — but **nothing consumes it**.
- The closeout `Template Update Candidates` table is advisory with a self-reported disposition; the design
  doc itself calls it *"easily skipped — promote it to a forced question."*

So lessons accumulate and get **confirmed** repeatedly while never being **applied**. f1Brainz #522 named
it: the same proven handoff mitigations were re-derived every gate because they lived only in `LESSONS.md`,
until the user hand-baked them into `CREW_CONTEXT.md` / `ORCHESTRATOR_CONTEXT.md`. The system confirmed
those lessons 9× without once asking *"should we apply them?"*.

Two things make now the right time. (1) The global-doctrine work (PR #41) created the **apply targets**
that did not exist before: general-workflow `constellation` lessons now have a home (`skills/_shared/global-*.md`),
and project lessons map onto the thin local delta docs / templates. (2) "Apply" is the move the human keeps
making by hand; the loop should prompt it.

**Goal:** make **apply-or-defer** a first-class, *forced* outcome for every ripe lesson — distinct from
"confirm" — so a validated, fixable lesson stops being silently re-banked.

## Decisions (settled in brainstorming, 2026-06-27)

1. **Coverage — unified across scopes.** Any ripe lesson forces an apply-or-defer, routed by scope:
   constellation → upstream; project → local context doc / template.
2. **Trigger — threshold-gated ripeness** (validation before promotion). Force only when a lesson is
   validated by recurrence/confirmation *and* names an editable target.
3. **Mechanism — feedback-step gate.** Where lessons are already distilled; an engine postcondition refuses
   to advance until every ripe lesson has a recorded disposition.
4. **Authority — Commander applies, bounded + human-confirmed.** Project → edit the thin local target;
   constellation → export. Escalate to Charter only for broad/contradictory doctrine shifts. Autonomous
   run without the latitude class → auto-defer "needs human."

## Data model (extends the existing playbook; *LLM proposes, script applies* preserved)

The LLM never edits `LESSONS.md` directly; it proposes ops, `apply_lessons_delta.py` applies them.

- **New optional field `target`** on a lesson — the editable artifact it would be applied to, e.g.
  `docs/agents/CREW_CONTEXT.md`, `.agent-work/templates/IMPLEMENTER_HANDOFF.template.md`,
  `skills/_shared/global-crew.md`, or `CONSTELLATION_FEEDBACK.md`. Set on `add` / `amend`. A lesson with no
  target is **not applicable** — it can only be internalized (`retire`) or kept.
- **New statuses** `deferred` and `exported`, joining `active | charter-review | recurrence-debt`.
- **New ops** in `apply_lessons_delta.py`:
  - `apply` — requires `target` + `applied_evidence` (citation of the edit: file+section or commit). For a
    **non-constellation** lesson it **deletes the lesson** (paid: the mitigation is now encoded in a durable
    target — same "retire deletes, no graveyard" semantics, with a stronger required citation). Refused for
    `constellation` scope (you cannot fix shared machinery from inside the project — route to `export`).
  - `export` — `constellation` only; requires the `CONSTELLATION_FEEDBACK.md` citation. Sets status
    `exported` and **keeps the lesson pinned** (the local-visible debt persists until upstream ships). A
    later run that sees the fix landed `retire`s it (the existing "constellation defect fixed upstream" path).
  - `defer` — any scope; requires `reason`; sets status `deferred` and records the recurrence/confirmed
    count *at* deferral. Re-fires only when the count climbs past that mark (no per-run nagging, no dropping).
    `route-to-Charter` is a `defer` with that reason.
- **Thresholds** live in the `playbook-state` marker (beside `cap` / `dormancy-runs`): defaults
  **constellation `recurrences ≥ 1`**, **non-constellation (handoff / commander / admiral / project)
  `confirmed ≥ 3`** (the design doc's N). Tunable per repo.

Retire-on-apply is the rule the user emphasized: **paid-and-encoded ⇒ gone; queued-but-not-yet-fixed ⇒ pinned.**

## The forced gate (the consumer the nag never had)

- **Ripeness is computed deterministically** in `apply_lessons_delta.py` (it owns the lesson model,
  counters, and thresholds): a lesson is *ripe* when its scope threshold is crossed and it lacks a terminal
  disposition this cycle. Exposed as a function plus a `--ripe` CLI emit.
- **A verifier `verify_lessons_applied.py`** (sibling of `verify_agent_feedback.py`) calls that ripeness
  function and **exits non-zero while any ripe lesson is unpaid** (neither `apply`/`export`ed nor freshly
  `defer`red). Wired as an engine **`command` postcondition on the Commander `feedback` step** (absolute
  bundled path, POSIX-safe) — this is what converts the skippable advisory table into a hard gate.
- Degrades cleanly: no `LESSONS.md`, or no ripe lessons ⇒ passes.

## Apply / defer by scope (authority routing)

- **Non-constellation lesson** (project / handoff / commander / admiral) → Commander makes the bounded edit
  to the named local target — a thin context doc or a project template working copy — gated on a **human
  `user-decision`**, then `apply` (deletes from bank). A broad or contradictory doctrine shift is not edited
  inline — disposition `defer` with reason `route-to-Charter`.
- **Constellation lesson** → `export` to `CONSTELLATION_FEEDBACK.md` (the existing channel; the skills-repo
  metabolize + the new global buckets are where it actually lands), status `exported`, pinned until shipped
  upstream then retired. "Apply" here = *guarantee it is queued*, never silently re-confirmed into a debt.
- **Defer** always carries a reason and is recurrence-bounded.

## Autonomous (Admiral-delegated) mode

- "Apply a lesson / fold doctrine" becomes a **decision class in `LATITUDE_CONTRACT`**. Delegated → the
  Commander/Admiral applies and logs a ruling in `ADMIRAL_LOG`. Not delegated / human unreachable →
  auto-`defer` with reason `needs human — outside latitude`. The Admiral `closeout` runs the same
  `verify_lessons_applied.py` across the epic.

## Files touched (reuse-heavy, bounded build)

- `scripts/apply_lessons_delta.py` — `target` field; `apply` / `export` / `defer` ops; thresholds in the
  state marker; `--ripe` emit + a `ripe_lessons()` function.
- `scripts/verify_lessons_applied.py` — **new** verifier (the gate).
- `skills/commander/templates/COMMANDER_SPINE.template.json` — `feedback` step imperative + a `command`
  postcondition running the verifier.
- `skills/admiral/templates/ADMIRAL_SPINE.template.json` — same verifier as a `closeout` postcondition.
- `skills/admiral/templates/LATITUDE_CONTRACT.template.md` — the "apply lessons" decision class.
- `skills/workbench/templates/LESSONS.template.md` — document the new field, statuses, ops, thresholds.
- `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` — **retire the `Template Update Candidates`
  table**; template-fix candidates become lessons carrying a `target`. (Flagged for review — it is the one
  removal, not an addition.)
- `scripts/install_constellation.py` `SKILL_SCRIPT_BUNDLES` — bundle `verify_lessons_applied.py` into
  `commander` and `admiral` (mirrors `verify_agent_feedback.py`).

## Testing

- `apply_lessons_delta.py`: each new op (`apply` deletes non-constellation + requires target/evidence;
  `apply` refused for constellation; `export` sets `exported` + pins; `defer` records count + re-fire
  semantics); threshold parse/round-trip in the state marker; all-or-nothing validation unchanged.
- `ripe_lessons()`: constellation `recurrences ≥ 1` and non-constellation `confirmed ≥ 3` selected;
  deferred lessons suppressed until the count climbs; targetless lessons excluded.
- `verify_lessons_applied.py`: passes on no-LESSONS / no-ripe; fails on an unpaid ripe lesson; passes once
  applied/exported/deferred. Exit codes drive the engine postcondition.
- Engine smoke: a `feedback` step with one ripe lesson refuses advance until disposition recorded.

## Out of scope (separate, enabled by this)

- The actual upstream **metabolize** of exported constellation lessons in the skills repo (`collect_feedback.py`
  → fold into `skills/_shared/global-*.md`). This spec only guarantees the in-project export/disposition.
- The broad **"any actionable lesson"** trigger (rejected in favor of threshold-gating).
- A full Charter-refresh redesign — `route-to-Charter` remains a disposition, not a new Charter mechanism.
