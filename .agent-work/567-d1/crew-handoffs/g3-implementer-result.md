# IMPLEMENTER_RESULT — g3-implement, door vocabulary in `specs/*.spine.toml`

**Return status: complete**

Work id `567-d1` · gate `g3-implement` · crew `constellation/567-d1/g3/implementer/attempt-1`
Worktree `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch `feat/567-d1-doctrine-sweep-guard` · parent `constellation/567-d1/lane-d1/commander-delegated`

Plan driven: `.agent-work/567-d1/crew-scratch/g3-implementer-attempt-1-74e194cfc852/IMPLEMENTER_PLAN.json`
(5 items, all complete, journal beside it). Session `constellation/567-d1-g3-implementer-attempt-1`.

---

## 1. What changed

Two files, `+81` lines, no deletions. `git diff --stat specs/`:

```
 specs/implementer.spine.toml | 39 +++++++++++++++++++++++++++++++++++++++
 specs/reviewer.spine.toml    | 42 ++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 81 insertions(+)
```

Nothing outside `specs/**` was edited. `git status --porcelain` at close carries only the two specs,
this crew's own `.agent-work/` records, and the Commander's own registry/gauge files, which were
already modified when I started.

### 1a. `specs/implementer.spine.toml`

**Before** — `m0-context`, whole gate. Zero mentions of the door, no `constraints` key:

```toml
[[gate]]
id    = "m0-context"
title = "Load baseline context"
imperative = """
Read your inherited global doctrine (this skill's references/global-crew.md and
references/global-everyone.md), then the project deltas if present:
docs/agents/CREW_CONTEXT.md, docs/agents/GLOSSARY.md, plus the handoff and the
relevant packet. Verify the handoff is complete (task, intent, scope,
exclusions, required evidence, test mode, stop conditions); if incomplete,
block and return. Attest c1.
"""
```

**After** — the original text is untouched; two paragraphs are appended to the imperative and a
`constraints` array is added. Added text, verbatim:

```
THE DOOR IS HOW YOU DRIVE THIS PLAN, and these gates are the plan -- there is
nothing else to drive. A role dispatched with a spine of its own starts with
SPINE_FILE and SPINE_SESSION already in its environment, so the door resolves
to that spine by itself and no session id is passed anywhere: spine_status
reads where you are, spine_start opens a gate, spine_advance closes one,
spine_evidence attests or attaches, spine_lease claims and gives back the
working lease, spine_capture appends an item or flags a triage candidate,
spine_halt blocks, and spine_amend re-plans under a named authority. A role
dispatched WITHOUT a spine of its own holds no lease, and an unbound door binds
one spine and then drives it identically -- the identity comes from that
spine's own work id, never from a string you supply.

WHAT YOU MAY NOT DO IS DRIVE A SECOND CHECKLIST FROM THIS PROCESS, and the
reason is a measured refusal rather than an oversight. One door drives one
spine at a time (`decision:one-spine-per-process-stands`). Measured in a fresh
process: with your own lease held, binding a second checklist is REFUSED --
"one door drives one spine at a time ... release it first" -- and the escape
that refusal names is barred for you, because the archive gate requires the
lease to cover every journaled action, so releasing it to reach a second
checklist fails your own closeout. Read the two halves together and the rule is
one rule, not a limitation: the door reaches the spine you hold a lease on, and
you hold a lease on exactly one. So do not author a plan of your own beside
this one. If these gates are wrong for the work, that is what spine_amend and
spine_halt are for.
```

```toml
constraints = [
  "The door is this role's whole interface to its spine -- no session id is passed to it, because this process is already bound to exactly one spine",
  "Author no second checklist beside these gates: one door drives one spine at a time, and while you hold your own lease the door refuses to bind another -- measured, not assumed",
]
```

Plus a header comment (quoted under §2, because it is the schema decision's record at the site).

### 1b. `specs/reviewer.spine.toml`

**Before** — `r0-context`, whole gate. Zero mentions of the door, no `constraints` key:

```toml
[[gate]]
id    = "r0-context"
title = "Load baseline context"
imperative = """
Read your inherited global doctrine (this skill's references/global-crew.md and
references/global-everyone.md), then the project deltas if present:
docs/agents/CREW_CONTEXT.md, docs/agents/GLOSSARY.md, plus the handoff, the
diff, and the relevant packet. Record pass when loaded.
"""
```

**After** — same shape, in the **survey dialect**. Added text, verbatim:

```
THE DOOR IS HOW YOU DRIVE THIS SURVEY, and these items are the survey -- there
is nothing else to drive. A reviewer dispatched with a spine of its own starts
with SPINE_FILE and SPINE_SESSION already in its environment, so the door
resolves to that spine by itself and no session id is passed anywhere. The
survey dialect is not the gated one: spine_status reads where you are,
spine_survey_result records each item pass or fail AND consolidates the verdict
at the end -- spine_advance is the gated plan's closing verb and is not yours --
while spine_evidence, spine_lease, spine_capture, spine_halt and spine_amend
are shared with every other plan. A reviewer dispatched WITHOUT a spine of its
own holds no lease, and an unbound door binds one spine and then drives it
identically -- the identity comes from that spine's own work id, never from a
string you supply.

WHAT YOU MAY NOT DO IS DRIVE A SECOND CHECKLIST FROM THIS PROCESS, and the
reason is a measured refusal rather than an oversight. One door drives one
spine at a time (`decision:one-spine-per-process-stands`). Measured in a fresh
process: with your own lease held, binding a second checklist is REFUSED --
"one door drives one spine at a time ... release it first" -- and the escape
that refusal names is barred for you, because the archive gate requires the
lease to cover every journaled action, so releasing it to reach a second
checklist fails your own closeout. Read the two halves together and the rule is
one rule, not a limitation: the door reaches the spine you hold a lease on, and
you hold a lease on exactly one. So do not author a survey of your own beside
this one. If these items are wrong for the diff in front of you, that is what
spine_amend and spine_halt are for, and r6-fowler's own REPAIR PATH below is
the worked example.
```

```toml
constraints = [
  "The door is this role's whole interface to its spine -- no session id is passed to it, because this process is already bound to exactly one spine",
  "Author no second survey beside these items: one door drives one spine at a time, and while you hold your own lease the door refuses to bind another -- measured, not assumed",
  "A survey item closes through spine_survey_result, never spine_advance -- the engine refuses the gated verb here",
]
```

**Why the reviewer text is not a copy.** A survey item closes through `spine_survey_result`, and the
engine refuses the gated verb outright: `checklist_engine.py:2621`, `advance is for gated
checklists; use record`. Handing a reviewer `spine_advance` would have handed it a verb the engine
rejects. The tool listing agrees (`mcp_spine_server.py:119`: `spine_survey_result -- record |
consolidate (survey plans only)`). The third constraint states that refusal directly.

---

## 2. The schema decision: prose only, no new keys — and the reason is the consumer

**Chosen: prose in existing carried fields.** Decided from what `scripts/generate_spine.py` does,
not from the plan's leaning.

`_compile_gate` (generate_spine.py:669-684) builds every compiled task from a **fixed field list** —
`id`, `title`, `imperative`, `preconditions`, `postconditions`, `constraints`, `directives`,
`child_checklist`, `status`, `status_detail`, `result`, `finding`, `evidence`, `rework_count` — and
`compile_spec` (:704-713) builds the top level the same way. So:

- **A new key would be dropped silently.** It is never copied into the compiled spine, and
  `spec_shape_faults` has no unknown-key fault, so nothing refuses it. The spec author would see the
  key in the file; the dispatched role would never see it. That is strictly worse than prose.
- **A new key would need a consumer that does not exist.** Writing one means editing
  `generate_spine.py` — outside `specs/**`, and a stop condition in the handoff.
- **TOML comments are dropped too**, so doctrine in a comment is doctrine nobody is handed.

Measured, not asserted: after the edit, `grep -c "Doctrine put anywhere else"` on both compiled
spines returns **0** (the comment does not survive), while `one door drives one spine` is present in
the compiled `m0-context.imperative` and `r0-context.imperative` and both gates carry their new
`constraints` (2 and 3 entries). The five fields an agent actually reads are `title`, `imperative`,
`constraints`, a condition `statement`, and a qualitative `because` (`compile_condition` folds
`because` into the statement) — so `imperative` + `constraints` is where this had to go.

That reasoning is recorded **in both spec files** as a header comment, so the next author does not
re-derive it:

```
# Door vocabulary lives in `imperative` and `constraints`, and this comment does
# not. That is not a style choice: generate_spine._compile_gate builds every
# compiled task from a FIXED field list, and compile_spec builds the top level
# the same way, so a new spec key reaches no reader and spec_shape_faults has no
# unknown-key fault to refuse it with -- it would be dropped silently. Comments
# are dropped too. Authored text an agent actually reads is `title`,
# `imperative`, `constraints`, a condition `statement`, and a qualitative
# `because` (compile_condition folds it into the statement). Doctrine put
# anywhere else in this file is doctrine nobody is handed.
```

**No test is owed.** No new runtime behaviour and no new key. The guard is the check and it already
walks `specs/**/*.toml`; `generate_spine.py --check-only` is the second one, and both are run below.

---

## 3. Evidence

### 3a. The guard reports no `specs/` address

Run after both edits (`python3 -m pytest tests/test_cli_retirement_guard.py -q`):

```
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_cli_fallback_clause_reaches_an_agent
FAILED tests/test_cli_retirement_guard.py::TestNoSecondPathReachesAnAgent::test_no_engine_invocation_reaches_an_agent
2 failed, 17 passed in 0.09s

