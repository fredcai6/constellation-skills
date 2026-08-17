# Implementer Handoff — g3: make the engine's spine write atomic

## Gate
`g3-implement` (epic-567-door/cmdr-a, lane A of epic #567). This is #613's
**atomicity half**.

Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`
Branch: `feat/567-a-spine-identity`. Use absolute paths — **the shell's working
directory does not persist between tool calls in this harness.**

## Task

`checklist_engine.save()` (`scripts/checklist_engine.py:237`) ends in a bare
`Path(path).write_bytes(payload)`. `write_bytes` opens with `O_TRUNC` then writes,
so:

- a reader concurrent with a writer can observe a **truncated or partial** spine and
  get a `JSONDecodeError` on state that is valid on disk;
- a crash between the truncate and the completed write leaves the spine
  **permanently corrupt** — and the spine is the only record that the work happened.

Spines are large enough for this to be real, not theoretical: a live commander spine
in this repo is ~35KB, far past any single-write atomicity.

Make the write atomic.

**This is not a theoretical defect. The repo's own test suite already documents it
and works around it.** `tests/test_crew_launcher.py:3250`, inside `_wait_until`'s
docstring, reads:

> "A transient exception (the predicate reads the SAME spine file the heartbeat
> thread is mid-write to — `checklist_engine.save` writes plain bytes,
> non-atomically) is treated as 'not yet', not a failure"

That is a written record of a torn read observed in practice, in the
parent-heartbeat test — which is #613's exact scenario.

## Protected Intent

- **The write is specified below, exactly. An earlier draft of this handoff told you
  to mirror `scripts/hooks/gauge_writer_hook.py:513` `_atomic_write_json`. Do NOT do
  that — that pattern is defective for this use and a cold critic caught it.**

  `_atomic_write_json` uses a **fixed** temp name, `path.with_name(path.name + ".tmp")`
  — one temp path per target. With two concurrent writers of one spine (which
  `run_crew.py`'s `_parent_lease_heartbeat` daemon thread makes a **supported** case,
  see `tests/test_crew_launcher.py:3211-3225` "the shared-spine case"), both writers
  open the *same* temp path. The loser's file handle then still points at the inode
  `os.replace` just installed as the live spine, so its buffered flush writes
  **directly into the live target after the rename**. Measured by the critic:

  ```
  installed: b'{"a": "S"}LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"}'
  parses: NO -> JSONDecodeError Extra data: line 1 column 11 (char 10)
  errors: ["FileNotFoundError: ... 'probe2.json.tmp' -> 'probe2.json'"]
  ```

  That is **worse than the bug we are fixing**: today's tear is transient and the
  next successful write heals it, whereas an installed unparseable document is
  permanent. The loser's `os.replace` also raises `FileNotFoundError`, which
  `save()`'s callers have never had to handle.

  **Write it this way instead:**

  1. `tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")` — a
     **unique** temp name per writer, in the **same directory** (`os.replace` is only
     atomic within one filesystem).
  2. Write the payload to that fd.
  3. When the target already exists, `os.fchmod` the temp to the target's current
     mode — a fresh `mkstemp` file is `0600` and a bare rename would silently change
     the spine's permissions.
  4. `f.flush()` then `os.fsync(fd)` **before** the rename. Without this the rename
     can be durable before the data is, so the "survives a crash" half of the claim
     is not actually delivered.
  5. `os.replace(tmp, path)`.
  6. Unlink the temp in a `finally` so no `.tmp` survives a failure.

  Report the fixed-name hazard in `gauge_writer_hook.py` as a **triage candidate** in
  your result — it is the same bug there, in a file you must not edit.
- **`save()`'s existing line-ending behaviour is preserved exactly.** `save` calls
  `_dominant_newline(path)` (`:224`) to preserve CRLF files, and that function reads
  the **existing** file. It must therefore still be consulted **before** the original
  is replaced. Getting this wrong silently rewrites every line ending in a CRLF
  file — which is the precise defect `save()`'s current docstring says it exists to
  prevent ("One engine verb would then rewrite a whole file's endings and destroy
  its blame").
- **The temp file must not survive a failure**, and must not survive the success
  path either.
- **Scope boundary, and it must appear in the docstring you write.** Atomic replace
  fixes **torn reads and crash corruption**. It does **not** fix **lost updates**:
  two writers that each `load()` → mutate → `save()` still clobber each other and
  leave a perfectly well-formed file with one update silently missing. That
  read-modify-write race is #613's **other half** (the parent heartbeat as a second
  concurrent writer) and is **out of scope here**.

  Say so in the docstring in plain words. The reason is not pedantry: after this
  change the failure mode stops being noisy, so anyone reading "save() atomicity
  fixed" as "concurrent spine writes are safe" will be wrong in a way the code no
  longer helps them notice. The repo already states the distinction in these words
  at `scripts/hooks/spine_rail.py:163` — "load-modify-save is atomic on the WRITE but
  not across the read-modify-write" — so you are matching existing house language,
  not inventing a caveat.

## Test Mode

**TDD required, and the test must be proven non-vacuous.**

A test that passes against **both** the old and the new implementation is a check
that cannot fail. You must show the new test **failing against the old
`write_bytes` implementation** — the red-proof — and then passing against the new
one. Paste both runs.

### The test must be DETERMINISTIC, not a thread race

A cold critic raised this and it is right: a threaded race against the old
`write_bytes` is **timing-dependent**, so it can come out green against the old
implementation by luck and thereby **fake its own red-proof**. A flaky red is not a
red.

So make the primary assertion mechanical:

- **Assert `save()` never opens the target path for writing** — only a temp sibling.
  Patch or wrap `builtins.open` / `os.open` for the duration of one `save()` call,
  collect the paths opened for writing, and assert the target is not among them.
  This fails cleanly and deterministically against the old code, which opens the
  target directly.
- **Assert the target's inode changes exactly once** across a save (`os.stat().st_ino`
  before and after). A rename swaps the inode; an in-place write does not. Also
  deterministic.
