# Implementer handoff — g5: the prose sweep, the doctrine tombstone, and the guard's last leg

**Worktree:** `C:/Programs/constellation-skills-wt/epic418-h-447` · branch `epic-418/h-447-episodes-retirement` · HEAD `77e428d`

## Protected intent

`.agent-work/LESSONS.md` (a playbook agents were told to **read** and condition behaviour on) and
`.agent-work/AGENT_FEEDBACK.md` (a write-only retrospective) are retired. Both are replaced by the
episode store: **a record of what happened**.

Tommy, verbatim, 2026-08-06:

> *"we shouldn't be reading the episodes like lessons, it's a store for things that happened to
> replace both feedback and lessons."*

g2 built the capture gate. g3 rewired both spines onto it. g4 carried the eight live lessons across,
untracked both files and deleted the machinery. **This gate makes the written surface tell the
truth, and gives the guard a way to reach green.**

**The failure mode of a doc gate is an absence-only edit.** A sweep graded purely on "the retired
names are gone" would pass just as happily having deleted the paragraphs entirely. That is why
invariants 7–10 below name what must **survive**, and why you will be graded on those as hard as on
the removals.

---

## What must become true

The invariants are **pre-authored and frozen**. Verify this list; do not invent grep-shaped proxies
for "the document says what it should".

### 1. `docs/agents/CREW_CONTEXT.md:60` — a live prescription in the doctrine directory

It currently says:

> *"Read them with `scripts/query_episodes.py` and the engine's `current` verb."*

**This is the run's governing constraint being violated in `docs/agents/` today** — a standing
instruction to read the store. Remove it. The record-stores table's **`.agent-work/LESSONS.md` row
is deleted**; the `episodes/` row **stays but describes the WRITE path only**.

**Also fix the census entry that approves it.** `tests/data/store_mentions.approved.txt` approves
this exact line under the reason *"names the store's WRITE path and the never-hand-edit rule"* — a
reason written once for a block of four consecutive lines and true of three of them. Fixing the
prose while leaving the wrong reason in the census leaves the guard telling a comfortable lie in
the exact category it exists to catch. **Fix both, and give each line its own reason.**

### 2. `docs/agents/GLOSSARY.md:16` — `harvest`

Currently: *"Reading stored episodes back to act on them."* **"Act on them" is the playbook.**
Either redefine `harvest` against the write path or remove the term.

**Look one line up while you are there.** Line 14 defines `episode` as *"One stored record of
something observed in a run, kept for later harvest."* If you remove or redefine `harvest`, that
definition must not be left dangling or still implying read-and-apply. Not in the frozen list —
report what you did with it either way.

### 3. `episodes/README.md:12` — the argument rests on a false fact

It claims *".agent-work/ is gitignored (see `.gitignore` line 1)"*. **That is FALSE and it is
measurable.** `.gitignore` line 1 is a comment reading *"# .agent-work/ is TRACKED: run artifacts,
verdicts, lessons and archives are durable project history, not scratch"*, and
`git ls-files .agent-work | wc -l` returns **3067**.

The store's "why a tracked path" argument currently rests on a false claim about a file it names by
line number. **Re-found the argument on a true one:** the store must be visible in every worktree
and every clone the moment a commit lands, which a plain tracked repo-root directory gives for free.
Do not simply delete the argument — it is a good argument with a bad premise.

**Also delete the "Not to be confused with" section.** It asserts the store is a **sibling** of the
playbook and that "this run does not touch `LESSONS.md` or its writer" — the exact claim this issue
reverses.

### 4. A TOMBSTONE in `docs/agents/ORCHESTRATOR_CONTEXT.md`

No mechanical leg can catch a **successor playbook that never names episodes**. This block is where
a good-faith agent acting from a stale instruction lands. It must name the **shape** of the
retirement:

- the two files are retired;
- `episodes/` replaces **both** — one store of observations, not two inboxes plus a playbook;
- episodes are **records** and are **never read back as rules**;
- a rule to follow goes in `docs/agents/*`, and putting one there is a human's call;
- there is to be **no successor playbook and no read-and-apply loop**.

Write it as doctrine an agent obeys, not as a changelog entry.

### 5. Every remaining LIVE pointer, repointed or removed

```
README.md:233,254                                        docs/CONSTELLATION_OVERVIEW.md:40
skills/admiral/SKILL.md:60,67,68,70                       skills/commander/references/commander-core.md:60
skills/admiral/references/fleet-doctrine.md:7,162,163,166 skills/commander-delegated/SKILL.md:17
skills/workbench/SKILL.md:16,29                           skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md:29
skills/charter/templates/AGENT_GUIDE.template.md:74,75    SKILL_INDEX.md
docs/POSITIONING.md                                       scripts/agent_work_root.py:4 (docstring)
```

