# Reviewer Handoff

## Gate
`g1` — verify + close primitives (of 3 gates; g2 adds reap + child-plan release, g3 composes `finish_work`)

## Survey State Location
Create your review survey checklist at `.agent-work/epic-567-door/cmdr-g/g1-review/review.json`.

## What Was Implemented
Three new functions in `scripts/spine_lifecycle.py`, plus tests:
- `done_refusal(spine, *, tree_clean, episodes_captured) -> str | None` — pure. Covers exactly two new checks (tree clean/staged, episodes captured), in that order. Does **not** call `closeout_refusal` and does **not** take an `archive_exists` argument.
- `_engine_call(argv) -> tuple[str, int]` — the module's single in-process choke point to `checklist_engine.main(argv)`; catches `SystemExit` (from `argparse`) and `EngineError`, plus a broad `Exception` clause for pre-`main()` failures (`parse_args`/`load()`); never raises.
- `_advance_and_release(spine_path, session_id, *, root, why=None) -> dict` — impure, via `_engine_call` only. Starts the active gate if `pending`, advances it (`--why` when given, else `--mechanical`), then releases. Returns a verbatim refusal and skips the release on any failed stage.

Plus 36 new tests in `tests/test_spine_lifecycle.py` (59 → 95).

**Context you need that a first read of the diff won't give you:** this worktree had a genuine, mid-run incident (documented in `RETURN.md` and the triage candidate at `.agent-work/567-g/triage-candidates/no-instrument-distinguishes-own-fork-writes-from-tampering.md`) in which a design-it-twice fork, sharing this Commander's own inherited context and lease identity, continued the run and dispatched a real `g1` implementer crew before the Commander corrected the handoff. That first implementer attempt built `done_refusal` against an early, buggy draft that delegated to `closeout_refusal` (refusing on every legitimate call — the exact defect both `PLAN_CRITIQUE.md` and `PLAN_CRITIC.md`, two independent cold critiques, found). The Commander corrected the handoff and abandoned that attempt in `crew-runs.json`; a second implementer dispatch found the buggy code already in the tree, independently re-confirmed the same defect from source, fixed `done_refusal` (removed the delegation and the `archive_exists` param), and left `_engine_call`/`_advance_and_release` — which were already correct — untouched. This is why the diff's history is unusual; the **final diff in the tree now** is what you are reviewing, not any intermediate state.

## How to Inspect the Diff
Uncommitted working tree in `/home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease`. Use `git status --porcelain` then `git diff -- scripts/spine_lifecycle.py tests/test_spine_lifecycle.py` (not `--name-only`).

## Task Statement
Add the three verify/close primitive functions above per `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g1-implementer-handoff.md` (the corrected version — it carries a "REWORK NOTE, load-bearing" paragraph under function (a); read the whole file, that note is the operative spec for `done_refusal`).

## Close Criteria
- `done_refusal`, `_engine_call`, `_advance_and_release` exist in `scripts/spine_lifecycle.py`.
- **`done_refusal` does NOT call or reference `closeout_refusal` anywhere in its own source** (docstring included) and does **not** accept an `archive_exists` parameter. This is the single most important thing to verify — it is the actual bug this rework exists to fix. Confirm with a source-text check yourself, not by trusting the implementer's own test for it: `python3 -c "import sys; sys.path.insert(0,'scripts'); import spine_lifecycle as sl, inspect; print('closeout_refusal' in inspect.getsource(sl.done_refusal))"` must print `False`.
- `done_refusal` is genuinely pure — no `Path`, `open`, `subprocess` in its body.
- `_engine_call` is the only call site of `checklist_engine.main` in `scripts/spine_lifecycle.py` — confirm: `grep -n "checklist_engine.main" scripts/spine_lifecycle.py` shows exactly one line, inside `_engine_call`'s own definition.
- `_advance_and_release`: a refused `advance` never attempts `release` (`engine_session.status` stays `"active"` on refusal) and passes the engine's refusal text through **verbatim**.
- The HARD-band path is genuinely exercised: a fixture gauge at/over the hard band, a why-less close refused with the engine's own "cannot be closed silently" wording, the same fixture closing cleanly once a `why` is supplied.
- `closeout_refusal` and `close_work` are byte-for-byte unchanged (still called from exactly one place — inside `close_work`).
- Fenced files empty diff: `git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py` must be empty.
- Full `tests/test_spine_lifecycle.py` green.

## Allowed Scope
`scripts/spine_lifecycle.py` (the three functions only), `tests/test_spine_lifecycle.py` (tests/fixtures/helpers for them).

## Specific Exclusions
`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, `scripts/hooks/spine_rail.py` — fenced, lane A's this wave, must show empty diff. `closeout_refusal`/`close_work` must be unchanged. `force_reap`, `_release_child_plans`, `finish_work`, `open_pr`, the CLI are g2/g3 — out of scope for g1, their absence is not a defect here.

## Constraints the Implementation Must Respect
- Never run against a live spine file — the implementer's own evidence must show fixtures under `tmp_path` only, and a read-only `validate_spine.py` check against this Commander's own `execute.json` (read, never written).
- POSIX-form commands; `PYTHONIOENCODING=utf-8` for captured subprocess output.

## Map Anchors (inbound)
- **Structural:** `scripts/spine_lifecycle.py` — `closeout_refusal` (:122-161), `close_work` (:384+). `scripts/checklist_engine.py` — `advance` (:2468), `release` (:1133), `main` (:3495) — read-only.
- **Capability:** mechanical-closeout verify + close primitives (#574 contract sketch steps 1-2).
- **Constraints/assumptions:** file-ownership fence; never test on a live lease.
- **Decision anchors:** `decision:library-reuse-over-file-edit` — the close sub-step calls `checklist_engine.main(argv)` in-process via `_engine_call`, mirroring `mcp_spine_server.py`'s existing pass-through pattern, never editing that file.
  `@grade: settled/measured · leans g1-implement,g3-implement`
- **Evidence expectations:** `done_refusal` must contain no reference at all to `closeout_refusal` — this is the load-bearing check for this whole gate.

## Evidence Produced
See `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g1-implementer-result.md` in full — it is thorough (pasted test bodies, pre/post counts, byte-identity comparisons against a separate-process engine run). The Commander independently re-ran the full suite and the source-text check before dispatching you; both passed. Verify them again yourself rather than trusting either account — that is the point of this gate.

## Suggested Model Tier
Sonnet — bounded, the review's one load-bearing check (no `closeout_refusal` reference) is mechanically verifiable.

## Stop Conditions
BLOCK if: `done_refusal` references `closeout_refusal` anywhere; a fenced file shows a non-empty diff; the suite is not green; the HARD-band test doesn't genuinely exercise the hard-band code path (e.g. a gauge fixture that silently collapses to no reading — check the four preconditions the implementer's own report names: gate `in-progress`, active lease, `observed_at >= claimed_at`, model in `gauge_reader._PROFILES`).

## Return Format
Return `REVIEW_RESULT` (verdict APPROVE/BLOCK, per-check findings, blockers, out-of-scope observations, workflow feedback) to `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g1-reviewer-result.md` before ending your turn.
