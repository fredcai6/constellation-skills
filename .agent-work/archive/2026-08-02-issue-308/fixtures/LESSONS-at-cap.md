# Lessons Inbox

<!-- playbook-state: run-tick=40 cap=20 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=issue-87,issue-99,issue-103,issue-106,issue-142,issue-140,issue-141,issue-143,issue-145,epic-138-audit,epic-178,epic-198-burndown,epic-226-lessons-audit,governor-261,governor-269,governor-268,governor-265,303,299,issue-309 -->

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
- runs-since-confirmed: 9
- history: confirmed 2026-07-19 (epic-198-burndown) — ADMIRAL_LOG PR#204 merge entry: #130 real-process-death test applied the concurrency-failsafe pattern again (kills a REAL runner process, concurrency-failsafe applied) on a new concurrent-I/O test — the lesson held and was needed a second time this epic.

### lesson:verify-launch-order-claims-against-code
- scope: project
- task-class: delegated-planning
- statement: A delegated commander must verify a launch order's NAMED defect/sub-fix against the current code (grep the named symbol/token) BEFORE planning, AND verify that any named EDIT TARGET (a section heading, file path, or anchor) actually exists at the named address — a headline mechanism already shipped becomes an honest-null, and a named-but-nonexistent edit target is a naming slip, not a build task. Recurred across two epics: 152/154 (mechanism-already-shipped, unnamed-sibling-token-pair); epic-226 wt-227 (mechanism-already-shipped, twice); epic-226 wt-230 (named edit target 'the Decision Anchors section of commander-core.md' does not exist under that name).
- grounding: staged-feedback/152-engine-verbs/lessons-delta.json (delegated-verify-subfix-against-code) + staged-feedback/154-init-placeholder/lessons-delta.json (verify-launch-order-defect-against-code-before-planning, which itself cites 152 as data point 1)
- bank-reason: Two data points this epic (waves 2 and 2B). Re-observe on a third delegated run whether launch-order baselines routinely overstate to-build work before promoting to a standing delegated-commander doctrine line.
- mentions: 9
- confirmed: 6
- disconfirmed: 0
- status: active
- added: 2026-07-19 (epic-198-burndown)
- last-confirmed: 2026-08-01 (issue-309)
- runs-since-confirmed: 1
- history: confirmed 2026-07-24 (epic-226-lessons-audit) — .agent-work/epic-226/verdicts/commander-227.md section 1 (item 1's imperative-elision and INV-2 purity halves already shipped at HEAD, caught by grep-before-plan)
- history: confirmed 2026-07-24 (epic-226-lessons-audit) — .agent-work/epic-226/verdicts/commander-230.md 'Workflow feedback' point 1 — third data point, NEW failure mode: the launch order named 'the Decision Anchors section of commander-core.md', which does not exist under that name.
- history: amended 2026-07-24 (epic-226-lessons-audit) — epic-226 wt-230's widening proposal (.agent-work/harvest-226/230/lessons-delta.json op confirm, field proposed-widening), corroborated by wt-227's confirm of the original mechanism-check half in the same wave. (was: A delegated commander must verify a launch order's NAMED defect/sub-fix against the current code (grep the named symbol/token) BEFORE planning — a headline mechanism already shipped becomes an honest-null, and the real live recurrence may be a different, unnamed sibling the prior fix never touched. Recurred across this epic: 152 heartbeat-on-mutate was already in #32 (honest-null caught by reconciling baseline vs code); 154's <epic-id> framing was already fixed by #173 while the real live defect was an unnamed token pair (<admiral-skill-dir>/<admiral-session-id>) found only by grepping the resolver vocabulary against shipped spine templates.)
- history: confirmed 2026-08-01 (301) — .agent-work/301/evidence/problem-statement.md 'Baseline verified against code': grep -ril for episode/stratum/rhyme returned ZERO hits before planning, settling the already-shipped question as fact. Negative result (premise held), but the check is what made it known rather than assumed.
- history: confirmed 2026-08-01 (300) — .agent-work/300/PROBLEM_STATEMENT.md section 'Baseline verified against code before planning': LAUNCH_ORDER-300 and the confirmed spec both describe 'the spine's existing gate-note loading' as the partially-grounded starting point to extend. Grepping first showed the grounding covers deterministic SELECTION only (engine `current` = render_human(state(cl)), spine-keyed, contract-versioned) and that ASSEMBLY does not exist at all -- canonical Markdown is named only inside imperative prose and opened by hand. Fourth data point, and a THIRD distinct failure mode alongside mechanism-already-shipped and named-but-nonexistent-edit-target: here the named baseline exists but is materially WEAKER than the order's framing implies, which would have produced an extension gate against a mechanism that was never there. Spec assumption 5 is correspondingly weaker than it reads.
- history: confirmed 2026-08-01 (299) — .agent-work/299/PROBLEM_STATEMENT.md 'Baseline verified against code before planning' + BASELINE_RECORD.md section 'What this arm is'. FIFTH data point, and a FOURTH distinct failure mode: not mechanism-already-shipped, not named-but-nonexistent-target, not weaker-than-framed, but a settled/human pre-ruling whose LABEL is contradicted by the corpus itself. f1Brainz CLAUDE.md:7 already names docs/architecture/index.md as the canonical entrypoint, so the order's 'no canonical entrypoint' arm label is false and what the epic is actually testing is a contract, not an entrypoint. Also corrected: corpus size 5928 -> 6435, and the ruling's stated evidence (both docs/architecture mentions in commander doctrine are the absent-map fallback at reconcile, not an instruction to read a map).
- history: confirmed 2026-08-01 (issue-309) — issue-309: the plan's first draft (MISSION_FRAME.md) inherited a stale premise not from the launch order's own text but from a DIFFERENT frozen project doc the launch order pointed at as the map substitute (docs/EPISODE_STORE.md section 1's git-check-ignore transcript for .agent-work/, accurate when written at #301 g1, invalidated by the unrelated #326 commit that made .agent-work/ tracked repo-wide). git check-ignore -v caught it before any seeded file was at risk.

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
- runs-since-confirmed: 9

### lesson:verify-harness-field-and-drive-real-writer
- scope: project
- task-class: testing
- statement: When a hook or decision depends on a harness-supplied payload field (e.g. a Stop-hook's cwd), verify the field's presence against the harness contract (docs) AND make the regression test drive the REAL writer path that populates it (run handle_post_tool_use to write the binding, then decide_stop), not a hand-injected fixture. A hand-set fixture asserts the field is present and passes green even if production never delivers it, hiding a silent no-op fix.
- grounding: staged-feedback/stop-rail-151/lessons-delta.json + plan-critic-disposition.md Finding 1 (cold critic: fix rode an unverified assumption that Stop carries cwd; injected-cwd unit tests pass green even if prod lacks it).
- bank-reason: Second testing-discipline data point this epic alongside test-harness-concurrency-failsafe (re-applied #204). Banked as staging for the pending needs-human graduation of both into a testing-conventions doc; if the human defers that graduation, re-observe a third harness-field-masked-by-fixture instance first.
- mentions: 6
- confirmed: 5
- disconfirmed: 0
- status: active
- added: 2026-07-19 (epic-198-burndown)
- last-confirmed: 2026-07-27 (governor-268)
- runs-since-confirmed: 5
- history: confirmed 2026-07-24 (epic-226-lessons-audit) — .agent-work/harvest-226/227/lessons-delta.json op confirm (INV-1 oracle hand-authored against verb bodies, not argparse-derived, avoiding self-confirmation)
- history: confirmed 2026-07-24 (epic-226-lessons-audit) — .agent-work/harvest-226/232/lessons-delta.json op confirm (g2's regression test drives the real post-fix _write_meta to produce an actual meta.json, then truncates real bytes, independently reproduced by the reviewer in an isolated scratch tree)
- history: confirmed 2026-07-27 (governor-261) — notes-261.md 'Empirical finding' section: docs confirmed cwd is present on every hook event, but a real (non-fixture) reproduction showed the field's SCOPE was wrong -- session-lifetime-fixed, not per-call-live -- for a Commander-in-worktree dispatch. Presence and liveness turned out to be different questions; verifying presence alone would have shipped a design (cwd-routing, considered and rejected mid-run per the Admiral's own ruling) that was a provable no-op. Two isolated real claim calls (one with no cd prefix, pwd-confirmed) established this, not a fixture.
- history: confirmed 2026-07-27 (governor-269) — notes-269.md 'Live evidence' section: this run's own ordinary tool calls fired real PostToolUse hooks during a live Commander dispatch into an isolation-verified worktree; the main checkout's .spine-rail-binding.json gained an entry for THIS session's own spine keyed to a main-checkout path, with 'worktree': the main checkout -- a fresh, non-fixture, independent reproduction of the CLAUDE_PROJECT_DIR pinning defect for #269 specifically (distinct from wave-1's #202/#261 cwd-based reproduction). Also confirmed directly: CLAUDE_PROJECT_DIR read as empty from this session's own Bash and PowerShell tool subprocess environments, live, not injected.
- history: confirmed 2026-07-27 (governor-268) — AGENT_FEEDBACK.md 'Friction / unclear' section, governor-268: after the surgical edit, actually confirmed on disk (via ls/Bash, not by reading the diff or trusting the launch order's prose) that skills/workbench/templates/STATE_NOTE.template.md exists and .agent-work/templates/ is absent in this fresh worktree -- an independent real re-check of the fallback claim, not an inference from the edit itself.

### lesson:round-trip-tests-prove-artifacts-not-parsers
- scope: project
- task-class: testing
- statement: A round-trip test that lints/parses the REAL shipped artifacts proves those artifacts are clean — it does not prove the parser/tool itself is correct. Bugs unreachable from the shipped artifacts pass it silently. Pair every round-trip/enumeration test over real artifacts with adversarial fixtures authored to make the tool return a WRONG answer (false FAIL on a valid input, silent PASS on an invalid one), and instruct reviewers to hunt that specific class rather than only re-running the suite.
- grounding: .agent-work/epic-226/verdicts/commander-230.md 'Workflow feedback' point 3 (grade_lint.py: 18 shipped tests including a four-template round-trip all passed while a greedy-placeholder regex silently PASSED an ungraded decision and a nested sub-bullet false-FAILed a valid plan, both unreachable from the shipped templates)
- bank-reason: Two data points already in hand this epic (see paired confirm below) but neither is a repeat of the SAME tool — round-trip-blindness in a linter (grade_lint) vs. an exclusion-set enumeration (checklist_engine). Banking to see whether a third instance is the same shape before promoting to standing reviewer-handoff doctrine.
- mentions: 4
- confirmed: 3
- disconfirmed: 0
- status: active
- added: 2026-07-24 (epic-226-lessons-audit)
- last-confirmed: 2026-08-01 (300)
- runs-since-confirmed: 2
- history: confirmed 2026-07-24 (epic-226-lessons-audit) — .agent-work/epic-226/verdicts/commander-227.md 'crew-reported friction' g3-reviewer round-3 entry: Inv3ExclusionCheck claimed totality on the excluded-verb set while exercising only 4 of 10, surviving rounds 1-2 of the same rework loop hunting exactly this class of defect
- history: confirmed 2026-08-01 (301) — Held twice, each time catching a real silent-wrong-answer that a green suite hid. g2: the line-boundary guard rejected only backslash-n and backslash-r while parse_episode() uses str.splitlines(), so a U+2028 value passed validation, forged the exact status line the guard existed to prevent, and silently truncated the record — found only because the reviewer was told to AUTHOR adversarial inputs rather than re-run the suite. g3: select_episodes() did set(values), so a bare string degraded to character membership and the most natural caller idiom returned the wrong episode.
- history: confirmed 2026-08-01 (300) — .agent-work/300/PLAN_CRITIC_DISPOSITION.md finding S7 plus .agent-work/300/execute.json g2-implement.c3: the candidate plan had promoted a same-tree regenerate-and-compare round trip to a HARD postcondition while the discriminating cross-environment check was a `check: null` self-attestation -- check strength inverted against the plan's own stated evidence hierarchy, in a plan whose constraints array already quoted this very lesson. Third instance and a NEW failure mode: not a round-trip test that fails to catch a bug, but a round-trip test promoted ABOVE the discriminating evidence in the same plan that cites the lesson. Fixed by restating c3 as necessary-not-sufficient and making the cross-environment check mechanical.

### lesson:checklist-engine-from-child-relative-path-and-gated-vs-survey
- scope: constellation
- task-class: commander / checklist engine gate-execution
- statement: checklist_engine.py's `advance <gate> --from-child <path>` (1) refuses a path to the child checklist given relative to cwd, only accepting an absolute path, unlike every other engine verb used in these runs; (2) only works when the child checklist is a SURVEY type (it has a `consolidation` object to attach as review-result) -- attempting it against a GATED-type child (e.g. execute.json, which has no consolidate step) refuses with 'has no consolidation yet', forcing a manual attest+advance instead. Neither behavior is documented in --help or the gate-execution doctrine text, and the REFUSED message itself names neither rule.
- grounding: .agent-work/harvest-226/228/lessons-delta.json op add (id checklist-engine-from-child-relative-path-and-gated-vs-survey) + .agent-work/harvest-226/231/lessons-delta.json op add (id from-child-refusal-undiscoverable-from-error, same defect, folded in per the confirm below) + .agent-work/epic-226/ADMIRAL_LOG.md 2026-07-24 RULING 'apply-a-lesson' (Admiral's own pre-resolution)
- bank-reason: Constellation-scoped shared-machinery defect; banked pending an upstream engine fix (REFUSED message naming the rule inline). Exported this run per the export op below — do not keep confirming into a permanent workaround.
- mentions: 2
- confirmed: 0
- disconfirmed: 0
- recurrences: 1
- status: exported
- added: 2026-07-24 (epic-226-lessons-audit)
- last-confirmed: 2026-07-24 (epic-226-lessons-audit)
- runs-since-confirmed: 8
- history: recurred 2026-07-24 (epic-226-lessons-audit) (constellation debt, not trust) — .agent-work/harvest-226/231/lessons-delta.json op add (id from-child-refusal-undiscoverable-from-error) -- SIBLING-FORK RESOLUTION applied here per the Admiral's own 2026-07-24 RULING: this is wt-231's independent rediscovery of the identical defect in the same wave, landed as a confirm (recurrence-debt) rather than a second add, preserving one stable identity for the recurrence counter.
- history: exported 2026-07-24 (epic-226-lessons-audit) — Two independent worktrees (wt-228, wt-231) hit the identical defect in one wave -- graduation weight per the constellation counter semantics (confirm = debt, not trust). See the ready CONSTELLATION_FEEDBACK.md entry in this delta's accompanying prose (Queued for Human Review section) for the text to append.

### lesson:harvest-before-sweep-enforcement-gap
- scope: constellation
- task-class: general-workflow / closeout
- statement: Doctrine already states 'harvest first, then remove' (constellation-admiral/SKILL.md Closeout step 4) but nothing mechanically checks it before a worktree sweep. A staged-feedback/<work-id>/ trio that passes its own Commander's feedback/archive gate (which verifies only the STAGING copy) looks identical to 'harvested and merged into the durable log' from the outside, but is not the same thing.
- grounding: epic-226 ADMIRAL_LOG.md 2026-07-25 'HARVEST EXECUTED'/'HARVEST MANIFEST' entries (this epic's own preventive, extra-diligence workaround) + cross-project sweep candidate 0cc4eefd032c (f1Brainz epic-601: 6/6 staged trios were the sole surviving copy of their worktrees' learning before a human caught it and hand-merged)
- bank-reason: Constellation-scoped, code-targeted (verify_agent_feedback.py harvest-completeness mode) -- banked pending the upstream fix; exported this run.
- mentions: 2
- confirmed: 0
- disconfirmed: 0
- recurrences: 1
- status: exported
- added: 2026-07-24 (epic-226-lessons-audit)
- last-confirmed: 2026-07-24 (epic-226-lessons-audit)
- runs-since-confirmed: 8
- history: recurred 2026-07-24 (epic-226-lessons-audit) (constellation debt, not trust) — Second independent occurrence in the same evidence window: f1Brainz epic-601's real data-loss-narrowly-averted event, corroborating epic-226's own preventive workaround as more than an abundance of caution.
- history: exported 2026-07-24 (epic-226-lessons-audit) — Two independent epics, two independent Admirals, same gap, in the same audit window -- see the ready CONSTELLATION_FEEDBACK.md entry in the Queued for Human Review section for the text to append.

### lesson:cold-critic-mandatory-for-measurement-dependent-plans
- scope: project
- task-class: delegated-planning
- statement: Run the cold plan critic as MANDATORY, not bias-to-yes/optional, for any gate plan whose acceptance depends on a before/after measurement or a required round-trip/parser test. Two commanders this epic independently found it caught a plan-invalidating defect before any crew was dispatched: wt-227 (g3's over-read baseline would have been unproducible after g1/g2 overwrote the engine) and wt-230 (an undefined Markdown decision-line grammar would have broken the issue's own required round-trip test).
- grounding: .agent-work/epic-226/verdicts/commander-227.md section 7 + .agent-work/epic-226/verdicts/commander-230.md 'Workflow feedback' point 3
- bank-reason: Two convergent recommendations in one epic, but neither has a directly-attributable rework-count (both are pre-crew catches with no counterfactual). Re-observe a third convergent recommendation, or a case where skipping the cold critic on a measurement-dependent plan actually cost rework, before hardening plan-step doctrine.
- mentions: 4
- confirmed: 3
- disconfirmed: 0
- status: active
- added: 2026-07-24 (epic-226-lessons-audit)
- last-confirmed: 2026-08-01 (issue-309)
- runs-since-confirmed: 1
- history: confirmed 2026-08-01 (300) — .agent-work/300/PLAN_CRITIC_DISPOSITION.md, findings B1 and B4: the cold plan critic found TWO postconditions that returned exit 0 at HEAD with nothing built. B1's `! A || B` bound the bash negation to the collection probe rather than to the lint, so the one condition whose stated purpose was 'prove the guard fires on bad input' was satisfied by never writing the guard; B4's `grep -qi 'context' docs/CHECKLIST_SCHEMA.md` already matched 10 lines. Both reproduced independently by the Commander before acting. This is a third convergent data point and the first with a directly-attributable counterfactual: without the critic, issue #300's plan would have frozen with two vacuous acceptance checks. The plan's acceptance depends on a cross-environment determinism measurement and on lint/parser tests -- exactly the class the lesson names.
- history: confirmed 2026-08-01 (299) — .agent-work/299/PLAN_CRITIC_DISPOSITION.md — 8 blocking + 9 serious findings on a frozen measurement rubric, 14 fixed before the freeze. FOURTH data point and the first where the critic caught a defect in the MEASURING INSTRUMENT rather than the plan: B4 (an absent source read recorded with the literal reserved for an absent map read, with the self-test asserting the defect) and B6 (field extraction exercised only against input.command while real transcripts use file_path/pattern) would together have turned total instrument failure into a clean-looking NO-MAP-READ finding across all five runs. Directly attributable counterfactual: without the critic this arm would have been captured, been unrecoverable, and read as a strong result.
- history: confirmed 2026-08-01 (issue-309) — issue-309's own plan (a recall/noise measurement, squarely the trigger class): PLAN_CRITIC_DISPOSITION.md, 2 BLOCKING + 3 SERIOUS findings, all fixed or mitigated before dispatch (see the confirm above for the two BLOCKING ones). Directly attributable counterfactual: without the critic, both would have shipped as vacuous acceptance evidence for the sweep's headline recall/noise numbers and the #321 fix's own test proof.

### lesson:windows-subprocess-env-does-not-shadow-path-resolution
- scope: project
- task-class: testing / windows subprocess probing
- statement: On Windows, passing a restricted env={'PATH': ...} into subprocess.run() does NOT shadow which executable an unqualified command name resolves to -- CreateProcess resolves the executable name against the CALLING process's real environment, not the child env= dict. A test that wants to genuinely make a candidate executable unresolvable must mutate the ambient os.environ['PATH'] directly, not pass a restricted env= override -- the latter looks correct but silently passes even when the probe logic is completely broken.
- grounding: .agent-work/harvest-226/228/lessons-delta.json op add; verdicts/commander-228.md 'Acceptance evidence' (two pasted py -c transcripts empirically comparing env={'PATH': d} vs mutating os.environ['PATH'] directly)
- bank-reason: Single occurrence, discovered empirically on one host/Windows build. Banking to see whether another Windows subprocess-probing surface hits the same trap before promoting to a doctrine/comment note.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-24 (epic-226-lessons-audit)
- last-confirmed: none
- runs-since-confirmed: 8

### lesson:prove-command-fails-postcondition
- scope: handoff
- task-class: general-workflow
- statement: A gate that must prove a command CORRECTLY FAILS (e.g. "the guard refuses this input") does not fit the engine's command-postcondition semantics (exit 0 = pass). A `! <command>` bash-negation wrapper as the postcondition's `command` field makes "the guard fired" a mechanically re-verified engine check instead of a self-reported attest.
- grounding: .agent-work/harvest-226/229/lessons-delta.json op add; AGENT_FEEDBACK.md 2026-07-24 issue-229 entry
- bank-reason: One data point from one Commander run -- needs to recur on a second gate/issue that also needs to prove a command fails before this is confidently a template-worthy pattern rather than a one-off improvisation.
- mentions: 2
- confirmed: 1
- disconfirmed: 0
- status: active
- added: 2026-07-24 (epic-226-lessons-audit)
- last-confirmed: 2026-08-01 (303)
- runs-since-confirmed: 3
- history: confirmed 2026-08-01 (303) — execute.json gate m2-fixtures: 3 command postconditions using `! py scripts/verify_spec_confirmed.py <fixture> --phase confirm`, all satisfied on first advance (no rework); notes-303.md 'm2' section records the verbatim commands/exit codes/stderr the wrapper mechanically re-verified.

### lesson:canonical-routing-can-dissolve-a-file-fence
- scope: handoff
- task-class: delegated-planning
- statement: When a launch order fences a contended file AND a canonical-source rule (PR-6-style) governs where the content belongs, resolve the canonical target FIRST -- routing the content to its canonical home can make the contended edit unnecessary, dissolving the collision instead of resolving it. A stop-and-float instruction that fires on 'another PR touches this file' should be qualified with 'if the edit is still required after canonical routing'.
- grounding: .agent-work/harvest-226/230/lessons-delta.json op add; verdicts/commander-230.md 'Floated decision' + 'Workflow feedback' point 2
- bank-reason: One occurrence. Re-observe whether concurrent-wave file fences routinely have a canonical-routing escape before hardening the launch-order template's stop-condition wording.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-24 (epic-226-lessons-audit)
- last-confirmed: none
- runs-since-confirmed: 8

### lesson:crew-plan-file-shares-parent-gauge-directory
- scope: commander
- task-class: crew-dispatch
- statement: A dispatched crew's own driven plan file (e.g. an implementer's <gate>-plan.json), if created directly in the work-id root (.agent-work/<work-id>/) rather than a subdirectory, resolves to the SAME gauge.json as the Commander's own spine.json (checklist_engine.py's _gauge_path keys purely off the checklist file's own containing directory). If the Commander's session is itself sharing a session_id/transcript with another concurrently-active top-level agent (e.g. its own Admiral), that shared gauge.json can hold a reading that has nothing to do with the freshly-dispatched crew, tripping the Context Governor's HARD band before the crew does any real work. Workaround this run: crew plan files placed in their own subdirectory (mirroring the reviewer role's own <gate>-review/ convention) get their own gauge.json, sidestepping the collision.
- grounding: Two consecutive g1-implement-rework2 attempts (governor-261) tripped HARD at m0-context before any code change, both traced to a shared .agent-work/governor-261/gauge.json holding claude-opus-5 readings while both the Commander and its dispatched implementer ran Sonnet -- the reading belonged to the epic's own Admiral, sharing this Commander's session_id and physical transcript (independently confirmed, posted to issue #266). A third attempt using a subdirectory-scoped plan file (.agent-work/governor-261/g1-implement-rework2-attempt3/) completed cleanly on the same task.
- bank-reason: One incident, one worktree, one specific session-sharing configuration (Commander sharing session_id with its own Admiral). Needs a second, independently-observed recurrence in a run where the Commander does NOT share a session_id with anything else, to confirm the directory-collision mechanism alone (without the session-sharing compounding factor) is enough to matter, before promoting subdirectory-scoped crew plan files from a workaround to a template default.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-27 (governor-261)
- last-confirmed: none
- runs-since-confirmed: 7

### lesson:reviewer-old-vs-new-repro-without-mutating-file-under-review
- scope: handoff
- task-class: review
- statement: When a reviewer needs to independently reproduce an OLD-vs-NEW behavior contrast (e.g. proving a bug is fixed by showing the old code reproduces it and the new code doesn't), the standard technique of temporarily editing the real file under review, running, then reverting is sometimes blocked by the permission classifier (a reviewer editing the artifact it is reviewing, reasonably flagged). A clean alternative: write a reviewer-side standalone script that loads the real module by file path (importlib) and defines the OLD handler inline as a local function, reusing the SAME real helper functions (e.g. resolve_gauge_path, compute_record) the new code also uses -- this reproduces the contrast without ever mutating the file under review.
- grounding: g1-review-rework2 (governor-261): the reviewer's REVIEW_RESULT workflow-feedback section reports being blocked attempting the temporarily-edit-and-revert technique, then improvising the load-by-path standalone-script technique successfully, and explicitly recommends promoting it as the documented default.
- bank-reason: One reviewer's own account of a single instance. Needs a second independent reviewer to hit and solve the same classifier block the same way before promoting this from 'one crew's improvisation' to a documented default technique in the reviewer skill.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-27 (governor-261)
- last-confirmed: none
- runs-since-confirmed: 7

### lesson:drill-scope-should-name-every-sibling-template
- scope: admiral
- task-class: doctrine-fix
- statement: A regression drill written to prove a doctrine-text fix is load-bearing (e.g. docs/superpowers/drills/dogfood-context-paths-absent.md, proving the STATE_NOTE-fallback wording matters) that names only ONE of several sibling role-templates sharing the same doctrine pattern (here: Commander spine, PR #75/#86) gives false confidence the whole class is fixed -- re-running the drill only re-checks the named template, so a structurally identical sibling (the Admiral spine, this issue #268) can carry the same unfixed defect indefinitely while the drill keeps reporting PASS. Candidate rule: when authoring or updating a drill for a doctrine pattern that recurs across sibling templates, the drill's 'doctrine under test' line should enumerate every sibling template carrying the pattern, or explicitly note which ones it does NOT cover.
- grounding: governor-268's launch-order-mandated class sweep (LAUNCH_ORDER-268.md part 2) found exactly this: skills/admiral/references/fleet-doctrine.md:57 carries the identical missing-fallback defect the Commander spine fix (and its drill) addressed, undetected until this sweep. AGENT_FEEDBACK.md 'Friction / unclear' section, governor-268.
- bank-reason: Single instance, one doctrine pattern (STATE_NOTE fallback), one drill. Needs a second independent recurrence -- a different doctrine pattern with sibling templates, or a different drill missing sibling coverage -- before promoting from a one-off observation to a documented drill-authoring rule.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-27 (governor-268)
- last-confirmed: none
- runs-since-confirmed: 5

### lesson:lightweight-critic-catches-real-findings-on-bounded-issues
- scope: commander
- task-class: general-workflow
- statement: Even a lightweight design-it-twice pass (2 candidates, single-context, not a full panel) plus one solo cold-critic subagent, run on a bounded single-issue plan whose design space the pre-rulings already narrowed, caught a genuine blocking design gap (undesigned fan-out/clearing scope for a new multi-path sidecar) before the implement gate started. Worth keeping as a default floor even when a run judges a full panel unnecessary.
- grounding: .agent-work/governor-265/PLAN_ALTERNATIVES.md (critic findings) + MISSION_FRAME.md decision:skip-sidecar-fanout-and-clear
- bank-reason: single data point from one run; needs re-observation across several more bounded-issue Commander runs before promoting to a stronger doctrine statement (e.g. making the lightweight critic pass non-skippable rather than bias-to-yes).
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-27 (governor-265)
- last-confirmed: none
- runs-since-confirmed: 4

### lesson:reviewer-fowler-template-path-wording-ambiguous
- scope: constellation
- task-class: general-workflow
- statement: The installed constellation-reviewer skill's r6-fowler imperative says to record the Fowler pass 'to templates/FOWLER_PASS.template.json', which read literally means overwriting the shared skill template rather than filling a per-run working copy. The reviewer in this run correctly inferred a working-copy fill (mirroring how review.json itself works) but had to reason past ambiguous wording to get there.
- grounding: .agent-work/governor-265/REVIEW_RESULT-g1.md, Workflow Feedback section
- bank-reason: one observation from one reviewer dispatch; needs re-observation across more reviewer runs to confirm this is a consistent stumbling point (not a one-off misreading) before an upstream doctrine edit is warranted -- delegated mode also cannot self-apply doctrine this run regardless.
- target: constellation-reviewer skill's checklist/imperative wording for r6-fowler (installed skill, not this repo)
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-07-27 (governor-265)
- last-confirmed: none
- runs-since-confirmed: 4

### lesson:guard-must-be-defined-by-the-consumer-not-a-character-list
- scope: project
- task-class: implementation
- statement: When a validator protects a downstream parser, define the guard in terms of the PARSER'S OWN BEHAVIOUR, never as a hand-listed set of characters or cases — the two definitions drift and the gap is silent. In #301 the writer rejected values containing backslash-n or backslash-r, but the parser sectioned files with str.splitlines(), which also breaks on vertical tab, form feed, the file/group/record separators, NEL, U+2028 and U+2029. So the precise injection the guard existed to block (a free-text field forging a '- status: retired' line) passed through, and content after the separator was silently dropped on the next touch. The fix was not a longer character list but the predicate 'value != empty and value.splitlines() != [value]', which cannot drift from the parser because it IS the parser's behaviour. Note the trailing-separator case: a length check alone is insufficient, since a value ending in a separator splits to one element. SECOND INSTANCE, same run, different costume (gate g4): binding the ratified file-move retirement layout moved membership from file CONTENT to file LOCATION, and the non-episode classifier was a hand-maintained filename allowlist (NON_EPISODE_FILENAMES) consulted only at the flat root while the two scanned directories were globbed unconditionally. The store as shipped could not be read by its own tooling: its own README placeholders became a phantom episode id in both directories at once. Fixed the same way as the first instance — replace the hand-maintained list with the computable property the store already owns (its id grammar), applied uniformly. The tell is identical both times: a list a human maintains standing in for a predicate the code can decide.
- grounding: .agent-work/301/crew-handoffs/g2-review-result.md (reviewer demonstrated the U+2028 attack end-to-end) and the fix in scripts/apply_episode_delta.py _reject_newline; SECOND INSTANCE: .agent-work/301/crew-handoffs/g4-review-result.md (cold panel BLOCK, reproduced by the commander in one command: `python scripts/query_episodes.py enumerate` erroring against the store the gate ships), fixed by episode_id_for() in scripts/apply_episode_delta.py
- bank-reason: First instance in this repo, but the shape is general and the repo now has two Markdown-record stores with validator/parser pairs (lessons and episodes). Re-observe whether the same drift appears in apply_lessons_delta.py's own guards or in #305/#308's consumers; a second instance would justify a standing validator-writing rule rather than a banked lesson.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-01 (301)
- last-confirmed: none
- runs-since-confirmed: 2

### lesson:a-panel-inherits-what-it-was-not-told-to-vary
- scope: commander
- task-class: design-it-twice
- statement: A PANEL VARIES WHAT IT IS TOLD TO VARY AND INHERITS EVERYTHING IT IS NOT, and it inherits from TWO sources, not one. Neither is visible in how the candidates differ, so convergence cannot surface either: unanimity across deliberately-differing constraints is evidence about the axis that was varied and evidence of nothing at all about the axis that was not.
- grounding: #301: git check-ignore .agent-work/episodes/ exits 0 and git ls-files .agent-work/ returns zero files, against all four candidates in .agent-work/301/design-it-twice/; correction recorded in the amend authority on execute.json and in docs/EPISODE_STORE.md section 1. #300: its own shared-assumption audit retracted the 'metadata only, never file content' convergence claim after finding it was the brief handed back, reported via admiral epic-298.
- bank-reason: Two independent instances in one epic, by two commanders, via two different inheritance sources - which is why this is stated as one lesson with two shapes rather than two lessons. It also pairs with this run's manufactured-consensus error: all three are failures about what candidates SHARE rather than how they differ, and in each case agreement read as evidence when it was only inheritance. Re-observe whether the shared-assumption audit, now that #300 has run it once successfully, keeps catching things on later panels; if it does, it belongs in design-it-twice-brief.md as a required convergence step rather than a banked lesson - and the brief-inheritance half needs an auditor who did not author the brief. CROSS-REFERENCE: see [stale-description-has-two-shapes-and-only-one-yields-to-verification], kept whole for the identical reason — halves with unequal fix costs invite fixing the cheap one and declaring the class closed. Two instances in one wave.
- mentions: 2
- confirmed: 1
- disconfirmed: 0
- status: active
- added: 2026-08-01 (301)
- last-confirmed: 2026-08-01 (300)
- runs-since-confirmed: 2
- history: confirmed 2026-08-01 (300) — Second independent instance, from #300's own 3-author panel rather than #301's four. Running the audit on my own panel retracted one of five reported convergences ('metadata only, never file content' was my own brief constraint echoed back, not independent agreement); found an unquestioned inherited declaration LOCATION whose per-work-area instantiation creates a legitimate committed-vs-instantiated disagreement a naive drift check would misreport (filed as an obligation onto #306); and found that all three authors had verified the blob-OID identity ONLY under the current '* text=auto' .gitattributes with no -text/binary exemption -- a silent-divergence hazard in the one primitive the whole manifest rests on, closed via the engine's amend verb as postcondition g1-implement.c7 and verified in both directions (exit 0 today, exit 1 after appending '*.md -text', tree restored). Evidence: .agent-work/300/DIT-COMPARISON.md ADDENDUM. Note the two sources of false convergence are DIFFERENT in the two instances: #301 inherited from PRIOR ART, #300 inherited from the BRIEF'S OWN fixed constraints -- so the failure mode is broader than either instance alone shows.

### lesson:a-check-that-cannot-fail-is-indistinguishable-from-one-that-passed
- scope: constellation
- task-class: verification
- statement: A verification that cannot fail reports the same signal as one that genuinely passed, so it is worse than no verification - it consumes the attention a real check would have earned. Three instances in epic-298 alone, by three different mechanisms: (1) #301's floor-interpreter guard discovered an interpreter BY NAME, found none, and SKIPPED - green, zero coverage; (2) #300 found two postconditions that passed vacuously; (3) the standing round-trip lesson describes tests that only ever see clean shipped artifacts and so cannot catch a parser bug. The repair is the same in each case: require the check to demonstrate it actually ran against something that could have failed it. For the interpreter guard that meant accepting a candidate only if it REPORTS the floor version when asked, rather than merely existing; for a test it means an adversarial fixture; for a postcondition it means a bash-negation that proves the guard fires. Mutation-testing a guard - break the thing, watch it go red, restore - is the cheap general form.
- grounding: #301 tests/test_episode_store.py FloorInterpreterPortabilityTests (first version skipped silently because `py` resolves to 3.12 in a shell and 3.14 inside a pytest subprocess); admiral epic-298 log recording #300's two vacuous postconditions; lesson:round-trip-tests-prove-artifacts-not-parsers
- bank-reason: Constellation-scoped because it recurred across THREE separate agents and mechanisms in one epic, which makes it shared-machinery signal rather than a project quirk. Re-observe at the next epic whether vacuous-pass checks keep appearing; if so the fix belongs in the crew handoff templates (require every new guard to be mutation-verified) rather than in a lesson each run rediscovers.
- mentions: 3
- confirmed: 0
- disconfirmed: 0
- recurrences: 2
- status: exported
- added: 2026-08-01 (301)
- last-confirmed: 2026-08-01 (issue-309)
- runs-since-confirmed: 1
- history: recurred 2026-08-01 (299) (constellation debt, not trust) — .agent-work/epic-298/baselines/extract_ordering.py self_test (33 checks) plus two verified mutations. FOURTH instance in this epic and a NEW shape: the mutation test itself was the check that could not fail. My first mutation attempt was a sed that silently did not match, the suite stayed green, and I nearly recorded that as 'mutant killed'. Only verifying that the mutation had ACTUALLY APPLIED (assert mut != src) exposed it. Second shape, same run: the self-test's synthetic fixtures used only input.command, so the extractor's real field-extraction path was never exercised until a real stream-json excerpt was checked in as a fixture.
- history: exported 2026-08-01 (299) — .agent-work/CONSTELLATION_FEEDBACK.md 2026-08-01 entry for 299 — exported with the originating lesson id in its Lesson field so the upstream sweep groups recurrences on stable identity. Fourth recurrence in this epic, NEW shape: the lesson's own prescribed repair (mutation-test the guard) has a vacuous mode of its own. A sed-applied mutant silently did not match, the file was unchanged, the suite stayed green, and 'mutant killed' was the natural misreading; only a separate assert that the mutation had applied exposed it. Second shape same run: the guard's fixtures were all author-synthesized and encoded a guess at the input format (input.command), passing every check against a shape that does not occur in real stream-json transcripts. Suggested upstream edit: extend the repair clause to 'mutate, ASSERT THE MUTATION APPLIED, then watch it go red', and require a fixture captured from the real format for any guard over an external format.
- history: recurred 2026-08-01 (issue-309) (constellation debt, not trust) — PLAN_CRITIC_DISPOSITION.md findings 1 and 2 (constellation-skills, issue-309): a solo cold plan critic found TWO independent vacuous-pass checks in this run's own gate plan before any crew was dispatched -- g1-seed's original postcondition (git status --porcelain over a directory that IS gitignored just silently omits it, so the check passed unconditionally whether or not the slice was ever seeded) and g0-fix321-implement's original adversarial-test spec (a traversal id that does not resolve to a real existing file returns None whether or not the ID_RE guard exists, so the test could pass with or without the fix). Both fixed before dispatch. Fifth+ recurrence in this epic, same mechanism class (a check whose failure path is never actually exercised).
- history: exported 2026-08-01 (issue-309) — .agent-work/CONSTELLATION_FEEDBACK.md 2026-08-01 entry for issue-309 -- exported with the originating lesson id in its Lesson field so the upstream sweep groups recurrences on stable identity. Fifth+ recurrence, two new vacuous-check shapes (git status --porcelain silently omitting an ignored-and-unpopulated directory; a not-found-id test standing in for a guard-fired test), both caught pre-dispatch by the mandatory cold plan critic and fixed before any crew was dispatched or any recall/noise number was produced.

### lesson:stale-description-has-two-shapes-and-only-one-yields-to-verification
- scope: constellation
- task-class: coordination
- statement: A description that was accurate when taken and wrong when used comes in TWO shapes with DIFFERENT fixes, and conflating them makes the second one worse. Keep them apart or a reader will apply 'verify harder' to a problem verification cannot reach.
- grounding: Shape 1: agent_work_root.py:136-141 vs its docstring; git ls-files .agent-work/ returning zero against all four candidates in .agent-work/301/design-it-twice/; .gitattributes containing '* text=auto', corrected on issue #319. Shape 2: admiral epic-298 fork resolution naming design-candidates-inherit-the-neighbours-assumptions-without-checking-them after it had been renamed to a-panel-inherits-what-it-was-not-told-to-vary, caught before harvest by comparing the live staged file; the same admiral's protective snapshot captured the superseded delta.
- bank-reason: Constellation-scoped because shape 2 is a property of the multi-agent machinery itself - it appears only where two agents share a fact neither can see the other write, which is exactly the worktree/harvest topology this corpus runs on, and it cost a near-miss on its first occurrence. Shape 1 is well-covered by existing verification lessons and is included ONLY so the contrast is legible; do not let an audit graduate shape 1 alone and consider the class closed, since that is the reading this lesson exists to prevent. Re-observe whether the quote-id-and-count protocol actually catches a second drift; if it does, it belongs in the admiral's harvest procedure rather than in a lesson. CROSS-REFERENCE, second instance of one authoring pattern: this op and [a-panel-inherits-what-it-was-not-told-to-vary] were BOTH deliberately kept whole rather than split, for the same reason — their halves have UNEQUAL FIX COSTS, so the cheap half (the one with an obvious mechanical mitigation) is the half that gets fixed alone and the class declared closed. Twice in one wave the right call was refuse to split a lesson whose halves have unequal fix costs. That generalization may outlive both lessons; it is recorded here rather than as a third op because the bank adjudicates, it does not accumulate.
- mentions: 1
- confirmed: 0
- disconfirmed: 0
- status: active
- added: 2026-08-01 (301)
- last-confirmed: none
- runs-since-confirmed: 2
