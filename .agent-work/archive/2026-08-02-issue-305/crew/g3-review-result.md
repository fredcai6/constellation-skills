# REVIEW_RESULT

## Assigned Gate
`g3-review` — issue #305, epic #298. Reviewing `g3-implement` attempt 1.

## Result
**`APPROVE-WITH-FOLLOWUPS`**

Stated plainly, because you asked me not to round it: **the negative control is real and
falsifiable on its central claim; two of its premise guards are not.** The field-comparison
machinery — the thing that actually tests `decision:zero-agent-effort-is-literal` — went red
under every attack I could aim at it. What did *not* survive are the two checks meant to enforce
C1 ("records nothing") and C3 ("ground truth is independently tallied"). Both are checks that
cannot fail. The shipped artifact is honest; its self-enforcement is not.

**Recorded explicitly:** your handoff pre-committed to `BLOCK` if any named attack scored green,
and **attack 3 did**. My technical judgment is that the A3 green does not make the control
vacuous (reasoning below), so I did not round up to BLOCK — but the pre-commitment is yours to
enforce and **I do not object if you do**.

Survey: `.agent-work/issue-305/g3-review/review.json`, 18 checks, all visited, consolidated
under lease `g3-review-reviewer-01`. Fowler record: `.agent-work/issue-305/g3-review/fowler-pass.json`
(`verify_fowler_pass.py` exit 0).

---

## The three named attacks

| # | attack | result | evidence |
|---|---|---|---|
| **A1** | composer → hardcoded constants | **RED** | 6 failed / 7 passed. `test_claimed_parent_topology…`: *"Left contains 10 more items, first extra item: 'run'"* — **all ten fields named**. |
| **A2** | delete the ground-truth tally | **RED** | 7 failed / 6 passed — both topology tests, the seam test, and all four red-proofs. |
| **A3** | every declared context ref → missing file | **GREEN — 13 passed** | See below. |

**Method note (the trap you warned about).** Every mutation's liveness was proven *before* its
colour was trusted. Mutations reach the engine **subprocesses** via a `sitecustomize.py` on
`PYTHONPATH`; each run first printed `episode_capture.__NC_MUT__` and
`mechanical_fields.__name__` from **both** the pytest process and a spawned subprocess. In-process
harness mutations use a pytest plugin that **raises** if the target module is not found and
self-reports `applied=<name>` at teardown. **No repository file was edited at any point** — final
blob OIDs below.

### A3 — the green, and my adjudication

I made every gate declare three `context_refs` to non-existent files, then **read the emitted
manifest** rather than assuming:

```
files: [{repo, does/not/exist/alpha.md, rev: null},
        {repo, does/not/exist/beta.md,  rev: null},
        {skill, does/not/exist/gamma.md, rev: null}]
```

All three `rev: null`. The control scored **13 passed**.

**Why this is defensible, not a vacuity:** `context-manifest-ref` is a **pin over the manifest
file's own bytes**, and the harness recomputed the blob OID from the *mutated* bytes and matched.
The field's derivation is genuinely being discriminated — it is just not an assertion about
manifest *content*, and by `docs/EPISODE_STORE.md` §8 it was never meant to be.

**What is genuinely missing, and it is upstream of that:** the shipped plan declares **no
`context_refs` at all** (measured: `any("context_refs" in t for t in _plan(...)["tasks"].values())`
is `False`), so the control's manifest is content-free (`files: []`) in **every** shipped case. The
fixture never exercises a manifest with a single resolved ref, so "context was delivered" and
"nothing was declared" are indistinguishable to it. Filed as **F3**.

---

## My own mutations — nine, all outside the seven spent

| # | mutation | caught? |
|---|---|---|
| **M1** | **every `advance --mechanical` → `advance --why <narrative prose>`; every `attest` given `--note <prose>`** | **NOT CAUGHT** |
| **M5** | `expectations()` reads its four tallies back out of `compose()` — self-comparison — with the `source` prose untouched | **NOT CAUGHT** |
| M2 | `run` ← checklist **directory name** instead of `work_id` | not caught (benign) |
| M3 | `spine-step` ← `items[-1]` instead of `active_id()` | not caught (benign) |
| M6 | `project` ← `base_dir.parent.parent.name` instead of git topology | not caught (benign) |
| M8 | `artifact-ref` truncated to `out[:1]` | not caught |
| M4 | **claim the child** — collapse the two topologies | **CAUGHT** (2 failed) |
| M7 | **unclaim the parent** — collapse the other way | **CAUGHT** (2 failed) |
| — | `compare_fields` probed directly on both sides of every boundary | **discriminates** |

