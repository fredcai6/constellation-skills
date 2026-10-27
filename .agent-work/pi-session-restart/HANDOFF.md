# Constellation Pi session restart

Updated 2026-10-23. Human requested a local handoff before restarting the session. Latest completed action: install reviewed targeted-handoff changes locally into Codex and Claude.

## Start here

Read this file, then the Pi README and the latest closeout:
- `/home/tommy/projects/constellation-pi/README.md`
- `/home/tommy/projects/constellation-pi/.agent-work/targeted-handoff-sufficiency/CLOSEOUT.md`
- Independent review: same directory, `reviewer-result-2.md`.

No new implementation task is approved beyond the completed slice. Resume discussion with the human. Do not rerun paid evaluations just to recover context. The active Pi workflow is at human acceptance pending; do not record acceptance on the human's behalf.

## Intent and design decisions

Pi owns Commander and crew sessions; external agents, eventually Telegram, are clients. Constellation's engine and Pi should feel native together, while existing direct Claude/Codex skill workflows continue working. This is a foundation expected to evolve, not a throwaway. Keep architecture light: ordinary actions follow role and workflow state, with explicit scoped direction by the human or supervising agent allowing exceptions. Catch failures with independent review rather than attempting to prohibit every possible mistake.

Files are the information flow. A complete workbench input/handoff must be sufficient without the invoking agent explaining it again. Planners distill long issues into targeted assignments; downstream workers should normally read their handoff, local project guidance and selected necessary evidence. They should not automatically reread the original initiating documents. Preserve operative requirements and authority by meaning, not literal repetition. Provenance is optional audit/conflict context, not required reading or a grant of authority.

Use Sonnet 5.5 for real engineering and Haiku 5.5 for smoke/fixture runs. User explicitly said not to skimp on real work merely to optimize for the lightest model. Track per-request time, money, tokens and cache usage for eventual local models. Remote access and local-provider hookup remain future work. No automatic session history compaction/rollover has been implemented.

## Repositories and commits

Pi: `/home/tommy/projects/constellation-pi`, branch main, latest local commit `7073d2e`.
- `7073d2e`: targeted sufficient assignments, optional Required Inputs/Provenance, hosted evaluation fixtures, telemetry fix.
- `ca84154`: Sonnet 5.5 engineering / Haiku 5.5 smoke defaults.
- `b7abb4e`: structured handoff authoring and request activity telemetry.

Shared skills source for this work:
`/home/tommy/.codex/worktrees/0432044c-83a2-4238-9d7c-1cf22a5c85ae/constellation-skills`
- Detached HEAD `efbc1381`: four targeted-handoff/result templates.
- Parent `c292dbd1`: concise result guidance.
- Earlier `90cb2cd9`: reviewer result artifact contract.
- Main checkout `/home/tommy/projects/constellation-skills` was NOT advanced/cherry-picked; last observed HEAD `3ac7a1ab`. Do not assume it contains these template changes. Use the worktree above as the Pi `--source` when exercising current templates.
- Commits are local only. No push.

GPU manager: `/home/tommy/projects/gpu-manager`; earlier read-only inventory change at `0f52797`, 60 tests reported then. No GPU-manager source or running GPU work was changed in this latest slice. Earlier handoffs/workflows remain separate; do not consolidate or close them without checking their state.

## What the latest slice changed

- Structured and handwritten role handoffs accept optional Required Inputs and Provenance, preserving mandatory fields, statuses and existing contracts.
- Current prompts are v4. Historical v1/v2 and first hosted v3 are preserved for saved-session compatibility.
- Explicit scoped overrides are supported. Authoring approval alone does not authorize implementation; an approved implementation plan authorizes its bounded actions.
- Reviewer judges semantic sufficiency. A finished BLOCK/COMMENT review returns status complete; blocked/partial mean the review was unfinished. Optional nonblocking suggestions may accompany APPROVE.
- Scalar result sections contain one value only. Trailing prose remains invalid; error/contract guidance improved.
- SDK telemetry now reads toolCall.name (not toolName), with a real SDK-shaped regression test. Names only; no tool arguments/content in telemetry. Historical null names remain unknown.
- Hosted evaluation is opt-in, bounded and exits nonzero on failed cases. No paid calls in npm test/imports.
- Engine, bridge, provider dependencies and model defaults were not changed by this slice.

## Evidence and evaluation

Pi workbench:
`/home/tommy/projects/constellation-pi/.agent-work/targeted-handoff-sufficiency/`

Final hosted evaluation `hosted-3/report.json` passed:
- A real Haiku planner read a 13,665-byte brief and authored a 4,233-byte packet, about 69% smaller; 0/24 unrelated canaries copied.
- The actual dispatched worker consumed that exact packet. Delivery, hidden behavior checks, unit tests, allowed scope, result evidence and no-observed-broad-read checks all passed.
- Observed reads: worker input snapshot, AGENTS.md, labels.py, test_labels.py.
- Four review packets shared the same correct candidate code: underspecified -> BLOCK; faithful -> APPROVE; falsely claims ASCII-only authorization -> BLOCK; concise exact-expression equivalent -> APPROVE. All completed/delivered and read selected original evidence.
- `provenance-probe/report.json`: additional controlled replay of the actual successful assignment, mechanically relocated and augmented with visible optional original-brief provenance plus scoped replay authority. All worker checks passed without an observed provenance read. This was not an independent second planner trial.
- These are narrow fixture results, not general proof of lossless semantic compression or total-context efficiency. Read tracing is heuristic, not a sandbox.

