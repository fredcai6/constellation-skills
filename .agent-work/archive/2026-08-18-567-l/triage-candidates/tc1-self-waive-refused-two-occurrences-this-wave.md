# Candidate: the door refuses a session waiving a check on its own bound spine — hit twice in one wave

**Status:** recommend-and-defer (pre-ruling `decision:no-issue-filing-mid-run` — file nothing this run)

## What happened

At lane L's `plan.c6` (`map_orient.py verify-frame`), `spine_evidence action=waive` was refused
unconditionally, regardless of the `authority` value passed: *"a crew must not waive its own
bound spine check — always ask up."* The refusal's own recovery text names two routes for a
parent to act on the child's spine instead, and both are filed defects: passing the child's
session id (impersonation, **#632**) and `claim --force` (erases actor attribution, **#369**).
Neither is actually usable.

The working recovery, worked out live over a cross-session exchange with the Admiral:
1. child calls `spine_halt action=block`, naming the blocker, and releases its lease;
2. parent binds to the same `spine.json`, claims it under its own real identity, waives with
   the full reason, releases;
3. child reclaims and calls `spine_halt action=resume`.

Nothing in the engine or its doctrine documents this sequence.

## Why this is now worth more than a one-off note

**This is the second occurrence in a single wave, in two different lanes.** Lane J hit the exact
same refusal earlier in epic-567-door's wave 3; lane L (this run) hit it again at `plan.c6`
independently. One occurrence reads as bad luck. Two in one wave, on the same check
(`verify-frame`), in two different Commander runs, is a mechanism gap worth fixing rather than
working around by hand each time.

## Recommendation

File an issue (once past this pre-ruling's mid-run restriction) proposing one of:
- a documented, first-class `spine_halt`/`spine_evidence` handshake verb for "parent waives a
  child's check the child cannot waive itself," replacing the ad hoc release-claim-waive-release-
  reclaim sequence with something the engine names and the refusal text points to directly; or
- narrowing the self-waive refusal so a check the *waiver text itself* already declares waivable
  for a stated class of run (e.g. `plan.c6`'s own "waive it for a genuinely trivial change" language)
  does not require full parent handoff at all.

Either fix should close **#632** and **#369** in the same pass if practical, since both are the
dead-end routes this refusal's own text currently offers in place of the real recovery.

## Provenance

- First occurrence: lane J, epic-567-door wave 3, `plan.c6`, 2026-08-18 (per the Admiral's message
  to this lane).
- Second occurrence: lane L (this run), epic-567-door wave 3, `plan.c6`, 2026-08-18. Resolved via
  the handshake above; Admiral confirmed authority=admiral (not human — the check is reversible
  and no human has ruled on it specifically) and independently reproduced the refusal on this
  lane's own frame before waiving.
- Note: this repo's own `.agent-work/*/triage-candidates/` did not contain a prior write-up of
  the first (lane J) occurrence as of this lane's triage step — it may live in lane J's own
  worktree (a separate `.worktrees/` checkout not visible from here) or have been passed to the
  Admiral out of band. Recommend the Admiral merge this candidate with lane J's original note,
  if one exists, rather than filing both separately.
