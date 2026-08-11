# Launch Order: `C2 — generate the spine from a spec instead of writing it by hand`

**Epic:** `epic-418-followon` · **Wave:** `w6-generator` · **Work id:** `epic-559/c2-generate-the-spine`
**Role:** commander · **Model:** Opus · **Your crews:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine` (branch `epic-559/c2-generate-the-spine`, base `0ab7ecab`)
**Your spine:** `.agent-work/epic-559/c2-generate-the-spine/spine.json`, already instantiated for you. It is bound into your environment.

## Mission

**Write the thing that writes spines.**

Today a human or an Admiral hand-authors every spine: the gates, the imperatives, and the check
commands. That last part is where it breaks. A check is a shell command typed from memory, and a
wrong one does not announce itself — it passes, and the gate opens on nothing.

Build a **spec format** an author can write without knowing the engine's JSON shape, and a
**generator** that emits a spine from it — one that refuses any spec whose output
`scripts/validate_spine.py` would reject. Then write **role specs** for at least the implementer and
the reviewer, and prove a spine generated from one drives to a terminal state in a real dispatch.

Two properties are not optional in the output:

1. **Every gate carries a place to record beliefs, concerns and open questions.** A crew that has to
   hand something back needs a gate to hand it back at. Use the `constraints` and `directives`
   substrate the engine already renders on the active gate — **not** a new field the engine ignores.
   Both are **task-level** fields — `checklist_engine.py` reads `t.get("constraints")` and
   `t.get("directives")` (lines 2024, 2032) and renders them on the active gate (2182, 2189).
   Neither is read at the top level, so do not put them there.

   Measured on your base commit across every engine-driven checklist in the tree — **560 spines,
   4341 tasks**:

   | field | shipped templates (12 spines, 61 tasks) | whole tree (4341 tasks) |
   |---|---|---|
   | `constraints` | 3 tasks | 970 tasks (22%) |
   | `directives` | 3 tasks | 22 tasks (0.5%) |

   The two are not symmetric, and an earlier Admiral estimate that both were near-empty was wrong —
   these are the measured counts. `constraints` is in real use and already carries an informal
   meaning; read some before you redefine it. `directives` is all but empty, which makes it the field
   you can give a job to without breaking anyone — and `_render_directive_lines` already handles
   **two shapes**, a dict of name → contract and a plain list of strings, which is more structure
   than `constraints` offers. Design against what is actually there.
2. **Judgment is carried up, not buried.** The human's rule, verbatim: *"as a general rule,
   judgement should be highlighted and brought to the higher level. greater claim requires greater
   review."* A generated spine should make a large claim visible to whoever reviews it rather than
   letting it sit inside a gate nobody looks at.

### Why this serves the epic

The epic's thesis is that prose instruction is a liability, because the reader may be weaker than
the writer, so anything that can sit behind a tool or a check should. A hand-authored check is the
same liability one level up — and it does not go away by making the author more capable. The
evidence is in the Prior-Wave Verdicts below, and it is about the Admiral, not about a crew.

`scripts/validate_spine.py` shipped last wave and can refuse a bad spine. Nothing yet writes a good
one. That is you.

## Prior-Wave Verdicts (pasted)

### The measurement that motivates this mission

The Admiral hand-authored roughly **ten work spines and seven review surveys** during wave 5. **Four
carried checks that could not do their job:**

- an unquoted pytest selector — `-k Door or Tie or Registry` — which the shell split into words, so
  the command never selected what it claimed to;
- a probe that ran `python -c 'import mcp_spine_server'` with no spine bound, which raises `KeyError`
  at import time, so the probe could only ever fail;
- a call written as `build_entry(session=...)` where the function's parameter is `work_id=` — argparse
  refused before anything ran;
- a population filter that was wrong twice: first over-broad to all of `.agent-work/`, then narrowed
  by filename substring to 14 files when the real population was 25.

**None was caught by its author first.** Each was found downstream — by a crew, by a reviewer, or by
argparse. That is the whole argument for this mission.

### C1's verdict (merged `0ab7ecab`) — the lint you must not be refused by

`scripts/validate_spine.py` refuses a spine or template the engine cannot read, plus four
falsifiability faults:

- `falsifiable-all-null` — a gate whose every postcondition check is `null`;
- `falsifiable-zero-collect` — a pytest selector that collects zero tests;
- an artifact check with no `match` whose statement asserts a property;
- `falsifiable-unresolved-placeholder` — a `<placeholder>` still in a check command.

It reports **undecidable** as a third channel distinct from OK, so *"could not tell"* is never
silently indistinguishable from *"checked, found nothing"*. Admiral's own control before merging:
neutering `validate()` turns **24 of 82** of its tests red.

Its round 1 was **BLOCKED** for refusing the corpus's own self-checking idiom —
`test $(pytest ... --collect-only 2>/dev/null | grep -c '::') -ge N && pytest ...` — with **8 of 9
reports being false positives**. Round 2 fixed it to 0 over 26 type-discovered checklists. **Read
that idiom; it is the corpus's documented way of making a test gate self-checking, and your
generator should be able to emit it.**

### B's verdict (merged `90b39e2b`) — what a check that cannot fail actually looks like

The Commander template's `g1-implement` gate promised *"no unresolved blockers"* while checking only
that some `implementer-result` artifact had arrived. Round 1 "fixed" it by constraining the check to
`match: {"status": "complete"}`. A census of **122 real `implementer-result` records** found:

```
    28  status=complete      <- the only shape the round-1 fix accepted  (23%)
    17  verdict=COMPLETE
    16  verdict=complete
     3  status=COMPLETE
     2  status=COMPLETED
    10  keys: path,summary
     8  keys: diff_digest,gate_id,green_command,green_exit
     5  keys: blockers,path,verified
