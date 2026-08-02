# Review Result 2 — issue-304 gate g2, scoped re-review of the m7 rework

Status values follow `skills/workbench/references/status-model.md`.

Companion to `g2-review-result.md` (round 1, BLOCK). **I wrote a separate file rather than appending** —
round 1 is the record of a BLOCK that was correct and acted on, and overwriting it would erase the
evidence trail that produced the fix.

Scope: the m7 fix (`9d57e9b`) and the narrative correction **only**, per the Commander's instruction.
Everything cleared in round 1 was re-checked *only* for collateral damage.

Survey: `.agent-work/issue-304/g2-review-2/review.json`, session
`constellation/issue-304/g2/reviewer/attempt-2`, consolidated `verdict=APPROVE findings=0`.

## Assigned Gate
`g2 — wire the contract at context and plan` (rework round)

## Result
`APPROVE`

---

## 1. Does the fix actually discharge the blocker? — **Yes, and it is not decorative.**

### The blocker is discharged

Re-ran my round-1 method verbatim — AST reachability from the three **real** subcommands, with
`self_test` **blocked as a traversal node** (the blocking is the whole point; without it the defect
hides):

```
substitute_label production-reachable (self_test BLOCKED): True

functions NOT reachable from the three real subcommands:
   _utf8_stdio                  DEAD
   (only _utf8_stdio expected -- module-level call at :250, g1 code)
```

Concrete call site, outside its own `def` and outside the harness:

```
$ grep -rn "substitute_label" --include=*.py . | grep -v "^./.agent-work"
./scripts/map_orient.py:704:def substitute_label(entry: object) -> str:
./scripts/map_orient.py:938:    Decoding is deliberately lenient (`substitute_label`): a receipt written
./scripts/map_orient.py:958:        label = substitute_label(entry)          <-- PRODUCTION
./scripts/map_orient.py:1607: … (self_test)
./scripts/map_orient.py:1612: … (self_test)
./scripts/map_orient.py:1617: … (self_test)

  render_verify_report     lines 923-965      <- :958 lands here
  cmd_verify_orientation   lines 1210-1235    <- and calls it
  self_test                lines 1306-1629    <- :958 is nowhere near this
```

The `source` key is now genuinely **read**, not merely written — written at `:1154` by
`pin_substitutes`, read at `:706` through `substitute_label` on the render path. **The Commander's
constraint that `source` stay on each receipt entry is honored** — untouched, still the committed prior
declaration `verify-frame` checks a frame against.

### It is not decorative — proved by attacking the call site

