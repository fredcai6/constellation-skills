# Reviewer Handoff

## Gate
`g1-review` — work-id `r418-460`, issue #460, worktree `C:/Programs/constellation-skills-wt/r418-460`.

## Survey State Location
Create your review survey checklist at
`C:/Programs/constellation-skills-wt/r418-460/.agent-work/r418-460/g1-review/review.json` — never at
the worktree root.

## What Was Implemented
A fourth op kind, `restate-assertion`, in `scripts/apply_episode_delta.py` — the episode store's
only write path. It replaces exactly one assertion's `statement` and appends one `- history:` line
carrying the **original statement verbatim**, built inside the writer from the parsed original so a
caller cannot misquote it. Registered in `OP_KINDS` and at both the apply and dry-run dispatch
sites, each of which gained an `else: raise`. 21 new tests in `tests/test_episode_store.py`.

Why the op exists: issue #460 asks for prescriptive `workaround` statements in `episodes/active/`
to be rewritten as observations and assumes `amend-assertion` can do it. It cannot — it changes
only `lifecycle-standing`. Gate g2 (next) applies the rewrite through this new op.

## How to Inspect the Diff
The review target is the **UNCOMMITTED working tree** of this worktree, not `git diff main...HEAD`.

```bash
cd C:/Programs/constellation-skills-wt/r418-460
git status --porcelain
git diff -- scripts/apply_episode_delta.py tests/test_episode_store.py
```

Everything under `.agent-work/` in that status output is run bookkeeping, not this gate's
deliverable. The two files above are the whole deliverable.

## Task Statement
Add `restate-assertion` to `scripts/apply_episode_delta.py`: fields `id`, `assertion` (`a<n>` or
`d<n>`), `statement` (new text), `history` (why it was restated). Replace exactly that one
assertion's `statement`; append exactly one history line carrying the original statement verbatim,
built inside the writer from the parsed original. Touch nothing else — not `kind`, `strength`,
`lifecycle-standing`, any sibling assertion, any `## Mechanical` line, or the `## Retirement` block.
Single-line enforcement on the new statement as at create time. Refuse: unknown episode id, unknown
assertion id, missing/blank `statement`, missing/blank `history`, any misfiled extra field. Register
at both dispatch sites with an `else: raise` at each.

## Close Criteria
Each is a review check. Run them; do not take the implementer's word.

1. `restate-assertion` is in `OP_KINDS` and is dispatched in **both** `apply_delta` and
   `_dry_run_log`, and **both** now end in an `else` that raises.
2. The history line is built **inside the writer from the parsed original statement**. Confirm by
   reading the code that no caller-supplied field can reach the quoted-original portion of that
   line. This is the load-bearing property of the whole gate — if a caller can supply the "original"
   text, the op destroys evidence instead of preserving it.
3. The applier leaves `kind`, `strength`, `lifecycle-standing`, every sibling assertion, every
   `## Mechanical` line and the `## Retirement` block untouched.
4. Tests exist and pass for each of: (a) only the named assertion's statement changes, siblings and
   mechanical lines byte-identical; (b) the appended history line contains the original statement
   verbatim; (c) multi-line statement REFUSED; (d) unknown assertion id REFUSED; (e) all-or-nothing
   — a two-op delta whose second op is invalid leaves the first op's file unchanged on disk;
   (f) restate under `--dry-run` LOGS the op and writes nothing; (g) misfiled extra field REFUSED.
5. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` is green. Run it yourself and record the
   real exit code. Expected: 1742 passed, 4 skipped, 672 subtests, exit 0.
6. Nothing under `episodes/`, `docs/`, or the three fenced scripts was modified.

## Allowed Scope
`scripts/apply_episode_delta.py` and `tests/test_episode_store.py` only.

## Specific Exclusions
Flag as a blocker if any of these was touched:
- `episodes/` — anything at all. This gate ships the write path, not the rewrite.
- `docs/EPISODE_STORE.md` — documenting the op is gate g4.
- `docs/agents/*` — promotion into doctrine is the human's call, never a crew's.
- `scripts/checklist_engine.py` (owned by issue #433), `scripts/collect_feedback.py` (#464),
  `scripts/verify_worktree_precondition_coverage.py` (#436) — concurrent siblings own these.
- Any new file that accumulates distilled advice for future agents, whatever it is named.

Scratch files the implementer left under `.agent-work/r418-460/` (mutation probes, its own work
area) are not deliverables and are the Commander's to clean up. Note them; do not block on them.

## Constraints the Implementation Must Respect
- `episodes/` is never hand-edited; `apply_episode_delta.py` is the only write path.
- Any invocation against the real store passes `--store-root episodes`; the default resolves against
  the installed skill directory and would build a store outside the repo while gates reported green.
- Test command is exactly `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`. Never `py` for
  pytest. Capture the real exit code.
- The record grows rather than getting rewritten (`docs/EPISODE_STORE.md` §5). This op answers that
  constraint only if the original wording survives verbatim in history. Check that it does.

## Map Anchors (inbound)
- **Structural:** `docs/EPISODE_STORE.md` (record grammar, write-path doctrine — hash-pinned
  substitute; this repo ships no packet map); `episodes/README.md` (store layout);
  `scripts/apply_episode_delta.py` (the only write path).
- **Capability:** the episode write path.
- **Constraints/assumptions:** an episode records what happened and is never read back as a rule
  (`docs/agents/ORCHESTRATOR_CONTEXT.md`, "The Retired Learning Playbook"); `docs/EPISODE_STORE.md`
  §5 — the record grows rather than getting rewritten.
- **Decision anchors:** add a `restate-assertion` op rather than annotating with `amend-assertion`.
  `@grade: settled/inherited · leans g1-implement` — Commander decision under LO-460's Inherited
  Latitude, ratified by the Admiral. Not the reviewer's to unsettle; if you find it contradicted by
  the code, return it as a decision candidate rather than a BLOCK on the choice itself.
- **Evidence expectations:** `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`, real exit code.
- **Map confidence flags:** no packet map exists (`map_orient` DEGRADED-NO-MAP, discharged with four
  hash-pinned substitutes). Verify line numbers against the file rather than trusting quoted ones —
  the implementer reported the handoff's line numbers were 20-90 lines stale.

## Evidence Produced
From `IMPLEMENTER_RESULT` at
`.agent-work/r418-460/crew-handoffs/g1-implement-result.md` — read it, then reproduce:
- Baseline before edit: 1721 passed, 4 skipped, 643 subtests, EXIT=0.
- After: 1742 passed, 4 skipped, 672 subtests, EXIT=0.
- Nine mutations of the shipped writer each drive the new tests red, including registering the op at
  `apply_delta` only (caught by 4 tests) and each `else` removed independently. Probes at
  `.agent-work/r418-460/evidence/mutate_probe.py` and `mutate_probe_dispatch.py`. Re-run at least
  the single-site-registration mutation yourself — a test that cannot fail is the defect class this
  whole issue exists to close.
- Wiring grep external call sites: `_apply_restate_assertion` 2, `_validate_restate_assertion` 1,
  `_restatement_history_line` 1, `_unhandled_op_kind_message` 2.

## Suggested Model Tier
Stronger (Opus). Small diff, but the correctness conditions are precise and this is the store's only
write path.

## Stop Conditions
Return BLOCK if: the diff cannot be accessed, evidence is absent or unverifiable, or a policy
decision is required before a verdict is possible.

## Return Format
Write **REVIEW_RESULT** to
`C:/Programs/constellation-skills-wt/r418-460/.agent-work/r418-460/crew-handoffs/g1-review-result.md`:
verdict (APPROVE or BLOCK), per-check findings against the six close criteria, blockers,
out-of-scope observations, workflow feedback. The file is what the Commander verifies; a verdict
returned only as chat text does not count.
