# Review Result — rework 2

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review` — issue #300 (epic-298), re-review after rework 2, commit `0b15d5b`
(`+449 / −99` over four files).
Survey re-driven: `.agent-work/300/g1-review/review.json`, session
`reviewer-300-g1-rework2` (`r2`, `r3`, `r4`, `r6` re-recorded; consolidated
`verdict=APPROVE`, findings=0).

## Result

# `APPROVE`

**0 blockers · 0 major · 0 minor.** Two new triage candidates (`tc7`, `tc8`).

Both panel blockers are genuinely fixed. I verified this against the real acceptance
test and against `HEAD~1`, rather than against the crew's mutation table or the
in-suite harness — and I found one thing about *why* the fix works that neither the
panel nor the implementer stated, which is worth carrying forward.

---

## First, the gap in my own round-1 work

The panel is right, and my round-1 harness could not have caught this. I mutated
`build_manifest`, `rows` and `rev` — all of which change the **data**. An
environment-dependent `encode()` changes only the **bytes**, and the parent
re-encoded both children's parsed artifacts before comparing, so every byte-level
defect was laundered before my mutations could reach it. My "3/3 mutants caught"
was true and also blind to an entire axis. Recording it plainly because the lesson
generalises: *a mutation set inherits the blind spot of the comparison it is run
through.*

---

## Blocker 1 — the acceptance test now compares what the environments wrote

Verified by re-running the mutation **myself**, against
`DeterministicAcrossEnvironments` (the real acceptance test — not
`TheComparisonHasTeeth`), at both commits, with the producer mutated via
`shutil.copyfile` interception so nothing on disk was edited:

```
PART 2 -- at HEAD~1 (before rework 2)
*** SURVIVED ***  D1 environment-dependent encode() [indent]   ran=6  failing=none
*** SURVIVED ***  D3 content() promotes a /run fact            ran=6  failing=none

PART 1 -- at HEAD (rework 2)
   CAUGHT  D1 environment-dependent encode() [indent]
           failing=['test_content_is_byte_identical_excluding_exactly_the_run_subtree']
   CAUGHT  D3 content() promotes a /run fact
           failing=[…byte-identity…, …no_absolute_path_leaks… ×2, …compared_bytes_are_the_ones_the_children_wrote… ×2]
 survived  baseline (unmutated)                                ran=7  failing=none
```

**The crew's table is accurate.** Survival at `HEAD~1` and death at `HEAD` are both
measured here, so the fix is doing the work rather than the harness having changed.

I added a variant of my own the panel did not run — **D2, an encoder that changes
key *order* rather than indentation** (`sort_keys` under one locale). Same object,
different bytes, and no indentation tell. Also caught. That matters because it is
the subtler shape of the same defect and it confirms the fix is byte-comparison, not
a formatting-specific patch.

The two supporting moves are real fixes, not garnish. Per-child `cwd=` matters
because `cwd` is the single environment fact `run_facts()` actually reads — with both
children inheriting pytest's cwd, the one live variable was pinned constant, and D3's
leak would have been invisible even after the byte-comparison fix.

## Blocker 2 — `/run` really is the exclusion set, and the two halves are complementary

**This is the part worth reading.** I mutated the leak in both spellings:

| my mutation | caught by |
|---|---|
| **D3** `content()` promotes `run.host.cwd` | the byte comparison (+4 others) |
| **D4** envelope grows a varying key, **not** added to `CONTENT_KEYS` | **only** the bidirectional set assertion |
| **D5** envelope grows a varying key, **also** admitted to `CONTENT_KEYS` | the byte comparison |

D4 is the interesting one. When a new varying key appears in the envelope but not in
`CONTENT_KEYS`, the allow-list **correctly drops it** — so the compared bytes are
identical and the byte comparison sees nothing at all. The only thing that can tell
you the key exists is `set(manifest) == set(content(manifest)) | {"run"}`, and only
in the direction the old one-directional `set(m) - set(content(m)) == {"run"}` was
structurally blind to.

So the allow-list and the bidirectionality are **complementary, not redundant**: the
allow-list makes a new key non-content by default, and the bidirectional assertion is
the only thing that can see the key at all. **Either one alone leaves a hole.** The
implementer shipped both and the module docstring explains the allow-list; nothing in
either write-up says the assertion is what covers the allow-list's own blind spot.
Worth stating so a future simplifier does not delete one as "covered by the other."

### Deny → admit dropped nothing legitimate

Checked, since the Commander asked. Old deny-spelling vs new admit-spelling over the
real Commander manifest and **9 real gated templates**:

```
real Commander manifest -> deny keys: ['contract','step','files']
                           admit keys: ['contract','step','files']
  byte-identical encodings: True
