# Candidate gate plan: smallest-diff

## Target

`tests/test_checklist_engine.py`, class `CommanderSpineBasisFields` (~line
8543). Replace the whole-repo `HEAD` pin (`PINNED_HEAD`, checked by
`_skip_if_head_moved`) with a pin to the **blob OID** of
`skills/commander/templates/COMMANDER_SPINE.template.json`, and replace the
skip-on-drift behavior with a fail-on-drift behavior. Everything stays
inline in this one class; no new file, script, or helper module.

## Mechanism

Rename the constant and the helper, keep everything else (the three test
methods, `EXPECTED_BASIS`, `_load_spine`) untouched — each test's first line
stays a one-call guard, just calling the renamed method.

```python
SPINE = ROOT / "skills" / "commander" / "templates" / "COMMANDER_SPINE.template.json"
SPINE_REL = "skills/commander/templates/COMMANDER_SPINE.template.json"

# Captured via `git rev-parse HEAD:<path>` at implementation time (g2 dispatch).
# Pins the TEMPLATE'S BLOB, not repo HEAD -- unrelated commits elsewhere
# must not perturb this.
PINNED_BLOB = "<blob-oid-of-template-at-g2-dispatch>"

def _fail_if_template_drifted(self):
    import subprocess
    out = subprocess.run(
        ["git", "rev-parse", f"HEAD:{self.SPINE_REL}"], cwd=str(ROOT),
        capture_output=True, text=True, encoding="utf-8",
    )
    self.assertEqual(out.returncode, 0, out.stderr)
    blob = out.stdout.strip()
    if blob != self.PINNED_BLOB:
        self.fail(
            f"CommanderSpineBasisFields' proof is stale: pinned to blob "
            f"{self.PINNED_BLOB} of {self.SPINE_REL}, current blob is "
            f"{blob} -- the template changed since this test's shape "
            "assumptions were verified. Re-verify EXPECTED_BASIS (and the "
            "rest of this class) against the new template content, then "
            "re-pin by running:\n"
            f"    git rev-parse HEAD:{self.SPINE_REL}\n"
            "and pasting the result into PINNED_BLOB above."
        )
```

Each of the 3 test methods' first line changes from
`self._skip_if_head_moved()` to `self._fail_if_template_drifted()`. No other
line in the class moves. `_skip_if_head_moved` is deleted (its whole-repo
scope is exactly the bug); `_load_spine` and `EXPECTED_BASIS` are unchanged.

## Drift detection and fail wording

Detection: compare `PINNED_BLOB` against `git rev-parse HEAD:<path>`, the
git-native "content OID of this path as committed at HEAD" query — already
a `subprocess` + `git` idiom this file uses elsewhere (`_skip_if_head_moved`
itself, plus other classes in the file that shell out to `git`). This is a
pure content pin: it changes only when the template's bytes change at a
commit, never when any other file in the repo changes.

The fail message (asserted verbatim-enough for a mutation-battery substring
match) must:
- name that the proof is **stale** ("proof is stale"),
- name the pinned vs. current blob OIDs,
- give the exact re-run command (`git rev-parse HEAD:<path>`) as copy-paste,
- say what to do with the output (paste into `PINNED_BLOB`).

That message text *is* the re-verify path under this constraint — no
separate script, doc, or make target is introduced.

## Re-verify path

Exactly the one-liner printed by the failure itself:

```
git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json
```

Whoever next legitimately edits the template runs this after their edit
lands (or against their working commit), reviews `EXPECTED_BASIS` and the
three test bodies against the new template shape by hand, updates them if
the template's `basis` shape changed, and pastes the printed OID into
`PINNED_BLOB`. No script is added; the command is already in the failure
message, so "cheap" here means "one `git` invocation, no new tooling."

## Gate structure in execute.json

Single gate is enough — this is a ~15-line, one-class, one-file change with
no new abstractions to review separately from the implementation:

- `g1-implement`: apply the rename (`PINNED_HEAD`→`PINNED_BLOB`,
  `_skip_if_head_moved`→`_fail_if_template_drifted`), compute the current
  blob OID via `git rev-parse HEAD:<path>` and set it as `PINNED_BLOB`,
  update the 3 call sites, delete the old helper. Evidence: diff + a local
  test run showing the 3 tests GREEN at the current blob.
- `g1-review`: independently re-derive the blob OID, confirm it matches
  `PINNED_BLOB`; confirm the fail message contains the four required
  elements (stale, both OIDs, the exact command, the paste target); run the
  two-direction mutation battery below.
- `g1-integrate`: merge; no separate integrate concerns beyond normal
  merge-and-confirm-green, since nothing outside this one class changed.

(No `g2` needed — the scope doesn't decompose further without padding.)

## Scoring

- **Depth**: high relative to size. It fixes the actual defect (pin
  granularity) rather than papering over symptoms (e.g. widening the skip
  window), and converts a silent-forever-skip failure mode into a loud,
  actionable one.
- **Locality**: maximal — one class, ~4 renamed identifiers, 3 one-line call
  sites, zero new files. Nothing outside `CommanderSpineBasisFields` moves.
- **Seam placement**: the seam is exactly right — a content-hash check at
  the one artifact the tests actually depend on, using the same
  `subprocess`/`git` seam the file already leans on, so it reads as this
  file's existing idiom rather than an import.
- **Testability**: high. The mechanism is directly provable in both
  directions with a single `git` command each (see below), and the fail
  message's required substrings make a mutation-battery assertion cheap and
  precise (no reliance on exit code or exception type alone).

## Mutation battery (prove both directions)

1. **Template-edit → RED**: checkout a scratch copy, mutate one byte of
   `skills/commander/templates/COMMANDER_SPINE.template.json` (e.g. touch
   whitespace) and commit it, so `HEAD:<path>`'s blob OID changes. Run
   `CommanderSpineBasisFields`. Expect: all 3 tests **FAIL** (not skip, not
   error), each failure message containing the substring `"proof is stale"`
   and the literal string
   `"git rev-parse HEAD:skills/commander/templates/COMMANDER_SPINE.template.json"`.
2. **Unrelated commit → GREEN**: on the same scratch copy, commit an
   unrelated change (e.g. append a line to a scratch file outside
   `skills/commander/templates/`) without touching the template. Run
   `CommanderSpineBasisFields`. Expect: all 3 tests **PASS** — `HEAD`
   changed but `HEAD:<path>`'s blob OID did not, so `PINNED_BLOB` still
   matches.
