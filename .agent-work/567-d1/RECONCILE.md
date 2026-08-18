# Architecture reconcile — lane D1 (#559)

**No packet map exists in this repo.** `map_orient` returns `DEGRADED-UNPARSEABLE`: there is no
`docs/architecture` packet map, `map/INDEX.md` carries no citable anchor id, and `map/ids.jsonl` is
empty (receipt: `.agent-work/567-d1/map-orientation.json`). No Cartographer subagent was dispatched,
because the default packet-map path has nothing to fold into. Per this step's own imperative, the
structural record is reconciled **directly** instead. This is not a no-op: two structural records
this change actually touches were updated in the run itself, and one new fact is recorded here.

## 1. Folded into the record it actually touches — `specs/*.spine.toml`

These two files **are** the structural record of what a gated role plan and a survey role plan are,
and they are the only role specs that exist. Gate `g3` folded the change into them directly: both now
name the door as the interface for the spine a role was launched against, and both state the boundary
that governs it — one door drives one spine at a time, so a second checklist is not reachable from a
process already holding its own lease, while a role dispatched without a spine arrives holding no
lease and binds its own plan directly.

That boundary is the structural fact this epic changes, and it is now recorded where a role reads it
rather than only in a run artifact.

## 2. Folded into the record that defines the checked surface — `tests/test_mcp_adoption.py`

That module's header is this repo's written definition of "agent-facing instruction text", and its
first rule is *"the corpus is WALKED, never listed."* Gate `g2` inverted the nine assertions that
required the CLI text and left both of the module's own rules intact; the walk itself is unchanged
and is now **imported** by the new guard rather than re-derived, so the repo holds exactly one such
definition instead of two that agree today and drift tomorrow.

## 3. New structural fact, recorded here because no existing doc owns it

**`.agent-work/templates/**` is now agent-facing instruction text with a machine check on it.**
Before this run it was read by no walk in the repo, while workbench doctrine told agents to *prefer*
it over the bundled `skills/` copy when instantiating. It is now inside
`tests/test_cli_retirement_guard.py`'s walk, with its own ≥60-file vacuity floor and an assertion
that the rule reaches the overlay and **not** a live run's own artifacts.

The residual structural concern is staged as triage, not fixed here: the same doctrine now exists in
**four** tracked copies — the `skills/` source, the overlay, the `.baseline/` mirror, and
`TEMPLATES_MANIFEST.json`'s hashes — with no automatic reconciler between them
(`triage-candidates/overlay-baseline-mirror-doubles-every-target.md`,
`triage-candidates/templates-manifest-is-a-fourth-copy.md`).

## 4. Deliberately not touched

`map/INDEX.md` is Admiral-owned and stale by construction on every parallel branch (#544);
`MapTreeFreshnessTests` is accepted red on this branch and the Admiral regenerates once on merged
`main`. `docs/agents/*` is the human's call (`decision:no-doctrine-promotion`), and
`docs/superpowers/**` are historical records.

## Decision candidates carried out of this run

- `decision:guard-scope-is-the-existing-corpus-walk` — settled/measured, exception list length zero,
  now extended to `specs/**/*.toml` and `.agent-work/templates/**`.
- `decision:guard-is-authored-first-against-the-dirty-tree` — settled/measured.
- `decision:second-checklist-clauses-are-reworded-not-deleted` — settled by the Admiral at F-1, with
  this run's correction to its supporting reasoning recorded in `notes-1.md`.
