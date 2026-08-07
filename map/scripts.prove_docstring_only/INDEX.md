# scripts.prove_docstring_only
scripts/prove_docstring_only.py, 126 lines, 1 holes

Decide — not assert — whether a Python file's change is docstring-only.

"Docstring-only, behaviour unchanged" is normally *asserted* by whoever made the
edit and taken on trust by whoever reads the diff. No amount of reading a diff
can establish it: a diff shows text moved, not whether meaning moved with it.

This turns it into a decidable three-way result, where each leg rules out a
different way of being wrong:

    raw bytes differ            -> the edit actually applied (not a no-op)
    full AST differs            -> the docstring genuinely changed
    docstring-stripped AST same -> no behaviour changed

All three must hold. Any two of them are satisfiable by a change that is *not*
docstring-only:

  * bytes differ + stripped-AST same, but full AST also same -> the change was
    whitespace or comments, not a docstring; the claim is mislabelled.
  * bytes differ + full AST differs, but stripped-AST differs too -> real code
    moved. This is the case the check exists to catch.

Stripping is applied to every module, class and function body, so a docstring
edit anywhere in the file is covered, not just the module header.

Written for #305 g4 (#327), where the claim under test was that
`scripts/checklist_engine.py` — the engine every gate in the fleet drives —
changed by docstring only. Kept as a tool rather than a scratch script because
the claim recurs whenever prose recording a decision is corrected in place.

    python scripts/prove_docstring_only.py <before-rev> <after-rev> <path>
    python scripts/prove_docstring_only.py 35d2686^ 35d2686 scripts/context_manifest.py
    python scripts/prove_docstring_only.py HEAD WORKTREE scripts/context_manifest.py

`WORKTREE` in place of a revision reads the file on disk. It is spelled without
leading dashes on purpose: `--worktree` would be parsed as an option, not as the
positional it stands in for.

Exits 0 when the change is proven docstring-only, 1 otherwise. The failure
message names WHICH leg failed, because "not docstring-only" and "no change at
all" are different problems.

A note on instruments: comparing raw bytes across a CRLF worktree and an LF
`git show` manufactures false results (see #319). This compares parsed ASTs, so
line endings cannot affect the verdict.

imports stdlib: __future__.annotations, argparse, ast, pathlib.Path, subprocess, sys
imported by: none found

- [source_at](source_at.md) function: File contents at `rev`, or the file on disk when rev is `WORKTREE`.
- [strip_docstrings](strip_docstrings.md) function: Drop the leading string-constant expression from every body that has one.
- [main](main.md) function: HOLE: no docstring
