# Reviewer handoff — gate `g1-review` (issue #542/#541, workstream F2)

## What was built

A **decision** and a **pin**, both by the Commander (this is a reasoning gate; the
implement dispatch was waived — see "Why you exist" below).

1. `.agent-work/epic-418-followon/commander-f2/IDENTITY_TRADE.md` — the recorded position
   on identity when the harness shares the container.
2. `tests/test_mcp_identity.py::IdentityBindingPinTests` — five tests pinning the binding
   that document selects.

Commit `36a1bdcd`. Nothing in `scripts/` changed: `git diff HEAD~1 -- scripts/` is empty
and must stay so.

## Why you exist — read this, it changes what you are for

The implement half of this gate was **waived**: the deliverable was a decision over
evidence the Commander already held, and doctrine says a crew on a pure design note is
*shallower, not safer*. What that waiver cost is an independent cold read of the identity
code **before** the decision was made. **You are the recovery of that loss.** You are not
here to rubber-stamp a document; you are here to be the only independent mind that reads
this before four more gates are built on top of it.

## How to inspect

```
cd /home/tommy/projects/constellation-skills-wt/f2-mcp-adoption
git show 36a1bdcd --stat
git diff HEAD~1 -- tests/test_mcp_identity.py
```

Read `.agent-work/epic-418-followon/commander-f2/IDENTITY_TRADE.md` in full, and
`scripts/mcp_spine_server.py:104-135` (the binding it is about).

## Task statement

Verify that the recorded identity position is **sound and honestly evidenced**, and that
the pin protecting it **can actually fail**.

## Close criteria — verify each, and say which you checked how

**A. The trade document carries all six frozen items.** This is a checklist, not a prose
judgement. Verify item by item and report per item:

1. The option taken, stated plainly.
2. The property given up, **named** — not gestured at.
3. For **each** rejected option: what it would have covered, and what it would not.
4. The general shape, stated fleet-wide rather than MCP-locally.
5. Whether the answer applies to the `spine_rail.py` hook seam, or explicitly does not,
   **and why**.
6. What a seam with **no per-call argument** does under this answer.

**B. The pin can lose.** This is the load-bearing half. **Mutate the real door** —
`scripts/mcp_spine_server.py`, not a copy — and report whether
`IdentityBindingPinTests` went **RED**, then restore and confirm **GREEN**. Run at least
these two, and invent a third of your own:

- give a tool's `inputSchema` a `spine_file` property;
- make `SPINE` late-bound (re-read from the environment on access) instead of bound at
  import.

The Commander already ran both and reports they went red on two *different* tests. **Do
not take that on trust — reproduce it.** Report the exact test ids that failed for each
mutation. If a mutation does **not** go red, that is a BLOCK and the most valuable thing
you could find.

**C. The pin is outcome-neutral, as claimed.** The document says the pin encodes "the
binding is what the record says," not "option C is correct." Check that claim against the
test code. A pin that could only ever be satisfied by one of the three options would mean
the trade was decided in the test rather than in the document — say so if you find it.

**D. The honest-scope claim holds.** The document says the *harness* seam (whether the
Task tool reuses a connected client inside one process) is **cited**, not re-measured
here. Verify no test in this gate claims to measure it. Over-claiming here would be worse
than a missing test.

**E. `git diff HEAD~1 -- scripts/` is empty.** The door was mutated and restored during
authoring; confirm nothing survived.

## Allowed scope

`tests/test_mcp_identity.py`, `IDENTITY_TRADE.md`, and read-only inspection of
`scripts/mcp_spine_server.py`. You may mutate `scripts/mcp_spine_server.py` **temporarily**
for criterion B — restore it and prove the restore with `git diff`.

## Specific exclusions

- **Do NOT edit `scripts/hooks/spine_rail.py`.** Its defect is real and is issue #549,
  outside this run's file fence. The trade document cites it deliberately.
- **Do NOT edit `scripts/checklist_engine.py`.**
- Do not re-open the identity decision itself. If you believe it is *wrong*, say so as a
  BLOCK with your reasoning — but the decision is the Commander's under inherited
  latitude, and your job is to test whether it is sound and evidenced, not to substitute
  your own.

