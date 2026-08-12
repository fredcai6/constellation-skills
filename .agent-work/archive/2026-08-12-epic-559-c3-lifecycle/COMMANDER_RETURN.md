# Commander return — C3: the work lifecycle is one thing

**Work id:** `epic-559/c3-lifecycle` · **Branch:** `epic-559/c3-lifecycle` · **Base:** `293b7721`
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c3-lifecycle`
**Parent:** `admiral-epic-418-followon` · **Mode:** delegated, no reachable human
**Verdict: all three pieces ship, both carried findings fixed, nothing refuted.**

## The headline

All three pieces the launch order asked for ship with violating fixtures, and both carried findings are
fixed. But the most useful things this run produced were **corrections to the launch order's own
premises**, and one of them changes what the epic should do next.

| | |
|---|---|
| Suite | **2824 → 2932** passed, 3 skipped, 1121 subtests |
| Corpus sweep | **23 → 23** fault lines — no shipped template moved |
| Gates | 5, each implement → review → integrate; **every reviewer verdict APPROVE** (g1 after one BLOCK + rework) |
| Crews | 15, **every one** with `--parent` naming this Commander and an explicit `--model sonnet` |
| Commits | 13 on the branch |

## Three corrections to the order's premises, measured

**1. The chicken-and-egg the order names is not the real one.** The order says the door "reads
`SPINE_FILE` at import time and raises `KeyError` without it," so a tool that creates a spine cannot live
there. Measured: `.mcp.json` binds `SPINE_FILE` with a **shell default**
(`${SPINE_FILE:-examples/mcp-interactive-demo/spine.json}`), so a real dispatch's door always starts.
The actual obstacles are two others — `_identity_violation` refuses any argv resolving `--file` off the
bound spine, and `tests/test_mcp_identity.py`'s choke-point pin AST-restricts every `return` in
`call_tool` to two shapes. That is why `spine_open` is a **module-level sibling** of `call_tool` rather
than a branch inside it, and why it earns its own containment pin instead of inheriting one written for a
pass-through hazard. `call_tool`'s body is provably byte-identical across the change.

**2. `not_yet_written` is worse than described.** The order calls it "a footgun on a field that exists to
make a check *not* run." Measured by driving `compile_spec` directly: a TOML string `"false"` does not
merely read as a declaration — it compiles the check to `None`, so **the gate silently loses its check
entirely**. A field whose author writes the word "false" deletes the check. That is a
check-that-cannot-fail arriving through a spelling mistake, and it is why the fix **refuses** rather than
coerces (deviation, below).

**3. `.agent-work/archive/<work-id>/` is not the shipped convention.** Measured on disk: **38** of 41
archive entries use `<YYYY-MM-DD>-<slug>` flat, one uses an older dash-less date form, one
(`curator-reports/`) is not a work area at all, and **none is nested**. Close follows the shipped
convention (deviation, below).

## What shipped

| gate | what | commit |
|---|---|---|
| g1 | **open** — `scripts/spine_lifecycle.py`: derives branch and worktree from the work id, refuses an occupied path and a work id another `engine_session` holds, provisions, scaffolds, compiles via `generate_spine` as a library, stamps a top-level `origin`, and self-verifies with `check_distinct_real` **in-process** rather than trusting `git`'s exit code. Any failure at or after the worktree add rolls back the worktree **and** the branch, scoped to what the call created. | `d8305d9c` |
| g2 | **close** — `closeout_refusal` (pure) is the whole ordering predicate; `close_work` archives spine-last, stages by name, commits, and reports **"ready to PR."** It never opens a PR, never removes a worktree, never judges the work good. | `d0358a3d` |
| g3 | **the door** — `spine_open`/`spine_close` on the already-registered `spine` server, no `.mcp.json` change. `generate_spine.py` is reachable through MCP; by the standing ruling it was a defect until now. | `386d7635` |
| g4 | **the declared dispatch** — `[[gate.dispatch]]`, three new spec-shape faults, and an injected **`command`**-kind postcondition reading `crew-runs.json`. | `b88f13a4` |
| g5 | **carried findings** — `spec-not-yet-written-not-bool`; `DESIGN_NOTE.md` §4/§7/§10 reconciled with §7 enumerated mechanically from source. | `51feb36c` |

## The Admiral's four questions

**Q1 — the chicken-and-egg.** Answered above. `spine_open` never calls `run_engine` and never references
`SPINE`/`SESSION`; it is dispatched from `call_lifecycle_tool`, routed in `main()`. The pin resolves
`call_tool`'s own `FunctionDef` and walks only that subtree, so a sibling is structurally outside it —
verified by parsing both revisions and comparing.

**Q2 — where the worktree record lives.** **Inside the spine**, top-level `origin`, on a measurement: a
spine carrying an unknown top-level key survived `claim → start → attest → advance` byte-identical, and
`validate_spine` has no unknown-key fault. The payoff is specific — `close_work` reads `origin.worktree`
instead of asking `durable_root()`, so its two-answer behaviour stops being close's problem rather than
being worked around. `durable_root` is untouched. **Residual, stated not patched:** nothing in the engine
defends `origin`; a regression test pins the round-trip and nothing else does. And
`checklist_engine.claim()` writes a *different*, lease-scoped `worktree` field that looks like it solves
this and does not.

**Q3 — data the engine consults, or an imperative a crew retypes?** **Data the engine consults by
checking it.** The generator injects a `command`-kind postcondition that reads the durable registry and
refuses `advance` unless a non-abandoned entry for that gate and role carries the declared `parent` and
`model`. `command`, never `artifact`, on measured grounds: `DESIGN_NOTE.md` §6's own correction records
that `record`/`consolidate` never evaluate artifact postconditions on a survey item, so an artifact check
would be silently inert there.

I confirmed the central claim by hand rather than from the crew's report: a registry entry recording
`admiral-epic-418-followon` against a declared `commander-session` **exits 1** naming the offending entry;
a wrong model exits 1; the matching case exits 0. **That is the exact defect the order describes, now
refusable at a gate boundary.**

**The honest residual, because you asked whether the defect moved rather than went.** It **narrowed**; it
did not close. `spec-dispatch-undeclared` detects a dispatch by matching three textual markers in the
imperative, so an author who writes "hand this to an implementer crew" is still invisible. The failure
goes from *"a crew forgets `--parent`, invisible for a wave"* to *"an author phrases a dispatch with none
of three markers, invisible for a wave"* — strictly smaller, not empty. Closing it fully needs the engine
to know what a dispatch is, which is above a Commander's latitude. The fault text, the contract and the
commit message all say this; none of them claims it is closed.

**Q4 — one tool or two?** **Two.** Their identity postures are opposite: `spine_open` acts on a spine that
does not exist and must never touch `SPINE`/`SESSION`; `spine_close` takes **no arguments at all** and
acts on the bound spine, so there is no field to redirect. An `action` switch would put both postures in
one body — precisely the "a guard written for one hazard covers the other by accident" failure
`_identity_violation`'s own docstring records as history.

## Two deviations from the order's literal wording — both inside latitude, both recorded

1. **`not_yet_written` refuses rather than coerces.** The order says "add the `isinstance` guard." A guard
   that silently reinterprets a value reproduces the exact silence the generator exists to end. Both plan
   candidates reached this independently. Fault: `spec-not-yet-written-not-bool`.
2. **The archive path is `<YYYY-MM-DD>-<work-id flattened>`**, per the shipped convention (38 of 41), not
   the order's `archive/<work-id>/` shorthand. The archive path is not in the order's hard-constraint list.

## The review standard, carried and paid off

Every reviewer handoff carried the two-question standard verbatim. It earned its keep three times:

- **g1 BLOCKed** on a write missing `newline="\n"` — `CREW_CONTEXT.md:43` requires it on every write and
  CI runs `windows-latest`, so this would have written a CRLF spine that **no test asserted against**. I
  verified all three supporting facts, returned it for rework, and required the test that would have
  caught it; I then falsified that test by mutation before accepting it.
- **The cold plan critic** found that every draft close criterion closed a spine `open_work` itself
  created, so a `close_work` hardcoding `"spine.json"` would have passed the whole suite and still been
  wrong — including for this Commander's own `execute.json`. The excluded names are now derived, with a
  mandatory differing-basename fixture I falsified by mutating the derivation to the literal.
- **And it caught a reviewer.** That critic's supporting number was wrong: it reported `execute.json`
  outnumbering `spine.json` "20 to 7"; re-measured, it is **48 vs 40** at depth 3 and 43 vs 42 excluding
  the archive — `spine.json` is a slight *majority*. **The finding survived its own wrong number.** The
  mechanism was right and the value it carried was wrong, which is the standard pointed back at the
  reviewer.

**One of my own checks was a false positive, and I am recording it rather than quietly fixing it.** My
first purity check on `_spine_open` used an AST substring scan and reported it referencing `SESSION`. The
hit was in a **docstring**. The mechanism ran correctly and the value it reported was wrong — the same
shape, in my own hands.

## Floats to the Admiral

**1. `archive.c2b` demands an OPEN or MERGED pull request; `archive.c2` demands the branch be pushed.**
The launch order forbids merge and push to `main` and makes this return the delivery;
`ORCHESTRATOR_CONTEXT.md` puts pushes and PRs behind explicit human approval. Opening a PR is an
outward-facing act this order does not authorize, so **I did not open one.** Handling is described at the
archive step below.

**2. T1 is the finding I would act on next.** The door binds one spine per process, but a Commander drives
**two** checklists — its spine and its gate plan. `_identity_violation` refuses the second, and the only
shipped way to bind one is a hand-registered second server in `~/.claude.json` — which is exactly what
your own `spine-epic` entry is. That is a manual config edit that cannot even take effect mid-session:
**the same unautomated class this epic just mechanized, sitting one tier up.** Consequence for this run: I
executed `GATE_PLAN.json` as a frozen document and ran every close-criterion command myself, rather than
driving it through the engine. Recorded, not routed around.

**3. This repo has no Cartographer packet map at all** (`docs/architecture/` absent, `map/ids.jsonl`
empty), so every Commander run here orients DEGRADED. Discharged with five hash-pinned substitutes. Not
fixable inside this order — `skills/**` and `docs/agents/*` are no-go.

**4. `docs/agents/engine-config.json` does not exist**, yet every spine's `config_ref` names it.

**5. The one-crew-per-worktree rule you had me enforce in code is prose, and the machinery is weaker.**
`active_duplicate` keys on work-id/gate/**role**/worktree, so two differently-roled crews in one worktree
are permitted. I honoured the prose rule and ran the two plan candidates **serially**, at real wall-clock
cost. `open_work` now enforces the stronger reading at provisioning time; whether the dispatch guard
should match is a fleet decision.

