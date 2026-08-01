# Lessons Inbox

<!-- playbook-state: run-tick=33 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=issue-87,issue-99,issue-103,issue-106,issue-142,issue-140,issue-141,issue-143,issue-145,epic-138-audit,epic-178,epic-198-burndown,issue-227 -->

Transitory inbox for between-audit workflow signal — **not** a playbook, and not a
permanent home for any rule. Read the Active section at the Commander context step
and condition planning/handoff authoring on it. Never edit by hand or by LLM: apply
structured deltas via `apply_lessons_delta.py`, which enforces cap, grounding, and
counter rules.

Lessons are **transitory**. An audit *ends* every lesson it reads: the operative
content **graduates** into the permanent doc that owns it — a template, a skill's
doctrine section, a reference file, or a code-fix issue — and the lesson is then
**retired**; a lesson with no durable home is **deleted with a reason**. Nothing an
audit reads stays active. The `retire` op is the deletion path; a graduation is a
paired edit-plus-retire whose retire reason names the destination. Between audits,
new signal may be **added** here as staging, but this file is where lessons pass
through, not where they live.

Counter semantics split by scope: for most scopes a confirm is trust (the lesson
held again). For a constellation-scoped lesson it is the opposite — a recurrence of
an unfixed shared-machinery defect, so it accrues recurrences (debt) and flags
recurrence-debt. Pay the debt by exporting to CONSTELLATION_FEEDBACK and fixing
upstream, then retire it; do not keep confirming it into a permanent workaround.

## Active

### lesson:test-harness-concurrency-failsafe
- scope: project
- task-class: testing
- statement: Test harnesses that drive real concurrent file I/O (threads doing actual reads/writes, not mocks) need the same fail-safe discipline as the production code under test: wrap per-iteration work in try/except with a guaranteed stop-signal in `finally`, and mark helper threads daemon=True as a backstop. A writer thread that dies on a transient OS error without signaling stop leaves a non-daemon reader spinning forever and hangs the whole pytest process.
- grounding: crew-handoffs/180-result.md:98-112 (TF9 concurrency test hung pytest indefinitely on a transient Windows os.replace sharing violation; fixed by try/except + daemon threads; 7 total green re-runs after)
- bank-reason: single instance so far in this repo; no dedicated testing-conventions doc exists to graduate this into yet. A second concurrent-file-I/O test hang would confirm this as a repo-wide pattern worth minting a reference doc for, rather than a one-off fixed in place.
- mentions: 2
- confirmed: 1
- disconfirmed: 0
- status: active
- added: 2026-07-18 (epic-178)
- last-confirmed: 2026-07-19 (epic-198-burndown)
- runs-since-confirmed: 2
- history: confirmed 2026-07-19 (epic-198-burndown) — ADMIRAL_LOG PR#204 merge entry: #130 real-process-death test applied the concurrency-failsafe pattern again (kills a REAL runner process, concurrency-failsafe applied) on a new concurrent-I/O test — the lesson held and was needed a second time this epic.

### lesson:verify-launch-order-claims-against-code
- scope: project
- task-class: delegated-planning
- statement: A delegated commander must verify a launch order's NAMED defect/sub-fix against the current code (grep the named symbol/token) BEFORE planning — a headline mechanism already shipped becomes an honest-null, and the real live recurrence may be a different, unnamed sibling the prior fix never touched. Recurred across this epic: 152 heartbeat-on-mutate was already in #32 (honest-null caught by reconciling baseline vs code); 154's <epic-id> framing was already fixed by #173 while the real live defect was an unnamed token pair (<admiral-skill-dir>/<admiral-session-id>) found only by grepping the resolver vocabulary against shipped spine templates.
- grounding: staged-feedback/152-engine-verbs/lessons-delta.json (delegated-verify-subfix-against-code) + staged-feedback/154-init-placeholder/lessons-delta.json (verify-launch-order-defect-against-code-before-planning, which itself cites 152 as data point 1)
- bank-reason: Two data points this epic (waves 2 and 2B). Re-observe on a third delegated run whether launch-order baselines routinely overstate to-build work before promoting to a standing delegated-commander doctrine line.
- mentions: 3
- confirmed: 1
- disconfirmed: 0
- status: active
- added: 2026-07-19 (epic-198-burndown)
- last-confirmed: 2026-07-24 (issue-227)
- runs-since-confirmed: 1
- history: confirmed 2026-07-24 (issue-227) — .agent-work/epic-226/verdicts/commander-227.md section 1 — third data point. Item 1's headline 'full imperative verbatim (never elided)' was ALREADY TRUE at HEAD: current() had no slicing, textwrap, or ellipsis in its render path, and INV-2 purity already held because current() never called _check_condition. The genuine gap was the unnamed sibling — the conditions block. Verified by grep BEFORE planning per PR-7, which redirected the gate plan away from work that did not need doing.

