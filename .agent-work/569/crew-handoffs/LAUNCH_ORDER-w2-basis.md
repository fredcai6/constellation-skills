# Launch Order: `w2-basis — #556, the declared basis that actually reaches the executor`

Commanders start cold. Everything you need is pasted below, including the measurements that reshaped
this issue. **#556 as filed is aimed at the wrong path — read the pre-rulings before the issue.**

## Mission

**Make a qualitative condition state, at plan time, what evidence would satisfy it — and make the
engine tell the agent that at the moment it matters, and refuse a bare assertion at attest.**

Epic 569 exists because a green qualitative gate does not currently mean anything. Measured: **65 of
105 conditions across the shipped spine templates are `check: null`**, satisfied by the executing
agent's own sentence. `checklist_engine.py`'s attest path is explicit about it:

```python
chk = c.get("check")
if chk is None:
    c["satisfied"] = True
    c["satisfied_by"] = note or "attested"
    return f"attested {iid}.{cond_id}"
```

`--note` is not required. `attest c1` with no argument writes `satisfied_by = "attested"` and the gate
opens.

**But the framing that matters is not "make attest refuse."** The reason those 65 conditions pass on
prose is not that agents are lazy — it is that **the condition never says what would count.** A
statement like *"problem statement and protected intent confirmed"* with `check: null` forces the
agent to invent the standard itself, cold, at the end of a long gate, under context pressure. That is
undelegated judgement dumped at the most expensive moment in the run.

Moving the basis to plan time — when someone is actually thinking about what the gate means — turns
attest into **pointing** rather than **composing**. Work comes off the agent's plate; the refusal is a
side effect, not the product. Build it that way round.

## Prior-Wave Verdicts (pasted)

Wave 1 measured the ground this issue rests on, and **falsified its stated entry point.**

From `docs/CHECK_SCRIPT_CENSUS.md` (committed, wave 1):

> **`generate_spine.py` has a genuinely live caller** — `scripts/spine_lifecycle.py::_compile_spine()`
> imports it directly ... `_compile_spine` is called from `spine_lifecycle.open_work()`, which is
> wired to the **`spine_open` MCP tool** ... **But that live path is not the one that produces the
> spines actually driven by real Commander/Admiral/Crew work — including this very run's own spine.**
> Per `references/stand-up-work-area.md`, a Commander's `spine.json` is produced by
> `scripts/init_work_area.py --spine <template>`, which resolves placeholders in a **pre-authored,
> hand-written** `*.template.json` and **never imports or calls `generate_spine.py` at all**.
> Confirmed directly: `grep -c '"because"' skills/commander/templates/COMMANDER_SPINE.template.json`
> → **0**, against **19** `"check": null` qualitative-style postconditions in that same file.

So #556's "half the fix already exists and is discarded" describes a compiler that **no shipped role
skill routes through**. Two further corrections to the issue text: `generate_spine.py` does not
*discard* `because` — line 521 folds it into the statement string, so it survives as prose and dies as
structure — and the human has ruled the spec-to-template migration **out of scope** for this epic
(`episodes/active/569-001.md`).

**Your target is the hand-written templates and the engine, not the compiler.**

## Pre-Rulings

- `decision:basis-lives-in-hand-written-templates` — add the basis to the shipped hand-written
  templates and make the **engine** carry it. Do not touch `generate_spine.py`, `specs/`, or the
  migration. Human ruling.
  `@grade: settled/human · leans g1`

- `decision:decorative-basis-is-a-failure` — **hard constraint.** A `because` that sits in a template
  and is neither rendered to the agent nor required at attest is **decorative**, and decorative rigor
  is the defect this epic exists to kill — not a step toward fixing it. The precedent is in this repo
  already: `map_check_note` is documented in `tests/test_checklist_engine.py`'s
  `TemplateOnlyFieldAllowlist` as *"Template-only prose ... read by no code at all. `render_human`
  emits a fixed field set, so it never reaches a run."* Do not ship that shape. Three things must be
  true together: the basis is **authored** at plan time, **rendered** by the engine at the active
  step, and **required** at attest.
  `@grade: settled/admiral · leans all-gates`

