# Launch Order: `commander-140 — issue #140 (engine rail)`

## Mission
Implement https://github.com/fredcai6/constellation-skills/issues/140 — one function `_rail(point, cl)` in `scripts/checklist_engine.py` appending a doctrine block to `claim`, `current`, `start`, `advance`, `attest`, `attach`, and REFUSED responses. This is channel A of the #138 counter-doctrine: engine-carried doctrine at every decision point so cheap models finish honestly. Deliverable: a green, reviewed PR on branch `issue-140`.

## Prior-Wave Verdicts (pasted)
From the CONFIRMED #138 design spec (§D2), the five strings — USE VERBATIM, single table, flat register:

| Decision point | Rail string |
|---|---|
| early (entry/first steps) | "Work the engine never saw did not happen. Run the step's checks, then `attest` and `advance <id>`." |
| mid-flight | "A working solution is the MIDDLE of this run — you are N steps from done. Next: <imperative>. Run it." |
| check-FAILURE | "This check failed; that verdict is scoped to this check, not the approach. Do the missing work and `attest`/`attach` the evidence, or escalate with `block`/`waive` and a reason. Report 'this check failed', never 'this step is impossible'. Quiet abandonment and fabricated evidence are the two forbidden exits." |
| near-terminal | "The finish is a sequence, not an announcement. Final `advance` first, then `release` — the journal, not your prose, is the proof." |
| terminal | "Release is your last journaled action. Run `release`; do not claim it." |

Design constraints (spec-settled, do not relitigate):
- Gate tokens (position, distance-to-terminal, next imperative) derive from existing `items` state — EXCEPT check-FAILURE, which keys on the `EngineError` refusal path in `main()`: after a failed `advance` the spine state is identical to plain mid-flight, so the refusal event is the only deterministic trigger. Unit-test it by invoking a failing verb.
- Boundaries: near-terminal = active step is the last step before release-eligibility; terminal = only `release` remains.
- No new verbs, no schema/journal changes, no per-step authored text, no rail on read-only verbs other than `current`.
- Canonicality note in the string table's docstring: this table is the canonical enforcement source; `_shared/global-everyone.md` elaborates and cites it; on conflict the table wins.
- Tone is research-settled (x3): flat imperative at the decision point, one plain consequence clause, NO all-caps/exclamatory — placement beats typography; caps is a variance risk on small models.

## Pre-Rulings
- Strings verbatim from the table above; if implementation truly forces a wording change, STOP and float it (spec-frozen text is a measurement precondition for #145).
- The rail block should be short and structurally set off (e.g. a leading marker) so it reads as instruction, not narration.
- Every skill's spine templates ride the same engine — no template changes in this issue.

## Honest-Null Clause
A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win.

## Inherited Latitude
You may: make implementation-detail decisions inside the constraints above; fix-now bounded defects you trip over in the engine (logged in your report). You must float: any wording deviation, any schema/verb change, anything touching eval task.md files (pre-ruled untouchable), scope changes. Merges are the human's — open the PR, never merge.

## File Ownership
Sole writer of: `scripts/checklist_engine.py` (this wave), your tests, and `.agent-work/epic-138/verdicts/commander-140.md` (in the MAIN checkout, absolute path below). Do not touch `skills/` doctrine files (commander-142's territory) or `scripts/hooks/` (commander-141's).

## Workspace
`C:/Programs/constellation-wt-140` — branch `issue-140`, base commit 93f38505 (main), created via `git worktree add ../constellation-wt-140 -b issue-140 main`.
First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-140` — it must exit 0. Paste its output into your return report.
NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself).

## Inherited Context
- Windows/py launcher conventions: run engine/scripts with `py`; write files UTF-8; `gh pr create -F <tempfile>` for PR bodies (never heredoc/here-string `--body`).
- Superpowers is a competitor — never cite or import its doctrine.
- Engine reference: `skills/workbench/references/checklist-engine.md` (in your worktree).
- The engine has an existing test suite — find it, keep it green, extend it.

## Pre-empted Steps
Context and plan are pre-empted by this order: the design was confirmed through a full explorer pass (3-designer panel, 3-lens critic review, human confirm). Cite this order; do not redo design. Your understand step is reading the engine code + this order.

## Data Locations
- Confirmed spec (untracked, main checkout): `C:/Programs/constellation-skills/.agent-work/archive/2026-07-12-explore-138/DESIGN_SPEC.md`
- Designer-A design doc (rationale detail): `C:/Programs/constellation-skills/.agent-work/archive/2026-07-12-explore-138/evidence/x1-designer-a.md`

## Budget
- **Model tier (required):** opus (engine logic with subtle failure modes; human-capped at opus or lower).
- **Compute/time, session-window:** target ≤ 60 min. Report partial + stop condition rather than overrun.

## Stop Conditions
Stop and return when: scope exceeded (schema/verb change needed), a wording deviation seems necessary, budget crossed, or you need context this order lacks — return-and-query the Admiral. Asking up is always sanctioned.

## Return Shape
Verdict + evidence to `C:/Programs/constellation-skills/.agent-work/epic-138/verdicts/commander-140.md`: PR URL, test results pasted (exit codes), the isolation-check output, any fix-now rulings, triage candidates, workflow feedback. Write your result artifact and send your verdict **before** going idle — the Admiral judges completion from artifacts, not from a message that may drop.
