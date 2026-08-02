# Implementation Result — #305 gate g4 (closes #327)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4-implement` — drop `run.dirty` from the context manifest, correct every stale prose site, and
record #300's successor line. Handoff:
`.agent-work/issue-305/crew/g4-implement-handoff.md`. Engine plan (driven end to end, session
`g4-impl-2026-08-02`): `.agent-work/issue-305/crew/g4-implement-plan.json`.

## Completed slice
The manifest producer no longer consumes the `dirty` half of the `repo_state` edge. No manifest
carries the field anywhere — not in `run`, not in `repo_rev`, not in `content()`. A depth-complete
regression guard pins that. Nine prose sites now record that the field was there and why it went,
using the measured counts, never the disproven "permanently true" claim.
`checklist_engine.repo_revision()`'s **behaviour is byte-unchanged** — docstring only.

## Scope
**Files changed:**
- `scripts/context_manifest.py` — `run_facts()` signature + returned dict; `build_manifest()` call
  site; module docstring property 1; `CONTENT_KEYS` comment; `default_repo_state()`, `run_facts()`,
  `build_manifest()` docstrings
- `tests/test_context_manifest.py` — new module-level `_dirty_key_paths()` helper; the guard;
  ~10 assertion sites; class docstring; 4 test renames
- `tests/test_context_determinism.py` — **docstring prose only**, zero assertion changes
- `docs/CHECKLIST_ENGINE_DESIGN.md` — corrected narrative + the #300 successor paragraph
- `scripts/checklist_engine.py` — **`repo_revision()` docstring only**

**Specific exclusions touched:** `no`.
- `CONTENT_KEYS` — untouched, still `("contract", "step", "files", "repo_rev")`.
- `checklist_engine.repo_revision()` behaviour — untouched; still returns `{commit, dirty}`;
  `tests/test_checklist_engine.py` 1058–1110 untouched and green.
- `#382` — not approached.
- `docs/CHECKLIST_SCHEMA.md` — confirmed no change needed (blob OID equals HEAD).
- `scripts/episode_capture.py` — blob OID equals HEAD.

## Behavior changed
`yes` — the emitted manifest envelope loses one key. `run` is now exactly
`{work_id, generated_at, roots, host}`. Nothing else about the producer changed; `content()` is
byte-identical to before, because `dirty` was never content.

## Test mode
**Required:** `test-first` (acceptance item 4 requires a regression guard).
**Satisfied:** `yes` — guard written and observed RED against the unchanged producer, then GREEN
after the change. Transcript below.

---

## 1. Full-suite numbers

```bash
cd C:/Programs/constellation-skills-wt/e298-305 && python -m pytest tests/ -q
```

```
1487 passed, 2 skipped, 471 subtests passed in 141.79s (0:02:21)
```

| | baseline at handoff | measured now | delta |
|---|---|---|---|
| passed | 1487 | **1487** | 0 |
| skipped | 2 | **2** | 0 |
| subtests | 472 | **471** | **−1** |

**The −1 subtest is fully accounted for and is not a regression.**
`tests/test_context_manifest.py::RevIsGitBlobOid::test_rev_equals_git_rev_parse_head_for_tracked_clean_files`
subtests over the *clean* subset of its four `TARGETS`, one of which is `scripts/checklist_engine.py`.
That file is now `M` in the working tree because of this gate's docstring edit, so it drops out of
the clean subset: 4 subtests → 3. The test measures cleanliness rather than assuming it (its own
comment says so), so this is the test behaving as designed against an uncommitted tree. Verified
directly:

```bash
$ python -m pytest "tests/.../test_rev_equals_git_rev_parse_head_for_tracked_clean_files" -q
1 passed, 3 subtests passed in 0.53s
$ git status --porcelain -- scripts/checklist_engine.py
 M scripts/checklist_engine.py
```

The count returns to 472 once the Commander commits. **No test was deleted or skipped to reach
these numbers**; the four renamed tests are the same tests under corrected names, and one new test
replaced one removed test (net 0).

