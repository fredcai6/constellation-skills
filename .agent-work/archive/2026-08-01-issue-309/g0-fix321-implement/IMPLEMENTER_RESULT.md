# IMPLEMENTER_RESULT — g0-fix321-implement (issue-309)

## Completed slice

Fixed issue #321: `resolve_episode_path(episode_id, root)` in
`scripts/apply_episode_delta.py` now validates `episode_id` against the store's own
grammar (`ID_RE.fullmatch`) as the **first** check inside the function, before
`_require_store_layout()` or any filesystem access. A malformed id (including any
`..` path-traversal-shaped id) returns `None` immediately, exactly matching the
function's existing "not found" contract. This is the ONE seam every id-taking
reader (`fetch_episode`, `neighbours`'s anchor fetch, the writer's own
`Transaction.load()`) already routes through, so no other call site needed to
change. `ID_RE`'s own pattern was not touched.

Full plan driven through the checklist engine to completion (`m0-context` →
`m1-red` → `m2-green` → `m3-suite`, all `complete`), session `impl-309-g0-fix321`,
plan file `.agent-work/issue-309/g0-fix321-implement/IMPLEMENTER_PLAN.json`.

## Files changed

### `scripts/apply_episode_delta.py` — `resolve_episode_path()` only

```diff
diff --git a/scripts/apply_episode_delta.py b/scripts/apply_episode_delta.py
index a152af2..2627b45 100644
--- a/scripts/apply_episode_delta.py
+++ b/scripts/apply_episode_delta.py
@@ -720,7 +720,18 @@ def resolve_episode_path(episode_id: str, root: Path) -> Path | None:
     answer: a store that is not there is not a store with no such episode (trap 5), and
     an id present in BOTH directories is a half-retired store, not a choice between two
     copies. The second one is what makes the half-retirement refusal reach fetch and the
-    writer, not only the scanning readers — this seam is the one they share."""
+    writer, not only the scanning readers — this seam is the one they share.
+
+    First check, before anything else touches the filesystem: the id must match the
+    store's own grammar (ID_RE, section 2). A caller-handed id (fetch/neighbours'
+    anchor fetch, and every other reader routed through this seam) is never validated
+    upstream the way a LISTED id is (iter_episode_ids -> _layout_episode_ids runs every
+    filename through episode_id_for() before it becomes a candidate) — without this
+    check, a crafted id containing `..` path-traversal segments would resolve outside
+    episodes/ entirely (issue #321). A malformed id can never legitimately exist, so
+    `None` is the correct, contract-preserving answer here — not a new exception type."""
+    if not ID_RE.fullmatch(episode_id):
+        return None
     _require_store_layout(root)
     found = [
         root / sub / f"{episode_id}.md"
```

### `tests/test_episode_store.py` — one new test class added

Inserted after `QueryFetchTests` (its final test,
`test_fetch_cli_emits_a_deterministic_json_envelope`) and before
`QueryEnumerateTests`. No existing test was moved, renamed, or restructured.

```python
class PathTraversalGuardTests(unittest.TestCase):
    """Issue #321 — resolve_episode_path() is the ONE seam every id-taking reader
    (fetch_episode, neighbours' anchor fetch, the writer's own Transaction.load())
    already routes through. Before this fix it built `root / sub / f"{episode_id}.md"`
    from a caller-handed id with zero format validation, then only checked `.exists()`
    — so a crafted id containing `..` segments could resolve outside episodes/
    entirely and read an arbitrary file that happens to exist at the traversed
    location. This proves the exposure existed AND that the ID_RE.fullmatch() guard
    now closes it — not merely that a not-found id returns None (a well-formed absent
    id already returned None before this fix too, which would be a check that cannot
    fail)."""

    TRAVERSAL_TARGET = ROOT / "SKILL_INDEX.md"

    def setUp(self):
        self.m = load()
        self.q = load_query()
        # Anchored directly under the repo root (dir=str(ROOT)), NOT the system
        # tempdir the other tests' EpisodeStoreTestCase.setUp uses — so a fixed,
        # small number of ".." segments deterministically reaches
        # ROOT/SKILL_INDEX.md regardless of where the OS places its temp
        # directory. self.root is 2 levels below ROOT (ROOT/tmpXXXX/episodes), so
        # root/active is 3 levels below ROOT.
        self.tmp = tempfile.TemporaryDirectory(dir=str(ROOT))
        self.root = Path(self.tmp.name) / "episodes"
        self.m.ensure_store_layout(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_traversal_id_would_have_escaped_the_store_and_the_guard_now_blocks_it(self):
        # 0. The assumption this whole test rests on: a real, tracked file sits at
        #    the repo root. Fail loudly rather than pass vacuously if that ever stops
        #    holding.
        self.assertTrue(
            self.TRAVERSAL_TARGET.exists(),
            f"{self.TRAVERSAL_TARGET} is assumed to exist at repo root for this "
            "adversarial test to be meaningful, but it does not -- pick another "
            "real, tracked file as the traversal target and update this test.",
        )

        episode_id = "../../../SKILL_INDEX"

        # 1. Prove the exposure: joined the OLD (pre-fix) way -- root / sub /
        #    f"{episode_id}.md", with no format check first -- the crafted id
        #    resolves to that real file, outside episodes/ entirely.
        old_style_path = self.root / "active" / f"{episode_id}.md"
        self.assertEqual(old_style_path.resolve(), self.TRAVERSAL_TARGET.resolve())
        self.assertTrue(old_style_path.exists())

        # 2. Prove the fix: the real, current resolve_episode_path() refuses the
        #    same id, for the same root, before returning any path for it. (Pre-fix,
        #    this line does not merely return the wrong Path -- because active/ and
        #    retired/ are same-depth sibling directories, a pure ".."-escape is
        #    symmetric across both branches and instead trips the half-retired
        #    guard, raising EpisodeDeltaError with the escaped path in its message.
        #    That is a second, independent symptom of the identical root cause --
        #    zero input validation -- and the guard below closes both at once.)
        self.assertIsNone(self.m.resolve_episode_path(episode_id, self.root))

        # 3. ...and the seam's caller-facing surface (fetch_episode) refuses it too.
        self.assertIsNone(self.q.fetch_episode(episode_id, self.root))
```

