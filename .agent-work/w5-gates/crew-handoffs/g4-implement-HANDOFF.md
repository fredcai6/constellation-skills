# Implementer Handoff

## Gate
`g4-implement` — composition floor + collateral repair, work-id `w5-gates`, epic #418 wave 5.
This is the **last gate of the last crew in the epic.**

Worktree: `C:/Programs/constellation-skills-wt/epic418-w5-gates`, branch `epic-418/w5-bookend-gates`.
Use absolute paths — your cwd resets between bash calls.

## Operational facts — each of these has cost this run real time

1. **Use `python`, never `py`.** Different interpreters here; `py` has no pytest, so `py -m pytest`
   exits nonzero and reads exactly like a red suite when the tests never ran. (`references/windows.md`
   §4 says the opposite. It is wrong on this box and has already cost two crews.)
2. **Never pipe a pytest command into `tail` or `head`.** `$?` then belongs to the pipe, and a
   zero-match `-k` selector — which exits **5** — reads as exit 0. Redirect to a file and echo `$?`;
   a redirect is not a pipe.
3. **Find code by text, not line number.** `tests/test_iterative_planning_doctrine.py` has grown
   **1032 lines** across g1–g3. Every line number in the frozen plan is stale.
4. **Beware `$(...)` in arguments you pass to the engine.** A previous crew had a finding mangled by
   command substitution. Use a heredoc for anything containing shell metacharacters.
5. Two files under `.agent-work/epic-418-redux/transitions/close-to-w5/` show `M` in `git status`
   with **empty diffs** — a CRLF stat artifact. **Leave them unstaged.**
6. **This host is CRLF.** A previous crew's mutation probe silently failed to apply because its
   literal was LF. **Always assert the mutation actually applied** before believing a red or a green.

## What already landed — you are proving these COMPOSE, not re-doing them

Three fixes are in, each independently reviewed and approved. Production diff across the wave:

```
143  22   scripts/verify_iterative_role_artifacts.py
  1   1   skills/commander/templates/COMMANDER_SPINE.template.json
1032   2   tests/test_iterative_planning_doctrine.py
```

