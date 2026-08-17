# Launch Order: `cmdr-567-b — #432 ExternalBackend refuses a spineless success`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Commanders start cold. Everything you need is pasted here.

## Mission

Make it **impossible for a dispatched role that drove no spine at all to return a clean success**, and delete the mtime-only verification path that currently lets it.

This serves epic #567's intent: the door is the interface, and an interface nothing verifies is prose. Your lane is independent of the other three — you are not blocked and you block nobody.

### What happened (pasted in full — #432)

Epic #418 wave 0 dispatched `impl-425-file-defects` (workstream G, issue #425) as an implementer-with-plan. Its launch order and its dispatch prompt both instructed it, explicitly, to invoke `constellation-implementer` and **drive its spine through the checklist engine to terminal**.

It produced a correct, verified deliverable — five issues filed (#427–#431), four comments posted, all confirmed to exist at the source via `gh issue view`. And it drove **no spine at all**.

Evidence, in the commander's worktree:
```
$ git status --porcelain
?? RETURN.md
```

That is the entire output. `RETURN.md` is the only artifact the run produced. There is no `.agent-work/<work-id>/spine.json` for that run — every `.agent-work/*` directory present was a pre-existing tracked one inherited from `main` @ `990712f`. No lease was claimed, no `current` was ever asked, no gate was advanced, no journal exists.

**Why it matters.** `constellation-implementer` and `constellation-commander-delegated` both open with the same hard rule, in bold: *"Work the engine never saw did not happen."* A run that solves the task directly "has **failed this dispatch** no matter how correct the answer." By that rule this dispatch failed. But its output is good — which is precisely the problem. **A compliance rule that a correct-looking result can walk straight past is a check that cannot fail.** The only thing that caught it was the Admiral going and looking at `git status` in the worktree, by hand, because it happened to be suspicious. Nothing in the pipeline would have.

**What is not claimed.** Not that the deliverable was wrong — it was verified correct at source. Not that this is the implementer skill's fault specifically — the same gap applies to every role carrying the engine-drive rule.

### The residual named in #567

> #432 residual: the Agent-tool (ExternalBackend) dispatch path verifies on **result-artifact mtime alone**; a crew that never drives a spine reads as clean success.

That mtime-only path is what your lane deletes.

## Prior-Wave Verdicts (pasted)

None — this is wave 1, lane B. The measured ground truth this wave launches from, at `600de02`:

| Claim | Measured 2026-08-16 |
|---|---|
| CLI-fallback clauses | **15**, across 11 files |
| live `<engine>` tokens | **11**, across 7 files |
| engine verb coverage by door tools | **closed** — 11 tools cover every verb |
| a role agent reaching its **own** spine through the door | **impossible** — no verb binds an existing spine; `spine_open` only mints |

That last row is lane A's mission, running concurrently. It does not block you, but note it: **a crew that could not reach its own spine had a real reason not to drive one.** If your check would have refused an agent that was structurally unable to comply, say so — that interaction is a finding, and the Admiral needs it at the wave checkpoint.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- `decision:the-check-must-be-able-to-fail` — assert against the **behaviour**, never against text describing the behaviour. Any guard that loops must **assert what it looped over** and state the count: an under-inclusive enumeration presented as complete reports clean *because* it never reached the interesting items. Prove your check red before you prove it green.
  `@grade: settled/doctrine · leans implement, verify · global-orchestrator.md §a-check-that-cannot-fail`
- `decision:test-the-shipped-path` — a red-proof against a fixture is not a red-proof. Demonstrate the refusal against the path a real dispatch actually takes. A check that runs against your own working copy is not a check on the world.
  `@grade: settled/doctrine · leans verify`
- `decision:refuse-or-report-is-yours-to-settle` — #559's text notes that "Agent-tool dispatch has no engine chokepoint to refuse at." If that holds, a hard refusal may be impossible and the honest deliverable is a **detection that cannot be missed** rather than a refusal. Establish which is true from the code before designing, and say which you built.
  `@grade: guess/admiral · leans understand · settle: read the ExternalBackend dispatch path and report whether it can refuse or only report`
- `decision:in-session-observation-is-not-evidence` — hooks and the engine execute from the **main checkout** regardless of worktree; `CLAUDE_PROJECT_DIR` resolves once at session launch and is inherited unchanged by every subagent (#269). An in-session observation after your edit is **not evidence**. Validate in a **fresh process** with explicit paths.
  `@grade: settled/project · leans verify · docs/agents/ORCHESTRATOR_CONTEXT.md`
- `decision:no-issue-filing` — **file no issues.** Tracking has been ballooning and the human ruled filing held for the whole run. Write triage candidates to `.agent-work/567-b/triage-candidates/<slug>.md` in **your worktree**; the Admiral disposes them at closeout.
  `@grade: settled/human · leans all gates`
- `decision:no-doctrine-promotion` — do not add a rule to `docs/agents/*`. Record the observation and say so; the human decides.
  `@grade: settled/project · leans all gates`
- `decision:net-deletion` — your lane must end with something deleted; the mtime-only path is the intended deletion. If it turns out not to be deletable, that is a finding to float.
  `@grade: settled/human · leans implement`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win. If the ExternalBackend path genuinely cannot refuse, and detection is the most that is available, that is a result — not a shortfall to dress up.

## Inherited Latitude

**You may decide**: where the check sits on the ExternalBackend path; its evidence shape; fix-now triage of bounded defects inside your lane's scope; test strategy.

**You must float to the Admiral**: any architecture or structural change; any scope change; a user-visible default; anything fitting none of these classes, with one line on why.

**You do not merge.** Open the PR and return. The Admiral merges, sequentially, gated on the check exit code.

**You do not file issues.**

## File Ownership

Sole writer this wave of: the ExternalBackend dispatch path and its tests.

**Fence — you do NOT own `scripts/checklist_engine.py` or `scripts/mcp_spine_server.py`.** Lane A owns both this wave. If your change needs either, **stop and float to the Admiral** rather than editing them; the Admiral will either sequence you behind lane A or rule otherwise. Two lanes editing one file this wave is a collision the Admiral must adjudicate, not a thing to work around.

Your working-notes file: `notes-b.md`, in your worktree root. Sole writer.

> Name it `notes-b.md`, **never** `findings-b.md`. The harness `Write` tool refuses any path whose basename contains "findings" — a guard aimed at unprompted report-dumping that cannot tell this file was deliberately assigned. The guard is not ours to change; the word is.

## Workspace

**Absolute worktree path:** `/home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend`
**Branch:** `feat/567-b-external-backend` · **Base commit:** `600de020` (main, verified fresh at dispatch)
**Provisioned by:** `git worktree add .worktrees/567-b-external-backend -b feat/567-b-external-backend main`

First step, before any git operation: **`cd` into that worktree**, then run
```
py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend
```
It must exit 0. Paste its output into your return report.

> **Order matters.** `--here` asserts about the directory you are *standing in*. Run it before `cd` and you get `fatal: not a git repository` from wherever your session started — which reads as "you are not isolated" when the truth is "you have not arrived yet". Do **not** resolve this by passing the path to git (`git -C <path>`): that compares the worktree to itself and disarms the check entirely.

NOTE: PR integration defaults to **server-side merge**.

**Isolation is git-only — hook code is not fenced by it.** `CLAUDE_PROJECT_DIR` is resolved once at session launch and inherited unchanged by every subagent, so you execute the **main checkout's** hook code against the **main checkout's** state even while git stays correctly fenced (#269). Validate anything touching that in a **fresh process** whose `CLAUDE_PROJECT_DIR` genuinely resolves to your worktree — never a fixture that hand-injects the value you are trying to prove the harness delivers.

## Inherited Context

- **This repo is Constellation itself. The engine under edit is not the engine in play.** Your session runs the **installed** copy at `/home/tommy/.claude/skills/constellation-*/scripts/`. Your worktree holds the **source** copy. Drive the **installed** copy for your own spine; **break the worktree copy** for red-proofs.
- **Python invocation:** `py <script>` works on this host.
- **Encoding:** set `PYTHONIOENCODING=utf-8` in the child env of any subprocess whose output you capture.
- **Lease staleness gates non-owners only.** Every mutating verb refreshes your own lease.
- **`durable_root()` points at your worktree, not the main checkout**, because the Admiral's epic lease is active. Write your work area, triage candidates and feedback export inside **your own worktree**. The Admiral harvests before sweeping it.
- **Crew cannot `SendMessage` its dispatching commander** (#413). Relay crew results yourself.

## Pre-empted Steps

- **Context is established.** The #432 evidence above is pasted in full from the issue; you do not need to re-derive it. Re-check only what you intend to change.
- **Worktree is provisioned and isolation-gated.** The Admiral ran `verify_worktree_isolation.py` across all four wave-1 worktrees; it reported "4 distinct worktrees", exit 0.

## Data Locations

Read-only in the main checkout: `/home/tommy/projects/constellation-skills/.agent-work/epic-567-door/` (the Admiral's contract, log and transition packets).

## Budget

- **Model tier (required):** **Sonnet**. This lane is bounded and well-specified; escalate only by floating to the Admiral with the reason.
- **Compute/time, session-window:** one of four concurrent Commanders on one account usage pool. Prefer bounded foreground work. Write your state note before any detach. Do not arm a per-progress-line monitor.

## Stop Conditions

Stop and return when: your change would need `checklist_engine.py` or `mcp_spine_server.py` (lane A's files); an architecture change is needed; scope must change; the honest null is reached; budget is crossed; evidence is impossible — or when you need **context this order does not cover and cannot safely proceed without**. Return-and-query the Admiral; it answers and continues you. Asking up is always sanctioned.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token cap, not a share of your window. The engine refuses only `start` and `reopen`, and only until a refresh-request exists for that gate. The legal sequence is: **attach the refresh-request against the current why-record, then `start`, then do the work.** Do not read a HARD advisory as an instruction to `advance --why` and hand off on turn one — that produces an infinite handoff chain with no deliverable.

## Return Shape

Write `RETURN.md` at your worktree root and send your verdict **before** going idle.

`RETURN.md` must carry:

1. **Verdict** — one line: what you delivered, or the honest null.
2. **Isolation evidence** — pasted `verify_worktree_isolation.py --here` output.
3. **Refuse or report** — which the ExternalBackend path can actually do, with the code that decides it, and which you built.
4. **The red-proof** — the check failing on a spineless dispatch, against the shipped path, with the count of what it enumerated. Then the green.
5. **Fresh-process validation** — command and output.
6. **What you deleted** — the mtime-only path, or why it survived.
7. **Touched paths** — exact file list, so the Admiral can sequence merges.
8. **The lane-A interaction** — whether your check would refuse an agent that was structurally unable to reach its own spine.
9. **PR** — number and URL. Do not merge it.
10. **Triage candidates** — paths under `.agent-work/567-b/triage-candidates/`. Not filed.
11. **Workflow feedback** — brief is fine.

When you open the PR, write the body to a temp file and use `gh pr create -F <file>` — never a heredoc `--body`.
