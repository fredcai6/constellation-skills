# Triage candidate: the spine template's `init` imperative asserts a binding that does not exist

- **Disposition:** `recommend-and-defer` for the wording; the underlying capability
  is what lane A actually fixes.
- **Raised by:** `cmdr-567-a` at `600de020`.
- **Depends on:** lane A's own deliverable. Fix the wording *after* the binding verb
  lands, or the corrected wording will be wrong again.

## The observation

`templates/COMMANDER_SPINE.template.json`'s `init` imperative — the very first
instruction any Commander reads — says:

> Claim the engine session lease on this spine ... by default, call the `spine_lease`
> MCP tool with `action=claim` ... **this is your own spine (the one this process's
> door is bound to)**, so the door needs no session id argument, it reads
> `SPINE_SESSION` from its own environment. CLI fallback: `<engine> claim
> --session-id ...`

The bolded clause is false for every dispatched Commander. Measured in this run, at
that exact step, with the spine on disk and no `SPINE_*` in the environment:

```
mcp__spine__spine_lease {action: heartbeat}  ->
REFUSED: no spine is bound to this door, so there is nothing for this tool to act
on. Call `spine_open` to mint a spine and bind this process to it, or relaunch this
door with SPINE_FILE set to an existing spine file.
```

Every door tool refuses identically, not just `spine_lease`.

## Why it is worth recording separately from the code defect

The imperative does not merely fail — it **teaches the agent something false about
its own situation** at the moment it has the least context to doubt it. An agent
that believes its door is bound will read the refusal as a broken door rather than
as an absent capability. Two agents in this epic reached for the CLI fallback here
and one (the Admiral) logged its own use of it as an `ADMIRAL ERROR`, which it was
not — it was the only available path.

There is a second, quieter problem. The refusal's two suggested remedies are both
wrong for this caller: `spine_open` **mints** (its own description says it "acts on
a spine that does not exist yet"), and "relaunch this door with `SPINE_FILE` set" is
not available to an agent that did not launch the door. So the refusal is
well-written for a case that is not the common one, and offers the common case no
route at all.

## Recommendation

Sequenced, because order matters here:

1. Land the binding verb (lane A's mission). Until then there is nothing true to
   say, and rewording the imperative would just relocate the falsehood.
2. Then change the `init` imperative from asserting the binding to **establishing**
   it: bind the door to this spine first, then claim. The imperative is currently
   the strongest single piece of evidence for why the verb is needed — every
   Commander is instructed to use a capability that does not exist.
3. Then widen `_unbound_refusal`'s remedy text to name the new verb, so the refusal
   routes the common case instead of only the mint case.

Step 3 is small and lands in `_HOW_TO_BIND` / `_HOW_TO_REBIND`
(`scripts/mcp_spine_server.py:383-390`), which are already factored out as named
constants for exactly this kind of edit.

## Not to be confused with

This is not the `<engine>` token sweep or the `CLI fallback` clause deletion (15
clauses across 11 files, 11 tokens across 7 files, both re-measured at `600de020`).
Those are wave 2 and are blocked behind the verb existing. This candidate is about
one imperative that states a false fact about the reader's own process.
