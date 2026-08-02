# Review Result — issue-304 gate g2

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g2 — wire the contract at context and plan`

Reviewed range: `6d35fe2..HEAD` (g1 baseline excluded; already APPROVED).
Survey driven through the engine at `.agent-work/issue-304/g2-review/review.json`
(13 checks, session `constellation/issue-304/g2/reviewer/attempt-1`, consolidated `verdict=BLOCK findings=1`).
Fowler record at `.agent-work/issue-304/g2-review/fowler-pass.json` (rail exit 0).

## Result
`BLOCK`

**One blocker, and it is narrow.** The gate is otherwise strong and much of it exceeds what the handoff
asked. The blocker is the defect class the handoff explicitly told me to hunt and explicitly designated
a BLOCK, so I am honoring the contract's own bar rather than substituting a softer judgement — but I
want the Commander to see clearly that the *deliverable is not broken*. This is dead code, not a
correctness bug, and it is cheap to resolve in either direction.

---

# THE QUESTION THIS HANDOFF EXISTS TO ASK

## CAN THIS CHECK FAIL? — **YES. Demonstrated by execution.**

I devised **four** mutations of my own, all provably outside the shipped eight, applied each to
`scripts/map_orient.py`, ran `tests/test_map_orient.py tests/test_map_contract_wiring.py`, and
**all four went red**.

Why each is outside the shipped eight:
- **MINE-A** attacks the unknown-**anchor** refusal in the **RESOLVED** arm. Shipped #7 attacks the
  undeclared-**substitute** refusal in the **DEGRADED** arm. Different arm, different refusal.
- **MINE-B** attacks the **code-cut-frame** refusal. Shipped #3 (`path.exists()` instead of citable
  content) attacks the `orient` resolver, not the frame checker.
- **MINE-C** attacks `substitute_label`, the **read** side of the label. Shipped #8 attacks
  `classify_substitute`, the **write** side.
- **MINE-D** removes the **no-backing vacuity** guard entirely. Not among the eight in any form.

Applied-before-red discipline held on every one (anchor unique = 1, gone after substitution = 0,
replacement count 0 → 1) so a non-matching anchor could never be miscredited as a kill.

### MINE-A — the UNKNOWN-ANCHOR refusal disabled (RESOLVED arm)

```
  anchor occurrences in original : 1 (must be 1)
  replacement count before       : 0 (must be 0)
  anchor gone after substitution : 0 (must be 0)
  replacement count after        : 1 (must be 1)

diff --git a/scripts/map_orient.py b/scripts/map_orient.py
@@ -776,7 +776,7 @@ def frame_verdict(
             )
         backing = [a for a in anchors if a in known]
         for anchor in anchors:
-            if anchor not in known:
+            if False:
                 problems.append(
                     f"{anchor} does not resolve against the map inventory -- anchor ids "
                     "exist only in the map, so an id that is not in it was not read from it"
```

```
  --- pytest returncode: 1 ---
    def test_an_anchor_that_does_not_resolve_refuses_and_names_it(self):
        repo = resolved_repo(self)
        frame(repo.root, UNKNOWN_ANCHOR_FRAME)
        proc = verify_frame(repo.root)
>       self.assertNotEqual(proc.returncode, 0)
E       AssertionError: 0 == 0

>       self.assertIn("struct:ghost_module", out)
E       AssertionError: 'struct:ghost_module' not found in 'FRAME-OK\nframe: .agent-work/w/MISSION_FRAME.md\norientation: RESOLVED\nframe citations resolve -- contract SATISFIED\nproblems: 0\n'

FAILED tests/test_map_orient.py::ContractShape::test_self_test_floor_passes
FAILED tests/test_map_orient.py::VerifyFrameResolved::test_an_anchor_that_does_not_resolve_refuses_and_names_it
FAILED tests/test_map_orient.py::VerifyFrameContractShape::test_verify_frame_only_echoes_ids_the_frame_itself_cited
3 failed, 96 passed, 53 subtests passed in 11.40s

  VERDICT for MINE-A: RED (killed)
```

### MINE-B — the CODE-CUT-FRAME refusal disabled

```
diff --git a/scripts/map_orient.py b/scripts/map_orient.py
@@ -803,7 +803,7 @@ def frame_verdict(
     if not backing:
-        if sources:
+        if False:
             problems.append(
                 "this frame is cut from CODE: its only citations are source paths "
```

```
  --- pytest returncode: 1 ---
E       AssertionError: 13 != 0 : self-test FAILED: 1 check(s)
E         - the cut-from-code refusal names a source path

>       self.assertIn("src/engine/solver.py", proc.stdout + proc.stderr)
E       AssertionError: 'src/engine/solver.py' not found in 'FRAME-REFUSED\n...problems: 1\n  - the frame cites no anchor id that resolves against the map -- the map resolved, so the frame has to be built from it\n'

FAILED tests/test_map_orient.py::ContractShape::test_self_test_floor_passes
FAILED tests/test_map_orient.py::VerifyFrameResolved::test_a_frame_cut_from_source_paths_refuses
2 failed, 97 passed, 53 subtests passed in 11.28s

  VERDICT for MINE-B: RED (killed)
```

### MINE-C — `substitute_label` always returns `known-fallback`

```
diff --git a/scripts/map_orient.py b/scripts/map_orient.py
@@ -705,7 +705,7 @@ def substitute_label(entry: object) -> str:
     if isinstance(entry, dict) and entry.get("source") in SUBSTITUTE_LABELS:
         return entry["source"]
-    return LABEL_AGENT_DECLARED
+    return LABEL_KNOWN_FALLBACK
```

```
  --- pytest returncode: 1 ---
E       AssertionError: 13 != 0 : self-test FAILED: 2 check(s)
E         - an unlabelled substitute reads as UNVERIFIED, never upgraded by omission
E         - a bogus label reads as unverified

FAILED tests/test_map_orient.py::ContractShape::test_self_test_floor_passes
1 failed, 98 passed, 53 subtests passed in 12.00s

  VERDICT for MINE-C: RED (killed)
```

**This kill is itself the blocker's evidence.** The *only* thing that moved was
`test_self_test_floor_passes` — i.e. the self-test. No behavioural test outside it noticed, because
nothing outside it uses the function.

### MINE-D — the no-backing vacuity refusal removed entirely

```
diff --git a/scripts/map_orient.py b/scripts/map_orient.py
@@ -802,7 +802,7 @@ def frame_verdict(
-    if not backing:
+    if False:
         if sources:
```

```
  --- pytest returncode: 1 ---
>       self.assertNotEqual(gating.returncode, 0)
E       AssertionError: 0 == 0
>       self.assertNotEqual(verify_frame(repo.root).returncode, 0)
E       AssertionError: 0 == 0

FAILED tests/test_map_orient.py::ContractShape::test_self_test_floor_passes
FAILED tests/test_map_orient.py::VerifyFrameResolved::test_a_frame_cut_from_source_paths_refuses
FAILED tests/test_map_orient.py::VerifyFrameResolved::test_a_frame_with_no_citation_at_all_refuses
FAILED tests/test_map_orient.py::VerifyFrameResolved::test_placeholder_anchors_do_not_count_as_citations
FAILED tests/test_map_orient.py::VerifyFrameContractShape::test_report_only_is_the_flag_flip_between_gating_and_reporting
FAILED tests/test_map_orient.py::VerifyFrameDegraded::test_a_degraded_frame_citing_nothing_declared_refuses
6 failed, 93 passed, 53 subtests passed in 12.32s

  VERDICT for MINE-D: RED (killed)
```

### Restore verification for all four (blob OID, never raw bytes)

```
  committed blob OID : 83f8fc194ecc465255d02edfba0ba3552dffedb3
  worktree  blob OID : 83f8fc194ecc465255d02edfba0ba3552dffedb3
  BLOB-OID-MATCH     : True
  git diff --quiet HEAD -- scripts/map_orient.py exit: 0 (0 == clean)
```

**The CRLF trap fired exactly as the handoff warned, and this is worth recording.** After each restore
`git status --porcelain` reported `M scripts/map_orient.py` **while** `git diff --quiet HEAD` returned
0 and the blob OIDs matched — line-endings only, because my harness wrote with `newline='\n'` into a
repo whose working tree is CRLF (measured: `CRLF: 0, bare LF: 1689` after the harness;
`CRLF: 1689, bare LF: 0` after `git checkout`). An agent trusting `porcelain` alone would have
reported a phantom modification. Final state is clean:

```
$ git status --porcelain
?? .agent-work/issue-304/g2-review/          # my own review artifacts, nothing else
```

---

# THE DEFECT CLASS THAT ALREADY BIT THIS GATE — hunted again, and FOUND

## Caller-grep audit — CALLERS, not definitions

I audited all **58** functions in `map_orient.py` by AST reachability from the **three real
subcommands** (`cmd_orient`, `cmd_verify_orientation`, `cmd_verify_frame`, plus `build_parser`), with
**`self_test` blocked as a traversal node**.

**That blocking is the whole trick, and it is why this defect survives review.** My first pass used
`main` as an entrypoint — `main` reaches `self_test` via `--self-test`, so every self-tested helper came
back "PRODUCTION-REACHABLE" and the audit reported a clean bill of health. Re-running with `self_test`
excluded is what exposed it.

```
=== functions NOT reachable from the three real subcommands (self_test blocked) ===
  _cand                          [harness/entry]
  _check                         [harness/entry]
  _utf8_stdio                    DEAD          <- module-level call at :250; g1 code, out of scope
  main                           [harness/entry]
  self_test                      [harness/entry]
  substitute_label               self-test-only   <-- THE FINDING
```

**25 of the 26 deliverable-demanded functions are genuinely wired.** Concrete call sites, each outside
its own `def` and outside any test:

```
probe_fallbacks            map_orient.py:1154   <- cmd_orient          (the m3 fix: real)
classify_substitute        map_orient.py:1126   <- pin_substitutes     (the m3 fix: real)
pin_substitutes            map_orient.py:1150   <- cmd_orient
frame_verdict              map_orient.py:1251   <- cmd_verify_frame
render_frame_report        map_orient.py:1252   <- cmd_verify_frame
map_inventory              map_orient.py:1249   <- cmd_verify_frame
declared_substitute_paths  map_orient.py:785    <- frame_verdict
cited_source_paths         map_orient.py:767    <- frame_verdict
```

**The one exception — `substitute_label`.** Whole-repo grep, every reference:

```
$ grep -rn "substitute_label" --include=*.py --include=*.json --include=*.md . | grep -v "^./.agent-work"
./scripts/map_orient.py:704:def substitute_label(entry: object) -> str:
./scripts/map_orient.py:1575:        substitute_label({"path": "README.md"}) == LABEL_AGENT_DECLARED,
./scripts/map_orient.py:1580:        substitute_label({"path": "README.md", "source": "trust-me"}) == LABEL_AGENT_DECLARED,
./scripts/map_orient.py:1585:        substitute_label({"path": "README.md", "source": LABEL_KNOWN_FALLBACK})
```

Three call sites. All inside `self_test()`. And the `source` key it decodes is **written and never read
back** — I confirmed by running a real degraded orient and inspecting both the receipt and every output
surface:

```
$ grep -n '"source"' scripts/map_orient.py
1126:                "source": classify_substitute(rel, path.is_file()),   # the only WRITE
# ...no read anywhere.

$ python scripts/map_orient.py verify-orientation --root <fixture> --work-id d
DEGRADED-NO-MAP
receipt: .agent-work/d/map-orientation.json
orientation contract SATISFIED
problems: 0
                                     # <- the label is never surfaced
```

`tests/test_map_orient.py:988` asserts `entry["source"] == mo.LABEL_AGENT_DECLARED` — that reads the
receipt dict **directly**, asserting the write; it does not go through `substitute_label`.

---

## Handoff compliance
**Pass.** All six declared deliverables landed, each verified independently rather than accepted:

1. **Anchor change** — the context imperative contains `"Before you open any source file, resolve and
   read the map input"`, read from the template JSON, not from a test.
2. **`verify-frame`** — refuses an absent frame, an unknown anchor (naming it), a code-cut frame, and a
   degraded frame citing an undeclared substitute. All four reproduced by execution.
3. **Asymmetric wiring** — whole-template scan: `verify-frame` appears in the **plan step only**.
4. **Fallback oracle** — a real receipt carries `fallbacks_probed` (5 entries) and per-substitute `source`.
5. **Installer registration** — `map_orient.py` present in `SKILL_SCRIPT_BUNDLES["commander"]`.
6. **Three new mutations** — `tests/test_mutation_floor.py`: `12 passed, 9 subtests passed in 110.31s`.

## Scope drift
**None.** Files touched outside `.agent-work/` across `6d35fe2..HEAD` are exactly the six declared:

```
scripts/install_constellation.py
scripts/map_orient.py
skills/commander/templates/COMMANDER_SPINE.template.json
tests/test_map_contract_wiring.py
tests/test_map_orient.py
tests/test_mutation_floor.py
```

Every named exclusion respected: `checklist_engine.py` untouched; no bootstrap/`CLAUDE.md` stanza
(ruled OUT by the human); no `reconcile` changes; g3's prose block still present (not deleted early);
no #341/#342/#344 fixes attempted. `C:/Programs/f1Brainz` was never given to any tool by me — every
`orient`/`verify-frame` run used a throwaway scratchpad fixture.

## Evidence verdict
**Pass — every claim reproduced at its source.**

### The close-criteria suite, re-run by me

```
$ python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_context_manifest.py \
    tests/test_context_declaration_lint.py tests/test_context_determinism.py \
    tests/test_install_constellation.py tests/test_map_contract_wiring.py -q

............................................................................................................................ [ 40%]
................................................. [ 57%]
.................................................... [ 74%]
................................................................... [ 96%]
...........                                                         [100%]
303 passed, 433 subtests passed in 154.74s (0:02:34)
exit code 0
```

Matches the implementer's superset paste (303 / 433 in 155.00s).

### `--self-test`, on both interpreters

```
$ python -c "import sys; print(sys.version.split()[0])"   ->  3.14.3
$ py     -c "import sys; print(sys.version.split()[0])"   ->  3.12.13

$ python scripts/map_orient.py --self-test
self-test OK
SELFTEST_EXIT=0

$ py scripts/map_orient.py --self-test          # CI's actual pin
self-test OK
PY312_SELFTEST_EXIT=0
```

### The three reconstructed TDD reds — all reproduce

**m4 — EXACT match:**
```
### m4: revert skills/commander/templates/COMMANDER_SPINE.template.json to 6d35fe2
  reverted-to blob OID : 7b5eba7574732d3df9eb668747443a084017db75
  HEAD blob OID        : 5062325d38199b00759c1b7b151910a4625d6945
  (differ, so the revert really changed the tree: True)
  FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_degraded_is_a_declared_reading_not_a_licence_to_start_from_code
  FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_later_source_reads_are_framed_as_confirming_not_building
  FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_the_context_imperative_names_the_orient_command_it_expects
  FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_the_map_read_is_anchored_before_any_source_file_is_opened
  FAILED tests/test_map_contract_wiring.py::ContractWiring::test_context_c2_is_a_command_check_naming_verify_orientation
  FAILED tests/test_map_contract_wiring.py::ContractWiring::test_the_plan_imperative_names_where_the_frame_must_be_written
  FAILED tests/test_map_contract_wiring.py::ContractWiring::test_the_plan_imperative_records_the_asymmetry_and_the_road_not_to_take
  FAILED tests/test_map_contract_wiring.py::ContractWiring::test_the_plan_imperative_states_that_the_check_is_a_floor_not_the_fix
  FAILED tests/test_map_contract_wiring.py::ContractWiring::test_the_plan_step_carries_a_verify_frame_command_check
  RESULT LINE: 9 failed, 10 passed, 7 subtests passed in 0.21s
  IMPLEMENTER CLAIMED: 9 failed, 10 passed, 7 subtests passed
  MATCH: True
  BLOB-OID-MATCH after restore: True   |   git diff --quiet HEAD exit: 0
```

**m5 — EXACT match:**
```
### m5: revert scripts/install_constellation.py to 6d35fe2
  SUBFAILED(skill='commander') tests/test_map_contract_wiring.py::ScriptIsBundled::test_map_orient_ships_with_every_skill_whose_template_invokes_it
  RESULT LINE: 1 failed, 120 passed, 306 subtests passed in 14.16s
  IMPLEMENTER CLAIMED: 1 failed, 120 passed, 306 subtests passed
  MATCH: True
  BLOB-OID-MATCH after restore: True   |   git diff --quiet HEAD exit: 0
```

**m2 — reproduces; one number differs and is fully explained:**
```
### m2: revert scripts/map_orient.py to 6d35fe2
  FAILED tests/test_map_orient.py::AbsentFrameRefuses::test_a_frame_without_a_receipt_refuses_rather_than_passing
  FAILED tests/test_map_orient.py::AbsentFrameRefuses::test_an_absent_frame_refuses_on_a_degraded_repo_too
  FAILED tests/test_map_orient.py::AbsentFrameRefuses::test_an_absent_frame_refuses_on_a_resolved_repo
  FAILED tests/test_map_orient.py::AbsentFrameRefuses::test_an_empty_frame_file_is_the_same_as_no_frame
  FAILED tests/test_map_orient.py::AbsentFrameRefuses::test_the_refusal_names_the_path_it_looked_for
  RESULT LINE: 5 failed, 75 deselected in 1.02s
  IMPLEMENTER CLAIMED: 5 failed, 63 deselected
```

The **5 failures and which 5** match exactly; only `deselected` differs. Arithmetic settles it — the
paste is genuine and was taken at the right commit:

```
$ for c in 72a7de0 8ba4529 22e5134 HEAD; do git show $c:tests/test_map_orient.py | grep -c "    def test_"; done
72a7de0: 68     <- m2's OWN commit:  5 selected + 63 deselected = 68  ✓ the implementer's paste
8ba4529: 80
22e5134: 80
HEAD:    80     <- my run:            5 selected + 75 deselected = 80  ✓
```

m3 and m6 added 12 tests to that file after m2 was recorded. **Not a discrepancy — a timestamp.**

## Code/doc quality
**Pass, with observations.** Fowler pass recorded and rail-verified:

```
$ python .../verify_fowler_pass.py .agent-work/issue-304/g2-review/fowler-pass.json
fowler pass ok: smells=12, flagged=['long-method', 'long-parameter-list', 'speculative-generality'],
overridden=['data-clumps', 'primitive-obsession', 'divergent-change']
FOWLER_RAIL_EXIT=0
```

Each override carries a named documented standard and why it subordinates the smell (data-clumps ← the
module's `PURE.` convention that makes the `--self-test` floor fixture-free; primitive-obsession ← the
reserved-stdout-literal + frozen-exit-code wire contract crossing a process boundary; divergent-change
← the `SKILL_SCRIPT_BUNDLES` single-file/zero-companion bundling contract).

**No overclaiming found.** The handoff asked me to flag any place the code or docs overstate the
citation check. I found none — the honest framing appears consistently at `map_orient.py:617`,
`tests/test_map_orient.py:651-655`, `tests/test_map_contract_wiring.py:28`, and the plan imperative.
The docstring states outright: *"It does not close the gap... Do not describe it as making the degraded
check sound; it converts part of it."*

**The CI-pin hazard is now proven, not assumed.** The implementer asserted "no 3.13+-only APIs were
introduced." I verified it by execution on CI's pin: both changed scripts byte-compile under 3.12.13
and the self-test passes there. A targeted scan of all 574 added script lines for 3.13/3.14-only APIs
(`read_text(newline=)`, `itertools.batched`, `typing.TypeIs`, `copy.replace`, `os.process_cpu_count`,
`glob.translate`, `Path.full_match`, `sys.last_exc`, `warnings.deprecated`,
`asyncio.eager_task_factory`, `random.binomialvariate`, `PythonFinalizationError`) returned **zero
hits**. This closes the PR #320 / 39-CI-failure hazard for this gate.

Windows constraint honored: the single receipt writer uses
`open(path, "w", encoding="utf-8", newline="\n")`; all reads pass `encoding="utf-8"`.

## Map impact verdict
- **Evidence supports claimed change:** Yes. Every behavioral claim (`verify-frame` subcommand, receipt
  `fallbacks_probed` + `source`, template gating, bundle registration) is backed by output I produced.
- **Constraints not violated:** Confirmed. The frozen g1 exit-code vocabulary is intact — the `EXIT_*`
  block diffs **IDENTICAL** against `6d35fe2`. The wider reading of codes 10/12 is documented in the
  module docstring (`:56-59`, `:738-742`) rather than left implicit, as claimed.
- **Notes match the diff:** Yes, with one correction. The Map Impact notes are accurate. The
  **`## Completed slice` narrative is not**: it says attempt-1 *"wrote `probe_fallbacks()`,
  `classify_substitute()` and `substitute_label()` — and never called any of them from `cmd_orient`"*
  then *"Fixed:"* lists two remedies covering only the first two. `substitute_label` was left
  uncalled. The paragraph reads as though all three were fixed. I judge this an **incomplete audit
  reported as complete**, not a fabrication — the implementer surfaced the defect class honestly and
  the report's other six deviations all check out.
- **Decision candidates surfaced:** Yes. The `verify-frame`-absent-at-context decision and its
  road-not-to-take are recorded in the plan imperative and the module docstring.
- **Durable context routed:** Yes — four triage candidates in the result, plus five I flagged.

## Reconciliation check
**No reconciliation needed.** This repo carries **no `docs/architecture/` tree**, so there is no
structural map to drift from and nothing to route to Cartographer.

The three template-pinning suites are **unchanged**, verified by blob OID rather than by re-running them:

```
tests/test_context_manifest.py           6d35fe2: 96a3e46e…  HEAD: 96a3e46e…  UNCHANGED: YES
tests/test_context_declaration_lint.py   6d35fe2: 2574bc1b…  HEAD: 2574bc1b…  UNCHANGED: YES
tests/test_context_determinism.py        6d35fe2: bf2a0390…  HEAD: bf2a0390…  UNCHANGED: YES
```

**Zero test-file lines were deleted anywhere in the gate** (`git diff 6d35fe2..HEAD -- tests/ | grep "^-"`
returns nothing), which independently proves no pre-existing assertion was weakened to accommodate the
template change.

---

## Named close criteria — each verified by execution or by reading the artifact

### An ABSENT frame REFUSES — attacked directly with **12 variants**, not just the shipped mutation

```
ATTACK  1: no frame file at all                     EXIT=12  FRAME-MISSING
ATTACK  2: zero-byte frame                          EXIT=12  FRAME-MISSING
ATTACK  3: whitespace-only frame                    EXIT=12  FRAME-MISSING
ATTACK  4: UTF-8 BOM only                           EXIT=10  FRAME-REFUSED
ATTACK  5: CRLF-only frame                          EXIT=12  FRAME-MISSING
ATTACK  6: frame is a DIRECTORY                     EXIT=12  FRAME-MISSING
ATTACK  7: frame parked at the WRONG path           EXIT=12  FRAME-MISSING
ATTACK  8: unfilled template placeholders only      EXIT=10  FRAME-REFUSED
ATTACK  9: prose with NO citation at all            EXIT=10  FRAME-REFUSED
ATTACK 10: a REAL anchor from the map               EXIT=0   FRAME-OK        <- the control
ATTACK 11: an INVENTED anchor                       EXIT=10  FRAME-REFUSED
ATTACK 12: no receipt at all (orient never ran)     EXIT=12  RECEIPT-MISSING
```

**Zero vacuous passes.** ATTACK 10 is the control: the one legitimate frame passes, so the check is not
merely always-refusing. ATTACK 12's stdout first line is the reserved literal `RECEIPT-MISSING` with
the detail on **stderr** — the reserved-first-line contract holds (I initially merged the streams and
had to separate them to confirm).

### `verify-frame` does NOT run at the context step — read from the template, not trusted to a test

```
--- step: context ---
  c1: kind=None     override_policy=None
  c2: kind=command  override_policy=None
       command: python <commander-skill-dir>/scripts/map_orient.py verify-orientation --root <repo-root> --work-id <work-id>
  'verify-frame' appears anywhere in this step's JSON: False

--- step: plan ---
  c6: kind=command  override_policy={'allowed': True, 'authority': 'human', 'reason_required': True}
       command: python <commander-skill-dir>/scripts/map_orient.py verify-frame --root <repo-root> --work-id <work-id>

=== whole-template scan: which steps mention verify-frame? ===
  plan
```

The claimed asymmetry holds exactly: context `c2` carries **no** `override_policy` (tighter); plan `c6`
carries the human-authority recorded-waiver policy.

### `orient` NEVER prints an anchor id — verified by running it

Fixture map declares `struct:solver_core`, `struct:io_layer`, `cap:solve`:

```
$ python scripts/map_orient.py orient --root <fixture> --work-id demo
RESOLVED
root: …/fixture-repo
root proof: positive: .git entry present at root
entrypoint: docs/architecture/index.md
anchor_count: 2
candidates tried:
  [1] generated-map: docs/architecture/generated/map.json -> absent (absent)
  [2] index: docs/architecture/index.md -> hit (2 unique anchors)
  [3] packets-dir: docs/architecture -> empty (0 packet(s), none non-empty)
receipt: .agent-work/demo/map-orientation.json

--- scanning that output for any anchor id present in the map ---
  not printed: struct:solver_core  OK
  not printed: struct:io_layer     OK
  not printed: cap:solve           OK
```

It prints `anchor_count` only. The citation check cannot be self-satisfied from the tool's own output.

### The context imperative is anchored to "before you open any source file"

```
contains 'Before you open any source file': True

…it becomes a disconfirm op at the feedback step). Before you open any source file, resolve and
read the map input: run python <commander-skill-dir>/scripts/map_orient.py orient --r…
```

The anchor governs the **map read itself**, not a later artifact.

### Gate-vs-report is a flag flip

```
--- GATING (no flag) ---                          --- REPORTING (--report-only) ---
FRAME-REFUSED                                     FRAME-REFUSED
frame: .agent-work/demo/MISSION_FRAME.md          frame: .agent-work/demo/MISSION_FRAME.md
orientation: RESOLVED                             orientation: RESOLVED
frame citations do NOT resolve -- REFUSED         frame citations do NOT resolve -- REFUSED
problems: 2                                       problems: 2
  - struct:totally_invented does not resolve…       - struct:totally_invented does not resolve…
  - the frame cites no anchor id that resolves…     - the frame cites no anchor id that resolves…
EXIT=10                                           report-only: NOT gating; would exit 10
                                                  EXIT=0
```

Identical verdict text; only blocking-ness moves. Same flag works on `verify-orientation`.

### No new exit codes

```
$ diff <(git show 6d35fe2:scripts/map_orient.py | grep "^EXIT_") <(grep "^EXIT_" scripts/map_orient.py)
IDENTICAL: no new exit codes
```

---

## Deviation 5 — the changed pre-existing assertion: **ACCURATE, and the change is legitimate**

**(a) It is the ONLY pre-existing assertion altered.** Every deleted line across `6d35fe2..HEAD` in
`scripts/` and `tests/`: **zero** test-file lines. Across `fdec654..HEAD`, exactly one `_check()` line
changed:

```
-    _check("that refusal names the undeclared path", any("claude.md" in p for p in problems), failures)
+    _check("that refusal names the undeclared path", any("CLAUDE.md" in p for p in problems), failures)
```

**(b) Matching IS still case-insensitive while reporting IS as-cited** — measured directly:

```
cited CLAUDE.md    -> undeclared-substitute DETECTED: True   report echoes: 'CLAUDE.md'  as-cited: True
cited claude.md    -> undeclared-substitute DETECTED: True   report echoes: 'claude.md'  as-cited: True
cited Claude.Md    -> undeclared-substitute DETECTED: True   report echoes: 'Claude.Md'  as-cited: True
cited CLAUDE.MD    -> undeclared-substitute DETECTED: True   report echoes: 'CLAUDE.MD'  as-cited: True
cited cLaUdE.mD    -> undeclared-substitute DETECTED: True   report echoes: 'cLaUdE.mD'  as-cited: True
```

5/5 detected, 5/5 echoed in the frame's own casing. Both halves of the claim hold.

**(c) Is it "strictly tighter"?** In substance yes; in wording, loose. Being precise — these are
case-sensitive string tests, so **neither formally implies the other**. What is decisive:

```
current (correct) message: "the frame cites CLAUDE.md, which the receipt never declared…"
  OLD assertion any("claude.md" in p) -> False
  NEW assertion any("CLAUDE.md" in p) -> True

buggy (lowercasing) message: "the frame cites claude.md, …"
  OLD assertion -> True    (defect ACCEPTED)
  NEW assertion -> False   (defect CAUGHT)
```

The assertion was **not changed to green a failing test** — it *had* to change once the reporting
behavior was corrected, and it changed in the direction that catches the bug the old one pinned.
**Verdict: the deviation is honestly reported and the reasoning holds.** Minor note for the record:
"strictly tighter" is right about power against this defect, but it is not a superset of the old
assertion, and the report would be more precise saying so.

## Deviation 6 — the declined `CONTENT_HASH_RE` fix: **CONFIRMED a false positive**

Re-measured by execution against the shipped `is_content_hash`:

```
shipped pattern: ^[0-9a-f]{64}$

-- SHIPPED  ^[0-9a-f]{64}$ --            -- PROPOSED 'free fix'  ^[0-9a-f]{64,}$ --
  len 63    -> False                       len 63    -> False
  len 64    -> True                        len 64    -> True
  len 65    -> False                       len 65    -> True
  len 128   -> False                       len 128   -> True

-- the decisive comparison --
  128-char sha512 under SHIPPED  {64}  accepted as a sha256 pin? False
  128-char sha512 under PROPOSED {64,} accepted as a sha256 pin? True
```

**The implementer is right on both halves.** The `$` anchor already rejects longer digests, and
`{64,}` would *loosen* the pin. Taking the addendum's "free fix" would have introduced the very hole it
claimed to close. **The g1 re-review survivor should be closed as NOT-A-DEFECT.**

I also probed two behaviors the implementer did not report; both are correct-by-design, not holes:
uppercase `"A"*64` → True and leading/trailing newlines → True, because `is_content_hash` applies
`.strip().lower()` before matching (hex digests are case-insensitive; whitespace trimming is
deliberate). An **embedded** newline correctly → False, so there is no multiline escape.

---

## Blockers

- **[BLOCKER — dead helper, the named defect class] `substitute_label()` is reachable only from
  `self_test()`.** `scripts/map_orient.py:704`. Three call sites, all inside `self_test` (`:1575`,
  `:1580`, `:1585`). Nothing reads the `source` key it decodes — written at `:1126`, never read by
  `verify-orientation` output, `verify-frame`, or any test. Confirmed three independent ways: AST
  reachability with `self_test` blocked, whole-repo grep, and mutation MINE-C (killed **only** by
  `test_self_test_floor_passes`).

  The handoff's rule is explicit: *"If any other shipped helper is reachable only from its own unit
  test, that is the same defect and it is a BLOCK."*

  **Scoping this fairly for adjudication:** the *deliverable* is intact. Deliverable 4 asks for
  substitutes "labelled by provenance," and the **write** side is fully wired — a real receipt carries
  `source: "known-fallback"` and the five-entry `fallbacks_probed` array. This is the unused **read**
  side. Nothing is functionally wrong at runtime. Cheap resolutions, any of which I would accept:
  (a) call it where the label should influence a verdict or a report line; (b) delete it and keep
  `classify_substitute`; or (c) keep it deliberately as the documented receipt-schema decoder for
  downstream consumers and say so at the `def`, with a test pinning the receipt contract through it.

  Related and worth the Commander's eye: `g2-result.md`'s `## Completed slice` narrative names all
  three previously-dead helpers and then lists fixes covering only two, reading as though all three
  were repaired. The audit was incomplete but reported as complete. Everything else in that unusually
  candid report checks out.

## Out-of-scope observations

- `build_receipt()` now takes **7 parameters** (g2 added `fallbacks_probed` as the 7th, defaulted). The
  next receipt field makes it 8. Keyword-only params, or carrying the field on `Orientation`, would help.
- `frame_verdict()` is **96 lines** with a two-arm RESOLVED/DEGRADED branch. Extracting
  `resolved_problems()` / `degraded_problems()` would let each arm be tested without constructing a
  receipt. Quality only, no defect.
- `self_test()` grew **201 → 324 lines** this gate. Straight-line and individually named via `_check()`
  so it still reads, but worth splitting per subcommand before it grows again.
- `map_orient.py` is now **1689 lines** across root proof, map resolution, receipt IO, degraded
  validation, frame checking and an in-file self-test. The `SKILL_SCRIPT_BUNDLES` single-file /
  zero-companion contract currently justifies keeping it whole — that override is logged in the Fowler
  record — but the file is near the size where the tradeoff deserves a deliberate re-examination.
- **Close the g1 re-review survivor `CONTENT_HASH_RE` as NOT-A-DEFECT** (evidence above).
- I did **not** re-report the three known limitations (measured sensitivity 0/4 & specificity 0/1; the
  partly self-attested degraded check; the crawl-source-then-write-anchors bypass). All three are
  correctly and non-overclaimingly described in the code and docs.

## Workflow Feedback

- **Handoff gaps:** None in the handoff itself — it was the best-specified review contract I have
  worked from, and the two instructions that mattered most (*"grep for CALLERS, not definitions"* and
  *"devise a mutation of your own"*) are precisely what surfaced the blocker. One gap **in the
  underlying evidence contract**, independently confirming the implementer's own complaint: the
  required-evidence command is stale by construction because the gate *adds* a test file
  (`test_map_contract_wiring.py`) the fixed list cannot cover. The handoff patched this in prose
  ("the last file is the gate's own addition, which the original required-evidence list predates")
  rather than at the source. It should read "the listed suites **plus any test file this gate adds**".
- **Context rediscovered:** That `self_test()` must be **excluded as a traversal node** when auditing
  reachability. My first audit used `main` as an entrypoint; `main` reaches `self_test` via
  `--self-test`, so every self-tested helper reported PRODUCTION-REACHABLE and the audit came back
  clean. The defect only appeared on re-run with `self_test` blocked. This is exactly how the defect
  survived before: `--self-test` is itself a production entrypoint, so naive reachability launders dead
  code as live. **This belongs in doctrine** — "grep for the caller" is necessary but not sufficient
  when the module ships its own test harness as a subcommand; the rule needs to be *"prove a call site
  outside the def **and outside the self-test**."*
- **Instructions improvised around:** The reviewer skill says to record the Fowler pass "to
  `templates/FOWLER_PASS.template.json`" — the installed *template* path. Writing there would mutate
  the shared skill install for every future run. I wrote the record to
  `.agent-work/issue-304/g2-review/fowler-pass.json` instead (matching where the g1 reviews put theirs)
  and pointed the rail at it. The skill should say "instantiate FROM the template INTO your survey
  directory," as it already does for the survey itself.
- **What would have made this easier:** One line the implementer themself asked for and which would
  have found this blocker before it reached me — a per-slice **wiring grep** in the handoff, e.g.
  *"m3 lands only if `grep -n 'probe_fallbacks\|classify_substitute\|substitute_label' scripts/map_orient.py`
  shows a call site for **each** outside its own def and outside `self_test`."* Naming all three
  functions in one grep is what makes a partial fix visible.

## Return status
`complete`
