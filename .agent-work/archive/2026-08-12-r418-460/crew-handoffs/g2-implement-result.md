# IMPLEMENTER_RESULT — g2-implement (issue #460, work-id r418-460)

Worktree `C:/Programs/constellation-skills-wt/r418-460`, branch `epic-418/b-460-episodes-observations`.
Engine plan `.agent-work/r418-460/crew-plans/g2-implement-plan.json`, session `g2-impl-r418-460`,
driven m0-context -> m1-inventory -> m2-first-write -> m3-restate-rest -> m4-check-447 -> m5-verify-report.

**Not committed.** The Commander commits.

## Completed slice

Every prescriptive agent-supplied and diagnosis statement in `episodes/active/` was examined against
the Commander-set wording standard. Twenty-seven were grounded and rewritten as records of what
happened, entirely through `python scripts/apply_episode_delta.py --store-root episodes` using only
the `restate-assertion` op. Five were not groundable and were left exactly as they are.

**48 examined / 32 in scope / 27 restated.**

## Files changed

- `episodes/active/*.md` — 24 files, all written by the writer, none hand-edited.
- `.agent-work/r418-460/deltas/` — 4 delta JSON files (evidence) + `classification.md` (the
  per-record classification pass).
- `.agent-work/r418-460/crew-plans/g2-implement-plan.json` (+ `.journal`) — the engine plan.
- `.agent-work/r418-460/evidence/g2-implement-pytest.txt` — suite output.

No file under `docs/agents/` was touched. No new file accumulating advice for future agents was
created. `scripts/apply_episode_delta.py`, `docs/EPISODE_STORE.md`, `scripts/checklist_engine.py`,
`scripts/collect_feedback.py` and `scripts/verify_worktree_precondition_coverage.py` are untouched.

---

## Evidence 1 — the 48 / 32 / N count, derived by command

```
$ ls episodes/active/*.md | wc -l
48
$ ls episodes/active/ | grep -cE '^(issue-304-g3|issue-308|issue-309)-'
32
$ ls episodes/active/ | grep -c '^issue-447-'
16
```

Assertion inventory across the 48 records (295 assertions):

```
$ grep -h "^- kind:" episodes/active/*.md | sort | uniq -c
     48 - kind: expected-behavior
     48 - kind: impact-cost
     48 - kind: observed-behavior
      6 - kind: proposed-remedy
      7 - kind: suspected-cause
     48 - kind: task-intent
     48 - kind: workaround
```

N = **27 restated** (22 `workaround`, 5 `proposed-remedy`), across 24 distinct episodes.

```
$ git diff -U0 episodes/ | grep "^+" | grep -v "^+++" | sed 's/^+\(- [a-z-]*\):.*/\1/' | sort | uniq -c
     27 - history
     27 - statement
$ git diff -U0 episodes/ | grep "^-" | grep -v "^---" | sed 's/^-\(- [a-z-]*\):.*/\1/' | sort | uniq -c
     27 - statement
```

## Evidence 2 — per-restatement grounding table

Every AFTER below is grounded in the record's own text. Where the grounding is a sibling assertion
it is named and quoted; where the grounding is the restated assertion's **own** recorded application
that is stated explicitly. The writer preserved every BEFORE verbatim in the assertion's `history`
line, so nothing is lost by any wording choice here.

### issue-304-g3-001.a5 (`workaround`)
- BEFORE: "None needed for the deletion itself. For the sentinels: re-point each assertion at prose that survives, preserving the test's intent and its assertion count, and name the edit as a deviation rather than silently widening scope."
- AFTER: "None was needed for the deletion itself. For the sentinels, each of the two out-of-scope test files had its prose sentinel re-pointed at surviving degraded-mode prose, and each edit was named as a deviation rather than silently widening scope."
- GROUNDING — sibling **a4**: "Two out-of-scope test files had to be edited to re-point their prose sentinels at surviving degraded-mode prose, each named as a deviation."
- DROPPED as ungrounded: "preserving the test's intent and its assertion count" — no sibling records that property. The drop is named in the `history` reason.

### issue-304-g3-001.d2 (`proposed-remedy`)
- BEFORE: "Before deleting shipped prose, grep the deleted phrases corpus-wide and treat every hit as a pin until proven otherwise, instead of trusting a handoff's suite list. Doing so here also found two live non-test references (a script docstring and a drill record) that the suite list could never have surfaced."
- AFTER: "Before the shipped prose was deleted, the deleted phrases were grepped corpus-wide and every hit was treated as a pin until proven otherwise, rather than the handoff's suite list being trusted; doing so also found two live non-test references (a script docstring and a drill record) that the suite list could never have surfaced."
- GROUNDING — **the assertion's own second sentence**, which records the sweep as performed: "Doing so here also found two live non-test references (a script docstring and a drill record) that the suite list could never have surfaced." Corroborated by sibling **d1**: "Grepping the deleted phrases across the repo finds those; listing the suites does not."

### issue-304-g3-003.a5 (`workaround`)
- BEFORE: "Answer 'was this already done?' with a command over git history rather than a reading of the current file, since it is a question about history: git log --format=%h -- <file>, then git show <sha>:<file> for each, printing the phrase under test."
- AFTER: "The question 'was this already done?' was answered with a command over git history rather than a reading of the current file, since it is a question about history: git log --format=%h -- <file>, then git show <sha>:<file> for each, printing the phrase under test."
- GROUNDING — sibling **a3**: "checking every one of the 8 commits that ever touched the template showed tasks.plan.imperative's opening phrase 'produce a mission frame from the current map' byte-identical from 5fad3e3 through fdec654 (the g2 anchor commit) to HEAD".

### issue-304-g3-003.d2 (`proposed-remedy`)
- BEFORE: "When a handoff asserts a prior gate already made a specific textual change, verify the specific STRING across the commits that touched the file, not the step's diff size or the commit message."
- AFTER: "The handoff asserted that a prior gate had already made a specific textual change; verifying the specific STRING across the 8 commits that touched the file, rather than the step's diff size or the commit message, is what falsified that premise."
- GROUNDING — sibling **a3**: "the handoff's premise was falsified: checking every one of the 8 commits that ever touched the template showed ... g2 APPENDED verify-frame prose without retargeting the phrase T3 named."

### issue-304-g3-004.a5 (`workaround`)
- BEFORE: "Locate a block by unique opening and closing phrases and delete the span between them, asserting uniqueness of both before touching the file; put the invariant in the editing tool as a refusal, not only in the test that runs afterwards."
- AFTER: "The block was located by unique opening and closing phrases and the span between them deleted, with the uniqueness of both asserted before the file was touched; the invariant was put in the editing tool as a refusal, not only in the test that runs afterwards."
- GROUNDING — sibling **a3**: "The deletion was performed by an offset-bounded slice located by the block's opening and closing phrases, each asserted UNIQUE in the raw file, never by a replace on the ambiguous phrase; the deletion script itself refuses (\"REFUSED (T4): phrase count after deletion is %d, expected exactly 1\") rather than leaving the guard only to the test suite."