- **Fix B (g1, #501 + #468)** — the installed-bundle guard decides by **structure, not by name**. A
  `constellation-decoy/` directory with no `SKILL.md` inside a marked root is **rejected**; the
  Commander worktree reaches not-installed without consulting the name. `--skills-root` was added and
  is **load-bearing**. Commits `c63c2bb0`, `6f48ece4`.
- **Fix A (g2, #506)** — `admiral-prelaunch` is decision-aware: a recorded, G2-verified, **rendered**
  stop transition packet closes the prelaunch check; advance and replan unchanged; **repair still
  refused**. Commits `57048457`, `bd56ac8a`, `4b8abc12`.
- **Fix C (g3, #439 + #484 + #446)** — `archive.c2b` derives its branch at check time from
  `<repo-root>`, accepts `{OPEN, MERGED}`, rejects CLOSED-unmerged and no-PR, and compares the count
  **in the shell** so the exit code carries the verdict. Commits `ff43e883`, `84d1e998`.

## Task Statement

**Three green gates do not prove the three fixes compose.** Each was measured through its own unit
fixtures. Add the regression floor that proves it **through the real artifacts**, then repair any
collateral red the three fixes left in the broader suite.

**This gate adds tests and fixes fallout. It introduces NO new behavior of its own.** If you find
yourself changing what a fix does, stop and float.

### The three composition tests

1. **The shipped `COMMANDER_SPINE` template still instantiates, and its archive check still
   resolves, after fix C.** Not "the string looks right" — instantiate the real template through the
   real resolver and confirm the resolved `archive.c2b` text carries no unresolved token.
2. **The verifier still refuses from a non-installed location after fix B, while accepting an
   installed bundle and honouring `--skills-root`.** All three legs, through the real script.
3. **The stop path still closes after fix A** — through the real verifier, not a unit fixture.

Then: **repair any collateral red in the broader suite, WITHIN THE OWNERSHIP SCOPE ONLY.**

## The one thing that makes this gate different: it must not be tautological

The reviewer's explicit instruction is that **each composition test must be shown to go red on a
stated broken input.** A composition test that passes because it asserts nothing is the exact defect
this whole wave is about — and this run has hit it **twice already**:

- At **g2** the reviewer BLOCKed: a mutation test had a **no-op leg**, a mutation that looked like it
  proved something but could not fail, because the mutated field was legitimately empty for that
  packet shape.
- At **g3** the reviewer BLOCKed: the `gh` stub **answered** unmodelled flags instead of refusing, so
  a check carrying `--repo someone/else` would have kept the whole four-state matrix green.

**For every test you write here, state the broken input that makes it red, and actually run it
broken.** Do not report a test as load-bearing you have not watched fail. And for each one, say what
would have to be true for it to be a **no-op** — that analysis is the single most valuable thing you
can put in your result.

## Allowed Scope

- `tests/test_iterative_planning_doctrine.py`
- `scripts/verify_iterative_role_artifacts.py`
- `skills/commander/templates/COMMANDER_SPINE.template.json`
- `scripts/init_work_area.py` — in scope, **expected to stay a zero-line diff**.

## Specific Exclusions — an unowned red is a FLOAT, never an edit

- `scripts/checklist_engine.py`, `tests/test_checklist_engine.py` — **crew 4 is their sole writer.**
- `scripts/install_constellation.py` — crew 2.
- The handoff templates — crew 3. `docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md` — crew 5.
- Hooks, any `settings.json`, `docs/agents/*` doctrine.
- `skills/admiral/templates/ADMIRAL_SPINE.template.json` — **not this run's file**, even though its
  execute prose still describes `repair` as an enforced exit after fix A. That is already a recorded
  triage candidate; do not fix it here.

**If collateral red lands in ANY file outside the ownership scope: STOP and FLOAT to the Commander
with the failing test named. Do not edit it, and do not reach for a waiver.** An unowned red is a
cross-crew finding, and the launch order's Honest-Null Clause covers reporting it as a partial. Four
other crews' work is already merged or queued behind this branch, so an unowned red is information
the Admiral needs, not a problem for you to solve.

## Evidence Expected

Run each bare (or redirected, never piped). Report the exit code you actually saw **and how many
tests each selector collected** — zero collected is a gate failure, not a pass.

- Your new composition tests, by whatever selector you give them.
- Coupled suite — currently **396 passed / 503 subtests, exit 0**:

```bash
python -m pytest tests/test_iterative_planning_doctrine.py tests/test_install_constellation.py tests/test_init_work_area.py tests/test_context_manifest.py tests/test_spine_provenance_check.py tests/test_map_contract_wiring.py tests/test_worktree_precondition_wiring.py tests/test_spine_rail.py -q
```

- **The full suite.** This is the gate's whole point and it is the first time it runs in this wave:

```bash
python -m pytest -q
```

**Budget for it: ~16 minutes (measured 947s, 1867 passed / 2 skipped at the base commit
`aa2038d9`).** Report your delta against 1867 and **account for every test of it.** An unexplained
delta is a finding, not a rounding error.

- **The run's own closure check**, which is this gate's sharpest piece of evidence:

```bash
python scripts/verify_iterative_role_artifacts.py commander --work-id w5-gates --skills-root C:/Users/fredc/.claude/skills
```

Before fix B this command **could not pass from this worktree** — that was this run's own finding 2,
in neither issue. After fix B it should run for real. This is where the epic's own check stops being
a formality and becomes evidence. **The `--skills-root` flag is load-bearing:** without it the check
validates against whatever is installed on this machine rather than the branch under review, and
would go green or red on machine state no PR reviewer can see. Report what it does.

## Map Anchors (inbound)

No architecture map — orientation is `DEGRADED-NO-MAP`, anchors named by path, no `struct:`/`decision:` ids.

- **Structural:** all three owned files together, plus the doctrine test file — the composition
  surface. **No map id exists for it, which is part of why it needs measuring.**
- **Capability:** all three affected capabilities at once — role-artifact verification, boundary
  transition verification, and spine instantiation/archive closure.
- **Constraints:** `docs/agents/ORCHESTRATOR_CONTEXT.md` — a mechanism or workflow behavior change
  owes targeted automated tests **plus** the relevant broader suite, and both commands must be named.
  This gate is where the broader suite is named. Also: a deliberately red suite across gates is a
  plan smell; the coupled-suite condition on g1–g3 was this plan's answer, and this gate is the
  full-suite backstop rather than the only place red is caught.
- **Decision anchor:** whether the run's own execute closure check counts as evidence. **It does**,
  and this gate is where it stops being a formality.
- **Map confidence flags:** this gate is itself the response to the unmapped seam — with no map
  asserting how templates, top-level scripts and installed bundles relate, composition is established
  by **running the real artifacts end to end** rather than by trusting the structure.

## Known state you should not rediscover

- Both `-k` selector families from earlier gates (`guard_*`, `stop_*`, `archive_*`) are load-bearing
  close criteria. **Do not rename or broaden them**, and do not let a new test's name collide into
  one of those selectors — that would let a sibling's test satisfy a gate's floor, which the selectors
  were split apart to prevent.
- One known benign full-suite interaction:
  `test_context_manifest::RevIsGitBlobOid::test_rev_equals_git_rev_parse_head_for_tracked_clean_files`
  subtests only files clean against HEAD, and the spine template is one of its targets — so it drops
  a subtest whenever that file is edited and uncommitted, and returns on commit. If your counts move
  by one there, that is why. Confirm rather than assume.

## HONEST NULL — read before you start

If a composition test **cannot** be written honestly through the real artifacts — for instance it
would need real network, real `gh` auth, or a real installed bundle you cannot produce — **say so
plainly** and report what you could and could not prove. **Do NOT substitute a weaker test that
re-reads a string and calls it composition.** Scope the null precisely: "this specific mechanism is
refuted because X", never "this approach is impossible."

## Stop Conditions

Return BLOCKED if: collateral red lands outside the ownership scope; a composition test cannot be
written honestly (the null); `init_work_area.py` appears to need edits; the full-suite delta cannot
be accounted for; or a policy decision is required.

## Return Format

Write your IMPLEMENTER_RESULT to `.agent-work/w5-gates/crew-handoffs/g4-implement-RESULT.md`. State
`COMPLETE` or `BLOCKED`, then: per-composition-test the **broken input you ran and the red you saw**,
the no-op analysis, full-suite count with the delta accounted test by test, what the closure check
did, files touched with `git diff --numstat`, anything you floated, and workflow feedback.

## Do not commit

Leave the work in the working tree. The Commander commits.

## Suggested Model Tier

Stronger. Composition tests through real artifacts have to be invented, and the red-on-broken-input
discipline needs judgment about what "broken" means for each one.