Interim runs: `tests/test_context_manifest.py tests/test_context_determinism.py` → 77 passed,
77 subtests; adding `tests/test_checklist_engine.py` → 407 passed, 100 subtests.

---

## 2. `git grep -n "run\.dirty"` — literal output

Every surviving hit is inside `.agent-work/` (archives, planning artifacts, prior gate handoffs and
results — the historical record, correctly left alone). **Zero hits in `scripts/`, `tests/`,
`docs/` or `skills/`:**

```bash
$ git grep -n "run\.dirty" -- ':!.agent-work'
$ echo $?
1
```

Full literal output, whole tree (35 hits, all `.agent-work/`):

```
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-implement/IMPLEMENTER_RESULT-rework1.md:20
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-implement/IMPLEMENTER_RESULT-rework1.md:28
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-implement/IMPLEMENTER_RESULT-rework1.md:68
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-implement/IMPLEMENTER_RESULT-rework1.md:197
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-implement/PLAN-rework1.json:78
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-implement/PLAN-rework1.json:338
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-implement/REWORK-1.md:45
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-review/REVIEW_RESULT-rework1.md:72
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-review/REVIEW_RESULT-rework1.md:114
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-review/REVIEW_RESULT-rework1.md:116
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-review/review.json:91
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g5-review/review.json:134
.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/spine.json:303
.agent-work/issue-305/MISSION_FRAME.md:82
.agent-work/issue-305/PLAN_CRITIC_DISPOSITION.md:138
.agent-work/issue-305/PROBLEM_STATEMENT.md:112
.agent-work/issue-305/STATE_NOTE.md:130
.agent-work/issue-305/crew/g1-implement-handoff.md:38
.agent-work/issue-305/crew/g1-implement-plan.json:198
.agent-work/issue-305/crew/g1-implement-result.md:32
.agent-work/issue-305/crew/g1-review-handoff.md:54
.agent-work/issue-305/crew/g1-review-result.md:230
.agent-work/issue-305/crew/g1-review-result.md:376
.agent-work/issue-305/crew/g2-review-handoff.md:198
.agent-work/issue-305/crew/g3-implement-handoff.md:193
.agent-work/issue-305/crew/g3-implement-result.md:28
.agent-work/issue-305/crew/g3-implement-rework-handoff.md:136
.agent-work/issue-305/crew/g3-implement-rework-result.md:360
.agent-work/issue-305/design-it-twice/candidate-A.md:107
.agent-work/issue-305/design-it-twice/candidate-B.md:73
.agent-work/issue-305/design-it-twice/candidate-B.md:165
.agent-work/issue-305/execute.json:855
.agent-work/issue-305/execute.json:856
.agent-work/issue-305/execute.json:913
.agent-work/issue-305/execute.json:949
.agent-work/issue-305/execute.json:962
.agent-work/issue-305/g1-review/review.json:61
.agent-work/issue-305/g3-review/review.json:70
.agent-work/issue-305/notes-2.md:37
.agent-work/issue-305/spine.json:176
.agent-work/issue-305/spine.json:204
.agent-work/issue-305/spine.json:543
```

**Reviewer, read this before you trust that grep.** See §5 finding 1: the grep **structurally cannot
see** the `scripts/checklist_engine.py` site, because that docstring never contained the literal
string `run.dirty` — it said "the manifest's excluded `run` subtree". Passing the grep does **not**
prove scope item 4 was done. Verify that site by reading `repo_revision()`'s docstring.

Complementary sweep, to show no "permanently true" claim was reintroduced:

```bash
$ git grep -ni "permanently\|self-caused" -- ':!.agent-work'
docs/removability_ledger.json:35          # to-prd, unrelated
docs/superpowers/plans/2026-06-24-lease-owner-liveness.md:228   # unrelated
docs/superpowers/specs/2026-06-24-windows-shell-hazards-design.md:60  # unrelated
docs/superpowers/specs/2026-06-24-worktree-isolation-real-fix-design.md:30  # unrelated
tests/test_context_manifest.py:206        # about git hash-object, unrelated
```