### issue-304-g3-004.d2 (`proposed-remedy`)
- BEFORE: "Pin a deletion in BOTH directions -- dead text absent AND the survivor present -- because an absence-only assertion passes just as happily on an emptied field. Add an occurrence-count assertion when the deletion is disambiguating rather than removing."
- AFTER: "This deletion was pinned in BOTH directions -- dead text absent AND the survivor present -- rather than by an absence-only assertion, which passes just as happily on an emptied field; and because the deletion was disambiguating rather than removing, an occurrence-count assertion was included, pinning the survivor as present exactly once."
- GROUNDING — sibling **a3**: "The survivor is pinned three ways in tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives -- present, exactly once, and at the offset INSIDE the substitute-and-record sentence, so no other sentence can satisfy the count."

### issue-304-g3-005.a5 (`workaround`)
- BEFORE: "None available at this gate. The forward requirement, stated so POST can be built to meet it: POST must sample runs under BOTH the late anchor and the context anchor with map_before_src measured the same way, rather than re-reporting map_before_src under the new anchor alone."
- AFTER: "None was available at this gate. What the gate established instead is the forward requirement: separating 'insufficient' from 'irrelevant' requires runs sampled under BOTH the late anchor and the context anchor with map_before_src measured the same way, which re-reporting map_before_src under the new anchor alone cannot supply."
- GROUNDING — sibling **a3**: "separating the two requires runs under BOTH anchors with map_before_src measured identically -- a comparative experiment nobody has run." The AFTER uses the record's own "requires", a statement of what the experiment needs, in place of the forward-aimed "POST must".

### issue-309-001.d2 (`proposed-remedy`)
- BEFORE: "A future coherence-sweep design that wants to measure REALISTIC noise from realistically-instructed viewpoints (rather than instrument-validate the pathway's raw capacity for noise) should seed a decoy the target lens's own guardrail does NOT already name as an exclusion, so the noise measurement isn't structurally deflated by the lens wording itself."
- AFTER: "This sweep's decoy was one the target lens's own guardrail already named as an exclusion, so the 0% noise figure measured lens discipline rather than realistic noise from realistically-instructed viewpoints."
- GROUNDING — sibling **d1**: "Well-instructed viewpoints (given an explicit 'do not flag two independent policy choices as a contradiction' guardrail) are, by construction, resistant to a decoy engineered around exactly that shape -- the 0% noise result measures lens discipline, not an absence of noise risk in the underlying pathway." Corroborated by **a3** (DECOY1 was not flagged by either real viewpoint) and **a4** ("the two carefully-worded lenses proved too disciplined to bait on their own").

### issue-309-002.d2 (`proposed-remedy`)
- BEFORE: "docs/EPISODE_STORE.md section 1 should be updated to drop or caveat the now-stale git-check-ignore transcript for .agent-work/ specifically -- the store's own root (episodes/, never under .agent-work/) is unaffected by this staleness, only the illustrative contrast against .agent-work/ is now wrong. Filed as a triage candidate rather than edited directly this run (doctrine-text edit is out of this issue's Allowed Scope)."
- AFTER: "A triage candidate was filed proposing that docs/EPISODE_STORE.md section 1 drop or caveat the now-stale git-check-ignore transcript for .agent-work/ specifically -- the store's own root (episodes/, never under .agent-work/) is unaffected by this staleness, only the illustrative contrast against .agent-work/ is now wrong -- rather than the doc being edited directly this run, a doctrine-text edit being out of this issue's Allowed Scope."
- GROUNDING — **the assertion's own final sentence**, which records the disposition: "Filed as a triage candidate rather than edited directly this run (doctrine-text edit is out of this issue's Allowed Scope)." Corroborated by sibling **a3**: "EPISODE_STORE.md section 1's own claim about .agent-work/'s ignore status is now stale."

### issue-308-001.a5 (`workaround`) — the handoff's own worked BEFORE
- BEFORE: "Give the harness the same fail-safe discipline as the production code under test: wrap per-iteration work in try/except with a guaranteed stop-signal in `finally`, and mark helper threads daemon=True as a backstop."
- AFTER: "The harness was given the same fail-safe discipline as the production code under test: per-iteration work was wrapped in try/except with a guaranteed stop-signal in `finally`, and helper threads were marked daemon=True as a backstop."
- GROUNDING — sibling **a4**: "7 green re-runs followed the fix" (a fix was applied and verified). Sibling **a3** names exactly the two defects this fix addresses: "A writer thread died on a transient Windows os.replace sharing violation without signalling stop, leaving a non-daemon reader thread spinning forever."

### issue-308-002.a5 (`workaround`)
- BEFORE: "Before planning, grep the launch order's NAMED defect or sub-fix against current code, AND verify that any named EDIT TARGET (section heading, file path, anchor) actually exists at the named address."
- AFTER: "Before planning, the launch order's NAMED defect or sub-fix was grepped against current code, and any named EDIT TARGET (section heading, file path, anchor) was checked for existence at the named address."
- GROUNDING — sibling **a4**: "Every instance was caught BEFORE planning by grepping the named symbol or token, so no rework is attributable to any of them." Sibling **a3** case (2) grounds the edit-target half: "A named EDIT TARGET did not exist under that name -- 'the Decision Anchors section of commander-core.md' (epic-226 wt-230)."

### issue-308-004.a5 (`workaround`)
- BEFORE: "Verify the field's presence against the harness contract (docs) AND make the regression test drive the REAL writer path that populates it -- run handle_post_tool_use to write the binding, then decide_stop -- rather than a hand-injected fixture."
- AFTER: "The field's presence was verified against the harness contract (docs) and the regression test was made to drive the REAL writer path that populates it -- running handle_post_tool_use to write the binding, then decide_stop -- rather than a hand-injected fixture."
- GROUNDING — sibling **a3**, which records both halves as done: "the docs confirmed `cwd` is present on every hook event, but a real non-fixture reproduction showed its SCOPE was wrong -- session-lifetime-fixed, not per-call-live -- for a Commander-in-worktree dispatch."

### issue-308-005.a5 (`workaround`)
- BEFORE: "Pair every round-trip or enumeration test over real artifacts with adversarial fixtures authored to make the tool return a WRONG answer -- false FAIL on a valid input, silent PASS on an invalid one -- and instruct reviewers to hunt that specific class rather than only re-running the suite."
- AFTER: "In #301 the reviewer was told to AUTHOR adversarial fixtures that would make the tool return a WRONG answer -- false FAIL on a valid input, silent PASS on an invalid one -- rather than only re-run the suite over the real artifacts, and that is what found the defect."
- GROUNDING — sibling **a4**: "In #301 the defect was found only because the reviewer was told to AUTHOR adversarial inputs rather than re-run the suite." Sibling **a3** supplies both wrong-answer shapes: "a greedy-placeholder regex silently PASSED an ungraded decision and a nested sub-bullet false-FAILed a valid plan."
- DROPPED as ungrounded: the generalization to "every round-trip or enumeration test over real artifacts". The record evidences one applied instance, not an adopted universal.

