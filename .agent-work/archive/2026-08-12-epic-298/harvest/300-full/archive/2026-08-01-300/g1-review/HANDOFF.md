# Reviewer Handoff

## Gate

`g1-review` (issue #300, epic-298). Worktree root: `C:/Programs/constellation-skills-wt/298-300`.
Absolute paths everywhere — your cwd resets between bash calls.

## Task statement

Independently verify gate `g1`: the deterministic projection substrate and its manifest. The
implementer's handoff (the frozen spec it was held to) is at
`.agent-work/300/g1-implement/HANDOFF.md`; its result is at
`.agent-work/300/g1-implement/IMPLEMENTER_RESULT.md`. Read the handoff **first** so you review
against the contract rather than against your own taste.

## How to inspect the diff

```bash
cd C:/Programs/constellation-skills-wt/298-300
git status --short          # 3 new files are UNTRACKED, not in git diff
git diff                    # shows exactly 1 modified file (the spine template, +8 lines)
```

Files: **new** `scripts/context_manifest.py`, `tests/test_context_manifest.py`,
`tests/test_context_determinism.py`, `tests/fixtures/context_declarations.json`; **modified**
`skills/commander/templates/COMMANDER_SPINE.template.json`.

`.agent-work/300/context/*.json` is **intentionally gitignored** — Tommy ruled the manifest lives
under `.agent-work/`. Do **not** expect it in the diff, and do not report its absence as a defect.

## Hunt these specific classes — do not just re-run the suite

The suite is green in the Commander's hands already (1209 passed, 2 pre-existing unrelated skips).
Re-running it proves nothing new. Your value is in the classes below.

**1. Round-trip blindness — the primary hunt.** A test that parses the real shipped corpus proves the
**corpus is clean**, not that the **tool is correct**; bugs unreachable from real artifacts pass
silently. Author your **own** adversarial fixtures aimed at making the tool return a **wrong** answer
— a false FAIL on valid input, or a silent PASS on invalid input. Do not accept the implementer's
fixtures as sufficient evidence that this class was covered; they were written by the same mind that
wrote the code.

**2. The identity function is the worst failure mode in this design.** `rev()` must equal
`git hash-object` for every real case in this repo. A silently-wrong hash produces plausible output
forever and is undetectable by inspection. Verify it yourself against files you choose — including a
CRLF file, a file with no trailing newline, an empty file, a UTF-8 file with non-ASCII bytes, and a
large file. Technique that avoids mutating the file under review: load the module by path with
`importlib` and call `rev` directly.

**3. A latent silent-skip in the acceptance test.** `tests/test_context_determinism.py` raises
`unittest.SkipTest` when `git worktree add` fails. All 7 tests genuinely ran here — I verified with
`-v` rather than trusting the count. But in an environment where worktree creation fails, **the
issue's single acceptance test would skip and the gate would still look green.** Judge whether that
is an acceptable degradation or should be a hard failure, and say which. This is your call to make,
not mine.

**4. Does the determinism test still test what it claims?** The implementer changed approach
mid-flight after finding two false-greens: a clean checkout at `HEAD` would have compared two copies
of *old* code (the change is uncommitted), and in a bare source checkout every declared row resolved
to `rev: null`, making byte-identity trivially true. The fix overlays working-tree copies onto both
checkouts. **Confirm the result is still two genuinely distinct environments** and that the
comparison is non-vacuous — i.e. that it would actually fail if the producer became
environment-dependent. Try to make it fail.

**5. The exclusion set must be exactly `/run`.** Content byte-identity is asserted with everything
except the `run` subtree excluded. Confirm nothing else is masked. If any other field has to be
excluded for the test to pass, that field is in the wrong subtree and the **design** is wrong.

**6. One selector, not two.** `constraint:extend-dont-parallel` requires the producer to reuse the
engine's existing `active_id()`. Confirm it is imported, not reimplemented, and that no second
selection path exists.

**7. Scope discipline.** Confirm nothing widened toward proving *use* (access tracing, transcript
reading, recording reads) — the manifest records **delivery** only. Confirm no committed
`CONTEXT_PROJECTION.json` or `scripts/context_projection.py` was built (ruled out of scope by Tommy),
and that `docs/CHECKLIST_SCHEMA.md`, `docs/CHECKLIST_ENGINE_DESIGN.md` and any lint were **not**
touched — those are gate g3's.

**8. Prose preservation.** The `context` step's imperative must still carry the
substitute-and-record rule and the "sanctioned degradation" rule verbatim. The declaration sits
*alongside* the prose, never replacing it.

## Constraints the change must respect

- `python -m pytest`, never `py -m pytest` (the `py` shim's runtime has no pytest here).
- **CI pins Python 3.12** (`.github/workflows/ci.yml:34`); this host is 3.14.3. Flag any 3.13+-only
  API — `Path.read_text(newline=)`/`write_text(newline=)` are the known traps. A sibling issue in
  this epic shipped a red CI on exactly that, so this is live, not hypothetical.
- Every file write must pin `newline="\n"`; no globs, no `os.listdir`, no `sorted()` over paths
  (declaration order is content).
- Metadata only — the manifest must never carry file contents.
- `.gitattributes` invariant: `rev` equals `git hash-object` only while no path is exempted from LF
  normalisation via `-text`/`binary`.

## Evidence already produced (reproduce it, do not take it on trust)

```bash
python -m pytest tests/test_context_manifest.py -q          # 45 passed
python -m pytest tests/test_context_determinism.py -q       # 7 passed
python -m pytest tests/test_checklist_engine.py -q          # 324 passed
python -m pytest tests/ -q                                  # 1209 passed, 2 skipped
grep -q 'context_refs' skills/commander/templates/COMMANDER_SPINE.template.json
test -f .gitattributes && ! grep -nE '(^|[[:space:]])(-text|binary)([[:space:]]|$)' .gitattributes
```

## Authority

Settled and **not** open for review comment: the identity function's definition; the `context_refs`
shape and name; no globs; one envelope with `/run` as the entire exclusion set; no CLI verb; no
committed artifact (Tommy's ruling); prose stays. Review the **implementation** of those decisions,
not the decisions.

Everything else — code structure, test design, fixture layout, naming — is fair game.

## Stop conditions

Return `BLOCK` rather than working around it if: the identity function disagrees with
`git hash-object` for any real case; the determinism comparison is vacuous or excludes more than
`/run`; a second selector exists; scope widened toward proving use; or an excluded file was touched.

## Return format

Write `REVIEW_RESULT` to
`C:/Programs/constellation-skills-wt/298-300/.agent-work/300/g1-review/REVIEW_RESULT.md`, with a
clear **verdict line: `APPROVE` or `BLOCK`**. Include: what you verified and how (commands and
outputs pasted), the adversarial fixtures **you** authored and what they proved, findings by
severity, out-of-scope observations, and workflow feedback.

A `BLOCK` is a successful review. Do not soften a real finding to be agreeable, and do not
manufacture findings to look thorough — say plainly where the change is sound.
