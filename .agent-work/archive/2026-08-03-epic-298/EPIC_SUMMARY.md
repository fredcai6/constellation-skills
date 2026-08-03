# Epic-298 — Grander Scale, cut 1: map-first tracer + one-framework lessons rework

**12 of 12 issues closed. Everything merged. Corpus deployed at `5c6d977` (`sha256:e8bac5a3`).**

---

## What shipped

**B3 — the map-first contract (#304, #307).** The Commander spine template now anchors the map read
before any source file. **Measured: `map_before_src` went 0/4 → 4/4.** The PRE arm was not
map-deprived — the map existed, was cited in an auto-loaded `CLAUDE.md`, was read in 4/4 runs and was
useful — and it still scored **0/5 on orientation order**. Per-task delivery moved what always-loaded
delivery could not.

**Limitation stated first, as the arm itself did:** the manipulation was 8 days and +31 files, not
#304 alone. Containment proven, exclusivity not. And "map-first" as delivered means
**first-among-content, not first-among-actions** — the spine runs `init` before `context`, so the
first map read lands at call 17–29, never 0–2. You accepted that as the win; it is worth keeping the
distinction visible.

**B1 — the lessons rework (#301, #305, #308).** The playbook is retired. **23 episodes migrated —
20 lessons one-for-one, plus 3 of the run's own observations — with 11 of 23 carrying an honest
UNKNOWN and nothing back-filled.** Store now holds 32 active.

The sharpest cut of that: **zero `observed-behavior` fields are unknown.** All 15 unknowns sit in
*what someone expected beforehand* and *what it cost*. Those are the parts nobody ever wrote down.

**B2 — the kernel-break gate (#310). Verdict: `not-yet-earned`.** One of the two "no" outcomes your
spec explicitly blesses. **No break decided — that call is still yours.**

It rests on gate (b) alone: never run, n=0, the gates are conjunctive, so a conjunction with an unrun
conjunct cannot close. **That argument uses no unit, no threshold and no number**, which is why it
survived you cutting the trend census as premature.

---

## The two findings that constrain what you build next

Everything else in this epic is downstream of these.

**1. You cannot decompose a role whose load surface you cannot compute.** Named reference tokens do
not resolve inside their own role's directory — **10 of 21 as the commander measured it; 29 of 46
when the auditor re-derived it independently.** Same finding, different denominator, because they
tokenized differently.

**That disagreement is the second finding in miniature.** Even the corpus's own count of its
references is unit-dependent.

**2. There is no unit, not just no threshold.** `docent` ranks 1st by lines and 5th by bytes — the
order **fully reverses**. `curate_corpus.py` carries three units in one file with no stated
relationship between them.

**So when the kernel-break question comes back to you, it is two questions.** A threshold without a
unit is unanswerable, and picking one now would be exactly the premature idealizing you called out.

---

## What the audit says to do, and what to ignore

**Six findings promoted, 39 issue numbers dropped in seven named groups** — sums checked by command,
not by eye. Full artifact: `.agent-work/epic-298/LESSONS_AUDIT.md`.

The one worth acting on first is mechanical and cheap:

> **`a-check-that-cannot-fail` graduated at the crew tier and never at the orchestrator tier.**
> `docs/agents/CREW_CONTEXT.md` carries the whole family. A grep across `skills/_shared/`, every
> `SKILL.md`, every `references/` and `docs/agents/` returns **2 lines, both in that one file, none at
> orchestrator tier.** And the orchestrator tier is where every expensive instance was authored.

**It stopped recurring where it was written down and kept recurring where it was not.** That is a
mechanism, verified by grep, not a moral.

**The largest dropped group is 10 apparatus findings** — real, well-evidenced, and they only bind if
another measurement arm is ever run. Your read was right: most of the ~80 issues are sediment from
this epic measuring itself.

---

## What went wrong, honestly

**I was the epic's largest source of defects.** Roughly twenty of my claims failed against the tree,
and **every one was caught by the commander or panel I handed it to** — never by me.

The dominant shape: **I reason about what happened; the tree records what is in force.**

Three that cost you directly:

- **I destroyed the run log** by fast-forwarding `main` while `.agent-work/` was becoming tracked.
  292 entries recovered from scratchpad files and the session transcript; the archived log holds 458.
- **I re-conflicted my own PR** by committing to `main` while it was open, which cost you a failed
  merge attempt and a second CI cycle.
- **I orphaned cited revisions twice — the second time within an hour of filing the issue about it.**
  Knowing the rule did not prevent it, because the sweep's checks interrogate the branch being deleted
  and never what depends on it. All nine SHAs in the B2 verdict are now reachable from `main` or a
  pushed tag.

**Ten cold critics. Ten blocking defects caught. No exceptions.** The last one found the #310 verdict
selecting on the very gap it was escalating; the commander re-founded the verdict rather than patching
the wording.

**And your three interventions each cut real work:** withdrawing the two-bin rule, ruling
observations-not-diagnosis, and cutting the census as premature. The last one shortened #310
substantially and did not weaken its verdict at all — because the verdict never needed the numbers.

---

## Open for you

- **The kernel break** — undecided, with threshold *and* unit both handed up.
- **The ablation arm (#414)** — declined with a cost estimate so the decline is attributable, not
  asserted-impossible. A disposable single-role arm would make gate (b) genuinely runnable.
- **`wip/clean-codebase`** — still parked at `f704273`. **It is a rebase, not a rescue:** the skill
  itself does not conflict at all; only two wiring files do, and your edits there are +2 and +28 lines
  against `main`'s +469 of drift underneath them.
- **`settings.json` remains unwired (#180)** — the Context Governor still never fires. Which is why
  the gauge was silent for this entire multi-day run (#383).

_Epic-298 closed 2026-08-03. Log, briefs, audit, reconcile and launch orders archived at
`.agent-work/archive/2026-08-03-epic-298/`._
