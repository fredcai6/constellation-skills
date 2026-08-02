# Latitude Contract Refresh: `601-fantasy-league` — next bite

## Epic Intent

Advance the confirmed fantasy-league research program toward the ~7.5 pts/race gap without guessing which model channel deserves capacity. This bite is issue #606: establish, from the league workbooks and leakage-free model results, where winners' advantage comes from.

## Success Shape

Issue #606 is complete when a tested normalization/reconciliation layer reproduces workbook totals, the scoring rule is pinned by multi-season fixtures, the model is inserted as a virtual competitor, per-channel point attribution is written up, and the result makes an evidence-backed capacity recommendation for DNF, quali, and physics work. An honest null or ambiguous attribution is acceptable if its scope and remaining uncertainty are explicit.

## Checkpoint Protocol

Cleared to completion. The Commander still runs design-it-twice and floats load-bearing choices, but the Admiral is authorized to adjudicate them and continue without waiting for the AFK owner. Continue through implementation, review, PR integration, issue disposition, and epic closeout while preserving the explicit safety and scope boundaries.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | delegated when required by confirmed epic scope; log ruling |
| Data/physics/evo boundary crossing | delegated when required by confirmed epic scope; log ruling |
| Scope change or new epic issue | delegated only when necessary to complete epic #601; log ruling |
| Merge to main | delegated |
| Push branch / open PR | delegated |
| Issue comments and bounded follow-up filing | delegated; log ruling |
| Issue closing | delegated |
| File deletion | delegated only inside the confirmed scope and after verification |
| Fix-now triage inside #606's fence | delegated; log ruling |
| Spend / model tier | delegated within the harness default; escalate materially long compute |
| Production defaults / user-visible behavior | delegated inside confirmed epic intent; log ruling |
| Apply a lesson / fold doctrine | delegated with normal evidence and export rules |
| Out-of-taxonomy | Admiral adjudicates conservatively; no unrelated scope expansion |

## Permission Prerequisites

| Delegated class | External actions | Pre-clearance or fallback |
|---|---|---|
| Push / open PR | `git push`, PR creation | Pre-cleared for this bite; if blocked, hold a verified local branch at checkpoint. |
| Issue comments / bounded follow-up filing | GitHub write | Allowed for evidence that otherwise becomes cross-session scratch; report at checkpoint. |
| Fix-now triage | Task-branch edits inside the frozen fence | Allowed only when bounded and required for #606's acceptance; otherwise defer. |

## Float-Up Routing

The Commander sends context questions and decisions to the Admiral. The Admiral answers facts from epic evidence, logs delegated rulings, and surfaces structural convergence, scope, merge, close, deletion, production behavior, and out-of-taxonomy decisions to the owner.

## Comms

Plain English first; technical evidence on demand.

## Budget / Model Parameters

One Commander for #606 in one explicitly provisioned worktree based on current `origin/main` (`919f1347` observed 2026-07-14). Use the harness default model tier and bounded foreground work. No multi-hour compute is expected; if discovered, return a plan before detaching it.

## Pre-Rulings

- The main checkout is stale and heavily dirty with pre-existing user work; do not update, clean, or build on it. Provision an isolated worktree directly from `origin/main` and fence all writes there.
- #604's command is merged in PR #613, but issue #604 remains open until the live Belgium shakedown; that does not block #606.
- Workbook totals reproduction is the first falsification gate. No channel-attribution claim is valid before it passes.
- The DB remains canonical for model truth. Workbooks are canonical only for league picks and recorded league totals; joins require explicit reconciliation rather than silent fallback.
- No hard-coded owner heuristic. FP/quali/reliability patterns must emerge from measured data.

## Expiry

At epic #601 completion, or if progress requires unrelated destructive action or scope beyond the confirmed epic.

## Confirmation

Confirmed by fredcai6 on 2026-07-14: "sounds good. you're authorized for agent use btw."

Expanded by fredcai6 on 2026-07-14: "im going afk. you're authorized for this and any other judgement calls. keep working without my intervention till completion".