$ grep -oE 'specs/[A-Za-z0-9_./-]+' /tmp/g3-m2.log | sort -u
(nothing)
```

The two failures are **byte-identical to the baseline I measured before touching anything**, and
their sites are `skills/workbench/references/checklist-engine.md` and `skills/workbench/SKILL.md` —
lane D2's fenced files, which the handoff names as expected and which `g5-final` re-checks after the
rebase. Both of my gate postconditions embedded this guard run as a `command` check, so the engine
re-ran and re-verified it at each `advance`, not just me at a terminal.

### 3b. Both specs still compile clean through all five generator layers

```
$ python3 scripts/generate_spine.py specs/implementer.spine.toml --out /tmp/g3-impl.json --check-only
check-only: specs/implementer.spine.toml would compile clean
$ python3 scripts/generate_spine.py specs/reviewer.spine.toml --out /tmp/g3-rev.json --check-only
check-only: specs/reviewer.spine.toml would compile clean
$ python3 scripts/generate_spine.py specs/implementer.spine.toml --out /tmp/g3-impl.json && \
  python3 scripts/generate_spine.py specs/reviewer.spine.toml --out /tmp/g3-rev.json
wrote /tmp/g3-impl.json
wrote /tmp/g3-rev.json
```

Both **also compiled clean at baseline**, measured before the edit, so this is a real before/after
and not a vacuous pass. Compiled output went to `/tmp`, never into the repo. TOML parse is asserted
separately in both gate checks (`tomllib.load` on each file).

Two shape rules the new prose had to respect, and does:

- `generate_spine._DISPATCH_MARKERS` — an imperative containing `run_crew.py`,
  `constellation-implementer` or `constellation-reviewer` triggers `spec-dispatch-undeclared` at
  spec-shape time. None of the three appears in either new imperative.
- `spec-all-qualitative-postconditions` — untouched; I added no postconditions.

### 3c. The guard's own patterns, against the new prose

No `<engine>` token; no `CLI`-anything in any spelling; no `checklist_engine.py` reference of any
shape; and no placeholder followed on the same line by an engine verb — the new text contains **no
bracket, brace, `$` or `%` placeholder at all**, which is the cheapest way to stay clear of
`ENGINE_STANDIN_COMMAND_RE` rather than relying on which word follows. The engine's 18 verbs were
read from `_engine_verbs()` before writing, not assumed.

---

## 4. The `config_ref` finding — recorded, deliberately not fixed

**Measured.** `docs/agents/` contains exactly `CREW_CONTEXT.md`, `GLOSSARY.md`,
`ORCHESTRATOR_CONTEXT.md`. `find . -name engine-config.json` returns **nothing anywhere in the
repo**. Both specs set `config_ref = "docs/agents/engine-config.json"`. The engine degrades
silently: `checklist_engine.load_config` (:407-422) returns `{}` when no candidate path exists, so
the plan runs on defaults (`DEFAULT_REWORK_CAP = 3`). `generate_spine.spec_shape_faults` only reads
`config_ref` **if the file exists** (:414-427), so nothing refuses the dangling reference either.

**Two things the existing triage candidate did not carry, and they change the disposition:**

1. **The absence is ruled deliberate.** `docs/CHECKLIST_SCHEMA.md:35-38`: "A *missing* path falls
   through to `{}` and is harmless, **which is why every shipped template's nonexistent
   `docs/agents/engine-config.json` is fine**." Creating the file would convert a documented no-op
   into a live crash surface (`load_config` calls `json.loads` on any `config_ref` that exists, and
   `validate_spine.py` carries no fault for the crashing case).
2. **For the survey half there is a pinned precedent going the other way.**
   `skills/explorer/templates/CYCLE.template.json` — also a survey — drops the key entirely, and
   `tests/test_explorer_templates.py:242-247` pins the reason: "a survey never consults
   `rework_cap` … the key is dropped rather than pointed at a file a fresh install won't have."
   `specs/reviewer.spine.toml` is `type = "survey"` and still carries it, so two shipped survey
   artifacts state opposite conventions. Nothing pins the specs' side —
   `tests/test_generate_spine.py:1195` pins only `parent == "<parent>"`.

**Not fixed, and why.** The handoff's bar was "free and obviously right". The gated half is a
rework-cap defaults decision for a human, and `CHECKLIST_SCHEMA.md` blesses the current state in
writing — changing it inside a doctrine-vocabulary gate would be an unrequested change made against
a documented ruling. The survey half is free but is one leg of a two-leg decision, and splitting it
would leave the two specs inconsistent with each other.

Staged: the existing `.agent-work/567-d1/triage-candidates/engine-config-json-absent.md` was
**updated in place** (a g3 addendum) rather than duplicated. Also flagged through the door as `tc2`
on my own plan. **No issue filed.**

---

## 5. Two findings the Commander needs before closing this gate

### 5a. The gate's own closing check cannot pass, at baseline, for a reason unrelated to my work

The handoff's closing check ends:

```sh
! grep -oE '(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+' /tmp/g3-guard.log | grep -qv '^skills/workbench/'
```

The guard's failure message embeds its own census — `(101 under skills/, 2 under specs/, 113 under
.agent-work/templates/)` — and `.agent-work/templates/` **matches that address pattern** while not
starting with `skills/workbench/`. Measured on the **unmodified tree, before my first edit**:

```
$ grep -oE '(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+' /tmp/g3-guard.log | grep -v '^skills/workbench/'
.agent-work/templates/
.agent-work/templates/
```

Two hits (one per failing test), grep exits 0, the negation is false. The check therefore only
passes once the guard is **entirely** green — i.e. after lane D2's fenced files are swept, which the
handoff itself assigns to `g5-final`, not here.

`specs/` is clean either way: the handoff's own **Verification Commands** section uses
`grep -oE 'specs/[A-Za-z0-9_./-]+'`, which prints nothing, because `specs/` in the census is
followed by a comma and the pattern needs at least one path character. That narrower form is the
one that reflects this gate's actual close criteria.

**Commander decision, not mine** — `execute.json` is outside my scope and the guard is fenced.
Flagged through the door as `tc1`.

### 5b. The handoff's premise about second checklists is right about the rule and wrong about the crews

The handoff states that a role driving a second checklist "cannot use the door", and that "every
crew this lane dispatched" drove its plan under a hand-supplied CLI session id. The rule is correct.
The claim about the crews is not, and it matters because the doctrine I was asked to write is
downstream of it.

**Measured first-hand this run.** My own dispatch has `spine: null` in `crew-runs.json` and **no
`SPINE_FILE`/`SPINE_SESSION`** in its environment (only `SPINE_PARENT`). So:

```
spine_status            -> REFUSED: no spine is bound to this door ...
spine_bind <my plan>    -> {"SPINE_SESSION": "constellation/567-d1-g3-implementer-attempt-1",
                            "work_id": "567-d1-g3-implementer-attempt-1", "already_bound": false}
