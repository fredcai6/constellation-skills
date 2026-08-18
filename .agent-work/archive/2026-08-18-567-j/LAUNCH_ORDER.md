# Launch Order: `cmdr-567-j` — a launcher must take declared defaults, not machine-local ones (#619 + #633)

Epic **#567** ("the door is the interface"), **wave 3**, lane **J**. Two lanes run: J and K.
You start cold; everything you need is pasted here, not linked.

## Mission

Two issues, one idea: **a launcher is taking a value from the machine it happens to be running on,
where it should be taking a declared one.**

**#619 — the installer.** It writes a machine-probed interpreter into the tracked `.mcp.json`. And
there is a worse half found by the previous wave: a real (non-`--dry-run`) install **rewrites the
calling repo's own `.mcp.json` regardless of `--dest`**. Lane D2 ran it with `--dest /tmp/...`,
entirely outside the repo, and its worktree's tracked `.mcp.json` changed from `"command":
"python3"` to the probed `"command": "py"`. The installer's own output names the cwd's file, not
`--dest`'s. Confirmed still live on `main`.

**#633 — the model tier.** `run_crew.py` reads `--model` from the host's `~/.claude/settings.json`
when the flag is unset. The launch order names a tier for the dispatched agent and nothing below
it. So a lane tiered to Sonnet dispatched **15 crew sessions, every one Opus**, 6 of them abandoned
and retried. The tier decision applied to one process in sixteen.

The human's design, which is not yours to redesign:

> "I really want to have a default expectation per role and an allowed choices per role that the
> dispatcher can choose from with reason"

and

> "one thing I want to make sure that we also support is multiple different harnesses so we need to
> be able to set the same values for what codex uses. and also I hope to set that the same thing for
> what we do locally and which one the harness chooses or the implementer chooses should be a
> function of what the harness they're currently in is or if that's limited to local use"

## Prior-Wave Verdicts (pasted)

**The previous wave measured both of these; you do not need to reproduce the measurements.**

Lane D2's finding on the installer, verbatim from its triage candidate:

> Running `py scripts/install_constellation.py --agent codex --scope user --dest /tmp/some-other-dir
> --skills workbench commander cartographer` (no `--dry-run`) from inside this worktree rewrote
> **this worktree's own** `.mcp.json` (`"command": "python3"` -> `"command": "py"`, the probed
> interpreter), even though `--dest` pointed entirely outside the repo. […] it targets the **cwd's**
> `.mcp.json`, not `--dest`'s.

The crew-tier measurement, from `crew-runs.json` across the wave-2 lane work areas: **8 completed,
6 abandoned, 1 running — all `model=opus`**, all from the single Opus-tiered lane. The four
Sonnet-tiered lanes spawned none, because lane E's implementer ran on the `external` backend
in-process.

**And the fix the Admiral proposed was rejected by the human**, which is worth carrying because it
is the obvious wrong answer:

> "wouldn't defaulting a model to its dispatcher lead to opus commanders defaulting to opus crews?"

Inheritance launders the escalation rather than removing it. **A tier is a property of the role and
the harness, not something to inherit.**

## Pre-Rulings

Ruled in advance. Each is overridable if evidence contradicts it — **say so in your return** when
you override one.

### Mission-specific

- `decision:ship-todays-tiers` — **settled/human.** Ship the table at the tiers the corpus actually
  runs at, not the ones it is heading for: admiral `opus`, commander `sonnet`, implementer `sonnet`,
  reviewer `sonnet`, critic and cartographer `sonnet`, with `haiku` in the allowed sets below them.
  The human's direction is commanders at Sonnet and crews at Haiku or local, and he said plainly
  *"we're not there yet."* **The point of the table is that moving it later is one edit.**
  `@grade: settled/human · leans j`
- `decision:fail-closed-cheaper` — an unset model resolves from the **role**, never from the host's
  settings, and resolves toward the **cheaper** tier when ambiguous. The failure being fixed was a
  silent escalation. `@grade: settled/human · leans j`
- `decision:refuse-by-name` — a model outside a role's allowed set is **refused by name**, the way
  the duplicate-crew guard refuses. A refusal that names the rule is worth more than one that
  silently corrects. `@grade: settled/doctrine · leans j`
- `decision:reason-on-deviation` — a non-default choice inside the allowed set **requires a reason**,
  recorded in the registry beside the model. The registry already records the model faithfully; the
  reason is what makes it readable after the fact, and nothing surfaced the escalation during the
  run. `@grade: settled/human · leans j`
- `decision:harness-dimension-is-required` — the table must express **Codex and local models**, not
  only Claude Code. Whether the harness can be detected or must be declared is your unknown to
  settle; that it must be expressible is not. `@grade: settled/human · leans j`

### Standing, this epic

- `decision:reduce-complexity` — judge a change by the human's test: **does this reduce work on
  agents by moving it into mechanisms?** `@grade: settled/human`
- `decision:honest-null-is-complete` — a measured negative on the stated question is a complete,
  successful deliverable, reported with the same rigor as a win. `@grade: settled/human`
- `decision:no-issue-filing-mid-run` — **file no issue.** Stage candidates under
  `.agent-work/567-j/triage-candidates/`. His reason: *"we've been ballooning out tracking."*
  `@grade: settled/human`
- `decision:no-doctrine-promotion` — do not promote an observation into `docs/agents/*`. That is
  the human's call. `@grade: settled/project`
- `decision:in-session-hook-observation-is-not-evidence` — hooks execute from the **main checkout**
  regardless of worktree (`CLAUDE_PROJECT_DIR` resolves once at session launch, #269). Validate
  engine, door or hook behaviour in a **fresh process** with explicit paths.
  `@grade: settled/project`
- `decision:map-index-is-admiral-owned` — do not regenerate or hand-edit `map/INDEX.md` (#544).
  Your branch is accepted green **except** `tests/test_code_map.py::MapTreeFreshnessTests`.
  `@grade: settled/doctrine`
- `decision:no-fork-for-design` — helpers are **fresh** agents, never a `fork`. A fork inherits its
  dispatcher's context and believes it *is* the Commander. `@grade: settled/doctrine`
- `decision:pass-model-explicitly` — **pass `--model sonnet` on every `run_crew.py` dispatch you
  make.** `run_crew.py` inherits this host's `settings.json` default (`opus`) when `--model` is
  unset, which cost the previous wave 15 unintended Opus crew sessions, 6 of them abandoned and
  retried. The human ruled Sonnet for all remaining work. **This is the defect lane J is fixing —
  do not rely on the fix while building it.** `@grade: settled/human`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with
the same rigor as a win. Do **not** substitute your own judgement for a measurement your mission
calls for and present the result as measured.

## Inherited Latitude

| Class | Your disposition |
|---|---|
| Implementation choices inside your own files | **yours** |
| The table's shape and where it lives | **yours** |
| How the harness dimension is expressed | **yours** |
| The tier values themselves | **fixed** — ship today's, above |
| Changing `checklist_engine.py` or a spine template | **fenced** — lane K |
| Architecture / structural change | **float to the Admiral** |
| Scope change | **float to the Admiral** |
| Issue filing | **ruled: none** |
| Promoting doctrine into `docs/agents/*` | **forbidden** — human's call |
| Anything fitting no class above | **float**, with one line on why |

Float by writing the question into your return **and** ending your turn with it stated plainly.
The Admiral answers and continues you. Asking up is always sanctioned.

## File Ownership

**You are sole writer this wave of:** `scripts/install_constellation.py`; `scripts/run_crew.py`; `skills/admiral/templates/LAUNCH_ORDER.template.md`; `.agent-work/templates/LAUNCH_ORDER.template.md`; tests covering those.

**Fenced — the other lane owns it:**

| Path | Owner |
|---|---|
| `scripts/checklist_engine.py`; `scripts/mcp_spine_server.py`; every `*SPINE*.template.json` under `skills/*/templates/`; `specs/`; tests covering those | lane K |
| `map/INDEX.md` | the Admiral |

Your working-notes file is `.agent-work/567-j/notes-1.md`. Name it exactly that — **never**
`findings-<n>.md`; the harness `Write` tool refuses any basename containing "findings".

## Workspace

- **Spine (yours, provisioned):** `/home/tommy/projects/constellation-skills/.worktrees/567-j-launcher-declared-defaults/.agent-work/567-j/spine.json`
- **Worktree:** `/home/tommy/projects/constellation-skills/.worktrees/567-j-launcher-declared-defaults`
- **Branch:** `feat/567-j-launcher-declared-defaults` · **Base:** `9b38b9d9`
- **Merge position:** **first.** Lane K rebases on your merge, because it is the larger and more dangerous change.

Your first command is `spine_lease` with `action=claim, claimed_by=commander, worktree=.`.

**Your door is bound to your own spine.** You were launched by `run_crew.py --backend cli --spine`,
which set `SPINE_FILE` and an assignment-keyed `SPINE_SESSION` in your environment and started you
in your own worktree. Drive every gate through the MCP verbs. **If you find yourself reaching for
`checklist_engine.py` on the command line, stop and record it** — this epic exists to remove that
path, and a place where it is still needed is worth more than the workaround.

**Isolation is git-only.** `CLAUDE_PROJECT_DIR` resolves once at session launch, so hook code runs
from the **main checkout** even inside your worktree (#269). Validate in a fresh process.

## Inherited Context

- **The merge gate is the full suite green on Linux**, run in a **clean detached worktree of your
  branch**, never your working copy. *A check that runs against your own working copy is not a check
  on the world.* Windows CI is red on a pre-existing ~122-failure path-casing baseline and is **not**
  the yardstick (#575 deferred).
- **Unset four variables for your suite run:** `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT
  -u CREW_SCRATCH_DIR`. A dispatched crew's own `CREW_SCRATCH_DIR` leaks into an assertion built on
  `os.environ` and reds
  `tests/test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry_without_worktree_key_does_not_crash_and_leaves_scratch_dir_unbound`
  — a test your change does not touch. Confirmed four independent ways, including on an untouched
  base commit. **Do not "fix" `run_crew.py` to satisfy it**; that is a real regression introduced to
  silence a false one.
- **A headless `claude -p` launched in this worktree inherits `SPINE_*` and the Stop hook.** Strip
  `SPINE_FILE`, `SPINE_SESSION`, `SPINE_PARENT` and `CREW_SCRATCH_DIR` from every helper you launch.
  In the previous wave one lane's probe agent began driving that lane's own spine, and a cold
  subagent read a session id out of a journal and drove a live run under it. Add `< /dev/null` —
  helpers hit `Warning: no stdin data received in 3s` without it.
- **A failing subtest is greppable.** The root `conftest.py` restates each failed subtest as a line
  beginning `FAILED `. Grep for `^FAILED` and trust it.
- **`episodes/` has one write path**, `scripts/apply_episode_delta.py`, always `--store-root
  episodes`. Order is **write → `git add` → suite → commit**. The observation guard cannot tell a
  past-tense verb from an imperative; rephrase rather than growing its exception list.
- **GitHub returns intermittent 503s.** Retry `gh pr create` and `gh pr merge`, and **gate each
  retry on whether the world actually changed**, never on the command's own output.
- **`.agent-work/` is tracked deliberately**, so your work area, return and triage candidates reach
  `main` with your branch.

## Pre-empted Steps

- **Work-area stand-up is done.** Worktree, `.agent-work/567-j/` and `spine.json` were provisioned
  by the Admiral per `skills/_shared/stand-up-work-area.md`. Your `init` step means one thing: claim
  the lease.
- **The `--here` arrival check is retired** (#610). Isolation was gated across both worktrees before
  dispatch.
- **The wave-3 transition is authored and verified** — `transitions/w3/`, `admiral-prelaunch` exit 0.
  You deliver; you do not replan the wave.

## Local Unknowns

Named so you do not mistake them for settled:

- Whether the harness an agent runs in can be **detected**, or must be **declared**. Establish this
  before choosing, because it decides the table's shape.
- Whether the installer's caller-mutation is one bug with the probed interpreter or two separate
  ones. The previous wave did not determine this.
- Whether any existing caller depends on the installer wiring the cwd's `.mcp.json` — check before
  removing it, since the behaviour may be load-bearing for the local dev loop.

## Budget

- **Model tier (required):** **Sonnet** for you.
- **Crew model tier (required):** **Sonnet** for every crew you dispatch — pass `--model sonnet`
  explicitly. This slot exists because the previous wave had none, and 15 crew sessions silently ran
  a tier above their lane.
- **Compute/time:** One focused session. Two bounded changes with clear acceptance tests.

## Stop Conditions

Stop and return when scope is exceeded, a decision outside your latitude is needed, budget is
crossed, the evidence is impossible to obtain, or you need context this order does not cover.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token cap
(150K on a 1M-window model), not a share of your window, so you can be over it on turn one having
done no work. The engine refuses only `start` and `reopen`, and only until a refresh-request exists.
The legal sequence is **attach the refresh-request, then `start`, then do the work.**

Do not read a HARD advisory as an instruction to `advance --why` and hand off on turn one. A fresh
agent that closes its gate before doing the gate's work produces an infinite handoff chain. **The
previous wave's D1 lane refused exactly that and left its gate pending with a refresh-request
attached — copy that behaviour.** Hand off when you have spent the context, not when you inherit
the reading.

**Do not end your turn with an engine gate open.** The Stop hook refuses it and outranks the
context-trip advisory (#595). The sanctioned exit is `spine_halt` with `action=block`, naming what
you cannot satisfy and the next action.

## Return Shape

Write your result to **`.agent-work/epic-567-door/results/lane-j-RETURN.md`** — that
exact path, in your own worktree, committed on your branch. Write it **before** going idle.

Include:

1. **Verdict** — delivered, or an evidenced honest null.
2. **The installer** — before and after, with `git diff .mcp.json` proving a real install with
   `--dest` outside the repo leaves the repo's file byte-identical.
3. **The table** — its values, its shape, where it lives, and how the harness dimension works.
4. **The refusal and the reason**, each demonstrated: a model outside the allowed set refused by
   name, and a non-default choice recorded with its reason in the registry.
5. **A crew dispatched with no `--model`** running at its role's default rather than the host's,
   proven **from the registry entry**, not from the code.
6. **Suite result** — full suite on Linux in a clean detached worktree of your branch, with the
   tally, the `^FAILED` grep, and the commit sha. `MapTreeFreshnessTests` may fail; nothing else may.
7. **Touched paths** — every file, and anything you wanted to touch but did not because it is fenced.
8. **Triage candidates** — as files under `.agent-work/567-j/triage-candidates/`, listed. None filed.
9. **Workflow feedback** — what helped, what got in the way, and **your own mistakes**. The previous
   wave's most useful returns were the ones that indicted their own author.
10. **PR** — opened against `main` from `feat/567-j-launcher-declared-defaults`, with the number and head sha.
