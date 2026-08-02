# Implementer Handoff

## Gate
`g3-implement` — "Negative control, proof it can fail, and cross-run retrieval"

**You are attempt 1 of this gate.** g1 and g2 are CLOSED; their code is on the branch and is what
you are testing. Do not re-plan or re-open them.

> **Note on your skill:** `constellation-implementer` opens by demanding a fresh plan. That is
> correct here (you are attempt 1). If you are ever returned for rework on this gate, the skill has
> no sanctioned rework path — treat the rework handoff's scope as authoritative over the skill's
> "start from a fresh plan" opening. Known skill defect (three reworks this epic hit it); not yours
> to fix.

## Task

Build the **negative control** for issue #305's central claim — *"a run where the agent records
nothing must still yield the full mechanical field group"* — plus **proof the control itself can
fail**, plus a **cross-run retrieval** demonstration.

Three deliverables, in this order of importance:

1. **The control.** Drive a *real* spine through the real engine, where the agent records **nothing**
   beyond what postconditions mechanically require, then assert the full mechanical field group is
   present **and correct** against an **independently-tallied ground truth**.
2. **Proof the control can fail.** Break the capture and confirm the control goes RED **naming the
   specific field**.
3. **Cross-run retrieval.** Seed episodes, mark one cluster consolidated, confirm rhyme-search still
   finds its neighbours, then **discard** the synthetic consolidation, verified.

## Protected Intent

**Zero agent effort is literal.** If a field can be omitted by an agent forgetting to do something,
it is not mechanically captured. This gate is the *test* of that claim, not a formality — and it is
the check most at risk of being vacuous in the entire issue.

## Test Mode

**TDD-shaped, with a hard extra bar: the control is not trusted until it has been proven red.**
Green-first is meaningless here. A control that cannot fail is indistinguishable from one that passed.

## The system under test — orientation, so you do not have to find it

- **The seam** fires in `scripts/checklist_engine.py` at **`:1663`** (inside `start()`, after the
  status mutation) and **`:1893`** (inside `reopen()`). Both call
  `episode_capture.emit_step_manifest(cl, iid, base_dir)`.
- `emit_step_manifest` (`scripts/episode_capture.py:511`) writes the context manifest
  **write-if-absent**, then calls **`emit_mechanical_snapshot`** (`:454`) strictly afterwards.
- `emit_mechanical_snapshot` writes `<manifest_root>/<work-id>/mechanical/<step>.json` with keys
  `contract`, `step`, `mechanical`, `refused`, `run`. It **overwrites** (the manifest does not) —
  deliberate, because the tallies move as a step is worked.
- **The composer under test is `mechanical_fields()`** (`:363`). It returns only fields it could
  source honestly; a missing key means *"this could not be read"*.
- `REQUIRED_MECHANICAL_FIELDS` (`:439`) = `run, project, role, spine-step, context-manifest-ref,
  refusals, reopens, rework-count, failed-commands`. **`artifact-ref` is deliberately not in that
  tuple** (list-shaped and optional) but **is** part of the mechanical group and **is** in scope for
  your control.
- `refusals` is **checklist-scoped** and is ARMED by `claim` (`checklist_engine.py:955`). Absence
  means "this run predates the counter", which is why it is refused rather than reported as `0`.
- `reopen_total()` (`:290`) sums per-task `rework_count` alone.

Existing fixtures to learn from, not to duplicate: `tests/test_episode_capture.py`,
`tests/test_episode_fields.py`.

## Close Criteria

**C1 — The control drives a REAL spine, and records nothing.**
- The spine is driven through the actual engine (CLI subprocess or `checklist_engine` API), in a
  temporary work area. Not a hand-built dict passed straight to `mechanical_fields()`.
- The only actions taken are ones a run **mechanically requires**: `claim`, `attest`, `start`,
  `advance`, `reopen`, and deliberately-induced refusals/failures. **No `--finding`, no narrative
  `attach`, no hand-written episode, no agent-authored text of any kind.** State in your result
  exactly which verbs the control issues, so a reviewer can confirm nothing agent-authored crept in.