### M1 — the headline. A check that cannot fail, on the criterion the control is named for.

`test_control_records_nothing_agent_authored` asserts **only** that issued verb *names* are in
`VERBS` — which `_ControlRun._run` **already asserts on every call** — plus two `not in` checks
those same asserts imply. It checks **no flag at all**. Its comment block claims *"No `--finding`,
no narrative `attach`, no `--why` … `attest` was passed no note, and `advance` was passed
`--mechanical`"* — **none of which the code checks.**

I rewrote every advance to carry narrative prose and gave every attest a narrative note. **The
suite stayed at 13 passed.** Landing verified before trusting the green:

```
ctl-parent: why_trail rows=7, rows carrying AGENT PROSE=4
  first prose row: {'id':'w-1','gate':'g1','why':'this is agent-authored narrative prose: I
    believe the gate is ready because I reasoned about it at length…','mechanical': False,…}
  postcondition satisfied_by: ['this is agent-authored narrative prose: …', None, None]
ctl-child:  why_trail rows=7, rows carrying AGENT PROSE=4      (identical shape)
```

So the claim *"this run recorded nothing agent-authored"* is, **in the suite, unfalsifiable**. The
shipped run really is clean — I verified the artifacts myself (every `why_trail` row
`mechanical: true`/`why: null`, every `satisfied_by == "attested"`) — but that is verified by
**inspection**, not by the check that carries the claim. This is the "costume of a check that
could not fail" pattern from #337, on C1. Filed as **F1 (must-fix)**.

### M5 — the C3 guard is prose-only

`test_every_field_has_a_named_independent_source` enforces independence by scanning each
expectation's `source` **string** for forbidden substrings. It cannot see the code. I rewired
`expectations()` to read `refusals`/`reopens`/`rework-count`/`failed-commands` straight back out
of `compose()` — textbook compare-the-thing-to-itself — and **left the source prose untouched**.
**13 passed.** C3 is the criterion your handoff says the whole gate rests on. Filed as **F2 (must-fix)**.

### M2/M3/M6 — not caught, but benign (your hunch was right, the consequence is milder)

You named `project_name()` and `active_id()`-derived `spine-step` as softest. They are — but for a
narrower reason than a hole. Each pair **coincides by fixture construction**:

```
honest run 'ctl-parent'  == mutated dirname 'ctl-parent'
honest step 'g2'         == mutated items[-1] 'g2'
honest project 'mechanical-control-repo' == mutated dirwalk 'mechanical-control-repo'
```

These are *wrong-but-still-mechanical* derivations, so they do not touch the zero-agent-effort
claim at all. What they show: per-field discrimination for `run`/`project`/`spine-step` catches a
**constant** (A1 does) but not a **wrong derivation**. Observation, not a follow-up.

### M4/M7 — the discriminating power you were most worried about holds

Neither topology can be silently collapsed. Claiming the child fails
`test_unclaimed_child_topology_refuses_only_role_and_refusals` + the seam test; unclaiming the
parent fails `test_claimed_parent_topology…` + the seam test.

And I verified `Expect(REFUSED, …)` **independently of R3**, at the predicate level rather than
through a hardcoded assertion:

```
REFUSED + absent   -> []          REFUSED + PRESENT     -> ['role']
present-but-wrong  -> ['reopens'] expected-but-ABSENT   -> ['reopens']
```

Both sides of every boundary discriminate. The refusal assertions are falsifiable. The four
counters `[1,2,3,4]` are asserted on the **expected** side, so an aliased harness tally is caught
there — and A2 confirms it goes red.

---

## Your three claims, adjudicated

### 1. `advance --mechanical` satisfies C1's "records nothing" — **UPHELD.** No re-cut needed.

Upheld on stronger ground than the reasoning you offered, and confirmed **at the world**, not just
in source. On a fresh temp gated plan:

```
advance g1  (neither flag)  -> exit 1  REFUSED: advancing a non-exempt gate requires a
                                       running understanding — pass --why … or --mechanical
advance g1 --mechanical     -> exit 0  g1 -> complete
why_trail: [{"id":"w-1","gate":"g1","why":null,"mechanical":true,"ts":…}]
satisfied_by: ['attested']
```

