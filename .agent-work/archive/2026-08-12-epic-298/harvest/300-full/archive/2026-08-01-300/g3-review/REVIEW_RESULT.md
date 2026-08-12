# Review Result — gate `g3-review`, issue #300 (epic-298)

## Verdict

**BLOCK**

2 blockers, 0 majors beyond them, 5 observations. Both blockers are in the lint's self-description
and its matching rule; both are cheap (a few sentences and one predicate). Everything else in the
change is sound, and I say so explicitly below.

Survey driven through the engine at `.agent-work/300/g3-review/review.json`
(13 items, all visited, consolidated `verdict=BLOCK findings=2`, session `g3rev-1785600325`).
Fowler pass at `.agent-work/300/g3-review/FOWLER_PASS.json`, rail exits 0.

---

## Blockers

### B1 — The lint claims the one guarantee it cannot deliver, and the claim now ships in a committed doc

`scripts/verify_context_declaration.py:17-20`:

> This catches exactly one failure shape: the declaration silently *narrowing away* from what the
> prose describes -- a path quietly dropped from `context_refs` while the prose still implies it is
> read.

That is false. Independent fixture (`h2_dropped.json`): a `context` task whose imperative names
`references/global-everyone.md`, `docs/agents/GLOSSARY.md` and `docs/agents/CREW_CONTEXT.md`, with
`context_refs` retaining only the first — i.e. two paths quietly dropped while the prose still names
them:

```
$ python scripts/verify_context_declaration.py <scratch>/h2_dropped.json
context declaration lint ok: 1 checklist(s) checked, 0 offenders
exit=0
```

Six lines further down, the same docstring correctly disclaims "prose naming a file the declaration
omits" — **the identical scenario**. The docstring both claims and disclaims the same guarantee, and
the claim half is the sentence a maintainer reads as the lint's purpose. The implementer's own
`test_prose_naming_more_than_declared_is_not_flagged` asserts that case is unflagged, so the
contradiction was visible in-gate.

What the lint actually catches is the reverse direction: **a declared path the prose never mentions**
(declaration ⊄ prose). It cannot see prose ⊄ declaration, which is what "narrowing" means.

The same inverted claim is repeated in two more places, one of them shipped:

- `docs/CHECKLIST_ENGINE_DESIGN.md`, new section: *"it catches the declaration silently narrowing
  away from the prose; it cannot catch the prose naming a file the declaration omits ... stated
  honestly in the lint's own docstring rather than oversold."* This is a committed doc asserting a
  guard that does not exist, and vouching for its honesty.
- `tests/fixtures/context_declaration_lint.json`'s `_readme`, which labels the `divergent` fixture
  "the declaration silently narrowing away from what the prose describes" when it is the opposite
  shape.

The handoff made this a named requirement: *"state the limit honestly in the module docstring ... Do
not claim a guarantee the check does not deliver."* The substance was delivered; the honesty clause
was not.

