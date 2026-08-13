# commander-315-native working notes — engine-native isolation against a stored spine origin

Run: `commander-315-native`, epic 568 wave 1 recut.
Branch `epic-568/c2-native-isolation`, base `9bb8c1b6`.
Launch order: `.agent-work/epic-568/LAUNCH_ORDER-wave1-recut.md` (in the main checkout).

The prior Commander's notes for issue #315 lived at this same path and are preserved in
git history at `9bb8c1b6:notes-1.md`. This file is now this run's notes, per the launch
order's file-ownership section.

## Worktree isolation (first git-adjacent action)

```
$ py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py \
     --here /home/tommy/projects/constellation-skills-wt/epic-568-315-native
worktree OK: in /home/tommy/projects/constellation-skills-wt/epic-568-315-native
EXIT=0
```

## Problem statement

A spine does not record where it lives. Every judgment about "is this agent in the right
tree" is therefore delegated to a subprocess command check that measures the **ambient
cwd** as its subject. The engine cannot check the thing itself, so the check can be
disarmed by anything that controls the child's cwd.

The fix is two halves that must land together:

1. **Write side** — `init_work_area.py` stamps an `origin` block carrying `worktree` (the
   resolved root) when it instantiates a spine. Line 148 already computes
   `Path(root).resolve().as_posix()` and throws it away.
2. **Read side** — `checklist_engine.py` reads `origin.worktree` and compares it against
   the engine's **own `Path.cwd()`** at verb entry. Spines with no `origin` fall back to
   inherited cwd, i.e. today's behaviour exactly.

The read side alone is inert (no spine carries `origin`, so it would report green while
doing nothing). The write side alone changes nothing. Hence one change.

## The trap, and why the comparison must be engine-native

Storing the root and passing it to `verify_worktree_isolation.py --here` as a forwarded
`cwd=` reproduces the defect byte for byte: `origin.worktree` and the EXPECTED value in
the check text both derive from the same resolved root at creation, so the comparison
becomes `X == X`. Demonstrated by the prior wave (pasted in the launch order):

```
origin.worktree stored in the spine : /tmp/tmp.8uTC5OULCX/wt
EXPECTED inside the check text      : /tmp/tmp.8uTC5OULCX/wt
IDENTICAL? True
cwd = launcher's own (today)        : REFUSED  (gate works)
cwd = origin.worktree (direction D) : PASS     (gate disarmed)
```

The engine asking the OS where its own process stands cannot be lied to by a child
process's cwd. That is the whole point: two independent sources — stored state, and the
live process location — instead of one source compared with itself.

## What I measured before planning

### Blast radius of a native refusal — who actually runs the engine

Enumerated by command over the tree (`grep -rln checklist_engine scripts/ tests/`),
excluding `.agent-work/archive/`:

| Caller | How it reaches the engine | Exposure to a native cwd refusal |
|---|---|---|
| `scripts/hooks/spine_rail.py` | **never subprocesses the engine** — reads the spine state file and reconstructs `current` in-process (module docstring line 16; its one subprocess is `git worktree list`, line 507) | **none** |
| `scripts/hooks/gauge_writer_hook.py` | writes `gauge.json`; the engine reads it | **none** |
| `scripts/mcp_spine_server.py` | `checklist_engine.main(argv)` in-process, **never chdirs** (no `chdir` anywhere in the file) | real: server cwd is the MCP host's, not the spine's |
| `scripts/run_crew.py` | launches crews; does not drive the engine's verbs | none |
| 41 test files | import the engine or drive spines built in temp dirs; none stamp `origin` today | none (fallback path) |

The launch order warned that "the wired hooks call the engine you are changing". Measured:
**they do not.** `spine_rail.py` states the contract explicitly and keeps it. This is a
measured negative on a stated risk, and it removes the hook hazard from this change.

### Which verbs the comparison may guard

The MCP server measurement above is the honest-null pressure point: a server process
launched from the main checkout serving a worktree spine would be refused on **every**
call if the comparison guarded every verb.

Independent of the door, doctrine mandates a cross-tree read-only workflow:
`references/global-orchestrator.md` §idle-subagent-adjudication has the invoker read a
subordinate's `current` to see a `REFRESH REQUESTED:` line. An Admiral in the main
checkout reading a Commander's `current` is legitimate and load-bearing.

So: **the comparison guards mutating verbs and `claim`, never read-only verbs.**
`current`, `heartbeat` and `release` stay reachable from anywhere. Doing work in the
wrong tree is the defect; reading state from elsewhere is a supported workflow. This is
the scope choice the launch order left in my latitude, decided on the evidence above.

### The `init.c0` collision — measured, and floated

Mission item 3 says delete `COMMANDER_SPINE`'s `init.c0` command check. Measured:

```
$ py -c "...strip tasks.init.preconditions..."   # deliberate breakage
$ py -m pytest tests/test_worktree_precondition_wiring.py -q
3 failed, 4 passed in 0.23s
```

Failing:
- `EnumerationDeliberateBreakage::test_refuses_broken_copy_and_passes_real_fixed_tree`
- `EnumerationGeneralizesPastOneEntry::test_refuses_new_second_entry_without_naming_known_fixed_entry`
- `EnumerationGeneralizesPastOneEntry::test_passes_once_new_entry_carries_the_precondition`

Cause: `scripts/verify_worktree_precondition_coverage.py` exists to assert that
`COMMANDER_SPINE.template.json`'s `init` gate wires a command check containing
`verify_worktree_isolation.py`. Three tests in the merged guard pin that contract, one of
them by using the real template as the known-good entry that must **not** be named in a
failure. Deleting the check makes the guard's own premise false.

The two instructions collide head on: item 3 says delete it; the same launch order says
the tripwire must be green and must not be weakened. I did not resolve that by picking an
authority source. See "Float" below.

## What I am shipping

Items 1 and 2, together, as one change. `init.c0` stays for now — with the honest note
that after this change it is a check that cannot fail for any spine carrying `origin`
(the native comparison already proved cwd is inside the worktree before the command check
runs, so `git rev-parse --show-toplevel` necessarily equals `<repo-root>`).

## Float to the Admiral — item 3

`decision:delete-not-repair-init-c0` is graded `settled/measured`. Inherited doctrine for
that tier: "you may re-measure; a contradicting new measurement is evidence: revisit, and
log the new measurement as the new provenance." The measurement above is that evidence.

Deleting `init.c0` coherently requires **also** retiring
`scripts/verify_worktree_precondition_coverage.py` and its three enumeration tests,
because per-template wiring coverage is the wrong question once enforcement is
engine-native and no template can omit it. Retargeting the coverage script instead would
make it vacuous — a guard that passes in both the healthy and the defective world, which
is the exact defect the script was written to prevent.

That is a structural change and a scope change. Both are named in the launch order's
"must float" list, so it is floated rather than taken.

Cost if the Admiral rules "delete": remove `init.c0` from the template, delete
`scripts/verify_worktree_precondition_coverage.py`, delete the three enumeration test
classes, keep `EngineDeliberateBreakage` and `IsolationGateSurvivesThroughTheCLI` (which
test the engine, not the template wiring, and stay green either way).
