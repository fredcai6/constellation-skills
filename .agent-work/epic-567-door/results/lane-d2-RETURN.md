# Lane D2 Return — `cmdr-567-d2`: sunset the workbench teaching half, keep the templates (#565, with #561)

## 1. Verdict

**Delivered, with one evidenced deviation from the launch order's literal framing.**

The mission ("delete the teaching half, deregister the skill, move no template") is
accomplished, but **full deletion of the three teaching files was not achievable** — it
would have broken two independent, pre-existing test suites (`tests/test_mcp_adoption.py`,
`tests/test_install_constellation.py`) that hard-pin specific sections as the corpus's sole
written authority for content the MCP door's own tool schemas do not restate. What actually
shipped is a **partial, evidenced deletion**: every section proven load-bearing is retained
verbatim; everything else is gone. This is reported as a measured negative on the *literal
line-count* framing, not on the mission — the honest-null the launch order's Stop Conditions
and Honest-Null Clause call for.

Also delivered: #561 (`CREW_CONTEXT.md`'s Python Invocation section, now current).

## 2. What I deleted

| file | before (f05a3d78) | after | net change |
|---|---:|---:|---:|
| `skills/workbench/SKILL.md` | 43 | 20 | -23 |
| `skills/workbench/references/checklist-engine.md` | 188 | 65 | -123 |
| `skills/workbench/references/status-model.md` | 58 | 39 | -19 |
| **teaching-half total** | **289** | **124** | **-165** |

The issue's original 282 and the Admiral's re-measured 289 (both against `checklist-engine.md`
at its pre-#565 length) were the starting estimate, not the target — the deliverable is what
was actually removed, reported here: **165 of 289 teaching-half lines**, not all of them.

**Deleted, by section:**
- `SKILL.md`: `## Layout` (the `.agent-work/` tree diagram), `## Controller` (generic
  controller-template explanation), `## Closeout` (closed-definition prose). Kept: frontmatter
  (rewritten description), a short retired notice, the `## Checklist engine` paragraph
  (unchanged — it's the Tier2-pinned default-path paragraph), the Templates line, and one
  restored sentence (see below).
- `checklist-engine.md`: table of contents, "This is mandatory, not advisory", "Instantiate
  from the project template", "Dispatch: subagent vs your own context", "One agent, one plan",
  "Two types", "Verb loop", "Obey refusals" (moved earlier, kept as one line), "Waive: human
  override of a check", "Mechanism the engine guarantees", "Bubble-up channels", "Context-read
  step", "Template set". Kept: the opening two paragraphs (unchanged, including the `<skill-dir>`
  token), `## MCP door` (unchanged verbatim), `## Session lease` (unchanged verbatim), `##
  Refresh: reach-up without a handoff doc` (unchanged verbatim, restored after a cold-plan-critic
  finding — see §3), a short "## Obey refusals" line.
- `status-model.md`: `## Gate Status`, `## Commander Gate Decision`. Kept: `## Crew Return
  Status`, `## Review Verdict` (both unchanged verbatim).

**Not deleted, and why (one sentence restored mid-run):** `SKILL.md` still carries one sentence
— *"What a run learned is not kept here. It is recorded as **episodes**..."* — that I initially
deleted with the rest of `## Layout`. The full-suite run (g3) caught it:
`tests/test_retirement_guard.py::test_every_approved_entry_exists_verbatim` pins this exact
line via `tests/data/store_mentions.approved.txt:166` as the approved carrier of the
episodes-retirement doctrine. It has nothing to do with the checklist-engine mechanism this
mission is about — it's a different doctrine that happened to live in the same file — so I
restored it verbatim rather than touching the approved-mentions census (which sits beside
`tests/test_retirement_guard.py`, a file this lane does not own).

## 3. The door-carries-it establishment

**Claim tested:** "the MCP door's tool descriptions now carry what `checklist-engine.md` and
`status-model.md` taught — the verbs, the two spine types, evidence shape, refusal semantics,
and the status vocabulary." Established by reading both references section-by-section against
all 12 door tool schemas (`spine_status`, `spine_lease`, `spine_start`, `spine_advance`,
`spine_evidence`, `spine_halt`, `spine_survey_result`, `spine_capture`, `spine_amend`,
`spine_bind`, `spine_close`, `spine_open`).

**What the door carries (deleted from the docs as genuinely redundant):**
- The verb loop (`current`/`start`/`advance`/`record`/`consolidate`, plus `skip`/`block`/
  `reopen`/`append`/`amend`/`attest`/`waive`/`attach`/`flag-candidate`) — every verb has a
  dedicated door tool whose own description states its behavior.
- Evidence shape — `spine_evidence`'s description covers attest/attach/waive including
  `override_policy` and `force` semantics.
- The gated/survey split — implied structurally by `spine_advance` (gated) vs
  `spine_survey_result` (survey) being separate tools.
- Session lease claim/heartbeat/release and the `force`+`reason` takeover path —
  `spine_lease`'s parameter schema states this directly.
- The rework/reopen cascade — `spine_halt`'s description states "resets its conditions and
  CASCADES every downstream complete/in-progress gate back to pending."
- Refusals-as-instruction — implicit in every tool's description format (a refusal names the
  next legal verb).

