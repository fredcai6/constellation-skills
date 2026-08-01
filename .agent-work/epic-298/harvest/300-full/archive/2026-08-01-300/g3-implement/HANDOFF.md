# Implementer Handoff

## Gate

`g3-implement` (issue #300, epic-298). Worktree root: `C:/Programs/constellation-skills-wt/298-300`.
Absolute paths — your cwd resets between bash calls.

Gate `g1` is **done and committed** (`75ee317`). You are documenting and pinning what it built.

## Task

Four bounded deliverables:

1. **A mechanical lint** pinning every declared `context_refs` path against the step's imperative
   prose — with a **negative test** proving it rejects a divergent fixture.
2. **One row** in the `docs/CHECKLIST_SCHEMA.md` Task table for `context_refs`.
3. **A narrative extension** in `docs/CHECKLIST_ENGINE_DESIGN.md` describing the manifest beside the
   existing state projection.
4. **`.agent-work/300/OBLIGATIONS-301.md`** — an explicit two-part statement of what issue #301 may
   and may not rely on — plus a **shape test** asserting a produced manifest is assignable to an
   episode `context` field untransformed.

## Protected intent

The `context` step's imperative prose carries rules a path list **cannot express** — the
substitute-and-record rule, and "a missing engine-config is a sanctioned degradation, do NOT create
the overlay file". **The prose stays. The lint pins it.** Deleting or reworking that prose is a
behaviour change to every Commander run and is a stop condition, not a cleanup.

## Background you need

`g1` added an optional ordered `context_refs` list to the spine task object. Each entry is
`{"root": "skill"|"repo"|"durable", "path": "<posix relative path>", "required": bool}`. Absent means
an empty manifest. Read `scripts/context_manifest.py` — it is the authority on the shape, and its
module docstring explains the design. The only spine carrying a real declaration today is
`skills/commander/templates/COMMANDER_SPINE.template.json`, on its `context` step.

## The lint

New `scripts/verify_context_declaration.py`, following the existing `scripts/verify_*.py`
convention in this repo (read two of them first and match their CLI and exit-code style).

**The rule:** for every spine task that declares `context_refs`, each declared `path` must appear
**verbatim** in that same task's `imperative` string. Exit non-zero, naming the offenders, when it
does not.

**Direction matters, and state the limit honestly in the module docstring:** this catches the
declaration silently *narrowing* away from the prose. It cannot catch the other direction — prose
naming a file the declaration omits — because the imperative is prose, not a parseable list. The
declaration is authoritative; the prose is the human explanation of it. Do not claim a guarantee the
check does not deliver.

## The negative test is the load-bearing one

`tests/test_context_declaration_lint.py` must include
`test_divergent_declaration_is_rejected` — that **exact** test id, because the gate's postcondition
names it.

A lint that only passes over the clean shipped corpus proves **the corpus is clean, not that the
lint works**. Author a fixture where the declaration and the prose genuinely diverge, and assert the
lint **fails** on it. Then also assert it **passes** on a valid fixture, so the failure cannot be
coming from something incidental.

Do not implement this by asserting a non-zero exit from a probe that fails for an unrelated reason —
that mistake is live in this repo's recent history and is what the postcondition is shaped to catch.

## The schema row

`docs/CHECKLIST_SCHEMA.md` has a Task-table. Add a row for `context_refs`. The gate's postcondition
greps `^\| *`?context_refs`?`, so it must be a genuine table row starting with a pipe, not prose
mentioning the word — the word "context" already appears ten times in that file, which is exactly why
the check is anchored this way.

## The #301 obligations statement

`.agent-work/300/OBLIGATIONS-301.md`. Two explicit halves, and the postcondition greps for both
phrasings (`may rely` and `may not`):

- **What #301 may rely on** — the manifest's contract version, its row shape, order stability,
  that every declared entry is retained including absent ones, and how an episode addresses one.
- **What #301 may not rely on** — anything under `/run` (the declared exclusion set), the on-disk
  pretty-printing, and the file path if the work-area layout moves.

Three facts that must appear, because they are real and #301 will otherwise be surprised:

- **Durability.** The manifest lives under `.agent-work/`, which is gitignored and destroyed by
  `git worktree remove`. Whether #301 inlines a copy or stores a reference is **#301's call** — the
  rows are small precisely so inlining is affordable.
- **Cardinality.** One manifest per spine **step**. If #301 assumed one `context` field per episode
  and an episode spans several steps, one of the two designs must change — that is an Admiral float,
  not something either side fixes unilaterally.
- **Delivery, not use.** The manifest records what was made available at which revision. It carries
  **no** claim that the agent read anything. #301 must not present it as evidence of use.

Read `.agent-work/300/DIT-COMPARISON.md` (the "Cross-interface risks toward #301" section and the
ADDENDUM) — the obligations are already worked out there; you are stating them cleanly, not
re-deriving them.

## The shape test

Add to `tests/test_context_manifest.py` a test whose id contains **`episode_context_field`** (the
postcondition selects on it with `-k`). It must produce a real manifest via the real producer, and
assert it is a JSON value assignable to an episode `context` field **with no transformation** —
`json.loads(json.dumps(manifest))` round-trips, no non-JSON types, no absolute paths in content.

## Allowed scope

- **New:** `scripts/verify_context_declaration.py`, `tests/test_context_declaration_lint.py`,
  fixtures under `tests/fixtures/`, `.agent-work/300/OBLIGATIONS-301.md`.
- **Edit:** `docs/CHECKLIST_SCHEMA.md` (one table row), `docs/CHECKLIST_ENGINE_DESIGN.md` (narrative
  section), `tests/test_context_manifest.py` (add the shape test only).

## Specific exclusions

- **Do not touch `scripts/context_manifest.py`.** It is committed, reviewed and approved. If you
  believe it is wrong, that is a stop condition — report it, do not edit it.
- **Do not touch `skills/commander/templates/COMMANDER_SPINE.template.json`**, and above all do not
  delete or reword its `context` imperative prose.
- **Do not touch** `scripts/checklist_engine.py`, `scripts/verify_skip_guard.py`, `.github/`.
- **Do not build** a committed `CONTEXT_PROJECTION.json` or `scripts/context_projection.py` — ruled
  out of #300's scope by Tommy.
- `verify_spec_confirmed.py` belongs to issue #303.
- Never hand-edit `.agent-work/LESSONS.md`.

## Pre-authored invariant chain

These are the gate's postconditions. They are pre-authored so you verify a **frozen chain** rather
than improvising a proxy for "the document says what it should":

```bash
python -m pytest tests/test_context_declaration_lint.py -q
python -m pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected -q
grep -q 'substitute the closest repo doctrine' skills/commander/templates/COMMANDER_SPINE.template.json
grep -q 'sanctioned degradation' skills/commander/templates/COMMANDER_SPINE.template.json
grep -qE '^\| *`?context_refs`?' docs/CHECKLIST_SCHEMA.md
test -f .agent-work/300/OBLIGATIONS-301.md && grep -qi 'may rely' .agent-work/300/OBLIGATIONS-301.md && grep -qi 'may not' .agent-work/300/OBLIGATIONS-301.md
python -m pytest tests/test_context_manifest.py -q -k 'episode_context_field' --no-header
```

The two `grep`s on the spine template are **non-regression guards** — they pass today and must keep
passing. The others fail today and must pass when you are done.

## Constraints

- **`python -m pytest`, never `py -m pytest`** — `py` resolves to a runtime with no pytest here.
- **CI pins Python 3.12** (`.github/workflows/ci.yml:34`); this host is 3.14.3. No
  `Path.read_text(newline=)`/`write_text(newline=)` — 3.13+.
- **CI also runs `python scripts/verify_skip_guard.py junit-report.xml`**, whose allow-list is an
  exact `(classname, name, message)` triple frozenset. **Do not introduce any `skipTest`.** A skip
  that fires on a clean checkout turns CI red — that exact defect blocked gate g1 and cost a rework
  round.
- All commands assume cwd = the worktree root.
- Every file write pins `newline="\n"`.

## Deliverable path check

- **Committed** — `git check-ignore` exit **1** (not ignored) verified for:
  `scripts/verify_context_declaration.py`, `tests/test_context_declaration_lint.py`,
  `docs/CHECKLIST_SCHEMA.md`, `docs/CHECKLIST_ENGINE_DESIGN.md`, `tests/test_context_manifest.py`.
- **Local-only** — `.agent-work/300/OBLIGATIONS-301.md`: `git check-ignore` exit **0**, intentionally
  gitignored. It is a working artifact the Admiral harvests, not a shipped file. The reviewer must
  not expect it in the diff.

New files are untracked until staged: they appear in `git status`, not `git diff`.

## Required evidence

**Load-bearing — prove rigorously:**

1. The negative test genuinely fails on a divergent fixture — show the fixture and the failure.
2. The lint passes over the real shipped spine templates.
3. The full invariant chain above, each command with its exit code.

**Confirmatory — spot-check:** the schema row renders as a table row; the obligations doc contains
both halves.

## Verification commands

```bash
cd C:/Programs/constellation-skills-wt/298-300
python -m pytest tests/test_context_declaration_lint.py -q
python -m pytest tests/test_context_manifest.py -q
python -m pytest tests/ -q --junitxml=junit-report.xml
python scripts/verify_skip_guard.py junit-report.xml     # must exit 0
rm -f junit-report.xml
```

## Suggested model tier

Simple bounded — the invariants are pre-authored and the scope is documentation plus one small
linter. The one subtle part is the negative test, which the handoff spells out.

## Authority

Settled, not yours: the `context_refs` shape; the lint's direction and its stated limit; the prose
stays; no committed artifact. Yours: the linter's internal structure, fixture layout, the wording of
the docs and the obligations statement.

## Stop conditions

Stop and return if: `scripts/context_manifest.py` appears wrong; the prose invariants cannot be kept
while doing the work; the lint cannot be made to fail on a genuinely divergent fixture; or any
excluded file must be touched.

## Return format

Write `IMPLEMENTER_RESULT` to
`C:/Programs/constellation-skills-wt/298-300/.agent-work/300/g3-implement/IMPLEMENTER_RESULT.md`:
completed slice, files changed, evidence produced (pasted transcripts), assumptions, stop conditions,
out-of-scope observations, and workflow feedback.
