# Launch Order: implementer — issue #179 (Why-capture + refresh primitives: engine schema)

You are an implementer dispatched by the Admiral running epic-178 (Context Governor v1). You start cold; everything you need is pasted here. Do NOT open other issues — the relevant spec is inline below.

## Mission
Implement issue #179 — the foundational engine-schema change (Modules 1 & 4 of the CONFIRMED spec) in `scripts/checklist_engine.py`. Deliverable: the schema + verbs below, fixture-based unit tests to green, a PR, and a result artifact. This is the load-bearing foundation the rest of the epic builds on — correctness and backward-compatibility are paramount.

## Frozen build spec (authoritative — from the epic's post-review amendments; where any prose differs, THIS governs)

**Module 1 — Why-capture:**
- On a **non-exempt `advance`**, the engine solicits a **single `why` field** (the running understanding). **Silence is REFUSED** — an advance of a non-exempt gate with neither a why nor the mechanical marker must fail closed (engine-enforced, not agent discipline). Add a `--why <text>` flag AND a plain **`--mechanical`** flag to the `advance` subparser; `--mechanical` discharges the prompt (no elaborate tagging, no magic string in a text field — a distinct flag).
- **Postconditions are checked BEFORE the why** (no buying past unfinished work — if postconditions fail, you get the postcondition refusal, not the why prompt).
- Per-task **`why_exempt`** boolean, read from the task definition, set at template-authoring time. **Default = NOT exempt (opt-out).** **NO migration pass** — legacy gates simply absorb the one-token `--mechanical` on first exercise.
- A dedicated **top-level append-only `why_trail`** list (sibling to `blockers` / `triage_candidates`), NOT the evidence list. Each entry records the gate id, the `why` text (or a mechanical marker), and enough to identify supersession. Append-only — never mutate/delete prior entries.
- The **live digest = the latest non-mechanical `why`**, surfaced on `current` as a **`DIGEST:` line** (no new verb). A `reopen` **freshens** the digest (a reopened gate's stale understanding stops being "latest" — the reopen writes/marks so the digest reflects it).

**Module 4 — Refresh primitives (this issue builds the PRIMITIVES only; the flow wiring is #183):**
- A **`refresh-request` evidence type**, written via the existing `attach` verb (payload = pointers only: `seam` = active gate id, `why_ref` = latest why-record id — NEVER copies of state).
- A pure predicate **`has_pending_refresh_request(cl, gate)`** returning bool — no shared mutable state, no side effects.
- A **`REFRESH REQUESTED:` line** on `current` when a pending refresh-request exists for the active gate.

## Acceptance (all fixture-based unit tests, no harness) — falsifiable
1. A non-exempt `advance` with no why and no `--mechanical` is **REFUSED** (fails closed). ← the load-bearing invariant; must fail.
2. An **exempt** gate (`why_exempt: true`) advances with **no** why prompt.
3. `--mechanical` discharges a non-exempt advance (advance succeeds; trail records the mechanical marker; that entry does NOT become the digest).
4. The latest non-mechanical `why` is **retrievable as the `DIGEST:` line** via `current`.
5. **reopen-freshens-digest**: after a reopen, the digest reflects the reopened state (the superseded understanding is no longer "latest").
6. `has_pending_refresh_request` + `refresh-request` **round-trip**: attach a refresh-request, predicate returns true and `current` shows `REFRESH REQUESTED:`; absent one, false and no line.

## Pre-Rulings (overridable only if evidence contradicts — say so if you override)
- **BACKWARD COMPATIBILITY IS MANDATORY.** The Admiral's own live spine (`.agent-work/epic-178/spine.json`) and many shipped spines have **no `why_trail` key and no `why_exempt` on their tasks**. The new engine MUST drive them without crashing: missing `why_trail` → create on first write (`setdefault`); missing `why_exempt` → treat as not-exempt. An advance of such a gate without `--why`/`--mechanical` should **REFUSE cleanly** (a clear message telling the caller to pass `--why` or `--mechanical`), never throw. Add/keep a test proving an existing-shape spine (no why fields) is drivable: exempt→advances silent; non-exempt→refused-then-passes-with-why.
- **File fence:** you may edit ONLY `scripts/checklist_engine.py` and `tests/test_checklist_engine.py` (add new test functions; do not delete existing tests). Do NOT create the gauge reader, the writer hook, or the Trip policy — those are sibling issues. Keep the diff one-concern.
- Follow the existing engine's idioms (how verbs are dispatched, how `current` renders, how evidence attaches, how the journal sidecar records mutations). Match its style; do not reflow unrelated code.
- The `why` **references** task-state for the *what*, never duplicates it — this half is prompt-upheld, not engine-enforceable; do not build a duplication lint (out of scope).

## Honest-Null Clause
A measured negative on a specific claim (e.g. "reopen cannot freshen the digest without X") is a complete, successful deliverable if honestly scoped — report it with the same rigor as a win and surface it to the Admiral rather than forcing a bad design.

## Inherited Latitude
You implement a frozen spec. You may make local implementation choices (data shapes within the record, helper factoring, test structure). **Float to the Admiral** (return and ask): any change to the interface contract above, anything the spec is silent on that affects other issues, or any discovered spec contradiction. Do not expand scope.

## Workspace
Your worktree: **C:/Programs/constellation-wt-179** (branch `epic178-179-why-capture`, base `54f5965`, provisioned via `git worktree add C:/Programs/constellation-wt-179 -b epic178-179-why-capture 54f5965`).
**First step, before any git operation:** run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-179` — it must exit 0. Paste its output into your return report.
PR integration is server-side merge (the Admiral merges); you just open the PR.

## Inherited Context (platform invariants)
- Windows box. Command-checks/tests run under bash; use `py` launcher for Python. Run tests with `py -m pytest tests/test_checklist_engine.py -q`.
- When opening the PR: write the body to a temp file and use `gh pr create -F <file>` — never a heredoc or PowerShell here-string for `--body` (they fail for PR bodies on Windows).
- Set `PYTHONIOENCODING=utf-8` in the child env of any subprocess whose output you capture.
- `.agent-work/LESSONS.md` Active section is empty this run — no extra lessons apply.

## Budget
- **Model tier:** Opus (highest blast radius — the engine driving live runs).
- Bounded single-issue implementation; keep it tight.

## Stop Conditions
Stop and return when: the interface contract needs to change, you hit a spec contradiction, scope would exceed the fence, or you need context this order doesn't cover and can't safely proceed. Return-and-query the Admiral — asking up is always sanctioned.

## Return Shape
Write your result to **C:/Programs/constellation-skills/.agent-work/epic-178/crew-handoffs/179-result.md** (the MAIN checkout path, not your worktree — so the Admiral can read it) BEFORE going idle. Include:
- Verdict (done / blocked / honest-null) + one-paragraph summary.
- The `verify_worktree_isolation.py --here` output.
- Test command run + full pass/fail output (paste it).
- Files changed + a short diffstat.
- The PR URL (open it with `gh pr create -F`).
- Any Admiral floats (interface questions, spec gaps), map-impact notes, and triage candidates.
Deliver the artifact + PR before any idle notification — the Admiral judges completion from what you produced, not a late message.
