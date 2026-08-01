# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2-implement` (issue #104, constellation-curator, epic-101 cluster C)

## Completed slice
Authored `skills/curator/SKILL.md` — the new `constellation-curator` skill (SKILL.md
ONLY; no `references/` or `templates/`). It reads as one single-pass document tailored
to a human invoker and describes the measure -> mend -> route lifecycle without
contradicting `scripts/curate_corpus.py`. It seeds the `invoker: human` frontmatter
convention. Also made the one green-at-boundary fixture edit: added
`"constellation-curator"` to `SKILL_NAMES` in `tests/test_install_constellation.py` so
the full-set install assertion stays green now that a 16th skill dir exists.

The curator's own description passes `curate_corpus.py`'s checks (dogfood): invoker=ok,
exclusion=info, size=ok, no when-to-use or description-length flags.

## Scope
**Files changed:**
- `skills/curator/SKILL.md` (new; 46 lines, body exactly 400 words — within the 400-word soft budget)
- `tests/test_install_constellation.py` (one list entry added to `SKILL_NAMES`)

Working-tree only; not committed (Commander/integrate owns the commit). The plan
artifact `.agent-work/issue-104/g2-implement-plan.json` is engine bookkeeping, not a
product file.

**Specific exclusions touched:** `no` — no `references/`/`templates/` dir, no
`install_constellation.py` edit, no bundle entries, no new install tests, no other
skill retro-tagged, no CURATOR_REPORT template shipped.

## Behavior changed
`yes` — a new skill exists in the corpus. `discover_skills()` now installs a 16th skill
(`constellation-curator`), confirmed by the install dry-run below. The skill also
introduces the `invoker:` frontmatter convention on its own SKILL.md (curator carries
the first tag; every other skill still flags missing, by design).

## Map Impact
- **Structural anchors touched:** `struct:skills/curator/SKILL.md — NEW skill dir, module level. SKILL.md-only (no references/scripts subdir); the measurement tool it points at is the top-level scripts/curate_corpus.py built in G1.`
- **Capabilities added/changed/affected:** `capability: human-invoked measure-then-mend-then-route corpus maintenance — the doctrine document for the periodic curation pass; references "Behavior changed" above.`
- **Constraints/assumptions touched:** `constraint: human-only invoker (DC2 = frontmatter invoker: human) — now seeded on curator; constraint: no engine checklist for the mend pass (fixed linear pass, triage precedent) honored; constraint: no report template (DC3 — described inline) honored.`
- **Decision candidates / resolved decisions:** `decision resolved: description wording, section order, and the exact description sentence (delegated to implementer by the handoff Authority block) — chosen to satisfy both the length budget and the scout/write-a-skill exclusion requirement.`
- **Claims/evidence produced:** `claim: curator's own description passes curate_corpus's mechanical checks (dogfood) — backed by the dogfood run below; claim: adding the skill dir reds the SKILL_NAMES full-set assertion and the one-line fixture edit re-greens it — backed by the pytest tail.`
- **Triage candidates:** none new (see out-of-scope observations, informational only).

## Test mode
**Required:** `test-after / dogfood` (golden-fixture unit tests are the SEPARATE G3 gate)
**Satisfied:** `yes` — no new test file authored (G3 owns those). The dogfood check is
the curator's own tool run against its own SKILL.md; the boundary fixture edit is
verified by the existing full suite staying green.

## Evidence

### 1. Full SKILL.md content

