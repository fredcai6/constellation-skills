# Review Result

## Assigned Gate
`epic-559/c1-spine-lint` / `g5-review` (reviewer)

## Result
`BLOCK`

## Handoff compliance
Met. `scripts/validate_spine.py` (484 lines) is an importable `validate(spine) -> list[Fault]` checker plus a thin CLI, covering the named shape faults and the four #518/#562 falsifiability faults. `tests/test_validate_spine.py` (539 lines) + `tests/fixtures/spine_lint/fixture_tests.py` match the commit's claimed line counts exactly. Full suite reproduced: 2638 passed, 1 skipped, 1121 subtests in 106s, matching IMPLEMENTER_RESULT.md verbatim. `IMPLEMENTER_RESULT.md` is present and detailed, including an honest triage-candidate list.

## Scope drift
None. All named no-gos (`checklist_engine.py`, `mcp_spine_server.py`, `run_crew.py`, `skills/implementer/*`, `skills/reviewer/SKILL.md`, `settings.json`, `docs/agents/*`, every shipped spine template) are untouched — confirmed by empty `git diff main...HEAD --stat` for each. `origin/main` sits at `90b39e2b`, exactly the handoff's cited base — no push to main. The one process deviation (an unquoted two-word `-k` selector in the g2-falsifiable gate's own frozen postcondition) was corrected through the sanctioned `spine_amend`/`retext-check` path, not a hand-edit — verified live in `.agent-work/epic-559/c1-spine-lint/mcp_amend_delta_20260811T103802357365.json` and the plan's journal.

## Evidence verdict
Satisfies the required evidence. Reproduced both headline claims personally: the full suite command from the handoff's Test mode section, and `python -m scripts.validate_spine --sweep` (12 templates, 4 clean, 21 all-null + 2 unresolved-placeholder = 23 faults, matching the result doc exactly). TDD evidence in IMPLEMENTER_RESULT.md is plausible and internally consistent (pre-code selectors genuinely collect zero in this epic's own archived `IMPLEMENTER_PLAN.json`, confirming the claimed red state actually happened). Minor staleness only: the doc's "61 passed" for `tests/test_validate_spine.py` alone is 62 on a fresh run — one test added after that snapshot, not a functional gap.

