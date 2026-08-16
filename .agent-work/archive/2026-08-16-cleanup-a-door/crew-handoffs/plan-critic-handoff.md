# Cold plan critic — lane A door cleanup

You are a **cold critic**. Read only the two artifacts named below and the source they
cite. You have no authoring context and you are not being told the reasoning that produced
the plan — that is deliberate. Nothing is sacred; deliberate decisions are attackable.

## Read, in this order

1. `.agent-work/cleanup-a-door/MISSION_FRAME.md`
2. `.agent-work/cleanup-a-door/execute.json`
3. The source they cite: `scripts/mcp_spine_server.py`, `.mcp.json`,
   `examples/mcp-interactive-demo/spine.json`, `tests/test_mcp_lifecycle.py`,
   `tests/test_mcp_identity.py`.

Do **not** read `.agent-work/cleanup-a-door/LAUNCH_ORDER.md` or `notes-a.md`. They carry the
authoring context this critique is supposed to be independent of.

## Three lenses — apply all three

- **Intent-fit.** The stated point is: a session started with no `SPINE_FILE` calls
  `spine_open`, gets bound, and drives a real spine end to end without touching the CLI.
  Does this plan actually reach that, or does it reach something adjacent that looks like
  it? Name any gap between the exit criterion and what the gates would actually produce.
- **Testability.** Can each pathway be exercised and falsified? Attack the postconditions
  specifically: is any of them a check that cannot fail — identical output in the healthy
  and the defective world? Is any guard vacuous, or does it enumerate only one side?
- **Simplicity / YAGNI.** What can be deleted? Is the three-gate split real, or is the
  ordering dependency between g1, g2 and g3 asserted rather than genuine?

## Attack these specifically

1. **The rebind's blast radius.** The plan claims exactly four import-time derivations of
   `SPINE` must become late-bound. **Enumerate them yourself, by command, over the whole
   module, and state your count.** If there is a fifth, that is the finding.
2. **The pin question.** g2 says the rebind helper passes
   `tests/test_mcp_lifecycle.py:194`'s identifier ban on its letter, and that the pin must
   be *extended* rather than routed around. Is that honest, or is it weakening a guard
   while describing it as strengthening one? Is there a placement that needs no pin change
   at all? Argue the strongest case *against* the plan's answer.
3. **Fail-closed reachability.** Can a server whose `SPINE_FILE` is unset actually start
   and refuse, given the module does work at import (`sys.path.insert`, importing
   `checklist_engine` and `spine_lifecycle`, deriving log paths)? Name anything at import
   that would still die before a refusal is reachable.
4. **Gate ordering.** g2's precondition claims g1 makes an unbound probe survivable, and
   g3's claims g2 makes the demo spine no longer the fallback. Are those real dependencies
   or narrative ones?
5. **Anything the plan does not mention** that a reader of the source would consider
   load-bearing.

## Out of scope for your critique

Publication, merge strategy, and the deliberately deferred items the frame lists under
"Out of scope". Do not relitigate that `_identity_violation`'s semantics are fenced or that
`map/ids.jsonl` is not being fixed — both are given.

## Return format

Write your findings to `.agent-work/cleanup-a-door/crew-handoffs/plan-critic-result.md`
**before ending your turn** — that write is the delivery. Structure:

- **Verdict:** one line — is this plan fit to freeze?
- **Findings**, each with: severity (blocking / serious / minor), the lens, what is wrong,
  the evidence (file:line or a command and its output), and what you would change.
- **What you checked and found sound** — so the reader can tell coverage from silence.
- **What you did NOT check**, stated plainly (scoped null).

You do not triage your own findings and you do not edit the plan. Report only.
