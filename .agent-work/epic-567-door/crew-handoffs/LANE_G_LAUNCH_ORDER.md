# Launch Order: `cmdr-567-g — #574 one-verb mechanical closeout + #552 archiving releases the lease`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Commanders start cold. Everything you need is pasted here.

## Mission

Make shutdown **the engine's problem, not the agent's** — and make an archived run stop claiming it is active.

Both issues are the same defect seen from two ends: closeout is agent-driven prose choreography executed at the moment of maximum context exhaustion, so its steps get skipped, and the skipped step leaves visible rot on disk.

### #574 — one-verb mechanical closeout (the design anchor)

Ruling from Tommy, 2026-08-12:

> The agent should be able to just say "I'm done with this task" and the engine should automatically close up the spine, move it to archive, and turn itself off with a note back / PR the worktree. There should be a very mechanical startup/shutdown process that makes everything very predictable and not the agent's problem.

**Why the evidence supports it.** The "release-is-last" provenance rule, and every ordering trap around it, exists only because an agent sequences 5–7 ritual steps by hand (episodes → capture gate → archive → final advance → release → worktree disposition). Episode record: an Admiral's closeout was refused at 23% context and completed by accidental compaction rather than the stated remedy; a crew released its Admiral's lease via inherited env; 43 archived spines still read `active` because the release step never ran.

