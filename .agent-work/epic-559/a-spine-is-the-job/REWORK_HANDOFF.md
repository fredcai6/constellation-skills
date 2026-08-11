# Rework handoff — A: the design is right; the contract and the denial are not

**Work id:** `epic-559/a-spine-is-the-job` · **Role:** implementer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job` (branch `epic-559/a-spine-is-the-job`, one local commit `6fc83013`)
**Your spine:** `.agent-work/epic-559/a-spine-is-the-job/REWORK_PLAN.json` — three gates, every postcondition a real command. The Admiral ran all six substantive checks before dispatching you: **all six are red right now.** Drive the spine gate by gate.

## Start with the good news, because it is load-bearing

A cold reviewer built a scratch two-gate spine and dispatched a real crew at it with `--spine` and
no `--handoff`. **It worked.** The crew drove the spine to done and released the lease. It did that
while reading the *stale installed copy* of the implementer skill — the one that still tells a crew
to build its own plan and use the CLI. The prompt alone beat contrary doctrine sitting in the
agent's own instructions.

That is a stronger result for job 1 than your own report claimed, and it is direct evidence for the
thing this repo is trying to become. Your design is right. Two things it did not follow through are
what block it.

## Blocker 1 — a spine-only crew that fully succeeds is recorded `failed`

The reviewer's probe crew finished cleanly, exit 0, spine at `DONE` — and `run_crew.py` printed
`... -> failed` and recorded `status: "failed"`, `result_present: false`.

You moved a crew's **input** from a document to the spine and left its **completion contract** a
document:

- `main()` still hard-requires `--result`.
- `CrewBackend.verify` decides completed-vs-failed purely on that artifact existing and being fresh.
- Your new spine-only prompt never mentions a result artifact. It ends *"until it reports done"*,
  where the handoff prompt it replaces ends *"The run is only complete when the result artifact the
  handoff names exists."*

So the crew is told its job ends at spine-done while the launcher judges it on a file nobody asked
it to write. Every honest spine-only dispatch reports failed, the duplicate-guard keeps holding the
gate, and `recover_crews.py` sees an unresolved run — a false negative handed to the dispatching
Commander.

**Ruling on which fix:** judge a spine-only dispatch on **its spine reaching a terminal state**, and
make `--result` optional in that case. The smaller patch — thread the result path into the prompt —
would work, but it re-attaches the document this whole wave exists to detach. Take the thesis.

### The test that hid it is the more important half

`SpineOnlyDispatchTests::test_main_cli_spine_only_dispatch_succeeds` passes
`fake_launch(RC, 0, write_result_at=root / result)`. The harness writes the artifact the real crew
is never told to write, so **the test passes for a reason that does not exist in production.** That
is a check that cannot fail, authored inside the wave whose entire subject is checks that cannot
fail. Your gate `w1.c2` is a command that reads the replacement test and refuses if it manufactures
its own precondition.

## Blocker 2 — the waive denial fails open, and hardcodes `python3`

Measured, not argued: an inline `PreToolUse` hook whose command cannot run lets the tool call
through **silently** — no error, no denial. Same for a hook that exits 0 printing non-JSON.

`crew_settings_json` emits the literal `python3 -c '...'`. On a host where `python3` is not the name,
the hook does nothing and a crew **can** waive its own bound spine check. The human's ruling is then
unenforced with no signal at all. The one mechanism whose entire job is to refuse has a hidden
fallback to permitting.

Read `install_constellation.py::build_hook_command` before you fix this. It already states the rule
in the repo's own words — the interpreter comes from a single probe, *"never re-probed here, never
hardcoded"*, because no single interpreter name works on every platform.

**The fix is one line and needs no probe at all.** `run_crew.py` is itself a running Python process,
so the interpreter that launched it is by definition present: emit `shlex.quote(sys.executable)`.

Two more, from the same reviewer item:

- **Add `"shell": "bash"` to the hook entry.** The repo's own `.claude/settings.json` sets it on all
  four of its hook entries. Without it, the single-quoted inline program does not survive a
  non-POSIX parse: `shlex.split(cmd, posix=False)` leaves the quotes on, and `cmd.exe` treats a
  single quote as an ordinary character, so Python receives a program starting with an apostrophe
  and dies — which, given the fail-open above, means the denial silently vanishes.
- **Replace the bare `assert` guarding `WAIVE_DENY_REASON` with `assert_shell_safe_command()`**,
  which already exists and raises. A bare `assert` is stripped under `python -O`. Your reasoning at
  that site was right and your mechanism was wrong.

Cite **#539** in a comment at the site. The human's ruling allows a hardcode short-term only when it
is recorded there; the Admiral has recorded this site on the issue, and the code should point back.

## What the reviewer confirmed and you should not redo

The handoff branch is byte-identical and pinned by a literal-string test — that is the right way to
make a risky change safe. The `PreToolUse`-via-inline-`--settings` mechanism is a genuinely good
answer to "grant a multi-action tool, deny one action," which `--allowedTools` cannot express; it
works, it just has to work everywhere. `--settings` does **merge** rather than replace (4 probes
against the installed binary), so that assumption in your docstring is now measured. The deleted
pins in `tests/test_mcp_adoption.py` are the right deletion — all three consumers of
`TIER2_SKILL_FILES` assert the fact the ruling overturned, nothing unrelated rode along, and the
replacement is proven two-sided by mutation. Every hard no-go held. The suite and the TDD-red
counts reproduce exactly.

## Scope

**In:** `scripts/run_crew.py`, `tests/test_crew_launcher.py`, and `map/INDEX.md` if the entity count
drifts.

**Out — hard no-gos:** `checklist_engine.py`, `mcp_spine_server.py`, `settings.json`,
`docs/agents/*`, and **all spine templates under `skills/*/templates/`** — another crew is editing
those right now, so a change there will collide. No merge or push to `main`.

## One thing to leave alone, deliberately

`tests/test_mcp_adoption.py`'s `DOOR_TOOL_NAMES` (7) and `CLI_ONLY_VERBS` (5 verbs) are stale — N1
already made all 18 verbs reachable through the door. A pin asserting a false fact is worse than no
pin, so this matters, but it is not yours: fixing it means unwinding a large test file mid-wave.
You were right to flag and leave it. Leave it again.

## Standing rulings

- **Scope discipline (human):** *"lets do what we need to do and no more."*
- **The goal is a weaker agent than you.** Prose instruction is a liability.
- **Honest null:** a measured negative is a complete deliverable.
- **Cold review:** the same reviewer standard applies again.
- **Stage by name.** `.agent-work/` is tracked here. Never `git add -A`.

## Deliverable

`.agent-work/epic-559/a-spine-is-the-job/IMPLEMENTER_RESULT.md` (your first-pass result is preserved
as `IMPLEMENTER_RESULT.pass1.md`), from the implementer skill's template, including its **Workflow
Feedback** section. Say whether your new tests would have caught the `failed`-status bug.
