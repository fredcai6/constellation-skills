# REVIEW_RESULT

**Verdict: APPROVE**

Repo: `/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle`
Branch: `feat/567-k-one-spine-mutable-middle`.

Driven through the checklist engine as a survey (`.agent-work/567-k/g2-review/review.json`,
session `g2-review-reviewer-attempt-1`); no spine was bound for this crew (`SPINE_PARENT` only,
`SPINE_FILE`/`SPINE_SESSION` unset), so I authored and drove my own survey per the reviewer
skill's documented branch for that case. I did not trust the implementer's account — every
criterion below was independently reproduced: diff read line-by-line, JSON loaded and computed
(not eyeballed), a wrong-gate mutation run to prove the pinning test can fail, all three templates
instantiated, and the end-to-end refusal/success pair reproduced fresh-process on a throwaway copy.

## Criteria (handoff's numbering)

**1. Exact declarations, nothing else.** Computed the flagged-gate set per template with
`json.load` + a set comprehension, not by reading the diff:
```
COMMANDER_SPINE.template.json actual= ['archive', 'init'] expected= ['archive', 'init'] MATCH
ADMIRAL_SPINE.template.json   actual= ['closeout', 'init'] expected= ['closeout', 'init'] MATCH
EXPLORER_SPINE.template.json  actual= ['init', 'route']    expected= ['init', 'route']    MATCH
```
No other gate in any of the three templates carries the flag (the same set comprehension would
have caught it). PASS.

**2. The pinning test can fail.** Moved the flag on `COMMANDER_SPINE.template.json` from `archive`
to `feedback` (backed up the original working-tree copy first) and reran:
```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_checklist_engine.py -k Bookend
...
AssertionError: Items in the first set but not the second:
'feedback'
Items in the second set but not the first:
'archive' : COMMANDER_SPINE.template.json: expected bookend gates ['archive', 'init'], got ['feedback', 'init']
1 failed, 11 passed, 456 deselected, 2 subtests passed
```
RED confirmed. Restored the file (see Workflow Feedback — my first restore attempt used
`git checkout --`, which reverted to pre-diff HEAD, not the implementer's working-tree state;
caught it immediately and restored correctly from my own backup). Confirmed tree clean afterward:
```
$ git diff --stat skills/commander/templates/COMMANDER_SPINE.template.json
(empty — matches original diff exactly)
$ python -m pytest -q tests/test_checklist_engine.py -k Bookend
11 passed, 456 deselected, 3 subtests passed
```
PASS.

**3. Templates still valid and instantiable.** `python3 -c "json.load(...)"` on all three: valid.
Instantiated each through the real path:
```
python scripts/init_work_area.py test-commander --root <tmp> --spine skills/commander/templates/COMMANDER_SPINE.template.json
python scripts/init_work_area.py test-admiral   --root <tmp> --spine skills/admiral/templates/ADMIRAL_SPINE.template.json
python scripts/init_work_area.py test-explorer  --root <tmp> --spine skills/explorer/templates/EXPLORER_SPINE.template.json
```
All three produced `spine ready: ...`; each resulting `spine.json`'s `tasks` carried the expected
bookend pair (`{'init','archive'}`, `{'init','closeout'}`, `{'init','route'}`) unchanged after
instantiation. PASS.

