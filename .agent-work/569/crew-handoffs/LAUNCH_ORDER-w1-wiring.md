# Launch Order: `w1-wiring — #345 / #444 / #368, the built-not-wired sweep`

Commanders start cold. Everything you need is pasted below. Do not open an issue URL expecting
context this order does not already carry.

## Mission

**Settle whether this project's "built but not wired" pattern deserves a mechanism, using a census
you take yourself — and then either build the smallest one that works, or delete the dead code and
report an honest null.**

Epic 569 exists because a green qualitative gate does not currently mean anything: 65 of 105
conditions across the shipped spine templates are `check: null`, satisfied by the executing agent's
own sentence. The epic's plan was to fix that by adding declared-basis machinery. **Your wave runs
first, and it exists to make sure that fix is not thrown into a hole.** The Admiral measured, before
planning, that this repo reliably builds capability and unreliably delivers it — so the epic's own
next wave would land on ground the epic distrusts.

Your deliverable is the guarantee that what epic 569 ships afterwards is actually reachable.

### The measurement that motivated this, and how it was taken

The Admiral ran, from the repo root:

```
for f in scripts/verify_*.py scripts/check_*.py scripts/prove_*.py scripts/measure_*.py; do
  b=$(basename $f)
  n=$(grep -rl "$b" skills/ 2>/dev/null | wc -l)
  g=$(grep -rn "\"kind\": \"command\"" skills/*/templates/*.json 2>/dev/null | grep -c "$b")
  printf "%-45s files=%-3s in-command-check=%s\n" "$b" "$n" "$g"
done
```

Result: **26 check-shaped scripts. 13 are referenced nowhere in `skills/`. Only 7 appear inside a
machine-checked `command` condition.** The thirteen with zero references were:

```
verify_context_declaration.py      verify_coverage_ledger.py
verify_epic_418_demo.py            verify_episode_observations.py
verify_installed_bundles.py        verify_iterative_planning_acceptance.py
verify_retirement.py               verify_skip_guard.py
check_corpus_freshness.py          check_role_spine_bookends.py
check_skill_freshness.py           check_template_overlay_freshness.py
prove_docstring_only.py
```

Three more are referenced in prose but never inside a `command` check:
`verify_declared_dispatch.py`, `verify_issue_set.py`, `verify_skill_registered.py`,
`verify_diagnosis.py`, `verify_worktree_isolation.py`, `measure_overread.py`.

**Treat this as a starting point, not as truth.** It is a crude grep. It cannot tell a script
invoked from a CI workflow, a git hook, a pytest test, or another script from one nothing calls at
all. Your first job is to redo it properly.

### The finding that reordered the epic — verify it yourself

`scripts/generate_spine.py` is the tool that compiles an authored gate-plan spec into an
engine-native spine. It **already requires** a `because` field on every qualitative condition
(`generate_spine.py:200-204`) — which is precisely the declared-basis mechanism epic 569's next wave
was going to build. The epic called this "half the fix already exists."

The Admiral found two things wrong with that:

1. It does **not** throw `because` away. Line 521 does
   `statement = f"{statement} -- QUALITATIVE: {cond['because']}"` — the basis survives as **prose
   inside the statement string** and dies as **structure**. That is a meaningfully different defect
   from "discarded," and it changes what wave 2 has to build.
2. **`grep -rln "generate_spine" skills/` returns only `docs/CHECKLIST_SCHEMA.md`.** The compiler has
   no caller in the skills corpus.

**Settling `generate_spine.py`'s disposition is a required deliverable of this mission**, because
epic 569's wave 2 is blocked on knowing whether a compiler path exists to carry `because` through.
Trace every live spine-instantiation path in this repo — `init_work_area.py`, the MCP `spine_open`
verb, `scripts/mcp_spine_server.py`, any test, any CI workflow — and report which one actually
produces the spines that get driven.

## Prior-Wave Verdicts (pasted)

None. This is wave 1 of epic 569; no commander has run before you.

The one prior artifact that constrains you is a **human commit that landed hours before your
dispatch**, `244665ee` "Rebuild the Commander plan step around the order it actually requires". Its
message states, verbatim:

