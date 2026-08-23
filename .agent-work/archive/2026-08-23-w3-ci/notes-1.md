# Commander notes — w3-ci

## understand (reconciled against LAUNCH_ORDER, delegated mode — no reachable human)

**Baseline verification.** Read `.github/workflows/ci.yml` at `135c34eb` (current `git log -1` HEAD,
matches the launch order's declared base commit). Confirmed exactly as the order describes:
- Single `test` job, `runs-on: windows-latest`, `defaults.run.shell: bash`.
- Triggers: `on: push: branches:[main]` and `on: pull_request` (no ref filter) — so GitHub
  already checks out `refs/pull/N/merge` for PR runs, per the order's pasted measurement.
- No `ubuntu-latest` job exists anywhere in the workflow. No matrix. One job only.

No discrepancy between the order's assumed baseline and the actual code — the headline mechanism
(a Linux job) is genuinely absent, not already shipped under a different name. Proceeding under
the order as written.

**Problem statement.** Add one `ubuntu-latest` job to `.github/workflows/ci.yml` that runs the
same suite the Windows job runs (full `pytest tests/`, skip guard, coverage floor — the parts that
are platform-portable), so that CI carries a signal that can actually be trusted instead of one
that is red on autocrlf/temp-path Windows-only bugs on 12/12 recent runs. Do not touch triggers,
do not restructure the workflow, do not fix or disable the Windows job. Prove the new job can go
red (decision:prove-it-can-go-red) via the cheapest honest local equivalent if a scratch-branch
CI-triggered red-proof is impractical — float that substitution rather than deciding it silently,
since the order marks it `guess/admiral`.

**Scope confirmed:** `.github/workflows/ci.yml` only. This is a single-file, mechanical CI change;
map orientation was DEGRADED-UNPARSEABLE (map covers Python packages, not workflow YAML) and was
discharged at `context` rather than treated as blocking — the map has nothing to say about a CI
workflow file.

No gap found that needs floating to the Admiral at this step.

## triage

One candidate, surfaced by the reviewer at g1-review and independently confirmed by the
Commander (see REPLAN_INPUT.json discrepancy `w3-ci-stale-skip-pin`):

**Candidate:** `scripts/verify_skip_guard.py` refuses (exit 1) on a fresh full-suite run at this
repo's current HEAD (135c34eb) -- 8 skips fail the documented allow-tuple, 3 of them explicitly
pinned to a stale revision (9d5aac6daa58a72fc6a665cb39879ee5705f7f71,
`tests/test_checklist_engine.py::CommanderSpineBasisFields`). This means the new `test-linux`
job's mirrored "Skip guard" step will itself go red on its first real CI run, for a reason
unrelated to any regression -- directly working against this mission's own point (a red CI that
means something).

**Disposition: recommend-and-defer.** Not `fixed-now`: it is outside this run's file ownership
(`.github/workflows/ci.yml` only) and outside inherited latitude (`decision:ci-changes-beyond-
this-are-surfaced` forecloses unrelated CI-adjacent changes; the fix also requires domain
verification of `checklist_engine.py`'s template shape at current HEAD, which is a different
subsystem than this mission). Not `filed`: opening a GitHub issue is a repo action this run was
not asked to take, and delegated-mode authority for issue creation is satisfied by citing the
launch order's Inherited Latitude, which does not name issue-filing as delegated. Recorded here
and flagged prominently in RESULT.md for the Admiral's disposition.

User-decision: recommend-and-defer citation LAUNCH_ORDER:Inherited Latitude (issue-filing not
delegated to this Commander; deferred to the Admiral, not silently filed).
