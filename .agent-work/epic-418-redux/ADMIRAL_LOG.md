# Admiral Log — `epic-418-redux`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Contract: `.agent-work/epic-418-redux/LATITUDE_CONTRACT.md` · Plan: _pending latitude; spec of record is `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md`_

The run's audit trail and the closeout retrospective's primary input. Append entries **as they
happen** — an unlogged ruling didn't happen. Own errors in the open: an ADMIRAL ERROR
entry that names the mistake and the fix is a closeout asset, not a liability.

Entry grammar (one line of date + tag, then the substance):

- `RULING` — an adjudication inside delegated latitude: what was decided, under which decision class, and why.
- `WAVE` — a wave launched: commanders, issues, worktrees, key launch-order terms (pre-rulings, fences, budgets).
- `INCIDENT` — a commander/crew death, stall, collision, or environmental kill: what died, autopsy, recovery action.
- `MERGE` — a PR merged: checks gated on exit code, diff verified in-fence, merge style and why.
- `ADMIRAL ERROR` — a mistake you own: what happened, cost, immediate fix, lesson candidate.
- `CHECKPOINT` — a contract checkpoint reached: what was presented, what the human decided.
- `ESCALATION` — a surfaced or out-of-taxonomy decision sent to the human, and the answer.
- `TRANSITION` — a replan boundary exit (`advance` / `repair` / `replan` / `stop`), verified.

## Predecessor run

This is a **relaunch**, not a fresh epic. The predecessor Admiral run (`epic-418`, 2026-08-05
to 2026-08-07) completed waves 0 and 1 and stopped clean before wave 2, after Tommy confirmed a
revised spec. Its artifacts are archived at `.agent-work/archive/2026-08-07-epic-418-waves-0-1/`.
What carries forward, and must not be re-derived:

| Fact | Source |
|---|---|
| Wave 0 (#419 #420 #422 #425) and wave 1 (#440 #447) merged and closed | predecessor STATE_NOTE, verified against the tracker |
| Spec of record is the REVISED_SPEC, CONFIRMED 2026-08-07 | `verify_spec_confirmed.py` exits 0 on `--phase review` and `--phase confirm` |
| Execution order: B extended → A2 → F → C → E; A-remainder and D-debt off-chain | REVISED_SPEC |
| `python -m pytest`, never `py`; `FORCE_COLOR=` and `NO_COLOR=1` or you get false reds | #454, fixed; `_COMMON.md` |
| Spine rail misattributes a descendant's gate to its ancestor — never obey a rail naming another spine | #457, live defect, 10 firings last session |

## Rulings & events

- `2026-08-07` — `RULING`: **Relaunch as `epic-418-redux` rather than resuming the predecessor spine.**
  Tommy's instruction was to archive the prior work and start fresh, and the predecessor's latitude
  contract had already expired by its own terms (expiry: the wave-1 checkpoint, which passed). A
  fresh spine plus a fresh contract is the honest state, and it is what the expiry clause demands.
  Decision class: out-of-taxonomy under the expired contract, resolved by the human's direct
  instruction in session.

- `2026-08-07` — `ADMIRAL ERROR` (caught before it cost anything): **the installed Admiral skill is
  stale against this repo, and I loaded the stale copy.** `Skill(constellation-admiral)` served
  `C:/Users/fredc/.claude/skills/constellation-admiral/`, which diverges from the repo's own
  `skills/admiral/` in two load-bearing places:
  1. `execute` — the repo's version carries the **iterative replan** loop (`NEXT_WAVE.json`,
     `transitions/<boundary-id>/` REPLAN_INPUT/RESULT packets, `TRANSITION` log lines, and a
     blocking `verify_iterative_role_artifacts.py admiral-prelaunch` check before any launch).
     The installed copy has none of it.
  2. `closeout` — the repo replaced the LESSONS-inbox model with **episodes**
     (`apply_episode_delta.py`, `verify_episode_captured.py`). The installed copy still runs the
     lessons auditor and `verify_agent_feedback.py`.

  This is the exact hazard `checklist-engine.md` warns about under dogfooding: nothing in the
  Skill-tool invocation flags which copy governs. **Fix applied:** the spine was instantiated from
  the repo's `skills/admiral/templates/ADMIRAL_SPINE.template.json` with
  `--skill-dir C:/Programs/constellation-skills`, so every check command resolves to the repo's
  vendored `scripts/`. Verified: the spine's three command checks point at
  `C:/Programs/constellation-skills/scripts/`. **Open risk carried:** Commanders I dispatch will
  load the *installed* crew skills, which may be stale the same way. Resolved before wave 1 — see
  the install-sync entry below.