> EDITOR PROSE OFF THE RUN'S BILL. The c6 rationale moved to a `map_check_note` sibling field on
> `context` and `plan`, the role `context_headroom_note` already plays on `execute`. render_human
> emits a fixed field set, so a note costs a run nothing while sitting where an editor is already
> looking; a test proves that rather than asserting it.

and

> New template-only task field registered in TemplateOnlyFieldAllowlist and documented in
> docs/CHECKLIST_SCHEMA.md.

**This directly affects #368.** See the pre-rulings.

## Pre-Rulings

- `decision:census-before-mechanism` — you do not decide whether this pattern deserves a mechanism
  until you have produced the census. Classify **every** check-shaped script in `scripts/` as
  **live** (reachable from a template `command` check, a CI workflow, a git hook, a test, or another
  script), **unwired** (correct and useful, nothing calls it), or **dead** (superseded, obsolete, or
  for a capability that no longer exists). One row, one evidence string, per script. Commit the
  census as an artifact in the repo — it is the input to every later decision, including the
  Admiral's, and it must outlive your worktree.
  `@grade: settled/admiral · leans g1`

- `decision:honest-null-is-a-win` — if the census shows the population is **mostly dead code**, the
  correct deliverable is **deletions and no lint at all**. Say so plainly and ship that. You will not
  be judged as having failed a wave. #345 itself asks "whether the pattern is worth a mechanism at
  all, or whether six instances in one epic is the cost of moving fast" and calls that "the human's
  call — a posture question, not a defect." The Admiral holds delegated latitude to make that call
  **on your census**, so give it the evidence to make it with.
  `@grade: settled/human · leans g1`

- `decision:registration-lint-shape` — if a mechanism **is** warranted, build #345's own options (1)
  and (2), not (3). Pasted from #345 verbatim:
  > 1. **A registration lint.** Every `scripts/verify_*.py` must appear in at least one
  > `templates/*.json` `"check"` block, or in an explicit allowlist with a stated reason. Cheap,
  > mechanical, catches instances 2–5 immediately. Would not have caught 1 (a producer, not a verifier).
  > 2. **A vocabulary rule.** Ban "RAIL" and "mechanically enforced" for anything not wired to a
  > `command`-kind check. Cheaper still, catches nothing, but stops the gap being *hidden* — which is
  > arguably the more expensive half.
  > 3. **A handoff question.** Add *"what calls this, and can that call fail?"* to the reviewer's
  > required questions. Catches all six, costs nothing mechanical, and is itself prose — which is the
  > joke, and possibly the point.

  Option 3 is rejected: it is prose enforcing prose, in an epic whose subject is that prose does not
  enforce. This is a **guess** and you may overturn it if your census gives you a reason — say so
  explicitly and give the reason.
  `@grade: guess/admiral · leans g2 · settle: if the census shows the unwired scripts are unwired because nobody knew they existed rather than because nothing checked, option 3 may be the better buy`

- `decision:no-new-unwired-checker` — **hard constraint, not overridable.** #345's closing words:
  > **Do not fix this by adding another unwired checker.** That failure mode is available here and
  > would be funny exactly once.

  If you build a lint, it must run somewhere that fails: a `command` check in a shipped template, a
  pytest test, or a CI job. Naming where it runs, and proving it can fail there, is part of the
  deliverable — not a follow-up.
  `@grade: settled/human · leans g2`

- `decision:report-only-names-its-trigger` — a new check that **refuses** ships non-blocking
  (report-only) **and must name its promotion trigger in the same PR**: what measurement, taken when,
  promotes it to blocking. A report-only check with no named trigger is this epic committing its own
  defect. Where you already have the adjudication in hand at authoring time, ship it blocking and say
  why. Note the human's own ruling in commit `244665ee`: *"reciting sensitivity 0/4 without its
  adjudication is what sends the next reader reaching for --report-only"* — weak numbers are not by
  themselves a reason to stage a check.
  `@grade: guess/admiral · leans g2 · settle: the Admiral confirms this reading with the human at the wave-2 checkpoint`

