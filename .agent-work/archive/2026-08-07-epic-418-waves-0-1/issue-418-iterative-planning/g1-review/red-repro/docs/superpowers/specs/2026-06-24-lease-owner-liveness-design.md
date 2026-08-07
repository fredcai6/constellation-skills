# Lease Owner-Liveness Design

**Issue:** [#32](https://github.com/fredcai6/constellation-skills/issues/32) — Engine: auto-refresh lease heartbeat on mutating verbs (stale-lease refusals across the whole fleet)

**Date:** 2026-06-24

## Problem

The checklist engine's session lease (`scripts/checklist_engine.py`) goes stale
after `lease_stale_seconds` (default 1800) without a heartbeat, and the next
mutating verb is then **refused** until a re-claim. This is the most-recurring
finding across the dogfooding fleet (~5 occurrences in all 3 projects), in two
distinct shapes:

1. **Active work with multi-minute steps** (f1Brainz issue-448 ~8-min g5 re-run;
   story_time execute→closeout) — verbs do fire, but the lease lapses between
   them.
2. **Genuine ~30-min idle between turns** (network_elo) — no verb fires during
   the idle gap, so the *next* verb arrives to an already-stale lease.

Each is worked around with a `--force` / same-id re-claim that **reads as a
takeover in the audit trail**, even though the rightful owner never left.

The refusal fires at verb *entry* (`require_session`), so a naive
"auto-heartbeat at verb *exit*" keeps a session fresh going forward but cannot
rescue a verb that arrives after the window already lapsed — it fixes shape (1)
but not shape (2).

## Principle

Staleness answers exactly one question: **"has the owner gone quiet long enough
that someone else may seize the lease?"** It therefore gates **non-owners
only**. The rightful owner is never blocked by its own staleness, because an
owner issuing a verb *is* the liveness signal. This one rule fixes both shapes
and removes the takeover smell.

## Behavior

### The gate: `require_session` becomes owner-blind to staleness

Ownership is checked **first**. Only the owner+stale cell changes from the
current behavior.

| Arriving session | lease fresh | lease stale |
|---|---|---|
| **owner** (id == lease.session_id) | pass | **pass (self-heal)** ← was: refuse |
| **non-owner** (mismatch, or `--session-id` omitted) | refuse — "owned by active session X" | refuse — "stale; claim it" |
| **no active lease** | pass (legacy, no session needed) | — |

Non-owner refusals are unchanged: the actor-authority guarantee — that a
different session cannot mutate a lease it does not own without an explicit
`claim` — is fully preserved.

**Safety against double-ownership:** self-heal triggers *only* when the arriving
session still **is** the recorded owner. If another session took over (via
`claim`) while the original owner was stale, the lease's recorded `session_id`
is now that other session, so the original owner's next verb hits the id-mismatch
refusal — not self-heal. Two sessions can never both believe they hold the lease.

### The liveness stamp: refresh on a successful mutating verb

After the gate passes, for any verb in `MUTATING_VERBS`, the engine advances the
active lease's `last_heartbeat` to now **iff the caller owns that lease**. This
is the "owner activity = liveness" half: every mutating verb the owner issues
keeps the lease fresh, so shape (1) never accumulates staleness in the first
place, and shape (2) self-heals on the first verb after the idle gap.

The gate (authority decision) and the stamp (liveness write) are kept as
**separate units** so each is independently testable:

- `require_session(cl, verb, session_id, config)` — pure decision: raise or
  return. No mutation.
- `_refresh_owner_heartbeat(cl, session_id)` — if the active lease is owned by
  `session_id`, set `last_heartbeat = _now()`; otherwise no-op. Called from
  `dispatch` immediately after `require_session` passes, for mutating verbs only.

### Silent self-heal (the audit-smell fix)

When the owner self-heals a stale lease, **no** `previous_session_id` or
`takeover_reason` is written — those fields stay reserved for genuine
cross-session takeovers via `claim --force`. The only observable effect is that
`last_heartbeat` advances. The owner resuming its own work does not, and must
not, read as a takeover.

## Deliberately unchanged (YAGNI)

- **`lease_stale_seconds` stays 1800.** With owner self-heal, the window no
  longer needs tuning for the owner; it now governs only non-owner takeover
  timing, where 1800s ("session looks dead") is reasonable. Raising it would
  trade away the lease's dead-session-detection purpose.
- **The explicit `heartbeat` verb stays.** Still useful for a monitor or idle
  wait where no mutating verb will fire and the session wants to signal liveness
  proactively. Rarely needed by the owner now, but removing it is churn and a
  breaking CLI change. Its owner-only refresh semantics are unchanged.
- **No new state fields.** The change reuses `last_heartbeat`,
  `engine_session.session_id`, and `MUTATING_VERBS`.

## Documentation

Fold the new doctrine into the three lease-lifecycle references, replacing any
"a stale lease must be re-claimed before mutating" wording and the issue's
"document that same-id re-claim is idempotent, not a takeover" ask:

- `docs/CHECKLIST_SCHEMA.md`
- `skills/workbench/references/checklist-engine.md`
- `skills/admiral/references/fleet-doctrine.md`

Stated doctrine: *the owner is never blocked by its own staleness; any mutating
verb by the owner refreshes the lease; explicit `heartbeat` is only for idle
waits with no intervening verb; staleness governs only whether a **different**
session may take over.*

## Testing

In `tests/test_checklist_engine.py`:

- **Rewrite** `test_stale_lease_blocks_mutation_until_reclaimed` (currently
  asserts same-session stale → refused): same-session stale now **proceeds** and
  the lease is no longer stale afterward.
- **Add** — owner issuing a mutating verb on a *fresh* lease advances
  `last_heartbeat` (the liveness stamp; previously only `claim`/`heartbeat` did).
- **Add** — owner self-heal of a stale lease writes **no** `previous_session_id`
  / `takeover_reason` (no takeover record).
- **Keep** as regression guards — non-owner against a stale lease is still
  refused with a claim instruction; a different active (fresh) session is still
  refused; `test_heartbeat_only_by_owner` (explicit `heartbeat` unchanged); the
  full-lifecycle CLI test.

## Out of scope

- Reopen-on-regression and any change to non-owner takeover semantics.
- Changing `claim` / `release` / `heartbeat` verb internals (only the gate and a
  new post-gate stamp in `dispatch` change).
