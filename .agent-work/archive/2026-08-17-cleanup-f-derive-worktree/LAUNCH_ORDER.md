# Launch Order: `cleanup-f-derive-worktree — #609 (absorbing #315)`

> Write per `constellation-how-to-talk` — clear, concise, grounded.

Commanders start cold. Everything you need is pasted below. This is a
**subtractive** change to engine identity, and the failure mode of getting it
subtly wrong is silent — read the whole order before the first edit.

## Mission

**A spine's worktree is derived from its path. Nothing stamps it, nothing
compares it, nothing reads an ambient cwd to find it.**

The layout is a convention, ruled by the human 2026-08-16:

```
<project>/.worktrees/<work-id>/.agent-work/<sub-work-id>/spine.json   # a spine that has a tree
<project>/.agent-work/<sub-work-id>/spine.json                        # a spine at the root
```

Derivation is lexical: **walk up to the nearest `.agent-work` ancestor and take
its parent.** That is the worktree. No git call, no cwd read, no stored value —
so there is no second source of truth that could disagree with the first.

### Why this is worth doing

Today two values must agree: a **stamp** (`origin.worktree`, written at birth) and
an **ambient reading** (`git rev-parse --show-toplevel` from the engine's cwd,
taken fresh on every guarded verb). That shape has been repaired twice in three
days — #577 added it, #585 silently weakened it by nesting worktrees inside the
primary checkout, #588 repaired it with equality — and it still blocks #315.

And it does not deliver what it costs. From `origin_worktree_refusal`'s own
docstring, which you should read before changing it:

> It does NOT make the comparison unforgeable. The engine reads its ambient cwd,
> so a check command authored as `cd <origin.worktree> && ...` still satisfies it.

A subprocess per guarded verb, for a forgeable comparison, that has needed two
structural repairs and blocks a third fix.

### What ships

1. **One derivation function**, pure and lexical, arbitrary depth, nearest
   `.agent-work` ancestor. No `.agent-work` ancestor at all means **unowned**.
2. **`origin_worktree_refusal` stops comparing.** What remains is a shape question
   — does this path place the spine? — answered without git and without cwd.
3. **The per-guarded-verb `git rev-parse --show-toplevel` in `main()` goes away.**
4. **#315, absorbed:** `_check_condition` (`checklist_engine.py:898`) already has
   `base_dir` in scope and does not pass it to `_run_check_command` (`:927`),
   which calls `subprocess.run` with no `cwd=`. Command-kind checks run in the
   **derived worktree**. That is the whole of #315 once the trap below is gone.
5. **`_foreign_worktree` stops being an ownership test** (see the second ruling).

### The trap that used to block #315, and why it is gone

`verify_worktree_isolation.py --here` compares `git rev-parse --show-toplevel`
from the **ambient cwd** against an expected path. Forcing cwd makes that
comparison `EXPECTED == EXPECTED` — always true — which is why PR #576 refused the
naive fix and landed `IsolationGateSurvivesThroughTheCLI` to catch anyone applying
it.

**That check no longer ships in any spine.** It used to sit on the Commander
spine's `init` precondition `c0` and was removed when the engine-native guard
landed. Verified 2026-08-16: zero occurrences of `verify_worktree_isolation` in
any template or spec. So threading `cwd` no longer disarms anything that ships.

**You do not touch `scripts/verify_worktree_isolation.py`.** Retiring `--here` as
a launch-order step is #610's, not yours. Its *gate mode* — the Admiral's pre-wave
check that provisioned paths are real, registered and distinct — stays either way.
`IsolationGateSurvivesThroughTheCLI` must still pass; if your change makes it fail,
stop and float, because that test is the tripwire for exactly this class of error.

## Prior-Wave Verdicts (pasted)

From #609's refinement, ruled by the human this morning, and the reason this lane
is not simply "add cwd=":

> Spines are 1:1 with **work areas**, not with worktrees. A Commander gets a
> worktree; an implementer usually does not — it works in its Commander's tree, in
> its own area. So one worktree holds several spines.
>
> Therefore **the worktree cannot answer "is this mine".** Any check shaped as
> *same worktree, therefore mine* is broken by construction the moment a crew
> shares its Commander's tree. `_foreign_worktree` (`spine_rail.py:639`) is
> exactly that check: for an in-tree implementer it reports "not foreign", and the
> parent's Stop is answered with its crew's gate. That is the #549 bug class, and
> #549 fixed it with binding-key provenance, not with worktree.

From the same ruling, on why the obvious hardening is wrong:

> 27 tracked paths carry two `.agent-work` segments, of the shape
> `.../harvest/ref-honest-run-1/workspace/.agent-work/...`. That inner
> `.agent-work` belongs to a nested sandbox project whose root is `workspace/`.
> Taking the **outermost** segment would derive the real repo as the root of a
> spine that belongs to the sandbox. **Nearest is correct.** The doubled-by-bug
> case (`.agent-work/.agent-work/`) is prevented at creation by #258's refusal.

