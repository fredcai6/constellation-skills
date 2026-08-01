# Launch Order: wave1-56 — Sweep the constellation debt + standing trigger (#56)

## Mission
The cross-project half of the learning loop is dormant: `scripts/collect_feedback.py` has collected 2 entries total (2026-06-11) while f1Brainz's queue grew to 56 KB; network_elo and story_time have NEVER been swept (no `.collected.json`). Full issue: `gh issue view 56`. Three parts:
1. **Operational sweep**: run `collect_feedback.py` (read its --help/source first; dry-run by default is its design) over `C:/Programs/f1Brainz`, `C:/Programs/network_elo`, `C:/Programs/story_time`. Updating `.collected.json` sidecars in those repos is sanctioned mechanical bookkeeping.
2. **Dedup/fingerprint report**: the corpus banks the same defect under different names (lease staleness ×4 names, worktree isolation ×3, idle-without-verdict ×2). Produce the deduped candidate list with recurrence counts — this is the checkpoint deliverable.
3. **Standing trigger**: in your branch, wire/document a standing cadence so the sweep never goes dormant again (e.g. a documented step in this repo's own epic closeout doctrine, or a documented scheduled-run recipe). Smallest durable mechanism wins; a doc-only trigger is acceptable if it's attached to an enforced step.

## HARD STOP — human-gated by contract
Do NOT file or comment on any GitHub issue in ANY repo, and do NOT write to `CONSTELLATION_INBOX.json` beyond what a dry-run records. Your deliverable ends at: sidecars updated + deduped dry-run report + trigger PR. The human reviews the dry-run at the wave-2 checkpoint and approves filings.

## Prior-Wave Verdicts
None — wave 1. Context you'd otherwise lack: epic issues #42–#55 already cover many swept findings (attest #44, lease #47, worktree shipping #43, portability #48, crew backend #53, idle doctrine #50). Your dedup report should mark which collected findings are ALREADY covered by an open epic issue vs genuinely new.

## Pre-Rulings
- Read-only toward the three dogfood repos except `.agent-work/*.collected.json` sidecars.
- If `collect_feedback.py` itself is broken/bitrotted, fixing it minimally is in scope (it's the mission's tool); note the fix in the PR.

## Workspace
Worktree: `C:/Programs/constellation-skills-worktrees/issue-56`, branch `constellation/issue-56`, base origin/main 363d27a. First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-worktrees/issue-56` must exit 0; paste output.

## File Ownership
Trigger doc/wiring files in your branch; `.collected.json` sidecars in the three dogfood repos; your dry-run report at `.agent-work/issue-56/sweep-report.md` (paste fully into your verdict — worktree copies are swept). Fence: everything else.

## Budget
Model tier: sonnet-class. Reviewer subagent for the trigger PR; the sweep report itself needs no crew review.

## Stop Conditions
Stop and query the Admiral if: sweeping would require mutating anything beyond sidecars; recurrence fingerprinting is ambiguous enough to change what gets filed; or the trigger needs a structural change to closeout doctrine (surfaced class).
