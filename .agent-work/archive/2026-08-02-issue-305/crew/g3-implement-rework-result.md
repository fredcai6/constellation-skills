# IMPLEMENTER_RESULT — g3-implement, ATTEMPT 2 (REWORK)

**Status:** COMPLETE. Three fixes landed, both required red-proofs reproduced and shown RED with
their assertion text, restoration proven by blob OID, suite green with every moved number accounted
for. **No third vacuous guard found** — the sweep and its reasoning are recorded below.

**Files changed:** `tests/test_episode_negative_control.py` only.
**Files NOT changed:** nothing under `scripts/`. Both red-proofs were confined to the test file, so
the `checklist_engine.py` safety-classifier workaround (`sitecustomize.py` / in-process monkeypatch)
was never needed.

**Engine plan driven:** `.agent-work/issue-305/crew/g3-implement-rework-plan.json`
(`issue-305-g3-implement-rework`, session `impl-305-g3-rework-2`), five items, all `complete`,
`DONE: no open items` before release.

---

## FIX 1 — `test_control_records_nothing_agent_authored` can now fail

### What changed

1. `_ControlRun` now records the **full argv** of every issued call (`self.calls`), not just
   `argv[0]`. Every claim this control makes about what it did *not* record is a claim about flags,
   and a flag it never wrote down is a flag no assertion can reach.
2. Three new module-level declarations:
   - `ALLOWED_FLAGS` — **closed-world**, per verb. `claim`: `--session-id/--claimed-by/--worktree`;
     `start`: `--session-id`; `attest`: `--cond/--which/--session-id`; `advance`:
     `--mechanical/--session-id`; `reopen`: `--reason/--session-id`.
   - `AGENT_TEXT_FLAGS` — every engine flag whose value is free-text, read off `checklist_engine.py`'s
     argparse block (2301–2397) rather than guessed.
   - `_flag_pairs(argv)` — flag/value extraction, positionals dropped.
3. The guard is now a census over `run.calls` for **both** topologies, asserting positively:
   - every flag token is sanctioned **for its verb** (closed-world, so a text-bearing flag the engine
     grows tomorrow is caught without this file naming it — that is the difference from a blacklist,
     and it is exactly what M1 walked through);
   - every `advance` carries `--mechanical`;
   - no `attest` carries `--note`;
   - `advances >= 8`, so the census is asserted to have actually seen the calls it is about;
   - the free-text census comes back holding **exactly** `{("reopen", "--reason", "control")}`.

### The bounded exception, stated not hidden

The docstring now makes the honest claim: *the only agent-authored text in the entire control is ONE
fixed constant, `reopen --reason "control"`, and it feeds no mechanical field* — **not** "nothing
agent-authored was recorded".

I verified this at the world rather than inheriting it: `checklist_engine.py:1916/1918` calls
`_append_reopen_marker`, which appends `{"id", "gate", "reopen": true, "reason": <string>, "ts"}` to
`why_trail` (and again for a cascaded descendant). By contrast `advance --mechanical` reaches
`_append_why(cl, iid, why=None, mechanical=True)` at line 1714 — no agent text at all, which is the
`--mechanical` ruling holding up under inspection.

### RED-PROOF (M1) — assertion text inline

Mutation applied by script, **verified applied by blob OID before the run**:

```
PRE-MUTATION  OID: 49059be6fece6ae1b8c06bfcfacf08fa29b787c4
apply: 9 substitutions          ("--mechanical", *s  ->  "--why", "<prose>", *s   x5
                                 "--which","postconditions",*s -> + "--note","<prose>"  x4)
POST-MUTATION OID: 11a7a012ee7e9d9426aeb50634e9170ac5c31c88   <- changed, so it really applied
```

Result: `1 failed, 12 passed`. The failing assertion:

```
>       assert violations == [], violations
E       AssertionError: ["parent: attest carries un-sanctioned flag --note='a hand-written note
        recording what I thought about this attestation'", ...]
E       assert ["parent: att...arent')", ...] == []
E         Left contains 44 more items, first extra item: "parent: attest carries un-sanctioned flag
        --note='a hand-written note recording what I thought about this attestation'"
```

**44 violations, distribution derived from a command** (`... -o verbosity_assertions=2 | sed -n
'65,200p' | grep -oE ... | sort | uniq -c`, i.e. the Full-diff block only, so no item is double
counted):