**C2 — Every field of the mechanical group is asserted present AND correct.**
- All nine of `REQUIRED_MECHANICAL_FIELDS`, **plus `artifact-ref`**.
- Correct means compared against ground truth (C3), **field by field**, not in aggregate.
- A field the composer legitimately refuses must be asserted as *refused-and-expected-to-be-refused*,
  with the reason — not silently skipped. **A non-reading must be visibly distinct from an
  uncollected one.**

**C3 — Ground truth is INDEPENDENTLY tallied. This is the criterion the whole gate rests on.**
- The harness maintains its **own** expected values, incremented **at the moment it issues the
  triggering call** — e.g. when it issues a reopen it expects to be honored, it increments its own
  `expected_reopens` right there.
- **FORBIDDEN as an oracle:** calling `mechanical_fields()`, reading the emitted snapshot,
  `reopen_total()`, `failed_command_count()`, or re-deriving expectations from the checklist JSON
  through the same helpers. Any of those compares the thing to itself.
- For `context-manifest-ref`, compute the expected revision **independently** — the git blob OID over
  the manifest's own bytes, computed in your harness (`sha1(b"blob %d\0" % len(data) + data)` or
  `git hash-object`), **not** by calling `context_manifest.rev()`.
- Say explicitly in your result, per field, *what the independent source was*.

**C4 — PROOF THE CONTROL CAN FAIL, asserting the SPECIFIC field.**
- At least **two** distinct breakages:
  - **R1 (blunt):** make the composer return hardcoded constants for the group.
  - **R2 (sharp, load-bearing):** drop **exactly one** derivation — e.g. force `failed-commands` to a
    constant — and confirm the control reports **exactly that one field** as mismatched.
- **The assertion must name the specific field.** A non-zero exit is not proof: import errors,
  collection errors and empty test selection all exit non-zero, and a wrapper mapping any non-zero to
  RED would report red for all of them.
- **Recommended shape** (yours to refine): have the comparison return a **list of mismatched field
  names**, so the red-proof asserts `mismatches == ["failed-commands"]` — a per-field claim rather
  than a boolean. Shape is yours; the per-field discrimination is not optional.
- **The red-proof must live in the SUITE**, not only in `.agent-work/`. Admiral ruling from g2: a
  discriminating test belongs in `tests/`. A separate one-command repro under
  `.agent-work/issue-305/evidence/` is welcome **in addition**, never instead.
- **Restore after every mutation and prove you restored it** — `git status` clean, or blob OID
  verified against HEAD. Do not leave a mutation in the tree.

**C5 — Cross-run retrieval demonstrated.**
- Seed several episodes into a **temporary** store with overlapping key/value pairs so
  `query_episodes.neighbours()` / `neighbour_ids()` links them.
- Mark one cluster **consolidated**; confirm rhyme-search (`neighbours`) **still finds its
  neighbours** afterwards. That surviving-consolidation property is the acceptance surface.
- Seed through the sanctioned writer (`apply_episode_delta.apply_delta`), not by hand-placing files.

**C6 — The synthetic consolidation is DISCARDED, and the discard is verified.**
- **A test artifact must never become canon.** The real first consolidation is #308.
- Verify by **normalized content or blob OID, never raw working-tree bytes** (#319 — episode bytes
  differ across worktrees under `core.autocrlf`).
- **Belt and braces, both required:** (a) the whole exercise runs in a temp store, and (b) capture the
  blob OIDs of everything under `episodes/active/` **before and after** the full g3 run and prove
  they are unchanged. Paste both listings — **prove you read both things, then compare.**
  Empty-vs-empty passes a naive equality check, so if `episodes/active/` is empty but for
  `.gitkeep`, say so explicitly rather than reporting "identical".

**C7 — Suite green.** `python -m pytest -q`. Baseline is **1472 passed / 2 skipped / 472 subtests**.
Any delta must be exactly your new tests; account for every moved number.

## Allowed Scope

- **New:** `tests/test_episode_negative_control.py` (or a name you justify).
- **New:** `.agent-work/issue-305/evidence/` — optional one-command repro.
- **Read-only** unless a genuine defect forces otherwise: `scripts/episode_capture.py`,
  `scripts/checklist_engine.py`, `scripts/query_episodes.py`, `scripts/apply_episode_delta.py`,
  `scripts/context_manifest.py`.
