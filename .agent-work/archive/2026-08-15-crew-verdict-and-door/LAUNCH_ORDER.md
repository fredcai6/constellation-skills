# Launch Order: `crew-verdict-and-door` — stop the launcher inverting the archive verdict

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

## Mission

Two defects in the crew dispatch path, both filed as triage candidates during epic 568. They are
**ranked**, and the first is the real deliverable.

Source documents, untracked, in the **primary checkout** (your worktree does not contain them):

- `/home/tommy/projects/constellation-skills/.agent-work/epic-568/triage-candidates/launcher-reports-failed-for-successful-archive.md`
- `/home/tommy/projects/constellation-skills/.agent-work/epic-568/triage-candidates/crew-dispatch-must-bind-the-spine-door.md`

Read both before planning.

## Task 1 — the inverted archive verdict (the real defect)

**Every successful archive is reported `failed`.** Not sometimes — structurally, always.

`run_crew.py` judges completion on the `--result` artifact. The `archive` gate in
`checklist_engine.py` **relocates the entire work area** — the result document included — into
`.agent-work/archive/<date>-<work-id>/`. So the launcher checks a path that the gate it just dispatched
has emptied.

The signal is not noisy, it is **inverted**: only a *failed* archive can leave the result where the
launcher expects it.

I located the mechanism for you; verify it rather than trusting it. `scripts/run_crew.py:997`:

```python
if result is not None:
    have_result = result_exists(result, root)
    fresh = result_fresh(result, root, since)
    done = fresh
else:
    have_result = False
    fresh = False
    done = spine is not None and spine_terminal(spine, root)
```

`spine_terminal` is consulted **only when `result is None`**. An Admiral who passes both `--spine` and
`--result` — the natural thing to do — can never have a terminal spine rescue a relocated artifact.

**The file already contains the shape of the fix.** Immediately below, `blocked_gate` is checked
**first**, ahead of both the artifact and spine-terminal checks, whenever a spine is bound at all — and
its docstring explains exactly why, in words that apply here almost verbatim:

> judging it against a file it was never told about produced a false `failed` for a crew that did
> everything asked of it.

Follow that precedent. The triage document's smallest honest version: **if the result artifact is
missing but the bound spine is terminal, report success and say which check decided it.** The registry
entry should record *which* check decided, so a later reader is not left guessing.

**Rejected alternative, do not propose it:** telling every Admiral to pass `--result` paths that survive
archival. That pushes a harness bug into every launch order and will be forgotten.

### Open questions from the triage — answer them if cheap, say so if not

- Does any gate **other than** `archive` relocate artifacts the launcher watches?
- Should a `failed` verdict ever be recordable while the bound spine is terminal? That combination is
  self-contradictory on its face and may warrant a refusal to record rather than a quiet mismatch.

## Task 2 — the unbound spine door (secondary, and **bounded**)

A crew whose MCP door is not bound resolves to `.mcp.json`'s demo default. A `claim` through a
demo-bound door **mutates the wrong spine while reporting success**. This happened during epic 568.

The `cli` backend already fixes this: `--spine` binds `SPINE_FILE` and an assignment-keyed
`SPINE_SESSION` into the spawned child. The gap is the **`external` backend**, which spawns no process
and therefore binds nothing — and which correctly refuses `--spine` today for that reason.

**Binding out-of-band is impossible by construction.** Do not attempt it. The deliverable here is to
make the hazard **impossible to miss**: the external-backend crew prompt and registry entry should state
plainly that the door is unbound and that the crew must verify its door before any mutating verb.

**If Task 2 turns out to need a design decision rather than a hardening, stop and report it.** Task 1
standing alone is a complete, shippable lane. Do not let Task 2 hold Task 1 hostage.

## Pre-Rulings — settled, do not relitigate

1. **`decision:task-1-is-the-lane` — settled.** Ship Task 1 even if Task 2 is deferred.
2. **`decision:no-admiral-side-workarounds` — settled.** The fix lives in the launcher, not in doctrine
   handed to every future Admiral.
3. **`decision:clear-caches-before-measuring` — settled.** A stale `.pyc` fabricated a convincing
   phantom failure last epic and cost four falsifications to attribute.

