---
name: constellation-to-issues
description: Cut a confirmed DESIGN_SPEC into a dependency-ordered, wave-ready issue set an Admiral can run. Use when an explorer agent or a human has a CONFIRMED spec and needs it decomposed into typed, edge-ordered issues. Not triage (single out-of-scope follow-ups) and not explorer (which shapes the spec, never cuts it).
invoker: both
---

# Constellation To-Issues

Turn one confirmed design into a runnable epic: read the spec, cut it into a dependency-ordered set of typed issues, let an independent reviewer check the cut, then file on a chat go-ahead. Run at Route by the explorer agent or a human, against a confirmed `DESIGN_SPEC` path.

**No checklist. Work the cut directly** — a thin lean pass, not a gated engine. Four rules are enforced; everything else is model judgment.

## The two artifacts

- **One manifest** — the tracker-agnostic issue set (`templates/ISSUE_SET.template.json`): an epic plus a list of issues, each with an id, title, body, `type`, and `blocks` edges. Single source of truth and evidence of the cut; never a review gate.
- **One filing adapter** behind one seam: `github` is the real default, `markdown` the offline fixture. GitHub-first, seam-pluggable, not GitHub-only; a `gitlab` seam is reserved but unbuilt.

## The four encoded rules (the rail)

`scripts/verify_issue_set.py` exits non-zero — and the filer refuses to file — when any holds:

1. **Unconfirmed spec.** Re-runs `verify_spec_confirmed.py`; an unconfirmed spec is never cut.
2. **No dependency edge.** A wave-ordered epic needs at least one `blocks` edge; an edge naming no known issue is also refused.
3. **An untyped issue.** Every issue is typed `HITL` or `AFK`.
4. **A HITL issue with no reason.** `hitl_reason` is required whenever `type` is `HITL`.

Everything past well-formed — coverage, invented scope, a risky `AFK` that should be `HITL` — is judgment, deliberately un-railed.

## Steps

1. **Read the confirmed spec.** Refuse if unconfirmed (rule 1). Cut vertical-slice-first; expand–contract is available for wide refactors.
2. **Cut the manifest.** One issue per bounded slice; draw `blocks` edges for real ordering; type each issue `AFK` or `HITL` and write the reason for every HITL.
3. **Get an independent read.** A fresh-context reviewer — never the author — checks coverage, invented scope, edge sanity, and risky-AFK-should-be-HITL. Surface the epic shape and notable calls conversationally.
4. **File on a chat "go".** The filer re-runs the rail, then files idempotently via a receipt (a crash mid-file re-runs with no duplicate epic). The epic body is the wave-ordered task list with AFK/HITL labels — the Admiral's intake consumes it.

The reviewer, not the manifest, decides review weight and whether a light case may skip the rail; a defended exception needs the reviewer's co-sign plus a log entry. Schema and adapter contract: `references/manifest.md`.
