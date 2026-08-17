# g3 rework — the delta, enumerated

Measured, not reasoned: every row is a scenario in
`crew-handoffs/g3-implement/m4_differential.py`, run across three pinned arms —
**BEFORE** the gate (`999b7663`), the **BLOCKED** intermediate (`e3e50a69`), and
**AFTER** this rework (working tree). Output in
`m4-differential-before-after.txt`.

The rework's own delta is `BLOCKED → AFTER`. `BEFORE → AFTER` is the gate's
total delta, which the Commander needs for #609's record.

## What newly BLOCKS: nothing new in this rework

`BLOCKED → AFTER` is **identical on every Stop row** — S1, S2, S3, S4, all six
S6 garbage rows, S7 and S8. The rework touched selection at `decide_session_start`
and shared the comparison; it changed nothing about whether a Stop blocks.

The gate's three newly-blocking classes are unchanged from the blocked
implementer's report, and they are `BEFORE → AFTER` rows, not mine:

| # | situation | BEFORE | AFTER | intended? |
|---|---|---|---|---|
| 1 | this agent claimed a spine while standing in another worktree, then stops (S3) | allowed | **blocks**, own gate rendered | Yes — its own mid-flight run; where it stands was never evidence about that |
| 2 | a crew in its **own** tree holds the only open gate; the parent stops (S4) | allowed | **blocks**, foreign-owner wording, imperative withheld | Yes — #419's ruling, which the tree test defeated for exactly those crews that had their own tree |
| 3 | recorded worktree and cwd differ only by case/separator (S8) | allowed on POSIX, blocked on Windows | **blocks** on both | Yes — removes a platform-dependent decision rather than adding one |

Nothing newly stops blocking, in either delta. The surviving allowed-Stop shapes
are unchanged: no binding, unreadable spine, released lease, honest engine block,
and the 3-strike hatch.

## What newly RESUMES DIFFERENTLY — this is the rework

Four rows move at `decide_session_start`, all in the `BLOCKED → AFTER` delta.

| # | situation | BEFORE | BLOCKED | AFTER | intended? |
|---|---|---|---|---|---|
| 1 | a crew claimed first, in another tree; the **parent's** session restarts (S9, reviewer's case 2) | no context | **crew's gate** | **parent's own gate** | Yes — the regression the reviewer BLOCKED. A parent being told "pick the run back up at this gate" about its crew's gate is the #549/#419 failure itself |
| 2 | the same binding, the parent's key written first (S10, case 6) | no context | parent's gate | parent's gate | Yes — and the pair S9/S10 is the point: the answer no longer depends on write order |
| 3 | only a **crew's** per-agent key exists; the parent never claimed (S11, case 3) | no context | **crew's gate** | **no context** | Yes — a session that claimed nothing is handed nothing. It falls through to the blind scan exactly as before |
| 4 | two crew agents; the payload **names** agent B (S12, case 5) | no context | agent A's gate | **agent B's gate** | Yes — the site reads `binding_key(payload)`, so it follows the payload's own identity instead of dict order. No evidence says SessionStart ever carries an `agent_id`; the point is that it is no longer ignored if it does |

Reviewer's **case 1** (an in-tree crew claimed first, parent restarts) was named
in the handoff as pre-existing and not mine to close. It **falls out of the fix**:
the parent's own bare-key entry is now selected whether or not the crew shares
its tree, so the in-tree variant is repaired by the same comparison. Nothing was
widened to reach it.

### One behaviour deliberately NOT changed

A session that owns **none** of the visible entries still falls through to
`_scan_active_spine`, which reads no binding key at all and can bind a session to
a spine it never claimed. That is the lane's `tc1`, it needs an authority
decision, and binding-key provenance cannot reach it — there is no binding key at
scan time. The tests are constructed so this path cannot manufacture a pass:
every SessionStart case asserts `_scan_active_spine(proj) == []` before acting.

## The collateral that needs the Commander's eye

Two pre-existing tests asserted the behaviour the B2 fix ends, and they could not
both stand:

- `test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key`
- `test_session_start_composite_key_entry_still_renders_full_imperative_unchanged`

Both build the reviewer's **case 3 in same-tree form**: a subagent claims a spine
under `sid#agent_id`, then a bare SessionStart (no `agent_id`) expects to resume
from it. They passed BEFORE only because the payload's `cwd` matched the recorded
worktree — the old answer was tree-dependent, exactly like case 2's.

Rewritten to the new rule, and **not weakened**: each still asserts #419's
read-through directly (the entry IS in `session_view`, and
`session_view_provenance` attributes it to the composite key), and the first adds
a round trip showing the entry is still reachable by the agent that owns it. What
changed is who gets answered with it.

**The alternative I rejected:** fall back to the leading entry when the session
owns none. That keeps both tests green untouched — and leaves the reviewer's case
3 unfixed, contradicting this handoff's own Close Criteria. The two are mutually
exclusive: any rule that resumes a bare session from another agent's entry
recreates case 3.
