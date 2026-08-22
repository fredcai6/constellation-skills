# Launch Order: `w2-reindex — make map/INDEX.md correct by construction`

Commanders start cold. Everything you need is pasted below. This lane comes from a measurement taken
during wave 1, not from a filed issue.

## Mission

**Regenerate and stage `map/INDEX.md` and `map/ids.jsonl` automatically at commit time, so the index
is correct by construction and nobody discovers staleness after a merge.**

## Prior-Wave Verdicts (pasted)

The measurements that motivated this, all taken by the Admiral during wave 1:

- **`python -m scripts.code_map build --root .` takes 2.9 seconds and is deterministic** — two
  consecutive runs produced byte-identical `INDEX.md`.
- **Base commit `244665ee` shipped its index stale.** Committed `map/INDEX.md` said
  `tests: 98 modules, 5430 entities`; a fresh build of that same tree said `99 modules, 5460`. It was
  short by one whole test module — its own new `tests/test_plan_step_contract.py`. That was a **human**
  commit whose message stated "map/INDEX.md rebuilt".
- **Wave 1 cost three separate reindex rounds across two lanes**: each branch reindexed for its own
  additions, then the second reindexed again after the first merged.
- **`install_constellation.py` wires Claude Code hooks** (`.claude/settings.json` → `scripts/hooks/`)
  and does **not** install git hooks. `.git/hooks/` in a fresh checkout is empty.

The human's ruling on the design, in their words: reindexing costs about two minutes and two
independent merges legitimately need two reindexes — *"that sort of feels like kind of the point."*
**The loss is not the cost of the repair; it is finding out late.** Mechanize it so the extra CI round
trip never happens.

## Pre-Rulings

- `decision:git-pre-commit-not-posttooluse` — build it as a **git pre-commit hook**, not a Claude Code
  `PostToolUse` hook. Two reasons, both measured: 2.9s per commit is free where 2.9s per `Write`/`Edit`
  is real friction on an agent making many edits; and **the observed failure was a human commit**, which
  a hook keyed to agent tool calls would not have caught. Design against the failure that actually
  happened.
  `@grade: settled/human · leans g1`

- `decision:regenerate-and-stage-silently` — when the index is stale the hook **regenerates it and
  stages it**, and the commit proceeds carrying it. It does not fail the commit and make a human do the
  work. Human ruling, chosen over the fail-loudly alternative.
  `@grade: settled/human · leans g1`

- `decision:do-not-weaken-the-freshness-test` — **hard constraint, not overridable.** Leave
  `tests/test_code_map.py`'s `MapTreeFreshnessTests` **exactly as strong as it is today.** Do not
  narrow it, skip it, or make it conditional on the hook. The hook removes routine friction; the test
  remains the backstop for `--no-verify`, fresh clones, contributors without the hook installed, and
  CI. **Know what you are doing here:** automating the fix means the test can no longer fail on the
  routine path, which is uncomfortably close to this epic's own subject. The layering is only honest if
  the backstop stays intact. If you find yourself wanting to soften the test to make the hook work, the
  hook is wrong — not the test.
  `@grade: settled/human · leans all-gates`

- `decision:must-be-installed-not-merely-built` — **hard constraint.** A git hook is a **new delivery
  path** and nothing currently installs one. Wire it into `install_constellation.py` and **prove it
  fires**. Shipping it uninstalled would be a built-not-wired capability delivered inside the very epic
  that merged a lint against exactly that pattern, in the wave immediately before yours. Wave 1's
  `RegistrationLint` exists because of #345's closing line: *"Do not fix this by adding another unwired
  checker. That failure mode is available here and would be funny exactly once."*
  `@grade: settled/human · leans g2`

- `decision:hook-must-be-honest-about-what-it-stages` — a pre-commit hook that silently adds files to a
  commit is mildly surprising. Make the staging **auditable**: the regenerated files are exactly the two
  tracked map artifacts and nothing else, and the hook must never stage an unrelated dirty file it
  happens to find. Prove that boundary with a test.
  `@grade: settled/admiral · leans g1`

