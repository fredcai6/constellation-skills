# Launch Order: `commander-315 — issue #315, engine command-check cwd`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Commanders start cold. Paste, don't point.

## Mission

Issue **#315**: *engine: command-kind checks inherit the launcher's cwd (no `cwd=` at all) — five shipped relative checks are silently fragile.*

`scripts/checklist_engine.py:775-799`, `_run_check_command`, calls:

```python
proc = subprocess.run([shell, "-c", command], capture_output=True, text=True)
```

There is **no `cwd=` argument at all**. A `command`-kind postcondition therefore runs wherever the launching process happened to stand, not where the spine lives. The filed consequence is fail-open: a decoy file in the launcher's directory satisfies a gate that should have refused.

**Deliverable.** A command-kind check runs where the spine lives, and every relative check in the shipped corpus resolves correctly under that change.

**How it serves the epic intent.** Epic 568's thesis is that engine state carries who it belongs to. A postcondition check that resolves against a stranger's working directory is the same defect in the verification layer: the check does not know whose spine it is checking. It is wave 1 — ahead of all other engine-core work — because **every gate verified before this lands was verified under a check that cannot fail.** Fix it late and every earlier fix in this epic inherits unfalsifiable evidence.

## Prior-Wave Verdicts (pasted)

No prior wave. This is wave 1. What follows is the evidence the Admiral measured at the latitude gate, pasted in full so you do not re-derive it:

> **Claim:** The command-kind check fail-open filed as #315 is real and present in current main.
> **Expected:** `subprocess.run` receives a `cwd=` argument naming the spine's root.
> **Observed:** `scripts/checklist_engine.py:787` calls `subprocess.run([shell, "-c", command], capture_output=True, text=True)` with no `cwd=` argument at all.
> **Source:** direct read of `scripts/checklist_engine.py:775-799` during the latitude interrogation.

> **Claim:** Nothing has partially landed against epic 568's 31 member issues.
> **Expected:** Some members closed or partly fixed by PR #564.
> **Observed:** All 31 member issues are OPEN.
> **Source:** `gh issue view` over all 31 member numbers.

**Advisory, explicitly NOT a measurement.** A crude `grep -c` over `.agent-work/templates/*.json` hits nine files carrying command-ish content: `ADMIRAL_SPINE` (7), `COMMANDER_SPINE` (16), `EXPLORER_SPINE` (11), `INTERROGATION` (2), `REVIEW_SURVEY` (2), `CHARTER` (1), `IMPLEMENTER_PLAN` (1), `EXECUTE_PLAN` (1), `CYCLE` (1). That is a line count, not an enumeration of *relative* checks, and it is pasted only to tell you the issue's "five" looks low. **Do not inherit either number.** Measure it yourself.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- `decision:wave-1-is-315-alone` — #315 is wave 1 alone, ahead of all other engine-core work. No other Commander is running against `checklist_engine.py` while you work.
  `@grade: settled/human · leans mission-scope`
- `decision:engine-core-serialized` — `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py` and `scripts/agent_work_root.py` are edited by one Commander at a time. You hold that lane for this wave; do not assume you may also edit the other two if the fix seems to want it — float first.
  `@grade: settled/human · leans mission-scope`
- `decision:repro-before-and-after` — this issue closes on a live repro that FAILS before the fix and PASSES after. Targeted tests plus the relevant broader suite ride alongside; they do not replace the repro.
  `@grade: settled/human · leans acceptance`
- `decision:enumerate-by-command` — the blast radius is enumerated **by command**, never from memory, and the count is **stated** in your return. This is the authoring-side blast-radius rule from `references/global-everyone.md`: a change to a resolution rule silently breaks every reader of that rule, and you are the only one positioned to know.
  `@grade: settled/inherited · leans acceptance`
- `decision:five-is-unverified` — the issue title's "five shipped relative checks" is an inherited claim, not a measurement. Re-measure it. If the real count is materially larger, that is a finding to report, not a reason to silently widen scope.
  `@grade: guess · leans acceptance · settle: enumerate by command across the shipped template corpus and state the count with what you enumerated over`
- `decision:preserve-no-posix-shell-behavior` — the existing POSIX-shell routing and the visible `returncode 127` / `no-posix-shell` failure path at `checklist_engine.py:775-799` are load-bearing (they exist so a Windows box fails visibly instead of misrouting POSIX text through `cmd.exe`). Preserve both.
  `@grade: settled/inherited · leans implementation`

