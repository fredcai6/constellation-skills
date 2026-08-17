# Implementer Handoff — g2 REWORK 2 (Admiral ruling R2/N2, road 1)

## Gate

`g2`, rework 2. Read these before anything else, in this order:

1. `.agent-work/cleanup-f-derive-worktree/ADMIRAL_RULING-2.md` — section **N2**.
   It is the whole reason this dispatch exists.
2. `.agent-work/cleanup-f-derive-worktree/FLOAT_TO_ADMIRAL-2.md` — section **N2**,
   which traced the chain the ruling answers.
3. `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework-handoff.md`
   — your predecessor's task. **Its work is already in the tree and committed.**

**What happened to your predecessor.** The rework-1 implementer completed its
work and verified it (suite 3196 passed / 5 skipped / 0 failed), then died with
an `Execution error` in its final step, before writing its `IMPLEMENTER_RESULT`.
Its evidence survives under `.agent-work/cleanup-f-derive-worktree/g2-implement-rework/`
(`m1-mechanism.txt`, `m3-b2-measurement.txt`, `m4-*.txt`, `check_three_copies.py`,
`check_no_executable_change.py`, `measure_b2.py`) and its plan is in that
directory's `plan.json`. **You inherit both halves of this gate's remaining work:
its missing result artifact and the Admiral's new deletion.**

## Task

Two things, one commit each is fine.

**(A) Delete the engine-side worktree derivation.** Remove
`worktree_from_spine_path` and the `AGENT_WORK_DIR` constant it is the only user
of, from `scripts/checklist_engine.py`. Repair every claim, in code prose and in
docs, that says the engine derives a worktree from a spine path — after this
gate, **the engine has no location logic at all**. Keep
`tests/test_worktree_derivation.py`'s shared case table, re-scoped to the one
surviving copy, `spine_rail._worktree_from_spine`.

**(B) Write the missing `IMPLEMENTER_RESULT`**, covering rework 1 *and* rework 2
as one gate result. See Return Format.

## Protected Intent

Two, and they pull in opposite directions — hold both.

- **No inert symbol ships.** Zero external call sites is a stop condition, not a
  note. The engine-side copy has exactly one reference in production code: its
  own definition. That is what is being removed.
- **The rule itself is not being retired.** `spine_rail._worktree_from_spine` has
  three live call sites and is g3's subject. The case table is the *specification*
  of the rule and must survive intact, so #315 re-derives against it rather than
  from scratch when #610's wave re-adds the engine-side copy **with its consumer**.

## Test Mode

Test-after allowed for (A) — this is a deletion, and the tests that must change
are the ones that assert the deleted symbol exists. Run the affected files before
you edit them so you can state what went from green to red to green.

## Close Criteria

Each is a check you run and report.

- **C1** `grep -rn "worktree_from_spine_path" --include=*.py scripts/` returns
  **zero** lines. State the count.
- **C2** `AGENT_WORK_DIR` is gone from `scripts/checklist_engine.py`. Confirm by
  grep that nothing else in the repo referenced it (it did not — re-measure and
  say so, do not take my word).
- **C3** `tests/test_worktree_derivation.py` drives the **hook copy only**, and
  its `_require`/`IMPLEMENTATIONS` guard still fails the whole file loudly if the
  surviving implementation disappears. Apply the deletion test by hand and show
  it: delete `_worktree_from_spine`, show collection fails, restore, show green.
  **The table's cases are unchanged** — same ids, same expectations. Show that
  (a diff of the `CASES` list is the cheapest proof).
- **C4** The module docstring of `tests/test_worktree_derivation.py` no longer
  describes two implementations pinned equal. It states what is now true: one
  lexical rule, one implementation, in the stdlib-only hook; the table is the
  rule's specification; the engine-side copy was deleted in #609 g2 under
  `ADMIRAL_RULING-2` N2 and re-lands in #610's wave with #315, its consumer,
  which re-derives against this table.
