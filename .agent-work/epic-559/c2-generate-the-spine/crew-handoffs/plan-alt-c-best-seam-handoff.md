# Handoff — plan-alternative candidate `c-best-seam`

**Work id:** `epic-559/c2-generate-the-spine` · **Dispatched by:** commander (delegated, Admiral
`admiral-epic-418-followon`) · **Role:** plan-alternative candidate author, one of three.

## Your assigned constraint: **best-seam-placement**

Put the boundary where the AUTHOR and the TESTS actually want it, even if that costs more machinery. Push it hard: start from what an author sits down to write and what a test needs to reach, and derive the seam from those two, not from what is convenient to implement. Ask where the pure function ends and the I/O begins, and whether a test can exercise the interesting half without a filesystem. Where the constraint costs you something real -- more files, more indirection, a heavier thing to learn -- say so rather than pretending the extra structure is free.

## Everything else

Read `.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/CANDIDATE_BRIEF.md` **in full** and
follow it exactly. It carries the problem, the required reading, what is fixed and not yours to
redesign, the two non-optional properties, the settling question, the test mode, the required
document structure, and the stop conditions.

## Allowed scope

Read anything in the worktree. **Write exactly one file: your result path below.** Change no code,
no template, no spine, no `.mcp.json`, no settings. Run no `git` write operation. Do not run
`scripts/install_constellation.py`.

## Required evidence in your document

- The pasted output of `python scripts/validate_spine.py --sweep --root .`, run by you.
- A complete worked implementer role spec in your format.
- The emitted `constraints`/`directives` JSON for one gate, plus what `current` would render for it.

## Success criteria

Your result file exists at the path below and contains all eight numbered sections the common brief
requires, including the self-scoring, the settling question, and the strongest argument against your
own candidate.

## Stop conditions

Per the common brief. Additionally: if you find the mission already done -- a generator already in
the tree -- stop and say so with the path.

## Return format

Write `.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/plan-alt-c-best-seam-result.md` **before
you end your turn**; that write is the delivery. Then return a short message naming your constraint,
your one-sentence recommendation, and that path.
