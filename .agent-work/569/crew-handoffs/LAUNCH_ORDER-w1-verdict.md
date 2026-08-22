# Launch Order: `w1-verdict — #371, the match comparison that wedges a gate`

Commanders start cold. Everything you need is pasted below, including the code. Do not open an issue
URL expecting context this order does not already carry — and note that **#371's body is partly stale**,
which is itself part of your mission. Read the pre-rulings before you read the issue.

## Mission

**Make a gate able to express "any of these acceptable verdicts" without wedging, and make a
mistyped `match` shape impossible to write silently.**

Epic 569 is about gates that cannot fail. Your issue is the mirror defect and the smallest real hole
in the epic: **a gate that cannot _pass_.** It matters more than an ergonomics papercut because of
what it pushes an agent to do when it wedges.

### The mechanism, verified by the Admiral before dispatch

`scripts/checklist_engine.py` compares evidence payloads against a condition's required `match` with
plain `==`, at **two** sites.

Site 1 — `_check_condition`'s artifact branch, around line 1083:

```python
    if kind == "artifact":
        want = chk.get("match", {})
        for ev in t.get("evidence", []):
            if ev.get("superseded"):
                continue
            if ev.get("type") == chk["evidence_type"] and all(
                ev.get("payload", {}).get(k) == v for k, v in want.items()
            ):
                cond["satisfied"] = True
                cond["satisfied_by"] = ev["id"]
                return True
```

Site 2 — `attest`'s artifact branch, around line 3438:

```python
                want_match = chk.get("match", {})
                if not all(ev.get("payload", {}).get(k) == v for k, v in want_match.items()):
                    raise EngineError(f"evidence {evidence_id!r} does not match required {want_match}")
```

**Consequence:** an author who writes `"match": {"verdict": ["APPROVE", "APPROVE-WITH-FOLLOWUPS"]}`
— the natural way to express "either of these is fine" — produces a condition that compares a
**string payload against a list** and is therefore **never satisfiable, by anything, ever.** Nothing
warns them. The gate simply cannot be closed.

