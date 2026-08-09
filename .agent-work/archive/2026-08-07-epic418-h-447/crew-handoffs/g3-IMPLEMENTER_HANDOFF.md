# Implementer handoff — g3: rewire the closeout obligations onto episode capture

**Worktree:** `C:/Programs/constellation-skills-wt/epic418-h-447` · branch `epic-418/h-447-episodes-retirement` · HEAD `dbf9a23`

## Protected intent — read this before anything else

We are retiring `.agent-work/LESSONS.md` (a playbook agents were told to **read** and condition
behaviour on) and `.agent-work/AGENT_FEEDBACK.md` (a write-only retrospective). Both are replaced
by the episode store: **a record of what happened**.

The human's constraint, verbatim, 2026-08-06:

> *"we shouldn't be reading the episodes like lessons, it's a store for things that happened to
> replace both feedback and lessons."*

**The named failure mode of this gate is re-pointing a read path at `episodes/`.** Every place you
find an instruction to *read the playbook, adjudicate it, check ripeness, or route a lesson*, the
answer is **delete it**, not *repoint it at the store*. Repointing reproduces the exact defect
under a new directory name and fails this gate. If a consumer needs a *rule to follow*, doctrine
lives in `docs/agents/*` and putting one there is a human's call — never yours, and never the
store's job.

g2 shipped `scripts/verify_episode_captured.py`, the write-side capture gate. This gate makes the
spines and the installer actually use it.

## Task

### 1. `skills/commander/templates/COMMANDER_SPINE.template.json`

**a) Replace the `feedback` step's `imperative`.**

Roughly 70% of the current text is apply-or-defer, ripeness, `bank_reason`, dormancy,
export/resolve/defer and delta-op vocabulary. **All of it is playbook machinery and it retires with
the playbook.** Do not translate it into episode vocabulary — delete it.

**Keep:** the honest-reflection opening (how closely you followed the skills/handoffs/checklists,
where you improvised, what was ambiguous or missing, what would have helped) and the requirement
that a `none` answer carries a run-specific reason. **Keep** the harvest of crew Workflow Feedback
gathered at each `gN-integrate`.

**Then it says, in substance:** record what happened as episodes — **one episode per distinct
thing that happened**, not one per run and not a summary — each stating `task-intent`,
`expected-behavior`, `observed-behavior`, `impact-cost` and `workaround`.

**It MUST carry this sentence explicitly and verbatim:**