### issue-308-006.a5 (`workaround`)
- BEFORE: "Pass an absolute path, and fall back to a manual attest-plus-advance when the child checklist is GATED rather than SURVEY."
- AFTER: "The runs fell back to a manual attest-plus-advance where the child checklist was GATED rather than SURVEY; where --from-child was usable at all, only an absolute path to the child was accepted."
- GROUNDING — sibling **a4**: "Forced a manual attest-plus-advance instead." Sibling **a3** (1): "It refuses a path to the child given relative to cwd, accepting only an absolute path -- unlike every other engine verb used in these runs."

### issue-308-007.a5 (`workaround`)
- BEFORE: "epic-226's own preventive extra-diligence workaround: write explicit HARVEST EXECUTED and HARVEST MANIFEST entries into the Admiral log before any sweep runs."
- AFTER: "epic-226's own preventive extra-diligence workaround was to write explicit HARVEST EXECUTED and HARVEST MANIFEST entries into the Admiral log before any sweep ran."
- GROUNDING — **the assertion's own subject phrase**, unchanged by the restatement: it already asserts this was epic-226's applied workaround. This is a mood-only rewrite adding no content. The record's mechanical `artifact-ref: epic-226/ADMIRAL_LOG.md` names the log it was written into.

### issue-308-008.a5 (`workaround`)
- BEFORE: "Run the cold plan critic as MANDATORY rather than bias-to-yes for any gate plan whose acceptance depends on a before/after measurement or a required round-trip or parser test."
- AFTER: "The cold plan critic was run as MANDATORY rather than bias-to-yes for gate plans whose acceptance depended on a before/after measurement or a required round-trip or parser test."
- GROUNDING — sibling **a4**, which records the policy as already in force: "This run, #308, is a further instance: the mandatory cold critic returned 2 BLOCKING findings on this issue's own gate plan." Read against sibling **a2**: "The cold plan critic was optional (bias-to-yes) at the time" — i.e. the record states the transition happened.

### issue-308-009.a5 (`workaround`)
- BEFORE: "Mutate the ambient os.environ['PATH'] directly rather than passing a restricted `env=` override."
- AFTER: "The ambient os.environ['PATH'] was mutated directly rather than a restricted `env=` override being passed."
- GROUNDING — sibling **a3**: "Established empirically by two pasted `py -c` transcripts comparing env={'PATH': d} against mutating os.environ['PATH'] directly."

### issue-308-010.a5 (`workaround`)
- BEFORE: "Use a `! <command>` bash-negation wrapper as the postcondition's `command` field, which turns 'the guard fired' into a mechanically re-verified engine check instead of a self-reported attest."
- AFTER: "A `! <command>` bash-negation wrapper was used as the postcondition's `command` field, which turns 'the guard fired' into a mechanically re-verified engine check instead of a self-reported attest."
- GROUNDING — sibling **a3**: "Confirmed once in 303: three command postconditions using the negation wrapper, all satisfied on first advance with no rework, with the verbatim commands, exit codes and stderr recorded in notes-303.md."

### issue-308-011.a5 (`workaround`)
- BEFORE: "Resolve the canonical target FIRST when a launch order fences a contended file, and qualify the stop-condition wording with 'if the edit is still required after canonical routing'."
- AFTER: "The canonical target was resolved FIRST under a launch order that fenced a contended file."
- GROUNDING — sibling **a3**: "Resolving the canonical target first made the contended edit unnecessary: under a PR-6-style canonical-source rule the content belonged in a different home, so the collision dissolved rather than needing resolution."
- DROPPED as ungrounded: "qualify the stop-condition wording with 'if the edit is still required after canonical routing'." Sibling **a4** says the opposite of applied: "UNKNOWN -- nothing beyond the floated decision is recorded."

### issue-308-012.a5 (`workaround`)
- BEFORE: "Place crew plan files in their own subdirectory, mirroring the reviewer role's <gate>-review/ convention, so they get their own gauge.json. A third attempt using .agent-work/governor-261/g1-implement-rework2-attempt3/ completed cleanly on the same task."
- AFTER: "The crew plan file was placed in its own subdirectory, mirroring the reviewer role's <gate>-review/ convention, so that it got its own gauge.json. A third attempt using .agent-work/governor-261/g1-implement-rework2-attempt3/ completed cleanly on the same task."
- GROUNDING — **the assertion's own second sentence**, which records the subdirectory attempt as run and clean. Corroborated by sibling **a3**: "checklist_engine.py's _gauge_path keys purely off the checklist file's own containing directory, so the crew's plan file resolved to the SAME gauge.json as the Commander's spine.json."

### issue-308-013.a5 (`workaround`)
- BEFORE: "Write a reviewer-side standalone script that loads the real module by file path (importlib) and defines the OLD handler inline as a local function, reusing the SAME real helpers the new code uses -- reproducing the contrast without ever mutating the file under review. The reviewer explicitly recommended promoting it as the documented default."
- AFTER: "The reviewer wrote a reviewer-side standalone script that loads the real module by file path (importlib) and defines the OLD handler inline as a local function, reusing the SAME real helpers the new code uses -- reproducing the contrast without ever mutating the file under review. The reviewer explicitly recommended promoting it as the documented default."
- GROUNDING — sibling **a3**: "The reviewer then improvised a working alternative within the same dispatch." Sibling **a4**: "no cost or rework is recorded; the reviewer solved it in-dispatch."

### issue-308-018.a5 (`workaround`)
- BEFORE: "Run a shared-assumption audit over the panel's convergences, by an auditor who did NOT author the brief, and treat unanimity across deliberately-differing constraints as evidence about the varied axis only."
- AFTER: "#300's panel ran a shared-assumption audit over its own convergences, which retracted one of five reported convergences after finding it was the BRIEF handed back rather than independent agreement, treating unanimity across deliberately-differing constraints as evidence about the varied axis only."
- GROUNDING — sibling **a3**: "In #300 the panel's own shared-assumption audit retracted a 'metadata only, never file content' convergence after finding it was the BRIEF handed back rather than independent agreement." Sibling **a4**: "#300's audit retracted one of five reported convergences."
- DROPPED as ungrounded: "by an auditor who did NOT author the brief." No sibling states the auditor's provenance.

