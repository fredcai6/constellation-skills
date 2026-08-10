# Triage — issue #424 (workstream F of epic #418)

Ten candidates, all routed. **Every one is `recommend-and-defer`.** No issue was filed and none was
fixed inside the run.

**Why nothing was fixed now.** Two candidates (T7, T8) clear all four rungs of the fix-now ladder.
They are still deferred, because the launch order overrides the ladder: *"Cheap fixes found mid-wave
are **routed, not implemented** inside a wave under measurement."* Workstream F is still open until
archive, so both are routed with the constraint named as the reason.

**Why nothing was filed.** `LAUNCH_ORDER-424-continuation.md` grants no issue-filing authority. It
scopes the run to six done-conditions, fences the files, and says "closing any issue" is excluded; it
never authorises opening one. Per delegated-mode doctrine, the `user-decision` at this step records
**the deferral**, not a filing approval — none was sought and none was given.

---

## T1 — `run_crew.py` cannot resolve a multi-segment work-id

**Classification:** `bug`, `tooling`
**Source:** this run's own dispatch loop; discrepancy `D5` in `REPLAN_INPUT.json`
**Structural anchor:** `skills/commander/scripts/run_crew.py`

### Observations

**Observation 1**
- **What's wrong:** `--verify-result` and `--resume` refuse with `cannot verify: no crew recorded
  with session name '...'` for any work-id containing a `/`. `load_registry_for_resume()` parses the
  work-id as `session.split("/")[1]`, so
  `constellation/epic-418-followon/commander-424/g1/implementer/attempt-1` resolves to work-id
  `epic-418-followon` and looks for `.agent-work/epic-418-followon/crew-runs.json`, which does not
  exist. The registry is at `.agent-work/epic-418-followon/commander-424/crew-runs.json`.
- **Expected:** the session name's work-id segment is reassembled to the full work-id, so the
  registry that recorded the crew is the registry consulted. `save_registry` already gets this right
  — it uses `entry["work_id"]` — so the read and write paths disagree.
- **Conditions:** any work-id with a `/`. Linux, this repo, the Agent-tool harness with
  `--dispatch external`. Recording a crew works fine; only resolution by session name fails.
- **Type:** `measured` — ran `--verify-result` against both inherited `g1` entries and got the
  refusal; read `load_registry_for_resume()` to confirm the cause; then created a read-side symlink
  `.agent-work/epic-418-followon/crew-runs.json -> commander-424/crew-runs.json` and watched every
  subsequent `--verify-result` in this run succeed.
- **Rev:** `/home/tommy/.claude/skills/constellation-commander/scripts/run_crew.py` as installed at
  the time of this run (branch `epic-418/f-424-mcp-door` at `05b35a2e`).

**Observation 2 — the consequence, which is worse than the refusal**
- **What's wrong:** two completed `g1` crews sat in `crew-runs.json` with `status: "running"` and
  `completed_at: null`, with both result artifacts already on disk. The predecessor could not close
  them, so the registry misreported finished work as live.
- **Expected:** a crew whose result artifact exists and is fresh is marked `completed`.
- **Conditions:** the predecessor dispatched both crews successfully; only the verification step
  failed, silently leaving the entries open.
- **Type:** `measured` — observed directly in `crew-runs.json` at the start of this run;
  `recover_crews.py` classified both `COMPLETE` from the artifacts while the registry still said
  `running`, which is the contradiction.
- **Rev:** the inherited work area at branch commit `33f4b3e6`.

### Possible fix
Reassemble the work-id from all segments between `constellation/` and the trailing
`<gate>/<role>/attempt-N`, e.g. `"/".join(parts[1:-3])`. For it to work, the session-name grammar
must be fixed at exactly three trailing segments — which `session_name()` guarantees today, but the
fix should assert it rather than assume it.

### Open questions
- Should `recover_crews.py` and `run_crew.py` share one session-name parser? They disagree today:
  `recover_crews.py` classifies these crews correctly while `run_crew.py` cannot find them, which is
  why the defect presents as confusing rather than obviously broken.

**Recommended priority:** `high`
**Reason:** it silently converts completed crews into apparently-running ones, and the next dispatcher
sees a false conflict. Multi-segment work-ids are the epic/commander convention, so this is the normal
path, not an edge case.

**Related artifacts:** `crew-runs.json`; `STATE_NOTE.md` (records the workaround)
**Disposition:** `recommend-and-defer` — `run_crew.py` is outside this run's file fence and no
issue-filing authority was granted.
**Issue creation authority:** `issue-ready only`

---

## T2 — `verify_iterative_role_artifacts.py` rejects a multi-segment work-id before verifying anything

**Classification:** `bug`, `tooling`
**Source:** this run's `execute` closeout
**Structural anchor:** `skills/commander/scripts/verify_iterative_role_artifacts.py`

### Observations

**Observation 1**
- **What's wrong:** `verify_iterative_role_artifacts.py commander --work-id
  epic-418-followon/commander-424` exits 1 with `REFUSED: work-id contains unsafe path characters`.
  `_work_area()` guards the id with `SAFE_ID = ^[A-Za-z0-9][A-Za-z0-9._-]*$`, which forbids `/`.
- **Expected:** the packet is verified against the G2 schema. This command is the `execute` step's
  own command postcondition in the shipped Commander spine, so on any multi-segment work-id that
  postcondition can never pass.
- **Conditions:** any work-id with a `/`; the guard fires before any file is read.
- **Type:** `measured` — ran the exact command, exit 1, no verification performed. Confirmed the
  cause by reading `_work_area()`.
- **Rev:** installed skills at the time of this run.

**Observation 2 — the guard was masking a real schema violation**
- **What's wrong:** the inherited `REPLAN_INPUT.json` had `completed_outcomes` as an array of
  **strings**, where G2 requires objects with `issue_id`/`outcome`/`evidence`. The path refusal fired
  first, so this was never reported.
- **Expected:** `input.completed_outcomes[0] must be an object` — which is exactly what the
  verification says once it is allowed to run.
- **Conditions:** present in the packet from the predecessor's run onward; invisible for as long as
  the path guard fired first.
- **Type:** `measured` — called `verify_replan.verify_replan_input()` on the packet directly and got
  the violation; repaired the packet and re-ran to `OK`.
- **Rev:** `REPLAN_INPUT.json` at branch commit `8b4e99ef`.

### Possible fix
Validate each **path segment** against `SAFE_ID` rather than the whole id, which keeps the
traversal protection (`..`, absolute paths, empty segments) while allowing the epic/commander
convention. The guard's purpose is path safety, and per-segment validation preserves it exactly.

### Open questions
- How many other role verifiers share `_work_area()`? If all of them do, no delegated Commander under
  an epic has ever had this postcondition actually execute — which would make the failure mode
  "silently never checked" rather than "loudly refused", and worth knowing.

**Recommended priority:** `high`
**Reason:** a check that cannot run is worse than no check: it reported REFUSED while a genuine schema
violation sat behind it undetected. Same defect class as T1, in a second tool — which suggests the
single-segment work-id assumption is systemic rather than local.

**Related artifacts:** `evidence/verify_replan_input.py` (the equivalent check on an explicit path);
the `amend` audit entry on `spine.json` recording the `retext-check`
**Disposition:** `recommend-and-defer` — outside the file fence; no filing authority.
**Issue creation authority:** `issue-ready only`

---

## T3 — `code_map build` cannot see an unstaged new file, and says so nowhere

**Classification:** `missing doc`
**Source:** g3 implementer result (triage candidate 1); independently rediscovered by the g1-rework
implementer
**Structural anchor:** `scripts/code_map/discovery.py`

### Observations

**Observation 1**
- **What's wrong:** `python -m scripts.code_map build --root .` silently ignores a newly created file
  that has not been `git add`ed, producing an empty diff that reads exactly like "nothing to update".
  The enumerator is `git ls-files`.
- **Expected:** either the new file is included, or the build says which files it skipped and why.
- **Conditions:** any freshly created, unstaged source file; documented only inside
  `discovery.py`'s own docstring.
- **Type:** `measured` — both crews ran the rebuild, saw an empty diff, and only found the cause by
  reading `discovery.py`; staging first then produced the expected map change.
- **Rev:** branch `epic-418/f-424-mcp-door` at `50fb7987` and again at `fda35ec0`.

### Possible fix
One line in the build command's `--help` and in whichever doc introduces `code_map`: "stage new files
before rebuilding — discovery enumerates tracked files." A warning when the working tree contains
untracked `.py` files under a scanned root would be stronger, but is a behaviour change.

**Recommended priority:** `medium`
**Reason:** it cost two separate crews a wasted cycle in one run, and the failure is silent — a user
can ship a stale map believing they rebuilt it, with the freshness test green because the map matches
the tracked corpus.

**Disposition:** `recommend-and-defer` — no filing authority granted this run.
**Issue creation authority:** `issue-ready only`

---

## T4 — a Task-tool subagent inherits its dispatching process's entire MCP scope

**Classification:** `research hardening`
**Source:** gate g3's live experiment; discrepancy `D9`
**Structural anchor:** `scripts/mcp_spine_server.py`, `.mcp.json`

### Desired behavior
- **Desired:** a documented, deliberate answer to "what identity does a Task-tool-dispatched crew
  carry?", so a future design that needs distinct identities per crew starts from evidence.
- **Today instead:** a Task-tool subagent inherits its dispatching process's **entire**
  `--strict-mcp-config` scope and reaches the parent's exact spine and session identity with no
  configuration of its own. Per-dispatch identity scoping is therefore per **top-level process**, not
  per agent-turn.
- **Type:** `measured` — a live `claude -p --mcp-config <generated> --strict-mcp-config` dispatch whose
  spine imperative carried an unguessable per-run nonce; the top-level agent and its Task-tool
  subagent both returned the same nonce, reproduced twice with independent nonces, corroborated by
  exactly two `current` entries per run in the server's own `mcp_calls.jsonl`.
- **Rev:** Claude Code 2.1.226, Linux, branch at `50fb7987`.

### Open questions
- The experiment cannot distinguish "the subagent reused the same server connection" from "the
  subagent independently re-resolved the identical config and got its own process bound to the same
  identity". Both give the same answer to the question that mattered here, but they differ for a design
  that wants per-crew identities.
- The repo's existing crew-dispatch pattern (each crew its own `claude -p`) already sidesteps this.
  That assumption is now evidenced rather than assumed, and is worth confirming before anything
  depends on it.

**Recommended priority:** `medium`
**Reason:** not a defect, but a load-bearing fact that is currently recorded only in this run's
evidence. It is exactly the fact a later agent would misread as justification to rebuild
`gen_mcp_config.py` — which is why the do-not-reintroduce note is already in
`docs/CHECKLIST_ENGINE_DESIGN.md`.

**Related artifacts:** `crew-plans/scratch-g3-live/`; `crew-handoffs/g3-implementer-result.md`
**Disposition:** `recommend-and-defer`
**Issue creation authority:** `issue-ready only`

---

## T5 — the engine cannot express "resolve a blocked gate on a later gate's evidence"

**Classification:** `architecture weakness`
**Source:** this run's g1/g3 ordering repair; discrepancy `D6`
**Structural anchor:** `scripts/checklist_engine.py`

### Observations

**Observation 1**
- **What's wrong:** a `blocked` gate holds the active slot, so no later gate can start
  (`REFUSED: g3-implement is not the active gate; start 'g1-integrate' first`), and `amend` refuses to
  move it because it only touches `pending` gates. When the evidence that clears a block lives at a
  later gate, there is no legal ordering that reaches it.
- **Expected:** either a way to set a blocked gate aside while its evidence is gathered, or a
  documented pattern for the situation. Today the only engine exits from `block` are `resume` and
  `skip` (OBE), and neither fits "still needed, evidence pending elsewhere".
- **Conditions:** a plan that records a claim at one gate and its evidence at a later one. The
  predecessor named this as its own plan defect before it hit it.
- **Type:** `measured` — attempted `start g3-implement` and got the refusal; read `amend`'s
  pending-only guard and the `block`/`resume`/`skip` exits.
- **Rev:** `scripts/checklist_engine.py` at `05b35a2e`.

### Possible fix
None proposed with confidence. The cheapest real mitigation is probably not an engine change at all
but a planning rule: at plan time, verify no gate's postcondition depends on a later gate's evidence.
The Commander's existing "enumerate the ownership scope against the authored gates before freezing the
plan" step is the natural place for it.

### Open questions
- Is this worth an engine change, or is it correctly a plan smell the engine should keep refusing?
  A gate that cannot close on its own evidence is arguably a mis-cut gate, and making it easy to work
  around may be the wrong fix.

**Recommended priority:** `low`
**Reason:** the workaround is straightforward once understood (gather the evidence as blocker
resolution, then reorder the pending tail by `amend`), and the underlying situation is a planning
error the engine is arguably right to make awkward.

**Disposition:** `recommend-and-defer`
**Issue creation authority:** `issue-ready only`

---

## T6 — two spines in one session share a session id, distinguished only by free-text `claimed_by`

**Classification:** `bug`
**Source:** inherited from `MISSION_FRAME.md`; confirmed reproducible by the g3 implementer
**Structural anchor:** `scripts/checklist_engine.py` (lease identity)

### Observations

**Observation 1**
- **What's wrong:** the engine accepts a lease claim carrying an inherited session id, so two
  different spines driven from one harness session both hold leases under the same id, differing only
  in the free-text `claimed_by` field. Lease identity is not actually distinguishing the two holders.
- **Expected:** two concurrent holders of two different spines are distinguishable by identity, not by
  a descriptive string a caller chooses.
- **Conditions:** any harness session driving more than one spine. Every crew this Commander
  dispatched shares one session id.
- **Type:** `measured` — observed directly across this run's own spines; the g3 implementer confirmed
  it reproduces trivially and recorded it as real rather than hypothetical.
- **Rev:** branch at `05b35a2e`.

### Open questions
- This is **not** DC3 and was deliberately kept separate from it. DC3 is about the door — whether an
  unconfigured subagent reaches the parent's *server instance*. This is about the engine's lease
  semantics. DC3 went green while this stayed red, correctly, and no engine change was made to force
  a test to pass.

**Recommended priority:** `medium`
**Reason:** real and confirmed, but explicitly out of workstream F's scope and untouched here by
instruction. Whoever scopes the engine-side fix should know it is confirmed rather than suspected.

**Disposition:** `recommend-and-defer` — out of F's scope by the launch order; no filing authority.
**Issue creation authority:** `issue-ready only`

---

## T7 — stale file-count in `tests/test_mcp_imperative_equivalence.py`'s header comment

**Classification:** `cleanup`
**Source:** g2 reviewer result
**Structural anchor:** `tests/test_mcp_imperative_equivalence.py`

### Observations

**Observation 1**
- **What's wrong:** the test file's own header comment states a file/template count of 19/7 where the
  actual discovered population is 20/8.
- **Expected:** the comment matches what the code discovers, or omits the count and lets the assertion
  carry it.
- **Conditions:** present as committed.
- **Type:** `measured` — the g2 reviewer compared the comment against the discovery function's live
  output.
- **Rev:** branch at `696caaea`.

**Recommended priority:** `low`
**Reason:** cosmetic, and the count is asserted at runtime, so the comment cannot mislead the test —
only a reader.

**Disposition:** `recommend-and-defer` — **clears all four fix-now rungs**, deferred solely because the
launch order forbids implementing cheap fixes inside a wave under measurement.
**Issue creation authority:** `issue-ready only`

---

## T8 — unused `import shutil` in `tests/test_mcp_spine_server.py`

**Classification:** `cleanup`
**Source:** g2 reviewer result
**Structural anchor:** `tests/test_mcp_spine_server.py`

### Observations

**Observation 1**
- **What's wrong:** `shutil` is imported and never used. Pre-existing, not introduced by this run's
  rework.
- **Expected:** no unused imports.
- **Conditions:** present as committed.
- **Type:** `measured` — the g2 reviewer read the file and confirmed no reference.
- **Rev:** branch at `fda35ec0`.

**Recommended priority:** `low`
**Reason:** trivial.

**Disposition:** `recommend-and-defer` — same reason as T7: fix-now eligible, blocked by the launch
order's routed-not-implemented constraint.
**Issue creation authority:** `issue-ready only`

---

## T9 — the gauge staleness guard makes a naive governor test silently unmeasurable

**Classification:** `missing doc`
**Source:** this run's first DC6 arm; recorded as UNMEASURED in `MEASUREMENT.md`
**Structural anchor:** `scripts/checklist_engine.py` (gauge reading), `scripts/gauge_reader.py`

### Observations

**Observation 1**
- **What's wrong:** a `gauge.json` written **before** the lease claim is declined with `CONTEXT GAUGE
  DECLINED: the reading ... was sampled 17s BEFORE session '...' claimed this checklist`. The guard is
  correct. But a test that seeds a gauge and then dispatches an agent produces a run in which **no
  threshold instruction is ever emitted**, and the agent's ordinary drive to done looks exactly like
  "the agent ignored the governor".
- **Expected:** the failure mode is discoverable by the test author. It is discoverable — the decline
  message is explicit and appears in the tool result — but only if someone reads the server call log
  rather than the agent's behaviour.
- **Conditions:** any governor test that seeds the gauge before the claim. Reproduced here on the
  first DC6 arm; the re-run wrote the gauge after the claim and the instruction was emitted.
- **Type:** `measured` — compared `dc6-mcp/mcp_calls.jsonl` (decline, no instruction, agent drove to
  done) against `dc6b-mcp/record.jsonl` (instruction in 2 of 33 tool results, agent acted on it).
- **Rev:** branch at `8b4e99ef`.

### Possible fix
A note wherever governor testing is described: seed the gauge **after** the claim, or the reading is
correctly declined as a predecessor's. The engine needs no change — the guard is doing its job.

### Open questions
- Separately, and worth its own look: in the re-run the agent **acted on** the HARD instruction
  (attached a `refresh-request`, advanced with a `--why` handoff) but ignored its "and stop" half,
  then drove four more gates, attaching a fresh `refresh-request` at each. Whether that is an agent
  compliance problem or an instruction-wording problem is not settled here. The door delivered the
  text faithfully, so it is not a door defect.

**Recommended priority:** `medium`
**Reason:** this exact trap turned a governor measurement into a silent null once already in this run.
Reported as UNMEASURED rather than as a negative, which is the only reason it did not become a false
finding.

**Related artifacts:** `evidence/g4-dc5/dc6-mcp/`, `evidence/g4-dc5/dc6b-mcp/`, `MEASUREMENT.md`
**Disposition:** `recommend-and-defer`
**Issue creation authority:** `issue-ready only`

---

## T10 — the episode writer and the episode capture gate cannot both be satisfied for a multi-segment work-id

**Classification:** `bug`, `tooling`
**Source:** this run's `feedback` step
**Structural anchor:** `skills/commander/scripts/apply_episode_delta.py`,
`skills/commander/scripts/verify_episode_captured.py`

### Observations

**Observation 1**
- **What's wrong:** the two tools demand contradictory values for the same field.
  `apply_episode_delta.py` validates `mechanical.run` against `RUN_RE = [a-z0-9][a-z0-9-]*`, which
  forbids `/`, and refuses `create.mechanical.run: '...' must be kebab-case` otherwise.
  `verify_episode_captured.py <work-id>` passes only when some active episode's `- run:` line **equals
  the work-id verbatim**. For `epic-418-followon/commander-424` the writer cannot emit the string the
  gate requires, so the `feedback` step's command postcondition — which the shipped Commander spine
  builds from the work-id — cannot pass no matter what is captured.
- **Expected:** an episode captured for this run satisfies this run's capture gate.
- **Conditions:** any work-id containing `/`. The gate reported `BLOCKED — no episode in
  episodes/active records run 'epic-418-followon/commander-424' (95 episode(s) scanned)` while six
  episodes for this very run sat in the store.
- **Type:** `measured` — wrote `run: epic-418-followon-commander-424` (the only form the writer
  accepts), applied six episodes successfully, then ran the gate with the work-id verbatim and got
  BLOCKED; ran the same gate with the kebab form and got `6 episode(s) recorded`, exit 0.
- **Rev:** installed skills at the time of this run; store at branch commit `8b4e99ef`.

### Possible fix
Either relax `RUN_RE` to permit `/` between kebab segments, or have the capture gate normalise the
work-id the same way the writer must. The second is smaller but leaves two places encoding one
convention. Whichever is chosen, the writer and the gate should share the normaliser rather than each
carrying its own rule.

### Open questions
- This is the **third** instance of the same defect family in one run, after T1 (`run_crew.py`) and T2
  (`verify_iterative_role_artifacts.py`). Three independent tools encode "a work-id is one path
  segment" while the epic/commander convention always nests one. Is that better fixed tool by tool, or
  by giving the corpus one work-id type with one parser and one normaliser?

**Recommended priority:** `high`
**Reason:** it makes a shipped spine step's postcondition unsatisfiable for every delegated Commander
under an epic. Unlike T1 and T2 it has no workaround inside the tools' own contracts — the two
requirements are mutually exclusive.

**Related artifacts:** `episodes/active/epic-418-followon-commander-424-00{1..6}.md`;
the `amend` audit entry on `spine.json` recording the `retext-check` of `feedback.c1`
**Disposition:** `recommend-and-defer` — both tools are outside this run's file fence and no
issue-filing authority was granted.
**Issue creation authority:** `issue-ready only`
