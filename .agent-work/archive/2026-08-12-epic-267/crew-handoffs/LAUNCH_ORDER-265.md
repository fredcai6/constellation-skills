# LAUNCH ORDER — issue #265 (governor: make non-reading visible)

> Epic #267, wave 2, batch 1. You are Commander `governor-265`. You own this issue end to end.
> Workspace fields were completed by the Admiral at dispatch.

## Mission

**Give the engine a way to say "the Governor is not reading" as distinct from "the Governor reads low."**

Today a missing context reading is silent, and silence is indistinguishable from healthy low fill. #252
already solved exactly one cause (uncalibrated model → `gauge-uncalibrated.json` sidecar +
`_uncalibrated_advisory()` surfaced on `current`). Its reasoning — *an unexplained silent governor is how
a miscalibration survives unnoticed* — is correct and generalizes to the causes it did not cover:

| Cause | Signal today |
|---|---|
| Hook not wired at all | none |
| No binding for this session (resume/compaction) | none |
| Transcript unreadable / no usable `usage` record | none |
| Gauge stale — collapses to `None` in the reader by design | none |
| **Ambiguous binding — two spines under one session id** | **none — see live evidence below** |
| Model uncalibrated | advisory (#252) |

The design constraint from #252 is settled and **not open for relitigation**: *fail-safe must not mean
unexplained.* A missing reading must never force or block — but it must be visible.

The issue lists candidate shapes (liveness line on `current`; a `doctor`-style wiring/binding/freshness
check; extending the `_uncalibrated_advisory` seam). **These are candidates, not a spec.** Choosing among
them, or proposing a better one, is your call and is the substance of this mission.

## This is now the highest-value issue in the wave — here is why

The Admiral promoted #265 from co-equal into batch 1 on the strength of a live incident, reproduced and
repaired hours before your dispatch. **Read this carefully; it is your best test case.**

The Admiral's own gauge froze at `fill_fraction 0.121553`, `observed_at 00:30:09Z`, and stayed frozen for
26 minutes across a PR review, a merge, a worktree sweep, a lessons harvest and four issue filings.
Wiring was intact. Driving `gauge_writer_hook.py` manually as a subprocess produced **exit 0, no write,
no output, not even a refreshed `observed_at`.**

Cause: `.spine-rail-binding.json` held **two** spines under the Admiral's session id — its real
`epic-267/spine.json`, and a **phantom** `.agent-work/governor-269/spine.json` that does not exist on
disk. A dispatched Commander inherits the parent's `session_id` (#263) and its hooks resolve state paths
to the main checkout regardless of worktree (#269/#275), so the subordinate's binding landed under the
Admiral's key. The writer could not choose, and failed open in silence.

Repair proving causation — one phantom entry removed, nothing else changed, same hook re-driven with the
same payload:

```
before:  {"fill_fraction": 0.121553, "observed_at": "2026-07-28T00:30:09.105Z"}   (26 min stale)
after:   {"fill_fraction": 0.102681, "observed_at": "2026-07-28T00:56:01.801Z"}   (live)
```

Full write-up: issue #271. Pre-repair state preserved at
`.agent-work/harvest-267/governor-269/binding-BEFORE-repair.json` in the **main checkout** (read-only to you).

**What this means for your mission.** The gauge failed to the *reassuring* state — a plausible number
that had quietly stopped moving. There was no error, no empty gauge, no flag. It was caught only because
a human-facing agent happened to look. Your work is what would have caught it automatically. The
ambiguous-binding case is not in the issue's original table; treat it as a first-class cause.

**Two properties worth designing for, offered as observations not requirements:**
- *Staleness is not conservative.* The stale reading here happened to be high. Nothing in the mechanism
  guarantees that; a stale-low reading is equally possible and would under-report pressure. Do not build
  anything that assumes silence errs safe.
- *The blind window is the dangerous one.* This failed at the exact moment the gauge mattered most —
  mid-wave, adjudicating returns. A signal that only surfaces at session start would not have caught it.

## Prior-wave verdicts — pasted, load-bearing

**#261 / #202 (wave 1, merged `2c169a5`).** Session→spine binding is now two-level:
`binding[session_id][abs_spine_path]`. Binding happens on resume, not only on `claim`. The old flat shape
is detected and filtered (fail open). This is why two spines under one session id is now *representable* —
wave 1 fixed the clobber, which means the ambiguity now persists instead of being overwritten.

**#269 (wave 2, merged `e3f6a5c`).** Three verdicts:
1. *Doctrine shipped.* Git worktree isolation is **not** hook-code isolation. `CLAUDE_PROJECT_DIR` is
   fixed at session launch and inherited unchanged by every subagent.
2. *Detection — verdict NO.* `verify_worktree_isolation.py` should not report hook resolution:
   `CLAUDE_PROJECT_DIR` is **empirically unreadable** from an ordinary tool subprocess (probed live in
   both Bash and PowerShell → empty). The harness injects it only when constructing a hook subprocess.
3. *Analysis only.* Hook **code** resolution is unchanged and stays pinned to the main checkout pending a
   human ruling. `decision:no-resolution-change` remains in force for you too.

**Also surfaced by #269, directly relevant:** `gauge_writer_hook.py` is wired **only** via
`.claude/settings.local.json`, which is gitignored and exists only in the main checkout. **A Commander in
a worktree has no gauge writer running at all.** That includes you. Do not interpret your own absent
gauge as evidence about your change.

## Pre-rulings — decided, do not re-open

- `decision:fail-open-is-inviolable` — every hook path exits 0 and never blocks a turn. Making a
  non-reading *visible* must not make it *blocking*. Visibility and enforcement are separable; you are
  building visibility only. `@grade: settled/inherited`
- `decision:no-threshold-values` — **do not introduce, tune, or hardcode any threshold value, including
  in test fixtures.** Any threshold number always surfaces to the human and is never delegated. If your
  design needs one, stop and float it. Staleness bounds count as thresholds. `@grade: settled/human`
- `decision:no-resolution-change` — do not change how `CLAUDE_PROJECT_DIR` or any hook path resolves.
  A separate issue (#275) owns the state-path defect. `@grade: settled/human`
- `decision:verify-by-fresh-process` — you **cannot** validate a hook-behavior change from inside your own
  worktree; you would be running the main checkout's unchanged code. Validate with a fresh process whose
  `CLAUDE_PROJECT_DIR` genuinely resolves where you intend, or with a plain subprocess for pure-function
  paths. **Never a fixture that hand-injects the value you are trying to prove the harness delivers.**
  `@grade: settled/inherited`
- `decision:extend-dont-duplicate` — #252 already built a working seam for exactly this class of problem
  (`_uncalibrated_advisory` + a sidecar). Prefer extending that seam over inventing a parallel mechanism.
  If you conclude the seam is wrong for the other causes, that is a legitimate finding — say so with
  reasons rather than quietly building beside it. `@grade: guess`
- `decision:no-repair` — your scope is **making non-reading visible**, not fixing the causes. Do not
  attempt to fix ambiguous bindings, wiring gaps, or staleness. Surfacing them is the whole job.
  `@grade: settled/inherited`

## Honest-null clause

A reasoned **no** is a complete deliverable and will be accepted as such — #269's part 2 came back "no"
and was merged. If you conclude some cause cannot be distinguished, or that a candidate shape is
unworkable, say so with the evidence.

An honest null must state **both** boundaries: what you tested and found negative, **and what you did not
search.** The Admiral got this wrong on #263 this week — scoped the tests honestly, then wrote a
conclusion broader than the evidence supported, and had to reopen the issue. Do not repeat it.

## Findings file — note the changed convention

Write working notes to **`notes-265.md` at your worktree root**. Name it `notes-265.md`, **never**
`findings-265.md` — the harness `Write` tool refuses any path whose basename contains "findings".

**New this wave, and required:** before you open your PR, post the substantive content of `notes-265.md`
as a comment on issue #265, then `git rm notes-265.md` in your final commit. Two prior Commanders left
their notes files permanently in `main` (`notes-261.md`, `notes-269.md`) because the old convention had
no removal step — an Admiral template defect, filed as #278, not a Commander failure. This closes it
without waiting on the convention decision. The notes stay durable and addressable on the issue; the
repo tree stays clean.

## Stop conditions — float to the Admiral, do not decide

- Any threshold value, staleness bound, or numeric constant that gates behavior.
- Anything that would write to `~/.claude/settings.json`, or change installer wiring (that is #262, owned
  by another Commander).
- Any change that would make a hook path block, refuse, or exit non-zero.
- Discovering that the #252 seam must be substantially reworked rather than extended.

## Inherited latitude

You hold the epic's latitude contract as refreshed by the human on 2026-07-28: decide freely **within**
this issue's scope; escalate anything touching thresholds or `~/.claude/settings.json`. Issue filing,
commenting and closing are **pre-cleared** — `gh issue create`, `gh issue comment`, `gh issue close`.
File spinoff defects rather than banking them in your worktree; a finding that dies with your worktree
did not happen.

Drive your own spine end to end and **release your engine lease as your final action.** Stage your
closeout trio at `.agent-work/staged-feedback/governor-265/` on your PR branch — the main checkout is
write-fenced to you.

**Lessons-delta gotcha, hit live this week (#277):** the playbook renders ids as `lesson:foo`, but the
delta validator **rejects the colon** and the delta is all-or-nothing. Write ids **bare** —
`verify-harness-field-and-drive-real-writer`, not `lesson:verify-harness-field-and-drive-real-writer`.

## Workspace

**Worktree:** `C:/Programs/constellation-skills-wt/governor-265`
**Branch:** `governor/265-make-non-reading-visible`
**Base commit:** `e3f6a5c` (current `origin/main`, verified fresh at dispatch 2026-07-28)
**Main checkout is read-only to you.** `C:/Programs/constellation-skills` — read it for evidence
(`binding-BEFORE-repair.json`, `.claude/settings.local.json`, the live `.spine-rail-binding.json`), never
write it.

**Isolation is git-only — hook code is not fenced by it.** Verify your worktree with
`py scripts/verify_worktree_isolation.py --here <your worktree>`, and understand that a pass proves git
topology only. See the `## Workspace` section of `skills/admiral/templates/LAUNCH_ORDER.template.md` at
your base commit — the #269 doctrine landed there and applies to you directly.
