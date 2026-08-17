# Implementation Result

## Assigned gate

`g3` — lane F, issue #609: **the worktree stops answering "is this mine."**
Worktree `/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`, diff base `999b7663` (read with
`git rev-parse HEAD`, not from the handoff — the handoff's `53c89ba1` was one
commit stale).

## Completed slice

`_foreign_worktree` is **deleted** with both its call sites. Ownership is now
binding-key provenance, and the two sites got **different** replacements,
because they were never symmetric:

- **`_entry_mid_flight_view`** now decides no ownership at all. Mid-flight is a
  property of the spine — an open gate under an active lease, not honestly
  blocked — so it reads no payload, and every such entry visible to the session
  blocks. Ownership moved **up** into `decide_stop`, where it decides only what
  is **rendered**: `session_view_provenance` is compared against
  `binding_key(payload)` — the acting agent's own key — instead of against the
  bare `sid`, and the stopping agent is answered with **its own** gate wherever
  it has one, otherwise with #549's foreign-owner wording, imperative withheld
  from both `reason` and `additionalContext`.
- **`decide_session_start`** simply stops testing the tree. SessionStart carries
  no `agent_id` — it is a per-harness-session event — so every entry in the
  merged view was claimed by *this* session, under its bare key or a per-agent
  key of its own (#419's read-through, which the tree test silently undid
  whenever a subagent claimed from elsewhere). There is no second live agent
  there to tell apart; membership in the view **is** the binding-key answer.