Arbitrary depth is real: `.agent-work/archive/2026-07-10-epic-101/harvest/issue-102/full/issue-102/spine.json`.
`_worktree_from_spine`'s current fixed `.agent-work/<id>/<name>.json` match is too
narrow and returns `None` for that.

## Pre-Rulings

- `decision:derivation-authoritative-stamp-becomes-provenance` — derivation is
  authoritative **immediately**. `origin.worktree` keeps being **written** as
  provenance, and **nothing reads it for a decision**. Pin that with a test. This
  needs no migration and reverses cleanly if we are wrong.
  `@grade: settled/human · leans g1-implement`
- `decision:worktree-is-location-spine-path-is-identity` — the derived worktree is
  used for **location** (cwd for checks, where git runs) and never for
  **ownership**. Ownership is the **lease**, and among spines sharing a tree the
  discriminator is binding-key provenance (#549), never the tree.
  `@grade: settled/human · leans all gates`
- `decision:nearest-ancestor-fail-closed` — nearest `.agent-work` ancestor, take
  its parent; arbitrary depth. **No `.agent-work` ancestor means unowned**: refuse
  the guarded verb rather than guessing a root, matching what
  `_worktree_from_spine` already does by returning `None`.
  `@grade: settled/human · leans g1-implement`
- `decision:normalize-once` — normalize at the derivation boundary only (realpath
  plus normcase), reusing `verify_worktree_isolation.normalize_path`'s definition
  rather than minting a second one. Do not normalize at call sites.
  `@grade: settled/measured · leans g1-implement`
- `decision:one-definition-or-a-pinned-equivalence` — **where** the function lives
  is yours to decide, under a hard constraint. `scripts/hooks/spine_rail.py`
  imports **stdlib only**, deliberately, because a hook that fails takes the turn
  with it. Giving it a cross-module import means a `SCRIPT_RUNTIME_COMPANIONS`
  entry in `scripts/install_constellation.py` — **which lane A owns and you may
  not touch**. So either place the definition where every consumer already reaches
  it without a new companion, or keep spine_rail's own copy and pin the two
  implementations equal with a shared table of cases in a test. Duplication without
  that test is not acceptable: the `gauge_reader`/`owner_key` note in the
  installer records what drift costs.
  `@grade: guess · leans g1-implement · settle: try the single-definition placement first and report what it would require; float rather than editing install_constellation.py`
- `decision:not-a-weaker-guard` — removing the origin comparison does not remove a
  guard. The **lease** is and always was the ownership guard; the worktree
  comparison was a location check wearing an ownership costume. If you find a case
  where the comparison was genuinely the only thing preventing harm, that is a
  finding — stop and float rather than shipping around it.
  `@grade: settled/human · leans g1-implement`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable.
If derivation turns out to be unsafe for a case this order did not anticipate,
that finding — measured, with the case — is the deliverable. Say so and stop.

## Inherited Latitude

**You may decide:** where the derivation function lives (under the ruling above),
the refusal wording, how `origin_worktree_refusal`'s remaining shape check is
expressed, test structure, and the order of the two halves.

**You must float to the Admiral:** anything that requires editing
`scripts/install_constellation.py` or any template; anything that makes
`IsolationGateSurvivesThroughTheCLI` fail; any case where removing the comparison
would genuinely permit something harmful; publication.

## File Ownership

Your working-notes file is `notes-f.md`, sole writer this wave.

> Name it `notes-<n>.md`, **never** `findings-<n>.md` — the harness `Write` tool
> refuses any path whose basename contains "findings".

**Files you own:** `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
`scripts/spine_lifecycle.py`, and their tests (`tests/test_checklist_engine.py`,
`tests/test_spine_rail.py`, `tests/test_spine_lifecycle.py`,
`tests/test_worktree_precondition_wiring.py`, `tests/test_spine_origin_isolation.py`),
plus any new test file.

**Fenced — two lanes are live right now:**

- Lane A (door): `scripts/mcp_spine_server.py`, `.mcp.json`, `examples/**`,
  `scripts/install_constellation.py`, `skills/commander/templates/**`.
- Lane E (crew tooling): `scripts/run_crew.py`, `scripts/recover_crews.py`,
  `tests/test_crew_launcher.py`.

`run_crew.py` also computes worktree paths, and deriving `--worktree` from
`--spine` there is a real cleanup — **it is not yours this wave.** It follows once
lane E lands. Do not touch it and do not design around touching it.

Also not yours: `scripts/verify_worktree_isolation.py` (see the Mission).

## Workspace

`/home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`,
branch `cleanup/f-derive-worktree`, base commit `e36e630b`, created with:

```
git worktree add .worktrees/cleanup-f-derive-worktree -b cleanup/f-derive-worktree e36e630b
```

`main` verified fresh at dispatch: `e36e630b`, clean tree, suite **3103 passed / 7
skipped / 0 failed**. Re-measure at gate time regardless — two lanes are live and
may land under you.

First step, before any git operation: **`cd` into that worktree**, then run `py
/home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py
--here /home/tommy/projects/constellation-skills/.worktrees/cleanup-f-derive-worktree`
— must exit 0, pasted into your report. Yes, this is the mechanism you are
retiring; it is still how this fleet dispatches until #610 lands, and using it
once is not an endorsement of keeping it.

**Isolation is git-only — hook code is not fenced by it.** This is the
load-bearing paragraph for you: `spine_rail.py` **is** the hook, and it fires on
your own turns. `CLAUDE_PROJECT_DIR` resolves once at session launch and is
inherited unchanged by every subagent, so your worktree still runs the **main
checkout's** hook against the **main checkout's** state (#269). You cannot
validate this from inside the session that contains it. Use a fresh process whose
`CLAUDE_PROJECT_DIR` genuinely resolves to your worktree, or call the functions
directly with constructed payloads and a constructed binding store.

## Inherited Context

- **Platform:** Linux, Python 3.12 as `py`. Suite:
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`.
- **Clear `__pycache__` before every measurement.** As of `43c577d4` a cache built
  in another tree fails a named test (`tests/test_bytecode_cache_provenance.py`)
  rather than surfacing as an unrelated assertion — if you see it, clear and
  re-measure instead of investigating whatever it landed on.
- **Merge gate:** local Linux green, independent APPROVE, failure-set difference
  against a `main` baseline re-measured at gate time.
- **CI is one `windows-latest` job**, red at baseline. Local Linux is the only real
  signal. Path handling is exactly where Windows differs — say what you did about
  it even though CI cannot tell you.
- **Drive your spine through the engine CLI** with an explicit `--session-id`. The
  operator-side door binding is still broken; that is lane A's mission (#603).
- **Relaunch works:** re-claiming your own lease re-stamps `claimed_at` (#601) and
  a reading is owner-keyed (#600), so a fresh leg gets its own number. Never
  `--force` for a routine relaunch. Handing off at a clean gate boundary when your
  context is spent is correct and is how three lanes have finished today.
- **`map/INDEX.md`** is generated and freshness-tested; rebuild and commit if
  entities change. It conflicts on every parallel branch (#544) — resolve by
  regenerating, never by hand-merging.

## Pre-empted Steps

- **Context is established by this order**, including the measurements quoted
  above (taken 2026-08-16 against `e36e630b`).
- **The worktree is provisioned and gate-verified.**
- **Triage and design are done.** #609 carries the rule, the retirement list, the
  two known limits and the migration question. Implement; do not re-derive the
  design.

## Data Locations

- The rule and its refinement: issue **#609** (read the whole body, including the
  refinement section appended 2026-08-16).
- The provisioning half, which closes derivation's one limit: issue **#610**. It
  is **not** yours — do not implement any part of it.
- `_worktree_from_spine`, the lexical derivation that already exists and is
  already right in shape: `scripts/hooks/spine_rail.py:712`.
- The 2026-08-15 worktree-identity ruling: `.agent-work/rulings/`. #609 supersedes
  it; cite it where your change contradicts it, and say so plainly.

## Budget

- **Model tier (required):** Opus 5. Subtractive change to engine identity, with a
  silent failure mode.
- **Compute/time, session-window:** one working session. Derivation and
  `origin_worktree_refusal` first; #315's `cwd=` thread is small once they land.

## Stop Conditions

Stop and return when scope is exceeded, a decision outside your latitude is
needed, the budget is crossed, evidence is impossible, or you need context this
order does not cover — return-and-query the Admiral. Asking up is always
sanctioned.

**Arriving over the context HARD band is not a stop condition.** It is an absolute
token cap; you can be over it on turn one having done nothing. The engine refuses
only `start` and `reopen`, and only until a refresh-request exists for that gate:
**attach the refresh-request against the current why-record, then `start`, then
work.** Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:` line, as
an instruction to hand off on turn one.

## Return Shape

A verdict — shipped, blocked with a measured reason, or an honest null — plus:

1. **Evidence over behaviour, not text.** For derivation: a table of paths and the
   worktree each derives, covering a spine at the root, a spine in a worktree, a
   crew area nested under a Commander's, the deep archived case named above, the
   nested-sandbox double-`.agent-work` case, and a path with no `.agent-work`
   ancestor at all.
2. **For the retirement:** the guarded-verb path exercised before and after, with
   the `git rev-parse` call gone and the same verbs still refused where they
   should be. `IsolationGateSurvivesThroughTheCLI` green throughout.
3. **For #315:** red-before/green-after showing a command check that used to
   inherit the launcher's cwd now running in the derived worktree — both the
   fail-open decoy case and the false-red case from the original repro.
4. **Where you put the derivation function and why**, plus the equivalence test if
   you kept a second copy.
5. **Full clean-env, cache-cleared suite** at your published head, plus a `main`
   baseline re-measured at gate time.
6. **Map impact**, triage candidates, workflow feedback, and your `--here` output.

Park at `archive`. **Do not merge.** Publication is the Admiral's class — and your
merge is deliberately **held behind lanes A and E**, so that their gates are not
measured against a moving engine. Expect to be parked for a while after you
finish; that is the plan, not a problem with your work.
