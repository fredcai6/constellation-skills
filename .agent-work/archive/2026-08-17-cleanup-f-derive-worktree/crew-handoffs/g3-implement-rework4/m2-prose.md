# B7 — every sentence that stated the guard's reach, one by one

`owners` is `session_view_provenance(binding, sid)`: the bare `sid` plus this
session's own `sid#agent_id` keys. It is a **view**, not the binding store. A
claim filed under a different harness `session_id` is not in it, so the guard
answers `False` for such a path and the caller proceeds. That is the limit every
sentence below now names. The guard's **reach is unchanged** by this rework —
widening it across the session boundary is the Admiral's call.

## The three the review named

| # | where | was | now |
|---|---|---|---|
| 1 | `_attributed_to_another_key` docstring, opening line | "Whether **the store** ALREADY attributes `spine_path` to a binding key other than `bind_key`" | "Whether **`owners`** ALREADY attributes…", followed by a `WHAT owners IS, AND IS NOT` paragraph naming the session-scoped limit and the cross-session gap |
| 2 | the bind-on-resume call site | "it may not CONTRADICT an attribution **the store already holds**" | "…an attribution already **VISIBLE TO THIS SESSION**", plus a paragraph spelling out that "visible to this session" is the literal reach and that a different `session_id`'s claim is not in it |
| 3 | `test_a_restarting_parent_is_not_bound_to_a_spine_its_crew_visibly_claims` docstring | "must not file a spine path **the store** already attributes to a DIFFERENT binding key" | "…a spine path **this session's VIEW of** the binding store already attributes…", naming the two key shapes and stating that this case does not exercise a cross-session claim |

## Three more copies of the same claim, found by grepping the claim

| # | where | repair |
|---|---|---|
| 4 | module-level three-states block: "`_attributed_to_another_key` refuses to file a path **the store** already attributes to a DIFFERENT binding key" | now "**THIS SESSION'S VIEW of** the binding store", names `session_view_provenance`'s two key shapes and the invisible cross-session claim; also updated to say the predicate now refuses to **render** as well as to file. This is one of the four taxonomy copies — repaired in place, no fifth copy added. |
| 5 | `test_the_writer_rule_refuses_only_a_contradicting_attribution` docstring: "a path **the store** attributes to NOBODY" | now "a path **the given attributions** place with NOBODY", with a paragraph saying the mapping under test is a `session_view_provenance` view and that a cross-session claim is what it genuinely cannot see. Renamed to `test_the_attribution_rule_…`: the predicate now has a second caller, so "writer rule" was narrower than what the test covers. The rename is recorded in the docstring itself. |
| 6 | `test_the_writer_rule_…`'s assertion labels | unchanged — they name the mapping, not the store |

## Sentences my own B6 repair made stale, and repaired in the same pass

| # | where | was | now |
|---|---|---|---|
| 7 | `_scan_active_spine` docstring | "while still wanting the same **'first match' spine** for the advisory-context injection" | "the spine it injects as advisory context is the first match **this session's view does not attribute to another binding key** — not simply the first" |
| 8 | `decide_session_start`, above the reader guard | "The scan below can hand it whatever **single** active-leased spine the tree holds … That case is answered at **the WRITE instead**" | "whatever active-leased spine the tree holds … answered below, by `_attributed_to_another_key`, asked once of what the scan **RENDERS** and once of what it **WRITES**" |
| 9 | the write branch's count comment | "Zero or 2+ matches: **inject context (below)** but write NO binding" | "write NO binding … while the context injection below still hands out **whatever the selection above kept**" |
| 10 | the write guard's comment: "the reason it is **here rather than one branch up with the selection**" | the selection one branch up now asks the same question, so that reason was false | now "asked again here rather than read off the selection above", with the reason it is asked twice: the two acts take the path in different ways, and the write files under the bare `sid` |
| 11 | module three-states block, third bullet: "the scan may then hand that agent whatever **single** active-leased spine the tree holds" | "whatever active-leased spine … **on one match by writing a binding as well, on two or more by rendering alone**" |
| 12 | `OwnershipIsBindingKeyNotWorktree` class docstring: "there are **two such fixtures and not one**" | a third fixture now exists, so the count was false; the paragraph names `_two_active_spines_and_the_parents_archived_spine` and why the scan COUNT is the variable it adds |

## Checked and left alone

- `_own_entries`' docstring — "The write is guarded at the write, by
  `_attributed_to_another_key`" is still true; the render guard does not
  contradict it, and restating the taxonomy there would be a fifth copy.
- "What the SECOND call renders, through the store the first one left" — about
  what the first call wrote, not about the guard's reach.
- "the store shape is production's" — about the fixture's writers.
- The three `store` mentions in the gauge/claim-resolution prose — a different
  subject entirely, untouched by this gate.
