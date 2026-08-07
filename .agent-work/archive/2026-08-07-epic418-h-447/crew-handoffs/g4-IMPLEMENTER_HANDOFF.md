# Implementer handoff — g4: carry the live content, then untrack and delete

**Worktree:** `C:/Programs/constellation-skills-wt/epic418-h-447` · branch `epic-418/h-447-episodes-retirement` · HEAD `100a33c`

## Protected intent

We are retiring `.agent-work/LESSONS.md` (a playbook agents were told to **read** and condition
behaviour on) and `.agent-work/AGENT_FEEDBACK.md` (a write-only retrospective). Both are replaced
by the episode store: **a record of what happened**.

The human's constraint, verbatim, 2026-08-06:

> *"we shouldn't be reading the episodes like lessons, it's a store for things that happened to
> replace both feedback and lessons."*

g2 built the capture gate. g3 rewired both spines onto it and stopped the installer shipping the
playbook's machinery. **This gate carries the live content across and then removes the old
machinery.** After it, nothing that ships knows how to write a playbook.

**The carry is the part you can get subtly and badly wrong.** A lesson's `statement` is
*prescriptive* — it tells a future agent what to do. An episode holds no rules. So a lesson's
statement becomes the **`workaround` assertion**: an observation of *what was done in that run*,
never a rule for the next one. Get that inversion right and the carry is honest; get it wrong and
you have migrated the playbook into the store, which is the one outcome this entire run exists to
prevent.

---

## PART 1 — carry the eight live lessons

### Where the source actually is — read this, it is not where you would look

Your worktree is based on `cbd9aee`. **`main` has since advanced to `861ecbe` and
`.agent-work/LESSONS.md` was union-merged there.** Its Active section now holds **EIGHT** lessons,
not the six your worktree's copy shows. **Do not read `.agent-work/LESSONS.md` in this worktree as
the source of truth.** Read:

```
.agent-work/epic418-h-447/context/LESSONS-main-861ecbe.md          # 140 lines, EIGHT active lessons
.agent-work/epic418-h-447/context/AGENT_FEEDBACK-main-861ecbe.md   # 2119 lines
```

These are read-only snapshots of main's copies, staged by the Commander. **Do not rebase or merge**
— you do not need to. Episodes land in `episodes/`, a tracked repo-root path that is yours to
write.

The Commander amended the spine through the engine (count 6 → 8, authority
`admiral:launch-order/H-447`) so the gate's own postconditions match reality.

### The eight, all of which qualify

Each has a `grounding` naming a concrete observed event, which is the plan's CARRY RULE:

1. `falsify-a-check-against-a-decoy-before-trusting-it`
2. `a-verdict-must-not-select-on-the-gap-it-escalates`
3. `grading-a-contested-claim-settled-launders-it`
4. `reasoning-gate-crew-waiver-can-be-wrong-for-synthesis`
5. `enumerate-the-sites-by-command-before-editing-a-claim`
6. `archive-the-producer-with-the-output`
7. `name-scoped-test-filter-gates-are-strong-but-structurally-blind` ← **new on main**
8. `crew-blocked-on-a-commander-blocked-on-that-crew-has-no-exit` ← **new on main**

**CARRY RULE:** carry only a lesson whose `grounding` already names the observed event. All eight
do. If you find one that would need a **synthesised** `observed-behavior`, **DROP it with a stated
reason** — inventing an observation is exactly the fabrication the store's doctrine forbids.

### The mapping — follow the precedent, do not invent one

Read `episodes/active/issue-308-001.md` first. It is the worked precedent for this exact migration.

| episode assertion | comes from the lesson's |
|---|---|
| `task-intent` | `grounding` — what the run was trying to do |
| `expected-behavior` | `grounding` — what was expected to happen |
| `observed-behavior` | `grounding` — what actually happened. **Never synthesised.** |
| `impact-cost` | the cost in the grounding, **plus** the lesson's counters and history verbatim: *"Playbook counters at migration: mentions N, confirmed N, disconfirmed N, last confirmed <date> (<run>), N runs since."* |
| `workaround` | **the lesson's `statement`, rewritten from a rule into an observation of what was done.** |

