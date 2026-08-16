# Mission Frame

Map input DEGRADED-UNPARSEABLE (`.agent-work/cleanup-g-crew-tier/map-orientation.json`): no
`docs/architecture` packet map exists in this repo, and the repo's own derived code map
(`map/INDEX.md`, `map/ids.jsonl`) carries zero citable anchor ids repo-wide at this baseline
(same finding independently made by `cleanup-c-liveness-rail`). This frame is therefore built
from the hash-pinned substitutes declared at the context step, not from map anchor ids — cited
below as plain paths, per `map_orient.py verify-frame`'s degraded-mode contract.

## Intent
Make a crew's model tier an explicit, recorded choice at the one seam where every dispatch
passes through — `build_crew_argv` in `scripts/run_crew.py` — instead of an accident of whatever
tier the dispatching process happened to run at. Refuse a tierless dispatch; wire the `cli`
backend's already-recorded-but-unused `reasoning_effort` metadata into the launcher's real
`--effort` flag; make the handoff templates' "Suggested Model Tier" field the thing doctrine says
a Commander decides *from*.

## Affected Capabilities
- crew dispatch (`scripts/run_crew.py`): `build_crew_argv` builds the `claude` CLI argv; `if
  model: argv += ["--model", model]` is the sole tier-forwarding path and currently accepts
  `None` silently. `CliBackend.dispatch`/`.resume` call it; `CrewSpec.reasoning_effort` is
  recorded into the registry entry (`build_entry`) but never reaches argv.
- dispatch doctrine (`skills/commander/references/crew-dispatch.md`): the prose a Commander reads
  before calling `run_crew.py`. Zero mentions of model/tier today (verified at `understand`).
- handoff authoring (`skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`,
  `skills/commander/templates/REVIEWER_HANDOFF.template.md`): each carries a "Suggested Model
  Tier" section (line 94 / line 60) that is advisory prose today, disconnected from what actually
  reaches `--model`.

## Examples / Events
- A Commander sonnet-tier itself dispatches an implementer with no `--model`: today the child
  inherits the machine default (`fable`, observed in lane A/E baselines); after this change,
  `run_crew.py` refuses the dispatch outright.
- A reviewer handoff says "stronger — concurrency correctness rewards careful reasoning" (lane E,
  live example cited in the launch order): today that request never reaches the launcher; after
  this change the Commander must have translated "stronger" into an actual `--model`/`--effort`
  pair before dispatch, or the refusal stops it.

## Structural Anchors
- `scripts/run_crew.py` — `build_crew_argv` (~line 755-818, the `if model:` line at 813-814),
  `CliBackend.dispatch`/`.resume` (~1490-1638, the two `build_crew_argv` call sites), `CrewSpec`
  (~1337-1364, `reasoning_effort` field), `build_entry` (~1107-1196, records `reasoning_effort`
  as metadata only), `build_parser`/`main` (~1884-2100, the `--model`/`--reasoning-effort` CLI
  surface and every subcommand that constructs a `CrewSpec`).
- `skills/commander/references/crew-dispatch.md` — the dispatch-mechanics doctrine file; owned,
  currently silent on model.
- `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md:94`,
  `skills/commander/templates/REVIEWER_HANDOFF.template.md:60` — the "Suggested Model Tier"
  fields this mission makes load-bearing.
- `tests/test_crew_launcher.py` — the launcher's existing test suite; owned, where new
  refusal/effort-forwarding coverage lands.

## Governing Constraints / Assumptions
- Fenced: `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
  `scripts/spine_lifecycle.py` and their tests (lane F is live in all three) — must not be
  touched even incidentally.
- Fenced: `skills/commander/templates/COMMANDER_SPINE.template.json`,
  `skills/admiral/templates/LAUNCH_ORDER.template.md`,
  `skills/admiral/references/fleet-doctrine.md`, `skills/_shared/**`,
  `scripts/install_constellation.py` — belong to the next-dispatched #610.
- `#607`'s parent-lease-heartbeat thread in `run_crew.py` (start/stop/join ordering around the
  blocking launch call) is load-bearing and must not be disturbed by this change.
- No crew's *effective* tier may change as a side effect of this mission (`decision
  do-not-change-what-anything-runs-at` in the launch order) — this makes the choice explicit, it
  does not repick tiers.

## Decision Anchors & Decision Pressure
The launch order's Pre-Rulings section carries five graded decisions governing this mission
directly (`refuse-a-tierless-dispatch`, `do-not-change-what-anything-runs-at`,
`record-the-resolved-tier`, `suggested-tier-becomes-load-bearing`, `reasoning-effort-follows-tier`
— see LAUNCH_ORDER.md, not restated here to avoid a second copy drifting from the first). One
fact resolved at `understand` sharpens the last of these: the `claude` launcher accepts `--effort
<low|medium|high|xhigh|max>`, so "if the launcher accepts it" is now settled yes, not an open
check the implementer still owes.

Decision pressure this run forces and does not yet resolve: exact refusal wording/exit code for a
tierless dispatch (Inherited Latitude: mine to decide), and whether `--effort` forwarding applies
to every `CliBackend` call site (`dispatch` and `resume`) or `dispatch` only — leaning toward both,
since `resume` relaunches the same crew and a tier that silently drops on resume reproduces the
exact defect this mission fixes.

## Claims / Evidence Surfaces
- Claim: `build_crew_argv`'s tier-forwarding is `if model: argv += ["--model", model]` with no
  refusal path today — checked by reading `scripts/run_crew.py:812-818` directly (done at
  `understand`); re-confirm at the implement gate against the actual current-branch line numbers,
  which may have shifted.
- Claim: `reasoning_effort` reaches the registry entry but never the subprocess argv on `cli` —
  checked by tracing `CrewSpec.reasoning_effort` -> `build_entry(..., reasoning_effort=...)` (recorded)
  vs. `build_crew_argv(...)` (no `reasoning_effort` parameter at all) — done at `understand`.
- Claim: `crew-dispatch.md` never mentions model — checked by `grep -n "model" crew-dispatch.md`
  (zero hits) at `understand`.
- Evidence this run must produce (Return Shape items 1-5 in the launch order): red/green refusal
  demonstration, the caller list (if any legitimately-tierless caller exists), what happened to
  `reasoning_effort` and why, this run's own dispatch record showing no defect reproduced, and a
  clean-env cache-cleared full-suite pass at both the published head and a re-measured `main`
  baseline.

## Map Confidence / Staleness / Disputes
- The repo carries no `docs/architecture` packet map, and `map/ids.jsonl` is empty repo-wide (not
  a staleness of this area specifically — a corpus-wide absence, already flagged as a triage
  candidate by `cleanup-c-liveness-rail` and reconfirmed here). Nothing in this mission's scope
  depends on packet-map claims; every anchor above is a direct file citation, verified by reading
  the file, not inferred from a map. No scout/verification gate is needed for this reason.

## Out of Scope
- `checklist_engine.py`, `spine_rail.py`, `spine_lifecycle.py` and their tests (fenced, lane F).
- `COMMANDER_SPINE.template.json`, `LAUNCH_ORDER.template.md`, `fleet-doctrine.md`,
  `skills/_shared/**`, `install_constellation.py` (fenced, queued #610).
- Picking *new* tiers for any existing dispatch site outside this run's own crews — explicitly
  ruled out by `do-not-change-what-anything-runs-at`.
- The `external` backend's `reasoning_effort` handling (#579) — already built; this mission's
  `reasoning_effort` work is scoped to the `cli` backend only, where the gap actually is.
