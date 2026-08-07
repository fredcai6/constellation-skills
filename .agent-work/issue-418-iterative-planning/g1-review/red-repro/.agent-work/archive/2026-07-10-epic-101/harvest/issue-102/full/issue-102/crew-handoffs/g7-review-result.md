# Review Result

## Assigned Gate
`g7-review` (issue #102, Move 11 — regression net)

## Result
`APPROVE`

## Handoff compliance
The two required tests are present in `tests/test_install_constellation.py` and do what the handoff asked:
- `test_relocated_doctrine_pins_ship_to_installed_destination` — installs explorer/commander/lessons-auditor to a temp dest and content-pins each relocated doctrine on its correct installed destination.
- `test_relocated_doctrine_leaves_no_residual_in_carrier_skill_md` — globs source `skills/**/SKILL.md` only, asserts each retired signature absent, with the move-9 residual scoped to `admiral/SKILL.md`.

Both pass (2 passed, 106 subtests). No production `skills/` file was edited by the implementer — diff is `tests/test_install_constellation.py` only, +80 additions.

## Scope drift
`git status --porcelain` shows exactly one modified file: `tests/test_install_constellation.py` (additions only). No production `skills/` edit, no new `global-*.md`, no other files. My own falsification edits to `_shared/global-everyone.md` and `commander/SKILL.md` were each `git restore`d and the tree re-verified clean.

## Evidence verdict
Independently reproduced, not accepted on claim:
- Full suite `py -m pytest tests/ -q` → **444 passed, 2 skipped, 132 subtests in 11.72s** (matches IMPLEMENTER_RESULT's 444).
- Signature source-of-truth greps: 5/5 everyone sigs in `_shared/global-everyone.md`; `Design-it-twice` / `Unchanged-tree shortcut` / `Idle subagent adjudication` at `_shared/global-orchestrator.md` lines 52/89/98; `forks its identity` at `lessons-auditor/SKILL.md:22`.
- Bucket map cross-checked against `install_constellation.py:98-113`.

## Code/doc quality
Tests model the existing content-pin mechanism faithfully: real install to a temp dest, then read the bundled `references/*.md` (not the source), which exercises the reference-bundle relocation end-to-end. Comments document each move→signature→destination mapping and the move-9 exception clearly.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the regression net locks the move 1-10 relocations (reconciled in prior gates) against future regression; suite reproduced green.
- **Constraints not violated:** Yes — no new `global-*.md`, residual SKILL.md-only, move-9 admiral-scoped, canonical `_shared` untouched.
- **Notes match the diff:** Yes — additions-only test file; no structural/capability surface added.
- **Decision candidates surfaced:** N/A — test-only.
- **Durable context routed:** N/A — no new durable context.

## Per-check findings (engine survey, all pass)
- **r4a — correct-tier destinations:** everyone moves (1,2,4,5,8) asserted on explorer's `references/global-everyone.md` (explorer is `_GLOBAL_ORCHESTRATOR`, which carries `global-everyone.md` — a valid "any installed skill" stand-in); orchestrator moves 6,7 + move-10 canonical asserted on **commander's** `global-orchestrator.md` (correct orchestrator tier, NOT a crew skill that lacks the bucket); move 9 asserted on `lessons-auditor/SKILL.md` (its single home). No orchestrator signature is asserted against any `global-everyone.md`. Correct-tier throughout.
- **r4b — residual scoping:** globs `ROOT/skills/**/SKILL.md`, SKILL.md bodies only; every `references/` file (bundled `_shared` copies + retained role refs `checklist-engine.md`, prototyper `measurement/ui.md`, admiral `fleet-doctrine.md`) is excluded. Move-9 residual (`breaks recurrence counting`) scoped to `admiral/SKILL.md` alone — an absence-sentinel (that phrasing exists nowhere now; it reds only if admiral's pre-trim rationale is restored), correctly paired with the `forks its identity` content-pin on the lessons-auditor home. Narrow but valid; noted, not blocked.
- **r4c — no new global, suite green:** confirmed.
- **r4d, r4e — executed falsifications:** see below.

## Executed falsification results (REQUIRED — both performed)
**(a) content-pin class →** Mutated the `reporting misfit is compliance` line in `skills/_shared/global-everyone.md` to `reporting misfit is XXXREDACTEDXXX`. Ran the content-pin test → **RED**:
`SUBFAILED(bucket='global-everyone', sig='reporting misfit is compliance')` — `AssertionError: 'reporting misfit is compliance' not found in ...` at `test_install_constellation.py:718`. Then `git restore skills/_shared/global-everyone.md`; tree re-verified (only tests modified). The content-pin genuinely reds on doctrine loss — not vacuous.

**(b) residual class →** Appended the banner `FOLLOW THIS SKILL STRICTLY` to `skills/commander/SKILL.md`. Ran the residual test → **RED**:
`SUBFAILED(sig='FOLLOW THIS SKILL STRICTLY', skill='commander')` — `AssertionError: 'FOLLOW THIS SKILL STRICTLY' unexpectedly found in ...` at `test_install_constellation.py:762`. Then `git restore skills/commander/SKILL.md`; tree re-verified (only tests modified). The residual test genuinely reds on a retired-inline reappearance — not vacuous.

Both falsifications restored; final `git status --porcelain` = only `tests/test_install_constellation.py`, `skills/` clean.

## Reconciliation check
No divergence for Commander to reconcile. Test-only regression net over already-reconciled relocations; no docs/contracts/structural baseline concern.

## Blockers
- None.

## Out-of-scope observations
- None. (The move-9 residual being a narrow absence-sentinel rather than a symmetric present/absent guard is by design and flagged in the handoff; not a defect.)

## Workflow Feedback
- **Handoff gaps:** none — the handoff was precise: it named the exact two falsifications, the bucket-map line range (`install_constellation.py:98-113`), and the move-9 sentinel caveat, which let me verify destinations without rediscovery.
- **Context rediscovered:** The installer lives at `scripts/install_constellation.py`, not repo root; the handoff cited "install_constellation.py:98-113" without the `scripts/` prefix, and the test's `INSTALLER`/`ROOT` helpers resolve it. Minor — one `find` resolved it. Worth prefixing the path in future handoffs.
- **Instructions improvised around:** The reviewer template's `config_ref` points at `docs/agents/engine-config.json`, which does not exist in this skill-source repo (no `docs/agents/`). I followed the prior g6-review precedent (same absent config) and drove the survey through the engine anyway; the engine did not require the config to be present. Also, the engine's `current` verb rejects `--session-id` (unlike record/consolidate) — cosmetic inconsistency, no impact.
- **What would have made this easier:** Prefix installer/source paths with their real repo location (`scripts/…`) in the handoff.

## Return status
`complete`