- **Assert no `*.tmp` sibling remains** after success and after a forced failure.

A concurrency test is still welcome **in addition** — two writers, then assert the
installed document always parses — but it is the *supporting* evidence, not the
load-bearing check. Say clearly in your result which assertions are deterministic
and which are racy.

The engine under edit is not the engine in play: **break the worktree copy** to get
the red-proof (revert it after), and never modify the installed copy at
`/home/tommy/.claude/skills/`.

## Close Criteria

- A reader concurrent with a writer observes either the **complete old** document or
  the **complete new** one, never a partial one. Exercised, not asserted.
- That test **fails** against the old implementation. Red-proof pasted.
- No temp file remains after a successful save, and none remains after a failed one.
- An existing CRLF-ending spine keeps CRLF endings after a save. An LF file keeps
  LF. A missing file and a mixed-ending file get LF, as today.
- The docstring carries the atomicity-is-not-mutual-exclusion boundary.
- `tests/test_checklist_engine.py` and `tests/test_crew_launcher.py` both green.

## Allowed Scope

- `scripts/checklist_engine.py` — the `save()` function and its docstring, plus a
  small private helper if the pattern reads better factored out.
- A **new** test module, e.g. `tests/test_checklist_engine_atomic_save.py`.
- `tests/test_crew_launcher.py:3250` — **one docstring correction only.** That
  comment asserts `save` "writes plain bytes, non-atomically", which your change
  falsifies. Correct the sentence; leave the `except (OSError, ValueError)`
  tolerance in place (it becomes unnecessary but stays harmless, and removing it is
  scope creep). This is the blast-radius fix: the Commander enumerated by command
  (`grep -rn` for atomicity claims across `scripts/ tests/ docs/ skills/` → 13
  files) and this is the **one** artifact asserting something about
  `checklist_engine.save` that your change makes false. Re-run that grep to confirm
  the count yourself.

## Specific Exclusions