- `decision:engine-first-backfill-where-it-earns-it` — human ruling on rollout. Ship the **mechanism**
  plus authored basis for **ONE** template as proof. Do **not** author all 65. Then backfill only
  where there is measured evidence of loose attestation — the episode store (`query_episodes.py`) and
  prior spines under `.agent-work/archive/` are your evidence for which gates really pass on prose. A
  rushed `because` on a condition nobody thought hard about **reads as rigor** and is worse than none.
  `@grade: settled/human · leans g2`

- `decision:locator-definition-is-yours` — what counts as a *resolvable* locator is the main design
  content of this mission and is genuinely open. Candidates visible in the corpus: an evidence id, a
  file path plus revision, a command and its exit code, a git blob OID. **Argue it in
  plan-alternatives against the real 65 conditions**, not against a hypothetical. Test each candidate
  by asking: could a third party re-run or re-read this without asking the author?
  `@grade: guess · leans g1 · settle: apply each candidate shape to the 19 qualitative conditions in COMMANDER_SPINE.template.json and count how many can express a real locator`

- `decision:widening-live-refusal-report-only` — rendering the basis is a **widening** and ships live.
  Making attest **refuse** a bare assertion is a **new refusal**: ships report-only with a named
  promotion trigger, unless you have the adjudication in hand at authoring time, in which case ship it
  blocking and say why.
  `@grade: guess/admiral · leans g3 · settle: Admiral confirms with the human at the wave-2 checkpoint`

## Honest-Null Clause

A measured negative is a complete, successful deliverable. Specifically: if you find that a
machine-checkable locator **cannot** be expressed for most of the 65 conditions without degenerating
into prose-in-a-different-field, **say so with the evidence**. That finding would be worth more than a
mechanism that technically refuses but that authors satisfy by pasting the statement into the basis
field. Report it with the same rigor as a win.

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

Your working-notes file is **`notes-w2a.md`** at your worktree root; you are its sole writer.

> Never name a file with "findings" in the basename — the harness `Write` tool refuses it.

**Fence:** The `w2-ledger` lane owns the override paths in `checklist_engine.py` — `waive()`, forced claim/release, `consolidate --override-reason`, and the trip ledger. Do **not** edit those. Your attest refusal will need an escape; design it, and float the ledger integration to the Admiral rather than building it yourself.

Separate worktrees make git collision impossible; these fences are about not invalidating each
other's evidence or colliding at integration.

## Workspace

- **Spine:** `/home/tommy/projects/569-w2-basis/.agent-work/w2-basis/spine.json`
- **Worktree:** `/home/tommy/projects/569-w2-basis`  ·  **Branch:** `epic-569/w2-basis`
- **Base:** `9d5aac6d` — verified green by the Admiral in a clean worktree: **3622 passed, 6 skipped, 0 failed**
- **Provisioned by:** `git worktree add ../569-w2-basis -b epic-569/w2-basis`
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
- **Wave 1 shipped a `RegistrationLint`** (`tests/test_check_script_registration.py`): any new
  `scripts/{verify,check,prove,measure}_*.py` must be wired into a real check or carry an allowlist entry
  with a stated reason. If you add such a script, satisfy that lint honestly.

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

Write `RESULT.md` to `/home/tommy/projects/569-w2-basis/.agent-work/w2-basis/RESULT.md` **before** going
idle — an idle notification with no artifact reads as stalled, not done.

Required: **verdict**; the **alternatives pass** and why the loser lost; **evidence** including a
red-proof pinned to the shipped SHA; **where any new check runs and proof it can fail there**;
PR number and full local suite result; **map impact**; **triage candidates** (remembering filing is
the disfavoured exit — say whether you fixed or wrote an episode, and why); and **workflow feedback,
including where this order was underspecified**.

Open the PR against `main`, referencing epic #569.