### lesson:observe-midprocess-state-not-via-end-output
- scope: handoff
- task-class: test-authoring
- statement: When a handoff tells a crew to observe a MID-process state (e.g. a run stuck 'launched'), the observation channel must survive the very kill/hang being tested. Do NOT instruct discovery via END-of-process output (a stderr line printed in a finally / after the function returns): a hard tree-kill skips finally and a hanging subject never returns, so the channel never fires. Prefer a channel written before/independently of the death (a child-scoped TMP/TEMP dir, a pre-written meta path).
- grounding: staged-feedback/runner-durability-130/AGENT_FEEDBACK.md (implementer friction 2): handoff said discover the kept temp dir via a stderr line printed in finally; impossible under hang+tree-kill; crew pivoted to a child-scoped TMP/TEMP env.
- bank-reason: One occurrence (Windows hard tree-kill skipping the finally that prints the temp-dir line). Re-observe across other kill/detach/timeout test handoffs before hardening the handoff template.
- mentions: 2
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-19 (epic-198-burndown)
- last-confirmed: none
- runs-since-confirmed: 2

### lesson:verify-harness-field-and-drive-real-writer
- scope: project
- task-class: testing
- statement: When a hook or decision depends on a harness-supplied payload field (e.g. a Stop-hook's cwd), verify the field's presence against the harness contract (docs) AND make the regression test drive the REAL writer path that populates it (run handle_post_tool_use to write the binding, then decide_stop), not a hand-injected fixture. A hand-set fixture asserts the field is present and passes green even if production never delivers it, hiding a silent no-op fix.
- grounding: staged-feedback/stop-rail-151/lessons-delta.json + plan-critic-disposition.md Finding 1 (cold critic: fix rode an unverified assumption that Stop carries cwd; injected-cwd unit tests pass green even if prod lacks it).
- bank-reason: Second testing-discipline data point this epic alongside test-harness-concurrency-failsafe (re-applied #204). Banked as staging for the pending needs-human graduation of both into a testing-conventions doc; if the human defers that graduation, re-observe a third harness-field-masked-by-fixture instance first.
- mentions: 2
- confirmed: 1
- disconfirmed: 0
- status: active
- added: 2026-07-19 (epic-198-burndown)
- last-confirmed: 2026-07-24 (issue-227)
- runs-since-confirmed: 1
- history: confirmed 2026-07-24 (issue-227) — .agent-work/issue-227/execute.json g2-implement constraint 3 + the cold-critic finding it encodes. INV-1's oracle would have been self-confirming had the verb->required-args map been walked from argparse required=True: 'advance --why' and 'attest --evidence' are required at RUNTIME (advance()'s why-capture block; attest()'s artifact branch) but OPTIONAL at the parser, so the map would have omitted exactly the two arguments agents most often read source to discover, and the test would have passed green while current() still failed the caller. The map was hand-authored against the verb bodies instead, and the test drives an artifact-kind postcondition and a non-exempt gate.

### lesson:execute-the-advice-a-test-asserts-on
- scope: project
- task-class: test-authoring
- statement: When a change's deliverable is GENERATED ADVICE — a hint, recovery line, or next-step suggestion naming a runnable command — the test must EXECUTE that advice and assert it does not refuse, over fixtures parameterized on every dimension the advice depends on. String-matching the rendered text is not evidence. In issue-227 gate g3 this failure recurred FOUR times with one root cause: the fixtures could not express the failing state. Single-task fixtures made a non-active gate structurally impossible, and a guard gate hardcoded to 'pending' hid the two active-gate statuses where the advice was wrong, so each fix was validated against a world where its own bug could not exist. The Commander's independent 640-combination sweep also came back clean because it shared the fixtures' blind spot; only a multi-gate fixture exposed it.
- grounding: .agent-work/issue-227/results/g3-review-result.md (three BLOCK verdicts across rework rounds 1-3) + .agent-work/issue-227/execute.json g3-implement rework_count=3/3 + .agent-work/epic-226/verdicts/commander-227.md section 3
- bank-reason: The four data points are all one surface (checklist_engine.py recovery lines), so the SCOPE is genuinely open: re-observe on a different generated-advice surface to learn whether this generalizes to any generated artifact, or specifically to advice that names runnable commands. That distinction decides whether the doctrine line belongs in crew test-authoring guidance broadly or only where a test asserts on emitted commands.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: deferred
- added: 2026-07-24 (issue-227)
- last-confirmed: none
- runs-since-confirmed: 1
- deferred-at: 0
- history: deferred 2026-07-24 (issue-227) at 0 — needs human — the fix target is project doctrine (crew test-authoring guidance, a .md edit), and per the feedback step a doctrine apply carries authority=human; a delegated Commander does not self-apply doctrine. My launch order additionally forbids any doctrine edit beyond item 6's two named riders, making this a float. Applied THIS run at the code and structural-record level instead (RecoveryRunnabilityAudit + fixtures parameterized over status and position + a standing-hazard note in docs/CHECKLIST_ENGINE_DESIGN.md), so the mitigation is live where it bites; only the generalized doctrine line awaits a human ruling. Surfaced to the Admiral in commander-227.md section 7.