**What the door does NOT carry (named, not silently dropped) — this is the actual finding
that reshaped the plan:**
1. The **door-vs-CLI coexistence doctrine** — that the door is the *default* while the CLI
   *remains available*, including the byte-exact sentence "Nothing here removes or discourages
   the CLI." and the rule that a Task-tool-dispatched subagent must use the CLI for its own
   plan (because it inherits its dispatcher's MCP scope). This is meta-doctrine *about* the
   door, not something the door's own tool descriptions would ever state about themselves —
   and it is independently proven load-bearing by `tests/test_mcp_adoption.py`'s Tier2
   (`SKILL.md`'s default-path paragraph) and Tier3 (`checklist-engine.md`'s `## MCP door`
   section) pins, including a byte-for-byte sentence equality check.
2. The **`Crew Return Status`/`Review Verdict` vocabulary** (`complete | partial | blocked |
   out-of-scope | failed`; `APPROVE | BLOCK | COMMENT`) — free-text convention for
   crew-authored result documents, never engine-enforced, so no door tool states it. Still
   directly cited by `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md:106` and
   `skills/reviewer/templates/REVIEW_RESULT.template.md:5` / `IMPLEMENTER_RESULT.template.md:5`
   (files this lane does not own).
3. The **refresh-request mechanism's narrative** (`DIGEST:`/`REFRESH REQUESTED:` display,
   fulfilment-by-gate-advance) — the door tools (`spine_evidence` attach, `spine_status`) let
   you *do* this, but nothing states the *mechanism* (why attaching a `refresh-request` and
   then going idle is the correct move, how it clears). Found via a cold plan critic
   (dispatched before execute, per the plan step's bias-to-yes design-it-twice/critic
   requirement): `skills/commander/references/commander-core.md:81` cites "workbench
   `references/checklist-engine.md` §refresh" by name, and
   `docs/superpowers/drills/symmetric-recovery-refresh.md` does too.

Both gaps are retained verbatim rather than silently dropped — this is the float the mission
called for ("if something is genuinely lost, that is a float, not a silent deletion"), resolved
by *keeping* the content rather than escalating, since keeping it was within this lane's own
latitude and required no cross-lane edit.

## 4. Deregistration