| count | violation |
|---|---|
| 7 | `parent: advance carries un-sanctioned flag --why` |
| 7 | `parent: advance without --mechanical` |
| 4 | `parent: attest carries un-sanctioned flag --note` |
| 4 | `parent: attest carries --note` |
| 7 | `child: advance carries un-sanctioned flag --why` |
| 7 | `child: advance without --mechanical` |
| 4 | `child: attest carries un-sanctioned flag --note` |
| 4 | `child: attest carries --note` |

Both arms of the guard fire independently (the unknown-flag arm and the positive
`--mechanical`/`--note` arms), which is what makes it a regression test rather than a one-off.

**Restored:** OID back to `49059be6fece6ae1b8c06bfcfacf08fa29b787c4`, 13 passed.

### What else carries the conclusions this guard was propping up

Nothing was resting on it that is not independently carried. The claim "the mechanical group is
correct under zero agent effort" is carried by
`test_claimed_parent_topology_...` / `test_unclaimed_child_topology_...` /
`test_the_seam_emits_the_same_group_unasked` against the independently-tallied oracle, and their
falsifiability by R1–R4. What the old guard uniquely claimed — "the run was set up with no agent
input" — was carried by **nothing**, which is precisely the defect; it is now carried by the census.
Empirically the two are independent: under M1, with maximal agent prose in the run, **not one
mechanical field moved** (12 of 13 tests still passed).

---

## FIX 2 — `test_every_field_has_a_named_independent_source` can now fail

### Approach chosen: (a) behavioural, with (b) static-over-AST kept as a second layer

I took **(a)**, because it proves independence by *execution* and no indirection defeats it. I kept
**(b)** as well rather than instead, because (a) has exactly one hole: a name bound at **import
time** (`from episode_capture import reopen_total`) that no attribute patch can reach. (b) closes
that, and it is cheap.

Critically, (b) walks the **AST**, not the text. A substring scan over the oracle's source would
false-positive on its own docstrings — the expectation descriptions genuinely contain the words
"never `context_manifest.rev()`" — which is the same "assert against the field, never a substring"
trap one level up. Walking `ast.Name.id` / `ast.Attribute.attr` means only real identifier use counts.

### What changed

- `FORBIDDEN_PRODUCERS`: `episode_capture.{mechanical_fields, reopen_total, failed_command_count,
  manifest_ref, _lease_role, _artifact_refs, project_name, snapshot_path,
  emit_mechanical_snapshot, emit_step_manifest}` and `context_manifest.{rev, build_manifest, rows,
  content}`.
- `_independence_harness()` — a context manager that patches all of the above to raise, patches
  `_ControlRun.compose` / `.snapshot` to raise, and guards `builtins.open`, `io.open`,
  `Path.read_text`, `Path.read_bytes` so any read of a path with a `mechanical/` component raises.
  Reads are *guarded*, not blocked: the oracle legitimately reads one file, the context manifest
  whose bytes it pins. `io.open` is patched as well as `builtins.open` because `Path.open` calls the
  former by reference.
- The test is now three layers: **(a)** rebuild the expectation inside the harness; **(b)** AST scan
  of `_ControlRun.expectations`, `blob_oid`, `_git` against `FORBIDDEN_IDENTIFIERS`, with a
  non-vacuity assert that identifiers were actually parsed; **(c)** the original prose check, kept as
  documentation and no longer the only thing standing.

### RED-PROOF (M5) — two arms, assertion text inline

Both arms leave every `Expect.source` description **untouched**, which is exactly why the old
prose-scanning guard could not see them.

**M5a — the oracle calls the composer.** `"reopens"` sourced from
`episode_capture.reopen_total(json.loads(self.path.read_text(...)))`.

```
PRE  OID: fb9dfc2f3dffdd2e9e9fca192fffe9c22a795788
apply arm a: 1 substitution
POST OID: d2834432983b35bbcdc99de4c6b49450df66469f     <- verified applied
```
```
1 failed, 12 passed
E       AssertionError: the oracle called episode_capture.reopen_total: the expectation is NOT
        independent of the thing under test - it would be comparing the thing to itself
```

Layer (b) catches it **independently** — confirmed by running the AST pass against the mutated module
directly, out of band, so the two layers are shown not to be one layer twice:

```
static layer (b) would report: ['episode_capture', 'reopen_total']
```