Nothing I wrote restates it. Where frequency is characterised at all, I used the measured counts
(47 `true` / 1 `false` / 1 field-absent across 49 manifests) and the read-then-write mechanism.

---

## 3. The two judgement calls

### Call 1 — the regression guard's shape

**Chose: a depth-complete guard, not three flat assertions.**
`test_dirty_lives_in_run_not_content` → `test_dirty_appears_nowhere_in_the_manifest`, in the same
`RepoRevContent` class. It asserts five ways:

1. `assertNotIn("dirty", m["run"])`
2. `assertNotIn("dirty", m["repo_rev"])`
3. `assertNotIn("dirty", cm.content(m))`
4. `assertEqual(_dirty_key_paths(m), [])` — a new module-level helper walking the whole envelope
   (dicts and lists, any depth) and returning every path at which a key named `dirty` occurs
5. `assertNotIn("dirty", cm.encode(m))` — the token absent from the encoded bytes

**Why:** the three flat assertions only guard the three places the field has historically lived. The
field has already been re-placed once (content → `run`); the failure mode worth guarding is it
coming back *somewhere new*, which flat assertions would miss silently. The recursive sweep plus the
encoded-token check catch a re-introduction under any nested or renamed parent.

**The `repo_state` fake still supplies `dirty=True`.** That is the point of the test: it proves the
consumer *ignores what it is handed*, which is a strictly stronger claim than proving nobody hands
it anything. Every other `repo_state` fake in the class also still supplies the field, unchanged —
that edge's contract is untouched.

### Call 2 — `test_content_is_unaffected_by_dirty_when_commit_is_equal`

**Chose: KEEP the test and TAKE the handoff's suggested strengthening.** The property is still true
and still valuable. Dropped the final `assertNotEqual` on the two `run.dirty` values (no subject
any more) and replaced it with two assertions that the **whole manifest** is now insensitive to
`dirty`:

```python
self.assertEqual(cm.content(m_clean), cm.content(m_dirty))          # unchanged
self.assertEqual(                                                   # new
    {k: v for k, v in m_clean["run"].items() if k != "generated_at"},
    {k: v for k, v in m_dirty["run"].items() if k != "generated_at"},
)
self.assertEqual(                                                   # new
    {k: v for k, v in m_clean.items() if k != "run"},
    {k: v for k, v in m_dirty.items() if k != "run"},
)
```

**Why:** the old test could only claim *content*-insensitivity because the two manifests genuinely
differed elsewhere. With the field dropped, that weaker claim now understates what is true, and the
stronger form is the one that catches `dirty` leaking back in under any key at all. `generated_at`
is the only field legitimately free to move (`roots`/`host`/`cwd` are constant within one process),
so it is the only exclusion.

### Three renames I made that the handoff did not ask for

Recorded because they are judgement, not mechanics. Each removes a name that would have become a
false description — exactly the stale-prose failure the handoff forbids. I verified by grep that no
tracked file outside `.agent-work/` archives references any of these test ids.

- `test_default_repo_state_against_the_real_repo_matches_git_oracles` →
  `..._matches_the_commit_oracle`. Its `git status --porcelain` oracle had no remaining assertion,
  so I **removed the now-dead subprocess block**; leaving a plural name over one oracle is stale.
- `test_default_repo_state_on_a_non_git_directory_yields_none_none` → `..._yields_no_commit`, and
  `test_default_repo_state_with_no_repo_root_mapped_yields_none_none` → `..._yields_no_commit`.
  "none_none" named the `{commit: None, dirty: None}` pair; the manifest now shows one field.
  (`default_repo_state` itself still returns both — that is unchanged and correct.)

---

## 4. Proof that `dirty` appears in no produced manifest

Not a unit fixture. **Three proofs, one script, all pass**
(`<scratchpad>/prove_no_dirty.py`, kept out of the repo):

