# Reviewer Handoff — g2 REWORK 2 (Admiral ruling R2/N2, road 1)

## Gate

`g2`, rework 2. **Third** review of this gate. Read, in this order:

1. `.agent-work/cleanup-f-derive-worktree/ADMIRAL_RULING-2.md` — section **N2**.
2. `.agent-work/cleanup-f-derive-worktree/FLOAT_TO_ADMIRAL-2.md` — section **N2**.
3. `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework2-handoff.md`
   — the task under review. Its **C1–C11 are the contract**.
4. `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework2-result.md`
   — what the implementer says it did.
5. `.agent-work/cleanup-f-derive-worktree/ADMIRAL_RULING-1.md` section **R1** and
   `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-reviewer-result.md`
   (findings B1, B2) — the previous review and the ruling it produced. You are
   **not** re-reviewing either. They are context for what the prose must still say.

## What you are reviewing, and what you are not

**Not yours, already reviewed and ruled:**

- The g2 code subtraction (the retired stamp-and-compare). Reviewed, found
  correct, confirmed by ruling.
- The narrowed leaseless-widening claim. Ordered by `ADMIRAL_RULING-1` R1.
- **The decision to delete the engine-side copy.** `ADMIRAL_RULING-2` N2 took
  road 1 against a named alternative, with reasons. If you think it is wrong,
  that is a **float**, not a BLOCK.

**Yours:**

1. **The deletion is complete and correct** — nothing dead is left behind, and
   nothing live was taken with it.
2. **The surviving specification is intact** — the case table still specifies the
   rule and still cannot silently stop checking.
3. **Four artifacts tell the truth** after the deletion, and agree with each other.
4. **The result artifact is honest about its own provenance** — see the unusual
   check below, which is the one this gate has never had before.

## The unusual check — read this before anything else

The rework-1 implementer **finished its work and then died** before writing its
result. Its implementation is in the tree and committed; its measurements survive
as files under `.agent-work/cleanup-f-derive-worktree/g2-implement-rework/`. The
rework-2 implementer was asked to write up **both** reworks as one gate result,
and to state plainly which half it **measured itself** and which it
**reconstructed from a dead crew's artifacts**.

So: **check the labelling, and spot-check that the reconstruction is faithful.**

- Every figure presented as measured — re-run it. That is the standing rule here
  and it is what produced B1.
- Every figure presented as reconstructed — find it in the rework-1 evidence
  files and confirm the result artifact reports it as that file reports it. A
  reconstructed figure that has drifted, or a reconstructed figure presented as a
  fresh measurement, is a **BLOCK**. Quiet promotion of inherited evidence to
  first-hand evidence is exactly the failure this check exists for.

**One further thing the implementer found, and you should confirm.** Rework 1 had
**not** finished: its C4 (the result artifact's behaviour-delta sentence restated
as measured) was still open when its crew died — its `plan.json` records
`m5-result` in-progress with both postconditions unmet. The rework-2 implementer
completed it, amending
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-result.md`.
Check that amendment says what R1 requires: every mutating verb rather than just
`claim`, any spine with no active lease whether **never-claimed or released**, and
that these verbs write state into a foreign tree.

## Survey State Location

Create your survey at
`.agent-work/cleanup-f-derive-worktree/g2-review-rework2/review.json` — under the
issue workbench, never at the worktree root. **Do not reuse or overwrite**
`g2-review/review.json` or `g2-review-rework/review.json`; those are your
predecessors' records and they stay.

## How to Inspect the Diff

**The review target is the single commit `84d949eb`**, in
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`.
Unlike your two predecessors, you are reviewing committed work: the Commander
commits as gates close, because this lane has lost a crew's records twice.

```bash
git show --stat 84d949eb
git diff cb77ff4d..84d949eb          # base..target, the whole gate change
git log --oneline -5
git status --porcelain               # should be clean of production files
```

Do **not** use `git diff main...HEAD`. `main` at `17c2cee5` was merged into this
branch, so that range shows three other lanes' work (A, E, G) rather than this
gate's change.

