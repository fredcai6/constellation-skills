# Latitude Contract: `tire-age`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
Take a hack at **tyre-age grip-evolution**: characterize how grip evolves with tyre age in races —
`μ_eff = μ_tyre(compound, age) × T_track(session)` — anchored by a fuel-mass model, producing an
equivalent ideal lap at any race point. Sub-epic of #509 (physics→prediction), Phase-C. The outcome
that must not be violated: honest covariance (no over-claiming on thin evidence), a single canonical
execution path, DB/telemetry-store as the only data source, and **measured-not-wired** (Phase-C
characterization; no evo wiring — that is Phase-P #450).

## Success Shape
Done = the foundation built and tested (mass model; race-session five-view fit path), then the
tyre-age grip-evolution output characterized to the §4 done-done bar (full test coverage · honest
covariance · single path · traceable dashboard) **plus the ratified supplant test** (does physics
μ(tyre-age) beat lap-time compound estimation?), landing a **per-axis readiness verdict** (GO /
CONTEXTUAL / NO-GO). **A measured negative is a complete, successful deliverable** — "race-fits can't
separate tyre from track at usable σ" or "physics doesn't beat the incumbent" bounds the bet and is a
legitimate terminal state. #443 (empirical telemetry grip-contrast sensor) is the independent
cross-check / the incumbent-challenger feeding the supplant test.

**The deep priority is a solid, expandable base** — the first build is a *baseline*, not the answer;
the user expects to pivot to research/improvement right after. Expandability is a first-class design
criterion (session-agnostic interfaces, injectable priors, per-axis vector channel, infra-reuse). A
**research-plan-for-improvement is a required closeout deliverable**, concretely a **list of 25 ideas
to try ("see what sticks")** in #443's throw-it-at-the-wall spirit — tested against the (now
load-bearing) pairwise-`P` evaluation harness (the iteration roadmap: deferred #443 threads,
fuel/team-mass estimation, richer sensors, the W3 separation refinements).

## Checkpoint Protocol
**2026-06-29 UPDATE (user AFK, "I'll trust you to manage it"): cleared-to-completion / autonomous.**
The Admiral runs the full chain end-to-end without per-wave human approval, adjudicates W2→W3 shaping
from the diagnose-first evidence itself, and presents the complete epic readout (+ the 25 improvement
ideas) when the user returns. Honest-null at any wave is a valid terminal state to proceed/close on.
The W2-merge contract-refresh becomes a self-adjudicated decision logged in the ADMIRAL_LOG (surface
on return). Escalate to the user out-of-band only for a genuinely epic-invalidating surprise.
*(Original: stop-and-present at every wave boundary — superseded while AFK.)*

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change (new fit path, new physics model shape) | **surfaced** |
| Load-bearing physics/modeling choice (fuel-burn rate, tyre↔track separation method, supplant metric) | **surfaced** |
| Scope change (issue added / dropped / materially re-scoped) | **surfaced** |
| Merge to main | **delegated** (2026-06-29, while AFK — merge green, reviewed PRs gated on check exit codes; was: surfaced) |
| Issue filing (foundation issues under #509: mass model, race-fit path, tyre-age, #443 arm) | **delegated** (within the agreed decomposition; all tracked under epic #509 for orderliness) |
| Issue closing | **delegated** (2026-06-29, while AFK — close after merge verified, per lesson:admiral-close-after-merge-verified; was: surfaced) |
| Routine execution (module placement under src/physics, fit hyperparameters, test layout) | **delegated** |
| Spend / model tier per issue | **delegated** |
| Production defaults / user-visible behavior | **surfaced** (none expected — Phase-C is measured-not-wired) |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

## Float-Up Routing
Commander floats a `user-decision`: delegated class → I adjudicate and log a RULING; surfaced /
out-of-taxonomy → I escalate to you. Commander **context query** (needs a fact/clarification) → I
answer from epic knowledge and continue it; beyond my knowledge/latitude → I reach you out-of-band.

## Comms
Plain English by default, minimal jargon; technical/physics depth on demand. **Posture for every
launch order:** take null/negative results *in stride* — a measured null is a successful baseline
step, not a failure; build the baseline, don't thrash or overreact to a negative, stay confident we
figure it out over the long run.

## Budget / Model Parameters
Commanders default **Sonnet**; **Opus** for W3 (tyre↔track separation + supplant test is subtle).
Crews Sonnet. Session-window aware (a reviewer hit a session limit in #512 — keep crew tasks bounded,
verify from artifacts not liveness).

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each is overridable by you at any checkpoint.
- **W1 first dispatch gated on #495 merged to main** (race-fits must sit on the hardened fit base).
- New code lands as **new modules under `src/physics/`** (race-state / mass), reading existing seams
  read-only; do not edit existing physics files pre-#495-land.
- **Fuel-mass is a known-physics anchor** (reg-min start fuel + linear burn), **not fitted** (spec MODEL_SCOPE).
- **Scope = 2022+ ground-effect era** (signal genuinely absent pre-2022 per #443); first build season
  **2023** (matches the existing 2023-Q estimate pool), structured for multi-season.
- **Measured-not-wired** — no evo wiring this epic.
- Honest-null is a complete deliverable; a NO-GO verdict is success.
- Shared playbook files (`LESSONS.md` / `AGENT_FEEDBACK.md` / `CONSTELLATION_FEEDBACK.md`) and a
  commander's own `.agent-work/<id>/` are **never committed on a mission branch** (applied centrally at closeout).
- **All epic issues filed under #509** (tracking-orderly); decomposition: mass model, race-fit path,
  tyre-age (#511), #443 arm.
- **Parallelize where dependencies allow.** The chain W1→W2→W3 is sequential, but the #443 empirical
  arm runs **parallel with W2**, and any independent sub-pieces within a wave parallelize.

## Expiry
**Re-confirm after W2 (race-fit path) merge**, or 72h, whichever first — W2's coverage result will
materially shape W3, so the contract refreshes before W3 dispatch.

## Confirmation
`2026-06-28 — LOCKED by user ("let's goooo") after full 18-question per-wave pre-interrogation and
presentation of the consolidated plan (WAVE_DESIGNS.md). W1 dispatch gated on #495 landing; contract
re-confirms after W2 merge.`
