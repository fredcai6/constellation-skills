# Rework 1 — gate `g5-doctrine-version`

The reviewer returned `BLOCK` and it is correct. Full review:
`.agent-work/300/g5-review/REVIEW_RESULT.md`.

**The error was mine, in the gate imperative, and it is worth understanding before you fix it.** I
wrote the settle condition myself — *"if two checkouts at the same commit disagree on the field, it
belongs in `/run`"* — and then, in the same imperative, wrote the sentence that guaranteed the test
could never reach that case: *"both children are worktrees at the SAME commit **and are equally
dirty**, so the field is identical across environments."* That is assuming the conclusion. You built
what I specified and the specification was self-blinding.

The reviewer built the case I had excluded: two worktrees at the same commit, **nothing overlaid**,
with the dirt confined to a file **no declaration names**. Declared rows byte-identical, same commit,
and `repo_rev` differs — `{'dirty': False}` versus `{'dirty': True}`. I reproduced the mechanism
myself: `git status --porcelain` is **repo-wide**, so editing any file — including one the manifest
never mentions — flips the flag.

## The fix — split the field, do not delete it

**`commit` stays in content.** It is canon-determined: identical in any checkout of that commit,
anywhere. That is Tommy's traceability stamp and it stays exactly where it is.

**`dirty` moves into `/run`.** It is a fact about *the working tree that produced the manifest*, not
about the bytes delivered. Two agents at the same commit, one mid-edit on an unrelated file, hand
over the same doctrine and must not produce different content records.

Concretely:
- `CONTENT_KEYS` becomes `("contract", "step", "files", "repo_rev")` with `repo_rev` carrying the
  **commit only**.
- The dirty flag appears under the `run` subtree.
- `repo_revision()` may keep returning both — the split belongs at the point of assembly, not
  necessarily in the git helper. Your call; say which you chose and why.

## Why this does not lose the honesty the marker was for

Worth stating in the docstring, because the next reader will ask. The concern was that a bare commit
SHA lies about a dirty tree. It still would — **but content does not rely on it for that.** Content
already carries the per-file blob OID, which is the honest answer to *which bytes did this agent
actually get*, for tracked, dirty, untracked and out-of-repo files alike. So content ends up with:

- `repo_rev.commit` — coarse, human-facing traceability ("which doctrine version"), canon-determined;
- per-file `rev` — precise content identity ("which bytes"), which is what the dirty-tree problem
  actually needed;
- and `run.dirty` — provenance about the producing environment, correctly excluded.

Each fact sits where its own determinism properties put it. Update the `repo_revision()` docstring,
which currently argues that `dirty` keeps the repo-wide SHA honest *inside content* — that argument
is what the reviewer disproved.

## The test that let this through must be fixed too

`test_context_determinism.py` cannot currently reach the varying case: `setUpClass` overlays the same
files into both worktrees, so both are dirty by construction. Do **not** weaken it — **extend** it
with the reviewer's case as a regression: two checkouts at the same commit where **one is clean and
one has an edit to a file no declaration names**, asserting content stays byte-identical. That case
must fail before your fix and pass after. Paste both transcripts.

This is the second time in this issue a test has been unable to see the defect it was written for.
Check the same way the reviewer did: mutate, and confirm the mutation is caught.

## Also in the review, address it

**MAJOR** — read the reviewer's own write-up for the detail and fix it in the same pass. Do not
expand beyond it.

## Not in scope

Do not touch the per-file `rev()`. Do not revisit the caller question (with the Admiral). Do not
widen beyond the split, the docstring correction, the test extension, and the reviewer's major.

## Constraints

`python -m pytest`, never `py -m pytest`. CI pins Python 3.12 (host 3.14.3) — no
`Path.read_text(newline=)`/`write_text(newline=)`. **No `skipTest`.** cwd = worktree root. Every
write pins `newline="\n"`.

## Verification

```bash
cd C:/Programs/constellation-skills-wt/298-300
python -m pytest tests/test_context_manifest.py -q -k 'repo_rev or doctrine_version' --no-header
python -m pytest tests/test_context_determinism.py -q
python -m pytest tests/ -q --junitxml=junit-report.xml && python scripts/verify_skip_guard.py junit-report.xml && rm -f junit-report.xml
```

Plus the new regression case, shown failing before and passing after.

## Return

`.agent-work/300/g5-implement/IMPLEMENTER_RESULT-rework1.md`. Keep it accurate to what ships — a
stale result artifact was a review finding earlier in this issue.
