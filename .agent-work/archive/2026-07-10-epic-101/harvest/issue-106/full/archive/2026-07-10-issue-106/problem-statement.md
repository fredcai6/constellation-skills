# Problem statement — issue #106 (Cluster E: autonomous eval harness)

## The ask, reconciled against the frozen launch order
Build a **repo tool** (not a skill — a skill wrapper fails the deletion test) that autonomously eval-tests the constellation skills corpus by running real constellation workflows end to end and judging them on **process** discipline, not answer-correctness. Downstream project failures (f1brainz) do not flow back here, so autonomous scenario runs are the substitute signal.

Five deliverable classes, each its own execute gate (launch-order "one execute gate per deliverable class"):
1. **Runner-contract design gate** (the spec's named deferred decision — run FIRST, design-it-twice): scenario schema, checks as plain scripts vs a DSL (spec leans plain), temp-install mechanics, headless-agent launch mechanics, N-of-M defaults. 3 alternatives on depth/locality/seam/testability; record; pick; proceed. Float to Admiral only on a genuine tie or out-of-scope machinery.
2. **Runner** `scripts/run_skill_eval.py`: temp-installs candidate skills from the worktree to a TEMP target, launches fresh headless agents on a scenario (reuse `run_crew.py`'s `build_crew_argv` launch form: `claude -p "<prompt>" [--model X]`), then executes the scenario's checks itself. Check hierarchy is contractual (T3): **process checks carry the verdict** (spine JSON completed its steps, expected artifacts present, tests written+green); answer-correctness is weak, NEVER sufficient. N-of-M (T4): each scenario runs N times with a pass-rate threshold; single-run verdicts disallowed. Pilot defaults small+justified (e.g. 2-of-3).
3. **Pilot scenarios** `evals/<name>/`: 2–3 Project Euler scenarios at graded difficulty — fixture-repo setup + task prompt driving a real constellation workflow + mechanical checks. Transcripts kept for diagnosis, never judged.
4. **Agent-free unit-test layer** `tests/test_run_skill_eval.py`: runner's own logic (schema parse, check execution, verdict/N-of-M math) on canned fixtures — must NOT launch agents, never wired into default pytest collection in a way that launches agents.
5. **Bar documentation** + **live acceptance**: situational bar documented in `evals/README.md`; ONE pilot scenario executed for real through the runner, N-of-M, verdict + process-check outputs pasted, plus falsification (a deliberately-broken variant must fail its process checks). Honest-null path if environment blocks live runs.

## Dispositioned decisions (NOT re-litigable — pre-rulings)
- Repo tool, not a skill: no `skills/eval-*`, no SKILL.md, no bundle-map entries.
- Nothing gates on evals; runner never launches agents from default suite collection.
- Process checks carry the verdict; answer-correctness weak-never-sufficient; N-of-M contractual (T3/T4).
- Transcripts kept for diagnosis, never judged by the runner.
- Source repo is authority; never edit installed copies; temp-installs under system temp / gitignored, never committed.
- The delegated-commander selection scenario (F's first non-Euler pilot) is OUT of scope — document as named next scenario only.

## My inherited latitude (decide without floating)
Runner-contract winner (via design-it-twice), scenario schema, N/M defaults (justified), Euler problem choices, dry-run design.

## Float to Admiral only if
Any urge to gate on evals, a skill wrapper, touching install bundles, or a runner contract needing repo-wide changes; or design candidates genuinely tie.

## Map confidence
Greenfield area (no `evals/`, no `scripts/run_skill_eval.py`, no packet map). Structural authority = issue #106 spec + launch order. No stale/disputed map to guard against; mission frame will be map-light and say so.

## Environment probe (feasibility, done at understand)
`claude --version` = 2.1.205 (Claude Code); `claude -p "Reply with exactly: OK"` returned `OK`, exit 0. Headless CLI works — live acceptance is feasible in principle this session, budget permitting (≤ ~6 agent-sessions; pilots one model tier down). Honest-null path armed if full workflow runs prove infeasible.