### issue-308-020.a5 (`workaround`)
- BEFORE: "For shape 2, a quote-id-and-count protocol: compare the live staged file before harvest rather than trusting a name taken earlier. Shape 1 is covered by ordinary verification. The lesson's author explicitly warns against graduating shape 1 alone and considering the class closed."
- AFTER: "For shape 2, a quote-id-and-count protocol: the live staged file was compared before harvest rather than a name taken earlier being trusted. Shape 1 is covered by ordinary verification. The lesson's author explicitly warns against graduating shape 1 alone and considering the class closed."
- GROUNDING — sibling **a3**: "a fact shared between two agents that neither could see the other write -- caught before harvest only by comparing the live staged file."
- Sentences 2 and 3 already report rather than instruct and are carried through unchanged.

### issue-308-021.a5 (`workaround`)
- BEFORE: "Replace the hand-written enumeration with a script that enumerates the corpus itself and asserts the enumeration is non-empty -- .agent-work/issue-308/checks/lesson_intake_is_cut.py -- and verify a new guard by reading which sites it actually names, not by its exit code."
- AFTER: "The hand-written enumeration was replaced with a script that enumerates the corpus itself and asserts the enumeration is non-empty -- .agent-work/issue-308/checks/lesson_intake_is_cut.py -- and the new guard was verified by reading which sites it actually named, not by its exit code."
- GROUNDING — sibling **a4**: "Both were caught: the first by a cold plan critic, the second by running the guard and reading which sites it named." Sibling **a3** records the guard as written: "one revision later and inside the guard written to fix that, the character class [^.backslash-n]{0,40} excludes the dot".

### issue-308-023.a5 (`workaround`)
- BEFORE: "Dispatch an independent cold sensor in addition to the solo read, and treat the solo read's singletons as unconfirmed rather than as negatives. The candidate instruction as the sensor phrased it, recorded as the sensor's words and deciding nothing: 'before a check counts as evidence, state the condition under which it would FAIL and show it can reach that condition; if that condition is unobservable to the instrument, report a measurement gap, not a pass.'"
- AFTER: "An independent cold sensor was dispatched in addition to the solo read, and it found a cluster the solo read had recorded as a singleton, so the solo read's singletons stand as unconfirmed rather than as negatives. The candidate instruction as the sensor phrased it, recorded as the sensor's words and deciding nothing: 'before a check counts as evidence, state the condition under which it would FAIL and show it can reach that condition; if that condition is unobservable to the instrument, report a measurement gap, not a pass.'"
- GROUNDING — sibling **a1**: "one solo read by the commander, plus an independent cold sensor over the same 7 episodes." Sibling **a3**: "The sensor found a second strong cluster the commander's solo read had MISSED -- the solo read had grouped issue-304-g3-005 as a singleton." Sibling **a4** grounds the singleton clause: "one read is not enough to trust a null on any individual cluster."
- The sensor's quoted instruction sits inside an explicit quotation frame the record already supplies ("recorded as the sensor's words and deciding nothing") and is carried through verbatim; restating another party's quoted words would misquote them.

### issue-308-024.a5 (`workaround`)
- BEFORE: "Correct the check through the engine's sanctioned re-planning verbs (amend rescope for a gate, amend retext-check for one condition) rather than waiving it, and re-verify the replacement RED before doing the work that turns it green. A waived check stays in the tree asserting the old rule; a corrected one becomes the acceptance test the gate actually needs."
- AFTER: "Both checks were corrected through the engine's sanctioned re-planning verbs (amend rescope for a gate, amend retext-check for one condition) rather than waived, and both replacements were re-verified RED before the work that turned them green. A waived check stays in the tree asserting the old rule; a corrected one becomes the acceptance test the gate actually needs."
- GROUNDING — sibling **a3**, near-verbatim: "Both were corrected through the engine's amend verb (rescope and retext-check) rather than waived, and both replacements were verified RED before the work that would make them green."

### issue-308-025.a5 (`workaround`)
- BEFORE: "Instruct the downstream reader to verify BY CONTENT rather than by count, naming each item that must survive, so a wrong total in the handoff cannot become a wrong action. The count was wrong and the work was still correct, because nothing depended on the count alone."
- AFTER: "The handoff instructed the downstream reader to verify BY CONTENT rather than by count, naming each item that had to survive, so the wrong total in the handoff did not become a wrong action. The count was wrong and the work was still correct, because nothing depended on the count alone."
- GROUNDING — sibling **a3**: "It was caught by the g5 reviewer following an instruction the same handoff carried: verify the surviving writer BY CONTENT, not by count." Sibling **a4**: "the reviewer's by-content check confirmed all four survivors afterwards."

## Evidence 3 — UNGROUNDED list (left untouched, exactly as found)

Five statements are instructions under the standard but the record cannot support a factual
restatement. All five were left alone. Gate g3's exception mechanism owns them.

1. **issue-304-g3-005.d2** (`proposed-remedy`) — "Either measure ordering where it is observable (a
   run transcript / a PreToolUse-style observer), or stop treating a receipt check as evidence about
   ordering and describe it as what it is -- a floor against orientation never happening at all."
   **Reason:** two branches of advice, and the record states that *neither* was taken. a3 records the
   gate as "NOT DETERMINABLE AT THIS GATE" and says the receipt "observes nothing about when any file
   was read"; d1 says ordering "is a property of the transcript, and no artifact in this pipeline
   carries the transcript." Restating it factually would either invent an act nobody performed, or
   collapse the assertion into a duplicate of d1.

2. **issue-308-014.a5** (`workaround`) — "When authoring or updating a drill for a doctrine pattern
   that recurs across sibling templates, enumerate every sibling template carrying the pattern in the
   drill's 'doctrine under test' line, or explicitly note which ones it does NOT cover."
   **Reason:** no sibling records that the drill was ever updated. a3 and a4 record only the defect —
   the drill named one sibling, the sweep found another, "the drill could not have surfaced it by
   re-running". Writing "the drill was updated to enumerate every sibling" would be a fabrication.

3. **issue-308-015.a5** (`workaround`) — "Keep the lightweight design-it-twice pass plus one solo cold
   critic as a default floor even when a run judges a full panel unnecessary."
   **Reason:** this asserts an adopted standing policy. The record evidences one run (governor-265)
   that used the pass and found a gap (a1, a3); no sibling says it was made a floor. a4 explicitly
   calls it "A single data point from one run." Restating it as "the pass was kept as a default floor"
   would claim a policy change the record does not contain, and restating it as "governor-265 ran the
   pass" would replace the assertion with a copy of a1 and a3 rather than restate it.

4. **issue-308-017.a5** (`workaround`) — "Replace the hand-maintained list with the computable property
   the code already owns. For the parser guard, the predicate 'value is non-empty and
   value.splitlines() != [value]' ... For the classifier, the store's own id grammar (episode_id_for()),
   applied uniformly to both directories."
   **Reason:** no sibling records the replacement as made. a3 describes the two defects and a4 records
   detection only ("The g4 instance was a cold-panel BLOCK"). The repo's `episodes/README.md` does say
   the classifier now uses `episode_id_for()`, but that is outside this record, and the handoff's rule
   is grounding *within the same record*.

