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

## Five things that MUST reach the PR body

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
4. **A red-proof against a revision that never ships proves nothing about what ships.**
   The rework's proofs ran against `49059be` and `fb9dfc2`; the shipped file is `667b5e4`.
   Admiral-elevated as a new member of the #345 pattern — *we reliably build the capability
   and unreliably wire the guarantee*: the proof existed, the proof was not attached to the
   thing. Filed by the Admiral; **it belongs in the PR body, not only in the issue.**
5. **An asserted property that was never attacked is a claim, not a guarantee.** The
   closed-world census was asserted and well documented by the rework and **never attacked**
   until V2 (`attest --evidence`, the exact shape a blacklist misses). Admiral-elevated as
   distinct from the costume family, and wanted in the PR body **alongside the decay guard**.

## Inherited-brief defects — six of the Admiral's claims failed against the tree this epic

Recorded because the Admiral is collecting them for the closeout audit, and because the
pattern is more useful than the list: **the Admiral reasons about what happened; the tree
records what is in force. Only one of those is state.**

- **Ruling 2's ratified sentence was false** (`--claimed-by`), and so was my correction
  (`--cond`). Three narrowings, three misses, each caught only by a mutation. The
  Admiral's own diagnosis, which is the reusable part: **every narrowing inspected the
  GUARD and asked "what does this fail to catch?" — nobody inspected the MECHANICAL FIELDS
  and asked "where does each one come from?"**, which answers it immediately, because
  `role`'s declared source is written in plain English at line 537. We kept auditing the
  detector instead of the thing being detected.
- **"305d received APPROVE-WITH-FOLLOWUPS and reopened rather than integrating"** — true as
  narrative, but it implied a review that still stood. The reopen **cascade-reset
  `g3-review` to `pending`**, so attempt 1's verdict was history, not the review of record.
- **"Re-prove V4 goes RED after the fix"** — see the note below; V4 cannot go red after the
  fix by design, and the Admiral ratified the reasoning for that in the same message.

## Also filed by the Admiral, and part of this issue's output rather than side debris

**#381** and the **#337 comment**. The successor should know the red-proof-revision gap was
found here, because the same discipline that found it is what g4 needs.

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

## What shape did the rework's sweep look for? (Admiral's question, answered)

The rework's "no third vacuous guard: NOT found" section states its own criterion: it swept
every remaining assertion **against "can this fail?"** — and for each one it named the input
that would turn it red (routes through `compare_fields` with live red-proofs; guards
non-vacuity first; `pytest.raises` on each path; asserts both a populated and an empty
result; asserts the retired member from both directions).

**On its own criterion the sweep was correct and complete.** That is the important part.
`test_control_records_nothing_agent_authored` **passes** that criterion — it can fail, and
M1/V1 prove it. The sweep was hunting costume eight and nine, whose defining property is
*cannot fail under any input*.

**The corollary's shape is a different property**: not *can it fail?* but **does what it
checks cover what it claims?** A guard can be fully falsifiable and still be scoped to less
than its docstring asserts — which is exactly the `--claimed-by` gap, and then the `--cond`
gap after it. A "can this fail?" sweep is **structurally blind** to it, because the answer
is yes in both the healthy and the defective case.

**So: the sweep holds, and it was searching for the wrong shape.** Those are compatible.
The re-sweep that finds this class asks, per assertion: *enumerate what the docstring
claims, enumerate what the code checks, and name the difference.* Applied to the mechanical
fields rather than to the guards, that question is answered by reading — no mutation needed.

## The V4 re-prove instruction — it cannot be carried out, and should not be

The Admiral asked me to **"re-prove V4 goes RED after the fix."** **It does not, by design,
and the same message ratifies the reasoning for why it must not.**

V4 replaced the fixture's role constant with a hand-written sentence. After the fix the
fixture reads `role=PARENT_ROLE` and the census asserts
`("claim", "--claimed-by", PARENT_ROLE)` — so mutating `PARENT_ROLE` moves **both sides
together** and stays green. Making it red would require a guard that fires when a role
string "looks like prose", which is the unfalsifiable theatre the Admiral explicitly called
*"the best judgement call in this exchange"* and ratified in the same breath.

**The correct discriminating proof is V5, and it is done:** the same mutation (the harness
*composes* `--claimed-by` at issue time) run against both trees, census test isolated —
**pre-fix `1 passed`, post-fix `1 failed`** naming the composed string. That is a genuine
before/after; V4 post-fix would only ever have been a tautology.

**Nothing was skipped here.** The instruction and its own ratification were inconsistent,
and this is the resolution.

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