One of the two flags is **mechanically required**, so C1's "actions a run mechanically requires"
covers it. `--mechanical` records **zero agent characters**, and `_latest_why_record` explicitly
skips mechanical rows so it can never become the digest.

**The decisive part is empirical, and it comes from M1:** injecting maximal agent prose into every
advance and every attest changed **not one** of the ten mechanical fields. The mechanical group is
**provably disconnected** from agent-authored content — so `--mechanical` versus `--why` cannot
influence the measurement in either direction. Your premise is sound.

**One narrowing, and I would state it rather than let it ride.** `reopen --reason` is *not* in the
same class: `_append_reopen_marker` **writes the reason string into `why_trail`**, so `"control"`
is literally agent-authored text that gets recorded. It survives C1 only because it is (a) required
by the verb, (b) a declared fixed constant, (c) provably field-disconnected by the above. Worth
saying as a **bounded exception** rather than as a flat "nothing agent-authored was recorded" — the
flat claim is false as stated.

### 2. Return-item-4 call-site-sever evidence — **UPHELD.** Reproduced, numbers identical.

Sever liveness proven first (`emit_step_manifest is <function <lambda>>`, `__SEVERED__ = True` in
the subprocess).

- **Part 1:** `SEVER_SEAM=1` on the control → **8 failed, 5 passed**, `FileNotFoundError` at
  `test_episode_negative_control.py:308`. Exactly your figures.
- **Part 2:** in-process sever of the `checklist_engine.emit_step_manifest` **binding** across
  `test_context_manifest.py` + `test_episode_capture.py` → **94 passed, 63 subtests passed**, and
  the instrumented counter reports **`severed call site reached 0 time(s) in-process`**.

Reached-count is **zero**, not non-zero. Your conclusion stands and **the PR body may carry it**.

### 3. The #379 honest null — **UPHELD, including the half you flagged.**

I checked "requires both" against `_validate_create`'s **actual behavior**, not the tuple's name —
driving `validate_delta` with a full group and dropping one field at a time:

```
full group        -> ACCEPTED
drop role         -> REFUSED: create.mechanical.role: is required
drop refusals     -> REFUSED: create.mechanical.refusals: must be a non-negative integer
drop BOTH         -> REFUSED
drop artifact-ref -> ACCEPTED          (correctly optional)
```

The mechanism is the `mech.get(key) -> None` fallthrough in the `MECHANICAL_SCALAR_FIELDS` loop,
not tuple membership. The other half holds against the **live** run, independently of the synthetic
fixture: `execute.json` (child) has `engine_session: null` and no `refusals` key; `spine.json`
(parent) has `claimed_by: commander-305d`, `refusals: 0`; and **all five** emitted snapshots
(`g2-implement`, `g2-integrate`, `g2-review`, `g3-implement`, `g3-review`) report
`refused: ['refusals','role']`. A real gate snapshot cannot become a validated episode without an
agent supplying both by hand. Correctly characterised.

*Minor, not a defect:* dropping both fields names only the first, so the refusal reports one field
where two are missing.

---

## Consolidation discard — verified independently, not inherited

