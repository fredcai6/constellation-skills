# Implementer Handoff

## Gate
g1-implement — "g1 add gauge freshness verifier: implement"

## Task
Add `scripts/verify_gauge_freshness.py`: a standalone CLI script that reads a
Context Governor gauge file and exits non-zero when the reading is stale (or
otherwise unusable), exit 0 only when it is fresh and well-formed. Ship it with
tests.

## Protected Intent
`scripts/gauge_reader.py` already implements the fail-safe read contract for
the gauge file (module 2 of the Context Governor, epic-178): every failure
mode — absent file, corrupt JSON, malformed record, staleness by
`observed_at`, clock skew, an uncalibrated model — collapses to `None`, and a
`Reading` that reaches a caller is fresh and well-formed *by construction*.
This gate's script must sit on top of that contract, not re-implement it: call
`gauge_reader.read()` (and `raw_record`/`skip_reason`/`uncalibrated_model` only
if useful for a diagnostic message) rather than re-parsing JSON or
re-deriving staleness/calibration logic independently. Two things this must
not regress:
- Do not reintroduce a fallback reading for an unrecognized model. Issue #252
  removed exactly that fallback after an uncalibrated model produced a wrong
  (not absent) reading and mis-tripped the governor — see the
  `_DEFAULT_PROFILE` / `uncalibrated_model` comments in `gauge_reader.py`.
  "No reading" must always mean "treat as stale" here, never "assume fresh."
- Do not change `gauge_reader.py`'s public contract (`read`, `Reading`,
  `DEFAULT_MAX_AGE`, `_PROFILES`, etc.) to make this script's job easier.

## Test Mode
Test-after allowed (per gate constraints).

## Close Criteria
- `scripts/verify_gauge_freshness.py` exists, is a runnable CLI script (`python
  scripts/verify_gauge_freshness.py <path-to-gauge.json>` or equivalent
  argument shape — implementer's choice, document it in the script's
  docstring/`--help`), and:
  - exits `0` when `gauge_reader.read()` on the given path returns a fresh
    `Reading`;
  - exits non-zero (pick and document one non-zero code; distinguishing
    sub-codes are optional, not required) for every case `read()` returns
    `None` for: missing file, corrupt JSON, missing/malformed field,
    stale-by-`observed_at`, clock-skew-in-the-future, uncalibrated model.
  - prints a short human-readable reason for a non-zero exit (may use
    `raw_record`/`skip_reason`/`uncalibrated_model` to say *which* failure
    mode, on a best-effort basis — this is a nicety, not a close criterion by
    itself).
- `tests/test_verify_gauge_freshness.py` exists and exercises, at minimum: one
  fresh-record pass (exit 0), and one case each for missing file, corrupt
  JSON, malformed/missing-field record, and a stale-by-`observed_at` record
  (exit non-zero). Additional cases (uncalibrated model, clock skew) are
  encouraged but not a hard close criterion.
- `.agent-work/proto-exc8/gauge.json` exists as a concrete sample record (not
  a `tests/` fixture) that the script can be run against directly as a
  demonstration. Implementer's choice whether it demonstrates the fresh or
  the stale path; state which, and why, in IMPLEMENTER_RESULT.
- New tests pass; full existing suite stays green (no regressions) — see
  Verification Commands.

## Allowed Scope
- New file: `scripts/verify_gauge_freshness.py`
- New file: `tests/test_verify_gauge_freshness.py`
- New file: `.agent-work/proto-exc8/gauge.json`
- Read-only: import from / read `scripts/gauge_reader.py` for its public
  functions and constants.

## Specific Exclusions
- Do not modify `scripts/gauge_reader.py` (the read-side module this script
  depends on — out of scope for this gate).
- Do not modify `scripts/hooks/gauge_writer_hook.py` or
  `docs/GAUGE_WRITER_HOOK.md` (the writer side — untouched by this gate).
- Do not modify `tests/test_gauge_reader.py` or `tests/test_gauge_writer.py`.
- Do not wire this script into any checklist/spine step command (e.g. no
  edits to any `*SPINE*.template.json`, `checklist_engine.py`, or similar).
  The task as given is "add a script... with tests," not "make something call
  it" — see Authority below on why that's deliberately out of scope here, not
  an oversight.
- Do not touch any other gate's files under `.agent-work/proto-exc8/`
  (`HANDOFF-A1-PROSE.md`, `HANDOFF-A2-NEITHER.md`, `HANDOFF-A3-SPINE.md`,
  `context/`, `mechanical/`) or anything under `arms/`.

