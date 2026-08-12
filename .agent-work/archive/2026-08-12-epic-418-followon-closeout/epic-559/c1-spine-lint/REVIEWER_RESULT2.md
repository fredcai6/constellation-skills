# Review Result

## Assigned Gate
`epic-559/c1-spine-lint` / `g6-review2` (reviewer, cold, round 2 -- z1-z4 rework of round 1's `v1` blocker)

## Result
`APPROVE`

## Handoff compliance
Met. `8708493b` implements exactly what `REWORK_HANDOFF.md` asked for: (1) exclude shell-redirect-shaped tokens from `_pytest_targets` (`_REDIRECT_TOKEN_RE`/`_REDIRECT_OPERATOR_ONLY_RE`), fixing the idiom-folding bug; (2) `_resolve_interpreter` resolves the interpreter the check's own command text names and confirms pytest is importable there before ever trusting an empty collection as a real zero, returning `None` (undecidable, not a fault) when it cannot -- matching the handoff's explicit "an undecidable check is not a failing check" instruction. `96fb9412` records the z3/z4 rework outcome. Both Admiral scripts (`check_idiom.py`, `check_corpus_fp.py`) were left unedited per the handoff.

## Scope drift
None. `git diff --stat 3c0fc7d2..HEAD` confirms zero touch to `checklist_engine.py`, `mcp_spine_server.py`, `run_crew.py`, `settings.json`, `docs/agents/*`, and every `skills/*/templates/*.json` spine template. `check_idiom.py`/`check_corpus_fp.py` appear only as new additions (Admiral-authored files tracked into the repo in `96fb9412`, never crew-edited). Branch is local-only, ahead of `main@3c0fc7d2` -- no push to main.

## Evidence verdict
Independently reproduced every headline claim in `IMPLEMENTER_RESULT.md`: full suite `2652 passed, 1 skipped, 1121 subtests passed in 106.13s` (exact match); `check_idiom.py` exits 0; `check_corpus_fp.py` prints "examined 14 spine files" and exits 0 (exact match); `tests/test_validate_spine.py` 76 passed, and the two new `-k` slices (`"Idiom or Redirect"` -> 11 passed, `"Interpreter or Unavailable"` -> 4 passed) both green. Confirmed the host fact the whole rework rests on: `python` has pytest 9.1.1, `python3` does not.

## Code/doc quality
New tests assert against behavior (`vs._pytest_targets`/`_resolve_interpreter`/`_collects_zero`/`validate()` directly, never message strings) with adversarial fixtures (fake interpreter scripts, a genuinely-zero selector as a control wrapped in the same idiom, parametrized redirect-token shapes) -- meets `CREW_CONTEXT.md`'s Verification Discipline. Minimal, narrowly-scoped diff; no speculative abstraction. Fresh Fowler pass (`FOWLER_PASS.json`, re-run against this round's diff, `scripts/verify_fowler_pass.py` exits 0): one non-blocking observation (`duplicated-code` -- `_REDIRECT_TOKEN_RE`/`_REDIRECT_OPERATOR_ONLY_RE` repeat the same core pattern), all other eleven baseline smells absent; round 1's still-open, diff-untouched findings (`_shape_faults` long-method, the `_RESOLVER_OWNED_TOKEN_RE` import override) carried forward, not re-litigated.

## Map impact verdict
- **Evidence supports claimed change:** yes -- `python scripts/build_architecture_map.py ... --check` reports inputs valid.
- **Constraints not violated:** yes -- public `validate`/`validate_file`/`discover_checklist_templates` API unchanged; only private helpers added.
- **Notes match the diff:** yes.
- **Decision candidates surfaced:** n/a, none required.
- **Durable context routed:** yes -- `check_corpus_fp.py`'s under-scoping (below) flagged as triage candidate `tc1`.

## Reconciliation check
No undisclosed architectural divergence. Architecture-map check passes.

## Blockers
None. See "Out-of-scope observations" for two real findings that were weighed and judged non-blocking, with reasoning.

## Out-of-scope observations

- **The decisive item (w1) is clean.** Independently re-swept 553 gated-or-survey files (541 under `.agent-work/` by each file's own `type` field + 12 shipped templates, within 1 of the crew's 552 -- natural drift). Fault-1/3/4 counts are EXACT matches to the crew's resweep table (637 / 128 (3 distinct texts) / 45 (5 distinct texts) -- zero regression into the three previously-clean families from the shared-tokenization fix. Fault-2 at exactly the claimed 1 hit, 0 false positives. Zero new false positives anywhere.

