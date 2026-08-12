---
name: constellation-write-a-skill
description: Mint a new constellation skill from a described capability — classify it, scaffold from an archetype, draft the skills/<name>/ tree, then hand to an independent reviewer. Use when a human wants to author a NEW skill. Not curator (which maintains existing skills, never mints).
invoker: human
---

# Constellation Write-a-Skill

Turn a described capability into a well-formed, installable skill: **classify → scaffold → draft → independent review**. The author *mints*; `curator` *maintains*; both judge goodness by one standard — `_shared/skill-goodness.md`. Read it first.

**No checklist. Work the draft directly** — a lean chat pass, not a gated engine. One rail is enforced; goodness past that is the reviewer's judgment.

## 1. Classify the target skill

Every skill is one of three archetypes; the described capability picks one, and it decides the scaffold:

| Archetype | When | Shape |
|---|---|---|
| **lean** | a judgement made repeatable; no multi-step state | chat-first prose, maybe one rail script (`to-initial-issues`, `diagnose`) |
| **gated-engine** | ordered steps that must not be skipped | a `templates/*.json` checklist driven through `checklist_engine.py` (`commander`) |
| **survey** | visit-every-item inquiry that consolidates a verdict | a `survey` checklist (`reviewer`, `interrogator`) |

Most new skills are **lean**. Reach for gated-engine/survey only for genuinely ordered gates or a consolidation step.


## 2. Scaffold from the archetype

Copy `templates/<archetype>-SKILL.template.md` into `skills/<short-name>/SKILL.md` and fill it. Directory is the short name; frontmatter `name:` is `constellation-<short-name>`. The description carries a **when-to-use** trigger and, for a confusable skill, an **exclusion clause**; add the `invoker:` tag.

## 3. Draft against the criteria

Draft `SKILL.md` (+ `references/`, `templates/` as needed) to satisfy `_shared/skill-goodness.md`: predictable process, sharp completion criteria, leading words, negative space, no sediment. Keep the body tight; push detail to `references/`.

## 4. Clear the one rail

`python <skill-dir>/scripts/verify_skill_registered.py --skill <short-name>` must pass. It refuses a **mechanically broken** skill (unparseable, no when-to-use marker, missing exclusion on a confusable skill, no invoker) or an **unregistered dead seam** — one not wired into `install_constellation.py`'s bundles, so it installs with no doctrine or rail script. It composes `curate_corpus.py` + `install --dry-run`. So **register the skill** while minting: add it to `SKILL_SCRIPT_BUNDLES` (if it ships a script) and `SKILL_REFERENCE_BUNDLES` (doctrine), and add `constellation-<name>` to the installer test's `SKILL_NAMES`. That missing registration is the failure mode the rail guards.

Semantic goodness is **not gated** — the rail proves the skill installs and is registered, never that it is *good*.

## 5. Hand to an independent reviewer

A fresh-context reviewer — never the author — judges the **semantic subset** of `_shared/skill-goodness.md`, decides review weight, and co-signs any rail exception with a log entry. Surface the shape and notable calls conversationally; mint on a chat go-ahead.