5. **issue-308-019.a5** (`workaround`) — "Require the check to demonstrate it actually ran against
   something that could have failed it: accept an interpreter only if it REPORTS the floor version when
   asked; author an adversarial fixture for a test; use a bash-negation proving the guard fires for a
   postcondition. Mutation-testing a guard ... is the cheap general form, and the mutation must itself
   be asserted to have applied."
   **Reason:** the record explicitly files this as a *proposal*, not an application. a4: "The suggested
   upstream edit recorded at export: extend the repair clause to 'mutate, ASSERT THE MUTATION APPLIED,
   then watch it go red'". Only one sub-clause has any applied instance (a3 (4), "exposed only by
   separately asserting the mutation had applied"); the requirement list as a whole was never adopted.

### Borderline calls recorded, not restated

Three statements were examined closely and judged OBSERVATION under the standard:

- **issue-304-g3-005.a1 and .a2** are the store's only two second-person hits
  (`grep -nE "^- statement:.*\b(you|your)\b" episodes/active/*.md` -> 2). Both are **quotations** of
  the context imperative under study ("before you open any source file"), not the record addressing
  its own reader.
- **issue-309-002.a2** — "git check-ignore -v ... should exit 0 (ignored)". A *predictive* `should` in
  an `expected-behavior` field, directing no reader. The standard's test is "used as a directive".
- **issue-309-002.a5** — "worktree-local .agent-work/issue-309/.gitignore ... keeps the seeded slice
  out of git". Noun-phrase subject, present-tense predicate, no imperative clause.

## Evidence 4 — doctrine candidates (COLLECTED ONLY, nothing promoted)

Nothing in this list was written anywhere but here. No file under `docs/agents/` was touched and no
new file was created to hold any of it. Promotion is the human's call.

Each entry states the rule as the record originally worded it; every original also survives verbatim
in its assertion's own `history` line in the store.

| # | episode.assertion | the rule as stated | why it looks like doctrine |
|---|---|---|---|
| 1 | issue-308-002.a5 | Before planning, grep the launch order's NAMED defect or sub-fix against current code, AND verify that any named EDIT TARGET actually exists at the named address. | The most-confirmed entry in the migrated bank (a4: "mentions 9, confirmed 6, disconfirmed 0 ... the most-confirmed entry in the bank and never disconfirmed"), six confirmations across three epics in four distinct failure modes. Applies to every delegated Commander, not to one run. |
| 2 | issue-308-008.a5 | Run the cold plan critic as MANDATORY rather than bias-to-yes for any gate plan whose acceptance depends on a before/after measurement or a required round-trip or parser test. | a3: "Every run that ran it found a plan-invalidating defect before any crew was dispatched" — five named runs. A standing planning policy, and a2 records that the policy was previously optional, i.e. this is a proposed change to a rule. |
| 3 | issue-308-019.a5 | Require the check to demonstrate it actually ran against something that could have failed it; mutation-test the guard and assert the mutation itself applied. | Five or more instances in one epic by different mechanisms (a3). Already recorded as exported constellation debt with a named upstream edit (a4). The clearest general rule in the set. |
| 4 | issue-308-005.a5 | Pair every round-trip or enumeration test over real artifacts with adversarial fixtures authored to make the tool return a WRONG answer, and instruct reviewers to hunt that class rather than only re-running the suite. | Confirmed three times over three different tools (a3). A test-design rule with no run-specific content. |
| 5 | issue-304-g3-004.d2 | Pin a deletion in BOTH directions -- dead text absent AND the survivor present -- because an absence-only assertion passes just as happily on an emptied field. | A general test-design invariant. The same record's a4 records the counterfactual: firing "would have silently degraded the artifact this issue set out to strengthen." |
| 6 | issue-304-g3-004.a5 | Locate a block by unique opening and closing phrases and delete the span between them, asserting uniqueness of both; put the invariant in the editing tool as a refusal, not only in the test that runs afterwards. | "Put the invariant in the tool as a refusal, not only in the test" is a general engineering posture, and it matches the corpus's existing "fail visibly rather than emit plausible wrong output". |
| 7 | issue-304-g3-001.d2 | Before deleting shipped prose, grep the deleted phrases corpus-wide and treat every hit as a pin until proven otherwise, instead of trusting a handoff's suite list. | A general blast-radius rule for prose deletions, and it names the exact failure the handoff's own suite list produced. |
| 8 | issue-304-g3-003.a5 + .d2 | Answer "was this already done?" with a command over git history rather than a reading of the current file; verify the specific STRING across the commits that touched the file, not the diff size or the commit message. | Both assertions in one record converge on the same rule. Reading the current file would have CONFIRMED the false claim (a3) — a check that cannot fail. |
| 9 | issue-308-021.a5 | Replace a hand-written enumeration with a script that enumerates the corpus itself; verify a new guard by reading which sites it actually names, not by its exit code. | a4 records recurrence 2 by the same agent within an hour "under maximal awareness -- the agent had just finished writing down that this is a recurring failure mode." Prose demonstrably did not stop it, which is itself an argument that it belongs in a mechanism rather than doctrine. |
| 10 | issue-308-025.a5 | Instruct the downstream reader to verify BY CONTENT rather than by count, naming each item that must survive, so a wrong total cannot become a wrong action. | a3 records this as "the THIRD instance of an under-inclusive enumeration presented as complete within issue #308 alone", and a4 that "The cost was zero because the counter-measure fired, not because the enumeration was right." A handoff-authoring rule. |
| 11 | issue-308-024.a5 | Correct a check through the engine's sanctioned re-planning verbs rather than waiving it, and re-verify the replacement RED before doing the work that turns it green. | a4's counterfactual is stark: "Had either been waived instead of corrected, the run would have finished green with a check in the tree asserting the opposite of its requirement." A rule about the engine's own waive/amend choice. |
| 12 | issue-308-023.a5 | Dispatch an independent cold sensor in addition to the solo read, and treat the solo read's singletons as unconfirmed rather than as negatives. | Generalises beyond rhyme-search to any single-reader survey. The sensor's own quoted phrasing inside this assertion is an even broader candidate: "before a check counts as evidence, state the condition under which it would FAIL and show it can reach that condition." |
| 13 | issue-308-018.a5 | Run a shared-assumption audit over a design panel's convergences, by an auditor who did NOT author the brief, and treat unanimity across deliberately-differing constraints as evidence about the varied axis only. | a3 states the underlying property generally: "A panel varies what it is told to vary and inherits everything it is not." A rule about design-it-twice, which this corpus runs as standard. |
| 14 | issue-308-017.a5 | Replace a hand-maintained list with the computable property the code already owns. | a3 quotes the lesson's author naming the general tell: "a list a human maintains standing in for a predicate the code can decide." Two instances in one run in different costumes. |
| 15 | issue-308-014.a5 | When authoring a drill for a doctrine pattern that recurs across sibling templates, enumerate every sibling carrying the pattern, or note which ones it does NOT cover. | The class-sweep counterpart of the blast-radius rule already in `global-everyone.md`. Note: the store's own canonical worked record in `docs/EPISODE_STORE.md` carries this same rule at `governor-268-003.d2`. |
| 16 | issue-308-007.a5 | Write explicit HARVEST EXECUTED and HARVEST MANIFEST entries into the Admiral log before any sweep runs. | a4 records a real "data-loss-narrowly-averted event, caught by a human rather than by any check" in f1Brainz epic-601. An Admiral closeout rule with an unpaid mechanical fix behind it. |
| 17 | issue-308-001.a5 | Give a test harness the same fail-safe discipline as the production code under test: guaranteed stop-signal in `finally`, helper threads daemon=True. | A general harness-authoring rule; the failure mode it prevents (a hung pytest process) hides the failure entirely rather than reporting it. |
| 18 | issue-308-013.a5 | Reproduce an OLD-versus-NEW contrast with a standalone script that loads the real module by file path and defines the old handler inline, rather than mutating the file under review. | The record notes "The reviewer explicitly recommended promoting it as the documented default" — an explicit promotion request already sitting in the store. |
| 19 | issue-308-015.a5 | Keep the lightweight design-it-twice pass plus one solo cold critic as a default floor even when a run judges a full panel unnecessary. | A standing floor for planning rigor. Weakest evidence in this list — one run, a4 records "A single data point." |
| 20 | issue-308-011.a5 | Resolve the canonical target FIRST when a launch order fences a contended file. | a3: resolving canonically "made the contended edit unnecessary ... the collision dissolved rather than needing resolution." A concurrency-wave rule for Admirals. |
| 21 | issue-308-020.a5 | Compare the live staged file before harvest rather than trusting a name taken earlier. | a4 scopes it as "a property of the multi-agent machinery itself -- it appears only where two agents share a fact neither can see the other write, which is the worktree-and-harvest topology this corpus runs on." |
| 22 | issue-304-g3-005.d2 | Either measure ordering where it is observable, or stop treating a receipt check as evidence about ordering and describe it as what it is -- a floor against orientation never happening at all. | A rule about what a receipt check may be claimed to prove. Also on the UNGROUNDED list. |