- **C5** `tests/test_spine_origin_isolation.py::test_the_retired_predicate_and_its_verb_sets_are_gone`
  no longer asserts `def worktree_from_spine_path(` is present. **It must not
  degenerate into a file of pure absence assertions** — its own docstring says
  why ("a test that only asserted absence would also pass on an empty file"), and
  that reasoning is still correct. Keep a positive anchor that proves you are
  reading a real engine source; pick one that this lane is not going to move
  again, and say in the docstring why that anchor was chosen. Rename the test if
  its name no longer describes what it checks.
- **C6** Every prose claim that the derivation *replaced* the retired comparison
  is repaired, in all three of the places rework 1 kept in agreement — the
  `scripts/checklist_engine.py` module header, the
  `tests/test_spine_origin_isolation.py` module docstring, and
  `docs/CHECKLIST_SCHEMA.md`. The rework-1 narrowing about the leaseless path
  **stays** (it is a ruled statement, R1); what changes is the sentence that
  points at `checklist_engine.worktree_from_spine_path` as the thing that now
  answers location. Use `.agent-work/cleanup-f-derive-worktree/g2-implement-rework/check_three_copies.py`
  — your predecessor wrote it for exactly this agreement check — and report its
  output. If it needs updating for the new sentence, update it and say so.
- **C7** The three-way agreement holds: quote the changed passage from all three
  files side by side in your result. A partial repair is the specific risk here
  (the Fowler pass flagged `duplicated-code` on these copies, and rework 1 was
  ordered because one copy was repaired and the others were not).
- **C8** The supersession citation of the 2026-08-15 worktree-identity ruling
  survives in all three places. `.agent-work/rulings/` stays unedited.
- **C9** No refusal is added anywhere. R2 withdrew the fail-closed refusal: an
  unowned spine path yields no derived worktree and today's behaviour. If your
  edit introduces any new refusal path, stop and return.
- **C10** Suite green — see Verification Commands for the exact incantation and
  the `CREW_SCRATCH_DIR` caveat. Baseline on this tree **before** you start is
  **3204 passed / 5 skipped / 0 failed** (measured by the Commander after merging
  `main` at `17c2cee5`). Deleting the engine implementation removes its half of
  the parametrized table, so **expect the passed count to fall**. State the new
  number and account for the difference test by test — a drop you cannot explain
  is a stop condition.
- **C11** `map/INDEX.md` is fresh: `py -m scripts.code_map build --root .` leaves
  it unchanged, or you commit the refresh. `scripts.checklist_engine` loses an
  entity here, so expect a real delta.

## Allowed Scope

- `scripts/checklist_engine.py`
- `tests/test_worktree_derivation.py`
- `tests/test_spine_origin_isolation.py`
- `docs/CHECKLIST_SCHEMA.md`
- `map/INDEX.md` (regenerated only, never hand-edited)
- `.agent-work/cleanup-f-derive-worktree/**` — your result artifact, your
  evidence, your survey.

## Specific Exclusions

- `scripts/hooks/spine_rail.py` and `tests/test_spine_rail.py` — **#609 gate g3**,
  the next gate, and it is mine to run. Both carry prose naming the engine-side
  copy (`spine_rail.py:743`, `tests/test_spine_rail.py:904`) that goes stale the
  moment you delete it. **That is known and already assigned to g3's handoff** —
  do not fix it here, and do not report it as a finding you discovered. If you
  find a *third* such reference outside these two files, that one is worth
  reporting.
