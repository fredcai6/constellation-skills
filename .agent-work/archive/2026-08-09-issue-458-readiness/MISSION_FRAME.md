# Mission Frame

Shrunk per this template's own permission: the context step's `map_orient.py orient` returned
`DEGRADED-NO-MAP` (no `docs/architecture/` exists in this checkout — this repo has never had a
Cartographer map built). No `struct:`/`capability:`/`decision:` anchor ids exist to cite; citing
one would be fabrication, which `map_orient.py verify-frame` refuses outright ("no map was read
and there is nothing for a map anchor to be a member of"). This frame is built from the declared
substitute — `README.md` (hash-pinned in `map-orientation.json`) — plus the frozen launch order,
per Intent below.

## Intent

Add a **readiness check** to `scripts/install_constellation.py`: one command that answers "is this
project set up to run Constellation" and **refuses with a named reason** when it is not, per
#458's own body and the launch order's Pre-Ruling 1 (build the CHECK; wiring stays a separate
opt-in behind `--wire-hooks`). It does not repair anything and never touches `settings.json`.

## Affected Capabilities

- `install_constellation.py`'s existing hook-wiring detector (`detect_hook_wiring` /
  `describe_hook_wiring`, README.md's own "Every install also **reports** whether the Context
  Governor's `PostToolUse` hooks are wired..." paragraph) — the readiness check reuses this
  reporting path for one of its four items rather than re-deriving it.
- `scripts/check_corpus_freshness.py` — precedent for the check-command shape this readiness
  check follows: distinct exit codes (0 current / 1 behind / 2 cannot-determine), no side effects.

## Examples / Events

- README.md's documented `install_constellation.py --dry-run` output line is the existing
  precedent for "a command reports a named condition without repairing it."

## Structural Anchors

None citable — DEGRADED-NO-MAP. The substitute in place of a structural anchor is `README.md`,
whose "Repo layout vs. installed layout" and "Install" sections describe where
`install_constellation.py` and its bundled skill copies live, both repo-source and installed
shapes.

## Governing Constraints / Assumptions

- `README.md`: "Every install also **reports** whether the Context Governor's `PostToolUse` hooks
  are wired into your `settings.json`... It only reports: nothing is written to `settings.json`
  without the opt-in flag." The readiness check inherits this constraint: report, never repair.
- Launch order Pre-Ruling 2 (not overridable): `settings.json` is never touched, at any scope.
- Launch order Pre-Ruling 3 (not overridable): must be run against a fresh clone and observed to
  refuse on a real unready checkout — a check only ever seen passing on the author's box is
  unproven.

## Decision Anchors & Decision Pressure

No `decision:` map anchors exist (DEGRADED-NO-MAP). One decision this run itself makes, already
settled by the launch order and not reopened here:

- Pre-Ruling 1 resolves the R-vs-#458 discrepancy toward the CHECK (workstream R's stronger
  "fresh clone produces a reading with no machine-local config" reading is declined this run).
  `@grade: settled/human · leans launch-order-pre-ruling-1 · settle: n/a — human-authored, frozen`

## Claims / Evidence Surfaces

- Claim: "engine present and runnable" means the engine can actually **import and run pytest**,
  not that a process launches — checked by invoking `python -m pytest --version` (or equivalent)
  and inspecting its exit code / stderr, not by checking `python --version` alone. Backed by the
  live `python` vs `py` measurement cited in this dispatch (#313-shaped): `py` on this box exits
  nonzero with `No module named pytest`, which looks exactly like a red suite rather than a
  missing interpreter.
- Claim: hook-wiring readiness means WIRED specifically in a file that **ships** — for project
  scope that means git-tracked (`git ls-files` membership, not merely present on disk: the
  Mission's own measured table shows wiring can exist only in `.claude/settings.local.json`,
  gitignored, while the tracked `.claude/settings.json` carries `spine_rail` but not
  `gauge_writer_hook`); user scope has no tracked/untracked axis at all (`~/.claude/settings.json`
  is never part of a repo), so its criterion is simply "is this the file the harness actually
  reads at runtime" — the two scopes need two distinct ships-checks, not one shared tracked test.
  Checked by reusing `detect_hook_wiring`'s existing WIRED/STALE/UNWIRED/CANNOT EVALUATE
  classification and reporting which file backs the answer, plus the scope-appropriate ships-test.
- Claim: "work area present" means the project satisfies README.md's own Baseline Assumptions
  ("Constellation assumes a Git repo, Markdown docs, and file-based workflow state") — checked by
  confirming a `.git` entry at root (this run's own `map_orient.py` root-proof pattern), not by
  requiring `.agent-work/` to already exist (a project ready to *start* using Constellation has
  not necessarily run it yet, so that would be circular).

## Cold-critic finding folded in before freeze

A cold plan critic (frame + plan only, no authoring context; launch order as its one allowed
authority) flagged that **cloning fresh only resets the repo tree, not the executing
environment** — items (1) engine-runnable and (3) hooks-wired-in-a-file-that-ships are properties
of *this agent's own Python/settings*, not of the cloned tree, so a fresh clone cannot make either
of them refuse by itself. Only (2) skills-installed and (4) work-area-present are tree-scoped and
can genuinely refuse from a clone alone. Pre-Ruling 3's "observe it refusing on a fresh clone" is
therefore satisfied by a tree-scoped item's refusal (2 or 4); items 1 and 3 are proven by their
own unit tests (an unready case constructed directly), not by the fresh-clone run — this
distinction is now explicit in `g1-integrate` rather than left for the integrator to discover.

## Map Confidence / Staleness / Disputes

- No map exists in this checkout at all (not stale — never built). Nothing here depends on map
  currency; this run depends on `README.md` and the frozen launch order instead, both read in
  full at `context`/`understand`.

## Out of Scope

- Wiring the gauge writer hook, or writing/mutating any `settings.json` at any scope (Pre-Ruling
  1 and 2).
- Extending the readiness list beyond a fifth item without a stated reason (Pre-Ruling 5 — the
  four named items are the known baseline; more is a judgment call, not a default).
- Touching `scripts/checklist_engine.py` or `tests/test_checklist_engine.py` (crew 4's file
  ownership this wave) or promoting any observation into `docs/agents/*` doctrine.
