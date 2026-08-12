# Implementation Result

## Assigned gate
`epic-559/c1-spine-lint` rework spine (`z1-idiom`, `z2-interpreter`, `z3-resweep`, `z4-verify`), following the reviewer's `v1` blocker on the original `g1`-`g4` run.

## Completed slice
Fixed the two mechanisms behind fault 2's (`falsifiable-zero-collected`) false positives, found by the reviewer's real-corpus sweep:

1. **The idiom bug (`z1`).** `_pytest_segments` split a command on bare `|`, so in the corpus's own recommended self-checking idiom — `test $(pytest ... --collect-only 2>/dev/null | grep -c '::') -ge N && pytest ...` — the `2>/dev/null` token landed inside the first segment. `shlex` tokenized it as one opaque word, `_pytest_targets` folded it in as a bogus positional pytest target (a nonexistent path), and `_collects_zero` ran pytest against that path and reported zero. Fixed by excluding shell-redirect-shaped tokens (`_REDIRECT_TOKEN_RE`/`_REDIRECT_OPERATOR_ONLY_RE`) from `_pytest_targets`, including the split-token form (`2> /dev/null`, two shlex tokens).
2. **The interpreter bug (`z2`).** `_collects_zero` always re-invoked pytest with `sys.executable`, discarding whatever interpreter the check's own command text named, and never confirmed pytest was importable there before trusting an empty result as "collected zero." On a host where `python3` has no pytest, `python3 -m scripts.validate_spine` produced 6 spurious zero-collect faults that `python -m scripts.validate_spine` on the identical file did not. Fixed by `_resolve_interpreter`: it resolves the interpreter the command text actually names (parsed out of `_pytest_segments`, stripping the `$(...)` command-substitution prefix), confirms `pytest` imports there via a probe subprocess, and returns `None` (undecidable, not a fault) when it cannot resolve or confirm.

Then re-swept the full corpus with both fixes in (`z3`) and verified the full suite, rebuilt `map/INDEX.md`, and committed (`z4`).

## Scope
**Files changed:**
- `scripts/validate_spine.py` (+108/-15: the two fixes above)
- `tests/test_validate_spine.py` (+116/-6: regression coverage for both, `-k "Idiom or Redirect"` and `-k "Interpreter or Unavailable"`)
- `map/INDEX.md` (rebuilt)

**Specific exclusions touched:** no. `check_idiom.py` and `check_corpus_fp.py` (Admiral-authored check scripts) were not edited, per the handoff — I blocked `z3` instead when I believed `check_corpus_fp.py`'s scope was wrong, and the Admiral fixed it (see Stop conditions hit). `checklist_engine.py`, `mcp_spine_server.py`, `run_crew.py`, `settings.json`, `docs/agents/*`, and every shipped spine template are untouched.

## Behavior changed
Yes. `validate_spine.py` no longer flags the corpus's own documented self-checking idiom, and no longer produces interpreter-dependent output — the same spine file now validates identically regardless of which `python` on the host ran the checker itself.

