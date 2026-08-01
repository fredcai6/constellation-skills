# LAUNCH ORDER — issue #262 (install: ship and opt-in-wire the hook rail)

> Epic #267, wave 2, batch 2. You are Commander `governor-262`. You own this issue end to end.
> Workspace fields were completed by the Admiral at dispatch.

## Mission

**Make the Context Governor installable — and therefore capable of ever running — in a consuming project.**

`scripts/install_constellation.py` contains no reference to hooks or to `settings.json` at all. Neither
`scripts/hooks/gauge_writer_hook.py` nor `scripts/hooks/spine_rail.py` exists anywhere under
`~/.claude/skills/`. #256 fixed the **read** side by bundling `gauge_reader.py`; the **write** side was
never bundled and its wiring was never installable.

So an install receives the reader, `thresholds_for`, `_read_gauge`, `_uncalibrated_advisory` and both
Trip bands — every one of which fail-safes to silence on an absent gauge — and **nothing that ever
writes one.** The Governor is inert by construction in every consuming project.

Evidence on file (2026-07-27): all six dogfood project roots searched for `gauge*.json`. Every hit is
inside `constellation-skills`. **f1Brainz, baseball_coaster, network_elo, story_time and tennis_elo have
never had a gauge file written, ever.** The only working wiring on this machine is
`constellation-skills/.claude/settings.local.json` — gitignored, one machine, one repo.
`~/.claude/settings.json` has no `hooks` key at all.

This is the load-bearing issue of the epic. Everything else the epic fixed — binding, visibility,
worktree doctrine — improves a mechanism that, outside this one repo, has never executed.

## Scope

- Bundle both hook scripts (`gauge_writer_hook.py`, `spine_rail.py`) into the install.
- Add an opt-in `--wire-hooks` flag that adds the PostToolUse entries **additively** — it must not
  clobber or nest inside existing matchers. `docs/GAUGE_WRITER_HOOK.md` has the exact snippet and the
  ordering note.
- Without the flag: **detect and report** unwired hooks. Silence is what let this survive.
- Resolve the path question below.

## The one real design question — and it now has a settled answer to build on

The documented snippet uses `${CLAUDE_PROJECT_DIR}/scripts/hooks/...`, which only resolves inside the
constellation-skills checkout. An installed wiring needs a path that resolves for a **consuming**
project. The issue calls this "a real design question, not a find-and-replace," and it is.

**What changed since the issue was filed — read this before designing.**

#269 established that `CLAUDE_PROJECT_DIR` is fixed at session launch and inherited unchanged by every
subagent; git worktree isolation is **not** hook-code isolation. It also established that
`CLAUDE_PROJECT_DIR` is **empirically unreadable from an ordinary tool subprocess** — probed live in both
Bash and PowerShell, both empty. The harness injects it only when constructing a hook subprocess. Do not
design anything that depends on reading it outside a hook.

**RULING (Fred, 2026-07-28) — #269 part 3: hook code pins to the main checkout.** The anti-tamper
property is now doctrine: *an agent's own branch cannot edit the code that judges it.*
`decision:no-resolution-change` — which fenced the two prior Commanders — **is lifted for you and only
for you.** You are the first Commander in this epic permitted to change how a hook path resolves, and
you are permitted it because the human answered the question the fence was protecting.

**My derived reading, handed to you as a `guess` and not a ruling.** The principle is "hook code resolves
to a root the measured agent does not control." Inside this repo that root is the main checkout. In a
consuming project the hook code is not in the project at all — it lives in the install tree. That
suggests the installed wiring should point at the **installed** script rather than at
`${CLAUDE_PROJECT_DIR}/scripts/hooks/...`. **You may reach a different conclusion with reasons; I would
rather be corrected than obeyed here.** What you may not do is pick a form without engaging the
anti-tamper principle, because that principle is what Fred actually ruled on. `@grade: guess/derived`

Note the asymmetry you must handle: the **hook code** location and the **state** location are different
questions. A consuming project's gauge must be written into *that project's* work area, while the code
that writes it may live in the install tree. #275 owns the state-path defect and is **not yours** — but
do not accidentally decide it. If your path form forces a state-path change, that is a stop condition.

## Design-it-twice — required by the latitude contract, not optional here

The human's refreshed contract names **#262 specifically** as the issue that gets a design-it-twice
panel. Read `skills/_shared/design-it-twice-brief.md` and run it properly:

