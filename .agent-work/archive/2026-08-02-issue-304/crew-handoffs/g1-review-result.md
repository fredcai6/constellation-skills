# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`issue-304 g1 — resolver, receipt, reported degraded mode`

## Result
`BLOCK`

One defect blocks. It is one line, it is in the gate's own protected intent, and it is untested.
Everything the handoff weighted heaviest — the exit-code collision, citable-content-not-existence,
the positive root proof, and applied-before-red — holds under independent execution.

Survey driven end to end through the engine: `.agent-work/issue-304/g1-review/review.json`,
session `rev-g1-304`, eight items (`r0` … `r6` plus an appended `r7-falsifiability`), consolidated
`verdict=BLOCK`. Fowler record: `.agent-work/issue-304/g1-review/fowler-pass.json`.

---

## THE QUESTION: CAN THIS CHECK FAIL?

**Yes — and I proved it by execution, not by reading.** But the floor is not airtight: **my own
mutation survived it.**

### 1. My own mutation (M4), not among the shipped three — **SURVIVED**

`unmapped_declared`, `scripts/map_orient.py:440`:

```
-    return not any(is_filler(entry) for entry in entries)
+    return not all(is_filler(entry) for entry in entries)
```

Driven through the shipped harness's own `apply_mutation` / `run_floor`:

```
MUTATION: M4 (reviewer): unmapped_declared `not any(filler)` -> `not all(filler)`
  applied: ORIGINAL.count(old)=1 mutated.count(old)=0 count(new) 0 -> 1
  source differs from original: True
  FLOOR exit=0  passed=42  failed_nodes=0
  >>> MUTANT SURVIVED -- the floor did NOT catch this. <<<
..........................................         [100%]
42 passed, 22 subtests passed in 4.84s
```

**Why it survives, and it is a real gap:** every filler case in *both* checks uses a **single-element**
list — `self_test()` at `map_orient.py:943` (`record["unmapped"] = [filler]`) and
`PartialFillMatrix::test_filler_unmapped_is_refused` at `test_map_orient.py:388`
(`unmapped=[filler]`). With one element, `any` and `all` are identical, so the per-entry filler rule
for **multi-entry** lists is pinned by nothing. Under the mutant,
`unmapped: ["src/ internals were never read", "n/a"]` discharges the record.

Narrow (the mutant still requires all three fields and still refuses an all-filler list), so this is
a **major observation, not the blocker** — but it is a genuine hole in a floor whose whole job is to
be a regression floor. Fix is one more test arm: a mixed list.

### 2. The shipped three are genuinely EARNED — verified semantically, not taken on trust

I did not rely on the harness's own kill report. I built each mutant and ran its CLI against real
fixtures to confirm it exhibits **wrong behavior**, not merely a crash:

```
### SHIPPED MUTATION 3 (citable -> exists): scaffolded-but-empty index
  ORIGINAL -> 'DEGRADED-UNPARSEABLE' exit=10
  MUTANT   -> 'RESOLVED'             exit=0    <-- FALSE RESOLVED == the real defect

### SHIPPED MUTATION 2 (UNRESOLVABLE-ROOT collapse): bare non-repo dir
  ORIGINAL -> 'UNRESOLVABLE-ROOT'    exit=11
  MUTANT   -> 'DEGRADED-NO-MAP'      exit=0    <-- 'could not look' sold as 'looked, found nothing'

### SHIPPED MUTATION 1 (all -> any): record carrying ONLY escalation
  ORIGINAL -> 'DEGRADED-NO-MAP'      exit=10
  MUTANT   -> 'DEGRADED-NO-MAP'      exit=0    <-- missing substitutes AND unmapped, DISCHARGED
```

Each mutant is importable, runs, and returns a *semantic* verdict that is wrong. The floor catches
all three. This is not #300: the check can fail, and it fails for the right reason.

### 3. The applied-before-red claim — **CONFIRMED, and stronger than reported**

The implementer claimed the count delta is load-bearing because *one* mutation's replacement text
already occurs elsewhere. Independently measured against the shipped module:

```
degraded-completeness `all` -> `any`
  anchor '    return all(checks)\n'          ORIGINAL.count(old)=1  ORIGINAL.count(new)=0
UNRESOLVABLE-ROOT collapsed into DEGRADED-NO-MAP, exiting 0
  anchor '        return MODE_UNRESOLVABLE_ROOT\n'                  ORIGINAL.count(new)=1  <-- pre-exists
  anchor '    return EXIT_OK if discharged else EXIT_DEGRADED_UNDISCHARGED\n'
                                                                    ORIGINAL.count(new)=2  <-- pre-exists
citable-content requirement weakened to mere existence
  anchor '    return candidate.anchor_count >= 1\n'                 ORIGINAL.count(new)=0

DEMONSTRATION: `new in ORIGINAL` (i.e. nothing substituted at all): True
  -> assertIn(new, ORIGINAL) would PASS. count-delta FAILS (2 != 2+1).
```

**Both** of mutation 2's substitutions have pre-existing replacement text, not one. `assertIn` would
have passed with nothing substituted. The count delta is doing real work. Claim verified true.

### 4. Attacking the harness — two attacks repelled, one succeeded

**Repelled — non-matching anchor.** Three realistic near-misses (a renamed predicate, a renamed
constant, a reflowed signature) all refuse loudly rather than reporting a mutant:

```
  renamed predicate: HarnessError -> HARNESS ERROR: mutation 'renamed predicate' did not apply -- the anchor text occurred 0 time(s), expected exac...
  renamed constant : HarnessError -> HARNESS ERROR: mutation 'renamed constant' did not apply  -- the anchor text occurred 0 time(s), expected exa...
  reflowed signature: HarnessError -> HARNESS ERROR: mutation 'reflowed signature' did not apply -- the anchor text occurred 0 time(s), expected exa...
```

**Repelled — the no-op mutation (`old == new`).** This is the sharpest version of the #300 failure:
`apply_mutation` accepts it (the anchor *does* occur exactly once), so the only thing standing
between it and a fraudulent kill is STEP 1:

```
  apply_mutation accepted it. mutated == ORIGINAL: True
  refused. 'HARNESS ERROR' in message: True
  'a red run would be a lie' in message: True
  reported as a killed mutant? False
```

`assertNotEqual(mutated, ORIGINAL)` catches it, and the count delta catches it a second time. The
applied-before-red rule is real and correctly ordered.

**SUCCEEDED — the kill criterion is CLASS-level, not REASON-level.** I replaced
`proof = probe_root(root)` with a bare `raise` — semantically unrelated to *any* pinned property,
and it produces no verdict at all:

```
MUTATION: ATTACK-A: crash cmd_orient outright (semantically unrelated to ANY property)
  applied: ORIGINAL.count(old)=1 mutated.count(old)=0 count(new) 0 -> 1
  FLOOR exit=1  passed=22  failed_nodes=25
  >>> KILLED. failing nodes: <<<
      - tests/test_map_orient.py::CitableContent::test_placeholder_ids_are_not_citable
      - tests/test_map_orient.py::CitableContent::test_the_shipped_index_template_itself_does_not_resolve
      ...
  node in expect_kills(CitableContent): True

  ATTACK-A mutant -> stdout=[] exit=1 (1 = traceback, NOT a semantic verdict)
```

All three guards are satisfied — red, `passed_count=22 > 0`, and a `CitableContent` node failed — so
the harness reports a **kill of the citable-content property that it did not earn**. The
`passed_count > 0` guard only catches a *total* import failure, not a partial collateral one.

**I am not blocking on this**, because it does not make the shipped three unearned — I verified those
independently in (2) above, behaviorally. It is a real limitation: the harness cannot self-detect a
*future* collateral kill, so a later refactor could silently convert a genuine kill into a hollow
one. Filed as triage candidate `tc2` with a concrete hardening (assert the mutant still returns a
semantic exit code on a smoke run before crediting a kill).

---

## Blockers

### B1 — `orient` reports "contract satisfied" (exit 0) on a substitute it could not read

`pin_substitutes` (`scripts/map_orient.py:719-730`) writes `sha256_of(path) or "unreadable"`, and
`is_filler("unreadable")` is **False** — `"unreadable"` is not in `FILLER_VALUES`. So a substitute
path that does not exist pins the literal string `"unreadable"` and **discharges the record**:

```
orient with a NONEXISTENT substitute -> 'DEGRADED-NO-MAP' exit=0
  receipt substitutes: [{'path': 'this-file-does-not-exist.md', 'content_hash': 'unreadable'}]
verify-orientation    -> exit=0  (DISCHARGED on a file that does not exist)
```

Why this blocks, in the gate's own terms:

- It defeats a **named handoff requirement**: *"Hash-pin the substitutes … so g2's frame check
  compares against this committed prior declaration rather than a same-breath assertion."* A pin of
  the constant string `"unreadable"` is not a prior declaration. g2 is built on this receipt.
- It contradicts a claim in the implementer's own report — *"a substitute without a content hash
  treated as a refusal"* — which is true for a hand-written empty hash and **false** for the
  tool-generated unreadable case, i.e. the supported path the report says agents should use.
- It is the **same defect class this issue exists to close**, one level down: a false *discharged* is
  to a degraded record what a false RESOLVED is to a map. The engine records only the exit code, so
  downstream this reads as a satisfied contract on a declaration that pins nothing.
- It needs no dishonesty to trigger — **a typo in a substitute path silently converts a refusal into
  a satisfied contract**, which is the exact silent-degradation the module refuses everywhere else.
- `"unreadable"` appears **once** in the codebase (`map_orient.py:727`) and in **no test**. It is not
  in the docstring's "Honest limits", so it is not a ratified limitation.

Fix is small: refuse an unreadable substitute at pin time (or add `"unreadable"` to `FILLER_VALUES`,
though refusing at the edge is better — it reports *which* path could not be read), plus a floor arm
and a `self_test` check. While there, the untested absolute-path branch in the same function
(`pin_substitutes:723,726`, flagged under speculative-generality) can go: `--substitute` is
documented as repo-relative.

---

## Handoff compliance

Assigned intent met on everything else, verified by execution rather than by reading the report.

- `python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_init_work_area.py -q`
  → `80 passed, 26 subtests passed in 27.30s`, exit 0.
- `python scripts/map_orient.py --self-test` → `self-test OK`, exit 0.
- **Exit vocabulary provably clear.** `10-13`, none in `{1, 2, 126, 127}`, all in `2 < c < 126`,
  asserted in `self_test()` *and*
  `ContractShape::test_semantic_exit_codes_avoid_the_argparse_traceback_shell_collision`, with the
  negative side pinned by `test_a_usage_error_exits_two_and_is_not_a_verdict`.
- **RESOLVED requires citable content.** Confirmed behaviorally: an index reading
  `"# Architecture Index\n\nComing soon.\n"` → `DEGRADED-UNPARSEABLE` / exit 10, and weakening the
  predicate flips it to `RESOLVED` / exit 0 (mutation 3 above).
- **"Could not look" vs "looked and found nothing"** distinguished by a positive proof: bare dir →
  `UNRESOLVABLE-ROOT` / 11; add `.git` → `DEGRADED-NO-MAP` / 10. One bit apart, both directions
  executed.
- **Three-way discharge** holds for the *missing-field* matrix; the *filler-quality* arm has the M4
  gap and the B1 hole.

## Scope drift

None. Files touched: `scripts/map_orient.py` (new), `tests/test_map_orient.py` (new),
`tests/test_mutation_floor.py` (new), `scripts/init_work_area.py` (placeholder + guard regex only),
`tests/test_init_work_area.py` (adjudicated deviation 2).

Exclusions all respected: no `verify-frame` implementation (docstring mention only), no template
wiring, no prose deleted, `skills/` and `templates/` and `scripts/checklist_engine.py` untouched
(`git diff --stat HEAD --` empty), episode store and the five fragile relative checks untouched.

**The three adjudicated deviations — reasoning verified true, not re-litigated:**

