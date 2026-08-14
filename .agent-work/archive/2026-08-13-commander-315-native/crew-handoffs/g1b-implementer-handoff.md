# Implementer Handoff — g1b, the Admiral-ruled delta

## Gate
`g1-implement` (second pass) of `.agent-work/commander-315-native/execute.json`.

Worktree `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`, branch `epic-568/c2-native-isolation`, HEAD `890ff76f`. **Never enter `/home/tommy/projects/constellation-skills-wt/epic-568-315`**; never write the main checkout.

## This is a bounded ADDITION to reviewed, committed work

The engine-native worktree isolation guard is already implemented, committed, and independently APPROVED. **Do not reopen its design.** Read `.agent-work/commander-315-native/COMMANDER_RESULT.md` §6 for the collision this delta closes, then implement the two ruled changes. Do not re-derive the collision — it is settled and ruled by the human.

## The ruling

`spine_open` creates a **new** worktree and stamps `origin.worktree` to it. The next verb on that spine is `claim`, issued in-process through the MCP door, which never chdirs — so it cannot already stand inside a directory that did not exist a moment earlier. `tests/test_mcp_lifecycle.py::FullStdioRoundTripTests::test_open_drive_close_round_trip_names_branch_commit_and_ready_to_pr` fails on exactly this.

**The human ruled options 1 + 2. Implement both.** Both modules are in scope. The forbidden list is **only** `scripts/hooks/spine_rail.py` and `scripts/agent_work_root.py`.

### Change 1 — `run_crew.launch_process` passes `cwd=<the spine's worktree>`

`scripts/run_crew.py:666`. It is documented as "The ONE place a real crew subprocess is spawned" and its `subprocess.run(...)` passes **no `cwd=`**, so a dispatched crew inherits the *dispatcher's* cwd — an accident of whoever launched it. Make it explicit: the crew runs in its own worktree.

- `run_crew.py` already carries `--worktree`, and the registry entry records it. Thread that value through to `launch_process`.
- **Test doubles monkeypatch `launch_process`** (its own docstring says so). Adding a *required* parameter breaks them. Add it **keyword-only with a default** so existing doubles survive, and reconcile any double whose explicit signature still refuses it. Name the doubles you touched.
- Callers are at `scripts/run_crew.py:1104` and `:1146` (both resolve `launch` at call time, per the docstrings at `:1320` and `:1346`).
- Guard the obvious: if the worktree path does not exist, fail with a clear message rather than letting `subprocess.run` raise a bare `FileNotFoundError` that reads like the CLI is missing.

### Change 2 — the door `chdir`s around its in-process `main()` call

`scripts/mcp_spine_server.py:361`, inside `run_engine`, is `code = checklist_engine.main(argv)` — in-process, no chdir. Wrap that single call so the process stands in the bound spine's own worktree for its duration, and **restore the previous cwd in a `finally`**, unconditionally, including on `SystemExit` and on any exception.

- Derive the target from the spine's own location, the way the module already does elsewhere: `_worktree_root_for_lifecycle` uses `cwd=SPINE.parent`. Reuse the existing helper rather than minting a new derivation.
- **`chdir` is process-global.** Establish and state whether this door can be handling more than one request at a time. If it is a single-threaded stdio request/response loop, say so explicitly and cite what you read; if it is not, say what you did about it. Do not assume.
- If the spine's worktree cannot be resolved (a spine outside any worktree, a removed directory), **do not chdir** and do not fail — let the call proceed as it does today. A door that cannot locate a tree must not become a door that cannot run.

### Change 2b — the documentation the Admiral explicitly called out

The module asserts its own cwd-independence in prose that this change makes false. At minimum `scripts/mcp_spine_server.py:454` ("never the process's own ambient cwd, which this door's request-handling…") and `:478` ("process's ambient cwd; this does the identical join, explicit about…"). Check the module docstring too.

**Update every place that documents the invariant as load-bearing**, in the same change. The Admiral's words: this wave has twice been bitten by docs that outlived the behaviour they described. Do not delete the reasoning — record that the door now deliberately stands in the bound spine's tree for the duration of an engine call, and why.

