# REVIEW_RESULT — g2-review: `spine_bind`

Verdict: BLOCK

**Gate:** `g2-review` (epic-567-door/cmdr-a, lane A of epic #567)
**Worktree:** `/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`
**Branch:** `feat/567-a-spine-identity`
**Diff reviewed:** `git diff 600de020..HEAD -- scripts/ tests/`
**HEAD at review time:** `37b688db` (moved from `70797237` mid-run — see Workflow Feedback)
**Reviewer:** second relaunch. This file replaces a stub a previous instance left.

Two blocking findings, both in the newly added code, both one-line fixes with a
test each. **Everything the reviewer handoff itself named as a blocking condition
passed** — the root mutation goes RED in my hands, the reach-delta negative test
exists and is discriminating, the pins hold with their controls, the argument is
still `spine_file`, the `IDENTITY_TRADE.md` amendment is in the diff, and
`checklist_engine.py` is untouched by this gate. The block is on two defects I
found by attacking, which is what this gate exists for.

---

## Summary of the two blockers

**B1 — the isolation property is FALSE as stated.** `decision:isolation-not-fencing`
claims *"one checkout's work-area tree per process"* in the tool description, the
module docstring, and `IDENTITY_TRADE.md` §7. I bound a spine in a **different
checkout** through a symlink whose parent directory is the door's own work area.
The cross-checkout guard (R6) asks git about `candidate.parent` — the *unresolved*
parent — so a symlink hides the target's real checkout from it while `_resolve_confined`
(R4), which *does* resolve, sees a path inside the boundary and passes it.

**B2 — `spine_bind` kills the door process on a NUL byte in `spine_file`.** A
declared argument on the one tool reachable while nothing is bound raises an
unhandled `ValueError`; `main()` catches only `KeyError`, so the server dies with
exit 1. This is new to this gate — the analogous pre-existing path
(`spine_advance(from_child=<NUL>)`) survives. It violates the gate's own Protected
Intent ("Fail closed. A spine that cannot be identified refuses").

---

## 1. My own root mutation — the second job. RESULT: RED.

The handoff's most serious warning: the implementer reports that its first root
mutation (M3) came back **GREEN**, because every fixture bound a door in a primary
checkout where `--show-toplevel` and `--git-common-dir` agree. I re-ran it.

### M3 — swap `_own_checkout_for_binding` for the wide root the design named

```python
 def _own_checkout_for_binding() -> Path:
-    anchor = SPINE.parent if SPINE is not None else Path(__file__).resolve().parent
-    return _checkout_containing(anchor)
+    # REVIEWER MUTATION M3 -- the wide --git-common-dir root the design named.
+    return _primary_checkout_for_lifecycle()
```

```
$ py -m pytest tests/test_mcp_spine_bind.py tests/test_mcp_lifecycle.py \
      tests/test_mcp_identity.py tests/test_mcp_door_unbound.py \
      tests/test_mcp_spine_server.py -q

FAILED tests/test_mcp_spine_bind.py::ReachDeltaTests::test_the_root_is_show_toplevel_never_git_common_dir
FAILED tests/test_mcp_spine_bind.py::TheRootMustBeTheDoorsOwnWorktreeTests::test_a_spine_in_a_SIBLING_worktree_is_refused
FAILED tests/test_mcp_spine_bind.py::TheRootMustBeTheDoorsOwnWorktreeTests::test_a_spine_in_the_PRIMARY_checkout_is_refused
FAILED tests/test_mcp_spine_bind.py::TheRootMustBeTheDoorsOwnWorktreeTests::test_the_doors_own_worktree_work_area_is_bindable
FAILED tests/test_mcp_spine_bind.py::TheRootMustBeTheDoorsOwnWorktreeTests::test_the_measured_reach_is_the_narrow_set_not_the_wide_one
FAILED tests/test_mcp_spine_bind.py::TheRootMustBeTheDoorsOwnWorktreeTests::test_the_two_roots_genuinely_disagree_here
FAILED tests/test_mcp_spine_bind.py::TwoDoorRoundTripTests::test_door_two_binds_what_door_one_minted_and_drives_it
7 failed, 139 passed, 14 subtests passed in 6.75s
```

The failure message is the right one — the door in a linked worktree drew the
primary checkout's boundary:

```
AssertionError: True is not false : spine_bind refused: REFUSED: this door may only
bind a spine inside its OWN checkout's work area ('/tmp/tmpuvc2p9f6/repo/.agent-work');
spine_file resolves to '/tmp/tmpuvc2p9f6/repo/.worktrees/bind-roundtrip/.agent-work/
bind-roundtrip/spine.json', which is outside.
```

### M3c — the flag swap alone, inside `_checkout_containing`

```python
-    return Path(_git_rev_parse("--show-toplevel", cwd=directory)).resolve()
+    # REVIEWER MUTATION M3c -- the one flag swapped, nothing else.
+    common = Path(_git_rev_parse("--git-common-dir", cwd=directory))
+    if not common.is_absolute():
+        common = directory / common
+    return common.resolve().parent
```

```
FAILED tests/test_mcp_spine_bind.py::TheRootMustBeTheDoorsOwnWorktreeTests::test_a_spine_in_a_SIBLING_worktree_is_refused
FAILED tests/test_mcp_spine_bind.py::TheRootMustBeTheDoorsOwnWorktreeTests::test_a_spine_in_the_PRIMARY_checkout_is_refused
FAILED tests/test_mcp_spine_bind.py::TheRootMustBeTheDoorsOwnWorktreeTests::test_the_doors_own_worktree_work_area_is_bindable
FAILED tests/test_mcp_spine_bind.py::TheRootMustBeTheDoorsOwnWorktreeTests::test_the_measured_reach_is_the_narrow_set_not_the_wide_one
FAILED tests/test_mcp_spine_bind.py::TheRootMustBeTheDoorsOwnWorktreeTests::test_the_two_roots_genuinely_disagree_here
FAILED tests/test_mcp_spine_bind.py::TwoDoorRoundTripTests::test_door_two_binds_what_door_one_minted_and_drives_it
FAILED tests/test_mcp_lifecycle.py::FullStdioRoundTripTests::test_open_drive_close_round_trip_names_branch_commit_and_ready_to_pr
7 failed, 139 passed, 14 subtests passed in 6.75s
```

**The narrowed root is genuinely tested.** Both root mutations go RED, and
`test_the_two_roots_genuinely_disagree_here` — the non-vacuity premise — is among
the failures, which is what proves the fixture reproduces the discriminating
linked-worktree topology rather than a topology where either root would pass.
The implementer's self-report on the most important claim in the gate is **honest
and reproduces**. (It reported "M3 RED — 4 failed"; I get 7 because my mutation
replaces the whole body rather than the anchor, which also takes the two-door
round trip down. Same direction, same conclusion.)

### M4 — is the cross-checkout guard (R6) itself pinned?

```python
-    if candidate_checkout != checkout:
+    if False and candidate_checkout != checkout:  # REVIEWER MUTATION M4
```

```
FAILED tests/test_mcp_spine_bind.py::SiblingWorktreeIsRefusedTests::test_a_nested_checkout_inside_the_work_area_is_refused_by_the_cross_checkout_rule
1 failed, 52 passed in 0.70s
```

R6 is pinned by **exactly one test, covering exactly one spelling** — the direct
path. That single-spelling coverage is what B1 walks through.

Every mutation was applied to `scripts/mcp_spine_server.py` (or
`tests/test_mcp_identity.py`), the named tests run, and the file restored from an
md5-verified `cp` backup. Final integrity check below.

---

## 2. BLOCKING FINDING B1 — the isolation property is false: R6 is defeated by a symlink

### The claim under attack

`_spine_bind`'s own docstring, quoted verbatim:

> **R6 is what makes the isolation claim true rather than aspirational.** R4 is
> lexical, and a checkout can be NESTED under `.agent-work/`, at which point a path
> inside the boundary is still in another repository. So the candidate's OWN
> `--show-toplevel` is asked and compared.

### The mechanism

```python
candidate, escapes = _resolve_confined(raw, join_relative_to=None, bound_dir=work_area)
#   -> escapes is computed on p.resolve(): symlinks ARE followed here
#   -> but `candidate` is returned UNRESOLVED
...
candidate_checkout = _checkout_containing(candidate.parent)   # <-- unresolved parent
if candidate_checkout != checkout:
    return _tool_error(...)                                    # R6
```

R4 resolves and sees a target inside the work area, so it passes. R6 then asks git
about `candidate.parent`, which for a symlink at `<work_area>/link.json` is
`<work_area>` — the door's own checkout — so R6 passes too. The bind then proceeds
and `_bind_process_to` resolves the symlink, so the door ends up driving the spine
in the other checkout.

### The attack, with its actual output

Topology: `repo/` primary checkout; `repo/.worktrees/lane-a/` is the door's own
checkout (door bound to `lane-a/.agent-work/mine/spine.json`); a linked worktree
`git worktree add repo/.worktrees/lane-a/.agent-work/nested`; and a wholly separate
`git init` repo at `lane-a/.agent-work/alien-repo`.

**A13 — nested checkout, DIRECT path. Correctly refused:**

```
[A13 nested checkout under work area (direct path)]
  arg      : '.../lane-a/.agent-work/nested/.agent-work/n/spine.json'
  outcome  : REFUSED (expected REFUSED) OK
  message  : REFUSED: '.../lane-a/.agent-work/nested/.agent-work/n/spine.json' sits
             inside a DIFFERENT checkout ('.../lane-a/.agent-work/nested') than this
             door's own ('.../lane-a'), even though its path is under this door's work
             area -- a checkout nested there is still another repository. One
             checkout's work-area tree per process. Name a spine under that work area,
             or use the CLI, which is per-call by construction.
```

**A14 — the same spine through a symlink. ESCAPED:**

```
[A14 nested checkout via symlink (parent is ours)]
  arg      : '.../lane-a/.agent-work/link-nested.json'
  outcome  : ACCEPTED (expected REFUSED) <<<< MISMATCH
  SPINE now: .../lane-a/.agent-work/nested/.agent-work/n/spine.json
  SESSION  : 'constellation/nested-work'
  message  : {"SPINE_FILE": ".../lane-a/.agent-work/nested/.agent-work/n/spine.json",
              "SPINE_SESSION": "constellation/nested-work", "work_id": "nested-work",
              "already_bound": false,
              "note": "this door now drives that spine; call spine_status to see where it is"}
```

**A15 / A16 — a wholly unrelated repository, direct then symlinked:**

```
[A15 alien repo nested under work area (direct)]
  outcome  : REFUSED (expected REFUSED) OK
  message  : REFUSED: '.../alien-repo/.agent-work/a/spine.json' sits inside a DIFFERENT
             checkout ('.../alien-repo') than this door's own ('.../lane-a') ...

[A16 alien repo nested under work area (via symlink)]
  arg      : '.../lane-a/.agent-work/link-alien.json'
  outcome  : ACCEPTED (expected REFUSED) <<<< MISMATCH
  SPINE now: .../lane-a/.agent-work/alien-repo/.agent-work/a/spine.json
  SESSION  : 'constellation/alien-work'
```

The door is now bound to, and driving, a spine in a repository it knows nothing
about, under an identity that repository dictated. That is the exact sentence
A2 of the amendment was written to make true: *"what an agent still cannot do:
drive a spine in another checkout."*

### The fix, verified by me

One token:

```python
-    candidate_checkout = _checkout_containing(candidate.parent)
+    candidate_checkout = _checkout_containing(candidate.resolve().parent)
```

With it applied, A14 and A16 refuse, the legitimate cases stay accepted, and the
door/identity suites stay green:

```
  ok A1 CONTROL own work area (must ACCEPT)               got=ACCEPTED   want=ACCEPTED
  ok A7 relative path landing inside (cwd=work area)      got=ACCEPTED   want=ACCEPTED
  ok A13 nested checkout under work area (direct path)    got=REFUSED    want=REFUSED
  ok A14 nested checkout via symlink (parent is ours)     got=REFUSED    want=REFUSED
  ok A15 alien repo nested under work area (direct)       got=REFUSED    want=REFUSED
  ok A16 alien repo nested under work area (via symlink)  got=REFUSED    want=REFUSED

$ py -m pytest tests/test_mcp_spine_bind.py tests/test_mcp_lifecycle.py \
      tests/test_mcp_identity.py tests/test_mcp_door_unbound.py -q
116 passed, 10 subtests passed in 4.96s
```

Restored afterwards; md5 verified.

### Why this blocks rather than being a note

- `decision:isolation-not-fencing` is graded `guess/admiral` and its recorded
  settle condition is *"name the property in the design doc and have the reviewer
  attack it."* I am that reviewer, the attack succeeded, and the property as
  written is false. Approving would record
  `constraint:one-checkout-work-area-per-process` in the map, and a section in a
  trade document three test suites cite by path, as an established fact when it is
  not.
- The failure mode is the one the module's own history warns about most loudly.
  `_identity_violation`'s docstring records six guards "each defeated by a shape it
  had not enumerated" and concludes *"enumerating spellings is the defect."* R6
  enumerates one spelling of "which checkout is this path in" and is defeated by a
  second. The lesson was written down in this file and then repeated in the guard
  added beside it.
- `docs/agents/CREW_CONTEXT.md`: *"A round-trip test over the real shipped artifacts
  proves the artifacts are clean — it does not prove the tool is correct. Pair it
  with adversarial fixtures authored to make the tool return a wrong answer."* R6's
  single test uses a cooperative fixture.
- The fix is one token plus one test.

### Honest scoping of the severity

I will not overstate it. **The escape reaches only checkouts nested inside the
door's own `.agent-work/`, and there are zero such checkouts in the live tree:**

```
$ find /home/tommy/projects/constellation-skills -path "*/.agent-work/*" -name ".git" | wc -l
0
```

The escapes with real files behind them — the primary checkout's work area (A3),
a sibling lane's worktree (A4), and both of those reached through symlinks (A11,
A12) — are all correctly refused, because R4 resolves. So this is not a live
cross-lane breach today; it is a guard that does not implement its stated property
and whose one test cannot tell. Exploiting it also requires the agent to create
both the symlink and the nested checkout inside its own work area, which is
self-escalation, not an attack from outside. That is why B1 is "fix the guard and
its test", not "the lane is unsafe".

