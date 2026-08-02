# REVIEW_RESULT — issue-304 gate g3

**Verdict: APPROVE**

Crew: `constellation/issue-304/g3/reviewer/attempt-1`
Worktree: `C:/Programs/constellation-skills-wt/e298-304`
Range reviewed: `a8d9467..HEAD` (9 commits, 20 files)
Survey: `.agent-work/issue-304/g3-review/review.json` — 13/13 checks visited, 13 pass, 0 fail,
consolidated `APPROVE`. Fowler record: `.agent-work/issue-304/g3-review/fowler-pass.json` (rail exit 0).

**Blockers: none.** Findings are 4 MINOR observations and 3 triage candidates.

---

## 1. CAN THIS CHECK FAIL — answered by execution

Four mutations of my own, **none among the nine in `tests/test_mutation_floor.py`** (all nine of those
target `scripts/map_orient.py`; mine target the shipped Commander template this gate actually edited).

Harness discipline, borrowed from the floor's own doctrine: each mutation **asserts it APPLIED** — the
JSON-encoded imperative must be unique in the file, the splice must land, the result must re-parse as
JSON — **before** it asserts red, so a non-matching substitution is a loud harness error and can never
masquerade as a killed mutant. The unmutated baseline is asserted GREEN first so a red is attributable.
Each restores in a `finally` and verifies the restore against git.

Harness: `<scratchpad>/mutate.py`. Verbatim output:

```
### BASELINE (unmutated HEAD) must be GREEN for a red to be attributable
--- pytest tail (baseline) ---
106 passed, 83 subtests passed in 2.13s
### exit: 0

==============================================================================
MUTATION: M1 T4-fires: delete the load-bearing substitute-and-record sentence
APPLIED: context imperative chars 2198 -> 1948; file chars 27365 -> 27115
=========================== short test summary info ===========================
FAILED tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives::test_overlay_phrase_occurs_exactly_once
FAILED tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives::test_substitute_and_record_rule_present
FAILED tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives::test_surviving_occurrence_is_the_rule_not_the_dead_claim
FAILED tests/test_context_manifest.py::CommanderSpineDeclaration::test_the_context_imperative_prose_is_not_replaced_by_the_declaration
FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_the_prose_rules_a_path_list_cannot_express_survive_the_rewrite
5 failed, 101 passed, 82 subtests passed in 2.14s
### exit: 1
RESULT: RED (mutant killed)
RESTORED: git diff --quiet HEAD exit = 0 (0 == identical to HEAD)

==============================================================================
MUTATION: M2 emptied imperative: replace the whole context imperative with a stub
APPLIED: context imperative chars 2198 -> 53; file chars 27365 -> 25220
    def test_substitute_and_record_rule_present(self) -> None:
>       self.assertIn(SUBSTITUTE_AND_RECORD, self.imp)
E       AssertionError: 'Where the repo carries no docs/agents/ overlay at all (e.g. a skill-source repo), substitute the closest repo doctrine you can find (README, CONTRIBUTING, top-level docs) and record the substitution' not found in 'Load baseline context. docs/agents/engine-config.json'
=========================== short test summary info ===========================
FAILED tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives::test_overlay_phrase_occurs_exactly_once
FAILED tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives::test_substitute_and_record_rule_present
FAILED tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives::test_surviving_occurrence_is_the_rule_not_the_dead_claim
3 failed, 5 passed, 6 subtests passed in 0.17s
### exit: 1
RESULT: RED (mutant killed)
RESTORED: git diff --quiet HEAD exit = 0 (0 == identical to HEAD)

==============================================================================
MUTATION: M3 reintroduce the dead block verbatim
APPLIED: context imperative chars 2198 -> 2570; file chars 27365 -> 27737
=========================== short test summary info ===========================
SUBFAILED(claim='a skill-source repo has no docs/agents/ overlay at all') tests/test_prose_deletions.py::SpineDeadPathProseAbsent::test_each_falsified_claim_absent
SUBFAILED(claim='do NOT create the overlay file') tests/test_prose_deletions.py::SpineDeadPathProseAbsent::test_each_falsified_claim_absent
FAILED tests/test_prose_deletions.py::SpineDeadPathProseAbsent::test_opening_phrase_absent
FAILED tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives::test_overlay_phrase_occurs_exactly_once
4 failed, 6 passed, 4 subtests passed in 0.18s
### exit: 1
RESULT: RED (mutant killed)
RESTORED: git diff --quiet HEAD exit = 0 (0 == identical to HEAD)

==============================================================================
MUTATION: M4 remove the re-pointed sentinel's prose
APPLIED: context imperative chars 2198 -> 2151; file chars 27365 -> 27318
=========================== short test summary info ===========================
FAILED tests/test_context_manifest.py::CommanderSpineDeclaration::test_the_context_imperative_prose_is_not_replaced_by_the_declaration
FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_the_prose_rules_a_path_list_cannot_express_survive_the_rewrite
2 failed, 104 passed, 82 subtests passed in 2.11s
### exit: 1
RESULT: RED (mutant killed)
RESTORED: git diff --quiet HEAD exit = 0 (0 == identical to HEAD)
```

