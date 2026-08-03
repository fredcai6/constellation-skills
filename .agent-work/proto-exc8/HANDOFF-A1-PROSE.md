# Implementer Handoff

## Gate
g1-implement — "g1 add gauge freshness verifier: implement"

## Task
Add a script, `scripts/verify_gauge_freshness.py`, that exits non-zero when the governor's gauge reading is stale, with tests.

## Protected Intent
The gauge's fail-safe contract must not be re-derived or weakened: `scripts/gauge_reader.py`'s `read()` already collapses every staleness/corruption/miscalibration failure mode to `None` and is the single source of truth for "is this reading usable." The new verifier must judge staleness by calling `gauge_reader.read()` (or `raw_record()` for the failure-detail path), not by reimplementing age-comparison or clock-skew logic inline — a second staleness calculation is exactly the kind of drift `gauge_reader.py`'s docstring warns against.

## Test Mode
test-after allowed (per gate plan constraints).

## Close Criteria
- `scripts/verify_gauge_freshness.py` exists and is executable via `python scripts/verify_gauge_freshness.py <gauge_path>`.
- It exits non-zero (document the exact code chosen, e.g. 1) when `gauge_reader.read(<gauge_path>)` returns `None` (covers: absent file, corrupt JSON, malformed/missing-field record, stale-by-`observed_at`, clock-skew, uncalibrated model).
- It exits 0 when `gauge_reader.read(<gauge_path>)` returns a fresh `Reading`.
- New tests in `tests/` (naming convention: mirror `tests/test_gauge_reader.py`, e.g. `tests/test_verify_gauge_freshness.py`) cover at minimum: a fresh reading (exit 0), a stale reading by `observed_at` (exit non-zero), and a missing gauge file (exit non-zero). Do not pin a specific count of test cases beyond this minimum — the implementer may add more.
- `python -m pytest` passes (full suite, no new failures).

## Allowed Scope
- New file: `scripts/verify_gauge_freshness.py`.
- New test file(s) under `tests/` covering the new script.
- Read-only use of `scripts/gauge_reader.py` (import and call `read()`/`raw_record()`; do not modify it).
- `.agent-work/proto-exc8/gauge.json` may be created/written as a local fixture or manual-verification artifact if useful, per the Deliverable Path Check below.

## Specific Exclusions
- Do not modify `scripts/gauge_reader.py`, `scripts/gauge_writer_hook.py`, or any other existing module — this gate is additive only.
- Do not touch `tests/test_gauge_reader.py` or `tests/test_gauge_writer.py` — this gate does not change gauge-reading/writing behavior, only adds a consumer of `read()`.

## Constraints
- Python 3.12.
- Run tests as `python -m pytest`.
- Reuse `gauge_reader.read()` for the freshness judgment; do not duplicate its staleness/clock-skew/calibration logic.

## Map Anchors (inbound)
None provided in this gate's plan data — the engine's `current` output referenced an anchors block, but no execute.json or map-anchor artifact was found under `.agent-work/proto-exc8/` (only `context/` and `mechanical/` sidecar files, which carry no anchor content). Proceeding without inbound anchors; the implementer should treat `scripts/gauge_reader.py`'s public `read()`/`raw_record()` contract (read directly, see docstrings) as the only inherited structural fact for this gate.

## Deliverable Path Check
- **Committed** — `scripts/verify_gauge_freshness.py` (`git check-ignore` exit 1 — not ignored). This is a new file: `git status` will show it under untracked (`??`) until staged; it does not yet appear in `git diff`.
- **Local-only** — `.agent-work/proto-exc8/gauge.json` (`git check-ignore -v` exit 0, matched `.gitignore:9:.agent-work/**/gauge.json`). Intentionally local-only per the repo's `.gitignore`; treat as a disposable fixture/manual-check artifact, not a committed deliverable.

## Required Evidence
- `python -m pytest` output showing the new test(s) passing and the full-suite result (pass count; if any pre-existing failures exist unrelated to this change, name them explicitly — do not silently fold them into "all green"). Load-bearing: this is the primary proof of Close Criteria.
- A manual demonstration (command + output) that the script exits non-zero against a stale or missing gauge file and exits 0 against a fresh one — e.g. construct `.agent-work/proto-exc8/gauge.json` with a stale `observed_at`, run the script, show the exit code (`echo $?` or `echo %errorlevel%`), then overwrite with a fresh record and show exit 0. Load-bearing.
- The exit code chosen for the non-zero case, stated explicitly (confirmatory).

## Wiring Grep
The new symbol is the script's entry point (module-level `main()` or equivalent) invoked via `if __name__ == "__main__":` — this is a standalone CLI script, not a library function other code imports, so there is no external caller to grep for.

`none — this is a standalone CLI script invoked as a subprocess (its own entry point), not a symbol other Python modules call; its only "caller" is command-line invocation, which is exercised by the Required Evidence manual demonstration above, not grep.`

## Verification Commands

```bash
python -m pytest
```

```bash
python scripts/verify_gauge_freshness.py .agent-work/proto-exc8/gauge.json ; echo exit=$?
```

## Suggested Model Tier
simple bounded — reason: small, additive, single-file script with a narrow contract (delegate to an existing, well-documented `read()` function); low ambiguity, low risk, no design decisions beyond exit-code choice.

## Authority
- The choice of non-zero exit code (e.g. `1`) is the implementer's to make and document; no other exit-code convention is mandated by this gate.
- Whether `.agent-work/proto-exc8/gauge.json` is created as a committed-looking fixture or left purely as an ephemeral manual-test artifact is the implementer's call — it is git-ignored either way, so nothing here is a durability decision.
- The implementer must not decide to modify `gauge_reader.py`'s staleness contract or add a second staleness algorithm — that is out of authority for this gate; escalate if `read()`'s contract appears insufficient for the task.

## Stop Conditions
Stop and return if: allowed scope must be exceeded (e.g. `gauge_reader.py` must change to satisfy the task), a specific exclusion must be touched, required evidence cannot be produced, or a decision outside the given authority is needed (e.g. `read()`'s existing staleness contract does not actually cover a case the task requires).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the work harder than it needed to be).