- The **one thing** designed twice is the **installed hook-path form** — the single load-bearing decision
  above. Not "the installer." One brief, one decision.
- **Count is yours to choose and to defend.** The brief says "when in doubt, panel." This touches
  architecture and every future install, which argues panel (3+); you own the call and must record the
  rationale in the panel-vs-single record where it can be overturned.
- **Convergence is human-only.** You generate and compare; you hand back **a defended recommendation,
  never a menu**. Handing back a menu is a failed run. Float that recommendation to me before you build
  on it — see stop conditions.
- Record every **untaken road** loudly. A silent skip is a failed run too.

## The overload escape hatch — read this, it is new and it is deliberate

Every Commander in this epic has finished past the HARD context band, one at 2.4x it, and **none of them
could see it happening** (#284). You are running the largest issue in the epic and you cannot measure
your own fill — the gauge writer is wired only via `.claude/settings.local.json`, which is gitignored and
exists only in the main checkout, so **you have no gauge writer running at all.** Do not interpret your
own absent gauge as evidence about your change.

**So: the panel recommendation alone is a complete, acceptable deliverable.** If you judge that panel plus
full implementation will run you long, stop after the recommendation, write it up, and say plainly that
implementation should go to a successor with a fresh window. That is not a failure and will not be treated
as one — it is the honest-null clause applied to your own capacity. What I do not want is a rushed
implementation of a well-chosen design.

## Pre-rulings — decided, do not re-open

- `decision:opt-in-wiring-only` — **the installer must never silently rewrite a user's `settings.json`.**
  Without `--wire-hooks` it detects and reports; it does not write. This is Fred's, taken 2026-07-27, and
  it is the reason this issue exists in the shape it does. `@grade: settled/human`
- `decision:fail-open-is-inviolable` — every hook path exits 0 and never blocks a turn. An installer that
  wires a hook which can block is a defect. `@grade: settled/inherited`
- `decision:no-threshold-values` — **do not introduce, tune, or hardcode any threshold value, including in
  test fixtures.** Any threshold number always surfaces to the human and is never delegated. Staleness
  bounds count. If your design needs one, stop and float it. `@grade: settled/human`
- `decision:additive-not-clobbering` — the wiring must add PostToolUse entries alongside whatever the user
  already has. It must not clobber, nest inside an existing matcher, or reorder unrelated entries.
  `@grade: settled/inherited`
- `decision:verify-by-fresh-process` — you **cannot** validate hook behaviour from inside your own
  worktree; you would be running the main checkout's unchanged code. Validate with a fresh process whose
  `CLAUDE_PROJECT_DIR` genuinely resolves where you intend, or with a plain subprocess for pure-function
  paths. **Never a fixture that hand-injects the value you are trying to prove the harness delivers.**
  This lesson has now been confirmed five times in this fleet; you are not the first to be tempted.
  `@grade: settled/inherited`
- `decision:275-is-not-yours` — the state-path defect belongs to #275. Do not fix it. `@grade: settled`

## Prior-wave verdicts — pasted, load-bearing

**#261 / #202 (wave 1, `2c169a5`).** Session→spine binding is two-level:
`binding[session_id][abs_spine_path]`. Binding happens on resume, not only on `claim`. The old flat shape
is detected and filtered, failing open.

**#269 (wave 2, `e3f6a5c`).** Worktree isolation is not hook-code isolation; `CLAUDE_PROJECT_DIR` is fixed
at session launch. Detection of hook resolution came back a reasoned **NO** and was merged as such.
Part 3 ruled 2026-07-28 as above.

**#268 (wave 2, `d6d25a6`).** `ADMIRAL_SPINE.template.json` pointed the state-note precondition at
`.agent-work/templates/STATE_NOTE.template.md`, a project-overlay path that exists neither in this repo
nor in a fresh install. Fixed to the bundled-fallback wording.
**Directly relevant to you: that defect is the same class as yours** — a path that resolves in a
developer's head but not in a fresh install. Assume more of them exist in what you touch.

**#265 (wave 2, `b69e6c8`).** Extended the #252 `_uncalibrated_advisory` seam to two more silence causes
the hook can positively localize — ambiguous binding (2+ candidate spines) and no usable transcript
record — via a new `gauge-skip.json` sidecar family, fanned out to every candidate on ambiguous binding,
cleared on any successful write. **Relevant to you:** "hook not wired at all" is still an *uncovered*
cause, because a hook that never runs cannot write a sidecar explaining that it never ran. That gap is
yours: the detect-and-report path is the only thing that can ever surface it.

## Honest-null clause

A reasoned **no** is a complete deliverable and will be accepted as such — #269's part 2 came back "no"
and was merged unchanged.

An honest null must state **both** boundaries: what you tested and found negative, **and what you did not
search.** The Admiral got this wrong on #263 this week — scoped the tests honestly, then wrote a
conclusion broader than the evidence supported, and had to reopen the issue. State your search boundary,
not just your test boundary.

## Artifacts — which are for the repo, which are for the harvest

This distinction cost round-trips twice in this wave. It is now explicit.

**For the repo (committed, reviewed, merged):** your code, tests and docs. Nothing else.

**For the harvest (staged in your worktree, left UNCOMMITTED):** your closeout trio at
`.agent-work/staged-feedback/governor-262/`. **Do not `git add` it. Do not commit it.** I harvest it
directly from your worktree before the sweep. A prior Commander force-added its trio past `.gitignore`
because I wrote "on your PR branch" — that wording was mine and it was wrong; this is the correction.

**Working notes:** write them to **`notes-262.md` at your worktree root** — name it `notes-262.md`,
**never** `findings-262.md`, because the harness `Write` tool refuses any path whose basename contains
"findings". Before you open your PR, post the substantive content as a comment on issue #262, then
`git rm notes-262.md` in your final commit. Two earlier Commanders left their notes permanently in `main`
(#278); this closes it. The notes stay durable and addressable on the issue; the tree stays clean.

**Lessons-delta gotcha (#277):** the playbook renders ids as `lesson:foo`, but the delta validator
**rejects the colon** and the delta is all-or-nothing. Write ids **bare** —
`verify-harness-field-and-drive-real-writer`, not `lesson:verify-harness-field-and-drive-real-writer`.

## Stop conditions — float to the Admiral, do not decide

- Any threshold value, staleness bound, or numeric constant that gates behaviour.
- **Your design-it-twice recommendation, before you implement it.** Float it with a one-paragraph
  summary; I judge whether it needs Fred and will not sit on it.
- Any wiring shape that would write `~/.claude/settings.json` in a way not covered by the opt-in ruling —
  including "helpfully" creating the file, or writing on a dry run.
- Anything that forces a change to state-path resolution (#275's territory).
- Any change that would make a hook path block, refuse, or exit non-zero.
- Concluding that the installer cannot wire hooks safely at all. That is a legitimate finding, not a
  failure — bring it with evidence.

## Inherited latitude

You hold the epic's latitude contract as refreshed by the human on 2026-07-28: decide freely **within**
this issue's scope; escalate anything touching thresholds or `~/.claude/settings.json` — and note that
this issue touches `settings.json` by design, so read the opt-in pre-ruling as the boundary of what is
already decided rather than as an invitation to decide more.

Issue filing, commenting and closing are **pre-cleared** — `gh issue create`, `gh issue comment`,
`gh issue close`. File spinoff defects rather than banking them in your worktree; a finding that dies
with your worktree did not happen.

Drive your own spine end to end and **release your engine lease as your final action.**

## Workspace

**Worktree:** `C:/Programs/constellation-skills-wt/governor-262`
**Branch:** `governor/262-install-wire-hooks`
**Base commit:** `b69e6c8` (current `origin/main`, verified fresh at dispatch 2026-07-28)
**Main checkout is read-only to you.** `C:/Programs/constellation-skills` — read it for evidence
(`.claude/settings.local.json` is the only working wiring in existence and is your best reference; also
the live `.spine-rail-binding.json` and `.agent-work/epic-267/gauge.json` for a real post-fix record).
Never write it.

**Isolation is git-only — hook code is not fenced by it.** Verify your worktree with
`py scripts/verify_worktree_isolation.py --here <your worktree>`, and understand that a pass proves git
topology only. See the `## Workspace` section of `skills/admiral/templates/LAUNCH_ORDER.template.md` at
your base commit — the #269 doctrine landed there and applies to you directly.

**A concurrent Commander (`governor-264`) is running in a separate worktree on the same base.** It owns
the end-to-end assertion. If you need something from it, or find yourselves converging on the same file,
float to me — do not coordinate directly and do not enter its worktree.
