# Plan Alternatives — w3-ci

## Panel-vs-single: neither run (skipped)

Design-it-twice (plan-alternatives) and the cold plan critic were both skipped as named untaken
roads. See `spine.json`'s `plan` gate evidence for `c4`/`c5` attestations.

**Reason.** The launch order's pre-ruling `decision:add-one-job-only`
(`@grade: settled/human · leans g1-implement`) already forecloses the structural question: add a
single `ubuntu-latest` job, do not restructure the workflow, do not add a matrix unless it is
genuinely the smallest expression, do not touch triggers. The only latitude actually delegated to
this Commander (`Inherited Latitude`: Python version, step layout, caching, naming, matrix-vs-
second-job) is cosmetic on a ~15-line YAML diff that largely mirrors the existing `windows-latest`
job's steps. There is no load-bearing interface, no seam placement choice, and no depth/locality
tradeoff for a parallel candidate panel to usefully compare.

**Untaken road, stated plainly:** a 2-candidate (or panel) comparison of "second job" vs "matrix
strategy" vs "reusable workflow" shapes was not run. If a future CI change in this repo is less
constrained by a settled pre-ruling, that comparison should run then.

## Recommendation (single path, no convergence needed)

Add one `ubuntu-latest` job to `.github/workflows/ci.yml`, structured to mirror the existing
`windows-latest` job's steps (checkout, setup-python 3.12, install deps, run the same test/skip-
guard/coverage-floor commands), with `shell: bash` as ubuntu's own default (no `defaults.run.shell`
override needed the way Windows requires one). This satisfies `decision:add-one-job-only` as
written.