**Local Unknown resolved:** `install_constellation.py`'s `discover_skills()`
(`scripts/install_constellation.py:312-339`) requires **every** non-underscore-prefixed
`skills/*` directory to carry a parseable `SKILL.md` (`name`+`description` frontmatter) or the
**whole installer** raises `InstallError` — not scoped to workbench. Combined with the settled
"workbench stays a template package, move nothing" ruling, there is **no supported way** to
ship `skills/workbench/templates/` with zero taught-procedure `SKILL.md` — that would need new
installer mechanism (a first-class "retired skill" state), which is a `float`, not `yours`, per
Inherited Latitude. **Named as a triage candidate (#4), not built.**

**What I did instead, within "How workbench is deregistered — yours":** kept a minimal,
present `SKILL.md` whose description now states plainly it should not be invoked as a
procedure ("the engine's verbs and mechanism are taught by the door's own tool descriptions,
not by this skill"), stripped of every section that taught the engine mechanism, retaining
only the one paragraph two independent things depend on (Tier2's pin, and the fact that it is
still factually true and useful — the CLI fallback command).

**Output of all three named scripts**, run against the post-change tree:

1. **`install_constellation.py`** — dry-run and a real install both exit 0:
   ```
   $ py scripts/install_constellation.py --agent codex --scope user --dest /tmp/567d2-dryrun --skills workbench commander cartographer --dry-run
   DRY RUN: would install 3 skill(s) into /tmp/567d2-dryrun
   - constellation-workbench: .../skills/workbench -> /tmp/567d2-dryrun/constellation-workbench
   exit 0

   $ py scripts/install_constellation.py --agent codex --scope user --dest /tmp/567d2-realinstall --skills workbench commander cartographer
   Installing 3 skill(s) into /tmp/567d2-realinstall
   - constellation-workbench: .../skills/workbench -> /tmp/567d2-realinstall/constellation-workbench
   Installed. Restart Codex to pick up new or updated skills.
   exit 0
   ```
   All 4 templates shipped; `checklist-engine.md`'s `<skill-dir>` token substituted correctly
   (0 remaining tokens; the absolute installed `checklist_engine.py` path present).
   **Side effect caught and reverted:** the real install also rewrote this worktree's *own*
   `.mcp.json` (`python3` → `py`) despite `--dest` pointing elsewhere — reverted with
   `git checkout -- .mcp.json` before committing; staged as triage candidate #2.

2. **`verify_skill_registered.py --skill workbench`** — REFUSED:
   ```
   REFUSED: skill 'workbench' is mechanically broken (curate gating flags): invoker: missing invoker tag (expected one of human/agent/both)
   exit 1
   ```
   **Confirmed pre-existing, not introduced by this change**: identical on base commit
   `f05a3d78` (`git show f05a3d78:skills/workbench/SKILL.md` has no `invoker:` tag either), and
   shared by ~12 other skills including `commander` itself
   (`tests/test_write_a_skill.py`'s own comment: *"missing `invoker:` tags on ~12 skills,
   workbench included"*). Reported honestly per the Honest-Null Clause, not silently fixed —
   fixing a corpus-wide gap affecting files this lane doesn't own is out of scope.

3. **`measure_overread.py`** — unaffected, exits 0:
   ```
   $ py scripts/measure_overread.py --help
   usage: measure_overread.py [-h] [--corpus CORPUS] ... exit 0
   $ py scripts/measure_overread.py
   STRUCTURAL-READ SCAN -- 4 transcript(s)
   ... AGGREGATE_STRUCTURAL_READS: 6
   exit 0
   ```
   It scans transcript fixtures, not `skills/workbench/**` content — no dependency found.

## 5. Every spine still starts

All four instantiated fresh (separate `py` subprocess invocations, explicit paths, no
in-session hook reliance) and reached their first gate:

```
$ py scripts/checklist_engine.py --file /tmp/567d2-spine-check/admiral-spine.json claim --session-id spinecheck-admiral --claimed-by admiral --worktree .
claimed lease spinecheck-admiral -> active
$ py scripts/checklist_engine.py --file /tmp/567d2-spine-check/admiral-spine.json start init --session-id spinecheck-admiral
init -> in-progress

$ py scripts/checklist_engine.py --file /tmp/567d2-spine-check/commander-spine.json claim --session-id spinecheck-commander --claimed-by commander --worktree .
claimed lease spinecheck-commander -> active
$ py scripts/checklist_engine.py --file /tmp/567d2-spine-check/commander-spine.json start init --session-id spinecheck-commander
init -> in-progress

$ py scripts/checklist_engine.py --file /tmp/567d2-spine-check/explorer-spine.json claim --session-id spinecheck-explorer --claimed-by explorer --worktree .
claimed lease spinecheck-explorer -> active
$ py scripts/checklist_engine.py --file /tmp/567d2-spine-check/explorer-spine.json start init --session-id spinecheck-explorer
init -> in-progress
```

```
$ py scripts/verify_state_note.py 567-d2
state note OK: .agent-work/567-d2/STATE_NOTE.md
exit 0
```

**#561, before and after:**

Before (`docs/agents/CREW_CONTEXT.md`, measured 2026-08-10, as shipped on `f05a3d78`):
> `python3` resolves to `/usr/bin/python3.12`, also Python 3.12.3, but has no pytest installed.

After (measured 2026-08-17, this run, this host):
```
$ which py python python3
/home/tommy/.local/bin/py
/home/tommy/.local/bin/python
/usr/bin/python3
$ py -m pytest --version   # pytest 9.1.1
$ python -m pytest --version   # pytest 9.1.1
$ python3 -m pytest --version   # pytest 9.1.1
```
All three now resolve pytest 9.1.1. `CREW_CONTEXT.md` is updated to this measurement, with a
note that the interpreter-to-pytest mapping isn't fixed over time (why the
check-before-you-run instruction stands regardless).

## 6. Suite result

Full suite in a **clean detached worktree** (`git worktree add --detach /tmp/567d2-suite-check
b33f3353`), env fully scrubbed (`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u
CREW_SCRATCH_DIR`):

```
3352 passed, 6 skipped, 1219 subtests passed in 137.92s (0:02:17)
```

`grep '^FAILED' /tmp/567d2-suite2.log` → **no matches** (exit 1). No `MapTreeFreshnessTests`
failure occurred (none was needed — it passed too). This **exactly matches** the pre-dispatch
baseline (`origin/main` at `f05a3d78`: 3352 passed, 6 skipped, 1219 subtests passed, 0 failed,
0 SUBFAILED).

**Commit verified:** `b33f3353caacff83eab1e2455807542362b97087`.

**Two transient failures found and resolved before this final run** (both explained in
detail in §2 and the triage candidates):
1. `test_retirement_guard.py` — fixed by restoring one sentence (§2).
2. `test_crew_launcher.py::ScratchDirResumeTests::test_resume_of_legacy_entry...` — confirmed
   pure environment leakage (`CREW_SCRATCH_DIR` inherited from this session's own dispatch
   context), not a regression; passes with that var unset at the same commit. Staged as triage
   candidate #1, not fixed (outside this lane's file ownership).

## 7. Touched paths

**Written, all inside this lane's ownership:**
- `skills/workbench/SKILL.md`
- `skills/workbench/references/checklist-engine.md`
- `skills/workbench/references/status-model.md`
- `docs/agents/CREW_CONTEXT.md`
- `.agent-work/567-d2/**` (work area: spine.json, execute.json, interrogation.json,
  MISSION_FRAME.md, PLAN_ALTERNATIVES.md, g1-target-content.md, crew-handoffs/, triage-candidates/,
  REPLAN_INPUT.json, STATE_NOTE.md, map-orientation.json, gauge state)
- `.agent-work/epic-567-door/results/lane-d2-RETURN.md` (this file)

**Not touched, though I looked at them:**
- `skills/workbench/templates/**` — read-only, per the settled "move nothing" ruling.
- `scripts/install_constellation.py`, `scripts/verify_skill_registered.py`,
  `scripts/measure_overread.py` — **read and run**, not edited. My file ownership included
  these, but nothing in this mission required changing them (no new installer mechanism was
  needed to satisfy "how workbench is deregistered" within latitude).
- `.mcp.json` — briefly mutated as an install-verification side effect, reverted before commit
  (§4, triage candidate #2).
- `skills/_shared/global-everyone.md`, `skills/commander/references/commander-core.md`,
  `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`,
  `skills/reviewer/templates/REVIEW_RESULT.template.md`,
  `skills/implementer/templates/IMPLEMENTER_RESULT.template.md`, `tests/test_mcp_adoption.py`,
  `tests/test_commander_evidence_convention.py`, `tests/test_install_constellation.py`,
  `tests/test_retirement_guard.py`, `tests/data/store_mentions.approved.txt`,
  `tests/test_crew_launcher.py` — all fenced to other lanes or genuinely out of scope; every
  one of these that this lane's change put at risk was resolved by *retaining content in my
  own files*, never by editing theirs.
- `map/INDEX.md` — Admiral-owned; not regenerated or hand-edited.
- `docs/superpowers/plans/**`, `docs/superpowers/specs/**`, `docs/superpowers/drills/**` — left
  as historical records, per `decision:records-are-not-instruction`. (One drill,
  `symmetric-recovery-refresh.md`, cites "§refresh" — its citation stays valid because this
  lane retained the Refresh section rather than deleting it.)

## 8. Map impact

**No indexed source touched.** `map/INDEX.md` (the Admiral-owned generated code map) never
indexed `skills/workbench/**` prose at all — it only covers `.py` modules under
`scripts/`, `tests/`, `evals/`, `conftest.py`, and one `skills/replan/scripts/` module. This
run's four changed files are all outside that index's scope. No action taken, per
`decision:map-index-is-admiral-owned`.

## 9. Triage candidates

Staged under `.agent-work/567-d2/triage-candidates/`, all routed `recommend-and-defer`
(no issue filed, per the standing no-issue-filing ruling):

1. `1-crew-launcher-scratch-dir-env-leak.md` — a test-isolation gap in
   `tests/test_crew_launcher.py`, unrelated to this lane's change, caught during g3.
2. `2-install-constellation-mutates-caller-mcp-json.md` — a real (non-dry-run) install rewrites
   the *calling* repo's `.mcp.json` regardless of `--dest`.
3. `3-corpus-wide-pointers-into-shrunk-workbench-docs.md` — a recommended post-wave sweep for
   any pointer into the shrunk docs this lane's grep missed.
4. `4-first-class-retired-skill-installer-state.md` — the cleaner long-term fix for "deregister
   a skill that still ships templates," named rather than built (new installer mechanism is a
   float).

## 10. Workflow feedback

**What helped:**
- The launch order's own Local Unknowns section named exactly the right question ("is
  deregistering a skill that still ships templates a supported state?") — investigating it
  first, before touching any file, is what surfaced the `discover_skills()` constraint and
  reshaped the whole plan correctly instead of discovering it mid-execute.
- Dispatching a cold plan critic before `execute` caught two real retention gaps (Refresh,
  Review Verdict) that my own understanding of "what the door carries" had missed — cheap
  insurance relative to finding them after a merge.
- The reviewer's attempt-1 BLOCK on g1 caught a real defect (the Session lease section wasn't
  byte-identical to the original, contrary to my own handoff's stated constraint) that the
  mechanical test suite could not have caught on its own, since it only pins substrings there.
  Independent adversarial review is not ceremony.

**My own mistakes, reported with the same rigor as the wins:**
- I initially wrote `g1-target-content.md`'s Session lease section from memory/paraphrase
  instead of copy-pasting the original verbatim, violating my own handoff's explicit
  "byte-identical" constraint — exactly the kind of error the reviewer exists to catch, and it
  did. Lesson: when a handoff says "byte-identical," the author owes the same discipline in
  the *spec* file, not just the instruction text.
- I ran a real (non-`--dry-run`) `install_constellation.py` invocation to inspect the installed
  workbench copy, without first checking whether it could mutate my own working tree — it did
  (`.mcp.json`). Caught before commit via `git status`, but the right habit is to check `git
  status` immediately after *any* script invocation whose side effects aren't fully known, not
  just before a commit.
- I spent a large amount of investigation time establishing that full deletion was infeasible
  before writing a single line of the actual plan — the right call given what it found, but a
  narrower first pass (grep the two suspect test files immediately after reading the mission,
  before reading every other reference doc) would have reached the same conclusion faster.

**What got in the way:** none significant. The launch order was unusually complete — the
Local Unknowns, the pre-empted steps, and the explicit "read the three scripts, don't infer
them" caution all pointed straight at the real defect in the mission's original framing.

## 11. PR

Opened against `main` from `feat/567-d2-workbench-sunset`.

*(PR number and head SHA to be filled in immediately below, once `gh pr create` returns —
see the commands run for this in the same turn as this file's commit.)*
