# Reviewer Handoff

## Gate
`g3-review` — `archive.c2b` reachability check (issues #439 + #484), work-id `w5-gates`, epic #418
wave 5.

Worktree: `C:/Programs/constellation-skills-wt/epic418-w5-gates`, branch `epic-418/w5-bookend-gates`.
Use absolute paths — your cwd resets between bash calls.

## Operational facts — these have each cost this run real time

1. **Use `python`, never `py`.** Different interpreters here; `py` has no pytest, so `py -m pytest`
   exits nonzero and reads exactly like a red suite when the tests never ran.
2. **Never pipe a pytest command into `tail` or `head`.** `$?` then belongs to the pipe, and a
   zero-match `-k` selector — which exits **5** — reads as exit 0. Redirect to a file and echo `$?`
   if you want both; a redirect is not a pipe.
3. **Find code by text, not line number.** g1, g2 and now g3 grew the test file by ~1000 lines. Every
   line number in the frozen plan is stale.
4. Two files under `.agent-work/epic-418-redux/transitions/close-to-w5/` show `M` in `git status`
   with **empty diffs** — a CRLF stat artifact, blob OIDs identical to HEAD. **Leave them unstaged.**

## What to review

The change is **committed**. Your target is a real ref, not the working tree:

```bash
git diff 4b8abc12 ff43e883 -- skills/commander/templates/COMMANDER_SPINE.template.json tests/test_iterative_planning_doctrine.py
```

`4b8abc12` is g2's last commit (the pre-g3 baseline); `ff43e883` is the change under review.

The implementer's contract — the document the diff is judged against — is at
`.agent-work/w5-gates/crew-handoffs/g3-implement-HANDOFF.md`. Its result is at
`.agent-work/w5-gates/crew-handoffs/g3-implement-RESULT.md`. **Read the result, then verify it rather
than trust it.** Everything under `.agent-work/` is local-only and correctly absent from the tracked
diff.

## The change in one paragraph

`archive.c2b` in `skills/commander/templates/COMMANDER_SPINE.template.json` was
`gh pr list --head <branch> --state open --json number --jq 'length > 0'`. It is now
`test "$(gh pr list --head "$(git -C <repo-root> rev-parse --abbrev-ref HEAD)" --state all --json state --jq '[.[] | select(.state == "OPEN" or .state == "MERGED")] | length')" -gt 0`.
The branch is derived at **check time** from the existing `<repo-root>` token. `{OPEN, MERGED}` are
accepted; **CLOSED-unmerged and no-PR are rejected**. The count is compared **in the shell** so the
**exit code** carries the verdict.

## The four required confirmations — this gate's core

The plan's own words: *the reviewer must independently confirm the new check is not a check that
cannot fail.* Build these mutations **yourself**; do not accept the implementer's word that they go
red.

1. **Reintroducing the literal `<branch>` token must go RED.**
2. **Narrowing back to `--state open` must go RED.** Note this only discriminates on a **MERGED**
   fixture — on an OPEN fixture it is a no-op that proves nothing. Say which fixture you used.
3. **A branch with NO pull request at all must go RED.**
4. **The test must read the command text OUT of the template, not restate it**, and
   `scripts/init_work_area.py` must have taken a **zero-line diff**. A retyped copy stops testing the
   shipped artifact — that is cold critic finding F2, which measured that a byte-identical template
   would have closed the old whole-file check green.

## Three claims to check hardest

**(a) The exit-code claim.** `docs/CHECKLIST_SCHEMA.md` says a `command` condition's verdict is its
exit code and stdout is **discarded**. #484's suggested replacement keeps `--jq 'length > 0'`, which
prints `true`/`false` but exits **0 either way** — adopting it verbatim would convert a check that
cannot pass into **one that cannot fail**, inside a wave about checks that cannot fail. Confirm the
new text's verdict genuinely rides the exit code, and that stdout is not doing any work.

**(b) The three-defects finding.** The implementer reports that the OLD text exited **1 in all four
states**, because the unquoted `<` is a shell **input redirection** and `gh` was never invoked — so
"the criterion accepts only an OPEN PR" was never a true description of shipped behaviour. This is a
correction to the issue bodies and it is going in the PR. **Verify it independently** — it is the
single most consequential claim in the diff.

**(c) The scoped null.** The `--jq` expression's behaviour under real `gojq` is **not** proven: no
`jq` on PATH and `gh` cannot evaluate filters offline. The mitigation claimed is that the stub
*derives* its filtering from the `--jq` text (making legs 4/5 load-bearing) and **refuses loudly** on
any unmodelled shape rather than passing. **Check that the refusal is real** — if the stub can
silently pass on a shape it does not model, the null is wider than reported. The Commander ran the
resolved text against four real branches on the live `gh` and got no-PR 1 / MERGED 0 /
CLOSED-unmerged 1 / MERGED 0, which closes the gap from the live side; you are checking the offline
side.

## A warning from this run's own history — the highest-value thing you can do

At gate **g2** the first review **BLOCKed** because the implementer's mutation test had a **no-op
leg**: a mutation that looked like it proved something but could not fail, because the mutated field
was legitimately empty for that packet shape. The reviewer found it by **building all three
shortcuts itself** and noticing one stayed green. That block was the gate working.

This implementer says it did that analysis pre-emptively and names four traps it claims to have
avoided (leg 3 is a no-op on an OPEN fixture; leg 6 is a no-op whenever a reachable PR exists; leg 1
fails at the shell redirect *before* `gh*` so it does not prove the branch **value** matters, which
is why leg 2 exists). **Check whether any surviving mutation in this diff still has that problem** —
including any leg the implementer did not flag.

## Test naming contract — LOAD-BEARING, do not suggest loosening it

This gate's close criteria are `-k` selectors on these substrings, and a zero-match selector exits
**5** and fails the gate **closed**. That is deliberate: it is the remedy for the cold critic's BLOCK
findings F1/F2. State-matrix tests must carry **`archive_c2b`**; mutation tests must carry
**`archive_mutation`**. If you think a name is wrong, that is a **finding**, not a rename.

## Evidence to reproduce

Run each bare (or redirected, never piped), and report the exit code you actually saw **and how many
tests each selector collected** — zero collected is a gate failure, not a pass.

- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k archive_c2b` — implementer saw
  exit 0, 4 tests / 4 subtests
- `python -m pytest tests/test_iterative_planning_doctrine.py -q -k archive_mutation` — implementer
  saw exit 0, 2 tests / 9 subtests
- Coupled suite — implementer saw exit 0, 396 passed / 500 subtests:

```bash
python -m pytest tests/test_iterative_planning_doctrine.py tests/test_install_constellation.py tests/test_init_work_area.py tests/test_context_manifest.py tests/test_spine_provenance_check.py tests/test_map_contract_wiring.py tests/test_worktree_precondition_wiring.py tests/test_spine_rail.py -q
```

**One delta is already accounted for and you should confirm the account rather than re-find it:** the
pre-g3 baseline was 390 passed / 488 subtests. The implementer reports +6 tests / +13 subtests of its
own and **−1** from
`test_context_manifest::RevIsGitBlobOid::test_rev_equals_git_rev_parse_head_for_tracked_clean_files`,
which subtests only files clean against HEAD — the spine template is one of its targets, so editing
it drops that subtest **until commit**. The change is now committed, so at `ff43e883` that subtest
should be **back**. If your coupled count does not reconcile, that is a finding.

## Map anchors (inbound)

No architecture map — orientation is `DEGRADED-NO-MAP`, anchors named by path, no `struct:`/`decision:` ids.

- **Structural:** `skills/commander/templates/COMMANDER_SPINE.template.json` — the `archive` task's
  `c2b` postcondition. Find it by the text `the work is REACHABLE`.
- **Capability:** Commander closeout reachability — a strengthened durable system.
- **Constraints:** `docs/CHECKLIST_SCHEMA.md` — a `command` condition's verdict is its **exit code**;
  stdout is **discarded**.
- **Decision anchor:** the branch is derived at check time from `<repo-root>`, not resolved at
  instantiation, because the branch may not exist when the spine is instantiated.
  `@grade: settled/human · leans g3-implement,g3-review · (pre-ruling 5 — two defects, not one; a contradiction is a float, not a revision)`
- **Map confidence flags:** the instantiate-time vs check-time ordering is this gate's **unmapped
  seam**. Measure `init_work_area.py`'s actual ordering rather than assuming it.

## Scope of the review

Tracked files that may change: `skills/commander/templates/COMMANDER_SPINE.template.json` and
`tests/test_iterative_planning_doctrine.py`. `scripts/init_work_area.py` was in scope but expected to
be a **zero-line diff**. **Flag any tracked file outside that set** —
`git diff --numstat 4b8abc12 ff43e883` should show only the two.

Out of bounds for this gate: `scripts/checklist_engine.py` and `tests/test_checklist_engine.py`
(crew 4 is their sole writer), `scripts/install_constellation.py` (crew 2),
`scripts/verify_iterative_role_artifacts.py` (gates g1/g2, already closed and approved). **Any red
outside the ownership scope is a FLOAT to the Commander, not an edit.**

## Return format

Write your REVIEW_RESULT to `.agent-work/w5-gates/crew-handoffs/g3-review-RESULT.md`. State
**APPROVE** or **BLOCK** on the first line, then per-criterion findings with the evidence you
produced yourself (mutations you built, exit codes you saw, collection counts), the no-op analysis,
anything you floated, and workflow feedback.

Return **BLOCK** if: the diff cannot be accessed; evidence is absent or unverifiable; any of the
three required mutations does **not** go red; the test restates the command text instead of reading
it from the template; a surviving mutation is a no-op; or the scoped null is wider than reported.
A BLOCK with proof is this gate working, not a failure of it — g2's block is exactly why the g2
change is trustworthy now.

## Suggested model tier

Stronger. You have to build the mutations yourself and reason about which fixture makes each one
discriminating.
