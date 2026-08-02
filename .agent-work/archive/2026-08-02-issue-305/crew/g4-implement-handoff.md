# g4-implement — handoff to constellation-implementer

**Issue:** #305 (gate g4). **Closes:** #327.
**Worktree:** `C:/Programs/constellation-skills-wt/e298-305` (branch `epic-298/305`). Work ONLY here.
**Never touch** `C:/Programs/constellation-skills` — it holds the human's uncommitted WIP.
**Interpreter: `python`** (3.14.3, has pytest). **NEVER `py`** — it is 3.12.13 with no pytest, it
silently no-ops and reads as a green suite.

---

## Task

**Remove `run.dirty` from the context manifest.** Removal, not repair — a settled, human-ratified
ruling. You are not being asked to re-litigate whether the field should go. You *are* being asked to
remove it completely and leave no stale prose behind.

`checklist_engine.repo_revision()` is **out of scope and must not change**: it stays a general
repo-facts primitive returning `{commit, dirty}`. What changes is that the manifest producer stops
*consuming* the `dirty` half.

### Why (the corrected justification — use this, not the older wording)

The older justification said `run.dirty` is "permanently, self-causedly true." **I measured it and
that is false.** Across all 49 manifests the producer has actually written in this tree:
**47 `true`, 1 `false`, 1 field-absent** (the absent one is a #300-era archive predating `repo_rev`).
The `false` is real and ours: `.agent-work/issue-305/context/g1-implement.json` at commit `2456130`.
I ruled out "#326 hadn't landed": `git merge-base --is-ancestor c2e16a8 2456130` exits **0** and
`.agent-work/` was already tracked at that commit.

The real mechanism: `emit_step_manifest` **reads then writes** — `build_manifest()`
(`scripts/episode_capture.py:539`) computes `dirty` *before* `write_manifest()` (`:547`) creates the
file. So the flag never reads its own side effect; **it reads its predecessor's.** `g1-implement` was
this run's first manifest, had no predecessor, and read the tree before it touched anything. All 7
successors read `true`.

**So the field is neither reliably constant nor informative.** It is repo-wide, so it reports dirt on
files no declaration names — dominated by the run's own bookkeeping — yet it is not dependably
`true`, so a reader can neither use a value nor safely ignore the field. Both readings are
unavailable. *That* is why it goes.

**Do not restate "permanently true" anywhere** — not in code comments, not in docstrings, not in the
design doc, not in your result. If you need to characterise the frequency, use the measured counts.

---

## Scope — the complete edit surface (I enumerated it; verify, don't trust)

### 1. `scripts/context_manifest.py`

- **`run_facts()` (line ~320):** drop the `dirty: bool | None = None` parameter and the
  `"dirty": dirty,` entry from the returned dict. **`run_facts` has exactly one caller**
  (`build_manifest`, line ~387) — I verified this by grep; confirm it yourself.
- **`build_manifest()` (line ~387):** stop passing `dirty=state.get("dirty")`.
  **`state` is still needed** for `state.get("commit")` — do not delete the `repo_state` call.
- **`CONTENT_KEYS` is UNCHANGED.** `dirty` was never content. Do not touch the tuple.
- **Prose corrections — stale prose describing a removed field is worse than no prose:**
  - module docstring, property 1 (lines ~24–38) — the `dirty`/`run.dirty` passage
  - the `CONTENT_KEYS` comment block (lines ~104–111) — currently says "excluded to `run.dirty` instead"
  - `default_repo_state()` docstring (lines ~303–312) — "Returns **both** `commit` and `dirty` …
    `dirty` becomes `run.dirty`". The *function* still returns both (correct, keep); what is now
    false is that `build_manifest` routes `dirty` anywhere. It is **dropped on the floor** by the
    consumer, and the docstring should say so plainly.
  - `run_facts()` docstring (lines ~329–334) — the "`dirty` joined this subtree in #300 g5 rework 1"
    paragraph.
  - `build_manifest()` docstring (lines ~367–372) — "`dirty` becomes `run.dirty`".

**The prose must record that the field was removed and why** (it is repo-wide and reads the run's own
bookkeeping, so it describes the producing environment's noise rather than the bytes delivered), not
merely fall silent. A reader of `main` must not think it was never there. Reference #327.

### 2. `tests/test_context_manifest.py` (~25 assertion sites, all in `RepoRevContent` + one at :864)

Lines with `dirty`: 71 (a comment about file dirtiness — **unrelated, leave it**), 861, 864, 901–902,
931, 937, 940–948, 950–959, 965, 974, 980, 986, 995, 1016, 1019, 1021, 1026.

Judgement required, not blind deletion:

- `test_dirty_lives_in_run_not_content` (940) — its subject is gone. **Replace it** with a test
  asserting `dirty` appears **nowhere** in the manifest: not in `run`, not in `repo_rev`, not in
  `content()`. That is the guard that keeps the removal from silently regressing.
- `test_content_is_unaffected_by_dirty_when_commit_is_equal` (950) — **keep the property**, it is
  still true and still valuable (two `repo_state` fakes disagreeing on `dirty` must produce
  byte-identical content). Drop only its last line, which asserts the two `run.dirty` values differ.
  Now the whole *manifest* — not just content — should be identical apart from `generated_at`.
  Consider strengthening it that way; say what you chose.
- The `repo_state` fakes (861, 931, 937, 944, 956–957, 965, 974, 1019, 1026) still legitimately
  **supply** `dirty` — that edge's contract is unchanged. Keep them supplying it; that is what proves
  the consumer ignores it. Remove only the assertions *about* `m["run"]["dirty"]`.
- 986, 995 (`assertIsNone(m["run"]["dirty"])`) and 1016 (the git-status oracle) — the assertion has no
  subject. Remove the `dirty` assertion; **keep each test's `commit` assertion**, which is the part
  that still has a subject.
- Class docstring (901–906) — correct the prose.

**Also check `tests/test_context_determinism.py:538–543`.** That test deliberately does *not* assert
which subtree `dirty` lives in, so it should still pass untouched — but its docstring says "`dirty`
moved to `/run`", which is now stale. Correct the prose; do not change the assertions.

### 3. `docs/CHECKLIST_ENGINE_DESIGN.md` — #300's shipped design doc

Two edits, both required:

- **Correct the stale narrative** at lines ~233–246 (the `run.dirty` split paragraph).
- **Add the #300 successor line.** Purpose, in the launch order's words: *so a reader of `main` can
  tell deliberate sequencing from oversight.* The fact to record: **#300 shipped the producer with no
  caller; #305 g1 wired the first one** (`episode_capture.emit_step_manifest`), **and #305 g4 then
  removed `run.dirty` (#327)** once a real caller made the field's behaviour observable. The field
  was not an oversight in #300 and its removal is not a reversal of a mistake — it is what having a
  caller revealed. Say that in the doc's own register (dense, declarative, no bullet-list padding —
  match the surrounding prose).

Also check `docs/CHECKLIST_SCHEMA.md` — I believe its only `context_manifest` mention (line 123) is
about `context_refs` and needs no change. Confirm.

### 4. `scripts/checklist_engine.py:574–621` — `repo_revision()` docstring

**Do not change the function.** Its docstring (lines ~587–599) currently asserts `dirty` "belongs in
the manifest's excluded `run` subtree" and that "the split is made once, at
`context_manifest.build_manifest`'s assembly point." **Both are now false.** Correct them: this
function still returns both fields as a general primitive, and its one manifest consumer now uses
`commit` only. Keep the "absence is normal" paragraph and the no-`subprocess` paragraph as they are.

---

## Acceptance

1. **`dirty` appears nowhere in any produced manifest.** Prove it against a real produced manifest,
   not only a unit fixture.
2. **Full suite green:** `python -m pytest tests/ -q` from the worktree root. Baseline at handoff is
   **1487 passed, 2 skipped, 472 subtests**. Report the actual numbers you get. A drop in the passed
   count that you cannot account for is a finding, not a rounding error.
3. **No stale prose survives.** `git grep -n "run\.dirty"` must return nothing outside `.agent-work/`
   archives and notes. Run it and paste the output.
4. **A regression guard exists** for the removal (item 2 in the test section above).

## Method warnings — these have already cost this issue real time

- **CRLF (#319) bit three commanders.** Worktree files here are **CRLF**; `git show HEAD:<path>`
  returns **LF**. A pattern built for one base matches **zero** sites in the other, **silently**, and
  reads as "applied, still green" — a false result manufactured by tooling. If you mutate a file to
  prove a test goes red, confirm the mutation landed by **blob-OID change** (`git hash-object`) and
  confirm the restore by **blob-OID match**. Raw byte comparison lies across that boundary; the OID
  does not, because the clean filter normalises.
- **Put every restore in a `finally:`, and verify it.** Two of my predecessor's scripts died before
  restoring — one on a cp1252 `UnicodeEncodeError` printing pytest output, one on a **broken pipe
  from `| head`**. Each left the tree mutated. Never pipe pytest output to `head`.
- **Assert the specific assertion, never a non-zero exit.** A wrapper mapping any non-zero to "red"
  also reports red for an import error or a collection failure. Name the assertion you expect.
- **A red-proof is not bound to the revision it proves (#381).** If you red-prove anything, prove it
  **against the file as it will ship** and record the blob OID in your result.

## Out of scope — do not widen

- **#382** (the aliased-import defeat of the AST layer, and `artifact-ref`'s one-element fixture).
  Filed. The reviewer ruled *fix the sentence, not the machinery*, and the Admiral upheld it.
- `checklist_engine.repo_revision()`'s **behaviour**, and its tests in `tests/test_checklist_engine.py`
  (1058–1110). Docstring only.
- `CONTENT_KEYS`.

## Return

Write `.agent-work/issue-305/crew/g4-implement-result.md`. State the suite numbers, the
`git grep -n "run\.dirty"` output, what you chose for the two judgement calls above, and **any place
this handoff was wrong against the tree** — say so plainly and proceed on what the tree shows. My
enumerated line numbers are from a read of the current files; if they have moved, trust the file.
An honest measured negative is a complete deliverable, not a failure.
