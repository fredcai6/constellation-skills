# Handoff — plan-alternative candidate `b-most-testable`

**Work id:** `epic-559/c2-generate-the-spine` · **Dispatched by:** commander (delegated, Admiral
`admiral-epic-418-followon`) · **Role:** plan-alternative candidate author, one of three.

## Your assigned constraint: **most-testable**

Maximize what the generator can FALSIFY AT GENERATION TIME. Push it hard: a wrong spec should fail loudly in the generator, not quietly at a gate three hours later. Ask of every field in your spec: what wrong value could an author write here, and what in the generator catches it before it reaches JSON? Consider actually executing or probing what the spec names at generation time -- does the script exist, does argparse accept those flags, does the selector collect anything. Where the constraint costs you something real -- generation-time cost, a dependency on the environment being right, machinery a reviewer must also verify -- say so rather than hiding it.

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

Write `.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/plan-alt-b-most-testable-result.md` **before
you end your turn**; that write is the delivery. Then return a short message naming your constraint,
your one-sentence recommendation, and that path.
