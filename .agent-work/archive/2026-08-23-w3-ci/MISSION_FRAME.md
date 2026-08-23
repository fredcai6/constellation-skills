# Mission Frame

**Shrunk to a substitute-only frame — no code map exists for this run.** Map orientation at
`context` came back DEGRADED-UNPARSEABLE (`map/INDEX.md` has content but no citable anchor id;
`docs/architecture` is empty) and was discharged with the substitute `docs/agents/AGENT_GUIDE.md`
(see `.agent-work/w3-ci/map-orientation.json`).

## Intent
Add one `ubuntu-latest` job to `.github/workflows/ci.yml` so CI carries a Linux signal that is not
red on 100% of recent runs for Windows-only bugs (autocrlf `git apply`, Windows temp-path
failures). The `pull_request` trigger already checks out the merge ref, so this restores an
existing signal rather than building new machinery.

## Structural Anchors
Per `docs/agents/AGENT_GUIDE.md`, the repo's agent-facing entrypoint: this run touches
`.github/workflows/ci.yml` only, a CI configuration file outside the Python-package surface that
`docs/agents/AGENT_GUIDE.md` and the code map (`map/INDEX.md`) describe. No package/module
structural anchor applies.

## Out of Scope
Everything `docs/agents/AGENT_GUIDE.md` describes as the Python package surface
(`conftest`/`evals`/`examples`/`scripts`/`skills`/`tests`) is untouched. The `windows-latest` job,
workflow triggers, branch protection, and required checks stay untouched per the launch order's
pre-rulings.