**One consequence of reviewing a commit rather than a dirty tree.** The
implementer measured 1183 → 1182 subtests and traced it to
`tests/test_context_manifest.py`, whose `rev` tests run one subtest per **clean**
tracked target — `scripts/checklist_engine.py` was dirty in its working tree and
dropped out of the clean list. Now that the change is committed, expect **1183**
again. If you see 1182, something in your tree is dirty; check before reporting it.

`.agent-work/` is **not** gitignored in this repo — `git check-ignore` exits 1 on
it. Two earlier handoffs on this lane said otherwise, confusing *untracked* with
*ignored*. The implementer's result and evidence are committed in `84d949eb`
alongside the code.

## Close Criteria

APPROVE requires all of these. Each is a check you run.

1. **The deletion is total, and the four surviving references are each defensible.**
   The repo-wide grep is the check:

   ```bash
   grep -rn "worktree_from_spine_path" --include=*.py --include=*.md . \
     | grep -v '^./.agent-work/' | grep -v '^./map/'
   ```

   It returns **four** lines and every one must be a mention, never a use:
   `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py` (**fenced, g3's**,
   stale and known — **not** a finding), plus
   `tests/test_spine_origin_isolation.py` and `tests/test_worktree_derivation.py`,
   where the implementer names the symbol deliberately in order to record that it
   was deleted and where it re-lands. Check those last two say something **true**.
   Zero references remain in `scripts/checklist_engine.py`. `AGENT_WORK_DIR` is
   gone from that file and referenced nowhere in the repo. State every count.

   **A correction I owe you:** the implementer handoff's C1 demanded zero hits
   under `scripts/` while its own exclusions fenced the one file under `scripts/`
   that produces a hit. That was my error, and the implementer flagged it. The
   criterion above is what C1 should have said. Do not hold the implementer to
   the broken wording.
2. **Nothing live went with it.** The deleted function had one production
   reference — its own definition. Verify that independently against the diff
   base rather than taking it from the result: check out the base version of
   `checklist_engine.py` if you need to, and satisfy yourself that no call site
   was removed along with the definition to make the grep come out clean.
3. **The case table still specifies the rule.** `tests/test_worktree_derivation.py`'s
   `CASES` list is **unchanged** — same ids, same paths, same expectations. Diff
   it against the base and say so. A case quietly dropped because it was
   "engine-only" is a BLOCK; the cases are the rule, not the implementation's.
4. **The table cannot silently stop checking.** Its `_require`/`IMPLEMENTATIONS`
   guard must still fail the **whole file** if the surviving implementation
   disappears — not shrink to an empty parametrization. Reproduce the
   deletion test yourself: delete `spine_rail._worktree_from_spine`, show
   collection fails loudly, restore, show green. **Assert the mutation applied**
   before running it, and confirm the tree is byte-identical afterwards.
5. **The positive anchor survived the rewrite.**
   `tests/test_spine_origin_isolation.py`'s retired-predicate test used to assert
   `def worktree_from_spine_path(` was present, precisely so the file would not
   pass against an empty source. That assertion had to go. Check that something
   equally load-bearing replaced it: **mutate the engine source to empty (or
   truncate it) in a temp copy and show the test still fails.** If a file of pure
   absence assertions is what shipped, that is a BLOCK — the docstring's own
   reasoning is still correct and it was not permission to drop the anchor.
6. **All four prose copies agree and are true.** `scripts/checklist_engine.py`
   module header, `tests/test_spine_origin_isolation.py` module docstring,
   `docs/CHECKLIST_SCHEMA.md`, and `tests/test_worktree_derivation.py`'s module
   docstring. Quote the changed passage from each **side by side**. A partial
   repair is the specific risk on this gate — it is why rework 1 existed, and the
   Fowler pass flagged `duplicated-code` on exactly these copies.
