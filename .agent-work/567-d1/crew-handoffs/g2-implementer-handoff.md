# Implementer Handoff

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g2-implement` — Sweep the corpus and invert the mandate. **Two halves of one gate**, because
doing either alone leaves the suite red.

## Task

Issue **#559**: *the door is the interface, not a second path — remove the CLI fallback for agents.*
The human's ruling, verbatim, is the thing you are enforcing:

> **"the agents should not know about the CLI. period."**

This text has been **deleted twice and has grown back twice**. Gate `g1` established *why*, and it
is the single most important fact in this handoff:

> **The regrowth has a mechanism, and it is a test.** `tests/test_mcp_adoption.py` currently
> **requires** the text you are about to delete, across a measured **nine** assertions. A lane
> deleted the clauses, the suite went red on a test whose own failure message says *"the CLI door
> must stay, never be removed or discouraged"*, and the lane put the text back believing it had
> broken a rule.

So the deletion is not the hard part. Inverting the mandate is. Do both, in this one gate.

The guard from `g1`, `tests/test_cli_retirement_guard.py`, is already in the tree and already RED.
It is your target state: **your work makes it go green as a consequence**, not by editing it.

## Protected Intent

- **No agent is left stranded.** The epic removes the CLI as an *agent-facing path*, not as a tool.
  Operator and debug use stays. Replacement wording names the path that actually works — it does
  not delete a sentence and leave the reader with no answer. `skills/_shared/global-everyone.md`:
  *"Fail visibly rather than emit plausible wrong output; no hidden fallback."*
- **`test_mcp_adoption.py` keeps its own two rules**: the corpus is WALKED, never listed; and no
  assertion may be satisfied by the negation of what it pins.
- **The door-tool-named-affirmatively halves stay exactly as strict.** You are inverting the
  CLI-presence halves only. A two-sided test becomes a one-sided test that still pins the door.

---

## Half (a) — THE SWEEP

### The exact census, measured at base `f05a3d78` and re-verified by the g1 guard

**13 `CLI fallback` clauses in this lane's files** (a 14th, 15th and 16th match exist under
`skills/workbench/**` — **lane D2's**, see Fenced below):

| # | Site |
|---|---|
| 1 | `skills/admiral/templates/ADMIRAL_SPINE.template.json` `.tasks.init.imperative` |
| 2 | `skills/admiral/templates/ADMIRAL_SPINE.template.json` `.tasks.closeout.imperative` |
| 3 | `skills/charter/SKILL.md:12` |
| 4 | `skills/commander/references/commander-core.md:127` |
| 5 | `skills/commander/templates/COMMANDER_SPINE.template.json` `.tasks.init.imperative` |
| 6 | `skills/commander/templates/COMMANDER_SPINE.template.json` `.tasks.plan.imperative` |
| 7 | `skills/commander/templates/COMMANDER_SPINE.template.json` `.tasks.archive.imperative` |
| 8 | `skills/explorer/SKILL.md:31` |
| 9 | `skills/explorer/templates/EXPLORER_SPINE.template.json` `.tasks.init.imperative` |
| 10 | `skills/explorer/templates/EXPLORER_SPINE.template.json` `.tasks.route.imperative` |
| 11 | `skills/interrogator/SKILL.md:26` ← **second-checklist site, reword** |
| 12 | `skills/write-a-skill/templates/gated-engine-SKILL.template.md:15` ← **second-checklist site, reword** |
| 13 | `skills/write-a-skill/templates/survey-SKILL.template.md:11` ← **second-checklist site, reword** |

**9 agent-facing `<engine>` lines carrying 10 occurrences.** Watch the one that is not
one-per-line: `skills/commander/templates/COMMANDER_SPINE.template.json` `.tasks.archive.imperative`
carries **two** — `<engine> waive archive --cond c4 ...` **and** `CLI fallback: <engine> release ...`.
**Edit both.** A one-per-line sweep leaves one behind. The other eight are one each, at:
`ADMIRAL_SPINE` init and closeout, `commander-core.md:127`, `crew-dispatch.md:35`,
`COMMANDER_SPINE` init and plan, `EXPLORER_SPINE` init and route.

**Also swept by the guard's third pattern:** command-shaped `checklist_engine.py` invocations at
`skills/charter/SKILL.md:12`, `skills/explorer/SKILL.md:31`, `skills/interrogator/SKILL.md:26`,
`skills/write-a-skill/templates/gated-engine-SKILL.template.md:15`,
`skills/write-a-skill/templates/survey-SKILL.template.md:11`. The guard leaves **bare prose
mentions** alone (a scripts manifest, "an epic that rewrites `checklist_engine.py`") — you may keep
those. What you may not keep is a path, an interpreter, or a flag next to it.

Run the guard to get the live list rather than trusting this table alone:
`python3 -m pytest tests/test_cli_retirement_guard.py -q`.

### The 10 bound-spine clauses — replace with the real agent path

For these, the door genuinely works and the CLI line is dead weight. The replacement states what an
agent actually does:

- A role's **own** spine is bound at launch: a dispatched crew is started by
  `run_crew.py --backend cli --spine`, which sets `SPINE_FILE` and an assignment-keyed
  `SPINE_SESSION`, so the door resolves to that crew's own spine and needs **no session id
  argument**.
- The **Agent-tool path binds nothing** and is refused rather than silently accepted (#432).

### The 3 second-checklist clauses — REWORD, do not delete

Sites 11, 12, 13. **The door provably cannot reach these**, measured in a fresh process:

| Step | Result |
|---|---|
| `spine_lease claim` on own spine | OK |
| `spine_bind` to a second checklist **while holding the lease** | **REFUSED** — *"one door drives one spine at a time"* |
| release the lease, then `spine_bind` | succeeds |

And the escape in step 3 is barred: `COMMANDER_SPINE.archive` requires the lease to cover every
journaled action, so an agent that released its lease to bind a second checklist fails its own
closeout. This is the case of an Interrogator's `interrogation.json`, an in-session crew's own plan
or survey, and a Commander's `execute.json`. **Confirmed independently: lanes F and H each drove
their `execute.json` under a hand-supplied CLI session id, and lane E's implementer drove its
`IMPLEMENTER_PLAN.json` the same way. Every child plan in this system is driven off-door.**

**The Admiral's ruling, which you implement:** sweep all 13 — no `CLI fallback` clause survives —
but for these three, **replace the clause with a statement of the measured truth**: this checklist
is not the one your door is bound to, and here is the path that does work. Do not delete an agent's
only path and leave it with nothing; that trades a documentation problem for a hidden-fallback
problem.

**Carry this framing into the wording:** *"'CLI fallback' is the wrong word, because a fallback
implies a working primary."* There is no primary here.

**The pattern constraint you must respect while doing it:** the guard's invocation pattern flags a
path, an interpreter, or a flag next to `checklist_engine.py`. So the reworded text may **name** the
engine as the thing that drives a second checklist, but **must not show the command**. If you
conclude the wording genuinely needs to show a command, **stop and return** — that is a deliberate
decision for the Commander, not a reason to patch the pattern.

---

## Half (b) — INVERT THE MANDATE

`tests/test_mcp_adoption.py` and `tests/data/store_mentions.approved.txt` are **yours this wave**
(the Admiral granted ownership explicitly; they were an omission in the original order). No other
lane touches them.

The **nine** mandating assertions, verified present at these lines today:

| Line | Assertion | Target |
|---|---|---|
| 737 | `TestTier1ImperativeFields::test_field_still_carries_cli_fallback` | 7 imperative fields — **all this lane's** |
| 784 | `TestTier1CommanderCoreAttachLine::test_paragraph_still_carries_cli_fallback` | `commander-core.md` — **this lane's** |
| 834 | `TestTier2SkillBodyDefaultPath::test_file_still_names_cli_at_all` | `TIER2_SKILL_FILES` — 3 this lane's + `skills/workbench/SKILL.md` |
| 950 | `TestTier3ChecklistEngineReference::test_still_names_cli_invocation` | `skills/workbench/references/checklist-engine.md` — **lane D2's** |
| 954 | `TestTier3ChecklistEngineReference::test_door_section_itself_keeps_the_cli` | same, **lane D2's** |
| 1132 | `TestTier4AuthoringTemplate::test_file_still_names_cli_at_all` | both `write-a-skill` templates — **this lane's** |
| 1149 | `TestTier5DoNotTouch::test_still_names_checklist_engine_as_artifact` | `global-everyone.md`, `fleet-doctrine.md` |
| 1324 | `TestCLIStaysAvailableNotDeprecated::test_the_canonical_cli_sentence_is_present_verbatim` | `skills/workbench/references/checklist-engine.md` — **lane D2's** |
| 1345 | `TestCLIStaysAvailableNotDeprecated::test_default_path_paragraph_states_the_cli_is_still_available` | Tier2 + Tier4 files |

**The precedent to generalize is already in this file, at line 838:**
`TestTier2SpineAlreadyBoundForDispatchedCrews` asserts *absence* for two files
(`test_file_never_names_the_cli_at_all`) and pins the same human ruling verbatim. Your inversion is
that precedent widened — **say so in the code**, so a future reader sees continuity rather than a
reversal.

### Rules for the inversion

1. **Turn each CLI-presence assertion into an absence assertion**, or delete it where the new guard
   already covers the same ground. Prefer inversion where the file survives and the assertion still
   says something; prefer deletion where the assertion's whole premise is gone.
2. **Where the target is another lane's file** (`skills/workbench/**`, rows 950/954/1324 and the
   `skills/workbench/SKILL.md` entry in `TIER2_SKILL_FILES`), **deleting the mandate is correct and
   sufficient.** Do not invert it into an absence assertion: those files still carry the text today,
   lane D2 deletes them and has not merged yet, and an inverted assertion would go red on a file you
   are fenced from. Coverage is not lost — `tests/test_cli_retirement_guard.py` already asserts
   absence over the whole corpus including `skills/workbench/**`. **Say in your result exactly which
   assertions you deleted for this reason.**
3. **`TestTier5DoNotTouch` (1149) most likely survives unchanged.** It asserts only that
   `checklist_engine.py` is *named as an artifact* in two files — a bare prose mention, which the
   guard deliberately leaves alone. Read it, decide, and state your reasoning either way.
4. **`TestTier3CLIOnlyVerbsStayCLI` (1040) and `TestCLIOnlyVerbsAcrossEveryInstructionFile` (1163)
   are a different claim** — the gap between engine verbs and door tools — not a fallback mandate.
   Leave them unless they break; if they break, say why.
5. **Keep every door-tool-affirmative half exactly as strict.** `test_field_names_door_tool_as_default`,
   `test_paragraph_names_door_tool`, `test_names_door_tools_as_default`, `test_no_door_tool_name_introduced`
   and their siblings are not yours to weaken.
6. **Then regenerate `tests/data/store_mentions.approved.txt`** — it carries verbatim copies of the
   ADMIRAL closeout and COMMANDER archive imperatives (around lines 122 and 128) and two `<engine>`
   tokens. Find and use its own regeneration path; do not hand-edit it if a generator exists.

---

## Half (c) — THE SPECIFICITY PROOF

This is the point of authoring the guard first, and it is the only proof in this plan that a wrong
pattern would fail. The cold plan critic killed the original version of it as vacuous.

1. On a **scratch edit**, reintroduce a genuine `CLI fallback:` clause **at one of the three
   reworded second-checklist sites** (11, 12 or 13). Show the guard goes **RED** and names that site.
2. **Revert the scratch edit.** Show the guard is **GREEN** on your reworded text itself.

Only a correct pattern passes both: the reworded text and a reintroduction live in the same file,
saying nearly the same thing, and the guard must tell them apart. Paste both runs verbatim.

Confirm a clean tree after the revert (`git status --porcelain`).

## Close criteria

1. `grep -rn -i 'CLI fallback' skills/ --exclude-dir=workbench` returns **nothing**.
2. `grep -rn '<engine>' skills/ --exclude-dir=workbench` returns **nothing**.
3. `python3 -m pytest tests/test_mcp_adoption.py -q` is **green**.
4. `python3 -m pytest tests/test_cli_retirement_guard.py -q` reports failures **only** at sites
   under `skills/workbench/` — nothing else. (It cannot be fully green until lane D2 merges; this
   lane merges last and `g5-final` re-runs it on the rebased tree. **This is expected, measured, and
   has a named cause — it is not a defect for you to fix.**) Prove it with:
   ```sh
   python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g2-guard.log 2>&1
   grep -oE '(skills|specs)/[A-Za-z0-9_./-]+' /tmp/g2-guard.log | grep -v '^skills/workbench/' | sort -u
   ```
   That last command must print **nothing**.
5. The specificity proof of half (c) is pasted verbatim, both directions, and the scratch edit is
   reverted.
6. `scripts/init_work_area.py:24` and
   `docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59` are **untouched**.
7. Every edited `.json` still parses (`json.load`).

## Allowed scope

- `skills/**` **except** `skills/workbench/**`
- `tests/test_mcp_adoption.py`, `tests/data/store_mentions.approved.txt`
- Nothing else.

## Fenced — do not edit, another lane owns it this wave

| Path | Owner |
|---|---|
| `skills/workbench/**`, `scripts/install_constellation.py`, `scripts/verify_skill_registered.py`, `scripts/measure_overread.py`, `docs/agents/CREW_CONTEXT.md` | lane D2 |
| `scripts/mcp_spine_server.py`, `episodes/**` | lane E |
| `scripts/run_crew.py` | lane F |
| `scripts/checklist_engine.py` | lane H |
| `map/INDEX.md` | the Admiral |
| `tests/test_cli_retirement_guard.py` | gate `g1` — **do not edit the guard to make your work pass** |

## Constraints

1. **Edit shipped compact-format JSON templates as RAW TEXT.** Never round-trip through
   `json.load`/`json.dump` — it reformats the whole file. Re-validate with `json.load` afterwards.
2. **Do not edit `docs/superpowers/**` or `episodes/**`** to make a count come out right. They are
   historical records; editing one falsifies the record.
3. **No exception list** anywhere, and **do not edit the guard**. If the guard fires on text you
   believe is legitimate, that is a finding to report, not a pattern to widen.
4. `episodes/` has exactly one write path, `scripts/apply_episode_delta.py --store-root episodes`.
   You should not need it.
5. Do **not** promote any observation into `docs/agents/*` — that is the human's call.
6. File **no** issues. Stage triage candidates as files under
   `.agent-work/567-d1/triage-candidates/`.

## Map anchors (inbound)

No architecture map exists in this repo (`map_orient` → `DEGRADED-UNPARSEABLE`). Entry points:

- **`tests/test_mcp_adoption.py:838`** — `TestTier2SpineAlreadyBoundForDispatchedCrews`, the
  in-tree precedent your inversion generalizes. **Read this first.**
- `tests/test_mcp_adoption.py:695–724` — `TIER1_JSON_FIELDS`, the 7 imperative fields and their
  exact pinned CLI command lines.
- `tests/test_cli_retirement_guard.py` — the guard, its three patterns, and its docstring listing
  what it deliberately does **not** enforce.
- `.agent-work/567-d1/notes-1.md` — the measured baseline, the second-checklist probe, the site
  enumeration.
- `.agent-work/567-d1/crew-handoffs/g1-implementer-result.md` — the guard's verbatim RED output with
  every site, and two census refinements you must not re-derive.

## Deliverable path check

`git check-ignore` returns exit 1 (not ignored) for `skills/`, `tests/test_mcp_adoption.py`,
`tests/data/store_mentions.approved.txt`, and
`.agent-work/567-d1/crew-handoffs/g2-implementer-result.md`. Verified.

## Verification commands

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
grep -rn -i 'CLI fallback' skills/ --exclude-dir=workbench          # expect: nothing
grep -rn '<engine>' skills/ --exclude-dir=workbench                 # expect: nothing
python3 -m pytest tests/test_mcp_adoption.py -q                     # expect: green
python3 -m pytest tests/test_cli_retirement_guard.py -q             # expect: red ONLY on skills/workbench/
python3 -c "import json,glob; [json.load(open(p)) for p in glob.glob('skills/**/*.json', recursive=True)]"
git status --porcelain
```

The gate's own closing check, which the Commander re-runs independently:

```sh
set -o pipefail
test -z "$(grep -rn -i 'CLI fallback' skills/ --exclude-dir=workbench || true)" \
  && test -z "$(grep -rn '<engine>' skills/ --exclude-dir=workbench || true)" \
  && python3 -m pytest tests/test_mcp_adoption.py -q >/dev/null 2>&1
