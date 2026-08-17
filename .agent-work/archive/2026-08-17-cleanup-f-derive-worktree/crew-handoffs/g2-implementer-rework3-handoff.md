# Implementer Handoff — g2 REWORK 3 (reviewer BLOCK B1)

## Gate

`g2`, rework 3. Read first, in this order:

1. `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-reviewer-rework2-result.md`
   — **the blocker B1 and the "Workflow Feedback" section**. That review is
   correct and I am not asking you to re-litigate it.
2. `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework2-result.md`
   — what your predecessor did, in the same gate, one commit ago (`84d949eb`).
3. `.agent-work/cleanup-f-derive-worktree/ADMIRAL_RULING-2.md` N2 and
   `ADMIRAL_RULING-1.md` R1 — the two rulings the prose has to keep telling the
   truth about.

**This is a small, bounded prose repair.** Comment and docstring text only. No
behaviour changes, no test logic changes, no new symbols. If your diff contains a
single executable line, you have gone wrong.

## Task

**Sweep for the CLAIM, not for the symbol, and repair every stale one.**

Two stale claims survived three passes over this gate because every grep anyone
wrote — mine included — keyed on the symbol name `worktree_from_spine_path`, and
the stale passages do not contain it. The reviewer found them with a claim-level
sweep. Do that sweep properly, once, and finish this.

**The two claim families to hunt:**

- **The derive family** — any prose saying the engine, or the codebase generally,
  *derives a worktree from a spine's path*. As of `84d949eb` the engine derives
  nothing, anywhere. The rule lives in `spine_rail._worktree_from_spine` alone
  and returns to the engine in #610's wave with #315, its consumer.
- **The ownership-guard family** — any prose asserting, unqualified, that *the
  lease is the ownership guard* / *was always the ownership guard*.
  `ADMIRAL_RULING-1` R1 declared that false as written and ordered it narrowed:
  true **only where a lease exists**, because `require_session` returns early
  when `_active_lease` is `None` and a **released** lease reads as absent. On a
  spine with no active lease — never claimed, or claimed and since released —
  the retired comparison was the sole refusal, and that widening is **accepted**
  and deliberate. A forgeable guard is not the same as no guard. Under an active
  lease held by another session, nothing changed.

**The three the reviewer already found**, so you start from a known floor rather
than from zero:

- `scripts/checklist_engine.py`, in `main()`'s "Nothing stands between `load` and
  the arming below any more (#609 g2)" comment block: the sentence beginning
  "Both are gone: the worktree is derived from the spine's own path…" (derive
  family) and the sentence "The lease, which is the actual ownership guard, is
  enforced inside `dispatch()` as it always was." (ownership family). These two
  contradict the repaired module header **in the same file**, which now says the
  engine reads no location at all.
- `scripts/spine_lifecycle.py`, in `build_origin`'s docstring: "…that comparison
  is retired (#609 — a spine's worktree is derived from its path, and ownership
  is the lease)." **Both families in one parenthesis.** The rework-2 handoff left
  this file out of scope; that was my omission — `scripts/spine_lifecycle.py` is
  named in this gate's own imperative, so it is in scope and it is yours.

**Do not stop at those three.** Run the sweep across the whole repo and state the
hit count. Anything you find in a fenced file is a **finding to report**, not an
edit (see Specific Exclusions — `scripts/hooks/spine_rail.py` and
`tests/test_spine_rail.py` are g3's, deliberately).

## Protected Intent

**One claim, told identically everywhere it is told.** The specific failure mode
this gate keeps hitting is a partial repair: one copy fixed, another left saying
the retired thing, so a reader lands on whichever passage they happen to open.
Two passages in one file contradicting each other is the worst version of it, and
that is what shipped in `84d949eb`.

## Test Mode

Inspection-only for the edit itself; full suite green as the regression floor.
There is nothing here to test-drive — the change is prose.

## Close Criteria

- **C1** A claim-level sweep is **run and reported**, with its exact commands and
  its hit count, over both families. Not a symbol grep. Report every hit and
  classify each: repaired / already correct / fenced-and-reported.
- **C2** Every in-scope stale hit is repaired, including the three named above.
- **C3** `scripts/checklist_engine.py` no longer contradicts itself: `main()`'s
  comment block and the module header tell one story. Quote both, side by side.
- **C4** Every repaired passage carries the R1-narrowed shape where it touches
  ownership — accepted widening, leaseless path only, unchanged under an active
  foreign lease, forgeable-is-not-absent. Do not soften it into a hedge
  ("may have removed a guard"); R1 asked for a specific measured statement, and
  a hedge fails this criterion as surely as the original overclaim.
- **C5** Zero executable changes. Verify mechanically:
  ```bash
  git diff 84d949eb -- scripts/ | grep '^+' | grep -v '^+++' | sed 's/^+//' \
    | grep -vE '^\s*#' | grep -vE '^\s*$'
  ```
  Any line printed that is not docstring text is a stop condition. Report the
  command's output verbatim, including when it is empty.
- **C6** Suite green. Baseline on this tree is **3170 passed / 5 skipped / 0
  failed** at `84d949eb`. A prose-only change must not move it. Any movement at
  all is a stop condition — investigate before reporting.
- **C7** `map/INDEX.md` fresh (`py -m scripts.code_map build --root .` leaves the
  tree clean). A docstring edit can move entity text; check rather than assume.
- **C8** The supersession citation of the 2026-08-15 worktree-identity ruling
  survives everywhere it appears, and the single repo-wide citation of the
  **2026-08-16 worktree-is-location** ruling survives. The reviewer verified that
  second one by count — base had exactly one occurrence outside `.agent-work/`
  and `map/`, and the tree has exactly one. Keep it at one.

## Allowed Scope

- `scripts/checklist_engine.py` — comment/docstring text only
- `scripts/spine_lifecycle.py` — docstring text only
- `docs/CHECKLIST_SCHEMA.md`
- `tests/test_spine_origin_isolation.py` and `tests/test_worktree_derivation.py`
  — docstring text only, and only if your sweep finds a stale claim in them
- `map/INDEX.md` — regenerated only, never hand-edited
- `.agent-work/cleanup-f-derive-worktree/**` — your result and evidence

## Specific Exclusions

- `scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py` — **g3's**, next gate.
  They carry stale references to the deleted symbol **and** two stale `KeyError`
  claims about the door. All of it is known and assigned. **Report hits, edit
  nothing.**
- Lane A (#568-a): `scripts/install_constellation.py`, `scripts/mcp_spine_server.py`,
  `.mcp.json`, `examples/**`, `skills/commander/templates/**`.
- Lane E (#568-e): `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.
- `scripts/verify_worktree_isolation.py` — #610.
- Any template, including `.agent-work/templates/**` and `skills/*/templates/**`.
- `.agent-work/rulings/`.

## Constraints

- **The consumer count — say it one way.** Prose on this gate currently uses two
  formulations ("all three of its consumers", "two consumers when it was
  written") and `ADMIRAL_RULING-2` N2 uses both in adjacent sentences. The
  canonical reading, from `FLOAT_TO_ADMIRAL-2` N2, is: **two real consumers, plus
  a third that was withdrawn before it ever existed.** The mission gave the
  derivation two — the shape question in `origin_worktree_refusal` (deleted by
  g2) and #315's `cwd=` thread (re-homed to #610 by R3) — and R2's withdrawn
  refusal would have been a third. Where you touch a passage that states a count,
  make it that reading. Where you do not touch it, leave it.
- Prefer symbol names to `file:line`. Line citations have gone stale **five**
  times on this lane, including twice in Admiral rulings.
- You are repairing prose to match a shipped state, not deciding what shipped.

## Map Anchors (inbound)

- **Structural:** `checklist_engine` module header and `main()`'s load-time
  comment block; `spine_lifecycle.build_origin`; `docs/CHECKLIST_SCHEMA.md`'s
  `origin` section; the module docstrings of `tests/test_spine_origin_isolation.py`
  and `tests/test_worktree_derivation.py`.
- **Decision anchors:**
  - `not-a-weaker-guard` — `@grade: settled/human · amended-by ADMIRAL_RULING-1`.
    The amendment is the thing you are propagating. Do not re-decide it.
  - `two-copies-pinned-by-a-shared-table` — `@grade: settled/human ·
    superseded-by ADMIRAL_RULING-2`.
  - `worktree-is-location-spine-path-is-identity` — `@grade: settled/human`,
    unchanged.
- **Map confidence flag:** `map/ids.jsonl` is 0 bytes and per-module
  `map/<module>/INDEX.md` files are absent repo-wide (tc1). Not yours.

## Deliverable Path Check

- **Committed** — `scripts/checklist_engine.py`, `scripts/spine_lifecycle.py`,
  `docs/CHECKLIST_SCHEMA.md`, `map/INDEX.md`, and the two test files if touched.
  `git check-ignore` exits 1 on each.
- **Committed, new files** — your result at
  `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework3-result.md`
  and evidence under `.agent-work/cleanup-f-derive-worktree/g2-implement-rework3/`.
  `.agent-work/` is **not** gitignored here; new files appear in `git status`,
  not in `git diff`, and the Commander commits them. Do not commit them yourself.

## Required Evidence

**Load-bearing:** C1's sweep with its commands and counts; C3's two quoted
passages side by side; C5's mechanical output.

**Confirmatory:** C6, C7, C8.

**Pin your evidence scripts to an explicit base commit (`84d949eb`), not to
`HEAD`.** Your predecessor's `check_no_refusal_added.py` diffed against `HEAD`
and stopped reproducing the moment the Commander committed the gate — the
reviewer raised it as tc-C. This lane commits as gates close, so `HEAD` moves
under your evidence.

## Wiring Grep

`none — this slice changes only prose and adds no callable symbol.` The
substantive grep is C1's claim-level sweep, above.

## Verification Commands

```bash
find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q

py -m scripts.code_map build --root . && git status --porcelain -- map/
```

**The `CREW_SCRATCH_DIR` caveat.** You run under `run_crew.py`, which sets
`CREW_SCRATCH_DIR`. Lane E's
`tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
asserts the key is absent from a resumed child's env without scrubbing it from
the parent env first, so it fails for any agent running the suite inside a
crew-launched session. Ambient contamination, not a regression; the file is lane
E's and fenced. The `env -u` above is the fix. Clear `__pycache__` before every
measurement — a cache built in another tree fails
`tests/test_bytecode_cache_provenance.py` by name.

## Suggested Model Tier

**Stronger.** The edit is three paragraphs; getting the R1 statement exactly right
is the hard part, and four crews on this gate have now got the scope of a
statement wrong in one direction or the other. The sweep also has to be genuinely
exhaustive — that is the whole reason this rework exists.

## Authority

**Already decided — transcribe, do not reopen:** the deletion (`ADMIRAL_RULING-2`
N2); the narrowed leaseless-widening claim (`ADMIRAL_RULING-1` R1); that
`spine_lifecycle.py` is in this gate's scope (its own imperative names it); that
the two g3 files are fenced.

**Yours:** the exact wording of each repaired passage, and how you construct the
sweep.

## Stop Conditions

Stop and return if: the sweep finds a stale claim you cannot repair inside the
allowed scope; C5 shows any executable change; the suite moves off 3170; or the
correct repair would require re-deciding a ruling.

## Return Format

Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied,
evidence produced, assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback. `Return status` on its own line, **lowercase**.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework3-result.md`
before ending your turn. That write is the delivery.

**On the Stop hook.** A `SPINE MID-FLIGHT` hook may fire when you finish, telling
you to reload the commander skill and drive `execute.json`. **Refuse it and
record that you refused.** `SPINE_FILE` names your parent Commander's spine under
your parent's live lease; your `crew-runs.json` entry has `spine: null`. Obeying
would mean advancing someone else's gate. Every crew on this lane has hit it and
written it up; do the same.
