# Implementation Result

## Assigned gate
`g1` — issue #604, telemetry-never-fatal.

## Completed slice

The MCP door's two telemetry writes can no longer fail a tool call or kill the server.
Both writes in `_log` are guarded against `OSError`; each drop is reported on `stderr`
with the record that was lost. A committed regression test drives the real server as a
subprocess and fails on the unfixed tree.

Committed as `0060dc08`.

**The count the close criteria asked for.** An independent `ast.walk` pass over
`scripts/mcp_spine_server.py` — run by me, not taken from the handoff — finds **four**
filesystem write call sites in the module:

| line | write | before this gate |
|---|---|---|
| `:181` | `CALLLOG.open("a")` in `_log` | **unguarded — mine** |
| `:184` | `START_MARKER.write_text` in `_log` | **unguarded — mine** |
| `:492` | `REJECTIONLOG.open("a")` in `_log_rejection` | already guarded, `try/except OSError` at `:494` |
| `:535` | `path.write_text` in `_write_amend_delta` | already guarded at its call site `:1289-1294` |

The other write calls the AST pass returns are `StringIO`, `sys.stderr` and `sys.stdout`
writes, not filesystem. **Both unguarded writes were mine and both are now guarded.**
`_log` has exactly **one** call site, `:461`, outside `run_engine`'s own `try/except`
(`:445-458`) — confirmed by `grep -n "_log(" scripts/mcp_spine_server.py`.

## Scope

**Files changed:**
- `scripts/mcp_spine_server.py` — `_log` and one new helper beside it; no other function
  touched.
- `tests/test_mcp_door_telemetry.py` — new, 262 lines, 7 tests.

Both are committed and neither is ignored (`git check-ignore` exits 1).

**Specific exclusions touched:** no. `_identity_violation`, `checklist_engine.py`,
`scripts/hooks/**`, `run_crew.py`, `gauge_reader.py`, `.mcp.json`, the import-time
`SPINE`/`ENGINE` reads at `:145-147`, `examples/mcp-interactive-demo/**`,
`install_constellation.py` and the Commander spine template are all untouched — the
diff is two files.

## Behavior changed

Yes. An `OSError` from either telemetry write used to unwind the process: the client
saw no reply, just a closed connection, and the server exited 1. Now the record is
dropped, the drop is reported on `stderr`, and the call is answered.

Unchanged on purpose: the `SPINE_CALLLOG` / `SPINE_START_MARKER` / `SPINE_REJECTION_LOG`
environment overrides (`tests/test_mcp_lifecycle.py:102-103` depends on them, and it
passes), and the start-marker semantics — still written on first successful engine call.

## Map Impact

- **Structural anchors touched:** `scripts/mcp_spine_server.py:180-219` — `_log` guarded
  and documented; one new module-private helper `_report_dropped_telemetry` inserted
  directly above it. `run_engine`'s call site `:461` is unchanged: the fix is inside
  `_log`, so nothing about the caller's contract moved.
- **Capabilities affected:** door telemetry — the call log and the start marker. Both are
  now best-effort: written when writable, reported and dropped when not. The door's
  answer no longer depends on either.
- **Constraints/assumptions touched:** `constraint:stdout-is-the-protocol-channel` —
  honored and now measured (post-fix probe: 2 stdout lines, both JSON-RPC 2.0, zero
  non-protocol lines, while both telemetry writes were failing).
  `constraint:env-overrides-for-log-paths-must-survive` — honored; the overrides are how
  the new test arranges its unwritable destinations, so the test would break if they were
  dropped.
- **Decisions resolved:** `decision:telemetry-never-fatal` — implemented as given. Two
  choices inside my authority, both recorded in the plan's `why_trail`: the two writes are
  guarded **separately**, not by one `try` around the body, because they are independent
  side-channels and one being unwritable must not suppress the other; and the drop report
  goes through one helper rather than two inline copies of `_log_rejection`'s shape.
- **Claims/evidence produced:** `claim:604-kills-the-server` — reproduced with its exit
  code and then shown not reproduced with its exit code (**EXIT 1 → EXIT 0**, same probe,
  same target). Evidence files listed below.
