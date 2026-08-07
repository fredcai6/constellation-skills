# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1-review` — issue #300 (epic-298), "the deterministic projection substrate and its manifest".
Worktree: `C:/Programs/constellation-skills-wt/298-300`.
Survey driven through the engine: `.agent-work/300/g1-review/review.json`
(session `reviewer-300-g1`, 7/7 items visited, consolidated `verdict=BLOCK`).

## Result

# `BLOCK`

**1 blocker · 1 major · 1 minor · 2 flagged code smells · 4 triage candidates.**

The blocker is small and mechanical (one `skipTest` call). Everything the issue actually
rests on — the identity function, the one-envelope shape, the single selector, the
`/run`-only exclusion, and the determinism acceptance test's non-vacuity — I attacked
independently and it held.

---

## Blockers

### BLOCKER-1 — the change ships a test that turns CI red on a clean checkout

`tests/test_context_manifest.py`, `SelectionUsesTheEnginesOwnSelector::test_a_live_spine_in_this_work_area_also_projects`:

```python
live = sorted((ROOT / ".agent-work").glob("*/spine.json"))
if not live:
    self.skipTest(".agent-work is gitignored; no live spine in this checkout")
```

`.agent-work` is gitignored, so `actions/checkout@v4` **never** produces one. The repo's own
CI job runs a skip rail immediately after the suite:

```yaml
- name: Skip guard -- no undocumented skips
  run: python scripts/verify_skip_guard.py junit-report.xml
```

`scripts/verify_skip_guard.py` REFUSES (exit 1) any `<skipped>` testcase whose
`(classname, name, message)` triple is not on its `ALLOWED_SKIPS` frozenset. This new
triple is not on it.

**Reproduced, not inferred.** I built the CI condition exactly — a fresh `git worktree add
--detach ... HEAD` (so no `.agent-work`), the five changed files overlaid on top, then the
two CI steps in order:

```
=== clean checkout has .agent-work? ===
ls: cannot access '.../ci-sim/.agent-work': No such file or directory

=== CI step: python -m pytest tests/ -q --junitxml=junit-report.xml ===
1208 passed, 3 skipped, 315 subtests passed in 34.40s
PYTEST EXIT=0

=== CI step: python scripts/verify_skip_guard.py junit-report.xml ===
REFUSED: 1 skip(s) not on the documented allow-tuple list:
  - classname='tests.test_context_manifest.SelectionUsesTheEnginesOwnSelector'
    name='test_a_live_spine_in_this_work_area_also_projects'
    message='.agent-work is gitignored; no live spine in this checkout'
SKIP GUARD EXIT=1
```

Contrast with the same two commands in this worktree, where the test does **not** skip
only because `.agent-work/300/spine.json` happens to exist here:

```
1209 passed, 2 skipped, 316 subtests passed in 33.96s
skip guard ok: 2 skip(s) in report, all match documented allow-tuples
GUARD EXIT=0
```

So the implementer's Evidence §5 (`1209 passed, 2 skipped … the two skips are pre-existing`)
is true **on this host and false in the environment the gate is for**. The Close Criterion
"targeted plus broader suites green" is unmet in CI. This is the same class of defect the
handoff warned about ("a sibling issue in this epic shipped a red CI on exactly that"),
reached through a different door than the 3.13-API trap — which, for the record, the
implementer *did* close properly.