Three mutations of my own, all provably outside the two the rework shipped (**#9** label forced to
`known-fallback`, **#10** provenance line dropped). **All three RED.**

#### MINE-F — the decorative-wiring attack (the one you asked for)

Leave `render_verify_report` **perfectly correct** and starve it at the **call site**. If the wiring
were ceremonial, this stays green.

```
diff --git a/scripts/map_orient.py b/scripts/map_orient.py
@@ -1227,5 +1227,5 @@ def cmd_verify_orientation(args: argparse.Namespace) -> int:
     for line in render_verify_report(
         first_line, code, problems, _rel(root, path),
-        declared if isinstance(declared, list) else [],
+        [],
     ):
         print(line)
```

```
  --- pytest returncode: 1 ---
E  AssertionError: 'known-fallback' not found in 'DEGRADED-NO-MAP\nreceipt: .agent-work/w/map-orientation.json\norientation contract SATISFIED\nproblems: 0\n'
E  AssertionError: 'README.md' not found in 'DEGRADED-NO-MAP\n…problems: 0\n'
E  AssertionError: 'agent-declared' not found in 'DEGRADED-NO-MAP\n…problems: 0\n'
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_BOTH_labels_appear_in_one_real_report
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_a_present_known_fallback_is_REPORTED_as_known_fallback
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_a_receipt_with_no_source_key_reports_as_agent_declared
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_an_agent_declared_substitute_is_REPORTED_as_unverified
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_an_unrecognised_source_value_reports_as_agent_declared
5 failed, 101 passed, 53 subtests passed in 16.44s

  VERDICT MINE-F: RED (killed)
```

**This is the answer to your question.** The tests assert against real **subprocess stdout**, so cutting
the feed — not the renderer — is what they catch. The wiring is pinned.

#### MINE-E — correct label, lying prose

```
@@ -958,5 +958,5 @@ def render_verify_report(
         label = substitute_label(entry)
-        if label == LABEL_KNOWN_FALLBACK:
+        if True:
             note = "found in the fixed fallback set and present on disk"
```

```
  --- pytest returncode: 1 ---
E  AssertionError: 'UNVERIFIED' not found in 'DEGRADED-NO-MAP\n…substitute: 
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_an_agent_declared_substitute_is_REPORTED_as_unverified
1 failed, 105 passed, 53 subtests passed in 16.15s

  VERDICT MINE-E: RED (killed)
```

The human-readable half is pinned too, not just the machine-readable label.

#### MINE-G — lenient decoding removed

```
@@ -704,5 +704,5 @@ def substitute_label(entry: object) -> str:
-    if isinstance(entry, dict) and entry.get("source") in SUBSTITUTE_LABELS:
+    if isinstance(entry, dict) and entry.get("source"):
         return entry["source"]
```

```
  --- pytest returncode: 1 ---
E  AssertionError: 13 != 0 : self-test FAILED: 1 check(s)
E    - a bogus label reads as unverified
E  AssertionError: 'agent-declared' not found in 'DEGRADED-NO-MAP\n…
FAILED tests/test_map_orient.py::ContractShape::test_self_test_floor_passes
FAILED tests/test_map_orient.py::SubstituteProvenanceIsReported::test_an_unrecognised_source_value_reports_as_agent_declared
2 failed, 104 passed, 53 subtests passed in 16.43s

  VERDICT MINE-G: RED (killed)
```

Applied-before-red discipline held on all three (anchor unique = 1, gone after substitution = 0,
replacement 0 → 1). Restores, blob OID not raw bytes:

```
  committed dbac7795c6a391bb1d1f7787d5a05565be3c2b5f
  worktree  dbac7795c6a391bb1d1f7787d5a05565be3c2b5f
  MATCH: True | git diff --quiet HEAD exit: 0 | porcelain: '?? .agent-work/issue-304/g2-review-2/'
```

**On your rationale:** the fix serves it. The stated value was *REPORTED* degraded mode — a reader
seeing the distinction between "the filesystem agreed" and "the agent said so." That distinction now
reaches a human in one report, and I confirmed it in real output rather than in a test (§2, block B).
I also agree with refusing option (c); MINE-F is precisely the mutation that a documented-but-unread
decoder would have survived.

---

## 2. `orient` must still never print an anchor id — **verified by running it, and attacked**

Scanned actual stdout with `ANCHOR_RE` (`\b(?:struct|capability|event|constraint|assumption|claim|decision):[A-Za-z0-9_.\-]+\b`)
rather than eyeballing. All fixtures in my scratchpad; **`C:/Programs/f1Brainz` never given to any tool.**

**(A) RESOLVED repo** — map declares `struct:solver_core`, `struct:io_layer`, `decision:use_wal`,
`capability:solve`:

```
--- orient stdout ---
RESOLVED
entrypoint: docs/architecture/index.md
anchor_count: 4
  [2] index: docs/architecture/index.md -> hit (4 unique anchors)
  ANCHOR IDS IN OUTPUT: NONE  OK

--- verify-orientation stdout ---
RESOLVED
receipt: .agent-work/w/map-orientation.json
orientation contract SATISFIED
problems: 0
  ANCHOR IDS IN OUTPUT: NONE  OK
```

**(B) The sharp attack — substitute CONTENT deliberately stuffed with anchor ids.** `README.md` cites
`struct:app`, `decision:d99`, `capability:cap_x`; `docs/notes/mine.md` cites `struct:secret_module`,
`event:boom`. This is the new print path carrying attacker-chosen content:

```
--- verify-orientation stdout (THE NEW OUTPUT SURFACE) ---
DEGRADED-NO-MAP
receipt: .agent-work/w/map-orientation.json
orientation contract SATISFIED
problems: 0
substitute: README.md [known-fallback] -- found in the fixed fallback set and present on disk
substitute: docs/notes/mine.md [agent-declared] -- UNVERIFIED -- declared by the agent, not corroborated by the filesystem
  ANCHOR IDS IN OUTPUT: NONE  OK
```

Only the **path** is echoed, never the content — and the path was agent-supplied to begin with, so
nothing is handed over that the tool was not already given. This block is also the clearest
demonstration that the deliverable now does what it exists to do: both labels, side by side, legible.

**(C) Smuggling an anchor through the substitute path itself** (`docs/struct_app.md`):

```
substitute: docs/struct_app.md [agent-declared] -- UNVERIFIED -- declared by the agent, not corroborated by the filesystem
  ANCHOR IDS IN OUTPUT: NONE  OK
```

**Reserved-first-line contract survives** the added output — first lines across all three runs were
`RESOLVED` / `DEGRADED-NO-MAP` / `DEGRADED-NO-MAP`, all reserved literals, with provenance lines
strictly below.

---

## 3. The narrative correction — **accurate, and it states the mechanism**

The `CORRECTION (rework m7)` block in `g2-result.md` does both things you asked for.

**Names the third helper:**

> `probe_fallbacks` and `classify_substitute` got call sites; **`substitute_label` did not.** It
> stayed reachable only from `self_test()`, so the `source` key was written to every receipt and read
> back by nothing — no output surface, no test outside the module's own harness.

**States the mechanism, not an apology:**

> **Why my reachability pass missed it, stated plainly:** I grepped for call sites rooted at `main`
> as the entrypoint. `main` reaches `self_test` via the `--self-test` subcommand, so every
> self-tested helper came back "reachable" — including one whose only caller was the test harness.
> **A module that ships its own test harness as a subcommand launders dead code as live.**

That is exactly the mechanism I found, stated better than I stated it. It goes past the requirement
with a self-critique worth keeping:

> Finding it once did not stop me from reproducing it, because I fixed the *instance* and never
> fixed the *method*.

Deviation 7 records the incomplete-audit-reported-as-complete honestly. **The transferable finding is
not lost** — it lands in the correction block, in the new test-file header, in mutation #9's `why`
string, and in the corrected rule (*a call site outside the def AND outside the self-test*), which is
what #364 carries.

**Deviation 8 independently verified.** The claim that the engine refused `append` on the gated plan is
true — reproduced on a **copy** in my scratchpad, never the live plan:

```
$ …checklist_engine.py --file <SCRATCH COPY of the gated plan> append m99 …
REFUSED: append only on survey checklists

$ …checklist_engine.py --file <my survey> append x99 …
appended x99
```

The gated-vs-survey asymmetry is real, so `amend` was the right verb. The plan carries `type: gated`
with `items [… m6, m7]` and `m7 status=complete`. Appending `m7` rather than reopening `m3` was also
the right call for the reason you gave — `reopen` would cascade-reset m4–m6, whose reds cannot honestly
be re-observed.

*(Housekeeping: my contrast probe genuinely appended `x99` to my own survey. I disposed of it through
the engine with `skip` and a reason naming it as a probe, rather than leaving it dangling or
hand-editing the file.)*

---

## 4. Collateral damage — none

```
$ python -m pytest tests/test_map_orient.py tests/test_mutation_floor.py tests/test_context_manifest.py \
    tests/test_context_declaration_lint.py tests/test_context_determinism.py \
    tests/test_install_constellation.py tests/test_map_contract_wiring.py -q

312 passed, 435 subtests passed in 210.34s (0:03:30)
exit code 0
```

Matches your 312/435. Up from round 1's **303/433** — **+9 tests, +2 subtests, nothing lost**.

```
$ python scripts/map_orient.py --self-test   ->  self-test OK   PY314_EXIT=0
$ py     scripts/map_orient.py --self-test   ->  self-test OK   PY312_EXIT=0   # CI's pin
$ py -c "py_compile.compile('scripts/map_orient.py', doraise=True)"
  map_orient.py COMPILES under 3.12.13
```

The PR #320 / 39-CI-failure hazard stays closed.

```
=== rework scope outside .agent-work ===
scripts/map_orient.py
tests/test_map_orient.py
tests/test_mutation_floor.py

=== no new exit codes (vs g1 baseline) ===
IDENTICAL: no new exit codes

=== template-pinning suites still blob-identical to 6d35fe2 ===
  tests/test_context_manifest.py           UNCHANGED: YES  (96a3e46e…)
  tests/test_context_declaration_lint.py   UNCHANGED: YES  (2574bc1b…)
  tests/test_context_determinism.py        UNCHANGED: YES  (bf2a0390…)

=== COMMANDER_SPINE untouched by the rework ===
  ec1d132: 5062325d38199b00759c1b7b151910a4625d6945
  HEAD   : 5062325d38199b00759c1b7b151910a4625d6945
```

No template and no installer touched, so round 1's clearance of those still stands unmodified.
Worktree left clean — only my own untracked review artifacts.

## Blockers
- None.

## Out-of-scope observations
- `render_verify_report()` now takes **5 parameters** (the rework added `substitutes`, defaulted). Same
  family as round 1's `build_receipt`-at-7 note. Rather than another per-function observation, one
  keyword-only pass across `map_orient.py` would settle both. Quality only, no defect. Flagged as `tc1`.
- The provenance line is emitted by `verify-orientation` but not by `orient`. I probed whether that is a
  gap and concluded it is **correct**: `orient` would be printing a label it computed moments earlier,
  whereas `verify-orientation` decodes a receipt read back **from disk**, which is the only place the
  lenient-decode contract (an older receipt with no `source` must read as `agent-declared`, never
  upgraded by omission) is real. Recording the reasoning so it is not re-litigated, not as a finding.

## Workflow Feedback
- **Handoff gaps:** None — and the scoping was the reason this round was cheap. Naming the three
  questions, pre-declaring the two shipped mutations so mine were provably outside them, and stating
  what was already cleared meant I spent my context on the decisive test (MINE-F) instead of
  re-deriving round 1. This is the shape a re-review handoff should have.
- **Context rediscovered:** Nothing material. The one thing I had to derive was that `self_test`'s line
  span moved (`1274` → `1306-1629`) after the edit, so "outside `self_test`" needed re-measuring rather
  than reusing round 1's numbers. Cheap, but it is the kind of stale line reference that silently rots
  in a report — computing the span from the AST rather than citing a line number would be sturdier.
- **Instructions improvised around:** Verifying the deviation-8 `append` refusal required *running* the
  refusing verb. There is no dry-run or read-only probe for "would this verb be refused on this
  controller type," so I copied the plan to scratch to attack it and used my own survey as the contrast
  — which mutated my survey with a junk item I then had to dispose of through `skip`. A
  `--dry-run` on the mutating verbs (the top-level flag exists but is not wired for this) would let a
  reviewer test a refusal claim without dirtying real state.
- **What would have made this easier:** Nothing for this round. Carrying forward from round 1: the
  wiring-grep line (#364) is the change that prevents this class outright, and it is already filed.

## Return status
`complete`