## Code/doc quality
Minimal, tested, and mostly project-rule compliant. Ran the full Fowler baseline catalog (`.agent-work/epic-559/c1-spine-lint/FOWLER_PASS.json`, `scripts/verify_fowler_pass.py` exits 0): `long-method` flagged as an observation (`_shape_faults`, 58 lines, five bundled validation concerns — not blocking); `feature-envy` overridden (imports `init_work_area`'s private `_RESOLVER_OWNED_TOKEN_RE` rather than re-declaring it, justified by CREW_CONTEXT.md's "define a guard by the consumer's own computed property" rule and precedented by `scripts/run_skill_eval.py:73-74`'s identical pattern); all ten other smells absent. Naming: the repo's `scripts/` has an established `verify_*.py` convention (20 scripts); this module is `validate_spine.py` — a reasonable departure given its richer importable API, but worth naming.

## Map impact verdict
- **Evidence supports claimed change:** yes — `map/INDEX.md`'s diff (scripts 55→56, tests 71→73) matches the new leaf modules exactly; no existing structural anchor's shape changed.
- **Constraints not violated:** yes — the one constraint named (`init_work_area._RESOLVER_OWNED_TOKEN_RE` as source of truth) is honored by import, with the one disclosed exception (`_BARE_RESOLVER_TOKENS`) explicitly logged as a triage candidate rather than silently absorbed.
- **Notes match the diff:** yes.
- **Decision candidates surfaced:** yes — the `<skill-dir>` resolver gap was surfaced rather than silently fixed out-of-scope.
- **Durable context routed:** yes — two triage candidates already logged by the implementer (resolver gap; checklist-engine.md's stale table), plus one more from this review (below).

## Reconciliation check
No undisclosed architectural divergence. `python scripts/build_architecture_map.py --root . --source-root scripts --source-root tests --source-root skills --source-root evals --check` reports inputs valid.

## Blockers
- **v1 — false positives in fault 2 (zero-collect), BLOCK.** Swept every gated/survey instance under `.agent-work/` (539 files) plus the 12 shipped templates, using the correct `python` interpreter. Faults 1, 3, and 4 held up under hand inspection of every distinct trigger — zero false positives found in any of them (fault 3: only 3 distinct statement texts across 128 hits, all 3 hand-verified genuine #562-shaped defects; fault 4: every distinct placeholder token confirmed genuinely unresolved). Fault 2 did not hold up: **8 of the 9 zero-collect findings in the correctly-run archive sweep are false positives**, all from the same mechanism. `_pytest_segments` splits a command on bare `|`, so the corpus's own recommended self-checking idiom — `test $(pytest ... --collect-only 2>/dev/null | grep -c '::') -ge N && pytest ...`, the exact pattern CREW_CONTEXT.md's Verification Discipline asks authors to write ("demonstrate it can reach a failing state") — puts `2>/dev/null` inside the first segment. `shlex` tokenizes `2>/dev/null` as one opaque non-flag token, so `_pytest_targets` folds it in as a bogus positional pytest target (a nonexistent path). `_collects_zero` then runs pytest against that bogus path, gets an empty/errored result, and misreports "collects zero." `_fault_zero_collect` dedupes by selector text in command order, so this corrupted first-segment verdict wins before the correct second (real-run) segment is ever reached.

  **Minimal reproduction:** a check running 32 real, passing tests (`pytest tests/test_validate_spine.py -k Shape`), wrapped in the idiom above, is flagged `falsifiable-zero-collected` — the same severity as `check: null` — for a check that not only can fail, but demonstrably passes:
  ```
  command = "test $(python -m pytest -q tests/test_validate_spine.py -k Shape --collect-only 2>/dev/null | grep -c '::') -ge 6 && python -m pytest -q tests/test_validate_spine.py -k Shape"
  validate(spine)  # -> [falsifiable-zero-collected] ... 'Shape' ... collects zero tests
  # but: bash -c command  ->  32 passed, 30 deselected, returncode 0
  ```
  This is not a corner case: it fires on this very epic's own `g1-shape`/`g2-falsifiable`/`g3-corpus` gates and on 3 other real spines (`epic-559/a-spine-is-the-job`'s REWORK/REWORK2 plans) every time the idiom is used, and would fire on any future spine that follows the repo's own documented best practice for exactly this fault family. It penalizes the most diligent authors and rewards the naive one-liner that skips the self-check — precisely the "refuses spines that are fine" outcome the handoff names as decisive.

  **Second, related mechanism** (found investigating the first): `_collects_zero` uses `sys.executable` for its own subprocess pytest re-invocation, discarding whatever interpreter the check's own command text names, and never confirms pytest is importable there before trusting an empty/failed subprocess as "collects zero." This host has `python3` with no pytest installed — a hazard `docs/agents/CREW_CONTEXT.md` documents explicitly. Reproduced through the real CLI: `python3 -m scripts.validate_spine .agent-work/w5-gates/execute.json` → 6 spurious zero-collect faults; `python -m scripts.validate_spine` on the identical file → 0. Nothing distinguishes "pytest didn't run" from "genuinely 0 collected," so an operator typing the more literal-looking `python3` silently gets false BLOCKs on every pytest-based check in the file.

  Both mechanisms are narrow and fixable (skip shell-redirect-shaped tokens in `_pytest_targets`; verify pytest importability, or invoke the command's own interpreter, before trusting an empty collect result) but as shipped, fault 2 is not safe to trust against the corpus's own recommended self-checking idiom.

## Out-of-scope observations
- `_shape_faults` (58 lines) bundles five validation concerns; a candidate for splitting into named helpers the way `_shape_task_faults` already was (Fowler pass, `long-method`, non-blocking).
- No fault family exists for a command check that can never PASS (opposite direction from the four shipped faults) — confirmed live against a `python -c "import mcp_spine_server"` check (reads `SPINE_FILE`/`SPINE_ENGINE` at import). A defensible scope exclusion for this gate (general detection is undecidable; the sound fix is a narrowly-scoped future fault, not a live-execution sweep of arbitrary commands) — flagged as triage candidate `tc1`.
- Naming: `validate_spine.py` departs from the repo's `verify_*.py` convention (20 existing scripts) — reasonable given its richer API, but worth a Commander/Charter call on whether to rename before the corpus grows around this name.
- Already-logged by the implementer, confirmed live and not re-litigated here: `init_work_area._RESOLVER_OWNED_TOKEN_RE`'s bare `<skill-dir>` gap; `checklist-engine.md`'s stale Template-set table (independently re-confirmed in v5: 6 rows, 5 real, vs. a measured 12).

## Workflow Feedback

- **Handoff gaps:** none in the handoff's wording. One near-self-inflicted gap worth naming for the next reviewer: the handoff doesn't warn that `_collects_zero` uses `sys.executable`, so a reviewer sweeping the archive with the wrong interpreter (I first used `python3`, which lacks pytest on this host) gets a wildly inflated, wrong false-positive count (175 zero-collect hits, not the real 9) with no error signal. I caught it only because the fault count looked implausibly high and I went hunting for why. A one-line addition to this gate's own Test mode note ("also true for validate_spine.py's own subprocess re-invocation") would have saved the detour — though finding it here, live, ended up being the review's central discovery.
- **Context rediscovered:** none beyond the above — the handoff's four fault descriptions and the `g1-review.c1`/`g1-integrate.c2` worked example were directly usable.
- **Instructions improvised around:** none — every survey item's imperative was directly actionable, including the unusual real postcondition on `r6-fowler` (record path resolved from the work-id substitution already established elsewhere in the survey).
- **What would have made this easier:** naming, in the handoff or the module's own docstring, which interpreter `_collects_zero` trusts (`sys.executable`, not the command's own named interpreter) — this is exactly the kind of fact a cold reviewer has to rediscover the hard way, and it is also the root of a real defect (the second mechanism under Blockers), not just a documentation gap.

## Return status
`complete`
