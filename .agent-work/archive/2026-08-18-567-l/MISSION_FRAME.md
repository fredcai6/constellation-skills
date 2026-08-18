# Mission Frame

Shrunk per the template's own escape clause: three trivial, already-decided, bounded
edits (an episode-store rephrase, one dict-literal value change, one small new lint
script) with existing/added tests as the acceptance bar. The map is DEGRADED
(`.agent-work/567-l/map-orientation.json`, discharged) and Admiral-owned per
`decision:map-index-is-admiral-owned` — it adds nothing here that reading the three
target files directly does not already give. Correction from the Admiral (attach
below): `map/INDEX.md` is not an unfilled template — it is a fully built 31KB source
scan across 167 module directories, fresh as of today. What is empty is
`map/ids.jsonl`, because it is written from *minted* anchor ids and this repo has
never minted any; `map_orient.py` reads that absence as DEGRADED-UNPARSEABLE
regardless of INDEX.md's own freshness.

## Intent
Land the three human-ruled changes from `LAUNCH_ORDER.md` so lane J's merge gate
(PR #637) goes green: (1) restate `episodes/active/567-j-004.md` assertion `a5` so
the observation guard's imperative trigger stops firing, without growing
`guard.EXCEPTIONS`; (2) widen `ROLE_MODEL_TIERS["claude"]["commander"]["allowed"]`
from `{sonnet, haiku}` to `{sonnet, opus}` (default unchanged, everything else
unchanged); (3) build a corpus lint that fails on a role spine template with zero
declared bookends, and on repo-vs-installed drift in those declarations, scoped to
role spine templates only, without touching `_is_bookend()`'s runtime-permissive
default.

## Affected Capabilities
- episode-observation guard (`scripts/verify_episode_observations.py`,
  `scripts/apply_episode_delta.py`'s `restate-assertion` op) — this run only calls
  the existing write path, adds no new capability.
- crew model-tier resolution (`scripts/run_crew.py::ROLE_MODEL_TIERS`,
  `resolve_model`) — one dict-literal value edit, no logic change.
- corpus freshness/declaration tooling (`scripts/checklist_engine.py::_is_bookend`,
  `skills/*/templates/*_SPINE.template.json`, `scripts/check_skill_freshness.py`) —
  new lint script added; no existing behavior changed.

## Structural Anchors
- `scripts/verify_episode_observations.py` — guard module (`triggers_for`,
  `EXCEPTIONS`, `IMPERATIVE_KINDS`, `IMPERATIVE_VERBS`).
- `episodes/active/567-j-004.md` — the one record being restated (assertion `a5`).
- `scripts/run_crew.py:847-858` — `ROLE_MODEL_TIERS` dict literal.
- `tests/test_crew_launcher.py::ResolveModelTests` — the pinning tests for the tier
  table; confirmed no existing case pins `commander`'s `allowed` set specifically.
- `scripts/checklist_engine.py:3045` — `_is_bookend()`, permissive-default read of
  an optional `bookend` key; explicitly not to be touched.
- `skills/commander/templates/COMMANDER_SPINE.template.json`,
  `skills/admiral/templates/ADMIRAL_SPINE.template.json`,
  `skills/explorer/templates/EXPLORER_SPINE.template.json` — the three role spine
  templates that currently exist repo-wide, each declaring 2 bookends; each shows 0
  in the installed corpus (`~/.claude/skills/constellation-{commander,admiral,explorer}/templates/`)
  — drift confirmed by direct grep before planning.
- `scripts/check_skill_freshness.py::check()` — compares a *project's*
  `.agent-work/templates/{.baseline,local}` against installed `upstream`; it does not
  compare *this repo's own skill source* against the installed corpus, which is the
  shape this lint needs. Reusing its three-way status machinery outright would
  require a project-scope manifest this repo (the skill source itself) does not
  have reason to carry — noted per the launch order's "say so if it does not".

## Governing Constraints / Assumptions
- `episodes/`'s only write path is `scripts/apply_episode_delta.py`; hand-editing is
  forbidden (doctrine, `docs/agents/ORCHESTRATOR_CONTEXT.md` "Retired Learning
  Playbook", and restated in the launch order).
- `restate-assertion` accepts exactly `op, id, assertion, statement, history` — no
  more, no less; `assertion` is the bare id (`a5`).
- `guard.EXCEPTIONS` does not grow (pre-ruling `decision:no-exception-list-growth`).
- `_is_bookend()`'s missing-key-reads-as-not-a-bookend default is frozen; the lint is
  a corpus check, not a runtime refusal (launch order Mission §3).
- `admiral`'s tier row and the `implementer`/`reviewer`/`critic`/`cartographer` rows
  are untouched — human-confirmed directly per the launch order.
- Suite gate runs in a clean detached worktree with
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR`.
- `episodes/` order is write -> `git add` -> suite -> commit.
- `map/INDEX.md` is Admiral-owned; do not regenerate or hand-edit it
  (`decision:map-index-is-admiral-owned`, #544). Branch accepted green except
  `MapTreeFreshnessTests`.

## Decision Anchors & Decision Pressure
- decision:map-index-is-admiral-owned — do not regenerate/hand-edit `map/INDEX.md`.
  @grade: settled/human · leans plan,archive
- decision:no-exception-list-growth — rephrase episode statements instead of
  growing `guard.EXCEPTIONS`.
  @grade: settled/human · leans g1-implement
- decision:commander-tier-upward-only — commander row: haiku out, opus in, default
  unchanged at sonnet; every other row unchanged.
  @grade: settled/human · leans g2-implement
- decision:lint-scope-role-spine-templates-only — the new lint checks role spine
  templates (`*_SPINE.template.json`) only, not every template in the corpus.
  @grade: settled/human · leans g3-implement
- decision pressure: whether `check_skill_freshness.py`'s machinery is reused or a
  small standalone script is written for the repo-vs-installed bookend comparison —
  resolved during plan authoring below (self-scoped, no float needed: the launch
  order explicitly delegates this call — "say so if it does not [fit]").

## Claims / Evidence Surfaces
- claim: the guard passes after the restate — checked by
  `pytest tests/test_episode_observations.py::RealStoreTests -q` (exit 0) and by
  direct `triggers_for("workaround", <new statement>)` returning `[]` before commit.
- claim: the commander tier change is upward-only and isolated — checked by
  `tests/test_crew_launcher.py::ResolveModelTests` (existing + one new pinning case)
  and by re-reading `scripts/run_crew.py`'s full `ROLE_MODEL_TIERS` diff.
- claim: the lint fails on an undeclared template and passes on a declared one —
  checked by the lint's own red-proof (a throwaway undeclared-template fixture)
  required in the Return Shape.
- claim: nothing else in the suite regresses — checked by the full suite in a clean
  detached worktree per Inherited Context, gated on the `^FAILED` grep.

## Map Confidence / Staleness / Disputes
- `map/INDEX.md` / `map/ids.jsonl` — DEGRADED-UNPARSEABLE per `map_orient.py`, not
  because `map/INDEX.md` is stale (it is a fresh, fully built 31KB scan) but because
  `map/ids.jsonl` is empty: this repo has never minted anchor ids, so there is
  nothing for a frame citation to resolve against regardless of INDEX.md's own
  freshness. Admiral-owned per pre-ruling. Altered plan:
  read the four target files directly instead of through the map (recorded in the
  context-step orientation receipt); no scout gate needed since the exact files were
  already located and confirmed by direct read at `understand`.

## Out of Scope
- Any twelfth `guard.EXCEPTIONS` entry.
- Any change to `admiral`, `implementer`, `reviewer`, `critic`, `cartographer` tier
  rows.
- Any change to `_is_bookend()`'s permissive default, or to plans without a declared
  bookend at runtime.
- Regenerating or hand-editing `map/INDEX.md`.
- Issue filing, doctrine promotion into `docs/agents/*` (pre-rulings
  `decision:no-issue-filing-mid-run`, `decision:no-doctrine-promotion`).