**The decisive result is M2.** Replacing the whole context imperative with a 53-character stub is the
"template that deleted everything" the handoff names. Under that mutant the **five ABSENCE tests
PASSED** and only the **three PRESENCE tests failed**. That is the direct, executed proof that
`tests/test_prose_deletions.py` is not a one-directional deletion pin: an absence-only suite would have
been green on an emptied template, and this one is red. M3 closes the loop from the other side — the
absence half is live too.

**This check can fail. Verified, not asserted.**

## 2. The sentinel deviation — no assertion weaker than what it replaced

**(a) Was the claim true — does the deletion genuinely break those sentinels, with no narrower fix?**
Yes, verified by count rather than narrative:

```
--- OLD sentinel phrases: occurrence counts in PRE-deletion imperative ---
  before=1  after=0   'sanctioned degradation'
  before=1  after=0   'do NOT create the overlay file'
  before=1  after=1   'record the substitution'
```

Each old sentinel occurred **exactly once**, and only inside the block this gate was ordered to delete.
There is no narrower fix.

**(b) Necessary AND sufficient — reconstructed by running it.** I reverted *only* the two sentinel files
to `a8d9467`, left both templates at `HEAD`, and ran the **full** suite:

```
$ git show a8d9467:tests/test_context_manifest.py > tests/test_context_manifest.py
$ git show a8d9467:tests/test_map_contract_wiring.py > tests/test_map_contract_wiring.py
REVERTED the two sentinel files to a8d9467; templates left at HEAD
FAILED tests/test_context_manifest.py::CommanderSpineDeclaration::test_the_context_imperative_prose_is_not_replaced_by_the_declaration
FAILED tests/test_map_contract_wiring.py::ContextImperativeAnchor::test_the_prose_rules_a_path_list_cannot_express_survive_the_rewrite
2 failed, 1536 passed, 2 skipped, 481 subtests passed in 203.80s (0:03:23)
### now restoring
RESTORED: tests/ identical to HEAD
```

Exactly two failures across 1538 tests, both the named ones. The two edits were **necessary** (nothing
narrower works) and **sufficient** (nothing else in the corpus broke).

**(c) Assertion-by-assertion, by AST — not by line count:**

```
tests/test_context_manifest.py
  a8d9467: total assert* calls = 154  {'assertEqual': 86, ..., 'assertIn': 12, 'assertNotIn': 16, ...}
  HEAD:    total assert* calls = 154  {'assertEqual': 86, ..., 'assertIn': 12, 'assertNotIn': 16, ...}
  --- a8d9467 test_the_context_imperative_prose_is_not_replaced_by_the_declaration: 3 asserts
        assertIn('record the substitution', ...)
        assertIn('sanctioned degradation', ...)
        assertIn('do NOT create the overlay file', ...)
  --- HEAD    test_the_context_imperative_prose_is_not_replaced_by_the_declaration: 3 asserts
        assertIn('record the substitution', ...)
        assertIn('do not treat those paths as guaranteed to exist', ...)
        assertIn('degraded is a declared reading, never a licence to start from code', ...)

tests/test_map_contract_wiring.py
  a8d9467: total assert* calls = 33   HEAD: total assert* calls = 33
  --- a8d9467 test_the_prose_rules_a_path_list_cannot_express_survive_the_rewrite: 2 asserts
        assertIn('record the substitution', ...)
        assertIn('sanctioned degradation', ...)
  --- HEAD    test_the_prose_rules_a_path_list_cannot_express_survive_the_rewrite: 2 asserts
        assertIn('record the substitution', ...)
        assertIn('degraded is a declared reading, never a licence to start from code', ...)
```

