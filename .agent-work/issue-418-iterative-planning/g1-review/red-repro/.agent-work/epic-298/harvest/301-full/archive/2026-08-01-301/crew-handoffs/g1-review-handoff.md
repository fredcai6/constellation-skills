# Reviewer Handoff

## Gate
`g1` — episode record grammar and store doctrine (issue #301, epic-298)

## What was implemented

A new doctrine document `docs/EPISODE_STORE.md` (503 lines) plus a new git-tracked store
directory `episodes/` containing `episodes/README.md`. **No executable code, no tests** — this
gate freezes the contract that gates g2 (validated writer) and g3 (retrieval) build against.

## How to inspect the diff

```bash
cd C:/Programs/constellation-skills-wt/298-301
git status --short                  # episodes/README.md staged; docs/EPISODE_STORE.md untracked
cat docs/EPISODE_STORE.md
cat episodes/README.md
```

Both files are **new**, so `git diff` shows nothing useful — read the files directly.

The implementer's own result is at `.agent-work/301/crew-handoffs/g1-result.md`; the original
handoff it worked from is at `.agent-work/301/crew-handoffs/g1-handoff.md`.

## Task statement (what the gate was asked for)

Document the episode record grammar, the mechanical/agent-supplied partition, the retirement
policy, and a concrete Stratum A assertion mapping — and put the store at a git-tracked path.

## Close criteria — verify each independently

- **C2** the partition is documented as literal section headings, enumerating which fields
  belong to which bin; bin membership is never inferred from a field's name.
- **C3** the retirement **policy** is stated (excluded from ordinary search, RETAINED in
  history, never deletion or truncation, non-empty reason required) **and the retirement
  LAYOUT is left genuinely OPEN** — both options stated, **neither chosen**, held for human
  ratification.
- **C4** a concrete field-by-field Stratum A mapping against a worked example: identified
  assertion, source, supporting evidence, challenging evidence, qualitative strength
  (weak/medium/strong), with **lifecycle standing as a separate dimension from strength**.
- **C5** per-field assertion addressability **in the agent-supplied bin only** — one field can
  be disputed while a sibling stays active **with no rewrite of the record**; mechanical facts
  stay flat `- key: value` lines carrying no strength and no standing.
- **C6** the store lives at a **git-tracked** path and the doc says why; the store root
  resolves through one named seam and does **not** call `durable_root()`.
- **C7** the store is stated to be mechanical and never guessing (no ranking, similarity, or
  embedding); rhyme detection is downstream at issue #308. The obligation on issue #300's
  manifest is stated as an obligation, not a specification of #300.
- **C8** the episode-id scheme is chosen **on its own merits with recorded reasoning**, and is
  explicitly **not** justified by citing panel unanimity (that claim was retracted — only 2 of
  4 design candidates used run-id + sequence).
- **C9** the doc states cross-worktree sharing works through **git itself**, needing no
  `durable_root()`, unaffected by the epic-lease exception and by the read-only fence on the
  main checkout.

## HUNT THIS SPECIFICALLY — the highest-value part of your review

I found one candidate defect while integrating and I want an independent read on it rather than
my own judgment alone. **Do not simply agree with me — test it.**

**The held decision may be partially pre-empted.** The retirement *layout* is held for human
ratification: Option A moves the file between `episodes/active/` and `episodes/retired/` (so
"which set is this episode in" is a **filesystem** fact, structurally immune to malformed or
hand-edited content); Option B flips a `status` field filtered negatively (stable path, but
membership becomes a **content-parsing** fact).

`docs/EPISODE_STORE.md` §7 states that g2's and g3's contracts "work identically under either
layout" because "the retrieval primitives operate on 'does this episode carry a non-retired
status,' never on 'does this path live under `active/`'."

My concern: if g3 builds ordinary-search membership on status-filtering, then later choosing
Option A yields the directory split but **ordinary search still parses content** — forfeiting
exactly the structural immunity that is Option A's entire reason for existing. That would make
the "held open" claim true in letter and hollow in effect.

Questions I want answered:
1. Is that reading correct, or does the document already avoid it somewhere I missed?
2. Does the doc's §7 claim ("binding the layout later is additive, not a rewrite") actually
   hold, or does binding Option A require rewriting g3's retrieval?
3. Is the right fix to route the **membership predicate** through the same named adapter seam
   as the writer's retire op, so Option A globs a directory and Option B filters a field? Or is
   there a better fix?

Also hunt, independently: is there **anywhere else** the document quietly assumes one layout —
in the worked example, the field list, the retrieval description, or the README?

## Allowed scope

Review only. **Do not edit any file.** Report findings; I integrate them.

## Specific exclusions

- Do not evaluate issue #300's manifest design (concurrent worktree, out of scope here).
- Do not evaluate capture wiring (#305) or consolidation (#308) — both correctly out of scope.
- Do not ask for tests in this gate; it is inspection-only by design and the test surface
  belongs to g2/g3.
- Do not propose changing `LESSONS.md` or `apply_lessons_delta.py`.

## Constraints the implementation had to respect

- Markdown in git only; no database, no query language, no backend.
- The store is the mechanical half of the design; rhyme detection is a downstream sensor job.
- Suspected cause and proposed remedy are separate, **optional** assertions — an episode with
  no diagnosis is complete and valid.
- The retirement layout is **not** the implementer's to choose, and was not mine either.

## Evidence produced by the implementer (reproduce it)

```bash
git check-ignore episodes/ ; echo "exit=$?"     # implementer reported exit=1 (NOT ignored)
python -m pytest tests/ -q                       # implementer reported 1157 passed, 2 skipped
```

I independently re-ran both: `git check-ignore episodes/` exits **1**, and the suite is
**1157 passed, 2 skipped, 260 subtests** — matching the pre-change baseline exactly, as
expected for a doc-only gate.

Use `python`, **not** `py` — on this host `py` has no pytest and reports "No module named
pytest", which looks like a broken suite.

## Return format

Return **REVIEW_RESULT** with a literal `VERDICT: APPROVE` or `VERDICT: BLOCK` line, plus:
findings ranked most-serious-first with a severity each, what you verified as fine (so I know
what was actually checked rather than assumed), what you could not check and why, and a
Workflow Feedback section.

`BLOCK` if a close criterion is unmet or the held decision is genuinely foreclosed. `APPROVE`
with findings is appropriate if the criteria are met and the issues are refinements for
downstream gates — say so explicitly, and say which gate should carry each finding.
