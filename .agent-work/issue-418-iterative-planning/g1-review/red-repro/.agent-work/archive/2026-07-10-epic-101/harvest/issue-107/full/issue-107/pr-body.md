## Cluster F: commander entry-split + cluster B commander diet (epic #101, issue #107)

Splits `constellation-commander` into two thin **entry-only** skills over one **mode-neutral core reference**, so a loaded context never holds competing per-audience instructions, and diets the crew-dispatch mechanics out of the always-loaded body.

### What changed
- **`skills/commander/references/commander-core.md`** (new): the full role doctrine, written once, mode-neutral against "your principal". Both entries point here; neither carries competing doctrine.
- **`skills/commander/SKILL.md`**: rewritten to a thin **human** entry (2452 → 254 words) — live-human binding (surface decisions; ask and wait), exclusion clause toward `constellation-commander-delegated`, pointer into the core.
- **`skills/commander-delegated/SKILL.md`** (new): thin **delegated** entry — frozen-launch-order binding (cite and proceed; genuine gaps go up to the Admiral), the admiral-confusable exclusion, and a prose pointer at the installed `constellation-commander` skill's bundled `references/commander-core.md` + `templates/`.
- **`skills/commander/references/crew-dispatch.md`** (new, cluster B diet): the ~250-word crew-backend + "never hand-launch a crew" paragraphs move here; the core keeps a one-line pointer.
- **`scripts/install_constellation.py`**: `commander-delegated` wired into `SKILL_REFERENCE_BUNDLES` (`_GLOBAL_ORCHESTRATOR`); deliberately omitted from `SKILL_SCRIPT_BUNDLES` (it ships no scripts and borrows commander's). Core reached by the prose-pointer precedent (reviewer/implementer → workbench's engine), not a token.
- **`SKILL_INDEX.md`** + **`SKILL_NAMES`** + two new falsifiable per-skill install tests (bucket composition; core-pointer existence + path-literal).
- **`skills/admiral/SKILL.md`**: ⚠️ **ONE frontmatter `description:` line edited** (flagged fence exception, granted by the launch order) to carry the reciprocal `commander-delegated ↔ admiral` exclusion. Nothing else in that file changed.

### Constraints honored
History-to-current-truth sweep applied to all rewritten commander prose; no new `global-*.md` filename; commander `templates/` and `_shared/` untouched; core name `commander-core.md` does not match the bundle-glob; the issue-102 move-8 residual guard is preserved (not amended) — a first-pass verbatim collision with "delegate is not a replacement" was resolved by rewording the binding to the single-source pointer form, not a test carve-out.

### Verification
- `py -m pytest tests/ -q` → **446 passed, 2 skipped** (up from 444; the 2 new per-skill tests), rebased onto `origin/main` @ 8fc8b02.
- **Cold fresh-context selection check (F's binding acceptance)** — a haiku agent (one tier down) given only skill descriptions + three contexts named: human-driving → `constellation-commander`; launch-order dispatch → `constellation-commander-delegated`; epic → `constellation-admiral`. All correct.

### Deferred (recommend-and-defer, for Admiral routing)
- `SKILL_INDEX.md` has no automated pin (a wrong entry passes every gate).
- Commander-authoring lesson: dry-run verbatim SKILL.md prose against the residual-guard grep before dispatch.
- `commander-delegated`'s co-install soft-dependency on `commander` (precedented by the workbench-engine reference; named accepted risk).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01PvLMZiq6tkSCQfsuAL86Yr
