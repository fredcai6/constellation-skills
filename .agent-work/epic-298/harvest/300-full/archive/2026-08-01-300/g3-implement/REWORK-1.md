# Rework 1 — gate `g3-implement`

Your original handoff still governs everything not listed here. The full review is at
`.agent-work/300/g3-review/REVIEW_RESULT.md`.

**First, my error, plainly.** Both blockers trace to a rule I wrote wrong in the handoff. You
implemented what I specified; the specification was inverted. The reviewer said so explicitly and it
is worth you knowing, because it changes what you should trust: **do not treat my prose about the
lint's direction as authoritative — reason it out from the predicate.**

**What is already sound and is not being reworked:** scope is clean (spine template,
`context_manifest.py`, `checklist_engine.py`, `verify_skip_guard.py` all byte-unchanged vs HEAD);
both protected prose rules survive verbatim; the shape test is genuinely discriminating (the reviewer
injected four defects and it caught 4/4); the obligations statement's claims check out line-by-line
against the producer and nothing in it promises *use*; no new `skipTest`, no 3.13+ API. Leave all of
that alone.

## BLOCKER 1 — the lint's stated direction is inverted, in four places

The predicate is: *every declared `path` must occur inside that task's `imperative`*. Work out what
that actually catches:

- A **declared path the prose never mentions** → caught. This is a declaration that has drifted
  *beyond* what the prose explains.
- A path **dropped from the declaration** while the prose still names it → **not** caught. The
  remaining declared paths all still appear in the prose, so the lint exits 0.

I reproduced both: a narrowed declaration exits 0 with "0 offenders"; a declared
`docs/THIS_PATH_IS_NOWHERE_IN_THE_PROSE.md` exits 1 and names it.

So the docstring's claim — *"the declaration silently narrowing away from what the prose describes —
a path quietly dropped from `context_refs` while the prose still implies it is read"* — describes
**exactly the case the lint cannot catch**. Its own next paragraph then correctly disclaims "prose
naming a file the declaration omits", which is the *same scenario in different words*. The docstring
contradicts itself.

**Fix the claim in all four places it now appears:**

1. `scripts/verify_context_declaration.py` docstring (~lines 14–26).
2. The new section in `docs/CHECKLIST_ENGINE_DESIGN.md` — which repeats the inversion **and** vouches
   that it is "stated honestly… rather than oversold". That endorsement must go or be corrected; it
   is a committed doc asserting a false safety property.
3. The `_readme` in `tests/fixtures/context_declaration_lint.json`.
4. Add a **characterization test** pinning the real direction: a narrowed declaration is
   **deliberately** not caught (assert exit 0, with a comment saying why), so the boundary is
   mechanically watched instead of restated in prose that can drift again.

State the value honestly. The lint's real guarantee is: *no `context_refs` entry names a path the
step's own prose never mentions* — i.e. the declaration cannot silently point somewhere the human
explanation does not cover. That is worth having. It is simply not the guarantee the text claimed.

## BLOCKER 2 — "verbatim" is bare substring containment

`if path not in prose` means a declared `agents/GLOSSARY.md` passes clean against prose naming
`docs/agents/GLOSSARY.md` — a **different, nonexistent file**. Reproduced: exit 0, 0 offenders. This
is the likeliest real drift shape, because a directory move produces exactly it.

**Fix:** match at a **path boundary**. A declared path counts as present only when the occurrence in
the prose is not preceded by a path character (`/`, `\`, or an alphanumeric/`.`/`-`/`_`), so a suffix
of a longer path does not satisfy it. Add fixtures for: the suffix case (must FAIL), a legitimate
occurrence at start-of-string (must PASS), one preceded by whitespace or a backtick (must PASS), and
one preceded by `(` or a quote (must PASS) — the real prose wraps paths in backticks, so do not break
the shipped template.

The shipped `COMMANDER_SPINE.template.json` must still lint clean afterwards. That is your regression
check, and it is not optional.

## Constraints unchanged

`python -m pytest`, never `py -m pytest`. CI pins Python 3.12 — no `Path.read_text(newline=)` /
`write_text(newline=)`. **No `skipTest`** — CI's skip guard uses an exact-triple allow-list. All
commands assume cwd = the worktree root. Do not touch `scripts/context_manifest.py`, the spine
template, `checklist_engine.py`, `verify_skip_guard.py`, or `.github/`.

## Verification

The full pre-authored invariant chain from the original handoff must still pass, plus:

```bash
cd C:/Programs/constellation-skills-wt/298-300
python -m pytest tests/test_context_declaration_lint.py -q
python -m pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected -q
py scripts/verify_context_declaration.py skills/commander/templates/COMMANDER_SPINE.template.json  # must exit 0
python -m pytest tests/ -q --junitxml=junit-report.xml
python scripts/verify_skip_guard.py junit-report.xml
rm -f junit-report.xml
```

**Prove B2 is fixed rather than merely described:** paste a transcript showing the suffix fixture
exiting **1** after the change, where it exited 0 before.

## Return

Write `.agent-work/300/g3-implement/IMPLEMENTER_RESULT-rework1.md` — the two fixes, the evidence for
each, and the before/after transcript for B2. Do not re-litigate what passed.
