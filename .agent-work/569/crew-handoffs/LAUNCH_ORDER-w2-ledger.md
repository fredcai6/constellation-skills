# Launch Order: `w2-ledger — #557, one append-only override ledger the engine writes`

Commanders start cold. Everything you need is pasted below.

## Mission

**Give every override path one auditable home that the engine writes and no CLI verb can forge, and
make closeout read it — so a completed runaway stops rendering identically to a clean run.**

## Prior-Wave Verdicts (pasted)

From #557 verbatim — the shape nobody had named:

> Four override paths exist, landing in four different places:
> | path | where it lands |
> |---|---|
> | `waive` (± `--force`) | a `waiver` evidence item on the task + `c["waived"]` — scattered per-task |
> | `claim --force --reason` / `release --force` | the session block |
> | `consolidate --override-reason` | `consolidation` |
> | `_append_trip_entry` | `trip_ledger` — **the good one** |
>
> Plus `skip --reason`, `amend --reason --authority`, `block`/`resume`.
>
> Three open issues are three faces of this one thing, filed separately:
> - **#503** — `--authority` on amend/waive is validated only as non-empty, so "human ratification" is enforced by nothing
> - **#504** — the trip ledger goes silent at closeout: a completed runaway renders identically to a clean run
> - **#259** — `--override-reason` has no sanctioned use case

And the model to copy, also from #557, quoting `checklist_engine.py:1704`'s own docstring:

> ENGINE-WRITTEN ONLY: the sole caller is `_trip_hard_gate`, which is reached from the `dispatch`
> chokepoint BEFORE `_run_verb`, so no CLI verb can create, edit, or delete an entry.

**That property — reachable only from the dispatch chokepoint, before any verb runs — is what makes
the ledger worth having. Preserve it or the whole thing is decoration.**

## Pre-Rulings

- `decision:engine-written-only` — **hard constraint, not overridable.** The ledger must be written
  from a path no CLI verb can reach. If an agent can append to it by calling a verb, it is a log, not
  a ledger, and this issue's entire value is gone. Prove the property, do not assert it.
  `@grade: settled/human · leans all-gates`

- `decision:503-and-504-are-in-scope` — commit `244665ee` deliberately left two defects open **for
  this issue**, stating so in its message: *"Still open, deliberately untouched: waive() hardcodes
  produced_by 'human' and override_policy.authority is never compared — filed on #557 rather than
  papered over with doctrine."* Both are yours. Fix them; do not paper over with doctrine.
  `@grade: settled/human · leans g1`

- `decision:259-may-be-a-deletion` — #259 says `--override-reason` has **no sanctioned use case**. If
  the census of real usage confirms that, **deleting it is a valid and preferred outcome** — one fewer
  override path is better than one more ledger entry type. Do not assume it must be preserved.
  `@grade: guess · leans g1 · settle: grep the archive under .agent-work/archive/ for real --override-reason uses; zero real uses means delete`

- `decision:closeout-must-render-it` — a ledger nothing reads is built-not-wired, which wave 1 shipped
  a lint against. Closeout must **visibly distinguish** a run carrying overrides from a clean one.
  That rendering is part of the deliverable, not a follow-up.
  `@grade: settled/admiral · leans g3`

- `decision:widening-live-refusal-report-only` — unifying the paths into one ledger is a widening and
  ships live. Any new **refusal** (e.g. rejecting an unrecognised authority) ships report-only with a
  named promotion trigger.
  `@grade: guess/admiral · leans g2 · settle: Admiral confirms with the human at the wave-2 checkpoint`

## Honest-Null Clause

A measured negative is a complete, successful deliverable. If the census shows the four paths cannot
be honestly unified — that they carry genuinely different semantics and one ledger would flatten a
distinction that matters — **say so with the evidence** and ship the smaller true thing instead.

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

Your working-notes file is **`notes-w2b.md`** at your worktree root; you are its sole writer.

> Never name a file with "findings" in the basename — the harness `Write` tool refuses it.

**Fence:** The `w2-basis` lane owns the **attest/condition** surface of `checklist_engine.py` and the shipped spine templates. You own the **override** surface: `waive()`, forced claim/release, `consolidate`, the trip ledger, and `amend`'s authority handling. You will both be in `checklist_engine.py` — stay inside your surface, and if your ledger needs an attest-side hook, float it to the Admiral to sequence rather than reaching across.

Separate worktrees make git collision impossible; these fences are about not invalidating each
other's evidence or colliding at integration.

## Workspace

- **Spine:** `/home/tommy/projects/569-w2-ledger/.agent-work/w2-ledger/spine.json`
- **Worktree:** `/home/tommy/projects/569-w2-ledger`  ·  **Branch:** `epic-569/w2-ledger`
- **Base:** `9d5aac6d` — verified green by the Admiral in a clean worktree: **3622 passed, 6 skipped, 0 failed**
- **Provisioned by:** `git worktree add ../569-w2-ledger -b epic-569/w2-ledger`
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

Write `RESULT.md` to `/home/tommy/projects/569-w2-ledger/.agent-work/w2-ledger/RESULT.md` **before** going
idle — an idle notification with no artifact reads as stalled, not done.

Required: **verdict**; the **alternatives pass** and why the loser lost; **evidence** including a
red-proof pinned to the shipped SHA; **where any new check runs and proof it can fail there**;
PR number and full local suite result; **map impact**; **triage candidates** (remembering filing is
the disfavoured exit — say whether you fixed or wrote an episode, and why); and **workflow feedback,
including where this order was underspecified**.

Open the PR against `main`, referencing epic #569.
