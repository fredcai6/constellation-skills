# Launch Order: implementer — issue #180 (Gauge writer: Claude Code PostToolUse hook + golden fixture) — HITL

You are an implementer dispatched by the Admiral running epic-178 (Context Governor v1). You start cold; everything you need is pasted here. Do NOT open other issues.

**This issue is HITL** — the final wiring into the human's `~/.claude/settings.json` and the live-transcript validation require the human. **Your job is to build everything UP TO that seam** so the human's remaining action is minimal and well-framed. **Do NOT edit any real `settings.json`.**

## Mission
Implement issue #180 — the harness-side gauge **writer** (Module 2, write side): a Claude Code `PostToolUse` hook that senses context fill and writes the gauge file the reader (#181) consumes. Deliverable: the hook script, a golden-sample transcript fixture, fixture-based tests (well-formed write, parse-failure-leaves-prior-file, atomic/torn-read), a wiring doc + format-drift note, and a result artifact framing the exact human action needed.

## Frozen build spec (authoritative)
- A Claude Code **`PostToolUse` hook** (a script) that:
  - Parses `transcript_path` and computes context fill via the **X2 strategic-compact technique — sum the token fields** in the transcript to get used tokens, normalize by the model's context window to a **`fill_fraction` in 0..1**, and read the **`model`**.
  - **Atomically (tmp file + rename)** writes the record to **`.agent-work/<work_id>/gauge.json`** (session-scoped, sibling to `spine.json`, reusing the hook rail's existing session→spine binding to resolve `<work_id>`).
  - **Record is FROZEN (identical to the reader, issue #181):**
    `{ "schema_version": <int>, "fill_fraction": <float 0..1>, "model": <str>, "observed_at": <ISO-8601 sampled moment> }` — these four only (no `source`, no `window`).
  - Is **non-blocking / fail-open**: a failure never blocks the tool call.
  - **Skip-on-uncertainty — NEVER write a placeholder/zero.** If it can't compute fill confidently, it writes nothing and lets the existing file **age into staleness** (the reader will drop it). No fabricated records.
- Ship a **golden-sample transcript fixture** (a captured/representative Claude Code transcript) and a **format-drift note** (documents the transcript token-field shape the parser depends on, so a future harness format change is caught).

## Acceptance
1. Given the golden-sample transcript, the hook writes a **well-formed record** (all four fields, fill in 0..1).
2. A **parse failure leaves the prior gauge file untouched** (skip-on-uncertainty; no clobber, no placeholder).
3. **A concurrent read during a write never observes a torn/partial record** (atomic tmp+rename — TF9). Demonstrate with a test.
4. Wiring is **documented** (the exact `settings.json` PostToolUse entry the human will add) — as a doc, NOT applied.

## The HITL seam (what you hand the human — build to here, stop here)
Produce, in your result artifact, a crisp **"human action" section**: (a) the exact `settings.json` snippet to add the hook, (b) how to run one real tool call and confirm `gauge.json` appears well-formed, (c) what "looks right" means (fill plausibly tracks a filling context). You do the buildable+testable 100%; the human does only the irreducible wiring+eyeball.

## Pre-Rulings (overridable only if evidence contradicts — say so if you override)
- **Do NOT modify any real `~/.claude/settings.json` or global config.** Wiring is documented for the human, never applied — this is the HITL boundary.
- **File fence:** create only new files — the hook script (e.g. `scripts/gauge_writer_hook.py`), the fixture (under `tests/fixtures/`), the test (`tests/test_gauge_writer.py`), and the wiring/format-drift doc (a `.md`, e.g. under `docs/` or alongside the hook). Do NOT edit `checklist_engine.py` or `gauge_reader.py`.
- **Session→spine binding:** locate the existing "hook rail" session→spine binding in the repo and reuse it to resolve `<work_id>`. If no such binding exists, derive `<work_id>` from the gauge-path convention, **document the assumption**, and **float it to the Admiral** rather than inventing a fragile mechanism.
- **Honest-null is expected and welcome here.** The X2 technique is "confirmed buildable but never run against the real harness" — if you find the live transcript token-field format can't be reliably summed, a well-scoped measured negative ("the fill estimate can't be computed reliably because X") is a COMPLETE, successful deliverable. Report it with full rigor; do not fake a working estimate.

## Honest-Null Clause
A measured negative on the fill-estimate question is a complete, successful deliverable — report it with the same rigor as a win.

## Inherited Latitude
You implement a frozen spec to the HITL seam. Local implementation choices are yours. **Float to the Admiral** any change to the frozen record format, the session→spine binding assumption, or a discovered impossibility in the fill estimate.

## Workspace
Your worktree: **C:/Programs/constellation-wt-180** (branch `epic178-180-gauge-writer`, base `54f5965`, provisioned via `git worktree add C:/Programs/constellation-wt-180 -b epic178-180-gauge-writer 54f5965`).
**First step:** run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-180` — must exit 0; paste output.
PR integration is server-side merge; you just open the PR.

## Inherited Context (platform invariants)
- Windows box. Run tests: `py -m pytest tests/test_gauge_writer.py -q`.
- PR body via temp file + `gh pr create -F <file>` — never a heredoc/here-string for `--body`.
- Set `PYTHONIOENCODING=utf-8` in captured-subprocess child envs.
- `.agent-work/LESSONS.md` Active section is empty this run.

## Budget
- **Model tier:** Sonnet (bounded build-to-seam; the hard part is honest measurement, not volume).

## Stop Conditions
Stop and return when: you'd need to touch a real settings.json, the record format needs to change, the session→spine binding is absent, or the fill estimate proves unreliable (report as honest-null). Return-and-query the Admiral.

## Return Shape
Write your result to **C:/Programs/constellation-skills/.agent-work/epic-178/crew-handoffs/180-result.md** (MAIN checkout path) BEFORE going idle. Include: verdict + summary; the `--here` isolation output; test command + full output; files changed + diffstat; PR URL; the **"human action" HITL section** (settings.json snippet + validation steps); any floats/map-impact/triage. Deliver artifact + PR before any idle notification.