Whole-file assertion totals **unchanged** (154 and 33). No assertion deleted. No assertion downgraded to
a weaker kind — every one is still `assertIn`, none became `assertTrue(x in y)`. No `skip`, no `xfail`.
The replacements are **longer and more specific** than what they replaced (22 -> 47 chars, 30 -> 66
chars).

**(d) Do the new sentinels pin something that would still be there for the right reason?** Yes. Both
replacements are *degraded-mode rules* — the same category the test's own name describes ("prose rules a
path list cannot express") — not phrases that merely happen to survive. And **M4 proves they still
bite**: deleting exactly that phrase turns both tests red.

**No assertion is weaker than what it replaced. This is a forced re-point, not a test changed to green.**

## 3. T4 — confirmed independently

```
--- overlay phrase count/offset ---
  before count: 2   after count: 1   after offset: 262
```

Count 2 -> 1 at offset **262**, inside the substitute-and-record sentence, both dead-path blocks gone.
And I checked the **pin**, not just the state: M1 removes the survivor and the suite goes red (three
`SubstituteAndRecordRuleSurvives` tests plus both sentinels). The survivor is genuinely pinned.

## 4. The 172-word count — re-derived, not accepted

`difflib.SequenceMatcher` over the JSON-decoded imperatives at `a8d9467` vs `ea52b2f` / `456cac0`:

```
=== SPINE context === removed segments: 1
 chars=566 words=86
 TOTAL WORDS REMOVED: 86
 len before/after chars: 2764 -> 2198
=== EXECUTE e0-context === removed segments: 1
 chars=569 words=86
 TOTAL WORDS REMOVED: 86
 len before/after chars: 911 -> 342
```

**86 + 86 = 172.** One contiguous removed span per template, nothing else removed. Confirmed, and it is
not 112.

## 5. Pre-registration integrity — the pathway is not void

```
=== blob OIDs of TRIPWIRES.md ===
0119fa4    13c41561db1b9d0e467e0a0183c13f00e842c2fc
1662b90    eab67aca3cc947fed3ed489cba059e52c05f46ac
ea52b2f    eab67aca3cc947fed3ed489cba059e52c05f46ac
456cac0    eab67aca3cc947fed3ed489cba059e52c05f46ac
baf09f2    eab67aca3cc947fed3ed489cba059e52c05f46ac
HEAD       eab67aca3cc947fed3ed489cba059e52c05f46ac
=== ancestry ===
0119fa4 IS ancestor of ea52b2f
0119fa4 IS ancestor of 456cac0
0119fa4 IS ancestor of baf09f2
1662b90 IS ancestor of ea52b2f
1662b90 IS ancestor of 456cac0
1662b90 IS ancestor of baf09f2
=== commit dates ===
0119fa4 2026-08-01 16:11:01 -0700 pre-register(#304): tripwire predictions BEFORE any prose deletion
1662b90 2026-08-01 16:20:20 -0700 pre-register(#304): T5, the anchor change, after PRE-B named the mechanism
ea52b2f 2026-08-01 20:51:48 -0700 g3 m1(#304): delete the dead-path block (a) from COMMANDER_SPINE context
=== worktree vs HEAD ===
worktree TRIPWIRES.md == HEAD (exit 0)
```

Compared by **blob OID**, never raw bytes. The file is byte-identical from `1662b90` through every
deletion commit to `HEAD`. `0119fa4 -> 1662b90` is a **pure addition** of the T5 section (+29 lines, 0
deletions) — T1–T4 were never touched after they were written. 6/6 ancestry checks positive.
Timestamps corroborate: predictions at 16:11 and 16:20, first deletion at 20:51 the same day.
**Nothing moved after the outcome was known.**

## 6. The RUN half — real, and independently reproduced