---

## 3. BLOCKING FINDING B2 — a declared argument kills the door process

`_spine_bind`'s first act on the raw string is `Path(raw).resolve()` (R0, line
1310). A NUL byte makes that raise `ValueError: embedded null byte`. `main()`'s
lifecycle branch catches only `KeyError`:

```python
elif nm in LIFECYCLE_TOOL_NAMES:
    try:
        result = call_lifecycle_tool(nm, call_args)
    except KeyError as exc:
        result = _tool_error(f"tool error: missing or unknown {exc}")
```

so the exception unwinds out of `main()` and the process exits. Driven against a
**real** server process over real JSON-RPC:

```
  healthy call first : {"jsonrpc": "2.0", "id": 1, "result": {"content": [...]}}
  NUL-byte call reply: ''
  !! B5 the door replies rather than dying on a NUL byte in spine_file
  next call -> BrokenPipeError: [Errno 32] Broken pipe
```

Probed across the surface to establish this is new, not inherited:

```
spine_bind(spine_file=<NUL>)                     replied=False exit=1  ValueError: embedded null byte
spine_advance(from_child=<NUL>)  [pre-existing]  replied=True  exit=0
spine_amend(delta obj)  [control]                replied=True  exit=0
spine_bind(spine_file=<5000 chars>)              replied=True  exit=0
spine_open(work_id=<NUL>)                        replied=True  exit=0
```

`spine_advance`'s path survives because `_identity_violation` runs inside
`run_engine`'s `except Exception` net. The lifecycle path has no such net, and
`spine_bind` is the first lifecycle tool to take a caller-supplied filesystem path.

Why it blocks:

- It contradicts this gate's own Protected Intent: *"Fail closed. A spine that
  cannot be identified refuses."* This input does not refuse — it terminates the
  server, and every one of the door's 12 tools is gone for the rest of the session.
- It is on the one tool reachable with **nothing bound**
  (`BINDS_WITHOUT_A_BOUND_SPINE`), so it is reachable at the moment an agent has
  no other way in.
- The module's stated design is that every refusal returns through `_tool_error`
  with a `rejection_class` so it lands in the rejection log. This one produces no
  refusal, no log line, and no reply.
- It is new to this change, measured above rather than assumed.

One-line fix, either shape: widen the R0 resolve to
`except (OSError, ValueError, RuntimeError)` and refuse with the existing
`bad-argument-type` class, or widen `main()`'s lifecycle catch. I did not fix it.

---

## 4. Every other attack — including the ones that correctly refused

