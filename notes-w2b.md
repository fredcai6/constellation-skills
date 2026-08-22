# w2-ledger working notes (sole writer: commander)

## Understand — baseline reconciled against actual code (2026-08-22)

Grep-verified against `scripts/checklist_engine.py` at HEAD (9d5aac6d + worktree):

- `waive()` (:3475-3520): evidence item hardcodes `"produced_by": "human"` (:3511)
  regardless of the `authority` argument actually passed (could be "commander",
  "admiral", any role string). Confirms #503 half 1.
- `override_policy.authority` (docs/CHECKLIST_SCHEMA.md:284): documented as
  "who is expected to accept the risk (**advisory**)" — `waive()` never reads
  `policy.get("authority")` at all, only `policy.get("allowed")` and
  `policy.get("reason_required")`. Confirms #503 half 2: nothing compares the
  passed `--authority` against the condition's declared expectation.
- `trip_ledger` / `_append_trip_entry` (:2167-2263) confirmed ENGINE-WRITTEN ONLY:
  only caller is `_trip_hard_gate`, called from `dispatch()` (:3663) BEFORE
  `_run_verb` for `TRIP_HARD_GUARDED_VERBS` (start/reopen). No CLI verb writes it
  directly — grep across the whole repo (excluding archive/tests) shows zero
  non-engine writers. This is the property to preserve/extend.
- `consolidate --override-reason` (:2906): a **survey**-checklist verb
  (reviewer/interrogator), gates `verdict == APPROVE` while a recorded item is
  `fail`. Structurally unrelated to the gated-spine dispatch chokepoint —
  survey verbs don't run through `_trip_hard_gate`/TRIP_HARD_GUARDED_VERBS at
  all (those are gated-spine-only: start/reopen).

## #259 census — decisive, contradicts the issue's premise

`grep -rn override-reason .agent-work/archive/` (117 files hit) shows **extensive,
routine, sanctioned use**: nearly every multi-round reviewer gate in the archive
(#298, #300, #301, #418-followon, #456, w3a-465, w5-gates, epic-568-510, issue-305,
issue-458) uses `--override-reason` on `consolidate` to record "this check
legitimately fails, verdict is APPROVE anyway, and here is the reasoned why" —
the standard APPROVE-with-findings pattern. #259's claim of "no sanctioned use
case" is **refuted by the evidence**, not confirmed.

**Per the Honest-Null Clause: this is a case where unifying would flatten a real
distinction.** `consolidate --override-reason` is a reviewer's own recorded
judgment about check severity on a survey verdict — never a bypass of
engine-enforced gate-advancement authority. The other three paths (waive, forced
claim/release, trip ledger) are all "the engine let me past a control it would
otherwise have enforced on a GATED spine." Folding the survey-verdict-annotation
into the same ledger as gate-authority bypasses would misrepresent ordinary,
constant, correct reviewer behavior as an audit-worthy override event.

**Recommendation carried into planning:** #259 closes with this evidence — not a
deletion (census shows heavy real use, not zero), not a fold-into-the-ledger
(genuinely different semantics per Honest-Null Clause) — the issue's own premise
was wrong and the fix is documenting why, not code. This is a fix-now (write an
episode + close the misconception), not a filing.

## Scope for the unified ledger (three genuine paths, not four)

1. `waive()` (± `--force`) — scattered per-task `waiver` evidence + `c["waived"]`.
2. `claim --force --reason` / `release --force` — lands in `engine_session` block.
3. `_append_trip_entry` → `trip_ledger` — top-level, append-only, dispatch-gated. The good one.

`skip --reason`, `amend --reason --authority`, `block`/`resume` (named in the
prior-wave verdict as adjacent) are reason-carrying but not override-of-a-control
in the same sense — `amend` already requires non-empty authority+reason and is
its own audited re-plan mechanism; `skip`/`block`/`resume` are status transitions,
not bypasses of a postcondition/authority check. Treat as out of this ledger's
scope unless plan-alternatives surfaces a reason to include one.

## Closeout-must-render-it (#504)

`trip_ledger` is read ONLY by the engine's own trip-advisory/why-supersession
logic (`_latest_why_record`, `_trip_advisory`) — nothing in `spine_lifecycle.py`'s
`finish_work`/`close_work`/`open_pr` path reads it. A run's PR body / archive
summary is caller-supplied prose with no ledger awareness. This is the gap: no
render step distinguishes a run whose ledger is non-empty from a clean one.
