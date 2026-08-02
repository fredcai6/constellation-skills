# Implementer Handoff — issue-304 gate g3: delete the superseded prose, then RUN

## Assigned task

Delete the prose the g2 contract supersedes, **run the affected workflows against it**, and record each
outcome against a prediction that was committed *before* the deletion existed.

**The pathway is deletion PLUS run, not deletion alone.** A deletion with no run is half this gate.

Work ONLY in `C:/Programs/constellation-skills-wt/e298-304`. Never touch
`C:/Programs/constellation-skills` or `C:/Programs/constellation-skills-wt/e298-331`.
**`C:/Programs/f1Brainz` is read-only and `orient` WRITES a receipt into whatever `--root` it is given —
do not point any tooling at it.**

## STEP 1 — PRE-REGISTRATION IS ALREADY DONE. DO NOT REDO IT.

`TRIPWIRES.md` is committed at the repo root, in two commits, **both before any deletion exists**:

```
0119fa4  pre-register(#304): tripwire predictions BEFORE any prose deletion   (T1-T4)
1662b90  pre-register(#304): T5, the anchor change, after PRE-B named the mechanism
```

Git history is the tamper-evident timestamp. **Read `TRIPWIRES.md` now** — T1 through T5 are your
falsifiable predictions and you will be recording outcomes against them by name.

Do **not** file episodes yet. `apply_episode_delta.py create` requires `observed-behavior`, so filing
before observing means inventing an observation — exactly what this pathway forbids. Episodes come at
STEP 4, after the run.

## STEP 2 — DELETE, in its own separate commit

Two byte-parallel 86-word blocks (**172 words total** — this count has been corrected twice; it is not
112):

**(a) `skills/commander/templates/COMMANDER_SPINE.template.json`, `tasks.context.imperative`** — the
block running from `The checklist config_ref (docs/agents/engine-config.json) is absent-by-design…`
through `…rather than chasing the dead path.`

**(b) `skills/commander/templates/EXECUTE_PLAN.template.json`, `tasks.e0-context.imperative`** — the
byte-parallel block, opening `This checklist's config_ref (docs/agents/engine-config.json) is
absent-by-design…` through the same closing phrase.

### THE ONE WAY THIS GATE GOES WRONG — read it twice

The phrase **`no docs/agents/ overlay at all` occurs TWICE** in `tasks.context.imperative`. I measured
the offsets so you do not have to: **262** and **2330**.

- **The FIRST (262) is LOAD-BEARING and MUST SURVIVE.** It is the substitute-and-record rule —
  *"Where the repo carries no docs/agents/ overlay at all (e.g. a skill-source repo), substitute the
  closest repo doctrine you can find (README, CONTRIBUTING, top-level docs) and record the
  substitution"* — the degraded-mode intake this whole issue exists to **strengthen**.
- **The SECOND (2330) is inside the dead-path block** and goes.

A naive string-level delete removes both and silently strips degraded-mode intake while appearing to
remove only dead prose. The cold critic caught this before any edit was made; that is tripwire **T4**,
and it is a tripwire aimed at *your own edit*.

### Why these go (so you can judge whether the deletion is right, not just execute it)

The prose is **wrong in both directions now**: `docs/agents/` **exists in this repo** (it holds
`ORCHESTRATOR_CONTEXT.md`), so *"a skill-source repo has no docs/agents/ overlay at all"* is false on its
face; and Charter ships a task that **writes** `docs/agents/engine-config.json`, so *"do NOT create the
overlay file"* contradicts a sibling role's shipped deliverable.

**#317 resolves by subtraction:** with these 172 words gone, Charter becomes the sole remaining statement
about `docs/agents/engine-config.json`. Note that in your result; your Commander records it on #336.

### T3's retargeting — verify before you edit

T3 covers retargeting the pathless *"the current map"* phrasing at context and plan. **Most of this
already landed in g2** (the context imperative was re-anchored to *"Before you open any source file"*,
and the plan imperative was rewritten). **Check what is actually left** rather than re-editing what is
done — and if nothing is left, say so plainly and record T3 as already-discharged-by-g2. Do not
manufacture an edit to have something to report.

Commit the deletion **separately** from everything else. The commit boundary is evidence.

## STEP 3 — RUN. Concretely, not as a thought experiment.

Materialize a **fresh Commander spine in THIS repo** — which has `docs/agents/` but **no
`docs/architecture/`**, and is therefore the **degraded common case**, not an edge case:

```
python scripts/init_work_area.py --spine ... --work-id <scratch-id>
```

Drive it through **`init` and `context`** with the engine and **capture the engine's own output
verbatim** — not your description of it. The context step now carries the `verify-orientation` command
check, so this is where the contract either reports degraded or silently passes.

Record each observed outcome in **`.agent-work/issue-304/TRIPWIRE_OUTCOMES.md`**, against the
pre-registered prediction **by name (T1…T5)**, **citing the pre-registration commit SHA**
(`0119fa4` for T1–T4, `1662b90` for T5).

**If a tripwire fires against you, record it as firing.** The launch order is explicit: *"record it
against the tripwire rather than explaining it away — that is the entire point of filing predictions
before deleting."* A measured negative reported honestly is a complete deliverable here, not a failure.
T3 and T5 both predict the contract does **not** move ordering; that is deliberate, and confirming it is
a result.

Use a scratch work-id you clean up, and do not disturb `.agent-work/issue-304/`.

## STEP 4 — FILE the episodes

Via `scripts/apply_episode_delta.py` — the **only** write path into `episodes/active/`. One per
tripwire, each carrying:

- `expected-behavior` = the pre-registered prediction, as written in `TRIPWIRES.md`
- `observed-behavior` = **what actually happened in STEP 3**, real and specific, citing the
  pre-registration SHA

