# Result — issue #182 (Trip: two-band gate policy) — Wave 1

**Verdict: DELIVERED (green).** Trip (Module 3) is wired into `scripts/checklist_engine.py`; 15 structural tests added; 181/181 pass; PR open. All four acceptance criteria met, including the falsifiable pair.

## Summary
At each **gate boundary** the engine reads the context-fullness gauge (#181 `read()`) and applies model-keyed thresholds (#181 `thresholds_for`), in two fail-safe bands:
- **SOFT** (`fill >= soft`): advisory stop-by-default question rides the read-only `current` output. Advisory only — never forces; declining = choosing to `advance`, which SOFT never blocks.
- **HARD** (`fill >= hard`): `advance` REFUSED until a `refresh-request` exists for the gate (#179 `has_pending_refresh_request`), pointing at the exact `attach` command. Always forces.
- **Missing/stale reading** (`read()` → None): no SOFT question, no HARD refusal — never forces.
- **Gate boundaries only** — no mid-gate check (deliberate accepted limit).

Both bands ride the `dispatch()` CLI chokepoint (like the merged #138 doctrine rail): SOFT is a suffix on `current`'s dispatch output; HARD is a pre-`advance` guard checked before the verb mutates state. `advance()`/`current()` stay pure → all 166 existing tests unchanged.

## Isolation (`--here`, exit 0)
```
worktree OK: in C:/Programs/constellation-wt-182
EXIT: 0
```

## Files changed (fence honored)
```
 scripts/checklist_engine.py    | 152 ++++++++++++++++++++++++++++-
 tests/test_checklist_engine.py | 214 +++++++++++++++++++++++++++++++++++++++++
 2 files changed, 365 insertions(+), 1 deletion(-)
```
Edited only the two fenced files. Imported `scripts/gauge_reader.py` (`read`, `thresholds_for`, `Reading`) by file path — did NOT modify or re-implement it. Reused #179's `has_pending_refresh_request` exactly as merged.

## Full test output
```
$ PYTHONIOENCODING=utf-8 py -m pytest tests/test_checklist_engine.py -q
........................................................................ [ 39%]
...................................................... [ 69%]
.......................................................                  [100%]
181 passed, 18 subtests passed in 13.39s
```
15 new tests (11 band-structure via `dispatch` with the read patched + 4 end-to-end via `main()` with a REAL `gauge.json` written sibling-to-spine, read by #181's real `read()`):
- `TripTwoBandGatePolicy`: soft_fires_at_and_above_soft, soft_never_below_soft, soft_never_forces_advance, hard_refuses_at_and_above_hard_without_refresh, hard_never_refuses_below_hard, hard_passes_once_refresh_request_exists, hard_refusal_leaves_state_unmutated, hard_advisory_on_current_points_at_attach, none_reading_never_forces_and_gives_no_advice, survey_checklist_gets_no_trip_policy, unresolvable_work_id_no_base_dir_no_reading
- `TripRealGaugeFileWiring`: fresh_hard_gauge_sibling_of_spine_refuses_then_passes_with_refresh, stale_gauge_reads_none_and_never_forces, absent_gauge_file_never_forces, fresh_soft_gauge_advises_on_current_but_advance_passes

### Acceptance mapping (all met)
1. SOFT fires at/above `soft`, never below — `test_soft_fires_at_and_above_soft`, `test_soft_never_below_soft`.
2. HARD refuses at/above `hard`, never lets a pass below — `test_hard_refuses_...`, `test_hard_never_refuses_below_hard`.
3. None reading → no advice, never forces — `test_none_reading_never_forces_and_gives_no_advice`, `test_stale_gauge_reads_none_and_never_forces`, `test_absent_gauge_file_never_forces`.
4. Falsifiable (must NOT happen): SOFT forcing → `test_soft_never_forces_advance` (advance passes in SOFT band). HARD passing without a refresh-request → `test_hard_refuses_...` + `test_hard_passes_once_refresh_request_exists` (only passes WITH one).

Thresholds are structural: NUMBERS deferred to first-run calibration. `_THRESHOLDS` ships empty (every model → DEFAULT 0.75/0.90); every test pins to whatever `thresholds_for` returns, never a hardcoded number. No per-model numbers seeded.

## PR
https://github.com/fredcai6/constellation-skills/pull/187  (branch `epic178-182-trip`, base `e2b8005`)

## ROLLOUT CAVEAT (carried into PR; do NOT "fix")
Do NOT enable/exercise the HARD band in production until #183's tier-skill wiring lands — an agent hitting HARD writes a refresh-request with no invoker watching and can strand. Rollout-ordering constraint, not a build dependency; both bands are built and tested here.

## Floats / notes to the Admiral (proceeded within latitude, no blocker)
1. **Gauge-path resolution — pairs with #180's writer (which the launch order didn't paste).** The launch order said "YOU construct `.agent-work/<work_id>/gauge.json`." The MERGED #180 writer (`scripts/hooks/gauge_writer_hook.py:105`) resolves the gauge as `Path(entry["spine"]).parent / "gauge.json"` — a **sibling of the spine**, and its docstring defines `<work_id>` as "that spine path's parent directory." The engine's `base_dir` (`path.parent` in `main()`) IS that spine directory, so I read `base_dir / "gauge.json"` — this pairs exactly with where the writer writes. Constructing a cwd-relative `.agent-work/<cl["work_id"]>/gauge.json` would MISS the writer's file whenever cwd ≠ repo root or the spine dir name ≠ the `work_id` field, so I deliberately did NOT key off `cl["work_id"]`. Unresolvable location (no `base_dir`) → no reading, no advice. This is the correct pairing, not a guess; flagging for visibility, not as a question. End-to-end proven by `test_fresh_hard_gauge_sibling_of_spine_refuses_then_passes_with_refresh`.
2. **Placement decision:** both bands ride the `dispatch` boundary (mirroring #138's doctrine rail) rather than living inside the verb bodies, to keep `advance()`/`current()` pure and the 166 existing exact-equality tests untouched. HARD is a pre-`advance` guard, so a HARD refusal preempts advance's postcondition/why checks (a HARD-tripped agent is out of context regardless). If the Admiral/reviewer prefers HARD ordered AFTER postconditions (inside `advance`, alongside the #179 why-capture), that's a one-function move — say so.
3. **Loader detail:** `gauge_reader.py`'s frozen `@dataclass` under `from __future__ import annotations` requires its module be registered in `sys.modules` before `exec_module` (Python 3.12+ dataclass quirk) — handled in `_load_gauge_reader`. No map impact, no triage.