## Honest-Null Clause

A measured negative on the stated question is a **complete, successful deliverable**. Report it with the same rigor as a win. If the fail-open does not reproduce as filed, or if threading `cwd=` proves to cost more than the defect does, say so with the measurement stated — that closes the issue successfully. Scoped nulls apply: state what you tested **and what you did not**.

## Inherited Latitude

From `.agent-work/epic-568/LATITUDE_CONTRACT.md`.

**You may exercise:** implementation choices inside `checklist_engine.py` for this issue; how `cwd` is resolved and threaded; repairs to relative checks in shipped templates that this change makes wrong; issue filing for anything you find outside scope; fix-now triage for bounded fixes **outside** the three engine-core files.

**You must float to the Admiral:** any architecture or structural change; any scope change (an issue added, dropped, or re-scoped); **any edit to `spine_rail.py` or `agent_work_root.py`** (engine-core outside this wave's issue); any change to production defaults or user-visible behavior; anything that fits no class above — out-of-taxonomy always escalates with one line on why it fit no class.

**The Admiral is reachable.** Float a decision beyond your latitude, or query for context this order does not cover, and it answers and continues you. Asking up is always sanctioned — do not guess past the edge of your latitude to avoid the ask.

## File Ownership

Your working-notes file: **`notes-1.md`**, in your worktree. You are its sole writer this wave.

> Name it `notes-<n>.md`, **never** `findings-<n>.md`. The harness `Write` tool refuses any path whose basename contains "findings" — a guard aimed at unprompted report-dumping, which cannot tell that this file was deliberately assigned. The guard is not ours to change; the word is.

No shared-file fences this wave — you are the only Commander running.

## Workspace

**Provisioned and verified by the Admiral before dispatch.**

- Worktree: `/home/tommy/projects/constellation-skills-wt/epic-568-315`
- Branch: `epic-568/c1-check-cwd`
- Base commit: `3e4e07a3ff83227320571ee011186dcd52fa4226` (main, in sync with origin, clean)
- Create command actually run: `git worktree add /home/tommy/projects/constellation-skills-wt/epic-568-315 -b epic-568/c1-check-cwd 3e4e07a3` → exit 0

`git worktree list` at dispatch time:

```
/home/tommy/projects/constellation-skills                  3e4e07a3 [main]
/home/tommy/projects/constellation-skills-wt/epic-568-315  3e4e07a3 [epic-568/c1-check-cwd]
```

You are the only Commander this wave; the other entry is the Admiral's main checkout, which is **read-only to you**.

First step, before any git operation: run `py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills-wt/epic-568-315` — it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its output into your return report.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a local merge that would diverge your worktree from main).

**Isolation is git-only — hook code is not fenced by it.** `verify_worktree_isolation.py` proves your git worktree is real and distinct; it says nothing about which project's hook scripts you are actually running. `CLAUDE_PROJECT_DIR` is resolved once, at session launch, and inherited unchanged by every subagent it spawns — so a Commander dispatched into an isolated worktree still executes the **main checkout's** hook code against the **main checkout's** state, even while every git operation stays correctly fenced (issue #269).

**This bites your mission directly.** `.claude/settings.json` wires `scripts/hooks/spine_rail.py` on Stop, SessionStart and PostToolUse, and `scripts/hooks/gauge_writer_hook.py` on PostToolUse. Those hooks call the engine. If your change to `_run_check_command` affects anything a hook path reaches, **you cannot validate it from inside the worktree that contains it** — that is the same process the harness uses to run the unchanged code. Validate with a **fresh process** whose `CLAUDE_PROJECT_DIR` genuinely resolves to your worktree (a headless `claude -p` launched with that value, or a plain subprocess with the env var set), never a fixture that hand-injects the value you are trying to prove the harness delivers.

## Inherited Context

