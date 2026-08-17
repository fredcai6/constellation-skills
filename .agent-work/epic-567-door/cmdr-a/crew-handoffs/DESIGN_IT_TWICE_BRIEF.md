# Design-it-twice Brief: `binding the MCP door to an existing spine`

Filled from `references/design-it-twice-brief.md`. Commander `cmdr-567-a`,
lane A of epic #567. Base `600de020`.

## The one thing being designed twice

**Where and how a running MCP door acquires a binding to a spine file that
ALREADY EXISTS.**

Not "how do we get per-dispatch identity" in general, and not the atomicity work
that rides in the same lane. One load-bearing interface decision: the shape by
which a process that did not launch its own door comes to drive its own spine
through that door.

## Count and panel — a surfaced choice

**N = 3 (panel).** Rationale, surfaced to the human and overturnable: this is a
load-bearing interface on the security boundary of the whole fleet's engine
access, it changes a recorded isolation property, and `decision:design-it-twice`
in the launch order names it "a load-bearing interface" explicitly. Doctrine says
"when in doubt, panel"; there is no doubt here.

## Ground truth every candidate must design against

Measured at `600de020` in `scripts/mcp_spine_server.py`. Do not re-litigate these;
they are the givens.

- `SPINE: Path | None` (`:201`) and `SESSION: str` (`:202`) are the two module
  globals that constitute this door's identity.
- `_bind_process_to(spine_file, session)` (`:878`) is the **one** function allowed
  to assign them outside module scope. It sets both globals and mirrors both into
  `os.environ`. It takes two plain strings and does not care where they came from.
- Its **only** caller today is `_spine_open` (`:1041`), which mints new work
  (`spine_lifecycle.open_work`) — a worktree, a branch, a work area, a compiled
  spine. Its tool description says it "acts on a spine that does not exist yet."
- `_unbound_refusal()` (`:393`) is asked **per call, never cached**, explicitly
  because a rebind can happen mid-life.
- `_identity_violation(argv)` (`:443`) asks `checklist_engine.parse_args` for the
  real resolved `--file`/`--session-id`/`--from-child`/`--delta` and refuses
  anything not equal to (or, for path arguments, not contained in) the binding.
  It compares against `SPINE` at CALL time, so it follows a rebind automatically.
- `_resolve_confined(value, join_relative_to, bound_dir)` (`~:330-380`) is the
  containment predicate. `bound_dir` defaults to `SPINE.parent` but is already a
  parameter, and `spine_open` already passes a different root (`wt_root`).
- `_rebind_refusal()` (`:920`) refuses a rebind while this process still holds an
  **active lease** on its current spine.

### Hard constraints — a candidate violating one is dead

1. `decision:one-spine-per-process-stands`. One process drives exactly one spine
   at a time. You may change WHEN the binding is decided; you may not raise the
   count.
2. A module-wide **AST pin** in `tests/test_mcp_lifecycle.py` asserts the set of
   assignments to `SPINE`/`SESSION` is exactly {module scope, `_bind_process_to`}.
   Any candidate that assigns those names anywhere else fails CI by construction.
3. `tests/test_mcp_lifecycle.py:137` pins every `return` in
   `call_lifecycle_tool` to literally `_spine_open(args)` / `_spine_close(args)`.
   A mutate-then-return inside `call_lifecycle_tool` is the banned shape.
4. `tests/test_mcp_lifecycle.py:194` bans the identifiers `SPINE`, `SESSION`,
   `run_engine` from `_spine_open`'s **own source**.
5. `decision:isolation-not-fencing`. The current property is "one file per
   process." Your candidate MUST state, explicitly, what property replaces it and
   what an agent can now reach that it could not before. A design that silently
   widens reach is a regression even if every test passes.
6. `decision:net-deletion`. The epic reduces paths. Say what your candidate lets
   us delete. "Nothing" is an allowed answer if argued.
7. No new user-visible default. No new environment variable if avoidable — say so
   if yours needs one.

### The trade this sits on

`.agent-work/archive/2026-08-09-epic-418-followon/...IDENTITY_TRADE.md` records:
env-binding buys isolation, per-call paths buy per-call identity, and **the
composition is what fails**. Your candidate should say which side of that trade it
takes and why the composition problem does not bite it.

## The constraints (one per agent, each distinct and named)

Each agent designs the SAME thing under exactly ONE constraint.

- **Candidate A — `minimal-interface`.** The smallest possible addition to the
  door's surface. Assume the answer is one new tool whose entire job is to bind
  the door to an existing spine file, and design that tool properly: name,
  arguments, refusal set, containment root, interaction with `_rebind_refusal` and
  the lease, and what happens when it is called twice.
- **Candidate B — `no-new-tool` (common-caller-first).** Add **zero** tools.
  Design the fix so the existing surface handles it — e.g. `spine_open` becomes
  adopt-or-mint (idempotent for a spine that already exists), or the unbound door
  resolves its own spine lazily at first call from something it can already see.
  Optimize for the caller who just wants `spine_status` to work.
- **Candidate C — `per-call-identity` (the issue's own recommendation).** Take
  #559's filed proposal seriously: generalize `_identity_violation`'s containment
  so a call may NAME its own spine file, enforced to lie within a bound **root**
  rather than equal a bound **file**. Isolation becomes "one tree" instead of "one
  file." Design what the bound root is, where it comes from, and why per-call
  identity does not reintroduce the composition failure `IDENTITY_TRADE.md`
  recorded.

## Compared on

Score your own candidate honestly on all four, and name where it LOSES:

- **Depth** — does it hide the right complexity behind the seam, or leak it upward?
- **Locality** — is the change contained, or does it fan out across callers?
- **Seam placement** — is the boundary where the caller and the tests want it?
- **Testability** — can each pathway be exercised and falsified on its own?

## Output contract

Write your candidate to the path given in your dispatch prompt, as Markdown:

1. **Candidate name and your one named constraint.**
2. **The design** — concretely enough to implement: exact function/tool names,
   arguments, the refusal messages, and the diff shape (which functions change,
   which are added, which are deleted). Reference real line numbers.
3. **The isolation property** — one paragraph: what replaces "one file per
   process", and what an agent can reach now that it could not before.
4. **Four-axis self-score**, including where it loses.
5. **What it lets us delete.**
6. **The strongest argument AGAINST your own candidate.** Required. A candidate
   with no stated weakness is not finished.
7. **What would have to be true for you to be wrong.**

## Untaken-road record

- **`max-flexibility`** — a candidate optimizing for arbitrary multi-spine access
  from one door. Not generated: it violates hard constraint 1
  (`one-spine-per-process-stands`), a `settled` decision that is not mine to
  unsettle. Named here so the skip is loud rather than silent.
- **`ports-and-adapters`** — an abstract "spine locator" port with pluggable
  adapters. Not generated: one adapter is a hypothetical seam
  (`global-everyone.md` §deep-module-vocabulary — "one adapter = a hypothetical
  seam; two = a real one"), and this door has exactly one way to find a spine, so
  the port would be speculative abstraction against "one canonical path; no
  speculative abstraction."

## Panel-vs-single record

Panel of 3, because the decision touches architecture and a recorded security
property. Surfaced to the human at the plan checkpoint; the human may overturn the
count.
