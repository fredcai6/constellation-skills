# Reviewer Handoff

## Gate
`g1-review` (issue #305, epic #298 — the context-manifest assembly seam)

## Survey State Location
Create your review survey checklist at `.agent-work/issue-305/g1-review/review.json`. Never at the worktree root.

Drive it with the **worktree's** `scripts/checklist_engine.py`, not the installed copy — this change modifies the engine, so mixing binaries is the hazard. On a **survey**, `record` is the re-record verb; `advance`/`reopen` refuse as gated-only.

## What Was Implemented
The #300 context-manifest producer had **zero callers in production** — its acceptance criterion "a manifest is produced on every deterministic assembly" was true definitionally, over zero assemblies. This gate wires it, so that producing the manifest is a **byproduct of assembly** rather than a step an agent can forget.

The seam is `checklist_engine.start()` and `reopen()` — the only two sites that set a task to `in-progress`, which `advance()` requires. That is what makes emission unskippable **without** touching the shared `dispatch()` chokepoint. All logic lives in a new `scripts/episode_capture.py`; the engine gains an import shim and one call per site.

## How to Inspect the Diff
Everything is **committed** on branch `epic-298/305` in worktree `C:/Programs/constellation-skills-wt/e298-305`. Base is `967493c`.

```
cd C:/Programs/constellation-skills-wt/e298-305
git diff 967493c..HEAD -- scripts/ tests/
```

Do **not** use `git diff main...HEAD` — it shows unrelated merged-PR divergence. Also run `git status --porcelain` to confirm nothing is stranded untracked.

Read `.agent-work/issue-305/crew/g1-implement-result.md` for the implementer's own evidence, and `.agent-work/issue-305/PLAN_CRITIC_DISPOSITION.md` for the adjudicated rulings (D1, D2, D4, D8 govern this gate). **`PLAN_CRITIC_DISPOSITION.md` beats `design-it-twice/CONVERGENCE.md` wherever they disagree** — the disposition is later and evidence-backed, and it reverses the convergence's seam choice.

## Task Statement
Emit the context manifest from `start()` and `reopen()`, write-if-absent, with all logic in a separate module, fail-soft but never fail-silent, and roots resolved mechanically with `durable` coming from `agent_work_root.durable_root()` (the **checkout** root).

## Close Criteria
Hunt these four **specifically**. They are not generic, and the gate plan names them:

1. **Can an agent still reach `advance` on a gate without ever triggering the emit? Try to construct the sequence.** This is the load-bearing claim of the whole design — that `start`/`reopen` are the only routes into `in-progress`. Attack it. `resume()` is worth your attention: the implementer flagged it as also reaching `in-progress` by restoring a prior status.
2. **Does the emit ever change a verb's exit code?** Test a terminal checklist, an unmapped root token, and a non-git directory. The implementer claims 10/10 identical exit codes against the pre-seam engine extracted from `967493c`. Reproduce that comparison rather than trusting it.
3. **Is the `durable` root the checkout root, resolving `.agent-work/LESSONS.md` WITHOUT double-nesting?** **Check the resolved absolute path, not the code.** The trap: `durable_agent_work()` would yield `.agent-work/.agent-work/LESSONS.md`, which does not exist, which the producer records as `rev: null` — structurally valid and silently wrong, with every gate green.
4. **Does a manifest with every row `rev: null` pass as success? It must not read as a healthy manifest.**

## Constraints the Implementation Must Respect
- **Write-if-absent, never overwrite.** The manifest is a per-step delivery snapshot. Verify a second `start`/`reopen` does not rewrite it — compare content hash **and** mtime.
- **Fail-soft but not fail-silent.** A failed emit writes a *stub* carrying `emit_error` and `files: null`. Verify `files: null` is genuinely distinguishable from the legitimate empty `files: []` ("this step declared nothing"). Note both are falsy — any consumer discriminating on truthiness conflates them.
- **No logic in the engine.** The engine diff should be an import shim plus two call sites, plus `base_dir` threading onto `reopen()`.
- Emission must happen **after** the status mutation, so `active_id()` selects the right step.

## Two things I am telling you because a check did not catch them

**A. The "nothing else" postcondition was vacuous, and I want your independent read on what actually landed.** The implementer's own job file checked "the engine diff is an import plus two call sites, nothing else" with the command `git diff --stat -- scripts/checklist_engine.py` — **which exits 0 no matter what the diff contains.** It could not fail. I verified the diff by reading it and judged it acceptable, but that is one pair of eyes on a criterion no machine checked. Form your own verdict on whether the engine diff is genuinely logic-free.

**B. The implementer self-reported exceeding a close criterion, and I accepted it.** `reopen()` had no route to the checklist's on-disk location — unlike `start()`, it never took `base_dir`. So the diff includes two plumbing lines: `reopen()` gained a `base_dir` parameter and `_run_verb` passes it. I accepted this under delegated structural latitude because the alternatives (a module global on shared engine state, or emitting from `dispatch()`/`_run_verb`) are worse and the latter is explicitly excluded by the plan. **You may disagree** — say so if you do.

## Specific Exclusions
- Do not touch `C:/Programs/constellation-skills` (the main checkout) or any sibling worktree.
- Do not re-litigate the seam choice (`start`/`reopen` vs `dispatch`) — that is settled by D1 with source verification.
- `run.dirty` removal is **g4**, not this gate. The `refusals` counter and the mechanical field-group composer are **g2**. Out of scope here; log anything you find as a note, not a BLOCK.

## Evidence Produced (verify, do not accept)
- Full suite: **1435 passed, 2 skipped, 410 subtests** — I reproduced this myself in 77s.
- Exit-code parity: 10/10 identical across five fail-soft cases vs. the pre-seam engine.
- A real `start` manifest whose durable row carries a **non-null** rev for `.agent-work/LESSONS.md` (`9bacc2c2...`) — this hash is the proof the double-nesting trap is disarmed.
- Mutation checks: a stub writing `files: []` kills 3 tests; going fail-silent kills 4.

## Your independent mutation is mandatory
**The implementer cannot audit its own falsifiability.** It shipped two mutants. You must devise **at least one mutation it did not ship**, outside its set, and confirm the suite catches it. If the suite does not catch your mutation, that is a finding, and it is the most valuable thing you can return.

**AUTHOR ADVERSARIAL INPUTS; do not merely re-run the suite** — a round-trip over shipped artifacts proves the artifacts, not the tool. Empty-vs-empty and missing-vs-missing both pass a naive equality check, so prove you read both things before you compare them.

Also apply the whole-predicate bar: a predicate with a boundary needs cases on **both** sides; one quantifying over a collection needs a **multi-element** case.

## Constraints on your own execution
- Tests: `python -m pytest` (3.14.3 / pytest 9.0.2). `py` is 3.12.13 with **no pytest**. Neither reproduces CI.
- Windows: explicit `encoding='utf-8', newline='\n'` on every write. `Path.read_text(newline=...)` is 3.13+ and **fails CI**.
- Compare normalized content or blob OIDs, **never raw working-tree bytes** (`core.autocrlf` differs across worktrees).

## Suggested Model Tier
**Opus** — stronger. The gate touches shared engine machinery three concurrent commanders depend on, and its central claim (unskippability) is a reachability argument over a status machine, which is exactly where a shallow read passes something false.

## Return
Write `REVIEW_RESULT` to `.agent-work/issue-305/crew/g1-review-result.md` with an explicit **APPROVE** or **BLOCK** verdict, per-criterion disposition, your independent mutation and its outcome, and a blunt `Workflow Feedback` section. Your final message must contain the same result.
