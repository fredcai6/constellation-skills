# Crash-resume state note — issue-467-trip-semantics

**Written by `commander-w4-467-i` at `g5-acceptance`. Replaces `commander-w4-467-g`'s note
wholesale — that note described the g4 rework, which is DONE and APPROVED.**

## Where the run is

- **step:** spine `execute` (in-progress) · `execute.json` gate **`g5-acceptance` — `complete`.**
  **15/17 complete.** Remaining 2: **`g5-review`** (ACTIVE, pending) and `g5-integrate`.
- **I TRIPPED AND STOPPED at 0.201541 >= hard 0.15**, my own live harness-written reading. I closed
  `g5-acceptance` carrying the full handoff (`w-15` — read it, it is the brief), filed the
  refresh-request `e-g5-review-1` against `g5-review` keyed to `w-15`, and released both leases.
  **This is a clean seam, not an interruption. Fourth live #431 on this run.**
- **next command:** `python C:/Programs/constellation-skills/scripts/checklist_engine.py --file
  .agent-work/issue-467-trip-semantics/execute.json current` — its `DIGEST:` is the whole handoff.
- **slug:** issue-467-trip-semantics · branch `epic-418/a2-467-trip-semantics` · worktree
  `C:/Programs/constellation-skills-wt/epic418-a2-467` · HEAD `cc4aed99`, tree clean at start.
- **engine leases:** RELEASED. Previously claimed by me on both `spine.json` and `execute.json` with
  `--session-id session_01TTKPTbD6nnMt7jFWw9GtjX` (no `--force`; every agent in this harness
  session shares that id, so `claim` takes the idempotent-resume path). **Verify against the raw
  JSON, not against this line.**
- **pid:** none — foreground. Agents A and B are synchronous Agent-tool subagents.
- **suite baseline at `cc4aed99`, my own run:** `1867 passed, 2 skipped, 829 subtests, exit 0`
  (`/tmp/g5_suite_baseline.txt`). Matches the g4 number.

## CORRECTION to my closing digest `w-15` — read this if you are cold-starting

`w-15` says "everything I produced lives under `.agent-work/`, which is ignored". **That is wrong:
`.agent-work/` is TRACKED here** (`git check-ignore` exits 1). I caught it right after the close and
committed everything at **`27ae8563`**; `git status --porcelain` is empty there. No file under
`scripts/` or `tests/` was touched — the engine blob is unchanged at
`c281cb68eaac65d1169dd6737a6a322728df98eb`. ACCEPTANCE.md section 8 carries the same correction.

## The acceptance round trip — what I built and where it is

Separate spine (NOT this run's spine), authored once and **never edited after agent A was
dispatched**, because editing it between A and B would smuggle a briefing to B:

- `.agent-work/acceptance-467/spine.json` — 2 gates `a1`, `a2`.
- `.agent-work/acceptance-467/check_gate.py` — the gates' `command` postcondition, strict about
  exact file content.
- `.agent-work/issue-467-trip-semantics/build_acceptance_spine.py` — the authoring script; it
  REFUSES to run twice.
- `.agent-work/acceptance-467/gauge.json` — planted fallback reading; the harness gauge writer
  overwrites it with each acting agent's own live fill once that agent claims the lease.

**The trip is engineered to fire on a LIVE reading, not on a plant.** Both gates declare
`context_headroom_tokens: 149000`, so the per-gate hard line is `1_000/1_000_000 = 0.001` and any
real reading is at/over hard. Verified in force: at a planted fill of **0.05** — well BELOW the
shipped 0.15 default — `current` renders the HARD band. That is impossible without the override.

`a1` carries a **pre-attached refresh-request** (`e-a1-1`, seam=a1) so agent A can `start a1` at
all; without it the begin-work guard refuses the first gate and nothing can run. That is the real
relaunch shape, not a contrivance: a fresh agent starting the gate a refresh was requested for is
exactly what I am on this run.

## The one rule that voids the measurement

**Agent B's dispatch prompt must contain NOTHING but the `current` output.** No summary, no
pointer, no help. `g5-review` reads B's actual prompt. If you are resuming me and B has not been
dispatched yet, re-derive `current` and paste it alone.

## Ordering ruling I am holding

Drive the RUN spine with MAIN's engine (`C:/Programs/constellation-skills/scripts/checklist_engine.py`).
`g5-acceptance` is the deliberate exception and exercises the **branch** engine
(`scripts/checklist_engine.py` inside the worktree), pinned by
`git rev-parse HEAD:scripts/checklist_engine.py` **re-derived at the moment of use** — never
copied forward from any document, including this one.
