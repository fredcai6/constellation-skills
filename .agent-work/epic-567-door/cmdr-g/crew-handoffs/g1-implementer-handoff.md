# Implementer Handoff

## Gate
`g1` — verify + close primitives (of 3 gates; g2 adds reap + child-plan release, g3 composes `finish_work`)

## Task
Add three functions to `scripts/spine_lifecycle.py` in this worktree:

**(a) `done_refusal(spine, *, tree_clean, episodes_captured) -> str | None`** — PURE (dict/bool in, str-or-None out; no `Path`, no `open`, no `subprocess`), sitting beside the existing pure helpers. Returns `None` when the two NEW checks below pass, else ONE refusal message naming why. Check order and exact strings:

1. `if not tree_clean: return "close refused: the working tree has uncommitted changes"`
2. `if not episodes_captured: return "close refused: this run captured no episode"`
3. `return None`

**REWORK NOTE, load-bearing (this superseded an earlier, incorrect draft of this handoff — read this even if you already started from the old version):** `done_refusal` must **NOT** call or fold in `closeout_refusal`, and takes **no** `archive_exists` argument. The reason: `done_refusal` is called on the CURRENT state, before `_advance_and_release` runs — the lease is BY DEFINITION still active at that point (that's the condition `_advance_and_release` exists to fix). `closeout_refusal`'s own first check refuses unless `engine_session.status == "released"` (`spine_lifecycle.py:143-144`) — so a `done_refusal` that includes it would refuse on every legitimate call, before the function that would actually release the lease ever runs. `closeout_refusal` is not re-derived here and not skipped either — it still runs, unchanged, exactly once, downstream in `close_work` (unmodified, called by `finish_work` in g3, after release) — that is the one and only place lease/terminality/archive-exists gets checked. If you find a prior partial implementation in this file that delegates to `closeout_refusal`, that is the bug to remove, not a shape to preserve.

**(b) `_engine_call(argv) -> tuple[str, int]`** — the SINGLE choke point for every in-process `checklist_engine.main(argv)` call in this module. Mirror the pattern `scripts/mcp_spine_server.py` already uses (its module docstring: *"Every tool builds an argv and calls `checklist_engine.main(argv)`, capturing stdout, stderr and the exit code"*): redirect `stdout`/`stderr` via `contextlib.redirect_stdout`/`redirect_stderr` into `io.StringIO`, call `checklist_engine.main(argv)`, return `(captured_output, exit_code)`.

It MUST catch **both** `checklist_engine.EngineError` **and** `SystemExit`. This is load-bearing: `argparse` calls `sys.exit(2)` on an unparseable argv, and `checklist_engine.main()`'s own try/except catches only `EngineError` — so an argv-shape mismatch (a typo, or lane A's concurrent rewrite changing a flag) escapes as `SystemExit` instead of the captured `(output, exit_code)` pair every caller here assumes. On `SystemExit`, return the captured output with `int(exc.code or 0)`. **Never raises.**

**(c) `_advance_and_release(spine_path, session_id, *, root, why=None) -> dict`** — impure, going through `_engine_call` only (never `subprocess`, never a second call path). Sequence:

1. Read the spine, find the active/terminal gate id (reuse `checklist_engine.active_id(cl)`).
2. If that gate's status is `"pending"`, `start` it.
3. If the gate is not yet terminal, `advance` it: pass `--why <why>` when `why` is a non-empty string, else `--mechanical`.
4. Then `release --session-id <session_id>`.

Return `{"ok": True, "output": ...}` on success, or `{"ok": False, "refusal": <verbatim text>, "stage": "advance"|"release"|"start"}` on a refusal.

### The load-bearing constraint on (c) — do not paper over it

`advance()`'s `require_why` parameter is computed **live at the CLI boundary** from `_trip_hard_band_reading(...)` — see `scripts/checklist_engine.py:2519-2534` (inside `advance`) and `_run_verb` at `:3361-3370`. It is **not** derived from any flag the caller passes. When it is true (context at/over the HARD band), the engine **refuses `--mechanical` outright**:

```
<gate>: context is at/over the hard limit, so this gate cannot be closed silently — a mechanical or why-less close records no understanding, and the next agent would cold-start from a digest written before your work. Closing the gate is NOT refused; only the silence is. Run: advance <gate> --why "<understanding>"
```

