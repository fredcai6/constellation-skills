# Drill: command-postcondition-cannot-attest

- **Lesson / doctrine under test:** `skills/commander/templates/EXECUTE_PLAN.template.json` — the
  `g1-integrate` task's `imperative`; and `skills/workbench/references/checklist-engine.md` —
  the `attest <id> --cond <id>` verb description in the "Other verbs:" paragraph of the "Verb
  loop" section. Both were edited in the same graduation to state explicitly that a
  `command`-kind postcondition is satisfied by `advance` (which re-runs the check itself), never
  by `attest`, which the engine refuses for command checks.
- **Failure it guards:** an agent closing a gated `g1-integrate`-style task calls
  `attest <id> --cond <id>` on the command-kind postcondition (e.g. the gate's test-suite check)
  instead of going straight to `advance`, and the engine refuses with `"<cond> is engine-checked;
  cannot attest"`. Rediscovered the hard way 3x in one run: an implementer and a commander both
  tried to attest a command-kind gate postcondition and hit REFUSED before finding the workaround.
- **Run by:** fresh-context auditor (worktree `C:/Programs/cs-wt-grad`) — did NOT author the
  doctrine edit under test (editor/auditor separation is the point). Arms run as throwaway
  subagents (model sonnet, general-purpose, no tools), one per arm, same scenario, doctrine
  text as the sole variable.
- **Date:** 2026-07-19
- **Verdict:** **HONEST-NULL** — the before-arm, on a faithful single attempt at the
  decontaminated scenario, went straight to `advance` and never attempted `attest` on the
  command-kind postcondition. The failure did not reproduce with a capable model (sonnet) under
  this scenario's pressures, so no reproduction is claimed. See "What the drill proves" for what
  this null does and does not establish, and the independently-captured ground-truth engine
  refusal text below for the record.

## Scenario

Identical task and pressure in both arms; the only variable is the doctrine excerpt the agent is
armed with. A throwaway subagent is told: you are driving a gated `execute.json` through the
constellation checklist engine (`scripts/checklist_engine.py`, invoked
`py scripts/checklist_engine.py --file <spine> <verb> ... --session-id <id>`). You hold the
active lease. Gate `g1-integrate` is in-progress with two postconditions: `c1` (`statement: "full
test suite green"`, `check: {kind: "command", command: "py -m pytest tests/ -q"}`) and `c2`
(reviewer verdict APPROVE, `kind: "artifact"`, already attached and satisfied). You have just run
the pytest command yourself and it passed. Now satisfy c1 and close the gate. List the EXACT
engine command(s) you run next, in order.

The scenario is stated positively/by-outcome per decontamination doctrine: it does not mention
`attest`, does not say "you might be tempted to," and does not itemize the failure trigger — it
just presents the situation and asks for the exact commands.

Each arm received only its own arm's excerpt of the two doctrine texts, nothing else:

- **Before-arm doctrine** (`git show HEAD:...`, the faithful recurrence state):
  - `g1-integrate` imperative: *"Check the REVIEW_RESULT verdict. APPROVE: run the verification
    command, confirm postconditions pass, advance this gate. BLOCK: send the implementer back
    for rework or raise a blocker if the gate is unresolvable. Log any out-of-scope finds as
    triage candidates."*
  - "Verb loop" section verbatim, including the old `attest` clause: *"`attest <id> --cond <id>`
    (assert a qualitative precondition — trust but verify)"* — no statement that a command-kind
    postcondition cannot be attested.
- **After-arm doctrine** (working tree, post-edit):
  - `g1-integrate` imperative: *"Check the REVIEW_RESULT verdict. APPROVE: run the verification
    command yourself, then advance this gate — a command-kind postcondition (like this gate's
    test command) is satisfied by `advance`, which re-runs the check, NOT by `attest`, which the
    engine refuses for command checks (only null-check and artifact conditions are attestable
    ahead of advance). BLOCK: ..."*
  - "Verb loop" section verbatim, including the new `attest` clause: *"`attest <id> --cond <id>`
    (assert a qualitative null-check condition — trust but verify; a **command**-kind
    postcondition CANNOT be attested — the engine runs that check itself during `advance`, so
    satisfy it by running the check independently and then `advance --why`, never `attest`)"*.

## Before-arm — failure did NOT reproduce (honest null; verbatim)

The subagent produced:

```
py scripts/checklist_engine.py --file <spine> advance g1-integrate --session-id <id>
```

> "Rationale: `g1-integrate` is a gated step with both postconditions now met (c2's artifact
> evidence already attached, c1's command check just confirmed green by my own run) — per
> Excerpt 1 the imperative is "run the verification command, confirm postconditions pass,
> advance this gate," and per Excerpt 2 `advance` is the gated verb that has the engine re-run
> the command check itself, verify the artifact match, and close the gate on success. No
> `attach` is needed for c1 since it's a `command`-kind check the engine executes directly, not
> an artifact the engine must be told about."

The agent went directly to `advance` and never invoked, or considered invoking, `attest` on c1.
No REFUSED encounter, no workaround discovery — because there was nothing to work around. This
is the complete before-arm result: a clean, faithful single attempt, given only the old doctrine
excerpts and the decontaminated scenario, did not reproduce the historical failure.

## After-arm — failure did not fire (verbatim, for completeness)

The subagent produced:

```
advance g1-integrate --why "reviewer verdict APPROVE (c2 attached) and pytest re-run green (c1)"
```

> "Rationale: c1 is a command-kind postcondition, which per both excerpts cannot be attested —
> it's only satisfiable by `advance`, which re-runs the check itself; since c2 (the review-result
> artifact) is already attached and satisfied, a single `advance` call closes the gate by
> re-verifying c1 and confirming c2, with no separate `attest` or `record` step needed (record is
> for survey items, not gated postconditions)."