New helper `_is_own_entry(owner_key, own_key)` holds that one comparison. It
never raises, and reads a missing key in two deliberate directions: an
unplaceable path is **own** (preserving the pre-#549 rendering), while an
unidentifiable *agent* matches nothing (blocks, withholds).

Task item 3 done: the two stale passages naming
`checklist_engine.worktree_from_spine_path` as a live twin now say what is true.

## Scope

**Files changed:**

- `scripts/hooks/spine_rail.py`
- `tests/test_spine_rail.py`
- `map/INDEX.md` — regenerated with `py -m scripts.code_map build`, never
  hand-edited (#544). Only `tests` moved: 4832 → 4843 entities. `scripts` is
  unchanged at 1224 because `_foreign_worktree` left as `_is_own_entry` arrived.
- `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement/**` — this
  run's plan, evidence and the differential harness. Left unstaged and
  uncommitted for the Commander, per the handoff.

**Specific exclusions touched:** no. No engine, no template, no installer, no
lane A/E file, no `scripts/verify_worktree_isolation.py`, no fail-closed
refusal, no `cwd` threading. `tests/test_worktree_derivation.py` is unedited
(`git diff --quiet` passes) and green.

## Behavior changed

Yes — the Stop hook blocks **more**, and two renderings change without changing
whether it blocks. Full detail with measured before/after in
`crew-handoffs/g3-implement/m4-call-sites-and-what-newly-blocks.md`.

**What newly blocks** (each row measured, `m4-differential-before-after.txt`):

| # | situation | before | after | intended? |
|---|---|---|---|---|
| 1 | This agent claimed a spine while standing in another worktree, then stops (S3) | allowed | **blocks**, own gate and imperative rendered | Yes — its own mid-flight run; where it stands was never evidence about that. The largest newly-blocking class. |
| 2 | A crew in its **own** tree holds the only open gate; the parent stops (S4) | allowed | **blocks**, foreign-owner wording, imperative withheld | Yes — this is #419's ruling, which the tree test was defeating for exactly those crews that had their own tree. Same-tree crews already blocked. |
| 3 | Recorded worktree and cwd differ only by case/separator (S8) | allowed on POSIX, blocked on Windows | **blocks** on both | Yes — it removes a platform-dependent decision rather than adding one. |

Nothing newly stops blocking. The surviving allowed-Stop shapes are unchanged:
no binding, unreadable spine, released lease, honest engine block, 3-strike
hatch. The nudge record stays keyed by `sid` alone (asserted).

**Renderings that change:**

- A parent with a gate of its own is answered with **its own** gate rather than
  with whichever entry led the merged view — routinely its in-tree crew's (S1).
  This is the #549 shape.
- A crew whose payload carries its `agent_id` is answered with **its own** gate,
  where before it was told its own gate was foreign and given nothing (S2).

## Map Impact

- **Structural anchors touched:** `_foreign_worktree` **deleted** (2 call sites,
  both removed); `_is_own_entry` **added** beside `_entry_mid_flight_view`;
  `_entry_mid_flight_view` signature narrowed from `(data, entry)` to `(entry)`;
  `decide_stop` gained the own-entry selection; `decide_session_start` lost the
  tree test. `_same_path` **survives** — it still has callers in
  `git_worktree_roots` and `resolve_spine_candidate` (plus an unrelated
  same-named helper in `scripts/map_orient.py`), and they ask it about paths,
  which is all it ever knew.
- **Capabilities affected:** `scripts.hooks.spine_rail` — Stop refusal and
  SessionStart resume-context injection, per "Behavior changed" above.
- **Constraints honored:** stdlib-only — the import block is byte-identical
  before and after (11 imports, printed by the differential). Fail-safe, not
  fail-open — six garbage rows block on both sides; uncertainty now also
  withholds. `_worktree_from_spine` returning `None` still refuses nothing.
- **Decisions:** `worktree-is-location-spine-path-is-identity` is now true of
  the hook, not just of the engine. The handoff's open decision pressure —
  *what replaces the skip at each call site* — is **resolved and asymmetric**;
  the two answers are stated separately above and in the evidence file, and I
  recommend recording that asymmetry rather than a single rule.
- **Claims/evidence produced:** the #549 shape is pinned by
  `OwnershipIsBindingKeyNotWorktree` in `tests/test_spine_rail.py`;
  `test_foreign_worktree_is_gone_and_stays_gone` pins the deletion so a
  re-landing is a deliberate act with a red test to answer for.
- **Triage candidates:** two, below under Out-of-scope observations.

## Test mode

**Required:** test-first (TDD).
**Satisfied:** yes — red observed against the unmodified hook, then green, with
the class named exactly as the close criteria require.

## Evidence

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_spine_rail.py -k OwnershipIsBindingKeyNotWorktree
# 8 passed, 152 deselected            (m1-green.txt)

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_spine_rail.py tests/test_worktree_derivation.py
# 178 passed, 1 skipped, 9 subtests passed

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q
# 3177 passed, 5 skipped, 1192 subtests passed, 0 failed   (m4-full-suite-after.txt)

py .agent-work/cleanup-f-derive-worktree/crew-handoffs/g3-implement/m4_differential.py
# BEFORE (999b7663) vs AFTER, same payloads, one process  (m4-differential-before-after.txt)
```

**Result:** pass.

**Baseline, re-measured on this tree at `999b7663` before any edit:** 3170
passed, 5 skipped, 0 failed — matching the handoff. After: **3177 passed, 5
skipped, 0 failed**. Delta **+7**, and it accounts for every test: 8 new
`OwnershipIsBindingKeyNotWorktree` methods, plus
`test_foreign_worktree_is_gone_and_stays_gone`, minus the 2 deleted
`_foreign_worktree` unit tests. Failure distribution derived mechanically
(`grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`): **empty on both sides**,
0 `FAILED` lines each (`m4-suite-arithmetic.txt`).

`CREW_SCRATCH_DIR` was scrubbed as the handoff instructed; lane E's
`test_crew_launcher.py` test was not touched. One intermediate run failed
`tests/test_code_map.py::MapTreeFreshnessTests` because entity counts had moved;
regenerating `map/INDEX.md` cleared it, and the run above is post-regeneration.

**Load-bearing evidence, all four:**

1. **The #549 shape, run.** Parent and in-tree crew sharing ONE worktree, both
   bound by the real claim writer from the pinned real payloads (parent without
   `agent_id`, crew with one). Failing before (`m1-red.txt`), passing after
   (`m1-green.txt`), and reproduced independently by the differential (S1).
   What the red output actually shows is worth the Commander's eye: before the
   change the parent's Stop was answered **about the crew's spine**
   (`.../run-crew/spine.json`, foreign-owner wording) with the crew's imperative
   already withheld by #549 — so the defect is that the parent's **own** open
   gate never rendered at all, not that the crew's imperative leaked.
2. **Before/after per call site, stated separately** — `m4-call-sites-and-what-
   newly-blocks.md` §"The two call sites are not symmetric".
3. **What newly blocks, enumerated** — the table above, three classes, each with
   its intent.
4. **The fail-safe direction, demonstrated with garbage.** Six rows (`worktree`
   null / int / empty; `cwd` int / dict / absent) block before **and** after,
   rendering the gate's own imperative. The comparison that could error is gone,
   so the fields it read are inert — and inert means blocked. The one new
   uncertainty is a malformed `agent_id`: `binding_key` refuses to compose a key,
   so nothing matches, and the stop **blocks with the imperative withheld** (S7).

**Confirmatory:**

- **No new import.** The differential prints both import blocks and asserts them
  identical: `errno, json, os, re, shlex, subprocess, sys, tempfile, time,
  datetime, pathlib` — 11, all stdlib, unchanged.
- **Windows.** Nothing in the ownership decision folds case or separators any
  more: session ids and agent ids are opaque harness tokens compared for exact
  equality, and `_AGENT_ID_ALLOWED` forbids a separator in an agent id outright.
  Both the test and the differential **construct** the expectation instead of
  inheriting it — `normcase("C:\Foo\wt") == normcase("c:/foo/wt")` is asserted
  true only on `win32`, and the Stop verdict is asserted `block` regardless.
  Before the change that same input gave two different answers on the two
  platforms. `_worktree_from_spine` still folds case; that is a location
  question, and its shared case table is unedited and green.
- **Wiring greps.** `_foreign_worktree|_same_path|session_view_provenance|_is_own_entry`
  over `scripts/ tests/`: **57** lines, down from 61. Call sites removed: 2
  (`_entry_mid_flight_view`, `decide_session_start`). Call sites added: 2
  `_is_own_entry` calls, both in `decide_stop` (selection, then rendering).
  `worktree_from_spine_path` in my two files: **0**.
- **Validated from outside the session.** Per the handoff, `decide_stop` and
  `decide_session_start` were called directly with constructed payloads and a
  constructed binding store; nothing relies on this session's own hook, whose
  `CLAUDE_PROJECT_DIR` resolves to the main checkout (#269).

## TDD evidence, if required

- **Failing test observed:** `m1-red.txt` — 8 failed (5 methods + 3 subtests),
  3 passed, 153 deselected, against the unmodified `spine_rail.py` at
  `999b7663`. The 3 green were deliberate controls (the differing-tree case the
  old code already got right; garbage location data already fail-safe).
- **Passing test observed:** `m1-green.txt` — 8 passed, 152 deselected.
- **Refactor while green:** yes — eight pre-existing tests were reworked after
  the class went green, and the suite was re-run to 0 failures.

## Docs/contracts touched

- `scripts/hooks/spine_rail.py` docstrings and section comment; the
  `_worktree_from_spine` twin passage (task item 3).
- `tests/test_spine_rail.py` — the same twin passage, and the section header
  where `_foreign_worktree`'s tests used to live.
- No `docs/` file changed. `docs/CHECKLIST_SCHEMA.md`'s amended
  `not-a-weaker-guard` wording was read, not edited: this gate removes no guard
  from a leased spine, it moves an ownership question off the tree.

## Assumptions

- **A Stop payload may or may not carry `agent_id`; the change is correct either
  way.** The pinned probe capture measures `agent_id` delivery for *PostToolUse*,
  not Stop. `decide_stop` asks `binding_key(payload)`, the single composer, so a
  payload without one yields the bare `sid` — exactly the pre-change comparison
  — and one with a usable id answers the acting agent with its own gate. No test
  claims the harness sends it at Stop.
- **Eight pre-existing tests moved, none weakened.** Two deleted with the symbol
  (`_foreign_worktree`'s unit tests, replaced by a pin on its absence); three
  flipped to assert the new refusal (`test_stop_own_claim_from_another_worktree_now_blocks`,
  `test_stop_door_claimed_own_spine_in_another_worktree_now_blocks`, and the
  post-release assertion in
  `test_binding_worktree_comes_from_resolved_spine_in_real_linked_worktree`);
  three had used a foreign worktree only as a *device* to reach a branch and now
  use an unreadable target, which is the shape that still reaches it.
- **`decide_stop`'s renderer had to change, and I read that as inside my
  latitude** ("what precisely replaces the skip at each of the two call sites").
  Removing the skip changes which entries reach the renderer, so leaving
  `mid_flight[0]` in place would have handed a Commander its crew's gate — the
  very thing the gate exists to stop. It changes only *which* blocking entry is
  named, never whether it blocks.

## Stop conditions hit

None. Allowed scope was sufficient, no exclusion needed touching, all required
evidence was producible, and nothing that must not be blocked turned out to
block.

## Out-of-scope observations

1. **Triage candidate — the SessionStart scan-bind still binds a session to a
   spine it never claimed, and this is the mechanism behind the five-crew
   failure the Protected Intent describes.** When a session has no binding at
   all, `decide_session_start` falls through to `_scan_active_spine`, and on
   exactly one active-leased spine it **writes a binding** for that session and
   injects "drive this gate". A `run_crew.py`-launched crew has its own
   `session_id` and no binding, so the single active spine it finds is its
   **parent Commander's**, under the parent's live lease. From that moment the
   crew's own Stop is answered with the parent's `execute` gate — and by
   provenance it now genuinely *is* the crew's binding, so this gate's fix
   cannot reach it. **Observed live in this very session:** my SessionStart
   context told me to reload the commander skill and drive `execute.json` on the
   parent's spine. Binding-key provenance cannot fix it because there is no
   binding key yet at scan time; the discriminator would have to be the engine
   lease's owner. Not mine — it needs an authority decision and it touches the
   scan-bind path, not the two call sites I was given.
2. **The handoff's Wiring Grep asks for zero repo-wide references to
   `worktree_from_spine_path`; that is not achievable and should not be.** Two
   remain outside my allowed scope, and **both are true prose recording the
   deletion**, not stale claims: `tests/test_worktree_derivation.py`'s header
   (which must stay unedited, and is where the accurate account lives) and
   `tests/test_spine_origin_isolation.py`'s docstring explaining why its
   positive anchor had to move off that symbol. The Close Criteria's narrower
   form — zero in `spine_rail.py` and `test_spine_rail.py` — is satisfied.
3. **A pre-existing test defect found and repaired in my own file.** Two legs of
   the old `test_session_start_foreign_skip_same_reinject_fallback_reinject`
   wrote their bindings in the pre-#202 **flat** shape, which `load_binding`
   drops on sight — so each was silently answered by the fallback scan rather
   than by the binding it named, and the "foreign is skipped" leg proved nothing.
   Rewritten through `bind()`'s real nested shape, with the readable leg placed
   outside the scan's reach so only the binding can explain its marker.
4. `map/ids.jsonl` is 0 bytes and per-module `map/<module>/INDEX.md` files are
   absent repo-wide — already recorded as tc1, confirmed still true, not chased.

## Workflow Feedback

- **Handoff gaps:** (a) The **Wiring Grep**'s "it must return **zero** lines
  when you are done" is wrong, and its stated reason — "every remaining
  reference to it is stale prose in your two files" — is factually false: two
  live outside my scope and both are correct prose. The Close Criteria's version
  of the same check is right; the two should agree. (b) The **diff base** is
  given as `53c89ba1` in the baseline table while the handoff elsewhere tells me
  to trust `git rev-parse HEAD`, which was `999b7663`. The instruction saved me;
  the stale number should just go, as the handoff did with line citations.
  (c) **Required Evidence item 1** says to show the #549 shape "failing before
  and passing after" but does not say *what* fails — I had to derive that the
  in-tree crew's entry wins `mid_flight[0]` and displaces the parent's own gate.
  Naming the observable ("the parent's own imperative never renders") would have
  removed the only genuinely ambiguous part of this gate.
- **Context rediscovered:** that `decide_stop`'s renderer compares provenance
  against the **bare `sid`**, not against the acting agent's key. The handoff
  says provenance "is already computed" at that site, which reads as *already
  correct*; it is the half that had to change for the crew-side inverse the
  Protected Intent describes. Also that this repo ships **no pytest config**, so
  a plain class named `OwnershipIsBindingKeyNotWorktree` would not be collected
  at all — it must subclass `unittest.TestCase`. A close criterion that mandates
  a non-`Test*` class name should say that, or the gate silently collects zero
  and reads as still-red.
- **Instructions improvised around:** the implementer skill opens with "a spine
  is bound for you; `spine_status` is your first call." My `crew-runs.json`
  entry has `spine: null` while `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT`
  point at the **parent Commander's** spine under the parent's live lease, so
  obeying it literally means advancing someone else's gate or force-taking a
  live lease. I authored my own plan under
  `crew-handoffs/g3-implement/IMPLEMENTER_PLAN.json`, claimed it with my own
  session id, and drove it through the `checklist_engine.py` CLI, writing
  nothing to the parent spine. This is the fifth crew on this issue to hit it.
  The durable fix is a lease-ownership check in the hook (observation 1), not
  more prose in the skill.
- **What would have made this easier:** one line in the handoff saying the
  gate's observable is *"the parent's own gate must render; today the crew's
  entry displaces it"* — that is the whole change, and everything else follows
  from it.

## On the Stop hook

**It fired, twice, and I refused it.** At the end of my turn the Stop hook
returned `SPINE MID-FLIGHT: gate execute is still open`, instructing me to
reload the commander skill and drive `execute.json` gate by gate.

Measured rather than assumed, before refusing:

- `SPINE_FILE` → `.agent-work/cleanup-f-derive-worktree/execute.json`, whose
  `engine_session` is `commander-cleanup-f-derive-worktree`, `status: active`,
  `claimed_by: commander` — **my parent's live lease, not mine.**
- My own `crew-runs.json` entry: `spine: null`, `parent:
  constellation/cleanup-f-derive-worktree/execute/commander/attempt-4`.
- My own plan: `LEASE released`, no open items.

So the gate the hook named is not mine to drive, and obeying would advance
someone else's run under someone else's lease. The hook's own escape hatches
are no better: `block` and `waive` both **write to that same parent spine**, so
the sanctioned honest stop is itself the destructive act. Hence a plain refusal,
recorded here and nowhere else — I wrote nothing to `execute.json`.

This is the sixth instance on this issue, and it is the inverse case the
Protected Intent describes, so it is worth being precise about what my change
does and does not touch. The hook keyed on the **spine's** mid-flight state
here, not on a binding of mine: my session holds no binding into `execute.json`
(the launcher's own `attach` at journal seq 76 is the Commander's write, not
mine), so this nudge came from the *parent's* own session state, which this gate
never claimed to fix. What binding-key provenance now prevents is the adjacent
failure — a crew that **has** been bound to its parent's spine being handed the
parent's imperative — and observation 1 above names the remaining mechanism that
creates such a binding in the first place.

My own plan is driven to done and its lease released; the run is complete on my
side.

## Return status

complete
