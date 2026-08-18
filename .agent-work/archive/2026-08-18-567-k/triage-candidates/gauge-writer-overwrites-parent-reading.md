# Triage candidate — the context-gauge writer wrote a child's reading into its parent's gauge file

**Not filed.** `decision:no-issue-filing-mid-run` — staged only.

## Observed, this run

`.agent-work/epic-567-door/gauge-constellation-epic-567-door-470f957c39f5.json` changed under me
without my ever writing it:

```
-{"fill_fraction": 0.122268, "model": "claude-sonnet-5", "observed_at": "2026-08-18T01:18:14.792Z",
  "owner": "constellation-epic-567-door-470f957c39f5"}
+{"fill_fraction": 0.048478, "model": "claude-opus-5",  "observed_at": "2026-08-18T04:46:29.458Z",
  "owner": "constellation-epic-567-door-470f957c39f5"}
```

`claude-opus-5` at 4.8% is **this lane-K session**, not the Admiral. The writer resolved the owner
to the epic (this session carries `SPINE_PARENT=constellation/epic-567-door`) and overwrote the
Admiral's own reading with a child's.

## Why it matters

The gauge is what drives trip advisories and the HARD-band refusal of `start`/`reopen`. A parent
whose gauge file is being overwritten by whichever child ran most recently is being advised on
someone else's context. The failure is silent in both directions: the Admiral reads a low fill and
never trips; a child could equally write a high one and trip a parent that is fine.

## Its likely sibling, seen the same run

The engine also reported, repeatedly:

```
CONTEXT GAUGE SILENT: this session is bound to 2 candidate spines at once, so the writer hook
could not tell which one a reading belongs to and wrote nothing rather than guess
```

So the writer has **two** behaviours for the same ambiguity — refuse to write, and write to the
parent anyway. Both were observed in this one session. Whichever is correct, they disagree.

## Disposition

`recommend-and-defer`. Out of lane K's scope (#634 is the bookend freeze) and its fix likely
touches gauge/hook code, not `amend`. Reverted the file with `git checkout --` so this branch does
not carry a corrupted reading of the Admiral's context; the hook may rewrite it, and if the branch
shows it again the revert is not the fix — the writer is.

## Not claimed

I did not read the gauge writer's source or determine which hook wrote it. This is an observation
with a diff, not a diagnosis.