## Test mode satisfied

TDD, red → green, as preferred by the handoff:
- **RED**: new test added, run alone against the unmodified script — FAILED (see
  evidence below). The unguarded `resolve_episode_path()` did not return `None`; it
  raised `apply_episode_delta.EpisodeDeltaError` (a half-retired false-positive —
  see note below), proving no validation existed.
- **GREEN**: fix applied (`ID_RE.fullmatch` guard as the first check), same test run
  again — PASSED. Full suite re-run — green, net +1 test, 0 regressions.

## Evidence produced

**Traversal target existence** (`SKILL_INDEX.md` at repo root):
```
>>> from pathlib import Path; Path('SKILL_INDEX.md').exists()
exists: True
```

**Baseline (before fix), full suite:**
```
$ python -m pytest tests/test_episode_store.py -q
........................................................ [ 52%]
.................................................s                       [100%]
105 passed, 1 skipped, 16 subtests passed in 5.09s
```

**RED — new test alone, against unmodified `resolve_episode_path()`:**
```
$ python -m pytest tests/test_episode_store.py -k PathTraversalGuardTests -v
...
        # 2. Prove the fix: the real, current resolve_episode_path() refuses the
        #    same id, for the same root, before returning any path for it.
>       self.assertIsNone(self.m.resolve_episode_path(episode_id, self.root))
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_episode_store.py:847: in test_traversal_id_would_have_escaped_the_store_and_the_guard_now_blocks_it
scripts\apply_episode_delta.py:731: in resolve_episode_path
    _reject_half_retired({episode_id}, {episode_id})

live = {'../../../SKILL_INDEX'}, archived = {'../../../SKILL_INDEX'}

    def _reject_half_retired(live: set[str], archived: set[str]) -> None:
        ...
        both = sorted(live & archived)
        if both:
>           raise EpisodeDeltaError(
                "half-retired store: " + ", ".join(both)
                + f" exists in BOTH {ACTIVE_DIR}/ and {RETIRED_DIR}/ ..."
            )
E           apply_episode_delta.EpisodeDeltaError: half-retired store: ../../../SKILL_INDEX exists in BOTH active/ and retired/ ...

scripts\apply_episode_delta.py:659: EpisodeDeltaError
=========================== short test summary info ===========================
FAILED tests/test_episode_store.py::PathTraversalGuardTests::test_traversal_id_would_have_escaped_the_store_and_the_guard_now_blocks_it
1 failed, 106 deselected in 0.34s
```

Note on this RED shape: `active/` and `retired/` are same-depth sibling directories
(single path components), so a pure `..`-escape id is structurally symmetric across
both branches of `resolve_episode_path()`'s list comprehension — `root/active/../../../SKILL_INDEX.md`
and `root/retired/../../../SKILL_INDEX.md` normalize to the identical real file. Given a
store with complete layout (both directories present, which `_require_store_layout()`
always requires), the unguarded function therefore does not silently return a wrong
`Path` for this traversal shape — it raises `EpisodeDeltaError` via the half-retired
guard, a second, independent symptom of the same root cause (zero id validation) that
the fix also closes. Close-criterion step 1 (proving the join lands on a real file) is
demonstrated independently via the inline `old_style_path` construction in the test,
per the handoff's explicit instruction to construct that path "inline in the test, not
by disabling the real fix."

**GREEN — same test, with the fix applied:**
```
$ python -m pytest tests/test_episode_store.py -q
........................................................ [ 52%]
..................................................s                      [100%]
106 passed, 1 skipped, 16 subtests passed in 3.97s
```

**Final confirmation run (verbatim, post-fix):**
```
$ python -m pytest tests/test_episode_store.py -q
........................................................ [ 52%]
..................................................s                      [100%]
106 passed, 1 skipped, 16 subtests passed in 4.04s
```

