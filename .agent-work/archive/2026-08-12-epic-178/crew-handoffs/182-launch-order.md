# Launch Order: implementer — issue #182 (Trip: two-band gate policy) — Wave 1

You are an implementer dispatched by the Admiral running epic-178 (Context Governor v1). You start cold; everything you need is pasted here. Do NOT open other issues. #179 and #181 are already MERGED to main — build on them as they actually shipped (below).

## Mission
Implement issue #182 — the Trip two-band gate policy (Module 3): the engine, at each gate boundary, reads the gauge (via #181's reader) and applies model-keyed thresholds. Deliverable: the policy wired into `scripts/checklist_engine.py`, fixture-based unit tests to green, a PR, and a result artifact.

## Prior-Wave Verdicts (pasted — real merged interfaces)

**From #179 (MERGED, in `scripts/checklist_engine.py`):**
- `has_pending_refresh_request(cl, gate)` — a pure predicate (bool), no side effects. "Pending" = a `refresh-request` evidence item present and NOT superseded. It does NOT yet mark a request *fulfilled* (no `fulfilled` field) — that's #183's concern, not yours.
- `refresh-request` is an evidence type carried by the existing `attach` verb; payload is pointers only (`seam`, `why_ref`).
- `current` render includes a `DIGEST:` line (latest non-mechanical why) and a `REFRESH REQUESTED:` line when a pending refresh-request exists for the active gate. Both ride the read-only `current` output for gated checklists, before the doctrine rail.
- `advance` now solicits a `--why`/`--mechanical` on non-exempt gates and checks postconditions BEFORE the why. Study how the advance path and the `current` render are structured; your SOFT/HARD logic hooks the same gate-boundary path.
- `why_trail` is a top-level append-only list; per-task `why_exempt` bool (default not-exempt).

**From #181 (MERGED, `scripts/gauge_reader.py`):**
- `read(path, *, now=None, max_age=DEFAULT_MAX_AGE) -> Reading | None` — a plain function. **`path` has NO default — YOU (Trip) must construct `.agent-work/<work_id>/gauge.json` yourself** from the checklist's work_id. Returns a `Reading` (frozen dataclass, fields `schema_version`, `fill_fraction`, `model`, `observed_at` as aware datetime) or `None`. A `Reading` reaching you is fresh + well-formed by construction (staleness already collapsed to None inside read()). It NEVER raises.
- `thresholds_for(model) -> (soft, hard)` — central model-keyed table; unknown model → `DEFAULT_THRESHOLDS` (currently soft=0.75, hard=0.90, placeholders labeled first-run-calibration TBD). NOTE: `_THRESHOLDS` currently ships EMPTY (every model resolves to the default). That's fine — do NOT seed real per-model numbers (calibration is deferred); just call `thresholds_for(reading.model)`.
- Import it (e.g. `from gauge_reader import read, thresholds_for` or the repo's import idiom) — do NOT re-implement or modify gauge_reader.py.

## Frozen build spec (authoritative)
- At each gate boundary the engine reads the gauge via #181's reader. **Checks at GATE BOUNDARIES ONLY** — the mid-gate runaway is a deliberately accepted limit; do NOT add any mid-gate check.
- **SOFT band (primary):** at `fill >= soft`, the gate response (on the boundary — i.e. the `advance`/`current` path) carries a **stop-by-default question**: "you've used most of your context; unless you're basically done, hand off here at this seam." **Advisory — SOFT NEVER forces.** The agent may decline with a reason (ANY reason accepted in v1; do not police reason quality).
- **HARD band (backstop):** at `fill >= hard`, the engine **REFUSES to advance** until a `refresh-request` exists for the gate (use #179's `has_pending_refresh_request`), pointing the agent at the exact `attach` command to create one. HARD ALWAYS forces.
- **Missing/stale reading → NO advice, never forces.** (The reader already collapses stale→None; a None reading must produce neither a SOFT question nor a HARD refusal.)
- The agent never introspects fill; the engine supplies the fill fact, the agent supplies the stop-point judgment.

## Acceptance (structural — threshold NUMBERS are deferred to first-run calibration; test structurally) — falsifiable
1. SOFT fires at/above `soft` and **never below**.
2. HARD refuses at/above `hard` and **never lets a pass below** `hard`.
3. A missing/stale reading (None) → no advice, **never forces** a handoff.
4. Falsifiable, must NOT happen: does SOFT ever force? does HARD ever let you pass without a refresh-request? (both must be NO).

## Rollout caveat (carry into your PR description; do not "fix")
Do NOT enable/exercise the HARD band in production until #183's tier-skill wiring lands — otherwise an agent hitting HARD writes a refresh-request with no invoker watching and can strand. This is a rollout-ordering constraint, not a build dependency: build both bands and test them; note the caveat.

## Pre-Rulings (overridable only if evidence contradicts — say so if you override)
- **File fence:** edit `scripts/checklist_engine.py` and `tests/test_checklist_engine.py`; import `scripts/gauge_reader.py` (do not modify it). Keep the diff one-concern.
- Your base already includes #179 + #181 (main e2b8005) — no rebase needed.
- Reuse #179's `has_pending_refresh_request` and #181's `read()`/`thresholds_for` exactly as merged — do not re-implement them.

## Honest-Null Clause
A measured negative on a specific claim is a complete, successful deliverable if honestly scoped.

## Inherited Latitude
Frozen spec. Float to the Admiral any interface mismatch with #179/#181 as merged, or any spec gap.

## Workspace
Your worktree: **C:/Programs/constellation-wt-182** (branch `epic178-182-trip`, base `e2b8005` = post-Wave-0 main with #179+#181+#180 merged, provisioned via `git worktree add C:/Programs/constellation-wt-182 -b epic178-182-trip e2b8005`).
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-182` — must exit 0; paste output.
PR integration is server-side merge; you just open the PR.

## Inherited Context (platform invariants)
- Windows box. Run tests: `py -m pytest tests/test_checklist_engine.py -q` (full file — don't break existing).
- PR body via temp file + `gh pr create -F <file>`.
- Set `PYTHONIOENCODING=utf-8` in captured-subprocess child envs.

## Budget
- **Model tier:** Opus (engine integration touching live advance/current paths).

## Stop Conditions
Stop and return on interface mismatch, spec contradiction, or scope beyond fence. Return-and-query the Admiral.

## Return Shape
Write result to **C:/Programs/constellation-skills/.agent-work/epic-178/crew-handoffs/182-result.md** (MAIN checkout path) BEFORE going idle: verdict + summary; `--here` output; full test output; diffstat; PR URL; the rollout caveat; any floats/map-impact/triage.
