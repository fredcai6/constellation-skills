# What newly withholds, and what it costs

Measured, not recalled: `m2_withhold_matrix.py`, three pinned arms
(`999b7663` / `6bba3fd2` / working tree), ten cells, each a **SessionStart then
a Stop sharing one binding store**. Output at `m2-withhold-matrix.txt`.

**Four of ten cells moved.** Six did not, which is evidence too: rework 1's
approved answers are unchanged.

## The change, stated exactly

`decide_session_start` returns `{}` when **all three** hold:

1. the merged view (`session_view`) is **non-empty**,
2. `_own_entries(...)` is **empty** — nothing in that view is attributable to
   the acting agent's `binding_key`, and
3. no own entry produced a readable spine.

Everything else reaches the fallback scan exactly as before.

## The classes that newly withhold

| # | class | before (`6bba3fd2`) | after |
|---|---|---|---|
| 1 | sees only another agent's entries; **one** active-leased in-tree spine | **binds `binding[sid]` to it**, renders that gate, and the next Stop answers with it as the session's own | no binding, no context; the Stop answers foreign-owner with the imperative withheld |
| 2 | same ownership shape; **2+** in-tree spines | no binding (ambiguous), but renders the scanned gate's context | no context either |
| 3 | same ownership shape; **no** in-tree spine | nothing | nothing — unchanged |
| 4 | `binding_key` refuses the payload (#441 malformed `agent_id`) with a non-empty view | **binds `binding[sid]`** to the scanned spine | no binding, no context |
| 5 | `tc5` collision loser: the session claimed a path its subagent also claimed, and last-key-wins attributed it to the subagent | renders the scanned gate's context | no context |

Class 1 is B4. Class 4 is the same defect reached by a different route and is
strictly worse in kind — it wrote an ownership record for an agent the hook had
just declined to identify. Class 2 and class 5 lose only rendered context.

## Does any session that legitimately needs a binding now fail to get one?

**No, with one narrow exception, named below.**

The argument is that the withheld class cannot contain a session's own work.
The view is keyed by harness session id and merges the bare `sid` plus every
`sid#<agent_id>` key. If this agent had ever claimed a spine, that claim wrote
under the key `binding_key` composes for it — the same key the comparison asks
about — so the entry would be in the view **and** owned, and condition 2 would
not hold. A session in the withheld class therefore has claims under its
session id, none of them its own. Any spine the scan could hand it is by
construction one it never claimed.

Three consequences checked rather than assumed:

- **#261 is untouched.** Its session's view is *empty*, so condition 1 fails.
  The matrix's first row is identical on all three arms, and
  `test_bind_on_resume_still_binds_a_session_that_has_no_binding_at_all` pins
  both the write and the next call's read of it.
- **An own entry whose spine is unreadable still scans and still binds.** It
  fails condition 2, not condition 1. Row 8 of the matrix is identical on all
  three arms, and two pre-existing tests (`..._still_writes_under_the_bare_key`,
  `..._merges_onto_existing_sibling_binding`) pin it.
- **The gauge.** `gauge_writer_hook.resolve_gauge_path` resolves from the
  binding key, so a withheld session gets no gauge path. That is the correct
  answer for classes 1–4: the session is not driving a spine, and the gauge it
  would otherwise have written was for **another agent's** spine under this
  session's name.

**The exception — class 5.** A session that genuinely claimed a path also
claimed by its subagent loses ownership of it to `session_view_provenance`'s
last-key-wins, and now loses the scan fallback with it. Before this change the
scan could re-bind it and restore an ownership it really did have. That is a
real, narrow loss, and it is not a reason to keep the fallback: papering over a
provenance collision by manufacturing ownership from a glob is the exact move
B4 condemns. It is `tc5`, it is already recorded, and it wants a decision about
which of two keys owns a path both claimed — not a wider fallback.

## What did NOT move

Rows 1, 2, 3, 5, 7 and 8 of the matrix are identical across `6bba3fd2` and the
working tree: #261's bind, the empty-and-nothing-to-find case, the ambiguous
scan on an empty view, the owns-nothing-and-nothing-to-scan case, resuming from
an own readable entry, and the unreadable-own-entry scan. The whole Stop column
is unchanged except where a binding the SessionStart wrote is what moved it.
