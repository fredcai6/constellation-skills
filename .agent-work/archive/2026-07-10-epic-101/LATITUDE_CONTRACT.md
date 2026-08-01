# Latitude Contract: `epic-101`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
Execute issue #101 (confirmed shaped-design spec, skill-simplification): consolidate the accreted skills corpus (dedup, diets, hygiene, entry-split), add the curator skill and the autonomous eval harness. Primary wins are drift-elimination and patch-once maintenance; the spec's cross-cutting conventions and mechanical regression net are binding. The confirmed spec is the authority — no re-litigation of its dispositioned decisions.

## Success Shape
All six clusters (A–F) dispositioned: merged, or honest-null closed with evidence, or deferred with a logged ruling. A measured negative (e.g. a dedup move that turns out unsafe on reconcile) is a complete deliverable when reported with scope. E is sequenced last and explicitly separable — the epic can close with E deferred if the human so rules at its checkpoint.

## Checkpoint Protocol
Cleared autonomous to completion (human amendment at confirmation: "just go knock it out"). Wave summaries are logged in the ADMIRAL_LOG as they complete; the full epic summary is presented at closeout. Surfaced decision classes and out-of-taxonomy still escalate immediately — clearance covers pace, not scope.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change (beyond what the spec specifies) | surfaced |
| Scope change (issue added/dropped/re-scoped vs the spec) | surfaced |
| Merge to main (green checks + reviewed, within spec scope) | delegated |
| Issue filing / closing (cutting the spec's clusters into child issues; closing them on merge) | delegated |
| Fix-now triage (bounded fix applied immediately, not filed as an issue) | delegated |
| Spend / budget / model tier (within the Budget section's bounds) | delegated |
| Production defaults / user-visible behavior (anything a downstream consumer of the skills sees that the spec didn't settle) | surfaced |
| Per-move execution detail (wording reconciliation on reconcile-then-cut, file placement within a spec-named destination, test naming) | delegated |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — delegated for lessons already Active in `.agent-work/LESSONS.md` (applies logged as RULINGs); new constellation-level doctrine changes beyond the spec are surfaced.

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Merge to main | `gh pr merge`, `git push` | 2026-07-10 human pre-clearance: "okay to merge this and future waves" — covers all remaining epic-101 wave merges (each still verified green + reviewed by Admiral before merging); if the classifier still vetoes a specific merge, queue it for a live approval |
| Issue filing / closing | `gh issue create/close/comment`, `gh pr create` | fallback: same shape — one live approval, batch the rest |
| Fix-now triage | commits within worktrees | no external surface; none needed |

## Float-Up Routing
Commander `user-decision`s inside delegated classes: adjudicate, log RULING. Surfaced classes and out-of-taxonomy: escalate to the human with the Commander's framing plus my recommendation. Context queries: answer from the spec/epic knowledge and continue the Commander; anything the spec doesn't settle and my latitude doesn't cover goes to the human before continuing.

## Comms
Plain English summaries at checkpoints; technical depth on demand. Plain-text decision asks only (no question dialogs — mobile constraint).

## Budget / Model Parameters
Commanders inherit the session model by default. Right-sizing: cluster D (hygiene) is small/bounded → direct implementer-with-plan dispatch, not a full Commander. Model-tier per issue recorded in each launch order. No hard token budget set; flag at a checkpoint if a wave's spend looks disproportionate.

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each overridable at any checkpoint.
- Sequencing per spec guidance: Wave 1 = A + D; Wave 2 = B + F; Wave 3 = C; Wave 4 = E (last, separable). A before B; C after A/B/F; F's manual fresh-context selection check runs before E exists.
- Cluster A constraint is contractual: append only to existing `global-*.md` bucket files; never mint a new `global-*.md` name; every move is reconcile-then-cut with pasted before/after grep carrier counts as gate evidence.
- Superpowers is a competitor: no citing or importing its doctrine anywhere in this epic's output; ROADMAP items stay constellation-native.
- Interrogator gets a register rewrite under B, not a split; F is commander-only.
- Where source-repo skills and installed copies diverge, the source repo (`skills/`) is authority; installed copies update via the installer.
- Honest-null on any single dedup move (unsafe on reconcile) → skip the move, keep the inline copy, log the finding; does not block the rest of cluster A.

## Expiry
Event: epic closeout acceptance, or any ground-shift (spec amendment, main diverging under an active wave) — whichever first forces a contract-refresh decision.

## Confirmation
2026-07-09 — confirmed by fredcai6 ("you got it bro, we discussed a lot already, just go knock it out"); checkpoint protocol amended to cleared-to-completion. Recorded as user-decision evidence on the latitude step.
