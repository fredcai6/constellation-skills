# Reviewer handoff — g1: the bookend guard in `amend()`

**Result path (write here before ending your turn — that write is the delivery):**
`.agent-work/567-k/crew-handoffs/g1-review-result.md`

**Suggested Model Tier:** sonnet. A bounded diff (~170 lines across three files) against an
explicit criteria list.

Repo: `/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle`
Branch: `feat/567-k-one-spine-mutable-middle`, base `9b38b9d9`.

You are the **independent reviewer**. You did not write this and you owe its author nothing.
Your job is to verify, not to agree. **Reproduce the evidence rather than reading it.**

## Task statement under review

Give `amend()` a declared-bookend guard so a role cannot amend away its own **closing** bookend,
while the middle of its plan stays freely mutable — issue #634, "frozen bookends, mutable middle".

## How to inspect the diff

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle
git diff scripts/checklist_engine.py scripts/mcp_spine_server.py tests/test_checklist_engine.py
```

Changed: `scripts/checklist_engine.py` (the `amend()` guards), `scripts/mcp_spine_server.py`
(tool-description prose only), `tests/test_checklist_engine.py` (new `AmendBookendGuard` tests).

The implementer's own account is at `.agent-work/567-k/crew-handoffs/g1-implement-result.md`.
**Read it last, and treat every claim in it as a pointer to something you must reproduce**, not as
a fact.

## Close criteria — check each, name each in your result

1. **The four guards refuse.** `drop`, `rescope` and `retext-check` of a gate carrying
   `"bookend": true` are refused; an `add` that would land **after** the last bookend is refused.
2. **`drop` refuses regardless of status** — including a `pending` bookend. This is the actual
   hole: at `9b38b9d9` `drop` gated on `status == "pending"` and nothing else, so a pending
   closing gate was wide open.
3. **The middle still grows.** An `add` into the middle of a declared plan still succeeds. A guard
   that froze the whole plan would pass criteria 1–2 and still be wrong.
4. **Backward compatibility.** A plan with **no** `bookend` key anywhere behaves **exactly** as at
   `9b38b9d9`. Verify against the real base, e.g. `git stash` or a worktree at `9b38b9d9`, rather
   than by reasoning about it.
5. **All-or-nothing survives.** A delta mixing a legal op with a bookend-violating op leaves the
   checklist **completely** unmutated — check `items` *and* that the legal op did not land.
   `main()` persists `cl` even on the error path, so this is a real risk.
6. **The one-way latch.** `rescope {bookend: true}` on an unmarked pending gate succeeds; a
   following `rescope {bookend: false}` on that gate is refused.
7. **One swappable seam.** The declaration is read in **exactly one** helper, and no guard site
   re-reads `task.get("bookend")` directly. This was a hard requirement — the human may still swap
   the declaration form, and the swap must stay one function. Verify by grep, not by trust.
8. **`from_child` and `consolidate()` untouched.** `advance(--from_child)` (`:2617`) and
   `consolidate()` (`:2733`) are out of scope and must be unchanged. Confirm from the diff.
9. **No fenced path was written.** The diff must not touch: `scripts/run_crew.py`,
   `scripts/install_constellation.py`, either `LAUNCH_ORDER.template.md`, `map/INDEX.md`,
   `scripts/generate_spine.py`, `specs/`, or any `*SPINE*.template.json` (those are gate g2).
10. **The tests can fail.** Pick at least two new tests, break the guard they cover (revert that
    guard locally), and confirm they go red. A test that passes in both the healthy and the
    defective world proves nothing. **Restore the code afterwards** and confirm the tree is clean.

## Required verification commands

```sh
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_checklist_engine.py
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_mcp_spine_server.py tests/test_mcp_identity.py
git status --porcelain     # must be clean of unintended edits when you finish
```

## Constraints

- **Never run a mutating engine verb against a live spine.** `.agent-work/567-k/spine.json`,
  `.agent-work/567-k/execute.json` and `.agent-work/epic-567-door/spine.json` are LIVE and
  read-only to you. Copy to a temp dir and drive the copy.
- The engine under edit is not the engine in play (#269): validate in a **fresh process with
  explicit paths**, never by observing your own session's behaviour.
- Leave the tree as you found it. If you break something to prove a test fails, restore it and say
  so.
- Out-of-scope improvements are **findings**, not edits. Do not fix them.

## Known context, so you do not re-derive it

- A contested decision, deliberately taken: the guard **does** cover `retext-check`. Design
  candidate A argued against it (a bookend whose typo'd check can never be corrected is worse).
  It was overridden because `retext-check` can rewrite a frozen gate's command check to something
  trivially true and pass it — a freeze that only stops deletion is not a freeze. **You may
  disagree**; if you do, say so as a finding rather than treating it as a defect.
- Reviewer/survey checklists are deliberately out of scope: `amend` on a survey already accepts a
  `retext-check`-only delta (`:3013-3029`).

## Return format

`REVIEW_RESULT` with a **`Verdict`** field of exactly `APPROVE` or `BLOCK`. Include: each of the
ten criteria with what you actually ran and observed; the red-proof from criterion 10 with the
failure output; the test tallies; any finding with severity; and a **Workflow Feedback** section
including your own mistakes.

`BLOCK` if any close criterion fails. An approving review that did not reproduce the evidence is
worth less than nothing here — this change alters the rule the repo's own live runs execute under.