**Non-emptiness asserted FIRST**, so this is not an empty-vs-empty pass: `episodes/active/` carries
**3 tracked paths, 2 of them real `.md` episodes** (`issue-309-001.md`, `issue-309-002.md`) plus
`.gitkeep`. I then **read both sides myself** — `git ls-files -s episodes/active/` captured before
I ran the full suite and again after, compared with `diff(1)`: **no differences**, same 3 paths,
same 3 blob OIDs (`48d80e66…`, `bf4ac0b7…`, `3e062589…`). Index blob OIDs, never raw worktree bytes
(#319).

**Stronger than the implementer's check:** `git status --porcelain --untracked-files=all episodes/`
is empty **before and after** — plain `--porcelain` would not have shown an untracked synthetic
episode. None exists.

## Suite and restoration

```
python -m pytest -q                                            -> 1485 passed, 2 skipped, 472 subtests
python -m pytest -q --ignore=tests/test_episode_negative_control.py -> 1472 passed, 2 skipped, 472 subtests
```

Delta **+13**, exactly the new file's 13 tests; skips and subtests unchanged. Baseline derived
myself rather than inherited.

Every file byte-identical to HEAD by blob OID:

```
scripts/episode_capture.py      8a38e33d1c12bb814d4383a42bfe389d6aee7e93  == HEAD
scripts/checklist_engine.py     cef065ab0751b855053df9755114a38b1f0aeeca  == HEAD
scripts/apply_episode_delta.py  2627b45a306b52fd2b2162ed5aa3ca8312203cc8  == HEAD
scripts/query_episodes.py       6fff12b822b8f5180604c1cb9c154932ba2cd338  == HEAD
scripts/context_manifest.py     77604fd15d3e6604539c616c3b3b75dcadafcd3f  == HEAD
tests/test_episode_negative_control.py 3df98226a123d05f7e38c9dab7ec6a45563a23aa == HEAD
```

`git status --porcelain --untracked-files=all` shows only my own survey artifacts under
`.agent-work/issue-305/g3-review/` and the pre-existing `crew-runs.json` modification. **Every
mutation lived in memory or in my scratchpad; none ever touched the tree.**

## Handoff compliance
C1–C7 each have a real deliverable and I verified each rather than inheriting it. C4's per-field
discrimination is genuine (A1 names all ten; A2/M4/M7 red). C6's guard asserts non-emptiness before
cleanliness, so it cannot start passing vacuously. C7 reproduced exactly.

## Scope drift
None. `git diff --stat 3f787a3..HEAD` touches exactly **one** non-`.agent-work` path:
`tests/test_episode_negative_control.py` (new, +720). Every named exclusion honored; `episodes/active/`
gained nothing, tracked or untracked.

## Evidence verdict
Sound. I **ran** the one-command repro both ways: clean → `GREEN … MISMATCHED FIELDS -> [] (all 10
fields match)` on both topologies, exit 0; under A1 → `RED … -> [all ten names]` with an
expected/actual/source triple printed per field. It reuses `_ControlRun`/`_plan`/`compare_fields`,
so a repro that greens while the suite reds is impossible — though see F5, the *fixture body* is
copy-pasted. TDD evidence is credible and self-incriminating in the right way (the #360 red was
real and diagnostic). **#321 sanity-checked and the inversion is correct**: `_validate_create`
raises outright on a supplied `id`, `retire` validates against `ID_RE`, while
`fetch_episode("NOT A VALID ID", root)` returns `None` — the unvalidated handed-id path is the
**read** side, inverting what the launch order assumed.

## Code/doc quality
Fowler pass: 12 smells, **4 flagged**, **3 overridden with logged standard + reason**, 5 absent.
Flagged: `duplicated-code` (the control fixture body and `g3_control_repro.py:main()` are 26-line
blocks differing in **only three lines** by `diff -w`); `shotgun-surgery` (same root, seen as change
amplification — both my coverage gaps need the identical edit in two places, with nothing detecting
divergence); `comments-as-deodorant` (the M1 comment standing in for the missing check);
`long-method` (`expectations()` does OID cross-check + table building in ~70 lines). Overridden:
`feature-envy` (C3 *forbids* calling the producer's own helper as oracle — the duplicated derivation
**is** the independence), `primitive-obsession` (the store contract is string-keyed; an enum would
insert a translation layer between assertion and format — and the one place a primitive *would* be
wrong, `None`-for-refused, is correctly a sentinel type), `divergent-change` (the g2 Admiral ruling
plus C4/C5/C6 scope all three concerns into this one gate). **Noted in the record:** this worktree
has **no `CREW_CONTEXT.md` and no `GLOSSARY.md`**, so every override cites only a standard that
genuinely exists.

Quality constraints met: assertions are against the **field** (no `json.dumps` substring scan
anywhere); every write carries `encoding='utf-8', newline='\n'`; no `Path.read_text(newline=…)`, so
CI's 3.12 pin is safe.

## Map impact verdict
- **Evidence supports claimed change:** yes — I re-derived the red four ways rather than inheriting
  `claim:negative-control-can-fail`.
- **Constraints not violated:** `throwaway-consolidation` and `no-raw-worktree-bytes` both honored
  and now mechanically enforced.
- **Notes match the diff:** yes. `struct:query_episodes` confirmed absent from the diff;
  `struct:episodes/active` read-only and OID-verified.
- **Decision candidates surfaced:** yes. `zero-agent-effort-is-literal` upheld **with the named
  lease-topology bound**, which I re-derived from the live run (all five production snapshots refuse
  `role`+`refusals`) — correctly scoped as *topology*-dependence, not agent-dependence.
  `refuse-never-fabricate` validated: A1's ten plausible constants pass the store validator (I
  confirmed the full group `ACCEPTED`) and are caught **only** by this control.