```
A  post-change engine manifest : .agent-work/issue-305/issue-305-g4-implement/context/m4-prose.json
A  dirty key paths             : []
A  control (pre-change sibling): .agent-work/issue-305/issue-305-g4-implement/context/m0-context.json
A  control dirty key paths     : ['/run/dirty']
B  freshly emitted manifest    : <tmp>/.agent-work/proof-run/context/only.json
B  dirty key paths             : []
B  run subtree keys            : ['generated_at', 'host', 'roots', 'work_id']
C  default_repo_state(real repo): {'commit': 'aa5d06dd41fd4ac98f74327a06b3d2824a6f72ab', 'dirty': True}
C  manifest built on real roots : dirty key paths []
C  repo_rev                     : {'commit': 'aa5d06dd41fd4ac98f74327a06b3d2824a6f72ab'}

PASS
```

**A — the strongest one, and it is free: this run produced its own before/after.** Driving my plan
through the engine made `checklist_engine.main() -> episode_capture.emit_step_manifest() ->
build_manifest() -> write_manifest()` emit a real manifest per step. `m0-context.json` was written
before the change and still carries `"dirty": true`; `m4-prose.json` was written by the **same code
path in the same run** after it and carries nothing. Verbatim:

```json
// m0-context.json (pre-change)          // m4-prose.json (post-change)
"run": {                                  "run": {
  "work_id": "issue-305-g4-implement",      "work_id": "issue-305-g4-implement",
  "generated_at": "2026-08-02T16:43:51Z",   "generated_at": "2026-08-02T16:50:22Z",
  "dirty": true,                            <-- gone
  "roots": {...}, "host": {...}             "roots": {...}, "host": {...}
}                                         }
```

**B** — a fresh end-to-end `emit_step_manifest` into a throwaway work area, right now.

**C — premise verified, not assumed.** `default_repo_state()` on the real repo root returns
`dirty: True` at this moment, so the edge *is* handing the field over; the manifest built from those
same live roots still has zero `dirty` paths, and its `repo_rev.commit` is non-null, proving the git
edge actually ran and the proof is not vacuous.

**Two false results caught and fixed rather than accepted:** my first `emit_step_manifest(checklist,
base)` call silently returned `None` (real signature is `(checklist, iid, base_dir=None)`, so
`base_dir` defaulted to `None` and nothing was written — it would have read as "no dirty found");
and my first proof `work_id` was `prove-no-dirty`, whose own name contains the substring `dirty` and
tripped the token check via `run.roots`.

**No tracked file was mutated for any proof**, so no restore was needed. Spot-checked
`scripts/episode_capture.py` and `docs/CHECKLIST_SCHEMA.md` blob OIDs still equal HEAD.

### TDD evidence

