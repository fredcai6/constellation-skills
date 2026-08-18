# Triage candidate — the crew recovery registry loses entries under concurrent dispatch

**Not filed.** `decision:no-issue-filing-mid-run` — staged only.
**Owner note: `scripts/run_crew.py` is lane J's this wave.** I did not touch it and am not
proposing that this lane touch it.

## Observation — measured, this run, rev `9b38b9d9`

I dispatched three design-candidate crews in one shell loop, backgrounded within the same second:

```sh
for n in A B C; do nohup ... py scripts/run_crew.py --gate g0-design-$n ... & done
```

All three **ran to completion**. All three wrote their results:

```
.agent-work/567-k/crew-handoffs/design-A-result.md
.agent-work/567-k/crew-handoffs/design-B-result.md
.agent-work/567-k/crew-handoffs/design-C-result.md
```

All three have captured output in the registry's own directory:

```
.agent-work/567-k/crew-runs/g0-design-A-design-candidate-attempt-1.{stdout,stderr}.txt
.agent-work/567-k/crew-runs/g0-design-B-design-candidate-attempt-1.{stdout,stderr}.txt
.agent-work/567-k/crew-runs/g0-design-C-design-candidate-attempt-1.{stdout,stderr}.txt
```

**But only `design-A` has a registry entry.** `recover_crews.py 567-k` reports 7 crews and never
mentions B or C. Expected: 9 crews, all three design candidates among them.

`type`: **measured** — by listing the registry against the stdout files and the results on disk,
and by running `recover_crews.py` and reading its output.

## Why it matters

`crew-runs.json` is described in `references/crew-dispatch.md` as the **durable recovery
registry**, written "before the crew starts", and `recover_crews.py`'s stated purpose is that a
relaunched Commander discovers an already-complete crew "purely from the durable registry and
result artifact, with zero dependency on which Commander instance is asking."

Under concurrent dispatch that guarantee does not hold. The shape is a read-modify-write race on a
single JSON file: each `run_crew.py` reads the array, appends its entry, and writes it back, so
near-simultaneous launches overwrite each other and the last writer wins.

The failure is **silent and in the dangerous direction**: the registry under-reports. A relaunched
Commander running `recover_crews.py` — exactly as doctrine instructs, before each dispatch — would
be told B and C never ran and would redispatch them, duplicating work whose results were already
on disk. That is precisely the failure the registry exists to prevent, and it looks clean while
doing it.

It also means my own compliance this run was weaker than it appeared: I ran `recover_crews.py`
before every dispatch, as required, against a registry that was already missing two entries.

## Possible fix (hypothesis, not a spec)

Make the append atomic — a lock file, or write-new-then-rename with a retry on the compare — the
way `checklist_engine.save()` already installs its document by atomic rename
(`tests/test_checklist_engine_atomic_save.py` exists for exactly this concern on the spine). The
engine solved this problem for its own state file; the crew registry did not inherit the solution.

## Open questions

- Does the same race hit two Commanders in different worktrees sharing one `--work-id`? I did not
  test that.
- Does `--abandon`/`--relaunch` compound it by rewriting the array from a stale read?

## Disposition

`recommend-and-defer`. Fails the fix-now ladder on **adjacent to current scope**: `run_crew.py` is
fenced to lane J this wave, and a concurrency fix to the dispatch layer is not a bounded diff
adjacent to a bookend-freeze change. **Worth routing to lane J's owner rather than to a backlog**,
since lane J already has that file open.

## Not claimed

I did not read `run_crew.py`'s registry-write code. The read-modify-write race is the obvious
explanation for the evidence and is stated as a hypothesis, not a diagnosis. What is measured is
the absence of the entries, not the mechanism that lost them.