- `decision:368-census-is-stale` — #368 ("the eleven-field mechanical group is duplicated across five
  sites with no consistency check") was filed before commit `244665ee` added `map_check_note` to
  `TemplateOnlyFieldAllowlist`. **Re-measure the field group yourself; do not copy the count from the
  issue.** The issue's "eleven" is stale by at least one field, and an issue body that is stale by
  construction is exactly the defect family this epic is killing.
  `@grade: settled/admiral · leans g1`

- `decision:444-is-the-same-shape` — #444 ("nothing links the gauge record's field count across its
  seven assertion sites") and #368 are the same defect as #345 at a smaller scale: a fact duplicated
  across N sites with no mechanism keeping them equal. Handle all three under one mechanism if one
  fits; report plainly if they need three, rather than forcing a false unification.
  `@grade: guess · leans g2 · settle: try one consistency check over both field groups; if it needs per-site special-casing, they are different problems`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the
same rigor as a win.

For this mission specifically, **three** outcomes are all successes:

- The population is mostly unwired capability → build the lint, wire it, prove it fails.
- The population is mostly dead code → delete it, ship no lint, report the census.
- `generate_spine.py` has no live caller and nothing needs a compiler → **deleting it is a valid
  answer**, and it unblocks wave 2 by telling it which path to modify instead.

What is **not** acceptable is reporting a disposition you did not measure.

## Inherited Latitude

**You may decide, without floating up:**
- Implementation shape of any lint or consistency check, and where it runs.
- Deleting a script your census classifies as dead, with the evidence row recorded.
- Fix-now triage: a bounded defect you find in-flight gets fixed here rather than filed.
- Editing `skills/*/templates/*.json` and `skills/_shared/global-*.md` — both **pre-cleared by the
  human** in the latitude contract.
- Re-scoping within this mission when evidence says a piece is not real.

**You must float to the Admiral:**
- Any architecture or structural change beyond the mechanism itself.
- Making a new refusing check **blocking** rather than report-only.
- Anything that changes production defaults or user-visible behavior.
- Filing a GitHub issue — see the next line.

**Filing is the disfavoured exit.** The human's standing ruling, verbatim from the latitude
conversation: *"strong prefer to just fix or write episodes if you see something just a little wonky
— issues are being saved for high certainty run impacts that can't be immediately fixed."* So: fix
it, or write an episode. Only a high-certainty run impact you cannot fix in this wave comes up as a
filing ask.

Anything fitting none of these classes is **out-of-taxonomy and always escalates**, with one line on
why it fit no class.

## File Ownership

Your working-notes file is **`notes-w1a.md`** at the root of your worktree. You are its sole writer
this wave.

> Name it `notes-<n>.md`, **never** `findings-<n>.md`. The harness `Write` tool refuses any path
> whose basename contains "findings" — a guard aimed at unprompted report-dumping, which cannot tell
> that this file was deliberately assigned. Three agents hit it in one epic and each worked around it
> with a shell heredoc. The guard is not ours to change; the word is.

**Fence:** the sibling commander `w1-verdict` is working in `../569-w1-verdict` on
`scripts/checklist_engine.py` (the `match` comparison at lines ~1090 and ~3439) and
`scripts/validate_spine.py`. You are in a separate worktree so git cannot collide, but **do not edit
those two files** — if your census says one of them needs a change, float it to the Admiral rather
than making it. The Admiral will sequence it.

## Workspace

- **Spine (your first command targets this):**
  `/home/tommy/projects/569-w1-wiring/.agent-work/w1-wiring/spine.json`