Six triage candidates are written up issue-ready in `TRIAGE_RECOMMENDATIONS.md`. **Nothing filed, nothing
dropped**, per your pre-ruling.

## Workflow Feedback

**What worked, and I would keep.**

- **The two-question standard is the highest-value paragraph in the launch order.** It is why g1's BLOCK
  happened, why the critic found the filename hardcode, and why I re-measured the critic instead of
  accepting it. Every reviewer handoff should carry it verbatim.
- **"A guard needs a violating case," enforced by *me mutating the code myself*.** I falsified four
  guards this run rather than trusting a green test. Two of them I would otherwise have accepted.
- **Design-it-twice converged for a real reason, not a ceremonial one.** The minimal candidate argued for
  the other candidate's structure inside its own "where this constraint hurts" section. That section is
  what made the comparison decidable — requiring it is the reusable lesson.
- **The registry now records `parent` and `model`, so the pre-ruling is checkable after the fact.** 15 of
  15 crews correct. Last wave's regression did not recur.

**What got in the way.**

- **The gate-plan filename collides with the spine.** The commander template names the gate plan
  `execute.json`; you named my spine `execute.json`. Writing the plan to its default path would have
  **overwritten the spine mid-run**. I used `GATE_PLAN.json`. Either the template should name it
  something else, or an Admiral should not name a commander spine `execute.json`.
