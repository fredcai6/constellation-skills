# Launch Order: implementer — issue #181 (Gauge reader: read() -> Reading|None + model-keyed thresholds)

You are an implementer dispatched by the Admiral running epic-178 (Context Governor v1). You start cold; everything you need is pasted here. Do NOT open other issues.

## Mission
Implement issue #181 — the engine-side gauge **reader** (Module 2, read side). Deliverable: a NEW module with a plain `read()` function + a central model-keyed threshold table, fixture-based unit tests to green, a PR, and a result artifact. This is a fail-safe boundary: its whole job is to never let bad data through.

## Frozen build spec (authoritative)
- Create a **NEW module `scripts/gauge_reader.py`**. Do **NOT** edit `scripts/checklist_engine.py` (a sibling issue owns it this wave; the Trip issue #182 wires your module into the engine later).
- A **plain function `read(...) -> Reading | None`** — NOT a Protocol/adapter/NoOp ceremony (explicitly cut for v1). `Reading` can be a small dataclass/namedtuple with the record fields.
- **The gauge file record is FROZEN (identical to the writer, issue #180):**
  `{ "schema_version": <int>, "fill_fraction": <float 0..1>, "model": <str>, "observed_at": <ISO-8601 string, the sampled moment> }`
  These four fields only — no `source`, no `window` (both cut as YAGNI; `fill_fraction` is already normalized).
- **Staleness** is resolved from the embedded **`observed_at`** (NOT file mtime — survives copy/sync/clock-skew): `now - observed_at > max_age` → treat as stale → return `None`. `max_age` is engine config with a sane default that lives in THIS module (e.g. a module constant / small config read).
- **Collapse EVERY failure to a single `None`, never raise:** absent file, corrupt JSON, malformed/missing-field record, stale (by observed_at), and clock-skew (observed_at in the future beyond tolerance) → all return `None`. A `Reading` that reaches the caller is **fresh + well-formed by construction** — staleness is resolved INSIDE the reader so a caller structurally cannot act on stale data.
- Make it **injectable/testable without touching the real filesystem or wall clock**: accept the path and a "now" (and/or the raw record) as parameters or via a thin injection seam, so tests are filesystem-free and clock-free. (Keep it a plain function — injection via default-arg parameters is enough; no class hierarchy.)
- **Central model-keyed threshold table (this module owns it — engine-side):** a mapping `model -> (soft, hard)` fill thresholds. **Unknown `model` → a default `(soft, hard)` pair.** Threshold NUMBERS are placeholders labeled first-run-calibration TBD (the spec defers real numbers); pick sane provisional values (e.g. soft=0.75, hard=0.90) and comment them as calibration TBD. Expose a helper like `thresholds_for(model) -> (soft, hard)`.

## Acceptance (fixture-based, no harness) — falsifiable
1. Each of the **five failure modes** returns `None`: absent, corrupt (bad JSON), malformed (missing/typed-wrong field), stale (observed_at too old), clock-skew (observed_at in the future). ← the fail-safe; must hold.
2. A valid **fresh** record returns a `Reading` with the parsed fields.
3. A **stale** record NEVER yields a usable reading (falsifiable: "does a stale file ever produce a reading?" — must be NO).
4. **Unknown model** falls back to the default `(soft, hard)` pair; a known model returns its keyed pair.

## Pre-Rulings (overridable only if evidence contradicts — say so if you override)
- **File fence:** create ONLY `scripts/gauge_reader.py` and `tests/test_gauge_reader.py`. Do NOT touch `checklist_engine.py`. Keep the diff one-concern.
- "Engine owns the threshold table" is satisfied by it living in this engine-side module (imported by the engine in #182) — the harness/writer never sees it. The portability seam is the file format, not this code.
- Match the repo's existing module/test idioms (look at a sibling like `scripts/verify_state_note.py` and `tests/test_*.py` for style, argparse-free helper shape, utf-8 stdio).

## Honest-Null Clause
A measured negative on a specific claim is a complete, successful deliverable if honestly scoped — report it with the same rigor as a win.

## Inherited Latitude
You implement a frozen spec. Local implementation choices are yours (Reading shape, injection mechanics, provisional threshold numbers). **Float to the Admiral** any change to the frozen record format or any spec gap affecting the writer (#180) or Trip (#182).

## Workspace
Your worktree: **C:/Programs/constellation-wt-181** (branch `epic178-181-gauge-reader`, base `54f5965`, provisioned via `git worktree add C:/Programs/constellation-wt-181 -b epic178-181-gauge-reader 54f5965`).
**First step:** run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-181` — must exit 0; paste output into your report.
PR integration is server-side merge; you just open the PR.

## Inherited Context (platform invariants)
- Windows box. Run tests: `py -m pytest tests/test_gauge_reader.py -q`.
- PR body via temp file + `gh pr create -F <file>` — never a heredoc/here-string for `--body`.
- Set `PYTHONIOENCODING=utf-8` in captured-subprocess child envs.
- `.agent-work/LESSONS.md` Active section is empty this run.

## Budget
- **Model tier:** Sonnet (bounded, mechanical, well-specified).

## Stop Conditions
Stop and return when the frozen record format needs to change, you hit a spec contradiction, or scope would exceed the fence. Return-and-query the Admiral.

## Return Shape
Write your result to **C:/Programs/constellation-skills/.agent-work/epic-178/crew-handoffs/181-result.md** (MAIN checkout path) BEFORE going idle. Include: verdict + summary; the `--here` isolation output; test command + full output; files changed + diffstat; PR URL; any floats/map-impact/triage. Deliver artifact + PR before any idle notification.
