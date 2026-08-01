# Implementer Handoff

Concise fragments. Omit filler.

## Gate
g2 — delegated entry skill + install wiring + index + tests + admiral description line.

## Task
Create the new `constellation-commander-delegated` entry skill and wire it into the install/test/index machinery so the full suite is green. The load-bearing description texts are AUTHORED BELOW verbatim — paste them exactly (they are the live skill-selection surface); do not reword.

## Protected Intent
An agent choosing a skill from frontmatter descriptions alone must be able to tell `constellation-commander` (live human drives one issue), `constellation-commander-delegated` (frozen LAUNCH_ORDER drives one issue), and `constellation-admiral` (runs an epic) apart. The split must not leave any test red.

## Test Mode
test-after allowed — this is install-plumbing; the evidence is the green suite + new per-skill assertions. (Not TDD: the wiring and its tests co-land in one gate.)

## Close Criteria
- `skills/commander-delegated/SKILL.md` exists with the EXACT frontmatter below.
- `py -m pytest tests/ -q` is fully green (the whole suite, not just the install file).
- `constellation-commander-delegated` installs, and its `references/` carries `global-everyone.md`, `global-orchestrator.md`, `windows.md`, `design-it-twice-brief.md` (the `_GLOBAL_ORCHESTRATOR` bucket).
- New per-skill install tests assert: (a) the skill installs (dir + SKILL.md present); (b) it gets the orchestrator+windows reference bucket; (c) the delegated SKILL.md contains the literal relative path string `references/commander-core.md` AND a full install of both skills yields an existing `constellation-commander/references/commander-core.md` file (existence + path-literal, NOT behavioral resolution).
- `SKILL_INDEX.md` has an accurate `## Constellation Commander (delegated)` entry.
- The one admiral description-line edit is applied (see below) and nothing else in `skills/admiral/SKILL.md` changes.

## Allowed Scope
- NEW: `skills/commander-delegated/SKILL.md` (only this file in that dir; no templates/scripts).
- EDIT: `scripts/install_constellation.py` — `SKILL_REFERENCE_BUNDLES` only (add one line).
- EDIT: `SKILL_INDEX.md` — add one entry.
- EDIT: `tests/test_install_constellation.py` — `SKILL_NAMES` list + add new per-skill test method(s). Pre-authorized: the two full-equality asserts over `SKILL_NAMES` will legitimately need the new name.
- EDIT: `skills/admiral/SKILL.md` — the frontmatter `description:` line ONLY (flagged fence exception, granted by launch order).

