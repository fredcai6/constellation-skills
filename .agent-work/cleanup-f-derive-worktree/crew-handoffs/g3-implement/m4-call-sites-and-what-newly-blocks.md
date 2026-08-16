# g3 — before/after per call site, and what newly blocks

Measured, not recalled: every row below is reproduced by
`m4_differential.py`, which loads the hook at `999b7663` and the hook in the
working tree into one process and feeds both the same constructed payloads and
binding store. Its output is `m4-differential-before-after.txt`.

## The two call sites are not symmetric

### Site 1 — `_entry_mid_flight_view`, reached from `decide_stop`

**Before.** The entry was skipped — the Stop was allowed on its account —
whenever `data["cwd"]` and the entry's recorded `worktree` were both truthy and
compared unequal under `normcase` + `normpath`. Whether the entry belonged to
this agent was never asked.

**After.** The function reads no payload at all. Mid-flight is a property of the
spine: an open gate under an active lease, not honestly blocked. Every such
entry visible to the session blocks.

**Ownership moved up, into `decide_stop`, where it decides only what is
RENDERED.** `session_view_provenance` already said which binding key sourced
each visible path; it is now compared against `binding_key(payload)` — the
acting agent's own key — rather than against the bare `sid`. The stopping agent
is answered with **its own** gate wherever it has one, and otherwise with the
foreign-owner wording, imperative withheld from both `reason` and
`additionalContext` (#549, unchanged). A payload carrying no `agent_id` yields
the bare `sid`, which is exactly the pre-change comparison.

Two things this deliberately does NOT do: it does not decide whether to block
(an open gate blocks either way), and it does not touch the nudge record, which
stays keyed by `sid` alone.

### Site 2 — `decide_session_start`

**Before.** The same tree comparison, deciding which bound entry a resumed
session reads.

**After.** The comparison is gone; the first entry with a spine wins, as the
comment always said it did. This is **not** site 1's rule repeated, and the
reason is the payload: SessionStart is a per-harness-session event and carries
no `agent_id`, so every entry in the merged view was claimed by *this* session —
under its bare key or under a per-agent key of its own (#419's read-through,
which the tree test silently undid whenever a subagent claimed from elsewhere).
There is no second live agent here to tell apart; membership in the view IS the
binding-key answer, and the tree added nothing to it.

The direction of that change is toward safety, not away from it: falling through
to `_scan_active_spine` is what hands a session a spine it never claimed, and a
session that reads its own binding never reaches the scan.

## What newly blocks

| # | situation | before | after | intended? |
|---|---|---|---|---|
| 1 | This agent claimed a spine while standing in another worktree, then stops (S3) | allowed | **blocks**, its own gate and imperative rendered | Yes. It is this agent's own mid-flight run; where it is standing was never evidence about that. This is the largest newly-blocking class. |
| 2 | A crew in its own tree holds the only open gate; the parent stops (S4) | allowed | **blocks**, foreign-owner wording, imperative withheld | Yes. This is #419's ruling — a parent must not read silence as "done" while a subordinate's gate is open — which the tree test was defeating for exactly the crews that had their own tree. Same-tree crews already blocked. |
| 3 | Recorded worktree and cwd differ only by case or separator (S8) | allowed on POSIX, blocked on Windows | **blocks** on both | Yes, and it removes a platform-dependent decision rather than adding one. |

Nothing newly **stops** blocking. The set of allowed Stops shrinks by exactly
these three, and the surviving non-blocking shapes are what they always were:
no binding, an unreadable spine, a released lease, an honest engine block, and
the 3-strike escape hatch.

**Two renderings change without changing whether it blocks:**

- A parent with a gate of its own is now answered with **its own** gate rather
  than with whichever entry led the merged view — routinely its in-tree crew's
  (S1). This is the #549 shape the gate exists to fix.
- A crew whose payload carries its `agent_id` is answered with **its own** gate,
  where before it was told its own gate was foreign and given nothing (S2).

## The fail-safe direction

Six garbage rows (S6) — `worktree` null, int, empty; `cwd` int, dict, absent —
block before and after, rendering the gate's own imperative. The comparison that
could error is gone, so there is no longer a comparison to fail; the fields it
read are now inert, and inert means blocked.

The one place uncertainty is new is S7: a payload whose `agent_id` is malformed
(`"a/b"`) makes `binding_key` refuse to compose a key (#441's allowlist), so the
hook cannot say who is stopping. Before, the entry read as the bare session's
own and its imperative was handed over. After, nothing matches an unplaceable
agent, so it still **blocks** and the imperative is **withheld**. Uncertainty
withholds; it never relaxes and never hands an unidentifiable agent someone
else's next step.

`_same_path`'s fail-safe `True` on error is untouched and still guards its
remaining callers, `git_worktree_roots` and `resolve_spine_candidate`.

## Windows

Nothing in the ownership decision folds case or separators any more, so there is
nothing platform-specific left to get wrong: session ids and agent ids are
opaque harness tokens compared for exact equality, and `_AGENT_ID_ALLOWED`
forbids a separator in an agent id outright.

Both the test and the differential **construct** the Windows expectation rather
than reading it off this host, because `os.path.normcase` is the identity
function on Linux and an inherited expectation would be vacuous here:
`normcase("C:\\Foo\\wt") == normcase("c:/foo/wt")` is asserted to be true only
on `win32`, and the Stop verdict is asserted to be `block` regardless. Before
the change that same input produced two different answers on the two platforms.

`_worktree_from_spine` still folds case, and its shared case table in
`tests/test_worktree_derivation.py` is unedited and green — it is a location
question, and location is the one thing the tree still answers.