`spine_close` (PR #564) **already refuses to archive an unreleased run** — the refusal half exists. This issue builds the half that makes the refusal never fire: the engine doing the sequence itself.

**Contract sketch** — one door tool (working name `spine_done`, extending `spine_lifecycle.close_work`):

1. **Verify**: closeout preconditions checked mechanically (episodes captured, gates terminal or explicitly waived, tree state clean/staged). A failed check returns ONE actionable refusal, not a ritual to re-derive.
2. **Close**: final advance on the terminal step; release the lease as the last journaled action (ordering is now the script's problem, not the agent's).
3. **Reap**: remove this owner's binding entries and gauge state; the stop-rail stops watching a done run.
4. **Archive**: move the work area under `.agent-work/archive/<date>-<work-id>/` — including child plans, whose leases must be released too (the #552 gap).
5. **Dispose of the worktree**: push the branch and open the PR / write the return note. **OPEN QUESTION (Tommy to rule): does PR-opening live in the engine verb or in the wrapper script that also manages the worktree?** — this one is **not yours to settle**; float it.
6. Symmetric startup: `spine_open` already mints identity/bindings/work area; open and done become the only two lifecycle points where per-owner state is created and destroyed.

**Exit criteria.** An agent at any tier finishes a run with a single door call; no agent-facing instruction anywhere sequences release/archive/advance by hand; a run that ends through this verb leaves zero active leases, zero bindings, zero gauge state, and a disposed worktree.

### #552 — archiving never releases the lease

Measured on `abad896d`, 2026-08-10. Every `*.json` under `.agent-work/` whose `engine_session.status` is `"active"`:

```
active leases: 43
          <1h:  0
        1-24h:  2      <- one is this session's live Admiral spine
         1-7d: 25
          >7d: 16
 no heartbeat:  0

inside .agent-work/archive/: 17

oldest:
  751.7h  by=reviewer   .agent-work/archive/2026-07-10-epic-101/harvest/issue-102/full/issue-102/g7-review/review.json
  746.4h  by=commander  .agent-work/archive/2026-07-10-epic-101/harvest/issue-103/full/issue-103/spine.json
  380.3h  by=admiral    .agent-work/archive/2026-07-25-epic-226/spine.json
```

**41 of the 43 are stale by more than a day. The oldest is 31 days. Seventeen are inside `.agent-work/archive/`.**

**The defect.** A run that reaches a clean, correct closeout has its work area moved into `.agent-work/archive/<date>-<epic>/`. Nothing in that move touches `engine_session`, so the archived spine keeps saying `status: "active"` forever. So the store cannot distinguish a run in progress, a run that died mid-flight and needs recovery, and a run that completed and was archived. All three read `active`. **The lease field answers "is someone working on this?" with "yes" for every run this repo has ever completed.**

## Prior-Wave Verdicts (pasted)

None — this is wave 1, lane G. Measured ground truth at `600de02`: 15 CLI-fallback clauses across 11 files; 11 live `<engine>` tokens across 7 files; the door's 11 tools cover every engine verb; **no verb binds the door to an existing spine** — `spine_open` only mints (lane A's concurrent mission).

That last fact matters to you directly: **your `spine_done` sits opposite `spine_open` in the lifecycle**, and lane A is concurrently deciding how a door binds to a spine at all. Design so your verb does not depend on a binding model lane A may change, and say in your return where the two designs touch.

## Pre-Rulings

- `decision:pr-opening-question-is-not-yours` — #574 step 5 carries an open question Tommy reserved: does PR-opening live in the engine verb or in a wrapper script? **Float it; do not rule it.** Design so either answer can be adopted without rework, and say which you assumed.
  `@grade: settled/human · leans design`
- `decision:the-refusal-half-already-exists` — `spine_close` (PR #564) already refuses to archive an unreleased run. Build the half that makes that refusal never fire. Do not rebuild the refusal.
  `@grade: settled/issue · leans understand`
- `decision:child-plans-count` — the archive step must release **child plans'** leases too, not just the top-level spine. That is the mechanism half of #552 and the reason 17 stale leases sit inside `archive/`.
  `@grade: settled/issue · leans implement`
- `decision:new-rot-first-old-rot-maybe` — stopping *new* stale leases accruing is the deliverable. Sweeping the **41 existing** ones is a separate question: if your change reaches them, say so; if not, say so. Either is fine; silence is not.
  `@grade: settled/admiral · leans implement`
- `decision:in-session-observation-is-not-evidence` — hooks and the engine execute from the **main checkout** regardless of worktree; `CLAUDE_PROJECT_DIR` resolves once at session launch and is inherited unchanged by every subagent (#269). An in-session observation after your edit is **not evidence**. Validate in a **fresh process** with explicit paths.
  `@grade: settled/project · leans verify · docs/agents/ORCHESTRATOR_CONTEXT.md`
- `decision:do-not-test-on-a-live-lease` — the Admiral's own epic lease is active right now, and this session's live Admiral spine is literally one of the 43 counted above. **Never run your verb against a live spine file.** Use copies and fixtures under your own worktree.
  `@grade: settled/admiral · leans verify`
- `decision:no-issue-filing` — **file no issues.** Write triage candidates to `.agent-work/567-g/triage-candidates/<slug>.md` in **your worktree**; the Admiral disposes them at closeout.
  `@grade: settled/human · leans all gates`
- `decision:no-doctrine-promotion` — do not add a rule to `docs/agents/*` on your own authority.
  `@grade: settled/project · leans all gates`
- `decision:net-deletion` — your lane must end with something deleted. The intended deletion is the hand-sequenced closeout ritual in agent-facing instruction: every place that tells an agent to order release/archive/advance by hand should be gone or reduced to the one verb.
  `@grade: settled/human · leans implement`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. If the sequence cannot be made mechanical without the engine taking on responsibilities it should not have, report that with the evidence rather than shipping a verb that half-works.

## Inherited Latitude

**You may decide**: how much of the closeout sequence the verb absorbs; the refusal's shape and wording; fix-now triage inside your lane's scope; test strategy.

**You must float to the Admiral**: the PR-opening open question (#574 step 5); any architecture or structural change; any scope change; a user-visible default; anything fitting none of these classes, with one line on why.

**You do not merge.** Open the PR and return. The Admiral merges sequentially, gated on the check exit code, and may hold you behind lane A.

**You do not file issues.**

## File Ownership

Sole writer this wave of: the lifecycle/archive path (`spine_lifecycle`, `close_work`, and the archive mover) plus its tests.

**Fence — you do NOT own `scripts/checklist_engine.py` or `scripts/mcp_spine_server.py`.** Lane A owns both this wave and is actively rewriting them. Your mission plausibly reaches both. **Expect this fence to bite, and float early rather than editing.** The Admiral will either sequence your merge behind lane A's, hand you a rebase at the boundary, or rule otherwise. Do not coordinate with lane A directly; you have no path to it.

Your working-notes file: `notes-g.md`, in your worktree root. Sole writer.

> Name it `notes-g.md`, **never** `findings-g.md`. The harness `Write` tool refuses any path whose basename contains "findings" — a guard aimed at unprompted report-dumping that cannot tell this file was deliberately assigned. The guard is not ours to change; the word is.

## Workspace

**Absolute worktree path:** `/home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease`
**Branch:** `feat/567-g-closeout-lease` · **Base commit:** `600de020` (main, verified fresh at dispatch)
**Provisioned by:** `git worktree add .worktrees/567-g-closeout-lease -b feat/567-g-closeout-lease main`

First step, before any git operation: **`cd` into that worktree**, then run
```
py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/567-g-closeout-lease
```
It must exit 0. Paste its output into your return report.

> **Order matters.** `--here` asserts about the directory you are *standing in*. Run it before `cd` and you get `fatal: not a git repository` from wherever your session started — which reads as "you are not isolated" when the truth is "you have not arrived yet". Do **not** pass the path to git (`git -C <path>`): that compares the worktree to itself and disarms the check.

NOTE: PR integration defaults to **server-side merge**.

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` is resolved once at session launch and inherited unchanged by every subagent, so you execute the **main checkout's** hook code against the **main checkout's** state even while git stays correctly fenced (#269). Validate anything touching that in a **fresh process** whose `CLAUDE_PROJECT_DIR` genuinely resolves to your worktree.

## Inherited Context

- **This repo is Constellation itself. The engine under edit is not the engine in play.** Your session runs the **installed** copy at `/home/tommy/.claude/skills/constellation-*/scripts/`; your worktree holds the **source** copy. Drive the **installed** copy for your own spine; **break the worktree copy** for red-proofs. This matters more to you than to most lanes: your mission is the shutdown path your own run will use.
- **Python invocation:** `py <script>` works on this host.
- **Encoding:** set `PYTHONIOENCODING=utf-8` in the child env of any subprocess whose output you capture.
- **Lease staleness gates non-owners only.** As the lease owner you are never refused for your own staleness; every mutating verb refreshes it.
- **`durable_root()` points at your worktree, not the main checkout**, because the Admiral's epic lease is active. Write your work area, triage candidates and feedback export inside **your own worktree**. The Admiral harvests before sweeping it.
- **Crew cannot `SendMessage` its dispatching commander** (#413). Relay crew results yourself.

## Pre-empted Steps

- **Context is established.** Both issues are pasted above in full, including #552's measured lease census and #574's contract sketch. Re-check only what you intend to change — though re-running the census against today's tree is a reasonable first move, since the Admiral's own live lease is now in it.
- **The PR-opening question is known to be open and reserved.** You need not discover it.
- **Worktree is provisioned and isolation-gated.** The Admiral ran `verify_worktree_isolation.py` across all four wave-1 worktrees; it reported "4 distinct worktrees", exit 0.

## Data Locations

Read-only in the main checkout:
- `/home/tommy/projects/constellation-skills/.agent-work/epic-567-door/` — the Admiral's contract, log and transition packets. **Its `spine.json` holds a live lease. Do not touch it.**
- `/home/tommy/projects/constellation-skills/.agent-work/archive/` — the 17 stale archived leases. Read them; copy before experimenting.

## Budget

- **Model tier (required):** **Sonnet**. Bounded and well-specified; escalate only by floating to the Admiral with the reason.
- **Compute/time, session-window:** one of four concurrent Commanders on one account usage pool. Prefer bounded foreground work. Write your state note before any detach. Do not arm a per-progress-line monitor.

## Stop Conditions

Stop and return when: your change needs lane A's files; the PR-opening question blocks your design; an architecture change is needed; scope must change; the honest null is reached; budget is crossed — or when you need **context this order does not cover and cannot safely proceed without**. Return-and-query the Admiral; it answers and continues you. Asking up is always sanctioned.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token cap, not a share of your window. The engine refuses only `start` and `reopen`, and only until a refresh-request exists for that gate. The legal sequence is: **attach the refresh-request against the current why-record, then `start`, then do the work.** Do not read a HARD advisory as an instruction to `advance --why` and hand off on turn one.

## Return Shape

Write `RETURN.md` at your worktree root and send your verdict **before** going idle.

`RETURN.md` must carry:

1. **Verdict** — one line: what you delivered, or the honest null.
2. **Isolation evidence** — pasted `verify_worktree_isolation.py --here` output.
3. **The verb's contract** — what `spine_done` (or your name for it) verifies, closes, reaps, archives, and disposes; and the one actionable refusal it returns when a precondition fails.
4. **The PR-opening float** — what you assumed, and why either answer can be adopted without rework.
5. **Lease proof** — a run archived through your path leaving **zero** active leases, child plans included. Show the before and after census. Run it on **copies**, never on a live spine.
6. **Old rot** — whether your change reaches the 41 existing stale leases, stated either way.
7. **What you deleted** — which hand-sequenced closeout instructions are gone.
8. **The lane-A touchpoint** — where your lifecycle design meets lane A's binding design.
9. **Fresh-process validation** — command and output.
10. **Touched paths** — exact file list, so the Admiral can sequence merges.
11. **PR** — number and URL. Do not merge it.
12. **Triage candidates** — paths under `.agent-work/567-g/triage-candidates/`. Not filed.
13. **Workflow feedback** — brief is fine.

When you open the PR, write the body to a temp file and use `gh pr create -F <file>` — never a heredoc `--body`.
