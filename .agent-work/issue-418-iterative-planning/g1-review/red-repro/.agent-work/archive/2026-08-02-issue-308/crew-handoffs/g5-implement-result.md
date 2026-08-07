# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g5-cut-intake-implement` (issue #308, epic-298)

## Completed slice
The lessons bank's **READ** path is cut across all 6 intake sites in 5 files, and the corpus's only
`durable` context-manifest declaration is gone. The **WRITER** is untouched: `apply_lessons_delta.py`,
the Commander spine's `feedback` step and its `verify_lessons_applied.py` check, the `deny_globs`
protection, the Admiral closeout audit, and `skills/lessons-auditor/**` all still work exactly as before.
Every dependent of the removed declaration (two test modules, two comment blocks in
`scripts/episode_capture.py`) was reworked rather than deleted.

## Scope

**Files changed: 8 source files — asserted, not eyeballed.**

```bash
$ git diff --name-only -- skills/ tests/ scripts/ | wc -l
8
$ git diff --name-only -- skills/ tests/ scripts/
scripts/episode_capture.py
skills/admiral/SKILL.md
skills/admiral/templates/ADMIRAL_SPINE.template.json
skills/admiral/templates/LAUNCH_ORDER.template.md
skills/charter/templates/AGENT_GUIDE.template.md
skills/commander/templates/COMMANDER_SPINE.template.json
tests/test_context_manifest.py
tests/test_episode_capture.py
```

`git diff --stat` shows **11** paths. The other three —
`.agent-work/issue-308/{crew-runs.json,execute.json,execute.json.journal}` — are **not mine**: they are
the Commander's engine state, already dirty when I was dispatched. Attribution derived by command, not
by assertion:

```bash
$ git diff .agent-work/issue-308/ | grep -c 'g5-impl-308b'
0        # my session id appears nowhere in them
```

New untracked files from this run: `.agent-work/issue-308/crew-handoffs/g5-implement-plan.json`
(+ `.journal`), `.agent-work/issue-308/issue-308-g5-implement/` (engine evidence dir), and this result.

**Specific exclusions touched:** `no`. Verified per-file, not per-filename:

| exclusion | still present |
|---|---|
| `skills/lessons-auditor/**` | untouched (3 files, 0 diff) |
| `scripts/apply_lessons_delta.py` | untouched |
| `skills/commander/references/commander-core.md:60` | untouched |
| `skills/admiral/SKILL.md:60`, `:67` | untouched (staging / closeout audit) |
| `skills/admiral/templates/ADMIRAL_SPINE.template.json:49`, `:57` | untouched (closeout audit + `verify_lessons_applied.py`) |
| `skills/admiral/references/fleet-doctrine.md:7` | untouched |
| `skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md:22` | untouched |
| `COMMANDER_SPINE` writer trio (`:109` feedback, `:112` verify, `:125` deny_globs) | **all three survive — asserted below** |

## Behavior changed
`yes` — a live agent no longer loads `.agent-work/LESSONS.md`. Concretely: the Commander spine's
`context` step neither instructs reading the bank nor mechanically declares it in `context_refs`, so the
episode-capture manifest no longer resolves it; the Admiral latitude step no longer reads it; launch
orders no longer carry an Active-lessons slot. No writer behavior changed.
`scripts/episode_capture.py` had **comments only** changed — zero behavior delta.

---

## The 6 sites — before and after

### Site 1 — `skills/admiral/SKILL.md:61`  (drop the lessons half, keep platform invariants)
**Before:**
```
- The project's lessons inbox (`.agent-work/LESSONS.md` Active section) and platform invariants ride in every launch order's inherited-context block.
```
**After:**
```
- The project's platform invariants ride in every launch order's inherited-context block.
```

### Site 2 — `skills/admiral/templates/ADMIRAL_SPINE.template.json:22`  (the **`latitude`** task, not `context`)
**Before** (fragment of the imperative):
```
..., then docs/agents/ORCHESTRATOR_CONTEXT.md and the Active section of .agent-work/LESSONS.md if present. In this context, load constellation-interrogator ...
```
**After:**
```
..., then docs/agents/ORCHESTRATOR_CONTEXT.md if present. In this context, load constellation-interrogator ...
```