- **w4, the surviving true positive, verified end to end.** Commit `75ee317a` added `test_a_live_spine_in_this_work_area_also_projects`; commit `0b15d5b8` deleted it outright (not literally "renamed," a minor wording correction -- same practical effect: the selector's target no longer exists, confirmed by the removed comment explaining the deletion as redundant coverage). `grep -n live_spine tests/test_context_manifest.py` today: zero matches. `pytest tests/test_context_manifest.py -q -k 'live_spine' --collect-only` today: "no tests collected (65 deselected)." Real, verified true positive.

- **w2/w3 -- a real, narrow false-negative gap, and a real reporting gap, judged non-blocking.** `_resolve_interpreter(None)` (the bare-`pytest`, no-`-m` case) still falls back to `sys.executable` -- exactly the fallback z2 was meant to eliminate, just for a shape (bare `pytest`) that names no interpreter in its own command text, so it fell outside REWORK_HANDOFF.md's "invoke the interpreter the command itself names" directive. Reproduced live: a spine whose only check is `pytest -q <fixture> -k this_matches_nothing_zzz` (genuinely zero-collect) reads `1 fault(s)` under `python -m scripts.validate_spine` and `OK` under `python3 -m scripts.validate_spine` -- on this exact host, using the exact documented hazard (`CREW_CONTEXT.md`) that motivated this whole rework. This directly falsifies `IMPLEMENTER_RESULT.md`'s claim that output no longer depends on which python ran the checker "regardless of which python on the host ran the checker itself" -- true only for `-m pytest`-shaped checks. Traced every return path in `_collects_zero`/`_fault_zero_collect`/`validate()`: there is no channel anywhere (return value or CLI output) that distinguishes "checked, found nothing wrong" from "could not tell" -- both read as a clean pass. Judged non-blocking because: (a) not a new false positive, the handoff's sole named auto-BLOCK trigger; (b) not a regression -- before this rework the same shape was broken in the more dangerous direction (false positive); (c) rare in the real corpus, 2 of ~592 pytest-invoking checks, both in dead archive files, not this epic's live spines or shipped templates; (d) genuinely outside the two mechanisms REWORK_HANDOFF.md scoped this rework to. **Recommend:** correct `IMPLEMENTER_RESULT.md`'s interpreter-independence claim to name the `-m pytest`-only scope, and open a follow-up to resolve bare `pytest` via `shutil.which("pytest")` rather than `sys.executable`.

- **w5 -- `check_corpus_fp.py` is measurably too narrow, flagged `tc1`.** `check_idiom.py` is fair and precise (verified live, exit 0). `check_corpus_fp.py`'s filename-substring population filter (`"PLAN"`/`"SPINE"` in name) undercounts its own claimed scope by 11 of 25 real files (44%) in the same two roots it already covers -- repeating the exact hand-maintained-filter anti-pattern the crew's own z3 resweep explicitly rejected in `IMPLEMENTER_RESULT.md`'s Assumptions section. The 11 omitted files include both prior REVIEW_SURVEY.json files and five `epic-418-followon` review spines. None currently carries a zero-collect fault (checked), so today's exit code is right by luck, not by design -- a future regression in any of those 11 files would go undetected while the check keeps printing a clean pass. Not the crew's to fix (Admiral-authored, explicitly out of the crew's editing latitude); routed to Triage as `tc1` for the same type-field rescoping already applied to the real z3 resweep.

## Workflow Feedback

- **Handoff gaps:** one real one. `REVIEW_HANDOFF2.md` line 6 says "Write your Fowler record to `.agent-work/epic-559/c1-spine-lint/FOWLER_PASS2.json`" -- but `REVIEW_SURVEY2.json`'s own `r6-fowler` postcondition hard-codes `python scripts/verify_fowler_pass.py .agent-work/epic-559/c1-spine-lint/FOWLER_PASS.json` (no "2"), and its imperative text explicitly forecloses treating that path as a fillable placeholder ("no separate placeholder to fill and no way to leave it stale"). I followed the engine's binding postcondition (`FOWLER_PASS.json`, overwriting round 1's record with a fresh pass against this round's diff) rather than the handoff prose, per "engine output is the state channel" / "current... not a licence to read around it" doctrine -- the mechanically-enforced path wins over a conflicting sentence in free text. Did not also write a `FOWLER_PASS2.json` nobody checks (one canonical path, no speculative duplication). Naming this explicitly since I almost missed it -- the two disagreed and only one is load-bearing.
- **Context rediscovered:** the two Admiral check scripts' exact scope history (why `check_corpus_fp.py` was rescoped once already) had to be reconstructed from `IMPLEMENTER_RESULT.md`'s "Stop conditions hit" section plus reading the script's own inline comment -- both were internally consistent and cross-checked cleanly, so this was confirmation work, not a gap.
- **Instructions improvised around:** none -- every item's imperative was directly actionable as written, including w2's "build real zero-collect defects in several shapes," which I read as license to construct my own fixture spines (7 shapes, `/tmp/w2_shapes.py`) rather than being handed a fixed list.
- **What would have made this easier:** nothing concrete. The handoff's explicit distinction between w1 (the one item carrying a binary "is a BLOCK" clause) and w2/w3/w4/w5 (each phrased as "say/judge/report") was load-bearing for how I weighed three real findings without mechanically blocking on each -- worth preserving as a pattern in future rework-review handoffs of this shape.

## Return status
`complete`
