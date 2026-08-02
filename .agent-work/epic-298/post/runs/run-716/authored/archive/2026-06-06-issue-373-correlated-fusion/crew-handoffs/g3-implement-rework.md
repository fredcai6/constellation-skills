# Implementer Handoff — G3 REWORK: robust constructor-name alignment in the scorecard runner

You are a fresh implementer crew. Work ONLY from this handoff. Repo: f1Brainz (Windows; `py` not
`python`). Branch `constellation/issue-373-correlated-fusion`; cwd = worktree root
(`C:\Programs\f1Brainz\.claude\worktrees\agent-a8cafc9a5b22bcd57`). Set `PYTHONIOENCODING=utf-8`
before EVERY python command.

## Starting point (already on disk — your inheritance)
A prior crew built `scripts/fusion_replay/scorecard.py` (the fusion-replay scorecard runner) and
`tests/unit/evo_predictor/test_fusion_scorecard.py`. They WORK and pass their tests, and the runner
produces a full scorecard over real records. READ both first. Do NOT rewrite the runner — you are
making ONE targeted robustness fix.

## The problem to fix (a coverage/data-alignment bug)
The runner maps each driver to a constructor via `DatabaseManager.get_race_driver_teams(year, round)`
(DB team name), then projects the constructor latent onto drivers via
`project_constructor_field_to_drivers`, which raises if a mapped constructor name is not EXACTLY in
the record's constructor `entity_ids`. Two real-world facts break exact matching:

1. **Lineage naming drift**: the per-year DB and the gold records use different FastF1 vintages, so
   the SAME constructor lineage appears under different names. Verified equivalences (all must match):
   - `Red Bull Racing` == `Red Bull`
   - `Alpine` == `Alpine F1 Team` == `Renault`
   - `Racing Bulls` == `RB F1 Team` == `RB` == `AlphaTauri` == `Toro Rosso`
   - `Kick Sauber` == `Sauber` == `Alfa Romeo` == `Alfa Romeo Racing`
   - `Aston Martin` == `Racing Point` == `Force India`
   - (Haas F1 Team, Ferrari, McLaren, Mercedes, Williams are stable.)
2. **Genuine absences**: some `race_weekend` constructor records legitimately omit constructors that
   did not register a relevant weekend session (e.g. 2025 R13 quali_weekend has only 6 constructors).
   For those, the affected DRIVERS must be DROPPED from the event (and counted) — NOT the whole event
   failed.

Current behaviour: ANY unmatched constructor makes `project_constructor_field_to_drivers` raise, the
whole event is caught and skipped. Result: race_start drops to 87/173 events; quali/race lose ~6.
Goal: recover coverage to as close to 173/173 as the data genuinely allows, dropping only individual
drivers whose constructor is truly absent from that event's record.

## What to build (exact changes — additive/surgical in scorecard.py)

### 1. A constructor-name normaliser
Add a pure helper, e.g. `_normalize_constructor_name(name: str) -> str`, that collapses a constructor
name to a lineage token. A verified implementation (use this — it is collision-free across all 1038
constructor record events, confirmed):
```python
def _normalize_constructor_name(name: str) -> str:
    n = name.lower()
    for suffix in (" f1 team", " racing", " team"):
        n = n.replace(suffix, "")
    n = (n.replace("red bull", "redbull")
           .replace("kick sauber", "sauber").replace("alfa romeo", "sauber")
           .replace("alphatauri", "rb").replace("toro rosso", "rb").replace("racing bulls", "rb")
           .replace("racing point", "astonmartin").replace("force india", "astonmartin")
           .replace("renault", "alpine"))
    return n.strip().replace(" ", "")
```

### 2. Per-event constructor matching + driver drop
At the point where the event's `constructor_by_driver` is built (`_preprocess_events` /
`_get_constructor_by_driver` and the driver-set filtering), change the logic so that, PER EVENT:
- Gather the constructor `entity_ids` actually present in THIS event's constructor records (both
  constructor-scope modules — recent AND weekend; a driver must be droppable if EITHER constructor
  module lacks its constructor, because both get projected during fusion). Build a map
  `normalized_token -> actual_record_constructor_name` per constructor module.
- For each driver, normalise its DB team name and look it up in BOTH constructor modules' token maps.
  If found in both, REMAP the driver's constructor to the record's actual name (so projection matches
  exactly). If the driver's constructor token is absent from EITHER constructor module's record,
  DROP that driver from the event's driver set and increment a counter
  `drivers_dropped_constructor_absent`.