Battery A, in a real linked-worktree topology (door in `.worktrees/lane-a`, other
lanes' work in the primary checkout and in `.worktrees/lane-b`). Fixture
non-vacuity asserted first:

```
--show-toplevel    : /tmp/g2rev-.../repo/.worktrees/lane-a
--git-common-dir   : /tmp/g2rev-.../repo
boundary           : /tmp/g2rev-.../repo/.worktrees/lane-a/.agent-work
```

```
  ok A1 CONTROL own work area (must ACCEPT)               got=ACCEPTED   want=ACCEPTED
  ok A2 absolute path outside any checkout                got=REFUSED    want=REFUSED
  ok A3 primary checkout's work area                      got=REFUSED    want=REFUSED
  ok A4 sibling linked worktree                           got=REFUSED    want=REFUSED
  ok A5 ../ traversal (absolute, lands in primary)        got=REFUSED    want=REFUSED
  ok A6 ../ traversal (relative, cwd=work area)           got=REFUSED    want=REFUSED
  ok A7 relative path landing inside (cwd=work area)      got=ACCEPTED   want=ACCEPTED
  -- A8 relative path with cwd OUTSIDE the checkout       got=ACCEPTED   (see note)
  ok A9 trailing slash on a bindable spine                got=ACCEPTED   want=ACCEPTED
  ok A10 trailing slash on an out-of-bounds spine         got=REFUSED    want=REFUSED
  ok A11 symlink in work area -> outside the checkout     got=REFUSED    want=REFUSED
  ok A12 symlink in work area -> sibling worktree         got=REFUSED    want=REFUSED
  ok A13 nested checkout under work area (direct path)    got=REFUSED    want=REFUSED
  !! A14 nested checkout via symlink (parent is ours)     got=ACCEPTED   want=REFUSED   <- B1
  ok A15 alien repo nested under work area (direct)       got=REFUSED    want=REFUSED
  !! A16 alien repo nested under work area (via symlink)  got=ACCEPTED   want=REFUSED   <- B1
  ok A17 the work-area directory itself                   got=REFUSED    want=REFUSED
  ok A18 a directory inside the work area                 got=REFUSED    want=REFUSED
  ok A19 empty file                                       got=REFUSED    want=REFUSED
  ok A20 JSON array []                                    got=REFUSED    want=REFUSED
  ok A21 JSON object with no work_id                      got=REFUSED    want=REFUSED
  ok A22 whitespace-only work_id                          got=REFUSED    want=REFUSED
  ok A23 non-JSON text file                               got=REFUSED    want=REFUSED
  ok A24 nonexistent path inside the boundary             got=REFUSED    want=REFUSED
  ok A25 empty string                                     got=REFUSED    want=REFUSED
  ok A26 whitespace only                                  got=REFUSED    want=REFUSED
  ok A27 missing spine_file                               got=REFUSED    want=REFUSED
  ok A28 non-string int                                   got=REFUSED    want=REFUSED
  ok A29 bool True                                        got=REFUSED    want=REFUSED
  ok A30 None                                             got=REFUSED    want=REFUSED
  ok A31 list                                             got=REFUSED    want=REFUSED
  !! A32 NUL byte in path                                 got=CRASHED ValueError        <- B2
```

Refusal texts, quoted, for the ones that held:

**A2/A3/A4/A5/A6/A10/A11/A12 — containment (R4). The boundary is named:**

```
REFUSED: this door may only bind a spine inside its OWN checkout's work area
('/tmp/.../repo/.worktrees/lane-a/.agent-work'); spine_file resolves to
'/tmp/.../repo/.agent-work/primary/spine.json', which is outside. One checkout's
work-area tree per process: a spine elsewhere -- including a sibling worktree of
this same repository -- belongs to work whose worktrees, hooks and tests this door
knows nothing about, and binding it would make this process the driver of a run it
cannot see. Name a spine under that work area, or use the CLI, which is per-call by
construction.
```

For the symlink cases the message names the **resolved** target, not the link,
which is the correct and more useful text:

```
A11: ... spine_file resolves to '/tmp/.../elsewhere/far/spine.json', which is outside.
A12: ... spine_file resolves to '/tmp/.../repo/.worktrees/lane-b/.agent-work/theirs/spine.json', which is outside.
```

**A17/A18/A24 — the usability ladder, shared with `_unbound_refusal`:**

```
REFUSED: spine_bind was given '.../lane-a/.agent-work', but that path is a directory,
not a spine file -- so there is no spine there to bind. Name a spine file that exists,
or call `spine_open` to mint one.

REFUSED: spine_bind was given '.../shapes/nope.json', but no file exists at that path
-- so there is no spine there to bind. ...
```

**A19/A20/A23 — not a spine:**

```
REFUSED: '.../shapes/empty.json' does not hold a JSON object, so it is not a spine
this door could drive (JSONDecodeError). Name the SPINE_FILE `spine_open` returned,
or call `spine_open` to mint one.

REFUSED: '.../shapes/arr.json' does not hold a JSON object (it holds a list), so it
is not a spine this door could drive. ...
```

**A21/A22 — no derivable identity, and the refusal explains why it matters:**

```
REFUSED: '.../shapes/nowid.json' carries neither `origin.work_id` nor a top-level
`work_id`, so this door cannot derive the session identity that spine is driven under
-- and a door bound with no session cannot `claim` (`checklist_engine.claim` refuses
an empty --session-id), which means it would not be a bound door at all. Every spine
the engine drives carries a `work_id`; a fragment or a hand-written JSON file does
not. Drive that one through the CLI, which takes --session-id per call.
```

Close criterion met exactly as specified, including the whitespace-only `work_id`
case, which is read as absent rather than as an identity.

**Note on A8 (not a finding).** With the door's cwd outside the checkout, a
relative `spine_file` resolves against the process cwd, and one that lands inside
the boundary binds. `_resolve_confined(..., join_relative_to=None)` deliberately
mirrors the engine's own resolution, and containment is checked on the resolved
path, so **cwd cannot produce an escape** — A6 confirms a cwd-relative traversal
out is refused. My "expected REFUSED" was the wrong expectation. It is worth one
line of Commander attention only because the Protected Intent says "never resolve
a binding from the process cwd or any ambient state", and a relative argument does
read the cwd — for naming, never for permission. `run_engine` moves the cwd, but
not around a `spine_bind` call, so there is no live divergence. Observation, not a
blocker.

---

## 5. Identity, leases, idempotency, rebind — battery B

```
  ok B1 origin:None + top-level work_id BINDS
  ok B1 SESSION == constellation/epic-567-door
  ok B1b explicit `origin: null` still binds via top-level work_id
  ok B1c origin.work_id WINS over top-level
  ok B2 an active lease under the derived identity REFUSES
  ok B2 refusal is about IDENTITY (two agents, one session id)
  ok B2 binding did not move
  ok B2b a STALE lease does not block a respawn
  ok B2c a live lease under a DIFFERENT session id does not block
  ok B3 bind the already-bound path is an idempotent SUCCESS
  ok B3 payload says already_bound=true
  ok B3b same path while holding a lease is still idempotent SUCCESS
  ok B3c a DIFFERENT path while holding a lease is REFUSED
  ok B3c refusal is _rebind_refusal and names spine_bind to retry
  ok B3c binding did not move
  ok B3d trailing-slash spelling of the bound path is a no-op success
  ok B3e relative spelling of the bound path is a no-op success
```

**The session derivation — the correction the whole gate turns on.** Measured, not
read. A spine with `origin = None` and a top-level `work_id`:

```
  fixture origin = None  top-level work_id = 'epic-567-door'
  -> isError=False  {"SPINE_FILE": ".../admiral/spine.json",
                     "SPINE_SESSION": "constellation/epic-567-door",
                     "work_id": "epic-567-door", "already_bound": false, ...}
```

It binds, and the session is the spine's own. An explicit `"origin": null` in the
JSON (not merely an absent key) also binds. `origin.work_id` still wins where
present. So both of the mission's named cases —
`.agent-work/epic-567-door/spine.json` and `IMPLEMENTER_PLAN.json`, both
`origin: None` — are served. This is the criterion the handoff said the gate turns
on, and it holds.

**Active lease held elsewhere under the derived identity — refused, and the
refusal is about identity:**

```
REFUSED: '.../held/spine.json' is under an active lease held as
'constellation/held-work', and that is the very identity this bind would take (it is
derived from the spine's own work id, never supplied). Two processes under one session
id are indistinguishable to the engine, so this bind would put two agents on one
lease. Whoever holds it must release it first (`spine_lease` with action 'release'),
or its lease must go stale.
```

That is the correct answer to lane G's live incident, and it is scoped to the
identity rather than to any active lease — verified in both directions (B2c: an
unrelated session's live lease does not block; B2b: a stale lease does not block a
genuine respawn).

**Ordering trap — R0 before `_rebind_refusal` — verified as the handoff specifies.**
Binding the already-bound path **while this door holds an active lease on it**
succeeds as a no-op (B3b), and binding a *different* path in the same state is
refused (B3c) with the binding demonstrably unmoved:

```
REFUSED: this door still holds an active lease on '.../leased/spine.json' as
'constellation/leased-work', and one door drives one spine at a time. Rebinding this
door now would leave that lease held by nobody. Release it first (`spine_lease` with
action 'release'), then call `spine_bind` again.
```

Note the refusal correctly says `spine_bind`, not `spine_open` — the
`acting_tool` parameter is wired.

---

## 6. Can a pass-through be pointed at a different spine after a `spine_bind`?

**No.** `_identity_violation` is byte-identical to its pre-gate version (AST
comparison of the function source at `600de020` vs `HEAD`), and it follows the
rebind for free because it compares against `SPINE` at call time. I bound the door
to spine *B* with `spine_bind`, then tried to reach spine *A*.

Every spelling the engine's parser actually accepts is refused:

```
  --fi= before verb (redirect)     -> REFUSED: ... resolves --file to '.../mine/spine.json', not the bound '.../victim/spine.json'
  --f= before verb (redirect)      -> REFUSED: ...
  --fil before verb (redirect)     -> REFUSED: ...
  --file before verb, outside repo -> REFUSED: ...
  claim --session-i= abbrev        -> REFUSED: ... resolves --session-id to 'constellation/attacker', not the bound session 'constellation/victim-work'
  claim --s= abbrev                -> REFUSED: ...
  amend --delta OUTSIDE            -> REFUSED: --delta names a delta file INSIDE the bound spine's own directory ...
  amend --delt= abbreviation       -> REFUSED: ...
  amend --de= abbreviation         -> REFUSED: ...
  control: plain current           -> not refused
  control: amend --delta INSIDE    -> not refused
```

**A correction to my own first pass, recorded because it nearly became a false
finding.** My first battery reported the `--file X` / `--file=X` / `--fil X` /
`--fi=X` forms appended *after* the verb as "not refused". They are not a bypass —
`--file` is a global option on the top-level parser, so an occurrence after the
subcommand is not a `--file` at all. The engine's own parser rejects the argv
before anything runs:

```
append --file              SystemExit(2) :: error: unrecognized arguments: --file /.../mine/spine.json
append --file= one token   SystemExit(2) :: error: unrecognized arguments: --file=/.../mine/spine.json
append --fil               SystemExit(2) :: error: unrecognized arguments: --fil /.../mine/spine.json
```

and `run_engine` confirms end to end that the engine never acts:

```
run_engine('current','--file',<other spine>) code= 2
  stderr= -: error: unrecognized arguments: --file /.../mine/spine.json
SPINE still: /.../victim/spine.json
```

`_identity_violation` returning `None` on a `SystemExit` is its documented and
correct behaviour ("malformed argv -- the real main() owns that message"). Fail-closed
holds; my first harness built an argv shape `run_engine` never builds.

Through the real tool surface, the only declared property that carries a path
(`spine_advance.from_child`) is confined after the rebind, to the **new** bound
spine's directory:

```
REFUSED: --from-child names a child checklist INSIDE the bound spine's own directory
('.../victim'); this call resolves it to '.../far/child.json', which is outside. The
child's `consolidation` is attached to the bound spine as a review-result, and a
review-result is what closes an artifact postcondition -- so a path outside the
binding would let any JSON file carrying a `consolidation` key close a gate. ...
```

Full declared-property inventory of all 12 tools, dumped from `module.TOOLS`, to
confirm no second path argument appeared:

```
  spine_status           []
  spine_lease            ['action', 'claimed_by', 'force', 'reason', 'worktree']
  spine_start            ['task_id']
  spine_advance          ['from_child', 'mechanical', 'task_id', 'why']
  spine_evidence         ['action', 'authority', 'condition_id', 'evidence_ref', 'evidence_type', 'fields', 'force', 'note', 'reason', 'task_id', 'which']
  spine_halt             ['action', 'authority', 'blocker', 'next_action', 'note', 'reason', 'task_id']
  spine_survey_result    ['action', 'finding', 'override_reason', 'result', 'summary', 'task_id', 'verdict']
  spine_capture          ['action', 'from', 'imperative', 'statement', 'task_id', 'title']
  spine_amend            ['authority', 'delta', 'reason']
  spine_open             ['base', 'spec', 'work_id']
  spine_bind             ['spine_file']
  spine_close            []
```

**The argument is named `spine_file`.** Not renamed to `work_file`, `plan_path`, or
anything else. The forbidden dishonest fix was not taken.

---

## 7. The pins, and their positive controls

I ran each pin and planted its regression on the **real** source rather than
trusting the control's own hand-written fixture.

| pin | state | control checked how |
|---|---|---|
| `test_mcp_lifecycle.py:135` `ALLOWED` | green | M7 below — the pin goes RED on a real mutate-then-return |
| `test_mcp_lifecycle.py:194` `_spine_open` source | green | `_spine_open` is **byte-identical** to its pre-gate version |
| `test_mcp_lifecycle.py:563` `OneBinderPinTests` | green | M9 below — RED on a second assignment site in `_spine_bind` |
| `test_mcp_identity.py:817` identity-arg | green | M6 and M11 below |

### The allow-list widening is honest (M7)

Planted in the **real** `call_lifecycle_tool`, on the `spine_bind` route:

```python
    if name == "spine_bind":
        out = _spine_bind(args)  # REVIEWER MUTATION M7
        out["content"][0]["text"] += "leak"
        return out
```

```
tests/.../test_call_lifecycle_tool_can_only_produce_content_two_ways FAILED
tests/.../test_the_lifecycle_choke_point_pin_can_fail                PASSED
AssertionError: Lists differ: [] != ['line 1481: out']
```

**The pin still forbids the shape with `_spine_bind` in the allow-list.** I accept
the handoff's argument: the pin bans *how* `call_lifecycle_tool` may produce
content (only by delegating to a named top-level dispatch function), and a third
named function preserves that property exactly. This is an allow-list widened, not
a ban loosened, and M7 is the measurement rather than the argument.

One observation on the control itself: `test_the_lifecycle_choke_point_pin_can_fail`
reimplements the detector loop over a hand-written source string, which is the
same anti-pattern amendment A3 item 3 forced the implementer to fix in
`test_mcp_identity.py` — and it is insensitive to `ALLOWED` (it plants
`return out`, an `ast.Name`, which is flagged whatever the set contains). So the
control does not control for the widening; M7 is what does. Not blocking — the pin
demonstrably catches the real regression — but worth the same extraction A3
mandated next door. Triage candidate.

### The binder pin (M9)

A second, quieter identity site inside `_spine_bind`:

```
tests/.../OneBinderPinTests::test_spine_and_session_are_assigned_only_at_module_scope_and_by_the_one_binder FAILED
tests/.../SpineBindIsWiredTests::test_the_dispatch_calls_the_one_binder_and_assigns_nothing_itself         FAILED

AssertionError: Items in the second set but not the first: '_spine_bind' : SESSION is
assigned somewhere other than module scope and _bind_process_to: ['_spine_bind'].
```

**The new dispatch function assigns neither `SPINE` nor `SESSION`** — confirmed by
the pin, by the bind suite's own AST test, and by `_bind_process_to` being
byte-identical to its pre-gate version. Both identity roots move together in one
call, and B1's `claim` succeeding in the round trip is the behavioural proof that
`SESSION` moved and not only `SPINE`.

### The identity-arg exemption is keyed on the PAIR (M6), and the detector is genuinely shared (M11)

M6 — key the exemption on the tool alone:

```python
+        if tool["name"] in binds_this_door:  # REVIEWER MUTATION M6 -- tool-wide skip
+            continue
```

```
FAILED tests/.../test_the_exemption_is_keyed_on_tool_and_property_not_on_the_tool
  + [] : a `session_id` argument on `spine_bind` was NOT flagged -- the exemption is
  keyed on the tool rather than on the (tool, property) pair ...
1 failed, 31 passed
```

M11 — blind the shared detector:

```
FAILED tests/.../test_the_exemption_is_keyed_on_tool_and_property_not_on_the_tool
FAILED tests/.../test_the_pin_can_fail
2 failed, 30 passed
```

**Both the pin and its control go down together**, which is only true because A3's
extraction is real: `identity_arg_offenders` is one module-level function, and the
pin, `test_the_pin_can_fail`, and the new keying test all reach it through
`self._offenders`. I confirmed by reading the diff that the control no longer
reimplements the loop, and that it asserts `planted["name"] not in BINDS_THIS_DOOR`
— so it cannot silently plant on an exempt tool. A hypothetical
`spine_bind.session_id` is still an offender, and so is `spine_advance.spine_file`;
both directions are asserted, which is necessary because either alone is
satisfiable by the wrong implementation.

### The `IDENTITY_TRADE.md` amendment exists

```
$ git log --oneline 600de020..HEAD -- ".../commander-f2/IDENTITY_TRADE.md"
0189dc26 feat(567-a): spine_bind -- bind the door to a spine that already exists
```

Same commit as the tool, +134 lines, §7 with subsections: *What changed / What the
property becomes / The reach delta, measured / What still holds it in / Which side
of the trade this takes / What §2's capability loss becomes / Two honest residuals*.
The pairing the pin's failure message demands is satisfied. **Caveat tied to B1:**
§7's "What the property becomes" states the property I broke, so the amendment will
need one correction alongside the R6 fix.

---

## 8. Wiring, scope, and constraints

- **`spine_bind` is in `BINDS_WITHOUT_A_BOUND_SPINE`** (`scripts/mcp_spine_server.py:1852`,
  `{"spine_open", "spine_bind"}`) and reaches its own dispatch when unbound —
  measured, not read: in the round trip an unbound door 2's `spine_bind` returns
  its own refusal/success rather than "no spine is bound", and
  `test_the_exempt_tools_are_genuinely_reachable_when_unbound` closes the
  enumeration from the other side.
- **`call_lifecycle_tool` gains exactly one route** and nothing else.
- **`scripts/checklist_engine.py` is untouched by this gate.** The g2 commits
  (`86109e2f`, `0189dc26`) touch only `scripts/mcp_spine_server.py`,
  `scripts/spine_lifecycle.py`, and five test modules. The engine change in the
  range belongs to gate g3 (#613 atomic save) and is not mine to review.
- **`scripts/hooks/*` untouched.** No new environment variable. No caller-supplied
  session. `_identity_violation` byte-identical.
- **The declared scope deviation is ratified.** `tests/test_mcp_spine_server.py`
  was edited outside the listed Allowed Scope, and the implementer flagged it
  rather than burying it. I agree with its reading: the file is named in the
  handoff's own Verification Commands, two of its assertions hand-copy the
  lifecycle set plus a literal count, and both must move when any lifecycle tool is
  added. The edit is narrowing (two hand copies collapse into one named constant;
  the literal `11` becomes `len(EXPECTED_TOOLS) + len(LIFECYCLE_TOOLS_COVER_NO_VERB)`).
  Not a breach.
- **The added test in `tests/test_mcp_door_unbound.py`** correctly closes the
  coverage hole that adding a name to the local `BINDS_WITHOUT_A_BOUND_SPINE`
  would otherwise open. Good instinct; the two tests are genuinely two-sided.

### The Commander's two edits outside the implementer's fence — reviewed, and correct

`scripts/run_crew.py`'s `CREW_ALLOWED_TOOLS` gains `"mcp__spine__spine_bind"`, and
`tests/test_crew_launcher.py`'s count control moves 11 → 12. Both are right and
both are necessary: without the grant the tool is inert for every dispatched crew,
and the `ExternalBackend` population — whose door is unbound by construction and
which refuses `--spine` — is exactly the population `spine_bind` exists for. The
count control earned its keep here in the way controls are supposed to: the tie
test went green on its own because both sides moved in lockstep, and only the
count stayed red. Leaving the method name saying "nine" is the right call for a
control whose value is being hard to change by accident, and the comment says so.

Both edits are covered by the green suite. No finding.

### The two-door round trip, re-run in my hands

Real processes, real newline-delimited JSON-RPC, throwaway checkout, door 2
launched from the **new worktree** with `SPINE_FILE` and `SPINE_SESSION` absent:

```
### DOOR-1: launched  script=repo/scripts/mcp_spine_server.py
    env: SPINE_FILE=<ABSENT>  SPINE_SESSION=<ABSENT>
  DOOR-1 -> spine_status()
    isError=True  REFUSED: no spine is bound to this door ... Call `spine_bind` with the
                  path to a spine that already exists, or `spine_open` to mint a spine ...
  DOOR-1 -> spine_open(work_id='rev-roundtrip', ...)
    isError=False {"SPINE_FILE": ".../repo/.worktrees/rev-roundtrip/.agent-work/rev-roundtrip/spine.json",
                   "SPINE_SESSION": "constellation/rev-roundtrip", ...}

### DOOR-2: launched  script=repo/.worktrees/rev-roundtrip/scripts/mcp_spine_server.py
    env: SPINE_FILE=<ABSENT>  SPINE_SESSION=<ABSENT>
  DOOR-2 -> spine_status()     isError=True   REFUSED: no spine is bound to this door ...
  DOOR-2 -> spine_bind(...)    isError=False  {..., "already_bound": false, ...}

  == BYTE-IDENTICAL?  SPINE_FILE True   SPINE_SESSION True

  DOOR-2 -> spine_status()                          isError=False  ACTIVE m1 [pending]
  DOOR-2 -> spine_lease(action='claim', ...)         isError=False  claimed lease constellation/rev-roundtrip -> active
  DOOR-2 -> spine_start(task_id='m1')                isError=False  m1 -> in-progress
  DOOR-2 -> spine_evidence(action='attach', ...)     isError=False  attached e-m1-1 (user-decision) to m1
  DOOR-2 -> spine_advance(task_id='m1', ...)         isError=False  m1 -> complete

  == on disk: tasks.m1.status='complete'
              engine_session.session_id='constellation/rev-roundtrip' status='active'

  == idempotency (still holding the lease):  isError=False  "already_bound": true
  == rebind to a DIFFERENT spine while holding the lease:  isError=True  (refused)
  == reach delta, from the same door:                      isError=True  (primary checkout refused)

ROUND TRIP: PASS  (reviewer-run)
```

Bound-by-binding and bound-at-launch are the same thing, and `claim` succeeding
against the engine is the half that proves the session moved and was the spine's
own, not one this door named. The load-bearing claim reproduces.

---

## 9. Full suite, with integrity stamps

```
PRE:
?? .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-review-review-result.md
37b688db469c17373383007582570c3a12e6fda9
7dfd9918ad84811da91083fb24539b49  scripts/mcp_spine_server.py
c627cc53786306eed092693aa38b70d9  tests/test_mcp_identity.py
1ed9ed8334b1fb920d798c36d9688f6b  tests/test_mcp_lifecycle.py

3263 passed, 5 skipped, 1218 subtests passed in 134.11s (0:02:14)

POST:
?? .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-review-review-result.md
7dfd9918ad84811da91083fb24539b49  scripts/mcp_spine_server.py
```

Zero failures, so no failure distribution to derive. For completeness, the
mechanical derivation on an empty set:

```
$ py -m pytest tests/ -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
(no output)
```

Note the two `test_crew_launcher.py` failures the implementer reported as its stop
condition (`11 != 12`) are **gone**, resolved by the Commander's grant commit
`70797237`, not by anything of mine.

**Working-tree integrity.** `scripts/mcp_spine_server.py` md5 `7dfd9918…` equals
`git show HEAD:scripts/mcp_spine_server.py | md5sum` exactly. The only entry in
`git status --short` is this result file. Every mutation I applied was restored
from an md5-verified backup and the restore confirmed before the next step. Nothing
of mine is in the tree.

---

## 10. Fowler / refactoring pass

Recorded and rail-verified:

```
$ py verify_fowler_pass.py .../fowler_pass_g2.json
fowler pass ok: smells=12,
  flagged=['large-class', 'duplicated-code', 'shotgun-surgery', 'divergent-change',
           'comments-as-deodorant'],
  overridden=['long-method', 'feature-envy']
exit=0
```

- **comments-as-deodorant — flagged, and it is B1.** The strongest claim in the
  diff lives only in prose. `_spine_bind`'s docstring says "R6 is what makes the
  isolation claim true rather than aspirational"; measured, R6 does not. Same in
  `_own_checkout_for_binding`, the tool description, and `IDENTITY_TRADE.md` §7.
  This is precisely what `docs/agents/CREW_CONTEXT.md` warns about: *"Assert against
  behaviour, never against text that describes it."* The comment volume itself is
  house style and not a defect.
- **shotgun-surgery — flagged.** One new door tool required seven coordinated
  edits, and it bit: the crew grant was missed by both handoffs and caught only by
  a hand-maintained count. CREW_CONTEXT's *"Define a guard by its consumer's
  behaviour, not by a hand-maintained list"* names this exactly.
- **large-class / divergent-change — flagged as observations.** The door is 1761 →
  2188 lines and now answers two different "where am I" questions with three root
  helpers. The mitigation chosen (name both roots, name the question each answers,
  share the one git call via `_checkout_containing`) is the right one short of
  splitting the module.
- **duplicated-code — flagged, minor.** The anchor expression
  `SPINE.parent if SPINE is not None else Path(__file__).resolve().parent` is now
  written twice verbatim (`:920`, `:985`).
- **long-method — overridden.** `_spine_bind`'s ten-guard, ~100-line body is a
  consequence of the handoff's mandated refusal voice (each refusal names its own
  problem and remedy, carries its own `rejection_class`, is independently
  reachable). The table-driven refactor would force one generic message shape,
  which is what that constraint exists to prevent.
- **feature-envy — overridden.** `_spine_bind` reaches three private
  `checklist_engine` members for "is this identity live"; the handoff forbids the
  alternative outright ("Do not define a second notion of any of these"). Reaching
  across the seam is the lesser evil the repo has chosen. The underscore reach is
  itself the marker that the engine owes a public accessor — triage candidate.
- absent: data-clumps, primitive-obsession, long-parameter-list, message-chains,
  speculative-generality.

---

## 11. Map Impact — verified against the diff

The implementer's Map Impact notes are accurate and complete, with one required
correction.

- Capability `door-binding` now has three moments (launch, mint, bind), count
  still one at a time — matches the code and the `_rebind_refusal` behaviour I
  measured.
- New structural entries, changed `_rebind_refusal` signature, and the
  `_primary_checkout_for_lifecycle`-as-binding-root tombstone: all correct, all
  present in the diff.
- **`constraint:one-checkout-work-area-per-process` must NOT be recorded as
  established until B1 is fixed.** The constraint as written is false; A14/A16 are
  the counterexample. This is the one materially wrong graph claim and is part of
  the block.
- **`decision:isolation-not-fencing` is NOT settled by this gate.** Its settle
  condition is "name the property and have the reviewer attack it". The property
  was named — good — and the attack found it false. It settles when the property
  and the code agree.
- Everything else (`decision:one-spine-per-process-stands` upheld,
  `decision:bind-on-open-over-new-verb` extended,
  `constraint:ast-pin-on-identity-assignment` re-verified via M9) is right.

---

## 12. What must change to clear this block

1. `_checkout_containing(candidate.resolve().parent)` in `_spine_bind`'s R6, plus a
   test that binds a nested checkout **through a symlink** and asserts refusal.
   Verified working above: closes A14/A16, keeps 116 door/identity tests green.
2. Catch `ValueError` (or `(OSError, ValueError, RuntimeError)`) around
   `_spine_bind`'s path resolution and refuse through `_tool_error` with the
   existing `bad-argument-type` class, plus a test that a NUL byte in `spine_file`
   returns a refusal and leaves the door alive.
3. Correct `IDENTITY_TRADE.md` §7's property statement and the tool description /
   `_own_checkout_for_binding` docstring to match what the fixed code does.

Not blocking, offered as observations: extract the lifecycle choke-point control's
detector the way A3 mandated next door; the duplicated anchor expression; the
cwd-relative note in §4.

## Triage candidates (no issues filed — `decision:no-issue-filing`)

1. **`main()` catches only `KeyError` around the whole tool surface.** B2 is one
   instance; the shape is general — any unhandled exception in a lifecycle dispatch
   kills the door. A broad `except Exception` returning through `_tool_error` would
   make the whole surface fail-closed instead of one call site at a time.
2. **The lifecycle choke-point positive control reimplements its detector inline**
   (`tests/test_mcp_lifecycle.py:170-190`) and is insensitive to `ALLOWED`. Same
   defect A3 item 3 fixed in `test_mcp_identity.py`; fix it the same way.
3. **`checklist_engine` owes a public "is this lease live" accessor.** Three
   private members (`_active_lease`, `_is_stale`, `load_config`) are now reached
   from the door.
4. **Adding one door tool touches seven places, two of them hand copies.**
   Derive `BINDS_WITHOUT_A_BOUND_SPINE` and the lifecycle set in tests from the
   module, and add "does the crew grant cover it?" to the wiring check for any
   future door tool.
5. **`subTest` can hide a raising test body under this repo's pytest config.**
   The implementer measured four of its own tests reporting PASSED while their
   bodies raised `AttributeError`. A measurement-integrity defect, repo-wide; I did
   not re-derive it but it is the class this epic cares most about.
6. **`IDENTITY_TRADE.md` lives under `.agent-work/archive/`** while three live test
   suites cite it by full path. The implementer flagged this; agreed.
7. **`_is_stale` in a binding decision inherits #600.** Recorded in §7 rather than
   hidden; agreed, correct today.
8. **`mcp_spine_server.py` at 2188 lines with three root derivations** (Fowler
   large-class / divergent-change).

---

## Workflow Feedback

**The handoff's single most valuable line was the one warning that a green suite is
not evidence.** It is the reason the implementer caught M3's green, and the reason
I did not stop at "the suite passes". A handoff that says *"this specific check has
already been defective once"* is worth more than one that says "be careful". Keep
doing this.

**The implementer's self-report was honest against its own interest, and it should
be said plainly.** It volunteered that its first root mutation came back GREEN and
that its entire response to the critic's worst finding was structurally untestable
until it built a new topology. I re-ran it and it reproduces. Everything else I
spot-checked in that result also reproduced. Nothing in it was overstated.

**Three genuine gaps in my dispatch.**

1. **My dispatch and the `constellation-reviewer` skill directly contradict each
   other, and I had to choose.** The skill's opening section says building a survey
   and claiming the engine lease is my *first command*, ahead of any verification,
   and that "work the engine never saw did not happen" — a survey driven to a
   consolidated verdict is described as the deliverable of a Reviewer run. My
   dispatch forbids exactly that: no checklist, no lease, no `mcp__spine__*`, and
   the `REVIEW_RESULT` write is the delivery. I followed the dispatch, because it is
   specific, recent, and gives its reason (an agent in this epic corrupted a live
   spine by inheriting context) — and because nothing was bound in my environment,
   so there was no spine to drive. But a crew member who resolves this the other way
   causes the incident the dispatch exists to prevent. **The skill needs a branch
   for "dispatched with no spine and explicitly told not to author one."** The
   memory note `crew-dispatch-spine-null` covers inherited `SPINE_*`; my case is
   `SPINE_*` genuinely absent *plus* an explicit prohibition, which is not covered.
   This is the second consecutive crew member to report this same conflict — the g2
   implementer's Workflow Feedback item 1 is the same finding.
2. **"Re-run that mutation yourself" and "mutate a copy, never the tracked file"
   are in tension, and I was caught in it.** My dispatch told me to replace the
   root derivation and run the suite. The only way the suite sees a mutation is if
   the file the suite imports carries it, so I mutated `scripts/mcp_spine_server.py`
   in place, with an md5-verified `cp` backup and a restore verified after each
   step. **Mid-run, the Commander polled the worktree, found my `REVIEWER MUTATION
   M3c` in `git status`, concluded the reviewer had died, restored the file under
   me, and committed `ff423924` recording it as an incident plus `b4489d79` ruling
   "mutate a copy, never the tracked file."** I was alive; the window it caught was
   between my mutate-and-test call and my restore call. No measurement of mine was
   corrupted — I overwrite from the pristine backup before each subsequent
   mutation, and every md5 check matched — and its independently-run M3 produced 7
   failures, identical to mine. But the incident record's premise about a dead
   reviewer is wrong, and the near-miss is real. **Two fixes, both cheap:** (a) the
   handoff should say to run mutations against a **copied checkout** (`cp -r` the
   repo, or `git worktree add` a scratch tree) so the tracked file is never touched
   — which is what the Commander's new ruling implies and what I would do next time;
   and (b) restore in the **same** tool call that mutates, never the next one, so no
   observable window exists. I recommend the handoff template carry both.
3. **Two reviewer instances were live on the same deliverable path.** I found a
   `Verdict: PENDING` stub at
   `crew-handoffs/g2-review-review-result.md`, written at 00:32 during my run,
   whose header says "Reviewer: relaunch (the previous g2 reviewer died mid-mutation)".
   I overwrote it, since the write is the delivery and a `PENDING` verdict is not a
   deliverable. But relaunching a reviewer onto a fixed output path with no liveness
   check means the two runs race, and the loser's evidence is lost silently. Worth a
   convention: either a per-attempt filename that the Commander consolidates, or a
   liveness probe before relaunch. Related: HEAD moved three times during my review
   (`70797237` → `ff423924` → `b4489d79` → `37b688db`). None of them touched
   `scripts/` or `tests/` after `70797237`, which I verified rather than assumed
   (`git diff --stat 70797237..37b688db -- scripts/ tests/` is empty), so my
   measurements stand — but a reviewer should not have to check that mid-run.

**Friction I improvised around.** My first pass at the pass-through redirect attack
built argv as `[verb, "--file", X]` rather than `run_engine`'s
`["--file", SPINE, verb, ...]`, and every case came back "not refused" — which
reads exactly like six defeated guards until you check the parser. It was my error,
not the code's, and I only caught it because the *controls* also came back "not
refused", which is impossible for a working guard. **A non-vacuity control on an
attack harness is what saved that finding from being false**, and it is worth
stating as a rule for this kind of review: every attack battery needs a case that
must be *accepted*, or a harness bug reads as a vulnerability. The handoff asked me
to try `--file=X` / `--fil X` / `--fi=X`, and it would have helped to also say
where in the argv `run_engine` puts `--file`, since post-verb spellings are
rejected by the engine's own parser rather than by the guard.

**One handoff field that was exactly right:** "Failures confined to
`tests/test_checklist_engine*.py` are probably the parallel g3 crew's, not g2's —
say so rather than attributing them." I had no failures to attribute, but the
instruction to check *which commits* touched `checklist_engine.py` rather than
inferring from the diff range is what let me confirm the scope constraint cleanly.
Note for the Commander: the g3 engine change is committed under
`fe2eb504 plan(567-a): act on the cold critic's five blocking findings`, a
Commander plan commit, not under a g3 implement commit. Two crews on one branch
makes provenance hard to read from `git log`; per-gate commit prefixes would fix it.

---
---

# APPENDIX R2 — independent second-pass confirmation

Verdict: BLOCK

**Reviewer:** a second relaunched g2 reviewer, dispatched because "a previous
reviewer on this gate died mid-run and produced no verdict." **Two reviewer
instances were live on this one deliverable path at the same time.** I wrote the
`Verdict: PENDING` skeleton at the top of this file; the instance above overwrote
it with the review that now precedes this appendix. I found that review already
here, complete and carrying `Verdict: BLOCK`. **I did not clobber it.** Destroying
a finished review to substitute my own would have lost real evidence, and its
verdict is the one I independently reached. So this is an appendix, not a
replacement.

**Everything below was measured in my own hands, before I read the review above
past its two blocker headings.** Where we agree, that agreement is two independent
reproductions, not one report copied.

**Attribution of my measurements.** Every number here is against the committed
code, `md5 7dfd9918ad84811da91083fb24539b49` for `scripts/mcp_spine_server.py`,
which is byte-identical at `37b688db` and at `e5957b76` (HEAD when I finished).

## R2.0 — my safety posture, since a predecessor's violation is why I exist

**I never wrote to a tracked file.** Every mutation experiment ran against a
MIRROR — `scripts/` and `tests/` copied to a scratch directory outside the repo,
with the one `IDENTITY_TRADE.md` the identity suite reads by absolute path. The
mirror's baseline is 121 passed, and it is restored from a pristine snapshot before
each mutation and re-verified after the last one. Attack harnesses load the door
module by path, which reads the file and never writes it.

## R2.1 — the two blockers, independently reproduced

### B1 — CONFIRMED, and I can add where its edge is

A **file symlink** placed directly in the door's own `<checkout>/.agent-work/`,
whose target is a spine inside a **nested different checkout**, binds. The door
then wrote a live lease into the other checkout's spine file.

```
door's checkout      : <tmp>/repo/.worktrees/lane-a
work area (boundary) : <tmp>/repo/.worktrees/lane-a/.agent-work
nested CHECKOUT      : <tmp>/repo/.worktrees/lane-a/.agent-work/nested-repo
victim spine         : <tmp>/.../nested-repo/.agent-work/victim/spine.json

symlink              : <tmp>/.../lane-a/.agent-work/victim-link.json
  -> resolve()       : <tmp>/.../nested-repo/.agent-work/victim/spine.json
                       inside boundary? True          <- R4 passes (it resolves)
  -> candidate.parent as R6 sees it (UNRESOLVED):
                       <tmp>/.../lane-a/.agent-work
  -> git --show-toplevel from that dir  = <tmp>/repo/.worktrees/lane-a   <- OURS
  -> git --show-toplevel from the TARGET's dir
                                        = <tmp>/.../nested-repo          <- theirs

[B1 ATTACK] isError=False
  {"SPINE_FILE": "<tmp>/.../nested-repo/.agent-work/victim/spine.json",
   "SPINE_SESSION": "constellation/victim-work", "work_id": "victim-work",
   "already_bound": false,
   "note": "this door now drives that spine; call spine_status to see where it is"}

  spine_lease claim -> isError=False
  the NESTED CHECKOUT's spine on disk now carries engine_session=
    {"session_id": "constellation/victim-work", "status": "active",
     "claimed_by": "attacker", ...}
```

Two refinements the review above does not record, both of which sharpen the fix
and its test:

1. **The DIRECTORY-symlink spelling is correctly REFUSED.** Link the *directory*
   and name `spine.json` through it, and `candidate.parent` is the symlink itself
   — a subprocess `cwd` there resolves physically, so git answers with the nested
   checkout and R6 fires:

   ```
   [B1 variant: DIRECTORY symlink in the work area -> nested checkout] isError=True
      candidate.parent as R6 sees it: <tmp>/.../lane-a/.agent-work/victimdir
      REFUSED: '<tmp>/.../victimdir/spine.json' sits inside a DIFFERENT checkout
      ('<tmp>/.../nested-repo') than this door's own ('<tmp>/.../lane-a') ...
   ```

   So the hole is **exactly** the case where the final path component is the
   symlink. A regression test that links a directory would pass against the
   unfixed code and prove nothing. **The test must link the file.**

2. **The direct path to the same spine is refused**, which is the one spelling R6's
   single existing test covers. The guard is not absent; it is out-spelled by one
   token. That is the failure mode `_identity_violation`'s own docstring records
   losing six times, now recorded a seventh — and this time in a docstring that
   asserts the opposite ("R6 is what makes the isolation claim true rather than
   aspirational").

**The one-line fix, verified on my mirror.** `_checkout_containing(candidate.parent)`
→ `_checkout_containing(candidate.resolve().parent)`:

```
[FIXED mirror] B1 symlink attack -> isError=True
  REFUSED: '<tmp>/.../victim-link.json' sits inside a DIFFERENT checkout
  ('<tmp>/.../nested-repo') than this door's own ('<tmp>/.../lane-a') ...
[FIXED mirror] CONTROL legitimate bind                        -> isError=False
[FIXED mirror] CONTROL symlink WITHIN the same checkout       -> isError=False
$ pytest tests/test_mcp_spine_bind.py tests/test_mcp_lifecycle.py \
         tests/test_mcp_identity.py tests/test_mcp_door_unbound.py \
         tests/test_spine_session_id.py -q
121 passed, 10 subtests passed
```

The second control matters: the fix must not refuse a symlink that stays inside
the door's own checkout, and it does not.

### B2 — CONFIRMED, and it is narrower than stated

```
[NUL byte]                        !!!!! RAISED ValueError: embedded null byte
[NUL byte alone]                  !!!!! RAISED ValueError: embedded null byte
[NUL inside a directory component] !!!!! RAISED ValueError: embedded null byte

   the pre-existing analogue, for comparison:
   spine_advance(from_child=NUL) isError=True  REFUSED: --from-child names a child
   checklist INSIDE the bound spine's own directory ... (survives)

   what main() catches around call_lifecycle_tool:
   2162:  result = call_lifecycle_tool(nm, call_args)
   2163:  except KeyError as exc:
```

**Refinement: it only raises on a door that is already BOUND.** The unguarded call
is R0's `Path(raw).resolve()` at `:1310`, which is reached only when
`SPINE is not None`. On a genuinely **unbound** door — the population `spine_bind`
exists for — R0 is skipped and `_resolve_confined`'s own
`except (OSError, ValueError, RuntimeError)` catches it, so the call refuses
cleanly. I confirmed both halves. The fix therefore belongs at R0, and its test
must use a **bound** door or it will pass against the unfixed code.

## R2.2 — the linked-worktree topology, built with real `git worktree`

Primary checkout plus two linked worktrees, door bound in `lane-a`, so the two
candidate roots genuinely disagree:

```
lane-a --show-toplevel  : <tmp>/repo/.worktrees/lane-a
lane-a --git-common-dir : <tmp>/repo/.git   (parent = <tmp>/repo)   <- the REJECTED root
_own_checkout_for_binding()             = <tmp>/repo/.worktrees/lane-a
_primary_checkout_for_lifecycle()       = <tmp>/repo
```

| # | attack | result |
|---|---|---|
| CONTROL | a spine in the door's OWN linked worktree | **ADMITTED** (non-vacuity) |
| A | a spine in a SIBLING linked worktree (`lane-b`) | REFUSED, boundary named |
| B | a spine in the PRIMARY checkout, door in a linked worktree | REFUSED, boundary named |
| C1 | file symlink in the work area → `lane-b`'s spine | REFUSED (R4 resolves) |
| C2 | directory symlink in the work area → `lane-b/.agent-work` | REFUSED |
| C3 | file symlink in the work area → the PRIMARY checkout's spine | REFUSED |
| D1 | a SEPARATE git checkout nested inside the work area, direct path | REFUSED, R6 |
| D2 | a LINKED WORKTREE OF THE SAME REPO nested inside the work area | REFUSED, R6 |
| E1 | absolute path outside any checkout | REFUSED |
| E2 | `../` traversal out of the work area | REFUSED |
| E3 | trailing-slash spelling of a sibling's spine | REFUSED |
| E4 | `.agent-work/../../etc/passwd` | REFUSED |
| F | **HARDLINK** in the work area to `lane-b`'s spine inode | **ADMITTED** — see R2.6 |
| — | mechanical reach count | **1 of 6 candidates admitted** |

D2 is a case neither the implementer nor the review above records: a nested
*linked worktree of the same repository*. `--show-toplevel` answers with the
nested worktree, so R6 refuses it. Correct, and worth a test — it is the nesting
this repo would actually produce, since `.worktrees/` is how every lane is made.

Every refusal named the boundary and offered the CLI escape hatch.

## R2.3 — the identity guard after a rebind: 9 tools × 5 spellings

Rebind live and confirmed first: after `spine_bind`, the engine acts on the new
spine and not the old one (`old engine_session=None`,
`new engine_session=constellation/liveb-work`).

`TOOL_NAMES` is 12; `LIFECYCLE_TOOL_NAMES` is 3; the pass-throughs are exactly the
9 named. Every one of the 9 carries at least one caller-controlled string that
reaches `run_engine`'s `*rest`, so each was injected with `--file=<foreign>`,
`--file`, `--fil=`, `--fi=` and `--f=<foreign>`:

```
[OK ] spine_advance   --file=<foreign>  isError=True  foreign-spine-touched=False
[OK ] spine_advance   --fi=<foreign>    isError=True  foreign-spine-touched=False
...  (40 cases: 8 tools x 5 spellings; spine_status takes no user string)
```

**40 of 40 refused, and the foreign spine was never touched.** I asserted the
side-effect, not only the return code.

`--session-id` is the flag that *is* declared on the subparsers, so it is the real
vector, and it is caught against the **post-rebind** session in every spelling
including the shortest unambiguous ones:

```
[OK ] --session-id <other>    REFUSED: this call resolves --session-id to
                              'constellation/OTHER', not the bound session
                              'constellation/sessd47b-work' ...
[OK ] --session-id=<other>    REFUSED ...
[OK ] --sess=<other>          REFUSED ...
[OK ] --s=<other>             REFUSED ...
[OK ] CONTROL bound session   None (allowed)      <- non-vacuity
```

**Why a post-verb `--file` cannot win, stated mechanically.** `--file` is declared
only on the top-level parser (`checklist_engine.parse_args:3228`) and
`run_engine` builds `argv = ["--file", str(SPINE), verb, *rest]`, so every caller
string lands *after* the verb, where no subparser accepts `--file` in any
spelling:

```
parse_args('--file=<foreign>') -> SystemExit(2) -- the parser refuses it
parse_args('--fi=<foreign>')   -> SystemExit(2) -- the parser refuses it
```

`_identity_violation` returns `None` on `SystemExit` by design, and the engine then
rejects the argv itself, so the tool-level outcome is `isError=True` with the
foreign spine untouched. I record this because a harness that checks only
`_identity_violation`'s return value reads this as six defeated guards when it is
the opposite. **The `ns.file` equality clause is defense in depth against a future
call site that puts caller data before the verb; today nothing can reach it.**

## R2.4 — lease interaction

| case | required | result |
|---|---|---|
| bind a spine ANOTHER session holds an ACTIVE lease on | refuse, on identity | REFUSED — "that is the very identity this bind would take" |
| the same spine, lease STALE | admit (legitimate respawn) | ADMITTED |
| active lease under a DIFFERENT session id | admit (not ours to collide with) | ADMITTED |
| bind twice, SAME path, no lease | idempotent success | `already_bound: true`, nothing changed |
| same spine, trailing-slash spelling | idempotent success | `already_bound: true` |
| same spine, redundant `./` spelling | idempotent success | `already_bound: true` |
| same spine reached by SYMLINK | idempotent success | `already_bound: true` |
| bind a DIFFERENT path while holding our own lease | refuse | REFUSED by `_rebind_refusal`, and it names `spine_bind`, not `spine_open` |
| **bind the SAME path while holding our own lease** | idempotent SUCCESS | `already_bound: true` — **the ordering trap the handoff named is handled** |

The three spelling variants of the idempotent case are the ones that matter: R0
compares on `resolve()`, so a retry that spells its own bound path differently is
still a no-op rather than a rebind refusal.

**One cross-contamination worth recording as a lesson, not a finding.** My first
lease battery reused two spines across cases, and a lease one case claimed made a
later bind refuse on R9 — which reads exactly like "idempotency is broken". It was
my harness. I rebuilt it with a fresh spine per case. Anyone re-running these
attacks should do the same.

## R2.5 — ten mutations, all RED, all on a copy

Baseline mirror: 121 passed. Restored and re-verified afterwards: 121 passed.

| # | mutation | result |
|---|---|---|
| MUT-1 | mutate-then-return planted on the `spine_bind` route in the REAL `call_lifecycle_tool` | **RED** 1 failed |
| MUT-2 | `_spine_bind` assigns `SPINE`/`SESSION` itself instead of calling `_bind_process_to` | **RED** `OneBinderPinTests` |
| MUT-3 | the identity exemption keyed on the TOOL alone, not the `(tool, property)` pair | **RED** `test_the_exemption_is_keyed_on_tool_and_property_not_on_the_tool` |
| MUT-4 | blind the SHARED identity detector | **RED** 2 failed — **the pin AND its control fall together** |
| MUT-5 | `_checkout_containing` uses `--git-common-dir` (the root the DESIGN named) | **RED** 7 failed |
| MUT-6 | delete the cross-checkout refusal (R6) | **RED** 1 failed |
| MUT-7 | delete the top-level `work_id` fallback | **RED** 13 failed |
| MUT-8 | rename the argument to `plan_path` and drop the exemption | **RED** 38 failed |
| MUT-9 | remove `spine_bind` from `BINDS_WITHOUT_A_BOUND_SPINE` | **RED** 4 failed |
| MUT-10 | widen the boundary from `<checkout>/.agent-work` to `<checkout>` | **RED** 6 failed |

**MUT-5 reproduces the Commander's number exactly — 7 failures, including
`TheRootMustBeTheDoorsOwnWorktreeTests::test_the_two_roots_genuinely_disagree_here`.**
That non-vacuity control failing is what proves the fixture reproduces a topology
where the two roots differ, rather than one where either would pass. **I agree with
the Commander's reasoning: the narrowed root is genuinely tested.**

```
FAILED ...::test_a_spine_in_a_SIBLING_worktree_is_refused
FAILED ...::test_a_spine_in_the_PRIMARY_checkout_is_refused
FAILED ...::test_the_doors_own_worktree_work_area_is_bindable
FAILED ...::test_the_measured_reach_is_the_narrow_set_not_the_wide_one
FAILED ...::test_the_two_roots_genuinely_disagree_here
FAILED ...::TwoDoorRoundTripTests::test_door_two_binds_what_door_one_minted_and_drives_it
FAILED tests/test_mcp_lifecycle.py::FullStdioRoundTripTests::test_open_drive_close_round_trip...
```

**MUT-6 is the one that matters for B1.** R6 is pinned by *one* test covering *one*
spelling (`test_a_nested_checkout_inside_the_work_area_is_refused_by_the_cross_checkout_rule`).
A guard with a single-spelling pin is a guard waiting to be out-spelled, and B1 is
that spelling.

**MUT-8 settles the rename question mechanically.** Renaming the argument does not
quietly pass — `test_its_one_argument_is_named_spine_file` fails by name. The
prohibition is enforced, not merely written down.

## R2.6 — a third finding of my own: a HARDLINK is not caught

`os.link(<lane-b's spine>, <own work area>/hardlinked.json)`, then bind the link:

```
[ATTACK F] isError=False
  {"SPINE_FILE": "<tmp>/.../lane-a/.agent-work/hardlinked.json",
   "SPINE_SESSION": "constellation/theirs-work", "work_id": "theirs-work", ...}
  inode(lane-b spine)=6037206  inode(link)=6037206  same=True
```

The door assumes **another lane's session identity** (`constellation/theirs-work`)
derived from another lane's spine content, on a path inside its own boundary. No
`resolve()` can see this: a hardlink has no target to follow.

**I am NOT raising this as a blocker, and the reason is worth recording.** Three
things bound it. The refusals themselves advertise the CLI as the escape hatch
("or use the CLI, which is per-call by construction"), so this boundary was never
an adversarial sandbox against an agent with a shell — and creating a hardlink
needs a shell. `checklist_engine.save` installs by atomic rename since #613, so a
write through the door replaces the link's inode rather than the victim's file.
And R9 still reads the linked *content*, so a victim holding an active lease is
still refused. What is left is an identity-assumption smell, not a write path into
another lane.

**But it does mean the property should be stated as what it is.** "One checkout's
work-area tree per process" is a claim about *paths*, and hardlinks are outside
what any path check can decide. If the property is to survive B1's repair, it
should say so — or say "one checkout's work-area tree per process, up to
filesystem aliases the path cannot distinguish". Triage candidate, not a blocker.

## R2.7 — are the pins honest? My judgement, item by item

**`ALLOWED` gaining one name widens an allow-list without loosening a ban —
agreed, and measured.** The pin forbids a *shape*: a `Return` whose value is not a
`Call` to a name in `ALLOWED`. A third named dispatch function preserves that
exactly, and MUT-1 proves it: a mutate-then-return planted on the **`spine_bind`
route in the real source** is still caught with `_spine_bind` in the allow-list.
The positive control at `:170` is byte-untouched and still fails on a
mutate-then-return, because it plants `return out` — an `ast.Name`, never a
`Call` — which no widening of `ALLOWED` can admit.

*Observation, not a blocker:* the pin's own failure message still reads "some way
other than `_spine_open(args)`/`_spine_close(args)`" and was not updated to name
`_spine_bind`. The message a future author reads now understates the allow-list by
one. And that control reimplements the detector loop inline rather than sharing it
— the exact defect A3 item 3 fixed next door in `test_mcp_identity.py`, left here
because the handoff required the control stay untouched. It happens to stay honest
because it reads `self.ALLOWED`, so the widening *is* felt; the coupling is
accidental rather than designed.

**The module-wide binder pin holds.** `_spine_bind` assigns neither global; it
calls `_bind_process_to`. MUT-2 is RED, so the pin is not vacuous.

**The identity exemption is keyed on the `(tool, property)` PAIR.**
`BINDS_THIS_DOOR = {"spine_bind": ("spine_file",)}`. MUT-3 — re-keying it on the
tool alone — is RED. Both directions are asserted, which matters because either
alone is satisfiable by the wrong implementation.

**The detector is genuinely shared between the pin and its control.** MUT-4 blinds
the module-level `identity_arg_offenders` and **both** the pin and
`test_the_pin_can_fail` fail together. That co-failure is the whole point of A3's
extraction, and it is now a measured fact.

**The argument is still `spine_file`.** Not renamed; MUT-8 shows a rename is caught.

**The `IDENTITY_TRADE.md` amendment is in the diff** — §7, 134 added lines, in the
same change, stating plainly that §2's sentence is now false on purpose and that
the amendment is not human-ratified.

*And this is where B1 bites hardest.* §7's one-line property statement is
"**one checkout's work-area tree per process**", and the tool description and
`_own_checkout_for_binding`'s docstring say the same. The pin's exemption is
justified *by* that property. B1 falsifies it, so the amendment currently records
a narrower reach than the code has. The record must be corrected with the code, or
the exemption rests on a claim that is not true.

## R2.8 — the Commander's two edits outside the implementer's fence

Both correct. Reviewed as part of this gate, as instructed.

```
CREW_ALLOWED_TOOLS mcp entries: 12
door TOOL_NAMES:                12
identical sets? yes  (mcp__spine__ + each of the 12 door tool names)
$ pytest tests/test_crew_launcher.py::CrewGrantTiesToDoorTests -q
2 passed
```

`scripts/run_crew.py` granting `mcp__spine__spine_bind` **restores** the tuple's
own documented invariant — the grant equals the door's surface — rather than
widening it past the door. Without it the tool is inert for exactly the population
it was built for: an `ExternalBackend` crew spawns no process and builds no
environment, so its door is unbound by construction and `spine_bind` is its only
route to its own plan. The comment records that reasoning rather than asserting it.

`tests/test_crew_launcher.py` moving 11 → 12 is a control being **acknowledged**,
not weakened. Its added comment records that the tie test went green on its own
because both sides moved in lockstep, and that only the count assertion went red —
which is precisely the failure a count control exists to catch, written down at the
moment it caught it. The stale method name ("nine") is left alone with a note
saying to read the assertion; I agree, renaming a control is churn against the one
property that makes it valuable.

## R2.9 — the full suite, in my hands

```
$ python3 -m pytest tests/ -q
3263 passed, 5 skipped, 1218 subtests passed in 135.31s (0:02:15)
```

Zero failures, so there is no distribution to derive and nothing to attribute to
the parallel g3 crew. This matches both the Commander's and the review above's
count exactly. The two `test_crew_launcher.py` failures the implementer reported as
its stop condition are gone, resolved by the Commander's grant commit.

`scripts/checklist_engine.py` and `tests/test_checklist_engine_atomic_save.py` are
in the diff range but belong to gate g3; I read them only to confirm this gate did
not touch them. `scripts/hooks/*` is untouched.

## R2.10 — Fowler / refactoring pass

Recorded independently and rail-verified. The record is kept **outside** the repo
so this review leaves no untracked scratch:

```
$ python3 verify_fowler_pass.py .../scratchpad/fowler_g2_reviewer2.json
fowler pass ok: (smells=12,
  flagged=['long-method', 'large-class', 'duplicated-code', 'shotgun-surgery',
           'divergent-change'],
  overridden=['feature-envy', 'primitive-obsession', 'speculative-generality',
              'comments-as-deodorant'])
exit=0
```

The five flagged, in one line each:

- **long-method** — `_spine_bind` is ~195 lines: a 66-line docstring then ten
  refusal blocks. The ladder order is load-bearing, so I would move the ten refusal
  *texts* to module constants the way `_THE_CLI_IS_PER_CALL` already shows, not
  split the function.
- **large-class** — `mcp_spine_server.py` is 2188 lines and carries three distinct
  git-root derivations plus the whole surface.
- **duplicated-code** — the anchor expression
  `SPINE.parent if SPINE is not None else Path(__file__).resolve().parent` is
  verbatim in `_primary_checkout_for_lifecycle:920` and
  `_own_checkout_for_binding:985`: the same fallback choice for two different root
  questions, so a change to it must be made twice. Plus the lifecycle control's
  inlined detector noted in R2.7.
- **shotgun-surgery** — one new door tool required seven edit sites, two of them
  hand copies of module state. The implementer's own stop condition (the crew grant)
  is a direct consequence: the tool shipped inert until a seventh site was found.
- **divergent-change** — the module changes for three unrelated reasons at once;
  the three root derivations are the symptom.

The four overrides each name the standard that wins and why, per the rail. The one
worth surfacing: I overrode **comments-as-deodorant** despite a
comment-dominated diff, because these docstrings carry the measured reach numbers,
the named tombstone, the ordering trap and each entry's falsification condition —
content with no other home, and what told me what to attack. **But B1 is the
bounded counter-example, and it is why the override is bounded rather than blanket:
one of these docstrings asserts a property the code does not have, in confident
prose that invites belief. That hazard is captured as a blocking finding, not as a
smell.**

## R2.11 — the working tree, and one thing in it that is not mine

At the moment I finished:

```
$ git status --short
 M scripts/mcp_spine_server.py
 M tests/test_mcp_spine_bind.py
?? .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-review-review-result.md
```

**The two modified tracked files are NOT mine, and I deliberately left them
alone.** They are an in-flight repair of B1 and B2 by whoever is now fixing this
gate: the diff rewrites `_spine_bind`'s refusal table to add `R2b bad-argument-type
— a string, but no path resolves from it`, changes R6 to ask about "the RESOLVED
path's own checkout", adds a docstring passage crediting the symlink escape, and
adds `ASymlinkCannotHideAnotherCheckoutTests` (+318 lines) to
`tests/test_mcp_spine_bind.py`. Reverting a working agent's uncommitted repair is
exactly the destructive act my dispatch was written to prevent, so I did not touch
it. My own contribution to `git status` is this one untracked result file.

Proof that nothing of mine reached a tracked file: my pristine snapshot of
`scripts/mcp_spine_server.py` is `md5 7dfd9918ad84811da91083fb24539b49`, identical
to `git show 37b688db:` and `git show e5957b76:`. Every mutation ran on the mirror.

## R2.12 — what must change to clear this block

I concur with the three items already listed above, and add the test-shape
requirements my measurements imply:

1. Resolve before R6. The regression test must symlink the **file**, not a
   directory — a directory symlink passes against the unfixed code.
2. Catch the resolution failure at **R0**, and test it on a **bound** door — an
   unbound door already refuses cleanly, so an unbound test passes against the
   unfixed code.
3. Correct the property statement in `IDENTITY_TRADE.md` §7, the tool description,
   and `_own_checkout_for_binding`'s docstring to match the fixed code, and say
   whether filesystem aliases (R2.6) are in or out of the claim.
4. Add the nested-**linked-worktree** case (D2) alongside the nested-repository
   case; that is the nesting this repo actually produces.

## R2.13 — Workflow Feedback (this reviewer)

**Two reviewer instances raced on one deliverable path, and the loser's work is
only in this file because I chose not to clobber.** I wrote a skeleton; the other
instance overwrote it; had I finished first, I would have overwritten a finished
review. Relaunching a reviewer onto a fixed output path with no liveness check is
the defect, and it has now fired twice on this gate — once as "the reviewer died"
(it had not) and once as two live reviewers. **A per-attempt filename the Commander
consolidates would cost nothing.** As it stands, both reviews reached BLOCK on the
same two findings by independent routes, which is more evidence than either alone;
that was luck, not design.

**"Do not redo the Commander's work; judge it" is the best instruction I have been
given, and it needs one more clause.** It saved real time and pointed me at the
gaps. But judging a claim honestly still means reproducing it, and I did reproduce
MUT-5's seven failures — the instruction says "you need not re-run it unless you
doubt it", which reads as permission to accept it. **The clause I would add: any
claim the verdict rests on must be reproduced, doubt or no doubt.** MUT-5 is
exactly such a claim.

**The dispatch's safety rule was specific, actionable, and correct, and it should
be the template.** "Copy the file to a scratch path, mutate the copy, load the
copy" is what I did, and the mirror-plus-pristine-snapshot pattern made ten
mutations cheap and left `git status` clean. The one thing it omitted: the
identity suite reads `IDENTITY_TRADE.md` by absolute path from `ROOT`, so a mirror
of `scripts/` and `tests/` alone reports one spurious failure. **Worth naming in
the template: mirror the two files-by-absolute-path the door suites read.**

**The `constellation-reviewer` skill and my dispatch directly contradict each
other, and this is now the third crew member on this lane to report it.** The
skill's opening says claiming the engine lease is my first command and that "work
the engine never saw did not happen"; my dispatch forbids any spine, lease,
checklist or `mcp__spine__*` call. I followed the dispatch — it is specific,
recent, gives its reason, and my environment had no `SPINE_*` at all, so there was
nothing to drive. I also ran the Fowler pass and its rail as the skill requires,
keeping the record outside the repo so closeout finds no orphan. **The skill needs
a branch for "dispatched with no spine and told not to author one", stating that
the `REVIEW_RESULT` write is the delivery and that the Fowler record goes to
scratch.** Without it, every reviewer on this lane spends part of its run
adjudicating its own instructions.

**A non-vacuity control on the attack harness is what kept me from filing a false
finding, and it should be a stated rule.** My first pass at the pass-through
redirect battery flagged six "successes" because I asserted that
`_identity_violation` must return a refusal, when the real mechanism is the
engine's parser rejecting a post-verb `--file`. The tell was that my **control**
also came back "not refused" — impossible for a working guard. Separately, my first
lease battery cross-contaminated itself with a lease it had claimed two cases
earlier, which read as broken idempotency. **Every attack battery needs a case that
must be ACCEPTED and a fresh fixture per case, or harness bugs read as
vulnerabilities.** The handoff asked for `--fil`/`--fi=` without saying where
`run_engine` puts `--file` in the argv; one sentence there would have saved the
detour.

**The implementer's self-report is honest.** It volunteered that its first root
mutation came back GREEN and that its answer to the critic's worst finding was
structurally untestable until it built a new topology. Everything in it that I
re-measured reproduced, including the reach direction, the census shape, the
ordering trap, and all twelve of its own mutation directions that overlap mine.
Nothing was overstated. It also correctly declined to fix the crew grant it found
broken, and the Commander fixed it — that division worked.

## R2.14 — final `git status --short`, as required

Run as my last act. It grew by one line since R2.11 while I was writing this
appendix — the in-flight repair reached `IDENTITY_TRADE.md`, which is fix item 3.

```
$ git status --short
 M .agent-work/archive/2026-08-12-epic-418-followon-closeout/epic-418-followon/commander-f2/IDENTITY_TRADE.md
 M scripts/mcp_spine_server.py
 M tests/test_mcp_spine_bind.py
?? .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-review-review-result.md
```

**Three modified tracked files, none of them mine.** All three are the live repair
of B1 and B2 by another agent, and the third arriving mid-write is itself evidence
of that: the repair is progressing through the fix list while I type. My only entry
is the untracked result file, which is this deliverable.

I mutated nothing tracked at any point. `scripts/mcp_spine_server.py` as I measured
it is `md5 7dfd9918ad84811da91083fb24539b49`, byte-identical to `git show 37b688db:`
and `git show e5957b76:`; every mutation ran against a mirror outside the repo, and
the mirror was restored and re-verified green afterwards.

**Verdict: BLOCK** — on B1 (the isolation property this gate exists to settle is
false, defeated by a one-token change of spelling) and B2 (a declared argument on
the one tool reachable while unbound kills the door process, against the gate's own
"fail closed" Protected Intent). Both reproduce independently in a second pair of
hands. Everything the reviewer handoff itself named as a blocking condition passed.
