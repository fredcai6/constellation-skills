# Review Result — g3-review: `checklist_engine.save()` writes atomically

Verdict: APPROVE

## Assigned Gate
`g3-review` (epic-567-door / cmdr-a, lane A of epic #567) — #613's atomicity half.

## Result
`APPROVE`

Every close criterion in the handoff is met, and I met each one by my own
measurement rather than by reading the implementer's. The red-proof reproduced
exactly. Blockers: none. Five out-of-scope observations are listed below, two of
which I believe the Commander must see before #613 is closed.

## Scope of my review

`scripts/checklist_engine.py`, `tests/test_checklist_engine_atomic_save.py`, and
the one docstring at `tests/test_crew_launcher.py:3250`. The parallel g2 crew's
`scripts/mcp_spine_server.py` (uncommitted) and `scripts/spine_lifecycle.py` /
`tests/test_spine_session_id.py` (commit `86109e2f`) are on the same branch and are
NOT reviewed here.

Reviewed at `HEAD = 92352431`, base `600de020`.

```
$ git diff 600de020..HEAD --stat -- scripts/ tests/
 scripts/checklist_engine.py                |  51 ++++-      <- mine
 scripts/spine_lifecycle.py                 |  27 ++-        <- g2's, not reviewed
 tests/test_checklist_engine_atomic_save.py | 295 ++++++++++  <- mine
 tests/test_crew_launcher.py                |  10 +-         <- mine
 tests/test_spine_session_id.py             |  78 ++++++      <- g2's, not reviewed
```

`checklist_engine.py` carries exactly three hunks — the `import tempfile`, the
docstring, and the `save()` body. Nothing else in the file is touched:

```
$ git diff 600de020..HEAD -- scripts/checklist_engine.py | grep '^@@'
@@ -19,6 +19,7 @@ import re
@@ -235,8 +236,8 @@ def _dominant_newline(path: Path) -> bytes:
@@ -245,14 +246,58 @@ def save(path: Path, data: dict) -> None:
```

---

## 1. The red-proof — MY OWN, and it reproduced exactly

I did not take this from the Commander or the implementer. I reverted `save()` in
the **worktree** copy to the old bare `write_bytes`, ran the module, restored, and
proved the restore byte-exact.

**Installed copies under `/home/tommy/.claude/skills/` were never touched.** Nine
copies of `checklist_engine.py` are installed; all nine were `md5
3137b0a3de9288de0ce7d66325a23942` before my proof and all nine still are after it.

### Green world (as shipped)

```
$ cd <worktree> && py -m pytest tests/test_checklist_engine_atomic_save.py -q
...........                                                              [100%]
11 passed in 1.60s
```

### The revert I applied (worktree copy only)

The whole `mkstemp`/`fchmod`/`fsync`/`os.replace`/`finally`-unlink block replaced by
the single line it used to be:

```python
    Path(path).write_bytes(payload)
```

### Defective world

```
$ py -m pytest tests/test_checklist_engine_atomic_save.py -q
E  AssertionError: 6034219 == 6034219 : the target's inode did not change: the
   document was written in place, not atomically renamed into place
=========================== short test summary info ============================
FAILED tests/test_checklist_engine_atomic_save.py::AtomicSaveTests::test_concurrent_reader_never_observes_a_partial_document
FAILED tests/test_checklist_engine_atomic_save.py::AtomicSaveTests::test_no_temp_sibling_after_a_failed_replace
FAILED tests/test_checklist_engine_atomic_save.py::AtomicSaveTests::test_save_never_opens_target_for_writing
FAILED tests/test_checklist_engine_atomic_save.py::AtomicSaveTests::test_save_writes_a_temp_sibling_in_the_same_directory
FAILED tests/test_checklist_engine_atomic_save.py::AtomicSaveTests::test_target_inode_is_replaced_exactly_once
5 failed, 6 passed in 1.55s
```

**5 failed / 6 passed — identical to the distribution the Commander reported and to
the implementer's own pre-change red.** The three named deterministic
discriminators are all in the failing set.

### The three deterministic ones really are deterministic

Because a flaky red is not a red, I ran the three deterministic discriminators
alone, three consecutive times in each world:

```
DEFECTIVE:  3 failed, 8 deselected in 0.04s
            3 failed, 8 deselected in 0.03s
            3 failed, 8 deselected in 0.03s
GREEN:      3 passed, 8 deselected in 0.04s
            3 passed, 8 deselected in 0.04s
            3 passed, 8 deselected in 0.04s
```

No timing dependence in either direction. The test module **discriminates**, and it
discriminates on assertions that do not need luck. The 6 that pass in both worlds
are the four line-ending cases, the mode case, and `test_no_temp_sibling_after_success`
— regression guards for behaviour that must *survive* the change, which is the
correct role for them.

### Restore proved exact

```
$ git checkout -- scripts/checklist_engine.py
$ md5sum scripts/checklist_engine.py
edc4514cef64ad5c271a95f23a632eb7  scripts/checklist_engine.py   <- same as before my proof
$ git diff --stat
 scripts/mcp_spine_server.py | 539 ++++++++++++++++++++++-----   <- g2's, untouched by me
 1 file changed, 483 insertions(+), 56 deletions(-)
$ git status --short
 M scripts/mcp_spine_server.py
?? tests/test_mcp_spine_bind.py
$ find /home/tommy/.claude/skills -name checklist_engine.py -exec md5sum {} \; | awk '{print $1}' | sort -u
3137b0a3de9288de0ce7d66325a23942
```

`checklist_engine.py` is absent from `git diff --stat`, so the restore is exact.
The only dirt in the worktree is the g2 crew's, exactly as it was when I started.

---

## 2. Line endings — measured, in a fresh process, from outside the test runner

`_dominant_newline(path)` reads the existing file, so the whole risk is that it
gets consulted after the original is gone. It is not: the diff reads it at line 273,
before the `stat`, before the `mkstemp`, before the `os.replace`.

My own fresh-process probe, importing the engine by absolute path and counting
bytes on disk:

```
== LINE ENDINGS + MODE + LEFTOVERS ==
crlf     CRLF= 10 bareLF=  0 eol=CRLF parses=YES inode_changed=True mode=0o640->0o640 leftover_tmp=[]
lf       CRLF=  0 bareLF= 10 eol=LF   parses=YES inode_changed=True mode=0o640->0o640 leftover_tmp=[]
mixed    CRLF=  0 bareLF= 10 eol=LF   parses=YES inode_changed=True mode=0o640->0o640 leftover_tmp=[]
missing  CRLF=  0 bareLF= 10 eol=LF   parses=YES inode_changed=n/a  mode=new->0o600 leftover_tmp=[]
```

- **A CRLF spine is still CRLF after a save, with ZERO bare LFs.** The count is
  `raw.count(b"\r\n") == 10` and `raw.count(b"\n") - raw.count(b"\r\n") == 0`.
- **LF stays LF** — no `\r` anywhere.
- **A missing file gets LF. A mixed file gets LF.** Unchanged from before.
- `inode_changed=True` on the same rows is the load-bearing part: the endings
  survive *through* the rename, which is exactly what could have regressed
  silently. The endings are not preserved by accident of the file never moving.

The regression `save()`'s own docstring exists to prevent — one engine verb
rewriting a whole file's endings and destroying its blame — has not happened.

## 3. File mode — neither narrowed nor widened

`mkstemp` creates `0600`, so the hazard is real in both directions. Measured across
four modes:

```
== MODE: not narrowed and not widened ==
  want=0o600 got=0o600 OK
  want=0o640 got=0o640 OK
  want=0o644 got=0o644 OK
  want=0o664 got=0o664 OK
```

`0o600` proves nothing is being widened; `0o664` proves nothing is being narrowed.
The `& 0o7777` mask carries setuid/setgid/sticky through as well. A brand-new file
gets `mkstemp`'s `0600`, which is the same "no existing mode to preserve" case the
old code had.

## 4. No temp survives — success, and a failure forced two different ways

The handoff asks for the success path and a forced failure. I forced it at two
different depths, because a failure at `os.replace` and a failure inside the write
take different paths out of the `try`:

```
== FORCED FAILURE: no temp survives, old doc intact ==
  os.replace raises  raised=OSError('forced replace') leftover_tmp=[] old_doc_byte_identical=True
  write raises       raised=OSError('forced write')   leftover_tmp=[] old_doc_byte_identical=True
```

Success path: `leftover_tmp=[]` on all four rows of the line-ending table, and the
suite's `test_no_temp_sibling_after_success` saves twice and lists the directory.
The concurrency test also asserts `_tmp_siblings() == []` after 1.5s of two writers
hammering the file. No stray temp on any path an exception can take, and the
previous document is byte-identical after a failure.

**One case the criterion does not cover — see observation O1.** A SIGKILL cannot
run the `finally`, and I measured that it does leave an orphan.

## 5. Same-directory temp — `os.replace` is atomic here

The suite's own check compares dirnames. I went further, because the suite's
fixture directory is itself under `/tmp`, which makes "the temp is a sibling" and
"the temp is in the system temp dir" indistinguishable. So I re-ran with the target
**outside** `gettempdir()`:

```
### target dir NOT under gettempdir(): /home/tommy/.cache/revprobe.tdYQ  (gettempdir=/tmp)
  temp=/home/tommy/.cache/revprobe.tdYQ/spine.json.ugm2e7i5.tmp
  temp_dir==target_dir: True
  temp under gettempdir(): False   (must be False)
  st_dev(temp_dir)==st_dev(target): True
```

The temp follows the **target**, not the platform temp dir, and lands on the same
`st_dev`. `dir=str(path.parent)` is doing its job. The cross-filesystem
non-atomicity hazard the handoff names does not exist here.

The temp name is also **unique** (`spine.json.ugm2e7i5.tmp`), not the fixed
`spine.json.tmp` that `gauge_writer_hook.py:513` uses. That is the right call and
the implementer's reasoning for it is correct.

## 6. `fsync` is called, and it is called BEFORE the rename

Wrapping `os.fchmod`, `os.fsync` and `os.replace` and recording the order:

```
== FSYNC ORDER ==
  call order = ['fchmod', 'fsync', 'replace']
  fsync present: True
  replace present: True
  fsync BEFORE replace: True
```

The crash-safety half is delivered as claimed: the data is durable before the
rename is even issued, so the rename cannot become durable ahead of the data. The
docstring's wording ("`fsync` it so the rename cannot become durable before the
data is") is accurate.

**The containing directory is not fsynced** — one `fsync`, on the temp fd. The
implementer disclosed this itself, under `Assumptions`, in the right terms: a crash
immediately after `os.replace` can lose the rename and leave the *old* complete
document. That is still a complete parseable document, which is the property
claimed. I agree this is not a defect and agree with not adding it uninvited: the
repo's own correct implementation at `scripts/hooks/spine_rail.py:369` does not
fsync the directory either, so adding it here would have made this the only place
in the repo that does.

## 7. The scope boundary — stated, and not exceeded

**Stated.** The docstring carries it in the house framing, matching
`scripts/hooks/spine_rail.py:163`:

> **Atomicity here is not mutual exclusion.** The WRITE is atomic; the
> read-modify-write is not. Two callers that each `load()` → mutate → `save()`
> still clobber each other, and the loser's update goes missing from a file that is
> perfectly well-formed — so nothing raises and nothing notices. Guarding that is a
> separate job (locking or compare-and-swap) and is deliberately not done here.

That is the required statement, in plain words, naming the mechanism, the symptom,
and the fact that it is deliberate. Not under-stated.

**Not exceeded.** Scanned every added line for the forbidden shapes:

```
$ git diff 600de020..HEAD -- scripts/checklist_engine.py | grep -inE '^\+.*(lock|flock|compare|cas|version|retry|sleep|attempt)'
45:+    separate job (locking or compare-and-swap) and is deliberately not done here; see
```

The single hit is the docstring saying those things are **not** done. No lock, no
advisory file lock, no compare-and-swap, no version or hash field, no retry.

`load()` is unchanged and still one line:

```python
def load(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
```

Neither direction is a finding. The boundary is stated and respected.

## 8. Fenced regions — byte-identical, verified by targeted diff

```
$ git diff 600de020..HEAD -- scripts/checklist_engine.py | grep -n "RAIL_STRINGS\|_refresh_attach_hint"
grep exit=1
```

Zero hits. `_RAIL_STRINGS` and `_refresh_attach_hint` are untouched and not
reformatted; lane C's #442 RAIL banner and HARD refusal remedy text are intact. The
three-hunk list in §"Scope of my review" independently confirms it — neither symbol
is inside any changed hunk.

Other exclusions:

```
$ git diff 600de020..HEAD --stat -- scripts/hooks/ scripts/mcp_spine_server.py
(empty)
```

`scripts/hooks/*` untouched. `scripts/mcp_spine_server.py` untouched **by the g3
commits** — the working-tree modification to it is the g2 crew's uncommitted work,
not g3's.

## 9. The one sanctioned blast-radius edit

```
$ git diff 600de020..HEAD -- tests/test_crew_launcher.py | grep -c '^@@'
1
```

One hunk, the docstring only. The `except (OSError, ValueError)` tolerance is still
in place immediately below it, as instructed:

```python
        def _safe() -> bool:
            try:
                return bool(predicate())
            except (OSError, ValueError):
                return False
```

The new wording correctly demotes the tolerance to belt-and-braces rather than
deleting it.

## 10. Blast-radius enumeration — I re-ran it, and I agree

The count reproduces, at three different revisions:

```
600de020  raw=17  excl_demo=13
3e4b0e20  raw=17  excl_demo=13
fe2eb504^ raw=17  excl_demo=13
fe2eb504  raw=19  excl_demo=15
HEAD      raw=19  excl_demo=15
```

**13 at the lane's baseline, once the four generated `docs/explainer-demo/*.html`
pages are excluded.** I agree with the exclusion: those four are Docent output about
an unrelated physics/evo-predictor codebase and match the word "atomic" only
incidentally.

HEAD is 15, and the two additions are exactly the change's own:

```
$ diff <(files at 600de020) <(files at HEAD)
> scripts/checklist_engine.py            <- the new docstring
> tests/test_checklist_engine_atomic_save.py  <- the new module
```

**Was a second stale artifact missed?** I searched wider than the implementer's
`checklist_engine\.save` + `atomic|plain bytes` grep, because a stale claim could
easily avoid both terms — I searched for `non-atomic`/`not atomic`/`plain
bytes`/`atomically`, for `write_bytes` in prose, for `torn`/`truncat`, and for
`mid-write`/`in place`/`clobber` intersected with `spine|checklist|engine|save`.

**No second stale artifact.** The string `writes plain bytes, non-atomically` now
appears 0 times. Every surviving `atomic` claim in `scripts/ tests/ docs/ skills/` is
about `gauge_writer_hook`, `spine_rail`'s binding store, the episode store, the code
map, or `run_skill_eval` — none says anything about `checklist_engine.save` that this
change falsifies. **I agree with the implementer: exactly one artifact was false,
and it was corrected.**

## 11. Suite runs, with the failure distribution derived mechanically

### Required suites

```
$ py -m pytest tests/test_checklist_engine.py tests/test_crew_launcher.py \
               tests/test_checklist_engine_atomic_save.py -q
FAILED tests/test_crew_launcher.py::CrewGrantTiesToDoorTests::test_crew_grant_mcp_entries_equal_the_doors_own_tool_names
FAILED tests/test_crew_launcher.py::CrewGrantTiesToDoorTests::test_door_has_all_nine_tools_todays_grant_expects
2 failed, 677 passed, 140 subtests passed in 6.98s
```

### Full suite

```
$ py -m pytest tests/ -q
8 failed, 3248 passed, 5 skipped, 1218 subtests passed in 131.68s

$ ... | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
      1 FAILED tests/test_code_map.py
      2 FAILED tests/test_crew_launcher.py
      1 FAILED tests/test_mcp_door_unbound.py
      1 FAILED tests/test_mcp_identity.py
      1 FAILED tests/test_mcp_lifecycle.py
      2 FAILED tests/test_mcp_spine_server.py
```

### Attribution — measured, not assumed

Two of the eight are in `tests/test_crew_launcher.py`, a file g3 **did** touch, so I
could not wave them off as "probably the parallel crew's". I exported committed
`HEAD` to a scratch tree with `git archive` — which drops the g2 crew's uncommitted
`scripts/mcp_spine_server.py` while keeping all of g3's work — and re-ran all eight.
This mutates nothing in the shared worktree.

```
$ md5sum scratch/scripts/mcp_spine_server.py ; git show HEAD:...| md5sum
66907eab932585af9ee4de33fcd72652   (both — the export is clean HEAD)
$ md5sum worktree/scripts/mcp_spine_server.py
7dfd9918ad84811da91083fb24539b49   (the g2 crew's in-flight edit)

$ (in the clean export) py -m pytest <the 8> -q
1 failed, 65 passed, 14 subtests passed in 4.88s
FAILED tests/test_code_map.py::MapTreeFreshnessTests::...
```

**Seven of the eight pass at clean HEAD with g3's change fully present.** They are
caused by the g2 crew's uncommitted `scripts/mcp_spine_server.py` — including both
`test_crew_launcher.py::CrewGrantTiesToDoorTests` failures, which assert the crew
grant matches the door's own tool names and so break the moment the door's tool list
is edited. **Not g3's.**

The eighth, `test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`,
needs a real git repo to run, so the export could not settle it. I settled it by
exporting `600de020` — the lane's baseline, with **no** g3 and **no** g2 work
present at all — into a fresh `git init`:

```
$ (at 600de020, git-init'd, g3 and g2 entirely absent)
   py -m pytest tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build -q
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
1 failed
```

**`map/INDEX.md` is already stale at the lane baseline.** Pre-existing, not g3's.
(In the dirty worktree the fresh build reports 1232 entities against a committed
1226. `save()` adds no new callable symbol — the implementer's wiring grep found
none and the diff adds no `def` or `class` — so g3 contributes 0 of that delta.)

**Zero of the eight failures are attributable to g3.** Nothing here for the
Commander to chase in lane A.

---

## Handoff compliance

Assigned intent, scope, required evidence and stop conditions were all satisfied.
The implementer did the honest thing on three counts worth naming: it reported its
23-line body against a ~20-line stop condition instead of hiding the overrun; it
labelled the thread-race test as supporting-only and built three deterministic
discriminators instead of resting on it; and it disclosed the missing directory
fsync as a limit on the crash claim rather than overclaiming. Its red-proof was
genuine test-first against unmodified `HEAD`, which is stronger evidence than a
break-and-restore, and my independent break-and-restore agrees with it exactly.

## Scope drift

None. Three hunks in one function plus one docstring elsewhere. Every named
exclusion — `_RAIL_STRINGS`, `_refresh_attach_hint`, `scripts/hooks/*`,
`scripts/mcp_spine_server.py`, `load()`, the `save()` signature, the four call
sites — is verified untouched by targeted diff, not by eye.

## Evidence verdict

Sufficient, and independently reproduced. TDD was required with a proven-non-vacuous
red; the red is real, it is deterministic, and it is not carried by the racy test.
Every claim in the implementer's result that I could re-measure, I re-measured, and
all of them held: the 5/11 red distribution, the four line-ending rows, mode
preservation, zero leftover temps, the same-directory temp, and the 13-file
blast-radius count. I found no claim I could not reproduce.

## Code/doc quality

Good. The body reads linearly, each step is commented with the reason rather than
the mechanic ("mkstemp makes 0600; don't narrow it"; "`os.replace` is only atomic
within one filesystem"), and it mirrors the repo's own correct implementation at
`scripts/hooks/spine_rail.py:369` step for step — including declining the
directory fsync that implementation also declines. Declining to extract a
one-caller helper was right, especially given the handoff forbade converging with
`gauge_writer_hook._atomic_write_json`.

### Fowler refactoring pass

Ran the full baseline catalog; the record clears the rail:

```
$ py verify_fowler_pass.py fowler.json
fowler pass ok (smells=12, flagged=['comments-as-deodorant'],
                overridden=['long-method', 'duplicated-code'])
rail exit=0
```

- **long-method — `overridden`.** 7 body lines to 23 (def-to-def span 65 with the
  31-line docstring). Standard that wins: `spine_rail.py:369` is the repo's own
  inline realisation of this exact pattern at this exact size, and the handoff's
  Protected Intent forbids factoring a shared helper. A one-caller helper would add
  indirection for no reader benefit and invite the convergence the handoff forbids.
- **duplicated-code — `overridden`.** This is now the **third** copy of
  mkstemp/flush/fsync/replace/finally-unlink (`spine_rail.py:369`,
  `run_skill_eval.py:968`, and now `save()`), with a fourth broken variant at
  `gauge_writer_hook.py:513`. Standard that wins: consolidating means editing
  `scripts/hooks/*`, which this lane was told to read and not write. Routed as O4
  rather than flagged against this diff.
- **comments-as-deodorant — `flagged`, observation O2 below.**
- **speculative-generality — `absent`,** and deliberately so: no lock, no CAS, no
  version field, no retry, no directory fsync. The boundary is documented rather
  than pre-built.
- large-class, feature-envy, data-clumps, primitive-obsession,
  long-parameter-list, shotgun-surgery, divergent-change, message-chains —
  `absent`.

## Map impact verdict

- **Evidence supports claimed change:** Yes. `spine-state-persistence` is now atomic
  against torn reads and crash corruption; I reproduced all four of the claimed
  mechanical properties myself.
- **Constraints not violated:** Yes. `constraint:rail-strings-untouched` verified by
  targeted diff; `constraint:no-hooks` verified by empty `--stat`;
  `assumption:engine-under-edit-is-not-engine-in-play` held on my side too — nine
  installed copies unchanged by md5 across my whole red-proof.
- **Notes match the diff:** Yes, with one omission — the notes name line endings and
  permission bits as the two properties held constant, but a third observable
  property (symlink and hardlink identity of the target) is **not** held constant.
  See O1. Not overstated anywhere; one property under-stated.
- **Decision candidates surfaced:** Yes. `decision:atomicity-is-not-mutual-exclusion`
  is settled in the docstring, and the implementer was explicit that its `settle:`
  condition is deliberately not exercised because demonstrating the lost update
  would have meant building the thing it was told not to build. That is the right
  call and the right disclosure.
- **Durable context routed:** Yes. Both pre-existing triage candidates were confirmed
  rather than duplicated, and the `gauge_writer_hook` note was usefully sharpened
  with `spine_rail.py:379` as the correct counter-example.

Not architecture-significant beyond one function's durability contract. Nothing
here approaches a BLOCK.

## Reconciliation check

`map/INDEX.md` is stale, but it is stale at `600de020` with this lane's work
entirely absent, so it is not this gate's to fix and not this gate's to be blocked
by. The docstring cites `scripts/hooks/spine_rail.py`'s binding-store transaction
without a line number; `:369` is the implementation and `:163` the prose. Trivial.

## Blockers

**None.**

## Out-of-scope observations

### O1. A symlinked or hardlinked spine now loses its link identity — undisclosed

`os.replace` installs a new regular file at the path. `Path.write_bytes` wrote
*through* a symlink and *into* a hardlinked inode. Measured:

```
symlink: is_symlink_after_save=False   (old write_bytes: True)
         underlying real.json updated=None   (old: 'w')
hardlink: nlink_after=1  (old: 2)   peer_sees_update=None  (old: 'w')
```

So a spine reached through a symlink is silently detached: the link becomes a
regular file and the file it pointed at never receives the update. **Not a blocker:**
nothing in the repo symlinks or hardlinks a spine, `spine_rail.py:1226-1232`
already treats a symlinked spine leaf as an *escape to guard against* rather than a
supported shape, and the house pattern at `spine_rail.py:369` has the identical
property. An ancestor directory being a symlink is unaffected — the temp is created
in `path.parent`, which resolves through it. Raised because it is a third
behaviour change and the result names only two. Triage candidate at most.

### O2. The docstring is now load-bearing documentation for an unfixed defect

This is the Fowler `comments-as-deodorant` flag, and it is worth the Commander's
attention rather than a refactor. The change makes the *remaining* half of #613
**silent** where it used to be noisy — before today a lost update at least
coexisted with visible tearing; now two racing writers produce a perfectly
well-formed file with one update missing and nothing raises. The docstring
paragraph is now the only surviving warning in the system, and
`scripts/run_crew.py:1431-1433` is a live `load()` → mutate → `save()` pair racing
the parent heartbeat. **#613 must not be closed on the strength of this gate**, and
the lost-update half should not be deprioritised on the grounds that "save is
atomic now". The implementer was right not to touch it; someone needs to hold the
other half open.

### O3. A hard kill mid-save leaves an orphan temp — the criterion covers exceptions, not signals

The close criterion "no temp file survives" is met for every path an exception can
take. It cannot be met for a signal, because `finally` does not run. Measured with
SIGKILL delivered after the temp is written and before `os.replace`:

```
SIGKILL mid-save: leftover=['spine.json.cvorxclv.tmp']  target_still_parseable_as='old'
```

The atomicity claim holds — the target is intact and parseable. But an orphan
sibling survives in the work area, nothing reaps it, and the archive will carry it.
Because the name is unique rather than the fixed `spine.json.tmp`, orphans
**accumulate** across repeated crashes instead of being overwritten, and no reader
will mistake one for the spine. This is inherent to the sanctioned pattern and is
strictly better than the old failure mode (a truncated live target), so it is not a
blocker. Triage candidate: a glob-based reap of `<spine>.*.tmp` at `load()` or at
closeout. Raised mainly because the handoff states the criterion absolutely and it
is true only for exceptions.

### O4. Third copy of the atomic-replace pattern; the broken one has the best name

`spine_rail.py:369`, `run_skill_eval.py:968`, and now `checklist_engine.save()` all
open-code mkstemp/flush/fsync/replace/finally-unlink. `gauge_writer_hook.py:513` is
a fourth, *incorrect* variant using a fixed `.tmp` name — and it is the one called
`_atomic_write_json`, i.e. the name a future author will grep for and copy. This
sharpens the already-filed
`.agent-work/567-a/triage-candidates/gauge-writer-hook-fixed-temp-name.md` rather
than adding a new candidate. I confirm the implementer's analysis of the hazard and
confirm this change does not inherit it.

### O5. Two agents in one worktree makes full-suite evidence non-reproducible

My full-suite distribution shares **no failure** with the implementer's. It reported
`1 test_retirement_guard + 2 test_spine_lifecycle`; I got `2 test_crew_launcher + 5
test_mcp_* + 1 test_code_map`, with its three now green and mine invisible to it.
Same branch, same worktree, hours apart. The implementer also had its staged files
swept into another lane's commit `fe2eb504`, losing its prepared commit message and
its attribution. So a full-suite result from a shared worktree is not evidence
about a lane — it is evidence about the worktree at an instant. The `git archive`
isolation I used above is the cheap fix and I recommend the Commander require it for
any attribution claim in this wave. Every attribution in this review rests on that
isolation, not on the shared run.

## Workflow Feedback

- **Handoff gaps.** The handoff was strong — naming the three deterministic
  discriminators, pre-empting the "temp in `/tmp`" trap, and demanding measurement
  over assertion for line endings all pointed me straight at the real risks. Three
  gaps:
  1. **The "no temp file survives" criterion is stated absolutely but is only true
     for exceptions.** It says to check "after a save forced to fail", which reads
     as covering all failure, and a `finally` block cannot cover a signal. I had to
     decide unaided whether the SIGKILL case (O3) was the criterion failing or a
     case outside it. Say "failure by exception" and the ambiguity disappears.
  2. **Nothing told me how to attribute a failure in a file BOTH lanes touch.** The
     handoff says failures confined to `test_mcp_*.py` are probably g2's, but two of
     my eight were in `tests/test_crew_launcher.py`, which g3 edits — so the
     confinement heuristic gave me no answer for the case that actually arose. I
     improvised the `git archive HEAD` isolation. That technique should be in the
     handoff, because the heuristic will keep failing while two lanes share a
     worktree.
  3. **"Prove the mode is not narrowed OR widened" needed a mode below the
     default to be a real test.** Every check I inherited used `0640`, which is
     narrower than `mkstemp`'s `0600` in the group bit but does not test widening
     in the owner bits. I added `0600` and `0664` to close both directions. Worth
     specifying the values.
- **Context rediscovered.** Two things:
  1. **`scripts/hooks/spine_rail.py:369` is the repo's correct implementation of the
     exact pattern under review**, and the handoff never names it — it cites `:163`
     for prose and `gauge_writer_hook.py:513` as an anti-pattern. It is the single
     most useful anchor for judging this diff, because "does this match the house
     pattern step for step" answered the directory-fsync question and the
     one-caller-helper question at once. The implementer flagged the same omission.
     It should be in the reviewer handoff too.
  2. **The test suite's own same-directory check cannot distinguish "sibling" from
     "system temp dir"** because its fixture lives under `/tmp`. I had to build a
     target outside `gettempdir()` to make that assertion mean what it claims. The
     handoff calls a temp in `/tmp` "a real defect" without noting that the shipped
     test cannot see the difference.
- **Instructions improvised around.** A direct conflict between my dispatch and the
  `constellation-reviewer` skill, resolved toward the dispatch:
  - The skill's first instruction is to build a survey from
    `REVIEW_SURVEY.template.json` and **claim the engine lease before touching the
    diff**, and it says a run that records a verdict without driving the engine
    "has **failed** this dispatch". My dispatch forbids exactly that: no spine, no
    checklist, no `checklist_engine.py` as an engine driver, no lease, no
    `mcp__spine__*` — because an agent in this epic corrupted a live spine by
    inheriting context and believing it was the Commander.
  - I checked rather than guessed: `SPINE_FILE`, `SPINE_SESSION` and `SPINE_PARENT`
    are all empty, so the skill's "a spine is already bound → `spine_status` first"
    branch did not apply either. Neither branch of the skill covers my situation.
  - I followed the dispatch and reviewed directly, keeping the skill's *substance*
    where it did not require the engine: I visited every close criterion, and I ran
    the Fowler pass through its real rail (`verify_fowler_pass.py`, exit 0) with the
    record in my scratchpad rather than in the workbench.
  - **This is the second crew member in this gate to hit the identical conflict** —
    the implementer's result documents the same override against
    `constellation-implementer`. That makes it structural, not a one-off: both
    skills lack a branch for "crew dispatched with engine-driving deliberately
    withheld", which is the correct safe configuration after a spine-corruption
    incident. As written, a crew member obeying a safety fence is told by its own
    skill that it has failed. Worth a real fix in both skills rather than a
    per-dispatch override.
- **What would have made this easier.** One change: put the `git archive <rev> | tar
  -x` isolation recipe in the handoff as the sanctioned way to attribute a suite
  failure, and cite `scripts/hooks/spine_rail.py:369` as the house pattern to judge
  the diff against. Those two would have saved most of my time, and the first is
  reusable by every lane in this wave.

## Return status
`complete`
