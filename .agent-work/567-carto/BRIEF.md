# Cartographer brief — architecture reconcile for epic #567 (closeout)

You are the architecture reconcile for **epic #567, "the door is the interface"**, dispatched at
its closeout by the Admiral. You start cold; everything you need is here.

**Your spine:** `/home/tommy/projects/constellation-skills/.agent-work/567-carto/spine.json`, already
provisioned. Your door is bound to it — your process was launched with `SPINE_FILE` set, so call
`spine_lease` with `action=claim, claimed_by=cartographer, worktree=.` and drive every gate through
the MCP door. **Do not reach for the CLI**: this epic just removed it as an agent-facing path, and
if you find yourself needing it, that is a finding worth more than the workaround — record it.

## What the epic changed

`origin/main` at `148ae62e`. Nine lanes across two waves. The net change, measured:

| Area | Change |
|---|---|
| `scripts/mcp_spine_server.py` | `spine_bind` added (wave 1); door refusals now captured into the episode store (+255 lines, lane E) |
| `scripts/checklist_engine.py` | atomic `save()`, lease-release-on-archive, `finish_work` (wave 1) |
| `tests/test_cli_retirement_guard.py` | **new, 718 lines** — the #559 regrowth guard |
| `tests/test_mcp_adoption.py` | **472 lines changed** — the mandate that required CLI text is inverted |
| `specs/{implementer,reviewer}.spine.toml` | +41 / +44 — door vocabulary, where there was none |
| `skills/workbench/**` | teaching half 289 → 124 lines; skill no longer teaches the engine |
| `skills/**`, `.agent-work/templates/**` | every `CLI fallback` clause and agent-facing `<engine>` token swept |
| suite | 3191 → **3374** tests |

**The structural claim worth checking:** the corpus now has *one* agent-facing path to the engine
(the MCP door) where it had two, and a test that fails if the second returns.

## What is already measured — do not spend your budget rediscovering it

- `map/INDEX.md` **is fully built**: 30,743 bytes, 165 module directories.
- `map/ids.jsonl` **is 0 bytes**, and rebuilding does not change that. `scripts/code_map/render.py:728`
  writes it from **minted anchor ids**, and this repo has none.
- `docs/architecture/` **does not exist** as a packet map (only an untracked, empty
  `generated/map.json`).
- Consequence, reported independently by two lanes this wave and confirmed by the Admiral: every
  run in this repo orients **DEGRADED**, permanently, and `verify-frame` therefore passes only
  frames that cite nothing.

## Your task, bounded

1. **Reconcile the epic's net change against current map truth** — whatever map truth exists.
2. **State plainly what a reconcile can and cannot mean here**, given there are no minted anchors.
   If the honest answer is that there is nothing to reconcile *against*, say so with the evidence.
   **An evidenced honest null is a complete, successful deliverable** and is preferred to ceremony.
3. **Report what minting anchors for this repo would actually take** — a size and shape, not a plan
   and not the work itself. That is a recommendation for the human, not a task you execute.

## Hard constraints

- **Do not mint the repo's anchors or build the packet map.** That is a large piece of work, it is
  outside this closeout, and it is the human's call to commission. Recommending it is your job;
  starting it is not.
- **Do not regenerate or hand-edit `map/INDEX.md`.** It is Admiral-owned this epic (#544) and was
  regenerated on merged main; it is currently fresh and passing.
- **Do not change code.** You own map truth, not source.
- **File no issue.** Stage anything for later under `.agent-work/567-carto/triage-candidates/`.
  The epic's standing ruling holds: tracking has been ballooning, so candidates get paired onto
  open issues or recorded as episodes at closeout, and nothing new is minted.
- **Do not promote anything into `docs/agents/*`.** That is the human's call.

## Budget

**Sonnet**, by human ruling — and if you dispatch any crew, pass `--model sonnet` explicitly.
`run_crew.py` otherwise inherits this host's Opus default, which cost this epic 15 unintended Opus
crew sessions. Given the size of this task, consider whether it needs a crew at all.

## Return

Write your result to `.agent-work/567-carto/RECONCILE.md`, and drive your spine to a terminal state.
Include: the reconcile verdict, what you established about map truth (with commands and output), the
anchor-minting recommendation with its size, and any triage candidates you staged.