- **Trust limitations / drift found:** `map/ids.jsonl` is tracked but 0 bytes, so no map
  anchor resolves anywhere in this repo. Everything above is read from source, never from
  a map claim. This is the handoff's `tc1` and it is still open.
- **Triage candidates:** two, below under Out-of-scope observations.

## Test mode

**Required:** test-first, for the regression test.
**Satisfied:** yes — the test was written first, observed failing on the unfixed tree,
and the failure captured before the guard was written. It was then re-measured against
the **final** test file (see below), because I corrected one assertion after the first
red run.

## Evidence

All measurements clear `__pycache__` first.

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
  tests/test_mcp_door_telemetry.py tests/test_mcp_spine_server.py tests/test_mcp_identity.py \
  tests/test_mcp_lifecycle.py tests/test_mcp_door_engine_cwd.py tests/test_mcp_friction_capture.py
```

**Result:** pass — `96 passed, 10 subtests passed in 5.59s`, run against the committed
tree. The five MCP test files the handoff names are in there; the sixth is the new one.

**The probe, before and after.** Same command, same target, same missing directory
(`/home/tommy/projects/constellation-skills/.agent-work/epic-418-followon` still does not
exist — verified this run):

```bash
py .agent-work/cleanup-a-door/door_probe.py \
  /home/tommy/projects/constellation-skills/.agent-work/epic-418-followon/spine.json