- Keep the existing "drop drivers with no DB team" and "skip event if <3 drivers" logic.
- The remapped `constructor_by_driver` passed to fusion/residuals must use the record's actual
  constructor names (so `project_constructor_field_to_drivers` never raises). If it still raises for
  an event, that is a real bug — let it surface (do not blanket-catch to hide it); but with correct
  remapping + dropping it should not.

IMPORTANT: the normaliser must be collision-safe WITHIN an event — if (defensively) two different
record constructor names in the same event normalise to the same token, raise a clear ValueError
naming the event + the two names (this should never happen on real data; it is a guard).

### 3. Update the missingness reporting
Add `drivers_dropped_constructor_absent` (and, if useful, `events_with_constructor_drops`) to the
per-task `miss_counts` in the scorecard JSON and the diagnostics. Keep ALL existing counters.

### 4. Tests (extend `tests/unit/evo_predictor/test_fusion_scorecard.py`, synthetic only)
- `test_normalize_constructor_name_lineages`: assert the verified equivalences above normalise equal
  (Red Bull Racing==Red Bull, Alpine==Alpine F1 Team==Renault, Racing Bulls==RB==AlphaTauri==Toro
  Rosso, Kick Sauber==Sauber==Alfa Romeo, Aston Martin==Racing Point==Force India), and that distinct
  lineages (Ferrari vs Mercedes etc.) normalise DIFFERENTLY.
- `test_driver_dropped_when_constructor_absent`: a synthetic event whose constructor record omits one
  driver's constructor -> that driver is dropped + counted, the rest of the event still scores.
- Keep all existing tests green. Seed RNG. No real data/DB/network.

## Close Criteria (prove each, paste output)
- `py -m pytest tests/unit/evo_predictor/test_fusion_scorecard.py -q` passes (new + existing).
- `py -m pytest tests/unit/evo_predictor/ -k "fusion or record or replay or scorecard" -q` passes.
- `py -m scripts.fusion_replay.scorecard --records-dir .agent-work/issue-373-correlated-fusion/records --out .agent-work/issue-373-correlated-fusion/evidence/scorecard.json`
  runs cleanly and now scores **>=160 events for ALL THREE tasks** (quali, race_start, race) — paste
  the full printed table showing `events_scored` per task. (race_start currently=87; it must rise to
  ~160+.) No event should fail with "constructor_by_driver references constructors absent" anymore —
  if any remain, report which and why.
- `py -m src.utils.simplification_limits --paths scripts/fusion_replay/scorecard.py tests/unit/evo_predictor/test_fusion_scorecard.py` passes (extract a helper if flagged).
- The scorecard JSON reports the new `drivers_dropped_constructor_absent` count per task.

## Allowed Scope
- EDIT: `scripts/fusion_replay/scorecard.py` (add normaliser + per-event matching + counters),
  `tests/unit/evo_predictor/test_fusion_scorecard.py` (add tests).
- You MAY add a small private helper module under scripts/fusion_replay/ if needed for simplification.
- Do NOT modify any production code, the other harness modules (records/scoring/baseline/variants),
  `_correlation.py`, or fusion.py. Do NOT regenerate records. Do NOT touch docs.

## Specific Exclusions
- No training, no FastF1, DB read-only. Do NOT change the fixed-unit-scale config or the metric set.
- Do NOT enter #374 interaction territory. Do NOT write findings/verdict prose (commander's job).

## Constraints
- numpy-only (+ existing scipy via scoring). PYTHONIOENCODING=utf-8. One canonical path.
- Missingness EXPLICIT and COUNTED; never impute a constructor. The normaliser is the ONLY fuzzy
  step and it must be collision-guarded.

## Suggested Model Tier
sonnet.

## Stop Conditions
Stop and return if: after the fix a task still scores <160 events and you cannot determine why within
scope (report the residual failures + counts); or the normaliser collides on real data (report it).

## Return Format
Return IMPLEMENTER_RESULT: the diff summary (what you changed in scorecard.py + tests), pytest tails,
the FULL printed scorecard table (all 3 tasks, events_scored each), the new missingness counts per
task, simplification tail, assumptions, stop conditions, out-of-scope notes. NO findings/verdict prose.