1. **`<repo-root>` → `as_posix()`.** True. `instantiate_spine` really does run `json.loads` on
   `resolve_spine`'s own output (`scripts/init_work_area.py:169-171`), and:
   ```
   str(Path.resolve())       -> 'C:\\Programs\\constellation-skills-wt\\e298-304'
                                json.loads FAILS: Invalid \escape: line 1 column 29 (char 28)
   Path.resolve().as_posix() -> 'C:/Programs/constellation-skills-wt/e298-304'
                                json.loads OK
   ```
   The handoff's specified value expression would have shipped a broken resolver on Windows. The
   deviation is correct and the in-code comment correctly frames `<repo-root>` as **robustness, not
   a repair**, per the corrected justification.
2. **Additive test class.** True. `git diff --stat` → `53 insertions(+)`, **0 deletions**; deletion
   count grepped independently = `0`. Nothing pre-existing modified.
3. **Three extra flags.** Correct and necessary — without a way to declare a substitute there is
   nothing for the tool to hash, so the frozen synopsis and the hash-pinning requirement could not
   both be literally satisfied. (Ironically this is also where B1 lives.)

## Evidence verdict

Evidence is real and independently reproduced. Test mode `test-first` is credible: the claimed red
(`24 failed, 28 passed`) is concentrated in `PartialFillMatrix` and `VerifyOrientation`, exactly the
arms implemented last, which is the signature of a genuine red rather than a retrofit.

**One false claim.** The report states *"The `.agent-work/probe/` directory was removed after
capture."* It is still on disk:

```
$ ls -la .agent-work/probe/
-rw-r--r-- 1 fredc 197609 978 Aug  1 15:50 map-orientation.json
```

Minor as untracked scratch, but it is a side-effect claim that does not match the world, and this
gate is specifically about not asserting things that were not verified. Delete it before closeout.

## Code/doc quality

Good, and unusually well-documented for its size. Module docstring carries modes, the frozen exit
table, the receipt schema, and an honest-limits section; pure decision layer is cleanly separated
from impure edges; `_utf8_stdio()`, `main(argv)` + `raise SystemExit(main())`, and the `--self-test`
floor all match house style. The falsification-floor pointers on `candidate_is_citable`,
`determine_mode` and `exit_code_for` — naming which mutation pins each branch — are a genuinely good
pattern worth spreading.

**Constraints clear.** All writes use `encoding='utf-8', newline='\n'`. **3.13+-only API scan: clean**
— no `Path.read_text(newline=)`, no `itertools.batched`, no `typing.override`, no `datetime.UTC`;
the module uses `datetime.now(timezone.utc)` (3.2+) and `open(..., newline='\n')`. The sole `UTC` hit
is prose in the receipt-schema docstring. Local 3.14.3 vs CI 3.12 poses no repeat of PR #320.

**Fowler pass** (`fowler-pass.json`, rail exits 0; 12 smells, 4 flagged, 3 overridden with logged
standards). Nothing blocking. Most useful finds: speculative-generality on `pin_substitutes`'
untested absolute-path branch (same code path as B1), and shotgun-surgery/duplicated-code on the
filler rule, which is expressed in three places and **has already drifted** — `'<placeholder>'` is in
`self_test()`'s filler list (`map_orient.py:938`) but absent from the floor's
(`test_map_orient.py:381,388`).

## Map impact verdict

- **Evidence supports claimed change:** Yes. I reproduced `DEGRADED-NO-MAP` against the live repo
  root and confirmed `docs/architecture/` genuinely does not exist.
- **Constraints not violated:** Yes. The newly-relied-on constraint (the engine records only
  `{cmd, exit, shell}` and discards stdout) is correctly identified as the reason the exit table is a
  frozen contract, and the implementation honors it.
- **Notes match the diff:** Yes. `scripts/map_orient.py` as a peer to the existing
  `scripts/verify_*.py` gate checks is accurate; no overstated structural impact.
