# Implementer Handoff

## Gate
`g2` — the acceptance run for issue #440 (epic-418 workstream A2). Worktree
`C:/Programs/constellation-skills-wt/epic418-a2-440`, branch `epic-418/a2-440-binding-cwd`.
**Use absolute paths — your shell's cwd resets between bash calls.**

## Task

Build a re-runnable **two-arm live-fire acceptance harness** under
`C:/Programs/constellation-skills-wt/epic418-a2-440/.agent-work/issue-440-binding-cwd/acceptance/`
and run it, to answer one question with evidence:

> **Does a HARD governor trip fire from a per-agent gauge reading produced by an agent that was
> dispatched into a worktree?**

Not "does the path resolve correctly" — a **fired trip**, observed, on a live run.

This is the Commander's done-condition and the whole point of the issue. A measured negative,
reported with the same rigor as a win, is a complete and valuable deliverable. A fabricated or
hand-assisted green is the one unacceptable outcome.

## Background you need

Three pieces of machinery, in a chain:

1. `scripts/hooks/spine_rail.py` — a `PostToolUse` hook. When it sees a `checklist_engine.py claim`
   command it records `binding[<agent key>][<absolute spine path>] = {...}` in
   `<project dir>/.agent-work/.spine-rail-binding.json`. The agent key is the bare `session_id` for
   a top-level agent and `session_id#agent_id` for a dispatched one (#419).
2. `scripts/hooks/gauge_writer_hook.py` — a `PostToolUse` hook on **every** tool call. It looks up
   that binding, parses the acting agent's own transcript for the latest `usage` block, and writes
   `gauge.json` **next to the bound spine**. On a dispatched agent's record it also writes a fifth
   field, `identity_resolution_ms`; a top-level agent's record has only four.
3. `scripts/checklist_engine.py` — at each gate boundary reads `gauge.json` beside the spine. When
   `fill_fraction >= hard`, `advance` is **REFUSED** until a `refresh-request` is attached.

**The defect (#440):** the binding resolved a relative `--file` against the payload's `cwd`, which
for a worktree-dispatched agent is the **main checkout** (`CLAUDE_PROJECT_DIR` is fixed at session
launch, #269). So the reading landed in a phantom `.agent-work/<work_id>/` in the main checkout while
the engine read the worktree's copy. Measured 2026-08-05: **60 of 64 live binding entries**.

**The fix (g1 + g1b, committed/staged in this worktree):** the resolution now walks ordered candidate
roots and takes the first that validates as a checklist, refusing to guess when two guessed roots
disagree.

## The trap that governs this entire gate — read it twice

**Hook code is not fenced by worktree isolation.** `CLAUDE_PROJECT_DIR` resolves once at session
launch and is inherited unchanged by every subagent, so an agent dispatched into this worktree still
executes the **main checkout's** hook code against the **main checkout's** state. You therefore
**cannot** validate this change from inside the worktree that contains it — that is the same process
the harness would use to run the *unchanged* code, and it will show you a green that means nothing.

So: **the very mechanism under repair is the mechanism that makes your own validation lie.** Your
harness must be built so that its green cannot be produced by anything except the fix.

## The construction

A **disposable sandbox pair**, entirely under a temp directory. Nothing in it touches the real repo.

- **sandbox main** — a scratch `git init` repo standing in for a main checkout.
- **sandbox worktree** — a real `git worktree add` of that repo.

Then, per arm:

- **an arm directory holding a COMPLETE `scripts/` tree.** Treatment = this worktree's current
  `scripts/`; control = `git archive cbd9aee | tar -x` (the base commit, pre-fix). It must be the
  whole tree, not two files: `gauge_writer_hook.py` imports `spine_rail.py` as a **filesystem
  sibling** and, if the sibling set is incomplete, writes **nothing, silently** — which would look
  exactly like the bug reproducing.
- **a settings file** wiring both hooks as `PostToolUse` commands **by absolute path** into that
  arm's tree, with `spine_rail.py` **ahead of** `gauge_writer_hook.py`.
- **a headless `claude -p`** launched with cwd **and** `CLAUDE_PROJECT_DIR` set to the **sandbox
  main** — this is what reproduces the defect's own precondition. The absolute hook path is what
  makes the arm's code run even though `CLAUDE_PROJECT_DIR` names the sandbox main.
- that session **dispatches a subagent into the sandbox worktree**, which:
  1. `claim`s a spine that lives in the sandbox worktree, using a **relative** `--file` (this is the
     real Constellation shape and the only shape the defect appears in);
  2. inflates its own context past its model's **absolute** HARD cap;
  3. runs at least one further tool call, so the gauge is written from a post-inflation transcript
     line;
  4. attempts `advance` on its own spine.

**The only difference between the two arms is which arm directory the absolute hook path points at.**
Everything else — the sandbox, the prompt, the model, the spine, the sequence — is identical.

## Expected outcomes (this is the hypothesis, not the answer — report what you observe)

- **Treatment:** the binding names the **sandbox worktree's** spine; `gauge.json` lands beside it;
  `advance` is **REFUSED** with the HARD-band message; exit code non-zero.
- **Control:** the binding names the **sandbox main's** path; `gauge.json` lands in a phantom
  `.agent-work/<work_id>/` inside the sandbox main; the engine sees nothing beside the real spine and
  `advance` **succeeds**.

## The control must be a POSITIVE control — this is the sharpest requirement here

A control arm that is merely *quiet* proves nothing. A missing sibling import, an uncalibrated model,
a subagent that never received an `agent_id`, a stale reading, a permission denial — every one of
these produces the same "no trip", and every one would masquerade as "the bug reproduced".

**So the control arm must be shown to have WORKED AND MISSED:** it must produce a real `gauge.json`
with `fill_fraction >= hard` **at the wrong path** (the phantom directory in the sandbox main). If the
control produces no gauge anywhere, the run is **inconclusive, not a pass** — say so and diagnose.

## Attribute the reading to the dispatched agent three independent ways

`gauge.json` itself carries no agent id, so "whose reading is this?" must be answered from
converging evidence, not one signal:

1. **The binding key is the composite `session_id#agent_id` shape.** Only a dispatched agent
   produces that; a top-level agent keys bare.
2. **`identity_resolution_ms` is present** in the record. The writer emits that fifth field **only**
   on a dispatched agent's record (#419), so a 5-field record is positive proof of subagent origin.
3. **Run the parent session and the dispatched subagent on different models**, so `gauge.json`'s own
   `model` field names which of the two produced it.

Capture all three. If they disagree, that disagreement is the finding.

## Before you run an arm — preflight assertions

- The acting model string is a key in `scripts/gauge_reader.py`'s `_PROFILES`. An uncalibrated model
  yields **no reading at all**, which would read as a false negative. Profiles today:
  `claude-opus-5`, `claude-opus-4-8`, `claude-sonnet-5`, `claude-fable-5` (1M window, hard 150000
  tokens) and `claude-haiku-4-5-20251001` (200K window, hard 140000 tokens). **Read the file; do not
  trust this list.** Note the cap is in **absolute tokens**, so the subagent has to genuinely reach
  ~140–150K of context. State your inflation method and its token budget.
- `claude --version` responds and a trivial headless write succeeds (already probed once for this
  run: a `claude -p ... --permission-mode acceptEdits` created its file, exit 0).

**Preflight facts already established for you — do not spend time rediscovering these:**

- `claude` is at `C:\Users\fredc\.local\bin\claude.exe`, version **2.1.223**.
- `claude --settings <file-or-json>` exists and is how you point an arm at its own hooks. Also
  available: `--model`, `--permission-mode`, `--add-dir`, `--append-system-prompt`.
- The user-level `~/.claude/settings.json` wires **no hooks** (only env, permissions, and a default
  model), and the real repo's `.claude/settings.json` will not apply because your cwd is the sandbox.
  So the arm's `--settings` file is the only hook source — that is what makes the arms clean.
- **The user's default model is `fable`.** An unspecified model is therefore a doctrine violation,
  not just a vague dispatch. Pass `--model` explicitly on every launch.
- `.agent-work/.spine-rail-binding.json` is written under **`resolve_project_dir()`**, i.e.
  `CLAUDE_PROJECT_DIR` — so with that set to the sandbox main, the store lands in the sandbox and the
  real one is never touched. Verify that after your first arm.
- The real store is currently **1 key holding 8 entries**, which is itself why the live governor is
  silent; do not be confused if you glance at it. Leave it alone.
- The two arms' `scripts/` trees differ **only** in `scripts/hooks/spine_rail.py` (and its tests) —
  prove it with a recursive diff and put the diff in the evidence.

## Close criteria

- `run_two_arm` (or however you name the entry point) is **re-runnable** and self-contained: it
  builds the sandbox, runs both arms, writes evidence, and cleans up after itself.
- Evidence on disk under `.agent-work/issue-440-binding-cwd/acceptance/evidence/`, per arm:
  the binding store dump, **both** candidate gauge paths (present/absent + contents), the full
  `advance` output and its **real** exit code, `observed_at` against wall clock, the acting model,
  and the composite-key / `identity_resolution_ms` / model-attribution facts.
- The arm diff (script diff + recursive `scripts/` tree diff).
- **`verify_evidence.py`** at
  `.agent-work/issue-440-binding-cwd/acceptance/verify_evidence.py` — a script the Commander runs at
  the integrate gate that reads the captured evidence and exits **0** only if it is complete and
  self-consistent (both arms present, control positive, attribution facts captured, arms differing
  only in the hook path). It checks the **evidence**, it does not re-run the arms. It must exit
  non-zero on missing or contradictory evidence — write it so it can fail, and show it failing on a
  deliberately truncated copy of the evidence.
- A plain-English verdict: did the trip fire from a worktree-dispatched agent's own reading, yes or no.

## Allowed scope

Everything under
`C:/Programs/constellation-skills-wt/epic418-a2-440/.agent-work/issue-440-binding-cwd/acceptance/`,
plus temp directories. **Nothing else.**

## Specific exclusions — hard

- **Do not modify** `scripts/hooks/spine_rail.py`, `scripts/hooks/gauge_writer_hook.py`,
  `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, or any test. If the acceptance run shows
  the fix is wrong, **that is a finding to report**, not a thing to patch. Report it and stop.
- **Never** hand-inject the value being proved. The harness must not place the worktree root into any
  payload field, fixture, or environment variable that the hook then reads back. The hook must
  **derive** it. A test that cannot fail is worse than no test, and this epic has already filed three
  issues in that family (#432, #446, and a finding inside #419's own run).
- **Never** touch the live main checkout `C:/Programs/constellation-skills`: not its
  `.agent-work/.spine-rail-binding.json`, not its `.claude/settings.json` or `.claude/settings.local.json`,
  not any real worktree. A live Admiral session is running against those files right now. Everything
  goes in temp directories.
- Do not commit.

## Constraints

- Use `python`, **never** `py` — `py` on this box resolves to a runtime with no pytest and produces
  fake failures. (It does work as a plain interpreter, which is why the repo's own hook entries use
  it; that is fine and not yours to change.)
- Windows 11. A Bash tool (git-bash) and a PowerShell tool are both available, each with its own
  syntax. Paths with spaces need quoting.
- **Gate on real exit codes.** `cmd | tail -5; echo $?` captures `tail`'s exit code, not `cmd`'s.
  Redirect to a file, then echo the exit code. This has already cost this epic one wrong call.
- A headless `claude -p` needs `--permission-mode acceptEdits` (or better) or its tool actions are
  silently denied and it produces nothing.
- **Cap every dispatched model at Opus or lower and name the model explicitly on every dispatch.
  No Fable at any tier** — note the user's global settings default to `fable`, so an unspecified
  model is a violation. Pass `--model` explicitly.
- A `.get()` on a guessed field name returns `None`, and `None` reads as a clean negative. Read the
  schemas in `scripts/gauge_reader.py` and `docs/GAUGE_WRITER_HOOK.md` rather than guessing field names.
- Headless runs are slow. Budget your time, run the arms sequentially, and keep logs.

## Map anchors (inbound)

No architecture map exists (`DEGRADED-NO-MAP`). Hash-pinned substitute: **`docs/GAUGE_WRITER_HOOK.md`** —
read it, especially "The payload fields this hook reads", "Skip-on-uncertainty, enumerated" (it
enumerates every reason the writer legitimately writes nothing — your diagnostic checklist when an arm
is quiet), and "Known limits of the binding store itself (#419)" (its first bullet is this defect).

- **Structural:** `scripts/hooks/spine_rail.py`, `scripts/hooks/gauge_writer_hook.py` — wired by
  absolute path, the only per-arm variable; `scripts/checklist_engine.py` `_trip_hard_gate` — the
  observer, identical in both arms; `scripts/gauge_reader.py` `_PROFILES` — the HARD cap.
- **Constraints:** hook code is not fenced by worktree isolation; #269 unchanged.
- **Decision anchor:** `existence-verified-resolution` — ordered rungs, first validating candidate
  wins, refuse to guess on disagreement.
  `@grade: guess · leans g1,g1b · settle: THIS GATE`
- **Confidence flag:** the mechanism under repair is the mechanism that makes an in-worktree green
  lie. The one-path-difference construction is what makes this green real — protect it.

## Deliverable path check

- **Local-only** — everything under `.agent-work/issue-440-binding-cwd/acceptance/`. `.agent-work/`
  is **tracked** in this repo, so these files WILL be committed by the Commander; keep them small,
  keep secrets and absolute temp paths out of anything gratuitous, and do not commit multi-MB logs.
  Run `git check-ignore` on your deliverables and report the exit codes.

## Required evidence

**Load-bearing — prove rigorously:**

1. The treatment arm's REFUSED `advance`, with the engine's own message and the real exit code.
2. The control arm's **positive** miss: a real `gauge.json`, `fill_fraction >= hard`, at the phantom
   path in the sandbox main, with `advance` succeeding.
3. The three attribution facts (composite key, `identity_resolution_ms`, model).
4. The arm diff proving the two arms differ only in `scripts/hooks/spine_rail.py`.

**Confirmatory — spot-check:** `verify_evidence.py` exiting 0 on the real evidence and non-zero on a
truncated copy; the preflight assertions; the cleanup.

## Verification commands

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440
python .agent-work/issue-440-binding-cwd/acceptance/verify_evidence.py; echo "EXIT=$?"
```

## Suggested model tier
**Stronger (Opus).** Orchestration-heavy, many ways to produce a green that means nothing.
**No Fable at any tier.**

## Authority

Decided, do not re-open: the sandbox-pair construction; the absolute-hook-path-is-the-only-difference
rule; the positive-control requirement; three-way attribution. Yours to decide: the inflation method
and token budget, the model pair, the evidence file layout, how `verify_evidence.py` is structured.

**Not yours:** changing any hook, engine or test to make an arm pass. If the fix looks wrong, stop
and report.

## Stop conditions

Stop and return if: scope must be exceeded; an exclusion must be touched; the headless permission
model blocks the run; the required evidence cannot be obtained; or a decision outside this authority
is needed. **An honest measured negative is a complete deliverable** — report "this specific check
failed", never "this approach is impossible".

## Return format

Write `IMPLEMENTER_RESULT` to
`C:/Programs/constellation-skills-wt/epic418-a2-440/.agent-work/issue-440-binding-cwd/crew/g2-implement/IMPLEMENTER_RESULT.md`
**before you go idle**, and deliver it as your final message: the verdict in plain English first,
then completed slice, files changed, evidence produced with real exit codes, assumptions, stop
conditions hit, out-of-scope observations, and workflow feedback.
