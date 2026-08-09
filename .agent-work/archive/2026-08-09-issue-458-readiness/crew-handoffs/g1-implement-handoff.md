# Implementer Handoff

Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
g1 (execute.json, work-id issue-458-readiness)

## Task
Add a readiness-check mode to `scripts/install_constellation.py`: one command that answers "is
this project set up to run Constellation" and refuses (nonzero exit, named reason) when it is
not. It reports only — never repairs, never writes `settings.json` at any scope.

## Protected Intent
The check must never give a false "ready" on a project that cannot actually run Constellation,
and must never silently pass on an untested condition. A check that always passes is the exact
defect this work exists to catch — do not let the readiness verdict degrade into that shape.

## Test Mode
TDD strongly preferred (this is a testable, four-item pure-function check plus thin CLI wiring;
no reason to defer tests to after the fact).

## Close Criteria
- Four separately-callable, separately-testable check functions exist, one per readiness item:
  1. **Engine present and runnable** (environment-scoped) — actually imports and runs pytest
     under `sys.executable` specifically (e.g. `[sys.executable, "-m", "pytest", "--version"]`),
     never a bare `python`/`py` shell-out. Discriminating case: `py` on a real box exits nonzero
     with `No module named pytest` and reads exactly like a red suite if only a launch is
     checked — your check must tell "interpreter present but pytest missing" apart from
     "interpreter missing" apart from "both present and working."
  2. **Skills installed and registered** (tree/target-scoped) — `CORPUS.json` / installed
     `constellation-*` folders present and matching what `--agent`/`--scope` would target. Decide
     and justify (in your return) whether this readiness mode requires `--agent`/`--scope` itself
     or stands scope-agnostic ahead of that parsing — this is not resolved for you.
  3. **Hooks wired in a file that ships** (environment-scoped) — reuse the existing
     `detect_hook_wiring`/`describe_hook_wiring` functions, but apply two DISTINCT ships-tests:
     project scope = the wiring file is git-tracked (`git ls-files` membership — presence on disk
     alone is not enough: `.claude/settings.local.json` is gitignored and can be WIRED there while
     the tracked `.claude/settings.json` is not, which must read as NOT ready); user scope has no
     tracked/untracked axis at all (`~/.claude/settings.json` is never part of a repo), so its
     ships-test is simply "is this the file the harness actually reads at runtime."
  4. **Work area present** (tree-scoped) — a `.git` entry at repo root (README.md's own Baseline
     Assumptions: "a Git repo, Markdown docs, and file-based workflow state"). Do NOT require
     `.agent-work/` to already exist — a project ready to *start* using Constellation has not
     necessarily run it yet.
- A thin CLI/report layer on top of the four functions prints a readiness verdict and exits
  nonzero with a named per-item reason when any item fails; exits 0 only when all four pass.
- Unit tests for each of the four functions, including a constructed-unready case for items 1 and
  3 (these are environment-scoped — a fresh clone alone cannot exercise them; see Required
  Evidence for how the fresh-clone check is instead exercised for items 2/4).
- Unit test(s) for the CLI mode's exit-code/refusal behavior (at least one all-pass and one
  refusing case).
- Never repairs anything, never writes `settings.json` at any scope, under any condition.

## Allowed Scope
- `scripts/install_constellation.py` (add the readiness mode/functions).
- `tests/test_install_constellation.py` (or the project's existing test file for this module —
  locate it first; add new tests there, pre-authorized to touch its existing fixtures/harness).
- A new standalone script under `scripts/` ONLY if you conclude, with stated reasons, that the
  separation is worth a second entry point (Pre-Ruling 4 defaults against this; overriding it
  needs a real argument, not just preference).