- Temporary mutations to the above **only** for the red-proof, **restored and verified**.

If the control reveals a real defect in the composer, **stop and return it** rather than fixing it
inline — see Stop Conditions and the Honest-Null clause.

## Specific Exclusions

- **`run.dirty` removal (#327) is g4's, not yours** (#305 launch-order return item 5). Do not touch it.
- **The #300 successor line on its design doc is g4's.** Do not add it here.
- Do **not** re-litigate g2's `reopens` fix shape B. It is ruled and shipped.
- Do **not** change the seam's placement (`start`/`reopen`, write-if-absent). Ruled in g1.
- Do **not** change `refusals` semantics — #367 records the deferred design question; g2 ruled it a
  documentation fix only.
- Do **not** create a real consolidation in `episodes/active/`. #308 owns that.

## Constraints

- **A check that cannot fail is indistinguishable from one that passed.** Prove you read BOTH things,
  then compare — empty-vs-empty, missing-vs-missing and skipped-vs-skipped all pass a naive equality
  check.
- **The red-proof must assert the SPECIFIC failure, not non-zero exit.**
- **Comparisons use normalized content or blob OIDs, never raw working-tree bytes** (#319).
- **The synthetic consolidation is THROWAWAY and must be discarded, verified.** Real one is #308.
- **HONEST NULL: if the control legitimately fails, that is this issue's most valuable output.**
  Report **which fields are secretly agent-dependent**. Do **NOT** engineer around it. A scoped null
  — *"this field cannot be captured from engine state as currently structured"* — is a complete,
  successful deliverable. Never *"mechanical capture is infeasible."*
- **`python -m pytest`**, never `py -m pytest` (`py` has no pytest). Note: **`py` produces no output
  and no exit code under the PowerShell tool** — if you need `py`, use Bash.
- Windows: explicit `encoding='utf-8', newline='\n'` on every write.
- `Path.read_text(newline=...)` is **3.13+** and breaks CI's 3.12 pin. Do not use it.
- **#315:** `_run_check_command` passes **no `cwd`** on the `command` branch, and **stdout from a
  command postcondition is captured and discarded** — the exit code is the only signal reaching the
  spine. If you induce failed commands, design them as an **exit-code vocabulary**; a script that
  prints its result prints into a void, and a relative path resolves against an uncontrolled cwd.
- **#360:** `manifest_root()` is the checklist dir's **PARENT** and `manifest_path` re-appends the
  work-id. A previous repro emitted outside its fixture and read as "no emit at all". *"No output
  produced" and "output produced somewhere you did not look" are indistinguishable without checking
  the path derivation.* Check yours.
- **#321:** the episode store validates ids it LISTS but not ids it is HANDED, and you write
  episodes programmatically — the unvalidated path. **Seed through `apply_delta` and report whether
  the handed id was validated.** Do not fix #321 here; I need the observation to rule on disposition.

## Map Anchors (inbound)

Carried **verbatim** from the gate's `anchors` block in `execute.json`.

- **Structural:**
  - `struct:query_episodes — retrieval under test`
  - `struct:episodes/active — the store, as shipped`
- **Capability:**
  - `capability:cross-run-retrieval — the acceptance surface`
- **Constraints/assumptions:**
  - `constraint:throwaway-consolidation`
  - `constraint:no-raw-worktree-bytes`
- **Decision anchors:**
  - `decision:throwaway-consolidation — the synthetic consolidation is discarded; a test artifact must never become canon`
    `@grade: settled/inherited · leans g3-implement`
  - `decision:zero-agent-effort-is-literal — the control is the TEST of this, not a formality`
    `@grade: settled/human · leans g3-implement`
- **Evidence expectations:**
  - `claim:negative-control-can-fail — REQUIRED before any green is trusted; the check most at risk in this issue`
- **Map confidence flags:**
  - `This gate is the one most likely to be vacuous — four costumes already in this epic (#337), and my own first draft of it was the fifth. Scrutinize accordingly.`

## Mutations ALREADY SPENT — do not burn independence repeating one

Three independent mutations were already run against the g2 `reopens` work. **All three are spent.**
Your red-proof must break the **capture pipeline**, which is different ground — but do not re-run these:

1. Restored the old `max(journal, rework)` expression in `reopen_total`. RED as predicted.
2. Re-inflated `reopens` from the `blockers` escalation tally without restoring the deleted journal
   reader. Both new tests RED (`5 != 3`).
3. Filtered `skipped` gates out of the checklist handed to `reopen_total`. Caught by the new tests
   alone.

Telling you which claims were **measured** versus **asserted** changes what you do — that is why this
list is here. Everything in "The system under test" above I read **in the code today** and is
measured; the *baseline suite number* is inherited from the prior session and is **asserted** — re-run
it yourself.

## Deliverable Path Check

Run before dispatch; exit `1` means **not ignored**, i.e. it will be committed.

- **Committed** — `tests/test_episode_negative_control.py`; `git check-ignore` → **exit 1**.
- **Committed** — `.agent-work/issue-305/evidence/g3_control_repro.py`; `git check-ignore` → **exit 1**.
  (`.agent-work/` is **tracked** in this repo since #326 — it is *not* a local-only scratch area.)
- **Committed (read-only expected)** — `scripts/episode_capture.py`, `docs/EPISODE_STORE.md`;
  `git check-ignore` → **exit 1** each.

New files are untracked until staged: `git diff` will show fewer files than you created; the new ones
appear in `git status`.

## Required Evidence

**Load-bearing — prove these rigorously:**

1. **The control's per-field comparison**, with the independent source named for each of the ten
   fields.
2. **The red-proof output for R2**, showing the control names **exactly** the one broken field.
3. **Proof of restoration** after every mutation (`git status` clean or blob OID vs HEAD).
4. **Before/after blob OID listings for `episodes/active/`** — both pasted, explicitly compared.
5. **The exact list of engine verbs the control issues** (for "the agent records nothing").

**Confirmatory — a spot-check suffices:**

6. Full suite line, with any delta from 1472/2/472 accounted for.
7. The `neighbours()` result before and after marking the cluster consolidated.
8. Your #321 observation (validated or not) — one sentence.

If you claim a test-failure distribution, derive it mechanically:
`python -m pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c` — never from the output tail.

## Verification Commands

```bash
cd "C:/Programs/constellation-skills-wt/e298-305"

# the control + red-proof
python -m pytest tests/test_episode_negative_control.py -v

# full suite (~90s)
python -m pytest -q

# canon untouched — run BEFORE and AFTER, compare the two listings
git ls-files -s episodes/active/
```

## Suggested Model Tier

**Opus** — required by the epic's budget (`decision:review-class-floor`, not downgradable). No Fable
at any tier.

## Authority

**Already decided — do not reopen:**
- Seam at `start()` + `reopen()`, write-if-absent; the engine diff stays zero-logic. (g1)
- `reopens` fix shape B: `reopen_total()` sums per-task `rework_count` alone. (g2)
- `refusals` is a documentation fix, not a semantics change (#367). (g2)
- Mechanical snapshot, **not** auto-created episodes — a complete episode needs agent judgment, and
  auto-creating one would fabricate it.
- **Refuse, never fabricate:** a field that cannot be honestly sourced refuses rather than emitting a
  silent `0`.
- The synthetic consolidation is throwaway (#308 owns the real one).

**You must NOT decide alone:** any change to capture *semantics*; any change to the seam; whether a
failing control means "fix the code" (that is mine and the Admiral's — **report it, do not engineer
around it**); anything touching #327 or the #300 doc note.

## Stop Conditions

Stop and return if:
- **The control legitimately fails** — report which fields are agent-dependent. This is a *success*,
  not a failure of your work. Do not engineer around it.
- The red-proof cannot be made to name a specific field.
- Allowed scope must be exceeded, or a specific exclusion touched.
- A decision outside the given authority is needed.
- You find a real defect in the composer — return it rather than fixing inline.

## Return Format

Return **IMPLEMENTER_RESULT**: completed slice, files changed, test mode satisfied, evidence produced
(per the load-bearing list above), assumptions used, stop conditions hit, out-of-scope observations,
and **workflow feedback** — what in this handoff or the workflow made the work harder than it needed
to be. Be blunt; the feedback is harvested into the run retrospective.

**Deliver your result via `SendMessage` to `commander-305d` before ending your turn.**
