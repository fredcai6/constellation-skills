# IMPLEMENTER_RESULT — g2 rework: clear B1 (symlink defeats R6) and B2 (NUL kills the door)

Return status: complete

**Gate:** `g2-rework` (epic-567-door/cmdr-a, lane A of epic #567)
**Worktree:** `/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`
**Branch:** `feat/567-a-spine-identity`
**HEAD at start:** `1bd7bd42` → moved to `88ad6d36` mid-run (Commander docs/triage; see Workflow Feedback)
**Commits:** `3d172f73` (the fix + tests + prose), `5444c45a` (code-map regeneration), `49bbf42e` (the hardlink qualifier)

Both blockers cleared. The symlink escape was **reproduced against HEAD first**, on a genuine
`git worktree` / `git init` topology, then refused after a one-token fix. The full suite is
green: 3276 passed, 5 skipped, 0 failed.

---

## 1. B1 — the symlink escape, BEFORE the fix

Reproduced with a standalone harness (`scratchpad/repro_b1.py`, not committed — it mutates
nothing and imports the worktree's `scripts/mcp_spine_server.py` as-is). Topology: primary
`repo/`; the door's own checkout is the linked worktree `repo/.worktrees/lane-a`, bound to
`lane-a/.agent-work/mine/spine.json`; a **second linked worktree** (`git worktree add`) nested
at `lane-a/.agent-work/nested`; a **wholly separate repository** (`git init`) at
`lane-a/.agent-work/alien-repo`; and two symlinks whose links sit in the door's own work area.

Against `HEAD = 1bd7bd42`, `md5(scripts/mcp_spine_server.py) = 7dfd9918ad84811da91083fb24539b49`
— byte-identical to the reviewed file:

```
topology     : /tmp/b1repro-ib45et__/repo
door checkout: /tmp/b1repro-ib45et__/repo/.worktrees/lane-a
boundary     : /tmp/b1repro-ib45et__/repo/.worktrees/lane-a/.agent-work

  ok A1  CONTROL own work area (must ACCEPT)    got=ACCEPTED want=ACCEPTED
  ok A13 nested checkout, DIRECT path           got=REFUSED  want=REFUSED
  !! A14 nested checkout VIA SYMLINK            got=ACCEPTED want=REFUSED    <<<< MISMATCH
       SPINE now : /tmp/b1repro-ib45et__/repo/.worktrees/lane-a/.agent-work/nested/.agent-work/n/spine.json
       SESSION   : 'constellation/nested-work'
       payload   : {"SPINE_FILE": ".../nested/.agent-work/n/spine.json",
                    "SPINE_SESSION": "constellation/nested-work", "work_id": "nested-work",
                    "already_bound": false, "note": "this door now drives that spine; ..."}
  ok A15 alien repo, DIRECT path                got=REFUSED  want=REFUSED
  !! A16 alien repo VIA SYMLINK                 got=ACCEPTED want=REFUSED    <<<< MISMATCH
       SPINE now : /tmp/b1repro-ib45et__/repo/.worktrees/lane-a/.agent-work/alien-repo/.agent-work/a/spine.json
       SESSION   : 'constellation/alien-work'

  !! A32 NUL byte in spine_file  -> CRASHED ValueError: embedded null byte   <<<< MISMATCH

MISMATCHES: 3
exit=1
```

The bug is real, and both halves of it. The door bound and took the identity of a spine in a
repository it knows nothing about.

## 2. B1 — the same harness, AFTER the fix

```
  ok A1  CONTROL own work area (must ACCEPT)    got=ACCEPTED want=ACCEPTED
  ok A13 nested checkout, DIRECT path           got=REFUSED  want=REFUSED
  ok A14 nested checkout VIA SYMLINK            got=REFUSED  want=REFUSED
  ok A15 alien repo, DIRECT path                got=REFUSED  want=REFUSED
  ok A16 alien repo VIA SYMLINK                 got=REFUSED  want=REFUSED

  ok A32 NUL byte in spine_file  -> REFUSED
       message   : spine_bind: spine_file is not a usable filesystem path (ValueError: embedded
                   null byte). Pass an absolute path to a spine file that exists -- the
                   SPINE_FILE value `spine_open` returned.

MISMATCHES: 0
exit=0
```

**The fix, one token, exactly as the review's §12 item 1 prescribed:**

```python
-    candidate_checkout = _checkout_containing(candidate.parent)
+    resolved = candidate.resolve()
+    candidate_checkout = _checkout_containing(resolved.parent)
```

The refusal text now names the resolved target rather than the link, matching what R4's own
symlink refusals already did — a refusal that named the link would tell an agent its own work
area is "a different checkout", which is both false and unactionable:

```
REFUSED: '/tmp/quote-.../repo/.worktrees/lane-a/.agent-work/nested/.agent-work/n/spine.json'
sits inside a DIFFERENT checkout ('/tmp/quote-.../repo/.worktrees/lane-a/.agent-work/nested')
than this door's own ('/tmp/quote-.../repo/.worktrees/lane-a'), even though its path is under
this door's work area -- a checkout nested there is still another repository. One checkout's
work-area tree per process. Name a spine under that work area, or use the CLI, which is
per-call by construction.

SPINE unmoved: True  /tmp/quote-.../repo/.worktrees/lane-a/.agent-work/mine/spine.json
```

### The required test

`tests/test_mcp_spine_bind.py::ASymlinkCannotHideAnotherCheckoutTests`, 9 tests, built on the
topology above — a real `git worktree add` nested under the work area, a real `git init` beside
it, real symlinks whose parents are the door's own work area, and a real sibling worktree.
Written **before** the fix and confirmed RED (§5). It asserts more than the outcome:

- the direct and symlinked spellings of one path are refused **by the same guard** — the
  rejection log's class must be `cross-checkout` for both, so a "fix" that made R4 refuse
  symlinks for the wrong reason would not pass;
- the symlink-to-sibling-worktree case is refused by `path-escape`, recording the two guards'
  division of labour rather than assuming it;
- the refusal names the resolved target, the target's checkout, and this door's own checkout,
  with `isError` asserted **first** (a success payload also contains all three paths — without
  that assertion the test would pass on the escape itself);
- two non-vacuity controls: the door's own work area still binds, and a symlink to the **bound**
  spine is still an idempotent no-op (which is what proves resolving in R6 did not break R0);
- a re-measured reach count over all seven spellings — exactly one is bindable;
- a premise test that the fixture is discriminating at all: the nested worktree's own
  `--show-toplevel` answers with itself, the alien repo's with itself, and every link's
  unresolved parent is the door's own work area, which is the directory the defeated guard asked
  git about.

## 3. B2 — a NUL byte returns a refusal and leaves the door alive

The crash, before the fix, from a **real server process** over real JSON-RPC (this is the
pytest failure output of the new test run against unfixed source):

```
AssertionError: no reply to spine_bind; stderr:
Traceback (most recent call last):
  File "/tmp/tmpl8r5k8ii/repo/scripts/mcp_spine_server.py", line 2188, in <module>
    main()
  File ".../mcp_spine_server.py", line 2162, in main
    result = call_lifecycle_tool(nm, call_args)
  File ".../mcp_spine_server.py", line 1479, in call_lifecycle_tool
    return _spine_bind(args)
  File ".../mcp_spine_server.py", line 1310, in _spine_bind
    if SPINE is not None and Path(raw).resolve() == SPINE:
ValueError: embedded null byte
```

**The fix:** a new guard `R2b`, placed **before** R0 — because R0's own `resolve()` is one of the
two lines that raised, and R0 runs only when something is bound, so a guard placed after it
would leave the *unbound* door still dying, and the unbound door is the one `spine_bind` exists
for:

```python
try:
    requested = Path(raw).resolve()
except (OSError, ValueError, RuntimeError) as exc:
    return _tool_error(
        f"spine_bind: spine_file is not a usable filesystem path "
        f"({type(exc).__name__}: {exc}). Pass an absolute path to a spine file that "
        f"exists -- the SPINE_FILE value `spine_open` returned.",
        tool="spine_bind", rejection_class="bad-argument-type",
    )
if SPINE is not None and requested == SPINE:   # R0, now on the already-resolved path
```

`bad-argument-type`, the existing class, as §12 item 2 specified. `OSError` and `RuntimeError`
join it for the same reason the two root resolutions below already catch them: a name too long
and a symlink loop are the same class of answer as a NUL, and each must be a refusal rather
than a dead door.

**Tests, four of them, in two halves.** The half that proves the process survives
(`NulByteDoesNotKillTheDoorTests`, a real subprocess — an in-process call cannot observe
liveness): a healthy call first as a measured baseline, then the NUL call, then
`assertIsNone(door.proc.poll())` **and** a further successful call, asserted both **unbound**
and **bound** (the two routes to the raising line). The half that proves the refusal is a
refusal (`RefusalSetTests`): the message is in the module's voice and the rejection log records
exactly `["bad-argument-type"]`, plus the unbound door refuses and stays unbound.

Post-fix, from the real process: refusal returned, `poll()` is `None`, `spine_status` answers
identically afterwards. The bound variant refuses and then drives `spine_status` successfully.

## 4. B3 — the prose now matches the code, including a limit that survives the fix

Corrected in all four places that stated the property, plus one the review did not name:

1. **`IDENTITY_TRADE.md` §7** — the one-line property, "What still holds it in" item 1 (now says
   the `--show-toplevel` asked for is the *resolved* candidate's), and a new subsection, **"The
   property was false as first shipped — corrected in gate `g2-rework`"**, recording the attack,
   the fix, why the single existing test could not see it, the honest scope of the live
   exposure, and the B2 defect under the same "a guard that kills the server is not fail-closed"
   heading.
2. **`_own_checkout_for_binding`'s docstring** — both halves of the pair are asked of the
   resolved path, and it was false until they were.
3. **The `spine_bind` tool description** — now also states that a nested checkout is refused and
   that the path is judged after resolution, so a symlink is not a way around either refusal.
4. **`_spine_bind`'s docstring** — the refusal table gains `R2b` and R6's line says "the
   resolved path's own checkout"; the R6 paragraph records the symlink defeat and points at the
   new test class.
5. **The module docstring** (`:68-77`), which the review's §2 named as a third claim site and
   §12 did not list — same correction.

**I did not leave the property unqualified, and this is a deliberate deviation from the
literal task.** Mid-run the Commander landed
`.agent-work/567-a/triage-candidates/hardlinks-defeat-path-based-containment.md` and a RETURN
sentence carrying its limit. A hardlink has no target to resolve — it is a second name for one
inode, and both names are equally real — so a hardlink planted inside the door's own
`.agent-work/` onto a nested checkout's spine answers every path-shaped question correctly and
is still a foreign spine. Resolving closes symlinks and nothing path-based closes hardlinks. So
the property as stated in all three claim sites is now **"one checkout's work-area tree per
process, enforced by path"** (commit `49bbf42e`). B3's instruction was that none of them may
claim a property the code does not have; the unqualified one-liner is such a property. I did
**not** attempt inode containment — that is a different mechanism, out of scope, and the triage
candidate's own warning is that adding a third path-shaped check is the failure
`_identity_violation` records six times over.

## 5. The tests were RED first (TDD), and are RED again on a planted regression

Written before the code, run against unfixed source — 7 failures, the exact set:

```
FAILED ...ASymlinkCannotHideAnotherCheckoutTests::test_a_nested_checkout_reached_THROUGH_A_SYMLINK_is_refused
FAILED ...ASymlinkCannotHideAnotherCheckoutTests::test_an_UNRELATED_REPOSITORY_reached_through_a_symlink_is_refused
FAILED ...ASymlinkCannotHideAnotherCheckoutTests::test_the_reach_including_symlinked_spellings_is_still_one_spine
FAILED ...RefusalSetTests::test_a_path_that_will_not_RESOLVE_refuses_instead_of_raising
FAILED ...RefusalSetTests::test_the_unresolvable_path_guard_covers_the_UNBOUND_door_too
FAILED ...NulByteDoesNotKillTheDoorTests::test_a_nul_byte_in_spine_file_is_refused_and_the_door_stays_alive
FAILED ...NulByteDoesNotKillTheDoorTests::test_the_door_also_survives_a_nul_byte_while_it_is_BOUND
7 failed, 59 passed in 1.11s
```

One of the nine (`test_the_refusal_names_the_RESOLVED_target_not_the_link`) passed in that run
even though the bug was live, because a **success** payload also names all three paths. I found
that by reading the RED output rather than counting it, and added the `isError` assertion that
makes it discriminating; it now fails under M-E below.

## 6. Confirmatory — the four pins pass, and each control fires

Every mutation was planted in a **separate scratch `git worktree`** under the scratchpad, never
in this worktree, and restored **inside the same process** that mutated it with an md5 check —
both fixes the g2 reviewer recommended after the Commander mistook its live mutation for a
crash. `git worktree list` afterwards shows the scratch trees removed.

Baseline, unmutated, all four pins and their controls: `59 passed, 10 subtests passed`.

| mutation | pin | result |
|---|---|---|
| M-A mutate-then-return on the `spine_bind` route | `CallLifecycleToolChokePointPinTests` | **RED** — `test_call_lifecycle_tool_can_only_produce_content_two_ways`; the control still passed |
| M-B a `SPINE` reference planted in `_spine_open` | `SpineOpenNeverBindsIdentityTests` | **RED** — `test_spine_open_never_references_spine_session_or_run_engine` |
| M-C `SESSION = session` planted inside `_spine_bind` | `OneBinderPinTests` | **RED**, plus `SpineBindIsWiredTests::test_the_dispatch_calls_the_one_binder_and_assigns_nothing_itself` |
| M-D2 a `session_id` property planted on `spine_bind`'s inputSchema | `IdentityBindingPinTests` | **RED** — `test_no_tool_accepts_an_argument_that_could_redirect_the_door` **and** `test_the_exemption_is_keyed_on_tool_and_property_not_on_the_tool` |
| M-E my own B1 fix reverted (`resolved = candidate`) | the new symlink class | **RED**, 4 tests |
| M-F my own B2 catch narrowed to `OSError` | the new NUL tests | **RED**, 4 tests |

M-D is worth one line of honesty: my **first** attempt at it came back green, and the pin was
not at fault — I had inserted the planted `session_id` after the `properties` dict's closing
brace, so it was a sibling of `properties`, not a declared property. The pin correctly ignored
it. Re-planted inside `properties`, it goes RED on both the pin and its keying test, with
`['spine_bind.session_id']` named. **The exemption is keyed on the `(tool, property)` pair, not
the tool.** A mutation that comes back green is a claim about the mutation before it is a claim
about the pin.

## 7. Verification commands

```
$ py -m pytest tests/test_mcp_spine_bind.py tests/test_mcp_identity.py \
      tests/test_mcp_lifecycle.py tests/test_mcp_door_unbound.py \
      tests/test_mcp_spine_server.py -q
159 passed, 14 subtests passed in 7.11s
```

```
$ py -m pytest tests/ -q 2>&1 | tail -5
3276 passed, 5 skipped, 1218 subtests passed in 135.14s (0:02:15)

$ py -m pytest tests/ -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
(no output — the failure set is empty)
```

### One failure I hit and fixed, declared as a scope deviation

The first full-suite run came back `1 failed`:
`tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`.

I did not assume it was mine or someone else's. I checked out `1bd7bd42` in a scratch worktree
and ran that class there: **2 passed**. So it was mine, and mechanically so — the diff is entity
counts for `tests.test_mcp_spine_bind` (87 → 108) and the `tests` package total, i.e. the
arithmetic consequence of adding test classes. The failing test names its own remedy ("rerun
`python -m scripts.code_map build --root .` and commit the result") and commit `bd9b2c85` on
this branch is the same move for the same reason. `map/ids.jsonl`, the only other tracked map
file, was **byte-identical** to a fresh build, so I copied only the freshly built `INDEX.md`
(commit `5444c45a`).

**This is outside the dispatch's stated fence** ("keep the diff to `scripts/mcp_spine_server.py`,
the `spine_bind` test module, and the prose in B3"). Flagged rather than buried, in the commit
message as well as here. If the Commander would rather the branch carry a red freshness gate
than a 3-line map diff, `git revert 5444c45a` is the whole reversal.

## 8. Diff

```
$ git diff --stat 88ad6d36..HEAD          # excluding this result file
 .../commander-f2/IDENTITY_TRADE.md |  74 ++++-
 map/INDEX.md                       |   6 +-
 scripts/mcp_spine_server.py        | 136 +++++++--
 tests/test_mcp_spine_bind.py       | 329 ++++++++++++++++++++-
 4 files changed, 501 insertions(+), 44 deletions(-)
```

`scripts/checklist_engine.py`, `scripts/hooks/*`, `_RAIL_STRINGS` and `_refresh_attach_hint` are
untouched. None of the review's non-blocking observations were taken up: the lifecycle
choke-point control's inline detector, the duplicated anchor expression, and the eight triage
candidates are all left exactly as recorded.

## Map Impact

Reusing the inbound anchor vocabulary. Recorded, not authored — I am not a map owner.

- **`constraint:one-checkout-work-area-per-process` — now recordable, in its qualified form
  only.** The review's §11 said it must not be recorded as established until B1 was fixed. It is
  fixed and tested. The wording to record is **"one checkout's work-area tree per process,
  enforced by path"**, with the hardlink residual attached; the unqualified constraint is still
  false and should not enter the graph.
- **`decision:isolation-not-fencing`** — its settle condition ("name the property in the design
  doc and have the reviewer attack it") is now met in full: named, attacked, found false, fixed,
  re-tested, and the surviving limit named rather than hidden. The property and the code agree.
- **Structural:** `_spine_bind` gains one guard (`R2b`, `bad-argument-type`) and its R6 now
  reads the resolved path — eleven refusals in dispatch order, not ten. `_checkout_containing`,
  `_own_checkout_for_binding`, `_resolve_confined`, `_bind_process_to`: signatures unchanged.
  New test entity: `tests/test_mcp_spine_bind.py::ASymlinkCannotHideAnotherCheckoutTests`,
  `NulByteDoesNotKillTheDoorTests`, and a shared `_RealDoorInAStagedCheckout` base that
  `TwoDoorRoundTripTests` now inherits (extracted, not copied, so two classes cannot drift into
  two different launch environments).
- **Capability `door-binding`:** unchanged in shape — three moments (launch, mint, bind), one
  at a time. What changed is that the third moment's confinement is now true of every spelling
  of a path.
- **`constraint:fail-closed-binding`:** strengthened and now actually true on this tool — before
  R2b, one declared argument value produced no refusal, no rejection-log line, and no server.
- **`constraint:ast-pin-on-identity-assignment`, `constraint:lifecycle-return-pin`:** re-verified
  by M-C and M-A against the real source.
- **Triage candidate confirmed by measurement, not raised anew:**
  `main()` catching only `KeyError` (candidate 1 in the review, and
  `door-main-catches-only-keyerror.md` on disk) is the general shape of B2. I fixed the one call
  site, as instructed, and the surface-wide net remains unfixed and correctly recorded.

## Workflow Feedback

**The single most valuable line in this dispatch was "show the bug before you show the fix."**
It is why the first thing I built was a harness against unmodified HEAD rather than a test
against my intended fix. Had I started from the fix, I would have written a test that passes for
reasons I never checked — and in fact one of my nine new tests *did* pass against the buggy code
(§5), which I only noticed because I was reading a RED run I expected to be uniformly red. A
dispatch that mandates the pre-fix reproduction buys the calibration for the whole run, not just
the one output.

**The engine-drive conflict is now three crew members deep, and the wording of the exemption
should be fixed in the skill rather than re-adjudicated each time.** `constellation-implementer`
opens by saying that building an `IMPLEMENTER_PLAN` and claiming the engine lease is my *first
command*, ahead of any problem-solving, and that "work the engine never saw did not happen". My
dispatch forbids exactly that: no spine, no lease, no `mcp__spine__*`, and the
`IMPLEMENTER_RESULT` write is the delivery. I followed the dispatch — it is specific, recent,
gives its reason, and my environment had no spine bound. The skill does have a branch for "a
dispatched crew's spine is bound for you", but not for **"dispatched with no spine and
explicitly told not to author one"**, which is now the third consecutive crew member in this
lane to report the same gap (the g2 implementer's item 1, the g2 reviewer's item 1, mine). The
memory note `crew-dispatch-spine-null` covers *inherited* `SPINE_*`; this case is `SPINE_*`
absent **plus** an explicit prohibition. One sentence in the skill would end it.

**"Never mutate a tracked file" and "prove the pin's control still fires" are only compatible
because of a mechanism the dispatch did not name.** A pin control is only evidence if the file
the suite imports carries the planted regression, so the two rules meet in one place: a
throwaway checkout. I used `git worktree add --detach <scratch> <sha>` and restored inside the
same process as the mutation, both of which the g2 reviewer recommended after the Commander
mistook its live mutation for a crash. **This should be in the handoff template, not rediscovered
per crew**, in one line: "plant mutations in a scratch `git worktree`, never in the dispatch
worktree; restore in the same tool call." It costs one command and removes the entire class of
incident that consumed two commits on this branch.

**The scope fence and the required evidence can contradict each other, and the handoff should
say which wins.** My fence was three files; my evidence requirement was a green full suite.
Adding tests moves a tracked map artifact, so those two cannot both be satisfied. I chose green,
regenerated `map/INDEX.md`, and declared it — but a crew that chose the fence would hand back a
red suite and be equally defensible. The general rule worth stating: *mechanical consequences of
an in-scope change, where a failing test names its own remedy, are in scope; say so, or say the
opposite.*

**One friction worth passing on to whoever writes the next attack harness.** My first `M-D`
mutation came back GREEN and for about a minute looked like a second blocker in the identity
pin. It was my mutation: I had planted the `session_id` property one closing brace too late, so
it was not a declared property at all. **A green mutation is a claim about the mutation before it
is a claim about the pin** — check the plant landed where you think before you believe the
result. The g2 reviewer reported the mirror-image version of this (a harness bug that read as
six defeated guards), so it is a recurring shape in this epic, not a one-off.

**Two things about mid-run HEAD movement.** HEAD moved from `1bd7bd42` to `88ad6d36` while I
worked (four Commander docs/triage commits). I verified rather than assumed that none touched
`scripts/` or `tests/`. One of them, the hardlink triage candidate, materially changed what my
B3 prose had to say — and I only found it because a `git diff --stat` against my starting SHA
listed files I had not written. **A crew doing prose work is the population most exposed to
concurrent doc commits**, and the cheap fix is for the dispatch to name any triage candidate or
RETURN sentence landed after the review, since B3 is precisely a "make the documents agree"
task. I would have written a §7 amendment claiming an unqualified property, correcting one
overstatement into another, purely for want of one line in the dispatch.

---

```
$ git status --short
?? .agent-work/epic-567-door/cmdr-a/crew-handoffs/g2-review-review-result.md
```

The only entry is the reviewer's own untracked result file, which was there before I started and
is not mine to commit. Nothing of mine is uncommitted, and no mutation of mine ever touched a
tracked file in this worktree — every plant went into a scratch `git worktree` that has since
been removed (`git worktree list` shows only the five real lane worktrees).