**Cheapest correct fix (implementer's call):** the property this test asserts —
"a real spine projects without crashing" — is already covered far more strongly by
`test_real_spine_templates_produce_a_manifest_without_crashing`, which runs against all 13
real committed gated templates. Replace the `self.skipTest(...)` with a plain `return`
(a no-op pass when there is nothing live to check), or delete the test. Adding the triple to
`ALLOWED_SKIPS` also works but spends a documented allow-slot on a test that proves nothing
new, and touches a file outside the allowed scope.

---

## Major (non-blocking)

### MAJOR-2 — `rev()`'s stated equality envelope is incomplete, and the check that "pins" it structurally cannot

`scripts/context_manifest.py:69-80`, the docstring:

> That equality holds only while no path is exempted from LF normalisation — a `-text` or
> `binary` attribute would make git stop normalising that path…

That is not the whole exemption set. Under `* text=auto`, git **also** declines to normalise
based on **content**, with no `.gitattributes` entry involved at all:

1. **a NUL byte anywhere** → git auto-detects binary and stores raw bytes;
2. **a lone CR** (a `\r` not followed by `\n`) → git's CRLF filter refuses to convert,
   because normalisation would not round-trip.

`rev()` normalises unconditionally, so it diverges in both cases. Four fixtures I authored,
oracle = `git hash-object` run against files I wrote:

| case | bytes | `rev()` | `git hash-object` | agree |
|---|---|---|---|---|
| `b"alpha\rbeta\r\n"` (lone CR) | 12 | `5bdcf0dd…` | `05cdef54…` | **False** |
| `b"alpha\r\r\nbeta\r\n"` (CR CR LF) | 14 | `5d1b5952…` | `df9f62ff…` | **False** |
| `b"\x00\x01\x02BINARY\r\nrow\r\n"` | 16 | `55ba2be5…` | `8a37c601…` | **False** |
| `b"a\r\n"*4000 + b"\x00"` (NUL past 8000B) | 12001 | `80c2fde7…` | `4d0d323c…` | **False** |

A diverged `rev` names a blob **git does not have**, silently and forever — which is the
design's own named worst failure mode, just triggered by content rather than by an attribute.
The gate's invariant command
`test -f .gitattributes && ! grep -nE '(-text|binary)' .gitattributes` cannot see either
trigger, so it certifies an invariant it does not actually hold.

**This is NOT a stop condition and I am not asking for the settled identity function to change.**
The handoff's stop condition is "disagrees with `git hash-object` for any **real case in this
repo**". I scanned for one and there is none:

```
== C:\Programs\constellation-skills-wt\298-300      scanned 312 files, 0 divergent
== C:\Users\fredc\.claude\skills                    scanned 234 files, 0 divergent
== C:\Programs\constellation-skills\.agent-work    scanned 2128 files, 0 divergent
```
plus all 263 tracked files hashed against the `git hash-object` oracle — **0 mismatches**.

**Asked fix:** correct the docstring to name all three exemption paths, and add the lone-CR
case to `RevIsGitBlobOid` as a documented known-divergence (an `assertNotEqual` against the
oracle is a perfectly honest test — it pins the envelope instead of pretending it is wider
than it is). Optionally, extend the gate check to a content guard over the declarable roots
(filed as triage candidate `tc3`) — that is the only form that would actually pin the claim.

**Why I did not make this the blocker:** the equality holds for every file that exists today
in every root a `context_refs` can name, and the corpus is markdown and JSON written under
`* text=auto`. The defect is a *false safety claim*, not a live wrong answer.

---

## Minor

### MINOR-3 — a drive-letter declaration path is accepted, where `resolve()`'s own comment claims it is caught

`scripts/context_manifest.py:154-159` says:

```python
# Belt and braces: the `..` rejection above is the primary guard; this catches
# anything the string form let through (drive-relative forms, odd separators).
```

It does not catch drive-relative forms. My fixture:

```
!!! windows drive-relative path 'C:/Windows/win.ini'
      expected=DeclarationError  got=ok
      [('repo', 'C:/Windows/win.ini', None)]
```

`PurePosixPath("C:/Windows/win.ini").is_absolute()` is `False` and its parts are
`('C:', 'Windows', 'win.ini')`; `ntpath.join` then applies same-drive semantics and folds
the whole thing to `<root>\Windows\win.ini`, which is inside the root, so the escape guard
passes. Consequences: the recorded `path` is **not** the path that was read, and the same
declaration resolves to a literal directory named `C:` on POSIX — i.e. it is content-
divergent across OSes. This is the same class as the glob-metacharacter rejection the
implementer added within latitude ("silently recording `docs/*.md` as one absent file would
be plausible wrong output"), and deserves the same treatment: reject a path whose first
segment ends in `:`. Three lines in `resolve()`, or just fix the comment to stop claiming a
guard that is not there.

---

## Handoff compliance

`satisfied, with the exceptions above.` All six deliverables are present and built to the
frozen spec: the in-process LF-normalised blob OID with no `git` subprocess and no commit SHA;
the optional ordered `context_refs`; a pure producer over `(checklist, roots, reader)` with a
single injected impure edge; the one envelope written to
`.agent-work/<work-id>/context/<step>.json`; the first real declaration on the Commander
spine's `context` step; and the cross-environment determinism acceptance test. No CLI verb
was added. No committed `CONTEXT_PROJECTION.json`, no `scripts/context_projection.py`.
`scripts/checklist_engine.py` is byte-unchanged — the "edit minimally if `active_id` needs
exporting" allowance was not used at all.

**Stop conditions: none tripped.** The identity function agrees with `git hash-object` for
every real case in this repo (0/263 mismatches); the determinism comparison excludes exactly
`/run`; no second selector exists; nothing widened toward proving use; no excluded file was
touched.

## Scope drift

`none.` `git diff` is one file. I compared the spine template field-by-field against `HEAD`
rather than reading the diff hunk:

```
same task ids: True
field-level diffs vs HEAD: [('context', 'context_refs')]
imperative byte-identical: True
top-level keys added/removed: set() set()
```

Only the `context` task carries a declaration. `docs/CHECKLIST_SCHEMA.md`,
`docs/CHECKLIST_ENGINE_DESIGN.md`, the declaration-vs-prose lint and
`verify_spec_confirmed.py` are all untouched (g3's and #303's). No widening toward proving
*use*: `grep -niE "transcript|access|trace|read_log|record_read|consumed|observed"` over the
producer returns exactly one hit — the module docstring disclaiming it.

## Evidence verdict

`fail` — see BLOCKER-1. Evidence §1–4 (the load-bearing four) all reproduce and are sound;
Evidence §5 (the suite-green transcript) does not reproduce in the target environment.

Verification commands re-run by me, at the source:

| command | result |
|---|---|
| `python -m pytest tests/test_context_manifest.py -q` | 45 passed, 46 subtests |
| `python -m pytest tests/test_context_determinism.py -v` | **7 passed** (verified with `-v`, not the count — all 7 genuinely ran) |
| `python -m pytest tests/test_context_manifest.py -q -k 'no_globs or newline_pinned or py312_compatible'` | 3 passed, 42 deselected, EXIT=0 (cannot exit 5) |
| `python -m pytest tests/test_checklist_engine.py -q` | 324 passed |
| `python -m pytest tests/ -q` | 1209 passed, 2 skipped *(here)* / **CI: guard REFUSES**|
| `grep -c 'context_refs' …COMMANDER_SPINE.template.json` | 1 |
| `.gitattributes` invariant | EXIT=0 |
| `git worktree list` before/after | 5 → 5, no strays |

**TDD mode satisfied.** Required test-first for `rev()`. The implementer recorded two reds and
was right to distrust the first: a collection error proves only that the module is missing.
The second red — a deliberately wrong `rev` that hashes raw bytes — is discriminating, and it
failed on **real repository files**, which is the correct shape of red for an identity function.

## The adversarial fixtures I authored, and what they proved

The handoff's primary hunt was round-trip blindness, with an explicit instruction not to
accept the implementer's fixtures. I wrote three independent harnesses. All three load the
module under review by path with `importlib`; **`scripts/context_manifest.py` was never
edited** (asserted byte-unchanged at the end of the mutation run).

**1. `rev_hunt.py` — 16 hand-chosen byte patterns + all 263 tracked files, oracle `git hash-object`.**
Agreed on: empty file, no trailing newline, CRLF with no trailing newline, UTF-8 non-ASCII
(LF and CRLF), UTF-8 BOM, trailing lone CR, mixed endings, a 405 KB CRLF file and its
400 KB LF twin (same OID), 1000 bare CRLFs, and UTF-16LE. **Diverged on four** — the lone-CR
and NUL classes above. This is the one place the implementer's suite was genuinely blind:
`RevIsGitBlobOid.TARGETS` is four clean corpus files, so it proves the corpus is clean, which
is exactly the failure mode the handoff named.

**2. `mutate_determinism.py` — is the acceptance test non-vacuous?**
This was hunt 4. I intercepted the test module's OVERLAY copy so each fresh checkout received
a *mutated* producer, then asked whether
`test_content_is_byte_identical_excluding_exactly_the_run_subtree` fires:

```
### baseline (no mutation)                         ran=6 failures=0  caught: False
### A: LC_ALL leaked into content                  ran=6 failures=1  caught: True
### B: rows ordered by hash() (seed-dependent)     ran=6 failures=1  caught: True
### C: rev salted with the platform                ran=6 failures=1  caught: True

producer under review is byte-unchanged: True
```

**The comparison is genuinely non-vacuous.** Each of the three ways a producer could become
environment-dependent — leaking an environment fact outside `/run`, letting `PYTHONHASHSEED`
reach row ordering, or letting the environment reach `rev` itself — is caught by the single
acceptance assertion. Mutation B is the sharpest: it proves the `PYTHONHASHSEED` axis is
load-bearing and not decorative.

I also confirmed the two environments are really distinct (distinct absolute checkout paths,
asserted), that the projection is non-empty (`INSTALL_SHIM` genuinely resolves the two
`global-*.md` rows to real OIDs — the false-green the implementer caught and fixed is
properly closed), and that the overlay does put the *uncommitted* change into both checkouts
rather than silently measuring `HEAD`.

**3. `producer_hunt.py` — 16 adversarial declarations.**
Correctly rejected: `//server/share/x.md`, empty and whitespace paths, a dict instead of a
list, a non-object entry. Correctly handled: `references/./doctrine.md`, `%2e%2e/…` (recorded
literally, no traversal), a directory path and a bare `.` (raise `PermissionError`, an
`OSError` — the spec's "present but unreadable → raise", so `null` keeps meaning one thing),
`NUL` (raises, resolves to `\\.\NUL` outside the root), a `str`-returning reader (`TypeError`,
fails visibly), and a `required` that is a string (harmlessly ignored — it never enters the
row). **One wrong answer:** the drive-letter path in MINOR-3.

## Code/doc quality

Sound, and better than most of what passes through this gate. The producer is 302 lines of
short pure functions with one injected impure edge, guard clauses that all fail visibly with
distinct messages, and no hidden fallback anywhere. The `-k` gate's three guards are the good
kind: each has an **AST half and a behavioural half**, and the no-globs behavioural half
booby-traps `os.listdir`/`scandir`/`walk` to raise and plants three decoy files — that is a
test that would actually catch the regression it names, not a string match. The 3.12 guard is
glob-discovered over `tests/test_context_*.py`, so a future sibling test file inherits it
rather than escaping it. The `constraint:extend-dont-parallel` test pins
`cm.active_id.__code__.co_filename` to the engine's own source file, which is the right
mechanical form of "not a copy".

**Fowler pass:** run over all 12 baseline smells, recorded to
`.agent-work/300/g1-review/FOWLER_PASS.json`; `scripts/verify_fowler_pass.py` exits 0
(`flagged=['duplicated-code','speculative-generality']`,
`overridden=['data-clumps','primitive-obsession','comments-as-deodorant']`, each override
carrying a named standard and a reason). Two flags, both observations rather than blockers:

- **duplicated-code** — `test_context_determinism.py` duplicates the entire second-checkout
  ritual (worktree add → OVERLAY copy → `SkipTest` guard → `remove --force`/`prune`/`rmtree`)
  in `DeterministicAcrossEnvironments.setUpClass` *and* inline in `RealCheckoutSkew`, and the
  two copies have **already drifted** — only the first applies `INSTALL_SHIM`. The skip
  handling under discussion is one of the duplicated fragments, so any change to it has to be
  made twice. `load()` is duplicated verbatim across both test modules.
- **speculative-generality** — the `run=` parameter on `build_manifest()` *and* `produce()`
  has **zero callers and zero tests**; the `step=` override is precisely the seam a second
  selection path could grow through (the one test using it could set task status instead, as
  `test_step_tracks_active_id_as_items_complete` already does); and the
  `raise ValueError(f"step {selected!r} is not a task on this checklist")` branch is
  unreachable on the default path — I reproduced `active_id()` raising `KeyError('x')` first,
  so that friendly message can never render. In a module that explicitly cuts the CLI verb as
  YAGNI, these three are inconsistent with its own standard.

## Map impact verdict

- **Evidence supports claimed change:** yes. `capability:spine-keyed-context-delivery` gains
  the declaration, the assembly and the record; the manifest transcript is real and I
  reproduced its inputs.
- **Constraints not violated:** confirmed independently. `delivery-not-use` (no file bytes in
  the record, no use vocabulary as code); `no-globs-order-is-content` (AST + booby-trapped
  behavioural); `windows-corpus` (`newline="\n"` on every text write, AST + behavioural);
  `extend-dont-parallel` (one import at `:50`, one call at `:243`, zero `def active_id`,
  engine byte-unchanged); `no-foreclosure` (row stays `{root, path, rev}`).
  `markdown-in-git` is honoured, but see MAJOR-2 — it is now *newly relied on* by `rev()`, and
  the reliance is stated more narrowly than it actually is.
- **Notes match the diff:** yes, including the honest under-claim that the engine needed no
  edit at all.
- **Decision candidates surfaced:** yes, and well. `decision:producer-is-a-sibling-module` was
  graded `guess` with the settle condition "if the import seam creates a second effective
  selector, inline it into `checklist_engine.py` instead"; the implementer ran the settle
  experiment, pinned it with a test, and regraded to `settled/measured`. That is the
  mechanism working as designed. Two new decisions were taken within latitude and logged
  (glob metacharacter raises; `required` is declaration metadata only) — I agree with both;
  the first is the same instinct MINOR-3 asks to extend one step further.
- **Durable context routed:** yes — four triage candidates flagged on the survey (`tc1`–`tc4`).

## Reconciliation check

`no divergence Commander must reconcile.` I confirmed both self-reported map-confidence items
at their source: `durable_root()` does return the worktree under an Admiral lease (so
`.agent-work/LESSONS.md` honestly records `rev: null`), and `context_manifest.py` appears
nowhere in `scripts/install_constellation.py` — the per-role script tuples at `:105-119` do
not name it, so the producer ships to the source repo but to no installed skill tree. Correct
for #300 (no caller yet), a real gap for #301.

## My call on the latent silent-skip (handoff hunt 3)

The handoff asked me to judge whether `unittest.SkipTest` on `git worktree add` failure is an
acceptable degradation or should be a hard failure. **My call: acceptable as written — but for
a reason the implementer did not rely on, and with one gate-command change.**

It is acceptable because this repo already owns the rail that closes it. In CI, a
`DeterministicAcrossEnvironments` skip can *never* pass `verify_skip_guard.py`: the class is
not on `ALLOWED_SKIPS`, and its message interpolates git's stderr, so the triple is not even
expressible as an allow-tuple. A worktree-add failure is therefore a **hard CI failure**, not
a silent green. Converting it to a hard `self.fail()` would buy nothing in CI and would break
a legitimate local run on a host without git.

What is *not* covered is the local path: the g1 gate command
`python -m pytest tests/test_context_determinism.py -q` would still read exit 0 with all 7
tests skipped. **Recommendation:** have the gate assert the count (`-q` output contains
`7 passed`) or run the junit + skip-guard pair, rather than trusting exit 0. That is a gate
wording change, not a code change.

Ironically, the same rail that makes this acceptable is the one BLOCKER-1 trips — the
implementer reasoned about `SkipTest` carefully in one test file and not at all in the other.

## Out-of-scope observations

- **`tc1`** — `scripts/context_manifest.py` is in no role's install bundle. #301's first real
  caller must add it or the producer will not exist at the seat it runs from. *(Confirmed
  independently; the implementer surfaced this and was right.)*
- **`tc2`** — the `durable` root token is a null-producer while an Admiral lease is active.
  Worth naming in #301's design rather than discovering later.
- **`tc3`** — the `.gitattributes` gate check cannot pin what it claims to pin (MAJOR-2). A
  content-level guard over the declarable roots would.
- **`tc4`** — the `-k 'no_globs or newline_pinned or py312_compatible'` gate is coupled to test
  names; a rename silently converts a real check into an exit-5 failure. An explicit node-id
  list would be sturdier. *(Implementer's observation 5; I agree.)*
- Case-insensitive path resolution on Windows means `REFERENCES/DOCTRINE.MD` resolves to a
  real `rev` here and would resolve to `null` on Linux. Genuinely outside the determinism
  test's stated same-OS limit, and correctly stated as a limit — noting it only so a later
  cross-OS claim is not made by accident.
- `contract` vs the engine's `_STATE_CONTRACT_VERSION`: both read `1`, are independent, and
  the naming + comment are the right mitigation. Nothing mechanically prevents a downstream
  store conflating them. Accepted as-is for g1.

## Workflow Feedback

- **Handoff gaps:** one, and it is the reason BLOCKER-1 exists rather than being caught
  upstream. The handoff's Constraints section names the CI-pins-3.12 hazard in detail ("a
  sibling issue in this epic shipped a red CI on exactly that") but never mentions that CI
  also runs `scripts/verify_skip_guard.py` and **fails the build on any undocumented skip**.
  That rail is invisible from the handoff, from the g1 evidence list, and from the
  verification-command block — all of which stop at `python -m pytest tests/ -q`, the one
  command that cannot see it. Both the implementer and I had to discover it by reading
  `.github/workflows/ci.yml`. It should be a named constraint and a verification command:
  `python -m pytest tests/ -q --junitxml=junit-report.xml && python scripts/verify_skip_guard.py junit-report.xml`.
- **Context rediscovered:** (a) that CI checkouts have no `.agent-work` at all, which is what
  makes a `.agent-work`-conditional `skipTest` a CI-only failure — nothing in the handoff's
  Deliverable Path Check connects "intentionally gitignored" to "therefore absent in CI",
  though it states the first half explicitly; (b) git's *content-driven* normalisation
  exemptions (NUL auto-binary, lone CR), which the `.gitattributes` invariant is written as
  if it covered; (c) the source-vs-installed skill layout, which the implementer also flagged.
- **Instructions improvised around:** the reviewer skill and `global-everyone.md` both say
  `advance` is the verb that moves a checklist on, and the SKILL text says "integrate it,
  `advance` that check". On a `survey` the engine REFUSES `advance` ("advance is for gated
  checklists; use record") — `record` both records and advances. Minor, but it costs a
  refused call on every survey run. The skill's own §3 wording should say `record` for
  surveys.
- **What would have made this easier:** one line in the handoff's Constraints —
  *"CI also runs `verify_skip_guard.py`: any new `skipTest` that can fire on a clean checkout
  fails the build, so a test conditional on `.agent-work` must not skip."* That single sentence
  is the whole of BLOCKER-1.

## Return status
`complete`
