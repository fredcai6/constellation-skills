# Candidate gate plan: best-seam-placement

## Target

`tests/test_checklist_engine.py`, class `CommanderSpineBasisFields` (~line
8543). Same defect as every candidate: whole-repo `PINNED_HEAD` +
`_skip_if_head_moved` must become a blob-OID pin that FAILs on drift. This
candidate's differentiator: the pin/drift/message mechanism is factored out
of the class into small, independently invocable module-level functions, so
the re-verify path is a *thing you run*, not just prose inside a failure
string.

## Precedent found

The file already has a module-level helpers area right after the imports
(`load_engine`, `gate`, `gated`, `survey_item`, lines ~18-60) that every
later `TestCase` class imports/calls — not a base class, not a separate
file. That is this file's established seam for shared test infrastructure,
and it is where this candidate's helpers go (appended near the end of that
block, or just above `RepoRevision`/`CommanderSpineBasisFields`, whichever
review prefers). There is also a same-shape oracle precedent:
`RepoRevision`/`tests/test_context_manifest.py`'s `rev()` both shell out to
`git hash-object`/`git rev-parse` via a small `_git()` helper — confirming
"subprocess + git rev-parse, wrapped in a small named function" is already
this codebase's idiom, not a new import surface.

**Landmine found, avoided:** line 1581 has a pre-existing, mid-file
`if __name__ == "__main__": unittest.main()` (dead relative to the file's
true end at line 8650 — a merge artifact, out of this mission's scope to
fix). Because Python executes top-to-bottom, running
`python tests/test_checklist_engine.py` directly hits that block first and
`sys.exit()`s before any code after it — including a new class or a new
`__main__`-guarded CLI block appended at the bottom — ever runs. So the
re-verify entry point below is a **plain importable function**, not a
`__main__`/argparse dispatch, deliberately sidestepping that landmine
instead of touching it.

## Mechanism

```python
# --- shared blob-oid pin helpers ------------------------------------------
# Any TestCase that pins its proof to one file's CONTENT (not whole-repo
# HEAD) reuses these instead of hand-rolling subprocess + a skip/fail
# message. Placed beside this file's other module-level test helpers.

def blob_oid(rel_path, root=ROOT):
    """Git's current blob OID for rel_path at HEAD. Raises on git failure."""
    import subprocess
    out = subprocess.run(
        ["git", "rev-parse", f"HEAD:{rel_path}"], cwd=str(root),
        capture_output=True, text=True, encoding="utf-8",
    )
    if out.returncode != 0:
        raise RuntimeError(f"git rev-parse HEAD:{rel_path} failed: {out.stderr}")
    return out.stdout.strip()


def reverify_pin(rel_path, root=ROOT):
    """THE re-verify entry point. Recomputes rel_path's current blob OID and
    prints the exact line to paste over a stale pin. Run directly:
        python3 -c "import sys; sys.path.insert(0, 'tests'); \
            import test_checklist_engine as t; t.reverify_pin(
            'skills/commander/templates/COMMANDER_SPINE.template.json')"
    """
    oid = blob_oid(rel_path, root)
    print(f"current blob OID for {rel_path}: {oid}")
    print(f'    PINNED_BLOB = "{oid}"')
    return oid


def assert_blob_pin_current(testcase, rel_path, pinned_oid, pin_name="PINNED_BLOB"):
    """Fail testcase (never skip) if rel_path's committed content has
    drifted from pinned_oid. Shared stale-proof wording."""
    current = blob_oid(rel_path)
    if current != pinned_oid:
        testcase.fail(
            f"{testcase.__class__.__name__}'s proof is stale: {pin_name} is "
            f"pinned to blob {pinned_oid} of {rel_path}, but the committed "
            f"content is now blob {current}. Re-verify this class's "
            f"assumptions against the new content, then re-pin by running:\n"
            f"    python3 -c \"import sys; sys.path.insert(0, 'tests'); "
            f"import test_checklist_engine as t; "
            f"t.reverify_pin({rel_path!r})\"\n"
            f"and paste the printed {pin_name} line into this class."
        )
```

`CommanderSpineBasisFields` shrinks to:

```python
class CommanderSpineBasisFields(unittest.TestCase):
    SPINE_REL = "skills/commander/templates/COMMANDER_SPINE.template.json"
    SPINE = ROOT / SPINE_REL
    PINNED_BLOB = "<blob-oid-of-template-at-g1-dispatch>"

    def _check_pin(self):
        assert_blob_pin_current(self, self.SPINE_REL, self.PINNED_BLOB)
```

Each of the 3 test methods' first line becomes `self._check_pin()`.
`_skip_if_head_moved` and `PINNED_HEAD` are deleted.

## Drift detection and fail wording

