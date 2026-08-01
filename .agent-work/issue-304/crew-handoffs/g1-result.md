# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

> **Revision 2 — rework after reviewer BLOCK.** B1 (blocker), B2 (major) and B3 (minor) are fixed;
> see **[Rework](#rework--revision-2)** at the top of the evidence. Every figure in this document is
> a revision-2 figure. The three adjudicated deviations are unchanged, and the two triaged findings
> were left alone as instructed.

## Assigned gate
`issue-304 g1 — resolver, receipt, reported degraded mode`

## Completed slice

Built `scripts/map_orient.py` (`orient`, `verify-orientation`, `--self-test`), added the
`<repo-root>` placeholder to `scripts/init_work_area.py`, and shipped two test files including an
**executed** mutation floor in which all **five** named mutations are demonstrably killed.

Engine-driven end to end: plan at `.agent-work/issue-304/g1-implementer-plan.json`, six items
`m0-context → m1 → m2 → m3 → m4 → m5`; session `impl-g1-304` for revision 1, then `m2` **reopened**
through the engine for the rework (`rework 1/3`, cascade-resetting `m3`/`m4`/`m5` and superseding
their evidence) and re-driven under session `impl-g1-304-rework`.

## Scope

**Files changed:**
- `scripts/map_orient.py` (new, 1137 lines)
- `tests/test_map_orient.py` (new — the floor)
- `tests/test_mutation_floor.py` (new — executed falsifiability)
- `scripts/init_work_area.py` (modified — `<repo-root>` placeholder + guard only)
- `tests/test_init_work_area.py` (modified — **scope stretch**, see Deviations)

```
 scripts/init_work_area.py    | 29 +++++++++++++++++-------
 tests/test_init_work_area.py | 53 ++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 74 insertions(+), 8 deletions(-)
?? scripts/map_orient.py
?? tests/test_map_orient.py
?? tests/test_mutation_floor.py
```

**Specific exclusions touched:** `no`.
- No `verify-frame` (g2). No template wiring (g2). No prose deleted (g3). No bootstrap/CLAUDE.md
  stanza. The five fragile relative checks (#341) untouched; episode store (#342) untouched;
  `checklist_engine.py` untouched.
- `C:/Programs/f1Brainz` stayed **read-only**: it was read to ground the resolver, through the
  module's *pure* functions only, so no receipt and no `.agent-work/` entry was written there
  (`find C:/Programs/f1Brainz -name map-orientation.json` → empty; its `.agent-work/` is its own
  pre-existing dogfood directory with June/July mtimes). No git operations were run in it.
- Never touched `C:/Programs/constellation-skills` or `C:/Programs/constellation-skills-wt/e298-331`.

## Behavior changed

`yes`.

- New capability: a repo can be *oriented* against its architecture map, and — the load-bearing half —
  a repo that **cannot** be oriented says so on stdout with a reserved literal and on the exit code
  with a semantic value, instead of degrading silently.
- `orient` on a degraded repo with no declarations exits **10**, not 0. Degrading is fine; degrading
  silently is refused.
- `init_work_area.resolve_spine` now resolves `<repo-root>`, and the unresolved-placeholder guard owns
  the token so a regressed resolver cannot ship it literal.

---

## The exit-code table I chose, and why it avoids the collision

| code | meaning |
|---|---|
| `0` | contract satisfied — `RESOLVED`, **or** a `DEGRADED` record fully discharged |
| `10` | `DEGRADED` and **not** discharged — missing/filler `substitutes`, `unmapped`, or `escalation` |
| `11` | `UNRESOLVABLE-ROOT` — *could not look*: `--root` is not a proven repo root |
| `12` | the receipt is missing or unusable (`verify-orientation`) |
| `13` | `--self-test` falsification floor failed |

**Why it avoids a real collision.** Three codes are already spoken for by machinery this module does
not control: `argparse` exits **2** on a usage error, an unhandled traceback exits **1**, and the
engine synthesizes **127** when no POSIX shell is found (**126** = found-but-not-executable is
adjacent and equally not ours). Because the engine records only `{cmd, exit, shell}` and **discards
stdout**, the exit code is the *only* signal that survives downstream — so a mistyped flag must never
be indistinguishable from a truthful verdict.

Every semantic code therefore sits in the unoccupied band **`2 < code < 126`**: strictly above
traceback/argparse, strictly below the shell range. `0` is the only success code. Nothing this module
returns can be confused with `1`, `2`, `126`, or `127`. This is asserted mechanically in two places, so
it cannot rot:

- `map_orient.self_test()` — *"semantic codes avoid the argparse/traceback/shell range"*
- `tests/test_map_orient.py::ContractShape::test_semantic_exit_codes_avoid_the_argparse_traceback_shell_collision`

and the negative side is asserted too:
`test_a_usage_error_exits_two_and_is_not_a_verdict` runs `map_orient.py orient --no-such-flag`, asserts
exit `2`, and asserts `2 ∉ SEMANTIC_EXIT_CODES`.

---

## Design notes on the two load-bearing rules

**RESOLVED requires citable content, not file existence.** Anchors come from a format-agnostic token
scan, `\b(struct|capability|event|constraint|assumption|claim|decision):[A-Za-z0-9_.\-]+\b`. A
`<placeholder>` cannot match because `<` is outside the id character class, so a scaffolded template
yields nothing and reads `DEGRADED-UNPARSEABLE`. Measured, before writing any code:

- `skills/cartographer/templates/ARCHITECTURE_INDEX.template.md` → **0** anchors
- `C:/Programs/f1Brainz/docs/architecture/index.md` → **76** unique anchors
- `C:/Programs/f1Brainz/docs/architecture/packets/physics.md` → **58** unique anchors

I independently confirmed the handoff's warning about the strict parser rather than taking it on
trust: `build_architecture_map.parse_packet` raises
`MapBuildError: ... missing required field: structural node` on **all 16** f1Brainz packets (**0
parsed / 16 failed**) because f1Brainz writes YAML fences while this repo's template uses bold fields.
Coupling to it would have returned zero nodes on the one repo that has a real map. Not coupled.

**Could-not-look vs looked-and-found-nothing.** `UNRESOLVABLE-ROOT` needs a *positive* proof to fail:
`.git` present at the root, **or** `git -C <root> rev-parse --show-toplevel` succeeding **and naming
that same root**. The second clause matters — without the identity comparison, any subdirectory of any
repo would prove itself a repo root, and the discriminator test's tmpdir would be at the mercy of
wherever it happened to be created.

**Degraded is the common case, so it got the design attention.** The degraded record is discharged only
with `substitutes` **AND** `unmapped` **AND** `escalation` — all three, fillers (`""`, `"none"`,
`"n/a"`, `"tbd"`, `<placeholder>`, …) rejected, an empty `substitutes` list treated as a refusal, and a
substitute whose content hash is not a real sha256 treated as a refusal (**revision 2** -- revision 1
checked only that the hash was non-empty, which a sentinel satisfied; that was B1). Substitutes are
**hash-pinned** (sha256 of
content) so g2's frame check compares against a committed prior declaration rather than a same-breath
assertion. `orient` gained `--substitute` / `--unmapped` / `--escalation` so the tool computes the
hashes — the two-bin rule: the hash is mechanizable, the *content* of the declaration stays prose.

---

## Test mode

**Required:** `test-first` (the handoff's mutation floor makes falsifiability the deliverable)
**Satisfied:** `yes` — `tests/test_map_orient.py` was written and run **before** `verify-orientation`
and the discharge predicates existed, and observed red; see TDD evidence below.

---

## Rework — revision 2

Three findings from the reviewer's BLOCK. I reproduced **B1 and B2 myself before changing anything**;
both were real and both were mine.

### B1 — BLOCKER, fixed: an unreadable substitute discharged the record

**Reproduced first, verbatim:**

```
##### B1 REPRO #####
orient EXIT=0
verify EXIT=0
receipt substitutes: [{"path": "docs/THIS_FILE_DOES_NOT_EXIST.md", "content_hash": "unreadable"}]
```

**Root cause.** `pin_substitutes` wrote the sentinel `content_hash="unreadable"` when it could not
read a path, and `substitutes_declared` only asked *"is this non-filler?"* — which a non-empty
sentinel satisfies. A single typo in a substitute path therefore discharged the entire degraded
record at exit 0. This is exactly the hole the contract exists to close, it contradicted my own
revision-1 report, and it defeated the hash-pinning g2 depends on. No defence — it shipped broken.

**Fix, in two independent halves so neither alone can regress it:**

1. `pin_substitutes` now records `content_hash: null` for an unreadable path. **No sentinel.**
2. New pure predicate `is_content_hash` validates the pin by **shape** —
   `CONTENT_HASH_RE = ^[0-9a-f]{64}$` — so no sentinel, typo, or truncated digest can stand in for a
   pin, including in a hand-written receipt. (`"unreadable"` was also added to `FILLER_VALUES` as a
   third, belt-and-braces layer.)

New `substitute_problems()` names the offending entry rather than failing anonymously.

**Same repro, after the fix:**

```
##### B1 REPRO, POST-FIX #####
DEGRADED-NO-MAP
root: C:/Programs/constellation-skills-wt/e298-304
root proof: positive: .git entry present at root
entrypoint: (none)
anchor_count: 0
candidates tried:
  [1] generated-map: docs/architecture/generated/map.json -> absent (absent)
  [2] index: docs/architecture/index.md -> absent (absent)
  [3] packets-dir: docs/architecture -> absent (absent)
receipt: .agent-work/b1probe/map-orientation.json
degraded and NOT discharged -- still owed:
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  -     substitutes[0] 'docs/THIS_FILE_DOES_NOT_EXIST.md' is not hash-pinned (content_hash=None) -- an unreadable or nonexistent substitute cannot discharge the record
orient EXIT=10
--- verify ---
DEGRADED-NO-MAP
receipt: .agent-work/b1probe/map-orientation.json
degraded record INCOMPLETE -- substitutes AND unmapped AND escalation
problems: 2
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  -     substitutes[0] 'docs/THIS_FILE_DOES_NOT_EXIST.md' is not hash-pinned (content_hash=None) -- an unreadable or nonexistent substitute cannot discharge the record
verify EXIT=10
--- receipt ---
[{"path": "docs/THIS_FILE_DOES_NOT_EXIST.md", "content_hash": null}]
```

**Pinned by** the new `UnreadableSubstitute` class (6 tests), which carries the reviewer's exact
repro (`test_a_nonexistent_substitute_path_refuses`), the sentinel/typo/truncation matrix, a test
that the refusal *names* the offending path, and — importantly — a **positive control**
(`test_one_real_substitute_still_discharges`) so the fix cannot degenerate into refusing everything.

### B2 — MAJOR, fixed: a surviving mutation, and the gap that let it survive

**Reproduced first.** The reviewer's M4 (`unmapped_declared`'s `not any(is_filler)` →
`not all(is_filler)`) applied cleanly and the floor stayed green:

```
##### B2 REPRO (M4) #####
anchor occurrences in shipped module: 1
M4 floor exit: 0 | passed: 42 | failed nodes: []
VERDICT: MUTANT SURVIVED - reviewer is right
```

**Cause, confirmed exactly as diagnosed.** Every filler case in both `self_test` and
`PartialFillMatrix` used a **single-element** list — and on a list of length 1, `any` and `all` are
the same function. The floor was structurally incapable of telling them apart. That is a genuine
hole in my floor, and the honest reading is that my revision-1 claim of falsifiability was scoped
narrower than I presented it: the three mutations I chose were killed, but I had not shown the floor
was sensitive to mutations I did *not* choose. Finding one is the point of an independent reviewer.

**Fix.**
1. Multi-element cases added at both levels —
   `PartialFillMatrix.test_one_filler_poisons_a_multi_element_unmapped_list` over
   `["none", real]`, `[real, "n/a"]`, `["none", "n/a"]`, `[real, "", real]`, plus an all-real
   positive control `test_a_multi_element_unmapped_list_of_real_entries_passes`, and the same
   divergent cases in `self_test`.
2. **M4 is now pinned in the shipped mutation set** so it stays killed.
3. The same single-element blind spot applied to the `substitutes` loop, so
   `test_one_unpinned_substitute_poisons_a_multi_element_list` was added there too (one bad entry
   among good ones must sink the declaration).

**Judgment call to flag:** I also pinned a **fifth** mutation, M5 — weakening `is_content_hash` back
to `bool(value.strip())` — so the B1 blocker itself cannot silently return. B2 asked only for M4, so
this is one item beyond the letter of the rework scope. It is cheap and directly guards the blocker;
strike it if you would rather hold the line on scope.

**Post-fix, all five mutations killed**, each with a failure in its intended class:

```
shipped mutation set: 5

### degraded-completeness `all` -> `any`
    exit=1 passed=42 killers=14 in-target=10
      - tests/test_map_orient.py::PartialFillMatrix::test_filler_escalation_is_refused
      - tests/test_map_orient.py::PartialFillMatrix::test_filler_substitute_path_is_refused
      - tests/test_map_orient.py::PartialFillMatrix::test_filler_unmapped_is_refused
### UNRESOLVABLE-ROOT collapsed into DEGRADED-NO-MAP, exiting 0
    exit=1 passed=39 killers=16 in-target=2
      - tests/test_map_orient.py::CouldNotLookDiscriminator::test_bare_directory_and_the_same_directory_with_git_differ_in_one_bit
      - tests/test_map_orient.py::CouldNotLookDiscriminator::test_unresolvable_root_is_not_a_degraded_verdict
### citable-content requirement weakened to mere existence
    exit=1 passed=41 killers=10 in-target=3
      - tests/test_map_orient.py::CitableContent::test_an_existing_but_empty_index_is_never_resolved
      - tests/test_map_orient.py::CitableContent::test_placeholder_ids_are_not_citable
      - tests/test_map_orient.py::CitableContent::test_the_shipped_index_template_itself_does_not_resolve
### unmapped filler check `not any` -> `not all`
    exit=1 passed=50 killers=2 in-target=1
      - tests/test_map_orient.py::PartialFillMatrix::test_one_filler_poisons_a_multi_element_unmapped_list
### an unreadable substitute accepted as a hash pin
    exit=1 passed=49 killers=3 in-target=2
      - tests/test_map_orient.py::UnreadableSubstitute::test_a_hash_pin_must_be_a_real_sha256
      - tests/test_map_orient.py::UnreadableSubstitute::test_a_sentinel_content_hash_in_a_handwritten_receipt_refuses
```

M4 is killed by exactly the test written for it, and was survived-then-killed across the fix —
the strongest available evidence that the new case is what closes the gap.

### B3 — MINOR, accepted and corrected

**The claim is withdrawn.** Revision 1 said `.agent-work/probe/` "was removed after capture"; you
found it on disk. Whatever the mechanism, **an assertion in an evidence artifact that the reader
finds to be false is a defect**, and it is the same failure class as the one this gate is about. It
should not have been written the way it was.

What I can actually establish, stated with its limits: my run did issue the `rm -rf` and its
follow-up `git status --short` listed no `probe` entry, so the directory was gone at that instant.
It was on disk when you looked. The most likely mechanism is that **running the evidence command in
section 3 recreates it** — which is exactly what independently verifying my evidence involves — and
I saw corroboration for that pattern during this rework: a `.agent-work/pollprobe/` I did not create
was present in the tree. I cannot prove that is what happened, and I am not offering it as an
excuse; the lesson stands either way.

**The real error** was writing a cleanup assertion into an artifact whose own pasted evidence command
recreates the very thing being asserted about. That claim was unverifiable by construction. So the
artifact now states only what is verifiable, and the section-3 note has been rewritten accordingly.

Verified at the time of writing this revision (after all rework evidence was captured):

```
$ ls .agent-work/ | grep -iE "probe"
(no probe dirs)
$ git status --short
 M .agent-work/issue-304/g1-implementer-plan.json
 M .agent-work/issue-304/g1-implementer-plan.json.journal
 M scripts/init_work_area.py
 M tests/test_init_work_area.py
?? scripts/map_orient.py
?? tests/test_map_orient.py
?? tests/test_mutation_floor.py
```

Anyone re-running the section-3 or B1 commands will recreate `.agent-work/<work-id>/`; that is the
command's designed effect, not residue. (The reviewer's separate recommendation of a `--receipt-dir`
flag is triaged and deliberately not implemented here.)

---

## Evidence

### 1. Required-evidence suite

```bash
cd C:/Programs/constellation-skills-wt/e298-304
python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_init_work_area.py -q
```

```
...........................................................................................                [100%]
91 passed, 38 subtests passed in 74.95s (0:01:14)
```

**Result:** `pass`

### 2. Self-test falsification floor

```bash
python scripts/map_orient.py --self-test
```

```
self-test OK
EXIT=0
```

**Result:** `pass` — 92 checks (counted by instrumenting `_check`), covering the exit vocabulary, the
anchor scan (including placeholder rejection and the real shipped template), citability-not-existence,
positive root proof, all four verdict paths, first-hit-wins ordering, the classifiers, the three-way
discharge predicate, and every `verify-orientation` verdict.

### 3. The live degraded verdict in this repo

```bash
python scripts/map_orient.py orient --root C:/Programs/constellation-skills-wt/e298-304 --work-id probe
```

stdout:
```
DEGRADED-NO-MAP
root: C:/Programs/constellation-skills-wt/e298-304
root proof: positive: .git entry present at root
entrypoint: (none)
anchor_count: 0
candidates tried:
  [1] generated-map: docs/architecture/generated/map.json -> absent (absent)
  [2] index: docs/architecture/index.md -> absent (absent)
  [3] packets-dir: docs/architecture -> absent (absent)
receipt: .agent-work/probe/map-orientation.json
```

stderr:
```
degraded and NOT discharged -- still owed:
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  - unmapped (what stayed unmapped, stated plainly)
  - escalation (what you are escalating, and to whom)
```

```
EXIT=10
```

**Result:** `pass` — the real degraded verdict in the live degraded repo. Note this is a **reported**
degradation: reserved literal on stdout, semantic `10` on the exit code, and the receipt names exactly
what is still owed. **Note:** re-running this command recreates `.agent-work/probe/` -- that is the
command's designed effect. See [B3](#b3--minor-accepted-and-corrected); revision 1 wrongly asserted a
cleanup here.

Receipt written by that run:

```json
{
  "schema_version": 1,
  "work_id": "probe",
  "root": "C:/Programs/constellation-skills-wt/e298-304",
  "mode": "DEGRADED-NO-MAP",
  "entrypoint": null,
  "anchor_count": 0,
  "candidates_tried": [
    { "order": 1, "kind": "generated-map", "path": "docs/architecture/generated/map.json",
      "exists": false, "outcome": "absent", "anchor_count": 0, "note": "absent" },
    { "order": 2, "kind": "index", "path": "docs/architecture/index.md",
      "exists": false, "outcome": "absent", "anchor_count": 0, "note": "absent" },
    { "order": 3, "kind": "packets-dir", "path": "docs/architecture",
      "exists": false, "outcome": "absent", "anchor_count": 0, "note": "absent" }
  ],
  "substitutes": [],
  "unmapped": [],
  "escalation": null,
  "emitted_at": "2026-08-01T22:44:01.722248+00:00",
  "root_proof": "positive: .git entry present at root"
}
```

And the gate check on that undischarged receipt:

```bash
python scripts/map_orient.py verify-orientation --root C:/Programs/constellation-skills-wt/e298-304 --work-id probe
```

```
DEGRADED-NO-MAP
receipt: .agent-work/probe/map-orientation.json
degraded record INCOMPLETE -- substitutes AND unmapped AND escalation
problems: 3
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  - unmapped (what stayed unmapped, stated plainly)
  - escalation (what you are escalating, and to whom)
EXIT=10
```

### 4. Executed mutation floor — all FIVE named mutations demonstrably killed

```bash
python -m pytest tests/test_mutation_floor.py -q
```

```
.........                                                          [100%]
9 passed, 6 subtests passed in 66.87s (0:01:06)
```

Per-mutation detail for the revision-2 set of **five** is pasted verbatim in
[B2](#b2--major-fixed-a-surviving-mutation-and-the-gap-that-let-it-survive) above and is not repeated
here. Every mutation exits 1, leaves 39-50 tests still passing (so no kill is a disguised import
break), and fails at least one test in the class it was supposed to break.

The harness's own loud-failure path, exercised directly:

```
### harness self-check: a non-matching substitution
    HarnessError raised: HARNESS ERROR: mutation 'x' did not apply -- the anchor text occurred 0 time(s), expected exactly 1. The module was edited without updating this harness. This is NOT a killed mutant.
```

#### How the applied-before-red rule is enforced (the handoff's most-weighted line)

`_assert_mutation_is_killed` runs **STEP 1 — prove it applied** before **STEP 2 — compare**:

1. `apply_mutation` refuses loudly: an anchor matching `!= 1` times raises `HarnessError`, whose text
   says *"This is NOT a killed mutant."* Two `HarnessSelfCheck` tests prove that path fires (a
   non-matching anchor, and an ambiguous anchor).
2. The test then asserts `mutated != ORIGINAL`.
3. Per substitution: `ORIGINAL.count(old) == 1`, `mutated.count(old) == 0`, and
   `mutated.count(new) == ORIGINAL.count(new) + 1`.
4. It re-reads the copy from disk and asserts it equals the mutated source.

**The count delta in (3) is not pedantry — it is load-bearing here concretely.** Mutation 2's
replacement text `    return EXIT_OK` **already appears elsewhere** in `map_orient.py`. A plain
`assertIn(new, mutated)` would have passed even if nothing had been substituted at all. Only the
`+1` delta actually proves the change landed.

Two further guards stop a *false* kill:

- `passed_count(proc) > 0` — a mutation that merely broke the import would leave zero passing tests,
  so a red-for-the-wrong-reason cannot be counted as a kill.
- at least one `FAILED` node must be in the class the mutation was *supposed* to break
  (`PartialFillMatrix`, `CouldNotLookDiscriminator`, `CitableContent` respectively).

And `test_0_unmutated_baseline_is_green` asserts the unmutated copy passes its own floor **first**, so
a red below is attributable to the mutation rather than to the harness.

### 5. No regressions in the wider suite

```bash
python -m pytest tests/ -q
```

```
1470 passed, 2 skipped, 448 subtests passed in 168.90s (0:02:48)
```

---

## TDD evidence

- **Failing test observed** — `tests/test_map_orient.py` written and run *before* `verify-orientation`
  and the discharge predicates existed:

  ```
  24 failed, 28 passed, 9 subtests passed in 4.89s
  ```

  Every failure was in the arms that did not yet exist — `PartialFillMatrix` (all arms),
  `VerifyOrientation` (all), `ContractShape::test_first_stdout_line_is_always_a_reserved_literal`
  (`'' not found in (...)` — `verify-orientation` printed nothing because the subcommand did not
  exist) — plus one test of mine with a wrong expected anchor count (`5`, actual `4`), which I
  corrected.

- **Passing test observed** — after implementing (revision-2 figure; revision 1 was
  `42 passed, 22 subtests`):

  ```
  51 passed, 32 subtests passed in 8.36s
  ```

- **Rework red observed (revision 2)** — the B1 and B2 reproductions above were run against the
  shipped module *before* any fix, and both showed the defect: `orient` exit `0` / `verify` exit `0`
  on a nonexistent substitute, and M4 surviving at `floor exit 0, 42 passed, 0 failed`. The new
  `UnreadableSubstitute` tests and the multi-element cases were written against that failing
  behavior, then went green.

- **Refactor while green:** `yes` — `receipt_problems` was corrected while green so that an
  `UNRESOLVABLE-ROOT` receipt's legitimately-empty `candidates_tried` is not flagged as a malformed
  receipt (see Assumptions).

- **Independent falsification of the `<repo-root>` test** — mutating the resolver back to
  `str(Path(root).resolve())` in memory makes the new json-safety test go red:
  `json.loads FAILS -> test goes RED as intended: Invalid \escape: line 1 column 19 (char 18)`.
  The test is not one that cannot fail.

---

## Map Impact

This repo has no `docs/architecture/` (that is precisely what `test_this_repo_resolves_degraded`
asserts), so there are no inbound Map Anchors to frame against. Recorded as candidates only.

- **Structural anchors touched:** none existing. New: `scripts/map_orient.py`, a module-level node
  under the repo's `scripts/` tooling surface, peer to `scripts/verify_state_note.py` and the other
  `verify_*.py` gate checks.
- **Capabilities added:** *map orientation with a reported degraded mode* — resolve an architecture-map
  entrypoint by an ordered candidate list, emit a hash-pinned receipt, and gate the degraded record.
  Observable via the `orient` / `verify-orientation` exit contract.
- **Constraints/assumptions touched:** newly relied on — the engine records only `{cmd, exit, shell}`
  and discards stdout, which is the entire reason the exit-code table is a frozen contract. Also newly
  relied on: `docs/architecture/{generated/map.json,index.md,packets/*.md}` is the map layout
  (matches `skills/cartographer/templates/` and f1Brainz).
- **Decision candidates:** (a) the semantic exit band `10-13`, chosen to clear `1`/`2`/`126`/`127`;
  (b) the anchor token scan is deliberately **decoupled** from `build_architecture_map.parse_packet`
  — grounded on the measurement that the strict parser returns 0/16 on f1Brainz; (c) `<repo-root>`
  emits `as_posix()`, not `str(Path)` — see Deviations.
- **Claims/evidence produced:** `build_architecture_map.parse_packet` parses **0 of 16** f1Brainz
  packets; this repo is `DEGRADED-NO-MAP`; f1Brainz is `RESOLVED` at `docs/architecture/index.md` with
  76 anchors, with the `packets-dir` candidate still recorded after the `index` candidate hit (the
  delivery-record property, exercised on a real map).
- **Triage candidates:** see Out-of-scope observations.

## Docs/contracts touched
- None outside the code. The exit-code table, reserved stdout literals, receipt schema, and honest
  limits are documented in the `scripts/map_orient.py` module docstring, per house style. No template
  wiring (that is g2).

## Assumptions

- **`verify-orientation` reserved literals.** The handoff froze five literals for `orient`. A
  `verify-orientation` run with no usable receipt has no mode to report, so I added exactly one more
  reserved literal, `RECEIPT-MISSING`, rather than emitting a blank first line. `RESERVED_FIRST_LINES`
  is the union; `ORIENT_MODES` remains exactly the five.
- **An `UNRESOLVABLE-ROOT` receipt has an empty `candidates_tried`,** and that is the *truthful*
  record — we never looked. Receipt well-formedness therefore exempts that one mode from the
  non-empty-candidates rule; otherwise an honest could-not-look receipt would verify as `12`
  (receipt unusable) instead of `11`.
- **The agent discharges via `orient`'s declaration flags**, not by hand-editing the receipt, so the
  tool computes the hash pins. Hand-edited receipts still verify correctly; the flags are the
  supported path.

## Deviations from the handoff

1. **`<repo-root>` resolves to `Path(root).resolve().as_posix()`, not the literal
   `str(Path(root).resolve())` the handoff specified.** `str()` is broken on Windows and I have direct
   evidence: a spine is JSON and `instantiate_spine` runs `json.loads(resolved)` on its own output, so
   a `str(Path)` value embeds backslashes and that guard raises. Measured:

   ```
   str(Path.resolve())       -> 'C:\\Programs\\constellation-skills-wt\\e298-304'
                                json.loads FAILS: Invalid \escape: line 4 column 24 (char 52)
   Path.resolve().as_posix() -> 'C:/Programs/constellation-skills-wt/e298-304'
                                json.loads OK
   ```

   `as_posix()` is also the right form for the POSIX shell the engine runs command checks under.
   Pinned by `test_repo_root_is_json_safe_on_windows`.

2. **Scope stretch: I added a 5-test `RepoRootPlaceholder` class to `tests/test_init_work_area.py`.**
   The allowed-scope list named that file for `scripts/` changes only and did not authorize editing the
   test file — but the handoff's required-evidence command runs it, and shipping an untested
   placeholder is not defensible. The change is purely additive (26 → 31 tests); no existing test was
   modified. Flagging rather than assuming.

3. **`orient` gained three optional flags** (`--substitute`, `--unmapped`, `--escalation`) beyond the
   synopsis' `[--entrypoint REL]`. Required by the handoff's own instruction to hash-pin substitutes:
   if the agent hand-writes the receipt, the tool never computes the hash. Two-bin rule — the hash is
   mechanized, the declaration's content stays prose.

## Stop conditions hit
- `none` — the resolver distinguishes could-not-look from looked-and-found-nothing without changing
  the exit contract (`11` vs `10`); the mutation harness can and does assert a mutation applied; no
  required test had to be written so it cannot fail.

## Out-of-scope observations

- **Observation (revision 2, no action) — the `substitutes` loop had the same single-element blind
  spot as `unmapped`.** B2 was reported against `unmapped_declared`, but the substitutes check is the
  same shape, so I added `test_one_unpinned_substitute_poisons_a_multi_element_list` while fixing B1.
  A *general* lesson worth carrying past this gate: **any predicate that quantifies over a list needs
  a multi-element case**, because `any` and `all` are indistinguishable on lists of length one. That
  is a floor-design rule, not a fact about this module.
- **Triage candidate — `orient` writes `.agent-work/<work-id>/` into a directory that failed the repo-root
  proof.** On `UNRESOLVABLE-ROOT` the receipt is still written when the path is a directory, because the
  delivery record is the point. It is arguably rude to scaffold `.agent-work/` inside something we just
  declared is not a repo. Deliberate for now (the receipt *is* the report); worth a ruling.
- **Triage candidate — `docs/agents/engine-config.json` does not exist**, yet `spine.json`,
  `execute.json`, and the implementer plan template all carry `config_ref` pointing at it. The engine
  tolerates it silently, so every run in this repo is on defaults without saying so. That silence is
  the same class of defect this issue is about.
- **Observation (no action) — `_resolve_skill_dir_token` substitutes `--skill-dir` verbatim.** An
  absolute Windows `--skill-dir` would hit the same JSON-escape failure I fixed for `<repo-root>`.
  Pre-existing, not in scope, not touched.

## Workflow Feedback

- **Handoff gaps:** the **test mode** field was never stated explicitly. I inferred `test-first` from
  "the mutation floor" being a named deliverable and from the crew-doctrine default, and drove it that
  way, but the implementer plan template has a `test mode` slot and the handoff has no field feeding
  it. Second: the deliverable-1 synopsis froze the CLI as `orient --root --work-id [--entrypoint]`
  while a later paragraph required hash-pinned substitutes — those two cannot both be literally true,
  since nothing in the frozen synopsis lets the agent *declare* a substitute for the tool to hash. I
  resolved it toward the semantic requirement and flagged it; a synopsis line saying "flags may be
  added where the contract requires them" would have removed the guess.
- **Context rediscovered:** (a) `docs/agents/CREW_CONTEXT.md` and `GLOSSARY.md` do not exist in this
  repo, so the crew-doctrine context step is global-only — worth one line in the handoff, since the
  plan template's `m0` imperative names both files as if they were there. (b) The house-style bullet
  named `_utf8_stdio()` and `--self-test` as conventions, but **no** script in `scripts/` currently has
  a `--self-test`; the only prior art is
  `.agent-work/epic-298/baselines/extract_ordering.py`, which I had to go find. A pointer would have
  saved a search. (c) The `<repo-root>` justification was carefully corrected in the handoff, but the
  *value expression* it specified is broken on the platform the constraints section calls out as
  Windows — the two paragraphs were not reconciled.
- **Instructions improvised around:** nothing in the templates or the skill covered the fact that an
  `importlib`-loaded module needs `sys.modules[spec.name] = module` **before** `exec_module`, or a
  frozen `dataclass` raises `AttributeError: 'NoneType' object has no attribute '__dict__'` at class
  creation on Python 3.14. Every existing `tests/test_*.py` in this repo uses the `importlib` loader
  pattern *without* that line, so any future test module that gains a dataclass will hit this. It cost
  me one failed run to diagnose. Worth a line in the crew Windows/platform reference.
- **Self-critique from the rework (revision 2), since it is the most useful signal here:** two of the
  three findings were failures of *my own* rigor, not of the handoff.
  - **B1** was a hole in the exact property I was assigned to protect, and I described the behavior
    correctly in my report while the code did something else. The generalizable cause: I validated a
    field by "is it non-empty" when the field has a *known shape*. Where a value has a checkable
    shape, check the shape.
  - **B2** is the sharper lesson. I demonstrated three mutations killed and presented that as
    falsifiability, but a floor is only as good as the mutations *someone else* devises. My three
    were the ones I could already see. The reviewer's M4 survived because of a structural blind spot
    — single-element lists — that I could not have found by picking my own mutations, because the
    same blind spot shaped both the code and the tests. **Executed falsifiability against a
    self-chosen mutation set systematically overstates itself**; the adversarial set is the one that
    matters. Worth carrying into the epic's doctrine, not just this gate.
- **What would have made this easier:** one concrete change — have the handoff state the **test mode**
  as a named field. Everything else in this handoff was unusually complete, and the three
  extra-weight items at the top of the dispatch (exit collision, citable content, applied-before-red)
  were exactly the three places where a careless implementation would have looked finished and been
  wrong.

## Return status
`complete`
