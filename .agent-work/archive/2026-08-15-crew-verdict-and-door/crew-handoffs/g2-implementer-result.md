# Implementation Result

> Written per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Assigned gate
`g2`

## Completed slice
Two pieces, both required by the corrected handoff:

1. **Registry entry field.** `build_entry` in `scripts/run_crew.py` now sets `entry["door_bound"] = (backend
   == BACKEND_CLI)` (`BACKEND_CLI == "cli"`), so every registry entry states plainly whether its door was
   bound: `True` for `cli`-backend entries (the only path that spawns a child and binds
   `SPINE_FILE`/`SPINE_SESSION` into it via `_crew_door_env`), `False` for `external`-backend entries (which
   spawn no process and build no environment). Written as an equality against `"cli"`, not an inequality
   against `"external"`, so a future third backend value defaults to the safer `False`.
2. **CLI stderr banner.** `ExternalBackend.dispatch` now prints an unconditional stderr line at the moment it
   records the entry, stating the door is unbound, names `.mcp.json`'s demo default, and instructs verifying
   `spine_status` before any mutating verb.

**Exact banner text (verbatim):**
```
WARNING: external-backend crew {session_name!r} has an UNBOUND MCP door -- ExternalBackend spawns no process
and builds no environment, so nothing binds SPINE_FILE/SPINE_SESSION. Its MCP door resolves to .mcp.json's
demo default, not this crew's own spine. Verify spine_status before any mutating verb.
```
(`{session_name!r}` is the entry's own `session_name`, e.g. `'constellation/issue-1/g1/implementer/attempt-1'`.)

No attempt was made to bind the door out-of-band — confirmed impossible by construction (module-import-time
env read in `scripts/mcp_spine_server.py`, pinned by `tests/test_mcp_identity.py:914`); this gate is
visibility-only, per the Protected Intent.

## Scope
**Files changed:**
- `scripts/run_crew.py` — `build_entry` (new `door_bound` field + docstring) and `ExternalBackend.dispatch`
  (new unconditional stderr banner) only.
- `tests/test_crew_launcher.py` — two new tests in `BuildEntryTests`, one new test near the existing
  external-dispatch tests in `BackendEquivalenceTests`.

**Specific exclusions touched:** no. `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
`.mcp.json`, `scripts/mcp_spine_server.py` untouched. `finalize_from_exit_code` (g1's change, commit
`f06d314e`) untouched — confirmed by diff, only `build_entry` and `ExternalBackend.dispatch` changed in
`run_crew.py`. `.worktrees/epic-568-441/` and `.worktrees/tc1-worktree-identity/` untouched.

## Behavior changed
Yes, additively:
- Every `build_entry(...)` call now returns a dict with a new `door_bound` key (previously absent). No
  existing key removed, renamed, or retyped; no call site needed to change.
- `ExternalBackend.dispatch` now writes one line to stderr on every call, in addition to its prior
  side effects (record entry, save registry, return `(None, entry)`). Its return value and the registry
  entry's other fields are unchanged.

## Exact diff
```diff
--- a/scripts/run_crew.py
+++ b/scripts/run_crew.py
@@ -917,7 +917,21 @@ def build_entry(
                      omitted, when no `--parent` was given -- a resume reads
                      this back so the SPINE_PARENT binding and prompt clause
                      stay stable across attempts instead of re-deriving from
-                     whatever the RESUMING process's own environment carries)."""
+                     whatever the RESUMING process's own environment carries).
+      * `door_bound` — `True` only for `backend == "cli"` (the one path that
+                     actually spawns a child and binds `SPINE_FILE`/
+                     `SPINE_SESSION` into its environment via `_crew_door_env`),
+                     `False` for every other backend, including `external`
+                     (which spawns no process and builds no environment, so
+                     nothing binds those variables and its MCP door silently
+                     resolves to `.mcp.json`'s demo default). Written as an
+                     equality against `"cli"`, never an inequality against
+                     `"external"`, so a future third backend defaults to the
+                     safer `False` instead of silently inheriting a bound
+                     door it never earned. This makes the hazard readable
+                     straight out of `crew-runs.json` -- a resumed/relaunched
+                     Commander or a human debugging a crew's behavior does not
+                     have to already know which backends bind a door."""
     name = session_name(work_id, gate, role, attempt)
     stdout_path, stderr_path = run_log_paths(work_id, gate, role, attempt, root)
     entry = {
@@ -929,6 +943,7 @@ def build_entry(
         "status": "running",
         "session_name": name,
         "backend": backend,
+        "door_bound": backend == BACKEND_CLI,
         "pid": pid,
         "worktree": worktree,
         "handoff": _relativize(handoff, root) if handoff is not None else None,
@@ -1332,6 +1347,20 @@ class ExternalBackend(CrewBackend):
         # finalize here (the caller verifies later with `verify`).
         entries.append(entry)
         save_registry(registry_path(spec.work_id, root), entries)
+        # UNCONDITIONAL visibility banner (issue: unbound-door hazard) — binding
+        # the door out-of-band is impossible by construction (module-import-time
+        # env read in mcp_spine_server.py, pinned by test_mcp_identity.py), so
+        # this gate's job is to make the unbound state loud, not to bind it. The
+        # out-of-band caller (a Commander) reads this at the exact moment it is
+        # building the out-of-band prompt for the crew it is about to dispatch.
+        print(
+            f"WARNING: external-backend crew {entry['session_name']!r} has an "
+            f"UNBOUND MCP door -- ExternalBackend spawns no process and builds "
+            f"no environment, so nothing binds SPINE_FILE/SPINE_SESSION. Its MCP "
+            f"door resolves to .mcp.json's demo default, not this crew's own "
+            f"spine. Verify spine_status before any mutating verb.",
+            file=sys.stderr,
+        )
         return None, entry
```

`CliBackend`'s entry construction was read (it calls the same shared `build_entry`, ~line 1193-1199) and
needed no separate edit: `door_bound` is computed inside `build_entry` from the `backend` argument every
caller already passes, so both backends get the field from the one shared constructor — no drift risk
between the two call sites.

## Test mode
**Required:** TDD (test-first, red before green) for both pieces per the handoff's Test Mode section.
**Satisfied:** yes — see TDD evidence below.

## Evidence

```bash
$ python -m pytest -q -k "test_build_entry_cli_door_bound_true or test_build_entry_external_door_bound_false or test_external_dispatch_prints_unbound_door_banner"
...                                                                      [100%]
3 passed, 3012 deselected in 0.80s
```

```bash
$ python -m pytest -q tests/test_crew_launcher.py
........................................................................ [ 41%]
........................................................................ [ 83%]
............................                                             [100%]
172 passed in 0.54s
```

**Result:** pass — both commands run foreground to completion, output pasted verbatim.

## TDD evidence, if required

**Failing test observed (RED), run against the UNCHANGED `build_entry`/`ExternalBackend.dispatch`:**

```
$ python -m pytest -q -k "test_build_entry_cli_door_bound_true or test_build_entry_external_door_bound_false or test_external_dispatch_prints_unbound_door_banner" 2>&1 | tail -40
...
        entry = RC.build_entry(backend="external", pid=None, **self._kwargs())
>       self.assertIs(False, entry["door_bound"])
                             ^^^^^^^^^^^^^^^^^^^
E       KeyError: 'door_bound'

tests/test_crew_launcher.py:2264: KeyError
__ BackendEquivalenceTests.test_external_dispatch_prints_unbound_door_banner ___
...
            banner = captured.getvalue()
>           self.assertIn("unbound", banner.lower())
E           AssertionError: 'unbound' not found in ''

tests/test_crew_launcher.py:2568: AssertionError
=========================== short test summary info ============================
FAILED tests/test_crew_launcher.py::BuildEntryTests::test_build_entry_cli_door_bound_true
FAILED tests/test_crew_launcher.py::BuildEntryTests::test_build_entry_external_door_bound_false
FAILED tests/test_crew_launcher.py::BackendEquivalenceTests::test_external_dispatch_prints_unbound_door_banner
3 failed, 3012 deselected in 0.83s
```

All three failed for the expected reason: `door_bound` did not exist on the entry dict yet, and nothing was
printed to stderr yet (empty string).

**Passing test observed (GREEN), run against the FIXED code:**

```
$ python -m pytest -q -k "test_build_entry_cli_door_bound_true or test_build_entry_external_door_bound_false or test_external_dispatch_prints_unbound_door_banner"
...                                                                      [100%]
3 passed, 3012 deselected in 0.80s
```

**Refactor while green:** no — the change was minimal (one dict key, one print call); no refactor pass
needed.

## Docs/contracts touched
- `scripts/run_crew.py` — `build_entry`'s docstring, updated in the same edit to describe the new
  `door_bound` field's semantics and rationale.

## Assumptions
- The banner's exact wording was left to my judgment within the handoff's required content (unbound door,
  `.mcp.json`'s demo default, verify `spine_status` before any mutating verb) and tone match (see Constraints:
  "match `run_crew.py`'s existing hazard-message style"). I reused phrasing already present in the file —
  "spawns no process and builds no environment, so nothing binds" (from the `--spine` refusal
  `CrewLaunchError` in `ExternalBackend.dispatch` itself) and "`.mcp.json`'s demo default" (from the
  `--spine` argparse help text) — rather than inventing new phrasing, so the hazard reads consistently
  wherever a caller encounters it in this file.
- `door_bound` is computed from `backend`, not from whether `_crew_door_env` was actually called for a given
  dispatch. This matches the handoff's literal ask ("`True` for `cli`-backend entries ... `False` for
  `external`-backend entries") and is correct today because `CliBackend.dispatch`/`.resume` always call
  `_crew_door_env` and `ExternalBackend.dispatch` never does — but it is a per-backend default, not a
  per-dispatch observation of whether binding actually happened. Not raised as a concern: no code path
  today calls `_crew_door_env` conditionally within the cli backend.

## Stop conditions hit
None. Both named pieces were buildable within `scripts/run_crew.py` alone; no third design decision arose.
`CliBackend`'s own entry construction needed no separate edit (see Exact diff note above) — this was
investigated, not assumed.

## Out-of-scope observations
- The banner text and the `door_bound` field are currently the only two places `crew-runs.json` /
  stderr state the hazard. Neither `verify_external_result` nor `recover_crews.py`'s classifier reads
  `door_bound` today (confirmed by the wiring grep below) — a natural follow-on would be surfacing
  `door_bound: false` in `recover_crews.py`'s human-facing report, but that is a new call site outside this
  gate's Allowed Scope (`build_entry`, `ExternalBackend.dispatch`, `CliBackend`'s entry construction, and
  `tests/`) and was not attempted.

## Wiring Grep
```
$ grep -rn "door_bound" --include=*.py .
./scripts/run_crew.py:921:      * `door_bound` — `True` only for `backend == "cli"` (the one path that
./scripts/run_crew.py:946:        "door_bound": backend == BACKEND_CLI,
./tests/test_crew_launcher.py:2252:    def test_build_entry_cli_door_bound_true(self):
./tests/test_crew_launcher.py:2256:        self.assertIs(True, entry["door_bound"])
./tests/test_crew_launcher.py:2258:    def test_build_entry_external_door_bound_false(self):
./tests/test_crew_launcher.py:2264:        self.assertIs(False, entry["door_bound"])
```
Count: 6 lines — 2 in `scripts/run_crew.py` (the docstring line and the one write site inside `build_entry`;
`ExternalBackend.dispatch` and `CliBackend.dispatch` both reach this write site through the shared
`build_entry` call, so there is exactly one write site, not two), 4 in `tests/test_crew_launcher.py` (my two
new tests). As expected per the handoff: no external readers exist yet — `door_bound` is a new observability
field the registry entry carries, not yet consumed by `recover_crews.py`, `verify_external_result`, or any
other caller.

## Deliverable Path Check
```
$ git check-ignore scripts/run_crew.py tests/test_crew_launcher.py; echo "exit:$?"
exit:1
```
Both deliverable files are tracked, not git-ignored.

## Map Impact
- **Structural anchors touched:** `scripts/run_crew.py:868-` `build_entry` (grew by ~15 lines: one new dict
  key + docstring paragraph; no signature change). `scripts/run_crew.py:1289-1310` (renumbered to
  ~1304-1366 after g1's earlier edit shifted line numbers) `ExternalBackend.dispatch` (grew by ~14 lines: one
  unconditional `print` call before `return`; no signature or return-type change).
- **Capabilities added/changed/affected:** every registry entry (`crew-runs.json`) now states its door-bound
  status explicitly; every external-backend dispatch now emits an unmissable stderr warning at record time.
  Both are pure additions — no existing capability's behavior changed.
- **Events added/changed/affected:** none.
- **Constraints/assumptions touched:** the handoff's Protected Intent ("the door must never SILENTLY read as
  bound when it is not") is now backed by two independent signals (registry field + stderr banner) instead
  of zero; the pinned prohibition against binding the door out-of-band (`scripts/mcp_spine_server.py`,
  `tests/test_mcp_identity.py:914`) was read, respected, and not touched.
- **Decision candidates / resolved decisions:** none new — the two-piece scope was pinned by the
  cold-critic-corrected handoff, not decided here.
- **Claims/evidence produced:** `door_bound` is a new claim surface (whether a given registry entry's
  backend binds its MCP door) with no external readers yet (see Wiring Grep) — a claim, not yet consumed.
- **Trust limitations / drift found:** none found; this gate does not change `finalize_from_exit_code`,
  `verify_external_result`, or any completion-judging logic — it only adds observability.
- **Triage candidates:** surface `door_bound: false` in `recover_crews.py`'s human-facing report (see
  Out-of-scope observations) — a natural follow-on, out of this gate's Allowed Scope.

## Workflow Feedback

- **Handoff gaps:** none of substance. The handoff's cold-critic correction (explicitly stating
  `ExternalBackend.dispatch` builds no prompt, and naming exactly where the two pieces belong) pre-empted the
  ambiguity a prior version apparently had; I did not need to re-derive that finding myself.
- **Context rediscovered:** had to read `CliBackend.dispatch`'s entry-construction call site (~1193-1199) to
  confirm it also goes through the shared `build_entry` and needed no separate edit — the handoff's Allowed
  Scope note ("`CliBackend`'s equivalent entry construction if `door_bound` needs setting there too — read
  both backends' entry-construction call sites before choosing where the field is actually set") correctly
  anticipated this check; confirming it cost one read, not a rediscovery.
- **Instructions improvised around:** none. The dispatch's explicit "no MCP spine door bound... build your
  own gated IMPLEMENTER_PLAN.json, drive it through the CLI checklist engine" instruction matched exactly
  what the environment presented (a `SPINE_FILE`/`SPINE_SESSION` pair bound to the parent Commander's own
  spine, not mine) — followed the dispatch's explicit override of the skill's default MCP-door guidance, as
  g1 did before me.
- **What would have made this easier:** nothing concrete — the corrected handoff was unusually precise about
  exactly where the two pieces belonged and why the original "crew prompt" framing was wrong.

## Return status
`complete`
