# Implementer Handoff

## Gate
g1-implement (issue #599)

## Task
In `scripts/run_crew.py`, replace `active_duplicate()`'s raw status-string check with a corroborated three-state liveness query, and wire it in so a corroborated-dead entry stops blocking a fresh crew launch while an uncorroborated one still blocks (fail-toward-active).

## Protected Intent
The launch-refusal guard must never silently free a slot held by a genuinely live crew (two agents racing one gate is the worst outcome). It's currently *broken the other way*: a dead crew's leftover `status: running` entry blocks forever. Fix the second without weakening the first.

## Test Mode
Test-after allowed (no TDD requirement in this repo's overlay for this class of change) — but the two existing tests named below (`test_duplicate_active_lock_is_refused`, and `process_alive`'s own tests) MUST still pass unmodified; write the new tests alongside them.

## Close Criteria
- A new pure function `entry_liveness(entry, now, alive=process_alive) -> str` returns exactly one of `"active"`, `"stale"`, `"unknown"` — never a boolean, never any other string.
- `entry_liveness` implements an explicit THREE-bucket rule, in this order, never collapsed to two:
  1. `entry.get("pid")` truthy → `"active"` if `alive(pid)` else `"stale"`.
  2. `entry.get("pid")` falsy AND `entry_backend(entry) == BACKEND_EXTERNAL` → corroborate by heartbeat age: read `entry.get("last_heartbeat")` (fallback `entry.get("started_at")` if `last_heartbeat` is absent), parse as ISO-8601, compute `age = now - hb`; if unparseable/missing → `"unknown"`; else `age.total_seconds() > HEARTBEAT_STALE_SECONDS` → `"stale"`, else → `"active"`.
  3. Anything else (pid falsy AND NOT external — a legacy/malformed entry with neither field, e.g. the real fixture in `tests/test_crew_launcher.py` at the existing `test_duplicate_active_lock_is_refused` test) → `"unknown"` directly. Do **not** attempt a heartbeat lookup for this bucket, and do **not** port `recover_crews.classify_entry`'s pid=None mapping (`alive(None)` is always `False` there, routing to `RESUMABLE`/`NEEDS_ABANDON`) — that is the OPPOSITE of this repo's fail-toward-active rule; this bucket must report `"unknown"`, which still blocks.
- `HEARTBEAT_STALE_SECONDS = 28800` (8 hours), added as a documented module constant near `ACTIVE_STATUSES` (`:47`), with a comment stating: longest observed genuinely-`completed` external run in this repo's archived registries is ~3h30m (12602s, `epic-568-510/g2-repair/commander/attempt-1`); shortest confirmed phantom (unmoved heartbeat, later abandoned) is ~22h27m (80820s, `epic-568-441/g1/implementer/attempt-1`, `.agent-work/archive/2026-08-15-epic-568-441/crew-runs.json`); 8h sits ≈2.3× above the healthy max and ≈2.8× below the phantom min.
- `active_duplicate(entries, work_id, gate, role, worktree, *, now=None, alive=process_alive)` gains these two keyword-only parameters with the stated defaults (`now=None` meaning "compute the current UTC time inside the function if not supplied" — a helper `_now()` returning `datetime.now(timezone.utc).isoformat()` is fine, or thread datetime objects directly; your call, keep it simple and consistent with how `entry_liveness` consumes `now`). Existing callers (the CLI at `:1800`, the existing test at `tests/test_crew_launcher.py:689`) must keep working with ZERO changes to their own code — only `active_duplicate`'s *return value* changes for a corroborated-dead entry (that is the entire point of #599).
- Inside `active_duplicate`'s loop, after the existing `is_abandoned`/`ACTIVE_STATUSES`/work_id+gate+role+worktree filters: call `entry_liveness(entry, now, alive)`. If `"stale"` → `continue` (skip this entry, look for another; this only changes what the READ reports — never write `abandoned` as a side effect, per the non-negotiable no-abandonment-by-inference rule). If `"active"` or `"unknown"` → `return entry` (both still block; this is the fail-toward-active rule, non-negotiable).
- `scripts/recover_crews.py` is UNCHANGED — confirm with `git diff --stat scripts/recover_crews.py` showing nothing.
- No fenced file touched: `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/mcp_spine_server.py`, `.mcp.json`.

## Allowed Scope
- `scripts/run_crew.py` — the new `entry_liveness` function and the `HEARTBEAT_STALE_SECONDS` constant, both placed directly above `active_duplicate` (`:253`); `active_duplicate`'s signature and body.
- `tests/test_crew_launcher.py` — new tests only, plus this file's existing tests must keep passing unmodified (do not delete or weaken any existing test).
- You may add a `from typing import Callable` import and a `from datetime import datetime, timezone, timedelta` import to `scripts/run_crew.py` if not already present — check first, this file may already import `datetime` for other functions (e.g. `result_fresh` at `:295` already uses `datetime.fromisoformat`).

## Specific Exclusions
- Do not modify `scripts/recover_crews.py` (read it for the `classify_entry` shape only, as negative precedent — see Close Criteria bucket 3).
- Do not add a periodic heartbeat-writer for external entries — out of scope; note in your result if you think it's worth a triage candidate, but do not build it.
- Do not touch `scripts/hooks/spine_rail.py` — that is a separate gate (g2), a different implementer dispatch.

## Constraints
- `entry_liveness` must be a genuinely PURE function: no reads of real wall-clock time or real PIDs inside it — `now` and `alive` are always caller-supplied (this is what makes it directly unit-testable).
- `process_alive`'s existing contract, docstring, and injectable seam (`scripts/run_crew.py:864`) must be byte-identical after this change — it is reused, not modified.
- `os.kill(pid, 0)` is POSIX-only; state in your IMPLEMENTER_RESULT that Windows behavior is unchanged (the pid branch reuses the existing unmodified `process_alive`; the heartbeat branch is pure ISO-timestamp arithmetic, OS-agnostic) — CI (a single `windows-latest` job) cannot confirm this locally, say so plainly rather than claiming a Windows-verified result.

## Map Anchors (inbound)
Map orientation for this repo is DEGRADED-UNPARSEABLE at baseline `a69bbac4` (zero authored map anchors exist corpus-wide — confirmed by rebuilding the map locally). No map artifact touches this gate; work from the file:line citations below instead.
- **Map entry point:** none — DEGRADED, see `.agent-work/cleanup-c-liveness-rail/MISSION_FRAME.md` for the full discharge record.
- **Structural:** `scripts/run_crew.py:253` `active_duplicate()`; `scripts/run_crew.py:864` `process_alive()`; `scripts/run_crew.py:47` `ACTIVE_STATUSES`; `scripts/run_crew.py:1393` external-backend `pid=None` entry construction; `scripts/run_crew.py:1800` the one launch-refusal call site.
- **Capability:** Crew launch-refusal / duplicate guard.
- **Constraints/assumptions:** `scripts/recover_crews.py::classify_entry` is read-only precedent, its pid=None mapping must NOT be ported (see Close Criteria bucket 3).
- **Decision anchors:**
  - fail-toward-active — uncorroborated liveness reports `active`, never free.
    `@grade: settled/human · leans g1-implement`
  - three-states-not-two — the query returns `active`/`stale`/`unknown`, never a collapsed boolean.
    `@grade: settled/measured · leans g1-implement`
  - pidless-means-heartbeat — external entry corroboration is heartbeat age vs. an 8h (28800s) window, measured from the archived registries (see Close Criteria).
    `@grade: settled/measured · leans g1-implement`
  - no-abandonment-by-inference — reporting stale is the deliverable; never write `abandoned` as a side effect.
    `@grade: settled/human · leans g1-implement`
- **Evidence expectations:** `tests/test_crew_launcher.py::test_duplicate_active_lock_is_refused` must keep passing unmodified (it exercises bucket 3 — no pid, no backend key).
- **Map confidence flags:** none (DEGRADED, discharged at context step).

## Deliverable Path Check
- **Committed** — `scripts/run_crew.py`; verified via `git check-ignore scripts/run_crew.py` exiting 1 (not ignored).
- **Committed** — `tests/test_crew_launcher.py`; verified via `git check-ignore tests/test_crew_launcher.py` exiting 1 (not ignored).

## Required Evidence
Both directions, using the REAL `crew-runs.json` shape (not a hand-built minimal dict) — pull the actual JSON shape from `.agent-work/archive/2026-08-15-epic-568-441/crew-runs.json` for the external/phantom case:
1. A `cli`-backend entry with a dead PID (`alive` stubbed to return `False`), `status: "running"` → `active_duplicate(...)` now returns `None` (frees the slot) where the pre-fix boolean check would have blocked.
2. The SAME shape with a live PID (`alive` stubbed `True`) → still returns the entry (blocks) — the honest-active control.
3. An `external`-backend entry shaped like the real `epic-568-441` phantom (`pid: None`, `last_heartbeat == started_at`), with `now` fixed to a time > 8h past `started_at` → `active_duplicate` returns `None` (frees).
4. The SAME external shape with `now` fixed to a time well inside the 8h window (e.g. 4h past `started_at`) → still returns the entry (blocks) — proves the fix does not fire on a healthy long-running crew's normal duration.
5. `test_duplicate_active_lock_is_refused` (existing) run and shown green, unmodified.
6. Full `tests/test_crew_launcher.py` suite run clean-env (clear `__pycache__` first): `find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null; env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py` — paste full output.
Load-bearing: items 1–4 (the actual behavior change) and item 5 (the regression guard). Item 6 is confirmatory.

## Wiring Grep
```bash
grep -rn "entry_liveness" --include=*.py . | grep -v "def entry_liveness"
```
State the count of call sites found outside the definition — `active_duplicate`'s own call is the expected one; the new tests calling it directly also count.

## Verification Commands
```bash
find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py
git diff --stat scripts/recover_crews.py
```

## Suggested Model Tier
Simple bounded — one new pure function with a clearly specified three-bucket rule, one small wiring change to an existing function, plus tests. No architectural ambiguity remains after this handoff.

## Authority
The three-bucket rule, the 8h window, and the fail-toward-active mapping are ALL already decided (see Decision anchors above) — do not re-derive or second-guess them. If you find a genuine correctness problem with the 8h number or the bucket rule while implementing, STOP and report it as a blocker rather than silently picking a different number.

## Stop Conditions
Stop and return if: the three-bucket rule as specified cannot be implemented as a pure function (e.g. `entry_backend` is not actually accessible/importable at that point in the file — it is defined earlier in `run_crew.py`, confirm before dispatch-time assumptions break), the existing `test_duplicate_active_lock_is_refused` cannot be kept green, or a fenced file would need to change.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (all 6 items above, load-bearing vs confirmatory noted), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

Write the full IMPLEMENTER_RESULT to `.agent-work/cleanup-c-liveness-rail/crew-handoffs/g1-implement-result.md` before ending your turn — that write is the delivery.
