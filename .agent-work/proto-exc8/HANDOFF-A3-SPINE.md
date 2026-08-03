# Implementer Handoff

## Gate
`g1-implement` — "g1 add gauge freshness verifier: implement"

## Task
Add `scripts/verify_gauge_freshness.py`: a CLI script that reads a gauge file
(same format `scripts/gauge_reader.py` already parses) and exits non-zero
when the reading is NOT fresh (stale by `observed_at`, absent, corrupt,
malformed, clock-skewed, or for a model with no calibration profile), exits
0 when it is fresh. Add tests for it. Also produce
`.agent-work/proto-exc8/gauge.json` as a real demonstration record at this
run's own gauge path (see Deliverable Path Check — this file is
intentionally local-only, not a commit target).

## Protected Intent
`scripts/gauge_reader.py`'s whole design point is: "every failure mode
collapses to `None`... never raises" (its own module docstring), so that a
caller structurally cannot act on stale or bad data. This gate's script is a
NEW caller of that reader, not a rewrite of it. It must inherit the same
fail-safe posture — no traceback on a missing/corrupt/malformed file, just a
clean non-zero exit — and it must NOT duplicate the staleness/parsing logic
that already lives in `gauge_reader.read()`/`raw_record()`. It also must not
become a second gate-boundary Trip mechanism: `checklist_engine.py` already
has a two-band SOFT/HARD Trip policy (#182) that reads the gauge at gate
boundaries (see Map Anchors below); this script is separate, additive
tooling, not a change to that dispatch path.

## Test Mode
Test-after allowed (per gate plan).

## Close Criteria
- `scripts/verify_gauge_freshness.py` exists, is a CLI (argparse, matching
  the shape of `scripts/verify_skip_guard.py`: `main(argv) -> int`,
  `raise SystemExit(main())`), takes a gauge-file path argument, and:
  - exits `0` when `gauge_reader.read(path)` returns a fresh `Reading`.
  - exits non-zero (pick one consistent code, e.g. `1`) when `read()`
    returns `None` for ANY reason (absent file, corrupt JSON, malformed
    record, stale `observed_at`, clock-skew, or uncalibrated model).
- New tests in `tests/test_verify_gauge_freshness.py`, runnable via
  `python -m pytest`, covering at minimum: a fresh reading exits 0; a stale
  reading exits non-zero; a missing file exits non-zero. Exact test count —
  derive it from the test file you actually write, don't let this handoff
  pin a number.
- Full suite stays green: `python -m pytest` after your change shows no
  failures beyond whatever baseline existed before you touched anything
  (capture that baseline first — see Required Evidence).
- No existing test's scenario is invalidated by this change — you are not
  touching `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`,
  or `scripts/checklist_engine.py`, so `tests/test_gauge_reader.py` and
  `tests/test_gauge_writer.py` need no reconciliation and should be left
  alone.
- `.agent-work/proto-exc8/gauge.json` exists on disk as a real record your
  script was actually run against (see Required Evidence) — it will NOT
  show up in `git status` as addable (it's gitignored by design, see
  Deliverable Path Check), so "should this be staged" is not a live
  question — don't fight the ignore rule.

## Allowed Scope
- New file: `scripts/verify_gauge_freshness.py`.
- New file: `tests/test_verify_gauge_freshness.py`.
- New local file (not committed): `.agent-work/proto-exc8/gauge.json`.
- Reading (not modifying) `scripts/gauge_reader.py`'s public surface:
  `read()`, `raw_record()`, `REQUIRED_FIELDS`, `DEFAULT_MAX_AGE`, the
  `Reading` dataclass.
- Reading (not modifying) `scripts/verify_skip_guard.py` as a structural
  precedent for CLI shape/argparse/exit-code convention in this same
  `scripts/` directory.

## Specific Exclusions
- Do not modify `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`,
  or `scripts/checklist_engine.py`. This gate adds a new standalone consumer
  of the reader; it does not touch the read/write/Trip modules themselves.
- Do not wire this script into `checklist_engine.py`'s gate-boundary Trip
  dispatch (SOFT/HARD, #182) — that machinery already exists and is out of
  scope here.
- Do not wire this script into `.github/workflows/ci.yml`. `verify_skip_guard.py`
  is invoked there, but adding a CI step is a separate decision this gate's
  Task does not ask for — see Wiring Grep below for how that's handled.
- Do not edit `.gitignore`'s existing `.agent-work/**/gauge.json` entry, and
  do not `git add -f` the demonstration `gauge.json` — its local-only status
  is intentional (see Deliverable Path Check).

## Constraints
- Python 3.12.
- Run tests as `python -m pytest`.
- There is no `scripts/__init__.py` package marker. Every existing test that
  loads a `scripts/` module does it via
  `importlib.util.spec_from_file_location` against an absolute path (see
  `tests/test_gauge_reader.py:9-17` and `tests/test_gauge_writer.py:16-26`
  for the exact pattern) — a plain `import scripts.gauge_reader` will not
  work from `tests/`. Load `gauge_reader` in your test file the same way.
  Inside `verify_gauge_freshness.py` itself, since it lives in the same
  `scripts/` directory as `gauge_reader.py`, a plain `import gauge_reader`
  works when the script is run as `python scripts/verify_gauge_freshness.py`
  (a script's own directory is on `sys.path`) — confirm this with a real
  run rather than assuming it; if it doesn't hold, fall back to the same
  `importlib.util.spec_from_file_location` pattern used in the tests.
- Reuse `gauge_reader.read()` (and `raw_record()` if useful for a message)
  rather than re-parsing JSON or re-deriving staleness yourself.
- Exit-code convention should match the existing `verify_*.py` scripts in
  `scripts/` (e.g. `verify_skip_guard.py`): `0` = pass, non-zero = refused,
  with a short human-readable message on stdout/stderr explaining which.

## Map Anchors (inbound)
No formal mission-frame/anchors file exists for this prototype run (`.agent-work/proto-exc8/`
has no `MISSION_FRAME.md` or equivalent) — the anchors below are derived
directly from reading the live source during handoff authoring:
`docs/GAUGE_WRITER_HOOK.md`, `scripts/gauge_reader.py`, and the Trip section
of `scripts/checklist_engine.py`.

- **Structural:** `struct:gauge-reader` — `scripts/gauge_reader.py`, module
  level — the read-side module this new script must call into (`read()`,
  `raw_record()`, `REQUIRED_FIELDS`, `DEFAULT_MAX_AGE`). The new work lands
  as a sibling script in `scripts/`, not inside this file.
- **Structural:** `struct:checklist-engine-gauge` —
  `scripts/checklist_engine.py:1173-1339` (the `_gauge_path` /
  `_read_gauge` / `_uncalibrated_advisory` / `_skip_reason_advisory` /
  `_stale_record_advisory` / `_no_reading_advisory` family), function-group
  level — the engine's own existing gate-boundary consumer of
  `gauge_reader`. This gate's script is a separate, standalone consumer and
  must not be merged into this dispatch path.
- **Capability:** `capability:gauge-read` — reading a `gauge.json` record
  and collapsing every failure mode (absent/corrupt/malformed/stale/
  clock-skew/uncalibrated-model) to one fail-safe result; this gate exposes
  that result as a process exit code for the first time.
- **Constraints/assumptions:** `constraint:fail-safe-reader` —
  `gauge_reader.read()` never raises (module docstring, `scripts/gauge_reader.py:1-15`).
  The new script must preserve this: no new exception path for a caller
  who points it at a bad path.
- **Constraints/assumptions:** `constraint:gauge-gitignored` —
  `.agent-work/**/gauge.json` is deliberately gitignored (`.gitignore`
  lines 6-9: "Live runtime state, not run history... machine-specific").
  The `.agent-work/proto-exc8/gauge.json` deliverable being local-only is
  by design, not a gap to fix.
- **Decision anchors:** `decision:trip-two-band` — `checklist_engine.py`'s
  existing SOFT/HARD Trip policy (#182, `scripts/checklist_engine.py:1143-1172`)
  already governs gate-boundary behavior on gauge fill.
  `@grade: settled/existing-shipped-code · settle: do not modify Trip's
  dispatch wiring in this gate — this script is additive, not a
  replacement or a second Trip mechanism.`
- **Evidence expectations:** `claim:read-never-raises` — re-confirm (by
  test) that `verify_gauge_freshness.py` itself never raises/tracebacks on
  an absent, corrupt, or malformed gauge file — only ever a clean exit code.
- **Map confidence flags:** none — the anchors above were read directly
  from source during this handoff, not inferred or recalled from memory.

## Deliverable Path Check
Commander-run, before dispatch:

```
$ git check-ignore -v scripts/verify_gauge_freshness.py
(no output)
$ echo exit=$?
exit=1
```
→ **Committed** — `scripts/verify_gauge_freshness.py` (not ignored; this is
a new, currently-untracked file — expect it to appear in `git status`, not
in `git diff`, until staged).

```
$ git check-ignore -v .agent-work/proto-exc8/gauge.json
.gitignore:9:.agent-work/**/gauge.json	.agent-work/proto-exc8/gauge.json
$ echo exit=$?
exit=0
```
→ **Local-only** — `.agent-work/proto-exc8/gauge.json` (matched by
`.gitignore` line 9, "Live runtime state, not run history... machine-specific").
This is expected and intentional — do not force-add it, do not edit
`.gitignore` to un-ignore it.

`tests/test_verify_gauge_freshness.py` is also a new committed deliverable
of this gate (implied by "with tests" in Task, not separately listed in the
gate's artifact paths) — same **Committed** treatment as the script; it was
not separately `check-ignore`d because it lives under `tests/`, which
carries no gauge-specific ignore rule.

## Required Evidence
Load-bearing (prove rigorously):
- `python -m pytest tests/test_verify_gauge_freshness.py -v` — full output,
  all new tests passing.
- A real CLI invocation, not just unit tests calling functions directly:
  `python scripts/verify_gauge_freshness.py .agent-work/proto-exc8/gauge.json`
  plus its exit code, against a genuinely fresh record you wrote at that
  path — this is what produces the `.agent-work/proto-exc8/gauge.json`
  deliverable. Quote the exact record you wrote (all four fields:
  `schema_version`, `fill_fraction`, `model`, `observed_at`) and the exact
  command output/exit code.
- A second real invocation against a deliberately non-fresh input (a stale
  `observed_at`, or a path that doesn't exist) confirmed to exit non-zero.
  Quote the command and exit code.
- Confirmation that neither invocation above produced a traceback —
  quote stderr (or its absence) for both.

Confirmatory (a spot-check suffices):
- `python -m pytest` (full suite) run once BEFORE you touch anything, to
  record the baseline pass count, and once after — report both counts. A
  claimed failure distribution, if any failures appear, must come from
  `pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`, not a
  glance at the tail.

## Wiring Grep

`verify_gauge_freshness.py` is a leaf CLI tool (same shape as
`scripts/verify_skip_guard.py`), not a library symbol other Python modules
are expected to import. Its "caller" in this gate is the shell invocation
you run yourself for Required Evidence above, not a grep-able Python call
site — Specific Exclusions above deliberately keeps it unwired from
`checklist_engine.py` and `.github/workflows/ci.yml` in this gate.

```bash
grep -rn "verify_gauge_freshness" --include=*.py --include=*.yml . | grep -v "def main" | grep -v test_verify_gauge_freshness
```

Expect **0 external call sites** here. This is the deliberate exception to
"zero external call sites is a stop condition": for a leaf CLI script with
no wiring requested in Task, the real-subprocess invocations captured under
Required Evidence are what prove it isn't shipped-inert — a human or a
future CI/engine change invokes it by path, not by import. If you believe
it should be wired into CI or the engine now, that's an out-of-scope
observation to report back, not a decision to make unilaterally in this
gate.

## Verification Commands

```bash
python -m pytest tests/test_verify_gauge_freshness.py -v
python -m pytest
python scripts/verify_gauge_freshness.py .agent-work/proto-exc8/gauge.json
```

## Suggested Model Tier
`simple bounded` — reason: small, well-scoped script with strong existing
precedent to mirror (`scripts/gauge_reader.py`'s public API is already
fail-safe and documented; `scripts/verify_skip_guard.py` is a ready-made CLI
shape template). Low ambiguity, low risk, no cross-module rewiring.

## Authority
Decisions already made (by the commander, from source reading, not to be
reopened by the implementer):
- Reuse `gauge_reader.read()`/`raw_record()`; do not reimplement staleness
  or JSON parsing.
- This script is NOT wired into `checklist_engine.py`'s Trip dispatch or
  into `.github/workflows/ci.yml` in this gate.
- `.agent-work/proto-exc8/gauge.json` is intentionally local-only; its
  absence from `git status`'s addable files is correct, not a defect.

Left to the implementer, to state explicitly in IMPLEMENTER_RESULT if
exercised:
- The exact non-zero exit code chosen for "not fresh" (a single code like
  `1` is sufficient; distinguishing stale-vs-absent-vs-corrupt by different
  codes is not required by Task, but not forbidden either — state your
  choice).

## Stop Conditions
Stop and return if: allowed scope must be exceeded (e.g. you find you need
to touch `gauge_reader.py`, `gauge_writer_hook.py`, or `checklist_engine.py`
to make this work), a specific exclusion must be touched (CI wiring,
`.gitignore` edit), required evidence cannot be produced, or a decision
outside the given authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode
satisfied, evidence produced, assumptions used, stop conditions hit,
out-of-scope observations, workflow feedback (what in this handoff or the
workflow made the work harder than it needed to be).