**Net: baseline 105 passed / 1 skipped → post-change 106 passed / 1 skipped. +1 test,
0 regressions.**

## Assumptions used

- `SKILL_INDEX.md` at the repo root was confirmed present via `Path.exists()` before
  being used as the traversal target, per the handoff's requirement to verify this
  rather than assume it.
- The adversarial test could not reuse the existing `EpisodeStoreTestCase.setUp`
  (which anchors its temp store in the system temp directory via
  `tempfile.TemporaryDirectory()`) because the exact traversal depth needed to reach
  `ROOT/SKILL_INDEX.md` from there is unpredictable and OS-dependent. Instead the new
  test class anchors its own temp store directly under the repo root
  (`tempfile.TemporaryDirectory(dir=str(ROOT))`), which makes the `..`-segment count
  fixed and deterministic (3 levels: `root/active` → `episodes` → `tmpXXXX` → `ROOT`).
  This is a new, small `setUp`/`tearDown` in the new test class only — no existing
  fixture or test was changed.
- Interpreted "You may add a small helper if needed" as covering this bespoke
  `setUp`, since the exploit demonstration requires a store position the shared
  `EpisodeStoreTestCase` cannot provide.
- The handoff's illustrative failure mode ("the unguarded function returns the
  traversed Path") turned out not to be exactly what happens for a purely
  `..`-based traversal id (see the RED note above — it raises `EpisodeDeltaError`
  instead, via the half-retired branch, since `active/`/`retired/` are symmetric
  siblings). This does not weaken the demonstration: the exposure itself (step 1,
  the raw join landing on a real file) is proven independently of what the live
  function call does, and the live call's pre-fix behavior (neither `None` nor a
  clean successful read) is itself evidence that no validation existed. Flagging
  this as a workflow-feedback item below rather than treating it as a stop
  condition, since the close criteria's three numbered steps are all satisfied by
  the test as written.

## Stop conditions hit

None. `ID_RE` behaved as documented (`fullmatch` rejects the traversal-shaped id
cleanly); the close-criteria test construction was achievable (with the ROOT-anchored
`setUp` described above); no exposure reachable through a path the handoff didn't
anticipate was found.

## Out-of-scope observations

None identified beyond the workflow-feedback item below. No other call site
constructs an episode path directly (verified: `grep -rn "resolve_episode_path("
scripts/*.py` shows only the definition and the two call sites the handoff already
named — `apply_episode_delta.py`'s own `Transaction.load()` and
`query_episodes.py`'s `fetch_episode`). `neighbours` was not separately grepped by
name but per the handoff's own description it also routes through
`resolve_episode_path()`, which is now fixed at the one seam.

## Workflow feedback

- The handoff's suggested traversal id shape (`"../../SKILL_INDEX"`, 2 levels) and
  its assumed failure mode (a clean wrong-`Path` return) implicitly assumed a store
  position where only one of `active/`/`retired/` would end up "hit" by the escape.
  In this store's actual layout, `active/` and `retired/` are always same-depth
  sibling directories that both physically exist (required by
  `_require_store_layout()`), so ANY pure `..`-escape id is structurally symmetric
  across both directories and instead trips the half-retired guard
  (`EpisodeDeltaError`), not a silent single-`Path` return. This doesn't change the
  fix or weaken the test (the exposure is proven via inline construction, per the
  handoff's own alternate instruction), but a future handoff writer describing this
  seam's traversal exploit might want to note the half-retired-collision wrinkle so
  the next implementer doesn't spend time reconciling the expected vs. actual RED
  failure text.
- No `docs/agents/CREW_CONTEXT.md` or `docs/agents/GLOSSARY.md` exist in this
  worktree — per doctrine this degrades gracefully to global-only context, which is
  what was used.
- `config_ref` in the plan template pointed at `docs/agents/engine-config.json`,
  which does not exist in this worktree; set to `null` in the instantiated plan
  (matching the precedent in `.agent-work/archive/20260708-issue-87/.../IMPLEMENTER_PLAN.json`),
  and the engine ran without needing it.

## Map Impact

- **Structural:** `scripts/apply_episode_delta.py:704 resolve_episode_path()` —
  function body grew by one guard clause (`if not ID_RE.fullmatch(episode_id): return
  None`) plus docstring addition; signature and return contract (`Path | None`)
  unchanged.
- **Capability:** episode store fetch/retrieval path — now validates every
  caller-handed id against the store's grammar before any filesystem access; no
  change to callers (`fetch_episode`, `neighbours`'s anchor fetch, the writer's own
  `Transaction.load()`) was required, confirming the seam-only fix held.
- **Constraints/assumptions:** #321 resolved — the store now validates ids it is
  handed, not only ids it lists. `decision:fix-321-at-the-seam` executed exactly as
  ruled (single-function fix, no caller changes).
- **Evidence:** `PathTraversalGuardTests` in `tests/test_episode_store.py`, proving
  the guard fires (not merely that a not-found id returns `None`).
