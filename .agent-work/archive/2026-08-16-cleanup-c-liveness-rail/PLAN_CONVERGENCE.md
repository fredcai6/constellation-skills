# Plan-alternatives convergence — cleanup-c-liveness-rail

## The one thing designed twice
The gate plan for #599 (`active_duplicate` corroborated liveness) and #549 (`decide_stop` provenance-aware reason).

## Count and panel — a surfaced choice
Single pair (N=2), not a full panel: both fixes are narrow, heavily pre-ruled (5 pre-rulings fix most of the design space already), and touch exactly 2 files. Not architecture-spanning. A 3-lens panel was judged not worth the extra dispatch cost for this weight.

## Constraints assigned
- **Candidate A — smallest-diff**: minimize new surface; call a small helper directly from inside the existing function.
- **Candidate B — most-testable**: standalone pure functions, injectable clock/predicates, decoupled from control flow.

## Compared on
- **Depth**: both hide the corroboration logic behind one call; B separates the *decision* (liveness state) from the *policy* (fail-toward-active mapping) slightly more cleanly — A folds "stale continues the loop" into the same function body as the state computation, B keeps `entry_liveness` returning a pure state and lets `active_duplicate` apply the policy. B's separation is real depth, not just extra surface.
- **Locality**: A touches marginally fewer lines. B's `_session_keys()` extraction for #549 is a genuine locality win — it makes `session_view` and the new provenance function share one walk, so they cannot drift apart; A's plan duplicates the walk in a second function, which is a smaller diff today but a live drift risk (two loops that must independently be edited in the same way if the merge rule ever changes).
- **Seam placement**: both put the new #599 function directly above `active_duplicate`. For #549, B's shared-walker seam is the more honest boundary — the "who is allowed to see what" rule now has exactly one implementation.
- **Testability**: B wins outright — pure functions with injected `now`/`alive`/predicates are directly unit-testable without going through the CLI or the hook's full payload shape.

## Critical facts surfaced by candidate B's read (adopted into the plan regardless of constraint)
1. **An existing test currently pins the #549 bug**: `tests/test_spine_rail.py::test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key` (~line 545) asserts `"COMPOSITE-MARKER" in out["reason"]` — i.e. it currently *requires* the subordinate's imperative to leak into the block reason, with a docstring explaining it was written for #419 to fix a *different* bug (silent allow). This test must be updated (not just supplemented) as part of g2, with the assertion inverted and a new one added for the owning-session text. Verified directly by reading the test.
2. **`reconstruct_current(spine)` feeds `additionalContext`, which embeds the same imperative** (`ACTIVE {aid} [...] -- {imp}`) the fix removes from `reason`. Leaving `additionalContext` untouched reopens the identical leak through a second field. In scope even though the mission text names only "reason" — same imperative, second door. Verified directly by reading `reconstruct_current` and `decide_stop`.
3. **No periodic heartbeat writer exists for a still-running `external` entry** — `last_heartbeat` is set once at dispatch and only touched again by `verify()`/`resume()`. "Heartbeat age" for a pidless entry is therefore "time since dispatch/resume," not a true liveness pulse. Stated explicitly in the implementation so it isn't misread as more corroboration than it is.

## Heartbeat window — resolved directly from the real registries (not merely one candidate's read)
Queried every archived `crew-runs.json`/`crew-runs.post-archive.json` for `backend == "external"` entries with a resolvable duration:
- **Confirmed phantom** (`epic-568-441/g1/implementer/attempt-1`): `started_at == last_heartbeat` = `2026-08-14T18:10:25Z`, still `status: running` when read ~`2026-08-15T16:37Z` (the moment a Commander misread it as active) — **~22h27m** stale, eventually marked `abandoned` at **~22h46m**.
- **A second, worse phantom** (`issue-440-binding-cwd/g2-implement/implementer/attempt-1`): same signature, abandoned at **~28h33m**.
- **Longest genuinely-`completed`** external run in the entire corpus: `epic-568-510/g2-repair/commander/attempt-1`, **~3h30m** (12602s) from `started_at` to `completed_at`.
- Every other completed external run in the sample is well under 3h.