spine_lease claim       -> claimed lease constellation/567-d1-g3-implementer-attempt-1 -> active
```

**This entire plan was driven through the door** — `spine_bind`, `spine_lease`, `spine_start`,
`spine_evidence`, `spine_advance`, `spine_capture` — with no CLI invocation at any point. The
session identity was **derived from the plan's own `work_id`**; I supplied no session string.

Corroborating: the g2 implementer's scratch directory carries `mcp_calls.jsonl`,
`mcp_server_started` ("started for …/IMPLEMENTER_PLAN.json") and three `mcp_amend_delta_*.json`
files — door telemetry written beside a bound spine — so that crew drove its own plan through the
door too.

**What survives, and what the specs now say.** The refusal is real and I did not soften it: it is
conditioned on **holding your own lease**, which is exactly the state of a role dispatched *with* a
spine. What is not true is that a dispatched crew has no door path to its own plan — an unbound
process binds one spine and drives it identically. Both specs state it that way, which is why the
vocabulary can be honest without either promising a path that does not exist or leaving a reader
stranded, and without naming a command line.

This also bears on the epic's premise: notes-1.md §M1 concluded the door "provably cannot" reach the
three second-checklist sites and that the CLI is "the **only** path" for them. That holds for a
process already holding a lease; it does not hold for the dispatched-crew case, which is the case
those three sites are mostly in. **Not mine to act on** — it is a `settled/human`-adjacent finding
and `skills/**` is fenced from me — but the Commander should float it before `g5-final` locks the
wording.

---

## 6. Close criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Both specs name the door | met — `spine_*` vocabulary in both `imperative`s and `constraints` |
| 2 | Both state the second-checklist truth | met — the refusal, its verbatim text, and the barred escape |
| 3 | Guard reports no violation at any `specs/` address | met — §3a, re-verified by the engine at each advance |
| 4 | Both files still parse as TOML | met — `tomllib.load` in both gate checks, plus a clean compile |
| 5 | Schema question settled and reasoned | met — §2, prose only, reason from `_compile_gate` |
| 6 | Dangling `config_ref` recorded with evidence | met — §4, candidate updated, `tc2` flagged |

Constraints honoured: no door path promised that the measurement does not show; the new prose does
not trip the guard; nothing promoted into `docs/agents/*`; **no issue filed**; nothing edited
outside `specs/**`. No stop condition was hit — the vocabulary never needed to show a command line.

---

## 7. Map Impact

No architecture map exists (`map_orient` → `DEGRADED-UNPARSEABLE`), so this is a note for whoever
builds one, in the handoff's own anchor vocabulary:

- `specs/implementer.spine.toml`, `specs/reviewer.spine.toml` — now the corpus's statement of **what
  the door is for a role**, and the only files that state the one-spine-per-process rule as role
  doctrine rather than as an implementation comment. A future map entry for either should reference
  `scripts/mcp_spine_server.py::_rebind_refusal` and `decision:one-spine-per-process-stands`.
- `scripts/generate_spine.py::_compile_gate` — the **carried-field list is a doctrine surface**, not
  just a compiler detail: it decides which authored text can ever reach an agent. Anything that adds
  a spec key must edit it, and until then a new key is a silent drop.
- No structural, capability or dependency change. Two prose additions and one comment.

---

## 8. Workflow Feedback

**What helped.**

- The handoff naming `scripts/generate_spine.py` as "read it before adding a key" was the single
  most useful line in it. The keys-vs-prose question answered itself in ten minutes from
  `_compile_gate`'s field list, and the answer came with its own evidence (the comment is measurably
  absent from the compiled output).
- Stating the guard's three forbidden shapes **in the handoff**, rather than making me derive them
  from the test, meant I wrote clean prose on the first pass. Zero guard iterations.
- The explicit warning not to run the whole suite (`test_gauge_chain_writer_to_trip.py:604`
  snapshots `.agent-work/`) saved me from a failure a sibling crew nearly misreported. Naming both
  the file and the near-miss is what made it land.
- The POSIX/`dash` warning about `set -o pipefail`. I wrote all four of my own `command` checks in
  POSIX form and none of them tripped.

**What got in the way.**

- **The handoff's premise about crews was wrong in a way that pointed the doctrine at the wrong
  rule** (§5b). Had I written it as handed — "a role driving a second checklist cannot use the
  door" — the two specs would tell every dispatched crew something false about its own situation,
  since a dispatched crew with `spine: null` binds and drives through the door fine. The evidence
  was already in the tree (`mcp_calls.jsonl` in the g2 crew's scratch directory) and one
  `spine_bind` call settled it. **Ask a crew to verify the measurement its doctrine restates**, not
  just to restate it.
- **The gate's own closing check is red at baseline** (§5a) and I could only find that by running it
  before I started. A handoff that ships a closing check should say whether it was run on the
  unmodified tree; this one had been reasoned about but not executed, and its `specs/`-only sibling
  three sections earlier is clean, so the two commands in the same document disagree.
- **The crew skill's opening instruction is wrong for a `spine: null` dispatch.** It says a spine is
  bound for me and `spine_status` is my first call; `spine_status` refused, because nothing was
  bound. The refusal text is excellent and told me exactly what to do, so this cost one call — but
  the skill states as fact something that is false for this dispatch mode, and the recorded
  precedent is that crews resolve it by driving the **parent's** spine, which would have advanced my
  Commander's `execute` gate. The durable fix is for the skill to branch on whether `SPINE_FILE` is
  set, which is a one-line check.

**My own mistakes.**

- I read the handoff's "every crew this lane dispatched did the same" as settled and nearly wrote
  the specs to match. What caught it was noticing `mcp_calls.jsonl` while looking for an unrelated
  naming convention — luck, not method. The method that should have caught it is the one I then
  used: bind the door myself and see.
- My first framing of the second-checklist paragraph was an apology ("the door unfortunately cannot
  …"). It read as a defect report about the door, which is the opposite of the epic's thesis. The
  version that shipped states one rule with two consequences. Same facts, and the handoff was right
  to flag the tone risk explicitly.
- I nearly fixed the `config_ref` on the reviewer spec because it is inside my scope and
  behaviourally free, before finding `CHECKLIST_SCHEMA.md`'s ruling that the absence is deliberate.
  "In scope and free" is not the same as "obviously right", and the handoff's phrasing was the thing
  that made me go look for the ruling.

---

## 9. Stop-hook refusal, recorded

After my plan reached `DONE` and I released my lease, the Stop hook fired twice with
`SPINE MID-FLIGHT: gate execute is still open`, instructing me to reload the **commander** skill,
rewrite `.agent-work/567-d1/STATE_NOTE.md`, and drive `execute.json` gate by gate.

**Refused.** That is my parent's spine, not mine.

Measured at the moment of refusal:

| | |
|---|---|
| My plan (`…/g3-implementer-attempt-1-74e194cfc852/IMPLEMENTER_PLAN.json`) | all 5 items `complete`, `lease: null` — terminal, released |
| `.agent-work/567-d1/execute.json` | `g3-implement` is `in-progress` — **my own gate**, held open by the Commander pending this artifact |
| Engine lease | `constellation/567-d1/lane-d1/commander-delegated`, active, heartbeat `2026-08-17T17:59:18` — the Commander is alive and holding it |

The hook is keyed on the **spine's** mid-flight state, not on the running agent's identity, so it
fires at a crew whose own work is finished and whose lease is already gone. Obeying it means
advancing my parent's `execute` gate on its behalf, or force-taking a live lease it holds.

**Its two sanctioned exits do not fit either.** `spine_halt block` and `waive` both write to a spine.
My door is bound to my own completed plan, so `block` would mark a finished gate blocked and enter
false state; pointed at the parent instead, it would write a blocker into a run that is not blocked —
the Commander is waiting for exactly the artifact this file is. The sanctioned honest stop is itself
the destructive act, so the honest action is to refuse and record it here.

**Nothing is abandoned.** `g3-implement` is `in-progress` precisely because my crew is what fills it;
it closes when the Commander verifies this result. This is the fourth run in this repo to hit the
same misfit. The durable fix is a **lease-ownership check in the hook** — fire only when the running
session is the one holding the lease — not more prose in the crew skills.
