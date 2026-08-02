# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1` — season runner + E-budget/refutil plumbing (#670 season-scale run)

## Result
`APPROVE`

## Handoff compliance
Both close criteria confirmed against source: `run_circuit` gained keyword-only `budget_s`
(default `E_WALLTIME_BUDGET_S`) and `refutil_db` (default `None` → the existing per-circuit
scratch path), both forwarded into its internal `run_stage_e(...)` call. Diff confirms
`run_stage_e` previously received no `budget_s` kwarg at all — the bug the handoff named is
real and is fixed. `scripts/run_season_670.py` implements slate build, per-round DB grid read,
scratch-copy-once, shared-refutil accumulation, the severity-vocabulary guard, and
park-on-missing exactly as specified. `scripts/verify_season_artifacts_670.py` implements the
G2 acceptance check and goes further than asked: it re-verifies a claimed-fresh round against
the actual slice DB rather than trusting `season_results.json`'s word. Required evidence
(pytest + pyright) independently reproduced. Stop conditions were not triggered — none of them
applied.

## Scope drift
None. `git status --porcelain` shows exactly the allowed set: `M src/physics/pilot/pipeline.py`
+ 3 new untracked files. `src/physics/layer2/frozen_constants.py` has an empty diff (untouched);
its only reference inside `pipeline.py` (line 697, inside `run_stage_c`) predates this diff and
is outside the changed hunk. `docs/architecture/*` untouched. The `pipeline.py` diff touches
only `run_circuit`'s signature/docstring and its `run_stage_e` call site — no stage-function
body or gating decider was changed.

## Evidence verdict
Independently re-ran, with the pinned 3.14 interpreter, from the worktree:
- `pytest tests/unit/physics/pilot/test_season_runner.py -q` → **15 passed in 0.79s** (matches claim)
- `pytest tests/unit/physics/pilot -q` → **44 passed in 9.02s** (29 pre-existing + 15 new, zero regressions; matches claim)
- `pyright src/physics/pilot/pipeline.py scripts/run_season_670.py scripts/verify_season_artifacts_670.py tests/unit/physics/pilot/test_season_runner.py` → **0 errors, 0 warnings, 0 informations** (matches claim)

Grepped all 3 new files for `fastf1`/`FastF1`/`requests`/`urllib`/`http(s)://` — zero import or
network-call hits (only doc-comment mentions of the offline guarantee). Traced every DB-open
call site in the new files: `DatabaseManager(db_path=db_path)` inside `read_round_grid` always
receives a caller-supplied path (the scratch copy in `main()`, or a synthetic `tmp_path` DB in
every test — never `src_db`); `sqlite3.connect(...mode=ro)` in `verify_season_artifacts_670.py`
opens the produced slice DB read-only, never the tracked DB. `copy_tracked_db_once` passes the
tracked path only to `shutil.copy` (a read). `test_tracked_db_never_written_only_scratch_copy_is`
independently confirmed via its own monkeypatched-`sqlite3.connect` guard + byte-identical
before/after check. Tests are behavior-real, not vacuous: e.g.
`test_run_circuit_forwards_budget_s_and_refutil_db` asserts both the override case AND the
default-unchanged case by capturing the actual kwargs `run_stage_e` receives;
`test_shared_refutil_db_accumulates_across_rounds_no_drop_or_dup` proves both no-drop (2 rounds
→ 4 observable rows, 2 gp_names) and no-dup (re-running round 1 leaves counts unchanged, proving
`INSERT OR REPLACE` idempotency, not a hand-rolled merge). Vocabulary-guard reality confirmed:
`test_check_round_vocabulary_flags_divergent_k` uses genuinely different `class_ids` (k=2 vs
k=3) and gets a real flip in the flag, not a hardcoded result — not vacuous.

## Code/doc quality
Minimal, matches surrounding conventions (`from __future__ import annotations`,
worktree-first `sys.path` guard mirroring `run_pilot_669.py`, docstrings explaining rationale
for the non-obvious design calls). No module-level mutable state introduced; `DatabaseManager`
constructed fresh per call (per-call DI, not a singleton). `print()` confined to the CLI
`main()`, matching the project rule that library code logs via `logging.getLogger` while
scripts print. No committed report-schema doc needed this gate (`season_results.json` is a
`.agent-work` artifact produced only in G2, not a committed schema).

