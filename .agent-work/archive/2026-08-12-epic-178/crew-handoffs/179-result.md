# Result: issue #179 — Why-capture + refresh primitives (engine schema)

## Verdict: DONE

Implemented Modules 1 & 4 of the CONFIRMED spec in `scripts/checklist_engine.py`, backed by fixture-based unit tests. All six acceptance criteria pass, plus legacy-shape drivability and CLI round-trips. Backward compatibility verified against the live `.agent-work/epic-178/spine.json`. One-concern diff inside the fence. PR: https://github.com/fredcai6/constellation-skills/pull/185

**Summary.** A non-exempt `advance` now solicits a single running `--why`; silence fails closed (engine-enforced refusal, not agent discipline), with a distinct `--mechanical` flag to discharge it. Postconditions are checked before the why. Understanding lands on a top-level append-only `why_trail`; the live DIGEST is the latest non-mechanical why, surfaced on `current`. `reopen` freshens the digest by *appending* reopen-markers (never mutating prior records) for the target and every cascaded gate. Module 4 adds the refresh PRIMITIVES only (flow wiring is #183): a `refresh-request` evidence type carried by the existing `attach` verb (pointers only), a pure `has_pending_refresh_request(cl, gate)` predicate, and a `REFRESH REQUESTED:` line on `current`.

## verify_worktree_isolation.py --here output

```
worktree OK: in C:/Programs/constellation-wt-179
EXIT=0
```

## Test command + output

Command: `PYTHONIOENCODING=utf-8 py -m pytest tests/test_checklist_engine.py -q`

```
........................................................................ [ 43%]
...................................................... [ 75%]
........................................                                 [100%]
166 passed, 18 subtests passed in 13.74s
```

145 prior tests + 21 new (WhyCapture, WhyCaptureBackwardCompat, RefreshPrimitives). No prior test deleted.

Acceptance mapping (all fixture-based unit tests, no harness):
1. Non-exempt advance, no why, no `--mechanical` → REFUSED, fails closed → `WhyCapture.test_non_exempt_advance_without_why_is_refused`
2. Exempt gate advances with no why prompt → `test_exempt_gate_advances_with_no_why_prompt`
3. `--mechanical` discharges; trail records marker; marker is NOT the digest → `test_mechanical_discharges_and_is_not_the_digest`
4. Latest non-mechanical why retrievable as `DIGEST:` via `current` → `test_latest_non_mechanical_why_is_the_digest_line`
5. reopen-freshens-digest (superseded understanding no longer latest) → `test_reopen_freshens_digest` (+ cascade variant)
6. `has_pending_refresh_request` + `refresh-request` round-trip; `REFRESH REQUESTED:` shown/absent → `RefreshPrimitives.test_refresh_request_round_trip`

Backward-compat (pre-ruling): `WhyCaptureBackwardCompat` — existing-shape spine (no `why_trail`, no `why_exempt`): non-exempt refused-then-passes-with-why; exempt advances silent; CLI refuses cleanly (exit 1, not a crash). Plus a live-spine smoke check: `py scripts/checklist_engine.py --file .agent-work/epic-178/spine.json --dry-run current` → exit 0, no crash, no spurious DIGEST/REFRESH lines.

## Files changed + diffstat

```
 scripts/checklist_engine.py    | 161 +++++++++++++++++++++---
 tests/test_checklist_engine.py | 274 ++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 419 insertions(+), 16 deletions(-)
```

Within the fence (only these two files touched).

## PR

https://github.com/fredcai6/constellation-skills/pull/185 (branch `epic178-179-why-capture`, base `54f5965`). Server-side merge is yours.

## Design notes (local implementation choices, within latitude)

- **why_trail entry shape.** Each entry is `{id: "w-N", gate, why, mechanical, ts}` for advances, and `{id: "w-N", gate, reopen: true, reason, ts}` for reopen-markers. Ids are simple sequential `w-N` (append order). `why_ref` in a refresh-request points at a why-record id.
- **Append-only vs. "reopen freshens".** The spec says why_trail is append-only ("never mutate/delete prior entries") AND that reopen must freshen the digest. I reconciled these by having reopen APPEND a reopen-marker rather than mutating prior entries. The digest predicate (`_latest_why_record`) treats a why-record as stale when a *later* reopen-marker names its gate — so a reopened gate's understanding drops out of "latest" without any prior row being edited. Re-advancing with a fresh why (a newer entry) restores a live digest. Cascade reopens append markers for every reset downstream gate too.
- **`--mechanical` + `--why` together.** `--mechanical` is a distinct discharge flag and takes precedence when both are passed (records a mechanical marker), keeping the flag's meaning crisp/predictable. Spec was silent; no acceptance test exercises the combination.
- **DIGEST/REFRESH placement.** Both ride the read-only `current` output (gated checklists only), before the doctrine rail that `dispatch` appends — no new verb, consistent with the #138 rail's boundary idiom.

## Admiral floats / notes

- **NO blocking floats.** No interface-contract change was needed; the frozen spec was implementable as written.
- **Semantics-change note (not a blocker, but worth your awareness).** The Module 1 invariant genuinely changes `advance()` semantics: a non-exempt gate now refuses a why-less advance. ~20 existing unit tests advance without a why and expect success. The postcondition-before-why ordering forces the gate to live *inside* `advance()` (it's a refusal that must block the state change, so unlike the #138 doctrine rail it cannot ride the dispatch boundary). To keep every prior test green with a minimal, honest change, I defaulted the shared `gate()` TEST helper to `why_exempt=True` (one-line change; these tests predate why-capture and are orthogonal to it). The ENGINE's real default stays not-exempt and is proven by the new non-exempt / no-key fixtures. If you'd prefer the legacy tests instead thread `--mechanical` on non-exempt gates (closer to production default, but ~20 edits), say so and I'll re-work.

## Map-impact / triage candidates

- **`docs/CHECKLIST_SCHEMA.md` needs updating** (OUT OF FENCE — did not touch): document the top-level `why_trail` (entry shapes incl. reopen-markers), the per-task `why_exempt` opt-out default, the `refresh-request` evidence type (pointers-only payload: `seam`, `why_ref`), and the `DIGEST:` / `REFRESH REQUESTED:` lines on `current`. Recommend a follow-up issue or a Cartographer pass.
- **#183 (refresh flow wiring)** will consume `has_pending_refresh_request` and the `refresh-request` evidence type. Note for #183: this issue defines "pending" as *present and not superseded*; it does not yet mark a request *fulfilled* (no `fulfilled` field) — #183 owns the consume/fulfil semantics and can extend the predicate or supersede the evidence to clear it.
- The `why` referencing (not duplicating) task-state is prompt-upheld, not engine-enforced (per spec — no duplication lint built).
