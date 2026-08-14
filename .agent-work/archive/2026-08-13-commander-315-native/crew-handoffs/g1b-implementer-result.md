# Implementation Result — g1b, the Admiral-ruled delta

## Assigned gate
`g1-implement` (second pass, the g1b delta) of `.agent-work/commander-315-native/execute.json`.
Driven through my own engine plan at
`.agent-work/commander-315-native/g1b-implement/IMPLEMENTER_PLAN.json`
(session `constellation/commander-315-native/g1b-implement/implementer/attempt-1`), gates
`m0-context` → `m6-result`.

## Completed slice
Both ruled changes, plus the documentation change. **The failure-set difference is empty.**

- **Change 1** — `run_crew.launch_process` takes a keyword-only `cwd` (default `None`) and passes
  it to `subprocess.run`. A new pure resolver, `crew_cwd(worktree, root)`, turns the registry's
  recorded worktree into the absolute directory to spawn in; `CliBackend.dispatch` and
  `CliBackend.resume` both thread it. A missing or non-directory `cwd` is refused **by name**
  before the spawn.
- **Change 2** — `mcp_spine_server.run_engine` wraps its one in-process
  `checklist_engine.main(argv)` call in `_standing_in_the_bound_spines_worktree()`, a context
  manager that chdirs into the bound spine's own worktree and restores the previous directory in a
  `finally`. Unresolvable worktree ⇒ no chdir, no failure.
- **Change 2b** — every place in `mcp_spine_server.py` that documented cwd-independence as
  load-bearing now records that the door deliberately stands in the bound spine's tree for the
  duration of an engine call, and why. **5 sites found, 5 updated.** No reasoning deleted.

`tests/test_mcp_lifecycle.py` **passes untouched** — the expected outcome the handoff named. No
assertion anywhere was adjusted to match observed output.

## Scope

**Files changed:**
- `scripts/run_crew.py` — `crew_cwd` (new), `launch_process` (+`cwd`), two call sites.
- `scripts/mcp_spine_server.py` — `_standing_in_the_bound_spines_worktree` (new), `run_engine`
  (one wrapped call + docstring), 5 documentation sites.