> An episode is a record, not a rule: write what you observed, and do NOT write a rule for a future
> agent to follow — a rule to follow belongs in docs/agents/* and is a human's call.

Write the delta to `.agent-work/<work-id>/episode-delta.json` and apply with:

```
python <commander-skill-dir>/scripts/apply_episode_delta.py --delta .agent-work/<work-id>/episode-delta.json --store-root episodes
```

`--store-root` is passed **explicitly and non-negotiably**: the writer's default resolves relative
to the installed skill directory, so on an installed copy it silently creates a store at
`~/.claude/skills/constellation-commander/episodes` — outside the repo — while every gate reports
green. That is #308's failure shape wearing a new name. See the comment already at
`scripts/apply_episode_delta.py` `store_root()`.

**b) `feedback.c1` — RETARGET IN PLACE.** Its `check.command` becomes
`python <commander-skill-dir>/scripts/verify_episode_captured.py <work-id> --phase feedback` and
its `statement` is rewritten to say an episode was captured for this run.
**Never delete a `c1`** — `c1` is the bare-form `attest` default in `checklist_engine.py`.

**c) `feedback.c2` — DELETE.** It is `verify_lessons_applied.py` ("no threshold-ripe lesson left
unpaid"). It is the TERMINAL postcondition, so removing it renumbers nothing. Its obligation does
**not** move anywhere: ripeness and apply-or-defer no longer exist.

**d) `archive.c1` — RETARGET IN PLACE** to
`python <commander-skill-dir>/scripts/verify_episode_captured.py <work-id> --phase archive`, with a
statement about the episode being captured **and tracked by git** so it survives the worktree.

**e) The `archive` imperative** currently opens by telling the agent to commit the appended
`.agent-work/AGENT_FEEDBACK.md` entry and later to run the archive-phase feedback invariant check.
Update those sentences: the durable record is now the committed episode under `episodes/`, which is
a tracked repo-root path and therefore survives `git worktree remove` and a fresh clone — the whole
`.agent-work/` is-it-gitignored dance goes away. Leave the rest of that imperative (PR body on
Windows, work-area move, the `c4` waiver path, the lease-release-last ordering) **untouched**.

**f) `archive.c4` `deny_globs`** — **KEEP** `.agent-work/LESSONS.md` and
`.agent-work/AGENT_FEEDBACK.md` in the list. After g4 untracks them they change meaning from "do
not commit this record dump" to "**do not re-stage the retired files**", which is a stronger reason
to keep them than the one they were added for. Do not remove them, and do not add `episodes/` to
`deny_globs` — episodes are *meant* to be committed.

Both retired paths will then still be *named* on a shipped surface, so **add them to the guard's
approved list** (see §4) with that reason.

### 2. `skills/admiral/templates/ADMIRAL_SPINE.template.json`

Same shape at `closeout`.

- **Delete the `constellation-lessons-auditor` dispatch and its whole disposition-routing
  paragraph** from the closeout imperative — the run brief, the auditor subagent, the
  graduate-and-retire / template-delta / Charter-nomination / export / inbox-delta /
  drop-with-reason vocabulary, the `apply_lessons_delta.py` instruction, the `authority=human`
  apply rules, and `bank_reason`. **Delete it; do not repoint it at `episodes/`.** An "episode
  auditor" that reads the store and routes dispositions IS the playbook, rebuilt. This is the
  single most important line in this handoff.
- Keep the epic retrospective (step 2), the cartographer reconcile (3), hygiene (4), user
  acceptance (5), and the lease release. Rewrite step 2 so the epic's record is episodes captured
  through `apply_episode_delta.py --store-root episodes`, carrying the same
  **record-not-a-rule** sentence as the Commander spine.
- Keep the surgical-raw-text-edit warning for shipped compact JSON — it is generally true and
  still applies.
- **`closeout.c1`** — statement rewritten (its `check` stays `null`). It should say the epic's
  observations were recorded as episodes, with no rule written for a future agent to follow.
- **`closeout.c2` — RETARGET** to
  `python <admiral-skill-dir>/scripts/verify_episode_captured.py <work-id> --phase feedback`.
- **`closeout.c6` — DELETE.** It is `verify_lessons_applied.py` and it is terminal.
- Leave `c3`, `c4`, `c5` alone.

### 3. `scripts/install_constellation.py`

In `SKILL_SCRIPT_BUNDLES`:
- **`admiral`** and **`commander`**: drop `apply_lessons_delta.py`, `verify_lessons_applied.py`,
  `verify_agent_feedback.py`; add `apply_episode_delta.py`, `verify_episode_captured.py`.
- **Delete the `lessons-auditor` entry** from `SKILL_SCRIPT_BUNDLES` **and** from
  `SKILL_REFERENCE_BUNDLES`.

**Do NOT bundle `query_episodes.py`** — the read path does not travel with the roles that write.

**But do NOT claim that as a structural guarantee.** The cold panel measured four ways around it:
repo-relative execution, plain `Read`/`Grep` on a tracked path, the unfiltered `copytree` at
`install_constellation.py:915`, and `SCRIPT_RUNTIME_COMPANIONS`. **Leave a comment at the bundle**
saying the omission is a default, not a boundary, and naming those four routes. An overclaim here
is worse than no claim: it would let a future reader believe the store is unreadable by an
installed role when it plainly is not.

### 4. `tests/data/store_mentions.approved.txt`

The g1 guard's `unapproved-store-mention` leg is a **frozen approval census**: one `# <reason>`
line, then one `<path>:<normalized line>` entry directly beneath it. `normalize()` collapses
whitespace, so re-indenting an approved line does not read as a new mention.

Two batches to approve, **each with its own honest reason** — and the reason is the thing being
reviewed, so write it as a real justification, not a label:

1. **The 9 lines in `scripts/verify_episode_captured.py`** (currently reported at lines 25, 37,
   126, 162, 180, 186, 196, 213, 228 — re-derive them, do not trust these numbers). These are the
   capture gate itself. The approvable reason is that it is a **write-side capture check that
   emits ids and counts and never statement text** — that is the discriminator the census exists
   to apply.
2. **Whatever your own edits add** — the spine imperatives now name `episodes` and
   `apply_episode_delta.py`, and `archive.c4`'s `deny_globs` names both retired paths. Approve
   them as write-path / re-staging-block mentions.

Run `python scripts/verify_retirement.py` and work the `unapproved-store-mention` leg to **zero**.
Do **not** approve anything that instructs an agent to *read* the store — if you find yourself
writing that reason, you have written the defect and must change the code instead.

### 5. `tests/test_install_constellation.py` — a GENERAL assertion, not a per-name one

Add: **every `kind: "command"` postcondition in both installed spine templates must name a script
that exists in that skill's installed `scripts/` directory.**

General, not per-name. A test that asserts "commander installs `verify_episode_captured.py`"
protects this rewiring only; a test that asserts "no spine command names a script the skill does
not install" protects **every future rewiring**, which is the whole reason this run exists. Parse
the command string for the script filename; a spine naming a script the installer does not ship is
a failure the gate must catch at install time rather than mid-run.

## Allowed scope — touch nothing else

```
skills/commander/templates/COMMANDER_SPINE.template.json
skills/admiral/templates/ADMIRAL_SPINE.template.json
scripts/install_constellation.py
tests/test_install_constellation.py
tests/data/store_mentions.approved.txt
```

**Explicitly NOT yours, they are g4/g5:** deleting `apply_lessons_delta.py`,
`verify_lessons_applied.py`, `verify_agent_feedback.py`; untracking `.agent-work/LESSONS.md` or
`.agent-work/AGENT_FEEDBACK.md`; deleting `skills/lessons-auditor/`; any prose in
`skills/*/SKILL.md`, `skills/commander/references/commander-core.md`, or `docs/`; writing any
episode.

**Fenced — another Commander owns these, do not touch and do not read into:**
`scripts/hooks/gauge_writer_hook.py`, `scripts/hooks/spine_rail.py`, `scripts/gauge_reader.py`,
`docs/GAUGE_WRITER_HOOK.md`.

## Constraints

- **Edit the shipped compact-format JSON templates as raw TEXT, surgically.** NEVER round-trip
  through `json.load`/`json.dump` — it reflows the whole file and destroys blame. **Re-validate
  with `json.load` after every edit.** This is a hard requirement and a reviewer will check the
  diff shape.
- `python`, **never** `py` — `py` has no pytest here and produces fake greens.
- Windows: `encoding='utf-8', newline='\n'` explicitly on every file write.
- **Never delete a postcondition with id `c1`** — retarget it in place. Only ever delete TERMINAL
  conditions (`feedback.c2`, `closeout.c6` — both verified terminal above).
- Edit canonical shared doctrine at `skills/_shared/global-*.md`, **never**
  `skills/<role>/references/global-*.md` (install-time copies, silently regenerated). You should
  not need to touch either in this gate.
- Do not commit. The Commander commits at integrate.
- Use your own session scratchpad for temp files, never `/tmp` — a concurrent Commander shares it.
- Scope discipline (Tommy's standing ruling): build the thing that needs to work and no more. A
  corner case you choose not to chase gets a comment **at the code site** naming it, and is
  reported up — never silently absorbed.

## The trap in this gate: you are editing the machinery you are running on

Your Commander's own `feedback`/`archive` step is gated by `verify_agent_feedback.py`, and you are
about to drop it from the install bundle. **Dropping it from `SKILL_SCRIPT_BUNDLES` does not delete
the already-installed copy** at `C:/Users/fredc/.claude/skills/constellation-commander/scripts/` —
no install runs in this gate. **Verify that, do not assume it**: run

```
python C:/Users/fredc/.claude/skills/constellation-commander/scripts/verify_agent_feedback.py epic418-h-447 --phase feedback
```

before and after your change and confirm the exit code is unchanged. If your edit somehow strands
that path, **stop and report it** — a stranded closeout is a blocker, not something to work around
by recreating a retired file.

## Required evidence — commands that can genuinely fail

Redirect to a file then `echo $?`. A pipe captures the pipe's exit code, not the command's.
Set `FORCE_COLOR=0 NO_COLOR=1` on suite runs: a colourised environment breaks
`tests/test_mutation_floor.py`'s harness regex and produces 10 phantom failures (Commander-measured,
`.agent-work/epic418-h-447/evidence/g2-mutation-floor-nocolor.txt`).

```
python -m pytest tests/test_install_constellation.py -q
python -c "import json;[json.load(open(p,encoding='utf-8')) for p in ('skills/commander/templates/COMMANDER_SPINE.template.json','skills/admiral/templates/ADMIRAL_SPINE.template.json')]"   # both must still parse
python scripts/verify_retirement.py ; echo EXIT=$?
python scripts/verify_retirement.py | cut -f1 | sort -u    # replacement-absent MUST be GONE; unapproved-store-mention MUST be GONE
python -m pytest tests/test_retirement_guard.py -q
FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q
```

Also show the diff shape proving you edited raw text rather than reflowing:
`git diff --stat` on the two templates — a surgical edit touches a handful of lines, a
`json.dump` round-trip rewrites the whole file. A whole-file rewrite is an automatic BLOCK.

## Close criteria

1. `verify_retirement.py`'s `replacement-absent` leg is **gone** — both spines name
   `verify_episode_captured.py` in a task imperative, both bundles carry it, the script exists.
2. `unapproved-store-mention` is back to **zero**, every new approval carrying a reason that names
   a **write** path or a re-staging block — never a read instruction.
3. Neither spine template contains any lesson/ripeness/apply-or-defer/bank_reason/dormancy
   vocabulary, and **no instruction anywhere tells an agent to read `episodes/`**.
4. The verbatim record-not-a-rule sentence is present in the Commander `feedback` imperative.
5. `feedback.c1` and `archive.c1` retargeted **in place**; `feedback.c2` and `closeout.c6` deleted;
   no other condition id changed.
6. Both templates still parse as JSON, and the diff is surgical.
7. The new install test is **general** (any spine command names an installed script), and you have
   shown it can fail — red-prove it by temporarily pointing a spine command at a nonexistent script
   and watching it go red, then restore.
8. Your own Commander's `verify_agent_feedback.py` path still runs with an unchanged exit code.
9. No new failures in the full suite beyond the tests you deliberately changed, each explained by
   name.

## Report back

`IMPLEMENTER_RESULT` to `.agent-work/epic418-h-447/results/g3-IMPLEMENTER_RESULT.md`: diff summary,
every evidence command with its **real** exit code, the guard's leg distribution before and after,
the red proof for the new install test, the before/after exit code of the `verify_agent_feedback.py`
reachability check, corner cases not chased with their comment file:line, unresolved blockers
(say "none" explicitly if none), and a **Workflow Feedback** section.

Deliver the substance of your result in your final message before ending your turn.

## Map anchors (inbound)

- **Structural:** `struct:skills/commander/templates/COMMANDER_SPINE.template.json`,
  `struct:skills/admiral/templates/ADMIRAL_SPINE.template.json`,
  `struct:scripts/install_constellation.py` (bundle level).
- **Capability:** `capability:run-closeout-learning` — the Commander/Admiral feedback step's write
  path. This gate is where it changes owner. `capability:episode-store`.
- **Constraints:** `constraint:episodes-are-not-prescriptions` — **THE constraint this run exists
  to honour**; `constraint:doctrine-lives-in-docs-agents`;
  `constraint:record-stores-never-hand-edited`.
- **Decisions:** `decision:episodes-replace-both` — one store of observations replaces two inboxes
  plus a playbook; **no successor playbook is created.** `@grade: settled/human`.
  `decision:untrack-do-not-delete` — g4 uses `git rm --cached`, not `git rm`. `@grade: settled/measured`.
  A contradiction with a `settled/human` anchor is a decision candidate to float up, not something
  to revise in place.
- **Evidence expectations:** `claim:suite-no-failures`.