**Fairness note, for the Commander:** the handoff itself carries the same inversion (*"this catches
the declaration silently narrowing away from the prose. It cannot catch the other direction — prose
naming a file the declaration omits"* — those are the same direction). This is an inherited defect,
not invention by the implementer. It still has to be fixed before it ships, and the handoff wording
should be corrected alongside it.

**Fix:** replace the characterisation in all three places with what the code does, e.g. *"This
catches exactly one failure shape: the declaration naming a path its own prose never mentions — a
declaration that has been retargeted, mistyped, or extended past the prose that justifies it. It
CANNOT catch the reverse: a path quietly dropped from `context_refs` while the prose still names it,
because the imperative is prose, not a parseable list."* The Task-table row in
`docs/CHECKLIST_SCHEMA.md` is already accurate ("lints that every declared path appears verbatim in
the task's own `imperative`") and needs no change.

### B2 — Substring containment is not a verbatim path match: silent PASS on a genuinely divergent declaration

`verify_context_declaration.py:76` implements "appears verbatim" as `if path not in prose` — bare
substring containment. A declared path that is a substring of a **longer, different** path in the
prose therefore passes clean:

```
# prose: "...then the project deltas: docs/agents/GLOSSARY.md. Attest c1."
# context_refs: [{"root": "repo", "path": "agents/GLOSSARY.md", "required": true}]
$ python scripts/verify_context_declaration.py <scratch>/h1_substring.json
context declaration lint ok: 1 checklist(s) checked, 0 offenders
exit=0
```

The declared path resolves to `<repo>/agents/GLOSSARY.md`, which does not exist; the manifest would
record `rev: null` for it while the prose promises a file that does exist elsewhere — and the lint,
whose single job is to detect exactly this disagreement, reports the declaration clean. Same hole in
the prefix direction: declared `references/global-everyone.md` passes against prose naming only
`references/global-everyone.md.bak`.

This matters because a directory move (`docs/agents/` → `agents/`) or a root-token change is the most
likely way a real declaration drifts, and it is precisely the shape that slips through. Note this is
literally conformant to the handoff's rule as written ("must appear verbatim in that same task's
imperative string"), so it is a defect of the rule as much as of the code — but the deliverable is
the lint, and the lint returns a wrong answer.

**Fix (one predicate):** require a delimiter boundary before the match — start-of-string, whitespace,
quote, backtick, or `(` immediately preceding the occurrence — and add the truncated-path case to the
fixture set. ~5 lines plus one test.

---

## Observations (not blocking)

1. **Deleting a declaration entirely is invisible, and nothing guards the only real one.**
   `context_refs` absent or `[]` both PASS (correct per the rule), but no test asserts that the
   shipped `COMMANDER_SPINE.template.json` still *carries* a declaration. So
   `test_lint_passes_over_real_shipped_spine_templates` is vacuously satisfiable: delete
   `context_refs` from the spine and the entire suite stays green. One `assertTrue` in
   `DiscoveryTests` closes it, and it is the natural partner to B1's real direction limit.
2. **Malformed `context_refs` is handled untidily.** `"context_refs": 5` raises an uncaught
   `TypeError` traceback (still exit 1, so CI stays correct); a string value iterates characters and
   emits one garbage diagnostic per character; a dict value emits one per key.
   `context_manifest.declaration_of()` already raises a clean `DeclarationError` for exactly these —
   worth mirroring the type check, ~3 lines. Not blocking: every case still fails non-zero.
3. **Lint blind spots vs. the producer.** An empty-string path and a glob path (`docs/*.md`) both PASS
   the lint but are rejected outright by `context_manifest.resolve()`. The lint is not a schema
   validator and does not claim to be; noted only so nobody assumes lint-clean means producible.
4. **Discovery glob is one level deep.** `skills/*/templates/*.json` misses a checklist template
   nested deeper or living outside `skills/*/templates/`. Fine for today's corpus.
5. **Obligations doc, one clause.** "selected through the engine's own `active_id(cl)` (never a
   second selector)" is true via `produce()`, but `build_manifest(..., step=...)` does let a caller
   pin a step. Worth a half-sentence so #301 does not read `active_id` as inescapable. This is the
   only imprecision I found in the whole document.

## Triage candidates

- The lint is not wired into `.github/workflows/ci.yml`. Correctly out of this gate's scope
  (`.github/` is a listed exclusion) and already raised by the implementer. Coverage is not zero in
  the meantime — `test_lint_passes_over_real_shipped_spine_templates` and
  `test_default_discovery_finds_the_commander_spine_and_passes` do run the lint over the real corpus
  on every suite run.

---

## What is sound — verified, not assumed

- **Scope discipline: clean.** `git diff HEAD` shows `skills/commander/templates/COMMANDER_SPINE.template.json`,
  `scripts/context_manifest.py`, `scripts/checklist_engine.py` and `scripts/verify_skip_guard.py`
  **byte-unchanged**; `.github/` untouched; no `scripts/context_projection.py`, no committed
  `CONTEXT_PROJECTION.json`. Edits confined to the three allowed files, three allowed new files, plus
  the intentionally-gitignored `OBLIGATIONS-301.md` (`git check-ignore` exit 0, matched by
  `.gitignore:1`).
- **Protected prose held.** Both non-regression greps pass on a template that is byte-identical to
  HEAD: `substitute the closest repo doctrine` and `sanctioned degradation`. The path-list refactor
  did not erode the imperative it sits beside — which was the gate's whole reason for existing.
- **The shape test is not incidental.** I mutated the module object the test itself uses
  (`tests/test_context_manifest.py:31` loads `cm` via importlib) and re-ran the single test: 4/4
  injected defects were caught — a row emitted as a tuple, a `Path` value in the manifest, an `int`
  dict key, and an absolute root path leaking into `content()`. Baseline passes. It genuinely proves
  JSON-native + round-trip-identical + no absolute paths in content, which is as close to "assignable
  to an episode `context` field untransformed" as is checkable before #301's record shape exists.
- **The obligations statement is truthful.** All five *may rely* claims verified line-by-line against
  `scripts/context_manifest.py`: `contract: 1` (L55/286); rows exactly `{root, path, rev}` with
  `required` deliberately not copied (L227-233); declaration order emitted verbatim, no sort, no glob,
  no directory enumeration; absent files retained as `rev: null` so `len(files) == len(context_refs)`
  (L231); `manifest_path()` == `<agent-work-root>/<work-id>/context/<step>.json` (L307-309). All three
  *may not rely* items are real, not decorative: `/run` really is the entire varying subtree
  (L250-262), `encode()` really is presentation (L304), the path really is layout-dependent. **Nothing
  in the document promises use** — the only "use" language is the explicit denial in fact 3, matching
  the producer's own docstring. The durability hazard is stated and true; the cardinality risk is
  stated correctly (one file per step, keyed by `manifest_path(..., step)`) and correctly escalated as
  an Admiral float rather than resolved unilaterally.
- **No false FAIL exists.** Twelve independent probes, including case mismatch, missing `imperative`,
  multiple offenders across multiple tasks, and non-checklist JSON: I could not make the lint reject a
  valid declaration. The accept path is real, so the negative test's failure cannot be coming from a
  probe that always fails — the specific trap the handoff was shaped to catch is genuinely avoided.
  The negative test also asserts the offending path appears in stderr, not merely a non-zero exit.
- **Constraints held.** `python -m pytest` throughout. No 3.13+-only API in any changed or new file —
  the single grep hit (`tests/test_context_manifest.py:692`) is a pre-existing *comment* naming
  `read_text(newline=)` as the hazard, not a call, and sits outside the diff hunk. No new `skipTest`
  anywhere: full suite `1221 passed, 2 skipped, 329 subtests passed`, exit 0, and
  `python scripts/verify_skip_guard.py` exits 0 ("2 skips, all match documented allow-tuples"). The
  defect that blocked the previous gate has not recurred.
- **Full invariant chain re-run in my hands, verbatim**, every command exit 0 — including the bare
  node-id `pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected`,
  which resolves because the test was correctly moved to module level.
- **Evidence reproduced, not accepted.** Every claim in `IMPLEMENTER_RESULT.md` that can be
  re-executed was re-executed and matched. The one exception is the TDD RED transcript, which is not
  independently reproducible now that the script exists; the GREEN half and all downstream evidence
  reproduce exactly, so I do not treat that as a finding.

## Map Impact check

Notes match the diff. The new lint is a read-only sibling of the existing `scripts/verify_*.py`
family and imports nothing from `context_manifest.py` (shared key name only, documented at L36-38).
No architecture-significant divergence to reconcile; nothing requiring Cartographer. The single
capability claim in the notes — "a mechanical guard now exists that keeps a spine step's
`context_refs` declaration from silently narrowing away from its own `imperative` prose" — is the
**same inverted claim as B1** and must be corrected with it: the guard is real, but it guards the
other direction.

## Workflow Feedback

- **The handoff propagated the direction inversion.** Its "The lint" section says the check catches
  "the declaration silently *narrowing* away from the prose" and then that it cannot catch "prose
  naming a file the declaration omits" — the same direction, described twice with opposite verdicts.
  The implementer copied the framing faithfully into three files. The rule the handoff states
  operationally ("each declared `path` must appear verbatim in that same task's `imperative`") is
  correct and unambiguous; the *narrative* around it is not. Handoffs that pin a mechanical rule
  should state the direction in set terms ("declaration ⊄ prose is an offense; prose ⊄ declaration is
  invisible") rather than in the language of narrowing/widening, which inverts under reading.
- **"Verbatim" was under-specified.** The handoff said "appear verbatim in that same task's
  `imperative` string" without saying whether a substring occurrence inside a longer path counts. The
  implementer took the literal reading, which is defensible; a one-clause "as a whole path token, not
  a substring of a longer path" would have foreclosed B2 at authoring time.
- **The pre-authored invariant chain worked exactly as intended** and caught a real defect in-gate
  (the bare node-id vs. class-nested test). The implementer's workflow-feedback point — that a
  postcondition pinning a bare `test_x` node id implies a module-level function — is correct and
  worth folding into the handoff pattern.
- **`docs/agents/CREW_CONTEXT.md` and `docs/agents/GLOSSARY.md` do not exist in this worktree**, so
  the survey's `r0-context` imperative and the Fowler record's default `repo_standards_ref` both point
  at absent files. I substituted the standards the repo actually ships (the `verify_*.py` convention,
  `docs/CHECKLIST_SCHEMA.md`, `context_manifest.py`'s docstring) and logged the substitution in the
  record. Worth reconciling in the reviewer skill's templates.

## Path to APPROVE

Both blockers are text-and-one-predicate fixes, in files already inside this gate's allowed scope:

1. Correct the direction statement in `scripts/verify_context_declaration.py`'s docstring, the new
   `docs/CHECKLIST_ENGINE_DESIGN.md` section, and the fixture `_readme` (and, for the record, the
   handoff).
2. Replace bare `in` with a delimiter-boundary match at `verify_context_declaration.py:76`, and add
   the truncated-path case (`agents/GLOSSARY.md` vs prose `docs/agents/GLOSSARY.md`) to
   `tests/fixtures/context_declaration_lint.json` with a test asserting it is rejected.

Observations 1, 2 and 5 are cheap enough to fold into the same round but are not conditions of
approval.
