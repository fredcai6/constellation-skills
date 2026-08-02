# Latitude Contract: `epic-601`

Confirmed by the human (Tommy / fredcai6) before wave 1, 2026-07-17.

## Epic Intent
Physics-as-feature-engine for evo: replace noisy raw lap-timing features with **believable, honest physics-derived capability features** as inputs to the evo qualifying predictor, and **prove whether they help** via an honest A/B, scored ultimately by fantasy pts/race vs actual. Underlying north star: beat human players in the ~20-player fantasy league, live 2026. The physics model is a first-class deliverable in its own right. Confirmed spec: `.agent-work/archive/2026-07-17-explore-physics-evo-hookup/DESIGN_SPEC.md`. Issues: #624(Ph0)+#623, #625(Ph1), #626(Ph2), #627(Ph3)+#506, #628(Ph3b), #513(Ph4), #629(Ph5), #630(Ph6), Ph7 folded.

## Success Shape
**The architecture is the deliverable; the gates refine it, they do not gate a go/no-go** (no automated kill switch — F1/F11). A measured negative at any gate (G0 correlation / G1 quali sign-acc+Brier vs the ~0.80 FP-data ceiling / G2 fantasy pts/race) is a **complete, successful, reportable deliverable**. "Done" for round 1: physics stability the user trusts, a consolidated stage-1 estimator, honest features flowing into evo through a clean seam, and a measured answer to "does this beat what we have."

## Checkpoint Protocol
**Stop-and-present at every phase boundary** (each phase issue = one wave). At a checkpoint the user gets a plain-English summary: what the wave built/measured, the gate read (either direction), any decisions asked, evidence on demand. Continue only on the user's go. Phase 0 additionally carries the spec-mandated informational scope-checkpoint (F1).

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | **surfaced** |
| Scope change (issue added/dropped/re-scoped) | **surfaced** (F1/F11 reserve scope cuts to the human) |
| Capability-ledger deferral (defer a phase/piece) | **surfaced** (spec-mandated human decision at checkpoints) |
| Merge to main | **delegated** (green + reviewed, merged sequentially, logged) |
| Issue filing (triage / follow-on) | **delegated** |
| Issue closing — a phase issue on verified-merged PR | **delegated**; closing the **epic** itself | **surfaced** |
| Fix-now triage (bounded fix applied, not filed) | **delegated — DEFAULT POSTURE is fix, not park** (see pre-ruling) |
| Spend / budget / model tier | **delegated** (policy below) |
| Production defaults / user-visible behavior | **surfaced** |
| Apply a lesson / fold doctrine | **surfaced** (doctrine graduations need human authority at closeout) |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Merge to main | `gh pr merge`, `git push` | Attempt delegated; **fallback** (classifier veto): one live user approval in the moment, batch remaining equivalent merges to the next checkpoint. |
| Issue filing/closing | `gh issue create/close/comment` | Attempt delegated; fallback: batch to checkpoint. |
| Fix-now triage | working-tree edits, commits | Pre-cleared (normal repo work). |

## Float-Up Routing
Commander floats a **decision**: adjudicate inside a delegated class → log a RULING in ADMIRAL_LOG; surfaced / capability-ledger / out-of-taxonomy → escalate to the user. Commander floats a **context query**: answer from epic knowledge and continue it; reach the user out-of-band only when the answer is beyond my knowledge or latitude.

## Comms
Plain English by default; technical/statistical depth on demand. Terse, no validation padding.

## Budget / Model Parameters
- **Commanders/crews: Sonnet default**; **Opus for the modeling/stats-heavy phases (2, 3, 3b, 4)** and for any adjudication needing deep reasoning.
- Commanders run as **full multi-step processes** (understand→plan→execute→reconcile), not one-shot implementers, per standing user preference. Right-size: a genuinely small, bounded issue may go to an implementer-with-plan.
- Detached long compute: state-note-before-detach, OS-detached (`Start-Process -WindowStyle Hidden`), no per-line watchers.

## Pre-Rulings
Each overridable by the user at any checkpoint.
- **Base = `main` (`c62a6430`) == `origin/main`** (verified clean fast-forward superset; the banner's fork alarm resolved). Wave worktrees branch from `main`.
- **Wave 1 = Phase 0** (#624 + #623). #623 (headless A/B deadlock) is fixed here as it gates every later automated gate.
- **#632** (f1_data DB bloat → 2GB, blocks DB commits): assess in Phase 0; fix if it blocks the tracer/A/B or DB commits, else file-and-defer with a note. Surface if it forces a scope decision.
- Honest-null is a complete deliverable at every gate — a null is reported, not treated as failure.
- Follow-on / triage issues may be filed without surfacing (delegated).
- **Proactive-cleanup default (owner ruling 2026-07-19):** commanders are pre-cleared to **fix small triage items in-flight** — a bounded, well-understood cleanup whose fix we already know — rather than parking it for closeout. Don't let small known-work items accumulate. Guardrails: (a) never let a cleanup destabilize a **frozen gate** — a fix that could touch held-out numbers rides its own small commit + independent review, freeze stays intact; (b) if a "small" item balloons past a bounded fix (new design, cross-cutting refactor, scope change), stop and float it — proactive ≠ scope-creep licence; (c) still record what was fixed in the verdict so the lessons audit sees it. Genuinely deferred items (too big / needs a decision) still get filed as issues, not silently dropped.
- Physics σ / covariance honesty is load-bearing — cross-view covariance persistence (Phase 3) is a non-deferrable minimum; do not let a commander quietly defer it.

## Expiry
~~End of this session, or after the Phase 3 merge~~ — REACHED 2026-07-19 (Phase 3 merged `59c2bc1f`).
**RENEWED 2026-07-19** (owner, same terms): present-at-each-phase · delegated-logged merges · Sonnet-default/Opus-hard. New sequence: **fix #644 (headless physics-fit hang) first** — it unblocks Phase 4 (#513) + the #646 store re-batch — then continue Phase 3b (#628) / Phase 4. New expiry: **end of session or after Phase 4 (#513) merge**, whichever first; cadence re-confirms at each phase boundary.

**RENEWED 2026-07-24** (owner "yeah cool let's go", same standing terms): Phase 4 (#513) merged `72577cef` → prior expiry reached. Terms carried forward unchanged — present-at-each-phase-boundary · delegated-logged merges · Sonnet-default/Opus-hard · proactive-cleanup-default (2026-07-19 amendment) · explicit-unknown contract · honest-null first-class. Concurrent authorized work: **Phase 5 (#629)** dispatched + the **powered F10 background run** (optimize-first ~5-10h, detached) commissioned. New expiry: **end of session or after Phase 6 (#630) merge**, whichever first; re-confirm at each phase boundary. Owner priority reminder: the powered F10 answer is the one deferred measured result — surface it when it lands.

## Confirmation
2026-07-17 — decision knobs confirmed by the user via AskUserQuestion (checkpoint=present-at-each-phase, merge=delegated-logged, model=Sonnet-default/Opus-hard). Contract body ratified below.
