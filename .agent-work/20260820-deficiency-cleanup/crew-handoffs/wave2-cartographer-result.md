# Cartographer Result — Wave 2 map lane

Worktree: `/tmp/constellation-20260820-integration`, branch `afk/20260820-deficiency-integration`.
Base: `896b3610` (merge of #613 into Wave 1 integration base `d3d0c9ac`).
Result commit: `efe92791d74105164cab64e2aa80f442d4541597` — "chore: regenerate root map/ (post Wave1+#613 integration base)".

## Surface 1 — root `map/`: regenerated

Ran `python -m scripts.code_map build --root .` at `896b3610`. Only `map/INDEX.md` changed; `map/ids.jsonl` had no diff (`git diff --stat map/ids.jsonl` empty). No source, test, or `.agent-work/` file is in the commit — `git show --stat efe92791` shows exactly `map/INDEX.md | 16 ++++++++--------`, `1 file changed`.

Exact diff shape — enumerated every changed line (`git diff | grep -E '^[+-]' | sort | uniq`), six paired entity/hole-count changes, nothing else:

| line | before | after |
|---|---|---|
| `scripts:` total | 1258 entities | 1274 entities |
| `tests:` total | 5266 entities | 5291 entities |
| `scripts.run_crew` | 68 entities, 12 holes | 84 entities, 23 holes |
| `tests.test_crew_launcher` | 322 entities, 245 holes | 338 entities, 259 holes |
| `tests.test_checklist_engine` | 648 entities, 495 holes | 653 entities, 500 holes |
| `tests.test_mcp_lifecycle` | 44 entities, 24 holes | 48 entities, 28 holes |

This matches the handoff's predicted shape (entity-count-only, no new modules, no format change) on all six named lines. One deviation from the *predicted numbers*, not the *shape*: the handoff's Admiral measurement said `tests.test_mcp_lifecycle` would be "unchanged in count," but it moved 44→48. I did not treat this as a stop condition because the change is still a plain entity-count delta on an already-named line, not a new kind of diff content. I verified independently that this delta predates #613: a scratch build at `d3d0c9ac` (Wave 1 base, before #613) already shows `tests.test_mcp_lifecycle` at 48 entities/28 holes. Tracing `git log --oneline 24b4665b..896b3610 -- tests/test_mcp_lifecycle.py scripts/mcp_spine_server.py` shows the source changes came from Wave 1 commits `7b55c477` ("fix: wire spine close through finish work") and `5891e80f` ("test: prove spine close refusal atomicity"), part of #638 — not from #613 (#613 is commit `8137814e`, which touches only `scripts/run_crew.py` and `tests/test_crew_launcher.py`, confirmed via `git show --stat 8137814e`). So this is a small inaccuracy in the Admiral's pre-measurement, not a build surprise — no stop, no report-as-finding beyond this note.

## Surface 2 — `docs/architecture/`: honest null

Evidence, exact paths and exact output:

- `find docs/architecture -type f` → only `docs/architecture/generated/map.json`. No `docs/architecture/packets/`, no `docs/architecture/overlays/`, no `docs/architecture/index.md` exist anywhere in the tree.
- `wc -c docs/architecture/generated/map.json` → `75 docs/architecture/generated/map.json`. Content:
  ```json
  {
    "findings": [],
    "nodes": [],
    "relationships": [],
    "version": 1
  }
  ```
- `python scripts/build_architecture_map.py --check --root .` → exact stdout: `architecture map inputs are valid`.
- Why the map is empty, read from `scripts/build_architecture_map.py:343-386`: `build_architecture_map()` builds nodes/relationships only from `docs/architecture/packets/*.md` and `docs/architecture/overlays/*.yml` (both globbed only `if packets_root.exists()` / `if overlays_root.exists()`, else skipped entirely with no error), plus a source-tree scan (`scan_source_tree`) rooted by default at `source_roots=("src",)`. This repo has no `src/` directory either (`ls -d src` → "No such file or directory"; top-level dirs are `docs/ episodes/ evals/ examples/ map/ scripts/ skills/ specs/ tests/`). So all three input classes — packets, overlays, and the default source-scan root — are simultaneously absent, and `validate_map` has nothing to reject: zero nodes, zero relationships pass validation trivially, hence `--check` reports success on an empty map.
- This is a property of the repository, not a defect of this epic: `skills/commander/references/commander-core.md:163` already names this shape in doctrine — "Where the run has no packet map (e.g. a skill-source repo with no `docs/architecture` map), reconcile the structural record directly" — i.e., this repository is the named example of the no-packet-map case, and Commander's own reconciliation path already accounts for it without treating it as a gap to close.
- What a future packet map would need: at least one `docs/architecture/packets/*.md` (or `docs/architecture/overlays/*.yml`) authored against `templates/ARCHITECTURE_PACKET.template.md`/`templates/ARCHITECTURE_INDEX.template.md` from the cartographer skill, naming real nodes/relationships in this repo's `scripts`/`tests`/`skills` layout (there is no `src/` to fall back on for a bare source-scan). The human ruled 2026-08-21 against commissioning one now — that authoring is explicitly out of scope for this lane.

No packet map was authored. No `docs/architecture` file was touched.

## Verification (exact output)

`python -m pytest -q tests/test_code_map.py -k MapTreeFreshness`:
```
..                                                                       [100%]
2 passed, 146 deselected in 5.20s
```

`python scripts/build_architecture_map.py --check --root .`:
```
architecture map inputs are valid
```
(no output written, per `--check`)

Ordinary suite, **before** regenerating the map (on the same `896b3610` base, map/ still stale):
```
=================================== FAILURES ===================================
_ MapTreeFreshnessTests.test_map_tree_freshness_root_index_matches_a_fresh_build _
...
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
1 failed, 3446 passed, 6 skipped, 1222 subtests passed in 140.18s (0:02:20)
```
Only the map-freshness test was red before this lane's change; nothing else needed repair.

Ordinary suite, **after** regenerating and committing `map/`:
```
3447 passed, 6 skipped, 1222 subtests passed in 142.54s (0:02:22)
```
Suite is green.

## Orientation — modules the #634/#638/#632/#357/#369/#615 cluster lives in

Read from the freshly built map (`map/INDEX.md` and each module's own `map/<module>/INDEX.md`). Descriptive only — no proposal, evaluation, or preference between future architectures; that is the two downstream candidates' work.

**`scripts.checklist_engine`** — `scripts/checklist_engine.py`, 3811 lines, 112 entities, 25 holes (undocumented entities, mechanically counted — e.g. `emit_step_manifest`, `_load_gauge_reader`, `EngineError.__init__` are each flagged "HOLE: no docstring" in their own `.md` page). Module docstring: "Workbench checklist engine: work one gated/survey plan through its gates. The engine holds the canonical state; an agent transacts with it one step at a time. It enforces *mechanism* ... and never judges quality." Recorded imports: stdlib only, plus one third-party import, `episode_capture.emit_step_manifest`. Recorded "imported by": none found.

**`scripts.mcp_spine_server`** — `scripts/mcp_spine_server.py`, 2589 lines, 38 entities, 3 holes. Module docstring: "MCP front door for the checklist engine ... This server WRAPS the engine — it never reimplements it. Every tool builds an argv and calls `checklist_engine.main(argv)`." Recorded third-party imports: `apply_episode_delta`, `checklist_engine`, `episode_capture`, `spine_lifecycle`. Recorded "imported by": none found.

**`scripts.spine_lifecycle`** — `scripts/spine_lifecycle.py`, 1203 lines, 28 entities, 3 holes. Module docstring: "Open and close Constellation work in one call each: `open_work` builds a worktree, a branch, a scaffolded work area, and a compiled, origin-stamped spine; `close_work` moves that work area into the archive, spine last..." States a pure/impure split at function granularity (`worktree_path_for`, `branch_name_for`, `archive_name_for`, `build_origin`, `closeout_refusal` are pure; `open_work`, `close_work`, `_engine_call`, `_advance_and_release` are impure). Recorded third-party imports: `checklist_engine`, `generate_spine`, `init_work_area`, `run_crew`, `spine_rail`, `validate_spine`, `verify_worktree_isolation`. Recorded "imported by": none found.

**`scripts.run_crew`** — `scripts/run_crew.py`, 2591 lines, 84 entities, 23 holes. Module docstring: "Safe crew launcher with a durable session-recovery registry. Commander must never hand-launch crew sessions." Notes deliberate testability seams: `build_crew_argv` (pure), `launch_process` (the only real-subprocess spawn point, monkeypatched in tests), plus pure registry read/write, session-name generation, duplicate detection, and result-artifact verification. States explicitly: "This wrapper does NOT advance gates, merge PRs, repair git, or integrate results." Recorded third-party imports: `checklist_engine`, `install_constellation`. Recorded "imported by": none found.

**Dependency direction, as the map records it**: every one of these four modules shows "imported by: none found" — the map's static-import scan does not resolve reverse edges for this cluster (worth naming as a documented map limitation: these files import each other by bare module name, e.g. `import checklist_engine`, rather than as `scripts.checklist_engine`, and the map's own "imports third-party" bucket picks that up as a forward edge but its "imported by" resolution does not connect it back). Reading the forward `imports third-party:` lines instead gives the graph: `scripts.mcp_spine_server` imports `checklist_engine` and `spine_lifecycle`; `scripts.spine_lifecycle` imports `checklist_engine` and `run_crew` (plus `generate_spine`, `init_work_area`, `spine_rail`, `validate_spine`, `verify_worktree_isolation`); `scripts.run_crew` imports `checklist_engine` (plus `install_constellation`). `scripts.checklist_engine` itself imports none of the other three — its only non-stdlib import is `episode_capture`. So as recorded, `checklist_engine` sits underneath the other three; `mcp_spine_server` and `spine_lifecycle` both sit above it directly, and `spine_lifecycle` also sits above `run_crew`.

## Workflow friction

1. **Diff-shape false alarm, resolved by an out-of-band check.** The handoff's stop condition ("anything that is not an entity-count or module-listing change") is about diff *shape*, but the accompanying prediction table gave specific numbers per module, including "unchanged" for `tests.test_mcp_lifecycle." When the actual regen showed that module moving, it read at first glance like a possible stop-and-report case. I resolved it by doing a scratch build at `d3d0c9ac` in a throwaway copy to confirm the delta predates #613 and is a plain entity-count change consistent with the permitted shape — not a genuine anomaly. Worth a note for future Cartographer handoffs: distinguish "diff shape" stop conditions from "predicted magnitude" mismatches explicitly, since the latter will legitimately drift as more work lands on a branch between when a prediction is made and when the lane actually runs.

2. **Self-inflicted worktree-metadata hazard, recovered cleanly.** To do the scratch-build check above, I `cp -r`'d the integration worktree to a scratch location and ran `git checkout -f d3d0c9ac` there. A git worktree's `.git` is a pointer file into the main repo's `.git/worktrees/<name>/` admin directory (HEAD, index) — copying the *working directory* copies that pointer file too, so the checkout in the copy silently repointed the **real** integration worktree's shared HEAD/index to `d3d0c9ac`, even though I never `cd`'d into the real worktree. `git status` in the real worktree then showed `scripts/run_crew.py` and `tests/test_crew_launcher.py` as spuriously "modified" and `.agent-work/20260820-issue-613/` as untracked, because git was diffing the (untouched, correct) on-disk files against the wrong tree. Recovered non-destructively: confirmed the branch ref `afk/20260820-deficiency-integration` still pointed at `896b3610` (untouched — only the detached-HEAD-via-shared-gitdir moved), then `git reset --mixed 896b3610` (rewrites HEAD + index only, touches no working-tree file) followed by `git checkout afk/20260820-deficiency-integration` (no-op switch since HEAD already matched the branch tip). Verified afterward with `git diff 896b3610 -- scripts/run_crew.py tests/test_crew_launcher.py` (empty) and `git status --porcelain` (only `map/INDEX.md`, my intended change) before committing. No working-tree file was ever actually altered by the mishap; only shared git metadata was, and only briefly. Lesson for future scratch-verification work against a linked worktree: never `cp -r` a linked worktree's own directory and `git checkout` inside the copy — use `git worktree add` (a genuinely separate admin dir) or `git archive`/`git show` into a fresh directory instead.

3. No other friction. The lane ran fully unrailed as instructed; no `mcp__spine__*` tool was called.