**4. The declaration works end to end.** Built a fresh fixture from
`COMMANDER_SPINE.template.json` (`init`/`context`/`understand`/`plan` complete, `execute`
in-progress, saved to a **copy** under `/tmp`, never the live spine), then in a **fresh**
`python scripts/checklist_engine.py` subprocess with crew env vars unset:
```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
    python scripts/checklist_engine.py --file <tmp>/copy.json amend \
    --delta <tmp>/delta_drop.json --reason "reviewer e2e proof: is closing bookend frozen?" \
    --authority "g2-reviewer"
REFUSED: drop archive: a declared bookend gate cannot be dropped, regardless of status Recovery: amend's drop only applies to a pending gate; archive is 'pending' and no verb reaches a pending status from here -- escalate to a human if the plan genuinely needs to change. Do not edit the JSON — use the engine.
exit=1
```
```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
    python scripts/checklist_engine.py --file <tmp>/copy.json amend \
    --delta <tmp>/delta_add.json --reason "reviewer e2e proof: does the middle still grow?" \
    --authority "g2-reviewer"
amended: added midstep (authority g2-reviewer)
exit=0
items now: ['init', 'context', 'understand', 'plan', 'execute', 'midstep', 'reconcile', 'triage', 'review', 'feedback', 'archive']
```
(`delta_add.json` op: `{"op":"add","id":"midstep","title":"Mid-run addition","imperative":"reviewer e2e proof gate","postconditions":[{"id":"c1","statement":"proof placeholder","check":null,"satisfied":false}],"after":"execute"}` — a bare `{"op":"add","id":"midstep","after":"execute"}` was refused first with `add midstep: a gated gate needs >=1 postcondition`, which is the engine's own general `add` validation, unrelated to the bookend guard.)
Both halves PASS.

**5. Diff hygiene.**
```
$ git diff --stat skills/ tests/test_checklist_engine.py
 skills/admiral/templates/ADMIRAL_SPINE.template.json     |  4 +--
 skills/commander/templates/COMMANDER_SPINE.template.json |  4 +--
 skills/explorer/templates/EXPLORER_SPINE.template.json   |  4 +--
 tests/test_checklist_engine.py                           | 31 ++++++++++++++++++++++
 4 files changed, 37 insertions(+), 6 deletions(-)
```
Each template hunk is a single-line change (the task object's status line gaining
`, "bookend": true`) — no reordering, no reformatting. The test file's 31 new lines are the new
`ShippedTemplateBookendDeclarations` class plus one `ALLOWLIST` entry with a stated reason. PASS.

**6. No fenced path touched.** `git diff --stat -- <path>` returned empty for every one of the 9
named paths (`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`,
`scripts/generate_spine.py`, `specs/`, `skills/implementer/templates/IMPLEMENTER_PLAN.template.json`,
`scripts/run_crew.py`, `scripts/install_constellation.py`, `LAUNCH_ORDER.template.md`,
`map/INDEX.md`). PASS.

**7. Judge the six choices.** The outermost-two freeze per spine is the right cut, but I traced a
downstream-enforcement asymmetry the handoff's rationale doesn't fully cover:

- **Commander:** `archive`'s postconditions (c1–c4) never reference `review`'s `user-decision`
  evidence, so dropping `review` removes human sign-off with **no downstream enforcement**.
  `feedback` is different in kind: `archive`'s c1 mechanically requires an episode to exist for
  this work_id (`verify_episode_captured.py` scans the store) — dropping the `feedback` *gate*
  doesn't bypass that invariant, because it's enforced by state, not by gate completion.
- **Explorer** shows the same asymmetry: `route`'s precondition p1 (`spec confirmed`) and
  postcondition c1 are both `check: null` (self-attested), so dropping `confirm` — the one gate
  with a mechanical `user-decision` artifact check — removes the only machine-enforced human
  sign-off with nothing pulling it back at `route`.
- **Admiral avoids this.** `closeout`'s own c5 bakes `"epic summary accepted by the human"`
  (artifact/`user-decision`) directly onto the **frozen bookend itself**, so it cannot be dropped
  away regardless of what happens to the mutable middle.

I would not block this diff on it — the six declarations are correct exactly as the handoff's
table specifies, and #634 already built the mechanism this gate only declares into. But Admiral's
pattern (bake the human-decision postcondition onto the frozen closing gate) is strictly more
robust than Commander's/Explorer's (leave the decision on a droppable middle gate and hope the
bookend's other checks compensate) — for `feedback` the compensation happens to hold, for
`review`/`confirm` it does not. Filed as a triage candidate (below), not a blocker.

## Fowler pass
Recorded to `.agent-work/567-k/FOWLER_PASS.json`: all 12 baseline smells `absent`. This diff is a
minimal 6-key declaration plus one small, single-purpose test class and one allowlist line — no
duplication, no scattered fan-out beyond the fixed 3-template footprint the task itself requires,
and the two comments present (the `ALLOWLIST` reason, the test class docstring) are non-obvious
WHY notes, not deodorant.
```
$ python /home/tommy/.claude/skills/constellation-reviewer/scripts/verify_fowler_pass.py .agent-work/567-k/FOWLER_PASS.json
fowler pass ok: .agent-work/567-k/FOWLER_PASS.json (smells=12, flagged=[], overridden=[])
exit=0
```
(The survey's `r6-fowler.c1` check text referenced `<reviewer-skill-dir>/scripts/verify_fowler_pass.py`,
but this repo vendors neither `scripts/verify_fowler_pass.py` nor
`skills/reviewer/scripts/verify_fowler_pass.py` — confirmed both absent. Corrected the check text
to the absolute installed path via `amend --delta ... ` with a single `retext-check` op, per global
doctrine on unvendored scripts, authority `constellation/567-k/lane-k/commander-delegated` — logged
in the survey's `amendments`.)

## Test tallies (fresh subprocess, crew env vars unset, per #269)

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_checklist_engine.py
467 passed, 143 subtests passed

env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  python -m pytest -q tests/test_generate_spine.py tests/test_init_work_area.py
202 passed

git status --porcelain
 M skills/admiral/templates/ADMIRAL_SPINE.template.json
 M skills/commander/templates/COMMANDER_SPINE.template.json
 M skills/explorer/templates/EXPLORER_SPINE.template.json
 M tests/test_checklist_engine.py
?? .agent-work/567-k/          (pre-existing, plus this review's own survey/Fowler-pass artifacts under it)
```
Both tallies match the implementer's claimed numbers exactly.

## Findings

- **[info, triage-filed] Human-confirmation gate is downstream-unenforced on Commander/Explorer,
  unlike Admiral.** See criterion 7 above. Filed as triage candidate `tc1` in the survey: consider
  baking Commander `archive`'s and Explorer `route`'s human-decision postcondition directly onto
  the frozen bookend the way Admiral's `closeout` c5 already does, so the mutable middle can't
  quietly drop the human-confirmation requirement. Not a blocker on this diff.
- **[nit] `add`'s postcondition requirement is a general engine rule, not bookend-specific.** The
  handoff's criterion 4 add-delta needed an explicit `postconditions` entry to succeed (a bare add
  is refused engine-wide with `a gated gate needs >=1 postcondition`) — worth a one-line callout in
  a future handoff so the next reviewer doesn't spend a cycle rediscovering it, but it did not slow
  this review down materially.

## Workflow Feedback

- **My own mistake:** my first restore attempt after the criterion-2 red-proof used
  `git checkout -- skills/commander/templates/COMMANDER_SPINE.template.json`, which reverted the
  file to pre-diff `HEAD` (the implementer's whole change is uncommitted, so `checkout --` discards
  it, not just my mutation) — the immediate re-run still showed RED, but for the wrong reason (no
  bookend at all, not a wrong-gate bookend). Caught it by re-checking the actual bookend set before
  trusting the "restored" state, restored correctly from a backup copy taken before the mutation,
  and reran to confirm green. Lesson: when red-proofing an **uncommitted** diff, back up the
  working-tree file first — `git checkout --` is not a safe restore path here.
- **Handoff gaps:** none of substance. The exact six-gate table and the seven numbered criteria
  were concrete and independently checkable without escalation.
- **Context rediscovered:** the repo does not vendor `scripts/verify_fowler_pass.py` anywhere
  (neither at the repo root nor under `skills/reviewer/scripts/`), unlike `checklist_engine.py`
  and most other bundled scripts this repo's dogfooding convention vendors. Had to retext-check the
  survey's own postcondition to the absolute installed path to proceed — see Fowler pass section.
  A future reviewer survey template could default `r6-fowler.c1` to the absolute path when the
  target repo is known not to vendor it, saving this step.
- **Instructions improvised around:** no spine was bound (`SPINE_PARENT` only), so I built and drove
  my own `REVIEW_SURVEY.json` at `.agent-work/567-k/g2-review/review.json` per the skill's
  documented branch for that case, using the repo-vendored `skills/reviewer/templates/` copy
  (dogfooding convention) rather than the globally-installed one.
- **What would have made this easier:** naming the Fowler-pass script's non-vendored status up
  front, as noted above — otherwise nothing.

## Return status
`complete`