### Site 3 — `skills/admiral/templates/LAUNCH_ORDER.template.md:57`  (keep the invariants clause)
**Before:**
```
`<Active lessons from .agent-work/LESSONS.md relevant to this mission; platform/technical invariants from the project playbook (encodings, shell quirks, crew-launch rules)>`
```
**After:**
```
`<The platform/technical invariants from the project playbook (encodings, shell quirks, crew-launch rules) relevant to this mission>`
```
The `**Charter-lite carrier:**` sentence on the next line is untouched — the launch order keeps its
doctrine-carrier role, as Protected Intent #2 requires.

### Site 4 — `skills/charter/templates/AGENT_GUIDE.template.md:75`  (read goes, write path stays)
**Before:**
```
- The curated lessons playbook at `.agent-work/LESSONS.md` is its bounded, distilled derivative: read the Active section before planning; update it only through `apply_lessons_delta.py` structured deltas, never by hand.
```
**After:**
```
- The curated lessons playbook at `.agent-work/LESSONS.md` is its bounded, distilled derivative. It is a staging bank an audit drains, not planning input for a live run — agents write to it only through `apply_lessons_delta.py` structured deltas, never by hand.
```
Decision I made (handoff left the wording to me): I replaced the read instruction with a *positive*
statement of what the bank now is, rather than just deleting a clause, so a Charter-compiled guide still
tells an agent why it does not read the file. The wording deliberately contains no token `read` anywhere
before the filename, so it cannot re-trip the guard's broadest marker (`[Rr]ead[^\n]{0,120}LESSONS\.md`).

### Site 5 — `skills/commander/templates/COMMANDER_SPINE.template.json:22`  (`context` imperative)
**Before** (fragment):
```
... do not treat those paths as guaranteed to exist. Read the Active section of .agent-work/LESSONS.md if it exists: these are distilled workflow lessons from prior runs — condition planning and handoff authoring on them, and note any lesson this run's evidence contradicts (it becomes a disconfirm op at the feedback step). Before you open any source file, resolve and read the map input: ...
```
**After:**
```
... do not treat those paths as guaranteed to exist. Before you open any source file, resolve and read the map input: ...
```

### Site 6 — `skills/commander/templates/COMMANDER_SPINE.template.json:34`  (`context_refs` declaration)
**Before:**
```json
        {"root": "repo", "path": "docs/agents/engine-config.json", "required": false},
        {"root": "durable", "path": ".agent-work/LESSONS.md", "required": false}
      ],
```
**After:**
```json
        {"root": "repo", "path": "docs/agents/engine-config.json", "required": false}
      ],
```

### Over-reach control — the three that had to survive
The handoff's central risk. I did not rely on care; I **measured** it before editing, by running the
guard's six regexes line-by-line over the pre-edit spine:

```
total lines with LESSONS.md: 5
  line 22: markers=['[Rr]ead[^\n]{0,120}LESSONS\.md', 'Active section of[^\n]{0,60}LESSONS\.md', 'read the Active section']
  line 34: markers=['"path":\s*"\.agent-work/LESSONS\.md"']
  line 109: markers=NONE      <- feedback imperative (apply_lessons_delta.py)
  line 112: markers=NONE      <- verify_lessons_applied.py --file
  line 125: markers=NONE      <- git-change-policy deny_globs
```
So the guard was satisfiable by cutting exactly sites 5 and 6, and there was never any pressure toward
the writer. Post-edit state, asserted by command:

```bash
$ grep -c 'LESSONS\.md' skills/commander/templates/COMMANDER_SPINE.template.json
3
$ grep -n 'LESSONS\.md' skills/commander/templates/COMMANDER_SPINE.template.json | cut -c1-40
108:      "imperative": "Before committin      # apply_lessons_delta.py — WRITER
111:        {"id": "c2", "statement": "no thre  # verify_lessons_applied.py — WRITER
124:        {"id": "c4", "statement": "staged   # deny_globs — WRITER
```
The engine check for `m3` additionally asserts each survivor by content, not just by count:
`grep 'LESSONS\.md' <spine> | grep -q 'apply_lessons_delta\.py'` and likewise for
`verify_lessons_applied\.py` and `deny_globs` — all three pass.

---