- **Durable context routed:** yes. `constraint:lease-topology-bounds-mechanical-capture` is a
  genuine addition worth Cartographer's attention.

## Reconciliation check
No reconciliation forced. No docs or contracts touched.

## Blockers
**None that I am raising myself.** F1 and F2 are must-fix follow-ups, not merge blockers: the
shipped control is honest and its central claim is genuinely evidenced. **One decision is yours:**
your handoff pre-committed to BLOCK on a green named attack, and A3 scored green. I have given my
reasoning for why it is not a vacuity; enforcing the pre-commitment anyway is a legitimate call and
I would not argue with it.

## Follow-ups (filed as survey triage candidates tc1–tc5)
- **F1 (must-fix)** — `test_control_records_nothing_agent_authored` cannot fail. Fix shape: assert
  on the recorded **artifacts** — every `why_trail` row has `mechanical is True` and `why is None`,
  and every `satisfied_by == "attested"`.
- **F2 (must-fix)** — the C3 independence guard scans prose, not code. It cannot detect a
  self-comparing oracle.
- **F3 (should-fix)** — the control declares no `context_refs`, so `context-manifest-ref` is only
  ever pinned over a content-free manifest. Fix: declare one ref that **resolves** and one that does
  not, and assert the manifest rows.
- **F4 (should-fix)** — `artifact-ref` has only a single-element case; M8 truncating to `out[:1]`
  passes. The handoff's own multi-element-collection constraint is unmet for this field. Fix: stage
  two files.
- **F5 (nice-to-have)** — extract the shared world-setup so the repro genuinely reuses the fixture
  rather than copying it.

## Out-of-scope observations
- The severed-seam red is a **crash** (`FileNotFoundError`), not a named diagnosis — you already
  recorded this; I confirm it reproduces.
- `_validate_create` names only the **first** missing field when several are absent.

## Workflow Feedback

- **Handoff gaps:** genuinely the best of the three, and the *"here are the seven mutations already
  spent, go find an eighth"* table is the single most valuable thing in it — it is what pushed me off
  the fields you had already covered and onto the **flags**, which is where the hole was. Two real
  gaps. (a) The **three named attacks are stated as imperatives without their success criteria.**
  "Confirm an all-null manifest does NOT read as success" does not say *which* assertion should
  catch it, so when it scored green I had to reconstruct from scratch whether that meant "the control
  is vacuous" or "this field is a byte-pin and content is out of scope." Those are opposite verdicts
  and the handoff does not distinguish them. Name the expected failing assertion per attack. (b) The
  **stop condition and the verdict note contradict each other**: "Stop and return if any named attack
  scores green (BLOCK)" versus "`APPROVE-WITH-FOLLOWUPS` is sanctioned, do not round." I hit exactly
  that case and had to decide which instruction won. I reported both. Say which governs.
- **Context rediscovered:** that the **engine runs as a subprocess** in this control, which decides
  the entire mutation strategy — an in-process `monkeypatch` cannot reach the seam, so every source
  mutation has to go through `sitecustomize`. Your `M-E` row hints at it and the evidence file has the
  worked example, but the *reason* (`refusals` only moves in `main()`'s error path) lives in the
  implementer's result, not the handoff. One line in the handoff would have saved a read.
- **Instructions improvised around:** the reviewer skill says to `advance` each check, but a `survey`
  refuses `advance` (*"advance is for gated checklists; use record"*) — `record` both records and
  advances. Minor, but it cost a refused call on my first step and the skill text is wrong for the
  checklist type it mandates. Also: the `FOWLER_PASS` template's `repo_standards_ref` names
  `CREW_CONTEXT.md` and `GLOSSARY.md`, **neither of which exists in this repo** — a reviewer following
  the template literally would cite standards that are not there. I substituted what actually exists
  and said so in the record.
- **What would have made this easier:** one line in the handoff's method section — *"prove your
  mutation is live by printing the mutated attribute from both the pytest process and a spawned
  subprocess, before you read the colour."* You warned about the trap and named the OID check, but the
  OID check only catches *file* mutations; the trap for an in-memory mutation is different and needs a
  different probe. That is the concrete transfer your `#360` feedback was asking for, one level up.

## Return status
`complete`
