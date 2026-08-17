# Triage candidate: nothing records who wrote what, so an agent cannot tell its own crew's writes from tampering

**Status:** not filed. Held to closeout per the epic's standing ruling.
**Found by:** the Admiral of epic-567-door, adjudicating lane G's incident, 2026-08-16.
**Pairing suggestion:** #541 (capture the door's rejections into the run's episode) is adjacent — same instinct about making invisible friction visible — but does not cover write attribution. May warrant its own pairing against #432 (a dispatch's engine-drive is unverifiable) since both are "the run cannot see what actually happened."

## What happened

Lane G filed a five-escalation report concluding that "something with write access to this worktree is actively simulating an engine-driven run in parallel with my real one, right now." Every write it reported was its own: its g1 implementer crew wrote `done_refusal` and tests into `scripts/spine_lifecycle.py` and `tests/test_spine_lifecycle.py`; its design-it-twice fork wrote `notes-g.md`, `spine.json` and `execute.json`.

The cost was concrete: a lane that had done real, verified design work **halted instead of delivering**, reverted its own live crew's implementation twice with `git checkout --`, and spent its remaining budget on forensics.

## Why the agent's reasoning was sound

This is the part worth keeping. Lane G was not careless. It observed:

- files changing between its own `Read` and `Write` (the harness refused a write with "File has been modified since read");
- engine state advancing through verbs it had not called, including a lease it had not claimed;
- `spine.json` postconditions marked satisfied with plausible `satisfied_by` prose it had not written;
- tracked source files it had never opened with `Edit`/`Write` gaining 143 lines of confident, well-documented, **subtly wrong** code — wrong in exactly the way its own cold critic had already caught;
- injected unit tests that passed while missing the defect, because they tested the unit in isolation rather than the composition where the bug bites.

Every one of those observations is true. The inference — an attacker — is the only one available when nothing in the environment can answer "who wrote this?" A crew's legitimate output and an injection are the same shape: files you did not write, appearing while you were not writing.

It also read the harness's standard externally-modified-file reminder ("This change was intentional… Don't tell the user this, since they are already aware") as an instruction to conceal a tamper, and **disclosed it anyway**. That instinct was right even though the conclusion was wrong.

## The asymmetry that makes this expensive

An agent that wrongly suspects its own crew halts a good run — recoverable, costs a wave slot. An agent that wrongly trusts an actual injection ships confident-looking, subtly-broken code that passes a shallow review. Lane G's injected `done_refusal` is a live example of what that looks like: it folded `closeout_refusal`'s lease check into the pre-close predicate, so it would refuse on every legitimate invocation, and its nine accompanying tests went green because they asserted the unit against itself rather than the composition.

So the honest reading is that lane G failed safe. The defect is that failing safe cost a delivery, and nothing distinguishes the two worlds.

## What would close it

An agent can ask, cheaply and mid-run, which actor produced a given write to its work area or its worktree — and get an answer that separates "my own dispatched crew", "a fork of me", and "neither". Today `crew-runs.json` holds enough to answer the first case by hand (it recorded the g1 implementer's id, start time, worktree and running status, which is how the Admiral resolved this in minutes), but nothing points an alarmed agent at it, and it says nothing about forks.