**M5b — the oracle reads the seam's emitted snapshot** (a *new* mutation, not a repeat of a spent
one; it exercises the read-guard arm that M5a leaves untouched). `"reopens"` sourced from
`json.loads((self.path.parent / "mechanical" / "g2.json").read_text(...))["mechanical"]["reopens"]`.

```
PRE OID: fb9dfc2f...  ->  ARM-B OID: bd2ef8c6cf43e745733889ffd859f709e5897d69   <- verified applied
```
```
1 failed, 12 passed
E       AssertionError: the oracle read the seam's emitted snapshot
        (...\negctl0\mechanical-control-repo\.agent-work\ctl-parent\mechanical\g2.json):
        that is the reading under test, not an independent source
```

**Restored:** both arms back to `fb9dfc2f3dffdd2e9e9fca192fffe9c22a795788`; 13 passed.

### What else carries the conclusions this guard was propping up

The C3 requirement — "the control can say, per field, what the independent source was" — was the
*only* thing this guard carried, and its declarative half is what M5 walked through. The *values*
were never resting on it: they are carried by the per-field `compare_fields` result and by R1–R4
naming exactly the broken field. What was genuinely unsupported before is the independence claim
itself, and it is now supported by execution.

---

## FIX 3 — the delivered-context half is now exercised, and A3's condition is reachable

### What changed

- `DECLARED_CONTEXT` — two real entries, `{repo, seed.txt}` and `{repo, changed_by_the_run.txt}`,
  declared on **both** gates of the control's plan. Both, not just the ending step: the manifest is
  written per-step and write-if-absent, so declaring only on `g2` would leave `g1`'s manifest empty
  and half the seam unexercised.
- `expected_rows(repo)` — what the rows must say, computed here from the files' own bytes via
  `blob_oid`; never `context_manifest.rev()`, never the manifest itself. `rev: null` for an absent
  file is produced the same way rather than special-cased.
- `compare_manifest_rows(expected, manifest)` — returns mismatched declared **paths**, in declaration
  order. A list of names, never a bool, for exactly the reason `compare_fields` is. Missing,
  out-of-order, wrong-`rev` (including `null` where a file was delivered) and surplus rows are all
  named.
- `_ControlRun.manifest(step)` — reads the step's manifest as bytes and decodes, matching how
  `expectations` reads it.
- `test_declared_context_is_delivered_and_pinned` — both topologies, rows compared per row, with
  `git hash-object --no-filters` as a code-disjoint second witness per file, and a premise assert
  that no expected rev is null (otherwise the comparison would be null-vs-null and vacuous).

### The manifest that is now actually produced (pasted, as required)

Identical rows on both topologies; parent shown:

```json
{
  "contract": 1,
  "step": "g2",
  "files": [
    {"root": "repo", "path": "seed.txt",               "rev": "e31de1f3a235fd5e8f97207b8e43cd2aa06a6417"},
    {"root": "repo", "path": "changed_by_the_run.txt", "rev": "587be6b4c3f93f93c489c0111bba5596147a26cb"}
  ],
  "repo_rev": {"commit": "62928397286ef64baa04497a644a0256ba1e7724"},
  "run": {
    "work_id": "ctl-parent",
    "generated_at": "2026-08-02T07:07:49Z",
    "dirty": true,
    "roots": {"skill": "...", "repo": "...", "durable": "..."},
    "host": {"platform": "win32", "python": "3.14.3", "cwd": "..."}
  }
}
```

Before this the `files` array was `[]` on every manifest the control produced.

### A3 reachability, and the deliberate assertion

`test_a3_a_null_manifest_does_not_read_as_success` builds a fresh temp repo in which **neither**
declared file exists (asserted, not assumed), drives `claim` + `start g1` through the real CLI so the
seam emits `g1`'s manifest, and then asserts three things deliberately:

1. **The declaration was honoured, not dropped.** Both rows are present, in declaration order, each
   with `rev: null` — `[("repo","seed.txt",None), ("repo","changed_by_the_run.txt",None)]` — and
   `expected_rows(repo)` agrees with the manifest independently. "Declared but not delivered" and
   "never declared" are different facts, and only the row keeps them apart.
2. **It does not read as success.** Compared against what the rows would say had the files been
   delivered, `compare_manifest_rows` names **every** declared path:
   `== ["seed.txt", "changed_by_the_run.txt"]`.
3. **The pin itself is still correct**, asserted rather than left implied:
   `fields["context-manifest-ref"] == f"ctx-a3-null-g1@{blob_oid(raw)}"`.

