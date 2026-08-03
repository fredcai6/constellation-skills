# Implementer Handoff

## Gate
g1-implement — "g1 add gauge freshness verifier: implement"

## Task
Add `scripts/verify_gauge_freshness.py`: a CLI script that reads the Context
Governor's gauge file and exits non-zero when the reading is stale (or
absent/malformed/unparseable), exits 0 when a fresh reading exists. Ship
tests covering both outcomes.

## Protected Intent
The Context Governor's gauge reader (`scripts/gauge_reader.py`) already
implements the whole staleness/parsing/calibration contract and is
deliberately fail-safe: `read()` collapses every failure mode — absent file,
corrupt JSON, missing/malformed field, stale `observed_at`, clock-skew, an
uncalibrated model — to a single `None`, and it never raises. This gate's
script must be a thin CLI wrapper around that existing contract, not a
second, independently-reasoned staleness policy. Concretely:
- Freshness/staleness must be decided by calling `gauge_reader.read()` (using
  its existing `DEFAULT_MAX_AGE` unless the CLI explicitly overrides it),
  never by re-deriving age/parsing logic locally.
- The script itself must never let an exception escape to a traceback for any
  of the ordinary failure modes above — every one of them must map to a
  clean non-zero exit, mirroring the fail-safe contract it wraps.
- The script answers exactly one question — "is there a fresh reading right
  now" — and must not additionally judge `fill_fraction` against the
  soft/hard thresholds (`thresholds_for()`); that is Trip's job elsewhere in
  the Context Governor and is out of scope here.

## Test Mode
test-after allowed (per gate plan / execute.json for g1-implement).

## Close Criteria
- `scripts/verify_gauge_freshness.py` exists, is invocable as
  `python scripts/verify_gauge_freshness.py <path-to-gauge.json>`, and:
  - exits `0` when `gauge_reader.read(path)` returns a `Reading` (fresh,
    well-formed, calibrated).
  - exits non-zero (`1`) when `gauge_reader.read(path)` returns `None` for
    any reason (missing file, corrupt JSON, malformed/missing field, stale
    `observed_at`, clock-skew, uncalibrated model).
- A new test file (naming convention already used in this repo:
  `tests/test_verify_gauge_freshness.py`) exists and covers at minimum: a
  fresh reading (exit 0), a stale reading whose `observed_at` exceeds
  `DEFAULT_MAX_AGE` (exit non-zero), a missing gauge file (exit non-zero),
  and a malformed/corrupt gauge file (exit non-zero). One test per scenario
  is the expectation — do not collapse them into a single parametrized case
  that hides which scenario actually failed.
- `python -m pytest` is green, including the new test file — record the
  pre-change and post-change collected/passed test counts (see Required
  Evidence).
- Deliverable Path Check (below) is satisfied for both listed deliverable
  paths.

Never pin a literal test count into this handoff beyond the four scenarios
named above — derive the exact pre/post pytest totals from the live run at
evidence time, not from a number recalled here.

## Allowed Scope
- New file: `scripts/verify_gauge_freshness.py`.
- New file: `tests/test_verify_gauge_freshness.py`.
- Read-only use of `scripts/gauge_reader.py`'s public API (`read`,
  `Reading`, `DEFAULT_MAX_AGE`, and — only if genuinely needed —
  `raw_record`/`skip_reason`/`uncalibrated_model`). Do not modify
  `gauge_reader.py`.
- Read-only reference to `tests/test_gauge_reader.py` for existing
  fixture/pattern conventions (constructing valid/invalid gauge records,
  injecting `now`) — pre-authorized to read for pattern-matching, not to
  edit.
- Producing `.agent-work/proto-exc8/gauge.json` as a local working
  fixture/example while developing or demonstrating the script (see
  Deliverable Path Check — this path is gitignored by design and must not
  be force-added).

## Specific Exclusions
- Do not modify `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`,
  or any other Context Governor module — this gate only adds a new read-side
  CLI consumer, it does not change the governor itself.
- Do not modify `.gitignore`.
- Do not modify or delete any other file already present under
  `.agent-work/proto-exc8/` (e.g. `HANDOFF-A1-PROSE.md`,
  `HANDOFF-A2-NEITHER.md`, `HANDOFF-A3-SPINE.md`,
  `IMPLEMENTER_HANDOFF.nosection.md`, `IMPLEMENTER_HANDOFF.stripped.md`, or
  the `context/`, `mechanical/` subdirectories) — those belong to other arms
  of this same rehearsal and must be left untouched.
