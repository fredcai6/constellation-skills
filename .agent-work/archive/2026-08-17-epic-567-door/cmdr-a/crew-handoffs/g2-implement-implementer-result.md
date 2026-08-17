# IMPLEMENTER_RESULT — g2-implement: `spine_bind`

Return status: complete

**Gate:** `g2-implement` (epic-567-door/cmdr-a, lane A of epic #567)
**Branch:** `feat/567-a-spine-identity`
**Commits:** `86109e2f` (the `session_id_for` extraction) and `0189dc26` (`spine_bind`),
deliberately separate — the design is not human-ratified
(`decision:convergence-is-human-only`), so the tool reverts on its own.

---

## 1. What was added

One MCP lifecycle tool, `spine_bind(spine_file)`, which binds this door process to a
spine that **already exists**. Nothing else about the door changes shape: the nine
engine pass-throughs are untouched, `_identity_violation` is untouched,
`_bind_process_to` is untouched, and no existing tool gains an argument or changes
behaviour.

`scripts/mcp_spine_server.py`:

| symbol | what it is |
|---|---|
| `_spine_bind(args)` | the dispatch function; nine refusals, one success |
| `_own_checkout_for_binding()` | the containment root — `--show-toplevel`, **not** `--git-common-dir` |
| `_checkout_containing(directory)` | the one `--show-toplevel` resolution; three anchors, three callers |
| `_derivable_work_id(spine)` | `origin.work_id` else the spine's top-level `work_id` |
| `_unusable_spine_reason(spine)` | `_unbound_refusal`'s ladder, extracted and shared |
| `_THE_CLI_IS_PER_CALL` | the one closing clause every containment refusal ends with |

Changed: `_unbound_refusal` delegates its ladder; `_worktree_root_for_lifecycle`
delegates its `--show-toplevel` resolution; `_rebind_refusal` gains
`acting_tool: str = "spine_open"` and its one text now says "Rebinding this door now"
rather than "Opening new work now"; `BINDS_WITHOUT_A_BOUND_SPINE` gains `"spine_bind"`;
`call_lifecycle_tool` gains one route; `LIFECYCLE_TOOLS` gains one schema entry; the
module docstring's "exactly ONE declared tool property carries a filesystem path" is
rewritten to two, with the second one's confinement named.

`scripts/spine_lifecycle.py`: `session_id_for(work_id)` extracted; `open_work` calls it.

**Deliberately not done.** Candidate A §5 proposed collapsing `_HOW_TO_REBIND` into
`_HOW_TO_BIND`. I took the fallback it names instead: both constants survive, and only
the *relaunch clause* is deleted from each ("or relaunch this door with SPINE_FILE set
to an existing spine file" — advice a model inside that door usually cannot follow).
Both now name `spine_bind` first and `spine_open` second. Keeping the split preserves
`_unbound_refusal`'s own argument that an unbound door has no path to name, and keeps
`test_mcp_door_unbound.py`'s `REBIND_ANCHOR` meaningful. The deletion is one clause
instead of one constant.

---

## 2. The containment root, and its measured reach

**Implemented: `git rev-parse --show-toplevel`, from `SPINE.parent` when bound and from
`Path(__file__).resolve().parent` when not — confined further to
`<that checkout>/.agent-work/`, plus a refusal for any candidate whose own
`--show-toplevel` differs from this door's.**

Handoff A1, followed. `_primary_checkout_for_lifecycle()` was **not** used.

### The reach delta, re-measured myself

Counting readable JSON objects under an `.agent-work/` carrying a derivable `work_id` —
which is exactly the set `_spine_bind` will accept — anchored on this door's own script
location in the live tree:

| containment root | candidates | with an active `engine_session` | inside a `.worktrees/` subtree |
|---|---|---|---|
| `_primary_checkout_for_lifecycle()` — `--git-common-dir` → `/home/tommy/projects/constellation-skills` | **6102** | **307** | 5089 |
| `_own_checkout_for_binding()` — `--show-toplevel` → `.../.worktrees/567-a-spine-identity` | **1014** | **51** | 1014 |
| **excluded by A1** | **5088** | **256** | — |

The active-lease counts reproduce the handoff's numbers exactly (307 and 51). The file
counts are higher than the handoff's 4205/683 because the tree has grown since it was
written; the ratio is 6.0x and the direction is identical. `_primary_checkout_for_lifecycle`
is still correct for `spine_open`, which must *create* a worktree and therefore must nest
it under the primary checkout — two questions, two roots, both named in the module
docstring so nobody merges them.

### A2: the design's false sentence is now true

`DESIGN_CONVERGENCE.md` claimed, eighteen lines apart, both "including a sibling
worktree's live spine may become the spine this process drives" and "what an agent still
cannot do: drive a spine in another checkout." A linked worktree *is* another checkout.
Under the shipped root the second sentence holds, and §4 below is the measurement.

---

## 3. The two-door round trip

Load-bearing evidence. Door 1 mints; door 2, launched with **no** `SPINE_FILE` and **no**
`SPINE_SESSION`, binds the same spine and drives it to terminal. Door 2 runs the door
script *from the new worktree* — the topology `.mcp.json` actually produces, since it
launches the project-relative `scripts/mcp_spine_server.py` against the client's own cwd.

```
throwaway checkout: /tmp/tmpt6y59vgu/repo

### DOOR-1: launched  script=repo/scripts/mcp_spine_server.py
    env: SPINE_FILE=<ABSENT>  SPINE_SESSION=<ABSENT>
  DOOR-1 -> spine_status()
    isError=True   REFUSED: no spine is bound to this door, so there is nothing for this
                   tool to act on. Call `spine_bind` with the path to a spine that already
                   exists, or `spine_open` to mint a spine and bind this process to it.
  DOOR-1 -> spine_open(work_id='bind-roundtrip', spec={...}, base='HEAD')
    isError=False  {"SPINE_FILE": "/tmp/tmpt6y59vgu/repo/.worktrees/bind-roundtrip/.agent-work/bind-roundtrip/spine.json",
                    "SPINE_SESSION": "constellation/bind-roundtrip", "SPINE_PARENT": "unknown",
                    "branch": "bind-roundtrip", "worktree": "/tmp/tmpt6y59vgu/repo/.worktrees/bind-roundtrip"}

  == door 1 was bound BY MINTING to:
     SPINE_FILE   = /tmp/tmpt6y59vgu/repo/.worktrees/bind-roundtrip/.agent-work/bind-roundtrip/spine.json
     SPINE_SESSION= constellation/bind-roundtrip

### DOOR-2: launched  script=bind-roundtrip/scripts/mcp_spine_server.py
    env: SPINE_FILE=<ABSENT>  SPINE_SESSION=<ABSENT>
  DOOR-2 -> spine_status()
    isError=True   REFUSED: no spine is bound to this door, so there is nothing for this
                   tool to act on. Call `spine_bind` with the path to a spine that already
                   exists, or `spine_open` to mint a spine and bind this process to it.
  DOOR-2 -> spine_bind(spine_file='/tmp/tmpt6y59vgu/repo/.worktrees/bind-roundtrip/.agent-work/bind-roundtrip/spine.json')
    isError=False  {"SPINE_FILE": "/tmp/tmpt6y59vgu/repo/.worktrees/bind-roundtrip/.agent-work/bind-roundtrip/spine.json",
                    "SPINE_SESSION": "constellation/bind-roundtrip", "work_id": "bind-roundtrip",
                    "already_bound": false,
                    "note": "this door now drives that spine; call spine_status to see where it is"}

  == door 2 was bound BY BINDING to:
     SPINE_FILE   = /tmp/tmpt6y59vgu/repo/.worktrees/bind-roundtrip/.agent-work/bind-roundtrip/spine.json
     SPINE_SESSION= constellation/bind-roundtrip
  == BYTE-IDENTICAL?  SPINE_FILE True   SPINE_SESSION True

  DOOR-2 -> spine_status()
    isError=False  ACTIVE m1 [pending] — do the thing / c1 [unmet] artifact — human decided / 0/1 met
  DOOR-2 -> spine_lease(action='claim', claimed_by='implementer')
    isError=False  claimed lease constellation/bind-roundtrip -> active
  DOOR-2 -> spine_start(task_id='m1')
    isError=False  m1 -> in-progress
  DOOR-2 -> spine_evidence(action='attach', task_id='m1', evidence_type='user-decision', fields={'decision': 'go'})
    isError=False  attached e-m1-1 (user-decision) to m1
  DOOR-2 -> spine_advance(task_id='m1', mechanical=True)
    isError=False  m1 -> complete
  DOOR-2 -> spine_lease(action='release')
    isError=False  released lease constellation/bind-roundtrip

  == on disk: tasks.m1.status='complete'
              engine_session.session_id='constellation/bind-roundtrip'  status='released'

  == idempotency:
  DOOR-2 -> spine_bind(spine_file=<the same path>)
    isError=False  {..., "already_bound": true,
                    "note": "this door was already bound to that spine; nothing changed"}
  == reach delta, from the same door:
  DOOR-2 -> spine_bind(spine_file='/tmp/tmpt6y59vgu/repo/.agent-work/primary-work/spine.json')
    isError=True   REFUSED: this door may only bind a spine inside its OWN checkout's work
                   area ('/tmp/tmpt6y59vgu/repo/.worktrees/bind-roundtrip/.agent-work'); ...
```

`claim` succeeding is the half that proves `SESSION` moved and not only `SPINE`: the
engine refuses a claim with an empty `--session-id`, so a door that can claim is a door
whose session is genuinely bound. The lease recorded on disk is
`constellation/bind-roundtrip` — the spine's own identity, not one this door named.

---

## 4. The reach-delta refusals, quoted

All from the **linked-worktree** topology, which is the only one where the two candidate
roots disagree:

```
door bound to      : <tmp>/repo/.worktrees/lane-a/.agent-work/mine/spine.json
--show-toplevel    : <tmp>/repo/.worktrees/lane-a     <- boundary is this + /.agent-work
--git-common-dir   : <tmp>/repo                       <- the DESIGNED root, rejected
```

**A path outside the boundary is refused, and the refusal names the boundary.** Note that
this candidate is *inside* the root the design document named:

> REFUSED: this door may only bind a spine inside its OWN checkout's work area
> ('/tmp/tmp5ay227ms/repo/.worktrees/lane-a/.agent-work'); spine_file resolves to
> '/tmp/tmp5ay227ms/repo/.agent-work/primary-work/spine.json', which is outside. One
> checkout's work-area tree per process: a spine elsewhere -- including a sibling worktree
> of this same repository -- belongs to work whose worktrees, hooks and tests this door
> knows nothing about, and binding it would make this process the driver of a run it
> cannot see. Name a spine under that work area, or use the CLI, which is per-call by
> construction.

**A spine in a sibling worktree is refused:**

> REFUSED: this door may only bind a spine inside its OWN checkout's work area
> ('/tmp/tmp5ay227ms/repo/.worktrees/lane-a/.agent-work'); spine_file resolves to
> '/tmp/tmp5ay227ms/repo/.worktrees/lane-b/.agent-work/theirs/spine.json', which is
> outside. One checkout's work-area tree per process: [...] Name a spine under that work
> area, or use the CLI, which is per-call by construction.

**A checkout NESTED inside the boundary is refused — lexical containment passed:**

> REFUSED: '/tmp/tmp5ay227ms/repo/.worktrees/lane-a/.agent-work/nested-repo/.agent-work/n/spine.json'
> sits inside a DIFFERENT checkout
> ('/tmp/tmp5ay227ms/repo/.worktrees/lane-a/.agent-work/nested-repo') than this door's own
> ('/tmp/tmp5ay227ms/repo/.worktrees/lane-a'), even though its path is under this door's
> work area -- a checkout nested there is still another repository. One checkout's
> work-area tree per process. Name a spine under that work area, or use the CLI, which is
> per-call by construction.

**Neither `work_id` — and the refusal says why it matters:**

> REFUSED: '<...>/anon/spine.json' carries neither `origin.work_id` nor a top-level
> `work_id`, so this door cannot derive the session identity that spine is driven under --
> and a door bound with no session cannot `claim` (`checklist_engine.claim` refuses an
> empty --session-id), which means it would not be a bound door at all. Every spine the
> engine drives carries a `work_id`; a fragment or a hand-written JSON file does not.
> Drive that one through the CLI, which takes --session-id per call.

**The identity is live somewhere else:**

> REFUSED: '<...>/held/spine.json' is under an active lease held as
> 'constellation/held-work', and that is the very identity this bind would take (it is
> derived from the spine's own work id, never supplied). Two processes under one session
> id are indistinguishable to the engine, so this bind would put two agents on one lease.
> Whoever holds it must release it first (`spine_lease` with action 'release'), or its
> lease must go stale.

---

## 5. My own re-derivation of the `work_id` census

Ordered as the handoff asks: measured before I wrote any code, not taken on trust.
Spine-shaped files (a JSON object carrying `items` and `tasks`) under `.agent-work/` and
`.worktrees/*/.agent-work/`, excluding `archive/` and `templates/`:

| | count | handoff said |
|---|---|---|
| live spine-shaped files | **60** | 52 |
| carrying `origin.work_id` | **5** | 4 |
| no origin, but top-level `work_id` | **55** | 48 |
| **neither** | **0** | 0 |

The population grew by 8 since the handoff was written; the shape is identical.
**`origin.work_id` alone would refuse 55 of 60 — 92%.** And the two cases the handoff
names, checked individually:

```
.agent-work/epic-567-door/spine.json
  origin=None   top-level work_id='epic-567-door'
.agent-work/implementer-315-native-g1/IMPLEMENTER_PLAN.json
  origin=None   top-level work_id='implementer-315-native-g1'
.worktrees/567-a-spine-identity/.agent-work/epic-567-door/cmdr-a/spine.json
  origin.work_id='epic-567-door/cmdr-a'   top-level work_id='epic-567-door/cmdr-a'
```

Confirmed exactly as stated. The Admiral's own live spine and the
`IMPLEMENTER_PLAN.json` both have `origin: None`, and the Commander's own spine — the
one an implementer would naturally have tested against — is the one that *does* carry
`origin.work_id`. That asymmetry is why the check could not have failed by accident.

`origin.work_id` still **wins** where present, so a spine minted by `open_work` yields a
byte-identical session through either field. The refusal narrows to "neither field", which
the census says is currently never and is still the right fail-closed posture.

---

## 6. Pins and their positive controls

### The three named pins

| pin | state | what changed |
|---|---|---|
| `test_mcp_lifecycle.py:135` `ALLOWED` | green | gained `_spine_bind` — **an allow-list widened, not a ban loosened** |
| `test_mcp_lifecycle.py:563` `OneBinderPinTests` | green | **nothing.** `_spine_bind` assigns neither global; it calls `_bind_process_to` |
| `test_mcp_identity.py:817` identity-arg | green | `(tool, property)`-keyed exemption + detector extracted + IDENTITY_TRADE.md §7 |

The positive control at `test_mcp_lifecycle.py:156` is **byte-untouched.** The entire diff
to that file is the `ALLOWED` set and a comment above it:

```
-    ALLOWED = {"_spine_open", "_spine_close"}
+    #: [14 lines of comment recording that this is an allow-list that grows]
+    ALLOWED = {"_spine_open", "_spine_bind", "_spine_close"}
```

### The controls are honest — twelve mutation experiments, all RED

A pin nobody has watched fail is not evidence, so each was watched. Every mutation was
applied to the real source, the named tests run, and the file restored.

| # | mutation | result |
|---|---|---|
| M1 | delete the containment refusal entirely | RED — 6 failed |
| M2 | widen `bound_dir` from `<checkout>/.agent-work` to `<checkout>` | RED — 2 failed |
| M3 | **root := `_primary_checkout_for_lifecycle()` (the root the design named)** | RED — 4 failed |
| M3b | root := `SPINE.parent` (candidate C's "safe" root) | RED — 2 failed |
| M3c | anchor := `--git-common-dir` inside `_own_checkout_for_binding` | RED — 5 failed |
| M4 | delete the cross-checkout refusal | RED — 1 failed |
| M5 | delete the session fallback (`origin.work_id` only) | RED — 5 failed |
| M6 | key the identity exemption on the **tool** alone | RED — 1 failed |
| M7 | plant a mutate-then-return leak in the **real** `call_lifecycle_tool` | RED — 1 failed |
| M8 | remove `spine_bind` from `BINDS_WITHOUT_A_BOUND_SPINE` | RED — 3 failed |
| M9 | assign `SPINE` inside `_spine_bind` instead of calling the binder | RED — 7 failed |
| M10 | blind the lifecycle detector **inside its own positive control** | RED — the control is a real control |
| M11 | blind the **shared** identity detector | RED — pin *and* control both fail together |

M7 is the answer to "does the widened `ALLOWED` still forbid the shape?" — it does: a
mutate-then-return planted on the `spine_bind` route is caught with `_spine_bind` in the
allow-list. M10 and M11 are the answer to "are the controls still controls?" — a detector
that stops detecting takes its own control down with it, which is only true because A3's
extraction made them share one function.

**M3 was GREEN on first run, and that is the most important line in this report.** Every
fixture I had written bound the door inside a *primary* checkout, where `--show-toplevel`
and `--git-common-dir` return the same directory — so swapping in the wrong root left the
whole suite green. The handoff's warning was exactly right: *a green suite is not evidence
that reach did not widen.* I added
`TheRootMustBeTheDoorsOwnWorktreeTests`, which reproduces the linked-worktree topology
(door in `.worktrees/lane-a`, other lanes' work in the primary checkout and in
`.worktrees/lane-b`), including a non-vacuity control that the door's *own* worktree
remains bindable and a reach count asserting exactly 1 of 3 candidates is admitted. All
three root mutations are RED against it.

### A3, item by item

1. **`IDENTITY_TRADE.md` §7** — shipped in the same commit. Records what changed, that §2's
   sentence is now false as written and deliberately so, the measured reach table, the four
   things that still hold it in, which side of the trade this takes, what §2's capability
   loss becomes (partly refunded, not deleted), and two honest residuals. It states plainly
   that it is **not human-ratified**.
2. **The exemption is keyed on `(tool, property)`** — `BINDS_THIS_DOOR = {"spine_bind":
   ("spine_file",)}`, and `test_the_exemption_is_keyed_on_tool_and_property_not_on_the_tool`
   asserts both directions: a hypothetical `spine_bind.session_id` is still an offender, and
   `spine_advance.spine_file` is still an offender. Either assertion alone is satisfiable by
   the wrong implementation, so both are made.
3. **The detector is extracted** to module-level `identity_arg_offenders(...)`, called by
   the pin, by `test_the_pin_can_fail`, and by the new keying test. The control previously
   reimplemented the loop *and applied neither exemption*, so it would have kept passing
   while no longer controlling for the thing that changed. It now also asserts that the tool
   it plants on is not itself exempt.
4. **The argument is named `spine_file`.** Not renamed.

---

## 7. Wiring grep — call-site counts

```bash
grep -rn "\b<sym>\b" --include=*.py . | grep -v .agent-work | grep -v "def <sym>"
```

| symbol | call sites outside its own definition |
|---|---|
| `_spine_bind` | **1 live route** (`call_lifecycle_tool:1479`) + 1 in `_unbound_refusal`'s docstring + 9 test references |
| `session_id_for` | **2 live callers** — `spine_lifecycle.open_work:382`, `_spine_bind:1393` |
| `_unusable_spine_reason` | **2 live callers** — `_unbound_refusal:497`, `_spine_bind:1338` |
| `_own_checkout_for_binding` | **1 live caller** — `_spine_bind:1318` |
| `_checkout_containing` | **3 live callers** — `_own_checkout_for_binding:986`, `_worktree_root_for_lifecycle:1039`, `_spine_bind:1348` |
| `_derivable_work_id` | **1 live caller** — `_spine_bind:1381` |

No symbol has zero external call sites. `session_id_for`'s two callers are the whole
justification for extracting it (one adapter is a hypothetical seam; two is a real one),
and `_checkout_containing`'s three are what keep one `--show-toplevel` derivation from
becoming three.

---

## 8. Verification

```
$ python3 -m pytest tests/test_mcp_lifecycle.py tests/test_mcp_identity.py \
                    tests/test_mcp_door_unbound.py tests/test_mcp_spine_server.py \
                    tests/test_mcp_spine_bind.py -q
146 passed, 14 subtests passed
```

New test modules: `tests/test_mcp_spine_bind.py` (53 tests) and
`tests/test_spine_session_id.py` (5 tests). Both were written **before** the code and both
were watched fail first: the bind suite reported `48 failed` and the extraction suite
`5 failed` against the unmodified tree.

**One TDD near-miss worth recording.** The bind suite's first red run reported `60 failed,
4 passed` — and the 4 "passes" were tests whose bodies raised `AttributeError` inside a
`with self.subTest(...)` block, which pytest's unittest integration recorded as subtest
failures while reporting the outer test PASSED. A test that can pass while its body raises
is not evidence. I replaced every `subTest` in the file with a plain loop, after which the
suite reported `48 failed, 0 passed` — genuinely red. This is a general hazard in this
repo's pytest configuration, not something specific to my file; see Triage below.

Full suite: see §9.

---

## 9. Stop condition hit — reported, not fixed

**`run_crew.CREW_ALLOWED_TOOLS` does not grant `mcp__spine__spine_bind`, so the tool is
inert for every dispatched crew until it does.**

```
FAILED tests/test_crew_launcher.py::CrewGrantTiesToDoorTests::test_crew_grant_mcp_entries_equal_the_doors_own_tool_names
FAILED tests/test_crew_launcher.py::CrewGrantTiesToDoorTests::test_door_has_all_nine_tools_todays_grant_expects
  AssertionError: 11 != 12
```

These are **mine**, not the parallel g3 crew's — `11 != 12` is my tool. But the fix is one
entry in `scripts/run_crew.py`, which is **not in this gate's Allowed Scope**, and
`tests/test_crew_launcher.py` is outside the door/identity suites, which the handoff names
as a stop condition: *"report it, do not fix it."* So I stopped.

The pin's own comment records that it exists for exactly this failure — "without these, a
dispatched crew is silently denied `spine_open`/`spine_close` even though the door itself
advertises them ... exactly the 'two tools silently denied to every crew' failure this
tuple's own drift-guard test exists to catch." It has now caught it a second time, which is
the pin working.

**The one-line change the Commander must authorize:**

```python
# scripts/run_crew.py:640
-    "mcp__spine__spine_open", "mcp__spine__spine_close",
+    "mcp__spine__spine_open", "mcp__spine__spine_bind", "mcp__spine__spine_close",
```

and `tests/test_crew_launcher.py:562`'s `self.assertEqual(11, len(server.TOOL_NAMES))` →
`12`, with its comment updated. Note this does **not** block the gate's close criteria: the
door itself reaches the tool (§3 spawns the real server directly), and an Admiral or a
human-driven session is not launched through `run_crew`. It blocks the *dispatched-crew*
population specifically.

### The full suite, otherwise

```
$ python3 -m pytest tests/ -q
FAILED tests/test_crew_launcher.py::CrewGrantTiesToDoorTests::test_crew_grant_mcp_entries_equal_the_doors_own_tool_names
FAILED tests/test_crew_launcher.py::CrewGrantTiesToDoorTests::test_door_has_all_nine_tools_todays_grant_expects
2 failed, 3261 passed, 5 skipped, 1218 subtests passed in 137.22s
```

**Those two are the only failures, and they are the §9 stop condition.** Nothing else in
3261 tests is red — in particular no `test_checklist_engine*.py` and no other
`test_crew_launcher.py` test, so the parallel g3 crew's work and mine are not colliding.

An earlier run of mine also showed
`tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
red. I confirmed it was **pre-existing and not mine** by `git stash -u`, running it against
the untouched tree, and watching it fail identically ("`map/INDEX.md` is stale"). It is green
in the final run — the Commander rebuilt the map in `11f43388`/`d7af0847`, which landed
mid-run. Recorded because the intermediate red is in my transcript and a reviewer will see it.

I touched neither `scripts/checklist_engine.py` nor `scripts/hooks/*`. Confirmed by the
commit's own file list.

---

## 10. One scope deviation, declared

`tests/test_mcp_spine_server.py` is **not** in the Allowed Scope list, and I edited it.
Two of its assertions are hand-copied restatements of `LIFECYCLE_TOOL_NAMES`
(`- {"spine_open", "spine_close"}`) plus a literal tool count, and both fail the moment any
lifecycle tool is added — so this is the same class as the two pre-authorized pin edits, and
unavoidable. I read it as inside "the door/identity suites" because the handoff's own
Verification Commands run it in the same command as the three listed files.

The edit is **narrowing, not widening**: the two hand copies collapse into one named
constant, `LIFECYCLE_TOOLS_COVER_NO_VERB`, and the count becomes
`len(EXPECTED_TOOLS) + len(LIFECYCLE_TOOLS_COVER_NO_VERB)` rather than a literal `11`. Both
properties are preserved exactly — 18 of 18 engine verbs covered by the 9 engine tools, and
the door advertises exactly its committed surface. Flagging it for the reviewer to ratify
rather than burying it in the diff.

I also **added** a test to `tests/test_mcp_door_unbound.py` (which *is* in scope), because
adding `spine_bind` to that file's local `BINDS_WITHOUT_A_BOUND_SPINE` removes it from
`test_every_tool_but_the_one_that_binds_refuses`'s enumeration — a silent coverage loss.
`test_the_exempt_tools_are_genuinely_reachable_when_unbound` closes it from the other side:
each exempt tool is driven unbound and asserted to refuse on its **own** grounds rather than
on "no spine is bound". The two tests are two-sided, so neither the local set nor the
module's can drift alone.

---

## 11. Close criteria

| criterion | status |
|---|---|
| `spine_bind` in the tool surface; an unbound door calls it and then runs `spine_status` | **met** — §3 |
| The two-door round trip; door 2's `SPINE`/`SESSION` byte-identical to door 1's | **met** — §3, both `True` |
| Reach-delta negative test: outside the root is refused, refusal names the boundary | **met** — §4, and RED under M1/M2/M3/M3b/M3c/M4 |
| Binding the already-bound spine twice is an idempotent success | **met** — §3, and under a lease this door holds (the ordering trap) |
| Neither `work_id` refuses, and explains that a door with no session cannot `claim` | **met** — §4 |
| The three lifecycle pins and the identity pin pass, and their controls still fail | **met** — §6, twelve mutations |
| Protected intent: `_bind_process_to` the only mutator | **met** — M9 RED; `_spine_bind` assigns neither global |
| Protected intent: `_identity_violation` not re-specified | **met** — zero lines changed; it follows the rebind for free |
| Protected intent: fail closed, no ambient resolution | **met** — no cwd read; anchor is `SPINE.parent` or `__file__` |
| Protected intent: both identity roots move together | **met** — one `_bind_process_to` call; `claim` succeeds after |

One item is **outside** the close criteria and unmet: the crew grant (§9).

---

## 12. `run_crew.py`'s stale comment

The handoff asked for a line on this. `ExternalBackend` refuses `--spine` and prints a
permanent warning calling out-of-band binding *"impossible by construction"*:

```
scripts/run_crew.py:1712
  f"no environment, so nothing binds SPINE_FILE/SPINE_SESSION. Its MCP ..."
```

**That premise is now stale, and `spine_bind` is what makes it stale.** An external-backend
crew's door is still launched unbound, but it is no longer *unbindable*: it can bind its own
plan in one call, provided the plan sits inside its own checkout's `.agent-work/` — which is
where `init_work_area.py` puts it. The warning should stop saying "impossible by
construction" and start saying "not bound at launch; call `spine_bind` with the plan's path".

I did not edit it: `scripts/run_crew.py` is outside Allowed Scope, and the same file needs
the `CREW_ALLOWED_TOOLS` entry (§9), so both changes belong in one authorized edit. Note the
irony worth flagging to the Commander — the external backend is precisely the population
Candidate A's §6 objection said `spine_bind` had no legitimate claim to, and it is the
population whose own warning text says the capability is impossible.

---

## Triage candidates

1. **`run_crew.CREW_ALLOWED_TOOLS` + the stale `ExternalBackend` comment** (§9, §12). One
   authorized edit to `scripts/run_crew.py` and one count in `tests/test_crew_launcher.py`.
   Blocking for dispatched crews; not blocking for this gate.
2. **`subTest` can hide a raising test body under pytest.** Measured on my own file: four
   tests reported PASSED while their bodies raised `AttributeError` against a function that
   did not exist. Any `subTest` in this repo's suites is a potentially-vacuous assertion. A
   repo-wide grep plus either `pytest-subtests` or a lint rule would settle it. This is a
   *measurement-integrity* defect, which is the class this epic cares most about.
3. **`_is_stale` in a binding decision inherits #600.** The identity-held refusal measures
   ownership in time as well as identity; `checklist_engine.py` already records that as a
   known defect with #600 against it. Correct today, inherits #600 tomorrow. Recorded in
   IDENTITY_TRADE.md §7 rather than hidden.
4. **`tests/test_mcp_spine_server.py`'s surface assertions are structurally fragile.** I
   narrowed two hand copies into one constant (§10), but the constant is still a hand copy
   of `LIFECYCLE_TOOL_NAMES` rather than a read of it. The suite is subprocess-only by
   design, so tying it to the module would need a deliberate choice.
5. **`map/INDEX.md` is stale repo-wide** (§9). Pre-existing; the handoff already records the
   map as `DEGRADED-UNPARSEABLE`.

---

## Map Impact

The map is `DEGRADED-UNPARSEABLE` repo-wide (`map/ids.jsonl` tracked and 0 bytes), so these
are candidates for reconcile, not map edits.

- **Capability `door-binding`** — how the door decides which spine it drives. Now has three
  moments, not two: launch, mint, bind. Count still one at a time.
- **New structural entries** — `_spine_bind`, `_own_checkout_for_binding`,
  `_checkout_containing`, `_derivable_work_id`, `_unusable_spine_reason`,
  `_THE_CLI_IS_PER_CALL` in `scripts/mcp_spine_server.py`; `session_id_for` in
  `scripts/spine_lifecycle.py`.
- **Changed signature** — `_rebind_refusal(acting_tool: str = "spine_open")`.
- **New constraint: `constraint:one-checkout-work-area-per-process`.** The replacement for
  "one file per process". Enforced by `_own_checkout_for_binding` plus `_resolve_confined`
  plus the cross-checkout refusal. Measured reach 1014 against 6102.
- **`constraint:ast-pin-on-identity-assignment`** — unchanged and re-verified (M9).
- **`decision:isolation-not-fencing`** — **settled** by this gate: the property is named in
  the tool description, the module docstring, and IDENTITY_TRADE.md §7, with the reach delta
  as a number and a test that goes red under the wrong root.
- **`decision:one-spine-per-process-stands`** — upheld, not touched.
- **`decision:bind-on-open-over-new-verb`** — extended by the same logic to a third moment.
- **Tombstone worth recording:** `_primary_checkout_for_lifecycle()` as a *binding* root is
  a documented dead end. It is correct for `spine_open` and wrong here by 6x. The module
  docstring says "do not simplify them into one helper" for exactly this reason.
- **`IDENTITY_TRADE.md` §2's confinement sentence is amended, not deleted** — §7 records
  what replaced it. The trade document lives under `.agent-work/archive/`, which is an odd
  home for a live constraint that three test suites cite by full path.

---

## Workflow Feedback

**What the handoff got right, and it is worth naming.** The five-item "most likely to go
wrong" list was worth more than the design document. Four of the five would have cost me
real time (`BINDS_WITHOUT_A_BOUND_SPINE` in particular is invisible until you test the
unbound path end to end), and the fifth — "a green suite is not evidence that reach did not
widen" — is the only reason M3 got caught. A handoff that says *"this specific check has
already been defective once"* is worth more than one that says *"be careful"*.

**The amendment-over-design layering worked but was fragile.** Three documents where the
first overrides the second in three named places, and the second overrides the third, is a
lot of precedence to hold. It worked because the amendment was explicit about *which*
sections it overrode. If it had said only "the design has defects", I would have had to
re-derive them.

**Genuine gaps.**

1. **The engine-drive instruction in `constellation-implementer` directly contradicts my
   dispatch.** The skill's opening section says building the plan and claiming the engine
   lease is my *first command*, ahead of any problem-solving, and that "work the engine never
   saw did not happen". My dispatch forbids exactly that: no `spine.json`, no
   `checklist_engine.py` as a driver, no lease, no `mcp__spine__*`. I followed the dispatch,
   because it is specific, recent, and gives a reason (an agent in this epic corrupted a live
   spine by inheriting context). But a crew member who resolves that conflict the other way
   causes the incident the dispatch exists to prevent. **The skill needs a branch for
   "dispatched with no spine and explicitly told not to author one."** The memory note
   `crew-dispatch-spine-null` covers the case where `SPINE_*` is inherited from the parent;
   my case is `SPINE_*` genuinely absent *and* an explicit prohibition, which is not covered.
2. **`tests/test_mcp_spine_server.py` should have been in Allowed Scope.** It is named in the
   Verification Commands and it *cannot* stay green when a lifecycle tool is added. Two of
   its assertions hand-copy the lifecycle set. Listing the three test files it did list, and
   not this one, made a forced edit look like a breach (§10).
3. **`scripts/run_crew.py`'s `CREW_ALLOWED_TOOLS` was not anticipated anywhere.** The handoff
   named `run_crew.py`'s `--spine` binding as out of scope and its stale comment as worth a
   line, but not the grant tuple — whose own drift-guard test exists precisely to catch a
   door tool that crews cannot call. The Wiring Grep section warns about "shipped-inert" at
   the function level and this is the same hazard at the *fleet* level: a correctly wired
   tool that no dispatched crew is permitted to invoke. Worth adding "does the crew grant
   cover it?" to the wiring check for any future door tool.
4. **The Map Anchors said "there is no map packet, do not go looking"** — which was correct
   and saved time. More handoffs should say that when it is true, instead of leaving a
   Map Anchors section that reads as an instruction to find something.
5. **Numbers in the handoff had drifted, and saying "re-derive it yourself" is what saved
   them.** 52→60 spine-shaped files, 4205→6102 candidates. The *ratios* and the
   active-lease counts held exactly. A handoff that cites a measurement should always say
   whether the number or the ratio is the claim; here the instruction to re-measure made it
   moot, and that instruction should be standard for any cited count.

**Friction I improvised around.** The design document and Candidate A number the refusals
R1–R9, but the amendment adds a tenth (cross-checkout) without renumbering. I numbered mine
R1–R10 in `_spine_bind`'s docstring and noted the correspondence, so a reviewer reading
either document can follow. Worth a convention: when an amendment adds a refusal to a
numbered set, say where it goes in the order.
