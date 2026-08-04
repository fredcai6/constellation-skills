# Prototype Result: spine carries the step instructions (exc-8)

## Question

Can step-specific instructions be moved out of a role's always-loaded skill prose into the spine
template the engine pushes per gate — demonstrated live on at least one real role step — without
losing the behavior, and what does the seam look like?

## Verdict

`answered-yes` — with one hard boundary and one cost, both named below.

**Answer:** Yes. A step-specific instruction relocated into the gate imperative is delivered
verbatim through the engine's `current` output and is acted on correctly by a cold subagent that
never saw the skill prose — including reconstructing an artifact section the template no longer
carried. **54% of the Commander's always-loaded words are step-specific and relocatable.** The
seam is the `imperative` string, and only that string: it is the sole free-text field of a task
that `current` renders. The boundary is a **bootstrap floor** — the instructions that instantiate
the spine and claim the lease fire before any engine call exists and can never ride the channel.
The cost is **exact 2x duplication**: the engine's RAIL advisory echoes the imperative verbatim, so
every relocated word is paid twice on every `current` call.

## What was tested AND what was NOT tested

### Tested

**The tracer instruction.** The Deliverable Path Check rule at `commander-core.md:73` — "for each
committed deliverable, run `git check-ignore <path>` and confirm exit 1, or record the artifact as
intentionally local-only." Chosen because a repo-wide grep proved it lives in exactly one place in
the always-loaded prose, it bites at exactly one gate (`gN-implement`), and the shipped
`EXECUTE_PLAN.template.json` imperative never mentions it. Its correct execution leaves an
unmistakable trace.

**The relocation.** `relocate.py` deletes the sentence from `commander-core.md` and inserts it into
the `g1-implement` imperative, then asserts exactly one home remains (`prose=0 gate_template=1`).
The duplicate how-to in `IMPLEMENTER_HANDOFF.template.md` was stripped too, so after relocation the
string `check-ignore` appears exactly once in the whole `skills/` tree.

**The delivery.** A real `execute.json` was instantiated from the shipped template with one
concrete gate and driven with the real engine (`claim → start → attest → advance → start`) to
`g1-implement` on both a control and a treatment arm. `current` on the treatment arm carries the
relocated sentence word-for-word; the control arm does not.

**Five cold sonnet subagents**, each given only its arm's `current` output plus identical gate data,
none of which loaded the Commander skill. Arm materials were isolated in per-arm directories and
the agent-visible work area was grep-verified clean of the tracer string before dispatch.