**Not doctrine — tool and platform facts, listed for completeness:** `issue-308-006.a5` (`--from-child`
needs an absolute path and a SURVEY-type child), `issue-308-009.a5` (on Windows, `CreateProcess`
resolves an executable name against the *calling* process's environment, so a restricted child `env=`
does not control resolution), `issue-308-010.a5` (the `! <command>` bash-negation wrapper as a
postcondition), `issue-308-012.a5` (crew plan files need their own subdirectory to get their own
`gauge.json`). These are facts about specific tools, and two of them name upstream defects with open
fixes rather than rules an agent should follow.

## Evidence 5 — `git diff --stat episodes/` and the no-hand-edit proof

```
$ git diff --stat episodes/ | tail -1
 24 files changed, 54 insertions(+), 27 deletions(-)
```

**How I know no file under `episodes/` was hand-edited** — four independent checks:

1. **Every changed file is traceable to a named delta file.** The set of files git reports changed is
   byte-identical to the set of episode ids the four delta JSONs name:
   ```
   $ git status --short episodes/ | awk '{print $2}' | tr -d '\r' | sort > /tmp/gitchanged.txt
   $ python -c "<extract every op's id from .agent-work/r418-460/deltas/*.json>" > /tmp/deltanamed.txt
   $ diff /tmp/gitchanged.txt /tmp/deltanamed.txt
   IDENTICAL: all 24 changed files are exactly the 24 episodes named by the delta files
   ```
   The same extraction asserts every op is `restate-assertion`: 27 ops, 24 distinct episodes.

2. **The diff has the writer's shape and only the writer's shape.** Across all 24 files the *only*
   lines added are 27 `- statement:` and 27 `- history:`, and the only lines removed are 27
   `- statement:`. No `kind`, `strength`, `lifecycle-standing`, mechanical line or retirement block
   moved — which is exactly the `restate-assertion` contract and is not what a hand-edit produces.
   (Commands and output under Evidence 1.)

3. **Every restatement carries a writer-built history line quoting the original verbatim.** The
   writer constructs `restated — <reason> — original statement was: <original>` from the statement it
   parsed off disk; a caller cannot supply it. 27 restatements, 27 such lines.

4. **No `Edit`, `Write` or `sed` was ever issued against a path under `episodes/`.** The only writes
   were four `python scripts/apply_episode_delta.py ... --store-root episodes` invocations, listed
   below. The store still parses under its own tooling afterwards:
   `python scripts/query_episodes.py --store-root episodes enumerate` -> exit 0.

`git status --short episodes/` lists 24 ` M` entries and no `??`, so nothing was added or removed —
only the 24 intended records changed. **No `issue-447-*` file appears** (`git status --short
episodes/ | grep -c 'issue-447'` -> 0), matching the m4 finding that all 16 are already compliant.
`episodes/retired/` was not touched.

## Evidence 6 — delta files and the exact writer invocations

All four delta files are kept as evidence under `.agent-work/r418-460/deltas/` (tracked;
`git check-ignore .agent-work` exits 1).

| delta file | ops | episodes |
|---|---|---|
| `01-issue-308-001.json` | 1 | issue-308-001 |
| `02-issue-304-g3.json` | 7 | issue-304-g3-001 (a5, d2), -003 (a5, d2), -004 (a5, d2), -005 (a5) |
| `03-issue-309.json` | 2 | issue-309-001 (d2), issue-309-002 (d2) |
| `04-issue-308.json` | 17 | issue-308-002, -004, -005, -006, -007, -008, -009, -010, -011, -012, -013, -018, -020, -021, -023, -024, -025 (all a5) |

Every invocation, each dry-run first and each carrying `--store-root episodes`:

```
python scripts/apply_episode_delta.py --delta .agent-work/r418-460/deltas/01-issue-308-001.json --store-root episodes --dry-run
python scripts/apply_episode_delta.py --delta .agent-work/r418-460/deltas/01-issue-308-001.json --store-root episodes
python scripts/apply_episode_delta.py --delta .agent-work/r418-460/deltas/02-issue-304-g3.json  --store-root episodes --dry-run
python scripts/apply_episode_delta.py --delta .agent-work/r418-460/deltas/02-issue-304-g3.json  --store-root episodes
python scripts/apply_episode_delta.py --delta .agent-work/r418-460/deltas/03-issue-309.json     --store-root episodes --dry-run
python scripts/apply_episode_delta.py --delta .agent-work/r418-460/deltas/03-issue-309.json     --store-root episodes
python scripts/apply_episode_delta.py --delta .agent-work/r418-460/deltas/04-issue-308.json     --store-root episodes --dry-run
python scripts/apply_episode_delta.py --delta .agent-work/r418-460/deltas/04-issue-308.json     --store-root episodes
```

