# Review Result

## Assigned Gate
g1 (g1-review) — report-only `basis` sibling field on `Condition`

## Result
`APPROVE`

## Handoff compliance
Full match. `basis` (locator_kind: `file`/`evidence_ref`/`abstain`) added as an optional sibling of `check` on `Condition`; `render_human` emits an indented `basis:` line under an open condition only when populated and non-abstain (verified by reading `_render_basis_line` and its call site, plus `test_abstain_basis_behaves_like_no_basis`); `attest()` resolves the locator for a populated non-abstain `basis` on a `check: null` condition and **always** attaches a `basis-check` evidence item, pass or fail, then falls through unconditionally to the pre-existing accept path — never raises. Only `file`/`evidence_ref` are implemented as dispatch branches. No shipped template carries `basis`, so no observable behavior change today (`GoldenOutputBriefing`/`TemplateOnlyFieldAllowlist`, 10/10, reproduced).

## Scope drift
None. `git diff --name-only` shows exactly the three allowed files (`scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`, `tests/test_checklist_engine.py`). Grepped the diff hunks for `waive`/`trip_ledger`/`override_reason`/forced-claim patterns — zero hits; the w2-ledger lane fence is untouched. No touch to `COMMANDER_SPINE.template.json`, `generate_spine.py`, or `specs/`.

## Evidence verdict
Independently reproduced, not taken on faith:
- Full suite: `511 passed, 145 subtests passed` on this host, matching the claim exactly.
- TDD red-proof re-derived myself: stashed `scripts/checklist_engine.py` + `docs/CHECKLIST_SCHEMA.md` (kept the new test file), reran `-k Basis` — 12 tests failed with the same failure shapes the IMPLEMENTER_RESULT quotes (`KeyError: 'basis'`, etc.); restored, reran full suite green again, dropped the temp stash.
- Wiring grep for `_resolve_basis_locator`/`basis-check` reproduced exactly: 1 production call site (inside `attest()`), 1 direct test call, rest are tests/docstrings.
- `evidence_ref` purity is asserted by `mock.patch`-ing `subprocess.run` to raise if touched (`test_resolve_basis_locator_is_pure_for_evidence_ref`) — passes.
- `base_dir` wiring is tested end-to-end through the real CLI dispatch path (`test_attest_wires_base_dir_from_cli_dispatch_to_checklist_directory`), not just in-process.
- Byte-identical legacy behavior for absent/abstain `basis` is directly asserted (`test_no_basis_attest_is_byte_identical_to_legacy`, `test_abstain_basis_behaves_like_no_basis`) — both pass, `evidence == []`.

## Code/doc quality
Fowler baseline pass run against all 12 smells (`.agent-work/w2-basis/FOWLER_PASS.json`, `verify_fowler_pass.py` exit 0): 11 absent, 1 overridden (`primitive-obsession` — `locator_kind` is a bare dispatched string rather than a typed enum, but every domain object in this file, including the pre-existing `check['kind']` dispatch, is a plain dict with string-keyed dispatch; introducing a typed value object for `basis` alone would break that established, load-bearing convention for no behavioral gain). No flagged smells. `attest()`'s param count (7) matches its sibling `waive()` (also 7) — not an outlier. The one-line `root = base_dir or Path.cwd()` idiom is reused from `_collect_changed_files`, not duplicated logic. `glob`/`min_matches` support (which could otherwise read as speculative) is directly required by the g1-implementer-handoff for g2's future `plan.c4` basis authoring — verified against `PLAN_ALTERNATIVES.md:56`.

## Map impact verdict
- **Evidence supports claimed change:** yes — every structural anchor the implementer named (`_condition_view`, `render_human`, `attest`, `_run_verb`) matches an actual diff hunk at the stated location.
- **Constraints not violated:** yes — INV-2 purity confirmed by grep (`_resolve_basis_locator` has exactly one production call site, inside `attest()`; render path never calls it); `ruling-widening-live-refusal-report-only` confirmed by code read (no branch on `problem` gates the accept) and by test; `ruling-decorative-basis-is-a-failure` honored (authored + rendered + resolved-and-recorded together).
- **Notes match the diff:** yes, no over- or under-statement.
- **Decision candidates surfaced:** none needed — locator-kind vocabulary was already ratified in `PLAN_ALTERNATIVES.md`, correctly not re-litigated.
- **Durable context routed:** n/a — additive, local change confined to one engine file plus its schema doc; no new module/seam, so no Cartographer reconciliation is owed.

## Reconciliation check
None needed. Local, additive change (one new function, one new render helper, a guard inside an existing function) with no new module/seam/adapter.

## Blockers
- none

## Out-of-scope observations
- none

## Workflow Feedback
- **Handoff gaps:** none — line-number anchors were close enough (per the implementer's own note) to locate the diff immediately; every close criterion in the handoff was independently checkable against the actual code.
- **Context rediscovered:** `SPINE_FILE`/`SPINE_SESSION` in this crew's environment resolve to the **Commander's** `execute.json` (`crew-runs.json` confirms `spine: null` for this crew's own entry), matching the implementer's own note and the known `crew-dispatch-spine-null` pattern. `spine_status` shows the Commander's `execute` gate, not a reviewer plan — per doctrine this crew never touched that spine (no `attest`/`advance`/`current`-driven mutation against `execute.json`), and instead authored and drove its own `REVIEW_SURVEY.json` at `.agent-work/w2-basis/g1-review/review.json` through `checklist_engine.py`'s CLI directly (`claim`/`start`/`record`/`consolidate`/`release`, under session id `constellation/w2-basis/g1/reviewer/attempt-1`). The SessionStart system-reminder repeatedly instructing "drive execute.json gate by gate" is addressed to the Commander session, not this reviewer crew; deliberately not acted on.
- **Instructions improvised around:** the CLI's `record`/`start`/`claim` subcommands require `--session-id` positioned after the verb's own positional args (not before), which the skill doctrine doesn't spell out — one-time lookup via `--help`, not a real gap.
- **What would have made this easier:** nothing concrete — handoff was precise and the implementer's own evidence (transcripts, wiring grep, diff-stat) was itself accurate enough to re-derive quickly.

## Return status
complete
