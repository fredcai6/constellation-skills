# Triage candidate — `docs/agents/CREW_CONTEXT.md` "Python Invocation" is stale

**Found at:** `g1-integrate`, lane D1, epic #567 wave 2. Reported **independently by both g1 crews**
— the implementer (out-of-scope observation 1) and the reviewer (`tc3`) — which is why it is worth
recording rather than shrugging off.

**What was found.** That section records, measured 2026-08-10, that `python3` has no pytest on this
host. Measured today (2026-08-17) by two crews separately: `py`, `python` **and** `python3` all
report pytest 9.1.1.

**Why it matters.** The section's own instruction is to re-run the check rather than trust the
recorded number, and both crews did, so nothing was harmed this run. But a crew that trusts the
recorded measurement instead of re-running it reaches the wrong conclusion about which interpreter
to use — and the whole point of writing a measurement down is that someone will eventually lean on
it. This is the general shape of `global-everyone.md`'s "pin a claim to the revision you read it
at": a measurement with a date but no re-measurement trigger decays silently.

**Why it is a candidate and not a fix.** `docs/agents/CREW_CONTEXT.md` is **lane D2's** file this
wave — explicitly fenced in the launch order's ownership table. This lane may not touch it.

**Disposition:** `recommend-and-defer`. Pair onto an open issue at epic closeout, or record as an
episode. **Not filed as an issue** — `decision:no-issue-filing-mid-run`.
