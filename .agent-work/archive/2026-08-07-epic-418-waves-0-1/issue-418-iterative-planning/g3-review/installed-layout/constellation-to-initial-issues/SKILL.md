---
name: constellation-to-initial-issues
description: Cut a confirmed shaped brief into one runnable current wave while preserving later outcomes as nonbinding forecast and uncertainty. Use when Explorer has confirmed a shaped brief and an Admiral needs the smallest evidence-supported initial issue cut.
invoker: both
---

# Constellation To-Initial-Issues

Turn one confirmed `SHAPED_BRIEF` directly into an initial-cut manifest. Only
`current_wave.issues` is runnable. Forecast, uncertainty, and parked
possibilities remain explicitly nonbinding.

## Artifacts

- Input: `templates/SHAPED_BRIEF.template.json`, the strict Explorer-to-cutter
  contract. Do not translate it through a prose handoff.
- Output: `templates/INITIAL_ISSUE_SET.template.json`, which preserves the
  brief's title, source identity, intent, boundaries, forecast, and uncertainty
  while adding current-wave issue drafts.
- Filing: one adapter seam with GitHub as the operational default and Markdown
  as the offline proof. Filing is receipt-backed and idempotent.

## Method

1. Verify the confirmed shaped brief with `scripts/verify_issue_set.py`.
2. Draft the smallest coherent current wave. Every issue is a bounded vertical
   slice with acceptance or falsification evidence and explicit latitude.
3. Build and verify the initial manifest. Zero dependency edges is valid;
   dangling targets and cycles are not.
4. Obtain an independent read of coverage, scope, edge sanity, and HITL/AFK
   choices.
5. On an authorized filing go-ahead, run `scripts/file_issue_set.py`. The filer
   re-verifies inputs and iterates only `current_wave.issues`.

The strict fields, eight rendered headings, and adapter/receipt invariants are
documented in `references/manifest.md`.