**Line numbers were measured before g4's commit — re-derive them, do not trust them.**
`python scripts/verify_retirement.py` gives you the live list.

### 6. `skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md:22`

Its `Lesson:` field must accept an **episode id** instead of a lesson id — one field, the minimum
that stops the referent dangling. **`CONSTELLATION_FEEDBACK.md` itself is NOT retired.**

---

## What must NOT change — survivors

An absence-only edit passes an absence-only check. These are the other half of the grade.

### 7. `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` — 33 sites stay UNTOUCHED

It gains **only** a superseding header at the top. It is a design **record** of the loop as built in
June 2026, not doctrine. Rewriting it to describe a system it never described would be **falsifying
history**. The header must say plainly that it is history and not instruction, and name where the
current loop lives.

`git diff --stat` on this file must show **only** the inserted header, and
`git grep -c 'LESSONS.md' -- docs/RECURSIVE_IMPROVEMENT_DESIGN.md` must be **unchanged**.

### 8. `docs/CONSTELLATION_OVERVIEW.md:98` — the ruling paragraph SURVIVES

It already rules the playbook out of the artifact taxonomy and is simply true now.

### 9. `docs/superpowers/**` and `tests/fixtures/**` are untouched records

### 10. `docs/EPISODE_STORE.md` — comparative references become descriptions

Its references to `apply_lessons_delta.py` cite a file the reader can no longer open. Turn each into
a description of the **property itself** — *"a validated, all-or-nothing delta writer"* — rather
than a pointer to a deleted module. Nine findings sit in this file; re-derive them.

---

### 11. THE GUARD MUST BE ABLE TO REACH GREEN — this is new, read it fully

**Invariants 1–6 and 10 cannot drive the `retired-name-on-shipped-surface` leg to zero, and they
were never going to.** Invariant 7 *requires* ~33 sites to survive. `archive.c4`'s `deny_globs`
deliberately keeps both retired path strings as a **re-staging block** — a stronger reason than the
one they were added for. `scripts/stage_feedback.py` survives by explicit ruling and names them 8
times.

Measured at `77e428d`: **85 findings**, of which roughly **51** sit on surfaces no invariant here
retires:

```
docs/RECURSIVE_IMPROVEMENT_DESIGN.md 33   scripts/stage_feedback.py 8
scripts/apply_episode_delta.py 3          scripts/verify_episode_captured.py 2
RETURN.md 2                               scripts/install_constellation.py 1
scripts/init_work_area.py 1               skills/commander/templates/COMMANDER_SPINE.template.json 1
```

**The leg has no approval mechanism at all** — `SCOPE_EXCLUSIONS` covers only `tests/` and the guard
itself. So `test_canon_is_clean`'s `xfail(strict=True)` could never XPASS and the scaffolding would
outlive the work. That is the **exact defect g1's own review already caught once** in this run.

**Build one.** A reason-carrying approval census at `tests/data/retired_names.approved.txt`, in the
**same format** as `tests/data/store_mentions.approved.txt` (`# <reason>` line, then one
`<path>:<normalized line>` entry beneath it) and **reusing the same load/normalize machinery** —
`load_approved()`, `ApprovedEntry`, `normalize()`. Do not fork a parallel implementation.

Then approve each residual with an **honest per-line reason**.

**The bright line:** a reason that amounts to *"an agent is still told to use the retired thing"* is
**NOT approvable** — fix the surface instead. Approvable reasons look like: a frozen historical
record; a deny-glob re-staging block; a survivor script naming what it stages; a comment recording
why the retirement was untrack-not-delete.

**Do NOT weaken the leg into a pattern allowlist.** The census names exact sites so anything new
still has to be looked at by a human and given a reason. A glob would make the whole leg decorative.

Add a test in `tests/test_retirement_guard.py` covering the new census the same way the existing
one is covered, **and red-prove it**: show the leg still fires on an unapproved site.

---

## Files in scope

Invariants 1–6 and 10's enumerated files; `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` **header only**;
plus for invariant 11: `scripts/verify_retirement.py`, `tests/data/retired_names.approved.txt`,
`tests/test_retirement_guard.py`, and `tests/data/store_mentions.approved.txt` (for the §1 reason
fix).

**Touch nothing else.** Not the spine templates beyond what invariant 5 names, not `episodes/`
content, not `docs/superpowers/**` or `tests/fixtures/**`.

**Fenced — a concurrent Commander owns these, do not touch:** `scripts/hooks/gauge_writer_hook.py`,
`scripts/hooks/spine_rail.py`, `scripts/gauge_reader.py`, `docs/GAUGE_WRITER_HOOK.md`.

**`RETURN.md` at the worktree root is NOT yours** — it is workstream A's, tracked and inherited.
Its 2 findings go in the census; do not edit the file.

## Constraints