- **Failing test observed** — against the producer at blob
  `77604fd15d3e6604539c616c3b3b75dcadafcd3f`, equal to `git rev-parse HEAD:scripts/context_manifest.py`,
  so the red is bound to the revision it proves (#381):

  ```
  >       self.assertNotIn("dirty", m["run"])
  E       AssertionError: 'dirty' unexpectedly found in {'work_id': 'w-1',
          'generated_at': '2026-08-02T16:46:57Z', 'dirty': True, 'roots': {...}, 'host': {...}}
  tests\test_context_manifest.py:964: AssertionError
  1 failed in 0.41s
  ```

  The **named assertion**, not a bare non-zero exit.
- **Passing test observed:** `77 passed, 77 subtests` over the two affected modules immediately
  after the producer change; `1487 passed` in the full suite.
- **Refactor while green:** `yes` — all prose edits were made after green and re-verified.

---

## 5. Where the handoff was wrong against the tree

The handoff was accurate on **every** enumerated site — all line numbers, the exact set of
`dirty`-bearing lines in the test file, and both now-false claims in `repo_revision()`'s docstring.
Three deltas, one of them material:

1. **MATERIAL — acceptance item 3's grep cannot verify scope item 4.**
   `scripts/checklist_engine.py` **never contained the literal string `run.dirty`**; its docstring
   said "belongs in the manifest's excluded `run` subtree". So
   `git grep -n "run\.dirty"` returning nothing is *not* evidence that the engine docstring was
   corrected — it would have returned nothing whether I touched that file or not. I handled the site
   by reading. **A reviewer who checks only the grep would pass a run that skipped scope item 4.**
2. **Cosmetic — `build_manifest()` "(line ~387)".** 387 is the *call site* inside the return dict;
   the `def` is at 351. No impact.
3. **Pre-existing, unrelated, NOT fixed — `docs/CHECKLIST_ENGINE_DESIGN.md:187`** states
   `build_manifest(checklist, roots, ...) -> {contract, step, files, run}`, omitting `repo_rev`.
   Stale since #300 g5 added `repo_rev`, nothing to do with #327. Left alone on scope discipline;
   flagged below as a triage candidate.

Also confirmed, as instructed: `run_facts()` has **exactly one caller** in tracked source
(`build_manifest`, `scripts/context_manifest.py:387`); every other `run_facts` hit is a comment or an
`.agent-work/` archive. `docs/CHECKLIST_SCHEMA.md:123` is the `context_refs` row and needs no
change (its blob OID equals HEAD). No other consumer of `manifest["run"]["dirty"]` exists anywhere
in `scripts/` or `tests/`, and no test asserts the exact key set of the `run` subtree, so dropping
the key breaks no shape test.

---

## Docs/contracts touched
- `docs/CHECKLIST_ENGINE_DESIGN.md` — the "Two-level revision scheme" narrative corrected, plus a
  new paragraph, **#300's successor and why the sequencing is deliberate (#305, #327)**, in the
  document's own dense declarative register. It records: #300 shipped the producer with **no
  caller**; #305 g1 wired the first one (`episode_capture.emit_step_manifest`); #305 g4 then removed
  the field (#327) once a real caller made its behaviour observable — read-then-write means each
  manifest reads its *predecessor's* tree, and the measured spread is 47 `true` / 1 `false` / 1
  field-absent over 49 manifests, so neither reading is available to a consumer. States explicitly
  that the field was **not an oversight in #300 and its removal is not a reversal of a mistake**.
- `docs/CHECKLIST_SCHEMA.md` — confirmed unchanged, correctly.

## Map Impact
- **Structural anchors touched:** `struct:context_manifest.run_facts` (`scripts/context_manifest.py:320`,
  function) — parameter dropped, returned dict loses one key;
  `struct:context_manifest.build_manifest` (`:351`, function) — call site narrowed to `commit`;
  `struct:checklist_engine.repo_revision` (`scripts/checklist_engine.py:574`, function) —
  **docstring only, behaviour and signature unchanged.**
- **Capabilities affected:** the manifest's delivery record no longer reports producing-environment
  dirtiness. Per-declared-file dirtiness remains derivable from content alone (row `rev` vs
  `git rev-parse <commit>:<path>`), scoped to the declared set.
- **Constraints/assumptions touched:** `CONTENT_KEYS` admission list **honored, untouched** — the
  removal needed no content change, which is evidence that admitting `repo_rev` by sub-field was the
  right shape. `repo_revision()` stays a general repo-facts primitive returning both halves;
  one consumer using one half is deliberate, not a seam to re-shape.
- **Decisions resolved:** `decision:drop-run-dirty` (`@grade: settled/human`) executed as ruled;
  not re-litigated. The corrected justification (measured, not "permanently true") is now the
  durable record in code and docs.
- **Claims/evidence produced:** `dirty` absent from every produced manifest — backed by §4's three
  proofs including an in-run pre/post control.
- **Triage candidates:** `docs/CHECKLIST_ENGINE_DESIGN.md:187` omits `repo_rev` from the stated
  `build_manifest` return shape (stale since #300 g5, unrelated to #327).

## Assumptions
- The `.agent-work/issue-305/issue-305-g4-implement/context/*.json` manifests my own engine run
  produced are **new untracked files** the Commander will pick up. `m0/m1/m2/m3` were emitted
  *before* the change and still carry `"dirty": true`; `m4/m5/m6` do not. That is an honest record of
  when each was taken, and it is the control that makes §4 proof A meaningful. **Commander decision:
  keep them as-is (recommended — they are this gate's own evidence) or drop the pre-change ones.**
  Acceptance item 1 is about what the *shipped* producer emits, and no manifest emitted after the
  change carries the field.

## Stop conditions hit
- `none` on the work. **One forced waiver on my own plan, disclosed here and surfaced to the
  Commander by message — Commander adjudicates at `g4-integrate`.**

### Forced waiver — `m6-suite-and-result.c3` (evidence `e-m6-suite-and-result-4`)

**The check was defective, not the work.** I authored c3 as
`test "$(git rev-parse HEAD)" = "$(git rev-parse origin/epic-298/305)" && git diff --cached --quiet`,
intending "this implementer created no commit and staged nothing." That is an invalid test of that
property: local `epic-298/305` is **9 commits ahead of `origin/epic-298/305`** (`a847897`), every one
of them the Commander's and all predating this dispatch. So c3 could only ever pass if I pushed —
which the handoff forbids.

The intended property **is** satisfied, proven three independent ways:

1. HEAD is still `aa5d06dd41fd4ac98f74327a06b3d2824a6f72ab`, the commit it was at when I claimed the
   lease — corroborated by this run's own first produced manifest `m0-context.json`, which recorded
   `repo_rev.commit = aa5d06d` before I touched anything.
2. `git reflog` `HEAD@{0}` is that same pre-dispatch commit — **no commit entry from this run at all.**
3. `git diff --cached --quiet` exits 0 — nothing staged.

`c1` (full suite) and `c2` (result artifact) **passed normally and are not waived.** The waiver is
recorded `forced: true` because I omitted an `override_policy` when authoring the condition. The
authority string names **me**, not the Commander: I requested authorization by message and acted
before a reply arrived rather than idling on a push-only channel, so the record must not imply a
consent I did not have.

## Out-of-scope observations
- `docs/CHECKLIST_ENGINE_DESIGN.md:187` — see triage candidate above.
- `emit_step_manifest(checklist, iid, base_dir=None)` returns `None` silently when `base_dir` is
  omitted. That is deliberate (documented: "a `base_dir` of `None` writes nothing at all"), but it
  means a caller that gets the positional arity wrong reads as "emitted nothing" rather than
  failing. It cost me one false-negative round in §4. Noting only; #382-adjacent territory and not
  mine to widen.

## Workflow Feedback
- **Handoff gaps:** the **Acceptance** section's item 3 is the one real defect. It presents
  `git grep -n "run\.dirty"` as the check that "no stale prose survives", but scope item 4
  (`scripts/checklist_engine.py`) is written in prose that never uses that string — so the stated
  acceptance check is silently blind to one of the four enumerated scope items. An acceptance
  criterion that cannot fail for a site it is meant to cover is the same class of manufactured-green
  hazard the handoff's own **Method warnings** section warns about (CRLF, `| head`).
- **Context rediscovered:** none of substance — the handoff's enumeration was accurate enough that
  m1 was pure confirmation. The one thing I had to derive myself was the `run_facts` caller count,
  which the handoff explicitly (and correctly) asked me not to take on trust.
- **Instructions improvised around:** the plan template's `config_ref` points at
  `docs/agents/engine-config.json`, which **does not exist in this worktree** (`docs/agents/` holds
  only `ORCHESTRATOR_CONTEXT.md`; there is no `CREW_CONTEXT.md` or `GLOSSARY.md` either). I set
  `config_ref: null`, matching the prior g1–g3 plans in this issue. The crew context overlay
  degraded to global-only, as `checklist-engine.md` says it should.
- **What would have made this easier:** state acceptance item 3 as *"`git grep -n "run\.dirty"` is
  necessary but NOT sufficient — `scripts/checklist_engine.py` never used that literal string;
  verify that site by reading"*. One clause, and it closes the only trap in an otherwise unusually
  precise handoff.

## Return status
`complete`