## Honest-Null Clause

A measured negative is a complete, successful deliverable. If you find that a pre-commit hook cannot be
made reliable here — because it cannot be installed portably, or because staging during a partial
commit (`git commit -p`, `git commit <path>`) would corrupt what the author intended to commit — **say
so with the evidence and ship nothing**. A wrong pre-commit hook is far more expensive than a manual
`code_map build`, because it silently changes what people commit. Investigate the partial-commit case
specifically; it is the sharpest known hazard in this design.

## Engine access

You were dispatched via `scripts/run_crew.py --role commander`, so you are **your own process with
your own harness session and your own spine door**. Your `mcp__spine__*` tools work and are bound to
**your** spine. Your spine's `init` imperative is correct as written: claim the lease with
`spine_lease`, `action=claim`, `claimed_by=commander`, `worktree=.`. The door needs no session id —
it reads `SPINE_SESSION` from its own environment.

Ask the engine what to do next at every step, do exactly what the active step's imperative says,
advance only once its postconditions pass, and never hand-edit `spine.json`. Work the engine never
saw did not happen.

**Dispatch your own crew through `python scripts/run_crew.py`**, never by hand. It needs `--parent`
(pass `constellation/569`) or it refuses. Its `--backend auto` resolves to `cli` here — `claude` is on
PATH — so you get real independent implementer and reviewer subprocesses. A sibling lane in wave 1
skipped this and self-reviewed every gate; an Admiral-ordered clean-room review then found two real
defects it had asserted were fine. **Use real crews.**

## Inherited Latitude

**Decide without floating:** implementation shape; fix-now triage; editing `skills/*/templates/*.json`
and `skills/_shared/global-*.md` (both human-pre-cleared); re-scoping within the mission on evidence.

**Float to the Admiral:** architecture or structural change beyond your mechanism; making a new
refusing check blocking rather than report-only; production defaults or user-visible behaviour;
filing a GitHub issue.

**Filing is the disfavoured exit.** Human's standing ruling, verbatim: *"strong prefer to just fix or
write episodes if you see something just a little wonky — issues are being saved for high certainty
run impacts that can't be immediately fixed."* Fix it, or write an episode.

Anything fitting no class is **out-of-taxonomy and always escalates**, with one line on why.

## File Ownership

Your working-notes file is **`notes-w2c.md`** at your worktree root; you are its sole writer.

> Never name a file with "findings" in the basename — the harness `Write` tool refuses it.

**Fence:** Both sibling lanes are working inside `scripts/checklist_engine.py` and the shipped spine templates. You should need neither. Stay in `scripts/hooks/`, `scripts/install_constellation.py`, `scripts/code_map`, and `tests/`. If your work needs an engine change, float it — it almost certainly means the design drifted.

Separate worktrees make git collision impossible; these fences are about not invalidating each
other's evidence or colliding at integration.

## Workspace

- **Spine:** `/home/tommy/projects/569-w2-reindex/.agent-work/w2-reindex/spine.json`
- **Worktree:** `/home/tommy/projects/569-w2-reindex`  ·  **Branch:** `epic-569/w2-reindex`
- **Base:** `9d5aac6d` — verified green by the Admiral in a clean worktree: **3622 passed, 6 skipped, 0 failed**
- **Provisioned by:** `git worktree add ../569-w2-reindex -b epic-569/w2-reindex`
- **Isolation:** proven pre-dispatch (`verify_worktree_isolation.py` over all three lanes). Do not re-prove it.

PR integration defaults to **server-side merge**. The Admiral merges; you push and open the PR.

## Inherited Context

- **Repo doctrine:** `CLAUDE.md` is a pointer; the guide is `docs/agents/AGENT_GUIDE.md`. Also
  `docs/agents/ORCHESTRATOR_CONTEXT.md`, `GLOSSARY.md`, `engine-config.json`, and
  `docs/CHECKLIST_SCHEMA.md`.
- **Canonical vs installed doctrine:** edit `skills/_shared/global-*.md`, **never**
  `skills/<role>/references/global-*.md` — that is an install-time copy `install_constellation.py`
  regenerates, so an edit there is silently overwritten.