- Lane A (#568-a): `scripts/install_constellation.py`, `scripts/mcp_spine_server.py`,
  `.mcp.json`, `examples/**`, `skills/commander/templates/**`.
- Lane E (#568-e): `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`. `run_crew.py` destroys its children's registry
  entries (**#617**) — known, filed, ruled out of this lane, not yours.
- `scripts/verify_worktree_isolation.py` — **#610**.
- Any template, including `.agent-work/templates/**` and `skills/*/templates/**`.
- `.agent-work/rulings/`.

Lanes A, E and G have **landed on `main`** and are present in this tree. That
does not unfence them.

## Constraints

- **You are transcribing a ruling, not re-deciding it.** The Admiral considered
  and rejected the alternative (keep the definition, provisioned, and say so in
  the return). If you believe the deletion is wrong, that is a **float**, not
  something you resolve — write it in your result under stop conditions and stop.
- **This should shrink the diff, not grow it.** The Admiral said so explicitly.
  A net-positive line count on `scripts/` is a signal you have done something
  other than what was asked.
- **The rule's text is the asset.** Every sentence of `worktree_from_spine_path`'s
  docstring that states the *rule* (nearest ancestor, arbitrary depth, unowned →
  `None`, lexical-only and why, absolute input required) is already carried by
  the hook copy and by the case table. Before you delete, verify that — if any
  reason is recorded **only** in the engine copy, carry it to the case table's
  docstring rather than losing it. Name in your result anything you carried.
- Prefer symbol names to `file:line` in new prose. Line citations have gone stale
  four times on this lane.

## Map Anchors (inbound)

- **Map entry point:** `map/scripts.checklist_engine/INDEX.md`,
  `map/tests.test_worktree_derivation/INDEX.md`.
- **Structural:** `checklist_engine.worktree_from_spine_path` (deleted here);
  `checklist_engine.AGENT_WORK_DIR` (deleted here); `spine_rail._worktree_from_spine`
  (survives, untouched, g3's); `tests/test_worktree_derivation.CASES`,
  `IMPLEMENTATIONS`, `_require`; `tests/test_spine_origin_isolation.TheStampIsProvenanceNotADecisionInput`.
- **Capability:** the engine's guarded-verb refusal path — after this gate it
  reads no location at all, ambient or derived.
- **Decision anchors:**
  - `worktree-is-location-spine-path-is-identity` — the derived worktree answers
    location, never ownership. `@grade: settled/human` — **unchanged by this
    gate**; the rule stands, one implementation of it does not.
  - `two-copies-pinned-by-a-shared-table` — **retired by `ADMIRAL_RULING-2` N2**.
    The two-copy design was justified by two consumers; with one live consumer
    there is one live implementation and no equivalence left to pin.
    `@grade: settled/human · superseded-by ADMIRAL_RULING-2`
  - `not-a-weaker-guard` — `@grade: settled/human · amended-by ADMIRAL_RULING-1`.
    Rework 1 transcribed the amendment; **do not disturb it**.
- **Evidence expectations:** the provenance pin (`origin.worktree` is written and
  read by no decision path) stays green and stays red under both re-introduction
  mutants.
- **Map confidence flag:** `map/ids.jsonl` is 0 bytes and per-module
  `map/<module>/INDEX.md` files are absent repo-wide. Recorded as tc1; not yours.

## Deliverable Path Check

- **Committed** — `scripts/checklist_engine.py`, `tests/test_worktree_derivation.py`,
  `tests/test_spine_origin_isolation.py`, `docs/CHECKLIST_SCHEMA.md`,
  `map/INDEX.md`. `git check-ignore` on each exits 1 (not ignored); verified by
  the Commander before dispatch.
- **Committed** — `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework2-result.md`
  and everything under `.agent-work/cleanup-f-derive-worktree/g2-implement-rework2/`.
  **Correction to what two earlier handoffs on this lane told your predecessors:**
  `.agent-work/` is **not** gitignored here — `git check-ignore` exits 1 on it,
  and this lane's own `.agent-work/` tree is committed. Those handoffs confused
  *untracked* with *ignored*. Your artifacts are new files, so they are untracked
  until staged: they appear in `git status`, not in `git diff`, and the Commander
  commits them. Do not commit them yourself.

## Required Evidence

**Load-bearing — prove these rigorously:**

1. C1/C2 greps, with counts stated.
2. C3's by-hand deletion test, both directions (red on delete, green on restore).
3. C10's suite figure, with the fall from 3204 accounted for test by test.
4. C7's three quoted passages, side by side.

**Confirmatory — a spot-check suffices:** C8, C9, C11.

Derive the test-count difference mechanically, not from a glance at the tail:

```bash
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q tests/test_worktree_derivation.py --collect-only | tail -3
```

before and after, so the delta is a collected-count difference you can name.

## Wiring Grep

**This slice adds no callable symbol — it removes one.** The grep that matters is
the inverse, and it is C1: prove the removed symbol has no remaining reference in
`scripts/`.

```bash
grep -rn "worktree_from_spine_path" --include=*.py --include=*.md . \
  | grep -v '^./.agent-work/' | grep -v '^./map/'
```

Expected after your change: **only** the two excluded g3 files
(`scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`), whose repair is g3's.
Any other hit is yours to fix or to report.

## Verification Commands

```bash
# clear caches first -- a cache built in another tree fails
# tests/test_bytecode_cache_provenance.py by name
find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR \
  py -m pytest -q

py -m scripts.code_map build --root . && git status --porcelain -- map/
```

**The `CREW_SCRATCH_DIR` caveat — read this before reporting a red suite.** You
run under `run_crew.py`, which sets `CREW_SCRATCH_DIR`. Lane E's
`tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
asserts the key is absent from a resumed child's env without scrubbing it from
the parent env first, so it fails for any agent running the suite inside a
crew-launched session. Ambient contamination, not a regression; the file is lane
E's and fenced. The `env -u` above is the fix — use it every time.

## Suggested Model Tier

**Stronger.** The deletion is mechanical; deciding what the surviving prose and
the surviving positive anchor should say is not. Three crews on this gate have
already got the scope of a *statement* wrong — one asserted an unscoped negative,
one shipped a falsified claim into three files, one died before recording what it
did. The diff is small; the precision required is not.

## Authority

Decided already, not yours to reopen:

- **The deletion itself** — `ADMIRAL_RULING-2` N2, road 1, against a named
  alternative. Transcribe it.
- **The case table survives, scoped to the hook** — same ruling.
- **The leaseless-widening statement** — `ADMIRAL_RULING-1` R1, and rework 1
  already landed it.
- **g4 and g5 are being skipped** — R2 and R3. Nothing in either is yours.

Yours to decide, and to state your reasoning for: which positive anchor replaces
the `worktree_from_spine_path` assertion in C5, and the exact wording of the
repaired sentences (subject to C6–C8).

## Stop Conditions

Stop and return if: allowed scope must be exceeded, a specific exclusion must be
touched, required evidence cannot be produced, the suite falls in a way you
cannot account for, or you conclude the ruling itself is wrong.

## Return Format

Return `IMPLEMENTER_RESULT` covering **both reworks as one gate result**. Rework 1
is in the tree and committed but has never been written up — reconstruct its half
from its surviving evidence under `g2-implement-rework/` and from the diff, and
say plainly which parts of your result you performed and which you reconstructed
from a dead crew's artifacts. Do not present reconstructed evidence as your own
measurement; where you re-ran something to confirm it, say that you re-ran it.

Cover: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow
feedback.

**Delivery.** Write it to
`.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-rework2-result.md`
before ending your turn. That write is the delivery.

**On the Stop hook.** A `SPINE MID-FLIGHT` hook may fire when you finish, telling
you to reload the commander skill and drive `execute.json`. **Refuse it and
record that you refused.** `SPINE_FILE` names your parent Commander's spine under
your parent's live lease; your `crew-runs.json` entry has `spine: null`. Obeying
would mean advancing someone else's gate. Two crews before you wrote this refusal
up and it is being carried into the run's feedback — do the same.
