# Review Result

> Written per `constellation-how-to-talk`.

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3-review` — DC2 separation and DC3 inheritance-fails-closed acceptance tests for the MCP front door (`tests/test_mcp_identity.py`), issue #424 workstream F.

## Result
APPROVE

## Handoff compliance
The handoff asked for independent verification of both done-conditions against the **net** state of `tests/test_mcp_identity.py` (commit 50fb7987 plus the g1-rework in fda35ec0), with the DC3 trap named explicitly. Verified against the net diff (`git diff origin/main`), both commits individually, and the implementer's result file in full. Every numbered close criterion in the handoff was driven as its own checklist item (`r7`..`r18`) through the engine survey at `.agent-work/epic-418-followon/commander-424/g3-review/review.json` — all 19 items recorded pass, consolidated APPROVE.

## Scope drift
Clean. `git diff origin/main --stat` shows only `.mcp.json`, `scripts/mcp_spine_server.py`, `tests/test_mcp_identity.py`, `tests/test_mcp_spine_server.py`, `map/INDEX.md`, plus workbench artifacts under `.agent-work/`. The five fenced files (`install_constellation.py`, `test_feedback_tooling.py`, `test_install_constellation.py`, `test_run_skill_eval.py`, `test_spine_rail.py`) show zero diff. `scripts/checklist_engine.py` shows zero diff — no engine lease semantics were touched to make a test pass. `settings.json` untouched at every scope checked. Issue #424 confirmed still `OPEN` (`gh issue view 424`). `docs/agents/*` zero diff.

## Evidence verdict
Holds under adversarial, not just cooperative, verification. Summary of what I did myself, not what the report claimed:

**DC3's trap — the positive control genuinely gates the assertion.** `assert_door_is_up_and_serving()` raises real `AssertionError`s and sits in the assertion path twice for the class that matters: once in `DC3InheritanceMechanismTests.setUp` (a setUp failure errors every test in the class — not bookkeeping a passing test can bypass), and again inline inside `test_subagent_with_no_special_configuration_gets_no_identity_never_the_parents` itself, after the subagent's no-reply is observed and before the parent's own lease is re-asserted. Red-then-green is real: three independently-distinguishable manipulations (server-path-not-found, `KeyError`/`SPINE_FILE` missing, up-but-wrong-content), each with proof of cause beyond "it raised" (exit code + literal stderr text), plus one green case.

**Mutate and watch (DC3).** I patched `scripts/mcp_spine_server.py:114` from `SPINE = Path(os.environ["SPINE_FILE"]).resolve()` to a version that falls back to a hardcoded identity when `SPINE_FILE` is unset — the exact leak DC3 exists to prevent. Result: precisely 2 of 12 tests went red — `test_control_is_red_when_the_config_never_delivered` and, critically, `test_subagent_with_no_special_configuration_gets_no_identity_never_the_parents` itself (`'SPINE_FILE' not found in stderr`). The other 10, including DC2 and DC3's other three positive-control cases, stayed green. Precise sensitivity, not blast radius. Restored (`git checkout`), confirmed `git diff` empty, reran 12/12 green.

**Mutate and watch (DC2 collision).** I separately patched the same line to ignore `SPINE_FILE` entirely and always point at one hardcoded shared spine file. All 5/5 DC2 tests went red, including the collision-control test's own "GREEN contrast" half, which collapsed because even its "separate" files were secretly the same shared one — proof the collision control is not vacuous. Restored, confirmed clean, reran 12/12 green.

**DC2 concurrency is genuine.** `ServerInstance.send()` never reads a reply — it writes and returns immediately, so the 25-round interleave genuinely has two requests in flight before either reply is consumed; a sequential driver could not produce it. The `threading.Barrier(2)` test asserts `max(start_A, start_B) < min(end_A, end_B)` — a real window-intersection check, not "both existed at some point."

**DC2 separation is genuine.** `write_marked_spine()` embeds distinguishing marker *content*, not just a distinguishing path, and the lease test corroborates via the raw JSON files directly (`engine_session` present on A's file, absent entirely on B's), not just the server's text projection.

**Mechanism distinctness.** The module and class docstrings explicitly separate DC3 (the door/env seam) from the CLI/engine-lease shared-session-id fact and from the product-internal Task-tool-connection-reuse question, naming each boundary and pointing the latter at the IMPLEMENTER_RESULT rather than smoothing it over.

**The g1-rework (fda35ec0) did not weaken anything.** Diffed it directly: only `DC3InheritanceMechanismTests.setUp`'s *parent construction* changed (shelling out to the now-deleted `gen_mcp_config.py` → building the parent directly via `ServerInstance`, matching every other class in the file). The subagent-side no-identity assertion — the actual DC3 claim — is byte-for-byte unchanged, and my own mutation above independently proves it is still sensitive. No guarantee weakened.

**No blocking read, no hang.** All three `.stderr.read()` calls are their own statement, each preceded by a `proc.wait(timeout=10)` on the same object (process already reaped), never inline inside an eagerly-evaluated assertion f-string — the g1 hang pattern is absent. Full suite completed in 97s with no hang.

**Full suite.** Independently reran: `2172 passed, 1 skipped, 1061 subtests passed, 0 failed` — matches the handoff's stated current-tree baseline exactly.

**Live DC3 experiment (scratch evidence, not the committed deliverable).** `nonce.txt`/`nonce2.txt` match `dispatch_stdout.json`/`dispatch2_stdout.json` verbatim in both runs. `mcp_calls.jsonl`'s *current* state (2 lines, both `verb: current`, both carrying run 2's nonce) independently corroborates run 2's exact call count from server-side ground truth. **Gap found:** the call log was cleared/reused between run 1 and run 2, so run 1's own 2-call state was not separately preserved — I can independently verify run 2's count but not run 1's from retained artifacts (logged as a triage candidate, tc2 below; not a defect in the committed suite). The implementer's stated limit on the YES (cannot distinguish literal connection-reuse from independent re-resolution of an identical config) is honestly stated and I found no downstream over-read of it — the Commander's own M2 inference in `g1-implementer-handoff-rework.md` ("a generated config is also bound at server-launch, per process — it can no more give an in-session Task-tool subagent its own identity than `${VAR}` can") is a correctly-scoped inference by mechanism symmetry, explicitly attributed as the Commander's own call, not an implementer overclaim.

## Code/doc quality
Fowler pass: 12/12 smells rendered, `verify_fowler_pass.py` exits 0. Four flagged, all non-blocking: `long-method` (two ~48-line integration tests, each scoped to one real scenario), `duplicated-code` (a "process crashed for the intended reason" check pattern repeats ~3x, worth a small helper), `long-parameter-list` (`ServerInstance.__init__` takes 7 params, mostly defaulted), `speculative-generality` (`extra_env` on `ServerInstance` is wired up but never passed by any caller in this file — real, unexercised generality). None weaken DC2/DC3 guarantees. Full record: `.agent-work/epic-418-followon/commander-424/g3-review/fowler-pass.json`.

## Map impact verdict
- **Evidence supports claimed change:** yes — verification-only, no production code changed; the implementer's Map Impact notes match (structural anchors touched are read-only exercises of `mcp_spine_server.py`/the deleted `gen_mcp_config.py`).
- **Constraints not violated:** yes — `constraint:no-duplicated-engine-logic` (checklist_engine.py diff empty), `constraint:cli-door-stays`, `constraint:settings-json-untouched` all re-verified.
- **Notes match the diff:** yes.
- **Decision candidates surfaced:** yes — the implementer correctly surfaced the per-top-level-process (not per-agent-turn) scoping finding as new information for the Commander rather than resolving it unilaterally.
- **Durable context routed:** yes, plus one gap I found independently (below).

## Reconciliation check
One real gap, non-blocking for this gate: `MISSION_FRAME.md` lines 94–98 still states "`gen_mcp_config.py` still earns its place... Per-dispatch generation is justified by identity and separation... Grade: settled/measured, on the corrected basis." That passage predates and is now contradicted by M1 (a single shared `.mcp.json` binding one `SPINE_FILE`/`SPINE_SESSION` for every consumer is not what ships — `${VAR}` expansion sources identity from the caller's environment) and M2 (this gate's own live experiment), and by the code itself (the file it says "earns its place" was deleted at fda35ec0). It was never regraded. `STATE_NOTE.md`'s own framing of the same facts is correct and current — the two documents now disagree. Flagged as tc1 below; this is Commander's decision record to reconcile, not a defect in `tests/test_mcp_identity.py`.

## Blockers
- none

## Out-of-scope observations
- **tc1** — `MISSION_FRAME.md`'s decision-anchor text for `gen_mcp_config.py` is stale and self-contradicting relative to `STATE_NOTE.md` and the current code; see Reconciliation check above. Worth reconciling before this gate's chain closes.
- **tc2** — The live g3 DC3 experiment's `mcp_calls.jsonl` was cleared/reused between run 1 and run 2, so only run 2's server-side call-log corroboration is independently reproducible from retained scratch evidence today. Not a defect in the committed suite (scratch evidence, not `tests/`), but worth a convention for future live-experiment evidence: snapshot the call log between reproduction runs instead of clearing it in place.
- **tc3** — Carried forward, confirmed real, not fixed here (from the implementer's own out-of-scope observations): (1) `scripts/code_map/discovery.py` silently misses untracked new files (`git ls-files` enumerator) with no warning; (2) Task-tool subagents inherit their dispatching process's entire `--strict-mcp-config` scope (per-top-level-process, not per-agent-turn) — a future workflow wanting distinct spine identities per Task-tool-dispatched crew within one Commander run would need each dispatch to be its own separate `claude -p` invocation.

## Workflow Feedback
Mandatory section, filled honestly.

- **Handoff gaps:** none of substance. The handoff was unusually precise about exactly where to press (the DC3 trap, the mutate-and-watch instruction, the exact stated limit to check for over-read) — that precision is what made the mutation tests fast to design correctly on the first try.
- **Context rediscovered:** the `gen_mcp_config.py` removal's full justification chain (M1 in `g1-implementer-handoff-rework.md`, M2 in this gate) isn't summarized in one place — I had to read `g1-implementer-handoff-rework.md`, `STATE_NOTE.md`, and `MISSION_FRAME.md` separately to see that the last of the three had gone stale relative to the other two. A single "decision ledger" reference in the handoff (even just "also check MISSION_FRAME.md's own gen_mcp_config.py justification for staleness") would have made that check less incidental to reach.
- **Instructions improvised around:** none. The mutate-and-watch instruction was concrete enough to execute directly against `scripts/mcp_spine_server.py:114` without guessing at intent.
- **What would have made this easier:** the live experiment's `mcp_calls.jsonl` being cleared between run 1 and run 2 meant I could only independently corroborate one of the two claimed reproductions from retained artifacts (tc2). A convention of copying the log to `mcp_calls_run1.jsonl` / `mcp_calls_run2.jsonl` instead of clearing in place would make a "reproduced twice" claim fully self-evidencing for the next reviewer, not partially.

## Return status
`complete`
