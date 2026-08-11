# Continuation handoff — E1: pick up from f3, your first two gates are done

**Work id:** `epic-559/e1-fail-up` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/e1-fail-up` (branch `epic-559/e1-fail-up`)
**Your spine:** `.agent-work/epic-559/e1-fail-up/IMPLEMENTER_PLAN.json` — `f1` and `f2` are already complete. Start at `f3`.

## What happened, so you do not repeat it

A previous instance did good work here and then ended its run with one sentence:

> *"I'll pause here and wait for the background dispatch to finish — it runs a real `claude -p`
> headless session so it may take a few minutes."*

**Nothing resumes a headless crew.** That sentence was the end of the run. Its work — `--parent`
binding and the `blocked` outcome — is intact and uncommitted in this worktree.

The rule against this exists and is well written, in `constellation-admiral`: *treat the thought
"I'll wait for it to finish" as the cue to start polling, never to stop and yield.* It appears
nowhere in the crew skills. Putting it there is part of your `f4`.

**You do not need to dispatch anything.** The Admiral ran the reachability probes itself.

## `f3` — record the measured finding

The gate's check has been amended through the engine: it now wants
`.agent-work/epic-559/e1-fail-up/REACH_FINDING.md` containing the marker `PROBE-EVIDENCE` and the
verbatim refusal string, plus the `Parent` tests from `f1` still passing.

Write that file. Here is the evidence, and it must go in verbatim rather than paraphrased.

A one-gate probe crew was dispatched with `--parent "Admiral session 717403d3 (constellation-skills,
epic-418-followon)"`. It recorded its own `ListAgents` output:

```
Peer sessions (6):
  mcp cs [5912e0]  ·  interactive  ·  busy  ·  started 18h ago
  tommy-f0 [9dfa0e]  ·  interactive  ·  idle  ·  started 2d ago
  new guy! [d86672]  ·  bg  ·  shell  ·  started 2d ago
  d1-stale-pins-9f [2639cc]  ·  interactive  ·  started 15m ago
  c1-spine-lint-b6 [06a20a]  ·  interactive  ·  started 15m ago
  f1brainz-cb [53e3b0]  ·  interactive  ·  shell  ·  started 1d ago
```

and its attempt:

```
{"success":false,"message":"No agent named 'Admiral session 717403d3' is reachable.\nUse ListAgents to see everyone you can message."}
```

**What that establishes.** A headless crew *is* on the peer graph — the two sibling crews running at
that moment appear in its list. But a crew cannot reach a parent named by a descriptive string; the
name must be the exact addressable one. The dispatching session does not get its own addressable
name for free, and `SendMessage` from the Admiral to `mcp cs` was itself refused, which is what you
would expect if that entry is the Admiral. A second probe was dispatched to test that name directly;
it reported its spine done and **wrote no artifact at all**, so it produced no evidence. Say that
plainly — an inconclusive probe recorded as inconclusive is worth more than a tidy claim.

**The ruling you are implementing:** the durable path is the mechanism, and messaging is at best a
latency improvement on top. A crew that cannot satisfy a check blocks; the blocked gate lives in its
spine and the parent is recorded in the registry; a polling parent finds both. That works whether or
not a message ever lands, and it survives the crew dying mid-question, which a message does not.

Keep `SendMessage` in the grant — it costs nothing and works when a real addressable name is passed
— but make the code and its comments say plainly that the parent record is the channel and the
message is an optimisation. **Do not make anything depend on a message arriving.**

## `f4` — say it in the skills, and fix a third copy

Three short additions, in `skills/implementer/SKILL.md` and `skills/reviewer/SKILL.md`:

1. A crew that cannot satisfy a check **blocks and names its parent**. It never waives its own gate
   and never invents an authority. (A reviewer did invent one this week, writing
   `--authority human`, because nothing told it who "up" was.)
2. **Never end your turn waiting on something you started.** Poll it inside your turn. This is what
   killed the previous instance of this very run.

Then the third copy. `skills/workbench/references/checklist-engine.md`, around line 34, still tells
a dispatched Implementer or Reviewer to drive its own plan through the CLI instead of the door.
Commit `6fc83013` deleted that exact instruction from both crew `SKILL.md` files and left this file
untouched, so it survives in a third place that every role loads. A cold reviewer confirmed it with
the best evidence available: **its own `SPINE_FILE` was bound to its own survey and it drove its
whole review through the door — the exact case that paragraph says cannot work.** Correct it.

Keep all of this short. The launcher does the mechanical half; the text only has to stop a crew
improvising.

## Scope

**In:** `scripts/run_crew.py`, `skills/implementer/SKILL.md`, `skills/reviewer/SKILL.md`,
`skills/workbench/references/checklist-engine.md`, `tests/`, `map/INDEX.md`.
**Out:** `checklist_engine.py`, `mcp_spine_server.py`, `settings.json`, `docs/agents/*`, every spine
template. No merge or push to `main`.

## Before you finish

Commit — gate `f5.c2` refuses on a dirty tree, and the previous instance left everything unstaged.
Rebuild `map/INDEX.md`. Write `IMPLEMENTER_RESULT.md` from the implementer skill's template with its
**Workflow Feedback** section.

If you add a module-scope import, check `SCRIPT_RUNTIME_COMPANIONS` in
`scripts/install_constellation.py` — `run_crew.py` ships in installed bundles, and an import of a
sibling that is not bundled with it broke every installed dispatch earlier this week.
