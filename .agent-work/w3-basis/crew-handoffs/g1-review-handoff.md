# Reviewer Handoff

## Gate
g1 (g1-review)

## Survey State Location
`.agent-work/w3-basis/g1-review/review.json`

## What Was Implemented
In `tests/test_checklist_engine.py`, class `CommanderSpineBasisFields` (~line 8543): replaced the
whole-repo-`HEAD` pin (`PINNED_HEAD`/`_skip_if_head_moved`) with a blob-OID pin on
`skills/commander/templates/COMMANDER_SPINE.template.json` (`PINNED_BLOB`/`_fail_if_template_drifted`).
Drift now calls `self.fail(...)`, never `self.skipTest(...)`. Docstring rewritten. Two new
mutation-battery test methods added, each proving one direction via an isolated `/tmp` git clone.
Committed to `epic-569/w3-basis` as commit `8691a40e`.

## How to Inspect the Diff
```
git show 8691a40e -- tests/test_checklist_engine.py
git log --oneline -3
git status --porcelain
```
Review target is commit `8691a40e` on branch `epic-569/w3-basis` at
`/home/tommy/projects/569-w3-basis` — the working tree is clean (no uncommitted changes riding
alongside it).

## Task Statement
Make `CommanderSpineBasisFields` pin to the BLOB OID of the template file it actually depends on
(not repo HEAD) and FAIL — not skip — on drift, with a cheap documented re-verify path, per the
converged smallest-diff plan (`.agent-work/w3-basis/PLAN_ALTERNATIVES.md`) with 4 critic fixes
folded in (`.agent-work/w3-basis/PLAN_CRITIC.md`).

## Close Criteria
- `PINNED_HEAD` (whole-repo `HEAD`) is gone; `PINNED_BLOB` (blob OID of
  `skills/commander/templates/COMMANDER_SPINE.template.json`, via `git rev-parse HEAD:<path>`)
  replaces it.
- No `self.skipTest` remains anywhere in `CommanderSpineBasisFields`'s drift path — drift is
  `self.fail(...)` only.
- The `git rev-parse` return-code guard (`self.assertEqual(out.returncode, 0, out.stderr)`) still
  runs before the blob comparison, so a `rev-parse` failure and a genuine drift failure stay
  distinct (critic finding 6).
- The fail message contains: the word "stale", both blob OIDs (pinned and current), the exact
  literal command `git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json`,
  and an instruction to paste the result into `PINNED_BLOB`.
- All 3 original test methods call `self._fail_if_template_drifted()` (not the old helper name);
  `EXPECTED_BASIS` and `_load_spine` are byte-identical to before this change.
- The class docstring's second paragraph no longer says "skip rather than assert" / describes the
  retired whole-repo-HEAD design — it describes blob-OID pinning + fail-on-drift instead.
- Any inline comment near `PINNED_BLOB` says "g1 dispatch", not "g2".
- Two new tests prove both directions against an **isolated clone** (never the shared worktree):
  template-edit → all 3 protected tests FAIL with the stale-proof message; unrelated commit → all
  3 PASS. Actually **run** these (not just read the source) and confirm they pass.
- `python3 -m pytest tests/test_checklist_engine.py::CommanderSpineBasisFields -q -rs` is GREEN,
  zero skipped, at commit `8691a40e`.
- `PINNED_BLOB`'s value matches the actual current committed blob OID of the template file (i.e.
  it is not stale against `w3-promote`'s edits, if any landed before this commit).

## Allowed Scope
The implementer was permitted to touch `tests/test_checklist_engine.py` only.

## Specific Exclusions
- `skills/commander/templates/COMMANDER_SPINE.template.json` — read-only, owned by `w3-promote`.
  Confirm via `git show 8691a40e --stat` that it is NOT in this commit's changed-files list.
- `scripts/checklist_engine.py` — must not be touched.
- No qualitative-condition population or `basis`-field rollout beyond `plan.c2/c4/c5`.

## Constraints the Implementation Must Respect
- Exactly one file changed: `tests/test_checklist_engine.py`.
- No new self-mutating side effects on the shared worktree from the mutation-battery tests (they
  must use isolated `/tmp` clones, verify by reading the test source).

## Map Anchors (inbound)
- **Structural:** `tests/test_checklist_engine.py::CommanderSpineBasisFields`.
- **Capability:** red-proof pinning for the commander spine template's basis-field shape.
- **Constraints/assumptions:** file-ownership, no-skip-on-drift, blob-oid-granularity, cheap-re-verify,
  prove-both-directions.
- **Decision anchors:**
  - `decision:blob-oid-not-head` — pin the blob OID, not repo HEAD.
    `@grade: settled/human · leans g1-implement`
  - `decision:drift-fails` — FAIL, never skip, on divergence.
    `@grade: settled/human · leans g1-implement`
  - `decision:ship-the-re-verify-path` — re-verify path must be cheap and documented.
    `@grade: settled/human · leans g1-implement`
  - `decision:prove-both-directions` — both directions demonstrated.
    `@grade: settled/admiral · leans g1-implement`
- **Evidence expectations:** `claim:pin-tracks-file-not-repo`, `claim:drift-fails-not-skips`,
  `claim:re-verify-is-cheap` — all three should be independently re-confirmed by actually running
  the tests, not just reading them.
- **Map confidence flags:** repo map is DEGRADED-UNPARSEABLE this run (not this gate's concern).

## Evidence Produced
Full `IMPLEMENTER_RESULT` at `.agent-work/w3-basis/crew-handoffs/g1-implement-implementer-result.md`.
Target postcondition this review's verdict feeds: `g1-integrate.c2` (`review-result`, match
`verdict: APPROVE`).

## Suggested Model Tier
simple bounded — one commit, one file, mechanical criteria list above is exhaustive and checkable.

## Stop Conditions
Return BLOCK if: the diff cannot be accessed at commit `8691a40e`; a close criterion above fails;
the mutation-battery tests don't actually pass when run; any file besides
`tests/test_checklist_engine.py` changed.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. Write the full `REVIEW_RESULT` to
`.agent-work/w3-basis/crew-handoffs/g1-review-reviewer-result.md` before ending your turn.