## Map Impact
- **Structural anchors touched:** `skills/commander/templates/COMMANDER_SPINE.template.json` (the
  `context` task's `context_refs` declaration), `skills/admiral/templates/ADMIRAL_SPINE.template.json`
  (`latitude` task), `skills/charter/templates/AGENT_GUIDE.template.md`,
  `skills/admiral/templates/LAUNCH_ORDER.template.md`, `skills/admiral/SKILL.md`.
- **Capabilities changed:** live-agent lessons intake is **removed**. Agents now condition planning on
  `docs/agents/` + global doctrine only. Lessons *production* (Commander feedback → delta → bank →
  Admiral/Curator audit) is unchanged.
- **Constraints touched:** the `durable` root token in `context_manifest`/`episode_capture` now has
  **zero shipped declarations** corpus-wide. The token, its resolution contract, and the
  double-nesting/repo-root traps all still exist and are still tested — but only against synthetic
  entries. Recorded in the code comments and in both test docstrings so it is not rediscovered.
- **Decision candidates:** the launch-order Inherited Context block is now single-purpose
  (invariants + charter-lite carrier). If a future epic wants per-mission lore in launch orders it will
  need a new carrier, not this one.
- **Trust limitations / drift found:** `episode_capture`'s durable-root trap is now unexercised by any
  shipped data — see Out-of-scope observations.

## Test mode
**Required:** `test-after / guard-led (red → green)` — the handoff shipped the acceptance guard already
authored and RED; that is the red step.
**Satisfied:** `yes` — guard observed red naming all 6 sites before any edit, green after; full suite green.

## Evidence

### 1. `lesson_intake_is_cut.py` — RED before, GREEN after

**RED (before any edit) — exit 1.** Read *which sites it names*, per the handoff:
```bash
$ python .agent-work/issue-308/checks/lesson_intake_is_cut.py
enumerated 11 files under skills/ referencing the lessons bank
  NOTE: skills/admiral/templates/LAUNCH_ORDER.template.md references the bank and is on neither list — review it
  NOTE: skills/charter/templates/AGENT_GUIDE.template.md references the bank and is on neither list — review it

FAIL: read-intake instruction survives in:
  skills/admiral/SKILL.md
      matched: LESSONS\.md[^\n]{0,60}Active section
  skills/admiral/templates/ADMIRAL_SPINE.template.json
      matched: Active section of[^\n]{0,60}LESSONS\.md
  skills/admiral/templates/LAUNCH_ORDER.template.md
      matched: Active lessons from[^\n]{0,60}LESSONS\.md
  skills/charter/templates/AGENT_GUIDE.template.md
      matched: LESSONS\.md[^\n]{0,60}Active section
      matched: read the Active section
  skills/commander/templates/COMMANDER_SPINE.template.json
      matched: [Rr]ead[^\n]{0,120}LESSONS\.md
      matched: Active section of[^\n]{0,60}LESSONS\.md
      matched: "path":\s*"\.agent-work/LESSONS\.md"
      matched: read the Active section
EXIT=1
```
It named **5 files covering all 6 handoff sites** (COMMANDER_SPINE contributes two: the prose marker and
the `"path":` literal). This is the guard reaching a genuine failing state against the real pre-change
tree, not a synthetic mutation — so it is not the "check that cannot fail".

**GREEN (after) — exit 0:**
```bash
$ python .agent-work/issue-308/checks/lesson_intake_is_cut.py
enumerated 10 files under skills/ referencing the lessons bank
  NOTE: skills/charter/templates/AGENT_GUIDE.template.md references the bank and is on neither list — review it
PASS: no live-agent artifact instructs reading the lessons bank
GUARD_EXIT=0
```
Two deltas a reviewer should confirm rather than skim:
- enumeration **11 → 10** files: `LAUNCH_ORDER.template.md` lost its only mention of the bank and so
  drops out of the `git grep -l` enumeration entirely. Nothing was hidden from the guard — the file no
  longer references the bank at all.
- `AGENT_GUIDE.template.md` still emits a NOTE (it is on neither ALLOWLIST nor PARTIAL) and that is
  correct and non-failing: it legitimately retains one write-path mention. The guard's NOTE is advisory.

### 2. Corrected c2 — RED before, GREEN after
```bash
$ python -c "import json,sys; d=json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json',encoding='utf-8')); refs=d['tasks']['context']['context_refs']; sys.exit(2) if not refs else None; bad=[e['path'] for e in refs if 'LESSONS.md' in e['path']]; print('context_refs entries:',len(refs),'| naming LESSONS.md:',bad); sys.exit(1 if bad else 0)"
```
**Before:** `context_refs entries: 6 | naming LESSONS.md: ['.agent-work/LESSONS.md']` → `C2_EXIT=1`
**After:**  `context_refs entries: 5 | naming LESSONS.md: []` → `C2_EXIT=0`

Note the check cannot pass vacuously: `sys.exit(2)` fires if `context_refs` is empty, so deleting the
whole declaration would fail loudly rather than read as clean.

### 3. Full suite
```bash
$ python -m pytest -q
1621 passed, 2 skipped, 540 subtests passed in 404.98s (0:06:44)
```
**Total test count is unchanged** (pre-rework run: `2 failed, 1619 passed` = 1621), which is the
mechanical proof that the rework did **not** delete the tests it reworked.

Mid-change failure distribution, derived by command as required — never from the pytest tail:
```bash
$ python -m pytest -q ... | grep '^FAILED' | sed 's/::.*//' | sort | uniq -c
      1 FAILED tests/test_context_manifest.py
      1 FAILED tests/test_episode_capture.py
```
Both inside the handoff's pre-authorized set; nothing red outside it at any point.

### 4. Confirmatory
```bash
$ python -c "import json,glob; ps=sorted(glob.glob('skills/*/templates/*.json')); assert len(ps)>=5, ps; [json.load(open(p,encoding='utf-8')) for p in ps]; print('parsed',len(ps),'shipped JSON templates')"
parsed 18 shipped JSON templates      # exit 0 — and it asserts what it looped over
```
Both JSON templates were edited **surgically as raw text** (exact-string replacement, no
`json.load`/`json.dump` round-trip): `git diff --stat` shows `ADMIRAL_SPINE.template.json | 2 +-` and
`COMMANDER_SPINE.template.json | 5 +-` — i.e. 1 and 2 logical lines respectively, no reflow.

## TDD evidence, if required
- Failing test observed: the acceptance guard red (exit 1, 5 files / 6 sites) + corrected c2 red
  (exit 1) — both captured against the untouched pre-change tree and attested to `m1-admiral.c1`
  **before** the first edit.
- Passing test observed: guard exit 0, c2 exit 0, `1621 passed, 2 skipped`.
- Refactor while green: `yes` — the stale-claim comment/docstring cleanups in
  `scripts/episode_capture.py` and `tests/test_episode_capture.py` were made with the suite green and
  re-verified green.

## Docs/contracts touched
- `skills/charter/templates/AGENT_GUIDE.template.md` — the doctrine a Charter run compiles into a
  project's agent guide. Consuming repos will get the new wording at their next Charter refresh; existing
  compiled `docs/agents/AGENT_GUIDE.md` files in downstream repos still carry the old read instruction.
  Flagged as a triage candidate below.
- `skills/admiral/templates/LAUNCH_ORDER.template.md` — the Inherited Context contract narrowed.

## Assumptions
- The `durable` root token is **kept** even though nothing declares it. The handoff authorized removing
  the declaration, not the token; removing the token would be a contract change to
  `context_manifest.ROOT_TOKENS` and well outside this gate.
- `git grep -c` counts **lines** containing the string, not occurrences. Every count in this report is a
  line count; each of these files happens to carry at most one mention per line, so the two coincide here.
- For the reworked `test_episode_capture` tests I chose `.agent-work/synthetic-durable.md` as the
  synthetic path (the handoff left this to me). It is deliberately a non-existent file: the resolution
  mechanics under test never stat the target, and a name that cannot be mistaken for a real declaration
  keeps the "stale claim" defect from re-entering by the back door.

## Stop conditions hit
`none` — none of the four fired, and I checked each rather than assuming:
- Cutting a site never required touching the writer/auditor/`apply_lessons_delta.py` — proved by the
  pre-edit marker probe above, not by hope.
- Removing the `durable` declaration broke exactly 2 tests, both pre-authorized, both reworkable without
  a design call.
- The guard went green without weakening it: **I did not modify `lesson_intake_is_cut.py` at all**
  (`git diff --name-only` does not list it; it is not in the changed set).
- Nothing red outside the two named test files at any point.

## Out-of-scope observations
1. **Triage candidate — downstream compiled agent guides still say "read the Active section".** This
   gate changed the Charter *template*. Any consuming repo whose `docs/agents/AGENT_GUIDE.md` was
   compiled before today still carries the read instruction, and the acceptance guard only scans
   `skills/`, so it cannot see them. This repo's own `docs/agents/` has no `AGENT_GUIDE.md` (only
   `CREW_CONTEXT.md` and `ORCHESTRATOR_CONTEXT.md`), so nothing local is affected — but the cutover is
   not complete in the fleet until consumers re-run Charter.
