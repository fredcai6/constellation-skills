# Investigation Handoff — is option C viable?

**Authority note.** The Wave 2 latitude contract has expired. This lane runs on
direct human instruction of 2026-08-21 and is investigation only — no design, no
implementation, no GitHub, no merge.

## The question

Option C is Lane E's D7: **demote the lease from a claim to a presence marker —
presence STAMPED rather than CLAIMED.** It is the only architecture-shaped move
left on the table. Everything else on the shortlist is display, message, or flag
work.

Decide whether C is **viable**, **viable with modification**, or **not viable**,
and name the exact constraint that decides it. Do not design C. Do not implement
anything.

## Why C is on the table at all

A crew on the shipped dispatch path drove a seven-gate plan with **0 claims and
0 releases** (`evidence/CHANNEL-EXPERIMENT.md`). The cold critic could not find
one mistake the lease's *refusal* has ever prevented. Lane E then found the
counterweight: `_entry_mid_flight_view` returns `None` for a released or
inactive lease, so that leaseless crew ran with the anti-abandonment Stop guard
**inert**. The lease's refusal prevents nothing; its **record** arms the one
guard that fires. C keeps the record and drops the permission.

## Q1 — the constraint that likely decides it

`tests/test_episode_negative_control.py::test_unclaimed_child_topology_refuses_only_role_and_refusals`
asserts that on an **unclaimed** child, `role` and `refusals` are structurally
unavailable, and pins that *exactly those two* of ten fields are absent.
`_lease_role` reads `engine_session.claimed_by`; `refusals` is armed only by
`claim`.

**So: can presence be stamped WITHOUT a `claimed_by`?**

- If a stamp carries `claimed_by`, `role` becomes available on a
  previously-unclaimed child and that negative control breaks. Establish whether
  it breaks — run it against a simulated stamped shape if you can do so without
  touching production code.
- If a stamp does not carry `claimed_by`, establish whether the Stop guard still
  arms. Read `_entry_mid_flight_view` and `decide_stop` and state exactly what
  they require — `status == "active"`? a `session_id`? a `claimed_by`? — and
  which of those a stamp would have to supply.

A stamp shape that arms the Stop guard *and* leaves `role`/`refusals`
unavailable is what makes C viable. Say whether one exists.

## Q2 — the three refusal paths

Lane E flagged that C changes behavior on `spine_bind` R9, `open_work`, and
`closeout_refusal`. For each: what does it read from `engine_session`, what
decision does it make, and what happens under presence-stamped semantics?

R9 matters most — Lane E called it *the one refusal in the corpus that prevents a
mistake it can name* (two doors under one derived identity). If C weakens R9,
that is close to disqualifying and you should say so plainly.

## Q3 — the release-obligation population

C would newly require an explicit `release` before close on a population that
never had that obligation. Quantify it: how many plans on disk closed without
releasing, what flows close a plan today, and which would need changing. A
migration whose blast radius is the whole corpus is a different proposition from
one touching two call sites.

## Q4 — complete the consumer census

Lane E reported "eleven consumers of `engine_session`, exactly one refuses a work
verb." References span eight modules. Redo it properly and report: how many sites
**read** `engine_session`, how many make a **decision** on it, and how many merely
record or display. The ratio is the argument for or against C in one number.

## Ground rules

- Verify from source and tests. Do not trust any prior lane's characterization,
  including the Admiral's — this epic has already produced four Admiral errors
  that lanes caught.
- Where you must simulate, work on copies in a scratch directory. Do not modify
  production code, tests, `map/`, or any plan another run owns.
- Report honest negatives. "C is not viable and here is the single reason" is the
  most valuable result available.
- Do not call any `mcp__spine__*` tool — the door is bound to the Admiral's spine.
- No commits, no push, no GitHub.

## Deliver

`architecture/C-VIABILITY.md`: a verdict, the deciding constraint, per-question
findings with exact file:line citations and command output, what would have to
be true for a "not viable" to flip, and your confidence with its basis.