- `python`, **never** `py` — `py` has no pytest here and produces fake greens.
- Prefix suite runs `FORCE_COLOR=0 NO_COLOR=1`. Baseline at `77e428d` is **1618 passed, 0 failed**.
  Without it you get 10 phantom `HARNESS ERROR` failures in `tests/test_mutation_floor.py`
  (Commander-measured, not a regression).
- Windows: `encoding='utf-8', newline='\n'` explicitly on every file write. **Several targets are
  CRLF** — check the bytes before and after; a text-mode rewrite that flips every line ending is a
  defect in its own right.
- `episodes/` is written ONLY through `scripts/apply_episode_delta.py`; `episodes/README.md` is
  ordinary prose and is yours to edit.
- Do not commit. The Commander commits at integrate.
- Use your own session scratchpad for temp files, never `/tmp` — a concurrent Commander shares it.
- Scope discipline (Tommy's standing ruling): build what needs to work and no more. A corner case
  you decline gets a comment **at the code site** naming it and is reported up.

## Required evidence — commands that can genuinely fail

Redirect to a file then `echo $?`; a pipe captures the pipe's exit code.

```
python scripts/verify_retirement.py ; echo EXIT=$?                      # MUST be 0, printing nothing
python scripts/verify_retirement.py | cut -f1 | sort -u                 # MUST be empty
python -m pytest tests/test_retirement_guard.py -q
git diff --stat docs/RECURSIVE_IMPROVEMENT_DESIGN.md                    # MUST show ONLY the inserted header
git grep -c 'LESSONS.md' -- docs/RECURSIVE_IMPROVEMENT_DESIGN.md        # MUST be unchanged vs HEAD
git diff --stat docs/superpowers/ tests/fixtures/                       # MUST be empty
FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q
```

Plus the **red proof for the new census**: point the census at a site it does not approve (or remove
one entry), watch the leg fire, restore, confirm byte-identical.

## Close criteria

1. Invariants 1–6 true, each demonstrated by a command, not by assertion.
2. Invariants 7–9 verifiably **unchanged**; invariant 10 changed **as specified** (descriptions, not
   pointers to a deleted module).
3. The `docs/RECURSIVE_IMPROVEMENT_DESIGN.md` header says it is history, not instruction, and names
   where the current loop lives.
4. The ORCHESTRATOR_CONTEXT tombstone carries all five clauses of invariant 4, written as doctrine.
5. `verify_retirement.py` **exits 0 and prints nothing.**
6. Every census entry — old and new, both files — carries a reason that describes **that line**.
   No entry's reason is "an agent is still told to use the retired thing".
7. The new census test exists and is **red-proved**.
8. `FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` reports **0 failed**, count delta explained by
   name. `test_canon_is_clean` still carries `xfail(strict=True)` at this gate — **g6** removes it,
   so a strict XPASS failure here is expected and is g6's to close. Say so if you see it.

## Report back

`IMPLEMENTER_RESULT` to `.agent-work/epic418-h-447/results/g5-IMPLEMENTER_RESULT.md`: diff summary;
**each of the eleven invariants with the command proving it**; the guard's leg distribution before
and after; the census red proof; the full text of the tombstone and the RECURSIVE_IMPROVEMENT_DESIGN
header (so they can be graded without opening the files); every census reason you wrote; the suite
count delta by name; corner cases not chased with their comment file:line; unresolved blockers (say
"none" explicitly if none); and a **Workflow Feedback** section. Deliver the substance in your final
message.

## Map anchors (inbound)

- **Structural:** `struct:docs/agents/ORCHESTRATOR_CONTEXT.md`, `struct:docs/agents/CREW_CONTEXT.md`,
  `struct:docs/agents/GLOSSARY.md`, `struct:episodes/README.md`, `struct:docs/EPISODE_STORE.md`,
  `struct:scripts/verify_retirement.py`.
- **Capability:** `capability:episode-store`; `capability:run-closeout-learning`.
- **Constraints:** `constraint:episodes-are-not-prescriptions` — **THE constraint, and invariants 1,
  2 and 4 are where it is written down**; `constraint:doctrine-lives-in-docs-agents` — this is the
  gate that makes that true in the doctrine directory;
  `constraint:record-stores-never-hand-edited`.
- **Decisions:** `decision:episodes-replace-both` `@grade: settled/human` — **no successor playbook
  is created**; `decision:untrack-do-not-delete` `@grade: settled/measured`;
  `decision:store-hardening-out-of-scope` `@grade: settled/human` — the store's own content quality
  is a different job. A contradiction with a `settled/human` anchor is a decision candidate to float
  up, not to revise in place.
- **Evidence expectations:** `claim:suite-no-failures`; `claim:guard-fails-on-purpose` — the census
  you build must be shown firing before it is trusted.