- **Decision candidates surfaced:** Yes — the exit band, the deliberate decoupling from
  `build_architecture_map.parse_packet` (grounded on a measurement, which I did not re-run but which
  is consistent with the two repos' differing packet formats), and `as_posix()` are all surfaced
  rather than silently taken.
- **Durable context routed:** Yes, to Triage rather than dropped.

## Reconciliation check

No divergence needing Commander reconciliation. The repo has no architecture baseline to diverge
from — which is the condition this gate exists to make legible rather than silent.

## Out-of-scope observations

- **`orient` writes a receipt into any directory it is pointed at** (requested finding —
  **severity: major, non-blocking**). `cmd_orient` writes `.agent-work/<work-id>/map-orientation.json`
  whenever `root.is_dir()`, with no `--no-write` or `--receipt-dir` opt-out, and it writes **even when
  the repo-root proof failed** — scaffolding `.agent-work/` inside something it just declared is not a
  repo. This already cost a cleanup in read-only `f1Brainz`. It is not a correctness bug (the receipt
  *is* the delivery record) but it makes the tool unsafe to point at a repo you do not own, which is
  exactly what a reviewer or an auditing agent wants to do. Recommend `--receipt-dir` (write the
  receipt anywhere, decoupled from `--root`) over a bare `--no-write`, since the degraded record
  should still be produced. Triage candidate `tc1`.
- **Harden the harness kill criterion from class-level to reason-level** — triage candidate `tc2`,
  see attack (4).
- **`self_test()`'s shipped-template check silently no-ops when the module runs from a copy.**
  `map_orient.py:853-861` resolves the template via `Path(__file__).parents[1]`, which under the
  mutation harness is a tmpdir, so `if template.is_file():` is False and the check is skipped. Benign
  today because `CitableContent::test_the_shipped_index_template_itself_does_not_resolve` covers the
  same ground with a stable `ROOT` — but it is a check that cannot fail in exactly the context this
  gate is about, and it is invisible. Worth a comment at minimum.
- **`docs/agents/engine-config.json` does not exist** yet every `config_ref` in this repo points at
  it (implementer's find, independently visible — the repo has only `ORCHESTRATOR_CONTEXT.md`). Same
  defect class as this issue: tolerated silently. Belongs in Triage.

## Workflow Feedback

- **Handoff gaps:** The handoff named the three shipped mutations and said mine must be *different*,
  but gave no acceptance bar for the outcome — I had to decide myself whether "my mutation survived"
  is a BLOCK or an observation. It is genuinely ambiguous: a surviving mutant means the floor has a
  hole, but the gate ships an explicitly-scoped *regression floor*, not exhaustive mutation coverage.
  A line like "a surviving reviewer mutation is a finding whose severity tracks the property it
  weakens; only a surviving mutation on a **close-criterion** property blocks" would have removed the
  guess. Second, smaller: the handoff said to attack the harness and treat a fooled kill as a BLOCK,
  but "fooled" turned out to have two very different readings — *the shipped three are unearned*
  (would be a BLOCK) versus *the criterion could credit some other unearned kill* (a limitation). I
  resolved it by verifying the shipped three behaviorally, which is the reading that matters, but the
  instruction as written points at the weaker one.
- **Context rediscovered:** That a `survey` checklist rejects `advance` (`REFUSED: advance is for
  gated checklists; use record`) — the reviewer SKILL.md says to "`advance`/`record` only once its
  postconditions pass" and to "run the engine's final `advance`/`consolidate`", which is gated-
  checklist vocabulary that does not apply to the artifact this skill actually creates. Cost one
  refused call. Also: `flag-candidate` needs `--from` and `--statement`, documented nowhere in the
  skill.
- **Instructions improvised around:** The reviewer skill has no vocabulary for *executing* anything —
  it is written for reading a diff and rendering judgment. To run mutations through the shipped
  harness rather than around it, I wrote a scratchpad driver that imports
  `tests/test_mutation_floor.py` and reuses its own `apply_mutation` / `run_floor` / `failed_nodes`.
  That mattered: driving the harness's own code is what let me test the *harness*, not just the
  module. If executed falsifiability is going to be a recurring reviewer duty, that driver pattern
  belongs in the skill as a reference.
- **What would have made this easier:** One concrete change — the handoff should state the **severity
  rule for a surviving reviewer mutation** (see Handoff gaps). Everything else in this handoff was
  exceptionally well-aimed: the three weighted items at the top were the three places where a
  careless review would have reported conformance and missed something, and the demand for a mutation
  of my own is what surfaced both the M4 gap and, indirectly, the B1 blocker.

## Return status
`complete`
