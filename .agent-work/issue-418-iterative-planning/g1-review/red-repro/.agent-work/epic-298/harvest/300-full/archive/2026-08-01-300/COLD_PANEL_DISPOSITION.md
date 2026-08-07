# Cold panel — findings and dispositions (issue #300)

Full cold panel per `decision:full-cold-panel` (spec B0.4). Three Opus critics, one lens each, each
reading **only** the committed diff and the mission frame — no authoring context, no gate results,
no sight of each other. Reports: `.agent-work/300/cold-panel/CRITIC-{intent-fit,testability,simplicity}.md`.

**41 findings: 3 BLOCKING · 17 SERIOUS · 21 MINOR.** Every one is dispositioned below. A critic never
self-triages; these dispositions are mine, and they are surfaced to the Admiral because no human is
reachable.

**UNTRIAGED: 0**

The panel earned its keep. Two of the three blockers were defects in the **acceptance test itself** —
the one test the whole issue rests on — and both had passed two independent reviewer rounds, because
each round reviewed against a contract that did not think to ask "does this test actually falsify?".
The panel's method (45 deliberate mutations, 11 surviving) is what found them.

---

## BLOCKING

**intent-fit B1 — nothing in the delivered system ever produces a manifest.** No caller anywhere;
AC1 is satisfied definitionally over a production population of zero.
- Disposition: **FLOATED to the Admiral — not mine.** This is a scope question (is #300 the substrate
  with wiring belonging to #305, or is #300 incomplete?), and my latitude sends adding or re-scoping
  work upward. Floated with my own read attached (substrate-is-correct plus a doc fix naming the
  successor issue, because a reader of `main` currently cannot tell deliberate sequencing from
  oversight). Rework 2 was explicitly instructed **not** to add a caller, so the Admiral's decision
  is not pre-empted.

**testability B2 — the acceptance test never compares the bytes the two environments produced.** It
re-encoded both parsed artifacts with the *parent's* encoder; a locale-dependent encoder passed green.
- Disposition: **EDIT — fixed in rework 2, with mutation proof.** Each child now writes its own
  content bytes and the parent byte-compares those; children run with distinct cwds (both previously
  inherited pytest's, holding constant the one environment fact the record reads). Mutation M49
  survives at HEAD, killed here.

**testability B1 — `/run` is not actually the exclusion set.** `content()` denied one key rather than
admitting known keys, and the set assertion was one-directional and blind to added keys.
- Disposition: **EDIT — fixed in rework 2.** `CONTENT_KEYS` allow-list plus a bidirectional set
  assertion, so a new key is excluded by default. Mutation M36 survives at HEAD, killed here.

---

## SERIOUS

**intent-fit S1 — nothing is assembled; bytes are read only to hash and discarded, yet the record
says files "were made available".**
- Disposition: **PARTIAL EDIT, remainder rides the float.** The overclaiming wording is corrected;
  whether assembly-proper belongs to #300 is the same scope question as B1.

**intent-fit S2 — the only real declaration projects six rows, all `rev: null`; revision identity is
demonstrated only under fixtures and a test-only install shim.**
- Disposition: **EDIT — fixed in rework 2** (`RealCheckoutSkew` now materialises real tracked files
  whose revs must agree, plus an untracked file whose rev must differ). The residue — that the
  *shipped* declaration resolves to null in a bare source checkout — rides the float, since it is the
  same "no production caller" fact seen from another angle.

**intent-fit S3 — `manifest_path()` settles the cardinality question unilaterally while the frame
calls it unsettled.**
- Disposition: **ACCEPT as flagged, no code change; obligation already routed.** One-manifest-per-step
  is stated in `OBLIGATIONS-301.md` as a named cross-interface risk requiring an Admiral float if #301
  assumed otherwise. That is the correct handling: state the obligation, do not unilaterally
  renegotiate it.

**intent-fit S4 — committed docs cite gitignored worktree-local files.**
- Disposition: **EDIT — fixed in rework 2.** Every `.agent-work/` citation removed from committed
  files; the `.gitattributes` condition converted from a citation of a worktree-local gate check into
  a committed, deliberately pattern-blind test. Three critics found this independently, and it was
  **my** doing — I put a gitignored path into a committed docstring.

**testability S3 — `RealCheckoutSkew` is vacuous in every environment.**
- Disposition: **EDIT — fixed in rework 2.** A test that cannot fail is worse than no test; it reads
  as coverage.

**testability S4 — the locale half of the mutation is inert on windows-latest, CI's only platform.**
- Disposition: **FILE — issue #323.** Real, and not honestly fixable inside #300: it needs either a
  locale-sensitive operation the producer actually performs, or a second CI platform. Filing beats a
  fix that pretends.

**testability S5 — the `root` token is unguarded in both producer tests and lint; retargeting an entry
`repo`→`skill` is invisible.**
- Disposition: **FILE — issue #323** (same issue, same shape). Not a live wrong answer today; a real
  hole in the guard.

**testability S6 — the shipped declaration's contents are unpinned; an entry can be silently dropped.**
- Disposition: **EDIT — fixed in rework 2**, pinned as a literal six-row list.

**testability S7 — `declaration_of`'s type guard is untested; an invalid declaration silently becomes
an empty manifest.**
- Disposition: **EDIT — fixed in rework 2.** Silence was the wrong failure mode; it now raises, driven
  through `str`/`bytes`/`dict`/`int`/`bool`. Mutation M19 survives at HEAD, killed here.

**testability S8 — the `.gitattributes` guard the docstring leans on does not pin what it claims;
exemptions scoped to the declared corpus survive it.**
- Disposition: **EDIT — fixed in rework 2**, converted to a pattern-blind committed test. Mutation S8
  survives at HEAD, killed here.

**simplicity S1 — `required` is a schema field with no reader.**
- Disposition: **REJECT, with reason.** It is declaration metadata whose consumer is issue #304
  (degraded-mode reporting on a missing required entry), which the frame lists as out of scope for
  #300. Deleting it now would force #304 to re-add it and re-migrate every declaration. The schema row
  already says "advisory (not enforced by the producer)", which is honest. Cost accepted knowingly.

**simplicity S2 — five injection seams and one constant with zero callers.**
- Disposition: **EDIT — deleted in rework 2** (`RUN_POINTER`, `run_facts(session_id=, now=)`,
  `build_manifest(step=, run=)`, `produce(run=)`). `RUN_POINTER` was the worst of them: it advertised
  a JSON-pointer contract the code did not implement.

**simplicity S3 — `AdversarialDeclarations` re-tests properties already covered inline (~90 deletable
lines).**
- Disposition: **REJECT, with reason.** The duplication is real but the fixture-driven form is what
  lets the lint be exercised over *whole realistic checklist shapes* rather than hand-built dicts;
  that is the difference between testing the parser and testing the tool. Paying ~90 lines for it is a
  fair trade, and this run has twice been bitten by tests that only exercised convenient inputs.

**simplicity S4 — the py3.12-compat AST guard duplicates CI's own pinned 3.12 job.**
- Disposition: **REJECT, with reason.** CI is the authority, but it reports *after* push; the AST
  guard reports in the local suite, which is where a crew finds out. A sibling issue in this very
  epic shipped a red CI on exactly this defect. The duplication buys a shorter feedback loop for a
  live, already-realised failure mode.

**simplicity S5 — `test_a_live_spine_in_this_work_area_also_projects` is a 24-line no-op.**
- Disposition: **EDIT — deleted in rework 2.** Its own comment argued for its deletion, and its
  earlier `skipTest` form was the g1 blocker.

**simplicity S6 — committed artifacts cite gitignored run artifacts.**
- Disposition: **EDIT — fixed in rework 2.** Same finding as intent-fit S4; two critics, independently.

**simplicity S7 — the lint's trailing-boundary rule is ~40 lines defending a shape absent from the
corpus.**
- Disposition: **REJECT, with reason.** I scoped that half in deliberately after reproducing the
  defect: declared `X.md` matching prose `X.md.bak` is the same bug as the leading half, and shipping
  one end without the other is arbitrary rather than principled. The corpus not containing a `.bak`
  sibling *today* is what makes the guard cheap insurance rather than a response to damage.

---

## MINOR

- testability M1 — neither root-escape guard is independently exercised.
  Disposition: **FILE — issue #323.**
- testability M2 — `_MANIFEST_CONTRACT_VERSION` is a self-referential oracle.
  Disposition: **ACCEPT, no change.** A contract version can only be checked against itself; the real
  guard is the bidirectional envelope assertion added for B1.
- testability M3 — no golden-bytes pin on a produced manifest.
  Disposition: **FILE — issue #323.** Worth having; not blocking.
- testability M4 — `run_facts()` has no direct test.
  Disposition: **ACCEPT, no change.** Everything it produces is in the excluded subtree by
  construction, so a defect there cannot reach content — which is now enforced by the allow-list.
- testability M5 — a checklist with no `work_id` silently writes to a directory named `None`.
  Disposition: **FILE — issue #323.** A real silent-wrong-path bug, just not reachable from any
  shipped checklist.
- testability M6 — `required: true` on an absent file is never exercised.
  Disposition: **DEFER to #304**, which owns degraded-mode reporting and is the field's only consumer.
- testability M7 — lint false FAIL on `./`-prefixed prose.
  Disposition: **FILE — issue #323.**
- testability M8 — lint false PASS on `docs/a.md.~1`.
  Disposition: **FILE — issue #323.** Same root as the reviewer's own `tc1` (tighten the trailing rule
  from a path-char deny-list to a punctuation allow-list); one fix closes both.
- testability M9 — non-canonical path spellings accepted and recorded verbatim.
  Disposition: **FILE — issue #323.**
- testability M10 — `INSTALL_SHIM` hardcodes the installed layout with nothing tying it to the
  installer. Disposition: **FILE — issue #323.**
- testability M11 — nothing in production calls either script.
  Disposition: **FLOATED** — duplicate of intent-fit B1.
- testability M12 — the tests mutate shared git state (worktree add/remove).
  Disposition: **ACCEPT, no change.** Verified across this run: worktree count 5 before and after
  every gate, with cleanup in `finally`. Noted as a standing hazard, not a defect.
- simplicity M1 — `rev()`'s docstring names a test method.
  Disposition: **EDIT — fixed in rework 2** with the `.agent-work/` citation removal.
- simplicity M2 — the escape guard in `resolve()` is unreachable (0 hits in 2745 fuzzed inputs).
  Disposition: **ACCEPT, no change.** Defence in depth on a security-shaped guard, behind cheaper
  checks that fire first. Deleting an unreachable path-escape guard to save four lines is the wrong
  trade.
- simplicity M3 — the design-doc section restates the module docstrings.
  Disposition: **ACCEPT, no change.** The docstring serves the code reader, the design doc the
  architecture reader; this repo's convention keeps both.
- simplicity M4 — `durable` and `repo` are never distinct.
  Disposition: **FILE — issue #323.** They diverge exactly when an Admiral lease is active — a
  condition verified live this run — so the token is right and the *test* coverage is what is missing.
- simplicity M5 — three `load()` helpers and two checklist-shape predicates.
  Disposition: **FILE — issue #323.** Genuine tidy-up, no behaviour change.
- simplicity M6 — double cleanup in the enumeration booby-trap.
  Disposition: **ACCEPT, no change.** Idempotent cleanup is not a defect.
- simplicity M7 — corpus-size magic numbers and a redundant round-trip.
  Disposition: **FILE — issue #323.**
- intent-fit M1 — `required` is dropped from the row on a rationale the row contradicts.
  Disposition: **EDIT — wording corrected**; the substance is simplicity S1's REJECT above.
- intent-fit M2 — root-token semantics defined nowhere committed; `durable` ambiguous against the code
  owning that word. Disposition: **FILE — issue #323.** The tokens are load-bearing and belong in the
  committed schema, not only in a docstring.

---

## Summary

- **EDIT (fixed in rework 2): 14** — including all three of the in-scope blockers' constituent parts.
- **FILE (issue #323): 14** — one consolidated follow-up; none is a live wrong answer today.
- **REJECT with reason: 5** — `required`, the fixture duplication, the AST guard, the trailing
  boundary, and the design-doc overlap.
- **ACCEPT, no change: 7** — verified non-defects.
- **DEFER to a named issue: 1** (#304).
- **FLOATED to the Admiral: 2** (intent-fit B1 and its duplicate testability M11).

**UNTRIAGED: 0**