- **Compact-format JSON templates:** edit raw text **surgically**; never round-trip through
  `json.load`/`json.dump`, which reflows the file and destroys blame. Re-validate with `json.load`.
- **Template overlay:** `.agent-work/templates/` mirrors `skills/*/templates/` with `.baseline`
  copies. Changing a shipped template means syncing both.
- **CI is Windows-only and known-red.** The local `pytest` run is the real gate. Read a CI failure
  anyway — a red that is not the known Windows flake is a real signal.
- **`map/INDEX.md` goes stale whenever you add code.** Run `python -m scripts.code_map build --root .`
  before your final commit (2.9s, deterministic) or the freshness test fails. A sibling lane is
  mechanizing this; until it lands, it is manual.

## Standing epic pre-rulings

- `decision:report-only-names-its-trigger` — a new check that **refuses** ships non-blocking and must
  name its promotion trigger in the same PR. A **widening** of an existing comparison is not a new
  refusal and ships live. Where the adjudication is in hand at authoring time, ship blocking and say why.
- `decision:no-new-unwired-checker` — **hard.** If you build a check it must run somewhere that fails:
  a `command` check in a shipped template, a pytest test, or a CI job. Naming where it runs and
  proving it can fail there is part of the deliverable.
- `decision:red-proof-pinned-to-shipped-revision` — your red-proof must run against the revision you
  actually **ship**. State the SHA; make it the shipped one.
- `decision:no-spec-migration` — do **not** touch `generate_spine.py`, `specs/`, or the
  spec-to-template migration. Human ruled it out of scope; see `episodes/active/569-001.md`.

## Pre-empted Steps

- **`understand`** — frozen by this order. Satisfy `c1` with a `user-decision` evidence item citing
  `LAUNCH_ORDER:Mission`. No human is reachable.
- **`plan`'s `c3`** — approved in advance by this order's scope; attach a `user-decision` citing
  `LAUNCH_ORDER:Mission`. You still author `execute.json` and still run plan-alternatives and the cold
  critic (`c4`/`c5`) — with **real dispatched crews**, not self-authored.
- **Worktree isolation** — proven by the Admiral.

## Budget

**Model tier: sonnet.** This is a deliberate epic-level experiment and you should know you are in it:
569's thesis is that declaring at plan time what would count takes work off the agent's plate. If a
well-specified launch order cannot let a smaller model do this work, the checklist is not taking
enough off the plate. Wave 1 supported the thesis at sonnet on both lanes.

**Where this order is underspecified, that is data, not a failing** — name, in your Workflow Feedback,
the decision you had to make that this order should have made for you.

**Recorded escalation:** returning blocked **twice on the same obstacle** re-dispatches you at opus.
Bounded fallback, not a judgement. Returning blocked with a clear obstacle statement is correct.

## Stop Conditions

Stop and return when scope is exceeded, a decision outside your latitude is needed, budget is crossed,
evidence is impossible, or you need context this order does not cover — return-and-query the Admiral,
which answers and continues you. Asking up is always sanctioned.

**Arriving over the context HARD band is not a stop condition.** It is an absolute token cap, so you
can be over it on turn one having done no work. The legal sequence is: attach the refresh-request
against the current why-record, **then** `start`, then do the work. Do not read a HARD advisory as
licence to advance and hand off on turn one — that produces an infinite handoff chain.

## Return Shape

Write `RESULT.md` to `/home/tommy/projects/569-w2-reindex/.agent-work/w2-reindex/RESULT.md` **before** going
idle — an idle notification with no artifact reads as stalled, not done.

Required: **verdict**; the **alternatives pass** and why the loser lost; **evidence** including a
red-proof pinned to the shipped SHA; **where any new check runs and proof it can fail there**;
PR number and full local suite result; **map impact**; **triage candidates** (remembering filing is
the disfavoured exit — say whether you fixed or wrote an episode, and why); and **workflow feedback,
including where this order was underspecified**.

Open the PR against `main`, referencing epic #569.
