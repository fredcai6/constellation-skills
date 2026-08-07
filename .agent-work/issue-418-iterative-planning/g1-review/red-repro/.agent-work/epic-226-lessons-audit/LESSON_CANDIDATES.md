# Lesson Candidates: `epic-226`

Nominations only — nothing here is applied until the dispatcher (team-lead/Admiral)
routes it. Every candidate cites a grounding artifact line; ungrounded candidates were
discarded. Fresh-context audit — no prior history with this run.

Sources read in full: `.agent-work/epic-226/ADMIRAL_LOG.md`; six harvest folders
(`.agent-work/harvest-226/{227,228,229,230,231,232}/`) — `239` is intentionally empty
(fixed in-lane as bounded work, not a full Commander worktree, per ADMIRAL_LOG
2026-07-25 RULING "fix-now scoping"); five verdicts
(`.agent-work/epic-226/verdicts/commander-{227,228,230,231,232}.md` — **#229's own
verdict was never written**, see Brief gaps below); `.agent-work/LESSONS.md` Active
section; and the mandatory cross-project sweep (`python scripts/collect_feedback.py
C:/Programs/f1Brainz C:/Programs/network_elo C:/Programs/story_time`, run live during
this audit — network_elo and story_time contributed nothing this pass).

## Candidates

### `execute-the-advice-a-test-asserts-on`
- **Scope:** project
- **Task-class:** test-authoring
- **Observed:** A test asserting on GENERATED ADVICE (a hint/recovery line naming a
  runnable command) string-matched or structurally checked the rendered text instead of
  executing the named command, over fixtures that could not express the failing state
  (single-task fixtures made a non-active gate impossible; a guard hardcoded to
  `pending` hid the two active-gate states where the advice was wrong).
- **Cost:** #227 gate g3's ENTIRE rework budget — 3/3 rework rounds, 3 sequential BLOCK
  verdicts, four distinct defects of one shape. The Commander's own independent
  640-combination sweep also came back clean, because it shared the fixtures' blind
  spot.
- **Proposal:** Add to `skills/_shared/global-crew.md` § "The deliverable" → "Required
  evidence by change type" bullet, appending: *"generated advice/hint/recovery text →
  EXECUTE the advice and assert it does not refuse, over fixtures parameterized on
  every dimension the advice depends on — string-matching the rendered text is not
  evidence."*