## A note on the ground moving under you

**The Admiral is dispatching live crews with `scripts/run_crew.py` while you edit it.** This is safe —
those dispatches run the **primary checkout's** copy, not yours — but it means two things:

- Do not "fix" anything by editing the primary checkout. Work only in your worktree.
- Your change lands by PR and merge, not by taking effect mid-flight. Do not expect to observe your own
  fix change a running dispatch.

## File Ownership

**Yours:** `scripts/run_crew.py`, its tests, your work area.

**NOT yours:**
- `scripts/checklist_engine.py` — the `archive` gate's relocation behavior is **correct**. Relocating the
  work area is what archiving *is*. Do not change the gate to satisfy the launcher; that is the tail
  wagging the dog, and another lane is editing this file right now.
- `scripts/hooks/spine_rail.py` — live target of in-flight work on #441.
- `.mcp.json` — shared config, and changing it would alter every other lane's door mid-run.
- Anything under `.worktrees/epic-568-441/` or `.worktrees/tc1-worktree-identity/`.

## The MCP door — verify before you mutate anything

This dispatch launches through the `cli` backend with `--spine`, which binds `SPINE_FILE` and
`SPINE_SESSION` into your process before your MCP servers start.

**`spine_status` must describe `crew-verdict-and-door`. If it resolves to any other spine — especially a
`f-424` demo spine — stop and report. Do not proceed and do not fall back.**

There is a pleasing recursion here: verifying your own door is precisely the discipline Task 2 exists to
make mandatory. **Record what you observe** — your own dispatch is a live specimen of the mechanism you
are hardening, and what it felt like to check is worth more than a paraphrase of the triage doc.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/crew-verdict-and-door`,
branch `fix/crew-verdict-and-door`, based on `main` at `453f8492`. Yours alone.
Work area `.agent-work/crew-verdict-and-door/` **inside your worktree**.

## Evidence required

- **Red before, green after**, over behavior: a dispatch given **both** `--spine` and `--result`, whose
  result artifact is absent and whose bound spine is terminal, must be recorded `completed` after your
  change and `failed` before it. Drive it through the real judging function — this bug is in how two
  real behaviors compose, and a mocked test would not have caught it.
- A test that a genuinely failed crew — spine **not** terminal, no result — is still `failed`. The fix
  must not turn the verdict into a rubber stamp.
- Confirmation that `blocked` still wins ahead of everything, unchanged.
- Full Linux suite, cache-clean. Clear first:
  `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
  **Baseline at `453f8492` is 3002 passed, 7 skipped, 0 failed, 1130 subtests passed** — measured
  cache-clean immediately before this dispatch.
- Regenerate the map: `python -m scripts.code_map build --root .` and commit if it moves.

## Budget

One implementation. Task 2 is capped at a hardening; if it grows, report instead of continuing.

## Stop Conditions

- `spine_status` does not resolve to `crew-verdict-and-door`.
- Green would require changing the `archive` gate's relocation behavior, or anything in the not-yours list.
- Task 2 needs a design decision rather than a hardening.
- The fix cannot be made without making a genuinely failed crew read as completed.

## Return Shape

Report: what `spine_status` resolved to, **named explicitly**; what you changed; the red/green proof for
the both-flags case; how you proved a real failure still reads `failed`; whether Task 2 shipped or was
deferred and why; answers to the two open questions or an explicit "not established"; cache-clean suite
counts before and after; whether the map moved; and anything floated.

**You may push your branch and open a PR** — your `archive` gate's postconditions require it.
**You are fenced from merging.** The Admiral merges, because the merge gate requires an independent
approval and a lane cannot approve itself. Say plainly in your report that the PR is open and unmerged.

## One thing you should find funny, and then handle correctly

Your own `archive` gate will relocate your own result document, and the launcher that dispatched you —
running the **unfixed** primary-checkout copy — will therefore probably report your run as `failed`.

**That verdict is the bug you were sent to fix, not a judgment on your work.** Do not react to it, do not
retry, and do not move the result back to satisfy it. Note it in your report as one more observation of
the defect. The Admiral judges this lane on spine state.
