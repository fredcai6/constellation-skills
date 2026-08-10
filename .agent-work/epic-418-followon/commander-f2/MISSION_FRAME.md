# Mission Frame — commander-f2 (#542 adoption, #541 friction capture)

**Read this first: why this frame carries no anchor ids.** The context step's orientation
came back `DEGRADED-UNPARSEABLE` — this repo has no `docs/architecture` packet map, its
own derived code map is an unfilled template, and `map/ids.jsonl` is empty. There is no
map for an anchor id to be a member of, so writing one here would be a citation to
nothing. The frame is built instead from the four readings the orientation receipt
hash-pinned as substitutes, named below wherever they carry the point. The launch order's
pre-rulings are referred to by their bare slug (`the-cli-door-stays`) rather than in
anchor grammar, for the same reason: they are the Admiral's rulings, not map anchors.

## Intent

Make the MCP front door the path agents actually take, and make it record the rejections
it currently answers in silence. Bounded by two issues (#542 adoption, #541 capture) and
by one hard additive constraint: the CLI door stays.

## Affected Capabilities

- **Driving a checklist spine through the engine.** Today: two doors. The CLI
  (`scripts/checklist_engine.py`), named as the default in 16 files under `skills/`; and
  the MCP door (`scripts/mcp_spine_server.py`, 7 tools over 13 of the engine's 18 verbs),
  named in **zero**. This run flips which one the instructions call default without
  removing either.
- **Recording what a run cost.** `docs/EPISODE_STORE.md` fixes the record grammar; the
  `## Mechanical` bin is a closed allowlist carrying `refusals`, `reopens`,
  `rework-count`, `failed-commands`. `scripts/apply_episode_delta.py` is the only write
  path. This run adds one class of observation to what that bin can honestly report.
- **Installing the corpus into a fresh project.** `scripts/install_constellation.py`
  copies skill trees, bundles `required_scripts`, rewrites an interpreter token, and
  optionally wires hooks. It has no MCP awareness and has never written a project-root
  dotfile. This run gives it one.

## Examples / Events

- **The event that has never happened**: an agent calling `mcp__spine__spine_advance`
  while driving its own role spine, because nothing tells it the tool exists.
- **The event that happens and is not recorded**: `mcp_spine_server.call_tool()` returning
  `_tool_error(...)` — a rejection the door answers itself, without entering the engine.
  It touches no counter, no log, no journal, no episode.
- **The event already recorded**: an engine refusal arriving through the door. It runs
  `checklist_engine.main()`, which increments `refusals` and persists it, and
  `scripts/episode_capture.py` reads it into the Mechanical bin. Intact; not this run's
  work.

## Structural Anchors

No map anchors exist (see the header). The structures this run lands in, by path, with the
declared substitute that describes each where one does:

- `scripts/mcp_spine_server.py` — the door. Identity is three module-level constants read
  from the environment at import (`SPINE_ENGINE`, `SPINE_FILE`, `SPINE_SESSION`); no tool
  takes a spine path. Described in `docs/CHECKLIST_ENGINE_DESIGN.md`.
- `scripts/checklist_engine.py` — the engine the door wraps and must never re-implement.
- `.mcp.json` — project-scope registration, read at session launch, `${VAR}`-expanded per
  process. The identity mechanism, per `docs/CHECKLIST_ENGINE_DESIGN.md`.
- `skills/*/templates/*.template.json` and the SKILL bodies — where the CLI is currently
  named as the default path.
- `scripts/install_constellation.py` — the fresh-install path.
- `scripts/apply_episode_delta.py` and `scripts/episode_capture.py` — the episode write
  path, contracted by `docs/EPISODE_STORE.md`.

**Blast radius, since the map cannot give it.** Derived by grepping the engine-invocation
surface under `skills/`: 16 files carry `checklist_engine.py`, `<engine>` or
`--session-id`. They fall into five tiers, and the tier boundary is what the g4 fence
lands on — literal command lines an agent executes (3 spine templates, 7 imperative
fields, plus `commander-core.md`), default-path prose in 6 SKILL bodies, the engine CLI
reference every one of those points at, 3 authoring templates that would propagate the CLI
default to future skills, and 4 incidental narrative mentions that are not invocations at
all and are deliberately left alone.

## Governing Constraints / Assumptions

- **The CLI door stays. F is additive.** Adoption changes the default, never the
  availability. An edit that removes the CLI fails g4. (Launch order pre-ruling
  `the-cli-door-stays`, settled/human.)
- **Never duplicate engine logic.** The door wraps the engine's own dispatch; `git diff`
  against `checklist_engine.py` was empty for the whole of F and stays empty.
- **`episodes/` is written only through `apply_episode_delta.py`**, `--store-root
  episodes` on every invocation, and the `## Mechanical` allowlist is closed
  (`docs/EPISODE_STORE.md` §4). Where a door rejection lands is therefore a real design
  question, not a free field.
- **An episode is a record, never read back as a rule.**
  `docs/agents/ORCHESTRATOR_CONTEXT.md`, "The Retired Learning Playbook" — binding, and it
  binds even though nothing in the ask mentions it.
- **Fail loud every turn.** A capture that cannot write says so on every occurrence, not
  once per run and not at exit. The owner's words; a capture that fails quietly is the
  same defect as the door it instruments.
- **Never write `settings.json` at user scope.**
- **Assumption carried from F, not re-derived**: `.mcp.json` is read at session launch and
  a live session does not hot-reload it. This is why the acceptance run must be an
  external dispatch and not an in-session subagent.

## Decision Anchors & Decision Pressure

Existing rulings this run is bound by (launch order Pre-Rulings, slugs only — see header):

- `the-cli-door-stays` — adoption changes the default, never the availability.
  `@grade: settled/human · leans g4a`
- `count-from-the-call-record` — the acceptance numerator is the driving agent's own
  record, never the server log. A client-side rejection never reaches the server.
  `@grade: settled/human · leans g4b`
- `fail-loud-every-turn` — every occurrence, not once per run.
  `@grade: settled/human · leans g2`
- `episodes-are-records-not-rules` — a rule for a future agent belongs in `docs/agents/*`
  and is the human's call.
  `@grade: settled/human · leans g2`
- `no-gen-mcp-config` — do not reintroduce **per-dispatch** config generation **on
  identity grounds**. Scope matters: `docs/CHECKLIST_ENGINE_DESIGN.md` tombstones a
  generator that minted a config per dispatch to key identity. Installing one
  project-scope `.mcp.json` into a target project at install time is neither.
  `@grade: settled · leans g1, g3 · override only with a measurement naming a case both ${VAR} and generation reach differently`
- `identity-trade-is-recorded` — whichever way g1 goes, the property given up is written
  down. Silence is a gate failure.
  `@grade: settled/human · leans g1`
- `zero-is-a-result` — report zero if zero; do not manufacture friction; do not read zero
  as proof the instrument works.
  `@grade: settled · leans g4b · settle: a seeded-rejection control proves the instrument can score`
- `remeasure-never-reuse` — no baseline carried across a code change.
  `@grade: settled · leans g4b`

**Decision pressure — choices this run forces, surfaced rather than buried:**

- **The identity trade (g1).** The harness shares the process; the door puts identity in
  the process. Three options, each giving something up. Decided at g1 with the property
  given up recorded there — that record is a deliverable, not a footnote.
- **Where a door rejection lands in the episode (g2).** Fold into `refusals`, add a
  mechanical field, or carry it as an agent-supplied observation. The Mechanical
  allowlist is closed, so this is a store-contract question, not a formatting one.
- **Whether the CLI arm gets the same instrumentation (g2).** Without it, future
  DC5-style measurements compare an instrumented door against an uninstrumented one.
- **How an installed `.mcp.json` names the installed door and engine (g3).** The
  committed one uses paths relative to this repo; a fresh install has neither at that
  path.

## Claims / Evidence Surfaces

Each gate re-confirms its own claim; none inherits another gate's evidence. This is the
shape wave 1 got wrong (a claim at g1 with its evidence at g3) and it is not repeated.

| Gate | Claim | Evidence that must exist at THAT gate |
|---|---|---|
| g1 | The identity composition is settled and the property given up is recorded | The written trade, plus a test pinning the invariant the decision rests on — so a later agent cannot silently take the rejected option |
| g2 | The door's own rejections reach the run's episode, and say so loudly when they cannot | Tests over the recording path AND over the loud-failure path; a seeded rejection that the instrument scores |
| g3 | A fresh install gets the door | Installer test proving `.mcp.json` is written with paths that resolve in the target, and the door script is bundled |
| g4a | Role spine instructions default to the door, CLI documented as fallback | A test asserting BOTH: the door named as default, and the CLI still present |
| g4b | A real dispatched agent drove a real role spine to done through the door alone | The driving agent's own `record.jsonl`, scored by F's own instrument; plus the three adoption counts re-measured |

**Instrument reuse, deliberate.** g4b reuses F's archived DC5 scorer
(`evidence/g4-dc5/score_arm.py`) rather than inventing a measure. It counts invocation
attempts from the driving agent's own stream-json record and detects `reached_done` from
tool results. Its docstring records two corrections found mid-measurement that both moved
the number *toward* the door and were disclosed as such. Reusing a proven, adversarially
corrected instrument is cheaper and more honest than a fresh one.

## Map Confidence / Staleness / Disputes

- **The whole map is absent, not merely stale.** `map/ids.jsonl` empty, `map/INDEX.md` an
  unfilled template, no `docs/architecture`. Every anchor this run would want does not
  exist. **How it alters the plan:** blast radius was derived by explicit grep and is
  written into this frame as a measured file inventory rather than assumed; no gate is
  authored against an unverified structural claim; and the condition is escalated to the
  Admiral as an epic-wide standing condition rather than repaired inside a wave under
  measurement.
- **F's DC5 numbers are not carried.** Per `remeasure-never-reuse`, this run's code
  changes invalidate them as a baseline. They are cited as prior art for the instrument
  and for the fumble-rate context, never as this run's measurement.

## Out of Scope

- Removing or deprecating the CLI path. Floats to the Admiral; an edit doing it fails g4.
- Reintroducing per-dispatch config generation on identity grounds.
- Any change to `scripts/checklist_engine.py`.
- Writing `settings.json` at user scope.
- Promoting any observation from this run into `docs/agents/*` — the human's call.
- The 4 incidental narrative mentions of `checklist_engine.py` in doctrine prose
  (`skills/_shared/global-everyone.md`, `skills/admiral/references/fleet-doctrine.md`).
  They name the engine as an artifact, not as a command to run; rewriting them would be
  churn, and they are left alone deliberately rather than missed.
- Repairing the empty code map. Routed to the Admiral as a triage candidate.
