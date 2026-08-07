# Implementer handoff — g1: the guard, authored and proven RED on the untouched tree

**Worktree (use absolute paths):** `C:/Programs/constellation-skills-wt/epic418-h-447`
**Branch:** `epic-418/h-447-episodes-retirement`

## Protected intent

Issue #308 declared this same retirement done and it came back — two commanders wrote to the "retired"
playbook three commits later. Issue #403's whole point is that the previous cut is **unverifiable** and
nothing prevents regression. You are building the thing that makes it verifiable.

**Author the guard BEFORE any retirement work exists**, so it is falsified against the *real disease*
rather than against a decoy. That sequencing is the deliverable, not an optimisation: a guard authored
after the tree is clean can only ever be falsified against synthetic decoys.

## Task

### 1. `scripts/verify_retirement.py`

Expose `scan(root: Path) -> list[Violation]` where `Violation` is a
`NamedTuple(leg: str, path: str, line: int, detail: str)`, sorted deterministically by
`(leg, path, line)`. A CLI wrapper prints violations and exits 1 if any, 0 if none.

**Return a list of named legs — never a bool, never a bare exit code.** The per-leg red-proofs must be
able to assert `== [LEG_X]`; a non-zero exit is produced identically by an import error, a collection
error and an empty test selection, so a bool cannot support discriminating proof. The archetype is
`tests/test_episode_negative_control.py`'s `compare_fields`, which returns field *names* for exactly
this reason — read it first.

**Enumerate surfaces from `git ls-files`, NOT `Path.rglob`.** A file deleted from the working tree but
still in the index must still be seen; scratch files must not produce phantom violations.

**Exactly four legs. Do not add more.** An earlier eight-leg design was cut by a cold panel that
measured four of them already green on the untouched tree, catching none of five plausible regressions.
Do not reintroduce: bundle-asymmetry, episode-address-regex, or schema-kind pinning.

| leg id | asserts |
|---|---|
| `retired-path-still-tracked` | `git ls-files` lists none of: `.agent-work/LESSONS.md`, `.agent-work/AGENT_FEEDBACK.md`, `scripts/apply_lessons_delta.py`, `scripts/verify_lessons_applied.py`, `scripts/verify_agent_feedback.py` |
| `unapproved-store-mention` | every shipped line naming `episodes/`, `episode store`, `query_episodes` or `apply_episode_delta` appears in `tests/data/store_mentions.approved.txt` |
| `replacement-absent` | the capture command `verify_episode_captured.py` is named in BOTH spine imperatives, is in the `commander` AND `admiral` install bundles, and exists on disk |
| `retired-name-on-shipped-surface` | none of `LESSONS.md`, `AGENT_FEEDBACK.md`, `apply_lessons_delta`, `verify_lessons_applied`, `verify_agent_feedback`, `lessons-auditor` appears on the shipped surface |

**`retired-path-still-tracked` is path-based on purpose** and cannot be paraphrased around. It is the
only leg that catches a future agent re-committing `.agent-work/LESSONS.md` verbatim — that file
advertises its own read path *in its own preamble*, so zero new mentions would appear anywhere else.
Leave a comment saying so, and noting that this run untracks with `git rm --cached` rather than
deleting, so "tracked" is the correct criterion rather than "exists".

**`unapproved-store-mention` is a frozen approval census.** `tests/data/store_mentions.approved.txt`
holds `path:normalized-line` plus a **required** one-line reason per entry. Seed it with the sites that
exist today — measured as ~18 lines, and **zero** under `skills/`. Its failure message must state the
discriminator verbatim:

> `a new shipped site now names the episode store: <path>:<line>. If this is a WRITE path, approve it
> with a reason. If it tells an agent to READ the store and condition behaviour on it, it violates
> constraint:episodes-are-not-prescriptions.`

Exclude the store's own module (`scripts/apply_episode_delta.py`, `scripts/query_episodes.py`) and its
own spec (`docs/EPISODE_STORE.md`).

**`replacement-absent` is the PRESENCE half**, and it is not optional.
`tests/test_prose_deletions.py`'s docstring states the rule: *"An absence-only suite would pass just as
happily on a template that had deleted everything."* Read that file; mirror its both-directions shape.
**At g1 this leg is legitimately RED and stays red until g3 ships the replacement.** That is correct,
not a bug.

