# Launch Order: `cmdr-C — #545 pyright baseline-diff CI gate + aggressive triage cleanup`

Commanders start cold. Paste, don't point. **Run the FULL `constellation-commander` gated spine** (understand → plan → implement → review → integrate). Multi-step commander (explicit user preference). This is real tooling + code work, so full depth applies.

## Mission
Two parts, fix-then-snapshot order:

1. **Triage cleanup (do FIRST):** aggressively fix the easily-handled genuine pyright
   baseline errors across `src/`, so the committed baseline is as small as honestly
   possible. Confirmed target: **`src/physics/layer2/decoupled_calibration.py:435` —
   `"CaseResult" is not defined` (reportUndefinedVariable)** — this is a real
   undefined-name (a latent NameError if that path runs, OR a broken annotation);
   investigate and fix properly. Sweep for other TRIVIALLY-SAFE reductions (unused
   imports, obvious missing annotations, simple Optional-narrowing). Anything that needs
   a risky refactor or changes behaviour → leave it in the baseline and FILE an issue,
   don't force it.
2. **#545 — pyright baseline-diff CI gate:** make the `pyright` CI job gate on a
   **baseline-diff** (fail only on NEW errors vs a committed baseline; report fixed
   ones so the baseline can ratchet down) instead of the useless always-red pass/fail.

## Prior-Wave Verdicts (pasted)

**#545 full text:**
> **Surfaced during #509-w2 review wave.** Problem: the `pyright` CI job sits at a
> standing ~83-error baseline across `src`, so pass/fail is useless as a PR gate — main
> is always red. Confirming "this PR added no NEW errors" requires manually grepping each
> PR's pyright job log per-file (done 4× by hand in #509-w2; done AGAIN by hand this wave
> for PR #548). Suggested fix: gate on a baseline-diff — a checked-in baseline (e.g.
> `pyright --outputjson` snapshot) + a CI diff step that fails only on NEW errors; or a
> tool like pyright-ratchet / a small diff script. Refs #509.

