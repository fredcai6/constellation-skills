# Implementation Result

## Assigned gate
`issue-305 g1 — the assembly seam: make the #300 context manifest a byproduct of starting a spine step`

> **Run note:** this result covers ONE job file driven by TWO agents. The first implementer
> died on a session usage limit partway through `m3-seam` (work committed at `fba7fae`, nothing
> lost). This agent cold-started from the job file's `current`, force-claimed the stale
> `impl-305-g1` lease, and drove `m3` → `m4` → `m5` to done. Milestones `m0`–`m2` are the
> predecessor's; their evidence is in the plan file's journal, and I re-verified their output
> by running the whole file rather than trusting the recorded green.

## Completed slice

The manifest is now **emitted by the act of activating a step**. Nothing calls a "write the
manifest" step, and there is no verb, flag, or agent instruction that produces one — which is
exactly `decision:manifest-is-a-byproduct`.

The seam sits on `start()` and `reopen()`, the only two sites in `checklist_engine.py` that
assign `status = "in-progress"`, which `advance()` requires. That is what makes it
unskippable **without** touching the shared `dispatch()` chokepoint two other live commanders
are running through.

## Scope

**Files changed (vs base `967493c`):**
- `scripts/episode_capture.py` — **NEW**, 229 lines. All logic lives here. (predecessor's, `fba7fae`; unchanged by me)
- `scripts/checklist_engine.py` — the seam wiring only (see the full diff below)
- `tests/test_episode_capture.py` — **NEW**, 33 tests. (predecessor's; I corrected one test and added one)

**Specific exclusions touched:** **no.** `apply_episode_delta.py`, `query_episodes.py`,
`context_manifest.py`, `dispatch()`, `main()`, and `run.dirty` are all untouched. No CLI flag
for roots was added. Verified: `git diff --name-only 967493c` lists only the three files above
plus `.agent-work/` run artifacts.

## Behavior changed

**Yes.** `start` and `reopen` now write `<agent-work>/<work-id>/context/<step>.json` as a
side effect. No verb's exit code, stdout, or stderr changes — proven below against the
pre-seam engine, not merely asserted.

---

## The engine diff — read this one closely

The gate's close criterion says *"an import plus two call sites. Nothing else."* The real diff
is **an import plus two call sites plus two lines of pure plumbing**, and I am flagging that
rather than letting a reviewer discover it:

```
$ git diff 967493c -- scripts/checklist_engine.py
 scripts/checklist_engine.py | 20 ++++++++++++++++++--
 1 file changed, 18 insertions(+), 2 deletions(-)

@@ -22,6 +22,18 @@ import sys
 from datetime import datetime, timedelta, timezone
 from pathlib import Path, PureWindowsPath

+sys.path.insert(0, str(Path(__file__).resolve().parent))
+try:
+    # The context-manifest assembly seam (#305). Imported here so `start`/`reopen`
+    # can emit; the sidecar is NOT bundled into every engine-carrying skill
+    # (install_constellation.SKILL_SCRIPT_BUNDLES), so its absence degrades to a
+    # no-op rather than breaking the engine — the same "absence is normal, never
+    # raise" rule the manifest producer itself follows.
+    from episode_capture import emit_step_manifest  # noqa: E402
+except ImportError:  # pragma: no cover — only reachable from a partial install
+    def emit_step_manifest(*_args, **_kwargs):  # type: ignore[misc]
+        return None
+

@@ -1633,6 +1645,7 @@ def start(cl: dict, iid: str, base_dir: Path | None = None) -> str:
     t["status"] = "in-progress"
+    emit_step_manifest(cl, iid, base_dir)  # #305: AFTER the mutation — active_id() picks the step.
     return f"{iid} -> in-progress"

@@ -1820,7 +1833,8 @@ def _supersede_evidence(t: dict, iid: str, reason: str) -> None:
-def reopen(cl: dict, iid: str, reason: str, cap: int | None = None) -> str:
+def reopen(cl: dict, iid: str, reason: str, cap: int | None = None,
+           base_dir: Path | None = None) -> str:

@@ -1850,6 +1864,7 @@ def reopen(...)
     t["rework_count"] = t.get("rework_count", 0) + 1
     t["status"] = "in-progress"
+    emit_step_manifest(cl, iid, base_dir)  # #305: AFTER the mutation — active_id() picks the step.
     t.setdefault("status_detail", {})["reopen_reason"] = reason

@@ -2445,7 +2460,8 @@ def _run_verb(cl: dict, args: argparse.Namespace, base_dir: Path | None) -> str:
     if v == "reopen":
-        return reopen(cl, args.id, args.reason, cap=rework_cap(load_config(cl, base_dir)))
+        return reopen(cl, args.id, args.reason, cap=rework_cap(load_config(cl, base_dir)),
+                      base_dir=base_dir)
```

**Why the two extra lines exist and why I judged them unavoidable.** `reopen()` had **no
route at all** to the checklist's on-disk location — unlike `start()`, which already took
`base_dir`. Without `base_dir`, `emit_step_manifest` returns `None` and writes nothing, so
`reopen` could not emit. The three options were:

1. Thread `base_dir` through as a keyword — 2 lines, no state, mirrors `start()` exactly. **Chosen.**
2. A module-level global holding the current file — hidden mutable state in a module three
   commanders are concurrently executing. Worse.
3. Emit from `dispatch()` / `_run_verb` after `reopen()` returns — **explicitly excluded** by
   the handoff, and it would put step-selection logic in the verb router.

**No logic entered the engine.** The engine gained an import, two one-line calls, and a
keyword argument. Every decision — which roots, where the file lands, write-if-absent,
fail-soft, the failure stub — is in `scripts/episode_capture.py`. If the Commander reads the
close criterion strictly, this is the one place to rule; I did not amend the criterion to fit
what I did.

---

## Evidence — pasted, not summarized

### 1. Full suite

```bash
cd "C:/Programs/constellation-skills-wt/e298-305" && python -m pytest tests/ -q
```
```
1435 passed, 2 skipped, 409 subtests passed in 69.78s (0:01:09)
```
**Result: pass.** (Note: 1435, not the ~1160 the brief expected — the suite has grown.)

CI's pinned interpreter has no pytest, so the closest available check there is an import:

```bash
$ py -c "import sys; sys.path.insert(0,'scripts'); import checklist_engine as e; ..."
engine imported OK on 3.12.13
emit_step_manifest -> episode_capture
reopen signature  -> (cl: 'dict', iid: 'str', reason: 'str', cap: 'int | None' = None, base_dir: 'Path | None' = None) -> 'str'
```
**Neither local interpreter reproduces CI. This green is not the gate.**

### 2. Required: the three resolved root tokens, from a real run

```bash
$ py scripts/episode_capture.py
{
  "skill": "C:\\Programs\\constellation-skills-wt\\e298-305",
  "repo": "C:\\Programs\\constellation-skills-wt\\e298-305",
  "durable": "C:\\Programs\\constellation-skills-wt\\e298-305"
}
```
All three coincide *here* because this repo IS the skill checkout and the worktree holds an
active Admiral epic lease (so `durable_root` correctly returns `start`). That coincidence is
precisely why the root tests use adversarial temp fixtures where the three **must** differ —
see §5.

### 3. Required: a manifest from a real `start`, with a non-null `rev`

Real engine CLI, temp git repo, a declaration covering `repo` + `durable` + a deliberately
absent file:

```bash
BEFORE start: manifest exists? False
$ engine start g1   -> exit 0  g1 -> in-progress
AFTER  start: manifest exists? True
```
```json
{
  "contract": 1,
  "step": "g1",
  "files": [
    { "root": "repo",    "path": "docs/agents/ORCHESTRATOR_CONTEXT.md", "rev": "90c4d51fa74e765acfb39a4fa781be9ec7421a4a" },
    { "root": "durable", "path": ".agent-work/LESSONS.md",              "rev": "9bacc2c2fb8f53b6e3607fe3238ef4b07f167fd5" },
    { "root": "repo",    "path": "docs/agents/DOES_NOT_EXIST.md",       "rev": null }
  ],
  "repo_rev": { "commit": "175a7ba3a31b079c504dfc0b65a34d11a3be0d46" },
  "run": {
    "work_id": "demo",
    "generated_at": "2026-08-02T02:22:22Z",
    "dirty": true,
    "roots": {
      "skill": "C:/Programs/constellation-skills-wt/e298-305",
      "repo": "C:/Users/fredc/AppData/Local/Temp/tmpetwk_d1v",
      "durable": "C:/Users/fredc/AppData/Local/Temp/tmpetwk_d1v"
    },
    "host": { "platform": "win32", "python": "3.14.3", "cwd": "C:/Programs/constellation-skills-wt/e298-305" }
  }
}
```

**The `durable` row is the double-nesting trap, disarmed and proven disarmed.** The one shipped
`durable` declaration `.agent-work/LESSONS.md` carries a **non-null rev**. Had the root been
`durable_agent_work()`, that path would have resolved to
`<root>/.agent-work/.agent-work/LESSONS.md`, which does not exist, and the row would read
`rev: null` — structurally valid, plausible-looking, and silently wrong. The non-null hash is
the discriminator.

### 4. Required: before/after showing write-if-absent

Same manifest, then the declaration is swapped underneath it and the gate is driven back to
`in-progress` a second time via a real `reopen`:

```
write-if-absent BEFORE  sha256: 61260fc0d77f26cf3f54b66ee776e2918276e65261c904c12da6de5aa7b88416
                        mtime : 1785637342465344100

$ engine reopen g1  -> exit 0  g1 reopened (rework 1/3)

write-if-absent AFTER   sha256: 61260fc0d77f26cf3f54b66ee776e2918276e65261c904c12da6de5aa7b88416
                        mtime : 1785637342465344100

BYTES IDENTICAL (snapshot not rewritten): True
still records the ORIGINAL declaration: ['docs/agents/ORCHESTRATOR_CONTEXT.md', '.agent-work/LESSONS.md', 'docs/agents/DOES_NOT_EXIST.md']
CRLF anywhere in the manifest: False
```

Not a byte comparison of two things that might both be absent: the file demonstrably existed
with that hash before, the declaration underneath it demonstrably changed, and the manifest
still names the **original** three paths. That is what makes the `<manifest-ref>@<revision>`
pin honest for g2.

### 5. Required: the three fail-soft exit codes — proven UNCHANGED, not merely observed

Comparing exit codes to nothing proves nothing, so I extracted the **pre-seam engine** from
`967493c` and ran every case through both binaries side by side:

```
case                         verb                        base(967493c)  with-seam
------------------------------------------------------------------------------------
1 fully-terminal checklist   current                                 0          0  SAME
1 fully-terminal checklist   start g1                                1          1  SAME
1 fully-terminal checklist   advance g1                              1          1  SAME
2 unmapped root token        current                                 0          0  SAME
2 unmapped root token        start g1                                0          0  SAME
3 not a git repository       current                                 0          0  SAME
3 not a git repository       start g1                                0          0  SAME
4 malformed declaration      current                                 0          0  SAME
4 malformed declaration      start g1                                0          0  SAME
5 reopen a complete gate     reopen g1 --reason rework               0          0  SAME
------------------------------------------------------------------------------------
ALL EXIT CODES UNCHANGED: True
```

And the fail-soft case is **not silent**. Case 2, in full:

```
$ engine start g1   -> exit 0   stdout='g1 -> in-progress'
  stderr             -> ''
  gate status        -> in-progress
  stub written       -> True
```
```json
{
  "step": "g1",
  "files": null,
  "emit_error": {
    "error": "DeclarationError",
    "message": "unknown root token 'vendor'; expected one of ('skill', 'repo', 'durable')"
  },
  "run": { "work_id": "wk", "generated_at": "2026-08-02T02:19:04Z" }
}
```

The verb succeeded, said nothing about the failure, and the failure is still on disk.

### 6. The seam dogfooded itself, unasked

While driving **this very plan file** through the wired engine, the seam emitted manifests for
my own milestones. I did not invoke anything to produce these; they are the byproduct:

```
.agent-work/issue-305/issue-305-g1-implement/context/m4-failsoft.json
.agent-work/issue-305/issue-305-g1-implement/context/m5-suite.json
```
```json
{
  "contract": 1,
  "step": "m5-suite",
  "files": [],
  "repo_rev": { "commit": "fba7faea081d7e15a0f6e9e8e1e238841cc01368" },
  "run": { "work_id": "issue-305-g1-implement", "generated_at": "2026-08-02T02:20:04Z", "dirty": true, ... }
}
```

`files: []` is correct and is the *real* reading here: my plan's tasks declare no
`context_refs`. Note there is **no** `m3-seam.json` — I resumed into `m3` already in-progress
and never ran `start m3-seam`. The absence is accurate, which is the whole point of §7.

---

## Test mode

**Required:** test-first (TDD). **Satisfied: yes**, with one honest caveat recorded below.

### TDD evidence — m3 (the seam)

Failing test observed on resume, before wiring `reopen()`:
```bash
$ python -m pytest tests/test_episode_capture.py -q -k seam
FAILED tests/test_episode_capture.py::Seam::test_seam_reopen_emits_the_manifest_too
E  AssertionError: False is not true : no manifest at ...\.agent-work\wk\context\g1.json
1 failed, 5 passed, 22 deselected
```
Passing after wiring:
```bash
$ python -m pytest tests/test_episode_capture.py -q -k seam
6 passed, 22 deselected in 1.47s
```

### 7. TDD evidence — m4, and the test that was wrong

The second standing red was **not** missing behavior. `test_failsoft_swallows_an_arbitrary_producer_crash`
asserted `emit_step_manifest(...) is None` on a producer crash:

```
E  AssertionError: WindowsPath('.../.agent-work/wk/context/g1.json') is not None
```

That assertion encodes the **superseded fail-silent contract**. The adjudicated contract
(ruling D8, `PLAN_CRITIC_DISPOSITION.md`) is that a failed emit is fail-soft but **never**
fail-silent: a vanished manifest is indistinguishable from a step nobody started. **The test
was wrong, not the implementation.** I rewrote it to the real contract rather than weakening
it — it now asserts the emit returns a path, the file exists, `emit_error` carries the
exception type, and `files` is `null`.

I also added `test_stub_files_null_is_not_the_same_reading_as_empty_files`, which pins the
collision the whole design turns on: `files: []` means *"this step declared no context refs"*
(a complete reading), `files: null` means *"the record could not be taken"* (no reading at
all). Both are produced from real emits and both are read, so it cannot pass on an
empty-vs-empty coincidence — and it pins the trap explicitly, that **both values are falsy**,
so any consumer discriminating on truthiness loses the distinction:

```python
self.assertFalse(bool(real["files"]))     # []   is falsy
self.assertFalse(bool(stub["files"]))     # null is falsy
self.assertNotEqual(real["files"], stub["files"])
self.assertIsNot(real["files"], None)
```

**Both new tests passed on their first run, which is not evidence of anything.** A check that
cannot fail is indistinguishable from one that passed, so I mutation-tested them:

| mutant | change | killed |
|---|---|---|
| A | stub writes `"files": []` instead of `None` | **3 tests** — `..._crash_leaves_a_stub_not_silence`, `..._null_is_not_the_same_reading...`, `..._records_the_failure...` |
| B | failed emit returns `None` (fail-silent) | **4 tests** — the three above plus `..._distinguishable_from_a_real_manifest...` |

Both mutants reverted. `git status` confirms `scripts/episode_capture.py` is byte-identical to
`fba7fae` — the only modified script is `checklist_engine.py`.

Refactor while green: no.

## Docs/contracts touched
- None. `context_manifest.py`'s contract is consumed, not changed. `EPISODE_STORE.md` untouched.

## Assumptions
- `build_manifest()` deliberately offers **no** step override — it selects via the engine's own
  `active_id()`. The seam is therefore correct only where `active_id(cl) == iid` after the
  mutation. For `start()` the engine already guarantees this (gated `start` refuses a non-active
  gate). For `reopen()` it holds because the reopened gate becomes the earliest non-terminal
  item. See the one edge case under Out-of-scope observations.
- `install_constellation.SKILL_SCRIPT_BUNDLES` does not ship `episode_capture.py` with every
  engine-carrying skill, which is why the import is guarded. **I did not verify whether it
  should now be added to a bundle** — flagged below.

## Stop conditions hit
- **None of the three named stop conditions fired.** The seam is unskippable (the premise is
  re-verified by `SeamPremise::test_seam_only_start_and_reopen_assign_the_in_progress_status`,
  which fails if a third assignment site ever appears). The engine diff stayed at two call
  sites plus two plumbing lines. Fail-soft and not-silent did **not** conflict — the stub
  resolves them cleanly.

## Out-of-scope observations (triage candidates)

1. **`install_constellation.py` may need `episode_capture.py` bundled.** The engine's import
   is guarded so a partial install degrades to a silent no-op — which is safe, but it means
   **any installed skill that ships `checklist_engine.py` without `episode_capture.py` emits no
   manifests at all, and nothing says so.** That is a fail-silent hole at the *packaging*
   layer, exactly the shape ruling D8 forbids at the runtime layer. Out of scope here; worth an
   issue.
2. **`reopen` + a non-terminal earlier gate.** If an item *earlier* than the reopened gate is
   `blocked` (non-terminal), `active_id()` returns that earlier gate and the manifest is
   recorded for it instead. The record is not false — it describes the genuinely active step —
   but it is not the reopened one. Unreachable through normal gated flow. Not fixable here
   without adding logic to the engine or a step override to the frozen `build_manifest`.
3. **`m0`'s recorded nuance is worth carrying forward:** `resume()` also lands a task in
   `in-progress` via `t["status"] = prior`, but only restores a status the gate already held,
   so every path to `advance` still passes `start`/`reopen` at least once. The premise holds,
   but a future refactor of `resume()` could break it without tripping the literal-assignment
   guard test.

## Map Impact
- **Structural anchors touched:** `scripts/episode_capture.py` — new module, sits between
  `checklist_engine` (caller) and `context_manifest` (producer). `scripts/checklist_engine.py`
  — `start()`/`reopen()` gained an emit; `reopen()` gained `base_dir`.
- **Capabilities added:** *context manifest emitted as a byproduct of step activation.*
  Observable as `<agent-work>/<work-id>/context/<step>.json` after any `start`/`reopen`.
- **Constraints touched:** fail-soft (no verb's exit code may move) — **honored and measured**
  against the pre-seam binary. Write-if-absent — **honored**, and now load-bearing for g2's
  `<manifest-ref>@<revision>` pin.
- **Decisions:** `decision:manifest-is-a-byproduct` — implemented as adjudicated. One forced
  choice needing Commander's eye: the two plumbing lines vs. the literal "nothing else"
  criterion (see the engine-diff section).
- **Trust limitations:** the import cycle (`context_manifest` → `checklist_engine` →
  `episode_capture`) is broken by a function-local import inside `emit_step_manifest`. That is
  a real constraint on the dependency graph and a future refactor could re-close the cycle.

## Workflow Feedback

- **Handoff gaps:** *(a) The close criterion "an import plus two call sites. Nothing else"* was
  **not achievable as literally written**, and nothing in the handoff acknowledged it. `reopen()`
  has no `base_dir` in its signature, so it physically cannot reach the checklist's location.
  Whoever wrote the criterion checked `start()` (which does take `base_dir`) and generalized.
  A criterion the implementer must quietly exceed is worse than one stated with its exception:
  *"an import, two call sites, and whatever argument-threading `reopen` requires — no logic."*
  *(b)* The handoff cites line numbers `:1635`/`:1852`, which had **already drifted** to
  `:1647`/`:1865` by the time I got here. Cite the symbol, not the line.
- **Context rediscovered:** The predecessor's death left **no note** distinguishing "this test
  is red because the feature is missing" from "this test is red because it asserts the wrong
  contract." My dispatcher had to hand-verify that and tell me. That verification should be a
  *durable artifact* the job file carries, not a message that dies with the session — a
  `finding` on the in-progress task would have carried it.
- **Instructions improvised around:** The skill says to build a plan from the template and claim
  the lease as the **first command**. For a *resume*, that is exactly wrong — the plan already
  exists and rebuilding it would destroy the journal. The correct move (force-claim the stale
  lease, then `current`) came from my dispatcher's brief, not from the skill. **The
  `constellation-implementer` skill has no resume path**, and a resuming agent that follows it
  literally will overwrite its predecessor's work. This is the single highest-value fix here.
- **What would have made this easier:** A one-line resume clause in the implementer skill:
  *"If a gated plan file already exists at your plan path, do NOT instantiate — force-claim its
  lease and cold-start from `current`."* Everything else in this run was smooth; the engine's
  RAIL output in particular did its job, and the "you are N steps from done" counter is what
  kept me from stopping at the code change.

## Return status
`complete`