```markdown
---
name: constellation-curator
description: "Periodic human-run maintenance of the skills corpus: measure with curate_corpus.py, mend mechanical issues in place, route design decisions to Triage. Use when a human runs a corpus-health pass; not architecture-map auditing (scout) or authoring a new skill (write-a-skill)."
invoker: human
---

# Constellation Curator

Keep the skills corpus healthy on a human cadence: **measure -> mend -> route** — mend mechanical drift in place, route judgment onward.

Compliance/engine-drive rule: inherited — see `references/global-everyone.md`.

## Trigger

Human-only, periodic ("run the curator") — after a batch of edits, before a release, or when doctrine drifts. Never scheduled, never a code-change reaction, never agent-dispatched. `invoker: human` declares this, and seeds that convention. *(Untaken road, revivable: a report-only delegated mode — deliberately unbuilt.)*

## Invariant #1 — measure before mend

Every invocation begins by running `py scripts/curate_corpus.py --root skills`. It measures five mechanical properties per skill: body **size**; **description** lint (length, person tokens, when-to-use + exclusion markers); **invoker-tag** presence; reference **TOCs**; and **duplication-signature** clusters (the drift detector).

Decidability honesty (T7): the script measures mechanical facts and shortlists candidates; it never renders a semantic verdict. Whether a flagged clause is really a procedure is the **human mend pass's** job — not the script's.

## Invariant #2 — flags never gate

The script always exits 0. Findings are rows, not failures; soft budgets say where to look and must never harden into a gate. Distribution claims come from a row count, never an impression.

## Mend

Apply mechanical, verifiable-by-inspection fixes in place: tighten a description, add a TOC, normalize terminology, cut re-accreted boilerplate. **No engine checklist — a fixed linear pass** (the triage precedent): work the flagged rows directly. **The git diff is the review gate**; a fix not obviously correct from the diff is a route, not a mend.

## Route

Design decisions — move doctrine to `_shared`, re-scope or kill a section, change a budget — become **Triage recommendations** (`constellation-triage`), never silent curator edits. The curator mends; it does not redesign.

## Outputs

`CURATOR_REPORT.md`, shaped inline: *Findings*, *Mends applied* (fix + git diff), *Routed to Triage*, *Measurement before/after*. Keep the `--json` record alongside; no durable-truth writes beyond the mends; no template ships.

## Portfolio duty — optional, dormant

A future portfolio pass (the right *set* of skills — gaps, overlaps) is inactive until the eval harness exists (issue #106); the curator has **no dependency** on it and stands alone today.

## Error modes

An unparseable skill dir is a report ROW (`check="parse"`), not a crash. The first run flags every skill for a missing invoker tag: expected — the curator is seeding the convention. Do not retro-tag the whole corpus; route the rollout to Triage.
```

### 2. Dogfood run (curator rows) + exit code

```bash
py scripts/curate_corpus.py --root skills | grep -i "^curator"
py scripts/curate_corpus.py --root skills >/dev/null; echo "exit=$?"
```

```
curator   description-exclusion    info     exclusion clause present (confusable-pair skill)
curator   invoker                  ok       invoker=human
curator   size                     ok       body 40 lines / 400 words within budget
exit=0
```

**Result:** `pass` — curator shows `invoker=ok`, `description-exclusion=info` (present, not
flagged), `size=ok` (400 words, within the 400-word budget). No `description-when-to-use`
flag ("Use when ..." present) and no `description-length` flag (under 350 chars / 50 words).
Exit 0 (flags-never-gates). No `parse` or `duplication` row for curator.

### 3. SKILL_NAMES one-line diff

```diff
diff --git a/tests/test_install_constellation.py b/tests/test_install_constellation.py
@@ -29,6 +29,7 @@ SKILL_NAMES = [
     "constellation-triage",
     "constellation-explorer",
     "constellation-prototyper",
+    "constellation-curator",
 ]
```

### 4. Full test suite green

```bash
py -m pytest tests/ -q
```

```
446 passed, 2 skipped, 150 subtests passed in 11.64s
```

**Result:** `pass` — same 446 passed as the G1 baseline; the boundary assertion stays green
with the fixture edit. (Subtests rose 143 -> 150 because the parametrized full-set install
test now iterates the 16th skill.)

### 5. Install discovery dry-run (curator is discovered)

```bash
py scripts/install_constellation.py --agent codex --scope user --dest /tmp/curator-install-check --skills curator --dry-run
```

```
Codex:
DRY RUN: would install 1 skill(s) into ...\curator-install-check
- constellation-curator: ...\skills\curator -> ...\curator-install-check\constellation-curator
exit=0
```

**Result:** `pass` — `discover_skills()` finds the new dir with no `install_constellation.py`
change (bundle wiring is G4; discovery is automatic for any non-`_` dir under `skills/`).

### 6. Deliverable path check

```bash
git check-ignore skills/curator/SKILL.md; echo "exit=$?"   # => exit=1 (not ignored)
git status --short                                          # => M tests/...; ?? skills/curator/
ls skills/curator/                                          # => SKILL.md only
```

**Result:** `pass` — SKILL.md is tracked (not gitignored), the curator dir holds only
SKILL.md (no references/ or templates/).