```

## Test mode

**Inversion-first.** The guard is already RED and is the specification. Do not edit it; make it go
green (outside `skills/workbench/`) by changing the corpus and the mandate.

## Required evidence

- The full swept diff, with the replacement wording for each of the 13 sites.
- For the 3 reworded sites: the before and after text, quoted.
- The list of `test_mcp_adoption.py` assertions inverted vs deleted, with the reason for each.
- Half (c)'s specificity proof, both directions, verbatim.
- The `grep -oE ... | grep -v '^skills/workbench/'` output showing nothing outside D2's files.

## Suggested model tier

**Opus**, elevated reasoning effort. This is the epic's headline diff and the wording is doctrine
that ships to every agent in the corpus.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1).

## Stop conditions

Stop and return if: the reworded wording for a second-checklist site genuinely needs to show a
command line (a Commander decision, not a pattern to widen); an assertion cannot be inverted without
weakening a door-affirmative half; the sweep would require editing a fenced file; or the guard fires
on text you believe is legitimate outside `skills/workbench/`.

## Return format

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/567-d1/crew-handoffs/g2-implementer-result.md` **before ending your turn** — that write
is the delivery. Include a `Return status` field whose value is exactly `complete` (lowercase) when
the close criteria are met. Include a `Workflow Feedback` section: what helped, what got in the way,
and your own mistakes.