2. **Triage candidate — the `durable` root's silent-trap tests are now synthetic-only.** After this
   change no shipped declaration exercises `resolve_roots`' durable path, so a regression in
   `durable_root`/`durable_agent_work` would be caught only by the three synthetic tests and by nothing
   in real data. That is exactly the situation the handoff anticipated (which is why the tests were
   reworked, not deleted), but it is worth a decision: either the token earns a real declaration again,
   or a later issue removes it. I recorded the state in both the code comments and the test docstrings
   so the next reader does not have to rediscover it.
3. **Handoff correction, measured.** The handoff states that *three* `test_episode_capture.py` tests
   "resolve 'the one shipped `durable` declaration' and assert it is `.agent-work/LESSONS.md`". Measured:
   only **one** did (`test_roots_durable_resolves_the_one_shipped_declaration_without_double_nesting`).
   The other two (`..._is_the_checkout_root_not_the_agent_work_directory`,
   `..._is_resolved_from_the_repo_root_not_the_checklist_directory`) already build their own entries and
   **passed unmodified**. I still touched their docstrings/literals, for a reason inside this issue's
   own subject matter: they *described* "the one shipped declaration", which after this change is a
   stale claim — the same defect class the `episode_capture.py` comments were called out for.
4. **`.agent-work/issue-308/` engine files were already dirty** when I was dispatched
   (`crew-runs.json`, `execute.json`, `execute.json.journal`). I left them alone; flagging so the
   Commander does not read them as crew output.