- Do not `git add -f` or otherwise force-commit
  `.agent-work/proto-exc8/gauge.json` — it is intentionally excluded by
  `.gitignore:9` (`.agent-work/**/gauge.json`, "live runtime state ...
  machine-specific").
- Do not wire `verify_gauge_freshness.py` into any checklist template's
  `postconditions` (no `skills/*/templates/*.json` edits). This gate's
  deliverable list is the script + tests only; hooking it into a gate's
  `check.command` is a separate, later decision outside this gate's scope
  (see Wiring Grep and Authority below for why this is called out
  explicitly rather than assumed).

## Constraints
- Python 3.12: write code that only relies on language/stdlib features valid
  under 3.12 (this repo's convention, seen throughout `gauge_reader.py`, is
  `from __future__ import annotations` at the top of new modules — follow
  it). Note: the interpreter actually resolved in this environment when I
  checked was 3.14.3 (`python --version`) — that is fine to develop/test
  against, but do not rely on any 3.13+/3.14-only syntax or stdlib addition.
- Run tests as `python -m pytest` (not `pytest` directly, not `unittest`).
- Follow the existing `scripts/verify_*.py` CLI convention used elsewhere in
  this repo (e.g. `scripts/verify_context_declaration.py`): `argparse`-based
  entry point, `sys.exit(0)` on pass / `sys.exit(1)` on fail, no bare
  top-level code that runs on import (guard with `if __name__ == "__main__":`).
- When calling `gauge_reader.read()`, its keyword parameters are `now:
  datetime | None = None` and `max_age: timedelta = DEFAULT_MAX_AGE` — pass
  these explicitly by name if overridden (e.g. from a test or a CLI flag),
  do not pass positionally.
- `gauge_reader.Reading` is a frozen dataclass with exactly four fields:
  `schema_version: int`, `fill_fraction: float`, `model: str`,
  `observed_at: datetime` — if the script prints anything on success, it may
  reference these fields by name but must not invent additional ones.

## Map Anchors (inbound)
The gate plan data handed to me for g1-implement (task, deliverable paths,
test mode, constraints) did not include an anchors block, and I was
instructed not to read `execute.json` or other files under
`.agent-work/proto-exc8/` beyond this template — so the anchors below are
derived directly from the fair-game parts of the repo I was able to read
(not carried from a mission-frame anchors block), and are best-effort
grounding rather than a verified inbound set.
- **Structural:** `scripts/gauge_reader.py` — Module 2 (Gauge), read side, of
  the Context Governor (epic #178); this is the module the new script must
  wrap, not reimplement. `@grade: unknown/provenance not available to me —
  treat as settled prior art, do not restructure it for this gate.`
- **Capability:** `gauge_reader.read()` — returns a fresh, well-formed,
  calibrated `Reading` or `None`; already the single source of truth for
  "is this gauge reading usable right now."
- **Constraints/assumptions:** `.gitignore:6-9` — `.agent-work/**/gauge.json`
  is deliberately untracked ("Live runtime state, not run history:
  per-session governor readings ... are rewritten constantly and are
  machine-specific"). Any gauge.json this gate's implementer produces is
  local-only by design, not a committed artifact.
- **Decision anchors:** epic #178 DESIGN_SPEC section "2. Gauge" (referenced
  in `gauge_reader.py`'s module docstring; I did not open the epic-178
  crew-handoffs in depth for this handoff) — governs the frozen 4-field
  record shape and the fail-safe/never-raise contract this gate's script
  must preserve. `@grade: unknown/provenance not available to me · settle:
  ask epic-178's owner if this gate's CLI wrapper needs review against that
  spec before merge.`
- **Evidence expectations:** re-confirm (do not just assume) that
  `gauge_reader.read()` truly never raises for the four failure fixtures
  this gate's tests construct — that is the load-bearing property the whole
  handoff leans on.
- **Map confidence flags:** none of the above were pulled from a verified
  anchors block — treat all of them as low-confidence relative to whatever
  the real g1-implement anchors block in `execute.json` says, and prefer
  that source if it becomes available.

## Required Evidence
Load-bearing (prove rigorously):
- Full `python -m pytest` output showing the suite green after the change,
  with the collected/passed test count reported both before and after this
  gate's change (e.g. `python -m pytest -q` summary line pre-change vs.
  post-change) — derive both counts mechanically from the actual run, never
  from a recalled number.
- The exit code of `python scripts/verify_gauge_freshness.py <path>`
  demonstrated for both outcomes: a path with a fresh, valid gauge.json
  (must print/show exit code `0`) and a path that is stale or
  missing/malformed (must print/show exit code non-zero, expected `1`) —
  quote the literal commands run and their `$?`/exit codes, not a
  paraphrase.
- The four test scenarios named in Close Criteria (fresh / stale / missing /
  malformed) each independently pass — name which test function covers each.

Confirmatory (spot-check is sufficient):
- CLI help text / docstring quality and consistency with the
  `scripts/verify_*.py` house style.
- Whether the script also prints a human-readable reason on failure (nice to
  have; not a close criterion — the exit code is what's load-bearing, not
  the message text).

## Wiring Grep

```bash
grep -rn "verify_gauge_freshness" --include=*.py --include=*.json --include=*.md . | grep -v "^scripts/verify_gauge_freshness.py:"
```

Expected: at least one hit outside `scripts/verify_gauge_freshness.py`
itself, coming from `tests/test_verify_gauge_freshness.py` invoking the
script (as a subprocess or via its `main()`/argparse entry point) — that
test invocation is this gate's only expected caller. **Zero hits outside the
script's own file is a stop condition**, same as for any other new symbol.

Explicitly NOT expected as part of this gate: a hit inside any
`skills/*/templates/*.json` checklist template wiring this script into a
`postconditions[].check.command` (the way `verify_cycles.py` is wired into
`skills/explorer/templates/EXPLORER_SPINE.template.json`, for example).
That kind of production wiring is real and is how every other
`scripts/verify_*.py` script in this repo ends up with a caller beyond its
own tests — but it is not in this gate's deliverable list, so its absence
here is expected, not a defect. Flag it explicitly as an out-of-scope
observation in the IMPLEMENTER_RESULT rather than silently adding it or
silently omitting it.

## Verification Commands

```bash
python -m pytest tests/test_verify_gauge_freshness.py -v
python -m pytest -q
python scripts/verify_gauge_freshness.py .agent-work/proto-exc8/gauge.json; echo "exit=$?"
git check-ignore -v scripts/verify_gauge_freshness.py; echo "exit=$?"
git check-ignore -v .agent-work/proto-exc8/gauge.json; echo "exit=$?"
```

## Suggested Model Tier
simple bounded — the underlying primitive (`gauge_reader.read()`) already
implements all staleness/parsing/calibration logic; this gate is a thin CLI
wrapper plus tests, following an already-established
`scripts/verify_*.py` pattern in this repo. Low ambiguity, low risk.

## Authority
- Gate scope (task, the two deliverable paths, test mode = test-after
  allowed, and the Python 3.12 / `python -m pytest` constraints) is fixed by
  execute.json for gate g1-implement of the proto-exc8 B3-SPINE arm; the
  implementer does not have authority to change any of those.
- The implementer may freely decide the concrete CLI shape (argument names,
  an optional `--max-age` override, whether to print a reason string) and
  the internal test structure, within the constraints above.
- Whether/how to wire `verify_gauge_freshness.py` into a checklist
  template's postcondition is explicitly NOT this gate's decision — do not
  decide it unilaterally either way; surface it as an out-of-scope
  observation for whoever plans the next gate.
- I (the Commander driving this checklist run) am not authorized in this
  environment to dispatch the actual `constellation-implementer` subagent —
  see Stop Conditions.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a specific exclusion
must be touched, required evidence cannot be produced (e.g.
`gauge_reader.read()` is observed to raise for some fixture, contradicting
its documented never-raise contract — that is a defect in the dependency,
not something to silently work around here), or a decision outside the
given authority is needed (e.g. whether to wire this into a template).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode
satisfied, evidence produced, assumptions used, stop conditions hit,
out-of-scope observations, workflow feedback (what in this handoff or the
workflow made the work harder than it needed to be).

---

## Deliverable Path Check

For each committed deliverable of this gate, `git check-ignore <path>` was
run from the repo root (`C:/Programs/.proto-exc8-spine-instructions`) and
must exit `1` (not ignored) to count as a real committed deliverable.

| Deliverable | Command | Result |
|---|---|---|
| `scripts/verify_gauge_freshness.py` | `git check-ignore -v scripts/verify_gauge_freshness.py` | no output; exit `1` — **not ignored, a real committed deliverable.** |
| `.agent-work/proto-exc8/gauge.json` | `git check-ignore -v .agent-work/proto-exc8/gauge.json` | `.gitignore:9:.agent-work/**/gauge.json	.agent-work/proto-exc8/gauge.json`; exit `0` — **is ignored.** |

`.agent-work/proto-exc8/gauge.json` is recorded as **intentionally
local-only**, not a committed deliverable: `.gitignore` lines 6-9 explain
this rule exists because "Live runtime state, not run history: per-session
governor readings ... are rewritten constantly and are machine-specific."
The implementer may still produce this file on disk (e.g. as a fixture used
while manually exercising the CLI per Verification Commands), but must not
force-add or otherwise fight the ignore rule to get it committed — its
absence from `git status`/`git diff` is expected and correct.
