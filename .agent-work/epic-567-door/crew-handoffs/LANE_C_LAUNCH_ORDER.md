# Launch Order: `cmdr-567-c — #442 rail/refusal readability + #595 advisory authority`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Commanders start cold. Everything you need is pasted here.

## Mission

Make the engine's own output work on the agent it is aimed at, and settle which of two competing advisories has authority.

Both issues are about the same surface: **what the engine says to an agent, and whether the agent can act on it.** They ride together because fixing one while leaving the other would leave a Commander still reading contradictory instructions.

### #442 — the rail and the HARD refusal read badly to a cold agent

Two observations from #419's live acceptance, where real dispatched agents met engine output cold:

1. **Agents read the `RAIL:` banner as a possible prompt-injection attempt and said so in their transcripts.**
2. The HARD refusal's remedy string — `Run: attach g1 --type refresh-request --field seam=g1 --field why_ref=<why-id>` — **assumes a Constellation-aware reader.**

**Importance.** The rail is doctrine the engine *pushes* at the agent, and an agent that treats it as hostile input discounts the very instruction the rail exists to deliver. The refusal is the governor's one moment of contact with the agent it is governing: an agent that trips without the corpus loaded gets an instruction it cannot act on.

**Evidence.** Both observed in the archived transcripts of #419's acceptance run.

**Acceptance.** A cold agent with no corpus loaded, shown only the rail and a HARD refusal, can state what it is being asked to do and do it. **Measured on real agents, not judged by an author.**

**Out of scope.** Redesigning the trip mechanic.

### #595 — Stop hook vs context-trip advisory: two mechanisms, different authorities, nothing says which wins

Two engine mechanisms tell a Commander opposite things about ending its turn, and nothing states which is authoritative.

- The **context-trip advisory** (surfaced on `spine_status`) recommends handing off at a gate boundary when context runs low: *"hand off here… advisory — decline with a reason if you're nearly done."*
- The **Stop hook** (`scripts/hooks/spine_rail.py:1197-1214`) refuses a mid-spine turn-end outright: *"SPINE MID-FLIGHT: gate {aid} is still open — you are in the MIDDLE of the spine, not at its end, so ending your turn now abandons an active run. Keep working the gate — do not end your turn to wait."*

Both are right in their own frame. An agent caught between them has no principled basis to choose.

**Two lanes hit it from opposite sides on 2026-08-15.** `launcher-hygiene` followed the advisory, ended its turn at a closed step boundary with `STATE_NOTE.md` rewritten — **and the Stop hook refused it**. Its episode records: *"only the Stop hook is actually enforced; the advisory alone is not license to end the turn."* `stop-hook-door-binding` hit the same fork and floated it explicitly, resolving by continuing rather than stopping. **Both lanes reached the correct answer. Neither had anything to reach it from** — they inferred it from which mechanism happened to bite.

**The cost is asymmetric.** An agent that wrongly follows the advisory gets refused and continues — a near miss. An agent that wrongly *distrusts* the Stop hook and works around it abandons a live run silently, which is the failure class #593 was merged to prevent.

**There is a real question underneath, not only a documentation gap.** If context genuinely runs out mid-gate, refusing the turn-end does not create context. The honest path already exists — `spine_halt block` with the reason recorded, so a parent resumes deliberately — but **neither mechanism currently points at it**. A Commander reading the advisory is being pointed at a handoff the Stop hook will not permit.

The issue's suggested resolution, which you may take, improve, or reject with evidence:
1. State the precedence explicitly where a Commander will read it (`crew-dispatch.md` and/or the advisory's own wording).
2. Have the context advisory point at `spine_halt block` as the sanctioned mid-run exit, rather than at a turn-end handoff the Stop hook refuses.
3. Consider whether the advisory should stay silent while a gate is open, since its recommendation is unactionable in that state.

## Prior-Wave Verdicts (pasted)

None — this is wave 1, lane C. Measured ground truth at `600de02`: 15 CLI-fallback clauses across 11 files; 11 live `<engine>` tokens across 7 files; the door's 11 tools cover every engine verb; **no verb binds the door to an existing spine** (lane A's concurrent mission).

You have already met the rail this run, incidentally: every CLI engine call in this epic printed `RAIL: Work the engine never saw did not happen. Run the step's checks, then attest and advance init.` — including on a bare read-only `current`. Whether a banner that fires on every call, including reads, still carries signal is inside your scope.

## Pre-Rulings

