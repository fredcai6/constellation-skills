# LAUNCH ORDER — issue #264 (governor: no end-to-end assertion that a live run produces a sane reading)

> Epic #267, wave 2, batch 2. You are Commander `governor-264`. You own this issue end to end.
> Workspace fields were completed by the Admiral at dispatch.

## Mission

**Make a wrong-but-well-formed gauge reading fail a test instead of surviving for eight days.**

Every `gauge.json` on disk predating the fix reads `fill_fraction: 1.0` — all of them, across every work
area in the repo — saturated by the clamp in `compute_record()` against the old 200K default denominator.
#252's bug was a 5x over-read that tripped HARD at roughly 14% of the real window. It ran through the
entire epic-226 and was caught by **a human noticing the number looked wrong.**

Eight days of `1.0` readings raised nothing, because nothing was looking.

Unit tests pin the tables and the parse. They **cannot** catch a wrong denominator, because a wrong
denominator produces a perfectly well-formed record. That is the gap.

## Task

1. **An end-to-end assertion that a live run produces a sane record across the whole chain:**
   writer → `gauge.json` → reader → `thresholds_for` → Trip.
2. **A plausibility check that would have caught the #252 class specifically.** A reading pinned at
   exactly `1.0`, or a run whose every sample saturates, is a defect signal rather than a measurement —
   real context fill does not sit at the clamp. Likewise, a run that produces **zero** records is
   currently indistinguishable from a run with nothing to report.

Note the shape of (2): you are asserting on the *distribution and liveness* of readings, not on their
values. Keep that distinction sharp — it is what lets you build this without touching a threshold.

## What has changed under this issue since it was filed — read before designing

**There is now real post-fix data, which the issue says did not exist.** The issue's claim "there is not
one post-fix reading anywhere in the fleet" was true when filed and is **no longer true.** The Admiral's
own live gauge has been producing correct records all epic, e.g.

```
{"schema_version": 1, "fill_fraction": 0.060006, "model": "claude-opus-5", "observed_at": "2026-07-28T04:32:25.509Z"}
```

at `.agent-work/epic-267/gauge.json` in the main checkout, and readings across the epic ranged roughly
`0.06`–`0.16`, moving live, responding to a compaction. **Use it as ground truth for what sane looks
like** — and note that this is exactly one session on one model, which is a narrow base for a
plausibility rule. Say so if it constrains what you can assert.

**#265 (`b69e6c8`) shipped a sidecar you should probably assert on.** It extended the #252
`_uncalibrated_advisory` seam to two more silence causes the hook can positively localize — ambiguous
session→spine binding (2+ candidate spines) and no usable transcript record — via a `gauge-skip.json`
sidecar family, fanned out to every candidate on ambiguous binding, cleared on any successful write.
This is directly load-bearing for your "zero records" case: **a skip sidecar is the difference between
"nothing to report" and "something prevented reporting."** An end-to-end assertion that ignores the
sidecar is asserting on half the chain.

**#271 is your best real-world test case.** The Admiral's gauge froze at `0.121553` and stayed frozen for
26 minutes across a PR review, a merge, a sweep, a harvest and four issue filings, with wiring fully
intact. Cause: two spines under one session id, one of them a phantom pointing at a path that does not
exist. Removing the phantom and re-driving the same hook with the same payload restored it
(`0.121553` stale 26 min → `0.102681` live). Pre-repair state is preserved at
`.agent-work/harvest-267/governor-269/binding-BEFORE-repair.json` in the main checkout — **a real
captured failure state you can build a fixture from.**

Two properties from that incident, offered as observations rather than requirements:

- **Staleness is not conservative.** One instance failed stale-*low*: displayed `0.126658` while true fill
  was `0.134497` against a `0.15` cap — under-reporting pressure while closing on it. Do not build
  anything that assumes silence or staleness errs safe.
- **The blind window is the dangerous one.** It failed at the moment the gauge mattered most. An
  assertion that only runs at session start would not have caught it.

## Prior-wave verdicts — pasted, load-bearing

**#261 / #202 (wave 1, `2c169a5`).** Binding is two-level: `binding[session_id][abs_spine_path]`. Binding
happens on resume, not only on `claim`. The old flat shape is detected and filtered, failing open. This is
why two spines under one session id is now *representable* — wave 1 fixed the clobber, so the ambiguity
now persists instead of being silently overwritten.

**#269 (wave 2, `e3f6a5c`).** Git worktree isolation is **not** hook-code isolation. `CLAUDE_PROJECT_DIR`
is fixed at session launch, inherited unchanged by every subagent, and is **empirically unreadable from an
ordinary tool subprocess** — probed live in both Bash and PowerShell, both empty; the harness injects it
only when constructing a hook subprocess. **This constrains your test design directly** — see
`decision:verify-by-fresh-process`.

**Also from #269:** `gauge_writer_hook.py` is wired **only** via `.claude/settings.local.json`, which is
gitignored and exists only in the main checkout. **You, in a worktree, have no gauge writer running at
all.** Do not interpret your own absent gauge as evidence about your change, and do not build a test that
silently depends on the ambient wiring being present.

**#268 (wave 2, `d6d25a6`).** A template pointed at a path that existed in a developer's head but not in a
fresh install. Same class as the gap you are closing, different surface.

## Pre-rulings — decided, do not re-open

- `decision:no-threshold-values` — **do not introduce, tune, or hardcode any threshold value, including in
  test fixtures.** Any threshold number always surfaces to the human and is never delegated. **This is the
  sharpest constraint on your issue**, because a plausibility check is one careless step from being a
  threshold. Asserting "not exactly 1.0" or "not all samples identical" is a *structural* check and is
  fine. Asserting "fill should be under X" is a threshold — stop and float it. Staleness bounds are
  thresholds too. `@grade: settled/human`
