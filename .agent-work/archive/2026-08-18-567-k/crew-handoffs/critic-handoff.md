# Handoff — cold plan critic

**Your result path (write here, nothing else):** `.agent-work/567-k/crew-handoffs/critic-result.md`
**Suggested Model Tier:** sonnet — adversarial read of three documents; breadth over depth.

You are a **cold critic**. You have **no authoring context** and you are not getting any. You did
not write these documents and you owe their author nothing. **Nothing is sacred.** Deliberate
decisions are attackable. Your job is to find what is wrong, missing, or overclaimed — not to
praise, summarise, or approve.

Repo: `/home/tommy/projects/constellation-skills/.worktrees/567-k-one-spine-mutable-middle`
Pinned to `9b38b9d9`.

## Read exactly these, and nothing about how they came to be

1. `.agent-work/567-k/MISSION_FRAME.md`
2. `.agent-work/567-k/execute.json`  — the gate plan under critique
3. `.agent-work/567-k/DESIGN_COMPARISON.md`

You may read repo source to check a claim. **Do not modify any tracked file.** Never run a
mutating engine verb against a live spine — `.agent-work/567-k/spine.json` and
`.agent-work/epic-567-door/spine.json` are LIVE, read-only. Copy to a temp dir if you must drive one.

## The three lenses — cover all three explicitly

- **Intent-fit.** The issue is #634: a run's plan should be frozen at its bookends, mutable in its
  middle, in one spine per agent — for Admiral, Commander AND crew. The human said: "there should
  likely be frozen required gates at the start and finish, but what we do in the middle is squishy";
  and "this isn't only a commander thing… I wouldn't be mad at a crew updating its plan along the
  way too. it'd probably be good for us to be able to capture 'the plan changed, here's how'."
  **Does this plan serve that point, or has it drifted into something adjacent and easier?**
- **Testability.** Can every gate's close criteria actually be exercised and falsified? Name any
  postcondition that would pass in both the healthy and the defective world — a check that cannot
  fail is the failure mode this repo cares most about.
- **Simplicity / YAGNI.** What can be **deleted**? Which gate is ceremony? Where is the plan
  buying something nobody asked for?

## Attack these specifically

- The comparison recommends candidate B. **Is that recommendation actually supported by the
  evidence in the document, or does the reasoning have a hole?** Argue the case for C, or for A.
- The comparison says "immediate protection, or backward compatibility. Not both." **Is that a
  real dilemma, or is there a fourth option all three candidates and the author missed?** Think
  hard about this one; it is where a genuine finding is most likely.
- Is the claim "the window to reify waves closes when `execute` starts" correct? Check it.
- `g3-proof` is a reasoning gate with no crew. **Is the stated crew waiver legitimate, or is it
  the author grading their own homework?**
- Does the plan actually cover its whole stated file-ownership scope
  (`scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, every `*SPINE*.template.json`,
  `specs/`, tests)? Name anything in scope that **no gate touches** — a missing gate surfaces only
  at review otherwise.
- The author floated a scope question rather than deciding it. **Is the float legitimate, or is it
  avoidance of work that is plainly in scope?**

## Output shape

Use these headings. For each finding: **what is wrong**, **why it matters**, **what you would do
instead**, and a severity of `blocking` / `should-fix` / `consider`.

### 1. Verdict in one paragraph
### 2. Intent-fit findings
### 3. Testability findings
### 4. Simplicity / YAGNI findings
### 5. The strongest argument AGAINST the recommendation of candidate B
### 6. Anything the author overclaimed, hedged, or quietly skipped
### 7. What is genuinely good (short — do not pad)

Do not triage your own findings — you do not decide what gets fixed. Report them.
An empty section is fine if you truly find nothing; padding is worse than silence.
Write your result file **before** ending your turn. That write is the delivery.