`scripts/validate_spine.py` does not catch it. It gained a fault for an artifact check with **no**
`match` (issue #562, `_fault_artifact_no_match`, around line 456) — because an empty match is
vacuously true and any arrival of that evidence type satisfies it. That is the *cannot-fail* half.
**The *cannot-pass* half — a `match` whose value is the wrong type — is unguarded.**

### Why this is not a papercut, in #371's own words

> **Why this matters more than an ergonomics papercut:** the wedge pushes a Commander toward
> attaching a *second* evidence item reading `APPROVE` — i.e. **fabricating a verdict the reviewer
> did not give**. That is precisely the `refuse-never-fabricate` violation the rest of that gate spent
> two review rounds hunting. The only honest exits are `waive --force` (what #305 did, with the real
> verdict on the record) or amending the gate mid-run to fit the result you got, which looks like
> moving the goalposts.

That is the whole reason your small change is in wave 1 rather than wave 4.

## Prior-Wave Verdicts (pasted)

None. This is wave 1 of epic 569.

The live incident #371 was filed from, pasted so you have the concrete shape:

> Hit live in #305 (epic #298), gate `g2-integrate`:
> ```
> REFUSED: evidence 'e-g2-review-2' does not match required {'verdict': 'APPROVE'}
> ```
> The reviewer had approved with no blockers. The match is a **literal string equality**, authored at
> plan time before anyone knew which of the two approve-flavored verdicts would come back.

## Pre-Rulings

- `decision:371-vocabulary-half-is-already-done` — **#371's body is stale and you must not act on the
  stale half.** The issue is written around `APPROVE-WITH-FOLLOWUPS`, a verdict it calls "a sanctioned
  verdict in the `constellation-reviewer` vocabulary." The Admiral measured before dispatch:
  **`APPROVE-WITH-FOLLOWUPS` no longer exists anywhere in this corpus.** A token census over `skills/`
  and `docs/` returns:

  ```
    34  APPROVE      24  BLOCK      4  REJECT      3  COMMENT
  ```

  with no competing approve-flavoured verdict. The epic body's claim of a "three-way
  verdict-vocabulary inconsistency across four documents" **did not reproduce** and has been formally
  dropped from epic 569's scope.

  **Do not reintroduce `APPROVE-WITH-FOLLOWUPS`. Do not go reconcile a vocabulary.** Your mission is
  the *mechanism* only. The mechanism is still fully real — a list-valued match is silently
  unsatisfiable today regardless of which verdicts exist — but it is now the entire job.
  `@grade: settled/admiral · leans g1`

- `decision:widening-ships-live-refusal-ships-report-only` — epic 569's standing posture is that a new
  check which **refuses** ships non-blocking and names its promotion trigger. Your mission splits
  across that line, so it is ruled in advance:
  - **Making `match` accept a set of values is a _widening_** of a comparison that is currently
    silently broken. It adds no wall. **Ships live.**
  - **Making `validate_spine` _reject_ a mistyped `match` shape is a new refusal.** Ships
    **report-only**, and **must name its promotion trigger in the same PR** — what measurement, taken
    when, promotes it to blocking.

  This split is the Admiral's reading of the human's ruling, not the human's own words, and the
  Admiral has flagged it for confirmation at the wave-2 checkpoint. If you think it is wrong, say so
  in your return; do not silently do it differently.
  `@grade: guess/admiral · leans g2 · settle: Admiral confirms with the human at the wave-2 checkpoint`

- `decision:backward-compatibility-is-non-negotiable` — every existing scalar `match` in the shipped
  corpus must keep working unchanged. Whatever shape you choose for "a set of acceptable values" must
  be distinguishable from a scalar without ambiguity. Inventory the existing matches first
  (`grep -rn '"match"' skills/*/templates/*.json`) so you are designing against the real corpus rather
  than a hypothetical one.
  `@grade: settled/admiral · leans g1`

- `decision:match-shape-is-yours-to-choose` — a bare list (`["A","B"]`) is the obvious shape, but it is
  not the only one, and a richer operator form (e.g. `{"any_of": [...]}`) buys explicitness and room
  to grow at the cost of verbosity. **Choose, and argue it in your plan-alternatives pass.** This is
  genuinely open and is the main design content of your mission.
  `@grade: guess · leans g1 · settle: run both shapes against the existing corpus of matches; the one that cannot be confused with a legitimate scalar list-valued payload wins`

- `decision:red-proof-pinned-to-shipped-revision` — your red-proof must run against **the revision you
  actually ship**, not an intermediate one. This is issue #381, open in this same epic, and it was
  found because a prior crew proved its red-proofs against `49059be` and `fb9dfc2` while shipping
  `667b5e4`. Iterating after proving is ordinary and correct; **re-running the proof against what
  landed** is what nobody required. Require it of yourself: state the commit SHA your proof ran
  against, and make it the shipped one.
  `@grade: settled/admiral · leans g2`

- `decision:558-is-not-yours` — #558 ("Review levels check different questions: establish high-level vs
  low-level review doctrine") was originally paired with #371 in this wave and has been **pulled
  entirely**. It is an open design question, not an implementation issue, and the human is settling it
  in conversation before wave 3. **Do not answer it, do not partially answer it, and do not let it
  expand your scope.** If your work surfaces something that bears on it, note it in your return for
  the Admiral to carry into that conversation.
  `@grade: settled/human · leans all-gates`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the
same rigor as a win.

Concretely for you: if you find that a list-valued `match` **cannot** be supported without breaking
something real — an ambiguity with legitimate list-valued payloads, or a corpus match that would
change meaning — then **saying so, with the evidence, is a complete deliverable.** The fallback
(making `validate_spine` refuse the shape loudly so nobody writes an unsatisfiable gate again) would
then be the whole fix, and that is a good outcome, not a half one.

## Inherited Latitude

**You may decide, without floating up:**
- The `match` shape and its implementation.
- Fix-now triage: a bounded defect you find in-flight gets fixed here rather than filed.
- Editing `skills/*/templates/*.json` and `skills/_shared/global-*.md` — both **pre-cleared by the
  human** in the latitude contract.
- Re-scoping within this mission when evidence says a piece is not real.

**You must float to the Admiral:**
- Any architecture or structural change beyond this mechanism.
- Making the new `validate_spine` refusal **blocking** rather than report-only.
- Anything that changes production defaults or user-visible behavior.
- Touching the verdict **vocabulary** itself (adding, removing, or renaming a verdict) — that is out
  of scope per the first pre-ruling, and if you think it is necessary, it is a float, not a decision.
- Filing a GitHub issue — see the next line.

**Filing is the disfavoured exit.** The human's standing ruling, verbatim: *"strong prefer to just fix
or write episodes if you see something just a little wonky — issues are being saved for high certainty
run impacts that can't be immediately fixed."* Fix it, or write an episode.

Anything fitting none of these classes is **out-of-taxonomy and always escalates**, with one line on
why it fit no class.

## File Ownership

Your working-notes file is **`notes-w1b.md`** at the root of your worktree. You are its sole writer
this wave.

> Name it `notes-<n>.md`, **never** `findings-<n>.md`. The harness `Write` tool refuses any path whose
> basename contains "findings" — a guard aimed at unprompted report-dumping, which cannot tell that
> this file was deliberately assigned. Three agents hit it in one epic and each worked around it with a
> shell heredoc. The guard is not ours to change; the word is.

**Fence:** the sibling commander `w1-wiring` is working in `../569-w1-wiring` on the built-not-wired
census (#345/#444/#368). It has been told **not** to edit `scripts/checklist_engine.py` or
`scripts/validate_spine.py` — those are yours this wave. In return, **do not** create or wire a new
`scripts/verify_*.py` or `scripts/check_*.py` script: that is its territory, and a new check-shaped
script appearing mid-census would corrupt its measurement. If your fix wants one, float it to the
Admiral and it will be sequenced.

You are in separate worktrees, so git cannot collide; this fence is about not invalidating each
other's evidence.

## Workspace

- **Spine (your first command targets this):**
  `/home/tommy/projects/569-w1-verdict/.agent-work/w1-verdict/spine.json`
- **Worktree:** `/home/tommy/projects/569-w1-verdict`
- **Branch:** `epic-569/w1-verdict`
- **Base commit:** `244665ee` (verified as `main`'s tip at dispatch; working tree clean)
- **Exact provisioning command the Admiral ran:**
  `git worktree add ../569-w1-verdict -b epic-569/w1-verdict`
- **Isolation:** verified by the Admiral before dispatch —
  `python3 scripts/verify_worktree_isolation.py ../569-w1-wiring ../569-w1-verdict` →
  `worktree isolation verified: 2 distinct worktrees`. You do not re-prove this.

Your first command is to `claim` the engine lease on the spine above. You do not scaffold anything;
the worktree, `.agent-work` directory, and `spine.json` already exist.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a local
merge that would diverge your worktree from main).

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` is resolved once, at
session launch, and inherited unchanged by every subagent it spawns, so you run the **main checkout's**
hook code even while git stays correctly fenced (issue #269). Your mission does not touch
`scripts/hooks/`, so this should not bite — but if it turns out that it does, validate with a fresh
process whose `CLAUDE_PROJECT_DIR` genuinely resolves to your worktree, never a fixture that
hand-injects the value you are trying to prove the harness delivers.

## Engine access — READ THIS BEFORE YOUR FIRST COMMAND

**Your spine's `init` imperative is wrong for how you were dispatched. Override it as follows.**

The shipped `COMMANDER_SPINE.template.json` `init` step tells you to "call the spine_lease MCP tool
with action=claim ... this is your own spine (the one this process's door is bound to), so the door
needs no session id argument, it reads SPINE_SESSION from its own environment."

That instruction assumes you were dispatched as a **separate harness process with its own door**. You
were not. You are an **in-harness subagent**, and you share the Admiral's harness session id — so the
MCP door resolves to the **Admiral's** spine (`constellation/569`), not yours. Calling `spine_lease`
would claim, drive, or corrupt the epic's own spine. Your tool list omits the `mcp__spine__*` tools
for exactly this reason, so the call will simply fail rather than do damage — but do not spend turns
trying to make it work.

**Drive your spine through the engine CLI instead**, from your worktree root
(`/home/tommy/projects/569-w1-verdict`), passing your spine explicitly with `--file` on every single call:

```bash
S=.agent-work/w1-verdict/spine.json

# your first command — the equivalent of the init step's "claim"
python3 scripts/checklist_engine.py --file $S claim --session-id constellation/w1-verdict --claimed-by commander --worktree .

# then, at every step, ask the engine what to do next
python3 scripts/checklist_engine.py --file $S current

python3 scripts/checklist_engine.py --file $S start <task-id>
python3 scripts/checklist_engine.py --file $S attest <task-id> --cond <c-id> --which postconditions --note "<verification>"
python3 scripts/checklist_engine.py --file $S attach <task-id> --type user-decision --field cite=LAUNCH_ORDER:Mission
python3 scripts/checklist_engine.py --file $S advance <task-id> --why "<understanding>"

# your LAST action, only after the final advance marks the spine done
python3 scripts/checklist_engine.py --file $S release --session-id constellation/w1-verdict
```

Run `<verb> --help` for exact flags; the verb set is
`current, claim, heartbeat, release, start, advance, record, consolidate, skip, block, resume,
reopen, append, amend, attest, waive, attach, flag-candidate`.

Everything else about engine discipline is unchanged and still binding: **ask the engine what to do
next at every step, do exactly what the active step's imperative says, advance only once its
postconditions pass, and never hand-edit `spine.json`** — the engine owns that state and stamps the
provenance that proves the work was really driven. Work the engine never saw did not happen.

Where an imperative on any step names an `mcp__spine__*` tool (`spine_lease`, `spine_evidence`,
`spine_advance`, `spine_status`, `spine_start`), read it as naming the corresponding CLI verb above.
That substitution is ruled in advance; you do not need to float it.

`@grade: settled/admiral · leans all-gates`

## Inherited Context

- **Repo doctrine:** `CLAUDE.md` is a pointer; the real guide is `docs/agents/AGENT_GUIDE.md`. Also
  read `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`, and
  `docs/agents/engine-config.json`. `docs/CHECKLIST_SCHEMA.md` and `docs/CHECKLIST_ENGINE_DESIGN.md`
  are directly load-bearing for your mission.
- **Canonical vs installed doctrine.** When editing global doctrine, edit `skills/_shared/global-*.md`
  — **never** `skills/<role>/references/global-*.md`, which is an install-time copy that
  `install_constellation.py` regenerates. An edit there is silently overwritten on the next install.
- **Compact-format JSON templates.** The shipped `*.template.json` files are compact-format. Edit the
  raw text **surgically**; never round-trip through `json.load`/`json.dump`, which reflows the whole
  file and destroys blame. Re-validate with `json.load` afterwards.
- **Template overlay.** This repo carries `.agent-work/templates/` as a project-local overlay of
  `skills/*/templates/`, plus `.baseline` mirrors. If you change a shipped template, the overlay and
  its `.baseline` mirror need syncing — commit `244665ee` did exactly this and its message says so.
- **Windows CI is known-red.** Do not chase it. The local `pytest` run is the real gate. Full suite at
  your base commit was green: 3564 passed, 6 skipped.
- **The engine has two enforcement strengths, and this matters to your design.** From #345:
  > `checklist_engine.py` supports two entirely different strengths of enforced — a gated spine's
  > `"check": {"kind": "command"}`, which the engine runs and refuses on, versus a survey's `record()`,
  > which stores whatever the agent types and invokes nothing.

  Note that `record()` deliberately evaluates only `command`-kind postconditions on a survey item;
  `null`-kind and `artifact`-kind stay unevaluated there, ruled out of scope by #422. **Your change is
  to `artifact`-kind matching, so check whether that scoping decision interacts with it** — and if it
  does, that is a float, not a scope expansion.
- **Known-open, deliberately left, and adjacent to you.** Commit `244665ee`'s message says:
  > Still open, deliberately untouched: waive() hardcodes produced_by "human" and
  > override_policy.authority is never compared -- filed on #557 rather than papered over with doctrine.

  `#557` is **wave 2's** work, not yours. If you touch `waive()` in passing, do not fix that; leave it.

## Pre-empted Steps

- **`understand`** — the ask is frozen by this launch order. Satisfy `c1` by attaching a
  `user-decision` evidence item citing `LAUNCH_ORDER:Mission`. Do not interrogate a human; there isn't
  one reachable.
- **`plan`'s `c3` (plan approved)** — approved in advance by this order's scope. Attach a
  `user-decision` citing `LAUNCH_ORDER:Mission`. You still author `execute.json` and still run
  plan-alternatives and the cold plan critic (`c4`/`c5`); the match-shape choice is exactly what the
  alternatives pass is for, so run it properly rather than as ceremony.
- **Worktree isolation** — proven by the Admiral, above. Do not re-prove it.

## Data Locations

Everything you need is tracked and present in your worktree. One path in the **main checkout** your
work may benefit from, which your worktree does not contain:

- `/home/tommy/projects/constellation-skills/.agent-work/` — prior epics' work areas, including real
  driven spines (`567-*`, `commander-315`). These are the best available corpus of **actual `match`
  usage in anger**, as opposed to the shipped templates. Read-only: **do not write there.**

## Budget

- **Model tier (required):** **sonnet**.

  This is a deliberate epic-level experiment, and you should know you are inside it. Epic 569's thesis
  is that declaring at plan time what would count takes work off the agent's plate. The Admiral is
  running every commander in this epic at sonnet to test it: if a well-specified launch order cannot
  let a smaller model do this work, the checklist is not taking enough off the plate — and that is a
  finding the epic wants. The compensating investment is the specificity of this order.

  **If this order is underspecified somewhere, that is data, not a failing.** Say so explicitly in your
  Workflow Feedback: name the decision you had to make that this order should have made for you.

- **Compute/time, session-window:** One wave, and a small one. The code surface is two comparison
  sites plus `validate_spine`. If you find yourself making large edits to `checklist_engine.py`, stop
  and re-read the mission — that is a signal you have drifted into #558 or into vocabulary work, both
  of which are out of scope.

## Stop Conditions

Stop and return when: your scope is exceeded, a decision outside your inherited latitude is needed,
your budget is crossed, the required evidence is impossible to obtain, or you need **context this
launch order does not cover and cannot safely proceed without** — return-and-query the Admiral (it
answers and continues you). Asking up is always sanctioned.

**Named escalation you should know about:** if you return blocked **twice on the same obstacle**, the
Admiral will re-dispatch this mission at opus rather than leave you grinding. That is a recorded,
bounded fallback in the latitude contract — not a judgement on you.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token cap, not
a share of your window (150K on a 1M-window model), so you can be over it on your first turn having
done no work. The engine refuses only the verbs that BEGIN work at a gate — `start` and `reopen` — and
only until a refresh-request exists for that gate. The legal sequence is: **attach the refresh-request
against the current why-record, then `start`, then do the work.** Attaching first sends the guard down
its release path; starting first is what gets refused.

Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:` line, as an instruction to
`spine_advance` and hand off on turn one. A fresh agent that closes its gate before doing the gate's
work produces an infinite handoff chain. Hand off when you have actually spent the context, not when
you inherit the reading.

## Return Shape

Write your result artifact to
`/home/tommy/projects/569-w1-verdict/.agent-work/w1-verdict/RESULT.md` **before** going idle — an idle
notification with no artifact reads as stalled, not done. The Admiral judges completion from what you
produced.

Required contents:

1. **Verdict** — one sentence: the shape you chose and whether both halves shipped.
2. **The chosen `match` shape**, and the alternatives pass that chose it — what you compared, and why
   the loser lost.
3. **Backward-compatibility evidence** — the inventory of existing `match` uses in the corpus, and a
   demonstration that every one still behaves identically.
4. **Red-proof, pinned** — the proof that a list-valued match is unsatisfiable **before** and
   satisfiable **after**, with the **commit SHA it ran against**, and that SHA being the shipped one
   (per `decision:red-proof-pinned-to-shipped-revision`).
5. **The `validate_spine` refusal** — what shapes it rejects, that it ships report-only, and its
   **named promotion trigger**.
6. **Evidence** — PR number and merge state; full local `pytest` result.
7. **Map impact** — whether `map/INDEX.md` or `docs/architecture/` needs reconciling.
8. **Triage candidates** — remembering that filing is the disfavoured exit; prefer fix-now or an
   episode, and say which you chose and why.
9. **Anything bearing on #558** that you noticed but did not act on, for the Admiral to carry into the
   human conversation before wave 3.
10. **Workflow feedback** — including, explicitly, where this launch order was underspecified.

When you open the PR, base it on `main` and reference epic #569 and issue #371 in the body.