## Constraints
- Python 3.12.
- Run tests as `python -m pytest` (not bare `pytest`).
- Reuse `gauge_reader.read()` for the fresh/stale judgment; do not
  reimplement JSON parsing, field validation, staleness, or calibration
  checks independently inside the new script.
- Exit-code convention: `0` = fresh reading confirmed; any non-zero = not
  confirmed fresh (file absent, unreadable, malformed, stale, or
  uncalibrated all collapse to "not confirmed fresh" — do not treat any of
  them as a soft-pass).

## Map Anchors (inbound)
None supplied. The gate plan data made available for this dispatch (task,
deliverable artifact paths, test mode, constraints, listed above) did not
include a separate map-anchors block, so no structural/capability/decision
anchors, evidence-expectation claims, or confidence flags are being carried
into this handoff. If the crew's own reading of the repo turns up a decision
or constraint this task appears to bear on (e.g. anything in the epic-178
DESIGN_SPEC or the `gauge_reader.py` module docstring beyond what's quoted
above), treat it as informative context, not a settled anchor, and surface it
rather than silently deciding for or against it.

## Required Evidence
Load-bearing (prove rigorously):
- `python -m pytest tests/test_verify_gauge_freshness.py -q` output, showing
  all new tests passing.
- The exit code of running the script directly against a hand-built fresh
  gauge record and against a hand-built stale one (two separate invocations,
  both exit codes shown — not just described).
Confirmatory (spot-check is enough):
- `python -m pytest -q` full-suite output showing no new failures relative to
  the pre-change baseline (run it before and after, or note the pre-change
  pass count from a clean baseline run).
- The exit code of running the script against `.agent-work/proto-exc8/gauge.json`
  as shipped, matching what Close Criteria says it demonstrates.

## Wiring Grep

```bash
grep -rn "verify_gauge_freshness\|verify_gauge_freshness\.py" --include=*.py --include=*.json --include=*.md . | grep -v "tests/test_verify_gauge_freshness.py" | grep -v "scripts/verify_gauge_freshness.py"
```

Expected result for this gate: no hits outside the new test file and the
script's own file/docstring — this script is not wired into any checklist
step, CI job, or other caller yet (see Specific Exclusions: wiring is
explicitly out of scope for this task as given). That means the CLI entry
point itself is currently reachable only by direct invocation and by its own
tests, not by any other module — record this plainly as a workflow/out-of-scope
observation in IMPLEMENTER_RESULT rather than silently going quiet about it or
trying to fix it by adding wiring outside the allowed scope.

## Verification Commands

```bash
python -m pytest tests/test_verify_gauge_freshness.py -q
python -m pytest -q
python scripts/verify_gauge_freshness.py <path-to-a-hand-built-fresh-record.json>; echo exit=$?
python scripts/verify_gauge_freshness.py <path-to-a-hand-built-stale-record.json>; echo exit=$?
python scripts/verify_gauge_freshness.py .agent-work/proto-exc8/gauge.json; echo exit=$?
```

## Suggested Model Tier
Simple bounded — thin CLI wrapper over an existing, well-documented,
fail-safe read function; the scope is small and the hard design decisions
(staleness semantics, calibration table, fallback prohibition) are already
made in `gauge_reader.py`.

## Authority
Fixed by this handoff (commander), not open to the implementer to relitigate:
- The deliverable file set and the task boundary (script + tests only; no
  wiring into a caller this gate).
- The constraint that the script must delegate to `gauge_reader.read()`
  rather than reimplement its logic.
- The prohibition on an unknown-model fallback reading (issue #252).

Left to the implementer's judgment, to be stated in IMPLEMENTER_RESULT:
- Exact CLI argument shape and exit-code value(s).
- Whether `.agent-work/proto-exc8/gauge.json` demonstrates the fresh or the
  stale path.
- Whether to surface a diagnostic reason string on non-zero exit (nicety, not
  required).

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion
must be touched (in particular: needing to modify `gauge_reader.py` itself,
or needing to wire this script into a checklist/spine caller to make the
task make sense), required evidence cannot be produced, or a decision
outside the given authority is needed (e.g. whether this script should also
handle the writer-hook sidecar files `gauge-uncalibrated.json` /
`gauge-skip.json` as first-class inputs rather than just via
`gauge_reader.read()`'s collapse-to-`None`).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode
satisfied, evidence produced, assumptions used, stop conditions hit,
out-of-scope observations, workflow feedback (what in this handoff or the
workflow made the work harder than it needed to be).