**The finding, stated in full and not hidden:** `context-manifest-ref` remains *correct* under A3, and
that is not a gap — the field is a byte-pin over the manifest's own bytes, the bytes really did
change, and the harness's independent OID tracks them. What A3 was reaching for is one level down,
whether the manifest's **rows** are honest, and that is what (1) and (2) now cover. A3's original
GREEN was therefore defensible for the field and vacuous for the attack; it is no longer vacuous.

### What else carries the conclusions this fixture was propping up

`context-manifest-ref`'s correctness was never resting on the declaration — it is carried by
`compare_fields` plus the M-C red-proof (constant sha1, caught naming `['context-manifest-ref']`).
What was resting on nothing is the *row contents*, and that is new coverage rather than repaired
coverage.

---

## Restoration proof

**No file under `scripts/` was ever mutated.** Verified regardless:

```
scripts/episode_capture.py    wt=8a38e33d1c12bb814d4383a42bfe389d6aee7e93  head=8a38e33d1c12bb814d4383a42bfe389d6aee7e93
scripts/checklist_engine.py   wt=cef065ab0751b855053df9755114a38b1f0aeeca  head=cef065ab0751b855053df9755114a38b1f0aeeca
scripts/context_manifest.py   wt=77604fd15d3e6604539c616c3b3b75dcadafcd3f  head=77604fd15d3e6604539c616c3b3b75dcadafcd3f
```

Every mutation was applied to `tests/test_episode_negative_control.py`, and each was verified applied
by an OID **change** before its red was trusted, and verified restored by an OID **match** after:

| mutation | pre | mutated | restored |
|---|---|---|---|
| M1 (`--why` + `--note`) | `49059be` | `11a7a01` | `49059be` ✓ |
| M5a (composer call) | `fb9dfc2` | `d283443` | `fb9dfc2` ✓ |
| M5b (snapshot read) | `fb9dfc2` | `bd2ef8c` | `fb9dfc2` ✓ |

Mutation scripts live in the session scratchpad, not in the repo. `git status --porcelain` carries
only the intended change and the engine plan:

```
 M .agent-work/issue-305/crew-runs.json          (pre-existing, not mine)
 M tests/test_episode_negative_control.py        (the change)
?? .agent-work/issue-305/crew/g3-implement-rework-plan.json
?? .agent-work/issue-305/crew/g3-implement-rework-plan.json.journal
```

