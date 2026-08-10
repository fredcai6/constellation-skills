# PLAN_ALTERNATIVE — commander-f2 (#542 adoption, #541 friction capture)

**Design-it-twice candidate. Constraint: MINIMAL.** The fewest gates that still produce, at
each gate, the evidence that closes that gate's own claim. Authored independently of the
drafted plan; `execute.json` was not read.

The mandated gate order is fixed and is not touched: **g1 identity → g2 capture → g3
installer → g4 adoption + acceptance.** The five "done" criteria are fixed and are not
reworded.

---

## 0. What minimality is allowed to buy, and what it is not

Commander doctrine (`skills/commander/references/commander-core.md` §"Crew gate vs
reasoning gate") permits a **reasoning gate**: a gate whose deliverable is a *document or
diagnosis*, whose context the Commander already holds, driven in the Commander's own
context with **no** `gN-implement`/`gN-review` crew dispatch, the crew-waiver reason stated
in the gate, and a closeout postcondition that is an attested (`check: null`) or
`user-decision` artifact rather than a crew `review-result`. The same passage warns that
"a crew on a pure design note is *shallower*, not safer," and reserves crews for gates that
produce code or an independently-verifiable change.

I applied that latitude to every gate in turn and it survives in exactly **one** place.
Recording the failures matters as much as the success, so all four rejections are below.

**Reasoning-gate candidates considered and rejected:**

- **g2 (capture) — rejected.** Deliverable is executable code in
  `scripts/mcp_spine_server.py` plus a write path through `apply_episode_delta.py`, plus a
  seeded-rejection control. Not a document.
- **g3 (installer) — rejected.** Deliverable is code in `install_constellation.py`, a file
  carrying two traps measured *this epic*. Not a document.
- **g4a (adoption edits) — rejected, and the line is worth stating.** The waiver covers a
  *document or diagnosis* — a design note, a decision, a diagnosis. It does **not** cover
  "changes to documents." g4a edits ~16 files across three tiers under `skills/`, under a
  hard failure condition (`the-cli-door-stays`) and a mechanical trap (surgical raw-text
  edits to compact-format JSON templates; never a `json.load`/`json.dump` round-trip). That
  is implementation work whose correctness a test asserts. Reading the waiver as covering
  it would also collide with `commander-core.md` §Role: "you never do another role's work
  yourself."
- **g4b (acceptance measurement) — rejected, emphatically.** A measurement is not a design
  note. It is a claim about the world whose named failure mode — per the launch order's own
  budget rationale — is "a confident wrong number, not a slow one." F's returned line is
  *"I had written a conclusion and was finding routes back to it after the evidence moved.
  Neither correction came from me."* Four reviewer BLOCKs, one of which flipped DC5 from
  negative to pass by finding a shell `for` loop scoring six engine invocations as one.
  Waiving the crew here removes the exact instrument that has historically produced the
  correction, and replaces it with the party that already holds the conclusion. **Not a
  defensible waiver at any budget.**

- **g1 (identity trade) — waiver granted.** Argued in full at g1 below.

---

## 1. The plan

**Four gates. One reasoning, three crew. Nine crew dispatches** (vs. the drafted plan's
five crew gates / fifteen dispatches).

I state this plan in full and honestly. §3 then names what it costs, and §4 recommends
against one of its own merges.

---

### g1 — the identity trade *(REASONING GATE)*

**Closes:** done-criterion **5** — "the identity trade is decided and the property given up
is written down."

**Kind:** reasoning gate. **Crew-waiver reason:** the deliverable is a decision record over
evidence the Commander already holds in full. The launch order carries F's complete verdict
set, the DC3 seam split verbatim, the three options and what each gives up, and the
`no-gen-mcp-config` tombstone with its scope. There is no code to write beyond one
invariant pin, and no independent fact for a crew to discover — an implementer would be
handed the Commander's own reasoning and asked to type it. Doctrine's warning applies
directly: a crew on this would be shallower, not safer. The launch order assigns Opus tier
naming this gate as the reason ("g1 is a design trade with no clean answer"), which places
the judgment at the Commander, not at a Sonnet implementer.

**Close criteria and the exact evidence produced AT this gate:**

1. **`IDENTITY_TRADE.md`** under `.agent-work/epic-418-followon/commander-f2/` naming: the
   option taken of the three; **the property given up, in one sentence, as a property** (not
   as a reassurance); the evidence each rejected option lost on; and an explicit statement
   of the seam that is *not ours* — that whether the Task-tool harness internally reuses a
   connected MCP client object inside one process is, verbatim from
   `DC3InheritanceMechanismTests`, "a product-internal mechanism with no observation point
   reachable from a subprocess-level test." Closeout postcondition: attested
   (`check: null`) artifact-presence, plus a `user-decision` evidence item citing
   `LAUNCH_ORDER:g1 — the identity trade` per delegated-mode doctrine.
2. **An executable invariant pin, authored and run AT g1**, in `tests/test_mcp_identity.py`.
   Its shape depends on the option taken:
   - *Option A (spine path becomes a per-call argument):* the pin asserts each tool accepts
     and validates a spine argument and refuses a path outside a declared allowlist. The
     property given up — "a server that can only ever touch the spine it was launched for"
     — becomes a runtime check rather than a structural guarantee, and the pin is what
     holds it.
   - *Option B (caller-supplied identity):* the pin asserts a caller-identity mismatch is
     refused. **The record must state that this pin is weak by construction** — a subagent
     cannot prove it is not its parent — because a pin that looks like proof and is not is
     worse than none.
   - *Option C (accept the composition; forbid the in-session case in doctrine):* the pin is
     a **drift prohibition** — identity remains three module-level constants read from the
     environment at import (`mcp_spine_server.py:113-115`), and **no tool schema exposes a
     spine path argument**. This is what stops a later agent silently taking option A.
3. **A self-administered positive control on that pin, with its output pasted into the
   record.** Mutate the real door in the direction the decision forbids (under C: add a
   spine-path argument to one tool schema), show the pin goes red, show the mutation was
   actually applied, revert, show it green. This is F's g3 reviewer's technique, run by the
   Commander. §3 states plainly what is lost by the author holding the knife.
4. Closeout `command` postcondition: the pin test runs green under `python -m pytest`
   (**not** `python3 -m pytest` — on this host that returns `No module named pytest` and
   reads as a false red).

**Dependency:** none. It is first because the order says the identity composition "is the
fact every later gate writes against," and because g2, g3 and g4a each write a *different
artifact* depending on which option lands (below).

**Constraints and traps carried down:**

- `identity-trade-is-recorded` — silence here is a gate failure, not a thin gate.
- `no-gen-mcp-config` — settled on evidence; do not re-litigate. **g1 also fixes its scope
  in writing for g3**: the tombstone forbids *per-dispatch* config generation *on identity
  grounds*. Installing one project-scope `.mcp.json` at install time is neither. Without
  that sentence written at g1, g3 either stalls on the tombstone or crosses it without
  noticing.
- **Do not author a test that pretends to observe the not-ours seam.** It is the single
  cheapest way to manufacture a false PASS at this gate, and DC3's PASS explicitly does not
  cover it.
- Never duplicate engine logic: `git diff` against `checklist_engine.py` was empty for all
  of F and stays empty.
- If the pin's premise is "no `SPINE_FILE`," it needs the positive control in the assertion
  path — F's g3 reviewer turned exactly the 2 tests with that premise red and left 10 green,
  which is what made DC3 credible.

**Why the dependencies below are real, not decorative** — this is the load-bearing case for
the mandated order:

- **g1 → g2.** Under option C, one server = one spine = one session, so "the run's episode"
  is unambiguous and resolvable from the module-level constants. Under option A the server
  no longer has *a* run; the capture must resolve an episode **per call**, and fail-loud
  acquires a new failure class (a call naming a spine that has no episode). g2's design
  changes shape, not just its wording.
- **g1 → g3.** The installed `.mcp.json`'s `env` block ships `SPINE_FILE`/`SPINE_SESSION`
  under C, and does not under A. g3 cannot author the installed config before g1 lands.
- **g1 → g4a.** Under C, the role spine instructions must state that an in-session
  Task-tool subagent uses the **CLI**. That makes `the-cli-door-stays` do real work rather
  than being a courtesy, and it is the concrete case where "if a subagent-dispatching role
  cannot safely use the door, then editing role spine instructions to default to it is the
  wrong edit" becomes an edit instruction.

---

### g2 — the door's own rejections reach the run's episode *(CREW GATE)*

**Closes:** done-criterion **4** — "the server's own rejections land in the run's episode
through `apply_episode_delta.py`, and say so loudly when they cannot."

**Kind:** crew gate. Code plus a control; not waivable.

**Close criteria and the exact evidence produced AT this gate:**

1. A test over the **recording path**: a door rejection that short-circuits before
   `run_engine()` reaches the run's episode through `apply_episode_delta.py` with
   `--store-root episodes`.
2. A test over the **loud-failure path**: when the capture cannot write, it says so on
   **every occurrence** — not once per run, not at exit. A test that only proves it says so
   once does not close this gate.
3. A **seeded rejection the instrument actually scores**, end to end. Without this, g4b's
   zero is uninterpretable.
4. A written decision, in the gate's result, on: per-call granularity vs. a summary at lease
   release; whether the **CLI arm** gets the same instrumentation; whether an
   immediately-corrected rejection weighs the same as an unresolved one; and **where** a
   door rejection lands in the `## Mechanical` bin.
5. **A written statement of the class this capture structurally cannot see.** See traps.

**Dependency on g1:** real and structural — see g1 above. The episode a rejection belongs to
is determined by whether identity is per-process or per-call.

**Constraints and traps carried down:**

- **The defect is narrower than the order's framing, and the narrow version is the real
  one.** Engine refusals arriving through the door are **already captured**:
  `run_engine()` calls `checklist_engine.main()` in-process, which increments `refusals`
  (`checklist_engine.py:3319-3321`), and `episode_capture.py:430-432` reads it into the
  Mechanical bin. **Do not rebuild that.** Only the four `_tool_error(...)` classes are
  mute: unknown tool name; unknown `action` on the four multiplexed tools; missing required
  argument (`_require`, 10 sites); and a client-side schema rejection.
- **The sharpest class is one a server-side capture cannot reach at all.** A client-side
  schema rejection never enters the server process. A capture that is claimed to cover "the
  door's rejections" while structurally blind to that class is the same defect as F's DC5
  server-log numerator — *a measure that cannot lose*. g2's deliverable must name this limit
  in its own words, or the gate closes on a claim wider than its evidence.
- `fail-loud-every-turn` (owner's words) — every occurrence.
- `episodes-are-records-not-rules` — write what was observed; nothing phrased as guidance
  for a future agent. That belongs in `docs/agents/*` and is the human's call
  (`ORCHESTRATOR_CONTEXT.md`, "The Retired Learning Playbook").
- `episodes/` is written **only** through `apply_episode_delta.py`, `--store-root episodes`
  on every invocation. The `## Mechanical` allowlist is **closed**
  (`docs/EPISODE_STORE.md` §4), so where a rejection lands is a store-contract decision, not
  a formatting one.
- **#543 is a dependency**: `apply_episode_delta.py` and `verify_episode_captured.py` were
  mutually unsatisfiable for a nested work-id until it landed. Confirm it is in the base
  before building on the write path.
- Windows: `encoding='utf-8', newline='\n'` explicitly on **every** write.
- Never pipe a command into `head`/`tail` and read the pipe's exit code — that is the
  pager's status. Redirect to a file and capture the command's own `$?`.
- Crew implementers are Sonnet (standing rule); dispatch only through
  `python scripts/run_crew.py`, never by hand.

---

### g3 — the installer ships and wires the door *(CREW GATE)*

**Closes:** done-criterion **3** — "`install_constellation.py` ships and wires `.mcp.json`,
so a fresh install gets the door."

**Kind:** crew gate. Code in a trap-laden file; not waivable.

**Close criteria and the exact evidence produced AT this gate:**

1. An installer test proving `.mcp.json` is written into a **target** root with paths that
   resolve **there** — the committed one uses paths relative to this repo, and a fresh
   install has neither the door nor the engine at that path.
2. The door script itself is bundled into the target (it is useless to write a config
   pointing at a script that was not installed).
3. Evidence that the `env` block matches g1's decision.
4. Whatever g2 added that a fresh install needs (a helper script, a new env var) is shipped
   — otherwise a fresh install gets a door whose capture is silently disabled, which
   violates `fail-loud-every-turn` at exactly the moment nobody is watching.
5. A measured statement of what hook wiring actually writes, if hook wiring is touched at
   all.

**Dependency on g2:** real. g2 may introduce a required script or an env var; if g3 does not
ship it, criterion 4 holds in this repo and fails in every fresh install.

**Constraints and traps carried down:**

- **The interpreter token.** The rewrite map stamps a resolved interpreter into every
  installed skill body. That path is now **hard-stopped** when no interpreter probes
  successfully (#540). **Do not reintroduce a fallback** to a member of the disproved
  candidate set.
- **`--wire-hooks` does not do what its name says.** It targets
  `.claude/skills/constellation-workbench/scripts/`, not `scripts/hooks/`, and wires only
  `PostToolUse`. If you touch hook wiring, **measure what it actually writes**.
- **Hook code is not fenced by git worktree isolation.** `CLAUDE_PROJECT_DIR` resolves once
  at session launch and is inherited unchanged by every subagent (#269), so a change to hook
  behavior cannot be validated from inside the worktree that contains it. Validate with a
  fresh process whose `CLAUDE_PROJECT_DIR` genuinely resolves to the worktree — **never** a
  fixture that hand-injects the value you are trying to prove the harness delivers.
- **Never write `settings.json` at user scope.**
- **Float to the Admiral**, do not decide: adding a `required_scripts` entry beyond what g3
  needs; changing `INTERPRETER_CANDIDATES` order; anything writing `settings.json` at user
  scope.
- The `no-gen-mcp-config` scope sentence from g1 rides in this gate's handoff. If g3's
  design ever drifts toward minting a config **per dispatch**, it has crossed the tombstone
  and must stop.
- **Carry down to g4a:** `install_constellation.py` **regenerates**
  `skills/<role>/references/global-*.md` at install time and silently overwrites it. Any
  doctrine edit must land in the canonical `skills/_shared/global-*.md`. g3 is where this
  fact is confirmed against the code, and it is the reason g3→g4a is a real dependency and
  not a queue position.
- Compact-format JSON templates are edited **surgically as raw text** — never round-tripped
  through `json.load`/`json.dump`, which reflows the file and destroys blame. Re-validate
  with `json.load` afterward.

---

### g4 — adoption and its acceptance measure *(CREW GATE — the merge this plan proposes)*

**Closes:** done-criteria **1** and **2** in one gate.

**Kind:** crew gate. Implementer performs the adoption edits and stages/executes the
acceptance run; reviewer verifies both.

**Close criteria and the exact evidence produced AT this gate:**

1. A test asserting **both** halves of criterion 1: the door's tools are named as the
   default path, **and** the CLI is still present and documented as the remaining fallback.
   A test asserting only the first half cannot detect the failure this gate is most likely
   to commit.
2. The driving agent's own `record.jsonl` from an **external dispatch**, scored by F's
   archived instrument (`evidence/g4-dc5/score_arm.py`), showing the agent reached `DONE`
   through the door alone.
3. The three adoption counts re-measured (all were zero at the wave boundary) as this run's
   own proof they moved.
4. The acceptance run's own friction recorded by g2's capture — reported as measured,
   including if it is zero.

**Dependency on g3:** the doctrine-regeneration fact above; the edits must land where the
installer will not overwrite them.

**Constraints and traps carried down:** see the g4a/g4b trap lists in §4, which apply
unchanged whether g4 is one gate or two.

---

## 2. Self-check against wave 1's defect

The order is explicit: wave 1's largest defect was "a plan that put a claim at g1 and its
evidence at g3," and merging gates is the easiest way to reproduce it. I ran every merge in
this plan against that shape.

- **g1 as a reasoning gate — does the claim outrun its evidence?** Only if the invariant pin
  is deferred. The obvious minimality saving here is to let g1 produce the decision document
  and let g2's crew write the pin test alongside its own code — one fewer thing at g1, and
  the pin lands in the same file g2 already touches. **That is verbatim the wave-1 defect:
  claim at g1, evidence at g2.** It is rejected on that ground alone. The pin is authored,
  run, mutated and pasted **at g1**, in the Commander's context. This is the specific
  temptation the order warned about, and it is the one this plan had to refuse.
- **The g4 merge — does it reproduce the wave-1 shape?** No, and I will not claim it does.
  It puts both claims and both bodies of evidence in the *same* gate, not in a later one.
  It has a different defect, which is fatal for a different reason (§3.2). Overstating it as
  the wave-1 shape would be the same move F confessed to — finding routes back to a
  conclusion.
- **g1 first — is it settled before anything is written against it?** Yes, and §g1 states
  three concrete ways g2, g3 and g4a each change shape under a different option. If those
  three dependencies were merely decorative, g1's placement would be ceremony. They are not.

---

## 3. Where minimality actually costs something

Two merges, two costs. One is acceptable. One is not.

### 3.1 Waiving the crew at g1 — cost stated, judged acceptable *with a substitute*

A five-crew-gate plan produces at g1 an `IMPLEMENTER_RESULT` and an independent
`REVIEW_RESULT`. Mine produces an attested decision record and a self-run control. Three
specific things are lost:

- **An independent challenge to the identity trade before four gates are built on it.**
  This is the largest single evidence loss in the plan. g1's decision is, in the order's own
  words, "the fact every later gate writes against." Under my plan no party other than the
  author reads it before it becomes load-bearing. F's credibility rested on four reviewer
  BLOCKs, all resolved on evidence, none overridden — and F's own retrospective line is that
  neither of the two decisive corrections came from itself.
- **An adversarial mutation control administered by someone who did not write the pin.**
  My self-run mutation proves the *mechanism* — the pin can go red, and the mutation
  demonstrably applied. It does not prove *independence*. The author choosing which
  mutation to apply is choosing which failure to demonstrate. F's g3 reviewer demonstrated
  red for **three distinct manipulations** with proof each applied; a self-control is that
  technique with the author holding the knife.
- **The `IMPLEMENTER_RESULT`/`REVIEW_RESULT` pair itself**, whose `Workflow Feedback`
  sections feed the run's lesson-candidate pool at the `feedback` step. A reasoning gate
  produces a thinner artifact into that pool.

**Why I judge this acceptable, and what replaces it.** An implementer/reviewer crew is a
poor instrument for challenging a *judgment*. A Sonnet reviewer handed a design trade with
no clean answer verifies that the document exists, is internally consistent, and matches the
handoff. It does not overturn the trade — it cannot, because the trade is a call about which
property to give up, and the crew has no standing to make it. Spending two dispatches to buy
a consistency check on a document is exactly what doctrine means by "shallower, not safer."

The right adversary for g1 is one tier up. `identity-trade-is-recorded` is graded
**settled/human**, and the order says plainly: *"Float to me and I answer and continue
you."* So this plan attaches a hard condition to the waiver:

> **g1's decision is floated to the Admiral for ratification before g2 opens.** The
> Commander does not proceed to g2 on its own authority over which property is given up.
> The float carries: the option taken, the property given up, the evidence each rejected
> option lost on, and the pin's mutation output.

That is a stronger challenge than a Sonnet reviewer, at the cost of one round trip instead
of two dispatches. It is the one place in this plan where minimality is paid for rather than
simply banked.

### 3.2 Merging g4a and g4b — cost stated, judged **not** acceptable

The merged g4 loses three things, and the second one is disqualifying.

- **A separate review verdict on criterion 1.** Merged, one `REVIEW_RESULT` covers two of
  the five "done" criteria. The order asks for a verdict per criterion. A BLOCK on the
  adoption edits and an APPROVE on the measurement cannot be expressed as one verdict.
- **The frozen tree the measurement needs.** `remeasure-never-reuse` is settled: no baseline
  is carried across a code change. In a merged gate, the implementer produces the adoption
  edits **and** measures against them, and the reviewer reads both afterward. **The
  reviewer's own BLOCK is a code change.** Any correction the reviewer wins — including the
  one this gate is most likely to need, an edit that quietly removed the CLI — voids the
  acceptance run and forces a full re-dispatch and re-measure. The merged gate's cheapest
  path to closing is therefore a review that finds nothing. That is a gate optimised to pass,
  which is the same structural sin as F's DC5 server-log numerator: *a measure that cannot
  lose is not a measure.* Split, g4a closes under review and the tree freezes; g4b then
  measures a reviewed, integrated tree and `remeasure-never-reuse` is satisfied by
  construction rather than by luck.
- **Undivided reviewer attention on the number.** DC5's flip from negative to pass came
  from a reviewer with nothing in front of it but the measurement, who noticed a shell `for`
  loop scoring six engine invocations as one. Put sixteen files of prose edits in the same
  handoff and that reviewer is now also the person checking whether `the-cli-door-stays` was
  honoured across three tiers of files. Both jobs get done; neither gets done the way the
  one that mattered was done.

There is also a fourth cost I want on the record because it argues *against* the instinct
that g4b's implementer is a formality. The implementer at g4b is not typing code — the
harness is archived and reused (`drive_via_mcp.py`, `mcp_client.py`,
`prove_headless_dispatch.py`, `score_arm.py`). What the implementer *is* is the separation
between the party holding a conclusion and the party producing the number. Collapsing g4b
into the Commander's context, or into a gate the Commander is also steering to a conclusion,
re-creates the precise condition F named in its own retrospective. The dispatch is the
control.

---

## 4. The recommended plan — converging to one

**I recommend against my own g4 merge.** The identity waiver at g1 survives; the g4 merge
does not. The plan I recommend is:

**Five gates. One reasoning, four crew. Twelve crew dispatches** (vs. the drafted plan's
fifteen), **plus one Admiral float**.

| Gate | Kind | Closes | Evidence produced AT that gate |
|---|---|---|---|
| **g1** identity trade | **reasoning** (waiver: decision over evidence the Commander already holds; no independent fact for a crew to find) | criterion 5 | `IDENTITY_TRADE.md` naming the property given up + the not-ours seam; an executable invariant pin in `tests/test_mcp_identity.py`; a self-run mutation control with pasted output; **floated to the Admiral before g2 opens** |
| **g2** friction capture | crew | criterion 4 | Recording-path test; loud-failure-every-occurrence test; a seeded rejection the instrument scores; the granularity/CLI-arm decisions; **a written statement of the class a server-side capture cannot see** |
| **g3** installer | crew | criterion 3 | Installer test: `.mcp.json` written into a target with paths that resolve there, door script bundled, `env` block matching g1, g2's new requirements shipped |
| **g4a** adoption edits | crew | criterion 1 | A test asserting **both** — door named default **and** CLI still present as documented fallback |
| **g4b** acceptance run | crew | criterion 2 | The driving agent's own `record.jsonl` from an external dispatch, scored by F's archived `score_arm.py`; the three adoption counts re-measured; the run's own friction recorded by g2's capture, zero reported as zero |

This differs from a five-crew-gate plan in exactly one place — g1 — and it pays for that
difference with an Admiral float rather than banking it. It differs from my own minimal
four-gate plan in exactly one place — the g4 split — and that difference is bought on
evidence, not on caution.

**g4a's traps** (unchanged from §1's merged form): `the-cli-door-stays` — an edit that
removes the CLI **fails** this gate; cite `skills/_shared/global-*.md`, **never**
`skills/<role>/references/global-*.md`, which the installer regenerates and silently
overwrites; compact-JSON templates edited surgically as raw text, re-validated with
`json.load`; the blast radius is three acting tiers (3 spine templates + 7 imperative fields
+ `commander-core.md`; 6 SKILL bodies; 3 authoring templates) and **the 4 incidental
narrative mentions in doctrine prose are left alone deliberately** — say so in the reviewer
handoff or the reviewer will BLOCK on them as misses; DC4's equivalence property (61 gates,
12 shipped templates, discovered by walking the tree) must stay green, and editing templates
moves that population; whatever g1 decided about the in-session Task-tool case is written
here.

**g4b's traps:** `count-from-the-call-record` — the numerator is the driving agent's own
record, **never** the server log; the acceptance run is an **external dispatch**, not an
in-session subagent, because `.mcp.json` is read at session launch and a live session does
not hot-reload it; `${VAR}` expansion keys `SPINE_FILE`/`SPINE_SESSION` from the dispatched
process's own environment; **read F's archived harness before writing a new one**;
`remeasure-never-reuse` — F's DC5 numbers are prior art for the instrument, never this run's
baseline; `zero-is-a-result` — report zero, do not manufacture friction, and do not read
zero as proof the capture works (that is what g2's seeded control is for); the batching
correction in `score_arm.py`'s docstring (one Bash `tool_use` ≠ one invocation attempt) is
load-bearing and both `invocation_attempts` and `tool_calls_carrying_them` are reported;
probe the **headless permission model** with a real file write, not `--version`, before
relying on a dispatched agent to do work; never read a pipe's exit code; `python -m pytest`;
**an UNMEASURED condition is not a measured negative and is never reported as one.**

---

## 5. Honest summary of this candidate

- The minimality latitude is real and it is worth taking **once**, at g1. Four of five gates
  produce code or a number, and doctrine's waiver does not reach them.
- The tempting second saving — letting g1 assert and g2 evidence — is verbatim the defect
  the order named. Refused.
- The third saving — merging g4 — looks clean and fails on a settled pre-ruling: it makes
  the acceptance measurement hostage to its own review, so the gate's cheapest close is a
  review that finds nothing.
- **The single most important thing my plan does not produce:** an independent challenge to
  the identity trade before four gates are built on it. I do not think a Sonnet
  implementer/reviewer pair is the right instrument for that challenge, which is why I take
  the waiver — but I do not pretend the loss is nil, and the Admiral float is the price, not
  a footnote.
