# Launch order — lane N: the tier table refuses the role this corpus actually dispatches

You are an implementer with a plan, dispatched by the Admiral of epic **#567**.
Your worktree is `.worktrees/567-n-role-key` on branch `feat/567-n-role-key` from `fbd5cdaa`.
Work only inside it. Do not touch the main checkout.

## What happened, exactly

Wave 3 (lane J, issue #633) added `ROLE_MODEL_TIERS` and `resolve_model()` to
`scripts/run_crew.py`, wired into `CrewLaunchSpec.__post_init__`. It is good work and the
human ruled on its tier values directly. But the Admiral's very next dispatch — the one
that would have closed this epic — was refused by it:

```
REFUSED: no model tier declared for role 'commander-delegated' under harness 'claude'
         -- refusing rather than guessing
```

That is `resolve_model` branch 1, working exactly as designed. The defect is not the
policy. **The defect is that the declared key set was drawn from the role names someone
expected the corpus to use, rather than measured from the role names it does use.**

Measured by the Admiral, from live doctrine (`skills/` and `specs/`, archive excluded):

| role term named in doctrine | mentions | declared in table |
|---|---|---|
| reviewer | 84 | yes |
| commander | 74 | yes |
| implementer | 42 | yes |
| critic | 29 | yes |
| admiral | 22 | yes |
| cartographer | 8 | yes |
| **commander-delegated** | **7** | **NO** |

Seven of seven doctrine role terms, six declared. One gap, and it is the role every
delegated Commander dispatch in this epic used (10 registry entries).

Separately measured, so you are not surprised by it: the full historical registry across
`.agent-work/**` contains ~41 distinct role strings, most of them one-off excursion names
(`x1-designer-a`, `designer-x5c`, `graph-tools-researcher`). Those are **archive**, not
live doctrine. They are out of scope. Do not declare them, and do not add a wildcard or a
prefix match — refusing an undeclared role by name is the design, the human signed off on
it, and `tests/test_crew_launcher.py:1123` pins it with `"scout"`.

## Your task

**1. Declare `commander-delegated`.** Under harness `claude`, at the commander tier, which
the human ruled on in these exact words: *"commander should be sonnet or opus allowed,
haiku can't handle it."* So: default `sonnet`, allowed `{sonnet, opus}` — identical to the
`commander` row. Match the file's existing style exactly.

**2. Write the guard that would have caught this.** This is the more valuable half and the
reason this is a lane rather than a one-line patch. A test that asserts the declared key
set covers **every role term live doctrine names** — derived by scanning `skills/` and
`specs/` at test time, not by hardcoding today's seven. Hardcoding the list reproduces the
original defect in test form: it would pass forever while doctrine grows a new role.

Design it yourself; the Admiral has not settled its shape and you should not treat the
sketch above as settled. Two things it must survive, and say in your return how you handled
each:

- **It must not be trivially green.** A scan that matches nothing passes vacuously. Assert
  a floor on what your own scan finds (`tests/test_cli_retirement_guard.py` does exactly
  this — it asserts its walk reaches >=60 files — read it for the in-tree precedent).
- **It must not red on archive noise.** `.agent-work/` and `docs/superpowers/plans/` carry
  dead role names. Scope your scan and justify the scope in a comment.

If your scan finds a doctrine role term beyond the seven above, that is a real finding:
declare it if the tier is obvious from the human's ruling, and **name it in your return**
either way. Do not guess a tier you cannot ground.

**3. Do not touch anything else.** Not `skills/workbench/**` and not its referrers — lane M
owns those in a parallel worktree, and the two of you must not collide. Not the `codex` or
`local` harness rows: they are empty on purpose (`decision:harness-dimension-is-required`),
every dispatch under them refuses today, and whether that is right is the human's call, not
this lane's. **If you form a view on it, put it in your return as a finding.**

## Standing hazards, inherited

- Unset `SPINE_FILE`, `SPINE_SESSION`, `SPINE_PARENT` and `CREW_SCRATCH_DIR` before running
  the suite — your own crew env reds `ScratchDirResumeTests`, and that red is not yours.
- `map/INDEX.md` is Admiral-owned this epic (#544). A green branch is green **except**
  `MapTreeFreshnessTests`. Do not regenerate it.
- Drive your spine through the MCP door. The CLI is not a fallback — this epic removed it as
  an agent-facing path. If you find yourself needing it, that is a finding worth more than
  the workaround: record it.
- File no issue. Stage anything for later under `.agent-work/567-n/triage-candidates/`.

## Done means

A green PR against `main`, and `.agent-work/567-n/RETURN.md` carrying: the declaration diff,
the guard's design and how it survives both hazards above, your scan's measured output
(the role terms it found and the file count it walked), and any finding on the empty
harness rows.

**Budget: Sonnet.** If you dispatch any crew, pass `--model` explicitly.