- `decision:measure-on-real-agents` — #442's acceptance is explicit: measured on real agents, not judged by an author. A rewrite you find clearer is not evidence. **If a real cold-agent measurement does not fit your budget, float that to the Admiral before spending the budget on it** — do not silently substitute your own judgement and present it as the measurement.
  `@grade: settled/human · leans verify`
- `decision:stop-hook-is-authoritative` — the correct precedence is already known from the two 2026-08-15 episodes: **the Stop hook is authoritative; the context advisory is advice.** You are not rediscovering this. You are making it stated and actionable, and pointing the advisory at `spine_halt block`.
  `@grade: settled/evidence · leans implement`
- `decision:no-third-mechanism` — adding a third advisory surface is out of bounds. This epic reduces paths. The deliverable is one of the two mechanisms deleted or explicitly subordinated in shipped text.
  `@grade: settled/human · leans implement`
- `decision:trip-mechanic-untouched` — #442 puts redesigning the trip mechanic out of scope. You change what it *says*, not when it fires.
  `@grade: settled/issue · leans implement`
- `decision:in-session-observation-is-not-evidence` — hooks execute from the **main checkout** regardless of worktree; `CLAUDE_PROJECT_DIR` resolves once at session launch and is inherited unchanged by every subagent (#269). **Your mission edits `scripts/hooks/spine_rail.py`, so this bites you hardest of any lane.** You cannot validate your hook change from inside the worktree containing it — that runs the same unchanged main-checkout code the harness would run anyway. Validate in a **fresh process** whose `CLAUDE_PROJECT_DIR` genuinely resolves to your worktree.
  `@grade: settled/project · leans verify · docs/agents/ORCHESTRATOR_CONTEXT.md`
- `decision:no-issue-filing` — **file no issues.** Write triage candidates to `.agent-work/567-c/triage-candidates/<slug>.md` in **your worktree**; the Admiral disposes them at closeout.
  `@grade: settled/human · leans all gates`
- `decision:no-doctrine-promotion` — do not add a rule to `docs/agents/*` on your own authority. Note that #595's resolution names `crew-dispatch.md`, which is **shipped skill doctrine**, not `docs/agents/*` — that one is in scope. Editing shipped doctrine, cite the canonical source `skills/_shared/global-*.md`, **never** `skills/<role>/references/global-*.md`, which `install_constellation.py` regenerates and would silently overwrite.
  `@grade: settled/project · leans implement`
- `decision:net-deletion` — your lane must end with something deleted. The intended deletion is one of the two competing advisories, or the unactionable half of the refusal string.
  `@grade: settled/human · leans implement`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. If a cold agent still cannot act on the refusal after your rewrite, **report that with the transcript** — a measured failure of the rewrite is worth more than a claim that it reads better.

## Inherited Latitude

**You may decide**: the wording of the rail and the refusal; which of the two advisories is subordinated and how; fix-now triage inside your lane's scope; how the cold-agent measurement is run.

**You must float to the Admiral**: any architecture or structural change; any scope change; changing *when* the trip fires; anything fitting none of these classes, with one line on why.

**You do not merge.** Open the PR and return. **Note for the Admiral's sequencing: you touch `scripts/hooks/*`, and concurrent lanes editing hook code can break every live session.** Report your touched paths precisely; the Admiral may hold your merge behind a fresh-process suite or behind another lane.

**You do not file issues.**

## File Ownership

Sole writer this wave of: `scripts/hooks/spine_rail.py` and the rail/refusal/advisory strings wherever they are authored.

**Fence — you do NOT own `scripts/checklist_engine.py` or `scripts/mcp_spine_server.py`.** Lane A owns both this wave. If the rail or advisory text you must change is authored inside either file, **stop and float to the Admiral** rather than editing it. This is a genuine possibility for your mission; expect it and ask early rather than late.

Your working-notes file: `notes-c.md`, in your worktree root. Sole writer.

> Name it `notes-c.md`, **never** `findings-c.md`. The harness `Write` tool refuses any path whose basename contains "findings" — a guard aimed at unprompted report-dumping that cannot tell this file was deliberately assigned. The guard is not ours to change; the word is.

## Workspace

**Absolute worktree path:** `/home/tommy/projects/constellation-skills/.worktrees/567-c-rail-readability`
**Branch:** `feat/567-c-rail-readability` · **Base commit:** `600de020` (main, verified fresh at dispatch)
**Provisioned by:** `git worktree add .worktrees/567-c-rail-readability -b feat/567-c-rail-readability main`

First step, before any git operation: **`cd` into that worktree**, then run
```
py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/567-c-rail-readability
```
It must exit 0. Paste its output into your return report.

> **Order matters.** `--here` asserts about the directory you are *standing in*. Run it before `cd` and you get `fatal: not a git repository` from wherever your session started — which reads as "you are not isolated" when the truth is "you have not arrived yet". Do **not** pass the path to git (`git -C <path>`): that compares the worktree to itself and disarms the check.

NOTE: PR integration defaults to **server-side merge**.

## Inherited Context

- **This repo is Constellation itself. The engine under edit is not the engine in play.** Your session runs the **installed** copy at `/home/tommy/.claude/skills/constellation-*/scripts/`; your worktree holds the **source** copy. Drive the **installed** copy for your own spine; **break the worktree copy** for red-proofs.
- **Python invocation:** `py <script>` works on this host.
- **Encoding:** set `PYTHONIOENCODING=utf-8` in the child env of any subprocess whose output you capture.
- **Lease staleness gates non-owners only.** Every mutating verb refreshes your own lease.
- **`durable_root()` points at your worktree, not the main checkout**, because the Admiral's epic lease is active. Write your work area, triage candidates and feedback export inside **your own worktree**. The Admiral harvests before sweeping it.
- **Crew cannot `SendMessage` its dispatching commander** (#413). Relay crew results yourself.

## Pre-empted Steps

- **Context is established.** Both issues are pasted above in full, including the two 2026-08-15 episode findings. Re-check only what you intend to change.
- **The precedence question is ruled.** The Stop hook is authoritative. You are not deriving that; you are making it stated.
- **Worktree is provisioned and isolation-gated.** The Admiral ran `verify_worktree_isolation.py` across all four wave-1 worktrees; it reported "4 distinct worktrees", exit 0.

## Data Locations

Read-only in the main checkout:
- `/home/tommy/projects/constellation-skills/.agent-work/epic-567-door/` — the Admiral's contract, log and transition packets.
- `/home/tommy/projects/constellation-skills/episodes/` — the two 2026-08-15 episodes cited in #595 (`launcher-hygiene` `-002`, `stop-hook-door-binding` `-002`). Read them; do not treat them as rules to obey.

## Budget

- **Model tier (required):** **Sonnet**. Bounded and well-specified; escalate only by floating to the Admiral with the reason.
- **Compute/time, session-window:** one of four concurrent Commanders on one account usage pool. Prefer bounded foreground work. Write your state note before any detach. Do not arm a per-progress-line monitor.

## Stop Conditions

Stop and return when: the text you must change lives in lane A's files; a cold-agent measurement will not fit the budget; an architecture change is needed; scope must change; the honest null is reached; budget is crossed — or when you need **context this order does not cover and cannot safely proceed without**. Return-and-query the Admiral; it answers and continues you. Asking up is always sanctioned.

**Arriving over the context HARD band is not a stop condition.** The band is an absolute token cap, not a share of your window. The engine refuses only `start` and `reopen`, and only until a refresh-request exists for that gate. The legal sequence is: **attach the refresh-request against the current why-record, then `start`, then do the work.** Do not read a HARD advisory as an instruction to `advance --why` and hand off on turn one.

## Return Shape

Write `RETURN.md` at your worktree root and send your verdict **before** going idle.

`RETURN.md` must carry:

1. **Verdict** — one line: what you delivered, or the honest null.
2. **Isolation evidence** — pasted `verify_worktree_isolation.py --here` output.
3. **The before and after text** — rail banner and HARD refusal, old and new, side by side.
4. **The cold-agent measurement** — how it was run, on what, and the transcript evidence of whether the agent could state and do what it was asked. If you floated instead of measuring, say so and give the Admiral's answer.
5. **The precedence change** — where the Stop hook's authority is now stated, and where the advisory now points at `spine_halt block`.
6. **What you deleted** — which advisory or which unactionable string is gone.
7. **Fresh-process validation** — command and output, since you edited hook code.
8. **Touched paths** — exact file list. Call out `scripts/hooks/*` explicitly; the Admiral sequences merges on it.
9. **PR** — number and URL. Do not merge it.
10. **Triage candidates** — paths under `.agent-work/567-c/triage-candidates/`. Not filed.
11. **Workflow feedback** — brief is fine. You are the lane best placed to say whether the rail read as hostile to *you*; that observation is wanted.

When you open the PR, write the body to a temp file and use `gh pr create -F <file>` — never a heredoc `--body`.
