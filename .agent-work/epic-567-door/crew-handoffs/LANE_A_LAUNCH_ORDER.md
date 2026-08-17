# Launch Order: `cmdr-567-a — #559 per-dispatch spine identity`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Commanders start cold. Everything you need is pasted here.

## Mission

Make **a role agent reach its own spine through the MCP door**, and make the engine's `save()` safe against concurrent writers.

This is the anchor of epic #567 ("the door is the interface — finish the MCP migration"). The epic's whole deliverable — deleting 15 CLI-fallback clauses and 11 `<engine>` tokens, sunsetting the workbench teaching half, and landing a regrowth guard — is blocked behind you. **You cannot delete a fallback that is currently the only path.** Wave 2 does not launch until this lane returns.

Three issues ride in this lane:

**#559 (anchor) — the door does not reach a dispatched subagent's own spine.** A Task-tool subagent inherits its dispatcher's MCP scope, and the door binds `SPINE_FILE`/`SPINE_SESSION` as module-level constants at launch. So the tools are callable from inside a dispatched Implementer but stay pointed at the **Commander's** `spine.json`, never the Implementer's own `IMPLEMENTER_PLAN.json`. Today's answer is "those crew use the CLI." With no CLI, in-session dispatched crew have **no path to their own plan file**.

The issue's own recommendation, which you may take, improve, or reject with evidence:

> **Containment instead of pinning, reusing a seam already built.** `mcp_spine_server.py:164` `_identity_violation` already confines `spine_advance.from_child` to paths under `SPINE.parent`. Generalize that: let a call name its own spine file, and enforce that it lies within the bound root. Isolation stops being "one file" and becomes "one tree," which is the property that was actually wanted, and it is already implemented once for `from_child`.

The trade is recorded in `.agent-work/archive/2026-08-09-epic-418-followon/...IDENTITY_TRADE.md`: env-binding buys isolation, per-call paths buy per-call identity, and **the composition is what fails**.

**The bind-own-spine gap — measured live this run, and NOT in the issue text.** The defect is not confined to dispatched subagents. It stopped the Admiral of this very epic, in its own process, at step one:

```
mcp__spine__spine_status  ->
REFUSED: no spine is bound to this door, so there is nothing for this tool to act on.
Call `spine_open` to mint a spine and bind this process to it, or relaunch this door
with SPINE_FILE set to an existing spine file.
```

No `SPINE_*` variables were in the environment. `spine_open` only **mints** a new worktree, branch and compiled spine — there is **no verb that binds the door to an existing spine file**. The Admiral drove its own `init` step on the documented CLI fallback and logged that as an `ADMIRAL ERROR`. So the general statement of the defect is: **any role reaching its own spine has no door path to it**, whether it is a dispatched crew member or the top-tier orchestrator. Solve the general case.

**#613 — `save()` is not atomic, and the parent heartbeat is a second concurrent writer.** The parent's heartbeat writes a spine the child already writes, and `checklist_engine.py`'s `save()` is not atomic, so the two can lose each other's updates. This is the same seam your identity work touches, which is why it rides here rather than separately. Fix the atomicity half.

## Prior-Wave Verdicts (pasted)

None — this is wave 1, lane A. The measured ground truth this wave launches from, at `600de02`:

| Claim | Measured 2026-08-16 |
|---|---|
| CLI-fallback clauses | **15**, across 11 files |
| live `<engine>` tokens | **11**, across 7 files (the epic body says 9; it is stale) |
| door vocabulary in `specs/*.spine.toml` | **zero** — only `implementer` and `reviewer` specs exist |
| engine verb coverage by door tools | **closed** — 11 tools cover every verb |
| a role agent reaching its **own** spine | **impossible** — see above |

Commands that produced it, for your own re-check:
```
grep -rn "CLI fallback" skills/ specs/ --include="*.md" --include="*.json" --include="*.toml" | wc -l
grep -rn "<engine>" skills/ specs/ scripts/ docs/ | wc -l
```

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- `decision:solve-the-general-case` — the mission is any role reaching its own spine, not the Task-tool crew case alone. The Admiral's own REFUSED `spine_status` is the grounding.
  `@grade: settled/admiral · leans design`
