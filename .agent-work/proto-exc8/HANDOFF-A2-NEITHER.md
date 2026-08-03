# Implementer Handoff

## Gate
`g1-implement` — "g1 add gauge freshness verifier: implement"

## Task
Add a script that exits non-zero when the governor's gauge reading is stale, with tests.

## Protected Intent
The Context Governor's fail-safe read contract must not be duplicated or contradicted: `scripts/gauge_reader.py`'s `read()` is the single place that decides "fresh vs. not" (absent file, corrupt JSON, missing/malformed fields, stale `observed_at`, clock-skew, and an uncalibrated model all already collapse to `None` there). This new verifier must reuse that judgment (import and call `read()`/`raw_record()`/`skip_reason()`/`uncalibrated_model()` as needed) rather than re-deriving its own staleness math against `gauge.json`'s `observed_at` field — two independent staleness computations could silently drift apart, which is exactly the failure mode `gauge_reader.py`'s own design note warns about ("this reader never branches on which harness wrote it").

## Test Mode
Test-after allowed (per this gate's constraints).

## Close Criteria
- `scripts/verify_gauge_freshness.py` exists: a CLI that takes a path to a gauge file and exits non-zero when the reading at that path is NOT a fresh, well-formed `Reading` per `gauge_reader.read()` (absent file, corrupt JSON, malformed record, or stale `observed_at` all count as "verification fails, exit non-zero"); it exits 0 only when `gauge_reader.read()` returns a `Reading`.
- The script determines staleness by delegating to `scripts/gauge_reader.py`'s `read()` — not by re-implementing age/threshold comparison itself.
- `tests/test_verify_gauge_freshness.py` exists and covers, at minimum: (1) a fresh well-formed reading -> exit 0, (2) a reading stale by `observed_at` -> exit non-zero, (3) a missing gauge file -> exit non-zero, (4) malformed JSON at the path -> exit non-zero. Each test injects `now`/`max_age` rather than touching the real wall clock (mirror `gauge_reader.read()`'s own `now`-injection contract — see its docstring).
- `.agent-work/proto-exc8/gauge.json` exists as a concrete, real fixture in this run's own work area (local-only — already gitignored, see Deliverable Path Check below) that the script can be run against directly; its content (fresh or stale, implementer's choice) must agree with the exit code the script actually produces when pointed at it.
- `python -m pytest tests/test_verify_gauge_freshness.py -q` passes, all green.
- Full suite stays green: no existing test's scenario is expected to change. State the pre-change and post-change `python -m pytest tests -q` totals; the only expected delta is the new test file's cases being added.

Never pin a literal count you didn't just derive — get the pre-change total from your own `python -m pytest tests -q` run at authoring/implementation time, not from a number recalled from memory.

## Allowed Scope
- New file: `scripts/verify_gauge_freshness.py`
- New file: `tests/test_verify_gauge_freshness.py`
- New/modified file: `.agent-work/proto-exc8/gauge.json` (local-only, gitignored — see below)
- Read-only reference (do not modify): `scripts/gauge_reader.py`, `tests/test_gauge_reader.py`, `tests/test_gauge_writer.py`, `scripts/verify_cycles.py` + `tests/test_verify_cycles.py` (closest existing precedent for this repo's `verify_*.py` CLI + test shape — argparse, a dedicated exception class, `main() -> int`, `if __name__ == "__main__": raise SystemExit(main())`, and a test file that loads the module via `importlib.util.spec_from_file_location` rather than a package import).

Pre-authorized: touching/creating only the test file listed above to exercise the new behavior. No existing test's scenario needs to change for this gate, so no reconciliation of other tests is expected or authorized.

## Specific Exclusions
- Do not modify `scripts/gauge_reader.py` or `scripts/hooks/gauge_writer_hook.py`, or any existing gauge test file (`tests/test_gauge_reader.py`, `tests/test_gauge_writer.py`).
- Do not wire this verifier into any spine/checklist template or engine (e.g. `skills/explorer/templates/EXPLORER_SPINE.template.json`'s `"check": {"kind": "command", ...}` pattern, `skills/commander/templates/EXECUTE_PLAN.template.json`, or `scripts/checklist_engine.py`) — out of scope for this gate; this gate's deliverable paths (per execute.json) are exactly the two files named in Close Criteria above, not a wiring change.
- Do not touch `skills/commander/references/commander-core.md`, `skills/commander/templates/EXECUTE_PLAN.template.json`, or `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md` — these already carry unrelated uncommitted local modifications on this branch (confirmed via `git status`) and are not part of this gate's task.
- Do not touch anything under `arms/`, or `instantiate.py` / `relocate.py` at the repo root — unrelated untracked material for a different exercise running in this same repo.

## Constraints
- Python 3.12.
- Run tests as `python -m pytest`.
- Match this repo's existing `verify_*.py` convention (see `scripts/verify_cycles.py` / `tests/test_verify_cycles.py`): argparse-based CLI, a dedicated exception class for the failure condition, `main(argv=None) -> int` returning 0/1, `if __name__ == "__main__": raise SystemExit(main())`; the test file loads the script module directly via `importlib.util.spec_from_file_location`, not as an installed package.
- Reuse `gauge_reader.read()` for the staleness judgment; import `scripts/gauge_reader.py` the same way its own sibling tests do (or via `importlib`/`sys.path` — implementer's choice, but must not duplicate its logic).
- Tests must inject `now` (and `max_age` if relevant) into the call chain — never depend on real wall-clock time for pass/fail.

## Map Anchors (inbound)
None provided. The engine's `current` output for this gate referenced "the inbound map anchors from this gate's anchors block," but no anchors block accompanied the gate plan data handed to the commander for this dispatch — no `execute.json` anchors section was found in `.agent-work/proto-exc8/`. Proceed without a map-anchor set. If in the course of implementation you find this gate genuinely depends on a decision or constraint anchor not named here, that is a stop condition (a decision outside the given authority), not something to infer or assume silently.

## Deliverable Path Check
- **Committed** — `scripts/verify_gauge_freshness.py` (new; untracked until staged — `git status` will list it, `git diff` will not show it until `git add`).
- **Committed** — `tests/test_verify_gauge_freshness.py` (new; same as above).
- **Local-only** — `.agent-work/proto-exc8/gauge.json` (confirmed gitignored: `.gitignore` line 9 is `.agent-work/**/gauge.json`; `git check-ignore -v .agent-work/proto-exc8/gauge.json` returns exit 0 and reports that match).

## Required Evidence
- `python -m pytest tests/test_verify_gauge_freshness.py -q` — full output, all green. **Load-bearing.**
- `python -m pytest tests -q` run once before any change and once after, with both totals stated side by side. **Load-bearing** for the "no existing test's scenario changed" claim — derive the numbers from these two actual runs, not from memory or a partial glance.
- Two direct CLI invocations of the finished script — one against a fresh reading, one against a stale/missing/malformed one — each immediately followed by printing its exit code (`echo $?` in POSIX sh/bash, or `echo %errorlevel%` in cmd, or `$LASTEXITCODE` in PowerShell, whichever shell you're actually in), showing 0 for the fresh case and non-zero for the other. **Load-bearing** — this is the actual close-criterion behavior, not the pytest suite's proxy for it.
- One line naming which of `scripts/gauge_reader.py`'s functions the new script calls (e.g. `read()`), confirming no independent staleness computation was written. **Confirmatory** — a spot-check of Protected Intent, not a rigorous proof.

## Wiring Grep
This gate does not wire the new verifier into any spine/checklist/engine caller — that's explicitly out of scope (see Specific Exclusions), because the deliverable paths given for this gate are only the script and the local fixture, not a template or engine change. The precedent in this repo (`verify_cycles.py`) is wired into a spine template's `"check": {"kind": "command", "command": "python <path> <work-id>"}` field in a *later* step than "add the script" — this gate is that earlier step. So run:

```bash
grep -rn "verify_gauge_freshness" --include=*.py --include=*.json . | grep -v "def verify_gauge_freshness" | grep -v "scripts/verify_gauge_freshness.py:"
```

and expect it to show **zero** call sites outside the new script's own definition and its own test file. That is expected and acceptable for this gate — state the count found and confirm it matches zero — rather than a stop condition, because no template/engine wiring is in this gate's allowed scope. (If the grep instead turns up a non-test, non-definition call site you didn't add, or a template file changed, stop: that means scope was exceeded.)

## Verification Commands

```bash
python -m pytest tests/test_verify_gauge_freshness.py -q
python -m pytest tests -q
python scripts/verify_gauge_freshness.py .agent-work/proto-exc8/gauge.json
```

(The exact CLI argument shape — e.g. a single positional path vs. a `--path` flag — is the implementer's choice; document it in the script's own `--help`/docstring and use it consistently across the script, its tests, and the command above.)

## Suggested Model Tier
Simple bounded — a small CLI-plus-tests slice with a directly precedented shape (`scripts/verify_cycles.py`) and a fail-safe primitive to reuse (`gauge_reader.read()`); no architectural ambiguity, no cross-module wiring in scope.

## Authority
The task, the two deliverable artifact paths, test mode ("test-after allowed"), and the Python/test-runner constraints are fixed by this gate's plan data (execute.json, as relayed by the commander) and given verbatim above — the implementer must not renegotiate them. Whether the CLI takes the gauge path positionally or via a flag, and whether to expose a `--max-age` override or rely on `gauge_reader.DEFAULT_MAX_AGE`, is the implementer's call within Allowed Scope. Anything touching `gauge_reader.py` itself, or wiring this verifier into the engine or any spine/checklist template, is outside the implementer's authority for this gate — stop and return rather than deciding it alone.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion must be touched, required evidence cannot be produced, or a decision outside the given authority is needed (including: this gate turns out to need wiring into a template/engine to be meaningful, or a map anchor this handoff doesn't carry turns out to matter).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this handoff or the workflow made the work harder than it needed to be).
