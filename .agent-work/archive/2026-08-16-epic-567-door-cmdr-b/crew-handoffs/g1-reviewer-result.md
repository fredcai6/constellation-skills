# Review Result

## Assigned Gate
`g1-review` — ExternalBackend default-refuse fix for #432 (epic #567 lane B)

## Result
`APPROVE`

## Handoff compliance
All close criteria met, verified against the diff and independently reproduced (not just
trusted from the pasted transcript):

- `ExternalBackend.dispatch()` accepts `--spine`, recorded on the entry, never bound
  (`scripts/run_crew.py` L1671-1706; `test_external_dispatch_refuses_spine`, re-run passing).
- `ExternalBackend.verify()` default-refuses when neither spine evidence nor
  `--accept-mtime-only-risk` is given — the rewritten
  `test_verify_result_absent_then_present_marks_completed` genuinely asserts
  `code_present == 1` where it previously asserted `0`; re-ran it myself: passes.
  Independently reproduced end to end in a fresh, non-pytest process: dispatched external
  with no `--spine`, wrote a fresh result artifact, `--verify-result` with no override →
  exit 1, `REFUSED: no spine evidence and no --accept-mtime-only-risk given ... see #432`.
- AND semantics confirmed both via `test_verify_named_spine_not_terminal_refuses` (re-run,
  passing) and my own separate fresh-process repro: dispatched with `--spine` naming a
  non-terminal (`pending`) gated fixture, wrote a fresh result artifact, `--verify-result`
  still refused (`REFUSED: spine ... never reached a terminal state`) despite the fresh
  result — a fresh result never rescues an undriven spine.
- `--verify-spine` (verify-time) is consulted independently of dispatch-time `--spine` and
  wins when both are given — `effective_spine = verify_spine if verify_spine is not None
  else spine` (L1800); `test_verify_time_spine_override_completes` re-run, passing.
- `--accept-mtime-only-risk` is loud: reproduced in my own fresh-process run — the
  `RISK ACCEPTED: ... see #432` line appears in BOTH captured stdout and stderr, and is
  recorded on the entry as `mtime_only_risk_accepted: {"reason": ..., "at": ...}`
  (L1806-1809).
- No crash on `result=None` + `spine=<path>`: `result_exists`/`result_fresh` are called only
  inside `if has_result:`, itself derived from `entry.get("result") is not None` (L1792-1795)
  — never with `result=None`. `test_verify_spine_only_external_dispatch_no_crash` re-run,
  passing.
- `.get(...)` used throughout the new code for `entry["spine"]`/`entry["result"]` — no bare
  bracket access on a possibly-absent key anywhere in the diff.
- `CliBackend`'s behavior is byte-for-byte untouched: grep confirms exactly one production
  call site of `.verify()` in the whole file (inside `verify_external_result`, calling
  `ExternalBackend().verify(...)`); `CliBackend` uses `finalize_from_exit_code` instead, and
  `CrewBackend.verify` (the shared base, L1475) has zero diff hunks inside its body —
  `ExternalBackend.verify()` is a genuine override, not a base-class edit.
- No edit inside `scripts/checklist_engine.py` or `scripts/mcp_spine_server.py` — absent from
  `git diff --name-only`; `spine_terminal` is called, never redefined, in the diff.
- Full suite: independently re-ran `pytest tests/test_crew_launcher.py -q` myself — **217
  passed**, matching both the implementer's and the Commander's claimed count exactly.

## Scope drift
None. `git status --porcelain` shows only `scripts/run_crew.py` and
`tests/test_crew_launcher.py` modified — exactly the Allowed Scope. The two Specific
Exclusions (`checklist_engine.py`, `mcp_spine_server.py`) are untouched. Untracked
`.agent-work/567-b/triage-candidates/*` and `.agent-work/epic-567-door/*` are workflow/triage
artifacts, not code scope creep.

## Evidence verdict
Required evidence present and independently reproduced, not merely trusted:
- Full suite (217 passed) — re-run myself, matches.
- The five most load-bearing individual tests (the four named intentional rewrites plus
  `test_verify_named_spine_not_terminal_refuses`) — re-run myself in isolation, all pass.
- Two fresh-process (non-pytest) CLI demonstrations of my own, driving `scripts/run_crew.py`
  directly against a scratch `--root`: (1) the #432 default-refuse → explicit-override
  scenario, and (2) the AND-semantics scenario (fresh result next to a non-terminal spine
  still refuses). Both reproduced cleanly, matching the claimed behavior exactly.
- Verified all four "intentional test-scenario rewrite" claims against the actual test diff
  line by line: each OLD scenario genuinely is what #432 asks this lane to forbid or narrow
  — none is a cover for an unrelated behavior change:
  1. `test_external_dispatch_refuses_spine` — was refuse, now accept-and-record. Matches
     change 1 of the handoff.
  2. `test_verify_result_absent_then_present_marks_completed` — was `code_present == 0`, now
     `== 1`. This is the #432 core fix, confirmed as the single most load-bearing change.
  3. `test_verify_is_uniform_across_backends` — was "both backends verify identically", now
     "CliBackend unchanged, ExternalBackend default-refuses, old behavior reachable via
     override". Matches the intentional, evidence-backed narrowing of Decision 2 for
     `ExternalBackend` only.
  4. `BackendInvariantContractTests.test_both_backends_verify_exists_and_fresh_identically`
     — steps (a)/(b) (missing/stale) stay shared and unchanged; only step (c) (fresh) splits
     per backend. Matches #3's reasoning exactly.
  No other test's scenario changed (confirmed: the two pre-existing STALE/absent tests are
  absent from the test diff — untouched).