The transcript's sequence is genuine (384 lines, `.agent-work/issue-304/evidence/g3-run-transcript.txt`):
`REFUSED: context: postconditions unmet ['c2']` -> `RECEIPT-MISSING` exit 12 -> `DEGRADED-NO-MAP ...
still owed` exit 10 -> one re-run exit 0 -> `orientation contract SATISFIED / problems: 0` exit 0 ->
`context -> complete` -> later `e0-context -> complete`.

I did not take that on trust. Reproduced from scratch in a **throwaway temp fixture** (no tooling pointed
at `f1Brainz`; a `git init` dir with a `README.md`):

```
=== 1. verify-orientation with no receipt ===
no receipt at .../fixture-repo/.agent-work/rv-repro/map-orientation.json -- run `orient` first
RECEIPT-MISSING
### exit: 12
=== 2. orient, undischarged ===
DEGRADED-NO-MAP
candidates tried:
  [1] generated-map: docs/architecture/generated/map.json -> absent (absent)
  [2] index: docs/architecture/index.md -> absent (absent)
  [3] packets-dir: docs/architecture -> absent (absent)
degraded and NOT discharged -- still owed:
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  - unmapped (what stayed unmapped, stated plainly)
  - escalation (what you are escalating, and to whom)
### exit: 10
=== 3. ONE command discharges it ===
DEGRADED-NO-MAP
### exit: 0
=== 4. verify-orientation again ===
DEGRADED-NO-MAP
orientation contract SATISFIED
problems: 0
substitute: README.md [known-fallback] -- found in the fixed fallback set and present on disk
### exit: 0
```

**One command discharged it and work continued.** The contract reports; it does not deadlock. That is
the property the handoff asked me to confirm, and it holds.

## 7. The three honest nulls — all honest, none quietly scored as a pass

- **T3 mapped-repo clause — UNTESTED.** `TRIPWIRE_OUTCOMES.md` says *"First clause UNTESTED at this
  gate"* and, explicitly, *"It is not scored as HELD."* The summary table reads "HELD in part, UNTESTED
  in part". Episode `-003` a3 says *"scored untested, not held."* The stated reason checks out: `orient`
  probes three `docs/architecture/` candidates in this repo and all three report **absent**.
  **Not rounded up to a pass.**
- **T5 — NOT DETERMINABLE, stated as a measurement gap.** Recorded as exactly the gap `TRIPWIRES.md`
  instructed be reported rather than rounded off, with the reason named (a single scripted drive by the
  agent who authored the anchor is not a behavioural sample of tool ordering), and it hands POST a
  concrete requirement instead of a number. Its supporting claim was **re-run, not accepted**:

  ```
  $ grep -n 'map_before_src' scripts/map_orient.py
  ### exit: 1        (no match)
  $ grep -rn 'map_before_src' scripts/ skills/
  ### exit: 0        (no output — no hits)
  ```

  The only repo occurrences are a **docstring** in `tests/test_map_contract_wiring.py` and the PRE-B
  baseline records under `.agent-work/epic-298/baselines/`. **No code observes ordering.** The claim
  that the gate reads receipt *content* only is correct.
- **T1 — HELD with a named near-miss.** The exemption is genuine, not a rationalization. §2(b) above
  is the proof: reconstructing the exact moment of decision produced **exactly two failures out of
  1538**, both the two named literal-string-absence ones. **Nothing failed for any reason other than the
  literal string being absent.** The near-miss (the prediction's confidence rested on an inventory that
  was incomplete) is volunteered by the implementer, not extracted.

## 8. All five episodes observed something

None restates its prediction. Each carries a distinct `a2` (the pre-registered text) and a distinct `a3`
citing `0119fa4` (`-001`..`-004`) or `1662b90` (`-005`):

- `-001` a3 — names two concrete failures **by full node id** and reports the incomplete inventory
  behind the prediction. Information the prediction did not contain.
- `-002` a3 — quotes verbatim engine output `e0-context -> complete` exit 0, and the `ls -l` result for
  the absent `config_ref`, before and after.
- `-003` a3 — splits the outcome (degraded clause did-not-fire with exit codes 12/10/0; mapped clause
  NOT TESTED) **and** reports that the handoff's own premise was falsified by checking all 8 commits.
