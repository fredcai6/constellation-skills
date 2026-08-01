# Latitude Contract: `epic-138`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
Implement the #138 confirmed design spec (archived at `.agent-work/archive/2026-07-12-explore-138/DESIGN_SPEC.md`): engine rail (#140), hook suite (#141), clamp restoration (#142), fencing-aware gates closing #134 (#143), warm-register pass (#144), then the three measured arms (#145). The corpus finishes honestly and the measurement decides what stays.

## Success Shape
Wave 1: green, reviewed PRs for #140–#144. Wave 2: three arms run at N=3 with transcripts, results presented WITH the kill-condition call — which is the human's. A measured negative (an arm adding nothing) is a complete, successful deliverable, not a failure. Honest scoped nulls anywhere (e.g. the compact-trigger probe) are deliverables.

## Checkpoint Protocol
Cleared autonomous through wave-1 build and PR review. STOP-AND-PRESENT at: (1) merge time — the human names merges explicitly, always; (2) wave-2 results + shrink/kill-condition decision; (3) closeout summary. Checkpoints carry a plain-English summary + decision asks; evidence on demand.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | surfaced |
| Scope change (issue added/dropped/re-scoped) | surfaced |
| Merge to main | surfaced — human names each merge (standing rule) |
| Issue filing / closing | delegated (follow-up filings logged as RULING; #140–#145 closes ride their merged PRs) |
| Fix-now triage (bounded fix applied immediately, not filed) | delegated, logged |
| Spend / budget / model tier | delegated within the Budget section's tiers |
| Production defaults / user-visible behavior | surfaced (rail strings are user-visible engine output — but their wording is spec-frozen, so only a *deviation* from spec wording surfaces) |
| Eval/harness changes beyond #145's stated scope | surfaced (task.md purity is standing and inviolable) |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — delegated for playbook deltas via `apply_lessons_delta.py`, logged as RULING; constellation exports always exported, never silently confirmed; template/doctrine changes beyond the spec surface at checkpoint.

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Issue filing / closing | `gh issue create/comment/close` | worked all session without veto; fallback: batch to next checkpoint |
| Fix-now triage | local edits + branch commits in commander worktrees | no external surface; fallback n/a |
| Spend / model tier | Agent-tool dispatches at stated tiers | no external surface; fallback: surface if a dispatch is refused |

## Float-Up Routing
Commander `user-decision`s: adjudicated inside delegated classes as RULINGs; surfaced classes and out-of-taxonomy go to the human in plain text (no question dialogs — mobile). Context queries: answered from epic knowledge (the spec + this session's design record) and the Commander continued; beyond that, the human is reached out-of-band — a delegate is not a replacement.

## Comms
Plain English by default; technical depth on demand. Decision asks in plain text, never AskUserQuestion dialogs.

## Budget / Model Parameters
**HARD CAP (human ruling at confirmation): all subagent models are opus or lower — no Fable subagents.** Commander tier per issue complexity (least-powerful that works): #142 clamps + #144 warm register = sonnet (bounded wording work, spec-frozen text); #140 rail, #141 hooks, #143 gates = opus (engine/hook logic with subtle failure modes). #145 runs the harness (eval subjects are sonnet by design; `DEFAULT_MODEL` stays pinned `claude-sonnet-4-5` — do not touch). Small bounded issues (#144) may get an implementer-with-plan instead of a full Commander. Background dispatches + deadline watchdogs per fleet doctrine; wave-1 target ≤ ~1.5h wall-clock.

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each is overridable by the human at any checkpoint.
- Rail strings, pointer-with-force sentence, and four-clause clamps are used VERBATIM from the spec; any deviation a commander wants surfaces (spec-frozen text is a measurement precondition).
- Superpowers is a competitor: never cited or imported as authority anywhere in the epic's output.
- Source repo is authority: no commander edits installed copies under `~/.claude/skills`; skills are edited in-repo. (#141's settings.json/live-probe work uses temp sandboxes for probing, per the x2 method.)
- Eval `task.md` files: zero changes, zero coaching — any commander proposing one is refused and it surfaces.
- Flat register in ALL enforcement text; warm register only inside #144's stated boundary.
- One writer per shared document per wave; findings files assigned in launch orders.
- If #141's compact-trigger live probe returns a scoped null, the SessionStart re-injection ships for `source=resume` only, with the null recorded — do not block the wave on it.
- Worktrees provisioned explicitly with `git worktree add` and verified with `verify_worktree_isolation.py` (harness worktree flag is a no-op on Windows).

## Expiry
Event: after the wave-2 (measurement) checkpoint is presented and ruled, or 48h from confirmation — whichever first. Crossing it forces a contract refresh before further dispatch.

## Confirmation
2026-07-12 — confirmed by fredcai6 ("go for it"), with one amendment at confirmation: subagent models capped at opus or lower, no Fable subagents (folded into Budget above). Recorded as user-decision evidence on the latitude step.