The `workaround` rewrite is the load-bearing step. Concretely: a statement that reads *"a gate must
always pair `-k` with an unfiltered suite run"* becomes *"the run paired the `-k` gate with an
unfiltered suite run, and that is what caught both defects."* Same information, no imperative mood,
no second-person address, no "must"/"should"/"always"/"never" aimed at a future agent.

**Self-check before you write each one:** read your `workaround` aloud as if you were a future agent
who just found it. If it reads as an instruction, rewrite it. If it reads as a report of something
that happened, it is right.

Carry the originating lesson id as an `artifact-ref` (`lesson:<slug>`) for identity continuity, plus
the grounding's artifact lines as further `artifact-ref`s. This is the precedent's own pattern.

### The delta format — do not go dig for it, here it is

`episodes/` is written **ONLY** through `scripts/apply_episode_delta.py`. Never hand-edit a file
there; hand-editing is a defect regardless of how correct the text looks.

The writer assigns ids (`issue-447-001` … `issue-447-008`) — **never supply one.** Delta shape,
read out of the validator so you do not have to:

```json
{"work_id": "issue-447",
 "ops": [{"op": "create",
   "mechanical": {"run": "issue-447", "project": "constellation-skills", "role": "commander",
                  "spine-step": "execute",
                  "context-manifest-ref": ".agent-work/epic418-h-447/MISSION_FRAME.md@100a33c",
                  "refusals": 0, "reopens": 0, "rework-count": 0, "failed-commands": 0,
                  "artifact-ref": ["lesson:<slug>", "<grounding artifact line>"]},
   "agent_supplied": {"task-intent":       {"strength": "strong", "statement": "..."},
                      "expected-behavior": {"strength": "strong", "statement": "..."},
                      "observed-behavior": {"strength": "strong", "statement": "..."},
                      "impact-cost":       {"strength": "strong", "statement": "..."},
                      "workaround":        {"strength": "strong", "statement": "..."}}}]}
```

Hard facts about that shape, each of which will reject your whole delta if violated:
- `work_id` at the top level is **required**.
- The mechanical allowlist is exactly `run, project, role, spine-step, context-manifest-ref,
  refusals, reopens, rework-count, failed-commands, artifact-ref` and nothing else. All four
  counters are required non-negative integers. `artifact-ref` is a **list**; every other field is a
  scalar.
- All **five** `agent_supplied` kinds are required. An assertion accepts **only** `strength` and
  `statement` — `lifecycle-standing` is rejected as misfiled (it always starts `active`).
- Statements are single-line: **no newlines** anywhere in a value.
- Application is **all-or-nothing** — one invalid op rejects the whole delta and leaves the store
  byte-for-byte unchanged. Use `--dry-run` first.

Write the delta to `.agent-work/epic418-h-447/episode-delta.json`, then:

```
python scripts/apply_episode_delta.py --delta .agent-work/epic418-h-447/episode-delta.json --store-root episodes --dry-run
python scripts/apply_episode_delta.py --delta .agent-work/epic418-h-447/episode-delta.json --store-root episodes
```

`--store-root` explicitly, always. `git add episodes/active/issue-447-*.md` — the archive-phase
gate requires them tracked.

### `AGENT_FEEDBACK.md` — DROPPED WITH REASON, not migrated

Its 2119 lines (state on main at `861ecbe`) are **not** migrated. The reason, which you must record
in your result: synthesising typed assertions from unstructured prose retrospectives is exactly the
fabrication the store's doctrine forbids, and git history retains the file at its final revision.
**Record the reason and the commit** — a reader must be able to find the content, not merely be
told it was dropped.

---

## PART 2 — untrack, do NOT delete

```
git rm --cached .agent-work/LESSONS.md
git rm --cached .agent-work/AGENT_FEEDBACK.md
```

**`--cached`. NOT plain `git rm`. This is load-bearing and it is measured, not a preference.**

`scripts/agent_work_root.py:136-140` redirects `durable_root()` to the fallback whenever an active
Admiral epic lease exists — and epic #418 holds one. So **this run's own `feedback`/`archive` gate
reads THIS WORKTREE's `.agent-work/AGENT_FEEDBACK.md`.** Deleting the working-tree copy strands this
run's closeout, and the only two exits from there are recreating the retired file — literally
#308's failure shape — or a human override in a run with no reachable human.