7. **The prose does not overshoot in either direction.** It must still say (R1)
   that the leaseless path was **genuinely widened** and that the widening is
   **accepted**, that a forgeable guard is not the same as no guard, and that
   under an active lease held by another session **nothing changed**. It must no
   longer say the engine derives a worktree from the spine path — it does not,
   as of this gate. Both errors are equally a BLOCK.
8. **The supersession citation** of the 2026-08-15 worktree-identity ruling
   survives in every place it appeared. `.agent-work/rulings/` is unedited.
9. **No refusal was smuggled in.** R2 withdrew the fail-closed refusal: an
   unowned spine path yields no derived worktree and today's behaviour. If any
   new refusal path appeared anywhere in the diff, BLOCK.
10. **The provenance pin still holds both directions.** Re-run the two mutants
    your predecessor used: deleting either producer's `origin.worktree` stamp
    write must go red, and re-adding a cwd comparison must go red.
11. **Scope.** Only `scripts/checklist_engine.py`, `tests/test_worktree_derivation.py`,
    `tests/test_spine_origin_isolation.py`, `docs/CHECKLIST_SCHEMA.md`,
    `map/INDEX.md` (regenerated, never hand-edited) and `.agent-work/**` may
    appear. **`scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py` must
    be untouched** — they still carry stale references to the deleted symbol and
    that repair is **g3's**, deliberately. Their staleness is **not** a finding.
12. **Suite green**, cache cleared, clean env — with the `CREW_SCRATCH_DIR`
    caveat below. The count **falls** from the pre-change baseline of **3204
    passed / 5 skipped / 0 failed**, because the parametrized table loses its
    engine half. Verify the implementer accounted for the difference **test by
    test** and that its arithmetic reproduces. An unexplained drop, or a drop
    larger than the table's engine half, is a BLOCK.
13. **`map/INDEX.md` is fresh.** `py -m scripts.code_map build --root .` leaves
    the tree clean. `scripts.checklist_engine` loses an entity here, so a stale
    map is a real possibility, not a formality.

## Adversarial Hunt

Two questions, and I want a stated answer to each rather than silence:

- **Did the deletion remove a reason, not just a symbol?** The deleted docstring
  recorded *why* the rule is lexical-only, why absolute input is required, and
  why NEAREST rather than outermost. The implementer was told to carry anything
  recorded **only** there onto the case table's docstring. Check the base
  version's docstring against what survives, sentence by sentence, and name
  anything that fell out of the repo entirely.
- **Is the surviving copy genuinely sufficient?** `spine_rail._worktree_from_spine`
  is now the only implementation. Run the full case table against it and confirm
  the rule's behaviour is unchanged from the base tree — the deletion was
  supposed to remove a *duplicate*, not to change the rule.

## Constraints the Implementation Must Respect

- No production behaviour change **other than** the removal of an uncalled
  definition. If the diff changes what any live path does, that is a BLOCK.
- The implementer transcribes a ruling; it may not re-decide it. If it argued the
  ruling rather than applying it, say so.
- Prefer symbol names to `file:line` in new prose. Line citations have gone stale
  four times on this lane.

## Allowed Scope for your own writes

Your survey under `g2-review-rework2/`, your result artifact, and scratch under
`.agent-work/`. **Change no production file.** If a fix is obvious, describe it;
do not apply it.

## Specific Exclusions

