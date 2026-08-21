# Wave 2 checkpoint — architecture decision packet

**Epic:** `20260820-deficiency-cleanup` · **Branch:** `afk/20260820-deficiency-integration` @ `efe92791`
**Status:** Wave 2 complete. Contract expires here. Nothing pushed, nothing on `main`, no GitHub mutation.

---

## 1. What shipped

| Lane | Commit | Review | State |
|---|---|---|---|
| #500 refresh consumption | `4999cf89` | APPROVED | merged locally |
| #636 registry worktree selection | `123f1674` | BLOCKED → repaired → APPROVED | merged locally |
| #638 mechanical closeout | `5891e80f` | BLOCKED → repaired → APPROVED | merged locally |
| #613 parent-heartbeat suppression | `9395bc2b` | BLOCKED → repaired → APPROVED | merged locally |
| root `map/` regeneration | `efe92791` | APPROVED | merged locally |

Ordinary suite green at `efe92791`: **3447 passed, 6 skipped, 1222 subtests**, verified twice independently.
`docs/architecture` is an accepted evidenced honest null — no packet map authored, per human ruling.

## 2. The finding

`_is_stale` exists, works, and is called in four places — **none of them a rendering path.**

Running `current` against a plan whose owner died 22 days ago:

```
RAIL: A working solution is the MIDDLE of this run — you are 7 steps from done.
      Next: the ACTIVE line above. Run it.
LEASE active: charter-refresh-20260728 (heartbeat 2026-07-29T17:52:38)
```

Worse, and unasked: `spine_rail.decide_session_start` injects *"Pick the run back up at
this gate and drive it through the engine"* at **session start**, selecting on
`status == "active"` with no staleness check anywhere in the path.

All 58 active leases in this checkout are stale. The system does not fail to warn an
honest agent. It instructs one into the mistake.

**Measured cost, as behavior:** in this repository's history, stale leases have been
reclaimed **0 times by plain `claim` and 25 times by `--force`.**

## 3. What the evidence retired

A reviewer crew dispatched through `run_crew --backend cli` — the shipped path — drove a
seven-gate plan to consolidation. Journal verb census for the whole run:

```
7 record   1 attest   1 consolidate
0 claim    0 release
```

**E1, E2, E3 and E5b all failed to reproduce.** The authority half of this cluster was
substantially manufactured by the Admiral's channel choice. Grants, capability splits and
supervise surfaces answer a question the main path does not ask.

**But the lease is not deletable.** `_entry_mid_flight_view` returns None for a
released/inactive lease, so that leaseless crew ran with the anti-abandonment Stop guard
inert. The lease's **refusal** prevents nothing; its **record** arms the one guard that
fires. Demote it to a presence marker; do not remove it.

## 4. Three errors I made, and who caught them

| I claimed | Truth | Caught by |
|---|---|---|
| No dispatched crew can be railed (E1) | `run_crew --backend cli` crews are fully railed; loss is channel-specific | Lane C, from source |
| A stranded plan cannot be reclaimed (E3) | A **plain `claim`** takes it — no force, no reason, from any directory | Lane A, then measured |
| The hazard is env inheritance (E2) | My `SPINE_*` were unset; it is a session-keyed binding file | The experiment |

A fourth, reported to you and corrected: I said the lineage edge is empty on both channels.
It is empty in `origin.parent` (0/40) but **172 of 545 registry entries carry a real
parent — 32%.** I generalized from n=1.

All three lanes were seeded from that dossier. Two caught my errors unprompted.

## 5. The decision

Ranked by the cold critic under your criterion, then revised by round 2:

1. **Minimal intervention** — messages, defaults, displays. No new subsystem.
2. **Candidate C** — lightest of the authority designs; ~⅓ of its machinery pays an adversary who does not exist.
3. **Status quo** — costs 58 lying leases and an unrailed epic, but beats any subsystem that does not fix the lie.
4. **Candidate A** — best diagnosis, worst bill; its own §9.6 concedes a tenth-cost design wins.
5. **Candidate B** — best measurement, hardest model, leaves the corpse reading `active`.

**Round 2's concrete shortlist**, in ship order:

- **Delete one token:** `"current"` from `RAIL_VERBS` (`checklist_engine.py:457`). This is what makes a dead plan say *Run it.* The five `_RAIL_STRINGS` stay byte-identical, so #145's frozen-string precondition holds. Cost: one pinned test line.
- **Archive banner + rail suppression** under `.agent-work/archive/`, and `HELD` instead of `active`, and `next (for the holder):`. Makes no liveness claim, so it cannot be wrong about liveness. Covers the 718 leaseless plans that today render **no ownership line at all** — the larger half of the defect, unnamed until round 2.
- **Add staleness to `_scan_active_spine`** so SessionStart stops injecting resume orders for dead runs.
- **Exempt `waive` from the session gate** — this, not the `PreToolUse` hook and not `waive` itself, is what forces the five-step handshake. **Do not** achieve it by removing `waive` from `MUTATING_VERBS`: `:3788` reads that set to decide journaling, so the naive edit silently deletes the waiver audit trail.
- **Fix `require_session`'s refusal text** (`:1148-1152`), which currently recommends two filed defects (#632, #369).
- **Delete `--parent`'s optionality** rather than writing a second lineage edge — `crew-runs.json:parent` is already read and gate-enforced by `verify_declared_dispatch.py`.

**Render age, never a verdict.** pid corroboration is missing for 55 of 57 stale leases, so
the stronger signal the critic wanted is not in the data.

## 6. Reconciliation — recommendations only, nothing sent

Ledger items 0, 1, 2, 4 fixed on `main` with named commits (ancestry verified). Item 3 (#500)
is fixed **only** on the unmerged branch — `4999cf89` confirmed not on `main`.

**Hold the close on #500, #613 and #636 until merge.** Closing an issue whose fix lives on an
unmerged branch puts a false statement on the tracker.

#638 partial (architecture question correctly open) · #615 live · #357 mostly stale premise ·
#369 partial · #632 **mis-scoped** — one channel fixed, the in-harness one not.

**New issue candidates, not filed:** the `require_session` refusal text; `origin.parent` never
populated; `init_work_area.py --spine` raw traceback on a `.toml` spec.

## 7. What needs you

1. **Choose the architecture direction** — the shortlist in §5, or redirect.
2. **Merge to main** — surfaced; requires your approval.
3. **GitHub actions** — every close, re-scope and new issue above is drafted and unsent.
4. **Contract refresh** — this contract expires at the end of Wave 2. Anything further needs new latitude.
