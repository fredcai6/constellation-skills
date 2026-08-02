# IMPLEMENTER_RESULT

## Assigned gate
`g3-implement` — "Negative control, proof it can fail, and cross-run retrieval" (issue #305, attempt 1)

## Completed slice
The negative control for `zero agent effort is literal`, driven through the real engine on **both**
lease topologies; four in-suite red-proofs that name the specific mismatched field; two source-level
mutations proven RED and restored; and the cross-run-retrieval / surviving-consolidation demonstration
in a throwaway store.

**Return status: `complete`. No stop condition hit — the control did NOT legitimately fail.** The
handoff's MEASURED FINDING is confirmed, and it is fully expressible as an *expected refusal* rather
than a failure: on the production child topology `role` and `refusals` are refused, and the control
asserts that refusal as the correct reading rather than skipping it.

## Scope

**Files changed:**
- `tests/test_episode_negative_control.py` — **new**, 13 tests (the control, 4 red-proofs, 4 retrieval/canon).
- `.agent-work/issue-305/evidence/g3_control_repro.py` — **new**, the one-command repro.
- `.agent-work/issue-305/crew/g3-implement-plan.json` (+ `.journal`) — **new**, my engine plan.
- `.agent-work/issue-305/issue-305-g3-implement/` — **new**, emitted by the seam itself during my own run.

`scripts/episode_capture.py` was mutated **twice, temporarily**, for the red-proof and restored both
times (proof below). It is byte-identical to HEAD now. No other production file was touched.

**Specific exclusions touched:** `no`. `run.dirty`/#327 untouched; no #300 doc note added; g2's
`reopens` shape B not re-litigated; the seam's placement unchanged; `refusals` semantics unchanged;
no consolidation created in `episodes/active/`.

## Behavior changed
`no` — test-only. The composer, the seam and the engine are unchanged.

---

# 1. Independent verification of the MEASURED FINDING (load-bearing)

**CONFIRMED. The code agrees with the handoff.** Verified two ways, neither inheriting the claim.

**(i) From scratch**, on a synthetic parent→child gated run in a fresh temp git repo (parent gate
carries `child_checklist`, child driven with no lease):

| checklist | `engine_session` | `refusals` key | refused |
|---|---|---|---|
| `spine.json` (parent, claimed) | active lease | present, `0` | `[]` |
| `execute.json` (child, never claimed) | `null` | **absent** | `['role', 'refusals']` |

**(ii) Against the live production run** in this worktree: `.agent-work/issue-305/execute.json` has
`engine_session: null` and no `refusals` key, and its emitted `mechanical/g3-implement.json` reports
`"refused": ["role","refusals"]`.

**Cause, read in the code today (measured, not reasoned):** `_lease_role` (`episode_capture.py:223`)
reads `engine_session.claimed_by`, and the child has none. `refusals` is armed *only* by `claim`
(`checklist_engine.py:964`) and incremented *only* in `main()`'s `EngineError` branch
(`checklist_engine.py:2617`) — so an unclaimed checklist never acquires the key at all.

**The scoped null, stated precisely:** *`role` and `refusals` cannot be captured from engine state at
the child-gate seam as currently structured, because the child checklist never receives a lease
(#357).* This is **lease-topology dependence, not agent dependence** — no agent action can change it.
It is **not** "mechanical capture is infeasible": the other **eight** fields are captured correctly on
the child topology, and all ten on the parent.

**Consequence for the control, and the vacuity trap avoided:** the control drives **both** topologies
through the **identical verb sequence**, so the lease is the only difference and the delta cannot be
attributed to anything else. A control driving only a claimed standalone spine would have reported ten
green fields and proved nothing.

# 2. The exact list of engine verbs the control issues (load-bearing)

`claim`, `start`, `attest`, `advance`, `reopen`. **That is the whole list**, and the harness asserts it
(`assert argv[0] in self.VERBS` on every call; `test_control_records_nothing_agent_authored`).

Nothing agent-authored crept in:
- **no `--finding`**, **no narrative `attach`**, no hand-written episode, no `flag-candidate`.
- `attest` is issued with **no `--note`**, so `satisfied_by` is the engine's own literal `"attested"`.
- `advance` uses **`--mechanical`**, never `--why`. This matters: `advance` refuses a non-`why_exempt`
  gate without one or the other (`checklist_engine.py:1712`), and `--why` is prose. `--mechanical` is a
  flag, and the engine explicitly never lets a mechanical marker become the digest.
- **One disclosed residue:** `reopen` requires `--reason`. It is a fixed constant `"control"`, feeds no
  mechanical field, and is declared as `_ControlRun.REOPEN_REASON` rather than hidden.

The control drives the engine as **CLI subprocesses, not the Python API** — load-bearing, because
`refusals` only ever moves inside `main()`'s error path, so an API-driven control would silently be
measuring a field production does move and it does not.

# 3. The per-field comparison, with the independent source named (load-bearing)

The harness increments its own expectation **on the line that issues the triggering call**. It never
calls `mechanical_fields()`, `reopen_total()`, `failed_command_count()`, the emitted snapshot, or
`context_manifest.rev()` to decide what the answer should be. `test_every_field_has_a_named_independent_source`
asserts, mechanically, that no expectation's stated source names any of those.

| field | expected (parent) | expected (child) | independent source |
|---|---|---|---|
| `run` | `ctl-parent` | `ctl-child` | the `work_id` string the harness wrote into the plan file |
| `project` | `mechanical-control-repo` | same | the directory name the harness chose for the temp repo |
| `role` | `commander` | **REFUSED** | the `--claimed-by` string the harness passed to `claim` / no lease was ever taken |
| `spine-step` | `g2` | `g2` | the gate the harness deliberately left active (it does not ask which) |
| `context-manifest-ref` | `ctx-ctl-parent-g2@<oid>` | `ctx-ctl-child-g2@<oid>` | `sha1(b"blob <n>\0" + manifest bytes)` computed in the harness, **cross-checked against `git hash-object --no-filters`** (a second, code-disjoint witness; the harness asserts the two agree before using the value) |
| `refusals` | `4` | **REFUSED** | count of calls the harness issued *expecting* a refusal / counter never armed |
| `reopens` | `2` | `2` | count of reopens the harness issued expecting them honored |
| `rework-count` | `1` | `1` | count of reopens the harness issued **against the active step only** |
| `failed-commands` | `3` | `3` | count of advances issued while the harness had deliberately left the flag file absent |
| `artifact-ref` | `["changed_by_the_run.txt"]` | same | the exact path the harness staged with `git add` |

**Result: `compare_fields(expected, actual) == []` on both topologies** — all ten present-and-correct on
the parent; eight present-and-correct plus two refused-and-expected-to-be-refused on the child.

Three anti-vacuity properties are asserted rather than hoped for:

1. **The four counters are four distinct numbers — `rework-count=1, reopens=2, failed-commands=3,
   refusals=4`** — asserted explicitly. No two can be swapped, aliased or coincidentally equal.
2. **A refused field must be ABSENT.** `Expect(REFUSED, …)` fails if the field turns up *present*, so
   the refusal assertions are falsifiable (proved in R3 below). A non-reading stays visibly distinct
   from an uncollected one.
3. **Absence on the child is structural, not "nothing happened".** The harness issues **four refused
   calls** against the unclaimed child and the `refusals` field is *still* absent — so `REFUSED` cannot
   be misread as `0`.

The seam is also checked separately from the composer: `test_the_seam_emits_the_same_group_unasked`
asserts the `mechanical/g2.json` the engine wrote **on its own during the run** matches the same
expectations and reports `refused: []` / `refused: ["refusals","role"]` respectively.

**Induced failures are an exit-code vocabulary (#315):** the induced check is
`test -f "<absolute path>"`. The engine passes no `cwd` on the command branch and discards the check's
stdout, so a check that printed its verdict would print into a void and a relative path would resolve
against an uncontrolled directory. Flag absent → exit 1; flag present → exit 0.

# 4. Proof the control can FAIL, naming the SPECIFIC field (load-bearing)

## Source-level mutations (both restored)

**R2 (sharp, load-bearing) — dropped exactly one derivation.** `failed_command_count` mutated to
`return 0` in `scripts/episode_capture.py`:

```
RED  (a) claimed parent spine: MISMATCHED FIELDS -> ['failed-commands']
       failed-commands: expected 3 (source: count of advances this harness issued while it had
                                    deliberately left the flag file absent...)
       failed-commands: actual   0
RED  (b) unclaimed child gate-plan: MISMATCHED FIELDS -> ['failed-commands']
```
and in the suite:
```
>       assert compare_fields(expected, parent.compose()) == []
E       AssertionError: assert ['failed-commands'] == []
E         Left contains one more item: 'failed-commands'
```
**Exactly one field named, on both topologies.**

**R1 (blunt) — composer returns hardcoded constants.** `mechanical_fields` mutated to return ten
plausible constants (each of which passes `apply_episode_delta._validate_create` cleanly, which is
precisely why the validator cannot be the oracle):
```
RED  (a) claimed parent spine: MISMATCHED FIELDS -> ['run', 'project', 'role', 'spine-step',
     'context-manifest-ref', 'refusals', 'reopens', 'rework-count', 'failed-commands', 'artifact-ref']
RED  (b) unclaimed child gate-plan: MISMATCHED FIELDS -> [ ...same ten... ]
```

Neither mutation repeats the three **spent** g2 mutations — both break the *capture pipeline*, which is
different ground.

## In-suite red-proofs (the discriminating tests live in `tests/`, per the g2 Admiral ruling)

Each asserts an **exact mismatch list**, never a boolean and never an exit code:

| test | breakage | assertion |
|---|---|---|
| `test_red_proof_blunt_hardcoded_composer` | `mechanical_fields` → constants | `== list(MECHANICAL_GROUP)` (all ten) |
| `test_red_proof_sharp_drops_exactly_one_derivation` | `failed_command_count` → `0` | `== ["failed-commands"]` |
| `test_red_proof_sharp_fabricated_role` | `_lease_role` → `"implementer"` on the **child** | `== ["role"]` |
| `test_red_proof_sharp_inflated_reopens` | `reopen_total` → `1` (the step-scoped value) | `== ["reopens"]` |

`test_red_proof_sharp_fabricated_role` is the one that closes the last vacuity hole: it proves the
**refusal** assertions can themselves go red. Without it, "role is absent on the child" would pass for
the same reason an empty check passes.

Each of these fails in **both** directions — if the monkeypatch did not take effect the list would be
`[]`, which is also `!=` the asserted list. They cannot pass vacuously.

**Why a non-zero exit is explicitly not the evidence:** stated in the repro's own docstring. Import
errors, collection errors and empty test selection all exit non-zero, so a wrapper mapping any
non-zero to RED would report red for all of them.

## Proof of restoration after every mutation

```
after R2:  git hash-object scripts/episode_capture.py -> 8a38e33d1c12bb814d4383a42bfe389d6aee7e93
           git rev-parse HEAD:scripts/episode_capture.py -> 8a38e33d1c12bb814d4383a42bfe389d6aee7e93
after R1:  git hash-object scripts/episode_capture.py -> 8a38e33d1c12bb814d4383a42bfe389d6aee7e93
           git rev-parse HEAD:scripts/episode_capture.py -> 8a38e33d1c12bb814d4383a42bfe389d6aee7e93
           git status --porcelain scripts/  ->  (empty)
```
Blob OIDs, not raw working-tree bytes (#319). No mutation is left in the tree; the plan's `m3.c3`
postcondition is itself the OID-equality command check, so the engine verified it too.

# 5. Before/after blob OIDs for `episodes/active/` — both read, then compared (load-bearing)

**BEFORE** (captured at m0, before any g3 work):
```
100644 48d80e66de4efb4d34602da33597e2acd5da3d70 0	episodes/active/.gitkeep
100644 bf4ac0b76726a7409c86186c11f946f395001c2e 0	episodes/active/issue-309-001.md
100644 3e062589bb0d433be62543297052456821de9040 0	episodes/active/issue-309-002.md
```
**AFTER** (captured at m5, after the full g3 run including the synthetic consolidation):
```
100644 48d80e66de4efb4d34602da33597e2acd5da3d70 0	episodes/active/.gitkeep
100644 bf4ac0b76726a7409c86186c11f946f395001c2e 0	episodes/active/issue-309-001.md
100644 3e062589bb0d433be62543297052456821de9040 0	episodes/active/issue-309-002.md
```
**Compared: identical — same three paths, same three blob OIDs, no additions, no removals.**
`git status --porcelain episodes/` is **empty**.

**The store is NOT empty**, so this is not an empty-vs-empty pass: it holds **two real episodes**
(`issue-309-001.md`, `issue-309-002.md`) plus `.gitkeep`. `test_canon_episode_store_untouched` asserts
that non-emptiness *first*, then the cleanliness — so if canon were ever emptied, the guard would fail
rather than silently start passing vacuously.

**Belt and braces:** (a) the whole retrieval exercise runs in a `tmp_path_factory` store outside the
repository (asserted: `REPO_ROOT not in root.parents`), and (b) the OID listings above.

# 6. Cross-run retrieval — `neighbours()` before and after

Seeded through the **sanctioned writer** `apply_episode_delta.apply_delta` (never hand-placed files):
three `cluster-*` episodes sharing `artifact-ref: shared/alpha.md`, each with a *distinct*
`role`+`spine-step` (that pair is always a join key, so varying it is what makes the fixture prove
something about `artifact-ref`), plus one unrelated `outsider-001`.

```
BEFORE  neighbour_ids(root, "cluster-002")  ->  ['cluster-001', 'cluster-003']
        neighbour_ids(root, "outsider-001") ->  []            # the join discriminates

        retire cluster-002, consolidated-into: cluster-001

AFTER   neighbour_ids(root, "cluster-002")  ->  ['cluster-001', 'cluster-003']    # UNCHANGED
```
**Rhyme-search survives consolidation**: the anchor is fetched *by id*, so a consolidated (archived)
member can still be walked back from — which is exactly what #308's consolidation pass needs. Both
directions are asserted so "it vanished" and "it moved" stay distinguishable:
`neighbour_ids("cluster-001") == ['cluster-003']` (ordinary set) and
`== ['cluster-002','cluster-003']` with `include_retired=True`; and
`fetch_episode("cluster-002").consolidated_into == "cluster-001"`.

# 7. #321 observation (one sentence, as requested)

On the **write** path the handed id *is* validated — `create` refuses a supplied `id` outright (the
writer assigns it) and `retire` validates its handed id against `ID_RE` before applying anything — so
the unvalidated-handed-id path is on the **read** side, where `query_episodes.fetch_episode("NOT A
VALID ID", root)` returns `None` rather than refusing, making "no such episode" and "you handed me
nonsense" read identically. Recorded, **not fixed** (`test_321_observation_where_a_handed_id_is_validated`).

# 8. Full suite

```
python -m pytest -q
1485 passed, 2 skipped, 472 subtests passed in 77.52s
```
**Delta accounted for exactly:** `1485 − 1472 = +13`, and my new file contributes exactly 13 tests.
`2 skipped` and `472 subtests` are unchanged.

The baseline was **asserted** in the handoff, so I re-verified it rather than inheriting it:
```
python -m pytest -q --ignore=tests/test_episode_negative_control.py
1472 passed, 2 skipped, 472 subtests passed in 72.87s
```
That is the handoff's number, independently reproduced. No failures anywhere, so no failure-distribution
claim is made.

## Deliverable path check
```
tests/test_episode_negative_control.py              -> git check-ignore exit 1  (committed)
.agent-work/issue-305/evidence/g3_control_repro.py  -> git check-ignore exit 1  (committed)
scripts/episode_capture.py                          -> git check-ignore exit 1  (committed, unchanged)
docs/EPISODE_STORE.md                               -> git check-ignore exit 1  (committed, untouched)
```

## Test mode
**Required:** `test-first, with the hard extra bar that the control must be proven red.`
**Satisfied:** `yes.` TDD red was observed **before** green (see below), and the control was proven red
by two source mutations plus four in-suite per-field red-proofs before any green was trusted.

## TDD evidence
- **Failing test observed:** first run of the control — `8 failed, 1 passed in 4.84s`. The failure was
  real and diagnostic, not a stub:
  `FileNotFoundError: .../.agent-work/ctl-parent/ctl-parent/context/g2.json`. **I had walked straight
  into #360** — `manifest_root()` is the checklist dir's **PARENT** and `manifest_path` re-appends the
  work-id, so deriving `<checklist dir>/<work-id>/context/` double-nests and reads as "no manifest at
  all". The handoff warned about exactly this and I still hit it; the corrected derivation carries a
  comment saying so.
- **Passing test observed:** `13 passed in 5.38s` (`9 passed` at the point the control alone was green).
- **Refactor while green:** `yes` — retrieval/canon tests added on top of a green control.

## Docs/contracts touched
- `none`. `docs/EPISODE_STORE.md` was read but not modified; the `refusals` documentation fix is g2's
  and is already shipped, and #367 records the deferred semantics question.

## Map Impact
- **Structural anchors touched:** `struct:query_episodes` — exercised, unmodified: `neighbours()` /
  `neighbour_ids()` now have an explicit surviving-consolidation regression test.
  `struct:episodes/active` — read-only; its blob OIDs are now asserted unchanged by a suite test.
- **Capabilities added/changed/affected:** `capability:cross-run-retrieval` — now has an executable
  acceptance test, including the negative case (`outsider-001` has zero neighbours), so the capability
  is demonstrated rather than asserted.
- **Constraints/assumptions touched:** `constraint:throwaway-consolidation` — honored, and now
  mechanically enforced by `test_canon_episode_store_untouched`.
  `constraint:no-raw-worktree-bytes` — honored: every comparison is a blob OID.
  **New constraint surfaced:** `constraint:lease-topology-bounds-mechanical-capture` — the mechanical
  group is complete only on a **claimed** checklist; on the production child gate-plan it is
  structurally eight-of-ten.
- **Decision anchors:** `decision:zero-agent-effort-is-literal` — **upheld with a named bound.** The
  claim holds fully for the eight lease-independent fields on every topology, and for all ten on a
  claimed checklist; `role` and `refusals` are bounded by lease topology (#357), not by agent effort.
  `decision:refuse-never-fabricate` — validated end to end: R1's ten plausible constants pass the
  store's own validator and are caught only by this control.
- **Claims/evidence produced:** `claim:negative-control-can-fail` — **SATISFIED**, by four per-field
  in-suite red-proofs plus two restored source mutations, each naming the specific field.
- **Trust limitations / drift found:** #357 (the child gate-plan never receives a lease) is now
  load-bearing for episode capture, not merely a workflow wart — worth reflecting in the map.
- **Triage candidates:** see Out-of-scope observations.

## Assumptions
- The plan lives at `.agent-work/issue-305/crew/g3-implement-plan.json` by convention with g1/g2; the
  handoff did not name a path for it.
- "Mark one cluster consolidated" is realized as `retire … consolidated-into: <id>`, the only
  consolidation verb the writer offers.
- `--mechanical` on `advance` counts as "records nothing" (it is a flag, and the engine explicitly
  excludes a mechanical marker from the digest). Flagged to the Commander at proof-of-life; not
  contradicted.

## Stop conditions hit
`none.` Specifically: the control did **not** legitimately fail, no red-proof was un-namable, allowed
scope was not exceeded, no decision outside my authority was needed, and **no defect was found in the
composer** — R1/R2 confirmed it is doing real derivation, not returning constants.

## Out-of-scope observations (triage candidates — not acted on)
1. **#357 is now load-bearing for capture, not just workflow.** Because the child gate-plan never gets
   a lease, every gate in production emits a mechanical snapshot missing `role` and `refusals` — the two
   fields `apply_episode_delta._validate_create` **requires**. So a real episode created from a real gate
   cannot be validated without an agent supplying those two by hand, which is the exact class this issue
   exists to eliminate. **This is a design decision for you and the Admiral, not mine**: options include
   claiming the child, having the seam consult the parent's lease, or narrowing the required set. I have
   deliberately done none of them.
2. **#321's live edge is the read path, not the write path** (see §7) — `fetch_episode` conflates a
   malformed id with a missing one.
3. **`emit_mechanical_snapshot` is a step-ACTIVATION reading.** Already documented in its docstring, but
   the control makes the practical consequence concrete: for a step's *final* tallies you must call
   `mechanical_fields()`, or reopen the step. Any consumer reading `mechanical/<step>.json` as an
   end-of-step record will under-count.

## Workflow Feedback
- **Handoff gaps:** genuinely few — this was the most usable handoff of the three. Two real gaps.
  (a) **C1 forbids "agent-authored text of any kind" but does not mention that `advance` structurally
  refuses without `--why` or `--mechanical`.** I had to discover `--mechanical` in the engine source and
  decide unilaterally that it satisfies C1; if it does not, the whole control is invalid, and that is too
  load-bearing to be left to the implementer's judgment. Same for `reopen --reason`, which C1 lists as an
  allowed verb without noting that it *requires* a text flag. **Name the exempt flags in C1.**
  (b) **No path was specified for the implementer plan file**; I inferred it from g1/g2 siblings.
- **Context rediscovered:** that `refusals` is incremented **only** in `main()`'s `EngineError` branch,
  which forces the control onto CLI subprocesses rather than the Python API. The handoff's orientation
  section gave me the *arming* site (`claim`, `:955`) but not the *incrementing* site, and the difference
  is what decides the control's entire execution model. One more line in "The system under test" would
  have saved a read of `main()`.
- **Instructions improvised around:** the `constellation-implementer` skill opens by demanding a fresh
  plan *before* reading the handoff closely, while the handoff is authoritative over the plan's shape —
  so the first plan is necessarily written with incomplete information. I wrote a coarse six-item plan and
  it happened to survive; a sharper task would have needed `amend`. The already-noted defect (no sanctioned
  rework path) has this mirror image at the *start* of a run.
- **What would have made this easier:** the `#360` warning in Constraints is stated as a general caution
  ("Check yours"). It is worth **one concrete line**: *the manifest lands at
  `<checklist dir>/context/<step>.json`, i.e. beside the checklist, NOT at
  `<checklist dir>/<work-id>/context/`.* I read the warning, agreed with it, and then made precisely that
  mistake — which suggests the abstract form of the warning does not transfer. That was my only red round-trip.
