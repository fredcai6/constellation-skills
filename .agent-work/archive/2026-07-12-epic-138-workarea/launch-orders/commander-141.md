# Launch Order: `commander-141 — issue #141 (hook suite)`

## Mission
Implement https://github.com/fredcai6/constellation-skills/issues/141 — `scripts/hooks/spine_rail.py` + project `settings.json` wiring: the harness-boundary channel of the #138 counter-doctrine (turn-end refusal, post-compaction re-injection). Deliverable: a green, reviewed PR on branch `issue-141`, including the compact-trigger live-probe log.

## Prior-Wave Verdicts (pasted)
From the CONFIRMED #138 design spec (§D3) — three registrations (PreCompact was CUT at critic review: breadcrumb with no consumer is speculative abstraction):

- **Stop** — refuse turn-end while a spine is mid-flight, judging **engine lease/journal truth, never agent claims**. Escape hatch: a 3-strike no-progress nudge counter keyed on (journal-seq, active_id); three consecutive refusals with no journal progress downgrade to a pass-through nudge, so a genuinely stuck agent is never trapped. Engine `block`/`waive` states are honored as honest stops.
- **SessionStart (compact | resume)** — re-inject the live `current` output for the bound spine. The `source=compact` trigger is DOCS-CITED ONLY — live-probe it in this issue (see pre-rulings).
- **PostToolUse on Bash** — maintain the session→spine binding by watching engine invocations. Its job is DISCOVERY only (which spine belongs to this session — Stop cannot cheaply derive this with multiple work areas and concurrent sessions); truth about mid-flight status is always read from the engine state file the binding points at. `release` deletes the binding = the suite's natural off-switch.

From the x2 hooks research (live-probed on this box, current CLI): project-local hooks FIRE for headless `claude -p` (SessionStart, UserPromptSubmit, PreToolUse, Stop, SessionEnd) and for Agent-tool subagents (SubagentStart/SubagentStop; subagent shares parent session_id, gets NO separate SessionStart). Stop CAN block a turn-end and force action on its reason — live-proven, headless included. NOT live-tested: SessionStart source=compact, PreCompact. Probe gotcha: MSYS path mangling on /tmp-style paths — use Windows-native paths in probe configs.

Accepted design costs (spec-settled, do not relitigate): the suite re-encodes "what is terminal" in a second place; Claude-Code-only portability (the engine rail is the only counter on hookless harnesses — that is THE reason the turn-end overlap with the rail exists).

## Pre-Rulings
- If the compact-trigger live probe returns a scoped null (cannot force a compaction / event doesn't fire), SHIP re-injection for `source=resume` only and record the null in the PR + your verdict — do not block the wave on it (Admiral pre-ruling from the latitude contract).
- Live probes run in temp sandboxes (per the x2 method), NEVER against installed skills at `~/.claude/skills` and never leaving artifacts in the repo.
- The hook script judges only engine-journal facts; it never parses agent prose.
- settings.json wiring must work headless — smoke-prove with a `claude -p` run in the sandbox.
- No engine changes in this issue (#140 owns `checklist_engine.py` this wave). If you need an engine-side affordance, float it.

## Honest-Null Clause
A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win.

## Inherited Latitude
You may: implementation-detail decisions inside the constraints; choice of binding-file location/format (document it). You must float: engine changes, anything touching eval task.md, scope changes. Merges are the human's — open the PR, never merge.

## File Ownership
Sole writer of: `scripts/hooks/`, project `settings.json` hook entries, your tests, and `.agent-work/epic-138/verdicts/commander-141.md` (MAIN checkout, absolute path below). Do not touch `scripts/checklist_engine.py` or `skills/` doctrine files.

## Workspace
`C:/Programs/constellation-wt-141` — branch `issue-141`, base commit 93f38505 (main), created via `git worktree add ../constellation-wt-141 -b issue-141 main`.
First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-141` — must exit 0; paste output into your report.
NOTE: PR integration defaults to **server-side merge**.

## Inherited Context
- Windows/py launcher conventions; UTF-8 file writes; `gh pr create -F <tempfile>` for PR bodies.
- Superpowers is a competitor — never cite or import its doctrine.
- Engine reference for journal/lease format: `skills/workbench/references/checklist-engine.md`.

## Pre-empted Steps
Context and plan pre-empted: design confirmed through a full explorer pass (panel + critic review + human confirm). Do not redo design; your understand step is the engine journal format + hook docs + this order.

## Data Locations
- Confirmed spec: `C:/Programs/constellation-skills/.agent-work/archive/2026-07-12-explore-138/DESIGN_SPEC.md`
- Designer-B full design (settings wiring, nudge counter detail): `C:/Programs/constellation-skills/.agent-work/archive/2026-07-12-explore-138/evidence/x1-designer-b.md`
- x2 hooks research (probe method + firing matrix): `C:/Programs/constellation-skills/.agent-work/archive/2026-07-12-explore-138/evidence/x2-hooks-research.md`

## Budget
- **Model tier (required):** opus (hook/refusal logic with subtle failure modes; human-capped at opus or lower).
- **Compute/time, session-window:** target ≤ 75 min including probes. Partial + stop condition over overrun.

## Stop Conditions
Stop and return when: an engine-side change looks necessary, scope exceeded, budget crossed, or context missing — return-and-query the Admiral. Asking up is always sanctioned.

## Return Shape
Verdict + evidence to `C:/Programs/constellation-skills/.agent-work/epic-138/verdicts/commander-141.md`: PR URL, test results (exit codes), probe logs (incl. the compact-trigger result, pass or null), isolation-check output, rulings, triage candidates, workflow feedback. Deliver artifacts **before** going idle.