- `tests/test_crew_launcher.py` — **the one test double** (`fake_launch`'s inner `fake`) reconciled
  to accept `cwd=None`. It is the only double of `launch_process` in the repo (`grep -rn
  "launch_process" --include=*.py .` → definition, this double, and prose in `docs/` and
  `.agent-work/`). `tests/test_run_skill_eval.py`'s eight doubles are for `run_skill_eval`'s own
  launch seam, which already took `cwd`, and are untouched.
- `tests/test_crew_worktree_cwd.py` — **new**, 9 tests for change 1.
- `tests/test_mcp_door_engine_cwd.py` — **new**, 10 tests for change 2.
- `map/INDEX.md` — regenerated. **Disclosed, not silent:** adding two functions made
  `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
  red, and that test names its own remedy (`python -m scripts.code_map build --root .`). The diff is
  4 lines: `scripts` 1169 → 1171 entities, `scripts.run_crew` 59 → 60, `scripts.mcp_spine_server`
  19 → 20 — exactly my two new functions, no other drift. The bar is an empty failure set, and this
  failure is mechanically forced by the authorized change.

**Specific exclusions touched:** no. `scripts/hooks/spine_rail.py`, `scripts/agent_work_root.py`,
`scripts/checklist_engine.py`, `scripts/init_work_area.py`, `scripts/spine_lifecycle.py` and
`tests/test_spine_origin_isolation.py` are all untouched (`git status` confirms).

## Behavior changed

**Yes**, two production behaviours:

1. **A dispatched crew's working directory is now its assigned worktree, not the dispatcher's.**
   Previously an accident of whoever launched it. A relative `--worktree` resolves against `--root`,
   never against the dispatching process's own directory. A legacy registry entry with no
   `worktree` key still resumes, degrading to the inherited directory (`crew_cwd` returns `None`).
2. **The MCP door's process moves for the length of one engine call.** It stands in the bound
   spine's worktree, then returns. Outside that window the door is cwd-independent as before.

**Concurrency, established rather than assumed.** `chdir` is process-global, so I read the door's
request loop before relying on it: `scripts/mcp_spine_server.py:main()` is
`for line in sys.stdin:` — it parses one request, builds one `result`, writes one reply, and only
then reads the next line. There is no thread, no task, no `asyncio` (the module imports
`contextlib`, `io`, `json`, `os`, `subprocess`, `sys`, `datetime`, `pathlib` — nothing concurrent).
**It is a single-threaded stdio request/response loop**, so no second in-flight request exists whose
cwd this could corrupt. That is a property a future change could quietly remove, so I pinned it:
`SingleThreadedDoorPinTests` fails if the module ever imports `threading`/`asyncio`/
`multiprocessing`/`concurrent`, or if `main()` stops being exactly one synchronous `for` loop.

**The known cost, stated plainly.** The door has lost its unqualified cwd-independence, exactly as
the Admiral's option 2 said it would. Non-forwardability is explicitly not claimed by the guard, so
a caller choosing where it stands remains the acknowledged limit. `_worktree_root_for_lifecycle`
runs one `git rev-parse --show-toplevel` per engine call — recomputed rather than cached, so a
worktree created or removed mid-session is never answered from a stale cache.

## Map Impact
- **Structural anchors touched:** `scripts.run_crew` — one new module-level pure function
  (`crew_cwd`), one keyword added to the spawn seam; entity count 59 → 60.
  `scripts.mcp_spine_server` — one new module-level context manager
  (`_standing_in_the_bound_spines_worktree`); entity count 19 → 20.
- **Capabilities changed:** crew dispatch now places a crew in its own worktree; the MCP door can
  drive a spine whose worktree is not the server's launch directory (the `spine_open` → `claim`
  round trip, previously impossible by construction).
- **Constraints/assumptions touched:** the assumption the previous pass **falsified** — "a
  dispatched crew's cwd is its spine's worktree" — is now **true by construction** rather than
  assumed. The invariant "this door never changes the process's cwd" is **retired**, deliberately,
  and its retirement is recorded at all 5 sites that relied on it.
- **Claims/evidence produced:** both changes are armed (each independently reverted and observed
  red, below); the engine's worktree guard is unweakened (`repro_native.py` still reports
  `GATE ARMED: True`).
- **Trust limitations:** `map/INDEX.md` regenerated and verified attributable; `map_orient.py`
  was not re-run.

## Test mode
**Required:** test-first (the handoff demands each change be shown to *do* something).
**Satisfied:** yes — red observed before green for both changes, and each change independently
reverted afterwards to re-observe the red.

## Evidence

### 1. The arming — each change proven on its failure side

**Change 1, whole file back to HEAD** (`git show HEAD:scripts/run_crew.py > scripts/run_crew.py`):

```
7 failed, 2 passed
TypeError: launch_process() got an unexpected keyword argument 'cwd'
```

**Change 1, finer cut — parameter kept, threading removed** (the two `cwd=crew_cwd(...)` arguments
deleted, nothing else):

```
4 failed, 5 passed
FAILED CrewSpawnCwdTests::test_dispatch_passes_an_absolute_worktree_as_the_child_cwd
FAILED CrewSpawnCwdTests::test_relative_worktree_resolves_against_root_not_the_dispatchers_cwd
FAILED CrewSpawnCwdTests::test_resume_passes_the_stored_worktree_as_the_child_cwd
FAILED CrewSpawnCwdTests::test_the_registry_records_the_same_worktree_the_spawn_received
```

This is the stronger arming: the signature alone does not carry the change, the threading does.

**Change 2, chdir removed, everything else kept** (`with _standing_in_the_bound_spines_worktree():`
deleted, the `main(argv)` call left):

```
3 failed, 16 passed
FAILED tests/test_mcp_door_engine_cwd.py::...::test_a_guarded_verb_on_a_foreign_worktree_spine_now_succeeds
FAILED tests/test_mcp_door_engine_cwd.py::...::test_engine_call_runs_inside_the_bound_spines_worktree
FAILED tests/test_mcp_lifecycle.py::FullStdioRoundTripTests::test_open_drive_close_round_trip_names_branch_commit_and_ready_to_pr
  REFUSED: claim refused: this spine belongs to the worktree /tmp/.../repo-wt/roundtrip-work,
  but the engine is running in /home/tommy/projects/constellation-skills-wt/epic-568-315-native.
```

Each revert was restored from a byte-identical copy (`diff -q` → `RESTORED-IDENTICAL`) before
continuing.

### 2. New coverage for change 1 — `tests/test_crew_worktree_cwd.py` (9 tests)

Asserted **on the value handed to the spawn**, not inferred: a recording double captures the `cwd`
keyword `dispatch`/`resume` actually pass (absolute worktree; relative worktree resolved against
`root`; resume from the stored entry; a legacy entry with no `worktree` key ⇒ `None`; the registry
entry and the spawn cannot disagree). Then, through a **real subprocess**, the seam is proven to
reach the OS: the child reports its own `os.getcwd()` and it is the worktree; omitting `cwd` keeps
the inherited directory; a missing directory and a file-where-a-directory-should-be are both
refused as `CrewLaunchError` naming the path, never a bare `FileNotFoundError`.

### 3. New coverage for change 2 — `tests/test_mcp_door_engine_cwd.py` (10 tests)

The engine call is observed **from inside** (a spy standing in for `checklist_engine.main` records
`os.getcwd()` at call time) on a spine whose worktree is a throwaway git repo under `/tmp`, i.e.
not the server's own directory — with a guard assertion that the fixture is not vacuous. `claim`,
an origin-guarded verb, then goes through the **real** engine end to end and writes its lease.
`Path.cwd()` is asserted before and after on every path: success, engine exception (code 1), engine
`SystemExit(2)`, and an ordinary engine refusal. Unresolvable worktrees (a spine outside any git
repo; a spine whose directory has been deleted) run without moving and without failing.
`SingleThreadedDoorPinTests` pins the concurrency property the chdir rests on.

### 4. The full suite

```bash
cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native
python -m pytest tests/ -q -p no:randomly
# 2979 passed, 6 skipped, 1130 subtests passed in 120.99s   (exit 0)

python -m pytest tests/ -q -p no:randomly 2>&1 | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
# (no output — the distribution is empty)

python -m pytest tests/test_spine_origin_isolation.py tests/test_worktree_precondition_wiring.py tests/test_mcp_lifecycle.py -q -p no:randomly
# 42 passed, 1 skipped, 10 subtests passed

python .agent-work/commander-315-native/repro_native.py
# A PASS / B REFUSED / C PASS / D PASS
# B refused AND took no lease (state fact): True
# GATE ARMED: True
```

**Both counts, and the difference.** `main`'s Linux baseline: **2934 passed, 5 skipped, 0 failed**.
This tree: **2979 passed, 6 skipped, 0 failed, 1130 subtests passed**. Failing-file set on `main`
`{}`, here `{}`. **Set difference: EMPTY.** The previous pass's `{tests/test_mcp_lifecycle.py}` is
closed. (+45 passed against baseline = the previous pass's +25 plus my 19 new tests, less
collection deltas; the +1 skipped is the pre-existing Windows-only case-folding test.)

`tests/test_gauge_chain_writer_to_trip.py::test_containment_repo_agent_work_untouched_by_the_chain`
**did not fail in either full run** — the known transient did not fire, so there is nothing to
re-run in isolation and nothing to misreport.

### 5. Wiring grep — one command per new symbol

```bash
grep -rn "crew_cwd(" scripts/ | grep -v "def crew_cwd"
# scripts/run_crew.py:1185:  cwd=crew_cwd(spec.worktree, root))        <- CliBackend.dispatch
# scripts/run_crew.py:1244:  cwd=crew_cwd(entry.get("worktree"), root)) <- CliBackend.resume
# count: 2

grep -rn "_standing_in_the_bound_spines_worktree" scripts/ | grep -v "def _standing"
# scripts/mcp_spine_server.py:452:  with _standing_in_the_bound_spines_worktree():   <- run_engine
# (+ 4 prose references: module docstring, run_engine's docstring, and 2 doc sites)
# count: 1 executable call site
```

Both non-zero, both production call sites outside the defining function and outside any self-test.
No stop condition triggered.

## TDD evidence, if required
- **Failing test observed (change 1):** `python -m pytest tests/test_crew_worktree_cwd.py -q -p
  no:randomly` → `7 failed, 2 passed`, `TypeError: launch_process() got an unexpected keyword
  argument 'cwd'`. Written and observed red **before** `scripts/run_crew.py` was edited; attested
  as `m1-crew-cwd.c1` on the engine before the implementation.
- **Failing test observed (change 2):** `python -m pytest tests/test_mcp_door_engine_cwd.py -q -p
  no:randomly` → `2 failed, 8 passed`; the two behavioural tests red, the restore/no-op/pin tests
  already green by construction. Attested as `m2-door-chdir.c1` before the implementation.
- **Passing test observed:** `169 passed` (change 1 + the existing launcher suite) and
  `19 passed` (change 2 + `test_mcp_lifecycle.py`), both run by the engine as the gate's own
  command check at `advance`.
- **Refactor while green:** yes — one. The full suite exposed that my new door tests were
  monkeypatching `checklist_engine.main` on the **shared** engine module without restoring it,
  which reddened 3 tests in `tests/test_mcp_identity.py` when both files ran in one session.
  Fixed with `_EngineSpyMixin` (save + `addCleanup` restore). Worth naming because the symptom
  appeared 100 tests away from the cause and only ever in a full-suite run.

## Docs/contracts touched
`scripts/mcp_spine_server.py`, 5 sites. Enumerated by command, not memory:
`grep -n -i "ambient\|cwd\|working directory\|chdir" scripts/mcp_spine_server.py`.

1. **Module docstring** — new paragraph opening the ambient-state section: the door *used to be*
   strictly cwd-independent, what changed, why (the guard reads ambient cwd; the door calls the
   engine in-process), and what is still cwd-independent.
2. **`_git_rev_parse`** (the handoff's `:454`) — the claim "this door's request-handling loop never
   changes cwd and should not start" was made false by this change. Replaced with the fact, and
   with why the explicit `cwd=` parameter is now *more* load-bearing than before, not less.
3. **`_primary_checkout_for_lifecycle`** (the handoff's `:478`) — the ambient-vs-explicit contrast
   is still true; recorded that it hardened from preference into requirement now that this
   process's cwd is a thing that moves.
4. **`_resolve_confined`** — "a relative value resolves against the process's own cwd" is now
   ambiguous between two directories. Recorded that `_identity_violation` runs **outside** the
   moved window on purpose (resolving containment against a directory the door is about to enter
   would change what "confined" means mid-check), and that no live divergence follows because this
   door only ever hands the engine absolute paths.
5. **The `--delta` inline comment in `_identity_violation`** — same distinction, at the call site.

No reasoning was deleted at any of the five; each keeps its original argument and gains the update.

## Assumptions
- Regenerating `map/INDEX.md` is in scope. It is neither allowed nor forbidden by name, but the
  handoff's bar is an empty failure-set difference, the failure is mechanically forced by the
  authorized change, and the failing test states the exact remedy. Disclosed above; revert it and
  `test_code_map.py` goes red.
- `crew_cwd` resolving a relative `--worktree` against `--root` (not against the dispatcher's cwd)
  is the reading that makes the change meaningful; resolving against the dispatcher would re-import
  the accident being removed.
- The `finally` restore is deliberately **not** itself wrapped in a swallow: if the directory the
  door came from has vanished, that surfaces as a failed call rather than a server left silently
  standing somewhere it did not choose.

## Stop conditions hit
None. `spine_rail.py` and `agent_work_root.py` were never wanted; no assertion was edited to match
output; the door is single-threaded, so the chdir is safe; no decision outside my authority arose.

## Out-of-scope observations
- **`ExternalBackend` spawns nothing, so change 1 does not reach it.** A crew dispatched
  out-of-band still lands wherever its harness puts it. Correct for this change (there is no
  process to place), but the guarantee "a crew stands in its own worktree" is a `cli`-backend
  guarantee only, and nothing says so at the `--backend external` seam.
- **`run_skill_eval.py` already had a `cwd`-carrying launch seam** with eight doubles declaring it.
  Two launch seams in one repo, one of which had this right for a year. Worth a look at whether
  they should be one.
- **The engine wrote its per-gate artifacts to a doubled path** —
  `.agent-work/commander-315-native/commander-315-native/{context,mechanical}/*.json` — because my
  plan file lives at `.agent-work/<work-id>/g1b-implement/` and the work-area root is re-derived
  from the plan's own directory. Harmless here, and I did not touch it, but a crew plan nested one
  level below the work area produces a confusing tree.
- **A child checklist gets no `origin` stamp.** My own `IMPLEMENTER_PLAN.json` carries none, so the
  worktree guard did not apply to it — the same gap the Commander already filed as `tc8`. Now that
  the door does chdir, a stamped crew plan would work rather than deadlock; the reason not to stamp
  is weaker than it was.

## Workflow Feedback
- **Handoff gaps:** none in the fields — task, intent, scope, exclusions, evidence, test mode, stop
  conditions and return format were all present, and the line-number citations (`run_crew.py:666`,
  `mcp_spine_server.py:361`, `:454`, `:478`) all landed within a few lines. One genuine gap: the
  **Allowed** list names source files but is silent on **generated artifacts**. Regenerating
  `map/INDEX.md` was forced by the bar and unmentioned by the scope, so I had to decide it myself
  and disclose it. A handoff whose bar is "zero failures" should say whether regenerated artifacts
  count as in scope — the previous pass hit the same thing (`COMMANDER_RESULT.md` §12).
- **Context rediscovered:** nothing material. The handoff's warning that doubles monkeypatch
  `launch_process` saved a rediscovery, and its instruction to *name* the doubles I touched was
  what made me grep the whole repo rather than fix the first breakage and move on — that grep is
  how I learned `run_skill_eval` has a second, older launch seam.
- **Instructions improvised around:** the implementer skill says to drive a **bound** spine
  (`SPINE_FILE`/`SPINE_SESSION`) when dispatched as a crew, and to author my own plan only when
  nothing is bound. This dispatch set `SPINE_PARENT` but neither `SPINE_FILE` nor `SPINE_SESSION`,
  so I took the second branch and authored `IMPLEMENTER_PLAN.json`. That is the documented fallback
  and it worked, but "parent bound, spine unbound" is a third state the instruction does not name.
- **What would have made this easier:** one line in the handoff on generated artifacts, per above.
  Everything else about this handoff was unusually good: the ruling was explicit, the authority
  boundary was drawn ("settled, not yours" vs "yours"), and demanding the **arming** rather than
  the pass is what turned the finer change-1 revert into real evidence instead of a `TypeError`.

## Return status
`complete`