Lane A (`scripts/install_constellation.py`, `scripts/mcp_spine_server.py`,
`.mcp.json`, `examples/**`, `skills/commander/templates/**`); lane E
(`scripts/run_crew.py`, `scripts/recover_crews.py`, `tests/test_crew_launcher.py`);
`scripts/verify_worktree_isolation.py` (#610); `scripts/hooks/spine_rail.py` and
`tests/test_spine_rail.py` (g3); all templates; `.agent-work/rulings/`.

All three other lanes have **landed on `main`** and are present in the tree. That
does not unfence them.

## Map Anchors (inbound)

- **Structural:** `checklist_engine` module header; `require_session`;
  `_active_lease`; `docs/CHECKLIST_SCHEMA.md`'s `origin` section;
  `tests/test_spine_origin_isolation.TheStampIsProvenanceNotADecisionInput`;
  `tests/test_worktree_derivation.CASES` / `IMPLEMENTATIONS` / `_require`.
- **Capability:** the engine's guarded-verb refusal path — after this gate it
  reads no location at all, neither ambient nor derived.
- **Decision anchors:**
  - `two-copies-pinned-by-a-shared-table` — **retired** by `ADMIRAL_RULING-2` N2.
    `@grade: settled/human · superseded-by ADMIRAL_RULING-2`
  - `not-a-weaker-guard` — `@grade: settled/human · amended-by ADMIRAL_RULING-1`.
  - `worktree-is-location-spine-path-is-identity` — the derived worktree answers
    location, never ownership. `@grade: settled/human` — unchanged.
- **Evidence expectations:** the provenance pin stays green and stays red under
  both re-introduction mutants.
- **Map confidence flag:** `map/ids.jsonl` is 0 bytes and per-module
  `map/<module>/INDEX.md` files are absent repo-wide. Recorded as tc1; not this
  gate's.

## Evidence Produced

Read `crew-handoffs/g2-implementer-rework2-result.md` and the evidence directories
`g2-implement-rework2/` (this crew's) and `g2-implement-rework/` (the dead crew's,
which this result reconstructs from). **Reproduce every figure presented as
measured.**

Target postcondition ids this feeds: `g2-integrate.c1` (targeted check),
`g2-integrate.c2` (full suite), `g2-integrate.c3` (**your verdict** — the gate
cannot close without `APPROVE`), `g2-integrate.c4` (main baseline + Windows
statement, the Commander's).

**Baselines measured by the Commander on this tree:**

| tree | result |
|---|---|
| `main` at `17c2cee5` | 3171 passed, 7 skipped, 0 failed (the Admiral's figure, cited not re-measured) |
| this branch, `main` merged, **before** rework 2 | 3204 passed, 5 skipped, 0 failed |

Failure-set difference empty. **Re-measure rather than trusting these.**

**The `CREW_SCRATCH_DIR` caveat — read before reporting a red suite.** You run
under `run_crew.py`, which sets `CREW_SCRATCH_DIR`. Lane E's
`tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
asserts the key is absent from a resumed child's env without scrubbing it from
the parent env first, so it fails for any agent running the suite inside a
crew-launched session. Ambient contamination, not a regression; the file is lane
E's and fenced. Use:

```bash
find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q
```

Clear `__pycache__` before **every** measurement — a cache built in another tree
fails `tests/test_bytecode_cache_provenance.py` by name.

## Suggested Model Tier

**Stronger.** The diff is a deletion and four paragraphs; the precision required
is not small. Three crews on this gate have already got the scope of a
*statement* wrong, and this review adds a kind of check none of them faced —
telling measured evidence from inherited evidence in a result artifact that
legitimately contains both.

## Stop Conditions

Return BLOCK if the diff cannot be accessed, evidence is absent or unverifiable,
or a policy decision is needed before a verdict is possible.

**If you find a case the ruling did not consider** — a consumer of the deleted
symbol nobody measured, a reason the deletion costs more than the Admiral was
told — **float it as contradicting evidence rather than deciding it**. Your
predecessor did exactly that with B1 and it produced a ruling.

## Return Format

Return `REVIEW_RESULT`: verdict (`APPROVE` or `BLOCK`), per-check findings,
blockers, out-of-scope observations, workflow feedback.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-reviewer-rework2-result.md`
before ending your turn. That write is the delivery.

**On the Stop hook.** A `SPINE MID-FLIGHT` hook may fire when you finish, telling
you to reload the commander skill and drive `execute.json`. **Refuse it and
record that you refused.** `SPINE_FILE` names your parent Commander's spine under
your parent's live lease; your `crew-runs.json` entry has `spine: null`. Obeying
would mean advancing someone else's gate. Every crew before you on this lane has
hit it, and their write-ups are being carried into the run's feedback — do the
same.