- **A crew dispatch silently did not happen.** The g4 reviewer's `run_crew.py` invocation produced no
  registry entry and no error I could see; I noticed because I polled the registry rather than the clock,
  and re-dispatched. A dispatcher that trusted "I ran the command" would have waited forever.
- **I made the exact mistake the order warns about.** I used a pathspec-scoped `git add -A` and it swept
  in a stray nested directory; and one of my commit messages described g5's code while the code was still
  unstaged. Both are corrected in `51feb36c`, in its own message. **Scoped `-A` is still `-A`.**
- **`validate_spine` has no `not_yet_written` concept**, so a hand-authored gate plan whose tests do not
  exist yet is indistinguishable from a vacuous one. My own `GATE_PLAN.json` reports exactly five such
  faults, one per gate.
- **Wall-clock is dominated by the one-crew-per-worktree serialization.** 15 sequential crews. If that
  rule is really "never two crews on the same assignment," this run could have been substantially shorter.

---

## Closeout state — the run is BLOCKED at `archive`, deliberately, and the lease is still held

**`archive` is `blocked`, bubbled to you.** Two of its postconditions require outward-facing acts this
run is not authorized to take:

- **`archive.c2`** — "branch committed and pushed". The branch is committed (16 commits). It is **not
  pushed**.
- **`archive.c2b`** — requires an OPEN or MERGED pull request. **None was opened.**

Neither condition declares an `override_policy`, and the `PreToolUse` hook `run_crew.py` emits for every
spawned crew **denied my waive outright** — exactly as your launch order predicted: *"Never a waive — the
door denies a crew's waive on `spine_evidence` anyway."* So this blocks rather than forces, which is the
path you prescribed.

**Everything else at `archive` is satisfied:** episodes captured and git-tracked, clean tree, suite 2932,
sweep 23, `COMMANDER_RETURN.md` written and committed.