## Specific Exclusions
- `scripts/checklist_engine.py` and `tests/test_checklist_engine.py` — owned by crew 4 this wave
  (epic #418 wave 5). Do not touch, even incidentally.
- Any `settings.json` file, at any scope, tracked or untracked. Read-only inspection is fine;
  writing is never in scope for this gate.
- `docs/agents/*` — do not promote any observation from this work into doctrine there.

## Constraints
- Report, never repair (README.md's own documented behavior for the existing `--dry-run` hook
  report is the precedent: "It only reports: nothing is written to `settings.json` without the
  opt-in flag").
- Reuse `detect_hook_wiring`/`describe_hook_wiring` rather than re-deriving hook-wiring detection.
- Follow `check_corpus_freshness.py`'s exit-code precedent (distinct codes per verdict, no side
  effects) as the shape to match, not copy verbatim.

## Map Anchors (inbound)
DEGRADED-NO-MAP for this repo (no Cartographer map exists) — no `struct:`/`capability:`/
`decision:` ids to cite. Substitute: `README.md` ("Repo layout vs. installed layout", "Install",
and "Baseline Assumptions" sections) plus the existing `detect_hook_wiring`/`describe_hook_wiring`
functions already in `scripts/install_constellation.py`.
- **Decision:** Pre-Ruling 1 resolves R-vs-#458 toward building the CHECK, not the stronger
  fresh-clone-produces-a-reading fix. `@grade: settled/human · leans launch-order-pre-ruling-1 ·
  settle: n/a — human-authored, frozen`. Do not reopen this.
- **Evidence expectations:** the two claims named in Close Criteria items 1 and 3 above (pytest
  via `sys.executable`; tracked-vs-runtime ships-tests) are exactly what your tests must prove.

## Deliverable Path Check
- **Committed** — `scripts/install_constellation.py` (existing tracked file, edited).
- **Committed** — the test file you add cases to (existing tracked file, edited) or a new tracked
  test file if you split it out — verify with `git check-ignore <path>` exiting 1 before you
  finish, and record the exact command + exit code in your return.
- **Local-only** — none expected; flag if your approach needs one.

## Required Evidence
- Full new-test output for every added test (not a summary — the actual pass lines).
- If any pre-existing test in the touched file fails or changes behavior, name it explicitly and
  say why (do not silently reconcile).
- The exact `git check-ignore` command and exit code proving your edited/added files are tracked.
- State, explicitly, your `--agent`/`--scope` decision for the readiness mode and your one-line
  reason (load-bearing — this is a real open decision point, not confirmatory).

## Wiring Grep
Required. For each new public function/CLI flag you add, one grep showing a call site outside its
own definition and outside any self-test path — e.g.:
```bash
grep -rn "check_readiness\|<your actual new symbol names>" --include=*.py . | grep -v "def " 
```
State the count of external call sites found for each new symbol (the CLI argparse wiring counts
as a call site for the top-level entry function).

## Verification Commands
```bash
python -m pytest tests/ -k readiness -q
```
(Substitute the exact test file/marker you actually use if `-k readiness` doesn't select your new
tests — state the real command you ran in your return.)

## Suggested Model Tier
simple bounded — reason: one well-specified issue with a strong existing precedent
(`detect_hook_wiring`, `check_corpus_freshness.py`) to follow; the hard part is scope discipline,
not technical difficulty (matches the launch order's own budget note).

## Authority
Already decided, do not relitigate: build a CHECK not a repair mechanism (Pre-Ruling 1); never
touch `settings.json` (Pre-Ruling 2); prefer a mode of `install_constellation.py` over a new
script absent a stated reason (Pre-Ruling 4); the four-item list above is the deliverable
(Pre-Ruling 5). Yours to decide, with stated reasons: `--agent`/`--scope` requirement for the new
mode; exact flag name/shape; whether a fifth readiness item belongs (default: it doesn't, absent
a real reason).

## Stop Conditions
Stop and return if: you conclude the standalone-script split is warranted and want it confirmed
before building it that way; a specific exclusion must be touched; required evidence cannot be
produced; you find yourself needing to touch `settings.json` for any reason.

## Return Format
Return IMPLEMENTER_RESULT (write it to
`.agent-work/issue-458-readiness/crew-handoffs/g1-implement-result.json`): completed slice, files
changed, test mode satisfied, evidence produced (full test output, the `git check-ignore`
command+exit code, the wiring grep + call-site counts), assumptions used (including your
`--agent`/`--scope` decision and reason), stop conditions hit (if any), out-of-scope observations,
workflow feedback.