checked 9 real gated templates; deny-vs-admit differences: 0
envelope order vs CONTENT_KEYS order: ['contract','step','files'] == ['contract','step','files'] -> True
```

The order check is not decoration: `json.dumps` preserves dict order, so a
`CONTENT_KEYS` sequence that disagreed with the envelope's insertion order would have
silently changed the compared bytes. It agrees.

## `TheComparisonHasTeeth` is not passing for an incidental reason

The Commander's concern — a harness that always fails, or a control that is not really
unpoisoned, would be the same defect one level up — is the right question. Three probes:

```
T0 as shipped                              failing: none
T1 neuter the encoder poison (no-op)       -> test_an_environment_dependent_encoder_is_caught  RED
T2 neuter the varying-field poison (no-op) -> test_a_varying_field_placed_outside_run_is_caught RED
T3 poison the CONTROL path                 -> test_the_real_producer_is_byte_identical…        RED
```

T1/T2 prove the **poison** is what makes the bytes differ, not the harness. T3 proves
the control genuinely runs the unpoisoned producer. It discriminates in both
directions, which is exactly what a negative control has to do.

One honest limit, recorded as `tc8` rather than as a finding: the harness runs against
`ROOT` with no `INSTALL_SHIM` and no second checkout, so it projects **6 rows, all
`rev: null`**. Its control therefore proves the comparison discriminates, but never
exercises real file hashing — it would pass with `rev()` entirely broken. That is fine
for its job (proving the comparison can fail; both poisons work on null rows), and the
real-content property is covered by the acceptance test's own
`test_the_content_is_a_real_projection_not_an_empty_one`. The class docstring's claim
that it runs "the *same* two-child harness" is just looser than the code — same child
script, different tree.

## Supporting fixes — spot-checked, all real

- **`RealCheckoutSkew` is no longer vacuous.** Baseline green; neutering its tracked
  rows to absent paths — reproducing the exact old all-null condition — turns it
  **RED**. The determinism half now genuinely executes, which the panel correctly said
  it never had.
- **`rev()` untouched.** No diff hunk in `0b15d5b` touches the hash, and my 16-pattern
  hunt is unchanged: the same four documented divergences, **0 mismatches across all
  270 tracked files**.
- **Producer behaviour unchanged** across my 16 adversarial declarations (identical to
  rework 1; the drive-letter rejection now comes from the colon guard, as intended).
- **Six zero-caller seams deleted**, which closes my rework-1 speculative-generality
  flag. `build_manifest(step=)` going is a real strengthening: there is now no way at
  all to build a manifest for a step production never reaches, so "`active_id` is THE
  selector" is enforced by absence rather than by convention.

## Scope

`clean.` `docs/CHECKLIST_ENGINE_DESIGN.md` is now legitimately editable — g3 landed at
`5dbbaae`, so it is no longer another gate's file. The spine template,
`verify_skip_guard.py`, `ci.yml` and `checklist_engine.py` are untouched.

I verified the implementer's reported verification-command discrepancy rather than
accepting it: `docs/CHECKLIST_SCHEMA.md`'s two `agent-work` hits are pre-existing
production paths (`allow_globs`, and the Context Governor's gauge path), and
`git diff 75ee317~1..HEAD -- docs/CHECKLIST_SCHEMA.md` shows #300 added exactly **one**
line to that file — the `context_refs` task-table row, containing no such path.
Narrowing the grep and reporting rather than widening was the correct call.

## Verification re-run at the source

| command | result |
|---|---|
| `pytest` the three context test files | 77 passed, 77 subtests |
| `pytest tests/ -q --junitxml=…` | **1234 passed, 2 skipped**, 337 subtests |
| `verify_skip_guard.py junit-report.xml` | `2 skip(s), all match documented allow-tuples` — exit 0 |
| `verify_context_declaration.py …COMMANDER_SPINE.template.json` | `1 checklist(s) checked, 0 offenders` |
| `grep -rn agent-work` over the two files | clean (exit 1) |
| `git status --short` | empty — no stray artifacts |
| `rev` vs `git hash-object`, all tracked files | 0/270 mismatches |

## One thing I observed and chased down, so nobody else has to

A worktree entry vanished mid-review (5 → 4). I traced it before reporting: the
`298-301` **directory was already gone** (its work merged as PR #320 — `origin/main` is
now `195e893 feat(#301): episode record and durable store`), its branch was deleted
deliberately, and `git worktree prune` then cleaned up the stale administrative entry.
**Nothing was lost** — `bef88f7` is still a reachable commit object.

This does confirm critic **M12** is live (the determinism tests run `git worktree prune`
against the real repository, which here carries long-lived Admiral worktrees), but it
also narrows the risk usefully: `prune` only ever removes entries whose directory is
**already gone**, and it never touches branches or commits. The blast radius is
stale-entry cleanup, not data loss. Filed as `tc7` with that correction, because
"non-local blast radius" overstates it.

## Out-of-scope observations

- **`tc7`** — M12, restated accurately as above.
- **`tc8`** — `TheComparisonHasTeeth` projects all-null rows; its control never
  exercises real hashing, and its docstring says "the same harness" when it is a
  different tree.
- **`tc5`** (rework 1) — **not** closed, correctly out of scope, and now slightly worse:
  `test_context_determinism.py` gained a **third** copy of the child-launch loop in
  `TheComparisonHasTeeth`. Still an observation; the duplication is deliberate in
  service of a real guarantee, but three copies is where an extraction starts paying.
- **`tc6`** (rework 1) — closed by the simplicity pass, except the still-unreachable
  `ValueError`, which is harmless.
- `tc1`–`tc4` stand as previously ruled.
- The implementer's own four out-of-scope items (`_MANIFEST_CONTRACT_VERSION` as a
  self-referential oracle, `INSTALL_SHIM` untied to the installer, `produce()` writing
  to a directory named `None`) are all real and correctly deferred. I agree with each.

