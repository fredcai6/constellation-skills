# m1 — what the engine copy's docstring says, and where each reason survives

Handoff constraint: "Every sentence of `worktree_from_spine_path`'s docstring that
states the *rule* is already carried by the hook copy and by the case table.
Before you delete, verify that — if any reason is recorded **only** in the engine
copy, carry it to the case table's docstring rather than losing it."

This is that verification, clause by clause, read at source in
`scripts/checklist_engine.py` (the docstring of `worktree_from_spine_path`) and
compared against `scripts/hooks/spine_rail.py` (`_worktree_from_spine`) and
`tests/test_worktree_derivation.py` (module docstring, `CASES` comments, and the
per-test docstrings).

**clauses examined: 13** — 9 carried already, 3 carried by this gate into the case
table's docstring, 1 already retired and deliberately not carried.

| # | clause in the engine docstring | survives in | action |
|---|---|---|---|
| 1 | The rule: walk up to the NEAREST `.agent-work` ancestor, return its parent; arbitrary depth; no such ancestor means unowned. | `spine_rail._worktree_from_spine` docstring; table module docstring; `CASES` | already carried |
| 2 | Derivable by anyone holding the path — no stamp to disagree with, no ambient reading to forge. | `CASES` case `relative-path-is-unowned` comment ("the whole point is that there is no ambient reading to forge") | already carried |
| 3 | Answers LOCATION only: where the spine lives, **hence where a check should run and where git should be invoked**. | the second half is nowhere else — it is the *consumer's* reason, and the consumer is #315 | **CARRIED** into the table docstring |
| 4 | Never answers "is this mine": ownership is the lease, and among spines sharing one tree the discriminator is binding-key provenance **(2026-08-16 worktree-is-location ruling)**. | the sentence is in the hook docstring; the **ruling citation** is engine-only (`grep -rn "worktree-is-location"` outside `.agent-work/` and `map/` returns exactly one hit, `scripts/checklist_engine.py:136`) | **CARRIED** (the citation) |
| 5 | NEAREST, never outermost, because the inner `.agent-work` under `.agent-work/archive/<epic>/workspace/` belongs to a nested sandbox project. | hook docstring; `CASES` case `nested-sandbox-double-agent-work-derives-the-inner-root` comment | already carried |
| 6 | LEXICAL ONLY — `normcase` + `normpath`, never `realpath`. | hook docstring; table module docstring; `test_derivation_is_lexical_not_realpath` | already carried |
| 7 | Lexical reason A: `spine_rail._is_valid_claim_target` checks lexically and then re-checks the RESOLVED path; resolving here would make that second check unfailable. | hook docstring; table module docstring; `test_derivation_is_lexical_not_realpath` docstring | already carried |
| 8 | Lexical reason B: importing `verify_worktree_isolation.normalize_path` would add an undeclared runtime sibling, so the idiom is inlined, as `agent_work_root._normalize` already inlines its own. | nowhere else | **CARRIED** into the table docstring |
| 9 | Lexical reason C, recorded as **retired**: keeping `origin_worktree_refusal` pure under a non-transitive purity test, retired with that predicate in #609 g2. | already retired at source; `test_derivation_is_lexical_not_realpath`'s docstring still records the purity argument for the historical record | not carried, deliberately — a retired reason is not an asset |
| 10 | Absolute input required: a relative path's answer would depend on the ambient cwd, the forgeable reading this derivation exists to remove. | hook docstring; `CASES` cases `relative-path-is-unowned`, `empty-string-is-unowned`, `non-string-is-unowned` | already carried |
| 11 | The `.json` suffix and a non-empty work-id segment are NOT required — shape questions, held at `spine_rail._is_claim_layout`. | hook docstring; `CASES` cases `non-json-leaf-still-has-a-location`, `dotfile-leaf-still-has-a-location`, `depth-zero-spine-directly-in-agent-work` | already carried |
| 12 | The twin exists because the hook is stdlib-only by design and may gain no import. | table module docstring (kept, re-scoped, in this gate's rewrite) | already carried — and must stay, it is why #610 re-adds a copy rather than an import |
| 13 | NEVER raises — returns `None` for any input it cannot derive from. | hook docstring; `test_derivation_never_raises` | already carried |

## The three carries, verbatim as they will read in the table docstring

1. **What the location is for** (clause 3): location means *where a check should
   run and where git should be invoked* — the consumer's reason, and the reason
   #315 needs the rule engine-side at all.
2. **The ruling citation** (clause 4): `(2026-08-16 worktree-is-location ruling)`
   against the sentence that ownership is the lease and the discriminator among
   spines sharing one tree is binding-key provenance.
3. **Why the idiom is inlined rather than imported** (clause 8): importing
   `verify_worktree_isolation.normalize_path` would add an undeclared runtime
   sibling; `agent_work_root._normalize` inlines its own for the same reason.
   Without this, #315 re-lands the engine copy and "improves" it into an import.

Nothing else in the engine docstring states a reason that is not already held by
the hook copy or by the case table.