## Map impact verdict
- **Evidence supports claimed change:** yes — every Map Impact claim was independently checked
  against source/tests, not accepted on the strength of the report.
- **Constraints not violated:** yes — offline-only, no-tracked-db-write, frozen-consumed-not-minted,
  and budget-is-run-param were all independently re-verified, not just re-asserted.
- **Notes match the diff:** yes — the structural/capability/decision notes match exactly what the
  diff and new files contain; no overstatement found.
- **Decision candidates surfaced:** n/a — no decision requiring authority beyond this gate's
  scope arose; the one design nuance (detective vs preventive vocabulary guard) was already
  licensed by the implementer handoff's own alternate phrasing, correctly treated as a documented
  judgment call rather than a silent decision.
- **Durable context routed:** yes, plus one addition from this review — flagged a triage
  candidate (`tc1` in the review survey) that G2/G3 handoffs must explicitly require the
  runbook/report consumer of `season_results.json` to check `vocabulary_divergent` /
  `vocabulary_guard.flagged_rounds`, since the guard is detective (flags after the fact) and a
  human or downstream stage skimming per-round JSON could otherwise miss it.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconciliation. The one real trust
limitation — the vocabulary guard is detective, not preventive, because splitting E out of
`run_circuit`'s single call is explicitly out of this gate's scope — is genuinely recorded (not
silently pooled-and-hidden): `season_results.json` carries `vocabulary_divergent` per round and
`vocabulary_guard.flagged_rounds` at top level; a divergent round stays `status: "covered"`,
flagged, never dropped. This is licensed by the handoff's own escape-hatch wording, not an
unauthorized departure.

## Fowler pass (r6)
Recorded to `.agent-work/670-season-run/g1-review/fowler_pass.json`;
`verify_fowler_pass.py` exits 0. Verdicts: 9 `absent`, 2 `flagged` (non-blocking), 1
`overridden` (logged).
- **flagged — data-clumps:** `circuit`/`round_idx`/`year`/`session_type` travel together across
  `read_round_grid`, `check_round_vocabulary`, `run_season`, `main()`. A small value object
  would reduce repetition. Minor, future cleanup, not this gate.
- **flagged — long-parameter-list:** `run_season()` takes 13 params (1 positional + 12
  keyword-only). Mirrors `run_circuit`'s own pre-existing long keyword-only signature (16 params
  after this diff), so it's internally consistent with the file it extends — still worth a
  future run-context consolidation.
- **overridden — speculative-generality:** `run_circuit_fn`/`grid_reader` injection points look
  like generality but are directly required and exercised by all 15 tests to satisfy this
  gate's own handoff-mandated test mode ("synthetic/monkeypatched `run_circuit`... never spawn
  real E"). Logged standard: `g1-implementer-handoff.md` Test Mode section. Noted nuance:
  `driver_grid_db` is a genuinely-unused knob (never given a distinct value by any test or by
  `main()`) — not severe enough to break the override, but worth trimming later.

## Blockers
- none

## Out-of-scope observations
- G2/G3 must actually consume `vocabulary_divergent`/`vocabulary_guard.flagged_rounds` from
  `season_results.json`, not just leave it sitting in the JSON — flagged as triage candidate
  `tc1` in the review survey (`.agent-work/670-season-run/g1-review/review.json`).
- `data-clumps` and `long-parameter-list` Fowler observations above (non-blocking, future cleanup).
- `driver_grid_db` in `run_season()` is an unexercised injection point — minor, not blocking.

## Workflow Feedback

- **Handoff gaps:** none blocking. The reviewer handoff correctly pre-empted the one likely
  point of confusion (detective-vs-preventive vocabulary guard) by explicitly stating it's
  ACCEPTABLE given the scope exclusion — that saved a round of second-guessing.
- **Context rediscovered:** none — `docs/agents/CREW_CONTEXT.md`/`GLOSSARY.md` were current and
  sufficient; no stale anchor encountered (the implementer's note that `src/data/database.py` is
  now a package was independently visible from the working import path and didn't block review).
- **Instructions improvised around:** none — the survey/Fowler-pass flow in the skill matched the
  work cleanly; no template or engine instruction failed to cover this gate's shape.
- **What would have made this easier:** none — the handoff's explicit close-criteria list mapped
  cleanly onto verifiable, independently-reproducible checks (diff inspection, grep, pytest,
  pyright); this was one of the more frictionless reviews.

## Return status
`complete`