All eight exited 0. Each dry run printed its `restated <id>.<assertion>` log and `DRY RUN — no write`;
each real run printed the same log with no `DRY RUN` line.

**The `--store-root episodes` guard was verified, not assumed.** Immediately after the first real
write: `git status --short episodes/` -> ` M episodes/active/issue-308-001.md`. The writer wrote into
the repo store, not into `~/.claude/skills/constellation-admiral/episodes`.

## Evidence 7 — test suite

Command exactly as specified, real exit code captured directly (not through a pipe):

```
$ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
FAILED tests/test_episode_negative_control.py::test_canon_episode_store_untouched
1 failed, 1744 passed, 4 skipped, 677 subtests passed in 426.93s (0:07:06)
EXIT=1
```

Full output: `.agent-work/r418-460/evidence/g2-implement-pytest.txt`. Exit code captured with
`echo "EXIT=$?"` written directly to the file immediately after the command, not through a pipe.

Against the handoff's stated baseline (1742 passed, 4 skipped, 672 subtests): **+2 passed, +5
subtests**, which is g1's rework, and **one failure**, characterized below.

### The one failure — `test_canon_episode_store_untouched`

**This is not a defect in the restatements, and it is not mine to fix.** It is a guard that goes red
whenever `episodes/` has *any* uncommitted change, which is the state issue #460 necessarily
produces. Because the Commander commits, not me, this gate cannot leave the suite green.

What the test asserts (`tests/test_episode_negative_control.py:1148-1150`):

```python
dirty = subprocess.run(
    ["git", "status", "--porcelain", "episodes/"], cwd=str(REPO_ROOT), ...
).stdout.strip()
assert dirty == "", f"canon episode store is dirty: {dirty}"
```

It reads `git status --porcelain` only. It never opens an episode file and never inspects any
statement, so no restatement's *content* can affect it.

**Proved by command, not argued:**

1. The dirty set it reports is exactly my 24 files and nothing else
   (`git status --porcelain episodes/ | wc -l` -> 24, and the assertion message lists those 24).
2. With `episodes/` clean the test passes, on this same tree:
   ```
   $ git stash push -- episodes/
   $ git status --porcelain episodes/ | wc -l
   0
   $ FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_episode_negative_control.py::test_canon_episode_store_untouched
   1 passed in 0.42s
   $ git stash pop
   $ git diff --stat episodes/ | tail -1
    24 files changed, 54 insertions(+), 27 deletions(-)
   ```
   The stash round-trip restored the work exactly — 24 files, 54 insertions, 27 deletions, 27
   `- statement` and 27 `- history` added lines, `git stash list` empty. Nothing was lost, and the
   restatements are in any case reproducible byte-for-byte from the four delta files.

**Why the guard is wider than its own stated intent.** Its docstring and the comment block above it
(`tests/test_episode_negative_control.py:983-995`) name its purpose as
`constraint:throwaway-consolidation` — "a test artifact must never become canon", the belt-and-braces
half of proving *this module's* synthetic consolidation ran in a temp store. The assertion two lines
above it (`assert REPO_ROOT not in seeded_store["root"].parents`) already establishes that. The
blanket dirty check adds a second, much broader claim — "nobody has uncommitted work in
`episodes/`" — and it cannot tell "this test module leaked into canon" apart from "the gate now
running legitimately changed the store through the sanctioned writer and has not committed yet."

