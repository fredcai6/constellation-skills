# Findings — Commander #229 (CI gate: 906-test suite + engine coverage floor + skip-guard)

Working notes. Owner: commander-229. Sole writer.

## PR-7 verify-before-plan (re-confirmed independently, not just cited from the launch order)

1. **`.github/` absent.** `ls .github` / `ls .github/workflows` both exit non-zero
   ("No such file or directory") in the `issue-229` worktree. Confirmed: from-scratch
   build, no partial workflow to reconcile.
2. **Skip-guard target real.** `tests/test_checklist_engine.py:1003-1006`:
   ```python
   def setUp(self):
       import shutil
       if shutil.which("git") is None:
           self.skipTest("git not available")
   ```
   (class `GitChangePolicyCollectorIntegration`, per the launch order.) Confirmed at
   the stated line.
3. **No engine coverage-floor tooling exists.** `scripts/*coverage*` matches only
   `verify_coverage_ledger.py` (corpus removability-ledger coverage — unrelated
   concept, naming collision only, confirmed by reading the file) and
   `verify_issue_set.py` (false positive, doesn't concern code coverage). No
   `pyproject.toml`/`tox.ini`/`Makefile`/`.coveragerc`/`pytest.ini` exists either —
   no coverage config of any kind pre-exists.

All three of the launch order's "Relevant settled history" claims independently
re-confirmed against code. No disagreement to log.

## Test count re-verified (do not cite "906" blindly — Stop Conditions)

`pytest tests/ -q --collect-only` -> **907 tests collected**, not 906. Full run:
`905 passed, 2 skipped, 244 subtests passed in ~30s`. The issue title's "906" is
off by one against the current checkout; using the measured 907 (and noting the
2 pre-existing, expected skips) below rather than the issue's stated figure.

## Pre-existing skips (matters for skip-guard design)

With git present in the working environment, the suite already carries **two**
pre-existing, environment-conditional skips, neither related to git:

```
tests/test_verify_spec_confirmed.py: "issue-58 DESIGN_SPEC.md not present in this
  checkout (untracked artifact)"
tests/test_verify_worktree_isolation.py: "symlink creation not permitted on this
  platform"
```

Design consequence: a naive "any skip fails the build" guard would **always** red
this repo on windows-latest (no Developer Mode / admin -> no symlink perms), which
is a false positive, not the defect the issue names. The skip-guard therefore needs
a **narrow allowlist** of known-expected skip messages, failing on anything outside
it — this is what actually catches the git-integration skip (message "git not
available", not in the allowlist) while not spuriously failing on the two standing
platform skips. Logged as a RULING (scope/engineering-detail latitude, delegated).

## Local environment note (not in scope for #229, informational only)

The `py` launcher in this session resolves to a sandboxed codex-runtime Python with
neither `pytest` nor `coverage` pre-installed; both were `pip install`-ed into that
environment to produce the local evidence below. This is a sandbox artifact of this
particular run, not a repo defect — flagged for awareness only, not fixed here (see
#228's Python-launcher-resolution scope, which this is adjacent to but does not
absorb per PR-8).

## Coverage floor measurement (issue-body command, run verbatim)

```
$ python -m coverage run --include="*/checklist_engine.py" -m pytest tests/test_checklist_engine.py -q
........................................................................ [ 34%]
...................................................... [ 60%]
........................................................................ [ 94%]
...........                                                              [100%]
209 passed, 18 subtests passed in 4.53s

$ python -m coverage report
Name                          Stmts   Miss  Cover
-------------------------------------------------
scripts\checklist_engine.py    1046     95    91%
-------------------------------------------------
TOTAL                          1046     95    91%
```

Measured: **91%**. Floor pinned at **current-minus-1 = 90%**, enforced via
`coverage report --fail-under=90`. Verified both directions:
- `--fail-under=90` -> exit 0 (91 >= 90, current state passes its own floor).
- `--fail-under=92` -> exit 2, "Coverage failure: total of 91 is less than
  fail-under=92" (proves the gate mechanism actually fires non-zero, not just that
  it exists).

Documented limitation (per launch order "Relevant settled history"): this 91%/90%
floor is measured on **this branch's** `checklist_engine.py` (based on pre-#227
`main`). #227 is concurrently rewriting that file; the floor is a wave-0 baseline,
expected to be re-measured after PR-3's batched wave-0 re-verification, not treated
as eternally fixed.

## windows-latest / git-bash pre-check — DOCUMENTED ASSUMPTION, not a measurement

Per PR-2b, this cannot be settled empirically (no Actions run triggered). Citation:
GitHub's `actions/runner-images` repository documents the `windows-latest` image
(currently Windows Server 2022, `windows-2022` label) software manifest as bundling
**Git for Windows**, which ships `git-bash.exe` as part of its standard install —
this has been a stable, documented inclusion across the `windows-2019`/`windows-2022`
runner image manifests for the lifetime of GitHub-hosted Windows runners. Recorded
here as a **documented assumption from GitHub's published runner-image spec**, not
as something this run observed executing.

## Deliverable shape (RULING — delegated, engineering-detail latitude)