- **Worktree:** `/home/tommy/projects/569-w1-wiring`
- **Branch:** `epic-569/w1-wiring`
- **Base commit:** `244665ee` (verified as `main`'s tip at dispatch; working tree clean)
- **Exact provisioning command the Admiral ran:**
  `git worktree add ../569-w1-wiring -b epic-569/w1-wiring`
- **Isolation:** verified by the Admiral before dispatch —
  `python3 scripts/verify_worktree_isolation.py ../569-w1-wiring ../569-w1-verdict` →
  `worktree isolation verified: 2 distinct worktrees`. You do not re-prove this.

Your first command is to `claim` the engine lease on the spine above. You do not scaffold anything;
the worktree, `.agent-work` directory, and `spine.json` already exist.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a
local merge that would diverge your worktree from main).

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` is resolved once, at
session launch, and inherited unchanged by every subagent it spawns — so you execute the **main
checkout's** hook code against the **main checkout's** state, even while every git operation stays
correctly fenced (issue #269). **This matters directly for your mission:** `scripts/hooks/` is one of
the places a check-shaped script could legitimately be wired, so your census must inspect it — but if
you change anything under `scripts/hooks/`, you cannot validate that change from inside this
worktree. Validate with a fresh process whose `CLAUDE_PROJECT_DIR` genuinely resolves to your
worktree (a headless `claude -p` launched with that value, or a plain subprocess with the env var
set), never a fixture that hand-injects the value you are trying to prove the harness delivers.

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
(`/home/tommy/projects/569-w1-wiring`), passing your spine explicitly with `--file` on every single call:

```bash
S=.agent-work/w1-wiring/spine.json

# your first command — the equivalent of the init step's "claim"
python3 scripts/checklist_engine.py --file $S claim --session-id constellation/w1-wiring --claimed-by commander --worktree .

# then, at every step, ask the engine what to do next
python3 scripts/checklist_engine.py --file $S current

python3 scripts/checklist_engine.py --file $S start <task-id>
python3 scripts/checklist_engine.py --file $S attest <task-id> --cond <c-id> --which postconditions --note "<verification>"
python3 scripts/checklist_engine.py --file $S attach <task-id> --type user-decision --field cite=LAUNCH_ORDER:Mission
python3 scripts/checklist_engine.py --file $S advance <task-id> --why "<understanding>"

# your LAST action, only after the final advance marks the spine done
python3 scripts/checklist_engine.py --file $S release --session-id constellation/w1-wiring
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
  `docs/agents/engine-config.json`.
- **Canonical vs installed doctrine.** When editing global doctrine, edit
  `skills/_shared/global-*.md` — **never** `skills/<role>/references/global-*.md`, which is an
  install-time copy that `install_constellation.py` regenerates. An edit there is silently
  overwritten on the next install.
- **Compact-format JSON templates.** The shipped `*.template.json` files are compact-format. Edit the
  raw text **surgically**; never round-trip through `json.load`/`json.dump`, which reflows the whole
  file and destroys blame. Re-validate with `json.load` afterwards.
- **Template overlay.** This repo carries `.agent-work/templates/` as a project-local overlay of
  `skills/*/templates/`, plus `.baseline` mirrors. `scripts/check_template_overlay_freshness.py`
  exists to catch drift between them — **and is one of the thirteen scripts with no reference in
  `skills/`**, which is either a live CI/hook caller your census will find, or a sharp irony your
  census should report. Commit `244665ee` says "Overlay and .baseline mirrors synced", so whatever
  keeps them synced is a live path worth tracing.
- **Windows CI is known-red.** Do not chase it. The local `pytest` run is the real gate. Full suite
  at your base commit was green: 3564 passed, 6 skipped.
- **Two engine enforcement strengths, and the vocabulary problem.** Pasted from #345, because it is
  the heart of your mission:
  > `checklist_engine.py` supports two entirely different strengths of enforced — a gated spine's
  > `"check": {"kind": "command"}`, which the engine runs and refuses on, versus a survey's
  > `record()`, which stores whatever the agent types and invokes nothing. Prose that says "enforced"
  > and means "instructed" makes the gap invisible to anyone who is not reading the JSON.

## Pre-empted Steps

- **`understand`** — the ask is frozen by this launch order. Satisfy `c1` by attaching a
  `user-decision` evidence item citing `LAUNCH_ORDER:Mission`. Do not interrogate a human; there
  isn't one reachable.
- **`plan`'s `c3` (plan approved)** — approved in advance by this order's scope. Attach a
  `user-decision` citing `LAUNCH_ORDER:Mission`. You still author `execute.json` and still run
  plan-alternatives and the cold plan critic (`c4`/`c5`) — those are not pre-empted, and given that
  your mission's central decision is *whether to build a mechanism at all*, the alternatives pass is
  load-bearing here rather than ceremonial.
