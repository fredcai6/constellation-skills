# Mission Frame — issue-456

**Orientation was DEGRADED-NO-MAP and this frame is cut from the substitutes the
receipt hash-pinned**, not from a map. constellation-skills carries no
`docs/architecture` map at all — no generated map, no index, no packets dir — so
there is no anchor id in existence for this area and none is cited below. Citing
one would be inventing it in the same breath as reading it.

The frame is built from the two declared substitutes:

- `.agent-work/issue-456/reference/DESIGN_SPEC.md` — the CONFIRMED design (hash `1200bbed…`)
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — action authority for this repo (hash `2f79929e…`)

That absence is the mission, not an obstacle to it: **this issue builds the tool
that would have produced the map this step wanted to read.** The run is
bootstrapping, and that is surfaced to the human at plan approval.

## Intent

Turn the measured `explore-code-map` prototype into a shipped, vendored tool: a
derived **code map** — extraction and render pipeline, agent-lean page format,
and the skills that consume it — behind checks that can actually go red. The
prototype's own diagnostics are print-only with no assertions and no exit code,
so today nothing downstream of them is trustworthy. Ten gates, in the
critic-reordered sequence.

## Affected Capabilities

No capability packets exist to name. Stated in behavior terms instead, from the
confirmed design:

- **Derive structure from source.** New. A two-pass AST walk with its own name
  resolution emits a statement-line store; measured at 1,224 files → 515,678
  statements in 9.7s, 9.26% unresolved.
- **Render an agent-lean page tree.** New. One page per entity, module indexes,
  a top index, `ids.jsonl`; 16,222 pages in 23.6s, double-build byte-identical.
- **Answer cross-file questions cheaply.** The point of the whole thing: blast
  radius before the first edit. Within-file questions stay with the source.
- **Hand crews their starting pages.** Already live on the exploration branch as
  a 5-file/9-line integration across the commander, implementer and scout
  skills; it ships with this branch and must keep working.
- **Compile authored architecture packets.** Untouched incumbent. Runs the
  opposite direction — validates hand-authored packets, never parses source.

## Examples / Events

- A dev agent picks up an issue, is handed named starting pages, learns the
  blast radius before its first edit, and the map rebuilds in under a minute at
  the end of the run. This is the motivating trace.
- Real dogfood already run: f1Brainz #708 fixed map-first and merged, then regen
  measured **98 lines of map churn against 84 lines of source diff (~1.2×)**.
- The adversarial case that has **never been measured**: churn under a
  widely-referenced-symbol rename. Accepted untested at confirm.

## Structural Anchors

Paths, not anchor ids — no map exists to have assigned one:

- `scripts/code_map/` — the new package. Departs from the 42 flat `scripts/*.py`;
  `scripts/hooks/` is the directory precedent. Ruled by the human.
- `tests/test_code_map.py` — the suite CI runs.
- `scripts/build_architecture_map.py` — 423 lines, the incumbent. No `ast`
  import, never parses source. A complement, but it owns the name
  "architecture map", so the derived tool is called the **code map**.
- `.agent-work/issue-456/reference/prototype/` — the reference implementation,
  read-only. `astx.py` hardcodes `ROOT` to an external repo and has no argparse
  anywhere; that gap is gate 0.
- `skills/commander/`, `skills/implementer/`, `skills/scout/` — the consumers.

## Governing Constraints / Assumptions

- **Stdlib only.** CI installs nothing but pytest and coverage, so a tool with a
  third-party import cannot run at all. Hard, mechanical, non-negotiable.
- **Checks must be able to fail.** Assertions with a nonzero exit and committed
  thresholds. Print-only diagnostics read as measurements, never as a suite.
- **Nothing committed carries a position.** Page suffixes and `ids.jsonl`
  locations move to a rebuildable cache. Positions are the churn that poisons
  every diff.
- **The run report carries no timings**, so the determinism diff can cover it.
- **Page register is agent-first and aggressively minimal.** Entity id as title,
  plain lines, no tables or footers or provenance markers, template text pure
  ASCII, docstrings verbatim. Do not restate prose the file shows; DO carry the
  structural summary that saves opening the file at all.
- **One name for one thing**, per the repo glossary — the reason for "code map".
- **Push and a full PR are pre-approved for this work; merge to `main` is NOT.**
  Per `docs/agents/ORCHESTRATOR_CONTEXT.md`, which requires explicit human
  approval unless pre-approved for the specified work.
- Assumed: this repo can be its own corpus. **Verified, not assumed** — 233
  tracked files, all 233 parse, 5,232 entities. So checks need no external repo
  and no network. Two catches: `.agent-work/` must be excluded (1,821 scratch
  entities, ~35%), and zero BOM files exist here, so gate 9's BOM defect needs a
  purpose-built fixture to go red.

## Decision Anchors & Decision Pressure

No graded anchors exist — there is no map to hold them. What governs instead is
the confirmed spec's rulings and the human's four rulings at understand.

Already ruled by the human, not reopenable by a gate:

- All nine issue gates ship this run, plus a gate 0 for the CLI layer every
  other gate leans on. The Commander's narrower recommendation was put to him
  and NOT taken.
- Tool lands at `scripts/code_map/` as a package.
- Crews are on — an explicit override of the standing instruction, for this run.
- The skills diff is cherry-picked onto this branch; push and full PR approved.

Pressure — choices this run forces, to be surfaced as candidates rather than
settled alone:

- The package layout departs from 42 flat scripts. Governs future structure;
  carried to reconcile as a candidate.
- The line base is silent in the schema today (defect D1) and must be declared.
  Whichever base is declared is durable — every consumer inherits it.
- Gate 8's cull test may collapse three tag kinds into one if the consumer
  treats them identically. That is a vocabulary decision with reach beyond
  this run.

## Claims / Evidence Surfaces

The falsifiers, each of which a gate must be able to trip:

- Determinism — any non-empty diff on unchanged source.
- Inbound-edge attribution — any page whose caller set differs from an
  independent full scan.
- Extraction correctness — a symbol resolved by an independent scan that the AST
  pass misses, outside the named inference-rule gaps; plus a hand-labelled edge
  sample per predicate below its recall floor.
- Churn boundedness — ratio above 3x on a local edit or on a rename.
- Redundancy rule — a page whose non-recoverable lines are a minority.
- Authored-layer staleness — a tag whose anchor body changed while its text did
  not, going unflagged.

## Map Confidence / Staleness / Disputes

- **The map is absent, not stale.** Confidence in it is not low; it is
  undefined. Every structural statement above is therefore cut from the
  confirmed spec or verified directly against the repo, and the ones verified
  directly say so.
- **The prototype's measurements are from another repo** (1,224 files) and do
  not transfer to this one (233). Thresholds must be committed against the
  corpus they will actually run on, or the first CI run is the experiment.
- **Recorded defect in the reach-up contract** (triage candidate `tc1`): a HARD
  context trip blocks `advance`, but `advance --why` is the only verb that
  writes the digest a replacement agent cold-starts from, so the brief goes
  stale exactly at handoff. Not this run's build, but it bit this run.

## Out of Scope

- Replacing source reading, or retiring the authored judgment layer. The derived
  spine is ~7% of that map's text.
- The incumbent packet compiler. Untouched — no integration required.
- Deliberately cut as premature by the critic panel, recorded with revival
  conditions: the redirect table, rename-motion machinery, tombstone machinery
  (a one-line convention instead), and the ranked test-coverage report.
- Non-Python languages; the mind-map interface end to end (zero anchor ids exist
  anywhere yet).
- **Merging to `main`.** Explicitly not covered by the human's approval.