**Record-only roots**, each carrying a **required non-empty reason string** (a root with an empty
reason must raise, so nobody adds a silent exclusion):
- `docs/superpowers/` — "historical plans, specs and drills: records of past work, not instructions"
- `tests/fixtures/` — "recorded transcripts; editing them would falsify a recording"
- `.agent-work/` — "run records and archives"
- `episodes/` — "the store itself"

### 2. `tests/test_retirement_guard.py`

- **One decoy red-proof per leg.** Each builds a minimal git repo in `tmp_path` (`git init`, a couple
  of tracked files) containing **exactly one** planted violation, and asserts **both**
  `[v.leg for v in scan(decoy)] == [LEG_X]` **and** the offending `path` — so a leg that fires for the
  wrong reason is caught, not just "something failed".
- **`test_every_leg_has_a_red_proof`** — the census. `set(LEGS) == set(_REGISTERED)`, with the leg
  roster pinned as an independent literal in the *test* module. A leg added later without a decoy
  fails; a leg quietly deleted fails. This is the anti-rot invariant.
- **`test_every_approved_entry_exists_verbatim`** — each approved-census entry must be found at its
  path, so a stale approval cannot silently widen the guard.
- **`test_canon_is_clean`** — `assert scan(REPO_ROOT) == []`, carrying
  `@pytest.mark.xfail(strict=True, reason="#447 g6 removes this marker — the tree is deliberately still dirty")`.
  The suite stays green while the tree is dirty, and **strict XPASS fails the suite the moment the tree
  goes clean**, so the scaffolding cannot outlive the work.

`tests/` is deliberately outside the shipped surface — the guard file itself must contain the forbidden
strings. State that in the module docstring as a principled scope choice, not a dodge.

## Allowed scope

**CREATE ONLY:** `scripts/verify_retirement.py`, `tests/test_retirement_guard.py`,
`tests/data/store_mentions.approved.txt`.

**Touch nothing else.** This gate deliberately produces zero retirement. If you find yourself editing a
skill, a spine, or a script, stop — that is a later gate.

## Constraints

- Use `python`, **never** `py` — `py` resolves to a runtime with no pytest here and produces fake greens.
- Windows: pass `encoding='utf-8', newline='\n'` explicitly on every file write.
- `.gitattributes` sets `* text=auto`; never compare files by raw working-tree bytes.
- Scope-discipline ruling (epic-418): build the thing that needs to work and no more. A corner case you
  choose not to chase gets a comment **at the code site** naming it, and is reported up — never
  silently absorbed, never stopped-to-fix.

## Required evidence — commands that can genuinely fail

```
python -m pytest tests/test_retirement_guard.py -q
python scripts/verify_retirement.py ; echo EXIT=$?          # MUST be 1 on the untouched tree
python scripts/verify_retirement.py | cut -f1 | sort -u     # MUST list >= 3 distinct legs
```

**Capture the third command's full output verbatim into
`.agent-work/epic418-h-447/evidence/g1-guard-red.txt` before finishing.** That transcript — the guard
failing on the real, untouched tree — is this gate's centerpiece evidence and the thing #308 could not
produce.

## Close criteria

1. Guard exists with exactly four legs.
2. Every leg has a passing decoy red-proof asserting **leg AND path**.
3. The leg census passes.
4. `scan()` on the real untouched tree returns violations across **at least three** distinct legs
   (`retired-path-still-tracked`, `replacement-absent`, `retired-name-on-shipped-surface` —
   `unapproved-store-mention` is seeded green by construction and goes red at g3).
5. `python -m pytest -q` shows no NEW failures beyond the pre-existing baseline (1688 passed, 2 skipped).

## Report back

An `IMPLEMENTER_RESULT` to `.agent-work/epic418-h-447/results/g1-IMPLEMENTER_RESULT.md` containing:
the diff summary, each evidence command with its **real** exit code, the verbatim red transcript, any
corner case you deliberately did not chase with the file:line of the comment naming it, and a
**Workflow Feedback** section. Deliver your result via your final message before ending your turn.
