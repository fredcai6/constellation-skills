# Prep Brief: build the full f1Brainz derived map (cycle 4, prep-fullmap)

## Task

Build the complete derived map of f1Brainz — statements, supplement, agent-lean per-entity pages, ids.jsonl — under `evidence/x13/map/`. This is mechanical adaptation of proven excursion tooling, not new design.

## Hard constraints

- `C:\Programs\f1Brainz` is READ-ONLY. All outputs land in `.agent-work/explore-code-map/evidence/x13/` (this worktree).
- Do NOT modify anything in `evidence/x7b/` or `evidence/x11/` — they are frozen excursion evidence. COPY scripts into `evidence/x13/` and adapt the copies.
- Template text pure ASCII; docstrings verbatim (their non-ASCII is source truth).
- Do NOT `git add`/commit — the orchestrator handles git (bulky derived artifacts get gitignored).

## Inputs (all exist)

- `evidence/x13/slice_manifest.json` — 1,224 files: all .py under f1Brainz `src/`, `scripts/`, `tests/` (`core` = all files, `importers` empty).
- `evidence/x7b/astx.py` — the ruled extractor. Its `main()` reads `slice_manifest.json` beside itself; `ROOT` is f1Brainz; **pass1 only indexes `src/`** (`SRC = ROOT/src`).
- `evidence/x11/supplement.py` — AST supplement pass (kind, signature, span, doc body, attrs, decorators, `__all__`), currently scoped to `src/utils`.
- `evidence/x11/render.py` + `render_fn.py` — data loading + the agent-lean per-entity renderer (the ruled rendering: one page per entity, entity id as title, plain lines, no decoration; module INDEX.md; top INDEX.md).

## Steps

1. Copy `astx.py` → `evidence/x13/astx.py`. Patch the copy: pass1 must index module tables for **src/ AND scripts/ AND tests/** (so names defined in scripts/tests resolve — e.g. `scripts/validate_segment_map_662.py` defines functions that src and tests call); manifest and outputs read/write in `evidence/x13/`. Treat every manifest file as core. Run it. Record parse failures.
2. Adapt supplement → `evidence/x13/supplement.py` over all 1,224 files. Same fields as x11's.
3. Write `evidence/x13/render_map.py` — a self-contained adaptation of `render_fn.py`'s lean rendering (copy its logic; load from x13 paths; derive the module list from the extracted statements instead of a hardcoded list). Output tree: `evidence/x13/map/<dotted.module>/INDEX.md` + one `.md` per entity, `evidence/x13/map/INDEX.md` on top. Keep the D1 correction (+1 on `q.line`). For the top INDEX with ~hundreds of modules, group by top-level package (src / scripts / tests) so it stays a routing surface.
4. Emit `evidence/x13/map/ids.jsonl` — the id→symbol-path lookup. No anchor comments exist in f1Brainz yet, so it will be EMPTY: still write the (empty) file; it establishes the well-known location.
5. Self-checks, all recorded in the result: (a) rebuild twice, `diff -r` the two map trees — must be identical (determinism); (b) non-ASCII scan over pages — template-sourced non-ASCII is a bug, docstring-sourced is fine; (c) entity count from statements vs supplement AST count — reconcile or explain; (d) spot-check that `scripts/validate_segment_map_662.py`'s entities got pages and that `split_half_boundary_drift`'s page shows its callers in `referenced by` (this page is the trial's entry point — it must be right).

## Return

`excursions/prep-fullmap-result.md`: counts (files parsed / failures, statements, entities, pages, holes), wall time per stage, the four self-check outcomes, and anything that surprised you (scale problems, resolution-rate changes vs the 9-file slice, noisy page classes). Your final text is a short data payload: status + counts + result path.
