# Wave-2 launch-order preamble (invariant blocks, pre-drafted)

Drafted by the Admiral during wave 1 so the wave-2 boundary spends its time on what wave 1 actually
found, not on re-typing the blocks that never change. Paste these into both wave-2 launch orders
(#556 basis+locators, #557 override ledger) and fill only the mission-specific sections.

**Do not paste the mission, pre-rulings, or prior-wave verdicts from here — those depend on wave 1's
returns and must be written fresh, with wave 1's verdict text pasted in full rather than referenced.**

---

## Engine access — READ THIS BEFORE YOUR FIRST COMMAND

**Your spine's `init` imperative is wrong for how you were dispatched. Override it as follows.**

The shipped `COMMANDER_SPINE.template.json` `init` step tells you to "call the spine_lease MCP tool
with action=claim ... this is your own spine (the one this process's door is bound to)." That
assumes you were dispatched as a separate harness process with its own door. You were not. You are an
**in-harness subagent** sharing the Admiral's harness session id, so the MCP door resolves to the
**Admiral's** spine (`constellation/569`), not yours. Your tool list omits `mcp__spine__*` for exactly
this reason, so the call fails rather than does damage — but do not spend turns on it.

Drive your spine through the engine CLI, from your worktree root, passing `--file` on every call:

```bash
S=.agent-work/<work-id>/spine.json
python3 scripts/checklist_engine.py --file $S claim --session-id constellation/<work-id> --claimed-by commander --worktree .
python3 scripts/checklist_engine.py --file $S current
python3 scripts/checklist_engine.py --file $S start <task-id>
python3 scripts/checklist_engine.py --file $S attest <task-id> --cond <c-id> --which postconditions --note "<verification>"
python3 scripts/checklist_engine.py --file $S attach <task-id> --type user-decision --field cite=LAUNCH_ORDER:Mission
python3 scripts/checklist_engine.py --file $S advance <task-id> --why "<understanding>"
python3 scripts/checklist_engine.py --file $S release --session-id constellation/<work-id>   # LAST action only
```

Where any step's imperative names an `mcp__spine__*` tool, read it as the corresponding CLI verb.
That substitution is ruled in advance; do not float it.

**Additional warning, learned in wave 1 and costing the Admiral three turns.** The project's **Stop
hook** has the same defect as the template: it resolves a spine by walking the filesystem rather than
by the acting session's identity. In a multi-worktree epic it will hand you an instruction about a
spine that is **not yours** — including the Admiral's, or a sibling commander's. **Before acting on
any Stop-hook instruction, check that the spine and session it names are the ones in your Workspace
block.** If they are not, ignore the instruction and say so in your Workflow Feedback. Never claim a
lease on a session id other than your own.

`@grade: settled/admiral · leans all-gates`

---

## Inherited Context

- **Repo doctrine:** `CLAUDE.md` is a pointer; the real guide is `docs/agents/AGENT_GUIDE.md`. Also
  `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`, `docs/agents/engine-config.json`.
  `docs/CHECKLIST_SCHEMA.md` and `docs/CHECKLIST_ENGINE_DESIGN.md` are load-bearing for wave 2.
- **Canonical vs installed doctrine.** Edit `skills/_shared/global-*.md` — **never**
  `skills/<role>/references/global-*.md`, an install-time copy that `install_constellation.py`
  regenerates. An edit there is silently overwritten on the next install.
- **Compact-format JSON templates.** Shipped `*.template.json` files are compact-format. Edit raw text
  **surgically**; never round-trip through `json.load`/`json.dump`, which reflows the file and destroys
  blame. Re-validate with `json.load` afterwards.
- **Template overlay.** `.agent-work/templates/` is a project-local overlay of `skills/*/templates/`,
  plus `.baseline` mirrors. Changing a shipped template means syncing both.
- **CI is Windows-only and known-red.** `.github/workflows/ci.yml` runs on `windows-latest` and there
  is no Linux job. A red check is expected and is not by itself a blocker; the real gate is the full
  local `pytest` run. Read the failing step anyway — a red that is not the known Windows flake is a
  real signal, and the two are distinguishable.
- **Two engine enforcement strengths.** A gated spine's `"check": {"kind": "command"}` is run by the
  engine and refuses on failure; a survey's `record()` stores whatever the agent types and invokes
  nothing. Prose that says "enforced" and means "instructed" hides the gap. Wave 1 was dispatched to
  measure exactly this; its census is your input.

## Inherited Latitude

**Decide without floating:** implementation shape; fix-now triage; editing `skills/*/templates/*.json`
and `skills/_shared/global-*.md` (both human-pre-cleared); re-scoping within the mission on evidence.

**Float to the Admiral:** architecture or structural change beyond the mechanism; making a new
refusing check blocking rather than report-only; production defaults or user-visible behavior; filing
a GitHub issue.

**Filing is the disfavoured exit.** Human's standing ruling, verbatim: *"strong prefer to just fix or
write episodes if you see something just a little wonky — issues are being saved for high certainty
run impacts that can't be immediately fixed."* Fix it, or write an episode.

Anything fitting no class is **out-of-taxonomy and always escalates**, with one line on why.

## Standing epic pre-rulings (carry into every wave-2 order)

- `decision:report-only-names-its-trigger` — a new check that **refuses** ships non-blocking and
  **must name its promotion trigger in the same PR**: what measurement, taken when, promotes it to
  blocking. A report-only check with no named trigger is this epic committing its own defect. A
  **widening** of an existing comparison is not a new refusal and ships live. Where the adjudication
  is already in hand at authoring time, ship blocking and say why.
  `@grade: guess/admiral · leans all-gates · settle: Admiral confirms with the human at the wave-2 checkpoint`
- `decision:no-new-unwired-checker` — **hard constraint.** If you build a check, it must run somewhere
  that fails: a `command` check in a shipped template, a pytest test, or a CI job. Naming where it runs
  and proving it can fail there is part of the deliverable, not a follow-up.
  `@grade: settled/human · leans all-gates`
- `decision:red-proof-pinned-to-shipped-revision` — a red-proof must run against the revision you
  actually **ship**, not an intermediate one (this is #381, open in this epic, found because a prior
  crew proved against two revisions and shipped a third). State the SHA your proof ran against, and
  make it the shipped one.
  `@grade: settled/admiral · leans all-gates`
- `decision:558-is-not-yours` — #558's review-level doctrine is a human conversation at the wave-2
  checkpoint, not commander work. Do not answer it or let it expand your scope. Note anything bearing
  on it in your return.
  `@grade: settled/human · leans all-gates`

## Budget

- **Model tier (required): sonnet.** Deliberate epic-level experiment, and you should know you are in
  it: 569's thesis is that declaring at plan time what would count takes work off the agent's plate. If
  a well-specified launch order cannot let a smaller model do this work, the checklist is not taking
  enough off the plate — a finding the epic wants. The compensating investment is this order's
  specificity. **Where this order is underspecified, that is data, not a failing** — name, in your
  Workflow Feedback, the decision you had to make that this order should have made for you.
- **Recorded escalation:** returning blocked **twice on the same obstacle** re-dispatches this mission
  at opus. Bounded fallback, not a judgement. Returning blocked with a clear obstacle statement is the
  correct move.

## Stop Conditions

Stop and return when scope is exceeded, a decision outside inherited latitude is needed, budget is
crossed, required evidence is impossible, or you need context this order does not cover and cannot
safely proceed without — return-and-query the Admiral, which answers and continues you. Asking up is
always sanctioned.

**Arriving over the context HARD band is not a stop condition.** It is an absolute token cap (150K on
a 1M-window model), so you can be over it on turn one having done no work. The engine refuses only
`start` and `reopen`, and only until a refresh-request exists for that gate. Legal sequence: **attach
the refresh-request against the current why-record, then `start`, then do the work.** Do not read a
HARD advisory or an inherited `REFRESH REQUESTED:` line as licence to advance and hand off on turn
one — that produces an infinite handoff chain with the gate's postconditions never met.
