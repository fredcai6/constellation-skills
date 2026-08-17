# Triage candidate: record WHO wrote each spine journal entry

- **Disposition:** `recommend-and-defer`. Not filed as an issue
  (`decision:no-issue-filing`). Not implemented — outside lane A's scope.
- **Raised by:** `cmdr-567-a`, epic #567 lane A, at `600de020`.
- **Severity:** high. This is the actual fix for a defect that cost a lane its run
  this wave.

## The observation

Lane G reported its worktree "actively compromised" with fabricated engine state.
It was not compromised. The writes were its own `g1` implementer crew plus its own
design-it-twice **fork**. A fork inherits the parent's entire context, so it
believed it *was* the Commander and drove the Commander's own `spine.json` under
the identical lease id.

The lane then spent its remaining budget investigating an attack that had not
happened, and could not complete its mission.

## Why the existing mechanisms did not catch it

Each of the three defences that look like they should have applied did not, and for
a different reason:

- **The lease did not help.** Both writers presented the same `session_id`, so
  every mutating verb was correctly authorized. A lease answers "is *a* session
  driving this spine"; it cannot answer "is this the same *agent* as last time."
  `docs/agents/GLOSSARY.md` states the intended property as "so a second agent
  cannot drive the same spine" — under a shared session id that property does not
  hold, and the glossary overstates what a lease buys.
- **Atomic `save()` will not help,** including after lane A's fix. Both writers
  produced well-formed JSON. The damage was a lost update plus journal entries
  nobody could attribute. Atomicity is about torn bytes, not about authorship.
- **Nothing records authorship at all.** This is the root. The journal says what
  happened and when; it does not say which process did it.

## Why it matters beyond one lane

An agent that cannot distinguish its own crew's writes from an attacker's has only
two available conclusions, and both are wrong: trust everything, or treat a
correct-looking spine as compromised. Lane G took the second, which is the safer
error and still cost the lane. The failure is not that the spine was damaged — it
is that **the damage was uninterpretable.**

This is also the same class as two other incidents in this epic's recent history:
`HEAD~4` is `chore(609): restore lane F's clobbered crew registry from git history`,
and lane A's own assigned `notes-a.md` was a tracked artifact of an earlier lane
which the current lane clobbered on first write (recovered, zero lines lost). In all
three, a writer held legitimate authority to write and had no way to know what was
already there. **Authority to write is not knowledge of what is there.**

## Recommendation

Record a writer identity on each journal entry the engine appends — enough to
distinguish two processes sharing one session id. The cheapest discriminator that
would have separated lane G's two writers is a per-process token (pid plus process
start time, or a uuid minted at door/engine startup), stamped beside the existing
session id rather than replacing it.

Then the useful diagnostic becomes possible: "this spine was driven by two distinct
processes under one session id", which is a statement a lane can act on in seconds
instead of hours.

## Explicitly NOT recommended here

Do not fix this by making the lease stricter — refusing a second writer under the
same session id would break the legitimate same-id re-claim that
`global-everyone.md` documents as free recovery after an idle gap. The problem is
observability, not permission. Solve it where it actually is.

## Related

- #613's lost-update half (the parent heartbeat as a second concurrent writer) is
  the same race with a different second writer. Lane A fixed only the atomicity
  half and says so.
- The context-inheriting fork is worth its own note: `subagent_type: "fork"`
  inherits the parent's context including its identity, which is what made the fork
  believe it was the Commander. Lane A deliberately used fresh general-purpose
  agents with explicit "you have no spine" prohibitions for its own design panel
  because of this report.