- **The `spine` MCP door is not trustworthy in this project right now.** In the Admiral's session it is bound to an unrelated wave-1 scratch demo spine in the `f-424` worktree, because `.mcp.json` defaults `SPINE_FILE` to `examples/mcp-interactive-demo/spine.json` when the variable is unset — which is what happens for any agent a human starts at a terminal. The `spine-epic` door is dead (`MCP error -32000: Connection closed`). **Call `spine_status` and confirm it names the gates you expect before trusting a single door call.** The CLI fallback (`py scripts/checklist_engine.py --file <your spine> <verb> --session-id <your session>`) is always correct and is what the Admiral is using.
- **Backticks in a double-quoted engine `--finding` are shell-substituted** (#551, an open member of this epic): a read-only review once ran a build and rewrote a tracked file that way. Avoid backticks in `--finding` and `--note` strings.
- `command` postconditions run under a POSIX shell — author `grep` / `&&` / pipe checks in POSIX form.
- **Applying an episode delta leaves the tree dirty, and `test_episode_negative_control.py::test_canon_episode_store_untouched` reads that as a failure** (post-418 handoff U4). Staging the episode files clears it. Do not chase it as a defect in your own change.
- **Windows shell hazards:** write PR bodies to a temp file and use `gh pr create -F <file>` — never a heredoc or a PowerShell here-string for `--body`.
- Project doctrine overlay is at `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/CREW_CONTEXT.md`, `docs/agents/GLOSSARY.md`. Read them; this project has a real overlay, so this block is not the doctrine carrier.
- **The repo cannot orient itself** (post-418 handoff W3): `map_orient.py` returns `DEGRADED-UNPARSEABLE`, anchor count 0. `docs/architecture/` is absent. Do not expect map anchors; use file paths.

## Pre-empted Steps

The Admiral has already performed or ratified these — cite this launch order rather than redoing them:

- **The defect is confirmed present in current main.** The read of `checklist_engine.py:775-799` is pasted above. You do not need to re-establish that the `cwd=` argument is missing; you *do* need the before/after repro, which is a different thing.
- **The issue's scope and ordering are frozen.** #315 is wave 1 alone. The scope question was settled with the human at the latitude gate.
- **Main freshness verified** at `3e4e07a3`, clean and in sync with origin.

## Data Locations

Worktrees do not contain untracked inputs. Everything this mission needs is tracked. If you need the Admiral's own artifacts for context, they are in the main checkout at `/home/tommy/projects/constellation-skills/.agent-work/epic-568/` — read-only to you.

## Budget

- **Model tier (required):** **Opus**. This is engine-core work on a 3352-line module whose blast radius spans the shipped template corpus; the ambiguity is in deciding what `cwd` should resolve *to*, which is a judgment call, not a mechanical edit.
- **Compute/time, session-window:** one Commander, serialized lane, no concurrent dispatch. Size crew dispatches to the session pool; if a usage-limit reset is near, finish or checkpoint rather than launching into it.

## Stop Conditions

Stop and return when:

- The fix wants to touch `spine_rail.py` or `agent_work_root.py` — that is engine-core outside this wave's issue and is **surfaced**, not yours.
- The blast-radius enumeration turns up a class of breakage that changes what this issue is (for example, if repairing the templates is larger than the engine fix by an order of magnitude, so wave 1 should split).
- A decision outside inherited latitude is needed.
- Evidence proves impossible to obtain — say so with the scope of what you tried.
- You need **context this launch order does not cover and cannot safely proceed without** — return-and-query the Admiral; it answers and continues you.

## Return Shape

Write your result artifact **before** going idle. An idle notification with no artifact reads as stalled, not done — the Admiral judges completion from what you produced, not from a message that arrives after you have gone quiet.

Your return must carry:

1. **Verdict** — fixed / honest null / blocked, in one line.
2. **The before/after repro** — the exact commands, and the two outputs showing the decoy satisfying the gate before and failing to after.
3. **The blast-radius enumeration** — the command you ran, what you enumerated over, the **stated count**, and the disposition of each hit (repaired, or explicitly ruled correct under the new resolution).
4. **Whether "five" was right.** State the measured number against the filed one.
5. **`verify_worktree_isolation.py --here` output** — the matched worktree path, as evidence you worked in isolation.
6. **Suite evidence** — the targeted tests and the relevant broader suite, with the command and the result.
7. **Map impact** — expect none given the degraded map; say so if that is the case.
8. **Triage candidates** — anything found outside scope.
9. **Workflow feedback** — what the process cost you. This becomes closeout episode material, so write what you *observed*, not a rule for a future agent to follow.

PR posted against `main`; the Admiral merges on a green check exit code plus an independent reviewer APPROVE.