An episode whose `observed-behavior` restates the prediction has not observed anything. The store has no
`confirmed` standing (#342), so a tripwire that held and one never checked look identical in the store —
which is exactly why the citation and the real observation matter.

## STEP 5 — Pin the deletion in BOTH directions

Add **`tests/test_prose_deletions.py`** asserting:

- the deleted strings are **ABSENT** from both shipped templates, and
- the surviving substitute-and-record rule is still **PRESENT** in
  `COMMANDER_SPINE.template.json` `tasks.context.imperative`.

Absence alone would pass on a template that deleted everything. The presence assertion is what makes T4
a real tripwire rather than a comment.

## STEP 6 — The trend snapshot

Write **`.agent-work/issue-304/TREND_SNAPSHOT.md`**: corpus size / per-role surface, **derived from
git**, as the standing aggregate baseline.

**Admiral amendment, mandatory:** the snapshot must **name its consumer** — the *next* snapshot — and
state **when the successor is expected**. A baseline with no declared successor is a number nobody ever
compares against.

## Allowed scope

`skills/commander/templates/COMMANDER_SPINE.template.json`,
`skills/commander/templates/EXECUTE_PLAN.template.json`, `tests/test_prose_deletions.py` (new),
`.agent-work/issue-304/TRIPWIRE_OUTCOMES.md` (new), `.agent-work/issue-304/TREND_SNAPSHOT.md` (new),
`episodes/active/` **via `apply_episode_delta.py` only**.

## Deliverable Path Check (run by your Commander, recorded here)

`git check-ignore` returned exit 1 — **not ignored, therefore committable** — for every deliverable of
this gate: both templates, `tests/test_prose_deletions.py`, `episodes/active/`,
`.agent-work/issue-304/TRIPWIRE_OUTCOMES.md`, `.agent-work/issue-304/TREND_SNAPSHOT.md`. Nothing here is
intentionally local-only. If a file you write does not show up in `git status`, that is a finding, not a
thing to work around.

## Specific exclusions

- **Do not re-register the tripwires.** They are committed. Re-writing `TRIPWIRES.md` destroys the
  pre-registration property.
- Do not touch `scripts/map_orient.py` or the g2 wiring — that gate is closed and reviewed.
- No bootstrap/`CLAUDE.md` stanza. **Ruled OUT** by the human: the map is orchestrator content, not
  implementer content.
- Do not fix #341 (relative command checks), #342 (episode store standings), #344 (stale installed
  corpus), or the `--receipt-dir` item.
- Do not modify `checklist_engine.py`.
- Do not run the g4 dogfood pass or the full suite as this gate's evidence — that is g4.

## Constraints

- **`COMMANDER_SPINE.template.json` is pinned by several suites**: `test_context_manifest.py` pins
  `tasks.context.context_refs` as a literal list; `test_context_declaration_lint.py` requires every
  declared `context_refs` path to appear **verbatim** in that task's imperative — so deleting prose that
  contains a declared path breaks it; `test_context_determinism.py` overlays the template into fresh
  checkouts. **Run all three**, and note that the block you are deleting mentions
  `docs/agents/engine-config.json`, which is a declared `context_refs` entry. Check whether it still
  appears elsewhere in the imperative after your deletion. If it does not, that is a real conflict —
  **stop and report it**, do not resolve it by editing what the tests pin.
- Windows: write files with explicit `encoding='utf-8', newline='\n'`.
- `python -m pytest`, **never** `py -m pytest` (`py` is 3.12 — CI's pin — with no pytest; `python` is
  3.14 with pytest). Neither reproduces CI. **No 3.13+-only APIs**: `Path.read_text(newline=...)` passed
  locally and cost 39 CI failures on PR #320.
- Compare normalized content or blob OIDs, never raw bytes — `core.autocrlf` makes working-tree bytes
  differ for identical committed content, and `git status --porcelain` will show a phantom `M` while
  `git diff --quiet HEAD` returns 0. Three agents hit this in this epic; the g2 reviewer hit it again.
- Commit after each step closes. Two agents on this issue died mid-gate on session usage limits and
  their work survived only because it got committed.

## Required evidence

```
cd C:/Programs/constellation-skills-wt/e298-304
python -m pytest tests/test_prose_deletions.py tests/test_context_manifest.py tests/test_context_declaration_lint.py tests/test_context_determinism.py tests/test_map_contract_wiring.py tests/test_init_work_area.py -q
```

Plus, pasted verbatim:
- the **word count** of what you deleted, derived from a command, not asserted;
- the **engine's own output** from the STEP 3 run through `init` and `context`;
- the episode ids filed, and one full episode showing its `observed-behavior`;
- proof the load-bearing first occurrence **survives** (the assertion, and its output).

## Stop conditions

Stop and report if: deleting the block removes a `context_refs`-declared path that appears nowhere else
in the imperative; the STEP 3 run cannot be driven through `context` at all (as opposed to being
*refused* at `context`, which is the contract working and is a **result**, not a blocker); or a tripwire
outcome cannot be honestly determined from what you observed.

Report **"this specific check failed"**, never "this approach is impossible." Never fabricate evidence,
and never smooth over a tripwire that fires.

## Return format

Write `IMPLEMENTER_RESULT` to `.agent-work/issue-304/crew-handoffs/g3-result.md` with evidence pasted
verbatim, every deviation and its reason, and any unresolved blocker. That file on disk is the contract
your Commander polls for and verifies. **Only claim a cleanup you have verified** — an earlier result on
this issue asserted a removal that had not happened, and a later one reported an audit as complete when
it had covered two of three items. Return thin.
