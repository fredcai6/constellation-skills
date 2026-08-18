# Mission Frame

## Intent

Two bounded fixes, one governing idea (LAUNCH_ORDER Mission): a launcher must take a
declared value, not a machine-local or launch-location-implicit one.

1. `scripts/install_constellation.py` — stop a real (non-`--dry-run`) install from
   rewriting the *installer's own checkout's* tracked `.mcp.json` whenever `--dest`
   (or `--project`) declares an install destination elsewhere. Keep the existing,
   tested self-install wiring (#539) for the no-`--dest` case.
2. `scripts/run_crew.py` — replace "no `--model` means refuse" (#611,
   `decision:refuse-a-tierless-dispatch`) with a role x harness tier table: an
   absent `--model` resolves to the role's declared default (never the host's
   settings); an explicit `--model` outside the role's allowed set is refused by
   name; a non-default in-set choice requires `--reason`, recorded in the
   registry beside `model`.

No docs/architecture packet map exists in this repo (a skill-source repo, not an
application with a generated map), and `map/INDEX.md` is stale/unparseable (links
to per-package `INDEX.md` files that do not exist on disk; `map/ids.jsonl` is
empty) — confirmed DEGRADED-UNPARSEABLE by `map_orient.py orient`
(`.agent-work/567-j/map-orientation.json`), discharged with two file-path
substitutes per `decision:map-index-is-admiral-owned` (#544, not this lane's to
regenerate). There is no map inventory of `capability:`/`struct:`/`decision:`
node ids to cite here without fabricating them. The anchors below are the two
substitute file paths themselves — the closest honest equivalent this repo's map
state offers.

## Affected Capabilities

- Skill installation (`scripts/install_constellation.py`): copies skill bundles to
  a target root and, on a real run, additionally wires the *installer checkout's
  own* `.mcp.json` interpreter command.
- Crew dispatch (`scripts/run_crew.py`): launches an implementer/reviewer/etc.
  subagent via a CLI launcher (`--command`, default `claude`), records a durable
  `crew-runs.json` registry entry, enforces one explicit model tier per dispatch.

## Structural Anchors

- `scripts/install_constellation.py` (substitute, hash-pinned in
  `map-orientation.json`) — `default_mcp_config_path()`, `apply_repo_mcp_config_wiring()`,
  `main()`'s `wire_repo_mcp_config` branch.
- `scripts/run_crew.py` (substitute, hash-pinned in `map-orientation.json`) —
  `CrewLaunchSpec.__post_init__`, `build_entry()`, `build_crew_argv()`, `build_parser()`.

## Governing Constraints / Assumptions

- `.mcp.json` is git-tracked and read directly by a fresh clone/CI/hook before any
  wiring step runs, so it can never sit on an unresolvable placeholder forever
  (#539) — the self-install wiring path stays, only its unconditional trigger
  narrows.
- `SCRIPT_RUNTIME_COMPANIONS`/`SKILL_SCRIPT_BUNDLES` in `install_constellation.py`
  are unrelated to this fix (bundle/companion wiring, not `.mcp.json` wiring) —
  out of scope, do not touch.
- `CrewLaunchSpec` is the one choke point every crew dispatch (cli and external
  backend) passes through — the tier table hooks in there, not per-backend.
- `--command` (`DEFAULT_LAUNCHER = "claude"`) is already the declared, not
  detected, harness signal — `build_crew_argv` already threads it to the actual
  launcher binary. The tier table keys on this value; no new detection machinery.

## Decision Anchors & Decision Pressure

- decision:map-index-is-admiral-owned — do not regenerate/hand-edit `map/INDEX.md`.
  `@grade: settled/doctrine · leans context,plan`
- decision:refuse-a-tierless-dispatch (#611) — superseded in scope, not reverted:
  an absent `--model` no longer hard-refuses when the role/harness pair has a
  table entry; it still refuses when no table entry exists (no invented default).
  `@grade: settled/human · leans g2-implement`
- decision:ship-todays-tiers — table values: admiral opus; commander, implementer,
  reviewer, critic, cartographer sonnet; haiku allowed below each of those.
  `@grade: settled/human · leans g2-implement`
- decision:fail-closed-cheaper — unset model resolves from role, never host
  settings; ambiguous resolves cheaper. `@grade: settled/human · leans g2-implement`
- decision:refuse-by-name — model outside a role's allowed set refused by name.
  `@grade: settled/doctrine · leans g2-implement`
- decision:reason-on-deviation — non-default in-set choice requires `--reason`,
  recorded in the registry beside `model`. `@grade: settled/human · leans g2-implement`
- decision:harness-dimension-is-required — table expresses Codex/local, not only
  Claude Code; declared via `--command`, not detected.
  `@grade: settled/human · leans g2-implement`
- decision pressure — codex/local harness rows: no verified real model
  identifiers for those harnesses exist in this repo today (no Codex/local
  dispatch is wired up anywhere yet). Surfaced at plan: populate only the
  `claude` harness with real tiers: `codex`/`local` get the same schema
  structurally (so the dimension is expressible) with no rows, so an actual
  dispatch against either refuses by name instead of guessing a model string I
  have not verified.

## Claims / Evidence Surfaces

- claim:mcp-dest-untouched — a real install with `--dest` outside the repo
  leaves the repo's own `.mcp.json` byte-identical. Checked by `git diff
  .mcp.json` before/after in a scratch/detached context, plus a unit test.
- claim:mcp-self-install-still-wires — a real install with no `--dest` (plain
  self-install) still wires the checkout's own `.mcp.json` exactly as before.
  Checked by the existing `WireRepoMcpConfigTests` suite plus one adjusted case.
  test.
- claim:role-default-resolves — a crew dispatched with no `--model` runs at its
  role's table default, not the host's settings default. Checked by a
  `run_crew.py` unit test and, at execute/review, one real dispatch inspected
  via the registry entry (not the code).
- claim:refuse-by-name — a `--model` outside the role's allowed set is refused,
  naming the model, the role, and the allowed set. Checked by a unit test.
- claim:reason-recorded — an in-set non-default `--model` requires `--reason`
  and records it in the registry entry beside `model`. Checked by a unit test.

## Map Confidence / Staleness / Disputes

- Whole-repo map (`map/INDEX.md`, `map/ids.jsonl`): DEGRADED-UNPARSEABLE, stale
  relative to disk (links to nonexistent per-package files). Not this lane's to
  fix (`decision:map-index-is-admiral-owned`) — altered the plan by substituting
  direct source reads for the two owned files rather than trusting any map
  claim about them.

## Out of Scope

- `SCRIPT_RUNTIME_COMPANIONS` / `SKILL_SCRIPT_BUNDLES` bundle wiring in
  `install_constellation.py` — unrelated to `.mcp.json` wiring.
- `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, every
  `*SPINE*.template.json`, `specs/` — fenced to lane K.
- `map/INDEX.md` regeneration — Admiral-owned (#544).
- Populating real Codex/local model identifiers into the tier table — no
  verified facts to populate them with; table shape stays expressible, rows
  stay empty until a harness is actually dispatched through this launcher.
- Whether `install_constellation.py`'s repo-mcp-wiring should also gate on
  `--project` pointing elsewhere without `--dest` — folded in as the same fix
  (both are "a declared destination other than this checkout"), not treated as
  a second decision.