- **`scripts/mcp_spine_server.py` — owned by gate `g2` this same wave (#559). Do not
  touch it.** Another crew is editing it in parallel.
- **`scripts/hooks/*` — out of scope for the whole lane (#567 lane A).** Read
  `gauge_writer_hook.py` and `spine_rail.py` for the pattern and the house wording;
  **write nothing** to either. Hooks execute from the main checkout for every live
  session, so editing them can break other running agents.
- **`_RAIL_STRINGS` and `_refresh_attach_hint` in `scripts/checklist_engine.py` are
  FENCED.** They are formally owned by this lane but a follow-up lane (lane C, this
  same wave) needs their text intact — specifically #442's RAIL banner in
  `_RAIL_STRINGS` and the HARD refusal remedy in `_refresh_attach_hint`. Do not
  rewrite them and do not gratuitously reformat them.
- **Do not attempt the lost-update / read-modify-write half.** No compare-and-swap,
  no locking, no version field. That is #613's other half and is deliberately not
  yours. If you think it is trivial to add, that is a stop condition and a
  triage-candidate note, not a licence.
- `load()` (`:220`) needs no change. A reader that gets a complete document is the
  whole point; do not add retry logic to compensate for a bug you just fixed.

## Constraints

- `save()` keeps its exact signature `save(path: Path, data: dict) -> None`. It has
  3 call sites inside `checklist_engine.py` and one external caller
  (`scripts/run_crew.py:1433`, paired with a `load` at `:1431` — that pair *is* the
  #613 parent-heartbeat second writer). None of them may need to change.
- No new third-party dependency. `os.replace` is stdlib.
- Keep the change small. This is ten-ish lines of implementation; if it is growing,
  stop and report.

## Map Anchors (inbound)

- **Map entry point:** none — map orientation is `DEGRADED-UNPARSEABLE` repo-wide
  (`map/ids.jsonl` tracked and 0 bytes). Start from
  `.agent-work/epic-567-door/cmdr-a/MISSION_FRAME.md` and this handoff. There is no
  map packet to find.
- **Structural:** `scripts/checklist_engine.py` — `save`(:237), `load`(:220),
  `_dominant_newline`(:224). Pattern source: `scripts/hooks/gauge_writer_hook.py`
  `_atomic_write_json`(:513). House wording source:
  `scripts/hooks/spine_rail.py`(:163).
- **Capability:** spine-state-persistence — the only read/write path for spine state.
- **Constraints/assumptions:** `constraint:rail-strings-untouched`;
  `constraint:no-hooks`; `assumption:engine-under-edit-is-not-engine-in-play`.
- **Decision anchors:**
  - `decision:atomicity-is-not-mutual-exclusion` — atomic replace fixes torn reads and crash corruption, not lost updates; the run says so out loud.
    `@grade: settled/measured · leans g3-implement,g3-review · settle: two writers each load-mutate-save a copy; observe a well-formed file with one update missing`
  - `decision:in-session-observation-is-not-evidence` — validate in a fresh process with explicit paths (#269).
    `@grade: settled/project · leans g3-implement`
- **Evidence expectations:** the concurrent-reader test plus its red-proof.
- **Map confidence flags:** whole map degraded; trust code and tests only.

## Deliverable Path Check

- **Committed** — `scripts/checklist_engine.py`, `tests/test_crew_launcher.py`, and
  your new test module. `git check-ignore` on each exits 1 (not ignored); verified
  before dispatch.
- **Committed** — your `IMPLEMENTER_RESULT` under
  `.agent-work/epic-567-door/cmdr-a/crew-handoffs/`. Note: **`.agent-work/` is NOT
  gitignored in this repo** — `git check-ignore .agent-work/x` exits 1. Measured, not
  assumed; the Commander's first draft of this handoff asserted it was ignored and
  that was wrong. Your result file will appear in the diff.
- The new test module is untracked until staged: it appears in `git status`, not in
  `git diff`.

## Required Evidence

**Load-bearing — prove rigorously:**

1. The concurrent-reader test passing against the new `save()`.
2. The **red-proof**: the same test failing against the old `write_bytes`
   implementation. Paste the failure.
3. The CRLF-preservation case, since that is the behaviour easiest to break silently.

**Confirmatory — spot-check:** no leftover temp files; `tests/test_checklist_engine.py`
and `tests/test_crew_launcher.py` green; the re-run of the atomicity-claim grep and
its count.

Derive any claimed failure distribution mechanically
(`pytest -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c`), never from a
glance at the output tail.

## Wiring Grep

If you factor out a helper, show it is actually called:

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
grep -rn "_atomic_replace\|_write_atomic" --include=*.py scripts/ tests/ \
  | grep -v "def _atomic_replace" | grep -v "def _write_atomic"
```

**State the count.** Zero external call sites is a stop condition. If you keep the
change inline inside `save()` with no new symbol, write `none — no new callable
symbol; the change is inline in save()` and that is a complete answer.

## Verification Commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
  py -m pytest tests/test_checklist_engine.py tests/test_crew_launcher.py -q
```

Your new module, and the whole suite for fan-out:

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
  py -m pytest tests/ -q 2>&1 | tail -25
```

A red result in the **door/identity** suites (`test_mcp_*.py`) is probably **not
yours** — a parallel crew is editing `scripts/mcp_spine_server.py` for gate g2.
Report it, do not fix it.

## Suggested Model Tier

**Simple bounded** — the change is small and the pattern is already in the repo. The
rigor is in the test, not the implementation.

## Authority

- The pattern is decided: temp-file-plus-`os.replace`, mirroring
  `gauge_writer_hook.py:513`. Do not substitute a different mechanism.
- The scope boundary is decided: atomicity only, not the lost-update half. The
  launch order scopes this lane to "the atomicity half" and that is not yours to
  widen.

**You must not decide alone:** adding any locking or compare-and-swap; changing
`save()`'s signature; touching `_RAIL_STRINGS` or `_refresh_attach_hint`; editing
anything under `scripts/hooks/`.

## Stop Conditions

Stop and return with what you have if: the atomic replace cannot preserve the
line-ending behaviour without restructuring `save()` substantially; `os.replace`
turns out not to be usable for a real case here; the red-proof cannot be
constructed (that would mean the test does not discriminate, which is a finding);
or the change starts growing past ~20 lines. A measured negative is a complete
deliverable.

## Return Format

Write `IMPLEMENTER_RESULT` to
`.agent-work/epic-567-door/cmdr-a/crew-handoffs/g3-implement-implementer-result.md`
**before ending your turn** — that write is the delivery. Include a
`Return status:` line whose value is exactly `complete` (lowercase) when the close
criteria are met, and a `Workflow Feedback` section on how the run went.
