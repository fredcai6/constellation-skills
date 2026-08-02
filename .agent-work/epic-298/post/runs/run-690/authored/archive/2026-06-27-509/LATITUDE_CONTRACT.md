# Latitude Contract: `509` (parallel Phase-F slice)

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
Make progress on epic #509 (connected physics → prediction pipeline) by clearing a
**parallel wave of low-overlap Phase-F foundation/hygiene sub-issues** that can run with
little oversight, **while #525 (physics units audit) proceeds separately** on branch
`feat/physics-units-audit-525`. The outcome that must not be violated: no parallel work
collides with #525's `src/physics/*` param-naming churn, and no two parallel commanders
collide in shared write territory.

## Success Shape
Each selected issue reaches its own done-bar (acceptance criteria met, region tests green,
simplification-limits clean where applicable) on its own branch + PR. A measured negative —
e.g. a #461 hygiene item that turns out OBE/not-worth-doing, or a #476 script that should be
**retired** rather than re-homed — is a complete, successful deliverable when documented.

## Selected Issues (the parallel wave — pending confirmation)
Chosen for disjoint write territory (zero `src/physics` overlap → no #525 collision) and
bounded, low-ambiguity scope:

| Issue | Territory | Why low-overlap / low-oversight |
|---|---|---|
| **#504** split `smoother.py` | `src/preprocessing/trajectory/smoother.py` | Pure mechanical file-split, no behavior change, byte-identical guarantee; crisp acceptance (simplification_limits + region tests). |
| **#461** trajectory-grading hygiene | `src/preprocessing/trajectory/loaders.py` + a GP-name normalization helper + scipy pin (`pyproject`) | 4 small documented hygiene items; no shared file with #504/#476. |
| **#476** re-home orphaned scripts | `scripts/*` (imports the trajectory API, doesn't modify it) | Bounded "re-home or retire" against the current loaders/smoother API. |

**Excluded and why:** all `src/physics`-param issues (#502/#499/#506/#483/#443, #495/#503,
#494) overlap #525's churn or `session_fit.py`; queued Phase-C (#511/#512/#513) are unspecced
→ not low-oversight; #450 is gated/last. #501 (force-residual diagnostics) is a meatier
optional add but carries read-coupling to #525's renames + a partial #497 dependency.

## Checkpoint Protocol
**Cleared autonomous through wave completion.** Stop-and-present at: (a) the wave checkpoint
when all PRs are review-ready, and (b) any escalation. Status that reaches the user: a
plain-English per-issue summary (done / blocked / honest-null), PR links, and any decision
asks; technical depth on demand.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change (beyond the issue's stated split/re-home) | **surfaced** |
| Scope change (issue added/dropped/re-scoped) | **surfaced** |
| Merge to main | **delegated** — I may merge a green, clean-room-reviewed PR for these bounded issues, then report (overrides the default "ask first"; gated on check exit code + verified MERGED) |
| Issue filing / closing | **delegated** for filing follow-up/triage; **closing** the worked issues is delegated post-merge |
| Spend / budget / model tier | **delegated** (Sonnet commanders/crews unless a task needs more) |
| Production defaults / user-visible behavior | **surfaced** (none expected — all three are non-user-facing) |
| Retire-vs-keep a #476 script | **delegated** (commander decides per evidence; logged as RULING) |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

## Float-Up Routing
For a Commander **decision**: adjudicate delegated classes and log a RULING; escalate surfaced
classes + out-of-taxonomy to the human. For a Commander **context query**: answer from epic
knowledge and continue it; reach the human out-of-band when the answer is beyond my knowledge
or latitude. Cross-issue collision risk (a commander needing to touch another's territory) →
stop that commander and escalate rather than letting it cross fences.

## Comms
Plain English by default (user is on remote-control), technical depth on demand. Minimize
jargon/acronyms.

## Budget / Model Parameters
Commander tier: **Sonnet** per issue (all three are bounded/mechanical). Crew tier: Sonnet.
Each commander in its own explicitly-provisioned git worktree (Windows: Agent-tool
`isolation` is a no-op → provision with `git worktree add`, gate with
`verify_worktree_isolation.py`). No long detached compute expected (no training/gold runs).

## Pre-Rulings
Overridable by the human at any checkpoint.
- **#504**: public API of `StintSmoother`/`NSStintSmoother` must stay byte-identical; if a
  clean split is impossible without an API change, **stop and surface** — do not change the API.
- **#461**: any hygiene item that is OBE or net-negative → document as honest-null and skip; do
  not invent scope. The GP-name normalization helper lands in a shared util, not duplicated.
- **#476**: a script with no current consumer and no characterization value → **retire** (delete
  with a one-line rationale) rather than re-home; log the call.
- All three: stay strictly inside the territory in the table above. Touching `src/physics`
  param files is forbidden (that is #525's lane) → stop and escalate if a fix seems to need it.
- Tests use `py` (Python Launcher), `py -m pytest`. Run from repo root.

## Expiry
Event-based: **the wave checkpoint** (all three PRs review-ready) forces a contract refresh —
I present results and re-confirm before any merge-and-next-wave. Also expires if #525 lands a
change that shifts the base under a running commander.

## Confirmation
`2026-06-27 — confirmed by user ("go go go"): trio #504/#461/#476 as proposed, Sonnet commanders, autonomous through wave checkpoint, merge authority delegated.`
