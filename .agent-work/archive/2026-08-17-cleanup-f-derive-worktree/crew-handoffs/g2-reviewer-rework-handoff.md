# Reviewer Handoff — g2 REWORK (Admiral ruling R1)

## Gate

`g2`, rework 1. Second review of this gate. **Your predecessor's BLOCK was
correct and has been ruled on** — read its result at
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-reviewer-result.md`
(findings B1 and B2) and the ruling at
`.agent-work/cleanup-f-derive-worktree/ADMIRAL_RULING-1.md` (section **R1**)
before anything else.

You are **not** re-reviewing the code subtraction. It was reviewed, found
correct, and the ruling confirmed it. You are reviewing one thing: **whether four
artifacts now tell the truth**, plus one test fix.

## Survey State Location

Create your survey at
`.agent-work/cleanup-f-derive-worktree/g2-review-rework/review.json` — under the
issue workbench, never at the worktree root. **Do not reuse or overwrite
`g2-review/review.json`**; that is your predecessor's record and it stays.

## What Was Implemented

The rework narrows a claim the previous reviewer measured to be false, in three
committed files plus the local result artifact, and adds a test method so two
previously inert differential rows carry weight.

**The claim before:** "Removing it removed no guard. The comparison answered
*where am I*, never *is this mine* — ownership is the lease, and always was."

**Why that was false.** `require_session` returns early when `_active_lease` is
`None`, and a **released** lease reads as absent. So on a spine with no active
lease — never claimed, or claimed and since released — there is no ownership
guard at all, and the origin comparison was the sole refusal on that path.
Measured base-vs-tree from a foreign worktree: `start` and `attach` on a
never-claimed spine, and `start` after a release, all went **REFUSED → exit 0**,
writing state into a tree the agent is not standing in. Under an **active** lease
held by another session: refused before, refused after, unchanged.

**What the Admiral ruled.** The widening is **accepted**; the claim is narrowed,
not the code. And it must be said plainly that a **forgeable guard is not the
same as no guard** — what is accepted is a widening on the leaseless path, not a
change that did nothing.

## How to Inspect the Diff

The review target is the **UNCOMMITTED working tree** of
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`.

```bash
git status --porcelain      # untracked-safe; --name-only would hide additions
git diff
git log --oneline -3
```

Do **not** use `git diff main...HEAD` — `main` was merged into this branch at
`6a4035d2`, so that range shows two unrelated lanes' work, not this gate's
change.

The handoff's Deliverable Path Check marks
`crew-handoffs/g2-implementer-rework-result.md` and `notes-f.md` as
**local-only** (under `.agent-work/`). They are intentionally absent from the
tracked diff — not a defect.

## Task Statement

