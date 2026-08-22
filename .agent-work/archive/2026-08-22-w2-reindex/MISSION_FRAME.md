# Mission Frame

Map-first frame for `w2-reindex`, authored under the frozen `LAUNCH_ORDER-w2-reindex.md`. This
repo's map orientation came back `DEGRADED-UNPARSEABLE`: `docs/architecture/generated/map.json`
carries no `nodes[].id`, `docs/architecture` has no packets, and `map/INDEX.md`/`map/ids.jsonl` —
this mission's own subject — carry no `map_orient`-citable anchor ids. Per `context`'s discharged
receipt, this frame is built from the declared substitutes cited below: `docs/agents/AGENT_GUIDE.md`,
`docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`, `CLAUDE.md`. No `struct:`,
`capability:`, `constraint:`, `assumption:`, `claim:`, `decision:`, or `event:` id-syntax is used
anywhere below — this run oriented DEGRADED, so no such anchor could ever resolve; the launch
order's own pre-ruling names are instead quoted as plain text (e.g. "git-pre-commit-not-posttooluse")
so they read unambiguously without minting unresolvable anchor tokens.

## Intent

Make `map/INDEX.md` and `map/ids.jsonl` correct by construction: a git pre-commit hook regenerates
and silently stages both tracked map artifacts whenever they are stale, wired into the installer
`scripts/install_constellation.py` (see `docs/agents/AGENT_GUIDE.md`) and proven to fire, while
`tests/test_code_map.py`'s `MapTreeFreshnessTests` — the doc-recorded backstop for `--no-verify`,
fresh clones, and CI — stays exactly as strong as it is today.

## Affected Capabilities