## Constraints

- Run the suite as **`python -m pytest`**, NEVER `python3 -m pytest`. On this host
  `/usr/bin/python3` answers and has no pytest, so `python3` returns `No module named
  pytest` and a non-zero exit that **reads as a red suite and is not one**.
- **NEVER pipe a command into `head`/`tail` and read the exit code** — that is the pager's
  status, not the command's. Redirect to a file and capture the command's own `$?`.
- Never edit `scripts/checklist_engine.py`.
- Canonical shared doctrine lives at `skills/_shared/global-*.md`, never
  `skills/<role>/references/global-*.md` (the installer regenerates those).
- Edit compact-format JSON as raw text, surgically; never round-trip through
  `json.load`/`json.dump`.
- Windows writes need `encoding='utf-8', newline='\n'` explicitly on every write.
- Work **only** in this worktree. `/home/tommy/projects/constellation-skills` is **fenced
  read-only**.

## Anchors

**Structural:** `scripts/mcp_spine_server.py:113-115` (map: `scripts.mcp_spine_server`, 8
entities / 5 holes) — `ENGINE`/`SPINE`/`SESSION` as module-level `os.environ` reads at
import, no tool taking a spine path. `tests/test_mcp_identity.py` — the DC2/DC3 classes the
pin joins. `.mcp.json` — `${VAR}` expansion, the per-**process** identity mechanism.
`scripts/hooks/spine_rail.py` `session_view()` — READ ONLY, the second seam (#549).

**Constraint:** one process = one server = one spine = one identity, for the life of the
process. A Task-tool subagent inherits its dispatching process's MCP scope wholesale
(measured YES, cited not re-measured). **The hook seam has no per-call argument** — a Stop
hook receives what the harness hands it.

**Decision:** `identity-trade-is-recorded` (settled/human) — the property given up is
written down; silence is a gate failure. `no-gen-mcp-config` (settled) — scoped to
per-dispatch generation on identity grounds.

**Confidence flag:** the harness-internal reuse seam has **no observation point reachable
from a subprocess-level test** (`DC3InheritanceMechanismTests` docstring). This gate must
cite the epic's existing measurement of it, never claim to have re-measured it.

## Evidence produced (verify it reproduces)

```
python -m pytest -q tests/test_mcp_identity.py::IdentityBindingPinTests
5 passed
```

## Required evidence from you

- A per-item verdict on the six frozen items in criterion A.
- For **each** mutation in criterion B: what you changed, the exact failing test ids, and
  the restore proof.
- Your own third mutation and its outcome.
- The full suite green after restore: `python -m pytest -q`, `0 failed`.

## Authority

Admiral, epic-418-followon, wave 2. The Commander is delegated; the human is AFK.

## Verdict

Write `APPROVE` or `BLOCK` with reasoning to
`.agent-work/epic-418-followon/commander-f2/crew-handoffs/g1-review-reviewer-result.md`
**before ending your turn — that write is the delivery.** Include a `Workflow Feedback`
section; it feeds the run's retrospective and is not dropped.

---

## ADDENDUM — standing requirement for every reviewer on this run

**Return `git status --porcelain` for your worktree in your result.** A read-only role that
ends with a dirty tree should have to say so. This is an Admiral instruction added after a
reviewer on this gate disclosed an accidental out-of-scope write; it exists to catch the
whole family, not that one instance.

**To the reviewer who disclosed it:** that was the right call and it cost you nothing. A
role that reports its own out-of-scope write is worth more than one that never makes one,
because the second kind mostly exists by luck. It has been written up as a repo problem
(#551), not as your slip — the engine's evidence verbs invite prose, prose about commands
invites backticks, every documented example uses double quotes, and double quotes do not
protect backticks in any shell we run. The journal even records the text *after*
substitution, so the record does not show what was typed. A `--finding-file` is proposed,
the same move `gh pr create -F` already forced on this repo for the same reason.

**Avoid backticks and command-looking text inside engine string arguments.**
