# G4 Implementer Result

`gate_id: g4`  
`red_exit: 1`  
`green_exit: 0`  
`diff_digest: sha256:251c48b0ae6308d01bbd813f037b06a4f2ad40e468e9cd90dda2baadff720355`

## Outcome

Built the hash-pinned, fully offline Epic #418 demonstration under `.agent-work/issue-418-iterative-planning/demo-epic-418-iterative-planning/`. It regenerates the historical five-item cut as one three-issue current wave, two nonbinding forecast outcomes, one active uncertainty, and a concrete blocking-discrepancy → repair walkthrough. All five required Markdown artifacts and strict machine packets are present.

## Frozen inputs and archive preservation

- `DESIGN_SPEC.md`: `b2ef1b2a51268b2ee806541f625d7fd8c52b28179239ed7291308a140d2e9ddb`
- `ISSUE_SET.json`: `17bb5086744f23956146cdff02b9cccf02116595be9ce93727a5fa12b002f1f6`
- Both matched before historical inputs were read.
- `ARCHIVE_BEFORE.sha256` and `ARCHIVE_AFTER.sha256` contain the same 28 ordinal path+SHA entries; no archive file changed.

## TDD and verifier evidence

Tests were authored before the verifier scripts, and both verifiers existed before the demo directory. The exact command first failed causally:

```text
uv run python scripts/verify_epic_418_demo.py --work-id issue-418-iterative-planning
REFUSED: demo directory missing
exit 1
```

After offline generation, the identical command passed:

```text
Epic 418 demo ok: issue-418-iterative-planning (5 original items, 28 archive files)
exit 0
```

The iterative acceptance verifier passed all ten frozen items. Registration rails passed for `to-initial-issues` and `replan`.

## Test evidence

- Relevant suite: `169 passed, 449 subtests passed`.
- Full suite after the bounded coverage-ledger rename fix: `1662 passed, 2 skipped, 636 subtests passed in 229.90s`.
- Initial full run exposed the last live home mapping (`to-issues`); only the Constellation home was renamed to `to-initial-issues`, while the external provenance name remained intact. The focused coverage rail then passed `5 passed`.
- Seven changed JSON templates parsed successfully; `git diff --check` exited 0.

## Demonstration result

- Derived counts: 4,844 → 767 words; 5 → 3 runnable issues; 3 → 2 edges.
- A/C/D form the coherent AFK current wave; B/E remain nonbinding HITL forecast.
- Every original A–E item has one disposition.
- Intent, constraints, decisions, evidence, and completion are explicitly preserved.
- Blocking repair holds current wave/forecast; evidence-only disposition creates no issue; fixed-boundary change remains inapplicable and escalates to human.
- Deny receipt records raise-on-write tracker, failing `gh` shim, subprocess/network spies, and zero calls.
- Latitude materially increases because current-wave issues retain implementation freedom while HITL obligations are removed from the runnable queue.

## Whole-change review identity

`G4_DIGEST_PATHS.txt` contains the 39 ordinal-sorted live product/test/doc paths for Gates 1–4, including deleted legacy paths. `recompute_g4_digest.ps1` hashes `UTF-8(path)`, NUL, raw bytes or `<deleted>`, NUL and reproduces:

```text
sha256:251c48b0ae6308d01bbd813f037b06a4f2ad40e468e9cd90dda2baadff720355
```

## Scope, authority, and dirty-tree audit

No live tracker/GitHub/network write, commit, push, PR, archive rewrite, or unrelated-worktree overwrite occurred. Push/PR/live-issue absence is reported as an authority/tool audit assertion, not fixture proof. `INITIAL_DIRTY_SNAPSHOT.md` and `FINAL_DIRTY_SNAPSHOT.md` record inherited-versus-G4 paths.

No stop condition remains. Fresh independent G4 review is required.

Registry recovery note: the original external worker session dropped after artifact generation; deterministic closeout resumed from the durable checklist and re-ran the full acceptance evidence before this result was finalized.
