# Latitude Contract: `epic-198-burndown`

Confirmed by the human before wave 1. The dial between "I don't care, go" and
"float me the details." Re-confirm on expiry or when the ground shifts under it.

## Epic Intent
Burn down the relevant backlog from the 2026-07-19 open-issue triage: the bounded bug/doc/engine
fixes across waves 1–3, plus the housekeeping closes that fall out. The "big" design threads
(#171, #172, #139, #136, #131, #156) are explicitly **out of scope** — Fred wants those discussed
on a clean basis afterward. Outcome that must not be violated: don't touch the out-of-scope design
issues, and don't make structural/architectural changes without surfacing them.

## Success Shape
Every in-scope issue dispositioned: fix merged, or closed as satisfied/duplicate, or deferred with a
logged ruling. A measured negative is a complete deliverable — if an issue turns out to be already
fixed or a non-problem, closing it with that finding is success, not failure. Done = waves 1–3 issues
merged/closed, housekeeping closes done, ROADMAP pruned of shipped threads, epic closed out through
the engine.

## Checkpoint Protocol
**Cleared autonomous through wave 3.** Post a brief plain-English status at each wave boundary
(what merged, what's next) — informational, non-blocking; Fred can interrupt to redirect. Stop-and-present
at completion for final acceptance. Surfaced-class decisions escalate as they arise (out-of-band).

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | surfaced |
| Scope change (issue added/dropped/re-scoped) | surfaced |
| Merge to main | delegated |
| Issue filing / closing | delegated |
| Fix-now triage (bounded fix applied immediately, not filed as an issue) | delegated |
| Spend / budget / model tier | delegated |
| Production defaults / user-visible behavior | surfaced |
| Doctrine/template edits that reshape doctrine (vs. mechanical graduation) | surfaced (at closeout) |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — code-target graduations (test suite as proof) autonomous; any graduation
  that edits project doctrine (`.md`/`.template.*`) is surfaced for human acceptance at closeout. Constellation
  debt is always exported, never silently confirmed.

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Merge to main | `gh pr merge`, branch push | Fallback: if classifier vetoes, get one live approval, batch remaining equivalent merges to the next wave boundary rather than re-asking per PR. |
| Issue filing / closing | `gh issue close/comment/edit` | Fallback: if vetoed, batch the closes into one approval ask at the wave boundary. |

## Float-Up Routing
Commander floats a `user-decision` in a delegated class → adjudicate and log a RULING. Surfaced class or
out-of-taxonomy → escalate to Fred out-of-band. Context query → answer from epic knowledge and continue the
Commander; reach Fred out-of-band only when the answer is beyond epic knowledge or latitude.

## Comms
Plain English by default (per standing register guidance); technical depth and evidence on demand. Project
dialect stays in agent-to-agent artifacts, not the status posts.

## Budget / Model Parameters
One Commander (or implementer-with-plan for the small bounded ones) per issue. Model tier by complexity,
**capped at opus, never fable**: engine/hooks issues (#153, #151, #152, #130, #191, #196) → opus; doc/test
graduations (#116, #118, #155, #157, #117, #192, #163, #189, #190) → sonnet where the change is mechanical.
Watch the subscription session pool on parallel waves; defer a wave past a limit reset rather than launching into it.

## Pre-Rulings
Each overridable by Fred at any checkpoint.
- Right-size dispatch: for a small bounded fix, dispatch an implementer-with-plan directly rather than a full Commander spine.
- #114 is a duplicate of #154 (same init-placeholder recurrence) → close #114 as dup, fold its regression-test ask into the #154 fix.
- #93's core ask (first real explorer dogfood run) was satisfied by the `explore-skillset-completeness` run that produced epic #164 → verify and close, don't re-run.
- #178 (Context Governor epic) v1 shipped+merged+dogfed → close the epic once its fast-follows (#189–192, #196) are dispositioned; the fast-follows stand on their own.
- An in-scope issue found already-fixed or a non-problem → close with the finding (honest null), don't invent work.

## Expiry
After wave 3 merge, or on any surfaced-class decision that changes epic scope — whichever comes first.

## Confirmation
2026-07-19 — confirmed by Fred: "go agree with defaults". Cleared autonomous through wave 3 with
non-blocking wave-boundary status; merge-to-main delegated; housekeeping pre-rulings approved; #136,
#131 out of scope (default); #117 tee-up-mechanical-defer-curator-run (default) accepted.