**Not raised, per the Commander's instruction:** that nothing in the system calls the
producer. It is a scope question floated to the Admiral and I have not treated its
absence as a defect of this rework.

## Workflow Feedback

- **Handoff gaps:** none for this dispatch — confirmed after review: the Commander's
  message named exactly which claims to re-derive rather than accept (the two blocker
  mutations), named the specific failure mode to hunt in the new harness (a control
  that is not really unpoisoned), named the one regression risk of the fix itself
  (deny→admit dropping something legitimate), and fenced off the one thing that was
  not mine to rule on. Every one of those was answerable with a command. This is the
  best-shaped re-review brief of the three rounds.
- **Context rediscovered:** that g3 had landed, which is what makes
  `docs/CHECKLIST_ENGINE_DESIGN.md` in-scope this round — the original handoff lists it
  as a specific exclusion and nothing in the rework brief says that expired. I had to
  read the commit log to be sure I was not looking at a scope violation. A rework brief
  that changes scope should say so.
- **Instructions improvised around:** nothing new. The survey-vs-gated verb mismatch
  (`advance`/`reopen` both gated-only; `record` is the survey verb for both recording
  and re-recording) bit again on this third pass — it is now the single most repeated
  friction across all three rounds and worth a one-line fix in the reviewer SKILL.
- **What would have made this easier:** the panel found two defects in the *test* that
  three rounds of my own attack did not, because I was mutating through the very
  comparison that was broken. The generalisable lesson — worth banking as a lesson, not
  just a finding — is that **a reviewer's mutation set inherits the blind spot of the
  comparison it runs through**, so at least one probe should attack the comparison
  itself rather than the code under it. `TheComparisonHasTeeth` is now that probe, made
  permanent, which is the right outcome.

## Return status
`complete`