## Code/doc quality
Minimal, maintainable, and matches surrounding conventions. `ExternalBackend.verify()`
(~48 code lines, one clean 3-way branch) matches the size and shape of the file's existing
`finalize_from_exit_code` precedent for backend-verdict computation — not disproportionate.
See the Fowler pass below for the two judgment calls raised (one non-blocking observation,
one logged override).

### Refactoring pass (Fowler code smells)
Recorded to `.agent-work/epic-567-door/cmdr-b/FOWLER_PASS.json`;
`scripts/verify_fowler_pass.py` exits 0 (`smells=12, flagged=['long-method'],
overridden=['comments-as-deodorant']`). All 12 baseline smells visited, none silently
skipped.
- **long-method** — `flagged` (observation, non-blocking): `main()`'s `--verify-result`
  branch grows by ~30 lines of nested message-priority logic on top of an already ~178-line
  dispatcher. Follows the exact inline-if-print-return style already used by the adjacent
  pre-existing STALE/absent branches in the same function, so it is consistent with the
  surrounding code, not a regression. A future pass could extract a
  `_verify_result_refusal_message(entry, args)` helper; out of this gate's Allowed Scope.
- **comments-as-deodorant** — `overridden`: the dense docstring on `ExternalBackend.verify()`
  and the inline rationale comments in `dispatch()`/`main()` are subordinate to the repo's
  own decision-fixedness doctrine (`@grade: guess` decisions in MISSION_FRAME.md's Decision
  Anchors require their rationale captured until settled) and `CREW_CONTEXT.md`'s
  Verification Discipline section (verification-design choices must be justified, not just
  asserted). The code itself is not confusing or masked by the comments — short branches,
  self-describing names (`effective_spine`, `has_result`, `result_ok`, `spine_verified`).
- All other 10 baseline smells (large-class, duplicated-code, feature-envy, data-clumps,
  primitive-obsession, long-parameter-list, shotgun-surgery, divergent-change,
  message-chains, speculative-generality) — `absent`.

## Map impact verdict
- **Evidence supports claimed change:** yes — see Evidence verdict above.
- **Constraints not violated:** yes — AND semantics, override-not-base-class-edit, and
  `.get()`-not-bracket were each independently re-verified against the diff (see per-check
  findings in the driven survey, items r4a/r4b/r4c).
- **Notes match the diff:** yes — the implementer's structural anchors, capability changes,
  and constraint narrowing all match what the diff actually touches; no missing or
  overstated impact found.
- **Decision candidates surfaced:** yes — MISSION_FRAME.md's decision-pressure item (whether
  `--spine` should become mandatory at dispatch in a future wave) is correctly left
  unresolved and floated to the Admiral, not decided in this lane.
- **Durable context routed:** yes — `docs/superpowers/specs/2026-07-07-crew-backend-design.md`
  Decision 2's now-stale "never forked" prose is correctly routed as a triage candidate
  (`.agent-work/567-b/triage-candidates/tc1-crew-backend-design-doc-drift.md`), confirmed
  by me as accurate (the doc file itself is unedited by this diff and still reads "never
  forked" at L35), not silently fixed or dropped.

## Reconciliation check
No `docs/architecture` map exists in this repo (confirmed: no such directory present), so
there is nothing to reconcile against structurally. The one real reconciliation item — the
crew-backend-design spec's Decision 2 prose going stale — is already correctly routed as a
triage candidate (see above), not a blocker for this gate.

## Blockers
- none

## Out-of-scope observations
- `docs/superpowers/specs/2026-07-07-crew-backend-design.md` Decision 2 needs a prose update
  recording the `ExternalBackend`-only narrowing (already flagged as a triage candidate by
  the implementer, confirmed by me — see Map impact verdict).
- `main()`'s Fowler long-method observation above (non-blocking, future refactor candidate).

## Workflow Feedback
- **Handoff gaps:** none — the handoff's Close Criteria and Stop Conditions translated
  directly into checkable items; no field was missing or ambiguous.
- **Context rediscovered:** none — the Map Anchors list (structural anchors, decision
  anchors, evidence expectations) pointed directly at everything needed; no extra digging
  was required beyond reading the named files.
- **Instructions improvised around:** the `constellation-reviewer` skill's r4-quality item
  says "Append a check per rule" without naming how many rules to expect; I read the
  handoff's three-item "Constraints the Implementation Must Respect" list as the rule set
  and appended one sibling check per constraint (`r4a-and-semantics`, `r4b-override-not-base`,
  `r4c-get-not-bracket`). This worked cleanly through the engine's `append` verb but is worth
  naming explicitly since a different reviewer might append a different granularity (e.g. one
  check per Close Criterion instead of per Constraint).
- **What would have made this easier:** none — the handoff's evidence section and the
  implementer's six-section evidence writeup were unusually easy to independently reproduce
  against; both the pytest re-run and the two fresh-process CLI demonstrations matched on the
  first try with no adjustment needed.

## Return status
`complete`