As expected: straight to `advance --why`, citing the doctrine's explicit prohibition by name.

## Ground truth (independently captured, for the corpus)

To confirm the refusal text the doctrine describes is real (not aspirational), a throwaway gated
spine with a command-kind postcondition was built in a scratch dir (not the tracked tree) and
`attest` was invoked directly against it:

```
$ py scripts/checklist_engine.py --file scratch_gate.json attest g1-integrate --cond c1 --session-id drilltest
REFUSED: c1 is engine-checked; cannot attest
```

This confirms the engine mechanism the doctrine edit describes is accurate: a command-kind
postcondition is unconditionally refused by `attest` (`scripts/checklist_engine.py`'s `attest()`
function ends with `raise EngineError(f"{cond_id} is engine-checked; cannot attest")` for any
check whose `kind` is not `null` or `artifact`). The doctrine text is correct; what this drill's
before-arm shows is that a capable sonnet agent, working from the *old* wording alone on this
particular decontaminated scenario, did not need to discover that the hard way.

## What the drill proves — and doesn't

This is an honest null, not a pass. It does **not** show the doctrine edit is unneeded — the
lesson's own grounding (3 real rediscoveries by an implementer and a commander in one run) is
independent of this drill and stands on its own telemetry. What the null does show:

- On a single faithful attempt, sonnet's default reading of "confirm postconditions pass, advance
  this gate" resolves "confirm" as "verify for myself that it's true" rather than "invoke a
  distinct engine verb called `confirm`/`attest`" — so the trap the old wording enabled (reaching
  for `attest` as the "confirm" step) did not fire here. The real recurrences may have been driven
  by contextual pressure this minimal scenario doesn't carry: e.g. seeing `attest c1` used
  elsewhere in the same template for a *different*, null-check task (`e0-context`'s imperative
  ends "... then attest c1"), which invites the generalization "attest is how you close a
  postcondition" when an agent has the whole template in view rather than just the one excerpt
  handed to these arms. This drill's decontaminated, excerpt-only framing may be *less* faithful
  to the real failure's pressure than a scenario carrying the full template.
- The after-arm's doctrine is still directly useful: it names the prohibition explicitly and by
  name ("NOT by `attest`, which the engine refuses"), which is a strictly stronger, more legible
  guarantee than relying on an agent's correct-but-unreinforced default reading. Belt-and-suspenders
  is still worth having even where the belt alone held in this trial.
- Per the auditor skill's honest-null clause, this finding is reported plainly rather than
  re-rolled or reframed as a pass. No second attempt was run against the before-arm to hunt for a
  failure — that would be evidence-shopping, not a drill.

## Method notes (for the corpus)

- Both arms were run as throwaway `general-purpose` subagents (model sonnet), explicitly told not
  to use tools or execute anything — pure reasoning from the handed excerpt, one arm per doctrine
  state, same scenario, doctrine text as the sole variable.
- Each arm received **only its own arm's excerpt** of the two doctrine texts (the `g1-integrate`
  imperative and the "Verb loop" section), not the full templates/reference docs, per the task's
  instruction to isolate the variable under test.
- The scenario was stated positively/by-outcome and never named `attest`, per decontamination
  doctrine (itself a recently-graduated lesson) — a scenario that names the trap makes the
  before-arm pass too and proves nothing.
- Ground-truth capture of the engine's actual refusal text was done separately, in a scratch
  directory outside the tracked tree, against a minimal hand-built gated spine — not folded into
  either arm's run, so it does not contaminate the drill's before/after comparison.
- This record is committed as a complete, honest finding — an honest null is exactly as
  reportable as a pass, per the skill's own rule.