| Round | Arm | Instruction delivered via | Handoff template | Ran `git check-ignore`? | Recorded exit codes? |
|---|---|---|---|---|---|
| 1 | A1-PROSE | always-loaded prose (today's real delivery) | has section + slots | yes | both paths |
| 1 | A2-NEITHER | nothing (negative control) | has section + slots | yes | ignored path only |
| 1 | A3-SPINE | **gate imperative via `current`** | has section + slots | yes | both, verbatim commands |
| 2 | B2-NEITHER | nothing (negative control) | **section removed** | **no** | — |
| 2 | B3-SPINE | **gate imperative via `current`** | **section removed** | **yes** | both, verbatim commands |

Round 1 was a scoped null on discrimination and is reported as such: all three arms ran the check,
because the template's `## Deliverable Path Check` heading with its Committed/Local-only slots is
itself an instruction carrier. That is a finding, not a failed run — the behavior was never at
risk in round 1, so round 1 cannot show the prose was load-bearing.

Round 2 removed that affordance and discriminates cleanly. `HANDOFF-B2-NEITHER.md` contains zero
occurrences of `check-ignore` and no path-check section; the agent never ran the command.
`HANDOFF-B3-SPINE.md` contains five, and the agent **created the section that the template no
longer had**, ran both commands, recorded exit 1 and exit 0 verbatim, and correctly classified the
trap path. The gate deliberately paired a non-ignored path (`scripts/verify_gauge_freshness.py`,
exit 1) with a genuinely ignored one (`.agent-work/proto-exc8/gauge.json`, exit 0, matching
`.gitignore:9`) so that asserting from path shape rather than running the command would be visible.
B3 quoted the `.gitignore` rationale back and told the implementer not to fight the ignore rule.

**Guards.** `tests/test_install_constellation.py`, `test_curate_corpus.py`, `test_spine_rail.py`,
`test_spine_provenance_check.py`, `test_check_corpus_freshness.py`, `test_write_a_skill.py` — 229
passed, 356 subtests, run as `python -m pytest`. The relocation trips no corpus guard, no residual
guard, and no spine-rail assertion.

**Duplication cost, measured.** Control `current` = 160 words; treatment = 250. The relocated
sentence is 45 words. 250 − 160 = 90 = exactly 2 × 45.

### NOT tested

- **Only one instruction was relocated.** No corpus rewrite, per the exclusions. The census is
  paper classification, not five more live tracers.
- **Only one role** (Commander) and **one gate** (`g1-implement`, in the `execute.json` child
  checklist). The ten top-level `COMMANDER_SPINE.template.json` steps were read and classified but
  not driven end to end — reaching `execute` requires satisfying real `map_orient.py` and
  `verify_state_note.py` postconditions that this prototype did not stand up.
- **Only sonnet**, one sample per arm. No repetition, so per-arm variance is unmeasured and the
  round-2 result rests on n=1 per arm.
- **Bulk relocation was not attempted.** Whether a ~1250-word `execute` imperative still reads as
  one instruction, or drowns its own key sentence, is untested and is the obvious next question.
- **No hooks were wired and `~/.claude/settings.json` was never touched**, per the exclusions.
- Shared-across-roles text (`global-everyone.md`, `global-orchestrator.md`) was excluded from both
  the tracer and the census.

### Next variant

The named next test is **dose-response on one imperative**: relocate all 1252 `execute`-bound words
into the `execute` imperative and re-run the same cold-agent design against three instructions
buried at different depths. That answers whether the channel has a saturation point, which is the
one thing this run's single-sentence tracer cannot speak to.

## The census

**Method.** Sources are the originals at `main`, not the edited worktree copies, read via
`git show`. YAML frontmatter is stripped. A unit is a markdown block — consecutive non-blank lines
— with headings counted as their own units, tables and fenced code kept whole, and top-level list
items split into separate units (the "Start here" 1–5 list and the delegated-mode bullets each span
several destination steps, so leaving them merged would have hidden the split). Each unit gets
exactly one class, assigned by hand, reproducible via `python census.py report`.

The three classes: **step-specific** means relocatable to one named gate. **always-needed** means
role identity, principal binding, the spine-use trigger, project focus, or any rule that spans two
or more steps — the multi-step rule is stated because several units (the four `user-decision`
checkpoints, the architecture bookend, decision candidates) are genuinely not one gate's business.
**reference-on-demand** means consulted at need, not carried in context.

**Full surface** — `SKILL.md` + `references/commander-core.md` + `references/crew-dispatch.md`,
97 units, 4064 words, 28478 bytes:

| Class | Units | Unit % | Words | Word % | Bytes | Byte % |
|---|---|---|---|---|---|---|
| step-specific (relocatable) | 37 | 38.1% | 2280 | 56.1% | 16005 | 56.2% |
| always-needed | 33 | 34.0% | 1390 | 34.2% | 9222 | 32.4% |
| reference-on-demand | 27 | 27.8% | 394 | 9.7% | 3251 | 11.4% |

**The sharper cut.** `crew-dispatch.md` is pointer-loaded ("Read it before dispatching a crew"), so
it is not really always-loaded. Excluding it leaves the true always-loaded core — `SKILL.md` +
`commander-core.md`, 82 units, 3675 words — at **54.2% step-specific**, 37.8% always-needed, 7.9%
reference-on-demand. `commander-core.md` alone is 57.4% step-specific.

Per file, by unit count: `SKILL.md` 6 units, **all six always-needed, zero relocatable** —
it is already the kernel the corpus claims it is, and this census found nothing to take out of it.
`commander-core.md` 76 units (29 step-specific, 27 always-needed, 20 reference-on-demand).
`crew-dispatch.md` 15 units (8 step-specific, 7 reference-on-demand).

Where the relocatable words would go:

| Destination step | Words | Share of full surface |
|---|---|---|
| execute | 1252 | 30.8% |
| plan | 653 | 16.1% |
| understand | 307 | 7.6% |
| reconcile | 68 | 1.7% |

The concentration is the headline: **`execute` alone would absorb 55% of all relocatable words**,
and `execute` + `plan` together absorb 84%. A general relocation is not an even redistribution
across ten steps; it is mostly two very large imperatives.

## The seam

**Where relocated text lives.** The task's `imperative` string, and nothing else. `current()` is
`render_human(state(cl))`, and `state()` projects exactly five things from the active task: `id`,
`status`, `imperative`, the **unmet** pre/postcondition `statement` strings, and the next verbs.
Everything else in the task object is invisible to the channel. Confirmed by reading
`scripts/checklist_engine.py:1548-1625` and confirmed empirically: the deliverable paths this
prototype wrote into the gate's `constraints` never appeared in `current`.

There is a second, narrower slot: a condition's `statement`, which rides only while that condition
is **unmet** and vanishes once satisfied. That makes it right for a precondition you must read
before acting and wrong for anything that must stay legible across the step.

**What the seam gives you for free.** The `imperative` is unvalidated free text — no schema, no
length cap, no sanitizing. Relocation needs no engine change whatsoever. The existing `amend`
verb already rescopes an imperative through a validated delta with reason and authority recorded,
so a relocated instruction remains changeable mid-run through the engine rather than by hand-editing
JSON. And the corpus already ships the machinery: `init_work_area.py --spine` resolves template
placeholders, so a relocated instruction is versioned in the template exactly like the prose it
replaces.

**Maintainability.** Relocated text moves from markdown into a JSON string, and that is the real
tax. It loses headings, lists, tables and code fences — the engine renders one flat line. The
`execute` imperative is already 1252 words *before* absorbing another 1252; concretely, the
`context` step's imperative on `main` is already a 400-word paragraph that has to be read as one
sentence-chain. Diffs get worse: a one-word change shows as a rewrite of a very long line. Two
mitigations exist without new machinery — keep the imperative as the operative instruction and
leave genuine reference material behind a pointer (the 9.7% reference-on-demand slice should not
move at all), and use the `context_refs` array for files the step must read, since it is already
carried per step even though it does not render into `current`.

**What breaks.**

1. **The bootstrap floor — the hard boundary.** Text needed before the first engine call cannot
   ride the channel, because there is no channel yet. `commander-core.md` units 19 and 20 are
   exactly this: "the moment this skill loads — before you read the issue closely" and "instantiate
   `spine.json` … then `claim` the lease." You cannot read the `init` imperative to learn how to
   create the file that contains the `init` imperative. This is irreducible, and it is why
   `SKILL.md` came back 100% always-needed. Any general relocation must leave a bootstrap kernel:
   role identity, principal binding, the spine-use trigger, and the instantiate-and-claim recipe.

2. **The 2x echo — the cost.** `checklist_engine.py:229` interpolates `{imperative}` into the RAIL
   advisory, which `current` emits *in addition to* the `ACTIVE` line. Measured at exactly 2x.
   Relocating `execute`'s 1252 words would add ~2500 words to every `current` call at that step.
   That inverts the stated goal — reducing always-loaded overhead — into a per-call cost, and it is
   the strongest argument for relocating selectively rather than wholesale. This is a real
   engine-side fix, not a doctrine problem: the RAIL could carry the imperative's first clause
   instead of the whole string.

3. **Text shared across roles has no single gate to move to.** Commander and
   commander-delegated share `commander-core.md` by design. Relocating into
   `COMMANDER_SPINE.template.json` is fine because both entries drive the same spine, but anything
   in `global-everyone.md` / `global-orchestrator.md` has no one template to land in and would have
   to be duplicated per role — trading prose overhead for a divergence risk. This run did not test
   it and it is the case most likely to bite.

4. **Multi-step rules degrade.** A rule spanning several steps must be duplicated into each one or
   stay in prose. The four `user-decision` checkpoints (92 words governing `understand`, `plan`,
   `triage`, `review`) are the clearest instance; this census classified them always-needed rather
   than pretend they belong to one gate.

5. **A structural affordance can carry an instruction invisibly** — the round-1 null. The template's
   section heading was doing work that nobody had written down as an instruction. Before deleting
   any prose as "relocated," check whether some artifact template's *shape* is the actual carrier,
   or you will delete prose, measure no regression, and conclude wrongly that the prose was dead.
   This is the trap a paper census cannot see and only a live tracer catches.

**Recommended shape.** Relocate step-specific text into its gate's imperative, keep the
reference-on-demand slice behind pointers, leave a bootstrap kernel plus multi-step rules in
`SKILL.md`, and fix the RAIL echo first — otherwise the 54% you remove from always-loaded context
comes back doubled at every gate.

## What it taught beyond the question

**A gate's `constraints` and `anchors` blocks are invisible to the agent driving it.** This was not
what the prototype set out to find. `EXECUTE_PLAN.template.json` gives every gate an `anchors`
block, and `commander-core.md` says gates inherit frame anchors so "every role plans from the same
map context" — but `state()` does not project `anchors` or `constraints`, so an agent driving from
`current` alone never sees them. They reach crews only if the Commander manually copies them into a
handoff. All five cold agents independently reported finding no anchors and several flagged it
rather than inventing anchors, which is the right behavior and also evidence the gap is real and
routinely hit. This is worth a tracker issue on its own; it bears directly on #393's finding that
`TREATMENT-VERIFIED` proves only that a skill loaded.

**`SKILL.md` is already done.** Six units, all always-needed. The "already kernel-shaped"
observation from #310 is confirmed *for the entry file* and disconfirmed for the reference file
behind it: `commander-core.md` is 57% step-specific. The overhead the human wants removed is not in
the file that loads first, it is in the 3475-word file that file tells you to read.

**A better question to ask next:** not "can instructions ride the spine" — they can — but "what is
the largest imperative an agent still executes faithfully?" The concentration finding (55% of
relocatable words land on one step) means the whole benefit turns on that number, and nothing here
measures it.

