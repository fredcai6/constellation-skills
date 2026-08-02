# Launch Order (implementer): `impl-659-660 — Frozen constant module`

Right-sized dispatch: small, bounded, values already ratified — an implementer-with-plan, not a full Commander. The HITL part of #660 (owner picks values) is DONE; this is the AFK build.

## Mission
Build issue **#660** (epic #659, manifest id `A`): the named, versioned frozen-constant module holding the epic's pre-registered thresholds, mirroring `src/physics/layer2/mixture_stability.py`'s constant style (`LOG_RADIUS_SCALE` etc.). The **values are ratified and fixed** — do NOT choose or fit any value; use exactly the RATIFIED SET.

## The RATIFIED SET (owner-frozen 2026-07-25 — copy verbatim, with each rationale line)
Read `.agent-work/epic-659/660-constant-menu.md` → the "RATIFIED SET — Fred, 2026-07-25 (freeze v1)" table is your exact spec. In brief:
- `CORNER_CURVATURE_THRESHOLD = 0.005` (1/m; radius ≤ 200 m ⇒ corner)
- `BRAKING_ONSET_QUANTILE = 0.10`
- `MIN_SEGMENT_LENGTH_M = 5.0`
- `MAP_STABILITY_DRIFT_M = 10.0`
- `SECTOR_CALIB_COVERAGE_NOMINAL = 0.90`, `SECTOR_CALIB_COVERAGE_OBSERVED_MIN = 0.85`, `SECTOR_CALIB_GROSS_MISCALIB_BOUND = 0.50`
Each carries its one-line rationale from the table + the freeze date/author. **Do NOT invent extra constants.**

## Pre-Rulings
- decision:corner-gate-is-curvature — the corner/straight gate is CURVATURE (0.005), not lateral-g (owner-approved reframe of spec §1). Lateral-g stays the severity descriptor elsewhere; this module does not define a lateral-g gate.
  @grade: settled/human
- decision:not-validated-wording — the `CORNER_CURVATURE_THRESHOLD` rationale must say "inherited from #625's pre-existing `straight_curvature_threshold`, NOT independently proven as the corner/straight gate; carried pending the map typing spot-checks + stability gate." Do NOT write "validated."
  @grade: settled/human
- decision:no-duplicate-005 — `0.005` already exists as `physics_config.straight_curvature_threshold`. Do NOT introduce a second literal `0.005`. Make the frozen module reference/re-export the existing source (single source of truth) OR document the canonical source explicitly — pick the LOWER-blast-radius option and note which; if honoring this would require editing many call sites across the repo, STOP and float to the Admiral rather than doing a wide refactor.
  @grade: guess · leans acceptance · settle: check how many sites read straight_curvature_threshold; if just segment_classifier, reference is cheap
- decision:replication-deferred — do NOT add any `REPLICATION_*` constant. That set is deferred to a #668 pre-registration and added later. Leave a clearly-marked docstring stub noting the deferral, nothing more.
  @grade: settled/human
- decision:discipline-docstring — module docstring states: changing any value requires a NEW named constant set + full re-derivation/re-run, never a silent edit.
  @grade: settled/human
- decision:unit-discipline — every value in explicit SI units with g-conversion documented where relevant (`GRAVITY_MS2` exists); closes the #639 undocumented-`a_lateral`-unit trap at the source.
  @grade: settled/human

## Acceptance
- The module exists with exactly the ratified set + rationale + freeze date/author + discipline docstring.
- A test asserts no epic-659 consumer defines its own copy of a frozen threshold (no literals at call sites). Since epic-659 has no consumers yet, this test guards the future; scope its literal-scan to the epic's source paths and make it pass trivially now but catch a future duplicate. Also assert the `0.005` collision is handled per the no-duplicate ruling (one source).
- `py -m pytest` for the new test green; `py -m src.utils.simplification_limits` on touched paths clean.

## Workspace
Worktree: **`C:/Programs/f1brainz-wt/epic659-660`** · branch `epic659/660-frozen-constants` · base `f404d2cb`.
First step: `py C:/Users/fredc/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here C:/Programs/f1brainz-wt/epic659-660` → exit 0, paste output.
PR = server-side merge (do not local-merge). Windows: `py` launcher; `gh pr create -F <tempfile>` (never a heredoc body). Do NOT commit any `.agent-work/` path on the branch. Editable-.pth trap: prefer pytest. Model tier: **Sonnet**.

## Return Shape
Verdict (built + test green) + evidence (test output, `simplification_limits` result, which no-duplicate-0.005 option you took) + module path + triage candidates + `verify_worktree_isolation.py --here` matched path. Open the PR, post the verdict; the Admiral gates+reviews+merges. Deliver artifact + post verdict before idling. Float to the Admiral if the no-duplicate ruling would force a wide refactor.