```

The engine's artifact match is exact dict equality, so every shape but the first failed. **The fix
flipped the defect's sign rather than removing it** — a gate that could not fail became one that
could not pass, shipping in the template every Commander instantiates. Round 2 wrote the convention
into the gate's own imperative and pinned it with the first tests in this repo that ask whether a
shipped template's gates are satisfiable by a real run.

**The lesson for you:** a check and the instruction that satisfies it must live in the same place, or
they drift. Your generator emits both from one spec, which is the structural version of that lesson.

### A's verdict (merged `9a056105`) — the shape a crew's job takes now

A crew dispatched with `--spine` and no `--handoff` drives its spine from the prompt alone. A cold
reviewer proved it by dispatching a real probe crew, which succeeded **while reading a stale
installed skill that told it to build its own plan and use the CLI**. The prompt beat contrary
doctrine sitting in the agent's own instructions.

`run_crew.py` now judges a spine-only dispatch on its spine reaching a terminal state
(`spine_terminal`), not on a result artifact. A survey with no `consolidation` is **not** terminal.

### E1's verdict (merged `094f573a`) — where a stuck crew goes

`blocked` is a recorded outcome distinct from `failed` and `complete`. A dispatch records the parent
a crew should reach, bound as `SPINE_PARENT` (value `unknown` when unset — that is a real answer, not
a missing one). **Measured:** a headless crew is on the peer graph but **cannot** reach a parent named
by a descriptive string. So the durable path — a blocked gate, a recorded parent, and a parent that
polls — is the mechanism, and messaging is an optimisation nothing may depend on. Do not design
anything that needs a crew to message you.

### What the lint says about the shipped corpus today

`python scripts/validate_spine.py --sweep` on your base commit:

- `falsifiable-all-null` on the **context gate of nine of twelve** shipped role templates;
- `falsifiable-unresolved-placeholder` on `<exact test command>` in `EXECUTE_PLAN.template.json`
  (`g1-integrate.c1`) and `IMPLEMENTER_PLAN.template.json` (`m1.c2`);
- `CYCLE`, `INTERROGATION` and `REVIEW_SURVEY` come back `OK`.

Run it yourself first. It is your acceptance oracle and your baseline.

## Pre-Rulings

Ruled in advance. Each is overridable if evidence contradicts it — say so plainly when you override,
with the evidence.

- **decision:placeholder-template-vs-instance** — A `<placeholder>` is a legitimate slot **in a
  template** and a fault **in an instantiated spine**. B's test allowlists `<exact test command>` as
  an authoring-time fill-in; C1's lint calls the same occurrences faults. Both are right about
  different objects: a template is written to be filled, and an instance that still carries a
  placeholder holds a check that can never run. The lint keys on which it is looking at, and **your
  generator refuses an instance that carries one.** This retires B's two-item allowlist, which had no
  test on its own growth — a future author could quiet a real offender by appending to it and nothing
  would notice. That is the escape-hatch shape this epic exists to find.
  `@grade: settled/admiral · leans plan, execute`
- **decision:qualitative-must-be-stated** — A gate with **no checkable postcondition must say in so
  many words that it is qualitative.** Silence is refused; the stated form is accepted. Nine of twelve
  shipped templates carry the silent default on their context gate and **none states the choice**,
  which makes it a default rather than a decision. The lint's own message already offers this out.
  How the spec expresses it is yours.
  `@grade: settled/admiral · leans plan`
- **decision:no-engine-format-change** — `checklist_engine.py`'s on-disk format is not changed. The
  generator emits what the engine already reads. If you find the format genuinely cannot carry
  something the mission needs, that is a **float to the Admiral**, not a patch.
  `@grade: settled/human · leans plan`
- **decision:notes-ride-in-existing-substrate** — Beliefs, concerns and open questions ride in
  `constraints` and `directives`, which `current` already renders on the active gate. A new field the
  engine ignores is worse than no field, because it looks like it works.
  `@grade: settled/human · leans plan, execute`
- **decision:spec-format-is-yours** — Whether the spec is JSON, TOML, YAML or something else, how it
  names checks, and how it is laid out are **entirely yours**. The one property to design against:
  the spec must not make its author retype a shell command from memory, because that is precisely
  where every hand-authored check failed. If your implementer spec still asks its author for a raw
  pytest invocation, the defect has **moved rather than gone** — say so honestly if that is where you
  land.
  `@grade: guess · leans plan · settle: read what your own role spec asks its author to type`
- **decision:sonnet-crews** — Dispatch your implementers and reviewers on **Sonnet**. The human's
  instruction is verbatim: *"prefer sonnet crews."* You run on Opus because designing a format is the
  highest-judgment work in this wave; that escalation is the Admiral's and is already recorded.
  Escalate a single crew to Opus only if a Sonnet crew has already failed the same task once, and say
  why.
  `@grade: settled/human · leans execute`
- **decision:cold-review-every-change** — Every change gets a cold reviewer independent of its
  implementer, and reworks until that reviewer approves. Three of six workstreams last wave were
  blocked on first review and one was blocked twice; two of those blocks caught a fix that had
  flipped its defect's sign. Neither would have been caught by reading the diff — both reviewers
  found them by **running** something. Tell your reviewers that.
  `@grade: settled/admiral · leans execute`
- **decision:no-template-edited-to-pass** — Do not edit a shipped template to make your generator's
  output validate. If a shipped template and your generator disagree, the generator is the thing
  under construction and the disagreement is a finding.
  `@grade: settled/admiral · leans execute`

## A defect in your own spine — read this before you drive it

Your instantiated `spine.json` still carries **four `<engine>` tokens**, in the imperatives of `init`
and `archive`. They instruct you to run the engine CLI. They are unresolvable — nothing in the corpus
defines `<engine>` — and they are residue from wave 5, which removed the token from crew-facing
skills and left it in the orchestrator-tier templates (`COMMANDER_SPINE`, `ADMIRAL_SPINE`,
`EXPLORER_SPINE`, `commander-core.md`).

**Ignore them and use the door.** The human's ruling is categorical: *"anything that we want to do
for the spine needs to be accessible via mcp. the agents should not know about the cli. period.
anything that we can only do via the cli is a defect."* All eighteen engine verbs are reachable
through nine `mcp__spine__*` tools; find them with `ToolSearch`.

This is also **in scope as a finding**: a spine that tells its own driver to use the CLI is the exact
defect your generator exists to prevent, and your generator must never emit such a token. Whether you
fix the four shipped templates in this wave is your call — say what you decided and why.

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. If you build the
spec format and find that it does not remove the failure mode — that authors still hand-write the
fragile part — **report that with the same rigor as a win.** It is more useful than a generator that
looks finished. Do not manufacture a success.

## Inherited Latitude

**Yours to decide and log:**

- The spec format, its file type, its layout, its vocabulary, and how it names checks.
- The generator's internals, its CLI shape, and its error messages.
- How many implementer/reviewer rounds the work takes, and how you decompose it into crews.
- Which role specs beyond implementer and reviewer to write, if any.
- Whether to fix the four shipped `<engine>` tokens this wave.
- How beliefs, concerns and open questions are represented inside `constraints`/`directives`.

**Float to the Admiral (that is me; I answer and continue you):**

- Any change to `checklist_engine.py`'s on-disk format.
- Any change to `scripts/validate_spine.py`'s fault set or its acceptance boundary. It is your oracle;
  moving the oracle to make your output pass is how a check stops meaning anything. Ask first.
- Editing `docs/agents/*` — the human's call, always.
- Any decision that fits none of the classes above. Say in one line why it fit none.

**Never:** touch `settings.json`. Push to `main`. Run two crews in one worktree. `git add -A` —
`.agent-work/` is tracked here, so stage by name.

## File Ownership

Your working-notes file is `.agent-work/epic-559/c2-generate-the-spine/notes-1.md`. You are its sole
writer this wave.

Name any additional notes file `notes-<n>.md`, **never** `findings-<n>.md` — the harness `Write` tool
refuses any path whose basename contains "findings", and three agents in one epic each burned a cycle
working around it with a shell heredoc. The guard is not ours to change; the word is.

## Workspace

`/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine`, branch
`epic-559/c2-generate-the-spine`, base `0ab7ecab` (current `main`, pushed, suite green at 2689
passed / 3 skipped / 1121 subtests).

Provisioned by:

```
git worktree add /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine \
  -b epic-559/c2-generate-the-spine main
```

First step, before any git operation:

```
python /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py \
  --here /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine
```

It must exit 0. Paste its output into your return report.

**Isolation is git-only.** `CLAUDE_PROJECT_DIR` resolves once at session launch and is inherited
unchanged by every subagent, so hook code still runs from the main checkout even though every git
operation is correctly fenced (#269). Your mission does not touch `scripts/hooks/*`, so this should
not bite — but if you find yourself validating hook behaviour, do it from a fresh process whose
`CLAUDE_PROJECT_DIR` genuinely resolves to your worktree, never a fixture that injects the value you
are trying to prove.

## Inherited Context

**Test mode.** Always:

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Unsetting the three spine variables matters: `scripts/mcp_spine_server.py` reads `SPINE_FILE` **at
import time** and raises `KeyError` without it, so a test that imports the door inherits your bound
environment and passes or fails for the wrong reason. Use `python`, not `python3`.

**The door.** Your spine is bound via `SPINE_FILE` / `SPINE_SESSION`; your parent is bound as
`SPINE_PARENT`. There is no per-call spine addressing — a tool acts on the spine bound at launch. Find
the tools with `ToolSearch`. `spine_evidence` with `action=waive` is **denied by a hook** for
dispatched crews, including you: you cannot waive your own gate. That is deliberate. A gate you
cannot satisfy **blocks** — `spine_halt block`, name the gate and your parent, and return to me.

**Never end your turn waiting.** You run headless. If you end your turn to wait for a crew, nothing
resumes you and the run dies mid-`execute`, however well the crew is doing. When you dispatch a crew
and must wait, wait **actively, inside your turn**: poll its result artifact or the crew registry in a
loop until it lands, then integrate it and drive on. Treat the thought *"I'll wait for it to finish"*
as the cue to **start polling**, never to stop. One crew in wave 5 died exactly this way.

**Dispatching crews.** `python scripts/run_crew.py` — `--work-id`, `--gate`, `--role`, `--model`,
`--worktree`, `--handoff`, `--result`, `--spine`, `--parent`. `--handoff` is optional when `--spine`
is given (the crew drives its bound spine); `--result` is optional the same way. Pass `--parent` so
your crews record who dispatched them. **One crew per worktree at a time.** If a crew needs its own
worktree, provision it explicitly and verify it.

**Compact JSON.** The shipped templates are stored compactly. Edit them as **raw text, surgically** —
never round-trip through `json.load` / `json.dump`, which reflows the whole file and destroys blame.
Re-validate with `json.load` afterward.

**Falsifiability idiom.** The corpus's documented way to make a test gate self-checking:

```
test $(pytest -q -k 'Selector' --collect-only 2>/dev/null | grep -c '::') -ge 4 && pytest -q -k 'Selector'
```

Quote the `-k` selector. An unquoted one is one of the four defects that motivated this mission.

**Three-way guard fixtures.** When you write a guard, pin its boundary the way
`tests/test_mcp_adoption.py::_cli_only_verb_violations` does: a VIOLATING fixture it must catch, an
INNOCENT one it must not, and an ACCEPTED_FALSE_ALARM it knowingly tolerates. A guard with no test on
its own false-positive boundary is how C1's round 1 shipped an 8-of-9 false-positive rate.

**`.agent-work/` is tracked in this repo.** Stage by name. Never `git add -A`.

**Do not run the installer** (`scripts/install_constellation.py`). It rewrites the tracked `.mcp.json`
interpreter from `python3` to a probed value — a known defect recorded on **#539**. The Admiral
handles installs and reverts that rewrite each time.

## Pre-empted Steps

Cite this launch order rather than redoing these:

- **`init`** — done. Your work area is scaffolded and `spine.json` is instantiated from
  `COMMANDER_SPINE.template.json` with placeholders resolved. You still **claim the lease** yourself
  (`c2`), through the door.
- **`understand`** — the problem statement and protected intent are the Mission and Pre-Rulings
  sections above, confirmed by the Admiral acting as the human's delegate. Record `c1`'s
  `user-decision` evidence citing this launch order; do not run an interrogation to re-derive it.
- **`plan.c3` (plan approved)** — the Admiral approves, not the human. Send me your gate plan and I
  will approve or amend it. This is a real gate, not a formality: your plan is the thing I most want
  to see before you spend crews on it.
- **`triage.c2` (user approved issue creation)** — **no issues are created this wave.** Route every
  triage candidate to me in your return report instead, and record `c2` citing this order.
- **`review.c1`** — the Admiral accepts the run summary. The human accepts the epic at closeout, not
  this wave.

Everything else is yours to drive: `context`, `plan` (the rest), `execute`, `reconcile`, `feedback`,
`archive`.

## Data Locations

Everything you need is tracked and present in your worktree. Two things live outside it:

- Installed skills: `~/.claude/skills/constellation-*` — refreshed from `main`@`0ab7ecab` at
  2026-08-11, so they carry current doctrine including the fail-up rule. Read the repo's
  `skills/` when you want the source of truth; the installed copies are what a dispatched crew
  actually reads.
- The Admiral's log for this epic:
  `/home/tommy/projects/constellation-skills/.agent-work/epic-418-followon/ADMIRAL_LOG.md` — readable,
  not writable by you.

## Budget

- **Model tier (required):** **Opus** for you; **Sonnet** for every implementer and reviewer you
  dispatch. The escalation to Opus at your tier is deliberate and recorded: designing a format is the
  highest-judgment work in this wave, and the human's rule is that a greater claim requires greater
  review.
- **Compute/time, session-window:** Generous. The human's instruction is verbatim: *"be thorough and
  take your time."* Prefer another review round over shipping something unproven. There is no
  deadline inside this session other than your own turn — which you must not end while a crew is
  running.

## Stop Conditions

Stop and return to me when:

- a decision falls outside your Inherited Latitude, including anything that would move
  `validate_spine.py`'s acceptance boundary;
- the evidence you need is impossible to get — say what you tried and what it would take;
- your scope would have to grow beyond the Mission to finish;
- you are blocked on a gate you cannot satisfy — `spine_halt block`, name the gate and your parent,
  and return;
- you need context this order does not cover and cannot safely proceed without.

**Asking up is always sanctioned.** I am your reachable tier and I answer and continue you. A
return-and-query costs one round-trip; a wrong guess costs a whole workstream. Wave 5 spent three
rework rounds on one issue because a crew guessed at a convention nothing documented.

## Return Shape

Write `.agent-work/epic-559/c2-generate-the-spine/COMMANDER_RETURN.md` **before** you go idle — an
idle notification with no artifact reads as stalled, not done. I judge completion from what you
produced.

It must contain:

1. **Verdict** — what was built, what holds, what does not.
2. **Evidence you personally ran** — commands and their output, not descriptions of them. Include the
   `verify_worktree_isolation.py --here` output.
3. **The control** — the spec your generator refuses, shown accepted before the guard existed and
   refused after. Without that pairing the refusal is not evidence.
4. **The honest answer to the settling question** — does your role spec still ask its author to type
   a shell command from memory? If yes, say so; the defect moved rather than went, and knowing that
   is worth more than a clean-looking result.
5. **Map impact** — regenerate with `python -m scripts.code_map build` if you add modules, and say
   what moved.
6. **Triage candidates** — routed to me, not filed as issues.
7. **Workflow feedback** — where the skills, templates or handoffs got in your way. This is the epic's
   improvement loop and it is not optional. Wave 5's most valuable single finding came out of a
   crew's feedback section.

Then: commit, push your branch, and open a PR (`gh pr create -F <file>` with the body in a temp file,
never a heredoc). **Do not merge.** The Admiral merges to `main` after cold review and a green suite.