## Scope

**Allowed:** `scripts/run_crew.py`, `scripts/mcp_spine_server.py`, `tests/test_mcp_lifecycle.py` (only if reconciliation is genuinely required — see below), any test double of `launch_process`, and new tests covering both changes.

**Forbidden:** `scripts/hooks/spine_rail.py`, `scripts/agent_work_root.py`. Also do not touch `scripts/checklist_engine.py`, `scripts/init_work_area.py`, `scripts/spine_lifecycle.py`, `tests/test_spine_origin_isolation.py`, or the deleted-template work — all reviewed and settled.

## The bar for done — an EMPTY failure-set difference

`main`'s Linux baseline is **2934 passed, 5 skipped, 0 failed**. The current difference is `{tests/test_mcp_lifecycle.py}` and it must become **empty**. This is not "close enough" — the Admiral refused to soften it.

**On `test_mcp_lifecycle.py`:** if options 1+2 make the flow it asserts genuinely work, it should **simply pass, untouched**. That is the expected outcome. Only if it asserts something the new contract deliberately changes may you reconcile it — and then you must **state explicitly what contract changed and why**. **Never adjust an assertion to match observed output.** If you find yourself editing an assertion to make a number agree, stop and return instead.

## Required evidence

**Load-bearing — prove rigorously:**

1. **The arming.** Each change must be shown to *do* something: revert change 1 and show its new test goes red; revert change 2 and show `test_mcp_lifecycle.py` (or your new door test) goes red. A change proven only on its pass side is the defect class this whole issue exists to remove.
2. **New coverage for change 1** — a crew spawned through `launch_process` actually receives the worktree as its cwd, asserted on the value passed to the spawn, not inferred.
3. **New coverage for change 2** — the door's in-process engine call succeeds on a spine whose worktree is not the server's cwd, **and the process's cwd is restored afterwards** (assert `Path.cwd()` before and after, including on the failure path).
4. **The full suite** and its mechanical distribution:

```bash
cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native
python -m pytest tests/ -q -p no:randomly
python -m pytest tests/ -q -p no:randomly 2>&1 | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
python -m pytest tests/test_spine_origin_isolation.py tests/test_worktree_precondition_wiring.py tests/test_mcp_lifecycle.py -q -p no:randomly
python .agent-work/commander-315-native/repro_native.py
```

State both counts and the difference explicitly.

**Known transient — do not misreport it.** `tests/test_gauge_chain_writer_to_trip.py::test_containment_repo_agent_work_untouched_by_the_chain` snapshots the **live** `.agent-work` tree and asserts equality, so any concurrent writer reds it. If it fails, **re-run it in isolation** before calling it a regression, and say which it was.

## Wiring grep

One command per new symbol, showing a call site outside its own definition and outside any self-test. State the count. **Zero external call sites is a stop condition.**

## Authority

Settled, not yours to revisit: that options 1+2 are the fix; that the door losing its cwd-independence invariant is accepted with open eyes (non-forwardability is explicitly **not** claimed by this change, so a caller choosing where it stands is the acknowledged limit, not a breach); and the whole of the already-reviewed guard.

Yours: how the worktree is threaded to `launch_process`, how the chdir is scoped and restored, the test shapes, and the doc wording.

## Stop conditions

Stop and return if: `spine_rail.py` or `agent_work_root.py` is wanted; the failure difference cannot be emptied without editing an assertion to match output; `chdir` turns out to be unsafe because the door handles concurrent requests; or a decision outside the authority above is needed.

**An honest null is a complete deliverable.** If options 1+2 do not empty the difference, report that with the measurement rather than forcing it.

## Return format

`IMPLEMENTER_RESULT`: completed slice, files changed, evidence, assumptions, stop conditions hit, out-of-scope observations, workflow feedback. `Return status` lowercase, one of `complete | partial | blocked | out-of-scope | failed`.

**Delivery:** write to `.agent-work/commander-315-native/crew-handoffs/g1b-implementer-result.md` before ending your turn.