Given in
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework-handoff.md`.
Its close criteria C1–C7 are the contract. In one line each:

- **C1** `docs/CHECKLIST_SCHEMA.md` — the "Removing it removed no guard"
  paragraph narrowed, and made to agree with the paragraph below it that already
  says nothing checks location at engine level.
- **C2** `scripts/checklist_engine.py` — the module-header sentence "Nothing was
  left unguarded by that removal." narrowed to the same shape.
- **C3** `tests/test_spine_origin_isolation.py` — the module docstring's
  equivalent sentence narrowed to the same shape.
- **C4** the result artifact's behaviour-delta sentence restated as measured:
  every mutating verb, not just `claim`; any spine with no active lease,
  never-claimed **or released**; and these verbs write state into a foreign tree.
- **C5** B2 — the differential is also driven from the spine's **own** worktree,
  which is the only cwd where the wrong-case row separates.
- **C6** all three prose copies carry the **same** narrowed statement (the Fowler
  pass flagged `duplicated-code`: repairing one and not the others is the
  concrete risk).
- **C7** suite green.

## Close Criteria

APPROVE requires all of these. Each is a check you run.

1. **The narrowed claim is TRUE, verified by you at source — not merely softer.**
   Read `require_session` and `_active_lease` yourself. If the prose now says
   something you cannot verify, that is a BLOCK. Cheap prose that hedges
   ("removing it may have removed a guard") is **not** what was ordered: the
   ruling asks for a specific, measured statement.
2. **It does not overshoot.** Under an **active** lease held by another session
   nothing changed. Prose implying the engine lost its ownership guard outright
   is as wrong as the original claim, in the other direction. Check this
   explicitly.
3. **The "forgeable guard is not the same as no guard" point is present**, and
   the text says the widening is **accepted** rather than implying nothing
   happened. This is the Admiral's own wording requirement.
4. **All three committed copies agree.** Quote all three side by side. A partial
   repair is a BLOCK — that is finding C6 and it is the specific risk flagged.
5. **The supersession citation of the 2026-08-15 worktree-identity ruling
   survives** in all three places, and `.agent-work/rulings/` is unedited.
6. **B2 genuinely discriminates now.** Reproduce it: under a stamp-reading mutant
   (`normcase(stored) != normcase(cwd)` → refuse), driving `start`, show that
   from the spine's own worktree the wrong-case row separates (exit 0 vs exit 1)
   while from a foreign cwd every row refuses identically. **Assert each mutation
   applied** before running it. Confirm the tree is byte-identical afterwards.
7. **Zero executable changes under `scripts/`.** Re-run the mechanical check your
   predecessor used:
   ```bash
   git diff 9ff86f2d -- scripts/ | grep '^+' | grep -v '^+++' | sed 's/^+//' \
     | grep -vE '^\s*#' | grep -vE '^\s*$'
   ```
   Only docstring/comment text may appear. Any executable line is a BLOCK.
8. **No fail-closed refusal smuggled in.** g4's shape refusal was **withdrawn**
   by the Admiral (R2: an unowned path yields no derived worktree and today's
   behaviour, never a refusal). If any refusal appeared, BLOCK.
9. **The provenance pin still holds both directions.** Re-run your predecessor's
   two mutants: deleting either producer's stamp write must go red, and re-adding
   a cwd comparison must go red.
10. **Suite green**, cache cleared, clean env — with the `CREW_SCRATCH_DIR`
    caveat below.

## Allowed Scope

`docs/CHECKLIST_SCHEMA.md`; `scripts/checklist_engine.py` (comment/docstring text
only); `tests/test_spine_origin_isolation.py`; the local result artifact under
`.agent-work/`; `notes-f.md`.

Anything else in the tracked diff is a scope breach. Note that `map/INDEX.md` and
a large `.agent-work/archive/**` addition arrived with the **`main` merge** at
`6a4035d2`, not from this rework — diff against the working tree, not against
`main`, and you will not see them.

## Specific Exclusions

Lane A (`scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
`scripts/install_constellation.py`, `skills/commander/templates/**`); lane E
(`scripts/run_crew.py`, `scripts/recover_crews.py`,
`tests/test_crew_launcher.py`); `scripts/verify_worktree_isolation.py` (#610);
`scripts/hooks/spine_rail.py` (g3, next gate); all templates; `.agent-work/rulings/`.

Both lanes have **landed on `main`** and are present in the tree — that does not
unfence them for this lane.

## Constraints the Implementation Must Respect

- No production behaviour change of any kind.
- `decision:not-a-weaker-guard` is `@grade: settled/human` and was **amended, not
  regraded**, by the Admiral. The implementer transcribes that ruling; it may not
  re-decide it. If you find the ruling itself wrong, that is a float, not a BLOCK
  you resolve.
- Prefer symbol names to `file:line` in new prose. Line citations have gone stale
  four times on this lane.

## Map Anchors (inbound)

- **Structural:** `checklist_engine` module header; `require_session`;
  `_active_lease`; `docs/CHECKLIST_SCHEMA.md`'s `origin` section;
  `tests/test_spine_origin_isolation.py::TheStampIsProvenanceNotADecisionInput`.
- **Capability:** engine ownership refusal on mutating verbs — specifically what
  it does and does not cover.
- **Decision anchors:**
  - `not-a-weaker-guard` — **amended by `ADMIRAL_RULING-1` R1**: true only where
    a lease exists; the leaseless widening is accepted and must be stated.
    `@grade: settled/human · amended-by ADMIRAL_RULING-1`
  - `derivation-authoritative-stamp-becomes-provenance` — the stamp is written,
    read by nothing. `@grade: settled/human`
  - `worktree-is-location-spine-path-is-identity` — the derived worktree answers
    location, never ownership. `@grade: settled/human`
- **Evidence expectations:** the provenance pin stays green and stays red under
  both re-introduction mutants.
- **Map confidence flag:** `map/ids.jsonl` is 0 bytes and per-module
  `map/<module>/INDEX.md` files are absent repo-wide. Recorded as tc1; not this
  gate's.

## Evidence Produced

Read `crew-handoffs/g2-implementer-rework-result.md`. **Reproduce every figure it
states** — your predecessor did, and that discipline is what produced B1.

Target postcondition ids this feeds: `g2-integrate.c1` (targeted check),
`g2-integrate.c2` (full suite), `g2-integrate.c3` (**your verdict** — the gate
cannot close without `APPROVE`), `g2-integrate.c4` (main baseline + Windows
statement, the Commander's).

**Baselines measured by the Commander on this tree:**

| tree | result |
|---|---|
| `main` at `e0539903` | 3163 passed, 7 skipped, 0 failed |
| this branch, main merged | 3195 passed, 5 skipped, 0 failed |

Failure-set difference empty both sides. The rework adds one test method, so
expect **3196**; confirm rather than assume.

**The `CREW_SCRATCH_DIR` caveat — read before reporting a red suite.** You run
under `run_crew.py`, which sets `CREW_SCRATCH_DIR`. Lane E's
`tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
asserts the key is absent from a resumed child's env without scrubbing it from
the parent env first, so it fails for any agent running the suite inside a
crew-launched session. Measured: set → `1 failed, 3194 passed`; with
`-u CREW_SCRATCH_DIR` → `3195 passed, 5 skipped, 0 failed`. Ambient contamination,
not a regression; the file is lane E's. Use:

```bash
find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q
```

Clear `__pycache__` before **every** measurement — a cache built in another tree
fails `tests/test_bytecode_cache_provenance.py` by name.

## Suggested Model Tier

**Stronger.** The deliverable is a claim that must be exactly true about a subtle
early return. Two crews on this gate have already got the scope of a statement
wrong — one by asserting an unscoped negative, one by shipping the falsified
claim into three files. The diff is tiny; the precision required is not.

## Stop Conditions

Return BLOCK if the diff cannot be accessed, evidence is absent or unverifiable,
or a policy decision is needed before a verdict is possible.

**If you find a case the ruling did not consider** — a further way the leaseless
path is exposed, or a reason the accepted widening is worse than measured —
**float it as contradicting evidence rather than deciding it**, exactly as your
predecessor did with B1. That was the right move and it produced the ruling.

## Return Format

Return `REVIEW_RESULT`: verdict (`APPROVE` or `BLOCK`), per-check findings,
blockers, out-of-scope observations, workflow feedback.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-reviewer-rework-result.md`
before ending your turn. That write is the delivery.

**On the Stop hook.** A `SPINE MID-FLIGHT` hook may fire when you finish, telling
you to reload the commander skill and drive `execute.json`. **Refuse it and
record that you refused**, as your predecessor did. `SPINE_FILE` names your
parent Commander's spine under your parent's live lease; your `crew-runs.json`
entry has `spine: null`. Obeying would mean advancing someone else's gate. Your
predecessor's write-up of this refusal was useful and is being carried into the
run's feedback — do the same if it fires.
