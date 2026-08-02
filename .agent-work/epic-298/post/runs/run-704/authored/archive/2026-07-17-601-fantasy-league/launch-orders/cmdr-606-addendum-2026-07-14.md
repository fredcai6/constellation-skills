# Launch Order Addendum — cmdr-606 workbook recovery

Ratifying authority: Admiral under fredcai6's 2026-07-14 instruction: "you're authorized for this and any other judgement calls. keep working without my intervention till completion".

## Ruling

Resume G1 using the separately named sanitized read-only copy below. This is an in-scope input-recovery ruling, not the production normalization-seam choice.

Original, unchanged:

- Path: `C:/Programs/f1Brainz/docs/reference_docs/Fantasy F1 2024.xlsx`
- SHA-256 before and after recovery: `C75B0F32B2835BD9FC253FDDB3B6562CC4ED4B405926493BB0C7DE6A3C97267B`

Sanitized copy:

- Path: `C:/Programs/f1Brainz/.claude/worktrees/606-league-decomposition/.agent-work/cmdr-606/sanitized-input/Fantasy F1 2024.sanitized.xlsx`
- SHA-256: `93C93BD362FD8F196C3811B2E551EDA6036A2F7540A601E7AF39AEDBB2D48560`
- Surgical change: 23 `xl/comments*.xml` classic-comment author fields changed from empty to `Recovered Author`.
- Package proof: same 521 entry names; zero non-comment entry content differences; every comment entry becomes byte-equivalent to the original when the single author replacement is reversed.
- Approved importer proof: loader-provided Node + `@oai/artifact-tool` imports the sanitized copy successfully and reports 27 sheets.

The two attempted hidden Excel open/repair passes failed before producing a copy; no Excel-generated artifact is in use. The accepted copy is mechanically verified and enters the study only because the approved importer independently reads it.

## Continued Latitude

fredcai6 cleared the Admiral to make all remaining in-scope judgments and continue without intervention through completion. The Admiral may adjudicate the upcoming seam convergence and all ordinary implementation, issue, PR, merge, and close decisions. Preserve safety boundaries: keep original inputs unchanged, keep work isolated, do not expand beyond epic #601, and do not perform unrelated destructive actions.
