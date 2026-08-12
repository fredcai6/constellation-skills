# Launch Order: `commander-gauge — #196 (+ CHECKLIST_SCHEMA verb-doc)`

Commanders start cold. Everything you need is pasted below.

## Mission
Two deliverables in ONE PR:
1. **#196 — Context Governor v2 thresholds as absolute-token caps.** This is the LAST Context Governor issue; closing it lets the epic-#178 umbrella close.
2. **Fix-now doc debt (Admiral-assigned):** document the two engine verbs shipped this epic in `docs/CHECKLIST_SCHEMA.md` — `resume` (unblock after a resolved block; restores pre-block pending/in-progress, refuses cap-escalations) and `amend`'s retext-check op (corrects an in-progress gate's postcondition check TEXT without satisfying the condition; deepcopy all-or-nothing; clears satisfied/waived/attested). These landed in PR #200/#152 but the schema doc (refreshed in #199) predates them.

**Issue #196 (verbatim):**
Current (v1): `gauge_reader._THRESHOLDS` stores per-model `(soft, hard)` FRACTIONS. Because context-rot degradation is absolute-token-driven, those fractions are really an absolute-token cap ÷ that model's window (80K/1M = 0.08 for a 1M model; 90K/200K = 0.45 for a 200K model). Works but fragile: it silently couples the reader's fraction to the writer's `MODEL_WINDOWS`, and a new model/window change needs a hand-recomputed fraction; a wrong/stale fraction mis-trips with no error.
v2: store the intent directly — an absolute-token cap (soft/hard in tokens), and have the reader convert using the model's window (better: have the writer emit `used_tokens` + `window` so the reader/Trip computes `min(fraction_cap, absolute_cap/window)` without a second window table). Then a new model just needs its window (already in `MODEL_WINDOWS`). Deferred because v1 table is correct today (windows fixed #194, fractions #195) — this is maintainability/robustness hardening, not a correctness bug. Also fold the research's open questions as measurement targets (see `.agent-work/epic-178/crew-handoffs/context-rot-research.md`).

## Prior-Wave Verdicts (pasted)
Base `0f354ed` (current main) includes all wave-1/2 merges. #199 refreshed CHECKLIST_SCHEMA.md (your doc target) and #200 added the resume/amend verbs you are documenting.

## Pre-Rulings (overridable with evidence)
- Prefer the "writer emits used_tokens + window; reader/Trip computes min(fraction_cap, absolute_cap/window)" shape if the writer hook can be extended cleanly — it removes the second window table entirely. If that's too invasive, store absolute caps + convert in the reader using MODEL_WINDOWS. Justify your choice.
- Keep v1 behavior numerically equivalent for the current model set (the fractions in #195 are correct today) — this is a refactor to a more robust REPRESENTATION, not a recalibration. Add a test proving the new path yields the same trip points as the current table for the known models.
- The research open-questions fold-in is a comment/doc pointer for future measurement, not code — do not build measurement machinery.
- The CHECKLIST_SCHEMA verb-doc is a separate concern in the same PR; keep it a clean doc addition matching the shipped verbs (read scripts/checklist_engine.py for the exact behavior).

## Honest-Null Clause
A measured negative is a complete deliverable. If the writer already emits enough for the reader to avoid the second table, report that and do the minimal wiring.

## Inherited Latitude
Choose the representation, implement, test, open the PR. FLOAT: any recalibration of the actual trip thresholds (that's a correctness change, surfaced); any new issue; anything outside file ownership. Merge is the Admiral's call.

## File Ownership
Sole writer this wave of: `scripts/gauge_reader.py`, the gauge writer hook if you extend it (`scripts/gauge_writer_hook.py` or equivalent — locate it), `docs/CHECKLIST_SCHEMA.md`, and their tests. Do NOT touch `scripts/checklist_engine.py` (read-only reference for the verb behavior), `scripts/agent_work_root.py`, or any template.

## Workspace
Worktree `C:/Programs/cs-wt-gauge` — branch `feat/gauge-abs-caps-196`, base `0f354ed`. Provisioned via `git worktree add -b feat/gauge-abs-caps-196 C:/Programs/cs-wt-gauge main`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/cs-wt-gauge` → exit 0; paste into report.
PR = server-side merge (Admiral merges).

## Inherited Context
**Windows hazards:** multiline `gh --body` → temp file + `gh pr create -F <file>` (heredoc/`@'...'@` both fail PS 5.1 `--body`; in the Bash/Git-Bash tool `@'...'@` is NOT a commit construct — use a real heredoc or quoted `-m`). Use `py` not `python`. Verify your worktree.
**Active lesson `test-harness-concurrency-failsafe`:** concurrent-file-I/O tests need try/except + stop-signal in `finally` + `daemon=True`.
Read-only reference: `.agent-work/epic-178/crew-handoffs/context-rot-research.md` (main checkout). Run the suite before/after; all pre-existing tests stay green.

## Budget
- **Model tier (required):** opus. Threshold representation with correctness-equivalence stakes on the Context Governor path.
- Checkpoint and return if you near a session limit.

## Stop Conditions
Stop and return when: the change would recalibrate real thresholds (float first); you need uncovered context; or you hit a budget/session limit. Asking up is always sanctioned.

## Return Shape
Report to `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/wave-3/W3-196-REPORT.md` BEFORE going idle: verdict (per deliverable), evidence (equivalence test proving same trip points for known models; verb-doc matches shipped behavior; full suite green), PR URL, map impact, triage candidates, workflow feedback (stage fenced trio, name path), isolation output. Open PR with `gh pr create -F <bodyfile>`; title `feat(governor): absolute-token-cap thresholds + document resume/amend-retext verbs (#196)`. Post verdict, go idle.
