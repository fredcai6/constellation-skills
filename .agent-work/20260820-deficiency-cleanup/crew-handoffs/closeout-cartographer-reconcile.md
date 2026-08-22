# Cartographer reconcile — epic closeout, `24b4665b..5858a85c`

Role: `skills/cartographer/SKILL.md`. Scope: architecture-map reconcile only,
read-only against the repo. No `mcp__spine__*` calls made (door is bound to
the Admiral's epic spine). No commits, no source/test/map edits.

## 1. Root `map/` freshness

```
python -m pytest -q tests/test_code_map.py -k MapTreeFreshness
2 passed, 146 deselected
```

`map/INDEX.md` and `map/ids.jsonl` — the only two tracked files under
`map/` (`.gitignore` lines 73–75: `map/*` then `!map/INDEX.md`,
`!map/ids.jsonl`; per-module packet subdirs are regenerated-on-demand local
artifacts, untracked by design) — match a fresh build from current tracked
source. Root map is current.

Three regen commits cover this range: `efe92791` (post-Wave1+#613 base),
`99a46a08` (batch A+B), `8957d925` (F1/F2 --parent doctrine + regression).
All three commit messages self-report entity-count-only diffs (no module
added/removed, no link retargeted, no docstring rewritten), and I confirmed
the actual `map/INDEX.md` diff across the full range matches that shape:
module/entity counts (`scripts` 1258→1277, `tests` 5266→5323,
`scripts.hooks` 87→89, `scripts.checklist_engine` 112→113,
`scripts.hooks.spine_rail` 65→67, `scripts.run_crew` 68→84, plus several
`tests.*` node counts) with the module-listing shape and every one-line
module description unchanged. No structural entries changed.

Aside (not a map defect): my working tree still holds a stale, gitignored
`map/scripts.mcp_spine_server/_spine_close.md` packet left over from an
earlier local build — it still describes the pre-epic `close_work`/
no-arguments shape. This is expected and immaterial: per-module packets
aren't tracked, aren't committed, and aren't covered by
`MapTreeFreshnessTests` (which only polices `INDEX.md`/`ids.jsonl`). Noted
so a future reader isn't confused by stray local artifacts; nothing to fix
in the repo.

## 2. `docs/architecture/` honest null

Confirmed: `docs/architecture/` contains only `generated/` — no `packets/`,
no `overlays/`, no `index.md`, and none exist anywhere else in the tree
(repo-wide search found only `map/**/INDEX.md`, which is the auto code map,
not the packet-layer `index.md`).

```
python3 scripts/build_architecture_map.py --check
architecture map inputs are valid
```

Reports valid on the empty set, as expected. The null holds. Nothing in
this epic's diff touches `docs/architecture/`, adds a `packets/` or
`overlays/` directory, or otherwise disturbs the 2026-08-21 human ruling
against commissioning a packet map. I did not author one.

## 3. Structural vs. behavioural

**No structural change.** Every production change in this range lands
inside already-mapped modules, calling already-mapped (or newly-added,
same-module) functions, with no new module, no new cross-module dependency
edge, no reversed dependency direction, and no ownership transfer:

- **#500** (refresh-request consumption): `checklist_engine.py`
  `has_pending_refresh_request`/`attach` gain a `lease_claimed_at` stamp
  comparison — internal state-machine correction inside the engine module,
  no new seam.
- **#636** (crew-registry concurrency + exact identity/worktree selection):
  `run_crew.py` gains `registry_lock`, `registry_transaction`,
  `append_registry_entry`, `mutate_registry_entry`,
  `_write_registry_atomic` and a rewritten `_parent_lease_heartbeat`. This
  is real new internal machinery (file locking around the registry file),
  but it is a same-module, same-owner concurrency-safety addition — not a
  new module, not a new external dependency, not a boundary change. The
  auto code map already reflects it as an entity-count delta
  (`scripts.run_crew` 68→84 entities), captured by the `efe92791` regen.
- **#638 mechanical half** (spine-close refusal atomicity + telemetry):
  `mcp_spine_server._spine_close` now calls
  `spine_lifecycle.finish_work(...)` instead of
  `spine_lifecycle.close_work(...)`, with a wider, required-argument tool
  schema (`tree_clean`, `episodes_captured`, `push`, `open_pr`, optional
  `why`) replacing the old zero-argument call. This is a materially
  different **contract** for the `spine_close` MCP tool (more readiness
  assertions demanded of the caller, one call now does verify + release
  children + advance/release + reap + archive + optional
  push/PR), but `finish_work` was already an existing, already-mapped
  function on the already-depended-on `spine_lifecycle` module (confirmed:
  zero diff to `scripts/spine_lifecycle.py` in this range, and
  `scripts.spine_done_cli`'s map description already named
  `spine_lifecycle.finish_work` before this epic). No new module, no new
  dependency edge — a rewiring of which existing function on an
  already-mapped dependency gets called, plus a widened caller-facing
  schema.
- **#613**: suppressing the redundant inherited parent-heartbeat writer is
  a behavioural de-dup inside `run_crew.py`'s heartbeat logic.
- **Batch A**: `RAIL_VERBS` membership, the archived-path banner/rail
  suppression, the lease-line render (`HELD` + age vs. `active`), the
  `next (for the holder):` label, `_scan_active_spine` staleness gating,
  and `require_session`'s refusal-text rewrite are all display/advisory
  text and gating-condition changes on existing surfaces. No new module,
  no new file, no dependency change.
- **Batch B**: exempting `waive` from the session gate (one added
  condition in `require_session`, deliberately kept in `MUTATING_VERBS` so
  journaling still fires) and making `--parent` required on `run_crew`
  (documented in `skills/commander/references/crew-dispatch.md`) are
  control-flow/interface-signature changes within existing functions, not
  new structure.

The `docs/agents/AGENT_GUIDE.md` consolidation (`a0777cfd`: retiring
`SKILL_INDEX.md` and `docs/POSITIONING.md` into one orientation doc, with
`AGENTS.md`/`CLAUDE.md` as pointers) is repo-orientation documentation, not
architecture-map territory — it doesn't touch `docs/architecture/` or
`map/`, and Cartographer owns `index.md`/`packets/`/`overlays/`/map/
`MAP_BUILD.md`, not root orientation docs. Out of scope for this reconcile,
noted only to confirm it isn't masking a structural move.

An evidenced "no structural change" is the complete, expected answer here:
this epic hardened concurrency safety, tool-contract atomicity, and
operator-facing advisory text on existing seams; it did not add, remove, or
redirect one.

## 4. What the map now misrepresents or under-describes

Nothing in the **tracked** map (`map/INDEX.md`, `map/ids.jsonl`) — it is
current and entity-count-accurate as of `5858a85c` (§1).

Nothing in the **docs/architecture packet layer** — it remains an
evidenced empty null, unaffected by this epic (§2).

One item worth a future reader's attention, outside my authority to change
today: `spine_close`'s tool description in
`scripts/mcp_spine_server.py`'s `LIFECYCLE_TOOLS` (and its module docstring
around line 163) already carry the new `finish_work`-composition behavior
accurately — the *source* documents itself correctly. The only thing that
doesn't is the stray local `_spine_close.md` packet noted in §1, which is
gitignored/uncommitted and self-heals on the next local rebuild — not a
repo-state defect.

## Verdict

Root map current (test green). `docs/architecture` null confirmed still
valid, not authored. Net change across all five lanes plus batch A/B is
concurrency-hardening, tool-contract-atomicity, and display/advisory-text
work on existing seams — no new module, no changed ownership, no changed
dependency direction. No map or docs/architecture edits made or needed.