**The work area is deliberately NOT moved to `.agent-work/archive/2026-08-12-epic-559-c3-lifecycle/`,**
because the ordering you fixed is advance → release → move, and this gate has not advanced. I applied
**this run's own `closeout_refusal` to this run's own spine** and it refused correctly:

```
close refused: gate 'archive' is not terminal (status 'in-progress')
```

That is the tool this run built, declining to eat the spine that is driving it. It is the best evidence I
can offer that the ordering guard is real.

**To finish:** push `epic-559/c3-lifecycle` and open the PR (as you did for C2 — PR #563, merged by your
own `e4c80f85`), then waive `c2`/`c2b` with human authority or re-advance `archive`. **The lease is still
held**, deliberately, so a second agent cannot enter a non-terminal spine; re-claim it with the same
session id (idempotent) or `--force` if it has gone stale.

## A defect I have to report against my own dispatches

**Every one of the 15 crews was dispatched without `--spine`, so every one inherited my `SPINE_FILE` and
`SPINE_SESSION` and had its MCP door bound to *my* spine under *my* identity.** `run_crew.py` never
required otherwise and I never noticed. One implementer during the `g3` window **claimed my commander
spine as `claimed_by: "implementer"` and released it at 11:03:28**, while I was still driving; I
continued for 14 more journaled gate actions with the lease reading `released`, and recovered with an
idempotent same-id re-claim once I found it at closeout.

Two distinct problems, recorded as `tc4`:

1. **`_crew_door_env`'s no-spine branch** is documented as leaving the inherited-environment route
   *"genuinely untouched"* — but untouched means the child points at the **parent's** spine, which is the
   one spine a crew must never drive. The docstring treats this as the safe default; on this run it was
   the unsafe one.
2. **The engine does not journal `claim` or `release`.** A grep of the 43-entry journal returns **zero**.
   So a lease released out from under its owner leaves **no trace** in the append-only record the terminal
   provenance check reads.

**What was not damaged, checked rather than assumed:** all 43 journal entries carry my session id and the
`prev_hash`/`hash` chain is intact, so no crew drove a gate on my spine. The damage was to the lease, not
to the work.

This one outranks the other five floats. It is a live cross-agent identity leak in the dispatch path,
found only because I read `engine_session` while demonstrating my own close predicate — and the fact that
**the journal could not have told me** is the more troubling half.

---

## Post-terminal: `close_work` has a defect, found by using it on this run

The run is terminal, archived and released. Before that, I ran **this run's own `close_work` on this
run's own work area** — and it failed, which is the most useful thing that happened at closeout.

```
git add .../mcp_calls.jsonl failed: The following paths are ignored by one of your .gitignore files
```

`close_work` `git add`s every top-level entry. The MCP door writes **`mcp_calls.jsonl`** and
**`mcp_server_started`** beside the spine, and both are **gitignored**, so `git add` refuses them.

**Two separate problems:**

1. **It does not handle gitignored entries.** A real work area contains them; a fixture one does not.
2. **It half-succeeded and has no rollback.** 22 entries moved, then it raised, leaving the work area
   split across two directories. That is precisely the refuse-rather-than-half-succeed property the launch
   order demanded of `open_work` — and `open_work` has it. **`close_work` was never asked for it, and I
   never noticed the asymmetry when I wrote the contract.** That omission is mine, not the crew's.

**Why no test caught it, and why that is the same lesson twice.** Every `close_work` test builds its work
area with `open_work`, which never produces a gitignored file. The cold critic named exactly this
blindness for the spine *filename* and I fixed it there with a mandatory differing-basename fixture — and
did not generalize it. **The matched-pair fixture problem had a second instance and I looked at only the
one I was told about.**

**What held, and it is the good news.** **Spine-last worked under a genuine, unplanned interruption.** The
failure landed after 22 entries had moved and before the spine did, and `execute.json` and
`execute.json.journal` were still at the original path — so the retry found them. The simulated
interruption fixture approximated this; the real one proved it.

I completed the move by hand, spine and journal last, and committed it (`b9bd628e`). **I did not patch
`close_work` after the fact** — the gate is reviewed and terminal, and a post-terminal edit to approved
code is exactly the unreviewed change this whole apparatus exists to prevent. **The fix is a follow-up
and it should be the first thing R-anything picks up.**

Suggested shape: classify each entry (tracked / untracked-not-ignored / ignored) and move each
accordingly — `git mv` for tracked, `git add` then move for untracked-not-ignored, plain filesystem move
for ignored — and wrap the whole sequence so a failure restores what it moved. Plus a fixture whose work
area contains a gitignored file, which is what a real one always does.
