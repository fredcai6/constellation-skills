# REVIEW_RESULT — issue #308, gate `g5-review`

**Verdict: ACCEPT (engine verdict: APPROVE).**
**Blockers: 0. Observations: 3. Triage candidates: 4.**

Change under review: commit `e33b933` — *feat(#308): cut live agents off from the lessons bank (g5 implement)*.
Survey driven through the engine at `.agent-work/issue-308/g5-review/review.json` (13 checks, all
recorded pass). Fowler pass at `.agent-work/issue-308/g5-review/fowler-pass.json`.

Everything below was reproduced by me. Where I report a count, the command that produced it is quoted.

---

## 1. The load-bearing result: my own enumeration, by a different route

The handoff told me to assume the acceptance guard is under-inclusive until proven otherwise, because
its own history includes going green while three live intake sites survived.

**My enumeration: 34 files.**

```bash
git grep -lIiE "lessons|playbook|Active section" -- \
  skills/ docs/agents/ scripts/ README.md CLAUDE.md '*.md' \
  ':!.agent-work' ':!episodes' ':!docs/superpowers' ':!notes-*.md' ':!tests' | sort | wc -l
# -> 34
```

**The guard's enumeration: 10 files.**

```bash
python .agent-work/issue-308/checks/lesson_intake_is_cut.py
# enumerated 10 files under skills/ referencing the lessons bank
#   NOTE: skills/charter/templates/AGENT_GUIDE.template.md references the bank and is on neither list
# PASS: no live-agent artifact instructs reading the lessons bank
# exit 0
```

My route differs on all three axes the guard could be wrong about: **semantic keys** (I never search for
the string `LESSONS.md`), **wider scope** (`docs/`, `scripts/`, repo root — not just `skills/`), and **no
allowlist short-circuit** (I read every hit).

I read the lessons-relevant lines of all 34 files and classified each.
**Result: zero surviving live-agent read-intake sites.** Every remaining reference is writer-side
(`apply_lessons_delta.py` invocations, the `verify_lessons_applied.py` gate, the `deny_globs` entry),
auditor-side (the `lessons-auditor` skill and its templates — the sanctioned drain), or descriptive
(`fleet-doctrine.md` saying where fleet lore does *not* live).

Three corroborating nulls, each a command I ran:

| probe | command | result |
|---|---|---|
| the phrase is gone from the live corpus | `git grep -nIi "Active section" -- skills/ docs/ scripts/ README.md SKILL_INDEX.md CLAUDE.md` | **no output** |
| the doctrine bundled into *every* skill is clean | `git grep -nIi "lessons" -- skills/_shared/` | **no output** |
| no hook injects a digest behind the spine's back | `grep -rniE "lessons" scripts/hooks/` | **no output** |

And the mechanical declaration is genuinely gone corpus-wide, not just from the one file:

```bash
git grep -n '"root": "durable"' -- skills/     # -> no output (zero shipped durable declarations)
```

### The guard's green *could* have gone red — but only in one of four directions

Four mutants, each appended to a real file, guard re-run, then the file restored **byte-exact**
(sha256 re-checked after every restore; `git status --porcelain -- skills/ docs/ scripts/ tests/`
is empty).

| # | mutation | guard exit | reading |
|---|---|---|---|
| **M1** | read sentence into `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` | **1** | **RED — the guard is not vacuous** |
| **M2** | same sentence into `docs/agents/CREW_CONTEXT.md` (live doctrine, outside `skills/`) | 0 | GREEN — **blind** |
| **M3** | same sentence into the allowlisted `skills/lessons-auditor/SKILL.md` | 0 | GREEN — **blind** |
| **M4** | `"read the Active entries of the curated lessons playbook under .agent-work/"` into `skills/commander-delegated/SKILL.md` | 0 | GREEN — **blind** |

M1 is what licenses the green: a real read-intake site added to an in-scope, non-allowlisted file is
caught. M2/M3/M4 bound what the green means. The mechanisms:

- **M2** — `git grep ... -- skills/` scopes the enumeration to `skills/` only.
- **M3** — `if f in ALLOWLIST: continue` runs *before* any `READ_MARKER` is evaluated, so an allowlisted
  file is exempt from every marker, not just from its one known reference.
- **M4** — the enumeration key is the literal `LESSONS.md`, so a file that describes the bank without
  naming it is never enumerated in the first place.

**This is guard debt, not a defect in the change.** I searched all three blind spots by hand and found
nothing living in them. Filed as triage candidate `tc1`.

---

## 2. The three hunted classes

### Class 1 — an intake site the enumeration missed: **searched for, NOT FOUND**
Covered above. 34 files enumerated by an independent route, all read, zero survivors. The three specific
blind spots I proved the guard has were each swept manually and each was clean.

### Class 2 — a template left syntactically valid but semantically broken: **searched for, NOT FOUND** (one fenced follow-on)
I read all six edited prose sites end to end, plus their surrounding paragraphs, plus **every** pre- and
postcondition on the two edited spine steps — not just the JSON parse.

- `COMMANDER_SPINE` `context` **c1** (*"orchestrator context, glossary, engine config loaded; current map
  read…"*) names no lessons: it was already lessons-free, so there is no c1-promises-what-the-imperative-
  no-longer-does break. **c2** is the map-orientation contract, untouched.
- `ADMIRAL_SPINE` `latitude` **c1/c2** (*latitude contract written / confirmed*) name no lessons. The
  trailing `if present` now correctly attaches to `ORCHESTRATOR_CONTEXT.md`, which is a true statement.
- `AGENT_GUIDE.template.md:75` reads as a complete sentence pair and now states the *positive* rule —
  *"a staging bank an audit drains, not planning input for a live run"* — rather than just deleting the
  old one.
- Both edited JSON templates `json.load` clean and are un-reflowed (5 changed lines across both).

No dangling conjunction, no excised object, no orphaned postcondition.

**One follow-on, explicitly fenced by the handoff, so not a defect of this gate.** The `COMMANDER_SPINE`
**`feedback`** imperative — which the handoff named as writer-side and off-limits — still carries language
that presupposed the read this gate removed:

> *"the playbook holds open problems **you are carrying forward**"* … *"a lesson goes in the bank (an add)
> ONLY because **it needs to be re-observed** to be understood, and every add must carry a `bank_reason`
> saying **what re-observation will clarify**"* … and the `confirm`/`disconfirm` ops.

The deleted context sentence was the other half of that mechanism: *"note any lesson this run's evidence
contradicts **(it becomes a disconfirm op at the feedback step)**."* With the read cut, no live agent
re-observes a banked lesson; only the auditor drains it. Reachable and editable, but out of this gate's
fenced scope → triage candidate `tc2`.

### Class 3 — platform-invariant guidance destroyed as collateral: **searched for, NOT FOUND**

| site | before → after | verdict |
|---|---|---|
| `skills/admiral/SKILL.md:61` | *"The project's lessons inbox (`.agent-work/LESSONS.md` Active section) **and platform invariants** ride in every launch order's inherited-context block."* → *"The project's **platform invariants** ride in every launch order's inherited-context block."* | complete sentence, same imperative force, invariants half intact |
| `LAUNCH_ORDER.template.md:57` | *"`<Active lessons from .agent-work/LESSONS.md relevant to this mission; platform/technical invariants from the project playbook (encodings, shell quirks, crew-launch rules)>`"* → *"`<The platform/technical invariants from the project playbook (encodings, shell quirks, crew-launch rules) relevant to this mission>`"* | the parenthetical enumeration — the load-bearing part — is **byte-identical**; *"relevant to this mission"* was carried over rather than dropped with the lessons clause |

**Charter-lite carrier untouched — proved, not asserted:**

```bash
git diff HEAD~1 HEAD -- skills/admiral/templates/LAUNCH_ORDER.template.md | grep -E "^[+-].*Charter-lite" | wc -l
# -> 0     (it appears in the diff only as an unchanged context line)
```

I also confirmed the neighbouring fleet-doctrine bullet (`admiral/SKILL.md:60`) kept its full
platform-invariant payload — the three kill vectors, watcher-sleep, detach + state-note-first, the
recovery drill, and the `execute` p2 precondition. Its only `LESSONS.md` clause is a *staging/write*
instruction, not a read.

---

## 3. The two things I had to satisfy myself about by running code

### The writer is intact — and still works

**By content, not by count** (all three named survivors present in `COMMANDER_SPINE.template.json`):

1. `apply_lessons_delta.py .agent-work/<work-id>/lessons-delta.json --file .agent-work/LESSONS.md`
   **and** `apply_lessons_delta.py --ripe --file .agent-work/LESSONS.md` — both in the `feedback` imperative
2. `verify_lessons_applied.py --file .agent-work/LESSONS.md` — `feedback` c2's command check
3. `.agent-work/LESSONS.md` in the `archive` c4 `git-change-policy` `deny_globs`

**Count correction, and it is exactly why the handoff said *verify by content*:**

```bash
git show HEAD~1:skills/commander/templates/COMMANDER_SPINE.template.json | grep -o "\.agent-work/LESSONS\.md" | wc -l   # -> 6
grep -o "\.agent-work/LESSONS\.md" skills/commander/templates/COMMANDER_SPINE.template.json | wc -l                     # -> 4
```

The handoff said five-minus-two-equals-three. It is **six minus two equals four** — the `feedback`
imperative invokes `apply_lessons_delta.py` twice. The two that went are exactly the read path
(the `context` imperative and the `context_refs` entry), confirmed by diffing the occurrence line
numbers between `HEAD~1` and `HEAD`.

**Driven end to end on a scratch copy** (`…/scratchpad/w/LESSONS.md`, real bank never touched):

```
$ python scripts/apply_lessons_delta.py <scratch>/delta.json --file <scratch>/LESSONS.md
added lesson:reviewer-writer-probe
tick -> run 41
playbook: 1 active (run 41)                                         exit 0
$ python scripts/apply_lessons_delta.py --ripe --file <scratch>/LESSONS.md          exit 0
$ python scripts/verify_lessons_applied.py --file <scratch>/LESSONS.md
lessons gate: clear — no ripe lesson awaiting apply-or-defer         exit 0
$ git status --porcelain -- .agent-work/LESSONS.md                   (empty — real bank untouched)
```

The entry landed with its `scope` / `task-class` / `statement` / `grounding` / `bank-reason` fields and
`run-tick` advanced `40 -> 41`. The writer also **refused** two malformed deltas before that (missing
`work_id`; missing `statement`), so its validation is live rather than bypassed.

### The reworked tests can still go red — established by construction

Three mutants, each restored byte-exact.

| # | mutation to production code | result |
|---|---|---|
| baseline | — | `3 passed in 0.75s` |
| **MUT-A** | `from agent_work_root import durable_root` → `import durable_agent_work as durable_root` — **the exact silent double-nesting trap these tests exist for** | **`3 failed in 0.91s`** |
| **MUT-B** | `"durable": durable_root(repo)` → `durable_root(Path(base_dir) if base_dir else repo)` — the other documented trap (resolve from the checklist dir, not the repo root) | **`3 failed in 0.78s`** |
| **MUT-C** | re-add `{"root":"durable","path":".agent-work/LESSONS.md"}` to `context_refs` | **`2 failed, 4 passed`** (baseline `6 passed, 5 subtests passed`) |

All three durable-root tests — **including the one reworked onto the synthetic fixture** — kill MUT-A and
MUT-B. The rework did not hollow the guard: the synthetic declaration exercises the same trap the shipped
one did, because the trap is a property of `resolve_roots`, not of which file is declared. MUT-C shows the
new "the corpus ships zero `durable` declarations" assertion makes a re-added declaration *visible* rather
than silently changing what the test exercises.

---

## 4. Counts I observed myself

```
$ python -m pytest -q
1621 passed, 2 skipped, 541 subtests passed in 416.15s (0:06:56)
```

Run with `python`, never `py`. Zero failures. The implementer's claimed total of 1621 matches (their
pre-rework run was `2 failed, 1619 passed` = 1621) — the total is **conserved**, which is the number that
would have moved had a broken test been deleted rather than repaired.

Independent reproduction of the two named checks:

```
$ python .agent-work/issue-308/checks/lesson_intake_is_cut.py            exit 0   (PASS)
$ python -c "...context_refs assertion..."
context_refs entries: 5 | naming LESSONS.md: []                          exit 0
```

Scope: `git show HEAD --stat` = 28 files, 20 of them `.agent-work/` workflow artifacts, **8 substantive**
(5 `skills/`, 2 `tests/`, 1 `scripts/`). `lesson_intake_is_cut.py` is **not** in the changed set — the
guard was not weakened to make itself green.

---

## 5. Fowler refactoring pass

Record: `.agent-work/issue-308/g5-review/fowler-pass.json`.
`verify_fowler_pass.py` → **exit 0**: `smells=12, flagged=['duplicated-code','shotgun-surgery'],
overridden=['long-method','speculative-generality']`, 8 absent. Both flags are observations, not blockers.

- **shotgun-surgery (flagged)** — the diagnostic one. One decision (*"a live agent no longer reads the
  bank"*) required five differently-phrased edits across five files plus a sixth mechanical declaration.
  That is precisely why a one-phrase grep is the wrong instrument here, and why the independent
  enumeration above was worth running. Not fixable at this gate: the doctrine is deliberately restated
  per audience.
- **duplicated-code (flagged)** — the synthetic fixture literal appears 4× in `tests/test_episode_capture.py`
  (`grep -c "synthetic-durable.md"` → 4). Cosmetic → `tc4`.
- **long-method (overridden)** — the spine imperatives are ~2000-character strings, but the checklist
  schema makes `imperative` one string per task and `global-everyone.md` makes engine `current` the sole
  state channel; splitting is not expressible. Both edited imperatives got *shorter*.
- **speculative-generality (overridden)** — the `durable` token now has zero shipped declarations, so
  three tests guard a path no shipped data reaches. Overridden because the trap is **silent** (a wrong
  root records `rev: null` without raising), so these tests are the only detector; the handoff fenced the
  decision; and the implementer surfaced the token's future as an explicit decision candidate.
- **comments-as-deodorant (absent, in the good direction)** — the quiet quality win of this diff: five
  stale assertions naming `.agent-work/LESSONS.md` as *"the single shipped `durable` declaration"* were
  corrected in the same commit rather than left to rot. I re-read each corrected comment against the code
  it annotates; each is now accurate.

---

## 6. Findings

### Blockers
**None.**

### Observations
1. **[medium] The acceptance guard's green is narrower than it reads.** Proven blind to (a) intake outside
   `skills/`, (b) intake in an allowlisted file, (c) intake that does not spell `LESSONS.md`. Commands and
   exit codes in §1. Guard debt, not a defect in this change — I swept all three blind spots by hand and
   they are clean. → `tc1`
2. **[low] `feedback`-step re-observation language is now orphaned.** §2 Class 2. Explicitly fenced by the
   handoff. → `tc2`
3. **[low] `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` carries two stale current-state claims** — `:118`
   *"Spine `context` step gains a read: load `LESSONS.md`…"* and `:171` a proposed `SessionStart` hook to
   *"inject the `LESSONS.md` digest"*. Neither is a live-agent instruction (design-rationale doc; no hook
   implements it — `grep -rniE "lessons" scripts/hooks/` is empty), so neither is a read-intake site. But
   the first is now false as written and the second would reintroduce intake if built. → `tc3`

**Reachable instance the Commander asked about:** the only *reachable* stale read-claim I found outside the
known-and-filed set is observation 3 (`RECURSIVE_IMPROVEMENT_DESIGN.md:118`). It is a design record rather
than an instruction, so I did not treat it as a missed site — but it is editable, unlike `#400`.

**Confirmed out of scope, not re-reported as defects:** the empty Active section + its stale preamble
(`#400`); downstream compiled `docs/agents/AGENT_GUIDE.md` (this repo has no local `AGENT_GUIDE.md` —
only `CREW_CONTEXT.md` and `ORCHESTRATOR_CONTEXT.md` — so nothing local is affected); episode-store
schema constraints (`#399`).

### Triage candidates
`tc1` guard hardening · `tc2` orphaned `feedback` re-observation language · `tc3` stale design-doc claims +
the `SessionStart` hook proposal · `tc4` test fixture literal duplication. All four are recorded in the
survey's `triage_candidates`.

---

## 7. Workflow Feedback

- **The handoff's occurrence count was wrong, and the handoff's own advice caught it.** It said
  `COMMANDER_SPINE.template.json` "held five `.agent-work/LESSONS.md` occurrences; two were removed and
  three must remain." Measured: **six** before, **four** after — the `feedback` imperative invokes
  `apply_lessons_delta.py` twice (delta apply + `--ripe`). Harmless here only because the same paragraph
  said *"verify by content, not by count."* Second count error in this gate's paperwork (the implementer
  found the "three tests" blast-radius count was over-inclusive by two). Both erred toward *more* review,
  but a handoff that states a count should derive it from a command, same as the runs it dispatches.
- **Nothing told me where to put the survey's Fowler record.** The skill says "record the pass to
  `templates/FOWLER_PASS.template.json`", which is the *template's* path inside the installed skill. I
  wrote it beside the survey at `.agent-work/issue-308/g5-review/fowler-pass.json`, matching the g3 gate's
  precedent. Worth stating explicitly in the skill.
- **`advance` is not a survey verb, and the skill text implies it is.** The reviewer SKILL.md says
  "`advance`/`record` only once its postconditions pass" and "run the engine's final `advance`/
  `consolidate`". On a `survey` the engine answers `REFUSED: advance is for gated checklists; use record`.
  Costs one refused call per reviewer; the wording should name `record` for surveys.
- **The handoff was otherwise excellent** — naming the three defect *classes* up front, before the work
  existed, is what made this review adversarial instead of confirmatory. The instruction to build a
  competing enumeration rather than re-run the guard is the reason §1 has content.
- **Restoring mutated files needs a stated recipe.** The handoff correctly forbids `git checkout` on a file
  under review but does not say what to do instead. I saved bytes, mutated, restored, and re-checked
  sha256 — worth promoting into the reviewer skill, since mutation testing is now a standing expectation.
