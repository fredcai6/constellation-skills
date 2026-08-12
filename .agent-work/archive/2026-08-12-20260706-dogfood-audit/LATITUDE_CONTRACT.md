# Latitude Contract: `20260706-dogfood-audit`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
Pay down the constellation debt surfaced by the 2026-07-06 dogfood audit (f1Brainz / network_elo / story_time corpora) and import the superpowers-inspired improvements: issues #42–#56 on fredcai6/constellation-skills. The outcome that must not be violated: the lessons loop closes (capture → apply/export/defer → verify), and no dogfood-confirmed engine defect with ≥3 recurrences survives the epic unfixed or un-dispositioned.

## Success Shape
Every issue #42–#56 dispositioned: merged, honest-null closed (documented negative — e.g. an issue's premise disproven by the current code — is a complete, successful deliverable), or deferred with a logged ruling. Test suite green on main at closeout. HITL design issues (#53, #54, #55) close with a recorded decision even if implementation is deferred.

## Checkpoint Protocol
Cleared autonomous through wave boundaries for AFK issues; brief plain-English wave summaries posted as the run proceeds. **Mandatory stop-and-present at the end of wave 2** to ratify the three HITL designs (#53, #54, #55) before wave 3 dispatch, and for #56's cross-repo issue-filing dry-run. Final stop at closeout for epic acceptance. Evidence on demand at any point.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | surfaced |
| Scope change (issue added/dropped/re-scoped) | surfaced |
| Merge to main (green, reviewed AFK issue PRs) | delegated — logged as MERGE |
| Merge to main (#42 branch merge) | surfaced (named HITL in the issue) |
| Epic issue closing on merge | delegated |
| Cross-repo issue filing (#56) | surfaced (human-gated by design) |
| Spend / budget / model tier | delegated within Budget section |
| Production defaults / user-visible behavior | surfaced |
| HITL design ratification (#53/#54/#55) | surfaced at wave-2 checkpoint |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — delegated for this epic (the epic IS lesson application); each apply logged as a RULING; constellation lessons always exported, never silently confirmed.

## Float-Up Routing
Commander `user-decision` floats: adjudicated inside delegated classes as logged RULINGs; surfaced classes and out-of-taxonomy escalate to the human. Context queries: answered from epic knowledge (the audit corpus and issue set) and the Commander continued; beyond that, the human is reached out-of-band before continuing.

## Comms
Plain English summaries at checkpoints; technical depth on demand; ADMIRAL_LOG carries the full audit trail.

## Budget / Model Parameters
Commander tier: sonnet for doctrine/template/docs issues (#45, #49, #50, #51, #52); opus for engine/code issues (#42, #43, #44, #46, #47, #48) and design issues (#53, #54, #55); #56 sonnet. Crew dispatches inherit the commander's tier or lower. Three waves of ~5 commanders; sequential merges per wave.

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each is overridable by the human at any checkpoint.
- **PR-1**: #42's commander works in the MAIN checkout on the existing `constellation/lessons-apply-or-defer` branch — the uncommitted Task 7 work lives only there. Every other commander gets a dedicated worktree; no other commander touches the main checkout during wave 1.
- **PR-2**: Wave plan — W1: #42, #44, #46, #49, #56 · W2 (after #42 merges): #43, #45, #47, #50, #51 · W3: #48, #52, #53, #54, #55 · W4 (user scope addition 2026-07-06): #58 brainstorm skill (HITL design), #59 engine re-plan (semantics ratified at a checkpoint), #60 triage fix-now lane (AFK), #61 explainer-website skill (HITL design). One checklist-engine writer per wave (#44 → #47 → #48 → #59). Merge order within a wave adjudicated by the Admiral; rebases at wave boundaries only.
- **PR-3**: Where existing doctrine (e.g. `global-everyone.md` attach-to-both guidance) documents a workaround an issue eliminates, the commander updates that doctrine in the same PR — doctrine follows mechanism.
- **PR-4**: "Test suite green" = repo's pytest suite exit 0, output pasted as evidence.
- **PR-5**: If investigation shows an issue's premise no longer holds against current code, close it honest-null with the documented negative; do not build to the stale premise.
- **PR-6**: Commanders run as autonomous delegates: interrogation resolves against their frozen LAUNCH_ORDER; genuine gaps float to the Admiral, never block on an unreachable human.

## Expiry
Event: epic closeout acceptance, or 7 days from confirmation — whichever first. Ground-shift (e.g. main moves under an unmerged wave in a way rebases can't absorb) forces a contract-refresh decision.

## Confirmation
2026-07-06 — confirmed by user ("Confirmed — launch wave 1", AskUserQuestion in-session); recorded as user-decision evidence on the latitude step.