## Workflow Feedback
- **Handoff gaps:** the **Test mode** field is not stated anywhere as a field. I inferred
  `test-after / guard-led` from the Close Criteria and the "run it before you edit and paste the red
  transcript" instruction. It happened to be unambiguous here *because* a red guard shipped with the
  handoff, but the Implementer skill's completeness check names test mode explicitly, so an implementer
  following that check literally would have blocked and returned on a handoff that was otherwise the
  most complete I could ask for. Also: the blast-radius section's "three tests" count was
  over-inclusive (see Out-of-scope #3) — ironic for this epic, and harmless only because it erred toward
  *more* review rather than less.
- **Context rediscovered:** (a) whether the three surviving `COMMANDER_SPINE` writer lines trip the
  guard's own regexes. The handoff asserts they must survive but not that they *can* — if any of them had
  matched a marker, the gate would have been unsatisfiable and I would have had to stop. I had to derive
  that myself by running the six markers line-by-line; it took one command and it is the single most
  decision-relevant fact on this gate. Worth carrying in the handoff. (b) `docs/agents/GLOSSARY.md` does
  not exist in this repo — the plan template and the spine both list it as a context ref, so every crew
  member here rediscovers its absence.
- **Instructions improvised around:** the plan template's `config_ref` defaults to
  `docs/agents/engine-config.json`, which **does not exist in this repo** (`git ls-files | grep
  engine-config` → empty) — yet 100+ existing work files under `.agent-work/` all carry that same dead
  path, so I matched the convention rather than diverging. The engine does not complain, which means the
  field is inert here; a field every artifact fills with a path that resolves to nothing is either a
  missing file or a field that should be dropped.
- **What would have made this easier:** one line in the handoff's over-reach warning stating that the
  three survivors were *verified clean against the guard's markers* — turning "don't touch these" into
  "these are already safe, and here is the command that shows it." That converts the highest-risk
  instruction on the gate from a prohibition into a reproducible fact.

## Return status
`complete`