- `2026-08-07` — `RULING`: **staleness quantified before asking Tommy to act on it** — I had one
  example and a recommendation resting on it, which is not evidence. Enumerated by command
  (`diff -q` per skill, repo `skills/<n>/` vs `~/.claude/skills/constellation-<n>/`): **12 skills
  diverge**, 6 of them in `SKILL.md` itself — `admiral`, `commander-delegated`, `docent`,
  `explorer`, `workbench`, `write-a-skill` — plus template drift in `cartographer`, `charter`,
  `commander`, `interrogator`, `reviewer`, and a script diff in `replan`. The load-bearing one for
  this run is **`commander-delegated`**: that is the skill every Commander I dispatch will load, and
  `workbench` carries the engine reference and spine templates underneath all of them. This turns
  decision 1 from a tidiness question into a correctness one. Decision class: out-of-taxonomy
  (mutates the human's global skills directory) — surfaced, not self-ruled.

- `2026-08-07` — `ESCALATION`: **latitude gate blocked on Tommy's confirmation** (engine: `latitude ->
  blocked`, bubbled to parent). Postcondition c2 is a `user-decision` artifact and cannot be
  self-satisfied; waiving it would be me deciding for the human, which is the one thing the bookend
  exists to prevent. Draft contract written; five decisions put to him in session:
  1. Re-run `install_constellation.py` to sync the stale installed corpus before wave 1? (recommended yes)
  2. Wave 1 shape — #433 + #460 as Commanders, #461/#464/#465 as implementers, #436 optionally riding along
  3. Run-ahead checkpoints vs stop-and-wait at each wave boundary (recommended run-ahead)
  4. Expiry — wave-2 boundary or 72h (recommended)
  5. Close #447 with evidence, and correct #418's stale spec pointer — both `surfaced` by class

- `2026-08-07` — `RULING`: **predecessor archived, revised spec carried forward rather than archived.**
  The spec is the live plan, so `spec-revision/` moved to `.agent-work/epic-418-redux/`; everything else
  from the `epic-418` run went to `.agent-work/archive/2026-08-07-epic-418-waves-0-1/`. Epic #418's body
  still points at the old spec path, so a breadcrumb sits at `.agent-work/epic-418/README.md` until the
  tracker pointer is corrected (queued as decision 5 — tracker edits wait for the contract).

- `2026-08-07` — `RULING`: **green-main baseline established for the wave, pinned to its revision.**
  `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` at `ca0e36a` (= `origin/main`, tree clean of
  source changes): **1721 passed, 4 skipped, 643 subtests, exit 0**, 309s. Real exit code captured,
  not inferred from the summary line.

  Recorded as a **discrepancy, not reconciled**: the predecessor's own STATE_NOTE carries two
  different figures — "1723 passed, 2 skipped" as the wave-1 green, and "main green at 1764 passed"
  for the #440 merge. Neither matches this run's 1721/4 (same total of 1725 collected as the first;
  two tests moved passed → skipped). I am not re-deriving where their numbers came from — the
  baseline any wave-1 PR is judged against is **this** one, at this SHA. Skips are environment-
  conditional, which is the likely cause and is cheap to confirm if a wave-1 review ever leans on it.

## Closeout

- _pending_