Preserve failed `hosted-1` and `hosted-2`; they exposed real authority, scalar-result and telemetry issues. `HOSTED_FINDINGS.md` explains them. Do not present only the final success as the whole history.

Validation: 110 Pi tests pass and typecheck clean. Final independent Sonnet review APPROVE in `reviewer-result-2.md`. Eight focused shared delivery/evidence tests pass. Earlier broader corpus runs hit environmental/preexisting failures and a baseline comparison timed out; no broad shared-suite success is claimed.

## Costs and time

`USAGE_FINAL.json` contains request-level telemetry and role/stage aggregates; `CLOSEOUT.md` explains accounting.
Known estimated costs (SDK model catalog, not invoices):
- Engineering workflow: $3.002947; 88 provider requests, two with unknown costs.
- Hosted failed iteration 1: $0.012735.
- Hosted failed iteration 2: $0.019380.
- Final passing hosted iteration 3: $0.016013.
- Optional provenance replay: $0.003656.
- Known subtotal: $3.054731, plus unknown usage for two engineering requests. Unknown is not zero.

Final hosted-3 summed API request time/cost by stage:
- Plan: 9.7 seconds / $0.002187.
- Implement (Commander plus worker requests): 31.8 seconds / $0.004839.
- Four reviews: 58.0 seconds / $0.008987.
These are sums of API request duration, not end-to-end wall times. Parent invocation elapsed includes crew waiting; do not add parent and child invocation durations. Provenance replay took about 18.4 seconds end-to-end.

## Active workflow and artifacts to preserve

Run: `/home/tommy/projects/constellation-pi/.constellation-pi/targeted-handoff-sufficiency`
Latest observed state: accept pending, reviewer APPROVE, 11 invocation calls, maxCalls 12. Do not manufacture human acceptance.
Approved task hash: `dad1dc48e1035b2c188a3c2c948e80b91cca161cebfb7fc1fb8f3a642f344cb9`.
Approved plan hash: `5c2be1dc3f3e2001220d6747fd535887495d73eac11742bd87e2f4689bdb3063`.

An earlier Commander accidentally used prose as the literal Result Artifact path. The completed invocation references this actual file and its hash:
`/home/tommy/projects/constellation-pi/Write a fresh concise implementation result at the path given by the controller Output Contract.`
Preserve it; do not commit or silently move/delete it. Tool schema guidance now asks for an exact pathname. This ergonomics limitation is recorded.

`.agent-work/` and `.constellation-pi/` contain untracked session evidence, not source changes to add wholesale. The source worktree also has existing unrelated workbench directories. Leave them intact. A recovery restored a worker-created stash containing exactly the four task-owned templates; no unrelated work was lost.

## Local installation just completed

Used repository installer with `--scope user --skills commander implementer reviewer --force` for Codex and Claude. Installed under:
- `/home/tommy/.codex/skills/constellation-{commander,implementer,reviewer}`
- `/home/tommy/.claude/skills/constellation-{commander,implementer,reviewer}`
All four installed template files were byte-verified against source. Engine bundle installed in both agents' `skills/constellation-engine/scripts`.

The standard installer removed Codex's pre-migration Workbench scripts directory, while the older Workbench reference still points there. Added compatibility symlink:
`/home/tommy/.codex/skills/constellation-workbench/scripts -> ../constellation-engine/scripts`
Verified the old checklist_engine.py path resolves and CLI --help works. Preserve compatibility during future installs; installer might remove that link again.

Claude's separately named legacy skills under `.claude/constellation/skills` and their symlinks remain in place; the refreshed `constellation-*` skills are separate. No hooks/settings were wired. Installer reported Context Governor hooks unwired and refused to edit git-tracked .mcp.json; this did not block skill installation. Installer also wired the source repo pre-commit hook. Restart Codex to refresh skill discovery.

## Safety and command notes

Standing human authorization: Pi may send relevant Constellation Pi and GPU manager source, docs, handoffs and tests to Anthropic Claude for planning, implementation and review, with bounded paid usage. Exclude secrets and unrelated personal data. Authorization persists until revoked. Restrictions on changing running GPU workloads remain.

Configured credentials: `/home/tommy/.config/constellation-pi/credentials.env`. Source only before authorized calls; never print its contents or expose keys in prompts/logs. No need to inspect credentials to resume.
Working Python:
`/home/tommy/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/bin/python`
Default shell python/py has environment issues; explicitly use working executable for checks.

From Pi project:
`node --import tsx src/cli.ts status --run .constellation-pi/targeted-handoff-sufficiency`
`node --import tsx src/cli.ts usage --run .constellation-pi/targeted-handoff-sufficiency`
For provider work, read README/current CLI help and pi-commander skill first. Reuse existing runs; do not start duplicate sessions to get around gates. Drive engine transitions through APIs, never hand-edit checklist JSON. No new paid calls needed for handoff recovery.

## Possible next discussion

The current targeted-handoff slice is implemented, reviewed and locally installed. Human acceptance remains the formal open step. Next work should be chosen with the human, likely a real bounded follow-up using these packets and accounting rather than more synthetic optimization. Session-history compaction, stable-prefix/cache evaluation, local providers and remote clients are separate future slices. No new issue or implementation scope has been approved for those here.
