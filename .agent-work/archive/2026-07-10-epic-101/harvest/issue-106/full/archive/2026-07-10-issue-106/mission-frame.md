# Mission Frame — issue #106 (autonomous eval harness)

## Intent
Ship a repo tool (`scripts/run_skill_eval.py` + `evals/` + agent-free `tests/`) that runs a real constellation workflow headlessly against a fixture repo and judges it on **process discipline** (engine spine completed, artifacts present, tests green) over N-of-M runs — the substitute signal for downstream project failures that never flow back here.

**Map note:** this is a **greenfield** area with no packet map (no `docs/architecture/`, no `evals/`, no `scripts/run_skill_eval.py`). Frame is deliberately map-light; structural authority is the issue #106 spec + the frozen launch order. No stale/disputed map to guard against.

## Affected Capabilities
- **Corpus eval (NEW):** autonomous, process-first evaluation of the post-cleanup skills corpus. Did not exist; this run creates it.
- **Crew launch mechanics (RELIED ON, not changed):** `scripts/run_crew.py::build_crew_argv` — the current claude-CLI headless form (`claude -p "<prompt>" [--model X]`; #91). The runner reuses this launch shape; it does not modify run_crew.py.

## Structural Anchors
- `scripts/run_skill_eval.py` — NEW, top-level script (file level). The runner.
- `evals/<name>/` — NEW scenario dirs (fixture setup + task prompt + checks + README).
- `tests/test_run_skill_eval.py` — NEW, agent-free unit layer (file level).
- `scripts/install_constellation.py` — RELIED ON: the temp-install mechanism (skills installed to a temp target). Read, not modified.
- `scripts/run_crew.py` — RELIED ON: `build_crew_argv` launch form + result-freshness pattern. Read, not modified.

## Governing Constraints / Assumptions
- constraint: repo tool, NOT a skill (skill wrapper fails the deletion test) — no `skills/eval-*`, no SKILL.md, no bundle-map entries.
- constraint: nothing gates on evals; the runner never launches agents from default pytest collection.
- constraint (T3): process checks carry the verdict; answer-correctness weak, NEVER sufficient.
- constraint (T4): N-of-M contractual; single-run verdicts disallowed.
- constraint: source repo is authority; never edit installed copies; temp-installs under system temp / gitignored, never committed.
- assumption: headless `claude -p` works this session (verified: exit 0 on a trivial prompt) — but a full workflow run may still hit usage limits; honest-null path armed.

## Decision Anchors & Decision Pressure
- decision (forced, mine by latitude, via G1 design-it-twice): the runner contract — scenario schema, checks-as-plain-scripts vs DSL, temp-install mechanics, headless launch mechanics, N/M defaults.
- decision (forced, mine): gate structure / tests-to-code coupling — see plan-alternatives (converged to Candidate B).
- decision pressure → Admiral only if: any urge to gate on evals, a skill wrapper, touching install bundles, or a contract needing repo-wide changes.

## Claims / Evidence Surfaces
- claim: "the harness guards the post-cleanup corpus" — re-confirmed by a live pilot run whose process checks pass on the known-good corpus (acceptance) AND fail on a deliberately-broken variant (falsification).
- claim: "runner logic is correct independent of agents" — re-confirmed by the agent-free unit layer (green, launches no agent).

## Map Confidence / Staleness / Disputes
None to guard — greenfield. No gate authored on an unverified map.

## Out of Scope
- The delegated-commander selection scenario (F's first non-Euler pilot) — documented as the named next scenario in `evals/README.md`, not built.
- Any edit to other skills' content, `_shared/`, `docs/ROADMAP.md`, install bundles, or `run_crew.py`.
- Windows CI parity execution and per-role token-cost measurement (deferred to later drills per the epic testing-pathways section).