- **Worktree isolation** — proven by the Admiral, above. Do not re-prove it.

## Data Locations

Everything you need is tracked and present in your worktree. Two paths in the **main checkout** that
your census may need to read, and which your worktree does **not** contain:

- `/home/tommy/projects/constellation-skills/.agent-work/` — prior epics' work areas
  (`567-*`, `commander-315`, `20260820-*`). Useful as evidence of which scripts actually ran in
  anger. Read-only: **do not write there.**
- `/home/tommy/projects/constellation-skills/episodes/` — the episode store. `query_episodes.py` over
  it is a good way to find whether a script was ever invoked in a real run.

## Budget

- **Model tier (required):** **sonnet**.

  This is a deliberate epic-level experiment, and you should know you are inside it. Epic 569's
  thesis is that declaring at plan time what would count takes work off the agent's plate. The
  Admiral is running every commander in this epic at sonnet to test that thesis: if a
  well-specified launch order cannot let a smaller model do this work, the checklist is not taking
  enough off the plate — and that is a finding the epic wants. The compensating investment is the
  specificity of this order.

  **If this order is underspecified somewhere, that is data, not a failing.** Say so explicitly in
  your Workflow Feedback: name the decision you had to make that this order should have made for you.
  That feedback is a primary deliverable of the wave, not a courtesy.

- **Compute/time, session-window:** One wave. Census first — it is cheap and it decides everything
  after it. Do not build a mechanism before you can show the census that justifies it.

## Stop Conditions

Stop and return when: your scope is exceeded, a decision outside your inherited latitude is needed,
your budget is crossed, the required evidence is impossible to obtain, or you need **context this
launch order does not cover and cannot safely proceed without** — return-and-query the Admiral (it
answers and continues you). Asking up is always sanctioned.

**Named escalation you should know about:** if you return blocked **twice on the same obstacle**, the
Admiral will re-dispatch this mission at opus rather than leave you grinding. That is a recorded,
bounded fallback in the latitude contract — not a judgement on you. Returning blocked with a clear
statement of the obstacle is the correct move, and it triggers the right machinery.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token cap,
not a share of your window (150K on a 1M-window model), so you can be over it on your first turn
having done no work. The engine refuses only the verbs that BEGIN work at a gate — `start` and
`reopen` — and only until a refresh-request exists for that gate. The legal sequence is: **attach the
refresh-request against the current why-record, then `start`, then do the work.** Attaching first
sends the guard down its release path; starting first is what gets refused.

Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:` line, as an instruction to
`spine_advance` and hand off on turn one. A fresh agent that closes its gate before doing the gate's
work produces an infinite handoff chain. Hand off when you have actually spent the context, not when
you inherit the reading.

## Return Shape

Write your result artifact to
`/home/tommy/projects/569-w1-wiring/.agent-work/w1-wiring/RESULT.md` **before** going idle — an idle
notification with no artifact reads as stalled, not done. The Admiral judges completion from what you
produced.

Required contents:

1. **Verdict** — one of: *lint built and wired*, *honest null: population is dead, deletions shipped*,
   or *mixed*, with one sentence saying which.
2. **The census** — every check-shaped script in `scripts/`, classified live / unwired / dead, one
   evidence string per row. Committed in the repo, not only in this artifact. Name the committed path.
3. **`generate_spine.py` disposition** — which live path actually produces driven spines, and whether
   the compiler has a caller. This is what wave 2 is blocked on; be unambiguous.
4. **#368 / #444 re-measurement** — the current field-group count, taken yourself, and whether one
   mechanism covers both or they are genuinely different problems.
5. **Evidence** — the PR number, the merge state, and for any new check: where it runs, and a proof
   that it can fail there. If it is report-only, the named promotion trigger.
6. **Map impact** — whether `map/INDEX.md` or `docs/architecture/` needs reconciling.
7. **Triage candidates** — remembering that filing is the disfavoured exit; prefer fix-now or an
   episode, and say which you chose and why.
8. **Workflow feedback** — including, explicitly, where this launch order was underspecified. See Budget.

When you open the PR, base it on `main` and reference epic #569 and issues #345, #444, #368 in the
body.
