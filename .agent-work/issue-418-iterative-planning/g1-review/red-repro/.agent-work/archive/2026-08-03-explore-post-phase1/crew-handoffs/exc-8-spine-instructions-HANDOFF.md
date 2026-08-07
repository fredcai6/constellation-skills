# Excursion handoff: exc-8-spine-instructions (PROTOTYPE_HANDOFF)

Full brief: `### EXCURSION_BRIEF exc-8-spine-instructions` in `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/IDEAS_BOARD.md` — read it first. Load the **constellation-prototyper** skill (Skill tool) and drive its workflow with that handoff.

## Question
Can step-specific instructions be moved out of a role's always-loaded skill prose into the spine template the engine pushes per gate — demonstrated live on at least one real role step — without losing the behavior, and what does the seam look like?

Background (why this is believed, not yet shown):
- The human's driver: "move any step specific skills/instructions into the spine so we can reduce the overhead on general agent instructions"; prose stays light except (a) ensuring spine use and (b) project focus.
- #310's B2 gate evaluation observed the corpus is "already kernel-shaped" (SKILL.md as trigger/pointer, references/ as doctrine, templates/ as interface) and that #307 showed per-task delivery through the spine template moved behavior that always-loaded delivery could not. That is inference from one case; this prototype is the live test.
- The engine already pushes each gate's full imperative through `current` (engine-output-is-the-state-channel doctrine). The question is whether skill prose currently duplicated or stranded in SKILL.md/references can ride that channel instead.

## Branch
logic

**Why this branch:** mechanism/data-flow behavior — instruction delivery through the engine — no UI, no measurement apparatus.

## Host-project conventions
- **Runtime / language:** Python 3.12
- **Task runner:** run tests as `python -m pytest` (NOT `py -m pytest` — #313)
- **Routing:** n/a
- **Other conventions:** skills under `skills/<role>/` (SKILL.md + references/ + templates/); spine templates are `skills/<role>/templates/*_SPINE.template.json`; engine is `scripts/checklist_engine.py`; the engine's `current` output is the canonical channel agents read.

## Location
worktree

**Driver:** agent-driven → throwaway worktree. Create it yourself off main; dispose per prototyper doctrine when done (or keep with a named reason).

## Stop conditions
- "Answered" requires all three of:
  1. **A live tracer:** pick ONE real role step (Commander is the richest candidate) where step-specific instruction text lives in SKILL.md or references/ but is only needed at one gate. Relocate it into the spine template for that gate in your worktree. Drive the engine and show `current` delivers the relocated text at that gate. Then spawn ONE cold subagent (Agent tool, model sonnet or lower, worktree-scoped) given only the spine channel (not the skill prose) and show it acts on the instruction correctly.
  2. **A relocation census for one role:** classify that role's SKILL.md + references/ paragraph-by-paragraph into: step-specific (relocatable to a gate), always-needed (spine-use trigger / role identity / project focus — stays), and reference-on-demand. Report counts and byte/word shares by category. State the method.
  3. **The seam description:** what a general relocation would look like (where relocated text lives in the template, how it stays maintainable, what breaks — e.g. text needed before any engine call, or shared across roles).
- Budget: ~3 variants on the delivery seam if the first fails; report even if inconclusive; scoped nulls — state what was and was NOT tested.
- Exclusions: nothing lands on main; do NOT rewrite the corpus (one tracer + census only); do NOT modify `C:/Users/fredc/.claude/settings.json`; do NOT wire hooks.

## Return format
`PROTOTYPE_RESULT` written to `C:/Programs/constellation-skills/.agent-work/explore-post-phase1/evidence/exc-8-spine-instructions-RESULT.md` (main checkout path, not your worktree): the answer, what was tested and NOT tested, the census table, what it taught, any surviving module, worktree disposition. Final return message: one verdict line + that path.
