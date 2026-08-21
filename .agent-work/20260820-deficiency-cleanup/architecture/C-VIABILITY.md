# Is option C viable?

**Lane:** Wave 3 bounded viability investigation (investigation only — no design, no
implementation, no GitHub, no `mcp__spine__*`).
**Date:** 2026-08-21. **Baseline:** `main` @ `24b4665b`, working tree unmodified.
All simulation ran on copies under a scratch directory; no production file, test,
`map/`, or foreign plan was touched.

---

## Verdict

**NOT VIABLE AS SCOPED — dominated.**

Not because C breaks something. Because **C does not deliver its own stated benefit**,
and the benefit it was proposed for is obtainable from a strictly smaller change that
touches one function and zero refusal paths.

C's premise, from the handoff: *"The lease's refusal prevents nothing; its **record**
arms the one guard that fires. C keeps the record and drops the permission."*

The second half of that premise is false. The Stop guard is not armed by the lease's
record. It is armed by the **binding store**, and the binding store is written by
exactly one trigger: the observed **act of claiming**. A lease record sitting in a
spine file with `status: "active"` is invisible to `decide_stop`, which never scans
spines at all. C keeps the half that does nothing and drops the half that does the
arming.

---

## The deciding constraint

> **`decide_stop` iterates the binding store, not the filesystem. A binding entry is
> written only by a `claim` (or removed by a `release`) observed in `PostToolUse`. So
> the thing that arms the anti-abandonment Stop guard is the CLAIM ACT, not the lease
> RECORD — and C removes the act while preserving the record.**

Measured, not inferred.

`scripts/hooks/spine_rail.py:1679` `decide_stop` opens with
`sid_bindings = session_view(binding, sid)` and at `:1712` returns `{}` when that
mapping is empty. Nothing below that line can run without a binding entry. The
per-entry predicate `_entry_mid_flight_view` (`:1644`) is only ever reached through
that loop.

The only writers of a binding entry are in `handle_post_tool_use`
(`scripts/hooks/spine_rail.py:1341`):

- Bash path `:1379` — `if verb not in ("claim", "release"): return {}`
- Door path `_handle_door_lease` `:1246`, `:1271` — `if action not in ("claim", "release"): return {}`

One narrow third writer exists: the `#261` bind-on-resume inside `decide_session_start`
(`:1957–1990`). It fires only on a `SessionStart` event, only under the **bare** `sid`,
and only when `_scan_active_spine` (`:1775`) finds **exactly one** active-leased spine at
`.agent-work/*/spine.json` **depth 1**. It cannot cover a crew subagent (per-agent
binding key, no `SessionStart` event of its own) — which is precisely the population
`evidence/CHANNEL-EXPERIMENT.md` measured.

### Executed proof

Scratch harness, real `spine_rail` module loaded from `scripts/hooks/spine_rail.py`,
spine carrying a presence-stamped `engine_session` (`status: "active"`, no `claimed_by`):

```
1. stamped lease, NO binding entry  -> {}
2. stamped lease, WITH binding entry -> {'decision': 'block', 'reason': 'SPINE MID-FLIGHT: gate g1 is still open ...'}

3. PostToolUse Bash verb=claim    -> session bound? True
3. PostToolUse Bash verb=advance  -> session bound? False
3. PostToolUse Bash verb=start    -> session bound? False
3. PostToolUse Bash verb=release  -> session bound? False   (release REMOVES, never adds)

4. PostToolUse door action=claim    -> session bound? True
4. PostToolUse door action=advance  -> session bound? False
4. PostToolUse door action=status   -> session bound? False
```

Line 1 is C's world. Line 2 is today's world. The stamp changes nothing about the
guard.

### Why this dominates rather than merely costs

The benefit C was bought for — arm the anti-abandonment guard for a crew that never
claims — is delivered by changing **which verbs `handle_post_tool_use` treats as a
binding trigger** (`spine_rail.py:1379` and `:1271`). That is one predicate in one hook,
in the subsystem that actually owns the arming. It touches:

- zero refusal paths,
- zero episode fields,
- zero spines on disk,
- `scripts/checklist_engine.py` not at all.

C pays a 19-site semantic fan-out across 7 production modules (§Q4) to buy something
that one function already controls. Whatever else C is, it is not the cheapest way to
the thing it was proposed for.

---

## The four answers

### Q1 — can presence be stamped without a `claimed_by`? **Yes. Q1 is not the constraint.**

A stamp shape exists that arms `_entry_mid_flight_view` while leaving both `role` and
`refusals` structurally unavailable. Executed against the real
`episode_capture.mechanical_fields`, real `spine_rail._entry_mid_flight_view`, real
`checklist_engine`:

| shape | Stop guard arms | `role` | `refusals` | `require_session` refuses a foreigner |
|---|---|---|---|---|
| A — unclaimed (today's production child, `#357`) | **False** | absent | absent | False |
| B — full claim (today's driving spine) | True | present | present | True |
| **C1 — stamp, no `claimed_by`, no `refusals` arming** | **True** | **absent** | **absent** | True |
| C2 — stamp + `refusals` armed | True | absent | **present** | True |
| C3 — stamp + `claimed_by` | True | **present** | absent | True |
| C4 — stamp with no `session_id` at all | True | absent | absent | True |

`_entry_mid_flight_view` (`spine_rail.py:1644–1667`) requires **only three things**, and
`claimed_by` is not among them: a truthy `entry["spine"]`, a loadable spine, and
`spine["engine_session"]["status"] == "active"` — plus the active gate not being
`blocked`. It reads no `session_id` and no `claimed_by`. `_lease_role`
(`episode_capture.py:267`) reads `engine_session.claimed_by` and returns `None` without
it. So **C1 satisfies both sides at once** and
`tests/test_episode_negative_control.py::test_unclaimed_child_topology_refuses_only_role_and_refusals`
survives on the child topology. Baseline confirmed green: `15 passed in 1.79s`.

**But the same table exposes the real Q1 finding, which is on the PARENT topology, not
the child.** `status: "active"` is one undifferentiated bit. Every C-shape that arms the
Stop guard **also** arms `require_session` — the permission C exists to drop. Change the
status value to anything else and both die together:

```
C5 stamp status="present"  -> stop_guard_arms=False  require_session_refuses=False  R9=False
C6 stamp status="stamped"  -> stop_guard_arms=False  require_session_refuses=False  R9=False
```

There is no field in the record that distinguishes *"someone claimed this"* from
*"someone was here"*. C is therefore not a demotion of one field; it is the **addition
of a discriminator bit plus an edit at every consumer that must treat the two
differently** (§Q4).

**And the parent topology breaks in a way the child's does not.** If presence is
stamped before `claim` runs, `claim` lands on its idempotent-resume branch
(`checklist_engine.py:1182–1213`), which returns at `:1213` **before**
`cl.setdefault("refusals", 0)` at `:1249`. The other arming point, `main()`
(`checklist_engine.py:3742`), is gated on `cl.get("engine_session") is None` — also
defeated by a prior stamp. Executed:

```
TODAY: virgin -> claim                        role=True  refusals=True
UNDER C: stamped -> claim (same session)      role=True  refusals=False   <-- refusals lost
UNDER C: stamped -> claim (different session) REFUSED: "checklist already owned by
                                              active session 'stampsid'"
```

Two consequences worth naming:

1. `refusals` becomes **structurally unavailable on every episode in the corpus**, not
   just child ones — because both of its arming points are guarded on the absence of an
   `engine_session`, and C's whole point is that one is always present. That breaks
   `test_the_seam_emits_the_same_group_unasked`, which pins `("parent", [])` — zero
   refused fields on the parent.
2. A presence marker whose `session_id` differs from the claimer's **refuses the claim**.
   A marker that refuses is a claim. Through the door the two ids coincide
   (`SPINE_SESSION` on both), so this is a CLI-path hazard, not a door-path one — but it
   is the demotion failing on its own terms.

Both are consequences of C landing on today's `claim`, and a real C design would edit
`claim` too. They are costs, not disqualifiers. **Q1 does not decide C.**

### Q2 — the three refusal paths. **R9 gets STRONGER under C. Lane E's characterization is backwards.**

| path | reads | decides | under presence-stamped semantics |
|---|---|---|---|
| `spine_bind` R9 (`mcp_spine_server.py:1726–1740`) | `_active_lease(payload)`, `lease["session_id"]`, `_is_stale` | refuse a bind whose derived identity is live elsewhere | **strengthened — fires on a population where it is inert today** |
| `open_work` step 3 (`spine_lifecycle.py:431` via `_active_engine_session_spine:300`) | `rglob` under `.agent-work/<work_id>/`, any `engine_session.status == "active"` | refuse opening a `work_id` that already has a live session | **more refusals, some false — stale stamps accumulate under the work id** |
| `closeout_refusal` (`spine_lifecycle.py:201–219`) | driving spine's `engine_session.status` | refuse close unless `"released"` | **unchanged for the driving spine** |

**R9 in detail.** It refuses only when `_active_lease(payload) is not None` *and*
`lease["session_id"] == spine_lifecycle.session_id_for(work_id)`. On a leaseless spine
`_active_lease` returns `None`, so R9 never runs. Executed:

```
                 R9 INERT (no active lease)   <- today: leaseless spine (0 claims) — the CHANNEL-EXPERIMENT shape
                                 R9 REFUSES   <- today: claimed spine
                                 R9 REFUSES   <- C: presence-stamped
```

R10 (`_rebind_refusal`, `mcp_spine_server.py:1339`) is gated the same way. **So today,
two doors CAN bind one derived identity, with no refusal at all, on exactly the
leaseless population C is aimed at.** The stamp would carry the right `session_id`
automatically: `run_engine` (`mcp_spine_server.py:733–735`) appends
`--session-id SESSION` to **every mutating verb**, claimed or not, and `SESSION` is
`session_id_for(work_id)` — the identical string R9 compares against.

C does not weaken R9. **C closes an existing R9 hole.** State that plainly: this
reverses the "close to disqualifying" concern in the handoff. It is C's one genuine
architectural argument, and it survives scrutiny.

**`closeout_refusal`** is unchanged, for a reason worth recording: an *unclaimed* spine
already fails it today —

```
A: unclaimed -> closeout_refusal = 'close refused: the lease is still active'
```

`status` of a missing block is `None`, which is `!= "released"`. So every spine that has
ever closed through `close_work` already claimed and released. C adds no obligation
there.

### Q3 — release-obligation migration. **Bounded, and smaller than feared.**

Disk census over all 791 spine-shaped JSON files (`items` + `tasks` present) in the
repo, 775 of them under `.agent-work/`:

```
spine-shaped under .agent-work:                              775
  leaseless (engine_session absent or null):                 197
    templates (never driven, never stamped):                  68
    real files:                                              129
      declared children (auto-swept by finish_work):          52
      NOT declared children:                                  77
        of those, actually driven (a gate non-pending):       54
```

Three flows close a plan today:

1. **`finish_work`** (`spine_lifecycle.py:1005`) — the composed "I'm done". It already
   calls `_release_child_plans` (`:855`) **before** the top-level release, which
   force-releases every **declared** child (`task.child_checklist`) whose own lease reads
   `active`. Under C those 52 declared children are swept automatically. No migration.
2. **`close_work`** (`spine_lifecycle.py:504`) called directly — checks
   `closeout_refusal` on the **driving spine only**. Children are irrelevant to it,
   stamped or not. No migration.
3. **MCP `spine_close`** (`mcp_spine_server.py:1759`) — calls `close_work` directly,
   **no child sweep at all**. Same answer.

Crucially, a leftover stamp **does not block a close**: `_release_child_plans` returns
undeclared active children in `unclaimed_active`, and `finish_work:1159` merely reports
that list in its result — no caller branches on it (`grep unclaimed_active` returns only
its own definition, its docstrings, and that one report line).

So the blast radius is **not** "every plan must now release". It is two second-order
effects on the ~54 driven-but-undeclared files:

- `open_work` R3 (`_active_engine_session_spine`, `rglob` over `.agent-work/<work_id>/`)
  would refuse re-opening a `work_id` whose area still holds a stale stamp.
- `_scan_active_spine` (`spine_rail.py:1775`, glob `.agent-work/*/spine.json`, depth 1)
  would see more matches, and `#261`'s bind-on-resume declines on 2+. Today 4 of ~76 live
  spines read `active`.

Test-side migration is the larger number: **18 test files, 222 occurrences of
`engine_session`**, and 25 files touching `claim`/`release`/`--session-id`.

### Q4 — consumer census, redone. **19 decide : 10 record-or-display. Two-thirds decide.**

29 read/write sites across **7 production modules** in `scripts/` (33 sites / 8 modules
counting `evals/*/checks/spine_completed.py` ×3 and the `run_skill_eval.py:873` producer).
Lane E's "eleven consumers … eight modules" undercounts the sites by roughly 2.5×.

**DECIDE — branches, refuses, or selects on the value (19):**

| site | decision |
|---|---|
| `checklist_engine.py:1083` `_is_stale` | staleness predicate (shared) |
| `checklist_engine.py:1101` `_active_lease` | liveness predicate (shared) |
| `checklist_engine.py:1124` `require_session` | **refuses a mutating WORK verb — the only one** |
| `checklist_engine.py:1155` `claim` | refuses a non-`--force` takeover |
| `checklist_engine.py:1267` `heartbeat` | refuses a non-owner |
| `checklist_engine.py:1282` `release` | refuses a non-owner / no active lease |
| `checklist_engine.py:1471` `_checklist_owner` | selects the gauge owner key |
| `checklist_engine.py:1597` `_lease_claimed_at` | governor: whether a gauge reading counts |
| `agent_work_root.py:78` `_active_epic_lease` | selects the durable root (`status` **and** `claimed_by == "admiral"`) |
| `spine_lifecycle.py:201` `closeout_refusal` | refuses close |
| `spine_lifecycle.py:300` `_active_engine_session_spine` | refuses `open_work` |
| `spine_lifecycle.py:968` (in `_release_child_plans`) | selects which children to force-release |
| `spine_rail.py:311` `_reap_binding_entries` | deletes a binding entry |
| `spine_rail.py:1644` `_entry_mid_flight_view` | **the Stop block** |
| `spine_rail.py:1775` `_scan_active_spine` | selects resume candidates |
| `spine_rail.py:1993` (in `decide_session_start`) | whether to inject resume context |
| `gauge_writer_hook.py:336` | selects the gauge owner (reads the **binding entry's** `engine_session` string) |
| `mcp_spine_server.py:1339` `_rebind_refusal` | R10 lease-held |
| `mcp_spine_server.py:1726` `_spine_bind` R9 | identity-held |

**RECORD or DISPLAY only (10):**

`checklist_engine.py:1110` `_refresh_owner_heartbeat` (write) · `:1250` claim's block write ·
`:1300` `_lease_line` (display) · `:1805` `_declined_reading_advisory` (display) ·
`:1837` `_owner_mismatch_advisory` (display) · `:3742` `main` (arms `refusals`) ·
`episode_capture.py:267` `_lease_role` (the `role` field) ·
`spine_lifecycle.py:914` (`_release_child_plans` audit caller-id) ·
`spine_rail.py:644` `reconstruct_current` (display) ·
`spine_rail.py:1966` (`decide_session_start` binding write).

**The one number: 19 of 29 — roughly two in three — decide something.** The field is not
predominantly a record wearing a permission's clothes. It is predominantly a permission
input, and 18 of those 19 decisions are ones C's own framing does not propose to remove.

Lane E's "exactly one refuses a work verb" is **literally correct and rhetorically
misleading**: `require_session` is indeed the only site that refuses an ordinary
mutating verb (`MUTATING_VERBS` = advance, amend, append, attach, attest, block,
consolidate, flag-candidate, record, reopen, resume, skip, start, waive). The other 18
refuse lifecycle verbs or select records, and they are decisions all the same. Sorting
by which verb gets refused makes 18 decisions vanish from the count.

---

## What would have to be true to flip this verdict

Four conditions. All four, not any one.

1. **The binding store learns to arm without a claim.** `handle_post_tool_use` must write
   a binding entry on the first mutating verb, not only on `claim`/`release`. *If this
   is done, the Stop-guard benefit is already delivered — and C's principal argument is
   gone with it.* This is the condition that makes the verdict "dominated" rather than
   "impossible": satisfying it dissolves the need for C.
2. **A discriminator bit exists in the record**, so `status: "active"` stops being one
   undifferentiated flag. Roughly 8 of the 19 decision sites must then learn to ignore a
   mere presence (`require_session`, `claim`'s blocking branch, `release`'s ownership
   check, `heartbeat`, `closeout_refusal`, `_active_engine_session_spine`,
   `_rebind_refusal`, `_active_epic_lease`), while ~5 must keep firing on it
   (`_entry_mid_flight_view`, `_scan_active_spine`, `_reap_binding_entries`, R9, the
   gauge owner/governor pair).
3. **`refusals` gets a new arming point** that a prior stamp does not defeat — otherwise
   a mechanical field goes permanently unavailable corpus-wide and
   `test_the_seam_emits_the_same_group_unasked` goes red on the parent case.
4. **`claim` survives as the role-declaring verb**, so `claimed_by` (and therefore the
   `role` mechanical field) is still obtainable on driving spines. C must be additive,
   never a replacement.

Meeting (2)–(4) without (1) buys a lease-semantics rewrite that still leaves the
anti-abandonment guard inert. Meeting (1) alone buys the guard. That asymmetry is the
verdict.

**One thing C would still have on the table after all this, and it should not be lost:**
the R9 hole is real and independently filable. Today two doors can bind one derived
identity on any spine that never claimed, because both R9 and R10 are gated on
`_active_lease` being non-`None`. That is a nameable defect with a nameable mechanism,
and it does not need C to fix.

---

## Confidence

**High** on the deciding constraint, on Q1, on Q2, and on the Q4 ratio.

Basis: every claim above was executed against the shipped modules — `spine_rail`,
`checklist_engine`, `episode_capture`, `spine_lifecycle` loaded from `scripts/`, driven
on scratch copies, with the outputs pasted verbatim rather than reasoned about. The
binding-trigger finding is the strongest: it is a direct observation that
`decide_stop` returns `{}` for a stamped spine with no binding entry, and that only
`claim` produces one, on both the Bash and door paths. `tests/test_episode_negative_control.py`
was run at baseline (15 passed) so the citations sit against a green suite.

**Medium-high** on Q3. The 129/52/77/54 split is a census of what is on disk **now**,
which is a proxy for the historical population, not a record of it; archived work areas
have been pruned and archives were sampled as-is. The direction (bounded, sweeping
handles the declared majority, nothing blocks a close) is robust to that imprecision —
the exact counts are not.

**Known limits.** I did not simulate a full engine run under a modified `claim`, because
that would mean editing production code. I did not exhaustively audit the 222 test
occurrences of `engine_session` to say which would break — only counted them. The
`_scan_active_spine` / `#261` interaction under C is reasoned from the code path and not
executed end to end.