## Map Impact
- **Structural anchors touched:** `scripts.validate_spine` (leaf module, no shape change — same public `validate`/`validate_file`/`discover_checklist_templates` API as the original gate; two private helpers added: `_resolve_interpreter`, `_COMMAND_SUBSTITUTION_PREFIX_RE`/`_REDIRECT_TOKEN_RE`/`_REDIRECT_OPERATOR_ONLY_RE`).
- **Capabilities added/changed/affected:** fault 2 (`falsifiable-zero-collected`) is now safe to trust against the corpus's own recommended idiom and is interpreter-independent — the reviewer's `BLOCK` condition is resolved.
- **Constraints/assumptions touched:** `_resolve_interpreter` never falls back silently to `sys.executable` when the command names its own interpreter; an unresolvable/no-pytest interpreter now yields `None` (undecidable) rather than a false fault. Callers of `_collects_zero` must treat `None` as "no verdict," same as before this rework.
- **Trust limitations / drift found:** `check_corpus_fp.py`'s original population (all of `.agent-work/`, filtered only by filename) assumed every spine under it ran its checks for real — true for this epic's own spines, false for spines archived from earlier epics whose selectors point at tests since renamed or deleted. The Admiral has since scoped it to `epic-559`/`epic-418-followon` (14 files); the epic-298 case is recorded as evidence the lint works, not forced clean. This is now resolved, not open, but worth carrying forward: any future corpus-wide check script needs the same scoping care.
- **Triage candidates:** none new this rework. The two already logged in the original `IMPLEMENTER_RESULT.pass1.md` (the `init_work_area._RESOLVER_OWNED_TOKEN_RE` bare-`<skill-dir>` gap; `checklist-engine.md`'s stale Template-set table) are unaffected by this rework and still open for a later wave.

## Test mode
**Required:** test-first (TDD implied by each gate's frozen postcondition — a `pytest --collect-only` floor plus a real run).
**Satisfied:** yes. Reproduced both reported bugs live before writing the fix: the idiom's first segment folding `2>/dev/null` in as a bogus target (`z1`), and `python3 -m scripts.validate_spine` vs `python -m scripts.validate_spine` producing different fault counts on the same file (`z2`) — see TDD evidence below.

## Evidence

```bash
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
2652 passed, 1 skipped, 1121 subtests passed in 107.03s
```
**Result:** pass.

```bash
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE NO_COLOR=1 python -m pytest -q tests/test_validate_spine.py
76 passed
```
**Result:** pass (was 61 at the original gate's close; +15 from `z1`/`z2` regression coverage).

```bash
$ python .agent-work/epic-559/c1-spine-lint/check_corpus_fp.py
examined 14 spine files
```
**Result:** exit 0 (was exit 1 with the epic-298 true positive, before the Admiral rescoped the check's population — see Stop conditions hit).

**Full-corpus resweep (`z3`), population = every file under `.agent-work/` whose own `type` field is `gated` or `survey` (540 files) plus the 12 shipped templates = 552, matching the reviewer's 539+12 baseline within one file of natural drift:**

| fault class | reviewer baseline (pre-fix) | this resweep (post-fix) |
|---|---|---|
| fault-1 `falsifiable-all-null` | not separately reported | 637 (616 corpus + 21 templates) — unaffected |
| fault-2 `falsifiable-zero-collected` | 9 hits, 8 false positive / 1 true positive (~88.9% FP) | 1 hit, 0 false positive / 1 true positive (0% FP) |
| fault-3 `falsifiable-artifact-asserts-property` | 128 hits, 3 distinct texts, all hand-verified genuine | 128 hits — identical count, stayed clean |
| fault-4 `falsifiable-unresolved-placeholder` | not separately reported | 45 (43 corpus + 2 templates) |

Faults 1, 3, and 4 hold their exact reviewer-baseline counts (128 for fault 3 confirmed identical; the neither-fix touches those code paths at all), so they were not re-litigated per the handoff's instruction — only reconfirmed clean.

Fault 2's single remaining hit, hand-inspected (not sampled — it is the only distinct trigger in the full sweep):
`.agent-work/epic-298/harvest/300-full/archive/2026-08-01-300/g1-implement/PLAN-rework1.json`, task `m1-blocker-skiptest.postconditions.c2`, selector `-k 'live_spine'` against `tests/test_context_manifest.py`. The check's command (`cd C:/Programs/constellation-skills-wt/298-300 && python -m pytest tests/test_context_manifest.py -q -k 'live_spine' --no-header`) has no redirect token, and its interpreter — literally `python` — resolves with pytest importable, so neither fixed mechanism explains this hit. It is a **true positive**: the referenced test (`test_a_live_spine_in_this_work_area_also_projects`, added in `75ee317a`) was renamed away in `0b15d5b8` ("fix(context): make the acceptance test and the /run exclusion actually falsify (#300)"), an unrelated commit from epic-298, not epic-559. This is a frozen historical record from epic-298's own archive (`archive/2026-08-01-300`, authored on a different machine per its Windows `cd` path), bulk-committed later via `c2e16a87` ("track .agent-work/ -- run history is project history"). It is the single best piece of evidence in this run that the lint catches real defects, not just its own past false positives.

## TDD evidence, if required
- Failing test observed (`z1`): before the redirect-token fix, a check running the corpus's own idiom over 32 real, passing tests (`pytest tests/test_validate_spine.py -k Shape`) was flagged `falsifiable-zero-collected` — verified live via `check_idiom.py`, which the Admiral had already written to pin this exact case, exiting 1 before the fix.
- Failing test observed (`z2`): before the interpreter fix, `python3 -m scripts.validate_spine .agent-work/w5-gates/execute.json` produced 6 spurious zero-collect faults on a host where `python3` has no pytest, while `python -m scripts.validate_spine` on the identical file produced 0 — reproduced directly via the CLI before any code changed.
- Passing test observed: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE NO_COLOR=1 python -m pytest -q tests/test_validate_spine.py -k "Idiom or Redirect"` and `-k "Interpreter or Unavailable"` both green; `check_idiom.py` exits 0; the two CLI invocations above now produce identical output.
- Refactor while green: no separate refactor pass — both fixes were applied as the minimal change to the reported mechanism, with regression tests added alongside.

## Docs/contracts touched
- none — `map/INDEX.md` is regenerated output, not an authored contract.

## Assumptions
- `check_corpus_fp.py`'s population (`.agent-work/epic-559` + `.agent-work/epic-418-followon`, filtered to `PLAN`/`SPINE` filenames) is the Admiral's own scoping decision after my `z3` block, not mine to second-guess further — I ran it as given and it exits 0.
- The `z3` resweep's "every gated-or-survey spine under `.agent-work/`" population is defined by each file's own `type` field (`gated`/`survey`), matching the reviewer's methodology exactly (confirmed by reproducing the reviewer's unaffected-family counts to the digit) — not a filename-substring filter, which over- and under-counts (verified: a naive `PLAN`/`SPINE`-in-filename filter found only 358 files and misclassified non-checklist JSON as shape faults).

## Stop conditions hit
- Blocked `z3` (not waived) on a single remaining zero-collect finding that neither fix explained. Named the reason precisely (redirect-token-free, interpreter resolves, selector genuinely collects zero against a since-renamed test) rather than forcing it clean. The Admiral confirmed the block was correct — the finding is a true positive from an out-of-scope archived epic, and `check_corpus_fp.py`'s population was the thing that was actually wrong. The Admiral rescoped that script (not mine to edit) and resumed the gate; see `UNBLOCK_HANDOFF.md`. This is the run's clearest piece of evidence that the lint works: it caught something real, I did not paper over it, and the right rung fixed the right thing.

## Out-of-scope observations
- None new. The two carried forward from the original run (`init_work_area._RESOLVER_OWNED_TOKEN_RE`'s bare `<skill-dir>` gap; `checklist-engine.md`'s stale Template-set table) are unaffected by this rework and remain open triage candidates.

## Workflow Feedback

- **Handoff gaps:** none in `UNBLOCK_HANDOFF.md`'s wording — it named the exact file, task id, and selector for the resolved finding, and was directly actionable without rediscovery.
- **Context rediscovered:** the reviewer's exact corpus-population methodology (filter by each file's own `type` field, not filename) wasn't restated in the rework handoff and had to be re-derived by reproducing the reviewer's unaffected-family counts (128 for fault 3) until they matched exactly — a naive filename filter gave a materially different, wrong population (358 files instead of 540). Worth naming explicitly in a `z3`-shaped handoff next time: "population = `type` field, not filename," since it's cheap to get wrong silently (the wrong population still runs, just measures the wrong thing).
- **Instructions improvised around:** none this rework — the two fixes were narrowly scoped to the reported mechanisms, and the block/resume cycle for `z3` worked exactly as the reach-up mechanism describes.
- **What would have made this easier:** nothing concrete beyond the population-methodology note above; this rework's handoffs (`REWORK_PLAN.json`, `UNBLOCK_HANDOFF.md`) were unusually precise about root cause, reproduction, and scope.

## Return status
`complete`

---

# u1: the lint must be able to say it could not tell

## Assigned gate
`epic-559/c1-spine-lint` `UNDECIDABLE_PLAN.json`, `u1-say-undecidable` — a finding the round-2 cold reviewer raised on the approved rework and judged non-blocking, promoted because it is this epic's own subject: `_collects_zero` returns `None` for two different reasons ("checked, found real tests" is not one of them, but "could not tell" and "found nothing wrong" shared the identical `None` return and neither `validate()` nor `main()` distinguished them), so an operator running under the wrong interpreter got a clean `OK` with no sign anything went unevaluated.

## Completed slice
Added a second return channel, threaded through every place a caller reads a result:

1. **`_collects_zero`** now returns `(_CollectOutcome, reason)` instead of `bool | None`. The old three-ways-in-one `None` is split into two real states: `NOT_APPLICABLE` (no `-k` selector in this segment — nothing to evaluate, not this fault's concern) and `UNDECIDABLE` (there was something to evaluate and pytest could not be run to find out — no interpreter with pytest importable resolved, or the subprocess itself failed/timed out), each carrying a human-readable reason for the latter.
2. **`_fault_zero_collect`** now returns `(faults, undecidable)` — a segment that reads `UNDECIDABLE` produces an `Undecidable` (new dataclass, same shape as `Fault`: `code`/`where`/`message`), never folded into the fault list and never dropped.
3. **`validate()`** returns a `ValidationResult` — a `list` subclass containing exactly the `Fault`s it always did (every existing caller that iterates/indexes/truthiness-tests it needs no change), plus a `.undecidable: list[Undecidable]` attribute and a `__str__` that names both counts, so `str(result)` cannot read as a clean pass when something went unevaluated.
4. **`main()`** prints the undecidable count and each `Undecidable` right after its existing `OK`/`N fault(s)` line — exit-code semantics are unchanged (undecidable never flips `any_faults`), but the CLI output for a run with zero faults and nonzero undecidables is no longer bare `OK`.
5. Regression coverage: `_collects_zero`'s three-way split (`ZERO`/`NOT_APPLICABLE`/`UNDECIDABLE`) is pinned directly; a new `TestUndecidableChannelIsReportedNotOmitted` class pins `ValidationResult.undecidable`, its `str()` output, `validate_file`'s propagation of the same channel, and the CLI's undecidable line via `capsys`.

## Scope
**Files changed:**
- `scripts/validate_spine.py` (`Undecidable` dataclass, `_CollectOutcome` enum, `_collects_zero`/`_fault_zero_collect` return-shape change, `ValidationResult`, `validate()`/`main()` updated to thread and print it)
- `tests/test_validate_spine.py` (existing `_collects_zero` call sites updated to the new tuple return; new `TestUndecidableChannelIsReportedNotOmitted` class)
- `map/INDEX.md` (rebuilt)

**Specific exclusions touched:** no. `check_corpus_fp.py` was not edited (the handoff notes the Admiral already fixed it a second time, to discover its population by each file's own `type` field rather than a filename substring) — `c3` passes unchanged against it, now examining 26 checklists. `checklist_engine.py`, `mcp_spine_server.py`, `run_crew.py`, `settings.json`, `docs/agents/*`, and every shipped spine template are untouched.

## Behavior changed
Yes, but narrowly: `validate()`/`validate_file()` still return something that behaves exactly like `list[Fault]` for every existing reader, and `main()`'s exit code and `OK`/`N fault(s)` line are unchanged for the common case. The new behavior is additive — a `.undecidable` attribute, an augmented `str()`, and an extra CLI line — visible only when a condition actually could not be evaluated.

## Map Impact
- **Structural anchors touched:** `scripts.validate_spine` (same module, no new public entry points besides `Undecidable`/`ValidationResult`/`_CollectOutcome`; `validate`/`validate_file`/`discover_checklist_templates` keep their names and call signatures).
- **Capabilities added/changed/affected:** a caller of `validate()`/`validate_file()` can now distinguish "sound" from "N conditions could not be judged" without re-deriving it from exit code or fault count; `main()`'s CLI output carries the same distinction.
- **Constraints/assumptions touched:** `_collects_zero`'s return shape changed from `bool | None` to `(_CollectOutcome, str | None)` — any future caller of that private helper (there are none outside this module and its tests) must be updated alongside. `validate()`'s return value is now a `ValidationResult`, not a bare `list`; it remains list-compatible by construction (`list` subclass) specifically so no other reader needed to change.
- **Trust limitations / drift found:** none new.
- **Triage candidates:** none new. The two already carried forward from earlier waves (`init_work_area._RESOLVER_OWNED_TOKEN_RE`'s bare `<skill-dir>` gap; `checklist-engine.md`'s stale Template-set table) are unaffected by this change.

## TDD evidence, if required
- Failing test observed: before the fix, `vs.validate(spine, repo_root=ROOT)` on a spine whose command names an interpreter with no pytest importable had no way to express "undecidable" at all — there was no `.undecidable` attribute to assert against, and `str()` of the plain `list[Fault]` never mentioned it. `main()`'s output for that spine was bare `path: OK`.
- Passing test observed: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE NO_COLOR=1 python -m pytest -q tests/test_validate_spine.py -k "Undecid or Unevaluat"` — 8 collected, all green. `c1`'s library-side probe (a spine whose check names `python3`, which lacks pytest on this host) confirms `validate_file()`'s result mentions "could not" in its own `str()`. `main()`'s CLI output for the same shape now reads `path: OK` followed by `path: 1 undecidable` and the `Undecidable` detail line, with exit code `0`.
- Refactor while green: no separate pass — the `_CollectOutcome` enum and `ValidationResult` class were the direct, minimal shape needed to carry the second channel through every existing call site without breaking any of them; verified by the full suite staying green throughout (`tests/test_validate_spine.py` first, then the repo-wide suite).

## Docs/contracts touched
- none — `map/INDEX.md` is regenerated output, not an authored contract.

## Assumptions
- `check_corpus_fp.py`'s population and scope are the Admiral's own prior decision (fixed a second time per the handoff, now discovered by `type` field); not mine to second-guess further. Ran as given, `c3` exits 0 against 26 checklists.
- "Undecidable" is scoped to the one mechanism the handoff named (`_collects_zero`'s pytest-selector evaluation) — the other three falsifiability faults (`falsifiable-all-null`, `falsifiable-artifact-asserts-property`, `falsifiable-unresolved-placeholder`) are read-only walks over the spine's own JSON with no external process to fail, so they have no undecidable state to report; only fault 2's mechanism spawns a subprocess whose success is not guaranteed.

## Stop conditions hit
- None. The rework's rule (undecidable is not a failing check, exit code does not change) held throughout; no blocker was raised.

## Out-of-scope observations
- None new.

## Workflow Feedback

- **Handoff gaps:** none — `UNDECIDABLE_HANDOFF.md` named the exact mechanism (`_collects_zero`'s four `None`-returning branches), the exact live reproduction (same file, two interpreters, `OK` vs `N fault(s)`), and the exact shape of the fix ("add that channel in both places a caller reads: the library return and the CLI output"), directly actionable without rediscovery.
- **Context rediscovered:** none.
- **Instructions improvised around:** the handoff did not specify whether `NOT_APPLICABLE` (no `-k` selector at all) should also read as undecidable. Judged it should not — reporting "undecidable" for a segment that was never asking the zero-collect question in the first place would itself be a false undecidable, the same class of misleading signal this fix exists to remove. Kept it a silent, unreported third state, distinct from both `Fault` and `Undecidable`.
- **What would have made this easier:** nothing concrete; this handoff was unusually precise.

## Return status
`complete`