- `decision:fail-open-is-inviolable` — every hook path exits 0 and never blocks a turn. A test that
  requires a hook to fail loudly is testing the wrong contract. `@grade: settled/inherited`
- `decision:verify-by-fresh-process` — you **cannot** validate hook behaviour from inside your own
  worktree; you would be running the main checkout's unchanged code. Validate with a fresh process whose
  `CLAUDE_PROJECT_DIR` genuinely resolves where you intend, or with a plain subprocess for pure-function
  paths. **Never a fixture that hand-injects the value you are trying to prove the harness delivers** —
  that is precisely the failure this issue exists to prevent, reappearing one level up. This lesson has
  been confirmed five times in this fleet. `@grade: settled/inherited`
- `decision:no-schema-change` — the gauge record schema is frozen by the latitude contract: exactly
  `schema_version`, `fill_fraction`, `model`, `observed_at`. No `source` field, no additions. Assert
  against it; do not extend it. `@grade: settled/human`
- `decision:assert-dont-repair` — your scope is **detecting** an insane reading, not fixing its causes.
  Do not fix bindings, wiring, or staleness. `@grade: settled/inherited`

## Honest-null clause

A reasoned **no** is a complete deliverable and will be accepted as such — #269's part 2 came back "no"
and was merged unchanged. If you conclude that some part of the chain cannot be asserted end to end
without a threshold, or without wiring you do not have, **say so with evidence rather than approximating
it with a unit test wearing an end-to-end name.** That specific substitution is the failure mode this
issue is about; committing it here would be ironic and would not be merged.

An honest null must state **both** boundaries: what you tested and found negative, **and what you did not
search.** The Admiral got this wrong on #263 this week — scoped the tests honestly, then wrote a
conclusion broader than the evidence supported, and had to reopen the issue.

## Artifacts — which are for the repo, which are for the harvest

This distinction cost round-trips twice in this wave. It is now explicit.

**For the repo (committed, reviewed, merged):** your code, tests and docs. Nothing else.

**For the harvest (staged in your worktree, left UNCOMMITTED):** your closeout trio at
`.agent-work/staged-feedback/governor-264/`. **Do not `git add` it. Do not commit it.** I harvest it
directly from your worktree before the sweep. A prior Commander force-added its trio past `.gitignore`
because I wrote "on your PR branch" — that wording was mine and it was wrong; this is the correction.

**Working notes:** write them to **`notes-264.md` at your worktree root** — name it `notes-264.md`,
**never** `findings-264.md`, because the harness `Write` tool refuses any path whose basename contains
"findings". Before you open your PR, post the substantive content as a comment on issue #264, then
`git rm notes-264.md` in your final commit. Two earlier Commanders left their notes permanently in `main`
(#278); this closes it.

**Lessons-delta gotcha (#277):** the playbook renders ids as `lesson:foo`, but the delta validator
**rejects the colon** and the delta is all-or-nothing. Write ids **bare** —
`verify-harness-field-and-drive-real-writer`, not `lesson:verify-harness-field-and-drive-real-writer`.

## Stop conditions — float to the Admiral, do not decide

- Any threshold value, staleness bound, or numeric constant that gates behaviour. Re-read
  `decision:no-threshold-values` — your issue is the one most likely to trip it by accident.
- Anything that would write to `~/.claude/settings.json`, or change installer wiring — that is **#262**,
  owned by a concurrent Commander.
- Any change to the frozen gauge record schema.
- Any change that would make a hook path block, refuse, or exit non-zero.
- Concluding that a genuine end-to-end assertion is impossible in CI without the wiring #262 is building.
  That is a legitimate and useful finding — bring it early rather than at the end, because it changes how
  the two batch-2 issues relate.

## A note on your dependency with #262

`governor-262` is running concurrently on the same base commit, building the installable wiring. There is
a plausible world in which your end-to-end test can only run once that wiring exists. **Do not block on
it and do not coordinate directly.** Build what you can assert today, and if you hit a hard dependency,
float it to me with the specific thing you need — I will sequence it. Two Commanders negotiating a shared
design between themselves is exactly what the one-Commander-per-issue rule exists to prevent.

## Inherited latitude

You hold the epic's latitude contract as refreshed by the human on 2026-07-28: decide freely **within**
this issue's scope; escalate anything touching thresholds or `~/.claude/settings.json`.

Issue filing, commenting and closing are **pre-cleared** — `gh issue create`, `gh issue comment`,
`gh issue close`. File spinoff defects rather than banking them in your worktree; a finding that dies
with your worktree did not happen.

Drive your own spine end to end and **release your engine lease as your final action.**

## Workspace

**Worktree:** `C:/Programs/constellation-skills-wt/governor-264`
**Branch:** `governor/264-e2e-assertion`
**Base commit:** `b69e6c8` (current `origin/main`, verified fresh at dispatch 2026-07-28)
**Main checkout is read-only to you.** `C:/Programs/constellation-skills` — read it for evidence: the
live `.agent-work/epic-267/gauge.json` (a real post-fix record), `.spine-rail-binding.json`,
`.claude/settings.local.json` (the only working wiring in existence), and
`.agent-work/harvest-267/governor-269/binding-BEFORE-repair.json` (a captured real failure state).
Never write it.

**Isolation is git-only — hook code is not fenced by it.** Verify your worktree with
`py scripts/verify_worktree_isolation.py --here <your worktree>`, and understand that a pass proves git
topology only. See the `## Workspace` section of `skills/admiral/templates/LAUNCH_ORDER.template.md` at
your base commit — the #269 doctrine landed there and applies to you directly.
