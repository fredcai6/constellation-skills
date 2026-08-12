# g2 classification pass — all 48 records in episodes/active/

Standard applied (Commander-set, not relitigated here): an INSTRUCTION is in imperative mood
(bare base-form verb opening a sentence or clause with no subject), addresses a reader
(`you`/`your`), or carries a forward-aimed deontic modal used as a directive. Everything else is
an OBSERVATION. `task-intent` written in the bare infinitive is the store's house convention
(`docs/EPISODE_STORE.md:171`) and is EXEMPT unless it addresses a reader in the second person.

Counts derived by command:
- `ls episodes/active/*.md | wc -l` -> 48
- `ls episodes/active/ | grep -cE '^(issue-304-g3|issue-308|issue-309)-'` -> 32
- `ls episodes/active/ | grep -c '^issue-447-'` -> 16
- assertion inventory: 48 task-intent, 48 expected-behavior, 48 observed-behavior,
  48 impact-cost, 48 workaround, 7 suspected-cause, 6 proposed-remedy (295 total)
- second person across all statements: 2 hits, both in `issue-304-g3-005` (a1, a2), both
  QUOTATIONS of the context imperative under study ('before you open any source file'), not the
  record addressing its own reader -> OBSERVATION, left alone.
- `grep -l "## Diagnosis" episodes/active/issue-447-*.md | wc -l` -> 0 (no 447 record carries a
  diagnosis bin).

## Verdicts

RESTATED = grounded instruction, rewritten through `restate-assertion`.
UNGROUNDED = instruction the record cannot support a factual rewrite of; left untouched.
CLEAN = no instruction found in any assertion.

### issue-304-g3 (5 records, in scope)

- issue-304-g3-001 — a5 RESTATED (grounded by a4); d2 RESTATED (grounded by its own recorded
  application + d1). a1 exempt task-intent; a2/a3/a4/d1 observation.
- issue-304-g3-002 — CLEAN. a1 exempt; a2/a3/a4/d1 observation; a5 is "none.".
- issue-304-g3-003 — a5 RESTATED (grounded by a3); d2 RESTATED (grounded by a3). a1 exempt;
  a2/a3/a4/d1 observation.
- issue-304-g3-004 — a5 RESTATED (grounded by a3); d2 RESTATED (grounded by a3). a1 exempt;
  a2/a3/a4/d1 observation.
- issue-304-g3-005 — a5 RESTATED (grounded by a3); d2 UNGROUNDED. a1/a2 carry second person only
  inside a quotation of the artifact under study. a3/a4/d1 observation.

### issue-309 (2 records, in scope)

- issue-309-001 — d2 RESTATED (grounded by d1 + a3). a1 exempt; a2/a3/a4/a5/d1 observation.
- issue-309-002 — d2 RESTATED (grounded by its own recorded filing + a3). a1 exempt; a2 uses a
  PREDICTIVE "should exit 0" in an expected-behavior field, directing no reader -> observation;
  a5 is a noun-phrase subject with a present-tense predicate -> observation; a3/a4/d1 observation.

### issue-308 (25 records, in scope)

- issue-308-001 — a5 RESTATED (grounded by a4 + a3). This is the handoff's own worked BEFORE.
- issue-308-002 — a5 RESTATED (grounded by a4 + a3).
- issue-308-003 — CLEAN. a5 already observational ("The crew pivoted to...").
- issue-308-004 — a5 RESTATED (grounded by a3).
- issue-308-005 — a5 RESTATED (grounded by a4).
- issue-308-006 — a5 RESTATED (grounded by a4 + a3).
- issue-308-007 — a5 RESTATED (self-grounding: the assertion's own subject phrase already names
  it as epic-226's applied workaround; only the mood changes).
- issue-308-008 — a5 RESTATED (grounded by a4).
- issue-308-009 — a5 RESTATED (grounded by a3).
- issue-308-010 — a5 RESTATED (grounded by a3).
- issue-308-011 — a5 RESTATED, PARTIAL (grounded by a3); the second clause dropped as ungrounded.
- issue-308-012 — a5 RESTATED (grounded by its own second sentence + a3).
- issue-308-013 — a5 RESTATED (grounded by a3 + a4).
- issue-308-014 — a5 UNGROUNDED.
- issue-308-015 — a5 UNGROUNDED.
- issue-308-016 — CLEAN. a5 already observational ("The reviewer inferred...").
- issue-308-017 — a5 UNGROUNDED.
- issue-308-018 — a5 RESTATED, PARTIAL (grounded by a3 + a4); the auditor-provenance clause
  dropped as ungrounded.
- issue-308-019 — a5 UNGROUNDED.
- issue-308-020 — a5 RESTATED (grounded by a3).
- issue-308-021 — a5 RESTATED (grounded by a4 + a3).
- issue-308-022 — CLEAN. a5 is "UNKNOWN -- no workaround was applied."
- issue-308-023 — a5 RESTATED (grounded by a1 + a3 + a4); the quoted sensor instruction is
  already framed as a quotation ("recorded as the sensor's words and deciding nothing") and is
  carried through verbatim.
- issue-308-024 — a5 RESTATED (grounded by a3, verbatim).
- issue-308-025 — a5 RESTATED (grounded by a3 + a4).

### issue-447 (16 records) — CHECKED, not assumed

All 16 read in full. Every `a1` is a bare-infinitive or past-tense `task-intent` (exempt / already
observational); every `a2`-`a5` is past tense with a real subject; no imperative-mood clause, no
second person, no forward-aimed deontic modal anywhere; no diagnosis bin exists in any of them.
**0 restatements needed.** Per-record verdict:

- issue-447-001 CLEAN — a5 "The two unfalsifiable postconditions were found by cold reading..."
- issue-447-002 CLEAN — a5 "Row R3 was deliberately not invoked..."
- issue-447-003 CLEAN — a5 "Decision 3 was regraded..."
- issue-447-004 CLEAN — a5 "One cold reader with a single-question brief was put on..."
- issue-447-005 CLEAN — a5 "The run paired each -k gate with an unfiltered whole-file..."
  (the handoff's own AFTER-SHAPE model)
- issue-447-006 CLEAN — a5 "The rework enumerated every site asserting the claim by command..."
- issue-447-007 CLEAN — a5 "The g4 reviewer regenerated the archived output..."
- issue-447-008 CLEAN — a5 "The g2 implementer used the engine's amend --op retext-check..."
- issue-447-009 CLEAN — a5 "The guard's own module was excluded from the scanned surface..."
- issue-447-010 CLEAN — a5 "The path was resolved before being handed to git..."
- issue-447-011 CLEAN — a5 "The reviewer wrote four leak mutations of its own..."
- issue-447-012 CLEAN — a5 "Every subsequent suite run in the run was prefixed..."
- issue-447-013 CLEAN — a5 "A reason-carrying approval census was added for the leg..."
- issue-447-014 CLEAN — a5 "Two different questions were separated..."
- issue-447-015 CLEAN — a5 "The comparison was re-founded on unmodified worktree files..."
- issue-447-016 CLEAN — a5 "The census entry was updated in the same edit as the prose..."

## Tally

48 examined / 32 in scope / 27 restated. 5 UNGROUNDED, left untouched.
