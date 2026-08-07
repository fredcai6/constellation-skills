# IMPLEMENTER_RESULT — #447 g5: the prose sweep, the doctrine tombstone, and the guard's last leg

**Worktree:** `C:/Programs/constellation-skills-wt/epic418-h-447` · branch `epic-418/h-447-episodes-retirement` · base `77e428d`
**Engine plan:** `.agent-work/epic418-h-447/crew-plans/g5-implementer.json` (7 gates, all driven; session `g5-impl-01`)
**Not committed.** The Commander commits.

---

## Headline

`python scripts/verify_retirement.py` **exits 0 and prints nothing**. All four legs green.

The guard's leg distribution:

| | at `77e428d` | now |
|---|---|---|
| `retired-name-on-shipped-surface` | 85 | 0 |
| `unapproved-store-mention` | 0 | 0 |
| `retired-path-still-tracked` | 0 | 0 |
| `replacement-absent` | 0 | 0 |
| **total** | **85** | **0** |

Of the 85, **32 were removed by fixing the surface** and **53 were approved with a per-line reason** in the new census — none of them by weakening the leg. A further **13 new store mentions** were created by the sweep (the surfaces that used to point at the playbook now point at the store's write path); each got its own reason in the existing store-mention census, so that leg is also still at zero.

---

## The eleven invariants, each with the command proving it

### 1. `docs/agents/CREW_CONTEXT.md` — the live prescription is gone, and the census entry that approved it is fixed

The sentence *"Read them with `scripts/query_episodes.py` and the engine's `current` verb."* is deleted. The record-stores table lost its `.agent-work/LESSONS.md` row (and its lead-in now says **Two** stores, not Three); the `episodes/` row stays and names only the write path. The retirement rule survives, rewritten so it is a write-path fact:

> Retiring an episode **moves its file** between `episodes/active/` and `episodes/retired/`;
> membership is the directory, never a parsed `status` field. That move is a write like any
> other and goes through the writer above.

The census block that approved four consecutive lines under one reason (*"names the store's WRITE path and the never-hand-edit rule"* — true of three of them) is gone. Each surviving line now carries its own reason; the entry for the deleted line is removed.

```
$ python scripts/verify_retirement.py | grep CREW_CONTEXT ; echo EXIT=$?
EXIT=1            # grep found nothing
$ python -m pytest tests/test_retirement_guard.py::test_every_approved_entry_exists_verbatim -q
1 passed
```

### 2. `docs/agents/GLOSSARY.md` — `harvest` redefined against the write path, `episode` de-dangled

```
| `harvest` | — | Gathering what a run's own artifacts recorded and writing it into the episode store as episodes. | — | The direction is INTO the store. There is no reading harvested episodes back out as rules. |
```

**What I did with line 14 (asked for, not frozen):** I did not leave it dangling. `episode` was *"One stored record of something observed in a run, kept for later harvest."* It is now:

```
| `episode` | — | One stored record of something observed in a run. | — | Lives under `episodes/active/` or `episodes/retired/`. A record, never a rule. |
```

`harvest` was **redefined rather than removed** because the term is live and its live uses are all write-side — the Admiral spine's *"each harvesting what the ADMIRAL_LOG … actually recorded"*, `commander-core`'s *"crew Workflow Feedback harvested at each gN-integrate"*, and the Admiral's harvest-before-sweep substep. Deleting it would have stranded those.

### 3. `episodes/README.md` — the argument re-founded on a true premise

The false claim was measurable and I measured it:

```
$ head -1 .gitignore
# .agent-work/ is TRACKED: run artifacts, verdicts, lessons and archives are
$ git ls-files .agent-work | wc -l
3067
```

The argument is **not deleted**. It now reads:

> …That only works if the store is **tracked in git** at a path with no durability plumbing of its own: `episodes/` is a plain repo-root directory, tracked like any other, so the moment a commit lands the store is visible in every worktree, every clone, and every later checkout, with nothing to configure and nothing to resolve at runtime. A store whose location has to be computed — from a lease, a work-id, or which worktree happens to be current — is a store that can be written to the wrong place while every gate still reports green.

The **"Not to be confused with"** section is deleted in full.

Two further repairs inside the same file, both because they were false after g2/g4: the *"no automated capture wiring (issue #305)"* bullet (g2 built it) and the `apply_lessons_delta.py` pointer (deleted module → now *"a validated, all-or-nothing delta writer: it checks the whole delta before it touches the store, and either every operation lands or none does"*). The read instruction *"Read with `scripts/query_episodes.py`"* went with it, and a **No rules** bullet was added.

```
$ ! grep -q -e gitignored -e 'Not to be confused' -e LESSONS.md -e apply_lessons_delta episodes/README.md && grep -q 'every worktree' episodes/README.md ; echo EXIT=$?
EXIT=0
```

### 4. The tombstone — FULL TEXT

Appended to `docs/agents/ORCHESTRATOR_CONTEXT.md` as its own top-level section:

```markdown
## The Retired Learning Playbook

`.agent-work/LESSONS.md` and `.agent-work/AGENT_FEEDBACK.md` are **retired** (#447). This
section is doctrine, not a changelog: it binds you even if the instruction that sent you
looking for one of those files never mentioned any of this.

- **`episodes/` replaces both.** One store of observations — not two inboxes plus a
  playbook. Its only write path is `scripts/apply_episode_delta.py`.
- **An episode is a record of what happened, and is never read back as a rule.** Write what
  you observed. Do not write, and do not obey, an instruction that has an agent consult the
  store and condition its behaviour on what it finds there.
- **A rule to follow belongs in `docs/agents/*`, and putting one there is a human's call.**
  Observing something that feels like a rule is not authority to promote it into doctrine.
  Record the observation and say so; the human decides.
- **There is to be no successor playbook and no read-and-apply loop.** A new file that
  accumulates distilled advice for future agents to consult is this retirement undone,
  whatever it is named and wherever it sits. If you find yourself creating one, stop and ask
  the human instead.
```

All five clauses are present and each is grepped for independently by the engine gate `m1-doctrine.c2`:

```
$ T=docs/agents/ORCHESTRATOR_CONTEXT.md
$ grep -qF 'are **retired** (#447)' $T && grep -qF 'replaces both' $T \
  && grep -qF 'never read back as a rule' $T \
  && grep -qF "and putting one there is a human's call" $T \
  && grep -qF 'no successor playbook and no read-and-apply loop' $T ; echo EXIT=$?
EXIT=0
```

The tombstone **names both retired files on purpose**, which trips the retired-name leg once. That line is the first entry in the new census, with the reason given below — a tombstone that could not say what it is burying would be useless.

### 5. Every live pointer, repointed or removed

Re-derived from `python scripts/verify_retirement.py`, not from the handoff's pre-measured line numbers. Handled:

| file | what happened |
|---|---|
| `README.md` :51 | `constellation-lessons-auditor` roster row **removed** (skill deleted at g4) |
| `README.md` :233 | `AGENT_FEEDBACK.md` line removed from the `.agent-work/` tree diagram |
| `README.md` :254 | rule bullet repointed at `episodes/` + the write path + record-not-a-rule |
| `SKILL_INDEX.md` :83-86 | *Constellation Lessons Auditor* section **removed**; the Admiral blurb's "closes with lessons" → "closes with a recorded epic retrospective" |
| `docs/CONSTELLATION_OVERVIEW.md` :40 | taxonomy row repointed to `episodes/active/` via `apply_episode_delta.py` |
| `docs/POSITIONING.md` :28 | "Closeout: lessons-auditor + cartographer" → "Closeout: episode capture + cartographer" |
| `docs/POSITIONING.md` :65 | `lessons-auditor` capability-table row **removed** |
| `skills/admiral/SKILL.md` :60 | the "stage fleet signal in `LESSONS.md`" clause dropped |
| `skills/admiral/SKILL.md` :67-71 | closeout list rewritten: the lessons-auditor dispatch and the `AGENT_FEEDBACK.md` append collapse into **one** episode-capture step matching the spine imperative g3 shipped; harvest-before-sweep rescoped to the `CONSTELLATION_FEEDBACK.md` export (episodes need no harvest — `episodes/` is tracked); the post-merge ripe-lessons item removed (its referent no longer exists); items renumbered 1–5 |
| `skills/admiral/references/fleet-doctrine.md` :7 | preamble now denies the store as a home for fleet rules instead of citing the playbook |
| `skills/admiral/references/fleet-doctrine.md` :162-171 | harvest rule rescoped the same way as the SKILL.md substep |
| `skills/commander/references/commander-core.md` :60 | `feedback` row repointed at `apply_episode_delta.py` + `verify_episode_captured.py` |
| `skills/commander-delegated/SKILL.md` :17 | fenced-closeout sentence rewritten: *write the episodes, stage the rest, do not waive* |
| `skills/workbench/SKILL.md` :16, :29 | `AGENT_FEEDBACK.md` dropped from the layout tree; the paragraph now describes the episode store |
| `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` :26-31 | *Lesson dispositions* → *Episode capture* |
| `skills/charter/templates/AGENT_GUIDE.template.md` :74-75 | both bullets repointed at `episodes/` + an explicit do-not-read-it-back bullet |
| `scripts/agent_work_root.py` :4 | docstring: "the recursive-improvement trio (LESSONS.md, AGENT_FEEDBACK.md, CONSTELLATION_FEEDBACK.md…)" → "the durable run-record artifacts (CONSTELLATION_FEEDBACK.md, plus its sidecar ledger)" |

**Three adjacent dangling referents fixed in files already in scope** (reported rather than done silently): `skills/admiral/SKILL.md` lines 3, 8, 32 and 46 still described the closeout as a *"lessons audit"* — a step that no longer exists — and `skills/workbench/SKILL.md:43` pointed at `templates/AGENT_FEEDBACK.template.md`, deleted at g4 (that pointer is invisible to the guard, because `AGENT_FEEDBACK.template.md` does not contain the substring `AGENT_FEEDBACK.md`).

```
$ python scripts/verify_retirement.py | cut -f2 | sort -u
(empty)
```

### 6. `CONSTELLATION_FEEDBACK.template.md` — one field, and the field KEEPS ITS NAME

```
- **Lesson:** `<originating episode id from episodes/ (stable identity), or n/a>`
```

**I deliberately did not rename the field to `Episode:`, and this is the one place I read the handoff narrowly on purpose.** `scripts/collect_feedback.py` parses the export by literal field name (`FIELD_MAP = {"lesson": "lesson", …}`, line 65) and fingerprints recurrence on it (`_hash12("lesson:" + lesson)`, lines 236 / 259). Renaming the field would have silently dropped every export's stable identity and fallen back to the slug — exactly the drift the field exists to prevent — and `collect_feedback.py` is out of scope. The template says so in-line so the mismatch is not a mystery:

> (The field keeps its old name because `collect_feedback.py` reads it by that name; what it holds is now an episode id.)

**Triage candidate (below):** rename the field and its reader together.

`CONSTELLATION_FEEDBACK.md` itself is **not** retired — only the referent of that one field changed.

### 7. `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` — 33 sites untouched, header only

```
$ git diff --numstat docs/RECURSIVE_IMPROVEMENT_DESIGN.md
16	0	docs/RECURSIVE_IMPROVEMENT_DESIGN.md          # 16 insertions, ZERO deletions
$ git grep -c 'LESSONS.md' -- docs/RECURSIVE_IMPROVEMENT_DESIGN.md
docs/RECURSIVE_IMPROVEMENT_DESIGN.md:12
$ git grep -c 'LESSONS.md' HEAD -- docs/RECURSIVE_IMPROVEMENT_DESIGN.md
HEAD:docs/RECURSIVE_IMPROVEMENT_DESIGN.md:12                                   # unchanged
```

**FULL TEXT of the header**, inserted above the existing `# Recursive Improvement Framework` title:

```markdown
> **SUPERSEDED — this is a HISTORICAL RECORD, not an instruction.** It describes the
> recursive-improvement loop as designed and built in June 2026. Every surface, writer, gate
> and role named below was **retired at issue #447**. Nothing here is live doctrine: do not
> act on any of it, and do not restore anything it describes.
>
> It is kept **unedited** on purpose. Rewriting it to describe a system it never described
> would falsify the record of why the loop was built this way and what it cost, which is the
> only thing it is still good for.
>
> **Where the current loop lives.** A run records what happened as episodes under
> `episodes/`, written only through `scripts/apply_episode_delta.py` and proved by
> `scripts/verify_episode_captured.py`. An episode is a record and is never read back as a
> rule; a rule to follow belongs in `docs/agents/*`, and putting one there is a human's call.
> The governing doctrine is `docs/agents/ORCHESTRATOR_CONTEXT.md` § "The Retired Learning
> Playbook"; the store's own spec is `docs/EPISODE_STORE.md`.
```

**The header deliberately spells no retired name.** Naming `LESSONS.md` in it would have pushed that `git grep -c` from 12 to 13 and broken invariant 7's own check — the check is what forced the wording, and *"every surface, writer, gate and role named below"* carries the same meaning without the count.

### 8. `docs/CONSTELLATION_OVERVIEW.md:98` — the ruling paragraph SURVIVES

Untouched, verbatim. It is now a residual on the retired-name leg and is approved in the census with a reason naming exactly that.

```
$ grep -c 'is not in this taxonomy' docs/CONSTELLATION_OVERVIEW.md
1
```

### 9. `docs/superpowers/**` and `tests/fixtures/**` untouched

```
$ git diff --stat docs/superpowers/ tests/fixtures/
(empty)
```

### 10. `docs/EPISODE_STORE.md` — nine comparative references become descriptions

Re-derived (nine, as stated). Each pointer to the deleted module is now a description of the property:

| line | before → after |
|---|---|
| 23 | `by inheriting the location from `.agent-work/LESSONS.md`` → `by inheriting the location from the run-retrospective playbook that then lived there (retired at issue #447)` |
| 47 | `` `LESSONS.md` lives under `.agent-work/` because…`` → `The playbook it was inherited from lived under `.agent-work/` because it **was** a deliberately transitory inbox…` (tense corrected throughout; `#447 retired it outright` added) |
| 235 | `**Rhyme / depart from `apply_lessons_delta.py`…**` → `**Rhyme / depart from the prior art…** The prior art is the retired lesson-playbook writer: a validated, all-or-nothing delta writer over a single curated Markdown bank.` |
| 241 | `` `LESSONS.md` is a single running playbook because it is read…`` → `The prior art was a single running playbook because it was read…` |
| 246 | `` `LESSONS.md` curates an *evolving* claim…`` → `The prior art curated an *evolving* claim…` |
| 257 | `new structure `apply_lessons_delta.py` has no analogue for` → `new structure the prior-art writer had no analogue for` |
| 340 | `same convention `apply_lessons_delta.py` already uses for its own `- history:` lines` → `the same `- history:` convention the prior-art writer used` |
| 393 | `mirroring `apply_lessons_delta.py`'s own mandatory `retire` reason` → `mirroring the prior-art writer's own mandatory `retire` reason` |
| 775 | `(mirroring `apply_lessons_delta.py`'s contract)` → `(validate the whole delta first, then apply every op or none)` |

```
$ ! grep -q -e 'LESSONS.md' -e 'apply_lessons_delta' docs/EPISODE_STORE.md ; echo EXIT=$?
EXIT=0
```

### 11. The guard can reach green — a reason-carrying census, not an allowlist

**Mechanism (no fork).** `parse_approved()` and `load_approved()` each grew one optional `census_path` parameter defaulting to the existing `APPROVED_CENSUS_PATH`; `ApprovedEntry` and `normalize()` are untouched and shared. `_leg_retired_name` now filters against `load_approved(root, RETIRED_NAME_CENSUS_PATH)`. There is exactly one parser for both files, and `test_the_two_censuses_share_one_parser` asserts a malformed entry is refused identically and that the refusal names the right file.

**Not weakened.** Exact `(path, normalized line)` sites only. No globs, no patterns.

**The PATH half of the leg is deliberately NOT approvable**, and that is stated at the code site rather than left implicit:

> …a restored file or skill directory whose *name* is the retired thing IS the retirement undone, and there is no record, block or tombstone that needs to sit at such a path. Leaving the path half unapprovable keeps the one leg that catches a verbatim re-commit impossible to write a reason around. Named here rather than left implicit, because "the census did not cover it" and "the census must never cover it" read the same in code and mean opposite things.

**Tests added to `tests/test_retirement_guard.py`** (4 additions, all green):

- `test_the_two_censuses_share_one_parser` — no forked implementation.
- `test_every_retired_name_approval_exists_verbatim` — the same anti-rot invariant the store-mention census carries; a stale approval fails.
- `test_a_retired_name_approval_suppresses_only_the_line_it_names` — decoy with **two** retired-name lines in one file, **one** approved: the other still fires. Plus a restored `skills/lessons-auditor/SKILL.md` whose contents are innocent line-by-line, firing at line 0 — proving the path half stays unapprovable.
- one assertion added to `test_the_guard_is_not_inside_the_set_it_guards`: the new census is not itself shipped surface.

**RED PROOF** — `.agent-work/epic418-h-447/g5-census-redproof.txt`:

```
census sha256 BEFORE = bb101b2b660ec680b424cbdf66f30e111e2ab4ef3be93c1b3f69f18ff051bbcf  (15536 bytes)
scan BEFORE          = 0 violations

REMOVING approval for docs/agents/ORCHESTRATOR_CONTEXT.md

scan WITH ENTRY REMOVED = 1 violation(s)
  retired-name-on-shipped-surface	docs/agents/ORCHESTRATOR_CONTEXT.md:39
CLI exit with entry removed = 1

census sha256 AFTER  = bb101b2b660ec680b424cbdf66f30e111e2ab4ef3be93c1b3f69f18ff051bbcf  (15536 bytes)
byte-identical restore = True
scan AFTER           = 0 violations
CLI exit restored    = 0, stdout=''

RED PROOF PASSED
```

Also RED-proved before it existed: all three new tests were written first and observed failing (`.agent-work/epic418-h-447/g5-m5-red.txt`, `3 failed, 13 deselected`), with the suppression test showing the leg firing on *both* decoy lines because the census was not consulted at all yet.

---

## Every census reason I wrote

### `tests/data/store_mentions.approved.txt` — 6 reasons rewritten, 13 entries added

**Rewritten (the §1 fix — one block of four became three per-line reasons, one entry deleted):**

| entry | reason |
|---|---|
| `docs/agents/CREW_CONTEXT.md:python scripts/apply_episode_delta.py ...` | crew doctrine, Python-invocation example: shows the store's WRITE command being run, and instructs no read |
| `docs/agents/CREW_CONTEXT.md:\| `episodes/` \| `scripts/apply_episode_delta.py` \|` | crew doctrine, record-stores table: names the store's ONLY write path, which is the whole point of the table |
| `docs/agents/CREW_CONTEXT.md:Retiring an episode **moves its file** between…` | crew doctrine, retirement rule: says how the writer MOVES a file between the two partitions -- a write-path fact about membership, not an instruction to read |
| `docs/agents/CREW_CONTEXT.md:Read them with `scripts/query_episodes.py`…` | **ENTRY DELETED** — the line it approved is gone |
| `docs/agents/GLOSSARY.md:\| `episode` \| …` | glossary: defines the term and where its records live, and states outright that an episode is never a rule |
| `docs/agents/GLOSSARY.md:\| `harvest` \| …` | glossary: defines `harvest` against the WRITE direction (into the store) and denies the read-back-as-rules direction in the same row |

**Added, g5 sweep block** (the block's own header records that the g1 census note's claim *"zero entries sit under skills/"* did not survive contact with the retirement, and restates the narrower property that actually matters):

| entry | reason |
|---|---|
| `docs/agents/ORCHESTRATOR_CONTEXT.md` (tombstone, `episodes/ replaces both`) | the retirement tombstone: names the store as the replacement for the retired playbook, and its only write path, in the act of forbidding a read-and-apply loop |
| `docs/agents/ORCHESTRATOR_CONTEXT.md` (tombstone, write path) | the retirement tombstone: names the store's only write path; the very next clause forbids reading the store back |
| `README.md` | repo README, workflow-artifacts rules: says where a run's record goes and through which write path, and states outright that an episode is never a rule to follow |
| `docs/CONSTELLATION_OVERVIEW.md` | architecture overview, artifact taxonomy row: names the store's write path as the closeout artifact; the row's own text says a record of what happened, never a rule to follow |
| `skills/admiral/SKILL.md` (closeout 1) | admiral closeout step 1: the WRITE path (apply_episode_delta.py --store-root episodes) plus the capture gate that follows it, and it forbids writing a rule in the same breath |
| `skills/admiral/SKILL.md` (closeout 3) | admiral harvest substep: names episodes/ only to explain why a committed episode needs NO harvesting before a worktree sweep |
| `skills/admiral/references/fleet-doctrine.md` (preamble) | fleet doctrine preamble: names the episode store in order to DENY it as a home for fleet rules and to deny reading it back as one |
| `skills/admiral/references/fleet-doctrine.md` (harvest) | fleet doctrine harvest rule: names episodes/ only to explain why the run's episodes are the exception that needs no harvesting |
| `skills/charter/templates/AGENT_GUIDE.template.md` | charter's repo-orientation template: names the store's write path and the never-by-hand rule; the bullet directly below forbids reading the store back |
| `skills/commander-delegated/SKILL.md` | delegated-commander fenced closeout: names the WRITE path and the capture gate a fenced run must still use before it commits; no read |
| `skills/commander/references/commander-core.md` | commander spine step table, feedback row: names the store's only write path and the capture gate that proves the write landed |
| `skills/workbench/SKILL.md` | workbench layout note: says a run's record lives in the store rather than under .agent-work/, names the write path, and states the record-not-a-rule property |
| `skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md` | constellation-export template field: cites an originating episode id as the export's stable identity -- an identifier reference, not an instruction to read the store |
| `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` | closeout template, episode-capture section: names the write path and the capture gate the Commander confirms passed |
| `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (new header) | superseding header on a retired design record: names where the CURRENT loop lives so a reader of the history is not left following it -- a write path and a denial of the read path, not an instruction to consult the store |

### `tests/data/retired_names.approved.txt` — NEW, 53 entries across 10 paths

Header states the format, why the census exists, the bright line, that it is not a pattern allowlist, that only the content half is approvable, and one open note (below).

**`RETURN.md` (2)** — workstream A's file, not editable from this gate:
1. a finding RECORD naming the two files a merge conflict was confined to
2. a finding RECORD naming where the conflicts that cost real time landed

**`docs/CONSTELLATION_OVERVIEW.md` (1)**
3. the ruling that the playbook is deliberately ABSENT from the artifact taxonomy — it names the retired file in order to record the exclusion, and #447 g5 invariant 8 requires this paragraph to survive

**`docs/RECURSIVE_IMPROVEMENT_DESIGN.md` (33)** — every reason opens *"June 2026 design record"*:
4. audit table row: names where the run retrospective was then written, and records that nothing read it
5. audit table row: names the lesson-disposition gate as it then stood
6. audit table row: names the feedback-invariant verifier as it then stood
7. gap analysis: records that the feedback log was write-only
8. parenthetical: names the gate that force-settled lesson application at the feedback step
9. proposal: names the verifier it would have extended to require a section's presence
10. superseded-block quote: the context-step read and digest injection the design proposed
11. superseded-block quote: names the writer the feedback step then distilled deltas through
12. Loop 2 proposal: names the append-only log half of the split durable store
13. Loop 2 proposal: names the curated-playbook half of the split durable store
14. Loop 2 proposal: the context-step READ this retirement exists to abolish, kept as the record of what was proposed
15. Loop 2 proposal: describes the delta update the playbook would take
16. Loop 2 proposal: names the verifier extension the split would have needed
17. Loop 3 proposal: names the gate that would refuse the feedback advance
18. Loop 5 proposal: the SessionStart digest injection into ad-hoc sessions, kept as history
19. sequencing list: names the read path Loop 2 would have added
20. role survey: names the Reflector role this retirement deleted
21. build list: names the skill it proposed and where it would be wired
22. open question: asks whether the digest injection should be unconditional
23. rejected alternative: names the LLM-editing shape the design refused
24. rejected alternative: names the script that would apply deltas mechanically instead
25. rejected alternative: names the verifier that script was proposed as a sibling of
26. drill proposal: names where the drill link would have been enforced
27. superseded note: records what the writer deliberately did NOT carry
28. concurrency hazard: names the shared log two parallel Commanders would race on
29. concurrency hazard: names the second shared file in that same race
30. resolution: names the trio the durable-root fix made canonical
31. resolution: names the first member of the worktree-local staged trio
32. resolution: names the verifier that accepted the staged shape in lieu of a durable write
33. follow-on: names what the staging script writes
34. follow-on: names the verifier whose accepted layout that script matched
35. ordering constraint: names the file the constraint was about
36. trigger proposal: names the entry-count threshold that would trigger an audit

**`docs/agents/ORCHESTRATOR_CONTEXT.md` (1)**
37. the retirement TOMBSTONE: names both retired files in order to FORBID them and to forbid any successor playbook — this block is where a good-faith agent acting on a stale instruction lands

**`scripts/apply_episode_delta.py` (3)**
38. the surviving store writer's module docstring: records which prior-art contract it inherited (validate-then-apply, all-or-nothing)
39. the surviving store writer: records a deliberate DEPARTURE from the prior art's date stamping
40. the surviving store writer: records that the mandatory non-empty retire reason was inherited, not re-decided

**`scripts/init_work_area.py` (1)**
41. placeholder-token comment: a HYPOTHETICAL example of a skill-dir token carrying hyphens, illustrating the parser's rule; it directs nobody to anything

**`scripts/install_constellation.py` (1)**
42. bundle comment: names, by analogy, which roles ship no script; nothing is installed under that name

**`scripts/stage_feedback.py` (8)**
43. survivor script's docstring: names the durable file the staged layout stood in for. Retained by explicit ruling at #447 g4; no shipped surface directs an agent to this script
44. survivor script's docstring: names the four-file staged layout the script writes
45. survivor script's docstring: names the verifier (deleted at g4) whose accepted shapes the layout was built to match — a record of why the layout is what it is
46. survivor script: the TRIO_FILES constant, the literal filenames it writes into a worktree-local staging dir
47. survivor script: the staged file's own header text, naming the durable destination it was staged for
48. survivor script: the FENCE.md manifest line describing one staged file
49. survivor script: a comment naming the verifier that would have rejected an invalid staged delta
50. survivor script: the write call that creates the staged file, named by its literal filename

**`scripts/verify_episode_captured.py` (2)**
51. the replacement gate's own docstring: names what it replaced, which is the fact that makes the gate's existence legible
52. the replacement gate's own docstring: names the second retired file and the issue that retired both

**`skills/commander/templates/COMMANDER_SPINE.template.json` (1)**
53. commander spine archive.c4: the deny_globs RE-STAGING BLOCK. Both retired path strings are kept here deliberately so a future run cannot re-stage either file — a stronger reason than the one they were added for

**No reason above amounts to "an agent is still told to use the retired thing."** The closest call is `stage_feedback.py`, and I checked rather than assumed: `grep -rn stage_feedback` outside its own tests and the historical design record returns **nothing**, so no shipped surface directs an agent to it. That is recorded as an open note in the census header and filed as a triage candidate below.

---

## Suite count delta, by name

```
$ FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q
5 failed, 1619 passed, 2 skipped, 549 subtests passed in 265.06s
```

Baseline at `77e428d`: **1618 passed, 0 failed**. The arithmetic closes exactly:

| | Δ passed | why |
|---|---|---|
| 3 new tests in `tests/test_retirement_guard.py` | **+3** | invariant 11's coverage |
| `test_canon_episode_store_untouched` passed → failed | **−1** | see below |
| `RealCheckoutSkew::test_a_clean_checkout_differs_only_in_rev_never_in_shape` passed → failed | **−1** | see below |
| `test_canon_is_clean` xfailed → failed | 0 | never counted as passed |
| **1618 + 3 − 2 = 1619** ✓ | | |

**The three failing nodes, by name:**

1. **`tests/test_retirement_guard.py::test_canon_is_clean` — `[XPASS(strict)]`. EXPECTED, and g6's to close.** The tree really is clean now, so the strict-xfail marker inverts and fails the build, which is exactly the design ("scaffolding that cannot outlive the work is the only kind worth leaving in"). **I did not remove the marker.** g6 removes it.

2. **`tests/test_episode_negative_control.py::test_canon_episode_store_untouched`** — asserts `git status --porcelain episodes/` is empty. Invariant 3 *requires* me to edit `episodes/README.md`, so it cannot pass while that edit is uncommitted, and I may not commit.

3. **`tests/test_context_determinism.py::RealCheckoutSkew::…`** (+2 `SUBFAILED` on `scripts/agent_work_root.py`) — declares `scripts/agent_work_root.py` "tracked and unmodified in this worktree" and diffs it against a clean checkout of the same commit. Invariant 5 *requires* the docstring edit there.

**Neither (2) nor (3) is a regression, and I proved it by causality rather than asserting it** — each file was restored from HEAD, the test re-run, and my version put back byte-identically (`.agent-work/epic418-h-447/g5-suite-delta-proof.txt`):

```
=== episodes/README.md
my version sha256 = 7771dc30c58d3ec6f1ae94cd0512e5bfe8cb2bd01caf57871d65e5d31759afb1
WITH my uncommitted edit : exit=1  1 failed in 0.23s
WITH the file at HEAD    : exit=0  1 passed in 0.20s
restored sha256   = 7771dc30c58d3ec6f1ae94cd0512e5bfe8cb2bd01caf57871d65e5d31759afb1  identical=True

=== scripts/agent_work_root.py
my version sha256 = 6b12d15c473da7c21ac348e83105a116a6dc25b6362c9c62e1176d84f4c05d26
WITH my uncommitted edit : exit=1  3 failed, 4 subtests passed in 1.95s
WITH the file at HEAD    : exit=0  1 passed, 6 subtests passed in 1.99s
restored sha256   = 6b12d15c473da7c21ac348e83105a116a6dc25b6362c9c62e1176d84f4c05d26  identical=True

BOTH FAILURES ARE UNCOMMITTED-WORKING-TREE ARTIFACTS; they clear at commit.
```

Both compare against **HEAD**, so both go green the moment the Commander commits. **Commander: re-run these two after committing — that is the confirming measurement I could not take.** I deliberately did **not** edit either test: they are out of scope, and editing a test to accommodate an uncommitted working tree would have been the wrong repair.

Everything else is green:

```
$ FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q \
    --deselect tests/test_retirement_guard.py::test_canon_is_clean \
    --deselect tests/test_episode_negative_control.py::test_canon_episode_store_untouched \
    --deselect 'tests/test_context_determinism.py::RealCheckoutSkew::test_a_clean_checkout_differs_only_in_rev_never_in_shape'
1619 passed, 2 skipped, 3 deselected, 545 subtests passed in 253.31s
EXIT=0
```

---

## Diff summary

```
 22 files changed, 331 insertions(+), 136 deletions(-)
 + tests/data/retired_names.approved.txt   (new, staged with `git add`, 53 entries)
```

`README.md` 4 · `SKILL_INDEX.md` 7 · `docs/CONSTELLATION_OVERVIEW.md` 2 · `docs/EPISODE_STORE.md` 36 · `docs/POSITIONING.md` 3 · `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` 16 (**16 insert / 0 delete**) · `docs/agents/CREW_CONTEXT.md` 9 · `docs/agents/GLOSSARY.md` 4 · `docs/agents/ORCHESTRATOR_CONTEXT.md` 19 · `episodes/README.md` 32 · `scripts/agent_work_root.py` 4 · `scripts/verify_retirement.py` 90 · `skills/admiral/SKILL.md` 22 · `skills/admiral/references/fleet-doctrine.md` 37 · `skills/charter/templates/AGENT_GUIDE.template.md` 4 · `skills/commander-delegated/SKILL.md` 2 · `skills/commander/references/commander-core.md` 2 · `skills/workbench/SKILL.md` 6 · `skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md` 15 · `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md` 10 · `tests/data/store_mentions.approved.txt` 71 · `tests/test_retirement_guard.py` 72

**Line endings.** Every target was CRLF in the working tree (`.gitattributes` sets `* text=auto`). Checked in Python bytes, not `grep` (`grep -c $'\r$'` proved unreliable here — it reported 0 on a file Python measured as 107/107 CRLF). The editor preserved CRLF on most files but flipped three to LF: `tests/data/store_mentions.approved.txt`, `scripts/verify_retirement.py`, `tests/test_retirement_guard.py`. All three were converted back in binary. Final state:

```
mixed/LF-only files: NONE -- every changed file is fully CRLF, as it was at 77e428d
```

**Nothing outside scope was touched.** `episodes/active/` and `episodes/retired/` untouched (no hand edit, no writer run). `RETURN.md` untouched — its two findings went into the census. The four fenced files (`scripts/hooks/gauge_writer_hook.py`, `scripts/hooks/spine_rail.py`, `scripts/gauge_reader.py`, `docs/GAUGE_WRITER_HOOK.md`) untouched. No commit, no push. No subagents dispatched.

---

## Corner cases declined, with their comment site

1. **The PATH half of `retired-name-on-shipped-surface` is not approvable by census.** Deliberate, not an omission. Comment at `scripts/verify_retirement.py`, in `_leg_retired_name`'s docstring and in the violation detail (`"This half is deliberately NOT approvable by census."`).
2. **A prescription split across two lines still escapes every leg**, because all matching is line-scoped. Pre-existing, already recorded in the `KNOWN BYPASSES` block at `scripts/verify_retirement.py:174-184`; my census inherits the same limit and I did not widen it — closing it means a paragraph-level parse this gate does not need.
3. **`CONSTELLATION_FEEDBACK.template.md`'s field is still named `Lesson:` while holding an episode id.** Comment at the site, `skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md:14-18`. Reason: `scripts/collect_feedback.py` is out of scope and reads the field by literal name.
4. **`scripts/stage_feedback.py` is orphaned and still writes retired-named files.** Comment at `tests/data/retired_names.approved.txt`, in the census header's "ONE OPEN NOTE" paragraph — the only site in my scope adjacent to it.

## Triage candidates

- **`CONSTELLATION_FEEDBACK` field rename.** Rename `Lesson:` → `Episode:` in the template *and* `FIELD_MAP` / `_hash12("lesson:"…)` in `scripts/collect_feedback.py` in one change, so one-name-for-one-thing holds without breaking recurrence fingerprinting. Out of g5's scope.
- **`scripts/stage_feedback.py` is orphaned.** It survives by explicit g4 ruling, but after this sweep no shipped surface references it (verified by grep), and it still stages an `AGENT_FEEDBACK.md` + `lessons-delta.json` and names a verifier deleted at g4. Either delete it, or rescope it to the `CONSTELLATION_FEEDBACK.md` export the doctrine now names. Eight of the 53 census entries would go with it.
- **Two suite guards fail on any uncommitted change to the paths they pin.** `test_canon_episode_store_untouched` blankets `git status --porcelain episodes/` (which covers `episodes/README.md`, explicitly not a record), and `RealCheckoutSkew` pins `scripts/agent_work_root.py`. Both make a legitimate in-flight working tree indistinguishable from a defect. Worth narrowing the first to `episodes/active/ episodes/retired/`.
- **`docs/EPISODE_STORE.md:23` still cites `#348`** for a stale-transcript paragraph whose contrast I have now corrected. Someone should check whether #348 can close.

## Unresolved blockers

**None.**

---

## Workflow Feedback

- **The handoff was complete** — task, intent, scope, exclusions, required evidence, test mode, stop conditions and return format were all present, and the eleven invariants were unusually easy to work from because each named a command rather than a feeling. Verifying the frozen list rather than inventing grep proxies was the right instruction and I followed it.
- **Two of the handoff's own acceptance commands were subtly wrong, and I had to correct them rather than obey them.** (a) `git grep -c 'LESSONS.md' -- <file>` prints `path:N` for the working copy but `HEAD:path:N` for the tree, so a naive comparison of the two can never be equal; the check needs to strip to the *last* colon on both sides. (b) `git diff --stat docs/RECURSIVE_IMPROVEMENT_DESIGN.md` "must show ONLY the inserted header" is not machine-checkable as written — `git diff --numstat` with a zero-deletions assertion is. Both are check-text defects, not work defects.
- **Close criterion 8 ("0 failed") is unreachable from a crew seat on this gate, and the handoff could say so.** Two invariants (3 and 5) mandate edits to files that two out-of-scope suite guards pin against HEAD. The only exits are committing (forbidden), editing out-of-scope tests (wrong), or proving the failures are pre-commit artifacts (what I did). A future handoff that mandates edits to `episodes/README.md` or `scripts/agent_work_root.py` should name those two tests up front.
- **The handoff's residual table (~51 across 8 paths) was one path short**: `docs/CONSTELLATION_OVERVIEW.md:98` is required to survive by invariant 8 and therefore also needs approving. Re-deriving rather than trusting the table caught it — which is what the handoff told me to do, so the instruction worked.
- **Engine friction, minor:** the `amend` verb's op kind is `retext-check` / `rescope` / `drop`, but nothing in `--help` lists the legal kinds; I had to read `checklist_engine.py` to find them after `unknown op kind 'set'`. A one-line enumeration in the help text would have saved a round trip.
- **My own error, recorded:** one `amend --reason` string contained backticks and bash command-substituted them, so that amendment's reason lost the words `git grep -c` and emitted a stray `fatal: no pattern given`. The reason is still legible. Engine reason/why strings should be written without backticks on this shell.
- **Windows note worth carrying:** `grep -c $'\r$'` is not a reliable CRLF detector in this Git Bash — it reported 0 on a file Python measured as fully CRLF. Every line-ending claim in this result is from `bytes.count(b'\r\n')`.

## Map Impact

- `struct:docs/agents/ORCHESTRATOR_CONTEXT.md` — **new section** "The Retired Learning Playbook"; this is where `constraint:episodes-are-not-prescriptions` is now written down as doctrine an agent obeys.
- `struct:docs/agents/CREW_CONTEXT.md` — record-stores table drops from three stores to two; the read instruction is gone.
- `struct:docs/agents/GLOSSARY.md` — `harvest` redefined write-side; `episode` de-dangled.
- `struct:episodes/README.md` — the tracked-path argument's premise changed (false → true); the sibling-of-the-playbook section removed.
- `struct:docs/EPISODE_STORE.md` — nine cross-module pointers became property descriptions; the doc no longer depends on a deleted module.
- `struct:scripts/verify_retirement.py` — **new seam**: `parse_approved`/`load_approved` are now census-parameterized and serve two censuses through one parser. New constant `RETIRED_NAME_CENSUS_PATH`. New artifact `tests/data/retired_names.approved.txt`.
- `capability:episode-store`, `capability:run-closeout-learning` — every shipped surface that names the loop now names the write path only.
- `constraint:doctrine-lives-in-docs-agents` — **satisfied in `docs/agents/` itself** for the first time by this gate.
- `constraint:record-stores-never-hand-edited` — unchanged, restated write-side in CREW_CONTEXT.
- `decision:episodes-replace-both` `@grade: settled/human` — honoured; no successor playbook created.
- `decision:untrack-do-not-delete` `@grade: settled/measured` — unchanged.
- `claim:guard-fails-on-purpose` — extended: the new census is red-proved twice (entry removal against the real tree, and a two-line decoy).
- **No contradiction with any `settled/human` anchor was found.**
