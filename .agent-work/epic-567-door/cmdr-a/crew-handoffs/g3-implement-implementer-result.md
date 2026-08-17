# Implementation Result — g3-implement: make `checklist_engine.save()` write atomically

Return status: complete

## Assigned gate

`g3-implement` (epic-567-door / cmdr-a, lane A of epic #567) — #613's **atomicity
half**.

## Completed slice

`checklist_engine.save()` no longer writes over the live spine. It writes a **unique**
temp sibling, `fchmod`s it to the target's existing mode, `fsync`s it, `os.replace`s it
into place, and unlinks the temp in a `finally`. Line-ending preservation is unchanged:
`_dominant_newline(path)` is still read **before** anything replaces the original.

## Scope

**Files changed:**

- `scripts/checklist_engine.py` — `import tempfile`; `save()` body and docstring. No
  other function touched.
- `tests/test_checklist_engine_atomic_save.py` — **new** module, 11 tests.
- `tests/test_crew_launcher.py` — the one docstring sentence at `:3250`. The
  `except (OSError, ValueError)` tolerance is left in place, as instructed.

**Specific exclusions touched:** no.

- `scripts/mcp_spine_server.py` — untouched (g2's).
- `scripts/hooks/*` — **read only** (`gauge_writer_hook.py`, `spine_rail.py`); nothing
  written.
- `_RAIL_STRINGS` / `_refresh_attach_hint` — untouched, not reformatted.
- `load()` — unchanged; no retry logic added.
- No locking, no compare-and-swap, no version field. The lost-update half is not
  attempted.
- `save()` keeps its exact signature; all four call sites are unchanged.

## Behavior changed

Yes. A reader concurrent with a writer now observes either the complete old document or
the complete new one. A crash mid-write can no longer leave a corrupt spine, because the
target is never in a partially-written state. Two other observable properties are held
constant on purpose: the file's line endings and its permission bits.

## The implementation

```python
path = Path(path)
payload = (json.dumps(data, indent=2) + "\n").encode("utf-8")
# Read the EXISTING file's endings and mode BEFORE anything replaces it.
eol = _dominant_newline(path)
if eol != b"\n":
    payload = payload.replace(b"\n", eol)
try:
    mode = path.stat().st_mode & 0o7777
except OSError:
    mode = None  # new file: keep whatever mkstemp's 0600 gives it
fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp",
                                dir=str(path.parent))
try:
    with os.fdopen(fd, "wb") as f:
        if mode is not None:
            os.fchmod(f.fileno(), mode)  # mkstemp makes 0600; don't narrow it
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_name, path)
    tmp_name = None
finally:
    if tmp_name is not None:  # a failure anywhere above leaves no .tmp behind
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
```

Each step is the handoff's, in the handoff's order. **It came out at 23 lines of body,
not "ten-ish".** The stop condition names ~20 lines, so this is worth saying out loud
rather than burying: the excess is entirely the `finally` unlink block and the mode
lookup, both of which the handoff mandates by name. Nothing speculative was added. I did
not treat 23 vs 20 as a stop, because the growth is not design drift — but the Commander
should know the estimate was low for the pattern it specified.

The docstring carries the boundary in house words:

> **Atomicity here is not mutual exclusion.** The WRITE is atomic; the read-modify-write
> is not. Two callers that each `load()` → mutate → `save()` still clobber each other,
> and the loser's update goes missing from a file that is perfectly well-formed — so
> nothing raises and nothing notices. Guarding that is a separate job (locking or
> compare-and-swap) and is deliberately not done here; see
> `scripts/hooks/spine_rail.py`'s binding-store transaction for the same distinction
> drawn in the same words.

## Test mode

**Required:** test-first, with a proven-non-vacuous red.
**Satisfied:** yes. The new module was written and run to red **before** `save()` was
touched, so the red-proof is against the genuine unmodified `write_bytes` implementation
at `HEAD` — I never had to break and restore anything, and the installed engine at
`/home/tommy/.claude/skills/` was never modified.

### Which assertions are deterministic and which are racy

**Deterministic (load-bearing).** These fail cleanly against the old implementation
every time, with no timing involved:

| Test | Mechanism |
|---|---|
| `test_save_never_opens_target_for_writing` | wraps `io.open` **and** `os.open`, collects every path opened in a write mode, asserts the target is not among them |
| `test_save_writes_a_temp_sibling_in_the_same_directory` | the recorded temp path's dirname equals the target's dirname (`os.replace` is only atomic within one filesystem) |
| `test_target_inode_is_replaced_exactly_once` | `st_ino` before ≠ after, **and** `os.replace` is counted so "exactly once" is measured, not inferred |
| `test_no_temp_sibling_after_a_failed_replace` | forces `os.replace` to raise, asserts no `.tmp` survives and the previous document is byte-identical |
| `test_no_temp_sibling_after_success` | directory listing after two saves |
| `test_existing_file_mode_is_preserved` | `chmod 0640`, save, mode still `0640` |
| the four line-ending tests | byte counts of `\r\n` vs bare `\n` |

Both doors are wrapped on purpose: `Path.write_bytes` reaches the target through
`io.open` (what `pathlib.Path.open` calls), while `tempfile.mkstemp` reaches its temp
through `os.open`. Wrapping only one would let the other slip past unseen.

**Racy (supporting only).** `test_concurrent_reader_never_observes_a_partial_document` —
2 writer threads alternating a ~90KB and an empty payload against 3 reader threads for
1.5s. It **exercises** the close criterion rather than asserting it, and it did catch
real torn reads against the old code (below), but a thread race can come out green
against broken code by luck, so it is deliberately not what discriminates. Tests 1–3 are.

## TDD evidence — the red-proof

Against the unmodified `write_bytes` implementation, before any edit to
`scripts/checklist_engine.py`:

```
$ cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
    py -m pytest tests/test_checklist_engine_atomic_save.py -q

>       self.assertNotIn(
            _real(self.path), rec.write_paths,
            "save() opened the live spine for writing; a concurrent reader can "
            f"observe a truncated document. write-opened: {rec.write_paths}",
        )
E       AssertionError: '/tmp/tmpisy51de1/spine.json' unexpectedly found in
        ['/tmp/tmpisy51de1/spine.json'] : save() opened the live spine for writing;
        a concurrent reader can observe a truncated document.
        write-opened: ['/tmp/tmpisy51de1/spine.json']
tests/test_checklist_engine_atomic_save.py:124: AssertionError

>       self.assertTrue(written, "save() wrote no temp file")
E       AssertionError: [] is not true : save() wrote no temp file
tests/test_checklist_engine_atomic_save.py:139: AssertionError

>       self.assertNotEqual(before, after,
                            "the target's inode did not change: the document was "
                            "written in place, not atomically renamed into place")
E       AssertionError: 5641419 == 5641419 : the target's inode did not change: the
        document was written in place, not atomically renamed into place
tests/test_checklist_engine_atomic_save.py:158: AssertionError

>       self.assertEqual(errors, [])
E       AssertionError: Lists differ: ['TORN READ: Expecting value: line 1 colum[121 chars] 0)'] != []
E         - ['TORN READ: Expecting value: line 1 column 1 (char 0)',
E         -  'TORN READ: Expecting value: line 1 column 1 (char 0)',
E         -  'TORN READ: Expecting value: line 1 column 1 (char 0)']
tests/test_checklist_engine_atomic_save.py:286: AssertionError

=========================== short test summary info ============================
FAILED tests/test_checklist_engine_atomic_save.py::AtomicSaveTests::test_concurrent_reader_never_observes_a_partial_document
FAILED tests/test_checklist_engine_atomic_save.py::AtomicSaveTests::test_no_temp_sibling_after_a_failed_replace
FAILED tests/test_checklist_engine_atomic_save.py::AtomicSaveTests::test_save_never_opens_target_for_writing
FAILED tests/test_checklist_engine_atomic_save.py::AtomicSaveTests::test_save_writes_a_temp_sibling_in_the_same_directory
FAILED tests/test_checklist_engine_atomic_save.py::AtomicSaveTests::test_target_inode_is_replaced_exactly_once
5 failed, 6 passed in 1.55s
```

Note what the last failure is: **all three reader threads got a `JSONDecodeError` at
char 0** — the empty-file window inside `write_bytes`'s `O_TRUNC`. The defect is
observed, not argued.

The 6 that passed against the old code are the line-ending cases and the mode case,
which the old implementation already got right. That is the correct outcome: they are
regression guards for behaviour that must **survive** the change, not discriminators.

### Green

```
$ cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
    py -m pytest tests/test_checklist_engine_atomic_save.py -q
...........                                                              [100%]
11 passed in 1.63s
```

Refactor while green: no.

## Line-ending evidence

The behaviour easiest to break silently, checked in a **fresh process** with explicit
absolute paths (`decision:in-session-observation-is-not-evidence`, #269) rather than only
inside the test runner:

```
$ py <fresh-process probe importing scripts/checklist_engine.py by absolute path>
crlf     CRLF=  8 bareLF=  0 eol=CRLF parses=YES inode_changed=True mode=0o640->0o640 leftover_tmp=[]
lf       CRLF=  0 bareLF=  8 eol=LF   parses=YES inode_changed=True mode=0o640->0o640 leftover_tmp=[]
mixed    CRLF=  0 bareLF=  8 eol=LF   parses=YES inode_changed=True mode=0o640->0o640 leftover_tmp=[]
missing  CRLF=  0 bareLF=  8 eol=LF   parses=YES inode_changed=n/a  mode=new->0o600  leftover_tmp=[]
```

Every close criterion for endings holds: **CRLF stays CRLF with zero bare LFs**, LF stays
LF, and missing and mixed both get LF, exactly as before. `inode_changed=True` on the same
line proves the rename really happened — the endings survive *through* the replace, which
is the thing that could have silently regressed. Mode is preserved; a brand-new file gets
`mkstemp`'s `0600`, which is the same "no existing mode to preserve" case as before.

## Wiring grep

```
$ grep -rn "_atomic_replace\|_write_atomic" --include=*.py scripts/ tests/ \
    | grep -v "def _atomic_replace" | grep -v "def _write_atomic"
0
```

`none — no new callable symbol; the change is inline in save()`. Factoring it out would
have created a one-caller helper for no reader benefit.

## Blast-radius grep — re-run, and the count reproduces

The handoff said the Commander found **13 files**. I re-ran the enumeration at `HEAD`
before my change:

```
$ git grep -lni 'atomic' HEAD -- scripts/ tests/ docs/ skills/
17 files
$ ... excluding docs/explainer-demo/*.html
13
```

**13 — the Commander's count reproduces exactly**, once the 4 generated
`docs/explainer-demo/*.html` pages are excluded. Those four are demo output about an
unrelated physics/evo-predictor codebase and match on the word "atomic" only
incidentally; the Commander evidently excluded them the same way. Reporting both numbers
so the filter is visible rather than implied.

Of the 13, exactly one asserts something about `checklist_engine.save` that this change
makes false:

```
$ git grep -n 'checklist_engine\.save' HEAD -- scripts/ tests/ docs/ skills/ \
    | grep -iE 'atomic|plain bytes'
HEAD:tests/test_crew_launcher.py:3250:  to -- `checklist_engine.save` writes plain
                                        bytes, non-atomically) is
```

Corrected. The string `writes plain bytes, non-atomically` now appears **0 times**
anywhere in `scripts/ tests/ docs/ skills/`. The other 12 are about
`gauge_writer_hook`, `spine_rail`'s binding store, the episode store, the code map, and
`run_skill_eval` — none of them says anything about `save` that is now wrong.

## Verification

```bash
py -m pytest tests/test_checklist_engine.py tests/test_crew_launcher.py \
             tests/test_checklist_engine_atomic_save.py -q
# 679 passed, 140 subtests passed in 6.75s
```

Both required suites green, with the new module.

Full suite, distribution derived mechanically:

```bash
py -m pytest tests/ -q | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
      1 FAILED tests/test_retirement_guard.py
      2 FAILED tests/test_spine_lifecycle.py
# 3 failed, 3200 passed, 5 skipped, 1217 subtests passed in 132.00s
```

None of the three is mine, and I checked rather than assumed:

- **`test_retirement_guard.py::test_canon_is_clean` — pre-existing, and not code at all.**
  It fails on `notes-a.md:365`, an uncommitted note in this worktree:
  `Violation(leg='unapproved-store-mention', path='notes-a.md', line=365, ...)`. It fails
  identically with my change stashed. Not mine, and not `scripts/`.
- **The 2 `test_spine_lifecycle.py` failures were transient, caused by a concurrent
  agent, and are gone.** Both are source-text guards over `scripts/spine_lifecycle.py`
  that failed with "the mutation did not change the source -- fixture is stale" — the
  signature of reading a file mid-edit. Another lane committed `86109e2f` into this same
  worktree during my full-suite run. Re-running both **with my change in place** after
  that commit landed: `2 passed`. Nothing for the Commander to chase.
- `tests/test_mcp_*.py`: **all green.** No sign of g2 trouble from where I sat.

## Triage candidates

### 1. `gauge_writer_hook._atomic_write_json`'s fixed temp name (already filed)

The handoff asked me to report this. It is **already filed** by the Commander at
`.agent-work/567-a/triage-candidates/gauge-writer-hook-fixed-temp-name.md` (raised by
`cmdr-567-a` at `600de020`, disposition `recommend-and-defer`), so I am confirming rather
than duplicating it.

Confirming from the implementer's side: the hazard is real and my change does **not**
inherit it. `scripts/hooks/gauge_writer_hook.py:513` uses
`path.with_name(path.name + ".tmp")` — one fixed temp path per target. Two concurrent
writers open the *same* temp, and the loser's file handle still points at the inode
`os.replace` just installed as the live file, so its buffered flush lands **inside the
live target after the rename**, installing a durably unparseable document. That is worse
than the transient tear fixed here, because today's tear heals on the next successful
write and an unparseable installed document does not. `mkstemp` in `save()` is what
avoids it, and it is why the handoff's instruction *not* to mirror that function was
correct.

Worth adding to the filed note: `spine_rail.py:379` already does it right (unique
`mkstemp` temp), so the repo contains both the correct and the incorrect pattern, and the
incorrect one is the one named `_atomic_write_json` — the name most likely to be copied.
Whoever fixes it should consider whether one shared helper is warranted.

### 2. #613's lost-update half remains open

Already filed at `.agent-work/567-a/triage-candidates/613-lost-update-half-remains.md`.
Confirming it is still true after this change, and that this change makes it *quieter*:
`run_crew.py:1431-1433` is a real `load()` → mutate → `save()` pair racing the parent
heartbeat, and after today it loses updates silently instead of noisily. The docstring is
the only thing now warning a reader. I did not touch it, per the handoff.

## Map Impact

- **Structural anchors touched:** `scripts/checklist_engine.py` — `save`(:237, now :237
  with a longer docstring), function-level. `_dominant_newline`(:224) and `load`(:220)
  read but unchanged. New module `tests/test_checklist_engine_atomic_save.py`.
- **Capabilities affected:** `spine-state-persistence` — the write is now atomic against
  torn reads and crash corruption. Still not serialized against concurrent
  read-modify-write.
- **Constraints/assumptions touched:** `constraint:rail-strings-untouched` honored
  (`_RAIL_STRINGS`, `_refresh_attach_hint` not touched);
  `constraint:no-hooks` honored (hooks read only);
  `assumption:engine-under-edit-is-not-engine-in-play` relied on and held — the red-proof
  came from running the new test before editing, so the installed engine was never
  modified.
- **Decisions resolved:** `decision:atomicity-is-not-mutual-exclusion` — settled in code
  and stated in the docstring in `spine_rail.py`'s existing words. Its `settle:`
  condition ("two writers each load-mutate-save a copy; observe a well-formed file with
  one update missing") is **not** exercised by my tests, deliberately: demonstrating the
  lost update would have meant building the very thing I was told not to build. The
  decision is honored as a documented boundary, not as a test.
  `decision:in-session-observation-is-not-evidence` — honored via the fresh-process
  line-ending probe.
- **Claims/evidence produced:** `save()` never opens the target for writing; the target's
  inode is replaced exactly once per save; no `*.tmp` survives success or failure; CRLF
  and mode both survive the replace. All four are mechanical and deterministic.
- **Trust limitations:** map orientation remains `DEGRADED-UNPARSEABLE` repo-wide
  (`map/ids.jsonl` tracked and 0 bytes), already filed as
  `.agent-work/567-a/triage-candidates/map-ids-jsonl-empty-repo-wide.md`. I worked from
  code and tests only, as the handoff said to.

## Assumptions

- `os.replace` is atomic on the same filesystem on this platform (POSIX). The temp is a
  sibling, so the same-filesystem precondition holds by construction.
- `fsync` on the file descriptor is enough for the crash claim. The containing
  **directory** is not fsynced, so a crash immediately after `os.replace` can in
  principle lose the rename itself and leave the *old* document in place. That is still a
  complete, parseable document, which is the property claimed — but it means "the save
  survives a crash" is not guaranteed, only "the file is never corrupt". I did not add a
  directory fsync: it is not in the specified pattern, `spine_rail.py:379` does not do it
  either, and adding it unasked would be the change growing.

## Stop conditions hit

None. Line-ending preservation needed no restructuring of `save()` — reading
`_dominant_newline` first was sufficient. `os.replace` was usable for every case. The
red-proof constructed cleanly and discriminated 5 of 11 tests.

## Out-of-scope observations

**A concurrent agent committed my staged files under its own commit message, and the
Commander should know.** I staged `scripts/checklist_engine.py`,
`tests/test_checklist_engine_atomic_save.py`, and `tests/test_crew_launcher.py` and ran
`git commit`, which returned `nothing to commit, working tree clean`: another agent
working in **this same worktree** had swept all three into `fe2eb504`
("plan(567-a): act on the cold critic's five blocking findings") seconds earlier,
apparently via an `add -A`-shaped commit.

- **No content was lost.** I verified every marker in `HEAD`: `mkstemp` ×3, `os.fchmod`,
  `os.fsync`, `os.replace(tmp_name, path)`, the "not mutual exclusion" docstring, the
  corrected `test_crew_launcher.py` sentence, the new 295-line test module, and
  `writes plain bytes, non-atomically` at 0 occurrences.
- **What is lost is attribution.** My prepared commit message — which carried the
  rationale for the unique temp name, the scope boundary, and the red-proof summary — has
  no commit to live on, so this result file is now the only record of it.
- I did **not** rewrite history to fix this. Amending or reordering commits under a
  concurrently-committing agent is how a lane loses work, and nothing authorized me to.
- The general hazard: **two agents sharing one worktree, at least one committing with a
  whole-tree add.** It cross-contaminates commits and would silently ship a half-finished
  edit from another lane. The `notes-a.md:365` violation failing
  `test_retirement_guard.py::test_canon_is_clean` for everyone in this worktree is the
  same root cause showing up as a red test.

## Workflow Feedback

- **Handoff gaps.** The handoff was unusually good — the "do NOT mirror
  `_atomic_write_json`" section with the critic's measured corruption output, and the
  "deterministic, not a thread race" section, both pre-empted exactly the mistakes I
  would otherwise have made. Two real gaps:
  1. **`Suggested Model Tier: Simple bounded` and the "ten-ish lines" estimate are both
     low for the pattern the handoff itself specifies.** Six mandated steps
     (`mkstemp`/`fchmod`/`fsync`/`replace`/`finally`-unlink/mode-lookup) cannot land in
     ten lines; it came out at 23, against a ~20-line stop condition. A handoff whose own
     spec exceeds its own stop condition puts the implementer in a false stop.
  2. **`Authority` contradicts `Protected Intent`.** Authority still says the pattern
     "mirror[s] `gauge_writer_hook.py:513`", which is precisely what Protected Intent
     spends 25 lines forbidding. Two sections in one document giving opposite
     instructions about the same line is dangerous even when one is emphatic. Fixing
     Authority when Protected Intent was revised looks like a missed edit.
- **Context rediscovered.** `spine_rail.py:379` — the repo **already** has the exact
  correct pattern (unique `mkstemp` + `flush` + `fsync` + `os.replace` + `finally` unlink),
  30 lines below the `:163` comment the handoff cites for wording. The handoff pointed at
  `:163` for prose and at `gauge_writer_hook.py:513` (as an anti-pattern) for structure,
  but never named the working implementation right there. Citing `spine_rail.py:379` as
  the pattern source would have been shorter, safer, and self-consistent.
- **Instructions improvised around.** A genuine conflict between my dispatch and the
  `constellation-implementer` skill, resolved toward the dispatch:
  - The skill opens with "CLAIM the engine lease" and "drive the engine before you touch
    the task", and states that a run which "solves the task directly ... has **failed**
    this dispatch". My dispatch forbids exactly that: no `spine.json`, no lease, no
    `mcp__spine__*`, no engine-driving — because an agent in this epic corrupted a live
    spine by inheriting context and believing it was the Commander.
  - I checked the environment rather than guessing: **no `SPINE_*` variables are set**
    (`env | grep -i '^SPINE'` → exit 1), so nothing was bound and the skill's
    "spine already bound → `spine_status` first" branch did not apply either. I followed
    the dispatch, worked directly, and am recording the deviation here because the skill
    says an undriven run is a failed run.
  - **The friction is structural, not a one-off:** this skill has no path for
    "implementer dispatched with engine-driving explicitly withheld", yet that is the
    exact safe configuration after a spine-corruption incident. As written, an implementer
    obeying a safety fence is told it has failed. That branch should be named in the
    skill, not left for each dispatch to override by hand.
- **What would have made this easier.** One change: make the handoff's `Authority`
  section quote its own `Protected Intent` instead of contradicting it, and cite
  `scripts/hooks/spine_rail.py:379` as the pattern source. The rest of the handoff was
  precise enough that the implementation was mechanical and the rigor went where it
  belonged — into the test.
