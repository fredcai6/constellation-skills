# Cartographer reconcile — epic-178 (Context Governor v1) — result: honest null (recurrence of epic-138)

Checklist driven end-to-end: `.agent-work/epic-178/cartographer-reconcile.json` (context -> advanced with `--why`; packets, index-overlays -> skipped OBE; map-compliance -> advanced with `--why`, one triage candidate flagged, released). Journal is the proof of record; this file summarizes it for the crew.

## Task

Reconcile the architecture map of `constellation-skills` with the epic-178 net change merged to main (diff `54f5965...e4e56a3`, 5 PRs: #179 why-capture + refresh primitives, #180 gauge writer PostToolUse hook, #181 gauge reader, #182 Trip two-band gate policy, #183 reach-up flow + job-file doctrine wiring).

## Finding

**No architecture map exists for this repo, and none ever has.** This is the second time this exact finding has been made — epic-138's cartographer run (2026-07-12, `.agent-work/archive/2026-07-12-epic-138-workarea/cartographer-result.md`, ratified in that epic's `ADMIRAL_LOG.md` closeout ruling) found and recorded the identical null. Re-verified independently for epic-178:

- No `docs/architecture/` directory anywhere in the working tree.
- `git log --all -- docs/architecture` and `git log --diff-filter=A --name-only --all | grep '^docs/architecture'` both return nothing — no commit, on any branch, has ever added a file under that path.
- No `packets/`, `overlays/`, `index.md`, or `MAP_BUILD.md`.
- No `docs/agents/` directory either (no `engine-config.json`, no `ORCHESTRATOR_CONTEXT.md`) — this repo has never run any of its own tier doctrine against itself; the map absence is one instance of a broader "factory repo doesn't dogfood its own scaffolding on itself" pattern.
- `docs/CONSTELLATION_OVERVIEW.md`'s Relationship Contract table still documents the *intended* contract (`docs/architecture/packets/` + `index.md`, consumed by Scout/Commander/Implementer/Reviewer/Docent) — the intent is on record, just never executed.
- `scripts/build_architecture_map.py` + `tests/test_build_architecture_map.py` remain real, working generator/validator tooling, still never pointed at this repo's own source tree.
- **GitHub issue #156** ("cartographer: initial architecture self-map of constellation-skills (never been mapped)") is already open and already seeded with a scope recommendation (containers-by-role split for `scripts/`, one container-per-skill for `skills/`, docs-as-overlays-not-structs, tests-as-verified-by-evidence-not-nodes). No duplicate triage candidate was filed here.

## Verdict

**Reconcile = honest null**, for the same reason as epic-138: there is nothing to reconcile the epic-178 net change against, because there is no baseline map. Producing a map now — even scoped only to epic-178's touched surface (`scripts/checklist_engine.py`'s why-capture/Trip additions, the new `scripts/gauge_reader.py`, the new `scripts/hooks/gauge_writer_hook.py`) — would misrepresent coverage: three fresh packets sitting alone would read as "this is what's mapped" when the other ~95% of the repo is equally unmapped and no more or less current. Partial coverage born from one epic's diff is sparse-by-accident-of-which-PRs-just-landed, not sparse-by-Inclusion-Rule, which is a worse signal than no map at all.

No map files were created or edited under `docs/architecture/`. No branch was created and no PR was opened, per this ruling.

## What the new subsystem WOULD need on the map, when #156 executes

Recorded here as forward-looking context for whoever eventually runs the initial build (not filed as new triage — #156 already covers the scope; this just adds epic-178-specific detail to that existing scope):

- **`scripts/gauge_reader.py`** is a clean new component: `read(path) -> Reading | None`, fail-safe (never raises), model-keyed thresholds. It's a good candidate for its own packet under the "Engine & Tooling" container from #156's recommendation — it's independently invoked, has a narrow contract, and other structs (the Trip gate policy inside `checklist_engine.py`) depend on it across a real boundary (reader owns parsing/fail-safety; engine owns policy).
- **`scripts/hooks/gauge_writer_hook.py`** is a second new component in the hook layer alongside `spine_rail.py` (already called out in epic-138's recommendation) — it crosses the same session-lifecycle-to-repo-state boundary (PostToolUse -> `.agent-work/<work_id>/gauge.json`), so it earns the same treatment: its own packet, not folded into `checklist_engine.py`'s.
- **The `.agent-work/<work_id>/gauge.json` file format itself** is worth a `capability:` or `constraint:` overlay anchor once the map exists — it's the portability seam between the writer hook and the reader (two independently-owned components on either side of a file contract), which is exactly the kind of cross-cutting behavior the Inclusion Rule wants captured as an anchor rather than left implicit in each component's prose.
- **The Trip two-band gate policy** (SOFT advisory / HARD refuse-advance) inside `checklist_engine.py` is cross-cutting enough (governs gate-boundary behavior for every checklist, not just one task) that it reads as a `capability:` node under the engine's existing sub-component packet (epic-138's recommendation already called out `_rail()` as warranting its own sub-component packet for the same reason — this is the same shape of finding).
- **Doctrine text added to `skills/_shared/global-*.md` and tier skills** (reach-up flow, job-file principle) stays as `capability:`/`constraint:` overlay prose per the existing recommendation — not new struct nodes.

## Code/docs mismatch found (flagged, not fixed — not Cartographer's artifact)

Confirmed and flagged as **triage candidate tc1** on the checklist (`.agent-work/epic-178/cartographer-reconcile.json`, `map-compliance` gate):

**`docs/CHECKLIST_SCHEMA.md` is stale against epic-178.** It documents the schema as of pre-epic-178 and is missing:
- top-level append-only `why_trail`
- per-task `why_exempt`
- the `--why`/`--mechanical` advance interface (fail-closed — confirmed live: my own `advance context` call above was refused until I supplied `--why`)
- `DIGEST:`/`REFRESH REQUESTED:` lines on `current` output
- the `refresh-request` evidence type
- the `has_pending_refresh_request(cl, gate)` predicate
- the Trip two-band (SOFT advisory / HARD refuse-advance) gate policy

This is a real mismatch, but `docs/CHECKLIST_SCHEMA.md` is not a Cartographer-owned artifact (Cartographer owns `index.md`/`packets/`/`overlays/`/`MAP_BUILD.md` under `docs/architecture/`, which doesn't exist) — no `depends-on`/`explained-by` edge exists to fix because there's no map node to hang it from. It routes to whoever owns schema-doc currency (Charter, per the Relationship Contract table's "Charter | engine config" row and general doctrine-doc ownership) as a docs-update triage item, folded into or filed alongside #156 rather than duplicated.

## Artifacts

- `.agent-work/epic-178/cartographer-reconcile.json` — the driven checklist (journal is the proof: context advanced, packets/index-overlays skipped-OBE, map-compliance advanced with tc1 flagged, lease released).
- `docs/architecture/` — unchanged (does not exist).
- Issue #156 — unchanged, still the correct home for the initial-build work; not duplicated here.
