Closes #32.

## The finding

The checklist engine's session lease went stale after `lease_stale_seconds` (default 1800) and then **refused the next mutating verb — even from the lease's own owner** — forcing a `--force` / same-id re-claim that reads as a takeover in the audit trail. It was the most-recurring finding across the dogfooding fleet (~5 occurrences in all 3 projects), in two shapes: active work with multi-minute steps, and genuine ~30-min idle between turns.

## The principle

Staleness answers exactly one question — *"has the owner gone quiet long enough that someone else may seize the lease?"* — so it should gate **non-owners only**. The rightful owner is never blocked by its own staleness, because an owner issuing a verb **is** the liveness signal.

## The change

Two small, separable pieces in `scripts/checklist_engine.py`:

- **`require_session` becomes owner-blind to staleness** — ownership is checked first; the owner passes regardless of staleness. Only the *owner + stale* case changes (refuse → pass). Every non-owner refusal is unchanged: a different active session, and a different session against a stale lease, are still refused exactly as before.
- **A liveness stamp** — a new `_refresh_owner_heartbeat` helper, wired into `dispatch` after the gate, advances the owner's `last_heartbeat` on every mutating verb. So an actively-working owner never goes stale, and a genuine idle gap self-heals on the owner's next verb.

The self-heal is **silent**: it writes no `previous_session_id` / `takeover_reason` (those stay reserved for genuine cross-session takeovers). That removes the "re-claim reads as a takeover" audit smell.

**Deliberately unchanged (YAGNI):** `lease_stale_seconds` stays 1800; the explicit `heartbeat` verb stays (now only needed for idle waits with no intervening mutating verb); no new state fields or config.

## Safety

- **Authority preserved:** the ownership-first reordering keeps every non-owner refusal reachable and unchanged (verified across different-active, different-against-stale, and `None`/missing-session cases).
- **No double-ownership:** if another session took over (via `claim`) while the original owner was stale, the recorded owner is now that other session, so the original owner's next verb hits the id-mismatch refusal — not self-heal.

## Docs

Folded the new doctrine into the three lease-lifecycle references — `docs/CHECKLIST_SCHEMA.md`, `skills/workbench/references/checklist-engine.md`, `skills/admiral/references/fleet-doctrine.md` — replacing the old "a stale lease must be re-claimed before mutating" wording. The admiral fleet-doctrine note that told agents to *expect* the stale-lease refusal is retired.

## Testing

- TDD: rewrote `test_stale_lease_blocks_mutation_until_reclaimed` → `test_stale_lease_self_heals_for_owner` (owner self-heal + asserts no takeover record), and added a non-owner-still-refused regression guard, an end-to-end stamp-through-`main` integration test, and a helper no-op unit test.
- Full suite: **205 passed, 15 subtests passed.**

Built subagent-driven (per-task TDD + spec/quality review + opus whole-branch review: *Ready to merge = Yes*, no Critical/Important/Minor blockers).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
