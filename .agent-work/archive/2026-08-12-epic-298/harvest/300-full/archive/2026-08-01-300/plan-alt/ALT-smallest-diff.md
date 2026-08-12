# Gate plan — ALT-smallest-diff (issue #300)

Constraint: **smallest-diff.** Minimise total files touched and gates authored. Every gate below
was tested against "could this land as an edit to something that already exists?" before being
allowed to create a new file or a new gate. Builds toward the DIT-COMPARISON hybrid recommendation
("C's two artifacts, A's row, B's resolver"); does not re-litigate that interface.

## Gate list

1. **e0-context** — load inherited doctrine (no diff; boilerplate).
2. **g1-implement** — the whole substrate in one dispatch: producer, resolver, CLI verb, generator
   script, schema/design-doc rows, and the prose-vs-declaration lint, as one bounded change.
3. **g1-review** — one 3-lens cold panel over the combined diff (satisfies `decision:full-cold-panel`
   directly; no separate closeout panel gate).
4. **g1-integrate** — verify side effects, re-run evidence in hand, harvest feedback and triage
   candidates (notably: which real role template to annotate first — deferred, see below).

Four gates total. No `g2`/`g3` split (the sample baseline's run-time-half / ahead-of-time-half /
doctrine-and-lint split, three implement+review+integrate triads plus a trailing cold-panel gate,
is collapsed to one triad because the recommended design is already **one producer function** with
two envelope modes — splitting it into separate gates would be splitting one deliverable, not two).

---

## e0-context

**Deliverable:** none — doctrine load only, no repo diff.
**Close criteria:** inherited global doctrine + `docs/CHECKLIST_ENGINE_DESIGN.md` §Answerability +
`docs/CHECKLIST_SCHEMA.md` Task table read.
**Required evidence:** qualitative attest (`check: null`), no command.
**What could go wrong:** skipped context loses the purity/contract-version idiom `state()` already
sets — low risk, cheap to catch at review since the diff would then not match the existing idiom.

## g1-implement