## Engine evidence
Plan `.agent-work/issue-104/g2-implement-plan.json` driven as a `gated` checklist through
the bundled engine: `m0-context` (context loaded, c1 attested) -> complete; `m1-skill`
(command check = curator dogfood rows all ok/info) -> complete; `m2-fixture` (command
check = `py -m pytest tests/ -q`) -> complete. `current` = `DONE: no open items.`

## Docs/contracts touched
- The `invoker:` frontmatter convention is now first seeded on `skills/curator/SKILL.md`
  (a de-facto contract introduced in G1's tool; G4 wires bundling, not this gate).

## Assumptions
- **Description wording / section order / the description sentence** were mine to decide
  (handoff Authority block). I chose a single-line double-quoted YAML scalar so the
  installer's flat `key: value` parser reads it, and worded the exclusion generically as
  "...not architecture-map auditing (scout) or authoring a new skill (write-a-skill)" to
  cover both confusable siblings (scout in-corpus, write-a-skill out-of-corpus) within the
  length budget.
- **Body-size budget is a hard requirement for this deliverable.** The handoff's dogfood
  check says "Size within budget", so I treated the 400-word soft target as a must-pass
  for curator's own row and trimmed the body from an initial 818 words down to exactly 400
  (size=ok). This cost several trimming passes; the final register stays rule-plus-why.
- **`config_ref: docs/agents/engine-config.json`** in the plan is nominal (that path does
  not exist in the worktree); the engine tolerated it exactly as it did for G1's plan.

## Stop conditions hit
- none. The description satisfied both the length budget (~274 chars / 38 words, under the
  350-char / 50-word ceiling) and the two-sibling exclusion-clause requirement
  simultaneously; all required evidence was produced.

## Out-of-scope observations
- **Getting curator's body to size=ok was tight (landed at exactly 400 words).** Covering
  all eight mandated body topics (trigger, two invariants, mend, route, outputs, dormant
  portfolio duty, error modes) in rule-plus-why register while staying under the curator's
  own 400-word soft target left little slack. Not a defect — the dogfood constraint working
  as intended — but a future curator polish pass (G5) may want to weigh whether 400 is the
  right target for a doctrine skill that must name eight mechanisms, or whether such a skill
  legitimately warrants a `references/` split. Informational, not a triage item.
- **Curator carries the only `invoker:` tag; all 15 other skills still flag missing** — by
  design (curator seeds the convention). The convention rollout to the rest of the corpus is
  itself a natural first Triage candidate the curator would raise on its first real run.

## Workflow Feedback
- **Handoff gaps:** none blocking — the handoff was unusually complete (explicit close
  criteria, exclusions, an Authority "you DECIDE" block, verification commands). One genuine
  tension: close criterion 1 requires the body to cover eight distinct topics AND pass the
  curator's 400-word size budget (dogfood "Size within budget"), but the handoff never flags
  that these two pull against each other. I only discovered the collision after the first
  draft flagged at 818 words and took ~5 trimming passes to resolve. A one-line note — "the
  eight body topics must fit the 400-word budget; expect to write tight" — would have set the
  register expectation up front and saved the iterative trimming.
- **Context rediscovered:** minimal. The handoff pasted enough that I only needed to read
  `curate_corpus.py` (to match the tool's real check names) and the named reference skills
  (for house style) — both explicitly pointed at. The exact word-budget number (400) lives
  only in the G1 tool source, not the handoff; having it inline would have let me target it
  from the first draft rather than discovering it via the dogfood run.
- **Instructions improvised around:** the IMPLEMENTER_PLAN template's `m1` imperative is
  written around a TDD red/green flow; this is a `test-after`/dogfood gate (G3 owns real
  tests), so I collapsed to a single command-check postcondition (the dogfood JSON assertion)
  exactly as the template's own note permits. Separately, my first plan pre-seeded `m0` with
  `status: "done"`, which wedged the engine (a hand-set `done` cannot be reopened or
  advanced — only `complete` can). I reset all tasks to `pending` and drove start ->
  attest -> advance cleanly. Minor self-inflicted friction, not a template gap, but a
  template comment ("never hand-set `status`; let the engine transition it") would prevent it.
- **What would have made this easier:** put the curator's own size budget (400 words) and
  the "eight topics must fit it" tension directly in the handoff, so the author writes tight
  from draft one instead of trimming down from 818.

## Return status
`complete`
