# FENCE — why this trio is staged, not written to the durable root

The Admiral's frozen `LAUNCH_ORDER-262.md` fences this run out of the main checkout:

> **Main checkout is read-only to you.** `C:/Programs/constellation-skills` — read it for evidence
> ... Never write it.

and directs the closeout trio to be staged **uncommitted** here instead:

> **For the harvest (staged in your worktree, left UNCOMMITTED):** your closeout trio at
> `.agent-work/staged-feedback/governor-262/`. **Do not `git add` it. Do not commit it.**
> I harvest it directly from your worktree before the sweep.

The durable log (`.agent-work/AGENT_FEEDBACK.md`) and the playbook (`.agent-work/LESSONS.md`) both
live in the main checkout, so the ordinary durable-root write is impossible under this fence. Per
the delegated-commander skill's fenced-closeout rule, the complete trio is staged here in lieu of
it — a `FENCE.md` citation without the full trio would fail the gate, and correctly so, because
learning must not be silently dropped.

**Contents of this directory:**

| File | What it is |
|---|---|
| `AGENT_FEEDBACK.md` | the dated run entry to append to the durable log |
| `lessons-delta.json` | structured delta ops to apply via `apply_lessons_delta.py` |
| `CONSTELLATION_FEEDBACK.md` | upstream exports (see the note in that file) |

**Note on lesson ids (#277):** ids are written **bare** — `verify-launch-order-claims-against-code`,
not `lesson:verify-launch-order-claims-against-code`. The playbook renders the `lesson:` prefix, but
the delta validator rejects the colon and the delta is all-or-nothing.

Nothing in this directory is committed. The PR carries code, tests and docs only.