No raw working-tree byte comparison was used anywhere (#319).

---

## Suite numbers — every moved number accounted for

| | baseline | now | delta |
|---|---|---|---|
| passed | 1485 | **1487** | **+2** |
| skipped | 2 | 2 | 0 |
| subtests | 472 | 472 | 0 |

The `+2` is exactly the two tests FIX 3 adds: `test_declared_context_is_delivered_and_pinned` and
`test_a3_a_null_manifest_does_not_read_as_success`. Nothing else moved. The control file itself goes
13 → 15 for the same reason; the other 11 pre-existing tests in it pass unchanged, and the four
in-suite red-proofs (R1–R4) still pass on the reworked file.

---

## Third vacuous guard: NOT found

Swept every remaining assertion in the file against "can this fail?":

- `test_claimed_parent_topology_...` / `test_unclaimed_child_topology_...` / `test_the_seam_emits_...`
  — all route through `compare_fields`, whose falsifiability is proven live by R1–R4 naming exactly
  one field each.
- `test_canon_episode_store_untouched` — guards its own non-vacuity first (`len(tracked) >= 2`, plus
  an `.md` present), which is the pattern I would otherwise have flagged.
- `test_321_observation_...` — `pytest.raises` on two paths and a positive `is None` / raises pair on
  the third.
- `test_cross_run_retrieval_...` — asserts both a populated result and an empty one, so the join is
  shown to discriminate.
- `test_rhyme_search_survives_consolidation` — asserts the retired member from both directions.

One **weakness, not a vacuity**, disclosed: `_flag_pairs` would mis-read a flag *value* that itself
begins with `--`. No engine verb takes one, and the mis-read biases toward reporting an unknown flag
— i.e. strictly more likely to fire, never less — so it cannot convert a violation into a pass. This
is stated in its docstring rather than left for a reviewer to find.

---

## Assumptions

1. `AGENT_TEXT_FLAGS` was transcribed from `checklist_engine.py`'s argparse block rather than
   inferred. It is a **secondary** layer: `ALLOWED_FLAGS` is closed-world, so a text-bearing flag
   missing from `AGENT_TEXT_FLAGS` is still caught. The census would only under-report if a flag were
   both added to `ALLOWED_FLAGS` and free-text — a deliberate two-place edit.
2. `blob_oid` does not LF-normalise while `context_manifest.rev` does. They agree here because every
   file this module writes uses `newline="\n"`. Pre-existing property of the harness, not introduced.
3. `_independence_harness` patches module attributes, so a future `from episode_capture import X` in
   the oracle would evade layer (a) — which is exactly why layer (b) exists and why I did not drop it.

## Stop conditions hit

None. No fix required re-cutting the control, no guard proved unfixable, scope was not exceeded, no
decision outside the handoff's "yours to decide" was needed, and no third vacuous guard was found.

## Out-of-scope observations (triage candidates, NOT fixed)

1. **The engine's `current` verb rejects `--session-id`** while every other verb accepts it via the
   shared parser loop. `checklist_engine.py current --session-id X` exits 2 with
   `unrecognized arguments`. Harmless but a papercut that costs a retry in every scripted drive.
2. **#379 (`role`/`refusals` honest null) left unfixed** as instructed.
3. `run.dirty`/#327 and the #300 successor line untouched — g4's.

---

## Map Impact

Reusing the inbound anchor vocabulary; recorded as candidates, not authored.

- `capability:cross-run-retrieval` — unchanged. This rework touched only the control's premise
  guards and the manifest's delivered-context half.
- `struct:query_episodes`, `struct:episodes/active` — unchanged; canon store still asserted clean.
- `decision:zero-agent-effort-is-literal` (`@grade: settled/human`) — **now genuinely tested**. The
  decision was previously asserted by a guard that could not fail; it is now asserted by a
  closed-world argv census with a live red-proof. The decision itself is unchanged; what changed is
  that the test of it is real. Worth a note on the anchor that its evidence moved from declarative to
  behavioural.
- `constraint:no-raw-worktree-bytes` — honoured throughout; all restoration by blob OID.
- `constraint:throwaway-consolidation` — untouched; the A3 fixture runs in its own temp repo and
  canon stays clean.
- **New, worth an anchor:** the control's plan now declares `context_refs`, so the manifest's
  `files` rows are exercised on both topologies. Previously every manifest the control produced had
  `files: []` — a whole half of `context_manifest.build_manifest`'s output was outside the control's
  reach.
- `claim:negative-control-can-fail` — now discharged at a second level: not only can the control's
  field comparison fail (R1–R4, M-C, M-D, M-E), its **premise guards** can fail too (M1, M5a, M5b).

---

## Workflow Feedback — blunt

1. **The `constellation-implementer` skill is actively wrong for reworks, and this is the fifth
   time.** Its opening paragraph demands a fresh plan before reading the handoff closely. Both the
   handoff and the dispatch had to spend their first paragraphs overriding it, in bold, with a
   parenthetical apologising for a known defect. A skill that every rework handoff must open by
   contradicting is a skill defect, not a handoff defect. It needs a rework branch: *"if the handoff
   says REWORK, drive a plan of the named fixes; do not re-plan the underlying work."* Filing this
   against the skill, not the epic, is the right move — but somebody has to actually file it.
2. **The handoff was otherwise excellent** and I want to be specific about why, because it is
   reusable: it named the exact mutation that beat each guard, gave me the mutation as a
   *reproduction target* rather than as a description, and pre-empted the "repairing a vacuous check
   does not retroactively support its conclusions" move. That last instruction changed what I wrote —
   without it I would have fixed the guards and moved on.
3. **"Verify every mutation actually applied by blob OID" should be doctrine, not a per-handoff
   reminder.** It is now the third handoff in this epic carrying the same warning in the same words.
   The mechanism is two commands. It belongs in the crew doctrine that red-proofs inherit.
4. **The `--mechanical` ruling would have been better with the argv census attached to it
   originally.** The ruling was correct and survived M1, but the *evidence* for it was a comment. The
   general lesson: when a ruling says "X is fine because we never do Y", the run that relies on it
   should assert it does not do Y — otherwise the ruling degrades into a claim nothing checks, which
   is #337's exact shape in a different costume.
5. **Minor engine papercut:** `current` not accepting `--session-id` (see out-of-scope 1). Every
   scripted drive pays one wasted invocation to learn this.