**Deliverable** (5 files total — the minimum this build can touch given the interface is fixed):
- `scripts/checklist_engine.py` (edit) — one resolver (`_resolve_context_rev(root, path, mode)`,
  mode ∈ {`committed`: object-DB only, tracked→OID else `None`; `run`: working-tree bytes, always
  resolves) and one pure producer `project_context(cl, aid, *, resolver, mode)` beside `state()`,
  selecting via the **existing** `active_id(cl)` — no second selector. Plus one read-only `context`
  CLI verb emitting the run-local envelope (mirrors `current`'s no-session read path).
- `scripts/context_projection.py` (**new** — the one new file this plan cannot avoid; the interface
  names it explicitly). A thin CLI that **imports** `project_context` from `checklist_engine.py`
  rather than reimplementing assembly, and writes the committed `skills/<role>/CONTEXT_PROJECTION.json`
  via `generate`/`regenerate`.
- `docs/CHECKLIST_SCHEMA.md` (edit) — one Task-table row for the new optional `context` field
  (root-token grammar `skill:`/`repo:`/`durable:`, `required` flag, "no globs, order is content").
- `docs/CHECKLIST_ENGINE_DESIGN.md` (edit) — fold into §Answerability: the producer is the sibling
  of `state()`/`render_human()`, same purity discipline, same `contract` version idiom.
- `tests/test_checklist_engine.py` (edit) — targeted tests below, plus the prose-vs-declaration lint
  written as a **plain test function**, not a new `scripts/verify_*.py` — it reuses the regex-over-
  prose pattern `verify_state_note.py` already established in this repo, inlined rather than
  promoted to a shared helper.
- One small fixture directory under `tests/fixtures/` (a handful of tiny files: a normal doc, a
  CRLF/LF twin pair, a gitignored file, an untracked file) — the one new-file *category* this plan
  cannot avoid, because `lesson:round-trip-tests-prove-artifacts-not-parsers` requires adversarial
  fixtures, not a corpus round-trip. Kept to the minimum set the four required fixtures need.

**Explicitly not touched in this gate:** `skills/commander/templates/COMMANDER_SPINE.template.json`.
The declaration is `decision:declaration-is-optional-spine-field` — absent means empty — so no
shipped spine needs the key added for the mechanism to work. No real
`skills/<role>/CONTEXT_PROJECTION.json` is generated for any actual role either; the generator is
proven against fixtures only. Both are named deferrals, not oversights (see "what I gave up").

**Close criteria:**
- committed envelope: zero varying fields, `rev` resolves from the git object DB only (`null` for
  anything untracked);
- run envelope: same row shape plus one `/run` pointer holding every varying fact (timestamps, run
  id) and nothing else — a new varying field cannot be "accidentally content";
- revision identity is the git blob OID of LF-normalised bytes, computed in-process, verified equal
  to `git hash-object`/`git rev-parse HEAD:<path>` for a tracked clean fixture file;
- declaration order preserved verbatim, never sorted; no globs;
- `newline="\n"` on every write (not optional on this Windows corpus);
- the lint test fails if a declared `required` path is not also named in the gate's imperative
  prose (pins declaration against prose per the converged finding).

**Required evidence (real commands, named):**
- targeted: `python -m pytest tests/test_checklist_engine.py -k "context_projection or context_declaration_lint" -v`
- broader (must stay green — project doctrine requires both, named): `python -m pytest tests/test_checklist_engine.py -v`
- determinism exercise: a pytest test that materializes the fixture tree into two temp directories
  via `git archive HEAD -- tests/fixtures/context_projection | tar -x` (simulating two clean
  checkouts / a second environment) and byte-compares the two generated committed artifacts.

**What could go wrong:**
- **Convergence is still floated** (`decision:convergence-is-human`). If the Admiral rules against a
  committed artifact, this gate's committed-artifact postconditions are dropped via `amend` and the
  plan *shrinks* (fewer files, not more) — this plan degrades gracefully either way, unlike a plan
  that pre-splits committed-vs-run-local into separate gates and would need real restructuring.
- **One shared resolver bug leaks into both envelopes at once.** Because committed and run modes
  share one function, a defect in the mode branch (e.g. the untracked-vs-absent inconsistency the
  DIT comparison's own amendment caught) can silently corrupt both outputs together, where a
  split implementation might have caught it in only one review pass.
- **Reopen blast radius.** A single failing postcondition (say, the CRLF fixture) reopens the whole
  gate — resolver, CLI verb, docs, and the lint test all go back into rework together, even though
  only one piece was actually wrong.

## g1-review

**Deliverable:** one `review-result` artifact, `verdict: APPROVE`/`BLOCK`, produced by a 3-reviewer
cold panel (satisfies `decision:full-cold-panel`'s "3-lens panel floor" directly — no separate
closeout cold-panel gate is authored, since there is only one implement gate to review).
**Close criteria:** each of the three reviewers independently re-runs the revision-identity equality
check and all four adversarial fixtures (CRLF/LF twins, stale-manifest-must-not-silently-pass,
untracked-vs-absent, declaration-order-permutation) in their own hands — not by reading the diff —
before consolidating; `consolidate` refuses `APPROVE` while any reviewer's item still reads `fail`
absent an explicit `override_reason`.
**Required evidence:** same two pytest commands as g1-implement, re-run by each reviewer; the
consolidated `review-result` artifact attached to `g1-implement`'s `artifact` postcondition.
**What could go wrong:** collapsing "per-half review" and "the required end-of-run cold panel" into
one gate trades a second independent pass for footprint — if the Admiral's intent for
`decision:full-cold-panel` was a *distinct* closeout audit on top of ordinary gate review (as the
sample baseline plan does with a trailing `g4-cold-panel`), this reading under-satisfies it; flagged
explicitly rather than assumed away.

## g1-integrate

**Deliverable:** verified, merged change; no new files.
**Close criteria:** verdict checked; side effects verified against the world directly (not trusted
from the crew's report); both pytest commands re-run in the integrator's own hands; triage
candidates logged — notably "annotate the first real role template" and "generate the first real
committed artifact," both explicitly deferred out of #300 by this plan.
**Required evidence:** `python -m pytest tests/test_checklist_engine.py -v` (re-run once more,
post-merge, as the integrator's own confirmation).
**What could go wrong:** because no real role was ever annotated, there is nothing yet to show a
human as "a reviewable diff of a doctrine change" — the substrate's stated purpose is proven
mechanically (tests) but not demonstrated experientially until a follow-on issue lands the first
annotation.

---

## What this constraint made me give up

1. **No real committed artifact for any actual role.** The generator and the committed-artifact
   contract are built and proven against fixtures only; the first real `CONTEXT_PROJECTION.json`
   and the first real diff a human can look at both land in a follow-on issue, not #300.
2. **No edit to `COMMANDER_SPINE.template.json`.** The optional `context` field is documented and
   code-supported but never demonstrated in a shipped template this run.
3. **No dedicated lint script.** The declaration-vs-prose lint is a test function, not a promoted,
   reusable `scripts/verify_context_declaration.py` — cheaper now, but not reusable by a future
   caller without either duplicating it or refactoring it out later.
4. **No run-time/ahead-of-time gate split.** One monster implement gate instead of two scoped ones
   trades review clarity and a smaller reopen blast radius for fewer total gates.
5. **No separate closeout cold-panel gate.** The full-cold-panel requirement is satisfied inside the
   single review gate rather than as a second, independent pass at the end.