## Surviving pure module

`census.py` — its `units()` segmenter is pure (text in, unit list out; the only I/O is the
`git show` read at the edge) and is the reproducible basis for running this census against any
other role. It is worth lifting to `scripts/` only if a general relocation is actually cut;
until then it stays with the worktree. The classification itself is hand-assigned and is
judgment, not code — it should not be mistaken for a mechanical measure.

## Disposition

`captured-to-worktree`

**Detail:** Worktree `C:/Programs/.proto-exc8-spine-instructions`, branch
`proto/exc8-spine-instructions`, commit `5a283ad`, off `main` at `79db918`. Nothing was pushed and
nothing touched `main`. Owner is excursion exc-8 under the explore-post-phase1 run; this file is the
pointer. Per prototyper doctrine it is kept until the human disposes it and is **swept at epic
close** — re-affirmed or deleted, not parked forever. Re-affirm only if the dose-response variant
above is going to be run; otherwise delete it, since the answer is captured here.

Contents: `relocate.py`, `instantiate.py`, `census.py`, `arms/` (five per-arm briefs and the
captured `current` output for both arms), and `.agent-work/proto-exc8/` (the five cold-agent
handoff artifacts, which are the primary evidence).

## One command to run

```
cd C:/Programs/.proto-exc8-spine-instructions && PYTHONIOENCODING=utf-8 python census.py report
```

To re-drive the tracer instead: `python instantiate.py --template
skills/commander/templates/EXECUTE_PLAN.template.json --out /tmp/x.json` then
`python scripts/checklist_engine.py --file /tmp/x.json current` after driving to `g1-implement`.