- `decision:design-it-twice` — this is a load-bearing interface, so generate **N≥2 candidates in parallel, each under one named distinct constraint**, and compare them on depth / locality / seam placement / testability. Converge to **one opinionated recommendation or a named hybrid — never a menu**.
  `@grade: settled/doctrine · leans design · global-orchestrator.md §design-it-twice`
- `decision:convergence-is-human-only` — you generate and compare; **the human picks**. Return your comparison and your recommendation. Do **not** treat your own recommendation as the ratified choice, and do not let implementation outrun it: if you implement your recommendation before the human sees it, say so plainly and make the change trivially revertible.
  `@grade: settled/human · leans design, implement`
- `decision:self-hosting-engine-edit` — you are rewriting `checklist_engine.py` and `mcp_spine_server.py`, **the very engine driving the Admiral's live spine and your own**. Implement and review inside your worktree. **Before you open the PR**, prove: (1) a read-only `current` on the live spine exits 0 under the new engine, and (2) a **mutating** verb (`advance`) run against a **copy** of a spine — never a live spine file — refuses or succeeds sanely rather than crashing. Paste both into your return.
  `@grade: settled/doctrine · leans implement · fleet-doctrine.md §engine-platform-quirks`
- `decision:in-session-observation-is-not-evidence` — hooks and the engine execute from the **main checkout** regardless of worktree; `CLAUDE_PROJECT_DIR` resolves once at session launch and is inherited unchanged by every subagent (#269). An in-session observation of engine or hook behaviour after your edit is **not evidence** — strike it from any gate that would accept it. Validate in a **fresh process** with explicit paths.
  `@grade: settled/project · leans implement, verify · docs/agents/ORCHESTRATOR_CONTEXT.md`
- `decision:no-issue-filing` — **file no issues.** Tracking has been ballooning and the human ruled filing held for the whole run. Write triage candidates to `.agent-work/567-a/triage-candidates/<slug>.md` in **your worktree**; the Admiral harvests and disposes them at closeout by pairing onto an open issue or recording an episode.
  `@grade: settled/human · leans all gates`
- `decision:no-doctrine-promotion` — do not add a rule to `docs/agents/*`. Recording an observation is not authority to promote it. Record it and say so; the human decides.
  `@grade: settled/project · leans all gates`
- `decision:net-deletion` — this epic reduces paths; it does not add mechanism. Your lane must **end with something deleted**. If your converged design cannot delete anything, that is a finding worth floating, not a detail to omit.
  `@grade: settled/human · leans design, implement`
- `decision:isolation-not-fencing` — the door's current isolation property is "one file per process." Whatever you build must state, explicitly, what isolation property replaces it and what an agent can now reach that it could not before. A design that silently widens reach is a regression even if every test passes.
  `@grade: guess/admiral · leans design · settle: name the property in the design doc and have the reviewer attack it`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win.

**Specifically**: if per-dispatch spine identity cannot be had without adding more mechanism than the doctrine sweep removes, **say so with the evidence and stop**. That finding is worth more than a mechanism that makes the epic net-positive, because wave 2's premise depends on it. Do not build something you would not defend just to have built something.

## Inherited Latitude

From `.agent-work/epic-567-door/LATITUDE_CONTRACT.md`:

**You may decide** (log it in your return): implementation mechanism inside your converged design; fix-now triage of bounded defects inside your lane's scope; test strategy and evidence shape; how much of #613's atomicity half is in scope.

**You must float to the Admiral**: any architecture or structural change beyond the converged design; any scope change (adding or dropping an issue); anything that would add a user-visible default; anything that fits none of these classes, with one line on why it fit none.

**You do not merge.** Open the PR and return. The Admiral merges, sequentially, gated on the check exit code, and may sequence your merge behind another lane's if both touch `scripts/hooks/*`.

**You do not file issues.** See `decision:no-issue-filing`.

## File Ownership

Sole writer this wave of: `scripts/mcp_spine_server.py`, `scripts/checklist_engine.py`.

**Fence — lane G also names `scripts/checklist_engine.py` as an anchor.** You own it. If lane G's change needs to touch it, the Admiral sequences that behind your merge. Do not coordinate with lane G directly; you have no path to it.

Your working-notes file: `notes-a.md`, in your worktree root. You are its sole writer.

> Name it `notes-a.md`, **never** `findings-a.md`. The harness `Write` tool refuses any path whose basename contains "findings" — a guard aimed at unprompted report-dumping, which cannot tell that this file was deliberately assigned. Three agents hit it in one epic and each worked around it with a shell heredoc. The guard is not ours to change; the word is.

## Workspace

**Absolute worktree path:** `/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`
**Branch:** `feat/567-a-spine-identity` · **Base commit:** `600de020` (main, verified fresh at dispatch)
**Provisioned by:** `git worktree add .worktrees/567-a-spine-identity -b feat/567-a-spine-identity main`

First step, before any git operation: **`cd` into that worktree**, then run
```
py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity
```
It must exit 0. Paste its output into your return report.

> **Order matters, and the failure is misleading if you get it wrong.** `--here` asserts about the directory you are *standing in*: it runs `git rev-parse --show-toplevel` in your ambient cwd and compares that to the path you pass. Run it before `cd` and you get `fatal: not a git repository` from wherever your session happened to start — which reads as "you are not isolated" when the truth is "you have not arrived yet". Do **not** resolve this by passing the path to git (`git -C <path>`): that compares the worktree to itself, is true for any valid worktree, and disarms the check entirely.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a local merge that would diverge your worktree from main).