```

| | RESULT | EXIT |
|---|---|---|
| pre-fix, at `a69bbac4` | `(the server never answered the call)` | **1** |
| post-fix, this run | the door answered `spine_status` | **0** |

The post-fix answer is `isError: true` naming the missing spine file. That is the
engine's own truth surfaced through a live door instead of a dead process. Fail-closed
wording for the missing/unbound case is gate g3's lane (#603), not this one.

Full output: `.agent-work/cleanup-a-door/evidence/post-fix-probes.txt`.
Baseline: `.agent-work/cleanup-a-door/evidence/pre-fix-probes.txt`.

**`stdout` stays pure JSON-RPC** while both telemetry writes fail — measured, not
inferred, in the same evidence file:

```
stdout lines examined: 2  non-JSON-RPC lines: 0
stderr carried 2 telemetry-drop report(s)
EXIT 0
```

This one needed its own measurement: the test's stdout-purity assertion **passes pre-fix
too**, because a dead door's stdout is empty and therefore trivially pure. It is
confirmatory, not load-bearing.

## TDD evidence, if required

- **Failing test observed** — demonstrated, not asserted. `scripts/mcp_spine_server.py`
  restored to its pre-fix blob with `git checkout b9135f1b -- scripts/mcp_spine_server.py`,
  and the revert **asserted** (`grep -c _report_dropped_telemetry` → `0`,
  `git diff --stat HEAD` non-empty) before measuring:

  ```
  $ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_mcp_door_telemetry.py
  FAILED …::test_an_unwritable_call_log_does_not_suppress_the_start_marker
  FAILED …::test_call_log_that_is_a_directory_is_not_fatal
  FAILED …::test_call_log_under_a_missing_directory_is_not_fatal
  FAILED …::test_start_marker_alone_being_unwritable_is_not_fatal
  FAILED …::test_the_dropped_record_is_reported_on_stderr
  5 failed, 2 passed in 0.34s
  EXIT 1
  ```

  Each failure carries the `FileNotFoundError` traceback through `_log` at `:181`/`:184`
  and `run_engine` at `:461` — the exact mechanism the handoff diagnosed. Captured in
  full at `.agent-work/cleanup-a-door/evidence/red-test.txt`, together with the revert
  assertion.

  **Naming the pre-fix commit is load-bearing, and I got it wrong once.** After the fix
  was committed, a re-measurement using `git checkout --` restored the file from my own
  fix commit and reported `7 passed` under a header claiming it had measured the unfixed
  tree. Caught by reading the output instead of the intent; redone against
  `b9135f1b` explicitly, with a `grep -c` assertion that now guards it. The captured file
  says so in its own header, because the next person to re-measure will reach for the same
  wrong command.

- **Passing test observed:** `7 passed in 0.32s` on the same file with the guard in.

- **The separate guards are pinned by a check that can fail.** The choice to guard the two
  writes independently is a claim about behaviour, so it is measured, not just documented:
  collapsing them into one `try` around `_log`'s body — mutation asserted, anchor text
  matched — turns `test_an_unwritable_call_log_does_not_suppress_the_start_marker` and
  `test_the_dropped_record_is_reported_on_stderr` red (`2 failed, 5 passed`). Appended to
  the same evidence file.

- **Which two pass pre-fix, and why that is fine:**
  `test_stdout_stays_pure_json_rpc_when_telemetry_fails` (a dead door's stdout is empty,
  so it is trivially pure) and `test_healthy_run_writes_both_telemetry_files` (the positive
  control — it exercises the writable path, which was never broken). The five that
  discriminate are the five that go red.

- **The gate's own reason for existing, confirmed:** the handoff notes that on the unfixed
  tree the plan's pytest postcondition reports `89 passed` — a check that reads identically
  in the healthy and the defective world. With this file added, the same suite selection
  reads `5 failed` there. The check can now fail.

- **Refactor while green:** no.

## Docs/contracts touched

None. The change is module-private: one new module-private helper and a rewritten `_log`
body, both documented in place in the file's own dense-docstring style. No public
interface and no schema moved.

Blast radius enumerated by command rather than from memory:
`grep -rn "mcp_calls\|START_MARKER\|SPINE_CALLLOG" docs/ skills/` returns **zero** hits —
nothing outside `scripts/` and `tests/` asserts anything about these two channels, so
there is no doc to bring along.

## Wiring grep

The handoff said `none — this slice adds no new callable symbol`, and offered the
alternative if I factored the guard into a helper. I did, so here it is:

```
$ grep -n "_report_dropped_telemetry" scripts/mcp_spine_server.py
180:def _report_dropped_telemetry(target: Path, exc: OSError, lost: str) -> None:
214:        _report_dropped_telemetry(CALLLOG, exc, line)
219:        _report_dropped_telemetry(START_MARKER, exc, f"start marker for {SPINE}")
```

**Count: 2 call sites outside the definition**, both in `_log`, one per guarded write.
It is exercised by every failing-telemetry test in the new file and by the post-fix probe.

## Assumptions

- **The two writes are guarded separately, not as one block.** Guarding the whole `_log`
  body once would mean an unwritable call log silently suppresses the start marker as
  well. They are independent side-channels; I treated them as such, and
  `test_an_unwritable_call_log_does_not_suppress_the_start_marker` pins it — verified by
  mutation, not by reading. My first draft of this section claimed the *existing*
  start-marker test defended the split; it does not — a shared guard passes it — so I
  added the test that does.
- **`OSError` is the whole catch width**, per the handoff's authority. `sys.stderr.write`
  itself is not guarded: if the transport's own stderr is broken there is no channel left
  to report on, and swallowing that would be the silent drop this gate exists to prevent.
- **One assertion in my test was wrong and I corrected it green-side.** The first draft
  grepped stderr for `spine_status`; the door logs the **engine verb** `current`, not the
  tool name, so it failed after the fix. The corrected test parses the lost record back
  out of the stderr line and asserts on `verb`/`code` — a test of what was reported, not
  of how it was worded. The red evidence was then re-measured with the corrected file, so
  the captured red is the final test's red.

## Stop conditions hit

None. Allowed scope was not exceeded, no exclusion was touched, the regression test does
fail pre-fix, and no decision outside the granted authority came up.

## Out-of-scope observations

Two triage candidates, neither fixed:

1. **`main()` still catches only `KeyError` around the dispatch (`:1355`, `:1360`).** This
   gate removed the one known way a non-`KeyError` reaches that frame, but it did not make
   the frame itself safe: any future unguarded `OSError` — or any other exception — inside
   `call_tool` still kills the process and presents to the client as a closed connection.
   The class-level fix is a top-level handler in `main()` that answers the in-flight
   request with a JSON-RPC error and keeps the loop alive. That is a behaviour change to
   the protocol surface with its own review, and it is outside this gate's allowed scope.
2. **`map/ids.jsonl` is tracked and 0 bytes** — the handoff's `tc1`. `map_orient.py`
   resolves no anchor for any area in this repo, so every crew in this epic is working
   from source with a `DEGRADED-UNPARSEABLE` orientation. Confirmed again this run.
3. **`git checkout -- <path>` is a silent no-op for pre-fix re-measurement once the fix is
   committed**, and it also stages what it restores — which quietly dropped my source fix
   out of an `--amend` until I read the committed blob back. Both are foot-guns for the
   red-before-green discipline this repo runs on, and neither is named in
   `docs/agents/CREW_CONTEXT.md`'s Verification Discipline section, which does tell you to
   assert the mutation applied but not which command silently fails to apply it. A two-line
   addition there — name the pre-fix commit, and re-read the commit rather than the
   worktree — would have saved both mistakes.

## Workflow Feedback

- **Handoff gaps:** one, and small. **Required Evidence** item 2 asks me to "paste both
  exit codes" for the probe, and the **Close Criteria** ask for the write count — but
  neither says *where* that goes, and the **Return Format** field list does not name an
  evidence-file path the way **Delivery** names the result path. I put both in this
  document and in `evidence/post-fix-probes.txt`; a reviewer looking only at one of them
  would find them, but that is luck rather than instruction. Naming the evidence directory
  in Return Format would fix it.
- **Context rediscovered:** none of consequence — the handoff's Map Anchors section did
  the work a map would have. Its `:180-184` / `:441-462` / `:472-499` / `:1322-1377` line
  spans were all accurate at `b9135f1b`, which is what let me skip re-deriving the
  mechanism as instructed. The one thing I dug up myself was the test harness shape:
  `tests/test_mcp_friction_capture.py`'s `McpRpcClient` is the closest existing analogue
  (real subprocess, `PATH`-only hermetic env, the same two log overrides) and the handoff
  does not point at it, though it does point at `_log_rejection` as the *source* shape to
  reuse. One more line — "and its test is the harness shape" — would have saved a search.
- **Instructions improvised around:** the implementer skill says to drive the bound spine
  when `SPINE_FILE`/`SPINE_SESSION` are in the environment, and not to author a plan of my
  own. Here the bound spine is the **Commander's** `execute` spine, leased by
  `commander-cleanup-a-door`, whose ACTIVE step is Commander work. Driving it would have
  been wrong, so I read it with `spine_status`, left it alone, and authored my own plan at
  `.agent-work/cleanup-a-door/crew-plans/g1-implementer-plan.json`, driving it through
  `checklist_engine.py` directly. The skill's rule reads as though a dispatched crew gets
  its **own** bound spine; what a crew actually inherits is the parent's. That is worth a
  sentence in the skill, because the two readings lead to opposite actions.
- **The Stop hook fires a false mid-flight warning at a crew.** On my way out it reported
  `SPINE MID-FLIGHT: gate execute is still open` and told me to keep driving it. That gate
  is **yours** — `execute`, leased by `commander-cleanup-a-door` — and the hook only saw it
  because a dispatched crew inherits the parent's `SPINE_FILE`. Obeying it would have meant
  seizing your lease and doing your job; its "honest stop" branch (`block` or `waive`) is no
  better, since I am not blocked and the gate is not mine to block. I verified my own plan
  reads `DONE: no open items` with the lease released, confirmed the result artifact exists
  and is fresh, and stopped. **The hook needs to compare the spine's lease owner against its
  own session id and stay quiet when they differ** — otherwise every crew in this epic ends
  its run against a warning that instructs it to take over its Commander's spine, and one
  that follows the instruction will corrupt the run rather than fail visibly.
- **What would have made this easier:** the plan template's `IMPLEMENTER_RESULT` shape and
  the handoff's Return-status rule disagree on the status line's form — the template writes
  `## Return status` with a bare value beneath, and nothing else in the corpus says so. My
  own plan check initially demanded `**Return status:** <value>`, and satisfying both would
  have put the same value in the artifact twice. I amended my check to read the template's
  shape (recorded in the plan's `amendments`). Pinning one form in the template and
  quoting it in the handoff would remove the ambiguity.

## Return status
complete