- `.github/workflows/ci.yml` — single job, `runs-on: windows-latest`, `shell: bash`
  steps per the repo's POSIX-shell convention (Platform invariants). Three logical
  gates in one job (sequenced, not matrixed): (1) suite + skip-guard, (2) coverage
  floor. Chose one job over multiple to keep the "command set" the wave-1 Commander
  copies as a single unambiguous sequence, per this issue's stated role as the
  literal contract for #232.
- `scripts/verify_skip_guard.py` — small helper script (delegated latitude: "inline
  shell or a small helper script" is explicitly engineering detail the issue leaves
  open). Chosen over inline shell/grep because the skip-guard needs structured
  parsing of JUnit XML skip messages against an allowlist — a POSIX one-liner would
  be fragile/unreadable for this, whereas the repo already has a `scripts/verify_*.py`
  convention (`verify_coverage_ledger.py`, `verify_worktree_isolation.py`,
  `verify_spec_confirmed.py`) this fits into directly.

Named untaken road (design-it-twice, self-authored/single given the bounded,
non-architectural, engineering-detail nature of this call — not panel-dispatched):
candidate B (rejected) — "fail the build on ANY skip, zero-tolerance" — rejected
because it would always red on windows-latest (symlink-permission skip is a standing
platform condition, not a regression), forcing noisy allowlist-by-exception via
workflow edits every time a legitimate new platform skip appears, versus candidate A
(chosen) — an explicit, commented allowlist of expected skip messages, default-deny
otherwise — which isolates exactly the git-integration skip as the one that must
never appear silently. Compared on locality (A: one small file to update per new
legitimate skip vs B: same file) and testability (A: directly unit-testable against
a fixture JUnit report; B: same) — the decisive axis was **correctness under the
actual measured environment** (2 known non-git skips already present), which B fails
today, not hypothetically.

## Plan step: design-it-twice + cold plan critic

**Plan-alternatives (self-authored, single given the bounded/non-architectural
nature — explicit named untaken road, not a silent skip):**
- Candidate A (chosen): one crew gate (implement -> review -> integrate) covers
  authoring both files AND producing all three PR-2b proof transcripts.
- Candidate B (untaken road): split into gate1 = author files, gate2 = produce
  proofs. Rejected: for a 2-file, low-ambiguity mechanical change, splitting adds a
  full extra implement/review/integrate cycle (cost) without a real checkpoint
  benefit — nothing meaningfully changes between "files exist" and "proofs pass" that
  a human/Admiral would want to gate on separately. Logged as RULING.

**Cold plan critic (dispatched: one sonnet subagent, mission-frame + plan only, no
author context) — findings and disposition:**

1. [intent-fit] Skip-guard allowlist keyed on message text alone is spoofable (a
   future test could reuse an allowed message string to sneak past the guard).
   **DISPOSITION: FIX (accepted).** execute.json g1-implement amended to require the
   allowlist key on (classname, test name) nodeid AND message together, not message
   alone.
2. [intent-fit] Coverage command (`tests/test_checklist_engine.py` only) may
   understate true coverage of `checklist_engine.py`, since 6 other test files also
   reference it (`test_spine_provenance_check.py`, `test_spine_rail.py`,
   `test_install_constellation.py`, `test_explorer_templates.py`,
   `test_feedback_tooling.py`, `test_curate_corpus.py` — confirmed by grep).
   **DISPOSITION: DOCUMENTED LIMITATION, not a redesign.** The coverage command is
   dictated verbatim by the issue body itself (not this Commander's design choice) —
   deviating from it would break the "exact command set #232 copies verbatim"
   contract this issue exists to produce. Recorded as a caveat: the 90% floor is a
   conservative lower bound against a narrow test-file scope, not the true
   full-suite coverage of that module.
3. [testability] Coverage guard's local proof was a happy-path readout only (showed
   the passing number, never showed `--fail-under` actually firing red).
   **DISPOSITION: FIX (accepted) — already independently satisfied.** This
   Commander's own investigation (above) already ran `--fail-under=92` and observed
   exit 2 ("Coverage failure: total of 91 is less than fail-under=92"), proving the
   gate fires both directions. execute.json now requires this same two-direction
   proof from the implementer's own local evidence too.
4. [testability] Git-less proof must not be a hand-fabricated junit.xml fixture; it
   must be a real PATH-stripped child pytest run that trips the real `skipTest`.
   **DISPOSITION: FIX (accepted).** execute.json g1-implement now says this
   explicitly, citing lesson:verify-harness-field-and-drive-real-writer by name.
5. [simplicity] Running the suite twice (full suite + narrow coverage run) is
   duplicate work / root cause of #2. **DISPOSITION: NOT TAKEN**, same reasoning as
   #2 — the two commands are the issue's own two distinct gates (suite pass/fail vs.
   coverage measurement), not an accidental duplication this Commander introduced.
6. [simplicity/process] Bundling authoring + all 3 proofs into one gate risks the
   harder proofs (3, 4) being satisfied by a shortcut. **DISPOSITION: MITIGATED, not
   split.** execute.json's g1-implement imperative now states the fault-injection
   requirement explicitly and specifically per proof, and g1-review's close criteria
   requires the reviewer to confirm each proof used real fault injection, not a
   readout or fixture — closes the gap without paying for a second gate.

Critic's overall verdict: PROCEED WITH FIXES. Disposition: proceeded, with fixes 1,
3, 4 applied to the plan; 2 and 5 documented as accepted limitations tied to the
issue's own mandated command, not redesigned.