Untracking removes them from the **index**, which is what "shipped" means and what the guard's
`retired-path-still-tracked` leg checks. The on-disk copies survive this run and die with the
worktree. That is the whole design.

**Leave a comment recording this at the guard's `retired-path-still-tracked` leg** in
`scripts/verify_retirement.py` — a future reader must find out *why* it is untrack-not-delete at
the place that enforces it. (`scripts/verify_retirement.py` is in scope **for this comment only**;
do not change its logic.)

Verify immediately after, and put the exit codes in your result:

```
git ls-files --error-unmatch .agent-work/LESSONS.md ; echo EXIT=$?          # MUST be non-zero
git ls-files --error-unmatch .agent-work/AGENT_FEEDBACK.md ; echo EXIT=$?   # MUST be non-zero
test -f .agent-work/AGENT_FEEDBACK.md ; echo EXIT=$?                        # MUST be 0 — still on disk
python C:/Users/fredc/.claude/skills/constellation-commander/scripts/verify_agent_feedback.py epic418-h-447 --phase feedback ; echo EXIT=$?
```

That last one is **this run's own closeout gate**. Record its exit code before and after your
change. If your change strands it, **stop and report a blocker** — do not work around it by
recreating a retired file.

---

## PART 3 — delete the machinery

```
scripts/apply_lessons_delta.py
scripts/verify_lessons_applied.py
scripts/verify_agent_feedback.py
skills/lessons-auditor/                        (whole tree)
skills/workbench/templates/LESSONS.template.md
skills/workbench/templates/AGENT_FEEDBACK.template.md
tests/test_apply_lessons_delta.py
tests/test_verify_lessons_applied.py
tests/test_verify_agent_feedback.py
```

Then **prune** — do not delete the files — the individual test methods in
`tests/test_agent_work_root.py` and `tests/test_feedback_tooling.py` that load a now-deleted module.
Keep everything else in both files. A pruned method's absence should be obvious from the diff; if a
whole class becomes empty, remove the class and say so.

### DO NOT DELETE `scripts/stage_feedback.py` or `scripts/collect_feedback.py`

The plan originally cut `stage_feedback.py` on the premise that the fence mechanism exists only
because `.agent-work/` is gitignored. **That premise is FALSE** — `.gitignore:1` shows
`.agent-work/` is tracked, and the fence branch exists for **epic-lease fencing**, which is real and
is this run's own situation. `.agent-work/CONSTELLATION_FEEDBACK.md` is a **third** file that #447
does not name and that is **NOT** retired. Leave all of it alone.

If deleting `verify_agent_feedback.py` breaks something in `stage_feedback.py` or
`collect_feedback.py`, that is a finding to **report**, not to fix by widening the deletion.

---

## Allowed scope

**WRITE (via the writer only):** `episodes/active/issue-447-*.md`
**CREATE:** `.agent-work/epic418-h-447/episode-delta.json`
**DELETE / UNTRACK:** exactly the paths listed in Parts 2 and 3
**EDIT:** `tests/test_agent_work_root.py`, `tests/test_feedback_tooling.py` (prune only);
`scripts/verify_retirement.py` (**one comment** at the `retired-path-still-tracked` leg, no logic change)

**Touch nothing else.** Not the spine templates, not the installer, not the prose in
`skills/*/SKILL.md` or `docs/` — that is g5.

**Fenced — a concurrent Commander owns these, do not touch and do not read into:**
`scripts/hooks/gauge_writer_hook.py`, `scripts/hooks/spine_rail.py`, `scripts/gauge_reader.py`,
`docs/GAUGE_WRITER_HOOK.md`.

## Constraints

- **Record stores are never hand-edited.** `episodes/` only through `apply_episode_delta.py`.
- `python`, **never** `py` — `py` has no pytest here and produces fake greens.
- Windows: `encoding='utf-8', newline='\n'` explicitly on every file write.
- Prefix suite runs with `FORCE_COLOR=0 NO_COLOR=1`. A colourised environment breaks
  `tests/test_mutation_floor.py`'s harness regex and produces 10 phantom `HARNESS ERROR` failures
  (Commander-measured; baseline at `100a33c` is **1716 passed, 0 failed**).
