# Reviewer Handoff — g3: make the engine's spine write atomic

## Gate
`g3-review` (epic-567-door/cmdr-a, lane A of epic #567). This is #613's
**atomicity half** and only that half.

Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`
**The shell's working directory does not persist between tool calls** — use absolute
paths or a single `cd <abs> && ...`.

## Task statement (what the implementer was asked to do)

`checklist_engine.save()` (`scripts/checklist_engine.py:237`) ended in a bare
`Path(path).write_bytes(payload)`, which truncates then writes. A concurrent reader
could observe a partial spine; a crash mid-write could leave one permanently corrupt.
The implementer was asked to make the write atomic by mirroring the repo's own
existing pattern — temp file in the **same directory**, then `os.replace` — and to
change nothing else.

Read, in order:
1. `.agent-work/epic-567-door/cmdr-a/crew-handoffs/g3-implementer-handoff.md`
2. `.agent-work/epic-567-door/cmdr-a/crew-handoffs/g3-implement-implementer-result.md`

## How to inspect the diff

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
  git diff 3e4b0e20..HEAD -- scripts/checklist_engine.py tests/ && git status --short
```

New test files are **untracked until staged** — check `git status` too.

## Your primary job: prove the test actually discriminates

This gate's whole risk is a test that passes in both the healthy and the defective
world. `global-orchestrator.md`: *"A check whose output is identical in the healthy
and the defective world cannot discriminate, however correctly it runs."*

So the load-bearing thing you verify is the **red-proof**:

1. Confirm the new concurrency test **passes** against the new `save()`.
2. Then **revert `save()` in the worktree copy to the old bare `write_bytes`** and
   confirm the same test **fails**. Restore afterwards.

If you cannot make the test fail against the old implementation, the test does not
measure atomicity and the gate is **not** closeable, no matter how green it is. That
is a blocking finding, and it is the most likely real defect in this gate.

**The engine under edit is not the engine in play.** Break the **worktree** copy for
this proof. Never touch the installed copy under `/home/tommy/.claude/skills/` — this
session is running it, and corrupting it breaks live agents.

## Close criteria you are verifying

- A reader concurrent with a writer observes either the **complete old** document or
  the **complete new** one — never a partial one. Exercised, not asserted.
- The red-proof above.
- **No temp file survives**, on either the success or the failure path. Check by
  listing the directory after a save, and after a save forced to fail. A stray
  `spine.json.tmp` left in a work area is a real defect: the next reader may find it
  and the archive will carry it.
- **Line endings are preserved.** This is the behaviour most easily broken silently.
  `save()` calls `_dominant_newline(path)` (`:224`) which reads the **existing** file,
  so it must still be consulted **before** the original is replaced. Verify by
  measurement: write a CRLF-ending spine, save through the engine, assert the file is
  still CRLF. Then LF stays LF; a missing file and a mixed-ending file get LF.
  `save()`'s own docstring says one verb rewriting a whole file's endings "would
  destroy its blame" — that is the regression to hunt.
- `os.replace` is used with the temp file in the **same directory** as the target.
  Cross-filesystem `os.replace` is not atomic; if the temp goes to `/tmp` or
  `tempfile.gettempdir()`, that is a finding.
- The docstring carries the scope boundary in plain words (next section).

## The scope boundary — verify it is stated, and that it was not exceeded

**Atomic replace fixes torn reads and crash corruption. It does NOT fix lost
updates.** Two writers that each `load()` → mutate → `save()` still clobber each
other and leave a perfectly well-formed file with one update silently missing. That
read-modify-write race is #613's **other half** and is deliberately out of scope.

Two findings to check for, in opposite directions:

- **Under-stating it.** The docstring must say this. Without it, a future reader takes
  "save() is atomic" as "concurrent spine writes are safe", which is false — and
  after this change the remaining bug is *silent*, so the code no longer hints
  otherwise. The repo already uses this exact framing at
  `scripts/hooks/spine_rail.py:163` ("load-modify-save is atomic on the WRITE but not
  across the read-modify-write"), so the implementer had house language to match.
- **Exceeding it.** If the diff contains a lock, a compare-and-swap, a version or
  hash field, or retry logic in `load()`, the implementer took the other half
  uninvited. That is a scope finding even if the code is good — it changes the
  concurrency contract this lane was not authorized to change.

## Fenced regions — confirm untouched

- **`_RAIL_STRINGS` and `_refresh_attach_hint` in `scripts/checklist_engine.py` must
  be byte-identical.** They are owned by this lane but a follow-up lane (lane C, this
  same wave) needs their text intact — #442's RAIL banner and the HARD refusal
  remedy. Verify with a targeted diff, not by eye:
  ```bash
  cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
    git diff 600de020..HEAD -- scripts/checklist_engine.py | grep -n "RAIL_STRINGS\|_refresh_attach_hint"
  ```
  Any hit is a finding.
- **`scripts/mcp_spine_server.py` is out of scope for g3** — a parallel crew owns it
  for gate g2. If the g3 diff touches it, that is a scope finding.
- **`scripts/hooks/*` untouched.** The implementer was told to read
  `gauge_writer_hook.py` for the pattern and write nothing.

## The one sanctioned blast-radius edit

`tests/test_crew_launcher.py:3250` carries a docstring asserting
`checklist_engine.save` "writes plain bytes, non-atomically". This change falsifies
it, so correcting that one sentence is **in scope and expected**. The
`except (OSError, ValueError)` tolerance around it should **stay** — it becomes
unnecessary but harmless, and removing it is scope creep.

Confirm the implementer re-ran the enumeration rather than trusting the handoff's
number: `grep -rn` for atomicity claims across `scripts/ tests/ docs/ skills/` found
**13 files**, of which this is the **one** asserting something about
`checklist_engine.save` that the change makes false. If the implementer found a
second such artifact and fixed it, that is good; if it found one and *didn't*, that
is a finding.

## Required evidence from you

- The red-proof, both directions, pasted.
- The line-ending cases, by measurement.
- The temp-file check after success and after a forced failure.
- The fenced-region diff check.
- ```bash
  cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
    py -m pytest tests/test_checklist_engine.py tests/test_crew_launcher.py -q
  ```
  and the full suite:
  ```bash
  cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
    py -m pytest tests/ -q 2>&1 | tail -25
  ```
  Derive any failure distribution mechanically. Failures confined to `test_mcp_*.py`
  are probably the **parallel** g2 crew's — say so rather than attributing them here.

## Verdict

`APPROVE` or `BLOCK`, tied to specific evidence. Do not soften a `BLOCK` into an
approval with notes. Out-of-scope defects are **triage candidates** listed in your
result, not blockers and not yours to fix. **File no issues**
(`decision:no-issue-filing`).

Write `REVIEW_RESULT` to
`.agent-work/epic-567-door/cmdr-a/crew-handoffs/g3-review-review-result.md`
**before ending your turn** — that write is the delivery. Include a `Verdict:` line
whose value is exactly `APPROVE` or `BLOCK`, and a `Workflow Feedback` section.