Same comparison as the smallest-diff candidate (`blob_oid(SPINE_REL) !=
PINNED_BLOB`), but the comparison and the message live in
`assert_blob_pin_current`, not inlined in the class — so any *future* class
that needs "pin content, fail on drift" (this repo will likely grow more of
these as more templates get frozen-content tests) reuses the same function
instead of copy-pasting a fifth `_skip_if_*`/`_fail_if_*` variant. The
message names "proof is stale", both OIDs, and the exact `reverify_pin`
invocation — a runnable command, not just a `git rev-parse` fragment to
retype by hand.

## Re-verify path (the discoverable/invokable angle)

Whoever legitimately edits the template runs, from repo root:

```
python3 -c "import sys; sys.path.insert(0, 'tests'); \
    import test_checklist_engine as t; \
    t.reverify_pin('skills/commander/templates/COMMANDER_SPINE.template.json')"
```

This is `reverify_pin` used exactly as the module was already built to be
loaded (mirrors the file's own `load_engine()`-via-`importlib` pattern for
reaching code outside the test tree — here it's simpler because
`test_checklist_engine.py` needs no `importlib.util` gymnastics, just a
`sys.path` insert, since it has no package `__init__.py`). It prints the
current blob OID and a ready-to-paste `PINNED_BLOB = "..."` line. Cheap: one
Python one-liner, no new script file, no new dependency — and unlike the
smallest-diff candidate, it's a *named, importable, independently callable*
function rather than a command string that only exists inside a failure
message, so it's discoverable by reading the module's top-level functions
even without ever triggering a failure first.

## Gate structure in execute.json

Single gate, same reasoning as smallest-diff — the added surface (three
small functions + one shrunk class) is still well under what justifies
`g1`/`g2` decomposition:

- `g1-implement`: add `blob_oid`/`reverify_pin`/`assert_blob_pin_current` to
  the module-helpers area; shrink `CommanderSpineBasisFields` to use them;
  run `reverify_pin(SPINE_REL)` once to populate `PINNED_BLOB`. Evidence:
  diff + local test run, 3 tests GREEN.
- `g1-review`: independently re-derive the blob OID; confirm
  `assert_blob_pin_current`'s message contains the four required elements;
  confirm `reverify_pin` is actually invocable standalone (run the `python3
  -c` command above from a clean shell, not just read the source); run the
  two-direction mutation battery below.
- `g1-integrate`: merge; confirm nothing outside `test_checklist_engine.py`
  changed (file-ownership constraint).

## Scoring

- **Depth**: equal to smallest-diff on the core fix (same comparison,
  same FAIL-not-skip correction); adds durability — the next class that
  needs this pattern doesn't re-derive it.
- **Locality**: slightly wider than smallest-diff (new module-level names
  instead of purely class-local ones) but still one file, ~35 new lines,
  zero new files — stays inside the `tests/test_checklist_engine.py`-only
  ownership boundary flagged in the launch order.
- **Seam placement**: this candidate's strength. The helpers land exactly
  where this file already keeps shared test infrastructure (the
  `load_engine`/`gate`/`gated` block), matching an established pattern
  instead of inventing a new one, and stay independent of any one test
  class — which is what makes `reverify_pin` runnable on its own rather
  than baked into one class's internals.
- **Testability**: high, same as smallest-diff for the FAIL-message
  substring checks, plus one more directly testable unit: `reverify_pin`
  and `blob_oid` are themselves plain functions a reviewer (or a future
  test) can call and assert on in isolation, without going through
  `CommanderSpineBasisFields` at all.

## Scope risk flagged

The constraint asks to consider a "tiny helper module" if there's clear
precedent for test-support helpers living outside the test file. There
isn't clear precedent for that here (no `tests/helpers.py` or similar
exists), and file ownership this wave is `tests/test_checklist_engine.py`
ONLY — so this plan keeps the helpers in-file. A genuinely separate helper
module is flagged as out of scope, not proposed.

## Mutation battery (prove both directions)

1. **Template-edit → RED**: on a scratch copy, mutate one byte of
   `skills/commander/templates/COMMANDER_SPINE.template.json` and commit,
   changing `HEAD:<path>`'s blob OID. Run `CommanderSpineBasisFields`.
   Expect: all 3 tests **FAIL** (not skip, not error), each message
   containing the substring `"proof is stale"` and the literal substring
   `"t.reverify_pin("` (proving the re-verify command, not just a bare
   `git rev-parse`, is what's surfaced).
2. **Unrelated commit → GREEN**: on the same scratch copy, commit a change
   to a file outside `skills/commander/templates/`. Run
   `CommanderSpineBasisFields`. Expect: all 3 tests **PASS** — `HEAD` moved,
   `HEAD:<path>`'s blob OID did not.
3. **Helper standalone check**: run `reverify_pin(SPINE_REL)` directly (the
   `python3 -c` invocation above) against the unmutated scratch copy and
   assert its printed OID equals `PINNED_BLOB` — proving the re-verify path
   is actually invocable outside of a test failure, not just referenced in
   one.