- `scripts/code_map` (per `docs/agents/AGENT_GUIDE.md`: "the generated code map... rebuild with
  `python -m scripts.code_map build`") — the build this mission calls from a new pre-commit hook
  instead of only by hand.
- `scripts/install_constellation.py` (per `docs/agents/AGENT_GUIDE.md`: "bundles each skill... into
  an agent's skills root") — the only existing delivery path; this mission adds a **second**
  delivery path (a git hook) that the same installer must wire, per the launch order's
  "must-be-installed-not-merely-built" pre-ruling.
- `tests/test_code_map.py::MapTreeFreshnessTests` — the CI/local-suite backstop named in
  `docs/agents/ORCHESTRATOR_CONTEXT.md`'s Evidence-and-Verification map ("targeted automated tests
  plus relevant broader suite"); must not be weakened per the launch order's
  "do-not-weaken-the-freshness-test" hard constraint.

## Examples / Events

- A human commit at base `244665ee` shipped `map/INDEX.md` stale by one whole test module while its
  own message claimed "map/INDEX.md rebuilt" — the motivating failure this mission exists to close
  (launch order, Prior-Wave Verdicts).
- Wave 1 paid three separate reindex rounds across two lanes — a cost this mission is not trying to
  eliminate (the human ruled two independent merges legitimately need two reindexes), only to stop
  from surfacing *late*.

## Structural Anchors

No map-resolvable anchors exist for this repo's own layout (DEGRADED-UNPARSEABLE). Path-level
anchors instead, all confirmed on disk this run:
- `scripts/hooks/` — existing hook script directory (currently `gauge_writer_hook.py`,
  `spine_rail.py`); this mission's git pre-commit hook script lands here per the launch order's
  fence.
- `scripts/install_constellation.py` — the installer; wires Claude Code hooks today
  (`.claude/settings.json` → `scripts/hooks/`) and, per the launch order's
  "git-pre-commit-not-posttooluse" pre-ruling, must additionally wire a **git** hook, which it does
  not do today.
- `scripts/code_map/` — `checks.py`, `cli.py`, `discovery.py`, `extract.py`, `render.py`,
  `thresholds.py`, `__main__.py`; `python -m scripts.code_map build --root .` is the regeneration
  command this mission's hook calls.
- `tests/test_code_map.py` — `MapTreeFreshnessTests` (line ~4656), the freshness backstop.
- `.git/hooks/` (common gitdir, verified via `git rev-parse --git-common-dir`) — confirmed empty of
  any non-sample hook this run; `core.hooksPath` unset.

## Governing Constraints / Assumptions

- Build as a git pre-commit hook, not a Claude Code `PostToolUse` hook (launch order pre-ruling
  "git-pre-commit-not-posttooluse").
- A stale index is regenerated and staged, and the commit proceeds; the hook never fails the commit
  (launch order pre-ruling "regenerate-and-stage-silently").
- `MapTreeFreshnessTests` stays exactly as strong as it is today — hard constraint (launch order
  pre-ruling "do-not-weaken-the-freshness-test").
- The hook must be wired into `install_constellation.py` and proven to fire, not merely built — hard
  constraint (launch order pre-ruling "must-be-installed-not-merely-built", echoing wave 1's
  `RegistrationLint`/#345).
- Staging is auditable: exactly the two tracked map artifacts, never an unrelated dirty file (launch
  order pre-ruling "hook-must-be-honest-about-what-it-stages").
- Do not touch `generate_spine.py`, `specs/`, or the spec-to-template migration — hard constraint
  (launch order pre-ruling "no-spec-migration").
- Any new check must run somewhere that can fail: a template `command` check, a pytest test, or a CI
  job — hard constraint (launch order standing epic pre-ruling "no-new-unwired-checker").
- The red-proof must run against the shipped SHA (launch order standing epic pre-ruling
  "red-proof-pinned-to-shipped-revision").
- Assumption under live investigation, not presumed true: a git pre-commit hook can be installed
  portably and can stage exactly two known paths without corrupting a partial commit
  (`git commit -p`, `git commit <path>`) — the Honest-Null Clause's named sharpest hazard.

## Decision Anchors & Decision Pressure

Pre-ruled by the launch order (grades as stated there; none revisited here):
- "git-pre-commit-not-posttooluse" — pre-commit hook, not PostToolUse.
  `@grade: settled/human · leans g1-implement`
- "regenerate-and-stage-silently" — regenerate+stage silently, never fail the commit.
  `@grade: settled/human · leans g1-implement`
- "do-not-weaken-the-freshness-test" — freshness test stays exactly as strong.
  `@grade: settled/human · leans g1-implement,g1-review,g2-integrate`
- "must-be-installed-not-merely-built" — wired into the installer, proven to fire.
  `@grade: settled/human · leans g2-implement,g2-review,g2-integrate`
- "hook-must-be-honest-about-what-it-stages" — staging boundary proven by a test.
  `@grade: settled/admiral · leans g1-implement,g1-review`

Decision pressure this run forces (implementation-shape choices inside inherited latitude, decided
without floating, recorded here rather than silently):
- How to detect staleness cheaply inside a pre-commit hook (full rebuild vs. incremental
  hash-compare).
- Whether the hook script lives as a standalone `scripts/hooks/*.py` invoked via a thin shell shim,
  or is itself the installed `.git/hooks/pre-commit` file.

## Claims / Evidence Surfaces

- The build is fast and deterministic — "`python -m scripts.code_map build --root .` takes 2.9
  seconds and is deterministic" (launch order, Prior-Wave Verdicts) — re-confirm by timing the
  shipped hook's own build call.
- The hook fires — installed and triggers on a real `git commit`; checked by a red-proof commit
  against a deliberately stale `map/INDEX.md` at the shipped SHA, run against a fresh-process
  install per `docs/agents/ORCHESTRATOR_CONTEXT.md`'s "Dogfooding" section (an in-session observation
  of hook behaviour after an edit is not evidence).
- The staging boundary is honest — the hook stages exactly `map/INDEX.md` + `map/ids.jsonl` and never
  an unrelated dirty file; checked by a test that dirties an unrelated tracked file, commits, and
  asserts it stayed unstaged.
- The freshness test is unchanged — `tests/test_code_map.py::MapTreeFreshnessTests` diff is empty (or,
  if touched, provably equivalent-or-stronger); checked by `git diff` over that file.

## Map Confidence / Staleness / Disputes

- The whole map layer for this mission is **DEGRADED-UNPARSEABLE**, not merely stale: neither
  `docs/architecture` (empty) nor `map/INDEX.md`/`ids.jsonl` (no citable anchor ids) resolve for
  `map_orient`. This is itself evidence for the mission's premise — the map artifacts this epic is
  hardening are not yet even in the shape a downstream tool like `map_orient` can consume — but it is
  **out of this mission's scope** to change `map_orient`'s parser or `code_map`'s anchor format; only
  freshness/staging automation is in scope. Alteration: no scout gate added — the launch order's file
  ownership fence (`scripts/hooks/`, `scripts/install_constellation.py`, `scripts/code_map/`,
  `tests/`) already excludes `scripts/map_orient.py` and `docs/architecture/`, so this frame does not
  plan around fixing it, only around working without it (path-level anchors above, substitute docs).

## Out of Scope

- `generate_spine.py`, `specs/`, spec-to-template migration (launch order "no-spec-migration", hard).
- `scripts/checklist_engine.py` and shipped spine templates — fenced to sibling lanes.
- Any new refusing/blocking check beyond the freshness test and the honest-staging test — those would
  need the launch order's "report-only-names-its-trigger" handling and are not required by the
  mission.
- Fixing `map_orient.py`'s parser or `code_map`'s anchor-id format so this repo's own map resolves
  RESOLVED in the future — a real gap, logged as a triage candidate, not fixed here.