- Do not commit. The Commander commits at integrate. **Exception:** `git rm --cached` necessarily
  stages; leave it staged and do not commit.
- Use your own session scratchpad for temp files, never `/tmp` — a concurrent Commander shares it.
- Scope discipline (Tommy's standing ruling): build what needs to work and no more. A corner case
  you decline gets a comment **at the code site** naming it and is reported up.

## Required evidence — commands that can genuinely fail

Redirect to a file then `echo $?`; a pipe captures the pipe's exit code.

```
python scripts/apply_episode_delta.py --delta .agent-work/epic418-h-447/episode-delta.json --store-root episodes --dry-run
python scripts/query_episodes.py select --field run --value issue-447          # count MUST be 8
python scripts/verify_episode_captured.py issue-447 --store-root episodes                  ; echo EXIT=$?   # MUST be 0
python scripts/verify_episode_captured.py issue-447 --store-root episodes --phase archive  ; echo EXIT=$?   # MUST be 0 once git add lands
git ls-files --error-unmatch .agent-work/LESSONS.md        ; echo EXIT=$?   # MUST be non-zero
git ls-files --error-unmatch .agent-work/AGENT_FEEDBACK.md ; echo EXIT=$?   # MUST be non-zero
python C:/Users/fredc/.claude/skills/constellation-commander/scripts/verify_agent_feedback.py epic418-h-447 --phase feedback ; echo EXIT=$?
python scripts/verify_retirement.py | cut -f1 | sort -u     # retired-path-still-tracked MUST be GONE
python -m pytest tests/test_episode_store.py tests/test_episode_fields.py -q
FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q
```

## Close criteria

1. **Eight** episodes under `episodes/active/` carry run id `issue-447`, all written through the
   writer, all `git add`ed.
2. Every one's `workaround` assertion reads as **an observation of what was done**, not a rule.
   Quote all eight `workaround` statements in your result so this can be graded without reopening
   the files — this is the criterion most likely to be got wrong.
3. Each carries `lesson:<slug>` as an `artifact-ref`.
4. `AGENT_FEEDBACK.md`'s content is dropped with a **stated reason naming the commit** that retains
   it.
5. `git ls-files` no longer lists either retired path; **both files still exist on disk.**
6. The retired scripts, the lessons-auditor skill tree and the two templates are gone; the pruned
   test files still pass; `stage_feedback.py` and `collect_feedback.py` **survive**.
7. Guard leg `retired-path-still-tracked` is **gone**.
8. This run's own `verify_agent_feedback.py` gate still runs with an unchanged exit code.
9. No new suite failures beyond tests you deliberately deleted or pruned, **each explained by
   name** — state the count delta and where every removed test went.

## Report back

`IMPLEMENTER_RESULT` to `.agent-work/epic418-h-447/results/g4-IMPLEMENTER_RESULT.md`: diff summary,
the eight `workaround` statements in full, every evidence command with its **real** exit code, the
guard leg distribution before and after, the suite count delta explained by name, corner cases not
chased with their comment file:line, unresolved blockers (say "none" explicitly if none), and a
**Workflow Feedback** section. Deliver the substance in your final message.

## Map anchors (inbound)

- **Structural:** `struct:episodes/README.md`, `struct:docs/EPISODE_STORE.md`,
  `struct:scripts/verify_retirement.py` (comment only).
- **Capability:** `capability:episode-store`; `capability:run-closeout-learning`.
- **Constraints:** `constraint:episodes-are-not-prescriptions` — **THE constraint, and the carry is
  where it is most at risk**; `constraint:record-stores-never-hand-edited`;
  `constraint:doctrine-lives-in-docs-agents`.
- **Decisions:** `decision:episodes-replace-both` `@grade: settled/human`;
  `decision:untrack-do-not-delete` `@grade: settled/measured` — g4 uses `git rm --cached`, not
  `git rm`, so this run's own closeout gate is not stranded. A contradiction with a `settled/human`
  anchor is a decision candidate to float up, not to revise in place.
- **Evidence expectations:** `claim:suite-no-failures`.