So: **never assume `--mechanical` succeeds.** When the advance half refuses for any reason, return that refusal text **verbatim** (the engine's own message already names the fix) and **do not attempt the release**. Do not re-word it, do not wrap it in a new sentence, do not swallow the exit code.

This matters because it is plausibly the exact scenario issue #574 cites — "an Admiral's closeout was refused at 23% context."

## Protected Intent
An agent finishing a run must get **one actionable refusal**, never a ritual to re-derive. A refusal that is silently swallowed, re-worded into something the engine never said, or followed by a release that should not have happened, defeats the whole point of the issue.

## Test Mode
Test-after allowed (these are new functions on an existing module with an established test file). Every behavior below needs a test; the HARD-band test (3) is the one that must not be skipped.

## Close Criteria
- `done_refusal`, `_engine_call`, `_advance_and_release` exist in `scripts/spine_lifecycle.py`.
- `done_refusal` is genuinely pure — no `Path`, `open`, or `subprocess` in its body — matching the module's stated pure/impure split at function granularity.
- `done_refusal` does **NOT** call `closeout_refusal` and does **NOT** take an `archive_exists` argument — it covers only the two new checks (tree clean, episodes captured). `closeout_refusal`'s lease/terminality/archive logic is neither restated nor delegated to here; it stays exclusively in `close_work`, called later (downstream, in g3), after release has already happened.
- `_engine_call` is the only place this module calls `checklist_engine.main`.
- Tests added to `tests/test_spine_lifecycle.py`, all passing:
  1. Fixture spine at its terminal gate, not yet advanced → `_advance_and_release` leaves `engine_session.status == "released"`.
  2. Fixture spine with an **unmet postcondition** → the refusal text passes through **unchanged**, and `engine_session.status` is still `"active"` (release never attempted).
  3. **HARD-band path** — write a gauge file at/over the hard band beside a fixture spine (see `scripts/gauge_reader.py`: `GAUGE_FILENAME` / `gauge_filename(owner)` for the filename shape, and the record's four required fields incl. `fill_fraction`, `model`, `observed_at`; pick a `fill_fraction` high enough to trip the hard band for the fixture's model). Assert a **why-less** attempt returns the engine's why-required refusal rather than silently closing, then assert the **same fixture** closes cleanly once a `why` is supplied.
  4. `_engine_call` returns a non-zero exit code (does **not** raise `SystemExit`) for a deliberately malformed argv.
- Full `tests/test_spine_lifecycle.py` stays green (1178 lines pre-change; run it and state the pre/post counts).

## Allowed Scope
- `scripts/spine_lifecycle.py` — add the three functions.
- `tests/test_spine_lifecycle.py` — add tests. Pre-authorized to add fixtures/helpers here.

## Specific Exclusions
- **`scripts/checklist_engine.py` — DO NOT EDIT.** Owned by **lane A (epic #567)** this wave; it is actively being rewritten. Read it, import it, call `main(argv)` — never modify it.
- **`scripts/mcp_spine_server.py` — DO NOT EDIT.** Same owner, **lane A (epic #567)**, same wave. It is the *pattern reference* for the in-process call only. No tool registration this gate.
- **`scripts/hooks/spine_rail.py` — do not edit** (g2 calls it as a library; this gate does not touch it at all).
- Do not add `force_reap`, `_release_child_plans`, `finish_work`, `open_pr`, or the CLI — those are g2/g3. Stay in this gate.
- Do not modify `closeout_refusal` or `close_work`.

## Constraints
- **Never run any new code against a live spine file.** `.agent-work/epic-567-door/spine.json` holds the dispatching Admiral's **active lease** — never read-modify it, never target it, never use it as a fixture. Same for `.agent-work/epic-567-door/cmdr-g/spine.json` and `execute.json` (this Commander's own live spines). Build fixtures under `tmp_path` only.
- Keep the module's pure/impure split at function granularity, as its docstring states.
- POSIX-form commands; `PYTHONIOENCODING=utf-8` in any subprocess whose output you capture.
- `py` works on this host.

## Map Anchors (inbound)
- **Map entry point:** none — `map_orient.py` returned DEGRADED-UNPARSEABLE for this repo (no `docs/architecture` packet map). The declared substitutes are `map/INDEX.md`, `scripts/spine_lifecycle.py`, `scripts/mcp_spine_server.py`, `scripts/hooks/spine_rail.py`, `docs/agents/ORCHESTRATOR_CONTEXT.md`. Start from `scripts/spine_lifecycle.py`'s own module docstring — it states the contract and the pure/impure split.
- **Structural:** `scripts/spine_lifecycle.py` — `closeout_refusal` (:122-161), `close_work` (:384+), the pure-helpers block (:58-161). `scripts/checklist_engine.py` — `advance` (:2468), `release` (:1133), `main` (:3495), `_run_verb` (:3355) — read-only.
- **Capability:** mechanical-closeout verify + close primitives (#574 contract sketch steps 1-2).
- **Constraints/assumptions:** file-ownership fence (checklist_engine.py, mcp_spine_server.py are lane A's this wave); never test on a live lease.
- **Decision anchors:** `decision:library-reuse-over-file-edit` — the close sub-steps call `checklist_engine.main(argv)` in-process rather than editing that file, mirroring how `spine_lifecycle.py` already imports `generate_spine`/`init_work_area`/`run_crew`/`validate_spine`.
  `@grade: settled/measured · leans g1-implement,g2-implement · settle: re-measure if lane A's rewrite lands first`
- **Evidence expectations:** `closeout_refusal` itself is byte-for-byte unchanged (`git diff` on its own line range is empty) and is called from exactly one place in this module after this gate: `close_work` (unchanged). `done_refusal` never references `closeout_refusal` at all — assert this with a source-text check (e.g. `"closeout_refusal" not in inspect.getsource(sl.done_refusal)`), not merely by eyeballing it.
- **Map confidence flags:** `scripts/checklist_engine.py` is being rewritten concurrently by lane A. Do not trust a remembered flag shape — read the current `parse_args` before composing an argv, and let `_engine_call`'s `SystemExit` guard be the backstop.

## Deliverable Path Check
- **Committed** — `scripts/spine_lifecycle.py`; `git check-ignore` exit **1** (not ignored).
- **Committed** — `tests/test_spine_lifecycle.py`; `git check-ignore` exit **1** (not ignored).
- Both files already exist and are tracked, so `git diff` shows both; nothing new appears only in `git status` this gate.

## Required Evidence
**Load-bearing (prove rigorously):**
- The HARD-band test (close criterion 3) — paste the test body and its passing output. This is the finding the whole gate exists to cover.
- The unmet-postcondition test proving the refusal text is **byte-identical** to the engine's and that `status` stayed `"active"`.
- `py -m pytest tests/test_spine_lifecycle.py -q` output, with the pre-change and post-change test counts stated.

**Confirmatory (spot-check suffices):**
- `git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py` → must be **empty**. Paste it.
- `done_refusal`'s purity (no `Path`/`open`/`subprocess` in its body).

## Wiring Grep
`done_refusal` and `_advance_and_release` are consumed by `finish_work` in **g3**, which does not exist yet — so at the end of THIS gate their only non-definition callers are the tests. That is expected and bounded: state the count you find and note g3 as the production caller.

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease && \
grep -rn "done_refusal\|_engine_call\|_advance_and_release" --include=*.py . \
  | grep -v "def done_refusal" | grep -v "def _engine_call" | grep -v "def _advance_and_release"
```

`_engine_call` must have at least one caller inside `spine_lifecycle.py` itself (`_advance_and_release`) — zero there is a stop condition, not a note.

## Verification Commands
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease
PYTHONIOENCODING=utf-8 py -m pytest tests/test_spine_lifecycle.py -q
git diff --stat -- scripts/checklist_engine.py scripts/mcp_spine_server.py scripts/hooks/spine_rail.py
PYTHONIOENCODING=utf-8 py scripts/validate_spine.py .agent-work/epic-567-door/cmdr-g/execute.json
```

## Suggested Model Tier
**Sonnet** (bounded, well-specified: three functions with stated signatures and exact refusal strings). The launch order fixes this lane at Sonnet.

## Authority
Already decided — do not re-litigate:
- The three function signatures and the refusal-string wording above.
- `--mechanical` is never assumed; a refused advance returns verbatim and stops.
- `_engine_call` catches `SystemExit` as well as `EngineError`.
- The fence: `checklist_engine.py`, `mcp_spine_server.py`, `spine_rail.py` are not yours to edit.

**You must not decide alone:** anything requiring an edit to a fenced file; any change to `closeout_refusal`/`close_work`'s existing behavior; adding an MCP tool registration.

## Stop Conditions
Stop and return if: allowed scope must be exceeded; a fenced file must be touched; the HARD-band refusal cannot be reproduced in a fixture (say so plainly with what you tried — a measured negative is a real result, not a failure); required evidence cannot be produced; a decision outside the authority above is needed.

## Return Format
Return `IMPLEMENTER_RESULT`: completed slice, files changed, test mode satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

`Return status` must be one of `complete | partial | blocked | out-of-scope | failed`, written **lowercase** — the Commander copies it verbatim into this gate's `implementer-result` evidence and the postcondition matches on exact case.

**Delivery.** Write the full `IMPLEMENTER_RESULT` to `.agent-work/epic-567-door/cmdr-g/crew-handoffs/g1-implementer-result.md` **before ending your turn** — that write is the delivery. A `SendMessage` ping to the dispatching Commander is a best-effort courtesy only, never the delivery.