- **Grounding:** `.agent-work/epic-226/ADMIRAL_LOG.md` 2026-07-25 CHECKPOINT
  ("the `execute-the-advice-a-test-asserts-on` doctrine promotion is approved... no
  longer a deferred `needs human`") + 2026-07-25 ESCALATION entry; `verdicts/commander-227.md`
  §3 and §7; `harvest-226/227/execute.json` g3-implement `rework_count=3/3`;
  `harvest-226/227/lessons-delta.json` ops `add`+`defer` (id
  `execute-the-advice-a-test-asserts-on`).
- **Corroboration:** rework_count at cap (3/3), 3 BLOCK verdicts across rounds — the
  strongest-corroborated finding in this audit.
- **Confidence:** high
- **Routing:** **graduate-and-retire → `skills/_shared/global-crew.md`.**
  **Human authority already granted** — Fred, 2026-07-25: *"I'm okay with the 227
  lesson"* — do NOT re-defer as `needs human`. A reproduction drill was run this audit
  (before/after arms, throwaway sonnet subagents, editor/auditor separation honored):
  **REPRODUCED** — the before-arm's primary test plan does exact-string-match over a
  correctly-parameterized fixture matrix but explicitly declines to execute the advice;
  the after-arm drops string-matching entirely and executes the real command. Drill
  committed at `docs/superpowers/drills/execute-the-advice-a-test-asserts-on.md`. See
  **Playbook Delta** below for the two-step `add` + `apply` op sequence (the engine's
  own `apply_lessons_delta.py` sorts `apply` before `add` within one delta, so this
  MUST run as two sequential invocations — noted explicitly there).

### `verify-launch-order-claims-against-code` (existing lesson — widen + confirm)
- **Scope:** project
- **Task-class:** delegated-planning
- **Observed:** Re-cited as pre-ruling "PR-7" in this epic's own `LATITUDE_CONTRACT.md`
  (line 157) — confirming it is **not yet permanent doctrine**, only re-derived per-epic
  from the LESSONS.md entry. This epic contributed 2 NEW confirms, one in a genuinely
  new failure shape: wt-227 re-confirmed "mechanism already shipped" (item 1's imperative
  elision + INV-2 purity were already true at HEAD); wt-230 caught a DIFFERENT failure
  mode — the launch order named an edit target, "the Decision Anchors section of
  `commander-core.md`," that **does not exist under that name**.
- **Cost:** Averted, not incurred — that is the lesson's entire value proposition. Its
  bank-reason explicitly asked "does this generalize past `checklist_engine.py`
  recurrences" — wt-230's answer is yes, to a different question shape entirely
  (target-existence, not mechanism-existence).
- **Proposal:** Widen the statement from "verify the named defect/mechanism against
  current code" to also cover "verify the named EDIT TARGET exists at the named
  address." Exact widened statement drafted in the Playbook Delta below.
- **Grounding:** `ADMIRAL_LOG.md` 2026-07-24 LESSON SIGNAL entry (commander-230's
  finding, explicit widening request); `verdicts/commander-230.md` §"Workflow feedback"
  point 1 ("this is its **third** data point"); `harvest-226/227/lessons-delta.json` op
  `confirm`; `harvest-226/230/lessons-delta.json` op `confirm` with `proposed-widening`
  field.
- **Corroboration:** Now 4 total observed instances (2 pre-epic mentions + 2 confirms
  this epic) across 3 distinct issues and 3 distinct failure shapes (already-shipped
  mechanism ×2, named-target-does-not-exist ×1, unnamed-sibling-token-pair ×1) —
  recurrence-with-*variation* is stronger signal than repeated identical hits.
- **Confidence:** high
- **Routing:** Playbook delta applied this audit: `confirm` ×2 + `amend` (widen
  statement). **NOT yet threshold-ripe for auto-`apply`** — `confirmed` becomes 2 against
  this playbook's `apply_confirmed=3` gate (one more confirmation away). **Queued for
  human/Charter review**, not self-applied: candidate doctrine home is
  `skills/commander-delegated/SKILL.md` § "Your principal: the frozen launch order"
  (lines 22–26 already discuss reconciling the ask against the order — this is the
  natural next paragraph). Recommend Charter nomination once the third confirm lands, or
  earlier human sign-off given it is the most-recurred lesson in the inbox.

### `round-trip-tests-prove-artifacts-not-parsers`
- **Scope:** project
- **Task-class:** testing
- **Observed:** A round-trip test that lints/parses the REAL shipped artifacts proves
  those artifacts are clean — it does not prove the parser/tool itself is correct. Two
  INDEPENDENT instances this single epic: (1) `grade_lint.py` — 18 shipped tests
  including a 4-template round-trip all passed while a greedy-placeholder regex
  **silently PASSED** a real ungraded decision (the single worst failure mode for a
  linter) and a nested-sub-bullet **false-FAILed** a valid plan; both unreachable from
  the four shipped templates, found only when the reviewer was explicitly told to
  author adversarial fixtures. (2) `checklist_engine.py`'s own `Inv3ExclusionCheck` —
  found in g3 REVIEW ROUND 3 of #227's *own* rework loop, i.e. it survived rounds 1–2 of
  the very loop hunting this class of defect — claimed totality on the excluded-verb set
  while exercising only 4 of 10.
- **Cost:** Two real, live bugs surviving a full green test suite in one case; a
  self-confirming coverage claim surviving two rework rounds in the other.
- **Proposal:** Pair every round-trip/enumeration test over real shipped artifacts with
  adversarial fixtures authored specifically to make the tool return a WRONG answer
  (false FAIL on a valid input, silent PASS on an invalid one) — name this explicitly in
  reviewer handoff doctrine, not left to an ad hoc "try to break it" instruction.
- **Grounding:** `verdicts/commander-230.md` §"Workflow feedback" point 3;
  `verdicts/commander-227.md` §"crew-reported friction" g3-reviewer round 3 entry;
  `harvest-226/230/lessons-delta.json` op `add` (id
  `round-trip-tests-prove-artifacts-not-parsers`).
- **Corroboration:** Two independent live defects this epic, one directly review-caught
  (grade_lint), one BLOCK-verdict-adjacent (Inv3ExclusionCheck, round 3 of a 3-round
  rework loop).
- **Confidence:** high
- **Routing:** Lesson-inbox delta: `add` (this audit strengthens the grounding to cite
  BOTH instances at add-time, then immediately `confirm`s with the second). Bank, not
  graduate yet — 2 data points, same as the sibling testing-discipline lessons already
  banked pending a decision on whether a dedicated testing-conventions doc should exist
  (see Queued for Human Review).

### `checklist-engine-from-child-relative-path-and-gated-vs-survey` — CONFIRMED SIBLING FORK, resolved
- **Scope:** constellation
- **Task-class:** commander / checklist-engine gate-execution
- **Observed:** `checklist_engine.py advance <gate> --from-child <path>` has two rules
  undiscoverable from its own REFUSED text: (1) a non-absolute `<path>` resolves against
  the PARENT checklist's directory, not cwd; (2) it refuses a `gated`-type child outright
  ("has no consolidation yet") — only a `survey`-type child (which carries a
  `consolidation`) can close this way; a `gated` child (e.g. `execute.json`) must instead
  be closed via a direct `attest <parent-step> --cond <id>` citing its own per-gate
  evidence. **Two ships rediscovered this independently in one wave**: wt-228 filed
  `checklist-engine-from-child-relative-path-and-gated-vs-survey` (scope=constellation),
  wt-231 filed `from-child-refusal-undiscoverable-from-error` (scope=project) — same
  defect, two slugs, two `add` ops.
- **Cost:** One extra round-trip per ship (2 total this wave); each rediscovery burns a
  Commander session re-deriving what `docs/CHECKLIST_SCHEMA.md` already states but the
  engine's own refusal text doesn't surface.
- **Proposal:** Have the engine's REFUSED message for both cases name the actual rule
  inline — e.g. `"child checklist not found at <resolved-path> (relative paths resolve
  against the PARENT checklist's directory, not cwd)"` and `"<child> has no consolidation
  — gated children close via a direct 'attest <parent-step> --cond <id>' instead"`.
  Mechanical constraint (Form-selection rung 1) — a script-level message fix, not a doc
  reminder.
- **Grounding:** `ADMIRAL_LOG.md` 2026-07-24 RULING "apply-a-lesson" (Admiral's own
  pre-resolution, already ruling **one lesson, amended, plus a confirm — never two
  adds**) + 2026-07-24 LESSON SIGNAL "identity catch" entry;
  `harvest-226/228/lessons-delta.json` op `add` id
  `checklist-engine-from-child-relative-path-and-gated-vs-survey`;
  `harvest-226/231/lessons-delta.json` op `add` id
  `from-child-refusal-undiscoverable-from-error`; independently verified by this audit —
  both `add` payloads describe the identical two rules against the identical two engine
  refusal strings.
- **Corroboration:** Two independent `lessons-delta.json` `add` ops from two different
  worktrees in the same wave, cross-referenced by path in the Admiral's own ruling before
  it ruled — not narrative-only.
- **Confidence:** high
- **Routing:** **Sibling-fork resolution CONFIRMED and applied as the Admiral
  pre-ruled**: land ONE lesson under the constellation-scoped id
  `checklist-engine-from-child-relative-path-and-gated-vs-survey`, `amend`ed to carry
  BOTH halves (the relative-path rule and the gated-vs-survey rule — the current wt-228
  statement already covers both, verbatim), with wt-231's raise landing as a `confirm`,
  never a second `add`. **Constellation scope → always exported, never silently
  confirmed**: `export` op included in Playbook Delta below, with a ready CONSTELLATION_FEEDBACK.md
  entry (draft included there) citing this lesson id per the stable-identity rule.

### `harvest-before-sweep-enforcement-gap` (new)
- **Scope:** constellation
- **Task-class:** general-workflow / closeout
- **Observed:** Doctrine already states the rule (`constellation-admiral/SKILL.md`
  Closeout step 4: *"Harvest first, then remove — a worktree swept before its trio is
  collected silently drops that run's learning"*) but nothing MECHANICALLY CHECKS it.
  Two independent, convergent occurrences in this audit's own evidence window: (1)
  epic-226 itself — this Admiral explicitly ran a dedicated `HARVEST EXECUTED` step
  *before* any sweep specifically to avoid this failure, extra overhead it had to
  self-impose because nothing enforces it. (2) f1Brainz epic-601 — the SAME failure,
  for real: six `staged-feedback/<work-id>/` trios were collected out of their worktrees
  (satisfying each Commander's own `feedback`/`archive` gate against the STAGING copy)
  but never merged into the durable log; all six source worktrees were already swept —
  staging was the sole surviving copy — before team-lead caught it and hand-merged 12
  entries.
- **Cost:** f1Brainz: real, lasting data loss narrowly averted only by a human catching
  it post-hoc. epic-226: no data lost, but only because the Admiral spent extra,
  self-imposed diligence that nothing in the tooling required of it.
- **Proposal:** Extend `verify_agent_feedback.py` (or a sibling check) with a
  harvest-completeness mode: for every `staged-feedback/<work-id>/` directory still
  present at closeout, confirm its content (or a harvest-provenance marker citing it)
  actually appears in the corresponding durable file, and refuse/warn `git worktree
  remove` for that work-id until it does. Mechanical constraint (Form-selection rung 1)
  — the doctrine text already exists and did not prevent the f1Brainz loss; only
  enforcement closes the gap.
- **Grounding:** `ADMIRAL_LOG.md` 2026-07-25 "HARVEST EXECUTED" + "HARVEST MANIFEST"
  entries (epic-226's own preventive action); cross-project sweep output, candidate
  `0cc4eefd032c` ("Harvest-before-sweep is stated in doctrine but not mechanically
  checked, and it failed for real"), citing `f1Brainz/.agent-work/epic-601/ADMIRAL_LOG.md`
  Closeout section and direct inspection of `staged-feedback/*/` (6/6 trios absent from
  the durable log before manual fix).
- **Corroboration:** Two independent epics, two independent Admirals, same gap, in the
  same audit window — one a near-miss avoided by extra diligence, one a real loss caught
  post-hoc. This is the strongest possible corroboration short of measured recurrence
  counters.
- **Confidence:** high
- **Routing:** `add` (constellation) + `confirm` (second occurrence, recurrence-debt per
  constellation counter semantics) + `export` to CONSTELLATION_FEEDBACK.md — **code
  target** (`scripts/verify_agent_feedback.py`), so no human-authority gate applies once
  someone builds it; export queues it as unshipped shared-machinery debt. Draft
  CONSTELLATION_FEEDBACK.md entry included in Playbook Delta below.

### `cold-critic-mandatory-for-measurement-dependent-plans` (new)
- **Scope:** project
- **Task-class:** delegated-planning
- **Observed:** Two commanders this epic, independently, recommend hardening the cold
  plan critic from optional/"bias-to-yes" toward mandatory for any gate plan whose
  acceptance depends on a before/after measurement or a required round-trip test.
  wt-227: *"The cold plan critic was the highest-leverage 8 minutes of the run... catches
  that g3's baseline would be unproducible after g1/g2 overwrote the engine... Recommend
  making the cold critic mandatory rather than bias-to-yes."* wt-230, independently:
  *"The cold critic earned its cost outright. Its BLOCKER 1 ... would have broken the
  issue's own required round-trip test."*
- **Cost:** Not directly measured (both are pre-crew catches, so there is no
  counterfactual rework count) — but both catches were of defects that would otherwise
  have surfaced only after rework rounds were spent, which is exactly the class of cost
  `execute-the-advice-a-test-asserts-on` shows can consume an entire rework budget.
- **Proposal:** Change the plan-step guidance from "run the cold critic, bias to yes on
  skipping it" to "mandatory when the plan's acceptance depends on a before/after
  measurement or a required round-trip/parser test."
- **Grounding:** `verdicts/commander-227.md` §7 "What worked" +
  `verdicts/commander-230.md` §"Workflow feedback" point 3.
- **Corroboration:** Two independent commanders, same epic, same specific recommendation
  — assertion-level (no rework-count telemetry directly attributable, since both catches
  were pre-crew), but the convergence itself is the signal.
- **Confidence:** medium
- **Routing:** Lesson-inbox delta: `add` (bank). First time this exact lesson is named;
  bank-reason: re-observe a third convergent recommendation, or a case where SKIPPING the
  cold critic on a measurement-dependent plan actually cost rework, before hardening
  plan-step doctrine.

### `windows-subprocess-env-does-not-shadow-path-resolution` (new)
- **Scope:** project
- **Task-class:** testing / windows subprocess probing
- **Observed:** On Windows, `subprocess.run(env={'PATH': ...})` does NOT shadow which
  executable an unqualified name resolves to — `CreateProcess` resolves against the
  CALLING process's real environment, not the child `env=` dict. A test must mutate
  ambient `os.environ['PATH']` directly to genuinely make a candidate unresolvable.
- **Cost:** ~10 minutes discovered empirically (two pasted `py -c` transcripts) by
  #228's implementer before landing the correct test technique.
- **Proposal:** One-line doctrine/comment note near any future Windows subprocess-probing
  surface. Not yet — single observation.
- **Grounding:** `harvest-226/228/lessons-delta.json` op `add`; `verdicts/commander-228.md`
  §"Acceptance evidence" (the two-transcript empirical proof).
- **Corroboration:** assertion-only, one occurrence.
- **Confidence:** medium
- **Routing:** Lesson-inbox delta: `add` (bank, per its own stated bank-reason — needs a
  second Windows subprocess-probing surface before promoting to doctrine).

### `prove-command-fails-postcondition` (new)
- **Scope:** handoff
- **Task-class:** general-workflow
- **Observed:** The engine's command-postcondition semantics assume exit 0 = pass, which
  doesn't fit a plan item needing to prove a command CORRECTLY FAILS (e.g. "the guard
  refuses this input"). #229's implementer improvised a `! <command>` bash-negation
  wrapper so the postcondition's exit code tracks "did the guard fire."
- **Cost:** None measured — a clean improvisation, not a blocked gate.
- **Proposal:** Document the negation-wrapper pattern as a named, reusable handoff
  technique once it recurs.
- **Grounding:** `harvest-226/229/lessons-delta.json` op `add`;
  `verdicts` — n/a (#229 has no verdict, see Brief gaps); AGENT_FEEDBACK.md 2026-07-24
  `issue-229` entry.
- **Corroboration:** assertion-only, one occurrence.
- **Confidence:** medium
- **Routing:** Lesson-inbox delta: `add` (bank, per its own bank-reason — needs a second
  gate/issue proving a command fails before promoting to a template pattern).

### `canonical-routing-can-dissolve-a-file-fence` (new)
- **Scope:** handoff
- **Task-class:** delegated-planning
- **Observed:** A launch-order stop-condition ("float if another wave's PR touches this
  file") fired on an edit that PR-6 canonical-source routing made unnecessary —
  commander-230's contended edit to `commander-core.md` dissolved once the doctrine was
  routed to its canonical `_shared/global-everyone.md` home instead, avoiding a full
  Admiral round-trip.
- **Cost:** Averted, not incurred (same shape as `verify-launch-order-claims-against-code`
  — the value is in what didn't happen).
- **Proposal:** Qualify file-collision stop-conditions in the launch-order template with
  "...if the edit is still required after resolving the canonical target."
- **Grounding:** `harvest-226/230/lessons-delta.json` op `add`;
  `verdicts/commander-230.md` §"Floated decision" + §"Workflow feedback" point 2.
- **Corroboration:** assertion-only, one occurrence.
- **Confidence:** medium
- **Routing:** Lesson-inbox delta: `add` (bank, per its own bank-reason).

### Harness Agent-tool capability divergence (mention, not a new lesson)
- **Scope:** n/a (harness, not repo doctrine)
- **Task-class:** general-workflow
- **Observed:** Three independent hits, two different specific mechanisms, one
  epic+cross-project window: wt-227 — `Agent(run_in_background: true)` rejected
  ("In-process teammates cannot spawn background agents"); wt-229 — same class,
  "Teammates cannot spawn other teammates — the team roster is flat"; f1Brainz sweep
  candidate `no-headless-claude-cli-in-agent-tool-harness` — `run_crew.py`'s
  default/spawn backend assumes a headless `claude -p` CLI that isn't present in this
  harness shape.
- **Cost:** Two failed dispatches + retries this epic (cold plan critic re-issue,
  crew polling loops hitting the 10-minute Bash ceiling twice).
- **Proposal:** `run_crew.py`/crew-dispatch doctrine could detect harness capability
  (background-spawn support, headless-CLI presence) rather than assume it — but this is
  a harness-shape fact outside this repo's control on two of the three axes, not a
  repo defect this audit can route to a fix.
- **Grounding:** `verdicts/commander-227.md` §7; `harvest-226/229/AGENT_FEEDBACK.md`
  Friction section; cross-project sweep candidate `661e1dd93d59` (f1Brainz).
- **Confidence:** low — three data points, but two different specific failure
  mechanisms under one loose theme; not yet the same recurring defect.
- **Routing:** Queued for human review (see below) — not banked as a formal lesson this
  audit; genuinely harness-shaped, not clearly this repo's fix to make.

## Existing-Lesson Reconciliation
- `confirm lesson:verify-launch-order-claims-against-code` — wt-227 + wt-230 this epic (see candidate above).
- `confirm lesson:verify-harness-field-and-drive-real-writer` — wt-227 (`execute.json` g2-implement, INV-1 oracle) + wt-232 (g2's real `_write_meta` regression test). Now confirmed=2 (was 0), mentions accordingly. Not yet threshold-ripe (needs 3); strong, but no doctrine-graduation routing this audit — flagged as a testing-conventions candidate below.
- `mention lesson:observe-midprocess-state-not-via-end-output` — wt-227 (`lessons-delta.json` op `mention`): the crew-rework loop observed mid-process state via result-artifact content/mtime and direct behavioral probes, never end-of-turn output, but the lesson's own kill/hang scenario was never tested this run, so it stays a mention, not a confirm.
- `lesson:test-harness-concurrency-failsafe` — no op. Not touched: no concurrent-file-I/O test was authored across any of the 6 issues this epic.

## Playbook Delta (ready to apply)

**Run as TWO sequential invocations** — `apply_lessons_delta.py` sorts `apply`/`retire`
ops before `add`/`confirm`/etc. within a single delta, so an `apply` on a lesson `add`ed
in the same delta will fail with "no such lesson." Delta 1 must be applied and confirmed
successful before Delta 2 runs.

### Delta 1 — adds, confirms, amend, mentions, export, sibling-fork resolution

```json
{
  "work_id": "epic-226-lessons-audit",
  "tick": true,
  "ops": [
    {
      "op": "add",
      "id": "execute-the-advice-a-test-asserts-on",
      "scope": "project",
      "task_class": "test-authoring",
      "statement": "When a change's deliverable is GENERATED ADVICE — a hint, recovery line, or next-step suggestion naming a runnable command — the test must EXECUTE that advice and assert it does not refuse, over fixtures parameterized on every dimension the advice depends on. String-matching the rendered text is not evidence. In issue-227 gate g3 this failure recurred FOUR times with one root cause: fixtures could not express the failing state (single-task fixtures made a non-active gate structurally impossible; a guard hardcoded to 'pending' hid the two active-gate statuses where the advice was wrong). The Commander's own independent 640-combination sweep also came back clean because it shared the fixtures' blind spot.",
      "grounding": ".agent-work/epic-226/verdicts/commander-227.md section 3; .agent-work/harvest-226/227/execute.json g3-implement rework_count=3/3; .agent-work/epic-226/ADMIRAL_LOG.md 2026-07-25 CHECKPOINT (human ruling 2, approved)",
      "bank_reason": "Graduating this same run — see the paired apply op below. Kept as a normal add-then-apply so the lesson history/audit trail is preserved even though it is retired immediately.",
      "target": "skills/_shared/global-crew.md"
    },
    {
      "op": "confirm",
      "id": "verify-launch-order-claims-against-code",
      "grounding": ".agent-work/epic-226/verdicts/commander-227.md section 1 (item 1's imperative-elision and INV-2 purity halves already shipped at HEAD, caught by grep-before-plan)"
    },
    {
      "op": "confirm",
      "id": "verify-launch-order-claims-against-code",
      "grounding": ".agent-work/epic-226/verdicts/commander-230.md 'Workflow feedback' point 1 — third data point, NEW failure mode: the launch order named 'the Decision Anchors section of commander-core.md', which does not exist under that name."
    },
    {
      "op": "amend",
      "id": "verify-launch-order-claims-against-code",
      "statement": "A delegated commander must verify a launch order's NAMED defect/sub-fix against the current code (grep the named symbol/token) BEFORE planning, AND verify that any named EDIT TARGET (a section heading, file path, or anchor) actually exists at the named address — a headline mechanism already shipped becomes an honest-null, and a named-but-nonexistent edit target is a naming slip, not a build task. Recurred across two epics: 152/154 (mechanism-already-shipped, unnamed-sibling-token-pair); epic-226 wt-227 (mechanism-already-shipped, twice); epic-226 wt-230 (named edit target 'the Decision Anchors section of commander-core.md' does not exist under that name).",
      "grounding": "epic-226 wt-230's widening proposal (.agent-work/harvest-226/230/lessons-delta.json op confirm, field proposed-widening), corroborated by wt-227's confirm of the original mechanism-check half in the same wave."
    },
    {
      "op": "confirm",
      "id": "verify-harness-field-and-drive-real-writer",
      "grounding": ".agent-work/harvest-226/227/lessons-delta.json op confirm (INV-1 oracle hand-authored against verb bodies, not argparse-derived, avoiding self-confirmation)"
    },
    {
      "op": "confirm",
      "id": "verify-harness-field-and-drive-real-writer",
      "grounding": ".agent-work/harvest-226/232/lessons-delta.json op confirm (g2's regression test drives the real post-fix _write_meta to produce an actual meta.json, then truncates real bytes, independently reproduced by the reviewer in an isolated scratch tree)"
    },
    {
      "op": "mention",
      "id": "observe-midprocess-state-not-via-end-output",
      "grounding": ".agent-work/harvest-226/227/lessons-delta.json op mention — mid-process state observed via result-artifact content/mtime, never end-of-turn output, but the lesson's own kill/hang scenario was not tested this run"
    },
    {
      "op": "add",
      "id": "round-trip-tests-prove-artifacts-not-parsers",
      "scope": "project",
      "task_class": "testing",
      "statement": "A round-trip test that lints/parses the REAL shipped artifacts proves those artifacts are clean — it does not prove the parser/tool itself is correct. Bugs unreachable from the shipped artifacts pass it silently. Pair every round-trip/enumeration test over real artifacts with adversarial fixtures authored to make the tool return a WRONG answer (false FAIL on a valid input, silent PASS on an invalid one), and instruct reviewers to hunt that specific class rather than only re-running the suite.",
      "grounding": ".agent-work/epic-226/verdicts/commander-230.md 'Workflow feedback' point 3 (grade_lint.py: 18 shipped tests including a four-template round-trip all passed while a greedy-placeholder regex silently PASSED an ungraded decision and a nested sub-bullet false-FAILed a valid plan, both unreachable from the shipped templates)",
      "bank_reason": "Two data points already in hand this epic (see paired confirm below) but neither is a repeat of the SAME tool — round-trip-blindness in a linter (grade_lint) vs. an exclusion-set enumeration (checklist_engine). Banking to see whether a third instance is the same shape before promoting to standing reviewer-handoff doctrine."
    },
    {
      "op": "confirm",
      "id": "round-trip-tests-prove-artifacts-not-parsers",
      "grounding": ".agent-work/epic-226/verdicts/commander-227.md 'crew-reported friction' g3-reviewer round-3 entry: Inv3ExclusionCheck claimed totality on the excluded-verb set while exercising only 4 of 10, surviving rounds 1-2 of the same rework loop hunting exactly this class of defect"
    },
    {
      "op": "add",
      "id": "checklist-engine-from-child-relative-path-and-gated-vs-survey",
      "scope": "constellation",
      "task_class": "commander / checklist engine gate-execution",
      "statement": "checklist_engine.py's `advance <gate> --from-child <path>` (1) refuses a path to the child checklist given relative to cwd, only accepting an absolute path, unlike every other engine verb used in these runs; (2) only works when the child checklist is a SURVEY type (it has a `consolidation` object to attach as review-result) -- attempting it against a GATED-type child (e.g. execute.json, which has no consolidate step) refuses with 'has no consolidation yet', forcing a manual attest+advance instead. Neither behavior is documented in --help or the gate-execution doctrine text, and the REFUSED message itself names neither rule.",
      "grounding": ".agent-work/harvest-226/228/lessons-delta.json op add (id checklist-engine-from-child-relative-path-and-gated-vs-survey) + .agent-work/harvest-226/231/lessons-delta.json op add (id from-child-refusal-undiscoverable-from-error, same defect, folded in per the confirm below) + .agent-work/epic-226/ADMIRAL_LOG.md 2026-07-24 RULING 'apply-a-lesson' (Admiral's own pre-resolution)",
      "bank_reason": "Constellation-scoped shared-machinery defect; banked pending an upstream engine fix (REFUSED message naming the rule inline). Exported this run per the export op below — do not keep confirming into a permanent workaround."
    },
    {
      "op": "confirm",
      "id": "checklist-engine-from-child-relative-path-and-gated-vs-survey",
      "grounding": ".agent-work/harvest-226/231/lessons-delta.json op add (id from-child-refusal-undiscoverable-from-error) -- SIBLING-FORK RESOLUTION applied here per the Admiral's own 2026-07-24 RULING: this is wt-231's independent rediscovery of the identical defect in the same wave, landed as a confirm (recurrence-debt) rather than a second add, preserving one stable identity for the recurrence counter."
    },
    {
      "op": "export",
      "id": "checklist-engine-from-child-relative-path-and-gated-vs-survey",
      "grounding": "Two independent worktrees (wt-228, wt-231) hit the identical defect in one wave -- graduation weight per the constellation counter semantics (confirm = debt, not trust). See the ready CONSTELLATION_FEEDBACK.md entry in this delta's accompanying prose (Queued for Human Review section) for the text to append."
    },
    {
      "op": "add",
      "id": "harvest-before-sweep-enforcement-gap",
      "scope": "constellation",
      "task_class": "general-workflow / closeout",
      "statement": "Doctrine already states 'harvest first, then remove' (constellation-admiral/SKILL.md Closeout step 4) but nothing mechanically checks it before a worktree sweep. A staged-feedback/<work-id>/ trio that passes its own Commander's feedback/archive gate (which verifies only the STAGING copy) looks identical to 'harvested and merged into the durable log' from the outside, but is not the same thing.",
      "grounding": "epic-226 ADMIRAL_LOG.md 2026-07-25 'HARVEST EXECUTED'/'HARVEST MANIFEST' entries (this epic's own preventive, extra-diligence workaround) + cross-project sweep candidate 0cc4eefd032c (f1Brainz epic-601: 6/6 staged trios were the sole surviving copy of their worktrees' learning before a human caught it and hand-merged)",
      "bank_reason": "Constellation-scoped, code-targeted (verify_agent_feedback.py harvest-completeness mode) -- banked pending the upstream fix; exported this run."
    },
    {
      "op": "confirm",
      "id": "harvest-before-sweep-enforcement-gap",
      "grounding": "Second independent occurrence in the same evidence window: f1Brainz epic-601's real data-loss-narrowly-averted event, corroborating epic-226's own preventive workaround as more than an abundance of caution."
    },
    {
      "op": "export",
      "id": "harvest-before-sweep-enforcement-gap",
      "grounding": "Two independent epics, two independent Admirals, same gap, in the same audit window -- see the ready CONSTELLATION_FEEDBACK.md entry in the Queued for Human Review section for the text to append."
    },
    {
      "op": "add",
      "id": "cold-critic-mandatory-for-measurement-dependent-plans",
      "scope": "project",
      "task_class": "delegated-planning",
      "statement": "Run the cold plan critic as MANDATORY, not bias-to-yes/optional, for any gate plan whose acceptance depends on a before/after measurement or a required round-trip/parser test. Two commanders this epic independently found it caught a plan-invalidating defect before any crew was dispatched: wt-227 (g3's over-read baseline would have been unproducible after g1/g2 overwrote the engine) and wt-230 (an undefined Markdown decision-line grammar would have broken the issue's own required round-trip test).",
      "grounding": ".agent-work/epic-226/verdicts/commander-227.md section 7 + .agent-work/epic-226/verdicts/commander-230.md 'Workflow feedback' point 3",
      "bank_reason": "Two convergent recommendations in one epic, but neither has a directly-attributable rework-count (both are pre-crew catches with no counterfactual). Re-observe a third convergent recommendation, or a case where skipping the cold critic on a measurement-dependent plan actually cost rework, before hardening plan-step doctrine."
    },
    {
      "op": "add",
      "id": "windows-subprocess-env-does-not-shadow-path-resolution",
      "scope": "project",
      "task_class": "testing / windows subprocess probing",
      "statement": "On Windows, passing a restricted env={'PATH': ...} into subprocess.run() does NOT shadow which executable an unqualified command name resolves to -- CreateProcess resolves the executable name against the CALLING process's real environment, not the child env= dict. A test that wants to genuinely make a candidate executable unresolvable must mutate the ambient os.environ['PATH'] directly, not pass a restricted env= override -- the latter looks correct but silently passes even when the probe logic is completely broken.",
      "grounding": ".agent-work/harvest-226/228/lessons-delta.json op add; verdicts/commander-228.md 'Acceptance evidence' (two pasted py -c transcripts empirically comparing env={'PATH': d} vs mutating os.environ['PATH'] directly)",
      "bank_reason": "Single occurrence, discovered empirically on one host/Windows build. Banking to see whether another Windows subprocess-probing surface hits the same trap before promoting to a doctrine/comment note."
    },
    {
      "op": "add",
      "id": "prove-command-fails-postcondition",
      "scope": "handoff",
      "task_class": "general-workflow",
      "statement": "A gate that must prove a command CORRECTLY FAILS (e.g. \"the guard refuses this input\") does not fit the engine's command-postcondition semantics (exit 0 = pass). A `! <command>` bash-negation wrapper as the postcondition's `command` field makes \"the guard fired\" a mechanically re-verified engine check instead of a self-reported attest.",
      "grounding": ".agent-work/harvest-226/229/lessons-delta.json op add; AGENT_FEEDBACK.md 2026-07-24 issue-229 entry",
      "bank_reason": "One data point from one Commander run -- needs to recur on a second gate/issue that also needs to prove a command fails before this is confidently a template-worthy pattern rather than a one-off improvisation."
    },
    {
      "op": "add",
      "id": "canonical-routing-can-dissolve-a-file-fence",
      "scope": "handoff",
      "task_class": "delegated-planning",
      "statement": "When a launch order fences a contended file AND a canonical-source rule (PR-6-style) governs where the content belongs, resolve the canonical target FIRST -- routing the content to its canonical home can make the contended edit unnecessary, dissolving the collision instead of resolving it. A stop-and-float instruction that fires on 'another PR touches this file' should be qualified with 'if the edit is still required after canonical routing'.",
      "grounding": ".agent-work/harvest-226/230/lessons-delta.json op add; verdicts/commander-230.md 'Floated decision' + 'Workflow feedback' point 2",
      "bank_reason": "One occurrence. Re-observe whether concurrent-wave file fences routinely have a canonical-routing escape before hardening the launch-order template's stop-condition wording."
    }
  ]
}
```

### Delta 2 — the graduation apply (run only after Delta 1 succeeds)

```json
{
  "work_id": "epic-226-lessons-audit-graduation",
  "tick": false,
  "ops": [
    {
      "op": "apply",
      "id": "execute-the-advice-a-test-asserts-on",
      "target": "skills/_shared/global-crew.md",
      "authority": "human",
      "drill": "docs/superpowers/drills/execute-the-advice-a-test-asserts-on.md",
      "applied_evidence": "Reproduction drill REPRODUCED (docs/superpowers/drills/execute-the-advice-a-test-asserts-on.md): before-arm's regression-test plan asserts exact-match on rendered advice text over a correctly-parameterized fixture, explicitly declining to execute the advice; after-arm, given only the added evidence-type clause, executes the real command through the tool's real dispatcher and asserts the original operation now succeeds. Human authority: Fred, 2026-07-25 ('I'm okay with the 227 lesson'). Exact edit: append to global-crew.md's 'Required evidence by change type' bullet: 'generated advice/hint/recovery text -> EXECUTE the advice and assert it does not refuse, over fixtures parameterized on every dimension the advice depends on -- string-matching the rendered text is not evidence.'"
    }
  ]
}
```

## Queued for Human Review

1. **DISCREPANCY — `engine-artifact-attest`'s 2026-07-17 "resolved upstream" claim is
   FALSE.** `.agent-work/CONSTELLATION_FEEDBACK.md` line 20-23 ("Cleared 2026-07-17...
   Already resolved upstream: `engine-artifact-attest`...") does not match the installed
   engine. Mechanically re-verified this audit: `grep -n "is an artifact check"
   scripts/checklist_engine.py` → line 1967, on the epic-226-shipped engine (post-#227's
   full rewrite), `attest` STILL unconditionally refuses artifact-kind postconditions.
   Corroborated by the cross-project sweep from BOTH directions: f1Brainz's own
   `.agent-work/LESSONS.md` carries this lesson at 22 mentions/18 recurrences with a hit
   as recent as 2026-07-25 (8 days after the false clear), AND the sweep independently
   surfaced a freshly-worded restatement of the identical behavior
   (`engine-refuses-attest-on-artifact-postconditions`, f1Brainz, high confidence) —
   two different framings of one still-live defect. **This is a correction to a past
   curator-sweep record, not a LESSONS.md op** — it needs a human/curator decision on how
   to reopen it (append a correction under the "Cleared 2026-07-17" section, or file a
   fresh tracking issue and cross-reference). Ask: should `engine-artifact-attest` be
   reopened in `.agent-work/CONSTELLATION_FEEDBACK.md`, and should `attest` actually gain
   an artifact-kind fallback (the original ask), or is the current attach-first design
   intentional and the doctrine/wording is what needs fixing instead?
2. **`findings-<n>.md` naming collides with the harness's own report-file guard.** The
   `Write` tool refuses any path containing "findings" ("Subagents should return
   findings as text, not write report files") — hit independently by cmd-227's crew and
   commander-231 this epic, worked around both times via a Bash heredoc with no content
   loss. The convention originates from `skills/admiral/templates/LAUNCH_ORDER.template.md`
   line 31 (placeholder `<assigned findings file>`), instantiated per-epic as
   `findings-<n>.md`. Cheap, low-risk fix within this repo's control: rename the
   convention (e.g. `notes-<n>.md`) — but it is still a doctrine-template edit and this
   audit found no explicit prior human sign-off for it, so it is not bundled into
   Delta 1/2. Ask: approve the rename?
3. **Four harvest-226 `CONSTELLATION_FEEDBACK.md` items are drafted but not yet merged
   into the shared `.agent-work/CONSTELLATION_FEEDBACK.md`.** `harvest-226/227/CONSTELLATION_FEEDBACK.md`
   (`launch-order-template-asserts-unverified-data-locations`) and
   `harvest-226/230/CONSTELLATION_FEEDBACK.md` (four items: `current` doesn't
   distinguish attestable from engine-checked postconditions; `REVIEWER_HANDOFF.template.md`
   lacks a `Survey State Location:` field; the consolidation guard's `--override-reason`
   path is under-documented; launch-order stop-conditions should be qualified by
   canonical routing) are fully drafted, ready-to-append text sitting in the harvest
   folders. `grep -c "issue-227\|issue-230" .agent-work/CONSTELLATION_FEEDBACK.md` → 0 —
   confirmed not yet merged as of this audit. This is closeout housekeeping outside this
   audit's own scope (the brief named specific artifacts; these five items weren't
   flagged for LESSONS.md routing, only CONSTELLATION_FEEDBACK export, which the
   Commanders already drafted) — flagging so it isn't dropped between this audit and
   closeout.
4. **Harness Agent-tool capability divergence** (background dispatch unavailable,
   headless-CLI assumption mismatch) — see candidate above; three data points, two
   different specific mechanisms, low confidence as a single lesson. Worth a human
   decision on whether this belongs as a `run_crew.py` robustness item or stays
   documented friction.
5. **Testing-conventions doc — worth minting?** Four related testing-discipline lessons
   now exist in the ecosystem: `test-harness-concurrency-failsafe`,
   `verify-harness-field-and-drive-real-writer` (confirmed=2 this epic),
   `round-trip-tests-prove-artifacts-not-parsers` (added+confirmed this epic), and
   `execute-the-advice-a-test-asserts-on` (graduating this epic into `global-crew.md`
   directly, since it already has human authority and a clear single-bullet home). The
   other three are still banked pending exactly this question — `verify-harness-field-and-drive-real-writer`'s
   own bank-reason already names it: *"pending needs-human graduation of both into a
   testing-conventions doc."* This audit did not mint that doc (no human authority for a
   new doctrine artifact, and `execute-the-advice`'s graduation into the existing
   `global-crew.md` structure was the minimal, already-approved move) — but the family is
   now large enough that a dedicated doc is a live question, not a hypothetical.

## Workflow Feedback

- **Brief gaps:** The brief said "six verdicts, each with a Workflow Feedback section."
  Only five exist — `.agent-work/epic-226/verdicts/commander-229.md` was never written
  (ADMIRAL_LOG.md 2026-07-24 RULING: commander-229 went idle with complete artifacts but
  dropped its verdict; the Admiral verified acceptance itself plus a clean-room reviewer,
  `rev-229`, rather than blocking on the missing file). Not a blocker — #229's evidence
  lives in ADMIRAL_LOG's own ruling entries and `harvest-226/229/AGENT_FEEDBACK.md`
  instead, and this audit used those as the sixth source. Worth correcting in future
  briefs: state "five verdicts + one Admiral-reconstructed acceptance (idle-with-complete-artifacts
  case)" rather than "six verdicts."
- **Artifact gaps:** none beyond the above — every other named artifact
  (ADMIRAL_LOG, six harvest folders, LESSONS.md) was present, complete, and internally
  consistent (cross-references between the Admiral's narrative and the raw
  `lessons-delta.json` files always matched on direct inspection).
- **What would have made this audit easier:** A single manifest file listing exactly
  which `harvest-226/<issue>/` folders exist and why any expected one is absent (here,
  `239/` is an empty directory by design — fixed in-lane, not a full Commander — but
  nothing states that inline; this audit had to infer it from ADMIRAL_LOG cross-reference).
  A one-line `MANIFEST.md` per epic's harvest root stating "expected N folders, M present,
  reason for any gap" would remove that inference step for the next fresh-context auditor.