**Live baseline facts (verified this wave):** on main `1c501ccf`, `python -m pyright`
reports ~77 errors over `src/` (down from 84 — PR #548's None-guard removed 6). Known
genuine error: `decoupled_calibration.py:435 "CaseResult" is not defined`. Two
`calibration.py` errors (tuple-return-type, `_fit_nonstationary_core` returns
`NSStintSmoother | None`) are pre-existing — annotate-or-leave per your judgment.

**pyright config:** `pyrightconfig.json` → `include:["src"]`, `typeCheckingMode:"basic"`,
excludes tests/venv/cache/data/archive. CI: `.github/workflows/typecheck.yml` runs
`python -m pyright` (currently bare, no baseline). pyright is **non-required** (main can
go red); the new diff job's exit code is what should distinguish NEW from baseline.

## Pre-Rulings
Ruled in advance, overridable with stated evidence.
- **Fix-then-snapshot:** reduce the baseline by fixing the easy genuine errors BEFORE
  you snapshot it, so the committed baseline reflects the cleaned state.
- **CRITICAL — line-number drift:** pyright error line numbers SHIFT when code above them
  changes (I hit this manually this wave: a calibration.py error moved 789→791 from lines
  added above it). A naive `(file:line:col, message)` baseline will false-positive on
  every unrelated edit. Your diff MUST normalize away volatile position — match on
  `(file, rule, message)` (drop line/col), or per-file error multiset, or an equivalent
  drift-robust key. State your chosen key and why it's stable.
- **Gate semantics:** the CI step fails (nonzero) ONLY on errors absent from the baseline
  (NEW); it should print NEW errors clearly and (nice-to-have) note errors fixed since
  baseline. Making the check "required" in branch protection is a repo-admin setting —
  out of scope; note it as a follow-up if relevant.
- **Don't force risky fixes:** an error needing a real refactor stays in the baseline +
  gets an issue. Honest-null: if robust baseline-diff in CI proves infeasible in budget,
  document why + file, and keep the documented manual norm — but this is expected to be
  very doable.
- **Self-test the gate:** prove it works — e.g. show it stays green on a no-op/whitespace
  change and goes red when you inject a deliberate new type error (then revert the inject).

## Honest-Null Clause
A measured negative ("baseline-diff in CI isn't feasible within budget for reason X") is a
complete deliverable if documented with evidence + a filed follow-up. Not expected here.

## Inherited Latitude
You MAY (delegated): all CI/tooling changes, the baseline file format + location, the diff
script design, fixing trivially-safe baseline errors, filing follow-on issues for
non-trivial ones. You MUST float: any change that would make a previously-passing required
check (arch-map, docs) start failing; any fix that changes runtime BEHAVIOUR beyond a
type/lint correction (surface it); any scope beyond #545 + baseline cleanup.

## File Ownership
Sole commander this wave (Wave-1 fences released — both prior lanes merged). Expected
territory: `.github/workflows/typecheck.yml`, a new baseline file (your chosen path, e.g.
`pyright-baseline.json` or `tools/`), a new diff script (e.g. `scripts/pyright_baseline_diff.py`),
`src/physics/layer2/decoupled_calibration.py` (the CaseResult fix) + any other src files you
clean. **DO NOT** edit `.agent-work/LESSONS.md`, `.agent-work/AGENT_FEEDBACK.md`, or
`.agent-work/CONSTELLATION_FEEDBACK.md`, and **DO NOT run `apply_lessons_delta.py`** — return
your lesson candidates + feedback IN YOUR REPORT; the Admiral applies them centrally at
closeout. (Two prior commanders deviated on this; don't repeat it.)
Findings file: `.agent-work/509-w3/crew-handoffs/cmdr-C-findings.md` (sole writer).

## Workspace
Worktree **already provisioned**: `C:\Programs\f1Brainz-509w3-ci`
- Branch: `chore/509w3-ci-cleanup`  ·  Base: `1c501ccf` (current origin/main, post-Wave-1)
- Created with: `git worktree add -b chore/509w3-ci-cleanup ../f1Brainz-509w3-ci origin/main`

First step, before any git op: `verify_worktree_isolation.py` does **NOT exist** — use the
native gate: `git -C "C:\Programs\f1Brainz-509w3-ci" rev-parse --show-toplevel` must return
your worktree path (NOT `C:\Programs\f1Brainz`, which is on the user's unrelated
`feat/541-parquet-telemetry-store` branch — do not touch it). Paste the output in your report.

## Inherited Context
Active lessons:
- **py-launcher:** `py` not `python` for running; tests `py -m pytest`. (Note: CI uses
  `python -m pyright` on ubuntu — that's the CI runner, leave it; locally use `py -m pyright`.)
- **shared-files-not-on-mission-branch:** never commit/edit `.agent-work/LESSONS.md`,
  `AGENT_FEEDBACK.md`, `CONSTELLATION_FEEDBACK.md`; return deltas in your report.
- **state-note-before-detach / crew-idle-strands-deliverable:** keep the state note current;
  poll any backgrounded sub-task to completion — the result file is the deliverable.
- **run-crew-cli-launcher-misfit:** dispatch crews via the Agent tool; record via run_crew.py
  pure functions; recover_crews before each dispatch.
- **handoff-cite-exact-seam-signature:** cite exact signatures from source.

Invariants: strict <1000 lines/file (`py -m src.utils.simplification_limits`); PR body via
temp file + `gh pr create -F <file>` (never heredoc / here-string for PR bodies).

## Data Locations
None needed (CI/tooling + type-error fixes; no telemetry). If a fix needs to import-check a
module, the worktree has all `src/` code.

## Budget
Model: **Sonnet**, full commander depth. This is bounded; should not need many hours.

## Stop Conditions
Stop and return when: a fix would change runtime behaviour or break a required check
(float); the baseline-diff approach hits an infeasibility (return the honest-null + a filed
issue); a decision outside inherited latitude is needed; or context is missing.

## Return Shape
Final report: what baseline errors you FIXED (per file) + what you LEFT (+ issues filed for
non-trivial ones); the #545 design (baseline file path + format, diff-key choice + why it's
drift-robust, CI step), your self-test evidence (green on no-op, red on injected error);
the final baseline error count; map impact; triage candidates; workflow feedback +
lesson candidates (do NOT apply them — return them); your `rev-parse --show-toplevel`
isolation output. Open ONE PR (`gh pr create -F <tempfile>`, title referencing #545 +
"Refs #509", `Closes #545`), required checks green, verdict in PR body, do NOT merge.
Commit trailers: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` +
`Claude-Session: https://claude.ai/code/session_01Pg84miea8Tmz2egJrGg2S4`; PR footer
`🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