## Specific Exclusions
- Do NOT add `commander-delegated` to `SKILL_SCRIPT_BUNDLES` (critic #6 — `SKILL_SCRIPT_BUNDLES.get(name, ())` already defaults to empty; the delegated skill ships no scripts of its own and borrows commander's installed copies via the core's prose pointers).
- Do NOT create `skills/commander-delegated/templates/` or `.../scripts/` or `.../references/` source dirs (the reference bucket is injected by the installer at install time).
- Do NOT touch `skills/commander/**` (owned/frozen this gate — g1 already landed it), `skills/interrogator/**`, `skills/docent/**`, `_shared/**`, `docs/ROADMAP.md`, or any admiral line other than the description.
- Do NOT edit the commander templates.

## Constraints
- Core reference name is `commander-core.md` — it must NOT match the `global-*.md` glob (it doesn't; leave it).
- Cross-skill reach is by PROSE POINTER (the reviewer/implementer→workbench `references/checklist-engine.md` precedent), never a `<…-skill-dir>` token (those only rewrite inside the owning skill's own install, so a token here would resolve wrong).
- `constellation-commander-delegated` ships no templates/scripts; it names its co-install dependency on `constellation-commander` for core + templates.
- Descriptions are third-person, what + when-to-use, never procedure; the confusable-pair exclusion exists BOTH ways (delegated names admiral; admiral names delegated).

## Exact content to paste

### `skills/commander-delegated/SKILL.md`
```
---
name: constellation-commander-delegated
description: Runs one bounded issue end to end under a frozen Admiral LAUNCH_ORDER with no reachable human, citing the order and proceeding while taking genuine gaps up to the Admiral, as the delegate's rigor scaffold. Use for a delegated/launch-order dispatch of ONE issue; do NOT use when a human is driving (use constellation-commander), and to run an EPIC as the human's delegate use constellation-admiral.
---

# Constellation Commander (delegated)

Run one bounded issue end to end under an Admiral **launch order**, autonomously, when no human is reachable at the keyboard. This is the entry an Admiral-dispatched agent loads; the human-driven variant (`constellation-commander`) is a separate skill over the same core. This is not the epic runner — an epic spanning multiple issues is `constellation-admiral`.

## Your principal: the frozen launch order

The ratified `LAUNCH_ORDER` is your frozen principal and the Admiral is the human's delegate for this run. Running from a launch order **is** the signal that the human is not directly reachable: reconcile the ask against the order (Mission, Pre-Rulings, Inherited Context, Inherited Latitude) rather than interrogating a human, and **cite the order and proceed**. Satisfy each `user-decision` checkpoint by attaching a `user-decision` evidence item citing the governing launch-order section (the Admiral ratifies; the human ratifies at the epic return boundary).

This is not a licence to guess. When the order leaves a genuine gap, take it **up to the Admiral** — float a decision beyond your latitude, or query for context you lack — via your return/stop shape. A delegate is not a replacement: asking up is always sanctioned, never a failure.

## The doctrine

The full role doctrine — the checklists you own, the gated spine (init → context → understand → plan → execute → reconcile → triage → review → feedback → archive), gate execution, the mission frame, and the architecture bookend — lives once, mode-neutral, in the **constellation-commander skill's bundled `references/commander-core.md`** (under the installed `constellation-commander` skill directory), and you drive the run from the **constellation-commander skill's `templates/`**. Read "your principal" there as this launch order. This skill therefore depends on `constellation-commander` being installed alongside it (the default full-set install provides it), the same way every role depends on the installed `constellation-workbench` skill's engine reference. Inherited doctrine is in this skill's bundled `references/global-orchestrator.md` and `references/global-everyone.md`.
```

### Admiral description-line edit (FLAGGED fence exception)
Replace ONLY the `description:` line in `skills/admiral/SKILL.md` frontmatter with:
```
description: Run an epic as the human's delegate — confirm latitude, dispatch Commanders in waves, adjudicate and merge, close with lessons and architecture audits. Use when handed work spanning multiple issues; for ONE issue under a launch order use constellation-commander-delegated, not this skill.
```

### `install_constellation.py` — add to `SKILL_REFERENCE_BUNDLES`
Add the line (keyed by source dir name):
```
    "commander-delegated": _GLOBAL_ORCHESTRATOR,
```

### `SKILL_INDEX.md` — new entry (place right after the Commander entry)
```
## Constellation Commander (delegated)
Path: `skills/commander-delegated/SKILL.md`

Runs one bounded issue end to end under a frozen Admiral LAUNCH_ORDER, autonomously — the delegated entry over the same commander core doctrine and templates as `constellation-commander`.
```

## Map Anchors (inbound)
- **Structural:** `skills/commander-delegated/SKILL.md` (new); `scripts/install_constellation.py` `SKILL_REFERENCE_BUNDLES`; `SKILL_INDEX.md`; `tests/test_install_constellation.py` `SKILL_NAMES`; `skills/admiral/SKILL.md` description line.
- **Capability:** skill-install/bundle-composition; skill-selection (confusable pair commander-delegated ↔ admiral).
- **Constraints:** bundle-glob tests stay green; no new `global-*.md`; green-at-boundary (dir+wiring+tests co-land).
- **Decision anchors:** delegated entry name = `constellation-commander-delegated` (launch-order recommendation); entry-only-over-core (epic #101).
- **Evidence expectations:** `py -m pytest tests/ -q` green; new per-skill tests falsifiable.

## Deliverable Path Check
- **Committed** — `skills/commander-delegated/SKILL.md`, `scripts/install_constellation.py`, `SKILL_INDEX.md`, `tests/test_install_constellation.py`, `skills/admiral/SKILL.md`: all tracked, not ignored. Run `git check-ignore <path>` for each and confirm exit 1 before you report done.

## Required Evidence
- `py -m pytest tests/ -q` full output tail (must show 0 failed).
- The new test method source, and a run of ONLY the new tests showing them pass.
- Falsification note: state what one-line break in `install_constellation.py` or the delegated SKILL.md would red each new test (prove the tests bite).
- `git status --porcelain` showing exactly the five paths above changed/added (new files show as untracked until staged — say so).

## Verification Commands
```bash
py -m pytest tests/ -q
py -m pytest tests/test_install_constellation.py -q
git status --porcelain
```

## Suggested Model Tier
simple bounded — mechanical wiring against exact-specified content; the judgment (descriptions, mechanism choice) is pre-made in this handoff.

## Authority
Decisions already made (do not re-open): delegated entry name `constellation-commander-delegated`; cross-skill reach by prose pointer not token; `commander-delegated` omitted from `SKILL_SCRIPT_BUNDLES`; reference bucket `_GLOBAL_ORCHESTRATOR`; the exact description/index/admiral texts above; admiral edit limited to the description line. You must NOT change these; if any proves unbuildable, STOP and return.

## Stop Conditions
Stop and return if: the suite cannot be made green without touching a fenced/excluded file; a new `global-*.md` filename would be needed; the prose pointer cannot be expressed without a token; or any exact-specified text does not fit the mechanism.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (command tails), assumptions used, stop conditions hit, out-of-scope observations, workflow feedback. Your FINAL MESSAGE must be the complete IMPLEMENTER_RESULT before you go idle.