**Chosen window: 8 hours (28800s).** It sits above the longest observed healthy completion by ≈2.3× (28800/12602), and below the shortest observed phantom by ≈2.8× (80820/28800 -- epic-568-441's ~22h27m expressed in seconds), so no observed data point on either side lands near the boundary. `@grade: settled/measured` — this run measured it directly from the corpus rather than asserting a number; recorded here and echoed into the code comment. If a legitimately longer external dispatch is ever observed, that observation should tighten this number, not this plan.

## Cold critic pass and resolutions
A cold critic (no authoring context, read only LAUNCH_ORDER.md + MISSION_FRAME.md + this document + the actual source) reviewed this convergence before it was cut into `execute.json`. Findings triaged:

1. **CONFIRMED, fixed here.** `recover_crews.classify_entry`'s pid=None handling (`is_alive = alive(None) = False` → routes to `RESUMABLE`/`NEEDS_ABANDON`, never `ACTIVE`) is the OPPOSITE of `decision:fail-toward-active`. MISSION_FRAME's "closest existing precedent" language was misleading — `classify_entry` is precedent only for *the shape of PID+result-based classification existing at all*, never for its pid=None mapping, which this lane deliberately diverges from. Corrected below and to be stated explicitly in `entry_liveness`'s docstring so an implementer does not silently port the wrong branch.
2. **CONFIRMED, fixed here.** `entry_liveness` needs a named THIRD bucket, not two: (a) pid present → `process_alive`; (b) pid absent AND `entry_backend(entry) == BACKEND_EXTERNAL` → heartbeat window; (c) pid absent AND NOT external (a legacy/malformed shape, e.g. the real fixture at `tests/test_crew_launcher.py:683-698` which has neither `pid` nor `backend`) → `"unknown"` directly, no heartbeat lookup attempted. `active_duplicate` still blocks on `"unknown"` (fail-toward-active), so `test_duplicate_active_lock_is_refused` keeps passing unmodified. This three-bucket rule is now a named, explicit requirement on the g1 gate, not left implicit.
3. **CONFIRMED, arithmetic fixed.** 28800/12602 ≈ 2.29×, not ">2.3×" — corrected to "≈2.3×" below. Does not change the chosen window (8h), only the stated ratio.
4. **Acknowledged, tightened.** The "defaults preserve today's behavior" parenthetical describes call-site *signature* compatibility only, not return-value behavior — #599's entire point is that `active_duplicate`'s return value changes for a corroborated-dead entry. Restated below to avoid that misreading.
5. **Noted as an implementation-time risk, not a plan defect.** `session_view`'s `key == sid` branch is untyped while its prefix branch requires `isinstance(key, str)`; `_session_keys()` must reproduce that exact asymmetry (not silently coerce), and g2-review must confirm it does. Added to g2's close criteria.
6–7. No defect — the "pins the bug" claim and the fenced/decide_session_start scope claims were verified accurate by the critic.

## Output — the recommendation
**Adopt candidate B's structure for both gates** (standalone pure functions, shared-walker seam for #549, injected `now`/`alive`), **with candidate A's `additionalContext` catch folded in**, and the **8h window** computed above (between A's 8h guess and B's 4h guess — B's own number came from a smaller sample than the full-corpus sweep just run; 8h is adopted as the better-evidenced figure). Concretely:

- **g1 (#599)**: `entry_liveness(entry, now, alive=process_alive) -> "active"|"stale"|"unknown"` as a new pure function directly above `active_duplicate` (`run_crew.py:253`), with an explicit THREE-bucket rule (never two): (a) `pid` truthy → `process_alive(pid)`; (b) `pid` falsy AND `entry_backend(entry) == BACKEND_EXTERNAL` → heartbeat-age vs. `HEARTBEAT_STALE_SECONDS`; (c) `pid` falsy AND NOT external (legacy/malformed shape) → `"unknown"` directly, no heartbeat lookup. `active_duplicate` gains keyword-only `now=None, alive=process_alive` (preserving the existing call sites' SIGNATURE unmodified — not their return value, which changes by design: a corroborated-dead entry now frees the slot) and applies the fail-toward-active policy (`stale` frees; `active` and `unknown` both still block) instead of a raw status-string check. `HEARTBEAT_STALE_SECONDS = 28800` (8h) as a documented module constant.
- **g2 (#549)**: extract `_session_keys(binding, sid) -> list[str]` as the single source of truth for "which binding keys this session's view merges"; `session_view` becomes a thin fold over it (unchanged return shape, unchanged existing test); add `session_view_provenance(binding, sid) -> dict[path, owning_key]` built from the same `_session_keys` list; in `decide_stop`, look up each mid-flight entry's owning key and branch the rendered `reason` AND `additionalContext` — bare-`sid`-owned entries keep today's `_mid_flight_reason`/`reconstruct_current` wording, per-agent-key-only entries get a new `_owning_session_reason(...)` that names the owning session and withholds the imperative from both fields. `decide_session_start` (the other `session_view` caller) is untouched in code and behavior — a regression test pins that.

## Untaken-road record
- A 3-candidate panel was not run (see Count and panel above) — named and surfaced here, not silently skipped.
- A design where `active_duplicate` is renamed/rewritten wholesale into a `classify`-style function (mirroring `recover_crews.classify_entry`'s 7-state shape) was considered and rejected by both candidates: it would widen the call-site contract (`run_crew.py:1800` expects `dict | None`) for no benefit this lane needs, and `recover_crews.py` is explicitly not owned this lane.

## Panel-vs-single record
Single pair (N=2), not a panel — restated per the design-it-twice contract. Rationale: narrow, heavily pre-ruled, 2-file scope. Surfaced at plan approval alongside the LAUNCH_ORDER citation.
