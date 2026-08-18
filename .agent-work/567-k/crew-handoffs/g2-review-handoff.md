# Reviewer handoff — g2: bookend declarations in the role spine templates

**Result path (write here before ending your turn — that write is the delivery):**
`.agent-work/567-k/crew-handoffs/g2-review-result.md`
**Suggested Model Tier:** sonnet. A ~37-line diff against an explicit criteria list.

Repo: `/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle`

You are the **independent reviewer**. Verify, do not agree. **Reproduce; do not read and trust.**

## Task under review

Gate g1 taught `amend()` to honour a per-gate `"bookend": true`. This gate declares the bookends
in the three role spine templates this lane owns, and pins them with a test.

## Inspect

```sh
git diff skills/ tests/test_checklist_engine.py
```

Implementer's account: `.agent-work/567-k/crew-handoffs/g2-implement-result.md`. Read it **last**;
treat every claim as a pointer to something you reproduce.

## Close criteria — address each by name

1. **Exact declarations, nothing else.** `COMMANDER_SPINE` = `init` + `archive`;
   `ADMIRAL_SPINE` = `init` + `closeout`; `EXPLORER_SPINE` = `init` + `route`. **And no other
   gate in any of the three carries the flag.** Verify by loading the JSON and computing the set,
   not by eyeballing the diff.
2. **The pinning test can fail.** Move the flag to a wrong gate in one template, confirm the test
   goes RED, then restore. A test that passes in both worlds proves nothing. Confirm the tree is
   clean afterwards.
3. **Templates still valid and instantiable.** Each still parses and still instantiates. Say which
   command you used.
4. **The declaration works end to end.** On a **COPY**, in a fresh process: take the Commander
   template, mark `init`..`plan` complete and `execute` in-progress, and confirm
   `{"ops":[{"op":"drop","id":"archive"}]}` is **REFUSED**. Then confirm an `add` into the middle
   (`after: execute`) still **SUCCEEDS**. Paste both.
5. **Diff hygiene.** No reformatting, reordering, or unrelated edits in these constantly-read
   templates. The diff should be six added keys plus the test.
6. **No fenced path touched.** Not `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`
   (gate g1, already integrated and committed), not `scripts/generate_spine.py`, `specs/`,
   `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` (out of scope, floated), not
   `scripts/run_crew.py`, `scripts/install_constellation.py`, `LAUNCH_ORDER.template.md`,
   `map/INDEX.md`.
7. **Judge the six choices, do not just verify them.** Is freezing only the outermost two per
   spine right? The human asked for "frozen required gates at the start and finish… what we do in
   the middle is squishy." Commander's `review` and `feedback` were also observed deletable
   (`.agent-work/567-k/evidence/probe-closing-bookend.md`) and were deliberately **left mutable**
   because they sit inside the middle and `archive` at the end stops the run terminating early.
   **If you think that is wrong, say so as a finding.** This is the one criterion where I want your
   judgement, not just your verification.

## Required commands

```sh
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR python -m pytest -q tests/test_checklist_engine.py
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR python -m pytest -q tests/test_generate_spine.py tests/test_init_work_area.py
git status --porcelain
```

## Constraints

- **Never run a mutating engine verb against a live spine.** `.agent-work/567-k/spine.json`,
  `.agent-work/567-k/execute.json`, `.agent-work/epic-567-door/spine.json` are LIVE, read-only.
  Copy to a temp dir and drive the copy.
- Fresh process, explicit paths (#269). Leave the tree as you found it; if you break something to
  prove a red, restore it and say so.
- Out-of-scope improvements are **findings**, not edits.

## Return format

`REVIEW_RESULT` with a **`Verdict`** field of exactly `APPROVE` or `BLOCK`. Include each criterion
with what you ran and observed, the red-proof output from criterion 2, both pastes from criterion
4, the test tallies, findings with severity, and **Workflow Feedback** including your own mistakes.
`BLOCK` if any criterion fails.