**Isolation is git-only — hook code is not fenced by it.** `verify_worktree_isolation.py` proves your git worktree is real and distinct; it says nothing about which project's hook scripts you are actually running. `CLAUDE_PROJECT_DIR` is resolved once, at session launch, and inherited unchanged by every subagent it spawns — so you still execute the **main checkout's** hook code against the **main checkout's** state, even while every git operation stays correctly fenced (#269). Your mission touches exactly this. Validate with a **fresh process** whose `CLAUDE_PROJECT_DIR` genuinely resolves to your worktree (a headless `claude -p` launched with that value, or a plain subprocess with the env var set for the non-agent paths) — never a fixture that hand-injects the value you are trying to prove the harness delivers.

## Inherited Context

- **This repo is Constellation itself. The engine under edit is not the engine in play.** Your session runs the **installed** copy at `/home/tommy/.claude/skills/constellation-*/scripts/`. Your worktree holds the **source** copy. Drive the **installed** copy for your own spine; **break the worktree copy** for red-proofs. Both #433 crews had to derive this unaided — you should not have to.
- **Python invocation:** `py <script>` works on this host. Engine CLI: `py /home/tommy/.claude/skills/constellation-commander-delegated/scripts/checklist_engine.py --file <plan> <verb>`.
- **Encoding:** the engine owns utf-8 stdio internally, but set `PYTHONIOENCODING=utf-8` in the child env of any *other* subprocess whose output you capture.
- **Lease staleness gates non-owners only.** As the lease owner you are never refused for your own staleness; every mutating verb refreshes it, so a long crew step or idle gap self-heals on your next verb.
- **`durable_root()` points at your worktree, not the main checkout**, because the Admiral's epic lease is active and the main checkout is fenced read-only for that reason. Write your work area, triage candidates and feedback export inside **your own worktree**. The Admiral harvests before sweeping it.
- **Crew cannot `SendMessage` its dispatching commander** (#413 — 4/4 dispatches failed). Relay crew results yourself; do not architect around a channel that does not exist.
- **`py` is a silent no-op under the PowerShell tool** (#373) — irrelevant on this Linux host, but do not copy a PowerShell recipe from an archived run.

## Pre-empted Steps

- **Context is established.** The measured ground truth above is the Admiral's, taken at `600de02`. Cite this order rather than re-deriving it; re-check only what you intend to change.
- **Worktree is provisioned and isolation-gated.** The Admiral ran `verify_worktree_isolation.py` across all four wave-1 worktrees; it reported "4 distinct worktrees", exit 0. Your `--here` check is your own confirmation, not a repeat of that gate.
- **Scope is ratified.** #559 + the bind-own-spine gap + #613's atomicity half is the human-confirmed lane content. You need not re-litigate whether #613 belongs here.

## Data Locations

Everything you need is tracked and present in your worktree. Untracked inputs in the main checkout that you may **read** but must not write:
- `/home/tommy/projects/constellation-skills/.agent-work/epic-567-door/` — the Admiral's work area (contract, log, transition packets). Read-only to you.
- `/home/tommy/projects/constellation-skills/.agent-work/archive/2026-08-09-epic-418-followon/` — the `IDENTITY_TRADE.md` record cited above.

## Budget

- **Model tier (required):** **Opus**. This lane is design-heavy and load-bearing; it is the one lane in wave 1 that warrants the tier.
- **Compute/time, session-window:** you are one of four concurrent Commanders drawing on one account usage pool. Prefer bounded foreground work over long detached compute. Write your state note before any detach. Do not arm a per-progress-line monitor — it is the dominant Commander kill.

## Stop Conditions

Stop and return when: your converged design would require an architecture change beyond this lane; the scope needs to change; the honest null is reached; your budget is crossed; the evidence you need is impossible to obtain — or when you need **context this launch order does not cover and cannot safely proceed without**. Return-and-query the Admiral; it answers and continues you. Asking up is always sanctioned.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token cap, not a share of your window, so a Commander that has loaded its skill, references, templates and this order can be over it on its first turn having done no work. The engine refuses only the verbs that BEGIN work at a gate — `start` and `reopen` — and only until a refresh-request exists for that gate. The legal sequence is: **attach the refresh-request against the current why-record, then `start`, then do the work.** Attaching first sends the guard down its release path; starting first is what gets refused.

Do not read a HARD advisory, or an inherited `REFRESH REQUESTED:` line, as an instruction to `advance --why` and hand off on turn one. A fresh agent that closes its gate before doing the gate's work produces an infinite handoff chain. Hand off when you have actually spent the context, not when you inherit the reading.

## Return Shape

Write `RETURN.md` at your worktree root and send your verdict **before** going idle — an idle notification with no artifact reads as stalled, not done. The Admiral judges completion from what you produced.

`RETURN.md` must carry:

1. **Verdict** — one line: what you delivered, or the honest null and what it measures.
2. **Isolation evidence** — the pasted output of `verify_worktree_isolation.py --here <your path>`.
3. **The design-it-twice comparison** — each candidate, its one named distinct constraint, and the four-axis comparison (depth / locality / seam placement / testability). Then your **single opinionated recommendation or named hybrid**, and what you would need to be wrong. This is the artifact the human converges on at the checkpoint; write it for a reader who has not seen your run.
4. **The isolation property** — what replaces "one file per process", stated explicitly, and what an agent can now reach that it could not before.
5. **Self-hosting proof** — the pasted output of the read-only `current` on the live spine under your new engine, and of the mutating `advance` against a **copy**.
6. **Fresh-process validation** — how you validated engine/hook behaviour outside your own session, with the command and its output.
7. **What you deleted** — the net-mechanism-negative accounting. If nothing, say so and why.
8. **Touched paths** — the exact file list, so the Admiral can sequence merges (it needs to know whether you touched `scripts/hooks/*`).
9. **PR** — number and URL. Do not merge it.
10. **Triage candidates** — the paths under `.agent-work/567-a/triage-candidates/`. Not filed as issues.
11. **Workflow feedback** — how the run went, positives and negatives, brief is fine.

When you open the PR, write the body to a temp file and use `gh pr create -F <file>` — never a heredoc `--body`.
