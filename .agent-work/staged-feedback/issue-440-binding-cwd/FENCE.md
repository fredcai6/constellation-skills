# Fence citation — issue-440-binding-cwd

The feedback trio beside this file is **staged**, not written to the durable root, and this file is
the citation that makes that legitimate. All three members are present: `AGENT_FEEDBACK.md`,
`lessons-delta.json`, `CONSTELLATION_FEEDBACK.md`. Nothing was dropped.

## Governing authority

**`.agent-work/epic-418/launch-orders/A2-440.md` § Known collision**, verbatim:

> **Known collision, and it is the Admiral's to resolve, not yours:** `.agent-work/LESSONS.md` and
> `.agent-work/AGENT_FEEDBACK.md` are shared append-style logs that every commander writes. They were
> the *only* merge conflict in all of wave 0. **Prefer staging your feedback trio under
> `.agent-work/staged-feedback/<your-work-id>/`** so I can harvest it cleanly.

Reinforced by this run's dispatch, which supersedes the launch order's "no shared-file fence this
wave: you are the only Commander running" line: **a second Commander (#447) is running concurrently
and owns the lessons/feedback/episode surface**, with no commander-to-commander coordination
permitted. Writing those shared logs directly would collide with an agent actively holding them.

## What the Admiral needs to do

1. Append the `AGENT_FEEDBACK.md` entry (heading `## issue-440-binding-cwd — 2026-08-07 …`) to the
   durable `.agent-work/AGENT_FEEDBACK.md`.
2. Append the `CONSTELLATION_FEEDBACK.md` entry to the durable
   `.agent-work/CONSTELLATION_FEEDBACK.md`. It carries the originating lesson id
   `lesson:falsify-a-check-against-a-decoy-before-trusting-it` so the upstream sweep groups it as a
   **recurrence on stable identity** — amend the existing entry, do not mint a new slug.
3. Apply the delta against the shared playbook:
   `python scripts/apply_lessons_delta.py <this dir>/lessons-delta.json --file .agent-work/LESSONS.md`

## Verification, so you are not applying an unvalidated delta

The delta was **validated but deliberately not applied** to this worktree's `LESSONS.md`, precisely
to avoid the merge conflict the launch order names. It is valid — `--dry-run` against
`.agent-work/LESSONS.md` at HEAD `b2810d9` reports:

```
recurrence-debt lesson:falsify-a-check-against-a-decoy-before-trusting-it (now 2 unfixed recurrence(s))
added lesson:a-dispatched-agent-can-decline-a-protocol-because-of-its-defensive-framing
exported lesson:falsify-a-check-against-a-decoy-before-trusting-it to CONSTELLATION_FEEDBACK (pinned until upstream ships)
tick -> run 44
playbook: 7 active (run 44)
```

`--ripe` reported **no** ripe-unpaid lessons at the feedback step, so none was left unsettled.

**One thing to read rather than mechanically apply:** the export is the **third** recurrence of
`falsify-a-check-against-a-decoy-before-trusting-it`, and it carries a sharper upstream shape than
the previous two. This instance was *not* authored from the spine template — the discriminator the
lesson's own bank-reason named, already settled at issue-419 — but a hand-written acceptance verifier
that shipped its own five-mutation selftest and still omitted its central assertion. A decoy suite
tests the checks you thought of; it cannot surface the fact you never asserted. That is debt worth
paying upstream rather than confirming a fourth time.
