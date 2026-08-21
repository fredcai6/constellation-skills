# Cartographer Handoff - Wave 2 map lane

## Task

On the post-#613 integration base, restore both current-map surfaces to honest current truth and return the ordinary repository suite to green.

## Base

- Worktree: `/tmp/constellation-20260820-integration`
- Branch: `afk/20260820-deficiency-integration`
- Base commit: `896b3610` (merge of #613 into the Wave 1 integration base `d3d0c9ac`)

## Surface 1 — root `map/`: regenerate

Root `map/` is stale on this branch because Wave 1 (#500, #636, mechanical #638) and #613 added code without regenerating. It is current on `main`; the staleness is this branch's alone.

```
python -m scripts.code_map build --root .
```

Only two files under `map/` are tracked: `INDEX.md` and `ids.jsonl`. The per-module subdirectories the build emits are untracked by design — see `tests/test_code_map.py::MapTreeFreshnessTests` and `.agent-work/issue-456/landing-zone-measurement.md` for why. Do not add them.

The Admiral measured the expected delta against a scratch build at `d3d0c9ac`: `map/INDEX.md` only, six line-pairs, all entity counts — `scripts` 1258→1274, `tests` 5266→5288, `scripts.run_crew` 68→84, `tests.test_crew_launcher` 322→335, `tests.test_checklist_engine` 648→653, `tests.test_mcp_lifecycle` unchanged in count. Adding #613 will move `run_crew`/`test_crew_launcher` further. **If the regenerated diff contains anything that is not an entity-count or module-listing change, stop and report it** — that would mean the build is seeing something we did not expect, and it is a finding, not a commit.

Commit `map/` alone. No source, test, or `.agent-work/` file belongs in that commit.

## Surface 2 — `docs/architecture/`: evidenced honest null, do not author

`docs/architecture/generated/map.json` is 75 bytes of empty arrays. It is empty because this repository has never had curated inputs: no `packets/`, no `overlays/`, no `index.md`. `build_architecture_map.py` builds only from those, and `--check` reports "architecture map inputs are valid" on empty inputs, so no script run can fill it.

**Do not author a packet map.** The human ruled on 2026-08-21 that commissioning one would widen the epic. `skills/commander/references/commander-core.md:163` already names this repository's shape — a skill-source repo with no `docs/architecture` map — and rules a reasoned no-op compliant there.

Your deliverable for this surface is an **explicitly evidenced honest null**: state what exists, what does not, why the generated map is empty, why that is a property of the repository rather than a defect of this epic, and what a future packet map would have to be built from. Cite the exact paths and the exact `--check` output. This is what satisfies the wave exit criterion's "or explicitly evidenced" branch.

## Verification

Run and quote exact output:

- `python -m pytest -q tests/test_code_map.py -k MapTreeFreshness` — both tests pass.
- `python scripts/build_architecture_map.py --check --root .` — record the exact result; do not write output.
- The ordinary repository suite: `python -m pytest -q`. Report the full counts. If anything other than map freshness was red before your change, say so plainly and do not repair it — it is a separate finding.

## Bounded extra deliverable — orientation for the architecture lanes

Two independent architecture candidates run after you, on the cluster #634 / #638 / #632 / #357 / #369 / #615: one-spine elimination and explicit parent-capability transitions. They will ground on root `map/` plus source, because there is no packet map.

From the freshly built map, write a short orientation section naming the modules and seams that cluster actually lives in — at minimum `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `scripts/spine_lifecycle.py`, `scripts/run_crew.py` — with their entity counts, their documented holes, and the dependency direction between them as the map records it. Describe what is there. Do not propose, evaluate, or prefer any future architecture: that is the candidates' work and the human has not chosen.

## Scope fence

Allowed: `map/` (regenerated), your own report under `.agent-work/20260820-deficiency-cleanup/`.
Excluded: authoring `docs/architecture` packets or overlays; any source or test change; choosing or implementing an architecture; rewriting issue scope; push, PR, GitHub mutation, or merge to `main`.

## Engine rail

This lane runs **unrailed**. Do not call any `mcp__spine__*` tool — the door in your session is bound to the Admiral's epic spine and driving it would corrupt the run.

## Result

Write `.agent-work/20260820-deficiency-cleanup/crew-handoffs/wave2-cartographer-result.md` in the main checkout at `/home/tommy/projects/constellation-skills`: what you regenerated, the exact diff shape, the honest-null evidence for `docs/architecture`, the verification output, the orientation section, and any workflow friction. Do not commit that result.