It was introduced at `4cec87a` (#305/#327), before both #447 and #460.

**I did not touch it.** `tests/` is not in this gate's Allowed Scope, which is `episodes/active/*.md`
through the writer plus my delta JSONs. Fixing it is a scope decision and a test-authorship decision,
both above me — raised to the Commander through the engine's `block` verb on `m5-verify-report` and
flagged as a triage candidate. Recommended resolutions, for the Commander to choose between:

- **Commit first, then re-run.** The guard goes green the moment `episodes/` is committed, so if the
  Commander's own gate ordering runs the suite after the commit, nothing needs changing. This is the
  zero-change option and my recommendation for unblocking #460 itself.
- **Narrow the guard to its stated intent** — assert that nothing *this test module* wrote reached
  canon, rather than that the whole store is clean. That is the durable fix, and it is a separate
  issue.

Every other check in the suite is green: 1744 passed, 4 skipped, 677 subtests.

---

## Engine state at handoff

Plan `.agent-work/r418-460/crew-plans/g2-implement-plan.json`, lease `g2-impl-r418-460` released.

| item | state |
|---|---|
| m0-context | complete |
| m1-inventory | complete |
| m2-first-write | complete |
| m3-restate-rest | complete |
| m4-check-447 | complete |
| m5-verify-report | **blocked**, bubbled to parent |

On `m5-verify-report`, **c2 is satisfiable and c1 is not**:

- **c2** (IMPLEMENTER_RESULT written with the count, grounding table, UNGROUNDED list, doctrine
  candidates, diffstat and suite exit code) — its check command passes now, exit 0. It shows `unmet`
  only because `advance` never ran; `advance` refuses while c1 fails, and the engine runs both checks
  together.
- **c1** (full suite green) — fails on the one guard described under Evidence 7, which needs the
  Commander's commit or a decision above this crew.

To resume after committing `episodes/`:
`resume m5-verify-report --reason "episodes/ committed; canon-store guard no longer dirty"`, then
`advance m5-verify-report`. Evidence `e-m5-verify-report-1` (the real suite run, exit 1) and triage
candidate `tc1` are already attached to the plan.

## Assumptions used

1. **The `restate-assertion` `history` field is the reason only.** The writer builds the quotation of
   the original itself (`_restatement_history_line`), so my `history` values state why the
   restatement was made and, where a clause was dropped, that it was dropped and why. I did not paste
   any original into `history`.
2. **Grounding may be the restated assertion's own recorded application.** In three cases
   (issue-304-g3-001.d2, issue-309-002.d2, issue-308-012.a5) the assertion's own trailing sentence
   records that the action was performed. I treated that as at least as strong as a sibling and said
   so explicitly rather than silently. See Workflow Feedback.
3. **A grounded clause may be kept when an ungrounded clause in the same statement is dropped.**
   Four restatements dropped a clause the record cannot support (304-g3-001.a5, 308-005.a5,
   308-011.a5, 308-018.a5). Nothing is lost: the writer preserves the full original verbatim in the
   assertion's history line. Each drop is named in the `history` reason and in the table above.
4. **A quoted instruction inside an explicit quotation frame is not the record instructing.** In
   issue-308-023.a5 the sensor's words are already framed "recorded as the sensor's words and
   deciding nothing"; rewriting them would misquote a third party. Carried through verbatim.
5. **`task-intent` in the bare infinitive is exempt** per the handoff and `docs/EPISODE_STORE.md:171`.
   No `task-intent` was touched. I checked all 48 for second person: the only two hits are quotations
   of the artifact under study.
6. **The engine was driven from the installed skill copy** (`C:/Users/fredc/.claude/skills/constellation-implementer/scripts/checklist_engine.py`),
   not the repo's vendored `scripts/checklist_engine.py`, because a concurrent sibling (#433) owns
   that file and the handoff forbids me touching it.

## Stop conditions hit

**One, at the last gate: the suite is red and fixing it would exceed scope.**
`tests/test_episode_negative_control.py::test_canon_episode_store_untouched` asserts that
`episodes/` has no uncommitted changes. Issue #460's whole deliverable is uncommitted changes to
`episodes/`, and I do not commit — the Commander does. The guard is proved content-independent and
clean-tree-passing under Evidence 7. `tests/` is outside this gate's Allowed Scope, so I raised it
rather than touching it: `block` on `m5-verify-report` through the engine, plus a triage candidate.
Recommended: commit `episodes/`, then re-run; separately, narrow the guard to its stated intent.

The other stop conditions did **not** fire. No hand-edit of `episodes/` was ever required; the writer
refused nothing; the restatement work itself is complete. The five UNGROUNDED statements are the
handoff's designed outcome, not a stop.

## Out-of-scope observations (triage candidates)

1. **`scripts/query_episodes.py` takes `--store-root` before the subcommand; `apply_episode_delta.py`
   takes it after.** `python scripts/query_episodes.py enumerate --store-root episodes` errors with
   "unrecognized arguments". Given that the whole hazard class this gate works under is a silently
   wrong `--store-root`, two sibling tools disagreeing on where that flag goes is worth one issue.
   Cosmetic, no data risk — the wrong form errors loudly.
2. **`docs/EPISODE_STORE.md`'s own canonical worked record contains a prescriptive assertion.**
   `governor-268-003.d2` at `docs/EPISODE_STORE.md` §3 reads "...the drill's 'doctrine under test'
   line should enumerate every sibling template carrying the pattern". If the store's rule is that a
   record never instructs, the documentation's model record teaches the opposite shape. That doc is
   gate g4's, so I did not touch it — flagging it so g4 sees it.
3. **`issue-308-014.a5` and the doc's `governor-268-003.d2` are the same rule**, one in the live store
   and one in the doc's example. If the human promotes it to `docs/agents/*`, both sites are affected.
4. **`test_canon_episode_store_untouched` is wider than its stated intent** and blocks any gate that
   changes `episodes/` before committing (full characterization under Evidence 7). Its own docstring
   scopes it to `constraint:throwaway-consolidation` — proving *this test module's* synthetic
   consolidation never reached canon — but it asserts the entire store is clean. Worth its own issue:
   narrow it to the module's own artifacts, or make it tolerate a working tree the running gate owns.
   Noted in passing: this is the same shape as the failure class the episodes it guards are about —
   a check whose pass condition is broader than the property it was written to establish.

## Workflow feedback

1. **The required-evidence format assumes grounding is always a *sibling* assertion.** Item 2 says
   "which sibling assertion, quoted". For three restatements the strongest grounding is the restated
   assertion's *own* recorded application of the advice it gives ("Doing so here also found...",
   "Filed as a triage candidate...", "A third attempt ... completed cleanly"). I labelled these
   explicitly rather than forcing a weaker sibling. A future handoff should say "sibling assertion or
   the assertion's own recorded application".
2. **The handoff has no stated policy for a *partially* grounded statement.** The worked contrast
   shows a clean one-for-one rewrite, but four statements bundle a grounded clause with an ungrounded
   one. I chose: restate the grounded part, drop the rest, and name the drop in the writer's own
   `history` reason — safe because the writer preserves the original verbatim. That was my call, not
   the handoff's; naming the policy would remove the judgment.
3. **"Deontic modal aimed forward (`must`, `should` ... used as a directive)" needed the trailing
   qualifier to be usable.** `expected-behavior` fields legitimately predict with "should"
   (issue-309-002.a2). "Used as a directive" resolved it, but only just — an explicit carve-out for
   predictive `should` in `expected-behavior` would make this mechanical rather than judged.
4. **The 48/32/16 scope split was accurate and the pre-computed counts saved a pass.** The instruction
   to CHECK rather than assume the 16 `issue-447` records was worth the time even though the answer
   was "clean" — they turned out to be the best available model of the target wording, and
   `issue-447-005.a5` is exactly the AFTER-SHAPE the handoff cites.
5. **The `--store-root episodes` warning was concrete enough to act on immediately** — flag, hazard,
   and the exact verification command. That is the most useful shape a constraint can take.

## Map Impact

Reusing the inbound anchor vocabulary; recorded as candidates, not authored into the map.

- **Capability — episode record content in `episodes/active/`:** changed in 24 of 48 active records
  (27 assertions). No record was created, retired or removed; the population is still 48 active / 0
  retired. Kind, strength and lifecycle-standing are unchanged everywhere.
- **Constraint — "an episode records what happened and is never read back as a rule"
  (`docs/agents/ORCHESTRATOR_CONTEXT.md`, The Retired Learning Playbook):** now honoured by 43 of 48
  active records. Five still carry an instruction the record cannot support restating (the UNGROUNDED
  list); that residue is gate g3's exception mechanism, and it is a known, enumerated set rather than
  an unbounded one.
- **Constraint — `docs/EPISODE_STORE.md` §5, "the record grows rather than getting rewritten":**
  upheld. Every one of the 27 restatements is additive on net (+2 lines, -1 line per assertion), and
  the original wording of all 27 survives verbatim in-record.
- **Structural — `scripts/apply_episode_delta.py` as the only write path:** unchanged and unmodified.
  This gate is the first use of g1's `restate-assertion` op at scale (27 invocations across 4 deltas,
  all clean, dry-run and real agreeing exactly). No defect found in the op.
- **Decision anchor — rewrite through `restate-assertion` rather than `amend-assertion`
  (`@grade: settled/inherited`):** executed as written, not revisited. The `history` line the op
  builds is what makes the "no invented facts" audit possible after the fact, because every BEFORE is
  still readable in-tree next to its AFTER.
- **Map confidence:** unchanged, still `DEGRADED-NO-MAP`. This slice adds no callable symbol and no
  new seam, so the Wiring Grep stays "none" as the handoff stated.
