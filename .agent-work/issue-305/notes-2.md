# commander-305e — working notes 2: HANDOFF STATE at the g3/g4 boundary

**Stopping at a clean gate boundary with runway left, per the launch order.** All of g3 is
complete. g4 is untouched and is a real code change, not a tail.

## Where the engine is — ask it, don't trust this file

```
cd C:/Programs/constellation-skills-wt/e298-305
python C:/Programs/constellation-skills/scripts/checklist_engine.py \
  --file .agent-work/issue-305/execute.json current
```

At handoff: `g4-implement [pending]`, **3 steps from done** on this child plan
(`g4-implement` -> `g4-review` -> `g4-integrate`). The lease is held by session
`commander-305e`; the successor should `claim --force` (`engine_session` behaviour under
child gate plans is #357 — expect it, it is not corruption).

Branch `epic-298/305`, worktree clean apart from engine state. **Nothing is pushed and no
PR exists.**

## Commits I added

| commit | what |
|---|---|
| `283175b` | census fix — `--claimed-by` counted, `PARENT_ROLE` declared, census asserts exactly two constants |
| `8bff6a8` | `g3-implement` closed — 305d's uningested gate |
| `83becc8` | docstring cut back to what the census actually checks (reviewer's F2) |
| `586da84` | `g3-review` + `g3-integrate` closed |

Suite at handoff: **1487 passed, 2 skipped, 472 subtests**. `g3-integrate.c1` is
engine-checked and its `command-output` evidence records `exit: 0` — the engine ran
`python -m pytest tests/ -q` itself.

## What is LEFT

1. **g4** — remove `run.dirty` from `scripts/context_manifest.py` (#327). Removal, not
   repair, per a settled/human ruling. Drop the parameter from `run_facts()`, stop
   `build_manifest()` reading `state.get('dirty')`, update ~25 assertion sites in
   `tests/test_context_manifest.py`, correct the module docstring prose. `CONTENT_KEYS` is
   unchanged — `dirty` was never content. Also add the **#300 successor line** to #300's
   shipped design doc. Close #327 with the removal.
2. **The parent spine** (`.agent-work/issue-305/spine.json`) — reconcile -> triage ->
   review -> feedback -> archive. Untouched by me.
3. **The PR.** Not opened. **Do NOT merge** — declare the branch FINAL or PENDING
   explicitly (#338) and hand the merge decision to the Admiral.

## Three things that MUST reach the PR body

1. **Return item 4's bound, verbatim, as a decay guard.** Severing the seam at its call
   site turns the control **RED 8/13**, so #300's AC1 is falsifiable — **but #300's own
   tests stay fully green and never reach the call site (measured reached-count 0, not
   inferred).** The falsifiability lives in **#305's control**, not in #300's tests.
   **Someone tidying away a control that looks redundant is the most likely way this
   mechanism dies quietly. Say that.**
2. **The corrected claim.** The ratified sentence in the launch order does **not** survive
   verification, and neither did my first correction. Write this instead:

   > The control supplies the engine no agent-authored **narrative**. Every string it
   > hands over is a fixed identifier declared in the test module — the work id, the temp
   > repo's directory name, the role, the condition ids, and one `reopen --reason` — and
   > nothing composed at issue time. The mechanical fields that echo those identifiers
   > (`run`, `project`, `role`) echo what the run is *made of*, not prose written *about*
   > it. What the argv census mechanically checks is narrower than that claim, and the
   > docstring says so.

   **Do not let a later summary re-broaden this.** It has now been wrong three times in
   three different ways, each caught only by a mutation.
3. **`g3-integrate.c2` and `g2-integrate.c2` were both waived `--force`** as the #371
   gate-plan defect. The real verdict, `APPROVE-WITH-FOLLOWUPS` with no blockers, is on the
   record in both cases. **No APPROVE was ever fabricated.** Expect the same wedge at
   `g4-integrate.c2`.

## Open triage candidates (recorded in the engine as tc1/tc2/tc3)

- **tc1 / F1** — the independence guard's static layer (b) is defeated by an **aliased
  import** (`from episode_capture import reopen_total as _alias`), the exact case its own
  docstring names as what it covers. Measured GREEN by the g3 reviewer.
- **tc2 / F3** — the fixture stages **one** `artifact-ref` path, so the multi-element
  constraint is unmet and mutation M8 (`out[:1]`) passes. Staging a second turns M8 red.
  Cheapest remaining fix in the file.
- **tc3** — crew doctrine: the spent-mutation rule should read *"not a repeat under the
  same conditions"*; and *"a battery whose failures are exceptions rather than assertions
  is broken, not a result"*.

Neither F1 nor F3 leaves a conclusion unsupported — that is the reviewer's judgment and I
accepted it. **They are real holes in a control whose whole purpose is to have none**, so
they should be filed, not dropped.

## Method warnings that cost me real time — inherit these

- **#319 is live and bit me three separate ways.** The worktree file is **CRLF on all 1119
  lines**; `git show HEAD:<path>` returns **LF**. A pattern built for one base silently
  matches **zero** sites in the other and reads as *"mutation applied, still green"* — a
  false negative-control result manufactured by the tooling. Derive EOL **per base**.
  `git hash-object` compares true across that boundary because its clean filter
  normalises, which is exactly why blob OID is the instrument and raw bytes are not.
- **Put the restore in a `finally:`.** Two of my scripts died before restoring — one on a
  cp1252 `UnicodeEncodeError` printing pytest output, one on a **broken pipe from `| head`**
  (the pipe kills the script mid-battery). Each left the tree mutated. OID-check the tree
  after **every** battery, not after the last one.
- **`python`, never `py`.** `py` is 3.12.13 with no pytest; it no-ops and reads green.
- The engine's `current` verb **rejects `--session-id`** while every other verb accepts it.
  One wasted invocation per scripted drive.
