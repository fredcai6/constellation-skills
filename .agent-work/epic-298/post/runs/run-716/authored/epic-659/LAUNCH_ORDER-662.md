# Launch Order (Commander): `cmdr-659-662 — Per-weekend segment-map derivation`

Full Commander (understand → plan → execute → reconcile). This is the **map keystone** of epic #659: it turns the merged SegmentMap runtime (#661) + frozen constants (#660) into an actual per-weekend tiling of a circuit into physically-meaningful segments. Getting the corner-typing gate subtly wrong **silently mis-types every corner** — rigor over speed.

## Mission
Build issue **#662** (epic #659, manifest id `C`): per-weekend segment-map derivation — complete tiling, FIA-sector nesting, severity membership — for **2023-first, quali-side** (Build 1). Populate the SegmentMap the #661 runtime consumes.

Read the issue body in full (`gh issue view 662`) — it is the spec. This order pre-rules the ambiguities; where it is silent, the issue governs.

## Owner rulings binding on the whole epic (do not relitigate)
- **No frame-kill.** A weak/absent signal routes to structural work or an honest scoped-null, NEVER to abandoning the frame. A measured negative is a complete, successful deliverable — say so plainly.
- **Frozen constants (F12).** Every threshold is imported from the merged `src/physics/layer2/frozen_constants.py` (#660) — NEVER a literal at the call site, NEVER a value picked or fit here. Changing a frozen value is out of scope; if one looks wrong, STOP and float to the Admiral (it becomes a new named set + full re-run, never a silent retune).
- **Pre-quali constraint.** The map is a *fixed-per-weekend* structure derived from session telemetry; it is upstream of prediction. No leakage of race outcomes into the map.
- **Lowest dimensionality / escalation dormant.** Sub-phase marks stay a reserved marks-only signature — do NOT build a backing store or populate them (mirror how #661 reserved them). Adjacency + turn-direction are the only ACTIVE attributes you populate.
- **No baked-in normality.** Severity memberships are SOFT (fractional weights). Consume the existing #638 class vocabulary as-is; the per-era Student-t refit + fresh F12 gate are DEFERRED to backfill (review T10) — state the deferral, don't silently skip it.

## Scouting already done — do NOT re-open (owner-settled 2026-07-25)
The owner asked whether official F1/FIA sector definitions could replace self-derivation. Two scouting agents (code probe + web research) settled it, owner-ratified:
- **Fine mini-sectors: self-derive from telemetry. Official data cannot serve the fine grain.** The F1 live-timing feed carries only per-segment *color/status* codes (no timestamps, no distances, no geometry); OpenF1 mirrors this (status-only); the FIA publishes NO mini-sector boundary geometry anywhere. Every ecosystem tool self-derives. Do NOT wire OpenF1/live-timing segment data — owner ruled it "optional to useless," dropped.
- **Official CORNER markers (`circuit_info.corners`) are demoted to OPTIONAL COSMETIC naming only** — a human-legible corner-number label you MAY join at the very end, never a boundary source and never a structural dependency. If noisy, drop it with zero impact. Do NOT anchor the derivation on it.
- **The 3 official TIMING sectors ARE used — but exactly as the spec already says:** reconstruct the sector *line* per weekend by time-to-distance interpolation off telemetry (they are time-only in the feed — you build the spatial line yourself). This is the coarse nesting frame, not fine data.
@grade: settled/human — do not reopen the official-data question.

## Pre-Rulings
- decision:reference-lap-gate — the canonical corner/straight/braking gate is computed off the **FIELD REFERENCE LAP** (a pooled/representative lap), NOT per-lap. Corner = reference-lap lateral acceleration (v_ref² × curvature) above `CORNER_CURVATURE_THRESHOLD`-equivalent typing (the frozen gate is curvature 0.005 1/m; honor the issue's `v_ref²×curvature` formulation using the frozen threshold — do not introduce a second literal). Per-lap kinematic gates are demoted to **observation filters**: the map is fixed per weekend, every lap scored against it, so driver-invariance holds by construction.
  @grade: settled/human (spec §1)
- decision:braking-envelope-not-mean — braking-zone onset = field **ENVELOPE** onset at the frozen robust low quantile (`BRAKING_ONSET_QUANTILE` = p10), running to corner entry. **NEVER a mean** — a mean onset sits *inside* the real braking zone. The median-pooled-ribbon failure is the documented precedent (`excursions/x2-RESULT.md` in the archived exploration record). If you cannot locate that record, the rule still stands: envelope low-quantile, never central tendency.
  @grade: settled/human (spec §1)
- decision:a-lateral-unit-trap — **READ ISSUE #639 BEFORE WRITING THE LATERAL-ACCELERATION GATE.** #639 documents an undocumented `a_lateral` unit convention + a duplicated fallback path in the #625 substrate this builds on — "a silent way to mis-type every corner." Confirm the unit (m/s² vs g) at the point you compute v_ref²×curvature; `GRAVITY_MS2` exists for the conversion. Document the unit explicitly at the call site. This is the single highest-risk step.
  @grade: settled/human
- decision:sector-nesting-splits-not-snaps — FIA sector lines are **mandatory cut points**. A segment straddling a sector line **SPLITS into same-class pieces** — never snapped (snapping distorts physical boundaries). Sliver-merge (`MIN_SEGMENT_LENGTH_M` = 5.0) EXEMPTS sector cuts. Sector-nesting **fails CLOSED** (`SectorLineUnavailableError`) rather than emit a map missing the invariant.
  @grade: settled/human (spec §1)
- decision:soft-membership — severity memberships are SOFT fractional weights flowing through every consumer; consume #638's k=4 vocabulary as-is (#642 cap consumed unchanged). No hard argmax typing.
  @grade: settled/human
- decision:dormant-subphase — sub-phase marks stay DORMANT (reserved signature only, no backing store, not populated). ACTIVE attributes = adjacency (neighbor class, following-straight length, direction flip — computed on demand, never persisted) + turn direction (int8 in the runtime array).
  @grade: settled/human
- decision:corner-marker-cosmetic — see scouting note above: official corner-number labels are optional cosmetic join at the end ONLY. Default to NOT joining them unless it is trivially clean; the map must be fully correct with zero official-corner input.
  @grade: guess · leans skip · settle: if the join is >~20 lines or needs any tuning, skip it and note it as a follow-on.

## Acceptance (honest test labels — review T3)
Construction checks (catch coverage/arithmetic bugs, NOT mis-typing — label them as construction checks, not validation):
- Tiling completeness: segments partition the lap with no gaps/overlaps.
- Sector-nesting exactness: every FIA sector line is a segment boundary; straddlers split; slivers merged except at sector cuts.

The substantive **GATING** checks (falsified by unstable or physically-wrong maps, not merely gaps):
1. **Cross-weekend map stability** — boundary drift between same-circuit 2023 weekends within `MAP_STABILITY_DRIFT_M` (10.0 m). (If only one 2023 weekend exists for a circuit, state the coverage gap honestly; do not fabricate a second.)
2. **Typing spot-checks** against independently-derived references — the ephemeris pilot's Bahrain corner windows (`excursions/P4-RESULT.md`) and the corner tallies in the #625 circuit-rollup artifacts. A right count + right locations on a couple of circuits is the real evidence.

Run tests on the **pinned interpreter** (below). `py -m src.utils.simplification_limits` clean on touched paths.

## Out of scope
Cross-year corner history; per-corner identity beyond arc-length within a layout version; live seeding. Do not build these.

## Workspace
Worktree: **`C:/Programs/f1brainz-wt/epic659-662`** · branch `epic659/662-segment-map-derivation` · base `f125e919` (current main; #660/#661/#663/#665 all merged).
**First step (paste output):** `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe C:/Users/fredc/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here C:/Programs/f1brainz-wt/epic659-662` — run it FROM inside the worktree; expect exit 0 and your assigned path echoed.

### Interpreter pin (CRITICAL — fleet-wide trap)
Bare `py` resolves to a codex-runtime **Python 3.12 with NO fastf1** — conftest fails collection, imports break. Pin the real project interpreter for ALL python/pytest/verification:
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` (Python 3.14, fastf1 3.8.1).
Run tests as `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/...`. The DB (`data/f1_data*.db`) is the data store; per-year DB is `data/f1_data_2023.db`. Prefer cached/DB data; do not trigger large online fetches.

### Substrate you build on (all merged to base)
- `src/physics/layer2/frozen_constants.py` (#660) — import every threshold from here. `CORNER_CURVATURE_THRESHOLD` re-exports the single-source `straight_curvature_threshold`; do not add a second `0.005`.
- `src/physics/segment_map/` (#661) — the runtime (`runtime.py` flat-array `segment_of`), `protocols.py`, `identity.py`, `from_mixture.py`, `store.py`. You POPULATE the map this runtime consumes; reuse its structures, don't fork them.
- #638 k=4 severity class vocabulary artifacts; #625 circuit-rollup substrate (heed #639).

### Cartographer hazard (carry into any cartographer dispatch)
If you dispatch a cartographer subagent to reconcile the arch map: it MUST write to THIS worktree's checkout, not the main checkout. A prior cartographer (cmdr-663's) wrote arch edits to `C:/Programs/f1Brainz` (main) git-invisibly. **Mandate a `git status` in BOTH the worktree AND `C:/Programs/f1Brainz` before it commits**, and confirm its edits are on the worktree branch. Better: for this epic, arch-map reconcile is CONSOLIDATED at Admiral closeout — so stage your map delta as `notes-662.md` + a `662-cartography/` dir and let the Admiral fold it. Do NOT edit `docs/architecture/*` on your branch (map fence).

## Constraints & hygiene
- Windows: `py` launcher exists but is the WRONG python — use the pinned path. `gh pr create -F <tempfile>` (never a heredoc body).
- Do NOT commit any `.agent-work/` path on the branch. Editable-`.pth` trap: prefer pytest over ad-hoc scripts (ad-hoc scripts in a worktree silently import MAIN repo `src/`).
- PR = **server-side squash merge** (do not local-merge). One writer per doc. Working notes → `notes-662.md` (never `findings-*.md`).
- Map fence: do NOT touch `docs/architecture/*`. Stage cartography for Admiral closeout consolidation.

## Model tier
**Opus.** This is the map keystone; the a_lateral unit trap + envelope-not-mean + reference-lap gate are subtle correctness hazards where a silent mis-type poisons every downstream consumer. (Deviation from the Sonnet default is a deliberate Admiral model-tier ruling for this issue.)

## Return Shape
Verdict (built + gating checks' results — stability drift numbers, typing spot-check counts/locations vs P4 Bahrain + #625 tallies) + evidence (test output on pinned interpreter, `simplification_limits` result, which `a_lateral` unit you confirmed and where) + module/artifact paths + the `verify_worktree_isolation.py --here` matched output + triage candidates + your staged `notes-662.md` / `662-cartography/` map delta. Open the PR, post the verdict; the Admiral gates + reviews + merges. A clean scoped-null on any gating check (e.g. single-weekend circuits blocking the stability gate) is a complete deliverable — report it, don't force it. Deliver artifact + post verdict before idling. Float to the Admiral on: a frozen value that looks wrong, the a_lateral unit being genuinely ambiguous after reading #639, or any decision outside these rulings.