- `-004` a3 — quotes the deletion script's refusal guard and its printed count (`... : 1`).
- `-005` a3 — reports NOT DETERMINABLE with the grep exit code and states what POST must do to close it.

Every `a3` contains information that could only come from having run the thing.

---

## Findings

### Blockers
**None.**

### MINOR (observations — no action required of this gate)

1. **A re-pointed sentinel's coverage is less independent than the phrase it replaced.** In
   `tests/test_context_manifest.py`, `"do not treat those paths as guaranteed to exist"` sits at offset
   **440**, in the **same sentence** as the surviving `"record the substitution"` at offset **414** — 26
   characters apart. The phrase it replaced sat ~700 characters away in a different rule. So that
   assertion now overlaps its neighbour instead of covering separate ground. It is **not redundant** (it
   still catches truncation of the sentence's tail clause) and it is **not weaker** in the strict sense —
   it pins live prose where its predecessor pinned prose this gate deliberately deleted, and M4 shows it
   bites. Recorded so the claim "counts and intent unchanged" is read precisely: the *count* is
   unchanged and the *intent* is preserved, but the number of **distinct prose rules** pinned by that
   test went 3 -> 2. `tests/test_map_contract_wiring.py`'s replacement is in a different sentence and
   has no such overlap.
2. **Trend snapshot successor timing diverges from the amendment as the reviewer handoff states it.**
   The reviewer handoff says the successor is *"due at epic-298 close"*. `TREND_SNAPSHOT.md` §0 instead
   binds it to *"the close of the epic that follows it"* — i.e. one epic **later**. The implementer's own
   handoff (STEP 6) required only "name its consumer" + "state when the successor is expected", which
   the file satisfies, and the retire-if-unread rule **is** stated (*"it should be deleted rather than
   maintained if that successor is never taken"*). This is a **handoff divergence for the Commander to
   reconcile**, not an implementer defect. If the Admiral meant epic-298 close, one sentence in §0 needs
   changing.
3. **Fowler: duplicated code in the new test scaffolding.** `SpineDeadPathProseAbsent` and
   `ExecutePlanDeadPathProseAbsent` are structurally identical classes differing only in
   `(path, step, opening-phrase)`; an `imperative(...)` reader helper now exists in three test modules
   with three signatures. 12 lines, test-only, and collapsing it would trade legible per-template failure
   names for brevity. Fair call to leave — raised for the record, not for action.
4. **Fowler: shotgun surgery is real here.** Deleting one prose block took coordinated edits in 5 files
   and left 2 further live references behind. The implementer found and named both stragglers itself and
   correctly declined to edit a historical drill record. The durable fix is a design question, filed
   below.

### Triage candidates (out of scope — flagged, not fixed)

- **tc1** — `scripts/verify_context_declaration.py` module docstring (lines 10–11) still quotes
  *"a missing engine-config is a sanctioned degradation, do NOT create the overlay file"* as its
  illustration. Illustrative only; the lint does not enforce it. It now cites text that exists nowhere in
  the corpus.
- **tc2** — `docs/superpowers/drills/dogfood-context-paths-absent.md` (lines 43, 79–80) quotes the
  deleted clause as *observed run behaviour*. A historical record; a dated note that the quoted doctrine
  was deleted at #304 is the right treatment, and it is a doc owner's call.
- **tc3** — Prose sentinels are scattered across suites named for unrelated properties, which is why one
  deletion needed 5 coordinated edits and still left 2 stragglers. Consider a single registry of pinned
  prose phrases, or a lint that fails when a pinned phrase disappears from the corpus.

---

## Constraint compliance

| Constraint | Status |
|---|---|
| `python -m pytest`, never `py -m pytest` | **Met** — every invocation used `python -m pytest` / `sys.executable -m pytest` |
| Flag any 3.13+-only API as a BLOCK | **No BLOCK.** Swept every added line for `itertools.batched`, `typing.override`/`@override`, `warnings.deprecated`, `Path.full_match`, `copy.replace`, `random.binomialvariate`, PEP-695 type-parameter syntax, `StrEnum`, `tomllib`, `except*`, `asyncio.TaskGroup`, `os.process_cpu_count`, `glob.translate`, `dbm.sqlite3` — **no match**. `tests/test_prose_deletions.py` imports only `json`, `unittest`, `pathlib`, `__future__.annotations`. Runtime is CPython 3.14.3, but nothing added requires >3.8. |
| Compare normalized content or blob OIDs, never raw bytes | **Met** — and the trap fired on me. My mutation harness restored LF-only bytes; `git diff --quiet HEAD` returned **0** (content identical) while `git status --porcelain` showed a phantom ` M`. Restored exact bytes with `git checkout HEAD --`; worktree blob OID is now `e74295ea094cc55840c5252f27659aed42745833` == `HEAD`. Five agents now. |
| Do not point tooling at `C:/Programs/f1Brainz` | **Met** — degraded reproduction used a throwaway `git init` fixture in the scratchpad |
| Never touch `constellation-skills` or `e298-331` | **Met** |
| Do not rewrite `TRIPWIRES.md` | **Met** — blob unchanged (`eab67ac` at HEAD and in the worktree) |
| Do not fix anything | **Met** — no change to the work under review; all mutations reverted and verified |

**Worktree state on exit:** `skills/`, `tests/`, `episodes/` and `TRIPWIRES.md` all identical to `HEAD`.
The only modifications are pre-existing Commander spine state I never touched
(`.agent-work/issue-304/{crew-runs.json,execute.json,execute.json.journal}`) plus my own survey directory
`.agent-work/issue-304/g3-review/` (untracked).

## Full-suite evidence at HEAD

```
$ python -m pytest tests/ -q
1538 passed, 2 skipped, 481 subtests passed in 224.54s (0:03:44)
```

---

## Workflow Feedback

1. **The reviewer handoff and the implementer handoff disagree about the trend snapshot's successor**
   (§Findings MINOR-2). The reviewer handoff states the Admiral amendment as *"the successor is due at
   epic-298 close, and the retire-if-unread rule must be stated"*; the implementer's STEP 6 says only
   *"name its consumer — the next snapshot — and state when the successor is expected"*, with no
   epic-298-close binding and no retire-if-unread requirement. I had to go read the implementer handoff
   to work out which contract to grade against, and I graded against the one the implementer was
   actually given. **A reviewer handoff should not introduce acceptance criteria the implementer was
   never handed.**
2. **No "Survey State Location" field in the handoff.** The skill names
   `.agent-work/<work-id>/<gate>-review/review.json`; the handoff's Return format names only the
   `REVIEW_RESULT` path. I improvised `.agent-work/issue-304/g3-review/review.json` from the skill's
   convention (and found the directory already created but empty). Worth adding the field explicitly —
   `g1-review`, `g1-review-2`, `g2-review`, `g2-review-2` already exist with inconsistent naming.
3. **Which engine copy governs is still unflagged at dispatch.** The installed
   `constellation-reviewer/scripts/checklist_engine.py` and the repo's vendored
   `scripts/checklist_engine.py` **diverge** (117,715 vs 126,300 normalized bytes). The workbench
   dogfooding rule says drive the repo's own copy on the skill-source repo; the reviewer SKILL.md says
   drive "this skill's bundled engine". I followed the dogfooding rule. This ambiguity is one line of
   handoff away from being settled and it recurs on every dispatch into this repo.
4. **The CRLF trap deserves a one-line recipe, not just a warning.** The handoff warns that four agents
   have been bitten. It bit me too — not on *reading* state but on *writing* it: any Python
   `read_text()`/`write_text()` round-trip silently converts CRLF to LF, producing a phantom ` M` that
   `git diff --quiet HEAD` reports as clean. The recipe that works is `git checkout HEAD -- <path>` for
   restore, then compare `git hash-object <path>` against `git rev-parse HEAD:<path>`. Adding those two
   commands to the constraint would end this.
5. **What worked and should be kept:** the handoff naming the *specific attacks* rather than asking for
   generic conformance. "Devise a mutation that is not among the nine, break the presence side, report
   red/green with real output" is an instruction that cannot be satisfied by reading. It is the single
   reason this review has an executed answer to "can this check fail" instead of an opinion — and the
   implementer's own two-directional pin held up under every one of them.
