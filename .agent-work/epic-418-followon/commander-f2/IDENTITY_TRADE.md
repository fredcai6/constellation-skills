# g1 — Identity when the harness shares the container

The launch order made this the first gate because it is the fact every later gate writes
against: *"if a subagent-dispatching role cannot safely use the door, then editing role
spine instructions to default to it is the wrong edit."* This document is the required
deliverable — `identity-trade-is-recorded` makes silence here a gate failure.

It is deliberately **not** an MCP-local trade. Mid-gate the Admiral found the same defect
in a second, independent seam (#549), and a decision written as "is the door's env-binding
right" would be re-litigated the first time anyone touched that one.

---

## 1. The option taken

**Bind identity to the container, and require every seam to declare the granularity at
which its container actually separates. A seam may not hand identity to anything below
that granularity.**

For the MCP door this means: `SPINE_ENGINE`/`SPINE_FILE`/`SPINE_SESSION` stay
module-level constants read from the environment at import
(`scripts/mcp_spine_server.py:113-115`). No tool gains a spine-path or identity argument.
The door's container is the **OS process**, which separates externally dispatched agents
and does **not** separate in-session Task-tool subagents — so the door serves the spine
its own process was launched for, and nothing else, and a role that dispatches in-session
subagents does not offer them the door for *their* spines. Those use the CLI.

## 2. The property given up, named

**An in-session dispatched crew member cannot drive its own plan through the door.**

Concretely: a Commander may drive `spine.json` through the door, but an Implementer or
Reviewer it dispatches in-session must reach `IMPLEMENTER_PLAN.json` or
`REVIEW_SURVEY.json` through `scripts/checklist_engine.py`. The door is available to the
process that owns the binding and to no one below it. That is a real capability loss, it
is the price of this option, and it is why `the-cli-door-stays` is not merely a
compatibility promise — the CLI is the **only** path for a whole class of agent.

What is bought for it: the door cannot be pointed at another run's spine — no tool
**declares** an argument that would let it, the dispatch **ignores** an undeclared one, and
before any argv reaches the engine `run_engine` asks `checklist_engine.parse_args` what that
argv actually resolves to and **refuses** unless it resolves to the bound spine under the
bound session (`scripts/mcp_spine_server.py::_identity_violation`). That is confinement by
construction rather than by convention.

**That last clause is a runtime guard, not a test, and it was added deliberately.** The
sentence above is a claim about what this process *does*. A CI pin makes a future violation
detectable; it does not make the sentence true. Both now exist: the pin
(`tests/test_mcp_identity.py::IdentityBindingPinTests`) and the guard.

**This sentence survived five reviewer falsifications. The sequence is worth more than the
sentence, and it is the most useful thing this gate produced.**

As first written it claimed "there is no argument that would let it." The g1 reviewer
mutated the real door so `call_tool`'s `spine_status` handler honoured an undeclared
`spine_override` key, **without touching any `inputSchema`**, and all five pin tests stayed
green. **A pin over declarations is a pin over intentions.** I added a runtime test and
narrowed the claim.

The re-reviewer then defeated *that*. My runtime test checked five literal key names
against one tool; it honoured a sixth, `target_spine`, and all seven tests stayed green. Its
finding was exact and is the more useful of the two: **an enumeration is not a property,
and the prose here was claiming a property.**

I widened the pin to the argv the engine is addressed with. **A third reviewer defeated
that too**, and its mutation is the one that shows what was actually wrong all along: a
handler that reads a decoy spine directly and **returns its contents without ever calling
the engine**. No argv is ever built, so a pin over argv inspects nothing — the loop runs
zero times and passes. *A property over the calls you make says nothing about the answers
you invent.*

So the pin is now the invariant `mcp_spine_server.py`'s own docstring already asserts —
that it "never inspects or rewrites the output beyond capturing it". **The door is a
pass-through.** For any tool and any arguments, either the engine was called, addressed at
the bound spine and bound session, and the result **is that call's output**; or no engine
call happened and the result is the door's own refusal. There is no third way to produce
content, so a redirect must surface as a wrong `--file`, as invented output, or as a
non-error answer nobody computed.

Verified red against five mutation classes at that point: `spine_override` (reviewer 1),
`target_spine` (reviewer 2), a direct-read handler that never calls the engine (reviewer 3),
and two I added afterwards that no reviewer had tried — calling the engine and then
answering with something else, and redirecting the **session** rather than the spine. All
five red, all restoring to an empty diff.

A **fourth** reviewer defeated even that: it called the engine honestly — bound spine,
bound session, genuine output — and then **concatenated** leaked file content onto the
result. My check asserted the engine's output was *contained* in the answer. *Containment
is not equality; a leak adds, it does not replace.* Now `assertEqual`, so any character in
the response that did not come from the bound call is itself the violation.

**And the limit that finally showed itself, stated rather than papered over.** That leak
fired on an argument key my sweep never generates. My key set is *generated* rather than
listed, which is better, but a generated set is still a set — **black-box argument fuzzing
cannot establish a property over all possible argument names.** Adding the reviewer's key
would have repeated the exact enumeration mistake the second reviewer caught.

So the last pin does not mention argument names at all. It is over the **shape of the
code**: `call_tool` may produce content in exactly two ways — `as_result(run_engine(...))`
or `_tool_error(...)` — and every `return` in it must literally be one of those. That is
reviewer 3's choke-point suggestion made structural. A handler that reads a file, or
concatenates onto a result, or builds a dict itself has to write a return this rejects,
**whatever it names its argument**.

The two pins are complementary and neither subsumes the other. The choke-point pin is blind
to a redirect that keeps the right shape; the runtime sweep catches that. The runtime sweep
is blind to a leak on an unguessed key; the choke-point pin catches that.

A **fifth** reviewer, cold, after this run had reported itself complete, defeated the pair
by argv **POSITION**: `run_engine` builds `["--file", SPINE, verb, *rest]` and the verb slot
is reachable from `call_tool`, so a second `--file` ahead of the subcommand wins in argparse
while the bound pair sits harmlessly at position 0. The pin read `argv.index("--file")` —
the FIRST match, which is the bound one by construction, so it could never fail. *A
first-occurrence check on a value you yourself put first cannot fail.*

A **sixth**, this round, defeated the fix: the replacement scanned for the literal token
`--file`, and argparse accepts `--file=X` (one token) and the unambiguous prefix
abbreviations `--fil X` and `--fi=X`. All three redirect the read; none is that token. The
identity half was worse — its assertion was CONDITIONAL on the token `--session-id` being
present, and `mutating=False` is reachable from `call_tool`, so a forged `claim` was
demonstrated recording a lease under `FORGED-SESSION` with the pin green. *Enumerating
shapes IS the defect.*

So the pin stopped reading argv. It hands argv to the engine's own `parse_args` and asserts
`ns.file == str(SPINE)` and `getattr(ns, "session_id", None) in (SESSION, None)` — the same
predicate the runtime guard applies, in the same call. There is no seventh spelling because
there is no spelling.

**None of the six corrections was mine.** Each defeat was one layer deeper than the last,
and the escalation is the record: a pin over declarations, then over an enumeration, then
over the calls made, then over the answers given, then over argv position, and finally over
how an option may be spelled.

## 3. The rejected options — what each would and would not have covered

### Option A — move the spine path to a per-call argument

- **Would have covered:** a subagent naming *its own* spine on each call.
- **Would NOT have covered:** a subagent naming *its parent's* spine — which is the
  actual failure. Two agents on one lease is what engine session leases exist to prevent,
  and a per-call argument does nothing to prevent it. If `SPINE_SESSION` also became
  per-call, the door would have no identity of its own at all.
- **What it would have cost:** the confinement in §2, traded for nothing the repo lacks.
  **The CLI already is the per-call-identity door** — it takes `--file` and `--session-id`
  on every invocation. Option A does not add a capability; it deletes the only property
  that distinguishes the two doors and leaves two copies of the same one.
- **And it does not generalise** — see §5.

### Option B — require a caller-supplied identity

- **Would have covered:** nothing. A subagent cannot prove it is not its parent. Any
  string it can supply, it can supply its parent's.
- **Cost:** an argument on every call, buying no property.

### Option C (taken, generalised into §1) — accept the composition, forbid the in-session case in doctrine

Argued against evidence rather than asserted, as the order required:

- `tests/test_mcp_identity.py::DC3InheritanceMechanismTests` measures the **environment**
  seam failing closed: a sibling process with no configuration gets no identity and
  crashes naming `SPINE_FILE`, never the parent's reading — with the parent's door asserted
  up throughout, and a leak counterfactual proving the assertion is not vacuous.
- The **harness** seam is, verbatim from that class's docstring, *"a product-internal
  mechanism with no observation point reachable from a subprocess-level test."* It measured
  **YES** — a Task-tool subagent inherits its dispatching process's MCP scope wholesale.
  This gate **cites** that measurement and does not claim to have re-measured it.
- `docs/CHECKLIST_ENGINE_DESIGN.md:310-312` already reached the same conclusion from the
  other direction: *"Per-dispatch identity scoping is per top-level process, not per
  agent-turn; giving Task-tool-dispatched crews distinct spine identities would need its
  own design."* This document is that position stated as doctrine rather than as a
  footnote on a tombstone.

## 4. The general shape

Twice now, in two seams that knew nothing about each other:

| Seam | Identity bound to | Container actually separates | Does NOT separate |
|---|---|---|---|
| MCP door (`mcp_spine_server.py:113-115`) | the OS process, via env at import | separate dispatched processes | in-session Task subagents |
| Stop-hook binding (`spine_rail.py`, #549) | the harness session | separate sessions | in-session Task subagents |

**The harness shares the container, and we put identity in the container.** Neither seam
is wrong to bind identity to a container — that is what makes each of them confineable.
Both are wrong to assume the container separates the thing they are identifying.

So the fleet-wide rule, which is the actual deliverable of this gate:

> **Identity may be bound to a container only at the granularity that container genuinely
> separates. A seam that binds identity to a container MUST name what that container does
> not separate, and MUST NOT hand identity to anything below that granularity — it fails
> closed there, or defers to a per-call path where one exists.**

The discriminating question at any future seam is not "is our binding safe" but
**"what does our container fail to separate, and what happens to those?"**

## 5. Does this apply to the hook seam?

**Yes, and it is the case that makes the general form necessary rather than decorative.**

The hook binding's failure is the same shape reached by a different route. Its binding
file *is* keyed per agent — #419's fix works — but `session_view()` merges the bare `sid`
key and every `sid#<agent_id>` key into one flat map, and `decide_stop` takes the first
non-foreign entry. **The discriminator exists and a merge two functions later discards
it.** The second guard cannot save it: `_foreign_worktree()` compares against a recorded
`worktree` that every child entry inherited from its parent, because `CLAUDE_PROJECT_DIR`
resolves once at session launch and is inherited unchanged (#269). The field that would
have answered the question was overwritten with the wrong value before it was written.

Under §1's rule the hook's obligation is: its container is the harness session, that does
not separate subagents, therefore it must not hand a subagent an identity — it says
nothing rather than saying the parent's spine.

**`scripts/hooks/spine_rail.py` is #549's and is outside this run's file fence. This gate
cites it and repairs nothing.** Naming it here is the difference between a decision and a
precedent.

## 6. What a seam with no per-call argument does

This is the constraint that kills Option A as a general answer, and it is why §1 is
phrased as a rule about granularity rather than a rule about arguments.

**The door has a fallback; the hook does not.** A Stop hook receives what the harness
hands it. There is no call for identity to ride on, so "move identity to the call" is not
an instruction such a seam can follow. Any answer of that form would have fixed one seam
and left the other with no expressible remedy.

Under §1 the answer is uniform and available to both: **a seam below its container's
separating granularity fails closed.** For the door that means the subagent's server
crashes on a missing `SPINE_FILE` — which is what DC3 already measures it doing — and the
agent uses the CLI, which is per-call by construction. For the hook it means emitting no
spine-bound instruction at all rather than emitting the parent's. Failing closed needs no
argument to attach to, which is precisely why it generalises and a per-call argument does
not.

---

## What pins this

`tests/test_mcp_identity.py::IdentityBindingPinTests`. It is written **outcome-neutrally**:
it pins *whichever* binding this document selects and goes red on a silent move to a
different one. It does not encode "option C is correct"; it encodes "the binding is what
the trade says it is, and a change to it must come with a change to this document."

The mutation experiment is the reviewer's, not mine: an assertion nobody has watched fail
is not evidence.

## Residual — stated, not hidden

The final tightening (equality, plus the choke-point pin) was made **after** the fourth
review and was verified by me against every mutation class recorded above, **not
independently reviewed**. The Admiral set a stopping rule at four passes because the
marginal value of a fifth was below the cost of not reaching the acceptance gate, and I
applied the fix rather than shipping a pin I had just watched be defeated.

Two cold reviews have since defeated that self-verified increment — once by argv position,
once by option spelling — so the residual is no longer a caution, it is a measured outcome:
**the self-verified increment was wrong twice.** A reader should weigh it accordingly: five
passes of independent adversarial review, and each of the two increments verified only by
their author was subsequently falsified.

## What this gate did not settle

Whether Task-tool-dispatched crews *should* eventually get distinct spine identities.
`docs/CHECKLIST_ENGINE_DESIGN.md` already records that it "would need its own design," and
nothing here changes that. This document says what the fleet does **until** such a design
exists, not that one is unnecessary.
